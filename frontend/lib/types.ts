export type Order = {
  agent: string;
  service: string;
  order_id: string;
  negotiation_id: string;
  tx_hash: string;
  price_usdc: string;
  status: string;
};

export type Demo = {
  request: {
    repo_url: string;
    commit_sha: string;
    issue: string;
    acceptance_criteria: string[];
    max_budget_usdc: string;
  };
  result: {
    status: string;
    patch: string;
    verification: {
      tests_passed: boolean;
      criteria_covered: boolean;
      review: string;
      test_summary: string;
    };
    downstream_orders: Order[];
    revenue_usdc: string;
    cost_usdc: string;
    gross_margin_usdc: string;
    input_hash: string;
    patch_hash: string;
    delivery_hash: string;
    events: Array<{ stage: string; detail: string }>;
    mode: string;
    failure_reason: string;
  };
};
