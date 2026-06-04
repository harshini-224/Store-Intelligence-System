"use client";

import { motion } from "framer-motion";
import { TrendingDown, ArrowRight } from "lucide-react";
import type { VideoDetail } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";
import { FunnelChartWidget } from "@/components/charts/funnel-chart";

type Props = { video: VideoDetail };

const STAGE_LABELS: Record<string, string> = {
    entry: "Entry",
    entry_count: "Entry",
    zone_visit: "Zone Visit",
    zone_visit_count: "Zone Visit",
    billing_queue: "Billing Queue",
    billing_queue_count: "Billing Queue",
    purchase: "Purchase",
    purchase_count: "Purchase",
};

export function FunnelWidget({ video }: Props) {
    const f = video.analytics._funnel_metrics;
    if (!f) return <EmptyState message="No funnel data available." />;

    const stages: { name: string; value: number }[] = [];
    const pairs: [string, string][] = [
        ["entry", "entry_count"],
        ["zone_visit", "zone_visit_count"],
        ["billing_queue", "billing_queue_count"],
        ["purchase", "purchase_count"],
    ];

    for (const [primary, fallback] of pairs) {
        const v = (f as Record<string, number | undefined>)[primary] ?? (f as Record<string, number | undefined>)[fallback];
        if (v !== undefined) {
            stages.push({ name: STAGE_LABELS[primary], value: v });
        }
    }

    if (stages.length < 2) return <EmptyState message="Insufficient funnel data." />;

    const dropoffs = stages.map((stage, i) => {
        if (i === 0) return null;
        const prev = stages[i - 1].value;
        const pct = prev > 0 ? (((prev - stage.value) / prev) * 100).toFixed(1) : null;
        return { from: stages[i - 1].name, to: stage.name, pct };
    }).filter(Boolean);

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <SectionHeader title="Funnel Analytics" subtitle="Visitor journey from entry to purchase" icon={TrendingDown} />

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
                <div>
                    <FunnelChartWidget data={stages} />
                </div>
                <div className="space-y-3">
                    {stages.map((stage) => (
                        <div key={stage.name} className="flex items-center justify-between rounded-xl bg-muted/40 px-4 py-3">
                            <p className="text-sm font-medium">{stage.name}</p>
                            <p className="text-lg font-bold tabular-nums">{stage.value}</p>
                        </div>
                    ))}
                </div>
            </div>

            {dropoffs.length > 0 && (
                <div className="mt-6">
                    <p className="mb-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">Drop-off Rates</p>
                    <div className="space-y-2">
                        {dropoffs.map((d) => d && (
                            <div key={`${d.from}-${d.to}`} className="flex items-center gap-2 text-sm text-muted-foreground">
                                <span>{d.from}</span>
                                <ArrowRight className="h-3 w-3 shrink-0" />
                                <span>{d.to}</span>
                                <span className="ml-auto font-semibold text-orange-400">{d.pct}% drop</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </motion.div>
    );
}
