from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Dict, List
from urllib.parse import urlparse


class RequestValidationError(ValueError):
    pass


@dataclass(frozen=True)
class MissionRequest:
    repo_url: str
    commit_sha: str
    issue: str
    acceptance_criteria: List[str]
    max_budget_usdc: Decimal = Decimal("2")

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "MissionRequest":
        url = str(raw.get("repo_url", "")).strip()
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "github.com":
            raise RequestValidationError("repo_url must be an https://github.com URL")
        sha = str(raw.get("commit_sha", "")).strip()
        if not sha or len(sha) > 64:
            raise RequestValidationError("commit_sha is required and must be at most 64 characters")
        issue = str(raw.get("issue", "")).strip()
        if len(issue) < 12:
            raise RequestValidationError("issue must contain at least 12 characters")
        criteria = raw.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria or any(not str(item).strip() for item in criteria):
            raise RequestValidationError("acceptance_criteria must be a non-empty string array")
        try:
            budget = Decimal(str(raw.get("max_budget_usdc", 2)))
        except Exception as exc:
            raise RequestValidationError("max_budget_usdc must be numeric") from exc
        if budget < Decimal("2"):
            raise RequestValidationError("max_budget_usdc must cover the 2 USDC specialist budget")
        return cls(url, sha, issue, [str(item).strip() for item in criteria], budget)

    def to_dict(self) -> Dict[str, Any]:
        value = asdict(self)
        value["max_budget_usdc"] = str(self.max_budget_usdc)
        return value


@dataclass
class OrderEvidence:
    agent: str
    service: str
    order_id: str
    negotiation_id: str
    tx_hash: str
    price_usdc: str
    status: str = "completed"


@dataclass
class Verification:
    tests_passed: bool
    criteria_covered: bool
    review: str
    test_summary: str


@dataclass
class MissionResult:
    status: str
    patch: str
    verification: Verification
    downstream_orders: List[OrderEvidence]
    revenue_usdc: str
    cost_usdc: str
    gross_margin_usdc: str
    input_hash: str
    patch_hash: str
    delivery_hash: str
    events: List[Dict[str, str]] = field(default_factory=list)
    mode: str = "mock"
    failure_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
