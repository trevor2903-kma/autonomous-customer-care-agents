import { statusMeta } from "./status";

// Pill trạng thái (design): chấm màu + nhãn, nền mềm cùng tông. Màu theo dữ liệu → dùng inline style.
export function StatusPill({ status, size = "sm" }: { status?: string | null; size?: "sm" | "md" }) {
  const m = statusMeta(status);
  const cls =
    size === "md" ? "gap-1.5 rounded-[7px] px-[11px] py-[5px] text-[12.5px]" : "gap-1.5 rounded-md px-[9px] py-[3px] text-[11.5px]";
  return (
    <span
      className={`inline-flex items-center whitespace-nowrap ${cls}`}
      style={{ color: m.color, background: m.soft }}
    >
      <span
        className={size === "md" ? "h-[7px] w-[7px] rounded-full" : "h-1.5 w-1.5 rounded-full"}
        style={{ background: m.color }}
      />
      {m.label}
    </span>
  );
}
