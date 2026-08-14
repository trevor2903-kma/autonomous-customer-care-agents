"use client";

import { useRouter } from "next/navigation";
import Image from "next/image";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";

type CustomerMode = "login" | "register";

function routeFor(role: string): string {
  return role === "admin" ? "/admin" : "/chat";
}

export default function LoginPage() {
  const { user, loading, login, register } = useAuth();
  const router = useRouter();

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

  const isRegister = mode === "register";

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
    <main className="flex flex-1 min-h-0 items-center justify-center px-4 py-10 overflow-y-auto">
      <div className="w-full max-w-[420px] rounded-[14px] border border-line bg-card bg-white p-8 shadow-card">
        {/* Brand */}
        <div className="mb-6 flex flex-col items-center gap-2.5">
          <Image
            src="/icon-192.png"
            alt="ThriftYourStyle"
            width={34}
            height={34}
            className="h-[34px] w-[34px] rounded-[8px] object-cover"
          />
          <span className="font-serif text-[22px] tracking-[0.2px] text-ink">ThriftYourStyle</span>
          <span className="text-[12.5px] text-faint">Chăm sóc khách hàng</span>
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

        <p className="mt-6 text-center text-[11.5px] text-dim">
          Hệ thống chăm sóc khách hàng tự trị · Multi-Agent AI
        </p>
      </div>
    </main>
  );
}

function EyeIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeOffIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
      <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
      <line x1="2" y1="2" x2="22" y2="22" />
    </svg>
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
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === "password";
  const inputType = isPassword ? (showPassword ? "text" : "password") : type;

  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[12.5px] font-medium text-muted">{label}</span>
      <div className="relative flex items-center">
        <input
          type={inputType}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          required={required}
          className={`w-full rounded-[10px] border border-line bg-white py-2.5 pl-3.5 text-[14.5px] text-ink outline-none placeholder:text-dim focus:border-olive ${
            isPassword ? "pr-10" : "pr-3.5"
          }`}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword((prev) => !prev)}
            tabIndex={-1}
            aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
            className="absolute right-2.5 flex h-7 w-7 items-center justify-center rounded-md text-faint hover:text-ink focus:outline-none focus:ring-1 focus:ring-olive transition-colors"
          >
            {showPassword ? (
              <EyeOffIcon className="h-[17px] w-[17px]" />
            ) : (
              <EyeIcon className="h-[17px] w-[17px]" />
            )}
          </button>
        )}
      </div>
    </label>
  );
}
