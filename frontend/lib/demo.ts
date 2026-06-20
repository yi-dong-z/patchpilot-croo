import type { Demo } from "./types";

export const fallbackDemo: Demo = {
  request: {
    repo_url: "https://github.com/patchpilot/demo-calculator",
    commit_sha: "demo-bug-001",
    issue: "Division incorrectly truncates fractional results.",
    acceptance_criteria: ["Division preserves fractional results"],
    max_budget_usdc: "2",
  },
  result: {
    status: "resolved",
    patch: "@@ -1,2 +1,2 @@\n def divide(total: float, parts: float) -> float:\n-    return total // parts\n+    return total / parts",
    verification: {
      tests_passed: true,
      criteria_covered: true,
      review: "Independent review confirms the one-line patch preserves floating-point division.",
      test_summary: "3 passed, 0 failed",
    },
    downstream_orders: [
      { agent: "Fixer Agent", service: "Generate verified patch", order_id: "mock_ord_8b7d18a1d92f", negotiation_id: "mock_neg_8b7d18a1d92f", tx_hash: "mock_tx_8b7d18a1d92f", price_usdc: "1", status: "completed" },
      { agent: "Verifier Agent", service: "Independently verify patch", order_id: "mock_ord_b390fb4f293d", negotiation_id: "mock_neg_b390fb4f293d", tx_hash: "mock_tx_b390fb4f293d", price_usdc: "1", status: "completed" },
    ],
    revenue_usdc: "3",
    cost_usdc: "2",
    gross_margin_usdc: "1",
    input_hash: "4be142ca29781cd8d9845353ea5283ae1c3f019db050d16657b8d7f87807ca26",
    patch_hash: "72c9d1676041c20cc0ab5202fc89dac19a8cd10dbdd85f343f157e02818c1347",
    delivery_hash: "b1189a60422d9bdc45218930a598702899f2ae9d42587c869573364b9070f118",
    events: [
      { stage: "mission.accepted", detail: "3.00 USDC customer escrow confirmed" },
      { stage: "budget.reserved", detail: "2.00 USDC reserved for specialist procurement" },
      { stage: "fixer.completed", detail: "Patch delivered and content hash recorded" },
      { stage: "verifier.completed", detail: "Acceptance criteria and regression tests checked" },
    ],
    mode: "mock",
    failure_reason: "",
  },
};

export async function getDemo(): Promise<Demo> {
  const base = process.env.PATCHPILOT_API_URL;
  if (!base) return fallbackDemo;
  try {
    const response = await fetch(`${base}/api/demo`, { next: { revalidate: 30 } });
    if (!response.ok) return fallbackDemo;
    return await response.json();
  } catch {
    return fallbackDemo;
  }
}
