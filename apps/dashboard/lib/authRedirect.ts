// Quay lại đúng trang sau khi đăng nhập (lại): RequireAuth gắn `?next=` khi đưa về /login, trang login đọc nó.
// KHÔNG import runtime nào → test Node trực tiếp (authRedirect.test.mts).

function homeFor(role: string): string {
  return role === "admin" ? "/admin" : "/chat";
}

/** URL /login mang theo trang đang mở. Trang gốc / chính /login → không mang `next`. */
export function loginUrl(current: string): string {
  if (current === "/" || current.startsWith("/login")) return "/login";
  return `/login?next=${encodeURIComponent(current)}`;
}

/** Đích sau đăng nhập: `next` nằm trong khu vực của vai (admin → /admin…, khách → /chat…) → về đó; còn lại (thiếu,
 *  link ngoài như `//evil.com`, khu vực của vai khác) → trang mặc định của vai. */
export function afterLoginPath(next: string | null, role: string): string {
  const home = homeFor(role);
  if (next && (next === home || next.startsWith(`${home}/`) || next.startsWith(`${home}?`))) return next;
  return home;
}
