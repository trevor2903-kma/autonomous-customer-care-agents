"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  type AuthUser,
  clearToken,
  getMe,
  getToken,
  login as apiLogin,
  register as apiRegister,
  setToken,
} from "@/lib/api";

// AuthContext (slice 11 P4) — JWT lưu localStorage; user nạp/validate qua /api/auth/me.
type AuthState = {
  user: AuthUser | null;
  loading: boolean; // true khi đang validate token lúc tải trang
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (email: string, password: string, displayName?: string) => Promise<AuthUser>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Tải trang: nếu có token → validate + nạp user; token hỏng/hết hạn → xoá.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!getToken()) {
        setLoading(false);
        return;
      }
      try {
        const me = await getMe();
        if (!cancelled) setUser(me);
      } catch {
        clearToken();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await apiLogin(email, password);
    setToken(res.access_token);
    const me = await getMe();
    setUser(me);
    return me;
  }, []);

  const register = useCallback(async (email: string, password: string, displayName?: string) => {
    const res = await apiRegister(email, password, displayName);
    setToken(res.access_token);
    const me = await getMe();
    setUser(me);
    return me;
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

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
