/*
 * Service worker TỐI GIẢN cho PWA (đăng ký chỉ ở production — xem app/PWARegister.tsx).
 * Nguyên tắc: KHÔNG cache /api/*, cross-origin (backend :8000, WebSocket), hay non-GET → luôn network
 * (tránh dữ liệu cũ). Chỉ precache app shell tĩnh; điều hướng dùng network-first + fallback cache khi offline.
 */
const CACHE = "acss-shell-v1";
const SHELL = ["/", "/chat", "/manifest.webmanifest", "/icon-192.png", "/icon-512.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      // allSettled: một URL lỗi không làm hỏng cả bước install.
      .then((cache) => Promise.allSettled(SHELL.map((url) => cache.add(url))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Chỉ xử lý GET cùng origin. API + non-GET + cross-origin → để trình duyệt tự network (không cache).
  if (
    request.method !== "GET" ||
    url.origin !== self.location.origin ||
    url.pathname.startsWith("/api/")
  ) {
    return;
  }

  // App shell: network-first (dữ liệu tươi khi online), fallback cache khi offline.
  event.respondWith(
    fetch(request).catch(() =>
      caches.match(request).then((cached) => cached || caches.match("/"))
    )
  );
});
