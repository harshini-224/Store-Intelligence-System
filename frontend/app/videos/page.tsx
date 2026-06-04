"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Grid, List, SlidersHorizontal } from "lucide-react";
import { useVideos } from "@/lib/hooks";
import { useVideoStore } from "@/stores/useVideoStore";
import { VideoCardComponent } from "@/components/video/video-card";
import { EmptyState } from "@/components/shared/empty-state";
import { cn } from "@/lib/utils";

const SORT_OPTIONS = [
    { value: "recent", label: "Most Recent" },
    { value: "visitors", label: "Most Visitors" },
    { value: "events", label: "Most Events" },
] as const;

const CAPABILITY_FILTER_OPTIONS = [
    { value: "", label: "All" },
    { value: "heatmap", label: "Heatmap" },
    { value: "queue", label: "Queue" },
    { value: "conversion", label: "Conversion" },
    { value: "funnel", label: "Funnel" },
];

export default function VideosPage() {
    const { data: videos = [], isLoading, isError } = useVideos();
    const { query, sort, viewMode, setQuery, setSort, setViewMode } = useVideoStore();
    const [capFilter, setCapFilter] = useState("");

    const filtered = videos
        .filter((v) => {
            const matchQuery = !query || v.name.toLowerCase().includes(query.toLowerCase()) || v.video_id.toLowerCase().includes(query.toLowerCase());
            const matchCap = !capFilter || v.capabilities[capFilter as keyof typeof v.capabilities];
            return matchQuery && matchCap;
        })
        .sort((a, b) => {
            if (sort === "visitors") return b.visitor_count - a.visitor_count;
            if (sort === "events") return b.event_count - a.event_count;
            return (b.processed_at ?? 0) - (a.processed_at ?? 0);
        });

    return (
        <div className="page-shell">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
                <h1 className="text-3xl font-bold tracking-tight">Video Library</h1>
                <p className="mt-1 text-muted-foreground">Browse and explore your processed analytics videos.</p>
            </motion.div>

            {/* Controls */}
            <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.08 }}
                className="mb-6 flex flex-wrap items-center gap-3"
            >
                {/* Search */}
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search videos…"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="h-10 w-full rounded-xl border border-border bg-card/60 pl-9 pr-4 text-sm outline-none focus:ring-1 focus:ring-primary"
                    />
                </div>

                {/* Sort */}
                <div className="flex items-center gap-1.5 rounded-xl border border-border bg-card/60 px-2 py-1">
                    <SlidersHorizontal className="h-3.5 w-3.5 text-muted-foreground ml-1" />
                    {SORT_OPTIONS.map((o) => (
                        <button
                            key={o.value}
                            onClick={() => setSort(o.value)}
                            className={cn(
                                "rounded-lg px-3 py-1.5 text-xs transition",
                                sort === o.value ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                            )}
                        >
                            {o.label}
                        </button>
                    ))}
                </div>

                {/* Capability filter */}
                <div className="flex items-center gap-1 rounded-xl border border-border bg-card/60 px-2 py-1">
                    {CAPABILITY_FILTER_OPTIONS.map((o) => (
                        <button
                            key={o.value}
                            onClick={() => setCapFilter(o.value)}
                            className={cn(
                                "rounded-lg px-3 py-1.5 text-xs transition",
                                capFilter === o.value ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                            )}
                        >
                            {o.label}
                        </button>
                    ))}
                </div>

                {/* View mode */}
                <div className="flex rounded-xl border border-border bg-card/60 p-1">
                    <button onClick={() => setViewMode("grid")} className={cn("rounded-lg p-1.5 transition", viewMode === "grid" ? "bg-primary text-primary-foreground" : "text-muted-foreground")}>
                        <Grid className="h-4 w-4" />
                    </button>
                    <button onClick={() => setViewMode("list")} className={cn("rounded-lg p-1.5 transition", viewMode === "list" ? "bg-primary text-primary-foreground" : "text-muted-foreground")}>
                        <List className="h-4 w-4" />
                    </button>
                </div>
            </motion.div>

            {/* Results count */}
            <p className="mb-4 text-sm text-muted-foreground">
                {isLoading ? "Loading…" : `${filtered.length} video${filtered.length !== 1 ? "s" : ""}`}
            </p>

            {/* Loading skeleton */}
            {isLoading && (
                <div className={cn("grid gap-5", viewMode === "grid" ? "sm:grid-cols-2 lg:grid-cols-3" : "")}>
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="h-64 animate-pulse rounded-2xl bg-muted" />
                    ))}
                </div>
            )}

            {/* Error */}
            {isError && (
                <div className="text-center py-16 text-muted-foreground">
                    <p>Could not connect to backend. Make sure the API is running.</p>
                </div>
            )}

            {/* Grid */}
            {!isLoading && !isError && filtered.length === 0 && (
                <EmptyState message="No videos match your search or filter." />
            )}

            {!isLoading && !isError && filtered.length > 0 && (
                <div className={cn(
                    "gap-5",
                    viewMode === "grid" ? "grid sm:grid-cols-2 lg:grid-cols-3" : "flex flex-col"
                )}>
                    {filtered.map((video, i) => (
                        <VideoCardComponent key={video.video_id} video={video} index={i} viewMode={viewMode} />
                    ))}
                </div>
            )}
        </div>
    );
}
