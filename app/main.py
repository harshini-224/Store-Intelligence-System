import logging
import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.health import router as health_router
from app.ingestion import router as ingestion_router
from app.metrics import router as metrics_router
from app.funnel import router as funnel_router
from app.frontend_api import router as frontend_router
from app.anomalies import router as anomalies_router
from app.insights import router as insights_router
from app.heatmap import router as heatmap_router
from app.recommendation import router as recommendations_router
from app.kpis import router as kpis_router
from app.ai_insights import router as ai_router
from app.video_ingest import router as video_ingest_router
from app.store_metrics import router as store_metrics_router

# ---------------------------------------------------------------------------
# Structured logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger("store_intelligence")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with trace_id, endpoint, latency, and status."""

    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("x-trace-id", uuid.uuid4().hex[:16])
        request.state.trace_id = trace_id
        start = time.perf_counter()

        response = await call_next(request)

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        store_id = request.path_params.get("store_id", "-")
        logger.info(
            '{"trace_id":"%s","method":"%s","path":"%s","store_id":"%s",'
            '"status_code":%d,"latency_ms":%.2f}',
            trace_id,
            request.method,
            request.url.path,
            store_id,
            response.status_code,
            latency_ms,
        )
        response.headers["x-trace-id"] = trace_id
        return response


app = FastAPI(
    title="Store Intelligence API",
    description="Real-time store analytics from CCTV footage",
    version="1.0.0",
)

app.add_middleware(StructuredLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(metrics_router)
app.include_router(funnel_router)
app.include_router(anomalies_router)
app.include_router(insights_router)
app.include_router(heatmap_router)
app.include_router(recommendations_router)
app.include_router(kpis_router)
app.include_router(ai_router)
app.include_router(video_ingest_router)
app.include_router(store_metrics_router)
app.include_router(frontend_router)
