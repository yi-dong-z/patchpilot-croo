import { cn } from "@/lib/cn";

export function Badge({ children, accent = false }: { children: React.ReactNode; accent?: boolean }) {
  return (
    <span className={cn("inline-flex items-center border px-2 py-1 font-mono text-[11px]", accent ? "border-[#c55227] bg-[#c55227] text-white" : "border-[#bdb8ae] text-[#4d4a45]")}>{children}</span>
  );
}
