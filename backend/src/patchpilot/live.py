"""Credential-gated CROO provider entrypoints.

The local demo never imports the SDK. These runners require Python 3.10+, the
official croo-sdk extra, and a dedicated key for each registered agent.
"""
from __future__ import annotations

import asyncio
import json
import os
import urllib.request
from typing import Any, Callable

from .models import MissionRequest
from .models import MissionResult, OrderEvidence, Verification
from .proof import sha256
from .croo_commerce import purchase_service
from .specialists import FixerAgent, VerifierAgent


def _sdk(key_env: str):
    from croo import AgentClient, Config

    return AgentClient(
        Config(base_url=os.getenv("CROO_API_URL", "https://api.croo.network"), ws_url=os.getenv("CROO_WS_URL", "wss://api.croo.network/ws")),
        os.environ[key_env],
    )


async def _order_requirements(client: Any, order_id: str) -> dict:
    """Resolve requirements through the SDK's Order -> Negotiation relation."""
    order = await client.get_order(order_id)
    negotiation = await client.get_negotiation(order.negotiation_id)
    return json.loads(negotiation.requirements or "{}")


async def _provider(key_env: str, execute: Callable[[dict], dict]) -> None:
    from croo import DeliverableType, DeliverOrderRequest, EventType

    client = _sdk(key_env)
    stream = await client.connect_websocket()

    def on_negotiation(event: Any) -> None:
        asyncio.create_task(client.accept_negotiation(event.negotiation_id))

    def on_paid(event: Any) -> None:
        async def handle() -> None:
            try:
                delivery = execute(await _order_requirements(client, event.order_id))
                await client.deliver_order(
                    event.order_id,
                    DeliverOrderRequest(deliverable_type=DeliverableType.SCHEMA, deliverable_schema=json.dumps(delivery)),
                )
            except Exception as exc:
                await client.reject_order(event.order_id, f"execution failed: {exc}")

        asyncio.create_task(handle())

    stream.on(EventType.NEGOTIATION_CREATED, on_negotiation)
    stream.on(EventType.ORDER_PAID, on_paid)
    await asyncio.Event().wait()


def run_fixer() -> None:
    agent = FixerAgent()
    asyncio.run(_provider("CROO_FIXER_SDK_KEY", lambda raw: agent.execute(MissionRequest.from_dict(raw))))


def run_verifier() -> None:
    agent = VerifierAgent()
    asyncio.run(
        _provider(
            "CROO_VERIFIER_SDK_KEY",
            lambda raw: agent.execute(MissionRequest.from_dict(raw["request"]), raw["fixer_output"]),
        )
    )


def run_patchpilot() -> None:
    async def execute(raw: dict) -> dict:
        request = MissionRequest.from_dict(raw)
        input_hash = sha256(request.to_dict())
        fixer = await purchase_service(os.environ["CROO_FIXER_SERVICE_ID"], request.to_dict())
        verifier_payload = {"request": request.to_dict(), "fixer_output": fixer.delivery}
        verifier = await purchase_service(os.environ["CROO_VERIFIER_SERVICE_ID"], verifier_payload)
        passed = bool(verifier.delivery.get("tests_passed") and verifier.delivery.get("criteria_covered"))
        patch = str(fixer.delivery.get("patch", "")) if passed else ""
        orders = [
            OrderEvidence("Fixer Agent", "Generate verified patch", fixer.order_id, fixer.negotiation_id, fixer.tx_hash, "1"),
            OrderEvidence("Verifier Agent", "Independently verify patch", verifier.order_id, verifier.negotiation_id, verifier.tx_hash, "1"),
        ]
        body = {"status": "resolved" if passed else "needs_human_review", "patch": patch, "orders": [item.__dict__ for item in orders]}
        result = MissionResult(
            status=body["status"], patch=patch,
            verification=Verification(passed, bool(verifier.delivery.get("criteria_covered")), str(verifier.delivery.get("review", "")), str(verifier.delivery.get("test_summary", ""))),
            downstream_orders=orders, revenue_usdc="3", cost_usdc="2", gross_margin_usdc="1",
            input_hash=input_hash, patch_hash=sha256(patch), delivery_hash=sha256(body), mode="live",
            failure_reason="" if passed else "Independent verification rejected the patch.",
        ).to_dict()
        evidence_url = os.getenv("PATCHPILOT_EVIDENCE_API_URL", "").rstrip("/")
        token = os.getenv("EVIDENCE_INGEST_TOKEN", "")
        if evidence_url and token:
            def publish() -> None:
                body = json.dumps({"request": request.to_dict(), "result": result}).encode("utf-8")
                req = urllib.request.Request(
                    f"{evidence_url}/api/live-evidence",
                    data=body,
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=15):
                    pass
            await asyncio.to_thread(publish)
        return result

    async def live_provider() -> None:
        from croo import DeliverableType, DeliverOrderRequest, EventType

        client = _sdk("CROO_PATCHPILOT_SDK_KEY")
        stream = await client.connect_websocket()

        def on_negotiation(event: Any) -> None:
            asyncio.create_task(client.accept_negotiation(event.negotiation_id))

        def on_paid(event: Any) -> None:
            async def handle() -> None:
                try:
                    result = await execute(await _order_requirements(client, event.order_id))
                    await client.deliver_order(event.order_id, DeliverOrderRequest(deliverable_type=DeliverableType.SCHEMA, deliverable_schema=json.dumps(result)))
                except Exception as exc:
                    await client.reject_order(event.order_id, f"downstream procurement failed: {exc}")
            asyncio.create_task(handle())

        stream.on(EventType.NEGOTIATION_CREATED, on_negotiation)
        stream.on(EventType.ORDER_PAID, on_paid)
        await asyncio.Event().wait()

    asyncio.run(live_provider())


def run_customer() -> None:
    async def execute() -> None:
        request = MissionRequest.from_dict(
            {
                "repo_url": "https://github.com/patchpilot/demo-calculator",
                "commit_sha": "demo-bug-001",
                "issue": "Division incorrectly truncates fractional results.",
                "acceptance_criteria": ["Division preserves fractional results"],
                "max_budget_usdc": 2,
            }
        )
        purchase = await purchase_service(
            os.environ["CROO_PATCHPILOT_SERVICE_ID"],
            request.to_dict(),
            timeout_seconds=int(os.getenv("CROO_ORDER_TIMEOUT_SECONDS", "1200")),
            sdk_key_env="CROO_CUSTOMER_SDK_KEY",
        )
        print(json.dumps({
            "negotiation_id": purchase.negotiation_id,
            "order_id": purchase.order_id,
            "tx_hash": purchase.tx_hash,
            "delivery": purchase.delivery,
        }, indent=2))

    asyncio.run(execute())
