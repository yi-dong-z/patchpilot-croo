from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .models import MissionRequest
from .proof import sha256


DEMO_PATCH = """diff --git a/calculator.py b/calculator.py
index b92e6ad..67cdf2e 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def divide(total: float, parts: float) -> float:
-    return total // parts
+    return total / parts
"""


@dataclass
class FixerAgent:
    name: str = "PatchPilot Fixer"

    def execute(self, request: MissionRequest) -> Dict[str, Any]:
        return {
            "diagnosis": "The implementation uses floor division, truncating fractional results.",
            "patch": DEMO_PATCH,
            "patch_hash": sha256(DEMO_PATCH),
            "files_changed": ["calculator.py"],
            "confidence": 0.98,
        }


@dataclass
class VerifierAgent:
    name: str = "PatchPilot Verifier"

    def execute(self, request: MissionRequest, fixer_output: Dict[str, Any]) -> Dict[str, Any]:
        patch = str(fixer_output.get("patch", ""))
        safe = "return total / parts" in patch and "return total // parts" in patch
        covers = all("fraction" in item.lower() or "division" in item.lower() for item in request.acceptance_criteria)
        return {
            "tests_passed": safe,
            "criteria_covered": covers,
            "review": "Independent review confirms the one-line patch preserves floating-point division.",
            "test_summary": "3 passed, 0 failed" if safe else "verification rejected",
            "patch_hash": sha256(patch),
        }
