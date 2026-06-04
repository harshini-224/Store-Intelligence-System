"use client";

import { use } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowLeft, Zap, Users, CheckCircle, XCircle, Clock } from "lucide-react";
import { useVideo } from "@/lib/hooks";
import { getRegisteredWidgets } from "@/lib/registry";
import { StatusPill } from "@/components/shared/status-pill";
import { api } from "@/lib/api";

type Props = { params: Promise<{ videoId: string }> };

export default function VideoDetailPage({ params }: Props) {
    const { videoId } = use(params);
    const { data: video, isLoading, isError } = useVideo(videoId);

    if (isLoading) {
        return (
            <div className="page-shell">
                <div className="space-y-4">
                    <div className="h-8 w-48 animate-pulse rounded-lg bg-muted" />
                    <div className="h-48 animate-pulse rounded-2xl bg-muted" />
                    {Array.from({ length: 3 }).map((_, i) => (
                        <div key={i} className="h-64 animate-pulse rounded-2xl bg-muted" />
                    ))}
                </div>
            </div>
        );
    }

    if (isError || !video) {
        return (
            <div className="page-shell text-center py-24">
                <XCircle className="mx-auto h-12 w-12 text-muted-foreground/30 mb-4" />
                <p className="text-muted-foreground">Video not found or backend unavailable.</p>
                <Link href="/videos" className="mt-4 inline-block text-sm text-primary hover:underline">
                    ← Back to library
                </Link>
            </div>
        );
    }

    const widgets = getRegisteredWidgets(video);
    const processedDate = video.processed_at
        ? new Date(video.processed_at * 1000).toLocaleString()
        : null;

    return (
        <div className="page-shell">
            {/* Back */}
            <Link
                href="/videos"
                className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition hover:text-foreground"
            >
                <ArrowLeft className="h-4 w-4" />
                Video Library
            </Link>

            {/* Header Card */}
            <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card mb-8 rounded-2xl p-6"
            >
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold">{video.name}</h1>
                        <p className="mt-1 text-sm text-muted-foreground font-mono">{video.video_id}</p>
                    </div>
                    <StatusPill status={video.processing_status} />
                </div>

                <div className="mt-5 grid gap-4 sm:grid-cols-4">
                    <MetricPill label="Visitors" value={video.visitor_count} icon={Users} />
                    <MetricPill label="Events" value={video.event_count} icon={Zap} />
                    <MetricPill label="Tracks" value={video.tracks_count} icon={CheckCircle} />
                    {processedDate && (
                        <div className="rounded-xl bg-muted/40 px-4 py-3">
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Clock className="h-3.5 w-3.5" />
                                <p className="text-xs">Processed</p>
                            </div>
                            <p className="mt-1 text-sm font-semibold">{processedDate}</p>
                        </div>
                    )}
                </div>

                {/* Capabilities */}
                <div className="mt-5 flex flex-wrap gap-2">
                    {Object.entries(video.capabilities).map(([cap, enabled]) => (
                        <span
                            key={cap}
                            className={[
                                "rounded-full px-3 py-1 text-xs font-medium capitalize",
                                enabled
                                    ? "bg-primary/15 text-primary"
                                    : "bg-muted text-muted-foreground line-through",
                            ].join(" ")}
                        >
                            {cap}
                        </span>
                    ))}
                </div>

                {/* Artifact links */}
                {video.artifacts.tracked_video && (
                    <div className="mt-5 flex flex-wrap gap-2">
                        <a
                            href={`${api.baseUrl}${video.artifacts.tracked_video}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="rounded-lg bg-muted/60 px-3 py-1.5 text-xs text-muted-foreground transition hover:bg-muted hover:text-foreground"
                        >
                            📹 Tracked Video
                        </a>
                        {video.artifacts.detected_video && (
                            <a
                                href={`${api.baseUrl}${video.artifacts.detected_video}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="rounded-lg bg-muted/60 px-3 py-1.5 text-xs text-muted-foreground transition hover:bg-muted hover:text-foreground"
                            >
                                🎯 Detected Video
                            </a>
                        )}
                    </div>
                )}
            </motion.div>

            {/* Widget Grid */}
            {widgets.length === 0 ? (
                <div className="text-center py-16 text-muted-foreground">
                    <p>No analytics widgets available for this video.</p>
                </div>
            ) : (
                <div className="space-y-6">
                    {widgets.map(({ capability, Component }, i) => (
                        <motion.div
                            key={capability}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 + i * 0.05 }}
                        >
                            <Component video={video} />
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}

function MetricPill({
    label,
    value,
    icon: Icon,
}: {
    label: string;
    value: number;
    icon: React.ElementType;
}) {
    return (
        <div className="rounded-xl bg-muted/40 px-4 py-3">
            <div className="flex items-center gap-2 text-muted-foreground">
                <Icon className="h-3.5 w-3.5" />
                <p className="text-xs">{label}</p>
            </div>
            <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
        </div>
    );
}
