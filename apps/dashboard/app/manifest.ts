import type { MetadataRoute } from "next";

// PWA manifest — Next.js App Router sinh /manifest.webmanifest và tự chèn <link rel="manifest">.
// Cho phép cài web lên màn hình chính (Add to Home Screen). PRD §6/§16: web là PWA, không codebase mobile riêng.
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Autonomous Customer Support — Admin",
    short_name: "ACSS Admin",
    description: "Bảng điều hành CSKH + cổng chat khách — Multi-Agent AI",
    start_url: "/",
    display: "standalone",
    background_color: "#fafafa",
    theme_color: "#171717",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
  };
}
