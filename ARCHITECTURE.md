# Architecture

## System Overview

Store Intelligence System converts retail CCTV footage into operational and business analytics. It detects people in video frames, maintains visitor identities across frames, emits structured behavior events, aggregates those events into metrics, and exposes the results through a FastAPI service and Streamlit dashboard.

The system is organized as a pipeline. Each stage writes artifacts to `data/outputs`, allowing later stages and reviewers to inspect intermediate results without rerunning the full stack.

```text
Videos
↓
Detection
↓
Tracking
↓
Events
↓
Analytics
↓
API + Dashboard
```

## Components

### Detection

Location: `data/pipeline/detection`

The detection stage reads input video and uses YOLO to identify people in each frame. It produces annotated detection videos in `data/outputs/detection`.

Responsibilities:

- Read raw CCTV videos from `data/raw` or uploaded files.
- Run person detection frame by frame.
- Preserve frame-level evidence for downstream tracking and review.

### Tracking

Location: `data/pipeline/tracking`

The tracking stage maintains identities for detected people across frames. It produces track JSON files and annotated tracked videos in `data/outputs/tracking`.

Key artifact:

```json
{
  "frame": 120,
  "track_id": 7,
  "center_x": 960,
  "center_y": 540,
  "bbox": [900, 420, 1020, 680],
  "confidence": 0.91,
  "is_staff": false
}
```

### Events

Location: `data/pipeline/events`

The event stage converts raw movement into business events. It applies line-crossing logic, zone transitions, queue detection, reentry heuristics, and conversion-derived purchase events.

Core events:

- `ENTRY`
- `EXIT`
- `REENTRY`
- `ZONE_ENTER`
- `ZONE_EXIT`
- `ZONE_DWELL`
- `BILLING_QUEUE_JOIN`
- `BILLING_QUEUE_ABANDON`
- `PURCHASE`

Outputs:

- `data/outputs/events/events.json`
- `data/outputs/events/events.csv`

### Analytics

Location: `data/pipeline/analytics`, `data/pipeline/conversion`, `data/pipeline/heatmaps`, `data/pipeline/insights`

Analytics aggregate tracking and event data into business metrics.

Included metrics:

- Visitor counts
- Zone dwell time
- Queue joins, abandons, wait time, and depth
- Funnel stages and dropoffs
- Conversion rate
- Heatmaps
- Recommendations and insights

Important summary files:

- `data/outputs/analytics/floor_a_summary.json`
- `data/outputs/analytics/floor_b_summary.json`
- `data/outputs/heatmaps/floor_a_heatmap.jpg`
- `data/outputs/heatmaps/floor_b_heatmap.jpg`

### API

Location: `app`

The FastAPI layer exposes analytics and operational status. It reads generated artifacts from `data/outputs`.

Primary endpoints:

- `GET /health`
- `GET /metrics`
- `GET /metrics/conversion`
- `GET /metrics/conversion/summary`
- `GET /metrics/queue`
- `GET /metrics/queue/summary`
- `GET /funnel`
- `GET /kpis`
- `GET /insights`
- `GET /ai-insights`
- `GET /recommendations`
- `GET /anomalies`
- `GET /heatmap/floor-a`
- `GET /heatmap/floor-b`

### Dashboard

Location: `dashboard/streamlit_app.py`

The Streamlit dashboard provides an interactive operator-facing view. It supports video upload, pipeline execution, KPI display, zone engagement charts, heatmap rendering, executive summaries, and recommendations.

## Data Flow

1. Input videos are selected from `data/raw` or uploaded through the dashboard.
2. Detection identifies people in each frame.
3. Tracking assigns stable `track_id`s and writes track JSON.
4. Events convert movement into semantic retail events.
5. Analytics aggregate tracks and events into summaries.
6. API and dashboard read summaries, events, heatmaps, and tracking artifacts.

## Operational Health

`GET /health` reports whether analytics, tracking, and event artifacts exist, whether the event feed is stale, the event count, the latest event timestamp, and the active camera count.

Example:

```json
{
  "status": "healthy",
  "event_count": 1234,
  "last_event_timestamp": "2026-06-02T11:55:00Z",
  "stale_feed": false,
  "active_cameras": 5,
  "analytics_available": true,
  "tracking_available": true,
  "events_available": true
}
```

## Staff Exclusion

Staff is represented as `is_staff: true` in tracking rows and event metadata. Staff visitors are excluded from conversion, queue, funnel, zone dwell, heatmap, recommendation, KPI, and insight calculations. See `STAFF_EXCLUSION.md` for the audit.
