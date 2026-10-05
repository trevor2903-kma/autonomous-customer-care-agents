"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  type AuthUser,
  getMe,
  login as apiLogin,
  logout as apiLogout,
  onSessionExpired,
  register as apiRegister,
} from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

// AuthContext (httpOnly cookies) — user nạp/validate qua /api/auth/me và refresh token.
type AuthState = {
  user: AuthUser | null;
  loading: boolean; // true khi đang validate cookie lúc tải trang
  // true sau khi CHỦ ĐỘNG đăng xuất (tới lần đăng nhập kế) → RequireAuth về /login KHÔNG kèm `?next=`:
  // đăng nhập lại luôn vào trang mặc định theo vai (khác hết phiên — quay lại trang đang mở).
  signedOut: boolean;
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (email: string, password: string, displayName?: string) => Promise<AuthUser>;
  logout: () => void | Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [signedOut, setSignedOut] = useState(false);
  const queryClient = useQueryClient();
  const toast = useToast();
  const userRef = useRef<AuthUser | null>(null);
  // true từ lúc xử lý hết phiên tới khi đăng nhập lại → request song song / đến muộn cũng được nuốt, không bật lỗi.
  const expiredRef = useRef(false);

  useEffect(() => {
    userRef.current = user;
  }, [user]);

  // Hết phiên GIỮA CHỪNG (req: 401 + refresh hỏng) → user = null → RequireAuth đưa về /login?next=<trang đang mở>
  // thay vì hiện lỗi 401. KHÔNG tự điều hướng ở đây: hai lệnh replace chạy đua có thể làm mất `next`.
  // Chưa đăng nhập (dò /me lúc tải trang) → false: để getMe nhận 401 như cũ.
  useEffect(() => {
    onSessionExpired(() => {
      if (expiredRef.current) return true;
      if (!userRef.current) return false;
      expiredRef.current = true;
      queryClient.clear();
      setUser(null);
      toast.error("Phiên đăng nhập đã hết hạn", "Vui lòng đăng nhập lại để tiếp tục.");
      return true;
    });
    return () => onSessionExpired(null);
  }, [queryClient, toast]);

  // Tải trang: gọi /api/auth/me với cookie (tự động thử refresh nếu 401)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const me = await getMe();
        if (!cancelled) setUser(me);
      } catch {
        queryClient.clear();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [queryClient]);

  const login = useCallback(async (email: string, password: string) => {
    expiredRef.current = false;
    queryClient.clear();
    await apiLogin(email, password);
    const me = await getMe();
    setSignedOut(false);
    setUser(me);
    return me;
  }, [queryClient]);

  const register = useCallback(async (email: string, password: string, displayName?: string) => {
    expiredRef.current = false;
    queryClient.clear();
    await apiRegister(email, password, displayName);
    const me = await getMe();
    setSignedOut(false);
    setUser(me);
    return me;
  }, [queryClient]);

  const logout = useCallback(async () => {
    // Request đang bay gặp 401 vì cookie vừa bị xoá → nuốt như hết phiên nhưng KHÔNG báo "phiên đã hết hạn".
    expiredRef.current = true;
    await apiLogout();
    queryClient.clear();
    setSignedOut(true);
    setUser(null);
  }, [queryClient]);

  return (
    <AuthContext.Provider value={{ user, loading, signedOut, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (ctx === null) throw new Error("useAuth phải nằm trong <AuthProvider>");
  return ctx;
}
