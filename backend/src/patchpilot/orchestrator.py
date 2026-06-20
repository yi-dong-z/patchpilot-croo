from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from .commerce import CommerceAdapter, MockCommerceAdapter
from .models import MissionRequest, MissionResult, OrderEvidence, Verification
from .proof import sha256
from .specialists import FixerAgent, VerifierAgent


class PatchPilot:
    REVENUE = Decimal("3")
    SPECIALIST_PRICE = Decimal("1")

    def __init__(self, commerce: CommerceAdapter | None = None):
        self.fixer = FixerAgent()
        self.verifier = VerifierAgent()
        self.commerce = commerce or MockCommerceAdapter(self.fixer, self.verifier)

    def run(self, request: MissionRequest) -> MissionResult:
        events: List[Dict[str, str]] = []

        def event(stage: str, detail: str) -> None:
            events.append({"stage": stage, "detail": detail})

        input_hash = sha256(request.to_dict())
        event("mission.accepted", "3.00 USDC customer escrow confirmed")
        event("budget.reserved", "2.00 USDC reserved for specialist procurement")
        orders: List[OrderEvidence] = []
        try:
            fixer_purchase = self.commerce.purchase("fixer", "Generate verified patch", {"request": request})
            orders.append(self._evidence("Fixer Agent", "Generate verified patch", fixer_purchase))
            event("fixer.completed", "Patch delivered and content hash recorded")

            verifier_purchase = self.commerce.purchase(
                "verifier",
                "Independently verify patch",
                {"request": request, "fixer_output": fixer_purchase.delivery},
            )
            orders.append(self._evidence("Verifier Agent", "Independently verify patch", verifier_purchase))
            event("verifier.completed", "Acceptance criteria and regression tests checked")

            verification_raw = verifier_purchase.delivery
            passed = bool(verification_raw.get("tests_passed") and verification_raw.get("criteria_covered"))
            patch = fixer_purchase.delivery.get("patch", "") if passed else ""
            status = "resolved" if passed else "needs_human_review"
            failure = "" if passed else "Independent verification rejected the proposed patch."
        except Exception as exc:
            patch, status, failure, verification_raw = "", "failed", str(exc), {}
            event("mission.failed", "A downstream purchase failed; no success claim was issued")

        cost = self.SPECIALIST_PRICE * len(orders)
        delivery_body = {
            "status": status,
            "patch": patch,
            "orders": [order.__dict__ for order in orders],
            "input_hash": input_hash,
        }
        return MissionResult(
            status=status,
            patch=patch,
            verification=Verification(
                tests_passed=bool(verification_raw.get("tests_passed")),
                criteria_covered=bool(verification_raw.get("criteria_covered")),
                review=str(verification_raw.get("review", failure)),
                test_summary=str(verification_raw.get("test_summary", "not run")),
            ),
            downstream_orders=orders,
            revenue_usdc=str(self.REVENUE),
            cost_usdc=str(cost),
            gross_margin_usdc=str(self.REVENUE - cost),
            input_hash=input_hash,
            patch_hash=sha256(patch),
            delivery_hash=sha256(delivery_body),
            events=events,
            mode=self.commerce.mode,
            failure_reason=failure,
        )

    def _evidence(self, name: str, service: str, purchase: Any) -> OrderEvidence:
        return OrderEvidence(
            agent=name,
            service=service,
            order_id=purchase.order_id,
            negotiation_id=purchase.negotiation_id,
            tx_hash=purchase.tx_hash,
            price_usdc=str(self.SPECIALIST_PRICE),
        )
