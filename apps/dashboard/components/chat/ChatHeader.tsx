import { CUST_STATUS, type CustStatus } from "./custStatus";

// Header màn khách (design): avatar "T" olive + tên trợ lý (serif) + chấm trạng thái.
// KHÔNG có link sang admin — khách và bảng điều hành là hai URL tách biệt.
export function ChatHeader({ status }: { status: CustStatus }) {
  const s = CUST_STATUS[status];
  return (
    <div className="flex items-center gap-[13px]">
      <span className="flex h-10 w-10 flex-none items-center justify-center rounded-[11px] border border-line-olive bg-olive-soft font-serif text-xl text-olive-dark">
        T
      </span>
      <div>
        <div className="font-serif text-[22px] leading-[1.1] text-ink">Trợ lý ThriftYourStyle</div>
        <div className="mt-[3px] flex items-center gap-[7px]">
          <span className={`h-[7px] w-[7px] rounded-full ${s.dot}`} />
          <span className="text-[13px] text-faint">{s.label}</span>
        </div>
      </div>
    </div>
  );
}
