"""Store-level metrics, funnel, heatmap, and anomalies endpoints.

Provides the challenge-required /stores/{store_id}/... routes that aggregate
existing analytics services into per-store responses.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.metrics_service import (
    load_floor_metrics,
    load_conversion_metrics,
    load_queue_metrics,
    load_funnel_metrics,
)
from app.health import build_health_payload
from app.analytics_utils import iter_zone_metrics

logger = logging.getLogger("store_intelligence")

router = APIRouter()

ANALYTICS_DIR = Path("data/outputs/analytics")
HEATMAP_DIR = Path("data/outputs/heatmaps")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _aggregate_visitors_and_dwell(floor_metrics: Dict[str, Any]):
    """Sum visitor counts and dwell times across all zone summaries."""
    total_visitors = 0
    total_dwell = 0.0
    zone_dwells: Dict[str, float] = {}

    for key, value in floor_metrics.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            for zone_key, zone_val in value.items():
                if isinstance(zone_val, dict) and "visitors" in zone_val:
                    v = zone_val.get("visitors", 0)
                    d = zone_val.get("total_dwell_time", 0.0)
                    total_visitors += v
                    total_dwell += d
                    if v > 0:
                        zone_dwells[zone_key] = round(d / v, 2)

    avg_dwell = round(total_dwell / total_visitors, 2) if total_visitors > 0 else 0.0
    return total_visitors, avg_dwell, zone_dwells


def _aggregate_conversion_rate(conversion_metrics: Dict[str, Any]) -> float:
    aggregate = conversion_metrics.get("_aggregate", {})
    return aggregate.get("aggregate_conversion_rate", 0.0)


# ---------------------------------------------------------------------------
# GET /stores/{store_id}/metrics
# ---------------------------------------------------------------------------

@router.get("/stores/{store_id}/metrics")
def get_store_metrics(store_id: str):
    """Aggregated metrics for a store: visitors, conversion, avg dwell, queue, abandonment."""
    floor_metrics = load_floor_metrics()
    conversion_metrics = load_conversion_metrics()
    queue_metrics = load_queue_metrics()
    funnel_metrics = load_funnel_metrics()

    visitor_count, avg_dwell, avg_dwell_per_zone = _aggregate_visitors_and_dwell(floor_metrics)
    conversion_rate = _aggregate_conversion_rate(conversion_metrics)
    queue_agg = queue_metrics.get("_aggregate", {})

    # Check for any meaningful data
    has_data = visitor_count > 0 or bool(conversion_metrics) or bool(queue_metrics)
    if not has_data:
        raise HTTPException(
            status_code=404,
            detail={
                "store_id": store_id,
                "status": "no_data",
            },
        )

    return {
        "store_id": store_id,
        "unique_visitors": visitor_count,
        "conversion_rate": conversion_rate,
        "avg_dwell_seconds": avg_dwell,
        "avg_dwell_per_zone": avg_dwell_per_zone,
        "queue_depth": queue_agg.get("average_queue_depth", 0),
        "abandonment_rate": queue_agg.get("abandonment_rate_percent", 0.0),
        "queue_metrics": queue_agg,
        "funnel_metrics": funnel_metrics,
    }


# ---------------------------------------------------------------------------
# GET /stores/{store_id}/funnel
# ---------------------------------------------------------------------------

@router.get("/stores/{store_id}/funnel")
def get_store_funnel(store_id: str):
    """Conversion funnel: Entry → Zone Visit → Billing Queue → Purchase."""
    funnel = load_funnel_metrics()
    funnel["store_id"] = store_id
    return funnel


# ---------------------------------------------------------------------------
# GET /stores/{store_id}/heatmap
# ---------------------------------------------------------------------------

@router.get("/stores/{store_id}/heatmap")
def get_store_heatmap(store_id: str):
    """Zone visit frequency + avg dwell, normalised 0-100."""
    floor_metrics = load_floor_metrics()
    zones: List[Dict[str, Any]] = []
    max_visitors = 0

    for key, value in floor_metrics.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            for zone_key, zone_val in value.items():
                if isinstance(zone_val, dict) and "visitors" in zone_val:
                    v = zone_val.get("visitors", 0)
                    d = zone_val.get("total_dwell_time", 0.0)
                    avg_d = round(d / v, 2) if v > 0 else 0.0
                    if v > max_visitors:
                        max_visitors = v
                    zones.append({
                        "zone_id": zone_key,
                        "visit_count": v,
                        "avg_dwell_seconds": avg_d,
                    })

    # Normalise 0-100
    for z in zones:
        z["intensity"] = round(z["visit_count"] / max_visitors * 100, 1) if max_visitors > 0 else 0

    data_confidence = "high" if sum(z["visit_count"] for z in zones) >= 20 else "low"

    return {
        "store_id": store_id,
        "zones": zones,
        "data_confidence": data_confidence,
    }


# ---------------------------------------------------------------------------
# GET /stores/{store_id}/anomalies
# ---------------------------------------------------------------------------

@router.get("/stores/{store_id}/anomalies")
def get_store_anomalies(store_id: str):
    """Active anomalies with severity and suggested_action."""
    alerts: List[Dict[str, Any]] = []

    files = list(ANALYTICS_DIR.glob("*_summary.json"))

    for file in files:
        try:
            with open(file) as f:
                data = json.load(f)

            # Zone-level anomalies
            for zone, values in iter_zone_metrics(data):
                visitors = values.get("visitors", 0)
                dwell = values.get("total_dwell_time", 0.0)

                # Dead zone: no visits
                if visitors == 0:
                    alerts.append({
                        "type": "DEAD_ZONE",
                        "zone": zone,
                        "severity": "WARN",
                        "message": f"No visitors detected in {zone}",
                        "suggested_action": f"Review zone {zone} placement and signage to attract foot traffic.",
                    })
                    continue

                avg_dwell = dwell / visitors

                # Low traffic
                if visitors < 5:
                    alerts.append({
                        "type": "LOW_TRAFFIC",
                        "zone": zone,
                        "severity": "INFO",
                        "visitors": visitors,
                        "message": f"Low traffic in {zone}: {visitors} visitors",
                        "suggested_action": f"Consider promotional displays or repositioning products in {zone}.",
                    })

                # High dwell (potential engagement or friction)
                if avg_dwell > 4:
                    alerts.append({
                        "type": "HIGH_DWELL_TIME",
                        "zone": zone,
                        "severity": "INFO",
                        "avg_dwell": round(avg_dwell, 2),
                        "message": f"High average dwell in {zone}: {avg_dwell:.1f}s/visitor",
                        "suggested_action": f"Investigate if high dwell in {zone} indicates engagement or confusion.",
                    })

            # Queue spike anomaly
            queue = data.get("_queue_metrics", {})
            max_depth = queue.get("max_queue_depth", 0)
            if max_depth >= 5:
                alerts.append({
                    "type": "BILLING_QUEUE_SPIKE",
                    "severity": "CRITICAL",
                    "max_queue_depth": max_depth,
                    "message": f"Queue spike: max depth reached {max_depth}",
                    "suggested_action": "Open additional billing counters or deploy queue management staff.",
                })

            # Queue abandonment anomaly
            abandon_rate = queue.get("abandonment_rate_percent", 0)
            if abandon_rate > 20:
                alerts.append({
                    "type": "HIGH_QUEUE_ABANDONMENT",
                    "severity": "WARN",
                    "abandonment_rate_percent": abandon_rate,
                    "message": f"Queue abandonment rate: {abandon_rate}%",
                    "suggested_action": "Reduce queue wait times — consider express checkout or self-service.",
                })

            # Conversion drop (compare to expected baseline)
            conversion = data.get("_conversion_metrics", {})
            conv_rate = conversion.get("conversion_rate", 0)
            if conversion and conv_rate < 15:
                alerts.append({
                    "type": "CONVERSION_DROP",
                    "severity": "WARN",
                    "conversion_rate": conv_rate,
                    "message": f"Low conversion rate: {conv_rate}%",
                    "suggested_action": "Review checkout friction — staffing, queue length, product availability.",
                })

        except Exception:
            pass

    return {
        "store_id": store_id,
        "anomalies": alerts,
        "count": len(alerts),
    }
