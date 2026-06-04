"use client";

import { motion } from "framer-motion";
import { Users, Clock, TrendingDown, AlertTriangle } from "lucide-react";
import type { VideoDetail } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";
import { cn } from "@/lib/utils";

type Props = { video: VideoDetail };

export function QueueWidget({ video }: Props) {
    const q = video.analytics._queue_metrics;
    if (!q) return <EmptyState message="No queue data available." />;

    const abandonment = q.abandonment_rate_percent ?? (q.abandonment_rate ? q.abandonment_rate * 100 : null);
    const abandonHigh = abandonment !== null && abandonment > 30;

    const metrics: { label: string; value: string | number; icon: React.ElementType; highlight?: boolean }[] = [
        { label: "Queue Joins", value: q.queue_joins ?? "—", icon: Users },
        { label: "Queue Abandons", value: q.queue_abandons ?? "—", icon: AlertTriangle, highlight: true },
        { label: "Queue Conversions", value: q.queue_conversions ?? "—", icon: TrendingDown },
        { label: "Abandonment Rate", value: abandonment !== null ? `${abandonment.toFixed(1)}%` : "—", icon: AlertTriangle, highlight: abandonHigh },
        { label: "Avg Wait Time", value: q.average_queue_wait_time !== undefined ? `${q.average_queue_wait_time.toFixed(1)}s` : "—", icon: Clock },
        { label: "Max Wait Time", value: q.max_queue_wait_time !== undefined ? `${q.max_queue_wait_time.toFixed(1)}s` : "—", icon: Clock },
        { label: "Avg Queue Depth", value: q.average_queue_depth !== undefined ? q.average_queue_depth.toFixed(1) : "—", icon: Users },
        { label: "Max Queue Depth", value: q.max_queue_depth ?? "—", icon: Users },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <SectionHeader title="Queue Analytics" subtitle="Queue depth, wait times, and abandonment" icon={Users} />

            {abandonHigh && (
                <div className="mt-4 flex items-center gap-2 rounded-xl border border-orange-400/30 bg-orange-400/10 px-4 py-3 text-sm text-orange-400">
                    <AlertTriangle className="h-4 w-4 shrink-0" />
                    High abandonment rate detected — consider adding staff or reducing wait time.
                </div>
            )}

            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {metrics.map(({ label, value, icon: Icon, highlight }) => (
                    <div
                        key={label}
                        className={cn(
                            "rounded-xl bg-muted/40 px-4 py-3",
                            highlight && "border border-orange-400/20 bg-orange-400/5"
                        )}
                    >
                        <div className="flex items-center gap-2 text-muted-foreground">
                            <Icon className="h-3.5 w-3.5" />
                            <p className="text-xs">{label}</p>
                        </div>
                        <p className={cn("mt-1 text-xl font-semibold", highlight && "text-orange-400")}>
                            {value}
                        </p>
                    </div>
                ))}
            </div>
        </motion.div>
    );
}
