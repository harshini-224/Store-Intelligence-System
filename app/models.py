import uuid

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional


class Event(BaseModel):
    """Canonical event schema.

    All pipeline events and API ingestion events use this schema.
    Legacy events with fewer fields are accepted via defaults and aliases.
    """

    model_config = ConfigDict(populate_by_name=True)

    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    visitor_id: int
    store_id: str = "STORE_001"
    camera_id: str = "CAM_UNKNOWN"
    timestamp: str
    event_type: str
    zone_id: Optional[str] = Field(default=None, alias="zone")
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EventBatch(BaseModel):

    events: list[Event]
