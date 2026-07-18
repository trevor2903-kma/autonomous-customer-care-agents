import Link from "next/link";

// Top bar dùng chung (design: hbar 53px, trắng, viền dưới). KHÔNG chứa nav admin —
// khách và admin là hai URL riêng, khách không thấy đường vào bảng điều hành.
export function TopBar() {
  return (
    <header className="sticky top-0 z-50 flex h-[53px] flex-none items-center justify-between border-b border-line bg-white px-[22px] mob:px-3.5">
      <Link href="/" className="flex min-w-0 items-center gap-3">
        <span className="flex h-[26px] w-[26px] flex-none items-center justify-center rounded-[7px] bg-ink font-serif text-base text-ink-paper">
          T
        </span>
        <span className="font-serif text-xl tracking-[0.2px] text-ink mob:text-[17px]">ThriftYourStyle</span>
        <span className="rounded-[5px] border border-line px-[7px] py-0.5 text-[11px] uppercase tracking-[1.5px] text-dim mob:hidden">
          Demo
        </span>
      </Link>
      <span className="text-xs text-dim mob:hidden">Pipeline 4 agent · HITL</span>
    </header>
  );
}
