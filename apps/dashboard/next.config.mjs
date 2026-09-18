// API_PROXY_TARGET (vd https://api.onrender.com): proxy `/api/*` qua CHÍNH domain dashboard → cookie auth thành cookie
// bên thứ nhất (Safari/iOS chặn cookie bên thứ ba khi FE & backend khác site). Không đặt → gọi thẳng backend như cũ.
const apiProxyTarget = process.env.API_PROXY_TARGET?.replace(/\/+$/, "");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["shared-types"],
  env: { API_PROXY_ENABLED: apiProxyTarget ? "1" : "" },
  async rewrites() {
    return apiProxyTarget ? [{ source: "/api/:path*", destination: `${apiProxyTarget}/api/:path*` }] : [];
  },
};

export default nextConfig;
