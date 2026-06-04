"""Store-level metrics endpoint.

Aggregates existing analytics services into a single per-store response.
"""

from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from app.services.metrics_service import (
    load_floor_metrics,
    load_conversion_metrics,
    load_queue_metrics,
    load_funnel_metrics,
)
from app.health import build_health_payload

router = APIRouter()


def _aggregate_visitor_count(floor_metrics: Dict[str, Any]) -> int:
    """Sum visitor counts across all zone summaries."""
    total = 0
    for key, value in floor_metrics.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            # Zone-level summaries have "visitors" key
            for zone_key, zone_val in value.items():
                if isinstance(zone_val, dict) and "visitors" in zone_val:
                    total += zone_val.get("visitors", 0)
    return total


def _aggregate_conversion_rate(conversion_metrics: Dict[str, Any]) -> float:
    """Extract aggregate conversion rate."""
    aggregate = conversion_metrics.get("_aggregate", {})
    return aggregate.get("aggregate_conversion_rate", 0.0)


@router.get("/stores/{store_id}/metrics")
def get_store_metrics(store_id: str):
    """
    Get aggregated metrics for a specific store.

    Returns visitor count, conversion rate, queue metrics, funnel metrics,
    and system health in a single response. If no analytics data exists
    for the store, returns a no_data status with HTTP 404.
    """
    floor_metrics = load_floor_metrics()
    conversion_metrics = load_conversion_metrics()
    queue_metrics = load_queue_metrics()
    funnel_metrics = load_funnel_metrics()
    health = build_health_payload()

    # Check if any meaningful data exists
    has_data = False

    # Floor metrics contain non-empty zone data
    for key, value in floor_metrics.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and value:
            has_data = True
            break

    if not has_data and not conversion_metrics and not queue_metrics:
        raise HTTPException(
            status_code=404,
            detail={
                "store_id": store_id,
                "status": "no_data",
            },
        )

    visitor_count = _aggregate_visitor_count(floor_metrics)
    conversion_rate = _aggregate_conversion_rate(conversion_metrics)

    queue_aggregate = queue_metrics.get("_aggregate", {})

    # Build group analytics if available
    group_analytics = {}
    for key, value in floor_metrics.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and "_group_metrics" in value:
            group_analytics = value["_group_metrics"]
            break

    response: Dict[str, Any] = {
        "store_id": store_id,
        "visitor_count": visitor_count,
        "conversion_rate": conversion_rate,
        "queue_metrics": queue_aggregate,
        "funnel_metrics": funnel_metrics,
        "health": health,
    }

    if group_analytics:
        response["group_analytics"] = group_analytics

    return response
