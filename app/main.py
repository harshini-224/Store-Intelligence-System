from fastapi import FastAPI

from app.health import router as health_router
from app.ingestion import router as ingestion_router
from app.metrics import router as metrics_router
from app.funnel import router as funnel_router
from app.anomalies import router as anomalies_router
from app.insights import router as insights_router

app = FastAPI(
    title="Store Intelligence API"
)

app.include_router(
    health_router
)

app.include_router(
    ingestion_router
)

app.include_router(
    metrics_router
)

app.include_router(
    funnel_router
)

app.include_router(
    anomalies_router
)

app.include_router(insights_router)
