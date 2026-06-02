from fastapi import APIRouter

from app.services.metrics_service import (
    load_floor_metrics,
    load_conversion_metrics,
    get_conversion_summary,
    load_queue_metrics,
    get_queue_summary
)

router = APIRouter()


@router.get("/metrics")
def get_metrics():
    """Get all floor metrics including zone data and conversion rates."""
    return load_floor_metrics()


@router.get("/metrics/conversion")
def get_conversion_metrics():
    """Get detailed conversion metrics by floor."""
    return load_conversion_metrics()


@router.get("/metrics/conversion/summary")
def get_conversion_summary_endpoint():
    """Get high-level conversion rate summary."""
    return get_conversion_summary()


@router.get("/metrics/queue")
def get_queue_metrics_endpoint():
    """Get detailed queue metrics by floor."""
    return load_queue_metrics()


@router.get("/metrics/queue/summary")
def get_queue_summary_endpoint():
    """Get high-level queue analytics summary."""
    return get_queue_summary()