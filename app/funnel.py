from fastapi import APIRouter

from app.services.metrics_service import load_funnel_metrics

router = APIRouter()


@router.get("/funnel")
def get_funnel():
    return load_funnel_metrics()
