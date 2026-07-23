import { AnalyzePanel } from "@/components/rag/AnalyzePanel";
import { ClassifyTester } from "@/components/rag/ClassifyTester";
import { DocumentsPanel } from "@/components/rag/DocumentsPanel";

// Module Quản lý tri thức (RAG) trong vỏ admin (slice 11 P5) — PRD §17 Module 1.
// Chuyển từ route riêng /rag vào cụm nav admin; khung + cuộn do AdminShell cấp.
export default function KnowledgePage() {
  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-8 mob:px-4">
      <header className="mb-6">
        <h1 className="font-serif text-[27px] text-ink">Quản lý tri thức</h1>
        <p className="mt-1 text-sm text-faint">
          Kho tri thức cho Agent 2 (chính sách/FAQ/sản phẩm) → embed Qdrant · test Agent 1 (intent) &amp;
          Agent 2 (truy hồi)
        </p>
      </header>

      <div className="grid gap-6">
        <DocumentsPanel />
        <ClassifyTester />
        <AnalyzePanel />
      </div>
    </div>
  );
}
