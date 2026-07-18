import type { Config } from "tailwindcss";

// Token ThriftYourStyle (docs/design/ThriftYourStyle CSKH.dc.html).
// LƯU Ý: cố ý KHÔNG đặt tên trùng palette mặc định của Tailwind (amber/green/blue…) —
// đặt trùng sẽ NUỐT cả thang mặc định (bg-amber-50 biến mất) và làm hỏng component chưa kịp restyle.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        page: "#FBFAF7",
        panel: "#FDFCFA",
        cream: { DEFAULT: "#F4F2EC", soft: "#F9F8F4" },
        ink: { DEFAULT: "#211F1B", "2": "#332F29", paper: "#F7F5F0" },
        muted: "#57534A",
        faint: "#8E887B",
        dim: "#B0A99B",
        dimmer: "#C4BEB1",
        line: { DEFAULT: "#E7E2D8", soft: "#F0EDE6", olive: "#DDE1D0" },
        olive: { DEFAULT: "#6B7A4F", dark: "#5A6743", soft: "#EEF0E6" },
        terracotta: {
          DEFAULT: "#B25B3C",
          soft: "#F6E7DF",
          line: "#EAD4C7",
          ink: "#8A4E33",
        },
        gold: { DEFAULT: "#B98534", soft: "#F7EFDD" },
        steel: { DEFAULT: "#42536B", "2": "#5A6B84", soft: "#E8ECF3", line: "#D4DAE6" },
        sage: { DEFAULT: "#5B7A5B", soft: "#E8EFE6" },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        serif: ["var(--font-serif)", "Georgia", "serif"],
      },
      boxShadow: {
        card: "0 2px 8px rgba(33,31,27,.04)",
        soft: "0 2px 10px rgba(33,31,27,.03)",
        drawer: "0 12px 44px rgba(20,18,15,.22)",
        draft: "0 4px 16px rgba(107,122,79,.10)",
      },
    },
  },
  plugins: [],
};

export default config;
