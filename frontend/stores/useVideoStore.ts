import { create } from "zustand";

type VideoViewMode = "grid" | "list";

type VideoStore = {
  query: string;
  sort: "recent" | "visitors" | "events";
  viewMode: VideoViewMode;
  setQuery: (query: string) => void;
  setSort: (sort: "recent" | "visitors" | "events") => void;
  setViewMode: (mode: VideoViewMode) => void;
};

export const useVideoStore = create<VideoStore>((set) => ({
  query: "",
  sort: "recent",
  viewMode: "grid",
  setQuery: (query) => set({ query }),
  setSort: (sort) => set({ sort }),
  setViewMode: (viewMode) => set({ viewMode }),
}));
