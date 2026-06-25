import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";

// Mobile Admin (PRD §6, §16): công cụ tối giản — ở scaffold chỉ hiển thị TRẠNG THÁI BACKEND.
// TODO (PRD §16/§11): danh sách hội thoại, chat với khách, nhận push EscalationCard.

// Lưu ý: thiết bị thật KHÔNG thấy "localhost" của máy dev — cấu hình host khi chạy device (expo-constants).
const API_BASE = "http://localhost:8000";

type Probe = { ok: boolean; detail: unknown };
type Health = {
  status: string;
  api: string;
  enable_llm: boolean;
  services: { database: Probe; redis: Probe; qdrant: Probe };
};

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setHealth((await res.json()) as Health);
    } catch (e) {
      setError(String(e));
      setHealth(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={load} />}
      >
        <Text style={styles.title}>ACSS — Admin (scaffold)</Text>
        <Text style={styles.subtitle}>Trạng thái backend</Text>

        {loading && !health && <ActivityIndicator color="#fff" style={{ marginTop: 24 }} />}
        {error && <Text style={styles.error}>Không gọi được backend:{"\n"}{error}</Text>}

        {health && (
          <View style={styles.card}>
            <Row label="Overall" ok={health.status === "ok"} detail={health.status} />
            <Row label="API" ok={health.api === "ok"} detail={health.api} />
            <Row label="Neon (Postgres)" ok={health.services.database.ok} detail={health.services.database.detail} />
            <Row label="Upstash (Redis)" ok={health.services.redis.ok} detail={health.services.redis.detail} />
            <Row label="Qdrant" ok={health.services.qdrant.ok} detail={health.services.qdrant.detail} />
            <Row label="LLM" ok={!health.enable_llm} detail={health.enable_llm ? "on" : "off (scaffold)"} />
          </View>
        )}

        <Text style={styles.hint}>Kéo xuống để làm mới.</Text>
      </ScrollView>
    </View>
  );
}

function Row({ label, ok, detail }: { label: string; ok: boolean; detail: unknown }) {
  return (
    <View style={styles.row}>
      <View style={[styles.dot, { backgroundColor: ok ? "#22c55e" : "#ef4444" }]} />
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowDetail}>{ok ? "ok" : String(detail ?? "—")}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0a0a0a" },
  content: { padding: 24, paddingTop: 64 },
  title: { color: "#fff", fontSize: 22, fontWeight: "700" },
  subtitle: { color: "#a3a3a3", fontSize: 13, marginTop: 4 },
  card: { marginTop: 20, backgroundColor: "#171717", borderRadius: 12, padding: 8 },
  row: { flexDirection: "row", alignItems: "center", paddingVertical: 10, paddingHorizontal: 8 },
  dot: { width: 10, height: 10, borderRadius: 5, marginRight: 10 },
  rowLabel: { color: "#e5e5e5", fontSize: 14, flex: 1 },
  rowDetail: { color: "#737373", fontSize: 12 },
  error: { color: "#fca5a5", marginTop: 24, fontSize: 13 },
  hint: { color: "#525252", fontSize: 12, marginTop: 20, textAlign: "center" },
});
