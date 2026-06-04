import { Badge } from "@/components/ui/badge";

export function StatusPill({ status }: { status?: string }) {
  const normalized = status || "unknown";
  const tone =
    normalized === "healthy" || normalized === "completed"
      ? "success"
      : normalized === "degraded" || normalized === "running"
        ? "warning"
        : normalized === "failed" || normalized === "offline"
          ? "danger"
          : "default";

  return <Badge tone={tone}>{normalized}</Badge>;
}
