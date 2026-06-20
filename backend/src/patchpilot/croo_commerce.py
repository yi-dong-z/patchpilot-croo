from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict

from .commerce import Purchase


class CrooPurchaseError(RuntimeError):
    pass


async def purchase_service(
    service_id: str,
    payload: Dict[str, Any],
    timeout_seconds: int = 300,
    sdk_key_env: str = "CROO_PATCHPILOT_SDK_KEY",
) -> Purchase:
    """Buy one CROO service and return its real negotiation/order/transaction proof."""
    from croo import AgentClient, Config, EventType, NegotiateOrderRequest

    client = AgentClient(
        Config(
            base_url=os.getenv("CROO_API_URL", "https://api.croo.network"),
            ws_url=os.getenv("CROO_WS_URL", "wss://api.croo.network/ws"),
        ),
        os.environ[sdk_key_env],
    )
    stream = await client.connect_websocket()
    loop = asyncio.get_running_loop()
    finished: asyncio.Future[Purchase] = loop.create_future()
    state: Dict[str, str] = {"order_id": "", "tx_hash": ""}

    def on_created(event: Any) -> None:
        if state["order_id"] or finished.done():
            return
        state["order_id"] = event.order_id

        async def pay() -> None:
            try:
                paid = await client.pay_order(event.order_id)
                state["tx_hash"] = str(getattr(paid, "tx_hash", ""))
            except Exception as exc:
                if not finished.done():
                    finished.set_exception(CrooPurchaseError(f"payment failed: {exc}"))

        asyncio.create_task(pay())

    def on_completed(event: Any) -> None:
        if event.order_id != state["order_id"] or finished.done():
            return

        async def collect() -> None:
            try:
                delivery = await client.get_delivery(event.order_id)
                text = delivery.deliverable_schema or delivery.deliverable_text or "{}"
                finished.set_result(
                    Purchase(
                        negotiation_id=state.get("negotiation_id", ""),
                        order_id=event.order_id,
                        tx_hash=state["tx_hash"],
                        delivery=json.loads(text),
                    )
                )
            except Exception as exc:
                finished.set_exception(CrooPurchaseError(f"delivery collection failed: {exc}"))

        asyncio.create_task(collect())

    def on_failure(event: Any) -> None:
        if getattr(event, "order_id", "") == state["order_id"] and not finished.done():
            finished.set_exception(CrooPurchaseError(f"order ended as {event.type}"))

    def on_negotiation_failure(event: Any) -> None:
        if getattr(event, "negotiation_id", "") == state.get("negotiation_id") and not finished.done():
            finished.set_exception(CrooPurchaseError(f"negotiation ended as {event.type}"))

    stream.on(EventType.ORDER_CREATED, on_created)
    stream.on(EventType.ORDER_COMPLETED, on_completed)
    stream.on(EventType.ORDER_REJECTED, on_failure)
    stream.on(EventType.ORDER_EXPIRED, on_failure)
    stream.on(EventType.NEGOTIATION_REJECTED, on_negotiation_failure)
    stream.on(EventType.NEGOTIATION_EXPIRED, on_negotiation_failure)
    negotiation = await client.negotiate_order(
        NegotiateOrderRequest(service_id=service_id, requirements=json.dumps(payload, sort_keys=True))
    )
    state["negotiation_id"] = str(negotiation.negotiation_id)
    try:
        return await asyncio.wait_for(finished, timeout=timeout_seconds)
    finally:
        await stream.close()
