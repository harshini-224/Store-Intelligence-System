"use client";

import { motion } from "framer-motion";
import { Users, Clock, TrendingUp } from "lucide-react";
import type { VideoDetail } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";
import { BarChart } from "@/components/charts/bar-chart";

type Props = { video: VideoDetail };

export function ZoneAnalyticsWidget({ video }: Props) {
    const zones = Object.entries(video.zones);
    if (zones.length === 0) return <EmptyState message="No zone data available." />;

    const chartData = zones.map(([name, metric]) => ({
        name: name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        Visitors: metric.visitors,
        "Dwell (s)": Math.round(metric.total_dwell_time),
    }));

    const totalVisitors = zones.reduce((s, [, m]) => s + m.visitors, 0);
    const totalDwell = zones.reduce((s, [, m]) => s + m.total_dwell_time, 0);
    const avgDwell = zones.length > 0 ? totalDwell / Math.max(totalVisitors, 1) : 0;

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <SectionHeader title="Zone Analytics" subtitle={`${zones.length} zones detected`} icon={Users} />

            <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <StatCard label="Total Visitors" value={totalVisitors} icon={Users} />
                <StatCard label="Avg Dwell Time" value={`${avgDwell.toFixed(1)}s`} icon={Clock} />
                <StatCard label="Zones Active" value={zones.length} icon={TrendingUp} />
            </div>

            <div className="mt-6">
                <p className="mb-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">Visitors per Zone</p>
                <BarChart data={chartData} dataKey="Visitors" nameKey="name" height={180} />
            </div>

            <div className="mt-4 space-y-2">
                {zones.map(([name, metric]) => {
                    const pct = totalVisitors > 0 ? (metric.visitors / totalVisitors) * 100 : 0;
                    return (
                        <div key={name} className="flex items-center gap-3 rounded-xl bg-muted/40 px-4 py-3">
                            <div className="flex-1">
                                <p className="text-sm font-medium capitalize">{name.replace(/_/g, " ")}</p>
                                <div className="mt-1 h-1.5 w-full rounded-full bg-border">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${pct}%` }}
                                        transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
                                        className="h-1.5 rounded-full bg-primary"
                                    />
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-sm font-semibold">{metric.visitors}</p>
                                <p className="text-xs text-muted-foreground">{Math.round(metric.total_dwell_time)}s</p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </motion.div>
    );
}

function StatCard({ label, value, icon: Icon }: { label: string; value: string | number; icon: React.ElementType }) {
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
