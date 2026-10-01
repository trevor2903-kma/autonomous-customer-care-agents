type ScrollToLatestButtonProps = {
  visible: boolean;
  onClick: () => void;
};

/** Nút nổi đưa người dùng về tin nhắn mới nhất khi đang đọc phần lịch sử phía trên. */
export function ScrollToLatestButton({ visible, onClick }: ScrollToLatestButtonProps) {
  if (!visible) return null;

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label="Cuộn đến tin nhắn mới nhất"
      title="Tin nhắn mới nhất"
      className="absolute bottom-3 left-1/2 z-10 flex h-10 w-10 -translate-x-1/2 items-center justify-center rounded-full border border-olive-dark bg-olive text-white shadow-[0_5px_18px_rgba(33,31,27,.20)] transition-colors hover:bg-olive-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-olive focus-visible:ring-offset-2"
    >
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M12 4v15" />
        <path d="m6.5 13.5 5.5 5.5 5.5-5.5" />
      </svg>
    </button>
  );
}
