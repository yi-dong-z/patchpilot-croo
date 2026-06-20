import asyncio
from dataclasses import dataclass

from patchpilot.live import _order_requirements


@dataclass
class FakeOrder:
    negotiation_id: str


@dataclass
class FakeNegotiation:
    requirements: str


class FakeClient:
    async def get_order(self, order_id):
        assert order_id == "order-1"
        return FakeOrder("neg-1")

    async def get_negotiation(self, negotiation_id):
        assert negotiation_id == "neg-1"
        return FakeNegotiation('{"issue":"fractional division"}')


def test_sdk_order_requirements_follow_negotiation_relation():
    payload = asyncio.run(_order_requirements(FakeClient(), "order-1"))
    assert payload == {"issue": "fractional division"}
