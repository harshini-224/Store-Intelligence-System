from fastapi import APIRouter
import json
from app.analytics_utils import iter_zone_metrics

router = APIRouter()


@router.get("/ai-insights")
def ai_insights():

    with open(
        "data/outputs/analytics/floor_a_summary.json"
    ) as file:

        analytics = json.load(file)

    zone_metrics = list(iter_zone_metrics(analytics))
    if not zone_metrics:
        return {
            "summary": "No zone analytics are available."
        }

    best_zone = max(
        zone_metrics,
        key=lambda x: x[1]["total_dwell_time"]
    )[0]

    worst_zone = min(
        zone_metrics,
        key=lambda x: x[1]["total_dwell_time"]
    )[0]

    return {
        "summary":
        (
            f"{best_zone} is attracting "
            f"maximum customer attention. "
            f"{worst_zone} is underperforming "
            f"and may require better promotions."
        )
    }
