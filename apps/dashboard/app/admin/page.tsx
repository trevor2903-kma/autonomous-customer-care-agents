// Pane chi tiết khi CHƯA chọn hội thoại. Danh sách nằm ở AdminShell (two-pane như design);
// trên mobile route /admin chỉ hiện danh sách nên trang này không xuất hiện.
export default function AdminIndexPage() {
  return (
    <div className="flex flex-1 items-center justify-center bg-panel px-6">
      <div className="max-w-sm text-center">
        <p className="font-serif text-[22px] text-ink">Chọn một hội thoại</p>
        <p className="mt-2 text-sm leading-relaxed text-faint">
          Chọn ca ở danh sách bên trái để xem toàn bộ lịch sử, EscalationCard và tiếp quản khi cần.
        </p>
      </div>
    </div>
  );
}
