import { DocumentsPanel } from "@/components/rag/DocumentsPanel";

// Module Quản lý tri thức (RAG) trong vỏ admin — PRD §17 Module 1.
// Hai panel dev ("Test Agent 1" + "Pipeline Inspector") đã GỠ ở slice obs P4: việc quan sát pipeline
// nay là của tab Báo cáo, chạy trên lượt THẬT của khách thay vì câu test single-shot.
export default function KnowledgePage() {
  return (
    <div className="mx-auto w-full max-w-4xl px-8 pb-12 pt-7 mob:px-4">
      <header className="mb-6">
        <h1 className="font-serif text-[27px] text-ink">Quản lý tri thức</h1>
        <p className="mt-1.5 max-w-[620px] text-[13.5px] leading-[1.55] text-faint">
          Tài liệu được tách đoạn → tạo vector → lưu vào kho tri thức, làm căn cứ cho phản hồi tự động.
        </p>
      </header>

      <DocumentsPanel />
    </div>
  );
}
