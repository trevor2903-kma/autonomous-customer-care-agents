"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  type AuthUser,
  getMe,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
} from "@/lib/api";

// AuthContext (httpOnly cookies) — user nạp/validate qua /api/auth/me và refresh token.
type AuthState = {
  user: AuthUser | null;
  loading: boolean; // true khi đang validate cookie lúc tải trang
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (email: string, password: string, displayName?: string) => Promise<AuthUser>;
  logout: () => void | Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const queryClient = useQueryClient();

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
    queryClient.clear();
    await apiLogin(email, password);
    const me = await getMe();
    setUser(me);
    return me;
  }, [queryClient]);

  const register = useCallback(async (email: string, password: string, displayName?: string) => {
    queryClient.clear();
    await apiRegister(email, password, displayName);
    const me = await getMe();
    setUser(me);
    return me;
  }, [queryClient]);

  const logout = useCallback(async () => {
    await apiLogout();
    queryClient.clear();
    setUser(null);
  }, [queryClient]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (ctx === null) throw new Error("useAuth phải nằm trong <AuthProvider>");
  return ctx;
}
