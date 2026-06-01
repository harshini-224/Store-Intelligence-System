from fastapi import APIRouter

from app.models import EventBatch
from app.storage import EVENTS

router = APIRouter()


@router.post("/events/ingest")
def ingest_events(batch: EventBatch):

    for event in batch.events:

        EVENTS.append(
            event.model_dump()
        )

    return {
        "message": "Events ingested",
        "count": len(batch.events)
    }