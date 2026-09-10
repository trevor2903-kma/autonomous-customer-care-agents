"use client";

import { useEffect, useMemo, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { adminInboxWsUrl, getToken } from "@/lib/api";
import { asString } from "@/lib/realtime";
import { useReconnectingSocket } from "@/lib/useReconnectingSocket";

// Inbox admin (FE-01.5): MỘT socket `/ws/admin-inbox` cho mọi trang /admin, thay polling 10 s (quy ước
// "Realtime KHÔNG polling"). Frame `{type:"inbox", conversation_id, event, status}` → gom trong ~800 ms rồi
// làm tươi danh sách + badge (và chi tiết ca vừa đổi status). `refetchInterval` 60 s ở các query chỉ còn là
// lưới an toàn khi socket rớt lâu.
const INBOX_DEBOUNCE_MS = 800;

export function useAdminInbox(): void {
  const qc = useQueryClient();
  const url = useMemo(() => {
    const token = getToken();
    return token ? adminInboxWsUrl(token) : null;
  }, []);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const changed = useRef(new Set<string>());

  function flush() {
    if (timer.current !== undefined) clearTimeout(timer.current);
    timer.current = undefined;
    qc.invalidateQueries({ queryKey: ["conversations"] });
    qc.invalidateQueries({ queryKey: ["escalations"] });
    for (const id of changed.current) qc.invalidateQueries({ queryKey: ["admin-conv", id] });
    changed.current.clear();
  }

  useReconnectingSocket(url, {
    onFrame: (f) => {
      if (f.type !== "inbox") return;
      const id = asString(f.conversation_id);
      if (f.event === "status" && id) changed.current.add(id);
      // Gom theo cửa sổ (không reset mỗi frame): dồn dập sự kiện vẫn làm tươi đều, không bị bỏ đói.
      if (timer.current === undefined) timer.current = setTimeout(flush, INBOX_DEBOUNCE_MS);
    },
    // Nối lại sau khi rớt: sự kiện trong lúc mất kết nối đã lỡ → làm tươi ngay một lần.
    onOpen: (isReconnect) => {
      if (isReconnect) flush();
    },
  });

  useEffect(
    () => () => {
      if (timer.current !== undefined) clearTimeout(timer.current);
    },
    [],
  );
}
