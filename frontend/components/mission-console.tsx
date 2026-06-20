import { Check, GitBranch, SealCheck } from "@phosphor-icons/react/dist/ssr";
import type { Demo } from "@/lib/types";
import { Badge } from "./badge";

export function MissionConsole({ demo }: { demo: Demo }) {
  const { request, result } = demo;
  return (
    <section id="mission" aria-labelledby="mission-title" className="mx-auto max-w-[1400px] px-5 py-16 md:px-8 lg:px-12 lg:py-24">
      <div className="grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
        <div>
          <h2 id="mission-title" className="text-balance text-3xl font-semibold md:text-5xl">A patch with receipts.</h2>
          <p className="mt-5 max-w-[55ch] text-pretty leading-relaxed text-[#67645e]">PatchPilot does not claim success until an independent paid agent verifies the patch against explicit acceptance criteria.</p>
          <dl className="mt-10 divide-y divide-[#d7d3ca] border-y border-[#d7d3ca]">
            <div className="py-4"><dt className="text-xs text-[#67645e]">ISSUE</dt><dd className="mt-1 font-medium">{request.issue}</dd></div>
            <div className="py-4"><dt className="text-xs text-[#67645e]">REPOSITORY</dt><dd className="mt-1 truncate font-mono text-sm">{request.repo_url}</dd></div>
            <div className="py-4"><dt className="text-xs text-[#67645e]">ACCEPTANCE</dt><dd className="mt-1">{request.acceptance_criteria[0]}</dd></div>
          </dl>
        </div>

        <div className="border border-[#bdb8ae] bg-[#ebe8e1] shadow-sm">
          <div className="flex items-center justify-between border-b border-[#bdb8ae] px-4 py-3">
            <div className="flex items-center gap-2"><GitBranch className="size-4" aria-hidden="true" /><span className="font-mono text-xs">calculator.py</span></div>
            <Badge>{result.status.toUpperCase()}</Badge>
          </div>
          <pre className="overflow-x-auto p-5 font-mono text-xs leading-7 md:p-7 md:text-sm"><code>{result.patch}</code></pre>
          <div className="grid border-t border-[#bdb8ae] md:grid-cols-2">
            <div className="border-b border-[#bdb8ae] p-5 md:border-b-0 md:border-r">
              <div className="flex items-center gap-2 text-sm font-semibold"><Check className="size-4 text-[#c55227]" weight="bold" aria-hidden="true" />Tests passed</div>
              <p className="mt-2 font-mono text-xs tabular-nums text-[#67645e]">{result.verification.test_summary}</p>
            </div>
            <div className="p-5">
              <div className="flex items-center gap-2 text-sm font-semibold"><SealCheck className="size-4 text-[#c55227]" weight="fill" aria-hidden="true" />Criteria covered</div>
              <p className="mt-2 text-xs text-[#67645e]">Independent verification complete</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
