# 05. Pipeline Walkthrough

## End-to-End Processing Flow

The Store Intelligence System transforms raw video into business insights through a multi-stage sequential pipeline.

### Stage 1: Detection (`run_detection.py`)
- **Action**: Runs YOLOv11 person detection on every Nth frame.
- **Output**: Temporary bounding box coordinates.

### Stage 2: Tracking (`run_tracking.py`)
- **Action**: Links detections across frames using ByteTrack.
- **Output**: `data/outputs/tracking/*_tracks.json` (ID, Frame, BBox).

### Stage 3: Event Generation (`run_events.py`)
- **Action**: Translates coordinate movements into semantic events (Entry, Zone Visit, Queue).
- **Output**: `data/outputs/events/events.json` and the mandatory `events.jsonl`.

### Stage 4: Analytics Summary (`run_zone_analytics.py`)
- **Action**: Aggregates events into counts and dwell times.
- **Output**: `data/outputs/analytics/*_summary.json`.

### Stage 5: Visualization & Alerts
- **Heatmaps**: `run_heatmap.py` generates occupancy density images.
- **Insights**: `app/services/metrics_service.py` identifies conversion funnels and anomalies.

## Execution Guide
To process a new clip manually:
1.  Place video in `data/raw/`
2.  Run `python scripts/generate_jsonl.py` (which orchestrates the above steps)
3.  Restart the API to pick up new artifacts.
