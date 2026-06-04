"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ZoomIn, ZoomOut, Maximize2, Download, Flame } from "lucide-react";
import type { VideoDetail } from "@/lib/types";
import { SectionHeader } from "@/components/shared/section-header";
import { EmptyState } from "@/components/shared/empty-state";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

type Props = { video: VideoDetail };

export function HeatmapWidget({ video }: Props) {
    const [zoom, setZoom] = useState(1);
    const [fullscreen, setFullscreen] = useState(false);
    const imgRef = useRef<HTMLDivElement>(null);

    if (!video.capabilities.heatmap || !video.artifacts.heatmap) {
        return <EmptyState message="No heatmap available for this video." />;
    }

    const src = `${api.baseUrl}${video.artifacts.heatmap}`;

    const handleDownload = () => {
        const a = document.createElement("a");
        a.href = src;
        a.download = `${video.video_id}_heatmap.jpg`;
        a.click();
    };

    return (
        <>
            <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card rounded-2xl p-6"
            >
                <div className="flex items-start justify-between">
                    <SectionHeader title="Heatmap" subtitle="Visitor movement density visualization" icon={Flame} />
                    <div className="flex items-center gap-1.5">
                        <ToolButton onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))} label="Zoom out">
                            <ZoomOut className="h-4 w-4" />
                        </ToolButton>
                        <ToolButton onClick={() => setZoom((z) => Math.min(3, z + 0.25))} label="Zoom in">
                            <ZoomIn className="h-4 w-4" />
                        </ToolButton>
                        <ToolButton onClick={() => setFullscreen(true)} label="Fullscreen">
                            <Maximize2 className="h-4 w-4" />
                        </ToolButton>
                        <ToolButton onClick={handleDownload} label="Download">
                            <Download className="h-4 w-4" />
                        </ToolButton>
                    </div>
                </div>

                <div className="mt-4 overflow-hidden rounded-xl border border-border bg-black/20">
                    <div
                        ref={imgRef}
                        className="overflow-auto"
                        style={{ maxHeight: 400 }}
                    >
                        <motion.img
                            src={src}
                            alt="Heatmap"
                            className="h-auto w-full object-contain origin-top-left transition-transform duration-200"
                            style={{ transform: `scale(${zoom})`, transformOrigin: "top left" }}
                            draggable={false}
                        />
                    </div>
                </div>

                <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                    <span>Zoom: {Math.round(zoom * 100)}%</span>
                    <span className="flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-blue-500" />Cold
                        <span className="ml-2 h-2 w-2 rounded-full bg-green-500" />Medium
                        <span className="ml-2 h-2 w-2 rounded-full bg-red-500" />Hot
                    </span>
                </div>
            </motion.div>

            {/* Fullscreen */}
            <AnimatePresence>
                {fullscreen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4 backdrop-blur-md"
                        onClick={() => setFullscreen(false)}
                    >
                        <motion.img
                            initial={{ scale: 0.92 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0.92 }}
                            src={src}
                            alt="Heatmap fullscreen"
                            className="max-h-[90vh] max-w-[90vw] rounded-xl object-contain shadow-2xl"
                            onClick={(e) => e.stopPropagation()}
                        />
                        <button
                            className="absolute right-6 top-6 rounded-full bg-white/10 p-2 text-white transition hover:bg-white/20"
                            onClick={() => setFullscreen(false)}
                        >
                            ✕
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}

function ToolButton({
    children,
    onClick,
    label,
}: {
    children: React.ReactNode;
    onClick: () => void;
    label: string;
}) {
    return (
        <button
            title={label}
            onClick={onClick}
            className={cn(
                "flex h-8 w-8 items-center justify-center rounded-lg bg-muted/60 text-muted-foreground transition",
                "hover:bg-muted hover:text-foreground"
            )}
        >
            {children}
        </button>
    );
}
