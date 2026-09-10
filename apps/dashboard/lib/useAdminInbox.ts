"use client";

import { useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { adminInboxWsUrl } from "@/lib/api";
import { asString, createInboxBatcher } from "@/lib/realtime";
import { useReconnectingSocket } from "@/lib/useReconnectingSocket";

// Inbox admin (FE-01.5): MỘT socket `/ws/admin-inbox` cho mọi trang /admin, thay polling 10 s (quy ước
// "Realtime KHÔNG polling"). Frame `{type:"inbox", conversation_id, event, status}` → gom theo cửa sổ 3 s
// (`createInboxBatcher`): danh sách ca nạp lại TỐI ĐA một lần mỗi cửa sổ; hàng đợi (badge) + chi tiết ca chỉ khi cửa
// sổ có sự kiện `status` (tin mới chỉ đổi thứ tự / preview của danh sách). Hai truy vấn này nặng nhất phía admin →
// lưu lượng khách không được quyết định tần suất nạp. `refetchInterval` 60 s ở các query chỉ còn là lưới an toàn
// khi socket rớt lâu.

// URL kênh inbox: trình duyệt tự động gửi kèm cookie access_token khi handshake.
function currentInboxWsUrl(): string | null {
  return adminInboxWsUrl();
}

export function useAdminInbox(): void {
  const qc = useQueryClient();
  const url = useMemo(currentInboxWsUrl, []);
  const [batcher] = useState(() =>
    createInboxBatcher(({ escalations, changed }) => {
      qc.invalidateQueries({ queryKey: ["conversations"] });
      if (escalations) qc.invalidateQueries({ queryKey: ["escalations"] });
      for (const id of changed) qc.invalidateQueries({ queryKey: ["admin-conv", id] });
    }),
  );

  useReconnectingSocket(url, {
    authRole: "admin",
    resolveUrl: currentInboxWsUrl,
    onFrame: (f) => {
      if (f.type === "inbox") batcher.push(f.event, asString(f.conversation_id));
    },
    // Nối lại sau khi rớt: sự kiện trong lúc mất kết nối đã lỡ → nạp lại ĐỦ ngay một lần.
    onOpen: (isReconnect) => {
      if (isReconnect) batcher.flushNow();
    },
  });

  useEffect(() => () => batcher.dispose(), [batcher]);
}
