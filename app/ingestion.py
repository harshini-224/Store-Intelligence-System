"""Event ingestion endpoint.

Accepts batches of up to 500 events with idempotency by event_id,
partial success on malformed events, and structured error responses.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Request
from pydantic import ValidationError

from app.models import Event
from app.storage import EVENTS, SEEN_EVENT_IDS

logger = logging.getLogger("store_intelligence")

router = APIRouter()


@router.post("/events/ingest")
async def ingest_events(request: Request):
    """Ingest a batch of events.

    - Idempotent by event_id: duplicate events are silently skipped.
    - Partial success: valid events are accepted even if some fail validation.
    - Structured error response for malformed events.
    """
    body = await request.json()
    raw_events: List[Dict[str, Any]] = body.get("events", [])

    if not isinstance(raw_events, list):
        return {
            "accepted": 0,
            "duplicates": 0,
            "errors": [{"index": 0, "error": "'events' must be a list"}],
        }

    if len(raw_events) > 500:
        return {
            "accepted": 0,
            "duplicates": 0,
            "errors": [{"index": 0, "error": f"Batch size {len(raw_events)} exceeds limit of 500"}],
        }

    accepted = 0
    duplicates = 0
    errors: List[Dict[str, Any]] = []

    for idx, raw in enumerate(raw_events):
        try:
            event = Event(**raw)
        except (ValidationError, Exception) as exc:
            errors.append({"index": idx, "error": str(exc)})
            continue

        # Idempotency: skip duplicate event_ids
        if event.event_id in SEEN_EVENT_IDS:
            duplicates += 1
            continue

        SEEN_EVENT_IDS.add(event.event_id)
        EVENTS.append(event.model_dump())
        accepted += 1

    return {
        "accepted": accepted,
        "duplicates": duplicates,
        "errors": errors,
    }