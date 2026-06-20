from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Protocol


@dataclass
class Purchase:
    negotiation_id: str
    order_id: str
    tx_hash: str
    delivery: Dict[str, Any]


class CommerceAdapter(Protocol):
    mode: str

    def purchase(self, agent: str, service: str, payload: Dict[str, Any]) -> Purchase: ...


class MockCommerceAdapter:
    """Deterministic local CAP simulator. IDs are explicitly prefixed mock_."""

    mode = "mock"

    def __init__(self, fixer: Any, verifier: Any):
        self.fixer = fixer
        self.verifier = verifier
        self._fixer_output: Dict[str, Any] = {}

    def purchase(self, agent: str, service: str, payload: Dict[str, Any]) -> Purchase:
        serializable = {
            key: value.to_dict() if hasattr(value, "to_dict") else value
            for key, value in payload.items()
        }
        token = uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(serializable, sort_keys=True, default=str) + service).hex[:12]
        if agent == "fixer":
            delivery = self.fixer.execute(payload["request"])
            self._fixer_output = delivery
        elif agent == "verifier":
            delivery = self.verifier.execute(payload["request"], payload["fixer_output"])
        else:
            raise ValueError(f"unknown specialist: {agent}")
        time.sleep(0.01)
        return Purchase(f"mock_neg_{token}", f"mock_ord_{token}", f"mock_tx_{token}", delivery)
