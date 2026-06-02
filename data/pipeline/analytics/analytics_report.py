import json
from typing import Optional, Dict, Any, List


class AnalyticsReport:

    def generate(
        self,
        dwell_results,
        output_file,
        conversion_stats: Optional[Dict[str, Any]] = None,
        queue_stats: Optional[Dict[str, Any]] = None,
        funnel_stats: Optional[Dict[str, Any]] = None
    ):
        """
        Generate analytics report.
        
        Args:
            dwell_results: Dwell time data by visitor-zone
            output_file: Path to save JSON report
            conversion_stats: Optional conversion statistics dictionary
                             with keys: total_visitors, converted_visitors,
                             conversion_rate, billing_zone_visitors, billing_zone_rate
            queue_stats: Optional queue analytics dictionary
                         with keys: queue_joins, queue_abandons, abandonment_rate, etc.
            funnel_stats: Optional session funnel dictionary
        """

        zone_summary = {}

        for record in dwell_results:

            zone = record["zone"]

            if zone not in zone_summary:

                zone_summary[zone] = {
                    "visitors": 0,
                    "total_dwell_time": 0
                }

            if "visitor_ids" not in zone_summary[zone]:
                zone_summary[zone]["visitor_ids"] = set()

            zone_summary[zone]["visitor_ids"].add(
                record["visitor_id"]
            )

            zone_summary[zone][
                "total_dwell_time"
            ] += record[
                "dwell_time_seconds"
            ]

        for zone in zone_summary:

            zone_summary[zone]["visitors"] = len(
                zone_summary[zone]["visitor_ids"]
            )

            del zone_summary[zone]["visitor_ids"]

        # Add conversion metrics if provided
        if conversion_stats:
            zone_summary["_conversion_metrics"] = conversion_stats
        
        # Add queue metrics if provided
        if queue_stats:
            zone_summary["_queue_metrics"] = queue_stats

        if funnel_stats:
            zone_summary["_funnel_metrics"] = funnel_stats

        with open(
            output_file,
            "w"
        ) as file:

            json.dump(
                zone_summary,
                file,
                indent=4
            )

        return zone_summary

    def compute_queue_analytics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compute queue analytics from events.
        
        Args:
            events: List of event dictionaries from EventGenerator
            
        Returns:
            Dictionary with queue metrics
        """
        queue_joins = 0
        queue_abandons = 0
        queue_conversions = 0
        queue_visitors_unique = set()
        
        for event in events:
            event_type = event.get("event_type")
            visitor_id = event.get("visitor_id")
            
            if event_type == "BILLING_QUEUE_JOIN":
                queue_joins += 1
                queue_visitors_unique.add(visitor_id)
            elif event_type == "BILLING_QUEUE_ABANDON":
                queue_abandons += 1
                queue_visitors_unique.add(visitor_id)
            elif event_type == "BILLING_QUEUE_CONVERT":
                queue_conversions += 1
                queue_visitors_unique.add(visitor_id)
        
        abandonment_rate = 0.0
        if queue_joins > 0:
            abandonment_rate = round(queue_abandons / queue_joins, 2)
        
        return {
            "queue_joins": queue_joins,
            "queue_abandons": queue_abandons,
            "queue_conversions": queue_conversions,
            "unique_queue_visitors": len(queue_visitors_unique),
            "abandonment_rate": abandonment_rate,
            "abandonment_rate_percent": round(abandonment_rate * 100, 2),
            "average_queue_depth": 0.0,
            "max_queue_depth": 0,
            "average_queue_wait_time": 0.0,
            "max_queue_wait_time": 0.0
        }

    def compute_funnel_analytics(
        self,
        events: List[Dict[str, Any]],
        converted_visitor_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        from data.pipeline.analytics.funnel_tracker import compute_funnel_metrics

        return compute_funnel_metrics(events, converted_visitor_ids)
