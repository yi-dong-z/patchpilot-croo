# Five-minute judge demo

## 0:00–0:35 — The problem

Open the PatchPilot console. Say: “Software agents can generate patches, but buyers still cannot tell who did the work, what was paid, or whether anyone independently checked it.”

## 0:35–1:10 — Reproduce the bug

Run `cd demo-fixture && pytest -q`. Show the fractional-division failure. Return to the mission input and point out the repository commit, issue, acceptance criterion, and 2 USDC procurement budget.

## 1:10–2:45 — Execute the paid chain

Start the Demo Customer requester. Show the customer’s 3 USDC CROO order, followed by the PatchPilot AA wallet buying the 1 USDC Fixer service and 1 USDC Verifier service. Keep the Agent Store and Railway logs visible long enough to capture all three order IDs.

## 2:45–3:35 — Verify the result

Show the unified diff, apply it to the controlled fixture, and rerun `pytest -q`. Show `3 passed`. Point out that the Verifier is a separately registered, separately paid CROO Agent.

## 3:35–4:25 — Show economic and cryptographic proof

Open the flow and ledger sections. Show the real order IDs, payment transaction hashes, input hash, patch hash, delivery hash, 3 USDC revenue, 2 USDC specialist spend, and 1 USDC gross margin.

## 4:25–5:00 — Close

Say: “PatchPilot is not another coding chatbot. It is a profitable autonomous buyer that turns specialist agents into accountable software delivery.” Show the public repository, MIT license, Agent Store listings, and deployed URL.

## Recording rule

Do not record the default mock page as live proof. The live recording must display `LIVE PROOF` and SDK-issued identifiers without the `mock_` prefix.
