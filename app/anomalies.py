from fastapi import APIRouter
import json
from app.analytics_utils import iter_zone_metrics

router = APIRouter()


@router.get("/anomalies")
def anomalies():

    alerts = []

    files = [
        "data/outputs/analytics/floor_a_summary.json",
        "data/outputs/analytics/floor_b_summary.json"
    ]

    for file in files:

        try:

            with open(file) as f:

                data = json.load(f)

            for zone, values in iter_zone_metrics(data):

                visitors = values["visitors"]
                dwell = values["total_dwell_time"]
                if visitors == 0:
                    continue

                avg_dwell = dwell / visitors

                if visitors < 5:

                    alerts.append(
                        {
                            "zone": zone,
                            "alert": "LOW_TRAFFIC",
                            "visitors": visitors
                        }
                    )

                if avg_dwell > 4:

                    alerts.append(
                        {
                            "zone": zone,
                            "alert": "HIGH_DWELL_TIME",
                            "avg_dwell": round(avg_dwell, 2)
                        }
                    )

        except Exception:
            pass

    return alerts
