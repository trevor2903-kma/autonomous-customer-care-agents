# SLICE — Cập nhật repo: bỏ React Native, chuyển sang PWA · plan one-shot

> **Bản chất:** plan ONE-SHOT cho một lát refactor + đồng bộ tài liệu. Xong thì bỏ. Nguồn chân lý: **`PRD.md`**.
> **Quyết định:** bỏ hẳn app mobile React Native (Expo). "App trên điện thoại" giờ là **web dashboard dạng PWA**
> (cài lên màn hình chính) — một codebase web duy nhất, responsive; không duy trì codebase mobile riêng.
> **Lý do:** nhu cầu trên điện thoại chỉ là Admin xem hội thoại + duyệt/nhận ca chuyển tiếp nhanh khi di chuyển,
> không cần truy cập phần cứng/OS → PWA đủ, giảm một codebase. Tuân thủ `CLAUDE.md`.

> **Lưu ý repo:** đây là hệ **CSKH shop quần áo** (Admin/nhân viên CSKH, khách hàng, RAG chính sách). Web hiện có
> 2 trang: `/` (Admin dashboard) và `/chat` (cổng chat khách). PRD của repo này đánh số: **§1.3** bối cảnh,
> **§6** kiến trúc, **§11** human_handoff + EscalationCard (mobile = FR-ESC-3), **§14.5** thông báo (FR-NOTI),
> **§16** bảng Web vs Mobile, **§21** tech stack, **§22** ngoài phạm vi/tương lai.

---

## 1. In scope / Out of scope

**In scope:**

- Gỡ bỏ `apps/mobile` (Expo/React Native) khỏi monorepo + mọi tham chiếu build/script.
- Biến `apps/dashboard` (Next.js) thành **PWA cài được**: web app manifest + service worker tối giản + icon.
- Đảm bảo các trang hiện có (`/`, `/chat`) responsive tốt trên khổ điện thoại.
- Cập nhật MỌI tài liệu nhắc tới mobile: `PRD.md`, `CLAUDE.md`, `docs/architecture.md`, `README.md`.
- Cập nhật cấu hình monorepo: `pnpm-workspace.yaml`, root `package.json`, `Makefile`, `.npmrc`, `.gitignore`,
  comment `packages/shared-types`.

**Out of scope (KHÔNG làm ở lát này):**

- KHÔNG làm push notification thật (đưa vào PRD §22 tương lai — iOS hạn chế PWA push; Phase 1 dùng badge in-app
  + realtime WebSocket thay thế).
- KHÔNG đụng backend, agent/node, logic nghiệp vụ. (Ngoại lệ đề xuất: 2 comment CORS trong backend còn nhắc
  "Expo web" — chỉ FLAG cho người dùng, KHÔNG tự sửa vì ranh giới "không đụng backend".)
- KHÔNG đổi tên `apps/dashboard` (giữ tên, tránh churn; nó là app web duy nhất: cổng chat khách + Admin + PWA).
- KHÔNG đổi `node-linker=hoisted` / phiên bản React (tránh churn cài đặt/rủi ro build) — chỉ dọn comment nhắc Expo.

---

## 2. Gỡ bỏ app mobile

- Xóa thư mục `apps/mobile/`.
- `pnpm-workspace.yaml`: bỏ mục `apps/mobile` + comment nhắc Expo.
- Root `package.json`: bỏ script `dev:mobile`.
- `Makefile`: bỏ target `dev-mobile` + `dev-mobile-web` (.PHONY, help echo, recipe); sửa comment header
  "Frontend/mobile" → "Frontend".
- `.npmrc`: giữ `node-linker=hoisted` + `enable-pre-post-scripts` (tránh churn), chỉ dọn comment nhắc Expo/RN/Metro.
- `.gitignore`: dọn comment "Expo" + bỏ dòng `.expo/`, `.expo-shared/` (không còn Expo).
- `packages/shared-types`: GIỮ NGUYÊN type (dashboard vẫn dùng). Chỉ sửa comment "backend ↔ dashboard ↔ mobile"
  → "backend ↔ dashboard" (không có type nào chỉ dành riêng cho mobile).
- Chạy `pnpm install` lại để cập nhật lockfile sau khi bỏ workspace.
- **FLAG (không sửa):** `apps/backend/app/main.py` + `app/core/config.py` còn comment ví dụ "Expo web :8081/:19006"
  trong CORS regex — báo người dùng, để họ quyết (ranh giới: không đụng backend).

