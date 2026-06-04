"use client";

import { motion } from "framer-motion";
import { Sparkles, AlertCircle, Info, TrendingUp } from "lucide-react";
import type { VideoDetail } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";

type Props = { video: VideoDetail };

interface Insight {
    type?: string;
    severity?: string;
    message?: string;
    detail?: string;
    description?: string;
    metric?: string;
    value?: string | number;
}

const severityConfig = {
    critical: { color: "border-red-400/30 bg-red-400/5", icon: AlertCircle, text: "text-red-400" },
    warning: { color: "border-yellow-400/30 bg-yellow-400/5", icon: AlertCircle, text: "text-yellow-400" },
    info: { color: "border-blue-400/30 bg-blue-400/5", icon: Info, text: "text-blue-400" },
    positive: { color: "border-emerald-400/30 bg-emerald-400/5", icon: TrendingUp, text: "text-emerald-400" },
    default: { color: "border-border bg-muted/40", icon: Sparkles, text: "text-muted-foreground" },
};

function getSeverityKey(insight: Insight): keyof typeof severityConfig {
    const s = (insight.severity ?? insight.type ?? "").toLowerCase();
    if (s in severityConfig) return s as keyof typeof severityConfig;
    return "default";
}

export function InsightWidget({ video }: Props) {
    const rawInsights = (
        video.analytics.insights ??
        video.analytics._insights ??
        video.analytics.ai_insights ??
        []
    ) as Insight[];

    if (!Array.isArray(rawInsights) || rawInsights.length === 0) {
        return <EmptyState message="No insights generated yet." />;
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <SectionHeader title="AI Insights" subtitle={`${rawInsights.length} insights generated`} icon={Sparkles} />

            <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {rawInsights.map((insight, i) => {
                    const key = getSeverityKey(insight);
                    const { color, icon: Icon, text } = severityConfig[key];
                    const msg = insight.message ?? insight.description ?? insight.detail ?? "Review analytics data.";
                    const sub = insight.metric
                        ? `${insight.metric}${insight.value !== undefined ? `: ${insight.value}` : ""}`
                        : "";
                    return (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 8 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.04 }}
                            className={`flex items-start gap-3 rounded-xl border p-4 ${color}`}
                        >
                            <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${text}`} />
                            <div>
                                <p className="text-sm font-medium leading-snug text-foreground">{msg}</p>
                                {sub && <p className="mt-0.5 text-xs text-muted-foreground">{sub}</p>}
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </motion.div>
    );
}
