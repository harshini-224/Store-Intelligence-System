import json

from fastapi import APIRouter

from data.pipeline.insights.recommendation_engine import (
    RecommendationEngine
)

router = APIRouter()


@router.get("/recommendations")
def recommendations():

    analytics = json.load(
        open(
            "data/outputs/analytics/floor_a_summary.json"
        )
    )

    engine = RecommendationEngine()

    return {
        "recommendations":
        engine.generate(analytics)
    }