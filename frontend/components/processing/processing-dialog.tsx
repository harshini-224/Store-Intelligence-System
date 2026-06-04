"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Check, Loader2, Play, Sparkles, Clock } from "lucide-react";
import { motion } from "framer-motion";
import { Dialog } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { processingStages, useProcessingStore } from "@/stores/useProcessingStore";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";

export function ProcessingDialog() {
  const router = useRouter();
  const { activeJob, dialogOpen, closeDialog, updateFromSSE } = useProcessingStore();
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Connect to SSE progress stream
  useEffect(() => {
    if (!dialogOpen || !activeJob || activeJob.status !== "running") return;

    const jobId = activeJob.id;
    const url = `${api.baseUrl}/ingest/${jobId}/progress`;
    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        updateFromSSE(data);
      } catch {
        // ignore parse errors
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [activeJob?.id, dialogOpen, activeJob?.status, updateFromSSE]);

  // Auto-scroll logs
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [activeJob?.logs]);

  // Auto redirect to the specific video analytics page
  useEffect(() => {
    if (activeJob?.status === "completed" && activeJob.videoId) {
      const timeout = setTimeout(() => {
        closeDialog();
        router.push(`/videos/${activeJob.videoId}`);
      }, 5000); // 5s to allow user to see summary
      return () => clearTimeout(timeout);
    }
  }, [activeJob?.status, activeJob?.videoId, closeDialog, router]);

  if (!activeJob) return null;

  const activeIndex = processingStages.indexOf(activeJob.currentStage);
  const completed = activeJob.status === "completed";
  const failed = activeJob.status === "failed";

  const handleManualNav = () => {
    closeDialog();
    if (activeJob.videoId) {
      router.push(`/videos/${activeJob.videoId}`);
    } else {
      router.push("/videos");
    }
  };

  return (
    <Dialog open={dialogOpen} onOpenChange={closeDialog}>
      <div className="relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(45,212,191,.25),transparent_28%),radial-gradient(circle_at_80%_10%,rgba(217,70,239,.18),transparent_24%)]" />
        <div className="relative p-6 md:p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-primary">Processing Experience</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight">Video intelligence run</h2>
              <p className="mt-2 max-w-xl text-sm text-muted-foreground">
                {failed
                  ? "An error occurred during processing."
                  : "The pipeline moves through tracking, events, analytics, and artifact generation."}
              </p>
            </div>
            <motion.div
              className={cn(
                "grid h-32 w-32 place-items-center rounded-full border bg-primary/10",
                failed ? "border-red-400/30" : "border-primary/30"
              )}
              animate={{ rotate: completed || failed ? 0 : 360 }}
              transition={{ duration: 6, repeat: completed || failed ? 0 : Infinity, ease: "linear" }}
            >
              <div className="grid h-24 w-24 place-items-center rounded-full bg-background/80 text-2xl font-semibold">
                {activeJob.progress}%
              </div>
            </motion.div>
          </div>

          <div className="mt-8 rounded-xl border border-border bg-background/70 p-4">
            <div className="mb-3 flex items-center justify-between text-sm">
              <span className="font-medium">
                {completed
                  ? "Processing complete"
                  : failed
                    ? "Processing failed"
                    : `${activeJob.currentStage} running`}
              </span>
              <span className="text-muted-foreground">{activeJob.videoName}</span>
            </div>
            <Progress value={activeJob.progress} className="h-3" />
            {(activeJob.remainingSeconds ?? 0) > 0 && activeJob.status === "running" && (
              <div className="mt-2 flex items-center justify-end gap-1.5 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span>Estimated: {Math.floor(activeJob.remainingSeconds! / 60)}m {activeJob.remainingSeconds! % 60}s remaining</span>
              </div>
            )}
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-2">
            {processingStages.map((stage, index) => {
              const done = completed || index < activeIndex;
              const running = !completed && !failed && index === activeIndex;
              return (
                <div
                  key={stage}
                  className={cn(
                    "rounded-xl border border-border bg-background/70 p-4",
                    done && "border-primary/30 bg-primary/10",
                    running && "border-sky-400/40 bg-sky-400/10"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{stage}</span>
                    {done ? (
                      <Check className="h-4 w-4 text-primary" />
                    ) : running ? (
                      <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
                    ) : (
                      <Play className="h-4 w-4 text-muted-foreground" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-[1fr_.8fr]">
            <div className="rounded-xl border border-border bg-background/70 p-4">
              <p className="mb-3 text-sm font-medium">Interactive Pipeline Logs</p>
              <div
                ref={logContainerRef}
                className="max-h-60 space-y-1.5 overflow-auto text-[11px] text-muted-foreground font-mono leading-relaxed scrollbar-thin scrollbar-thumb-muted"
              >
                {activeJob.logs.map((log, index) => {
                  const isStage = log.includes("▶ Starting");
                  const isSuccess = log.includes("✓") || log.includes("successfully");
                  const isError = log.includes("ERROR") || log.includes("⚠") || log.includes("failed");

                  return (
                    <p
                      key={`${log}-${index}`}
                      className={cn(
                        "break-all",
                        isStage && "text-sky-400 font-bold mt-2",
                        isSuccess && "text-emerald-400",
                        isError && "text-red-400"
                      )}
                    >
                      <span className="opacity-40 select-none mr-2">{String(index + 1).padStart(3, "0")}</span>
                      {log}
                    </p>
                  );
                })}
              </div>
            </div>
            <div className={cn(
              "rounded-xl border p-4",
              failed ? "border-red-400/20 bg-red-400/10" : "border-primary/20 bg-primary/10"
            )}>
              <div className={cn("flex items-center gap-2", failed ? "text-red-400" : "text-primary")}>
                <Sparkles className="h-4 w-4" />
                <p className="font-medium">{failed ? "Error details" : "Completion summary"}</p>
              </div>
              {failed ? (
                <p className="mt-3 text-sm text-red-400">{activeJob.error || "An unknown error occurred."}</p>
              ) : (
                <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                  <SummaryMetric
                    label="Events"
                    value={activeJob.summary?.events != null ? String(activeJob.summary.events) : "—"}
                  />
                  <SummaryMetric
                    label="Visitors"
                    value={activeJob.summary?.visitors != null ? String(activeJob.summary.visitors) : "—"}
                  />
                  <SummaryMetric
                    label="Tracks"
                    value={activeJob.summary?.tracks != null ? String(activeJob.summary.tracks) : "—"}
                  />
                  <SummaryMetric
                    label="Heatmaps"
                    value={activeJob.summary?.heatmaps != null ? String(activeJob.summary.heatmaps) : "—"}
                  />
                </div>
              )}
              {(completed || failed) ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  <Button size="sm" onClick={handleManualNav}>
                    {completed ? "View Analytics" : "Go to Library"}
                  </Button>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </Dialog>
  );
}

function SummaryMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-background/70 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-xl font-semibold">{value}</p>
    </div>
  );
}
