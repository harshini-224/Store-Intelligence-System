from fastapi import APIRouter

from app.services.metrics_service import (
    load_floor_metrics
)

router = APIRouter()


@router.get("/metrics")
def get_metrics():

    return load_floor_metrics()