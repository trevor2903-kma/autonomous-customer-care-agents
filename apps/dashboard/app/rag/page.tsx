import Link from "next/link";
import { ClassifyTester } from "@/components/rag/ClassifyTester";
import { UploadPanel } from "@/components/rag/UploadPanel";

// Trang Quản lý tri thức (RAG) — PRD §17 Module 1. Upload tài liệu + test phân loại intent/entities.
export default function RagPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="mb-8 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Quản lý tri thức (RAG)</h1>
          <p className="text-sm text-neutral-500">
            Upload tài liệu (.pdf/.docx/.txt/.md) → embed Qdrant · test phân loại intent + entities
          </p>
        </div>
        <Link
          href="/"
          className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-100"
        >
          ← Dashboard
        </Link>
      </header>

      <div className="grid gap-6">
        <UploadPanel />
        <ClassifyTester />
      </div>
    </main>
  );
}
