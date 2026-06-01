import json

from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard")
def dashboard():

    floor_a = json.load(
        open(
            "data/outputs/analytics/floor_a_summary.json"
        )
    )

    floor_b = json.load(
        open(
            "data/outputs/analytics/floor_b_summary.json"
        )
    )

    return {
        "floor_a": floor_a,
        "floor_b": floor_b
    }