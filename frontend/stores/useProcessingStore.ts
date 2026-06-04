import { create } from "zustand";
import type { ProcessingJob, ProcessingStage } from "@/lib/types";

const stages: ProcessingStage[] = [
  "Tracking",
  "Event Generation",
  "Zone Analytics",
  "Conversion Analytics",
  "Heatmap",
];

type ProcessingStore = {
  activeJob: ProcessingJob | null;
  dialogOpen: boolean;
  /** Called after POST /ingest responds with job_id + video_id */
  startJob: (videoName: string, jobId: string, videoId: string) => void;
  /** Update the active job from an SSE progress event */
  updateFromSSE: (data: {
    status: string;
    progress: number;
    current_stage: string;
    logs: string[];
    summary?: { events: number; visitors: number; tracks: number; heatmaps: number } | null;
    completed_at?: number | null;
    estimated_seconds?: number;
    remaining_seconds?: number;
    error?: string | null;
  }) => void;
  closeDialog: () => void;
};

export const useProcessingStore = create<ProcessingStore>((set, get) => ({
  activeJob: null,
  dialogOpen: false,

  startJob: (videoName, jobId, videoId) => {
    set({
      dialogOpen: true,
      activeJob: {
        id: jobId,
        videoName,
        videoId,
        status: "running",
        progress: 0,
        currentStage: stages[0],
        logs: ["Queued video processing job."],
        startedAt: Date.now(),
      },
    });
  },

  updateFromSSE: (data) => {
    const job = get().activeJob;
    if (!job) return;

    set({
      activeJob: {
        ...job,
        status: data.status as ProcessingJob["status"],
        progress: data.progress,
        currentStage: (data.current_stage || job.currentStage) as ProcessingStage,
        logs: data.logs.length > 0 ? data.logs : job.logs,
        completedAt: data.completed_at ?? job.completedAt,
        estimatedSeconds: data.estimated_seconds,
        remainingSeconds: data.remaining_seconds,
        error: data.error ?? job.error,
        summary: data.summary ?? job.summary,
      },
    });
  },

  closeDialog: () => set({ dialogOpen: false }),
}));

export const processingStages = stages;
