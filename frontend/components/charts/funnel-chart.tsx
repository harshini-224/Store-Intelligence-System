"use client";

import { ResponsiveContainer, FunnelChart, Funnel, Tooltip, LabelList } from "recharts";

interface FunnelStage {
    name: string;
    value: number;
    fill?: string;
}

interface FunnelChartProps {
    data: FunnelStage[];
    height?: number;
}

const COLORS = ["#2dd4bf", "#818cf8", "#fb923c", "#f472b6"];

export function FunnelChartWidget({ data, height = 220 }: FunnelChartProps) {
    const enriched = data.map((d, i) => ({
        ...d,
        fill: d.fill ?? COLORS[i % COLORS.length],
    }));

    return (
        <ResponsiveContainer width="100%" height={height}>
            <FunnelChart>
                <Tooltip
                    contentStyle={{
                        background: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "0.5rem",
                        fontSize: "0.875rem",
                    }}
                />
                <Funnel dataKey="value" data={enriched} isAnimationActive>
                    <LabelList
                        position="right"
                        fill="hsl(var(--foreground))"
                        stroke="none"
                        dataKey="name"
                        style={{ fontSize: "0.75rem" }}
                    />
                </Funnel>
            </FunnelChart>
        </ResponsiveContainer>
    );
}
