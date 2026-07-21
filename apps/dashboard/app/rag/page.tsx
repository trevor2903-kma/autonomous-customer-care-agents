import { redirect } from "next/navigation";

// RAG đã chuyển vào cụm nav admin (slice 11 P5). Giữ /rag làm redirect cho link/bookmark cũ.
export default function RagRedirect() {
  redirect("/admin/knowledge");
}
