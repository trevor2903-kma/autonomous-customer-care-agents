"use client";

import { useEffect } from "react";

// Đăng ký service worker CHỈ ở production — tránh SW phá hot-reload khi dev.
// SW là tiến bộ tăng cường (progressive enhancement): lỗi thì bỏ qua, app vẫn chạy.
export function PWARegister() {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production") return;
    if (!("serviceWorker" in navigator)) return;
    navigator.serviceWorker.register("/sw.js").catch(() => {
      /* bỏ qua: không có SW thì vẫn là web bình thường */
    });
  }, []);

  return null;
}
