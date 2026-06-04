"use client";

import { motion } from "framer-motion";
import { Clock, Users, TrendingDown } from "lucide-react";
import type { VideoDetail } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";
import { BarChart } from "@/components/charts/bar-chart";

type Props = { video: VideoDetail };

export function DwellWidget({ video }: Props) {
    const zones = Object.entries(video.zones);
    if (zones.length === 0) return <EmptyState message="No dwell data available." />;

    const sorted = [...zones].sort((a, b) => b[1].total_dwell_time - a[1].total_dwell_time);
    const totalDwell = zones.reduce((s, [, m]) => s + m.total_dwell_time, 0);
    const totalVisitors = zones.reduce((s, [, m]) => s + m.visitors, 0);

    const chartData = sorted.map(([name, metric]) => ({
        name: name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()).slice(0, 12),
        "Avg Dwell (s)": metric.visitors > 0 ? +(metric.total_dwell_time / metric.visitors).toFixed(1) : 0,
    }));

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <SectionHeader title="Dwell Analytics" subtitle="Time visitors spent in each zone" icon={Clock} />

            <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <StatBlock label="Total Dwell Time" value={`${totalDwell.toFixed(0)}s`} icon={Clock} />
                <StatBlock label="Total Visitors" value={totalVisitors} icon={Users} />
                <StatBlock
                    label="Avg Per Visitor"
                    value={totalVisitors > 0 ? `${(totalDwell / totalVisitors).toFixed(1)}s` : "—"}
                    icon={TrendingDown}
                />
            </div>

            <div className="mt-6">
                <p className="mb-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">Avg Dwell per Zone</p>
                <BarChart data={chartData} dataKey="Avg Dwell (s)" nameKey="name" color="#818cf8" height={180} />
            </div>
        </motion.div>
    );
}

function StatBlock({ label, value, icon: Icon }: { label: string; value: string | number; icon: React.ElementType }) {
    return (
        <div className="rounded-xl bg-muted/40 px-4 py-3">
            <div className="flex items-center gap-2 text-muted-foreground">
                <Icon className="h-3.5 w-3.5" />
                <p className="text-xs">{label}</p>
            </div>
            <p className="mt-1 text-xl font-semibold">{value}</p>
        </div>
    );
}
