import { ArrowDown, GithubLogo, Wrench } from "@phosphor-icons/react/dist/ssr";
import { AgentFlow } from "@/components/agent-flow";
import { Badge } from "@/components/badge";
import { MissionConsole } from "@/components/mission-console";
import { getDemo } from "@/lib/demo";

export default async function Home() {
  const demo = await getDemo();
  const { result } = demo;
  return (
    <main>
      <nav aria-label="Primary navigation" className="mx-auto flex h-16 max-w-[1400px] items-center justify-between border-x border-[#d7d3ca] px-5 md:px-8 lg:px-12">
        <a href="#top" className="flex items-center gap-2 font-semibold"><Wrench className="size-5 text-[#c55227]" weight="fill" aria-hidden="true" />PatchPilot</a>
        <div className="flex items-center gap-5 text-sm">
          <a href="#proof" className="hidden text-[#67645e] hover:text-[#191917] sm:block">Proof</a>
          <a href="https://github.com" aria-label="View PatchPilot on GitHub" className="active:translate-y-px"><GithubLogo className="size-5" aria-hidden="true" /></a>
        </div>
      </nav>

      <header id="top" className="border-y border-[#d7d3ca]">
        <div className="mx-auto grid min-h-[calc(100dvh-4rem)] max-w-[1400px] border-x border-[#d7d3ca] lg:grid-cols-[1.15fr_0.85fr]">
          <div className="flex flex-col justify-center bg-[#f4f2ed]/95 px-5 py-14 md:px-8 lg:px-12">
            <Badge accent>CROO AGENT COMMERCE</Badge>
            <h1 className="mt-6 max-w-4xl text-balance text-5xl font-semibold leading-[0.95] md:text-7xl lg:text-8xl">Software fixes that buy their own proof.</h1>
            <p className="mt-7 max-w-[52ch] text-pretty text-lg leading-relaxed text-[#67645e]">One paid mission hires a fixer, funds an independent verifier, and returns a patch with economic receipts.</p>
            <div className="mt-9 flex flex-wrap gap-3">
              <a href="#mission" className="inline-flex items-center gap-2 bg-[#191917] px-5 py-3 text-sm font-semibold text-white active:translate-y-px">Inspect mission <ArrowDown className="size-4" aria-hidden="true" /></a>
              <a href="#proof" className="inline-flex items-center border border-[#8f8a80] px-5 py-3 text-sm font-semibold active:translate-y-px">View CAP proof</a>
            </div>
          </div>

          <aside aria-label="Mission economics" className="flex flex-col justify-end border-t border-[#d7d3ca] bg-[#ebe8e1]/95 p-5 md:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="mb-auto flex items-center justify-between"><span className="font-mono text-xs">MISSION / 001</span><Badge>{result.mode.toUpperCase()}</Badge></div>
            <p className="mb-6 mt-20 max-w-sm text-pretty text-xl">PatchPilot turns one customer order into two accountable specialist purchases.</p>
            <dl className="divide-y divide-[#bdb8ae] border-y border-[#bdb8ae]">
              {[
                ["Customer revenue", result.revenue_usdc],
                ["Specialist spend", result.cost_usdc],
                ["Gross margin", result.gross_margin_usdc],
              ].map(([label, value]) => <div key={label} className="flex items-end justify-between py-5"><dt className="text-sm text-[#67645e]">{label}</dt><dd className="font-mono text-3xl tabular-nums">{value}<span className="ml-1 text-xs">USDC</span></dd></div>)}
            </dl>
          </aside>
        </div>
      </header>

      <MissionConsole demo={demo} />
      <AgentFlow orders={result.downstream_orders} mode={result.mode} />

      <section aria-labelledby="proof-ledger" className="mx-auto max-w-[1400px] px-5 py-16 md:px-8 lg:px-12 lg:py-24">
        <h2 id="proof-ledger" className="text-balance text-3xl font-semibold md:text-5xl">The proof ledger</h2>
        <p className="mt-4 max-w-[60ch] text-pretty text-[#67645e]">Canonical inputs, patch contents and final delivery are independently hashed for an auditable handoff.</p>
        <dl className="mt-10 divide-y divide-[#d7d3ca] border-y border-[#d7d3ca] font-mono text-xs">
          {[["INPUT", result.input_hash], ["PATCH", result.patch_hash], ["DELIVERY", result.delivery_hash]].map(([label, value]) => <div key={label} className="grid gap-2 py-5 md:grid-cols-[120px_1fr]"><dt className="text-[#c55227]">{label}</dt><dd className="break-all text-[#67645e]">{value}</dd></div>)}
        </dl>
      </section>

      <footer className="border-t border-[#d7d3ca]">
        <div className="mx-auto flex max-w-[1400px] flex-col gap-3 px-5 py-8 text-sm text-[#67645e] md:flex-row md:items-center md:justify-between md:px-8 lg:px-12"><p>PatchPilot — built for the CROO AI Agent Hackathon.</p><p className="font-mono text-xs">MIT / 2026</p></div>
      </footer>
    </main>
  );
}
