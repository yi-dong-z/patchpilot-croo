import { ArrowRight, CheckCircle, Cpu, ShieldCheck, User } from "@phosphor-icons/react/dist/ssr";
import type { Order } from "@/lib/types";
import { Badge } from "./badge";

const nodes = [
  { name: "Customer", role: "3 USDC mission", icon: User },
  { name: "PatchPilot", role: "Plans + procures", icon: Cpu },
  { name: "Fixer", role: "1 USDC order", icon: CheckCircle },
  { name: "Verifier", role: "1 USDC order", icon: ShieldCheck },
];

export function AgentFlow({ orders, mode }: { orders: Order[]; mode: string }) {
  return (
    <section id="proof" aria-labelledby="flow-title" className="border-y border-[#d7d3ca] bg-[#191917] text-[#f4f2ed]">
      <div className="mx-auto max-w-[1400px] px-5 py-14 md:px-8 lg:px-12">
        <div className="mb-10 flex flex-col items-start gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 id="flow-title" className="max-w-2xl text-balance text-3xl font-semibold md:text-5xl">One mission becomes an agent economy.</h2>
            <p className="mt-3 max-w-[60ch] text-pretty text-[#aaa69e]">Every specialist has a separate service, price, order and immutable delivery proof.</p>
          </div>
          <Badge accent>{mode.toUpperCase()} PROOF</Badge>
        </div>

        <div className="grid gap-px overflow-hidden border border-[#46443f] bg-[#46443f] md:grid-cols-4">
          {nodes.map((node, index) => {
            const Icon = node.icon;
            return (
              <div key={node.name} className="relative min-h-44 bg-[#222220] p-5">
                <div className="flex items-center justify-between">
                  <Icon className="size-6 text-[#dc7147]" weight="duotone" aria-hidden="true" />
                  <span className="font-mono text-xs tabular-nums text-[#77736b]">0{index + 1}</span>
                </div>
                <h3 className="mt-12 text-xl font-semibold">{node.name}</h3>
                <p className="mt-1 text-sm text-[#aaa69e]">{node.role}</p>
                {index < nodes.length - 1 && <ArrowRight className="absolute -right-3 top-1/2 z-10 hidden size-6 bg-[#222220] text-[#dc7147] md:block" aria-hidden="true" />}
              </div>
            );
          })}
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          {orders.map((order) => (
            <article key={order.order_id} className="border-t border-[#57534c] pt-5">
              <div className="flex items-center justify-between gap-4">
                <h3 className="font-semibold">{order.agent}</h3>
                <span className="font-mono text-sm tabular-nums text-[#dc7147]">{order.price_usdc}.00 USDC</span>
              </div>
              <p className="mt-1 text-sm text-[#aaa69e]">{order.service}</p>
              <dl className="mt-5 grid gap-2 font-mono text-xs text-[#8e8a82]">
                <div className="flex gap-3"><dt className="w-16 text-[#f4f2ed]">ORDER</dt><dd className="truncate">{order.order_id}</dd></div>
                <div className="flex gap-3"><dt className="w-16 text-[#f4f2ed]">TX</dt><dd className="truncate">{order.tx_hash}</dd></div>
              </dl>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
