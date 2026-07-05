import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { PWARegister } from "./PWARegister";

export const metadata: Metadata = {
  title: "ACSS — Admin Dashboard (scaffold)",
  description: "Autonomous Customer Support System — Multi-Agent AI",
  manifest: "/manifest.webmanifest",
  appleWebApp: { capable: true, title: "ACSS Admin", statusBarStyle: "default" },
  icons: { icon: "/icon-192.png", apple: "/icon-192.png" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#171717",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>
        <Providers>{children}</Providers>
        <PWARegister />
      </body>
    </html>
  );
}
