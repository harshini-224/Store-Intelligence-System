import type { ComponentType } from "react";
import type { Capability, VideoDetail } from "@/lib/types";
import { ConversionWidget } from "@/components/analytics/conversion-widget";
import { DwellWidget } from "@/components/analytics/dwell-widget";
import { FunnelWidget } from "@/components/analytics/funnel-widget";
import { HeatmapWidget } from "@/components/heatmaps/heatmap-widget";
import { InsightWidget } from "@/components/analytics/insight-widget";
import { QueueWidget } from "@/components/analytics/queue-widget";
import { RecommendationWidget } from "@/components/analytics/recommendation-widget";
import { ZoneAnalyticsWidget } from "@/components/analytics/zone-analytics-widget";
import { EventTimelineWidget } from "@/components/events/event-timeline-widget";

export type WidgetProps = {
  video: VideoDetail;
};

const widgets = new Map<Capability, ComponentType<WidgetProps>>();

export function registerWidget(capability: Capability, component: ComponentType<WidgetProps>) {
  widgets.set(capability, component);
}

export function getRegisteredWidgets(video: VideoDetail) {
  return Object.entries(video.capabilities)
    .filter(([, enabled]) => enabled)
    .map(([capability]) => ({
      capability: capability as Capability,
      Component: widgets.get(capability as Capability),
    }))
    .filter((entry): entry is { capability: Capability; Component: ComponentType<WidgetProps> } => {
      return Boolean(entry.Component);
    });
}

registerWidget("zones", ZoneAnalyticsWidget);
registerWidget("dwell", DwellWidget);
registerWidget("queue", QueueWidget);
registerWidget("conversion", ConversionWidget);
registerWidget("funnel", FunnelWidget);
registerWidget("heatmap", HeatmapWidget);
registerWidget("recommendations", RecommendationWidget);
registerWidget("insights", InsightWidget);
registerWidget("events", EventTimelineWidget);
