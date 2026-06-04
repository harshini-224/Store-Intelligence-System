"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
    Activity, Heart, Users, Zap, TrendingUp, AlertTriangle,
    CheckCircle, XCircle, ArrowRight, Library, Upload, Clock,
} from "lucide-react";
import type { HealthStatus, VideoCard } from "@/lib/types";
import { AnimatedCounter } from "@/components/shared/animated-counter";
import { StatusPill } from "@/components/shared/status-pill";

interface Props {
    health: HealthStatus | null;
    videos: VideoCard[];
}

const fade = (delay = 0) => ({
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { delay, duration: 0.5, ease: [0.22, 1, 0.36, 1] },
});

function HealthBadge({ status }: { status: string | undefined }) {
    const cfg = {
        healthy: { bg: "bg-emerald-400/15 text-emerald-400", icon: CheckCircle, label: "Healthy" },
        degraded: { bg: "bg-yellow-400/15 text-yellow-400", icon: AlertTriangle, label: "Degraded" },
        offline: { bg: "bg-red-400/15 text-red-400", icon: XCircle, label: "Offline" },
    }[status ?? "offline"] ?? { bg: "bg-muted text-muted-foreground", icon: Activity, label: "Unknown" };

    return (
        <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium ${cfg.bg}`}>
            <cfg.icon className="h-3.5 w-3.5" />
            {cfg.label}
        </span>
    );
}

export function HomeDashboardClient({ health, videos }: Props) {
    const completed = videos.filter((v) => v.processing_status === "completed");
    const totalVisitors = completed.reduce((s, v) => s + v.visitor_count, 0);
    const totalEvents = completed.reduce((s, v) => s + v.event_count, 0);

    // Derive aggregate conversion rate from videos that have conversion capability
    const convVideos = completed.filter((v) => v.capabilities.conversion);
    const convRate = convVideos.length > 0 ? 12.4 : null; // placeholder until backend exposes aggregate

    const recent = [...videos].sort((a, b) => (b.processed_at ?? 0) - (a.processed_at ?? 0)).slice(0, 5);

    return (
        <div className="page-shell">
            {/* Header */}
            <motion.div {...fade(0)} className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight">Video Intelligence</h1>
                <p className="mt-1 text-muted-foreground">
                    Capability-driven analytics for any camera, any environment.
                </p>
            </motion.div>

            {/* KPI Cards */}
            <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <KpiCard
                    label="Total Videos"
                    value={videos.length}
                    icon={Library}
                    color="text-primary"
                    delay={0.05}
                />
                <KpiCard
                    label="Total Visitors"
                    value={totalVisitors}
                    icon={Users}
                    color="text-indigo-400"
                    delay={0.1}
                />
                <KpiCard
                    label="Total Events"
                    value={totalEvents}
                    icon={Zap}
                    color="text-yellow-400"
                    delay={0.15}
                />
                <KpiCard
                    label="System"
                    value={0}
                    icon={Heart}
                    color={health?.status === "healthy" ? "text-emerald-400" : "text-red-400"}
                    delay={0.2}
                    custom={<HealthBadge status={health?.status} />}
                />
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Recent Videos */}
                <motion.div {...fade(0.25)} className="lg:col-span-2">
                    <div className="glass-card rounded-2xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="font-semibold">Recent Videos</h2>
                            <Link href="/videos" className="flex items-center gap-1 text-xs text-primary hover:underline">
                                View all <ArrowRight className="h-3 w-3" />
                            </Link>
                        </div>
                        {recent.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                                <Library className="h-10 w-10 mb-3 opacity-30" />
                                <p className="text-sm">No videos processed yet.</p>
                                <Link href="/upload" className="mt-3 text-xs text-primary hover:underline">Upload a video →</Link>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {recent.map((video, i) => (
                                    <motion.div
                                        key={video.video_id}
                                        initial={{ opacity: 0, x: -8 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.3 + i * 0.05 }}
                                    >
                                        <Link
                                            href={`/videos/${video.video_id}`}
                                            className="flex items-center gap-3 rounded-xl p-3 transition hover:bg-muted/50"
                                        >
                                            <div className="h-10 w-14 shrink-0 overflow-hidden rounded-lg bg-muted flex items-center justify-center">
                                                <Zap className="h-4 w-4 text-muted-foreground/50" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="truncate text-sm font-medium">{video.name}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {video.visitor_count} visitors · {video.event_count} events
                                                </p>
                                            </div>
                                            <StatusPill status={video.processing_status} />
                                        </Link>
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* System Health */}
                <motion.div {...fade(0.3)} className="flex flex-col gap-4">
                    <div className="glass-card rounded-2xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="font-semibold">System Health</h2>
                            <Link href="/health" className="text-xs text-primary hover:underline">Details →</Link>
                        </div>
                        {health ? (
                            <div className="space-y-3">
                                <HealthBadge status={health.status} />
                                <div className="space-y-2 pt-2">
                                    <HealthRow label="Events" value={health.event_count} />
                                    <HealthRow label="Active Cameras" value={health.active_cameras} />
                                    <HealthRow label="Tracking" value={health.tracking_available ? "✓" : "✗"} highlight={!health.tracking_available} />
                                    <HealthRow label="Analytics" value={health.analytics_available ? "✓" : "✗"} highlight={!health.analytics_available} />
                                    {health.last_event_timestamp && (
                                        <div className="flex items-center gap-2 text-xs text-muted-foreground pt-1">
                                            <Clock className="h-3 w-3" />
                                            Last event: {new Date(health.last_event_timestamp).toLocaleTimeString()}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                <XCircle className="h-8 w-8 mx-auto mb-2 opacity-30" />
                                <p className="text-sm">Backend offline</p>
                            </div>
                        )}
                    </div>

                    {/* Quick Actions */}
                    <div className="glass-card rounded-2xl p-6">
                        <h2 className="font-semibold mb-4">Quick Actions</h2>
                        <div className="space-y-2">
                            <Link
                                href="/upload"
                                className="flex items-center gap-3 rounded-xl bg-primary/10 px-4 py-3 text-sm font-medium text-primary transition hover:bg-primary/20"
                            >
                                <Upload className="h-4 w-4" />
                                Process a Video
                            </Link>
                            <Link
                                href="/videos"
                                className="flex items-center gap-3 rounded-xl bg-muted/60 px-4 py-3 text-sm transition hover:bg-muted"
                            >
                                <Library className="h-4 w-4 text-muted-foreground" />
                                Browse Library
                            </Link>
                            <Link
                                href="/health"
                                className="flex items-center gap-3 rounded-xl bg-muted/60 px-4 py-3 text-sm transition hover:bg-muted"
                            >
                                <Activity className="h-4 w-4 text-muted-foreground" />
                                System Health
                            </Link>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}

function KpiCard({
    label,
    value,
    icon: Icon,
    color,
    delay = 0,
    custom,
}: {
    label: string;
    value: number;
    icon: React.ElementType;
    color: string;
    delay?: number;
    custom?: React.ReactNode;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            className="glass-card rounded-2xl p-5"
        >
            <div className={`flex items-center gap-2 ${color}`}>
                <Icon className="h-4 w-4" />
                <p className="text-xs font-medium">{label}</p>
            </div>
            <div className="mt-3">
                {custom ?? (
                    <p className="text-3xl font-bold tabular-nums">
                        <AnimatedCounter value={value} />
                    </p>
                )}
            </div>
        </motion.div>
    );
}

function HealthRow({
    label,
    value,
    highlight,
}: {
    label: string;
    value: string | number;
    highlight?: boolean;
}) {
    return (
        <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{label}</span>
            <span className={highlight ? "text-red-400 font-medium" : "font-medium"}>{value}</span>
        </div>
    );
}
