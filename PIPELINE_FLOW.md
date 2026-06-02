# Pipeline Flow

## Overview

The pipeline converts raw video into metrics in six stages:

```text
Input Video
↓
Detection
↓
Tracking
↓
Events
↓
Analytics
↓
Dashboard/API
```

## 1. Input Video

Videos are read from `data/raw` or uploaded through the Streamlit dashboard.

Example inputs:

- `data/raw/entrance.mp4`
- `data/raw/floor_a.mp4`
- `data/raw/floor_b.mp4`
- `data/raw/billing.mp4`
- `data/raw/corner.mp4`

The dashboard infers the video type from the file name and runs the matching pipeline stages.

## 2. Detection

Detection identifies people in each frame.

Command example:

```bash
python data/pipeline/detection/run_detection.py --input-video data/raw/floor_a.mp4 --video-name floor_a
```

Sample output:

- `data/outputs/detection/floor_a_detected.mp4`

## 3. Tracking

Tracking assigns persistent IDs to detected people.

Command example:

```bash
python data/pipeline/tracking/run_tracking.py --input-video data/raw/floor_a.mp4 --video-name floor_a --output-dir data/outputs/tracking
```

Sample outputs:

- `data/outputs/tracking/floor_a_tracked.mp4`
- `data/outputs/tracking/floor_a_tracks.json`

Sample tracking JSON:

```json
[
  {
    "frame": 120,
    "track_id": 3,
    "center_x": 742,
    "center_y": 388,
    "bbox": [690, 240, 810, 520],
    "confidence": 0.88,
    "is_staff": false
  }
]
```

## 4. Events

Events translate movement into business actions.

Command example:

```bash
python data/pipeline/events/run_events.py --video-name floor_a --track-file data/outputs/tracking/floor_a_tracks.json
```

Sample outputs:

- `data/outputs/events/events.json`
- `data/outputs/events/events.csv`
- updated analytics summary fields for queue and funnel metrics

Sample event JSON:

```json
{
  "event_id": "9e1f23b95c9d44d2a2f4d7d95f870f3d",
  "visitor_id": 3,
  "store_id": "STORE_001",
  "camera_id": "CAM_FLOOR_A",
  "timestamp": "2026-06-02T10:15:20Z",
  "event_type": "ZONE_ENTER",
  "zone_id": "SKINCARE_BROWSING",
  "confidence": 0.88,
  "metadata": {
    "source": "zone_transition",
    "frame": 120,
    "is_staff": false
  },
  "event": "ZONE_ENTER"
}
```

## Sample Event Lifecycle

One customer journey can produce the following lifecycle:

```text
ENTRY
↓
ZONE_ENTER: SKINCARE_BROWSING
↓
ZONE_DWELL: SKINCARE_BROWSING
↓
ZONE_EXIT: SKINCARE_BROWSING
↓
BILLING_QUEUE_JOIN
↓
PURCHASE
↓
EXIT
```

If the visitor leaves the frame and later returns, the event stream can include `REENTRY` while preserving the canonical visitor ID.

## 5. Analytics

Analytics aggregate tracks and events into metrics.

Zone analytics command:

```bash
python data/pipeline/analytics/run_zone_analytics.py --video-name floor_a --tracks-file data/outputs/tracking/floor_a_tracks.json
```

Conversion command:

```bash
python data/pipeline/conversion/run_conversion.py --tracks-file data/outputs/tracking/floor_a_tracks.json --analytics-file data/outputs/analytics/floor_a_summary.json
```

Heatmap command:

```bash
python data/pipeline/heatmaps/run_heatmap.py --input-video data/raw/floor_a.mp4 --video-name floor_a --tracks-file data/outputs/tracking/floor_a_tracks.json
```

Sample analytics summary:

```json
{
  "SKINCARE_BROWSING": {
    "visitors": 24,
    "total_dwell_time": 186.4
  },
  "PREMIUM_SKINCARE": {
    "visitors": 11,
    "total_dwell_time": 92.1
  },
  "_conversion_metrics": {
    "total_visitors": 35,
    "converted_visitors": 9,
    "billing_zone_visitors": 13,
    "conversion_rate": 25.71,
    "billing_zone_rate": 37.14
  },
  "_queue_metrics": {
    "queue_joins": 13,
    "queue_abandons": 2,
    "abandonment_rate_percent": 15.38,
    "average_queue_depth": 2.4
  },
  "_funnel_metrics": {
    "entry": 35,
    "zone_visit": 30,
    "billing_queue": 13,
    "purchase": 9
  }
}
```

## 6. Dashboard/API

The API serves generated outputs.

Run API:

```bash
uvicorn app.main:app --reload
```

Run dashboard:

```bash
streamlit run dashboard/streamlit_app.py
```

Sample API calls:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/metrics
curl http://127.0.0.1:8000/metrics/conversion/summary
curl http://127.0.0.1:8000/metrics/queue/summary
curl http://127.0.0.1:8000/funnel
curl http://127.0.0.1:8000/recommendations
```

Sample `/health` response:

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

Sample recommendation response:

```json
{
  "recommendations": [
    "Low engagement in PREMIUM_SKINCARE. Consider promotions.",
    "SKINCARE_BROWSING has high dwell time. Upsell opportunities exist."
  ]
}
```

## End-to-End Dashboard Flow

1. Open the dashboard.
2. Upload or select a processed video.
3. Run detection, tracking, events, analytics, and heatmap generation.
4. Review KPIs, zone engagement, heatmap, executive summary, and recommendations.
5. Use API endpoints for monitoring, integration, or automated review.
