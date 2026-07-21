"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";

type Tab = "customer" | "admin";
type CustomerMode = "login" | "register";

function routeFor(role: string): string {
  return role === "admin" ? "/admin" : "/chat";
}

export default function LoginPage() {
  const { user, loading, login, register } = useAuth();
  const router = useRouter();

  const [tab, setTab] = useState<Tab>("customer");
  const [mode, setMode] = useState<CustomerMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Đã đăng nhập mà mở /login → về trang đúng vai.
  useEffect(() => {
    if (!loading && user) router.replace(routeFor(user.role));
  }, [loading, user, router]);

  const isRegister = tab === "customer" && mode === "register";

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const u = isRegister
        ? await register(email.trim(), password, displayName.trim() || undefined)
        : await login(email.trim(), password);
      router.replace(routeFor(u.role));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Có lỗi xảy ra");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-[calc(100vh_-_53px)] items-center justify-center px-4 py-10">
      <div className="w-full max-w-[420px] rounded-[14px] border border-line bg-card bg-white p-8 shadow-card">
        {/* Brand */}
        <div className="mb-6 flex flex-col items-center gap-2.5">
          <span className="flex h-[34px] w-[34px] items-center justify-center rounded-[8px] bg-ink font-serif text-lg text-ink-paper">
            T
          </span>
          <span className="font-serif text-[22px] tracking-[0.2px] text-ink">ThriftYourStyle</span>
          <span className="text-[12.5px] text-faint">Chăm sóc khách hàng</span>
        </div>

        {/* Tabs Khách / Quản trị */}
        <div className="mb-6 flex rounded-[9px] border border-line bg-cream-soft p-1">
          {(["customer", "admin"] as Tab[]).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => {
                setTab(t);
                setError(null);
              }}
              className={`flex-1 rounded-[7px] py-2 text-[13.5px] font-medium transition-colors ${
                tab === t ? "bg-white text-ink shadow-soft" : "text-faint hover:text-muted"
              }`}
            >
              {t === "customer" ? "Khách hàng" : "Quản trị"}
            </button>
          ))}
        </div>

        <h1 className="mb-5 text-center font-serif text-[21px] text-ink">
          {isRegister ? "Tạo tài khoản" : "Đăng nhập"}
        </h1>

        <form onSubmit={onSubmit} className="flex flex-col gap-3.5">
          {isRegister && (
            <Field
              label="Tên hiển thị"
              type="text"
              value={displayName}
              onChange={setDisplayName}
              placeholder="Tên của bạn"
              autoComplete="name"
            />
          )}
          <Field
            label="Email"
            type="email"
            value={email}
            onChange={setEmail}
            placeholder="ban@email.com"
            autoComplete="email"
            required
          />
          <Field
            label="Mật khẩu"
            type="password"
            value={password}
            onChange={setPassword}
            placeholder={isRegister ? "Tối thiểu 6 ký tự" : "••••••••"}
            autoComplete={isRegister ? "new-password" : "current-password"}
            required
          />

          {error && <p className="text-[13px] text-terracotta">{error}</p>}

          <button
            type="submit"
            disabled={busy}
            className="mt-1 rounded-[8px] bg-olive py-2.5 text-[14.5px] font-semibold text-white transition-colors hover:bg-olive-dark disabled:opacity-60"
          >
            {busy ? "Đang xử lý…" : isRegister ? "Tạo tài khoản" : "Đăng nhập"}
          </button>
        </form>

        {tab === "customer" && (
          <p className="mt-5 text-center text-[13px] text-faint">
            {mode === "login" ? "Chưa có tài khoản? " : "Đã có tài khoản? "}
            <button
              type="button"
              onClick={() => {
                setMode(mode === "login" ? "register" : "login");
                setError(null);
              }}
              className="font-medium text-olive hover:text-olive-dark"
            >
              {mode === "login" ? "Tạo tài khoản" : "Đăng nhập"}
            </button>
          </p>
        )}

        <p className="mt-6 text-center text-[11.5px] text-dim">
          Hệ thống chăm sóc khách hàng tự trị · Multi-Agent AI
        </p>
      </div>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  type,
  placeholder,
  autoComplete,
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type: string;
  placeholder?: string;
  autoComplete?: string;
  required?: boolean;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[12.5px] font-medium text-muted">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        required={required}
        className="rounded-[10px] border border-line bg-white px-3.5 py-2.5 text-[14.5px] text-ink outline-none placeholder:text-dim focus:border-olive"
      />
    </label>
  );
}
