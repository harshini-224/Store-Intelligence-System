"use client";

import { motion } from "framer-motion";
import { Lightbulb, TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { VideoDetail } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";

type Props = { video: VideoDetail };

interface Recommendation {
    zone?: string;
    type?: string;
    action?: string;
    priority?: string;
    reason?: string;
    metric?: string;
    value?: number | string;
    suggestion?: string;
    message?: string;
}

function getPriority(r: Recommendation): "high" | "medium" | "low" {
    const p = (r.priority ?? "").toLowerCase();
    if (p === "high") return "high";
    if (p === "low") return "low";
    return "medium";
}

const priorityColors = {
    high: "border-red-400/30 bg-red-400/5 text-red-400",
    medium: "border-yellow-400/30 bg-yellow-400/5 text-yellow-400",
    low: "border-emerald-400/30 bg-emerald-400/5 text-emerald-400",
};

const TrendIcon = ({ p }: { p: "high" | "medium" | "low" }) => {
    if (p === "high") return <TrendingDown className="h-4 w-4" />;
    if (p === "low") return <TrendingUp className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
};

export function RecommendationWidget({ video }: Props) {
    const rawRecs = (video.analytics.recommendations ?? video.analytics._recommendations ?? []) as Recommendation[];
    if (!Array.isArray(rawRecs) || rawRecs.length === 0) {
        return <EmptyState message="No recommendations available." />;
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <SectionHeader title="Recommendations" subtitle={`${rawRecs.length} actionable insights`} icon={Lightbulb} />

            <div className="mt-4 space-y-3">
                {rawRecs.map((rec, i) => {
                    const priority = getPriority(rec);
                    const colorClass = priorityColors[priority];
                    const message =
                        rec.message ?? rec.action ?? rec.suggestion ??
                        (rec.zone ? `Optimize ${rec.zone} zone` : "Review analytics for improvement opportunities");
                    const reason = rec.reason ?? rec.metric ?? "";

                    return (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -8 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.05 }}
                            className={`flex items-start gap-3 rounded-xl border p-4 ${colorClass}`}
                        >
                            <TrendIcon p={priority} />
                            <div className="flex-1">
                                <p className="text-sm font-medium text-foreground">{message}</p>
                                {reason && <p className="mt-0.5 text-xs opacity-70">{reason}</p>}
                            </div>
                            <span className="shrink-0 rounded-full px-2 py-0.5 text-xs font-medium capitalize opacity-80 ring-1 ring-current">
                                {priority}
                            </span>
                        </motion.div>
                    );
                })}
            </div>
        </motion.div>
    );
}
