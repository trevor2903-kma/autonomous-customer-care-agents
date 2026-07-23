"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import type { RagInfo } from "shared-types";
import {
  type KnowledgeDocument,
  type ReindexResult,
  deleteRagDocument,
  getRagDocuments,
  getRagInfo,
  reindexRag,
  uploadKnowledgeDoc,
} from "@/lib/api";

// Console tri thức (P3). Đường nạp CHÍNH = "Nạp lại từ repo" (reset-and-reingest từ apps/backend/knowledge).
// Upload chỉ là AD-HOC: non-canonical, mất khi nạp lại. Doc canonical không xoá được ở đây (xoá file trong repo).

const TYPE_LABEL: Record<string, string> = {
  faq: "FAQ",
  case: "Tình huống",
  reference: "Tra cứu",
  promotion: "Khuyến mãi",
  upload: "Tải lên",
};

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return `${d.toLocaleDateString("vi-VN")} ${d.toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  })}`;
}

function DocRow({ doc, onDelete, deleting }: { doc: KnowledgeDocument; onDelete: () => void; deleting: boolean }) {
  return (
    <div className="flex items-center justify-between gap-3 px-[18px] py-3">
      <div className="flex min-w-0 flex-col gap-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[14px] font-medium text-ink">{doc.title}</span>
          <span className="rounded-[5px] border border-line bg-[#F6F3EC] px-1.5 py-0.5 text-[10.5px] font-medium text-dim">
            {TYPE_LABEL[doc.doc_type ?? ""] ?? doc.doc_type ?? "—"}
          </span>
          {!doc.canonical && (
            <span className="rounded-[5px] border border-gold/40 bg-gold/10 px-1.5 py-0.5 text-[10.5px] font-medium text-gold">
              tạm thời
            </span>
          )}
        </div>
        <span className="truncate font-mono text-[11.5px] text-dim">
          {doc.source}
          {doc.intent ? ` · ${doc.intent}` : ""}
        </span>
      </div>
      <div className="flex flex-none items-center gap-3">
        <span className="text-right text-[12px] text-faint">
          <span className="font-medium text-ink">{doc.chunks}</span> chunk
          <br />
          <span className="text-[11px]">{fmtDate(doc.indexed_at)}</span>
        </span>
        {!doc.canonical && (
          <button
            onClick={onDelete}
            disabled={deleting}
            className="rounded-[7px] border border-line px-2.5 py-1 text-[12px] text-dim transition-colors hover:border-terracotta-line hover:text-terracotta disabled:opacity-50"
          >
            Xoá
          </button>
        )}
      </div>
    </div>
  );
}

export function DocumentsPanel() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [selected, setSelected] = useState<File | null>(null);

  const docs = useQuery<KnowledgeDocument[], Error>({ queryKey: ["rag-documents"], queryFn: getRagDocuments });
  const info = useQuery<RagInfo, Error>({ queryKey: ["rag-info"], queryFn: getRagInfo });

  const refreshAll = () => {
    qc.invalidateQueries({ queryKey: ["rag-documents"] });
    qc.invalidateQueries({ queryKey: ["rag-info"] });
  };

  const reindex = useMutation<ReindexResult, Error, void>({ mutationFn: reindexRag, onSuccess: refreshAll });
  const remove = useMutation<KnowledgeDocument, Error, string>({
    mutationFn: deleteRagDocument,
    onSuccess: refreshAll,
  });
  const upload = useMutation({
    mutationFn: uploadKnowledgeDoc,
    onSuccess: () => {
      refreshAll();
      setSelected(null);
      if (fileRef.current) fileRef.current.value = "";
    },
  });

  const err = reindex.error ?? remove.error ?? upload.error ?? docs.error;

  return (
    <section className="overflow-hidden rounded-[12px] border border-line bg-white shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line-soft px-[18px] py-3.5">
        <div className="min-w-0">
          <h2 className="text-[14px] font-semibold text-ink">Tài liệu tri thức</h2>
          <p className="mt-0.5 text-[12.5px] leading-[1.5] text-faint">
            Nguồn chân lý là thư mục <code className="font-mono text-[11.5px]">knowledge/</code> trong repo —
            sửa file <code className="font-mono text-[11.5px]">.md</code> rồi nạp lại.
          </p>
        </div>
        <button
          onClick={() => {
            if (window.confirm("Nạp lại toàn bộ từ repo? Tài liệu tải lên tạm thời sẽ mất.")) reindex.mutate();
          }}
          disabled={reindex.isPending}
          className="flex-none rounded-[8px] bg-olive px-3.5 py-2 text-[13px] font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {reindex.isPending ? "Đang nạp…" : "Nạp lại từ repo"}
        </button>
      </div>

      {info.data && (
        <div className="border-b border-line-soft bg-[#FBFAF7] px-[18px] py-2.5 text-[12.5px] text-faint">
          Collection <code className="font-mono text-[11.5px] text-dim">{info.data.collection}</code> ·{" "}
          <span className="font-medium text-ink">{info.data.points_count}</span> point ·{" "}
          <span className="font-medium text-ink">{docs.data?.length ?? 0}</span> tài liệu
        </div>
      )}

      {docs.isLoading && <p className="px-[18px] py-4 text-[13px] text-dim">Đang tải tài liệu…</p>}
      {docs.data?.length === 0 && (
        <p className="px-[18px] py-4 text-[13px] text-dim">
          Chưa có tài liệu nào được index — bấm “Nạp lại từ repo”.
        </p>
      )}

      <div className="divide-y divide-line-soft">
        {docs.data?.map((d) => (
          <DocRow
            key={d.id}
            doc={d}
            deleting={remove.isPending && remove.variables === d.id}
            onDelete={() => {
              if (window.confirm(`Xoá tài liệu tạm thời “${d.title}”?`)) remove.mutate(d.id);
            }}
          />
        ))}
      </div>

      {/* Upload AD-HOC — non-canonical */}
      <div className="border-t border-line-soft bg-[#FBFAF7] px-[18px] py-3.5">
        <div className="flex flex-wrap items-center gap-3">
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            onChange={(e) => setSelected(e.target.files?.[0] ?? null)}
            className="max-w-full text-[12.5px] text-dim"
          />
          <button
            onClick={() => selected && upload.mutate(selected)}
            disabled={!selected || upload.isPending}
            className="rounded-[8px] border border-line px-3 py-1.5 text-[13px] font-medium text-ink transition-colors hover:bg-[#F2EFE8] disabled:opacity-50"
          >
            {upload.isPending ? "Đang nạp…" : "Tải lên tạm thời"}
          </button>
        </div>
        <p className="mt-1.5 text-[12px] leading-[1.5] text-dim">
          .pdf · .docx · .txt · .md — không có frontmatter nên không gắn được intent, và sẽ mất khi nạp lại
          từ repo. Tri thức lâu dài hãy thêm file vào <code className="font-mono text-[11.5px]">knowledge/</code>.
        </p>
      </div>

      {err && <p className="border-t border-line-soft px-[18px] py-2.5 text-[12.5px] text-terracotta">Lỗi: {err.message}</p>}
      {reindex.data && (
        <p className="border-t border-line-soft px-[18px] py-2.5 text-[12.5px] text-olive">
          Đã nạp {reindex.data.documents} tài liệu → {reindex.data.points} point.
        </p>
      )}
    </section>
  );
}
