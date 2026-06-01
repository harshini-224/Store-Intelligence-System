from fastapi import APIRouter
import json

router = APIRouter()


@router.get("/funnel")
def get_funnel():

    funnel = {}

    files = [
        "data/outputs/analytics/floor_a_summary.json",
        "data/outputs/analytics/floor_b_summary.json"
    ]

    for file in files:

        try:

            with open(file) as f:

                data = json.load(f)

            for zone, values in data.items():

                funnel[zone] = values["visitors"]

        except Exception:

            pass

    return funnel