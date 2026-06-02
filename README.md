# Store Intelligence System

Store Intelligence System is an end-to-end retail analytics platform that turns CCTV footage into visitor behavior metrics, operational signals, recommendations, and dashboard views.

The system processes store videos through detection, tracking, event generation, analytics, API serving, and dashboard visualization. Its goal is to give physical retail teams visibility similar to what e-commerce teams already have: traffic, engagement, conversion, queue friction, and dropoff behavior.

## Features

- Person detection from retail CCTV footage.
- Visitor tracking with persistent frame-level identities.
- Canonical visitor IDs for reentry handling.
- Structured event generation for entry, exit, zone movement, dwell, queue, and purchase behavior.
- Zone dwell analytics and visitor counts.
- Queue analytics including joins, abandonment, depth, and wait time.
- Funnel analytics from entry to zone visit, queue, and purchase.
- Conversion analytics by correlating billing-zone visits with POS transactions.
- Staff exclusion for customer-only analytics.
- Heatmap generation from movement tracks.
- Recommendation, insight, anomaly, KPI, and health endpoints.
- Streamlit dashboard for upload, pipeline execution, and review.

## Architecture

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

Main components:

- Detection: YOLO-based person detection in `data/pipeline/detection`.
- Tracking: visitor identity tracking in `data/pipeline/tracking`.
- Events: business event generation in `data/pipeline/events`.
- Analytics: dwell, queue, funnel, conversion, heatmap, and recommendations in `data/pipeline/analytics`, `data/pipeline/conversion`, `data/pipeline/heatmaps`, and `data/pipeline/insights`.
- API: FastAPI app in `app`.
- Dashboard: Streamlit app in `dashboard/streamlit_app.py`.

See [ARCHITECTURE.md](ARCHITECTURE.md), [DESIGN.md](DESIGN.md), and [PIPELINE_FLOW.md](PIPELINE_FLOW.md) for reviewer-level details.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Run the dashboard:

```bash
streamlit run dashboard/streamlit_app.py
```

Run a floor video through the core pipeline:

```bash
python data/pipeline/detection/run_detection.py --input-video data/raw/floor_a.mp4 --video-name floor_a
python data/pipeline/tracking/run_tracking.py --input-video data/raw/floor_a.mp4 --video-name floor_a --output-dir data/outputs/tracking
python data/pipeline/events/run_events.py --video-name floor_a --track-file data/outputs/tracking/floor_a_tracks.json
python data/pipeline/analytics/run_zone_analytics.py --video-name floor_a --tracks-file data/outputs/tracking/floor_a_tracks.json
python data/pipeline/heatmaps/run_heatmap.py --input-video data/raw/floor_a.mp4 --video-name floor_a --tracks-file data/outputs/tracking/floor_a_tracks.json
```

## API Examples

Health:

```bash
curl http://127.0.0.1:8000/health
```

Example response:

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

Metrics:

```bash
curl http://127.0.0.1:8000/metrics
curl http://127.0.0.1:8000/metrics/conversion
curl http://127.0.0.1:8000/metrics/conversion/summary
curl http://127.0.0.1:8000/metrics/queue
curl http://127.0.0.1:8000/metrics/queue/summary
curl http://127.0.0.1:8000/funnel
```

Insights:

```bash
curl http://127.0.0.1:8000/kpis
curl http://127.0.0.1:8000/insights
curl http://127.0.0.1:8000/ai-insights
curl http://127.0.0.1:8000/recommendations
curl http://127.0.0.1:8000/anomalies
```

Heatmaps:

```bash
curl http://127.0.0.1:8000/heatmap/floor-a
curl http://127.0.0.1:8000/heatmap/floor-b
```

## Analytics Examples

Sample event:

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

Sample analytics summary:

```json
{
  "SKINCARE_BROWSING": {
    "visitors": 24,
    "total_dwell_time": 186.4
  },
  "_conversion_metrics": {
    "total_visitors": 35,
    "converted_visitors": 9,
    "billing_zone_visitors": 13,
    "conversion_rate": 25.71
  },
  "_queue_metrics": {
    "queue_joins": 13,
    "queue_abandons": 2,
    "abandonment_rate_percent": 15.38
  },
  "_funnel_metrics": {
    "entry": 35,
    "zone_visit": 30,
    "billing_queue": 13,
    "purchase": 9
  }
}
```

## Project Structure

```text
Store-Intelligence-System/
├── app/                         FastAPI routers and services
├── dashboard/                   Streamlit dashboard
├── data/
│   ├── pipeline/
│   │   ├── detection/           YOLO detection pipeline
│   │   ├── tracking/            visitor tracking pipeline
│   │   ├── events/              event generation
│   │   ├── analytics/           zone, queue, and funnel analytics
│   │   ├── conversion/          POS conversion correlation
│   │   ├── heatmaps/            movement heatmap generation
│   │   └── insights/            recommendations and ranking
│   └── outputs/                 generated artifacts
├── docs/                        supporting design notes
├── ARCHITECTURE.md              architecture overview
├── DESIGN.md                    design decisions and tradeoffs
├── PIPELINE_FLOW.md             end-to-end pipeline walkthrough
├── STAFF_EXCLUSION.md           staff exclusion audit
├── requirements.txt
└── README.md
```

## Output Artifacts

Common generated files:

- `data/outputs/detection/*_detected.mp4`
- `data/outputs/tracking/*_tracked.mp4`
- `data/outputs/tracking/*_tracks.json`
- `data/outputs/events/events.json`
- `data/outputs/events/events.csv`
- `data/outputs/analytics/*_summary.json`
- `data/outputs/analytics/*_dwell.csv`
- `data/outputs/heatmaps/*_heatmap.jpg`

## Review Notes

- The system is event-oriented: metrics are derived from track and event artifacts.
- Staff visitors are excluded from customer analytics when marked with `is_staff: true`.
- Conversion is correlation-based, using billing-zone visits and POS timestamps.
- Health is operational: `/health` reports missing outputs, event count, latest event timestamp, staleness, and active cameras.
- The current repository uses file artifacts for transparency and reviewability; production deployment can replace these reads with durable storage.

## Additional Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md): system components and operational layout.
- [DESIGN.md](DESIGN.md): design choices, rationale, and tradeoffs.
- [PIPELINE_FLOW.md](PIPELINE_FLOW.md): stage-by-stage flow with sample outputs.
- [STAFF_EXCLUSION.md](STAFF_EXCLUSION.md): staff filtering audit.
- [docs/10_conversion_analytics.md](docs/10_conversion_analytics.md): conversion implementation details.
