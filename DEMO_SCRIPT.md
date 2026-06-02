# Demo Script

## Goal

Show a complete Store Intelligence flow in 3-5 minutes: upload a store video, run the pipeline, inspect generated artifacts, and demonstrate analytics through the dashboard and API.

## Setup Before Demo

Open two terminals:

```bash
uvicorn app.main:app --reload
```

```bash
streamlit run dashboard/streamlit_app.py
```

Use a short floor video named with one of the supported camera keys, for example `floor_a.mp4` or `floor_b.mp4`.

## 3-5 Minute Flow

### 1. Upload Video

Open the Streamlit dashboard. Use the sidebar upload control to upload a store video.

Talk track:

"The system starts with ordinary CCTV footage. No special sensors are required. The dashboard accepts the video and runs the same pipeline used by the backend scripts."

### 2. Run Pipeline

Click `Process Video`.

Talk track:

"The pipeline runs detection, tracking, event generation, analytics, and heatmap generation. Each stage writes artifacts so the result is inspectable, not a black box."

### 3. Show Tracking

Point to tracking artifacts in `data/outputs/tracking`, especially:

- `floor_a_tracked.mp4`
- `floor_a_tracks.json`
- `floor_b_tracked.mp4`
- `floor_b_tracks.json`

Talk track:

"Tracking turns detections into persistent visitor identities. These IDs are the foundation for dwell time, queue sessions, funnel stages, and conversion analysis."

### 4. Show Events

Show `data/outputs/events/events.json` or explain the generated event schema.

Sample event:

```json
{
  "event_type": "ZONE_ENTER",
  "visitor_id": 3,
  "camera_id": "CAM_FLOOR_A",
  "zone_id": "SKINCARE_BROWSING",
  "timestamp": "2026-06-02T10:15:20Z",
  "metadata": {
    "source": "zone_transition",
    "is_staff": false
  }
}
```

Talk track:

"Events translate raw movement into business language: entry, exit, zone enter, dwell, queue join, queue abandon, and purchase."

### 5. Show Heatmap

In the dashboard, show the `Customer Movement Heatmap` section.

Artifacts:

- `data/outputs/heatmaps/floor_a_heatmap.jpg`
- `data/outputs/heatmaps/floor_b_heatmap.jpg`

Talk track:

"The heatmap highlights where customers actually spend time and move. Staff rows are excluded when tracking data includes the `is_staff` flag."

### 6. Show Funnel Metrics

Open:

```bash
curl http://127.0.0.1:8000/funnel
```

Talk track:

"The funnel aggregates customer progression from entry to zone visit, queue, and purchase. It is session-based, so duplicate events do not inflate counts."

### 7. Show Queue Metrics

Open:

```bash
curl http://127.0.0.1:8000/metrics/queue/summary
```

Talk track:

"Queue metrics show operational friction: joins, abandonment, depth, and wait time. This helps managers identify checkout bottlenecks."

### 8. Show API Response

Open:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/metrics
curl http://127.0.0.1:8000/metrics/conversion/summary
```

Talk track:

"The same analytics visible in the dashboard are available through API endpoints for monitoring, integration, and automated reporting."

### 9. Show Recommendations

Open:

```bash
curl http://127.0.0.1:8000/recommendations
```

Talk track:

"The recommendation layer converts analytics into actions, such as improving low-engagement zones or upselling in high-dwell areas."

## Closing Summary

"This demo shows raw video becoming structured retail intelligence: tracking, events, heatmaps, queue and funnel metrics, conversion analytics, API responses, and recommendations. The system is designed so each stage is inspectable and each output is usable by store operators."

## Backup Demo Path

If live video processing takes too long, use pre-generated outputs in `data/outputs`:

1. Select an existing processed video in the dashboard sidebar.
2. Show analytics and heatmaps from existing summary files.
3. Use API endpoints to show metrics and health.
4. Run `python run_smoke_test.py` to show artifact validation.
