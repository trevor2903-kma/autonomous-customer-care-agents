"use client";

import React from "react";

interface PaginationProps {
  page: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  pageSizeOptions?: number[];
  onPageChange: (newPage: number) => void;
  onPageSizeChange: (newPageSize: number) => void;
}

export function Pagination({
  page,
  totalPages,
  totalItems,
  pageSize,
  pageSizeOptions = [5, 10, 15, 20],
  onPageChange,
  onPageSizeChange,
}: PaginationProps) {
  if (totalItems <= 0) return null;

  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, totalItems);

  // Generate page numbers with ellipsis for large number of pages
  const getPageNumbers = () => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const pages: (number | "ellipsis")[] = [];
    pages.push(1);

    if (page > 3) {
      pages.push("ellipsis");
    }

    const start = Math.max(2, page - 1);
    const end = Math.min(totalPages - 1, page + 1);

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    if (page < totalPages - 2) {
      pages.push("ellipsis");
    }

    pages.push(totalPages);
    return pages;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_auto_1fr] sm:items-center px-[18px] py-3 text-[12.5px] text-muted border-t border-line-soft bg-cream-soft/30">
      {/* Cột trái: Ô select số lượt nằm ngoài cùng bên trái */}
      <div className="flex items-center gap-2">
        <label htmlFor="pagination-page-size" className="text-faint text-[12px]">
          Số lượt/trang:
        </label>
        <select
          id="pagination-page-size"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="cursor-pointer rounded-[7px] border border-line bg-white px-2.5 py-1 text-[12px] font-medium text-ink shadow-sm transition-colors hover:border-dim focus:border-olive focus:outline-none focus:ring-1 focus:ring-olive"
        >
          {pageSizeOptions.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>

      {/* Cột giữa: Phần phân trang nằm ở giữa */}
      <div className="flex justify-center">
        {totalPages > 1 && (
          <nav aria-label="Phân trang" className="flex items-center gap-1">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
              className="inline-flex h-7 min-w-[28px] items-center justify-center rounded-[6px] border border-line bg-white px-2 text-[12px] font-medium text-ink transition-colors hover:bg-cream disabled:pointer-events-none disabled:opacity-40"
              aria-label="Trang trước"
            >
              ‹
            </button>

            {pageNumbers.map((p, idx) => {
              if (p === "ellipsis") {
                return (
                  <span key={`ellipsis-${idx}`} className="px-1 text-dim">
                    …
                  </span>
                );
              }
              const isActive = p === page;
              return (
                <button
                  key={p}
                  type="button"
                  onClick={() => onPageChange(p)}
                  aria-current={isActive ? "page" : undefined}
                  className={`inline-flex h-7 min-w-[28px] items-center justify-center rounded-[6px] px-2 text-[12px] font-medium transition-colors ${
                    isActive
                      ? "border border-ink bg-ink text-white"
                      : "border border-line bg-white text-muted hover:bg-cream"
                  }`}
                >
                  {p}
                </button>
              );
            })}

            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
              className="inline-flex h-7 min-w-[28px] items-center justify-center rounded-[6px] border border-line bg-white px-2 text-[12px] font-medium text-ink transition-colors hover:bg-cream disabled:pointer-events-none disabled:opacity-40"
              aria-label="Trang sau"
            >
              ›
            </button>
          </nav>
        )}
      </div>

      {/* Cột phải: Giữ cân bằng cột giữa */}
      <div className="hidden sm:block" />
    </div>
  );
}
