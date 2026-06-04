import type { HealthStatus, VideoCard, VideoDetail, EventRecord } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`${path} failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request<HealthStatus>("/frontend-api/health"),
  videos: async () => {
    const payload = await request<{ videos: VideoCard[] }>("/frontend-api/videos");
    return payload.videos;
  },
  video: (videoId: string) => request<VideoDetail>(`/frontend-api/videos/${videoId}`),
  events: async (videoId: string) => {
    const payload = await request<{ events: EventRecord[] }>(`/frontend-api/videos/${videoId}/events`);
    return payload.events;
  },
  heatmapUrl: (videoId: string) => `${API_BASE_URL}/frontend-api/videos/${videoId}/heatmap`,
  recommendations: () => request<{ recommendations: unknown[] }>("/recommendations"),
  kpis: () => request<Record<string, unknown>>("/kpis"),
};
