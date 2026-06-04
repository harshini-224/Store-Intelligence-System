"use client";

import { motion } from "framer-motion";
import { ShoppingCart, TrendingUp, Users } from "lucide-react";
import type { VideoDetail } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";
import { AnimatedCounter } from "@/components/shared/animated-counter";

type Props = { video: VideoDetail };

export function ConversionWidget({ video }: Props) {
    const c = video.analytics._conversion_metrics;
    if (!c) return <EmptyState message="No conversion data available." />;

    const rate = c.conversion_rate !== undefined ? c.conversion_rate * 100 : null;
    const billingRate = c.billing_zone_rate !== undefined ? c.billing_zone_rate * 100 : null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <SectionHeader title="Conversion Analytics" subtitle="Visitor-to-purchase conversion metrics" icon={ShoppingCart} />

            <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <ConvCard
                    label="Total Visitors"
                    value={c.total_visitors ?? 0}
                    icon={Users}
                    color="text-primary"
                />
                <ConvCard
                    label="Converted Visitors"
                    value={c.converted_visitors ?? 0}
                    icon={ShoppingCart}
                    color="text-emerald-400"
                />
                <ConvCard
                    label="Billing Zone Visitors"
                    value={c.billing_zone_visitors ?? 0}
                    icon={TrendingUp}
                    color="text-indigo-400"
                />
            </div>

            {rate !== null && (
                <div className="mt-6 flex flex-col items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 py-8">
                    <p className="text-sm text-muted-foreground">Overall Conversion Rate</p>
                    <p className="mt-2 text-6xl font-bold tabular-nums text-primary">
                        <AnimatedCounter value={rate} decimals={1} suffix="%" />
                    </p>
                    {billingRate !== null && (
                        <p className="mt-2 text-sm text-muted-foreground">
                            Billing Zone Rate: <span className="font-semibold text-foreground">{billingRate.toFixed(1)}%</span>
                        </p>
                    )}
                </div>
            )}
        </motion.div>
    );
}

function ConvCard({
    label,
    value,
    icon: Icon,
    color,
}: {
    label: string;
    value: number;
    icon: React.ElementType;
    color: string;
}) {
    return (
        <div className="rounded-xl bg-muted/40 px-5 py-4">
            <div className={`flex items-center gap-2 ${color}`}>
                <Icon className="h-4 w-4" />
                <p className="text-xs font-medium">{label}</p>
            </div>
            <p className="mt-2 text-3xl font-bold tabular-nums">
                <AnimatedCounter value={value} />
            </p>
        </div>
    );
}