## 3. Biến dashboard thành PWA (tối giản, không thư viện nặng)

Ưu tiên cách thủ công gọn, tránh phụ thuộc dễ vỡ (KHÔNG `next-pwa`):

- **Manifest:** thêm `app/manifest.ts` (Next.js App Router sinh ra `/manifest.webmanifest`): `name`,
  `short_name`, `start_url: "/"`, `display: "standalone"`, `background_color`, `theme_color`, `icons` (192, 512).
  App Router tự chèn `<link rel="manifest">`.
- **Icon:** sinh icon placeholder đơn giản (ô vuông màu neutral + vòng tròn) kích thước 192×192 và 512×512 vào
  `public/` (PNG). Không dùng thư viện nặng — sinh bằng script Node một lần (không commit script).
- **Service worker:** thêm `public/sw.js` TỐI GIẢN — precache app shell (`/`, `/chat`, manifest, icon);
  request `/api/*`, cross-origin (backend :8000, WebSocket) và non-GET → **network (không cache)** tránh dữ liệu
  cũ. Shell: network-first + fallback cache khi offline. Không cần chiến lược caching phức tạp.
- **Đăng ký SW:** client component `app/PWARegister.tsx` (thêm vào `app/layout.tsx`), đăng ký `sw.js` **chỉ ở
  production** (`process.env.NODE_ENV === "production"`) để tránh SW phá hot-reload khi dev.
- **Meta:** thêm `export const viewport` (`themeColor` + `width=device-width`) + `metadata.manifest`
  (+ `appleWebApp`/apple-touch-icon cho iOS "Add to Home Screen").
- **Responsive:** rà `/` và `/chat` hiển thị tốt trên khổ điện thoại (không tràn ngang, chạm được); chỉ chỉnh
  tối thiểu nếu thật sự tràn.

> Ghi chú: PWA cài được cần HTTPS ở production (localhost dev thì OK). Không xử lý gì thêm ở lát này.

## 4. Cập nhật tài liệu (đồng bộ — quan trọng)

| File                   | Sửa gì                                                                                                                                                                        |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PRD.md`               | §1.3, §6, §11 (FR-ESC-3), §14.5 (FR-NOTI-2), §16 (bảng), §21 (stack), §22 — đổi "Mobile Admin (React Native/Expo)" → "trên điện thoại: web PWA"; đưa push thật vào §22. Wording dưới. |
| `CLAUDE.md`            | Mục stack: "Mobile: React Native / Expo…" → "Điện thoại (PWA): web dashboard cài được lên màn hình chính cho Admin (không codebase mobile riêng)". Bỏ mọi nhắc React Native/Expo.     |
| `docs/architecture.md` | Bảng thành phần: bỏ dòng "Mobile (Expo)"; dòng Web ghi rõ là PWA cài được. Không còn nhắc `apps/mobile`.                                                                       |
| `README.md`            | Bỏ `make dev-mobile`/`dev-mobile-web` + ghi chú Expo/Metro/duplicate-React; xóa `apps/mobile` khỏi cây thư mục; thêm dòng "web là PWA, cài trên điện thoại qua Add to Home Screen".  |

**Wording mới cho các mục PRD (áp đúng, không tự chế thêm):**

- §1.3: "Trên điện thoại, chính web này (dạng PWA cài được lên màn hình chính) cho Admin xử lý nhanh hội thoại
  được chuyển tiếp khi di chuyển."
- §6: "Trên điện thoại (PWA): chính Web Admin ở trên, cài lên màn hình chính — Admin xem danh sách hội thoại +
  duyệt/nhận ca chuyển tiếp nhanh. Một app web duy nhất, responsive; KHÔNG có codebase mobile riêng."
- §11 FR-ESC-3: "FR-ESC-3 (trên điện thoại — PWA): bản rút gọn responsive của EscalationCard (tóm tắt + intent +
  lý do + nháp + nút Nhận) để xử lý nhanh. Thông báo: badge số ca chờ hiển thị trong app. (Web push đẩy thật
  xuyên nền tảng: xem §22.)"
- §14.5 FR-NOTI-2: "FR-NOTI-2: thông báo tới Admin khi có ca chuyển tiếp / chờ duyệt — badge (số ca chờ) trên
  dashboard/PWA, realtime qua WebSocket. (Web push đẩy thật xuyên nền tảng: §22.)"
- §16 (bảng): đổi tiêu đề `## 16. Web vs Mobile` → `## 16. Web vs Điện thoại (PWA)`; cột "Mobile Admin" →
  "Điện thoại (PWA, Admin)"; giữ nguyên các ✓/✗ chức năng; ô "✅ rút gọn + push" → "✅ rút gọn" (push → badge).
  Ghi chú layout "Mobile Admin: …" → "Trên điện thoại (PWA): Conversation List → Chat Screen (rút gọn), cài lên
  màn hình chính; badge số ca chờ." Thêm dòng dưới bảng: "Chỉ một app web (Next.js), responsive; cột 'Điện thoại
  (PWA)' là ưu tiên hiển thị + duyệt nhanh trên màn hình nhỏ, KHÔNG phải app riêng. Web push đẩy thật: §22."
