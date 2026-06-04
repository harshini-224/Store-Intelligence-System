"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    retry: 2,
    refetchInterval: 30_000,
  });
}

export function useVideos() {
  return useQuery({
    queryKey: ["videos"],
    queryFn: api.videos,
    retry: 2,
  });
}

export function useVideo(videoId: string) {
  return useQuery({
    queryKey: ["video", videoId],
    queryFn: () => api.video(videoId),
    enabled: Boolean(videoId),
    retry: 2,
  });
}

export function useEvents(videoId: string) {
  return useQuery({
    queryKey: ["events", videoId],
    queryFn: () => api.events(videoId),
    enabled: Boolean(videoId),
  });
}
