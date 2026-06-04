"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { Upload, Film, X, CheckCircle, AlertCircle } from "lucide-react";
import { ProcessingDialog } from "@/components/processing/processing-dialog";
import { useProcessingStore } from "@/stores/useProcessingStore";
import { api } from "@/lib/api";

type UploadState = "idle" | "ready" | "uploading" | "success" | "error";

export default function UploadPage() {
    const router = useRouter();
    const [file, setFile] = useState<File | null>(null);
    const [state, setState] = useState<UploadState>("idle");
    const [errorMsg, setErrorMsg] = useState("");
    const [dragOver, setDragOver] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const { startJob, dialogOpen } = useProcessingStore();

    const handleFile = (f: File) => {
        if (!f.type.startsWith("video/")) {
            setErrorMsg("Please select a video file.");
            setState("error");
            return;
        }
        setFile(f);
        setState("ready");
        setErrorMsg("");
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files[0];
        if (f) handleFile(f);
    };

    const handleProcess = async () => {
        if (!file) return;
        setState("uploading");

        try {
            const formData = new FormData();
            formData.append("file", file);
            const res = await fetch(`${api.baseUrl}/ingest`, {
                method: "POST",
                body: formData,
            });
            if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
            const data = await res.json();
            // Start the real processing job — the dialog will connect via SSE
            startJob(file.name, data.job_id, data.video_id);
            setState("success");
        } catch (err) {
            const message = err instanceof Error ? err.message : "Upload failed";
            setErrorMsg(message);
            setState("error");
        }
    };

    return (
        <div className="page-shell max-w-2xl">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold tracking-tight">Process Video</h1>
                <p className="mt-1 text-muted-foreground">
                    Upload a video to extract visitor tracking, events, heatmaps, and analytics in demo mode.
                </p>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
            >
                {/* Drop zone */}
                <div
                    onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={handleDrop}
                    onClick={() => inputRef.current?.click()}
                    className={[
                        "relative flex min-h-[280px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed transition",
                        dragOver ? "border-primary bg-primary/10" : "border-border bg-card/60 hover:border-primary/50 hover:bg-muted/50",
                    ].join(" ")}
                >
                    <input
                        ref={inputRef}
                        type="file"
                        accept="video/*"
                        className="sr-only"
                        onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
                    />
                    <AnimatePresence mode="wait">
                        {file ? (
                            <motion.div
                                key="file"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                className="flex flex-col items-center gap-3 text-center"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <div className="rounded-2xl bg-primary/10 p-4">
                                    <Film className="h-8 w-8 text-primary" />
                                </div>
                                <div>
                                    <p className="font-semibold">{file.name}</p>
                                    <p className="text-sm text-muted-foreground">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                                </div>
                                <button
                                    onClick={() => { setFile(null); setState("idle"); }}
                                    className="flex items-center gap-1 rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground transition hover:bg-destructive/10 hover:text-destructive"
                                >
                                    <X className="h-3 w-3" /> Remove
                                </button>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="empty"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="flex flex-col items-center gap-3 text-center"
                            >
                                <div className="rounded-2xl bg-muted p-4">
                                    <Upload className="h-8 w-8 text-muted-foreground" />
                                </div>
                                <div>
                                    <p className="font-semibold">Drag & drop a video file</p>
                                    <p className="text-sm text-muted-foreground">or click to browse — retail, warehouse, airport, hospital, and more</p>
                                </div>
                                <p className="text-xs text-muted-foreground">Supports MP4, MOV, AVI, MKV</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {state === "error" && (
                    <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-4 flex items-center gap-2 rounded-xl border border-red-400/30 bg-red-400/10 px-4 py-3 text-sm text-red-400"
                    >
                        <AlertCircle className="h-4 w-4 shrink-0" />
                        {errorMsg}
                    </motion.div>
                )}

                {/* Capability info */}
                <div className="mt-6 rounded-2xl border border-border bg-muted/40 p-5">
                    <p className="text-sm font-semibold mb-3">What gets extracted</p>
                    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                        {[
                            "YOLO-Powered Tracking",
                            "Visitor Tracking",
                            "Zone Analytics",
                            "Dwell Time",
                            "Queue Analysis",
                            "Conversion Rate",
                            "Funnel Metrics",
                            "Heatmap Generation",
                            "AI Recommendations",
                        ].map((cap) => (
                            <div key={cap} className="flex items-center gap-2 text-xs text-muted-foreground">
                                <CheckCircle className="h-3 w-3 text-primary shrink-0" />
                                {cap}
                            </div>
                        ))}
                    </div>
                </div>

                <motion.button
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    disabled={!file || dialogOpen}
                    onClick={handleProcess}
                    className="mt-6 w-full rounded-xl bg-primary py-4 text-base font-semibold text-primary-foreground shadow-lg shadow-primary/20 transition disabled:opacity-50 disabled:pointer-events-none hover:bg-primary/90"
                >
                    {dialogOpen ? "Processing…" : "Process Video"}
                </motion.button>
            </motion.div>

            <ProcessingDialog />
        </div>
    );
}
