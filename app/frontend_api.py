import json
import re
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(prefix="/frontend-api", tags=["frontend"])

OUTPUTS = Path("data/outputs")
ANALYTICS_DIR = OUTPUTS / "analytics"
TRACKING_DIR = OUTPUTS / "tracking"
EVENTS_DIR = OUTPUTS / "events"
HEATMAP_DIR = OUTPUTS / "heatmaps"
DETECTION_DIR = OUTPUTS / "detection"


def _load_json(path: Path, default: Any = None) -> Any:
    try:
        with open(path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _artifact_key(path: Path) -> str:
    return re.sub(
        r"_(summary|tracks|tracked|detected|heatmap)$",
        "",
        path.stem
    )


def _summary(video_id: str) -> Dict[str, Any]:
    return _load_json(ANALYTICS_DIR / f"{video_id}_summary.json", {}) or {}


def _zone_records(summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in summary.items()
        if (
            not key.startswith("_")
            and isinstance(value, dict)
            and "visitors" in value
            and "total_dwell_time" in value
        )
    }


def _events() -> List[Dict[str, Any]]:
    events = _load_json(EVENTS_DIR / "events.json", [])
    return events if isinstance(events, list) else []


def _events_for_video(video_id: str) -> List[Dict[str, Any]]:
    events = _events()
    filtered = [
        event for event in events
        if video_id in str(event.get("camera_id", "")).lower()
        or video_id in str(event.get("video_name", "")).lower()
    ]
    has_camera_identity = any(
        event.get("camera_id") or event.get("video_name")
        for event in events
    )
    if filtered or has_camera_identity:
        return filtered
    return events


def _capabilities(video_id: str) -> Dict[str, bool]:
    summary = _summary(video_id)
    events = _events_for_video(video_id)
    return {
        "tracking": (TRACKING_DIR / f"{video_id}_tracks.json").exists(),
        "events": bool(events),
        "heatmap": (HEATMAP_DIR / f"{video_id}_heatmap.jpg").exists(),
        "zones": bool(_zone_records(summary)),
        "dwell": bool(_zone_records(summary)),
        "queue": bool(summary.get("_queue_metrics")),
        "conversion": bool(summary.get("_conversion_metrics")),
        "funnel": bool(summary.get("_funnel_metrics")),
        "recommendations": bool(_zone_records(summary)),
        "insights": bool(_zone_records(summary) or events),
    }


def _video_ids() -> List[str]:
    ids = set()
    patterns = [
        (ANALYTICS_DIR, "*_summary.json"),
        (TRACKING_DIR, "*_tracks.json"),
        (TRACKING_DIR, "*_tracked.mp4"),
        (DETECTION_DIR, "*_detected.mp4"),
        (HEATMAP_DIR, "*_heatmap.jpg"),
    ]
    for folder, pattern in patterns:
        if folder.exists():
            ids.update(_artifact_key(path) for path in folder.glob(pattern))
    return sorted(ids)


def _video_card(video_id: str) -> Dict[str, Any]:
    summary = _summary(video_id)
    zones = _zone_records(summary)
    events = _events_for_video(video_id)
    visitors = sum(int(zone.get("visitors", 0)) for zone in zones.values())
    artifact_times = [
        path.stat().st_mtime
        for path in [
            ANALYTICS_DIR / f"{video_id}_summary.json",
            TRACKING_DIR / f"{video_id}_tracks.json",
            TRACKING_DIR / f"{video_id}_tracked.mp4",
            HEATMAP_DIR / f"{video_id}_heatmap.jpg",
        ]
        if path.exists()
    ]

    return {
        "video_id": video_id,
        "name": video_id.replace("_", " ").title(),
        "processing_status": "completed",
        "processed_at": max(artifact_times) if artifact_times else None,
        "visitor_count": visitors,
        "event_count": len(events),
        "capabilities": _capabilities(video_id),
        "thumbnail_url": (
            f"/frontend-api/videos/{video_id}/heatmap"
            if (HEATMAP_DIR / f"{video_id}_heatmap.jpg").exists()
            else None
        ),
    }


@router.get("/videos")
def list_videos():
    return {
        "videos": [_video_card(video_id) for video_id in _video_ids()]
    }


@router.get("/videos/{video_id}")
def video_detail(video_id: str):
    if video_id not in _video_ids():
        raise HTTPException(status_code=404, detail="Video not found")

    summary = _summary(video_id)
    events = _events_for_video(video_id)
    tracks = _load_json(TRACKING_DIR / f"{video_id}_tracks.json", []) or []

    return {
        **_video_card(video_id),
        "analytics": summary,
        "zones": _zone_records(summary),
        "events": events,
        "tracks_count": len(tracks) if isinstance(tracks, list) else 0,
        "artifacts": {
            "tracked_video": (
                f"/frontend-api/videos/{video_id}/tracked-video"
                if (TRACKING_DIR / f"{video_id}_tracked.mp4").exists()
                else None
            ),
            "detected_video": (
                f"/frontend-api/videos/{video_id}/detected-video"
                if (DETECTION_DIR / f"{video_id}_detected.mp4").exists()
                else None
            ),
            "heatmap": (
                f"/frontend-api/videos/{video_id}/heatmap"
                if (HEATMAP_DIR / f"{video_id}_heatmap.jpg").exists()
                else None
            ),
        },
    }


@router.get("/videos/{video_id}/events")
def video_events(video_id: str):
    return {"events": _events_for_video(video_id)}


@router.get("/videos/{video_id}/heatmap")
def video_heatmap(video_id: str):
    path = HEATMAP_DIR / f"{video_id}_heatmap.jpg"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Heatmap not found")
    return FileResponse(path)


@router.get("/videos/{video_id}/tracked-video")
def video_tracked_video(video_id: str):
    path = TRACKING_DIR / f"{video_id}_tracked.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Tracked video not found")
    return FileResponse(path, media_type="video/mp4")


@router.get("/videos/{video_id}/detected-video")
def video_detected_video(video_id: str):
    path = DETECTION_DIR / f"{video_id}_detected.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Detected video not found")
    return FileResponse(path, media_type="video/mp4")
