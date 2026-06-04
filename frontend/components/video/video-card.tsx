"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Calendar, Users, Zap, CheckCircle, Clock, XCircle, Loader2 } from "lucide-react";
import type { VideoCard } from "@/lib/types";
import { StatusPill } from "@/components/shared/status-pill";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";

const CAPABILITY_LABELS: Record<string, string> = {
    tracking: "Tracking",
    events: "Events",
    heatmap: "Heatmap",
    zones: "Zones",
    dwell: "Dwell",
    queue: "Queue",
    conversion: "Conversion",
    funnel: "Funnel",
    recommendations: "AI Recs",
    insights: "Insights",
};

const statusIcon = {
    completed: <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />,
    running: <Loader2 className="h-3.5 w-3.5 animate-spin text-sky-400" />,
    queued: <Clock className="h-3.5 w-3.5 text-yellow-400" />,
    failed: <XCircle className="h-3.5 w-3.5 text-red-400" />,
};

interface VideoCardComponentProps {
    video: VideoCard;
    index?: number;
    viewMode?: "grid" | "list";
}

export function VideoCardComponent({ video, index = 0, viewMode = "grid" }: VideoCardComponentProps) {
    const capabilities = Object.entries(video.capabilities)
        .filter(([, enabled]) => enabled)
        .map(([cap]) => cap);

    const imgSrc = video.thumbnail_url ? `${api.baseUrl}${video.thumbnail_url}` : null;
    const processedDate = video.processed_at
        ? new Date(video.processed_at * 1000).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })
        : null;

    if (viewMode === "list") {
        return (
            <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.04 }}
            >
                <Link
                    href={`/videos/${video.video_id}`}
                    className="flex items-center gap-4 rounded-xl border border-border bg-card/60 px-5 py-4 transition hover:border-primary/30 hover:bg-primary/5"
                >
                    <div className="h-14 w-20 shrink-0 overflow-hidden rounded-lg bg-muted">
                        {imgSrc ? (
                            <img src={imgSrc} alt={video.name} className="h-full w-full object-cover" />
                        ) : (
                            <div className="flex h-full items-center justify-center text-muted-foreground">
                                <Zap className="h-5 w-5" />
                            </div>
                        )}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="truncate font-semibold">{video.name}</p>
                        <div className="mt-1 flex flex-wrap gap-1">
                            {capabilities.slice(0, 5).map((cap) => (
                                <span key={cap} className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">
                                    {CAPABILITY_LABELS[cap] ?? cap}
                                </span>
                            ))}
                            {capabilities.length > 5 && (
                                <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                                    +{capabilities.length - 5}
                                </span>
                            )}
                        </div>
                    </div>
                    <div className="hidden shrink-0 items-center gap-6 sm:flex text-sm text-muted-foreground">
                        <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />{video.visitor_count}</span>
                        <span className="flex items-center gap-1"><Zap className="h-3.5 w-3.5" />{video.event_count}</span>
                        <StatusPill status={video.processing_status} />
                    </div>
                </Link>
            </motion.div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.06 }}
            whileHover={{ y: -2 }}
        >
            <Link
                href={`/videos/${video.video_id}`}
                className="group flex flex-col overflow-hidden rounded-2xl border border-border bg-card/60 transition hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
            >
                {/* Thumbnail */}
                <div className="relative h-40 w-full overflow-hidden bg-muted">
                    {imgSrc ? (
                        <img
                            src={imgSrc}
                            alt={video.name}
                            className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                        />
                    ) : (
                        <div className="flex h-full items-center justify-center">
                            <Zap className="h-8 w-8 text-muted-foreground/40" />
                        </div>
                    )}
                    <div className="absolute right-3 top-3 flex items-center gap-1.5 rounded-full bg-black/50 px-2.5 py-1 backdrop-blur-sm">
                        {statusIcon[video.processing_status]}
                        <span className="text-xs font-medium capitalize text-white">{video.processing_status}</span>
                    </div>
                </div>

                {/* Body */}
                <div className="flex flex-1 flex-col gap-3 p-4">
                    <div>
                        <p className="font-semibold leading-snug">{video.name}</p>
                        {processedDate && (
                            <p className="mt-0.5 flex items-center gap-1 text-xs text-muted-foreground">
                                <Calendar className="h-3 w-3" />
                                {processedDate}
                            </p>
                        )}
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />{video.visitor_count} visitors</span>
                        <span className="flex items-center gap-1"><Zap className="h-3.5 w-3.5" />{video.event_count} events</span>
                    </div>

                    <div className="flex flex-wrap gap-1">
                        {capabilities.slice(0, 4).map((cap) => (
                            <span key={cap} className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">
                                {CAPABILITY_LABELS[cap] ?? cap}
                            </span>
                        ))}
                        {capabilities.length > 4 && (
                            <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                                +{capabilities.length - 4} more
                            </span>
                        )}
                    </div>
                </div>
            </Link>
        </motion.div>
    );
}
