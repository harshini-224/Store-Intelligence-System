from pydantic import BaseModel


class Event(BaseModel):

    event_id: str
    visitor_id: int
    event_type: str
    timestamp: str

    zone: str | None = None


class EventBatch(BaseModel):

    events: list[Event]