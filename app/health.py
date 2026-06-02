import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from fastapi import APIRouter

router = APIRouter()

HEALTH_STALE_THRESHOLD_MINUTES = int(
    os.getenv("HEALTH_STALE_THRESHOLD_MINUTES", "15")
)

ANALYTICS_DIR = Path("data/outputs/analytics")
TRACKING_DIR = Path("data/outputs/tracking")
EVENTS_DIR = Path("data/outputs/events")


def _load_json(path: Path) -> Any:
    with open(path, "r") as file:
        return json.load(file)


def _parse_event_timestamp(timestamp: Optional[str]) -> Optional[datetime]:
    if not timestamp or timestamp.startswith("frame:"):
        return None

    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _load_json_events(events_dir: Path) -> List[Dict[str, Any]]:
    events_file = events_dir / "events.json"
    if not events_file.exists():
        return []

    events = _load_json(events_file)
    if isinstance(events, list):
        return [
            event for event in events
            if isinstance(event, dict)
        ]

    return []


def _load_csv_events(events_dir: Path) -> List[Dict[str, Any]]:
    events_file = events_dir / "events.csv"
    if not events_file.exists():
        return []

    with open(events_file, "r", newline="") as file:
        return list(csv.DictReader(file))


def _load_events(events_dir: Path) -> List[Dict[str, Any]]:
    events = _load_json_events(events_dir)
    if events:
        return events
    return _load_csv_events(events_dir)


def _latest_event_timestamp(
    events: Iterable[Dict[str, Any]]
) -> Optional[datetime]:
    timestamps = [
        parsed
        for parsed in (
            _parse_event_timestamp(event.get("timestamp"))
            for event in events
        )
        if parsed is not None
    ]
    if not timestamps:
        return None
    return max(timestamps)


def _camera_ids_from_events(events: Iterable[Dict[str, Any]]) -> Set[str]:
    return {
        str(event["camera_id"])
        for event in events
        if event.get("camera_id")
    }


def _camera_ids_from_tracking(tracking_dir: Path) -> Set[str]:
    return {
        path.stem.replace("_tracks", "")
        for path in tracking_dir.glob("*_tracks.json")
    }


def _has_analytics(analytics_dir: Path) -> bool:
    return any(analytics_dir.glob("*_summary.json"))


def _has_tracking(tracking_dir: Path) -> bool:
    return any(tracking_dir.glob("*_tracks.json"))


def _has_event_files(events_dir: Path) -> bool:
    return (
        (events_dir / "events.json").exists()
        or (events_dir / "events.csv").exists()
    )


def build_health_payload(
    analytics_dir: Path = ANALYTICS_DIR,
    tracking_dir: Path = TRACKING_DIR,
    events_dir: Path = EVENTS_DIR,
    current_time: Optional[datetime] = None,
    stale_threshold_minutes: int = HEALTH_STALE_THRESHOLD_MINUTES
) -> Dict[str, Any]:
    current_time = current_time or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    analytics_available = _has_analytics(analytics_dir)
    tracking_available = _has_tracking(tracking_dir)
    event_files_available = _has_event_files(events_dir)
    events = _load_events(events_dir) if event_files_available else []
    events_available = event_files_available and bool(events)

    last_event = _latest_event_timestamp(events)
    stale_feed = False
    if last_event is None:
        stale_feed = bool(event_files_available)
    else:
        age_minutes = (
            current_time.astimezone(timezone.utc) - last_event
        ).total_seconds() / 60
        stale_feed = age_minutes > stale_threshold_minutes

    event_camera_ids = _camera_ids_from_events(events)
    tracking_camera_ids = _camera_ids_from_tracking(tracking_dir)
    active_cameras = len(event_camera_ids or tracking_camera_ids)

    degraded = (
        not analytics_available
        or not tracking_available
        or not events_available
        or stale_feed
    )

    return {
        "status": "degraded" if degraded else "healthy",
        "event_count": len(events),
        "last_event_timestamp": (
            last_event.isoformat().replace("+00:00", "Z")
            if last_event
            else None
        ),
        "stale_feed": stale_feed,
        "active_cameras": active_cameras,
        "analytics_available": analytics_available,
        "tracking_available": tracking_available,
        "events_available": events_available
    }


@router.get("/health")
def health():
    return build_health_payload()
