"use client";

import React, { useEffect } from "react";

export interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  message: React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "warning" | "olive" | "default";
  isLoading?: boolean;
}

function WarningIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="16" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12.01" y2="8" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title = "Xác nhận hành động",
  message,
  confirmText = "Đồng ý",
  cancelText = "Hủy",
  variant = "danger",
  isLoading = false,
}: ConfirmModalProps) {
  // Đóng khi nhấn phím Escape
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isLoading) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isLoading, onClose]);

  // Khóa cuộn trang nền khi mở modal
  useEffect(() => {
    if (!isOpen) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prevOverflow;
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const isDanger = variant === "danger";
  const isOlive = variant === "olive";
  const isWarning = variant === "warning";

  const iconBg = isDanger
    ? "bg-terracotta-soft text-terracotta"
    : isWarning
      ? "bg-gold-soft text-gold"
      : isOlive
        ? "bg-olive-soft text-olive"
        : "bg-steel-soft text-steel";

  const confirmBtnBg = isDanger
    ? "bg-terracotta hover:opacity-90 text-white"
    : isOlive
      ? "bg-olive hover:bg-olive-dark text-white"
      : isWarning
        ? "bg-gold hover:opacity-90 text-white"
        : "bg-ink hover:bg-ink-2 text-white";

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4 backdrop-blur-[2px] transition-all"
      onClick={() => {
        if (!isLoading) onClose();
      }}
    >
      <div
        className="relative w-full max-w-[420px] rounded-[16px] border border-line bg-panel p-5 shadow-drawer"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-3.5">
          <div className={`flex h-10 w-10 flex-none items-center justify-center rounded-full ${iconBg}`}>
            {isDanger || isWarning ? <WarningIcon /> : <InfoIcon />}
          </div>

          <div className="min-w-0 flex-1 pt-0.5">
            <h3 id="confirm-modal-title" className="text-[15.5px] font-semibold text-ink">
              {title}
            </h3>
            <div className="mt-1.5 text-[13px] leading-relaxed text-muted">
              {message}
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            aria-label="Đóng"
            className="flex-none rounded-lg p-1 text-faint transition-colors hover:bg-cream hover:text-ink disabled:opacity-50"
          >
            <CloseIcon />
          </button>
        </div>

        <div className="mt-5 flex items-center justify-end gap-2.5 border-t border-line-soft pt-3.5">
          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            className="rounded-[9px] border border-line bg-white px-4 py-2 text-[13px] font-medium text-muted transition-colors hover:bg-cream hover:text-ink disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isLoading}
            className={`inline-flex items-center gap-1.5 rounded-[9px] px-4 py-2 text-[13px] font-semibold shadow-sm transition-all disabled:opacity-50 ${confirmBtnBg}`}
          >
            {isLoading && (
              <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
            )}
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
