import type { MetadataRoute } from "next";

// PWA manifest — Next.js App Router sinh /manifest.webmanifest và tự chèn <link rel="manifest">.
// Cho phép cài web lên màn hình chính (Add to Home Screen). PRD §6/§16: web là PWA, không codebase mobile riêng.
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "ThriftYourStyle — Chăm sóc khách hàng",
    short_name: "ThriftYourStyle",
    description: "Bảng điều hành CSKH + cổng chat khách — Multi-Agent AI",
    start_url: "/",
    display: "standalone",
    // Khớp bảng màu design (§2) thay vì màu xám mặc định của scaffold.
    background_color: "#FBFAF7",
    theme_color: "#F9F7E7",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
