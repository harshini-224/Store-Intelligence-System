"use client";

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, Filter, Search, User, ArrowRight } from "lucide-react";
import type { VideoDetail, EventRecord } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";
import { cn } from "@/lib/utils";

type Props = { video: VideoDetail };

function formatTime(ts: string | undefined): string {
    if (!ts) return "—";
    const d = new Date(ts);
    if (isNaN(d.getTime())) return ts;
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function eventColor(type: string): string {
    const t = type.toLowerCase();
    if (t.includes("enter") || t.includes("join")) return "bg-emerald-400";
    if (t.includes("exit") || t.includes("leave")) return "bg-slate-400";
    if (t.includes("queue")) return "bg-yellow-400";
    if (t.includes("purchase") || t.includes("convert")) return "bg-primary";
    if (t.includes("zone")) return "bg-indigo-400";
    return "bg-muted-foreground";
}

const EVENT_TYPES = ["All", "enter", "exit", "zone", "queue", "purchase"];

export function EventTimelineWidget({ video }: Props) {
    const [search, setSearch] = useState("");
    const [typeFilter, setTypeFilter] = useState("All");
    const [limit, setLimit] = useState(30);

    const events: EventRecord[] = video.events ?? [];

    const filtered = useMemo(() => {
        return events.filter((e) => {
            const type = (e.event_type ?? e.event ?? "").toLowerCase();
            const matchType = typeFilter === "All" || type.includes(typeFilter);
            const matchSearch = !search || type.includes(search.toLowerCase()) ||
                String(e.visitor_id ?? "").includes(search) ||
                (e.zone_id ?? "").toLowerCase().includes(search.toLowerCase());
            return matchType && matchSearch;
        });
    }, [events, typeFilter, search]);

    const visible = filtered.slice(0, limit);

    if (events.length === 0) return <EmptyState message="No events recorded for this video." />;

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <SectionHeader title="Event Timeline" subtitle={`${filtered.length} of ${events.length} events`} icon={Clock} />

            {/* Controls */}
            <div className="mt-4 flex flex-wrap items-center gap-3">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search events…"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full rounded-lg border border-border bg-muted/40 py-2 pl-8 pr-4 text-sm outline-none focus:ring-1 focus:ring-primary"
                    />
                </div>
                <div className="flex items-center gap-1 rounded-lg bg-muted/40 p-1">
                    <Filter className="ml-1 h-3.5 w-3.5 text-muted-foreground" />
                    {EVENT_TYPES.map((t) => (
                        <button
                            key={t}
                            onClick={() => setTypeFilter(t)}
                            className={cn(
                                "rounded-md px-3 py-1 text-xs transition",
                                typeFilter === t ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                            )}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </div>

            {/* Timeline */}
            <div className="mt-5 space-y-1">
                <AnimatePresence initial={false}>
                    {visible.map((event, i) => {
                        const type = event.event_type ?? event.event ?? "Unknown";
                        const dot = eventColor(type);
                        return (
                            <motion.div
                                key={event.event_id ?? i}
                                initial={{ opacity: 0, x: -8 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0 }}
                                transition={{ delay: Math.min(i * 0.02, 0.3) }}
                                className="flex items-start gap-3 rounded-xl px-4 py-2.5 transition hover:bg-muted/40"
                            >
                                {/* dot + line */}
                                <div className="flex flex-col items-center pt-1.5">
                                    <span className={`h-2 w-2 rounded-full ${dot}`} />
                                    {i < visible.length - 1 && <span className="mt-1 h-4 w-px bg-border" />}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm font-medium capitalize">{type.replace(/_/g, " ")}</span>
                                        {event.zone_id && (
                                            <span className="flex items-center gap-0.5 text-xs text-muted-foreground">
                                                <ArrowRight className="h-3 w-3" />
                                                {event.zone_id}
                                            </span>
                                        )}
                                    </div>
                                    <div className="mt-0.5 flex items-center gap-3 text-xs text-muted-foreground">
                                        <span className="flex items-center gap-1">
                                            <Clock className="h-3 w-3" />
                                            {formatTime(event.timestamp)}
                                        </span>
                                        {event.visitor_id !== undefined && (
                                            <span className="flex items-center gap-1">
                                                <User className="h-3 w-3" />
                                                Visitor #{event.visitor_id}
                                            </span>
                                        )}
                                        {event.confidence !== undefined && (
                                            <span>Conf: {(event.confidence * 100).toFixed(0)}%</span>
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>
            </div>

            {filtered.length > limit && (
                <button
                    onClick={() => setLimit((l) => l + 30)}
                    className="mt-4 w-full rounded-xl border border-border py-2.5 text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground"
                >
                    Show more ({filtered.length - limit} remaining)
                </button>
            )}

            {visible.length === 0 && (
                <EmptyState message="No events match your filter." />
            )}
        </motion.div>
    );
}
