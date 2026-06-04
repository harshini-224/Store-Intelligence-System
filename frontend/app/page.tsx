import Link from "next/link";
import { ArrowRight, Activity, Users, TrendingUp, AlertTriangle } from "lucide-react";
import { api } from "@/lib/api";
import type { HealthStatus, VideoCard } from "@/lib/types";
import { HomeDashboardClient } from "@/components/shared/home-dashboard-client";

async function getData() {
    try {
        const getApiUrl = () => process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
        const [health, videos] = await Promise.all([
            fetch(`${getApiUrl()}/health`, { next: { revalidate: 30 } })
                .then((r) => r.ok ? r.json() as Promise<HealthStatus> : null).catch(() => null),
            fetch(`${getApiUrl()}/frontend-api/videos`, { next: { revalidate: 30 } })
                .then((r) => r.ok ? r.json().then((d: { videos: VideoCard[] }) => d.videos) : []).catch(() => [] as VideoCard[]),
        ]);
        return { health, videos };
    } catch {
        return { health: null, videos: [] as VideoCard[] };
    }
}

export default async function HomePage() {
    const { health, videos } = await getData();
    return <HomeDashboardClient health={health} videos={videos} />;
}
