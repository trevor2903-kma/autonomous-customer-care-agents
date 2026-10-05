"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";

// Toast góc phải dưới cho kết quả thao tác (đóng ca, tải lên / xoá tài liệu). Hai trạng thái: thành công / thất bại.
// Context chỉ mang API ổn định (success/error/dismiss) → component gọi toast KHÔNG render lại mỗi khi danh sách đổi.

type ToastVariant = "success" | "error";

interface ToastItem {
  id: number;
  variant: ToastVariant;
  title: string;
  description?: string;
}

interface ToastApi {
  success: (title: string, description?: string) => void;
  error: (title: string, description?: string) => void;
  dismiss: (id: number) => void;
}

// Lỗi ở lâu hơn để kịp đọc lý do (vd 409 "ca do nhân viên khác giữ").
const DURATION_MS: Record<ToastVariant, number> = { success: 4000, error: 7000 };
const MAX_VISIBLE = 4;

const ToastContext = createContext<ToastApi | null>(null);

export function useToast(): ToastApi {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast phải dùng bên trong <ToastProvider>");
  return ctx;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const seqRef = useRef(0);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback((variant: ToastVariant, title: string, description?: string) => {
    const id = ++seqRef.current;
    // Quá MAX_VISIBLE → bỏ cái cũ nhất, không để chồng kín màn hình.
    setToasts((prev) => [...prev, { id, variant, title, description }].slice(-MAX_VISIBLE));
  }, []);

  const api = useMemo<ToastApi>(
    () => ({
      success: (title, description) => push("success", title, description),
      error: (title, description) => push("error", title, description),
      dismiss,
    }),
    [push, dismiss],
  );

  return (
    <ToastContext.Provider value={api}>
      {children}
      {/* z trên modal (50) và drawer mobile (70). Vùng aria-live luôn có mặt để trình đọc màn hình bắt được toast mới. */}
      <div
        aria-live="polite"
        className="pointer-events-none fixed bottom-[max(16px,env(safe-area-inset-bottom))] right-4 z-[80] flex w-[360px] max-w-[calc(100vw-32px)] flex-col gap-2.5"
      >
        {toasts.map((t) => (
          <ToastCard key={t.id} toast={t} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastCard({ toast, onDismiss }: { toast: ToastItem; onDismiss: (id: number) => void }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), DURATION_MS[toast.variant]);
    return () => clearTimeout(timer);
  }, [toast.id, toast.variant, onDismiss]);

  const isError = toast.variant === "error";

  return (
    <div
      role={isError ? "alert" : "status"}
      className={`animate-toast-in pointer-events-auto flex items-start gap-3 rounded-[12px] border border-l-[3px] bg-white py-3 pl-3 pr-2.5 shadow-drawer ${
        isError ? "border-terracotta-line border-l-terracotta" : "border-line border-l-sage"
      }`}
    >
      <div
        className={`flex h-8 w-8 flex-none items-center justify-center rounded-full ${
          isError ? "bg-terracotta-soft text-terracotta" : "bg-sage-soft text-sage"
        }`}
      >
        {isError ? <ErrorIcon /> : <SuccessIcon />}
      </div>
      <div className="min-w-0 flex-1 pt-[5px]">
        <p className="text-[13.5px] font-semibold leading-[1.35] text-ink">{toast.title}</p>
        {toast.description && (
          <p className="mt-1 break-words text-[12.5px] leading-[1.5] text-muted">{toast.description}</p>
        )}
      </div>
      <button
        type="button"
        onClick={() => onDismiss(toast.id)}
        aria-label="Đóng thông báo"
        className="flex-none rounded-lg p-1 text-faint transition-colors hover:bg-cream hover:text-ink"
      >
        <CloseIcon />
      </button>
    </div>
  );
}

function SuccessIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <line x1="12" y1="7" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
