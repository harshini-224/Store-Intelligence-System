from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()


FLOOR_A_FILE = (
    "data/outputs/analytics/floor_a_summary.json"
)

FLOOR_B_FILE = (
    "data/outputs/analytics/floor_b_summary.json"
)


def load_json(path):

    if not Path(path).exists():
        return {}

    with open(path, "r") as file:
        return json.load(file)


@router.get("/insights")
def get_insights():

    floor_a = load_json(FLOOR_A_FILE)
    floor_b = load_json(FLOOR_B_FILE)

    insights = []

    # =====================================
    # FLOOR A
    # =====================================

    if floor_a:

        top_zone = max(
            floor_a.items(),
            key=lambda x: x[1]["total_dwell_time"]
        )

        insights.append(
            {
                "camera": "floor_a",
                "type": "TOP_ENGAGEMENT_ZONE",
                "zone": top_zone[0],
                "dwell_time": round(
                    top_zone[1]["total_dwell_time"],
                    2
                )
            }
        )

    # =====================================
    # FLOOR B
    # =====================================

    if floor_b:

        top_zone = max(
            floor_b.items(),
            key=lambda x: x[1]["total_dwell_time"]
        )

        insights.append(
            {
                "camera": "floor_b",
                "type": "TOP_ENGAGEMENT_ZONE",
                "zone": top_zone[0],
                "dwell_time": round(
                    top_zone[1]["total_dwell_time"],
                    2
                )
            }
        )

    # =====================================
    # CROSS FLOOR COMPARISON
    # =====================================

    all_zones = []

    for zone, data in floor_a.items():

        all_zones.append(
            (
                f"Floor A - {zone}",
                data["total_dwell_time"]
            )
        )

    for zone, data in floor_b.items():

        all_zones.append(
            (
                f"Floor B - {zone}",
                data["total_dwell_time"]
            )
        )

    if all_zones:

        best_zone = max(
            all_zones,
            key=lambda x: x[1]
        )

        insights.append(
            {
                "type": "BEST_STORE_ZONE",
                "zone": best_zone[0],
                "dwell_time": round(
                    best_zone[1],
                    2
                )
            }
        )

    return {
        "insights": insights
    }