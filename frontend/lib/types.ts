export type Capability =
  | "tracking"
  | "events"
  | "heatmap"
  | "zones"
  | "dwell"
  | "queue"
  | "conversion"
  | "funnel"
  | "recommendations"
  | "insights";

export type CapabilityMap = Record<Capability, boolean>;

export type HealthStatus = {
  status: "healthy" | "degraded" | "offline";
  event_count: number;
  last_event_timestamp: string | null;
  stale_feed: boolean;
  active_cameras: number;
  analytics_available: boolean;
  tracking_available: boolean;
  events_available: boolean;
};

export type ZoneMetric = {
  visitors: number;
  total_dwell_time: number;
};

export type QueueMetrics = {
  queue_joins?: number;
  queue_abandons?: number;
  queue_conversions?: number;
  abandonment_rate?: number;
  abandonment_rate_percent?: number;
  current_queue_depth?: number;
  average_queue_depth?: number;
  max_queue_depth?: number;
  average_queue_wait_time?: number;
  max_queue_wait_time?: number;
};

export type ConversionMetrics = {
  total_visitors?: number;
  converted_visitors?: number;
  billing_zone_visitors?: number;
  conversion_rate?: number;
  billing_zone_rate?: number;
};

export type FunnelMetrics = {
  entry?: number;
  zone_visit?: number;
  billing_queue?: number;
  purchase?: number;
  entry_count?: number;
  zone_visit_count?: number;
  billing_queue_count?: number;
  purchase_count?: number;
  dropoffs?: Record<string, number>;
  rates?: Record<string, number>;
};

export type AnalyticsSummary = Record<string, unknown> & {
  _queue_metrics?: QueueMetrics;
  _conversion_metrics?: ConversionMetrics;
  _funnel_metrics?: FunnelMetrics;
};

export type EventRecord = {
  event_id?: string;
  event_type?: string;
  event?: string;
  timestamp?: string;
  frame?: number;
  visitor_id?: number;
  zone_id?: string | null;
  camera_id?: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
};

export type VideoCard = {
  video_id: string;
  name: string;
  processing_status: "queued" | "running" | "completed" | "failed";
  processed_at: number | null;
  visitor_count: number;
  event_count: number;
  capabilities: CapabilityMap;
  thumbnail_url: string | null;
};

export type VideoDetail = VideoCard & {
  analytics: AnalyticsSummary;
  zones: Record<string, ZoneMetric>;
  events: EventRecord[];
  tracks_count: number;
  artifacts: {
    tracked_video: string | null;
    detected_video: string | null;
    heatmap: string | null;
  };
};

export type ProcessingStage =
  | "Tracking"
  | "Event Generation"
  | "Zone Analytics"
  | "Conversion Analytics"
  | "Heatmap";

export type ProcessingJob = {
  id: string;
  videoName: string;
  videoId?: string;
  status: "queued" | "running" | "completed" | "failed";
  progress: number;
  currentStage: ProcessingStage;
  logs: string[];
  startedAt: number;
  completedAt?: number;
  estimatedSeconds?: number;
  remainingSeconds?: number;
  error?: string;
  summary?: {
    events: number;
    visitors: number;
    tracks: number;
    heatmaps: number;
  };
};
