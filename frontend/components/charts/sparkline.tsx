"use client";

import {
    ResponsiveContainer,
    AreaChart,
    Area,
    Tooltip,
} from "recharts";

interface SparklineProps {
    data: number[];
    color?: string;
    height?: number;
}

export function Sparkline({ data, color = "#2dd4bf", height = 40 }: SparklineProps) {
    const chartData = data.map((v, i) => ({ i, v }));
    return (
        <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={chartData}>
                <defs>
                    <linearGradient id={`sg-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                        <stop offset="95%" stopColor={color} stopOpacity={0} />
                    </linearGradient>
                </defs>
                <Tooltip
                    content={() => null}
                    cursor={false}
                />
                <Area
                    dataKey="v"
                    stroke={color}
                    strokeWidth={2}
                    fill={`url(#sg-${color.replace("#", "")})`}
                    dot={false}
                    isAnimationActive
                />
            </AreaChart>
        </ResponsiveContainer>
    );
}