- §21 (stack): dòng "| Mobile | React Native / Expo (SDK 51+) |" → "| Điện thoại (PWA) | Chính Web (Next.js) cài
  lên màn hình chính — không codebase mobile riêng |".
- §22 (thêm dòng vào Phase 3 hoặc mục thông báo): "Web push notification xuyên nền tảng cho Admin (đặc biệt trên
  iOS, vốn hạn chế PWA push) — thay cho push native của app mobile cũ."

> Giữ nguyên tắc: PRD là nguồn chân lý — sau lát này PRD phải phản ánh đúng rằng mobile = PWA.

## 5. Verify

1. `pnpm install` OK; `apps/mobile` đã biến mất; không còn tham chiếu mobile trong workspace/Makefile/package.json;
   lockfile không còn expo/react-native.
2. `make dev-dashboard` (hoặc `pnpm --filter dashboard dev`); mở `http://localhost:3000` — `/` chạy bình thường,
   `/chat` (cổng chat khách, WebSocket echo) vẫn hoạt động.
3. `pnpm --filter dashboard build` (production) PASS; kiểm tra `/manifest.webmanifest` + `/icon-192.png` +
   `/icon-512.png` truy cập được.
4. Ở bản production/preview: DevTools → Application → Manifest hiện đúng name/icons; Service Worker đăng ký OK
   (chỉ ở production); trình duyệt cho phép "Install app" / "Add to Home Screen".
5. Thu nhỏ cửa sổ / DevTools device mode (khổ điện thoại) → `/` và `/chat` responsive, không tràn ngang.
6. `grep -ri "react-native\|expo\|apps/mobile" .` (trừ node_modules, git history) → không còn kết quả trong
   **tài liệu & config** (backend CORS comment "Expo web" đã FLAG — ngoài phạm vi, người dùng quyết).

## 6. Definition of Done

- [ ] `apps/mobile` đã xóa; `pnpm-workspace.yaml`/`package.json`/`Makefile`/`.npmrc`/`.gitignore` sạch tham chiếu
      mobile; `pnpm install` OK; lockfile sạch expo/react-native.
- [ ] `pnpm --filter dashboard build` PASS; `/manifest.webmanifest` + icon 192/512 tồn tại.
- [ ] Service worker đăng ký ở production; app "Install/Add to Home Screen" được; API/cross-origin không bị cache.
- [ ] Các trang hiện có (`/`, `/chat`) responsive trên khổ điện thoại.
- [ ] `PRD.md` §1.3/§6/§11/§14.5/§16/§21/§22 đã cập nhật đúng wording ở mục 4; push thật nằm ở §22.
- [ ] `CLAUDE.md`, `docs/architecture.md`, `README.md` không còn nhắc React Native/Expo; mô tả PWA.
- [ ] `grep` không còn "react-native"/"expo"/"apps/mobile" trong tài liệu & config (backend comment đã FLAG).

## 7. Ranh giới & quy ước (theo CLAUDE.md)

- CHỈ làm: gỡ mobile + PWA hạ tầng cho dashboard + cập nhật tài liệu/config. KHÔNG đụng backend/agent/logic.
- Đơn giản trước: PWA tối giản (manifest + SW cơ bản + icon), không thư viện nặng, không caching phức tạp,
  KHÔNG push thật. Đừng đẻ thêm việc ngoài mục 2–4.
- SW không cache API/dữ liệu động (tránh dữ liệu cũ); SW chỉ bật ở production.
- Commit nhỏ theo bước (vd `chore(repo): remove react-native mobile app`, `feat(pwa): manifest + service worker
  + icons`, `docs: sync mobile→PWA in PRD/CLAUDE/architecture/README`).
- Kết thúc: in tóm tắt thay đổi, kết quả verify, checklist DoD đã đạt.
