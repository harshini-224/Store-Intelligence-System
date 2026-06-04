"use client";

import { motion } from "framer-motion";
import {
    Activity, CheckCircle, XCircle, AlertTriangle,
    Camera, Zap, Calendar, Clock,
} from "lucide-react";
import { useHealth } from "@/lib/hooks";

function HealthBadge({ status }: { status?: string }) {
    const cfg = {
        healthy: { bg: "bg-emerald-400/15 text-emerald-400 border-emerald-400/30", icon: CheckCircle, label: "Healthy" },
        degraded: { bg: "bg-yellow-400/15 text-yellow-400 border-yellow-400/30", icon: AlertTriangle, label: "Degraded" },
        offline: { bg: "bg-red-400/15 text-red-400 border-red-400/30", icon: XCircle, label: "Offline" },
    }[status ?? "offline"] ?? {
        bg: "bg-muted text-muted-foreground border-border",
        icon: Activity,
        label: "Unknown",
    };

    return (
        <span className={`inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-semibold ${cfg.bg}`}>
            <cfg.icon className="h-4 w-4" />
            {cfg.label}
        </span>
    );
}

export default function HealthPage() {
    const { data: health, isLoading, isError, dataUpdatedAt } = useHealth();

    const rows = health
        ? [
            { label: "Event Count", value: health.event_count, icon: Zap },
            { label: "Active Cameras", value: health.active_cameras, icon: Camera },
            { label: "Tracking Available", value: health.tracking_available ? "Yes" : "No", icon: Activity, bad: !health.tracking_available },
            { label: "Analytics Available", value: health.analytics_available ? "Yes" : "No", icon: Activity, bad: !health.analytics_available },
            { label: "Events Available", value: health.events_available ? "Yes" : "No", icon: Zap, bad: !health.events_available },
            { label: "Stale Feed", value: health.stale_feed ? "Yes" : "No", icon: AlertTriangle, bad: health.stale_feed },
        ]
        : [];

    return (
        <div className="page-shell max-w-3xl">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight">System Health</h1>
                <p className="mt-1 text-muted-foreground">Real-time status of the backend detection and analytics pipeline.</p>
            </motion.div>

            {isLoading && (
                <div className="space-y-4">
                    <div className="h-24 animate-pulse rounded-2xl bg-muted" />
                    {Array.from({ length: 4 }).map((_, i) => (
                        <div key={i} className="h-16 animate-pulse rounded-xl bg-muted" />
                    ))}
                </div>
            )}

            {isError && (
                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col items-center justify-center rounded-2xl border border-red-400/30 bg-red-400/5 py-16 text-center"
                >
                    <XCircle className="h-12 w-12 text-red-400 mb-3" />
                    <p className="font-semibold text-red-400">Backend Offline</p>
                    <p className="mt-1 text-sm text-muted-foreground">Could not reach the API. Make sure the FastAPI server is running.</p>
                </motion.div>
            )}

            {health && (
                <>
                    {/* Status banner */}
                    <motion.div
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass-card mb-6 rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                    >
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Overall Status</p>
                            <HealthBadge status={health.status} />
                        </div>
                        <div className="text-sm text-muted-foreground flex flex-col gap-1">
                            {health.last_event_timestamp && (
                                <span className="flex items-center gap-1.5">
                                    <Clock className="h-3.5 w-3.5" />
                                    Last event: {new Date(health.last_event_timestamp).toLocaleString()}
                                </span>
                            )}
                            {dataUpdatedAt > 0 && (
                                <span className="flex items-center gap-1.5">
                                    <Calendar className="h-3.5 w-3.5" />
                                    Updated: {new Date(dataUpdatedAt).toLocaleTimeString()}
                                </span>
                            )}
                        </div>
                    </motion.div>

                    {/* Metrics grid */}
                    <div className="grid gap-3 sm:grid-cols-2">
                        {rows.map(({ label, value, icon: Icon, bad }, i) => (
                            <motion.div
                                key={label}
                                initial={{ opacity: 0, y: 12 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.05 * i }}
                                className={[
                                    "flex items-center gap-4 rounded-xl border px-5 py-4 glass-card",
                                    bad ? "border-red-400/30 bg-red-400/5" : "",
                                ].join(" ")}
                            >
                                <Icon className={`h-5 w-5 shrink-0 ${bad ? "text-red-400" : "text-primary"}`} />
                                <div className="flex-1">
                                    <p className="text-xs text-muted-foreground">{label}</p>
                                    <p className={`text-lg font-semibold ${bad ? "text-red-400" : ""}`}>{String(value)}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>

                    <p className="mt-6 text-center text-xs text-muted-foreground">
                        Health data refreshes every 30 seconds automatically.
                    </p>
                </>
            )}
        </div>
    );
}
