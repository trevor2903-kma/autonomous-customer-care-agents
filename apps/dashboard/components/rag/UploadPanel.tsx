"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import type { RagInfo, RagUploadResult } from "shared-types";
import { getRagInfo, resetRag, uploadKnowledgeDoc } from "@/lib/api";

// Quản lý tri thức RAG (PRD §17 Module 1): upload tài liệu → embed Qdrant; xem chunk/nguồn; reset.
export function UploadPanel() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [selected, setSelected] = useState<File | null>(null);

  const info = useQuery<RagInfo>({ queryKey: ["rag-info"], queryFn: getRagInfo });

  const upload = useMutation<RagUploadResult, Error, File>({
    mutationFn: uploadKnowledgeDoc,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["rag-info"] });
      setSelected(null);
      if (fileRef.current) fileRef.current.value = "";
    },
  });

  const reset = useMutation<RagInfo, Error, void>({
    mutationFn: resetRag,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rag-info"] }),
  });

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
        Quản lý tri thức (RAG)
      </h2>
      <p className="mb-3 mt-1 text-xs text-neutral-400">
        Tài liệu <span className="font-medium text-neutral-500">Agent 2</span> truy hồi để trả lời (không
        phải tài liệu phân loại intent).
      </p>

      <div className="flex flex-wrap items-center gap-3">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          onChange={(e) => setSelected(e.target.files?.[0] ?? null)}
          className="text-sm"
        />
        <button
          onClick={() => selected && upload.mutate(selected)}
          disabled={!selected || upload.isPending}
          className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-neutral-700 disabled:opacity-50"
        >
          {upload.isPending ? "Đang nạp…" : "Upload"}
        </button>
        <button
          onClick={() => {
            if (window.confirm("Xoá toàn bộ vector trong collection?")) reset.mutate();
          }}
          disabled={reset.isPending}
          className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100 disabled:opacity-50"
        >
          {reset.isPending ? "Đang reset…" : "Reset"}
        </button>
      </div>
      <p className="mt-1 text-xs text-neutral-400">Định dạng: .pdf · .docx · .txt · .md</p>

      {upload.isError && (
        <p className="mt-2 text-sm text-red-500">Lỗi upload: {upload.error.message}</p>
      )}
      {upload.data && (
        <p className="mt-2 text-sm text-green-700">
          Đã nạp <strong>{upload.data.chunks}</strong> chunk từ <code>{upload.data.source}</code>.
        </p>
      )}

      <div className="mt-3 rounded-md bg-neutral-50 p-3 text-sm">
        {info.isLoading && <span className="text-neutral-400">Đang tải thông tin collection…</span>}
        {info.isError && (
          <span className="text-red-500">Không tải được collection — backend chạy chưa?</span>
        )}
        {info.data && (
          <div>
            <div>
              Collection <code>{info.data.collection}</code> ·{" "}
              <strong>{info.data.points_count}</strong> chunk · {info.data.sources.length} nguồn
            </div>
            {info.data.sources.length > 0 && (
              <ul className="mt-1 list-disc pl-5 text-neutral-600">
                {info.data.sources.map((s) => (
                  <li key={s}>
                    <code>{s}</code>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
