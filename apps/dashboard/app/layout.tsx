import type { Metadata, Viewport } from "next";
import { Be_Vietnam_Pro, Playfair_Display } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { PWARegister } from "./PWARegister";
import { TopBar } from "@/components/shell/TopBar";

// Hệ chữ ThriftYourStyle (docs/design): serif hiển thị cho brand/heading, sans cho body/UI.
// THAY font gốc của design (Instrument Serif/Sans) vì cả hai KHÔNG có subset `vietnamese` —
// chữ có dấu (ộ, ế, ạ, ữ…) sẽ rơi sang font hệ thống GIỮA từ. Cặp thay thế giữ đúng vai trò thị giác:
// Playfair Display = serif tương phản cao (thay Instrument Serif); Be Vietnam Pro = sans dựng RIÊNG cho tiếng Việt.
const sans = Be_Vietnam_Pro({
  subsets: ["latin", "latin-ext", "vietnamese"],
  weight: ["400", "500", "600"],
  variable: "--font-sans",
  display: "swap",
});

const serif = Playfair_Display({
  subsets: ["latin", "latin-ext", "vietnamese"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-serif",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ThriftYourStyle — Chăm sóc khách hàng",
  description: "Hệ thống chăm sóc khách hàng tự trị — Multi-Agent AI",
  manifest: "/manifest.webmanifest",
  appleWebApp: { capable: true, title: "ThriftYourStyle CSKH", statusBarStyle: "default" },
  icons: { icon: "/icon-192.png", apple: "/icon-192.png" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#FBFAF7",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={`${sans.variable} ${serif.variable}`}>
      <body className="font-sans">
        <Providers>
          {/* Vỏ app (design): cột dọc 100vh — top bar 53px + vùng nội dung co giãn. */}
          <div className="flex min-h-screen flex-col bg-page">
            <TopBar />
            {children}
          </div>
        </Providers>
        <PWARegister />
      </body>
    </html>
  );
}
