import Link from "next/link";

export function Header({ connected }: { connected: boolean }) {
  return (
    <header className="flex items-center justify-between border-b border-neutral-200 bg-white px-4 py-3">
      <div>
        <h1 className="text-base font-semibold">Shop Quần Áo — Hỗ trợ</h1>
        <p className="text-xs text-neutral-500">
          <span
            className={`mr-1 inline-block h-2 w-2 rounded-full ${
              connected ? "bg-green-500" : "bg-neutral-300"
            }`}
          />
          {connected ? "Đang hoạt động" : "đang kết nối…"}
        </p>
      </div>
      <Link href="/" className="text-xs text-neutral-500 hover:underline">
        ← Admin
      </Link>
    </header>
  );
}
