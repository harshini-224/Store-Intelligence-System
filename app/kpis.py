import json

from fastapi import APIRouter

router = APIRouter()


@router.get("/kpis")
def kpis():

    analytics = json.load(
        open(
            "data/outputs/analytics/floor_a_summary.json"
        )
    )

    total_visitors = 0
    total_dwell = 0

    top_zone = None
    best_time = 0

    for zone, data in analytics.items():

        total_visitors += data["visitors"]
        total_dwell += data["total_dwell_time"]

        if data["total_dwell_time"] > best_time:

            best_time = data["total_dwell_time"]
            top_zone = zone

    return {
        "total_visitors": total_visitors,
        "top_zone": top_zone,
        "total_dwell_time": round(
            total_dwell,
            2
        )
    }