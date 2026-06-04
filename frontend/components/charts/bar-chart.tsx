"use client";

import {
    ResponsiveContainer,
    BarChart as RBarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
} from "recharts";

interface BarChartProps {
    data: Record<string, string | number>[];
    dataKey: string;
    nameKey?: string;
    color?: string;
    height?: number;
    label?: string;
}

export function BarChart({
    data,
    dataKey,
    nameKey = "name",
    color = "#2dd4bf",
    height = 200,
}: BarChartProps) {
    return (
        <ResponsiveContainer width="100%" height={height}>
            <RBarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" vertical={false} />
                <XAxis
                    dataKey={nameKey}
                    tick={{ fontSize: 11 }}
                    className="fill-muted-foreground"
                    axisLine={false}
                    tickLine={false}
                />
                <YAxis
                    tick={{ fontSize: 11 }}
                    className="fill-muted-foreground"
                    axisLine={false}
                    tickLine={false}
                />
                <Tooltip
                    contentStyle={{
                        background: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "0.5rem",
                        fontSize: "0.875rem",
                    }}
                    cursor={{ fill: "hsl(var(--muted))" }}
                />
                <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} />
            </RBarChart>
        </ResponsiveContainer>
    );
}
