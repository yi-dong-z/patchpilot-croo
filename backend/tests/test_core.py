from decimal import Decimal

import pytest

from patchpilot.models import MissionRequest, RequestValidationError
from patchpilot.orchestrator import PatchPilot
from patchpilot.proof import sha256
from patchpilot.specialists import DEMO_PATCH


def request(**overrides):
    raw = {
        "repo_url": "https://github.com/patchpilot/demo-calculator",
        "commit_sha": "abc123",
        "issue": "Division truncates fractional output.",
        "acceptance_criteria": ["Division preserves fractional results"],
        "max_budget_usdc": 2,
    }
    raw.update(overrides)
    return MissionRequest.from_dict(raw)


def test_valid_request_and_budget():
    assert request().max_budget_usdc == Decimal("2")


@pytest.mark.parametrize("url", ["http://github.com/a/b", "https://gitlab.com/a/b", "not-a-url"])
def test_rejects_untrusted_repo_url(url):
    with pytest.raises(RequestValidationError):
        request(repo_url=url)


def test_rejects_insufficient_specialist_budget():
    with pytest.raises(RequestValidationError):
        request(max_budget_usdc=1)


def test_patch_hash_is_stable():
    assert sha256(DEMO_PATCH) == sha256(DEMO_PATCH)


def test_full_mock_procurement_flow():
    result = PatchPilot().run(request())
    assert result.status == "resolved"
    assert result.verification.tests_passed is True
    assert len(result.downstream_orders) == 2
    assert result.cost_usdc == "2"
    assert result.gross_margin_usdc == "1"
    assert all(item.order_id.startswith("mock_ord_") for item in result.downstream_orders)


def test_verifier_rejection_never_returns_patch():
    req = request(acceptance_criteria=["Completely unrelated behavior"])
    result = PatchPilot().run(req)
    assert result.status == "needs_human_review"
    assert result.patch == ""
    assert result.failure_reason


class FailingCommerce:
    mode = "mock"

    def __init__(self, reason):
        self.reason = reason

    def purchase(self, agent, service, payload):
        raise RuntimeError(self.reason)


@pytest.mark.parametrize("reason", ["order timed out", "insufficient_balance", "provider rejected order"])
def test_downstream_failures_never_claim_success(reason):
    result = PatchPilot(FailingCommerce(reason)).run(request())
    assert result.status == "failed"
    assert result.patch == ""
    assert reason in result.failure_reason
    assert result.gross_margin_usdc == "3"


def test_replayed_mission_is_idempotent_in_mock_mode():
    first = PatchPilot().run(request())
    second = PatchPilot().run(request())
    assert [item.order_id for item in first.downstream_orders] == [item.order_id for item in second.downstream_orders]
    assert first.patch_hash == second.patch_hash
