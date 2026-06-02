# Validation Checklist

Use this checklist before a final demo or review. Mark each item after checking the artifact or endpoint.

## Detection Output

- [ ] `data/outputs/detection` exists.
- [ ] At least one `*_detected.mp4` file exists.
- [ ] Detected video opens and contains person annotations.

Expected examples:

- `data/outputs/detection/entrance_detected.mp4`
- `data/outputs/detection/billing_detected.mp4`

## Tracking Output

- [ ] `data/outputs/tracking` exists.
- [ ] At least one `*_tracked.mp4` file exists.
- [ ] At least one `*_tracks.json` file exists.
- [ ] Track JSON contains `frame`, `track_id`, `center_x`, and `center_y`.

Expected examples:

- `data/outputs/tracking/floor_a_tracks.json`
- `data/outputs/tracking/floor_b_tracks.json`

## Events Output

- [ ] `data/outputs/events` exists.
- [ ] `events.json` or `events.csv` exists.
- [ ] Event output contains one or more events.
- [ ] Events include `visitor_id` and `event_type`.
- [ ] Events include `timestamp` when freshness monitoring is needed.

Expected examples:

- `data/outputs/events/events.json`
- `data/outputs/events/events.csv`

## Analytics Output

- [ ] `data/outputs/analytics` exists.
- [ ] At least one `*_summary.json` file exists.
- [ ] Summary contains zone records with `visitors` and `total_dwell_time`.
- [ ] Summary can include `_conversion_metrics`, `_queue_metrics`, and `_funnel_metrics`.

Expected examples:

- `data/outputs/analytics/floor_a_summary.json`
- `data/outputs/analytics/floor_b_summary.json`

## Heatmap Output

- [ ] `data/outputs/heatmaps` exists.
- [ ] At least one `*_heatmap.jpg` exists.
- [ ] Heatmap image opens and visually overlays customer movement.

Expected examples:

- `data/outputs/heatmaps/floor_a_heatmap.jpg`
- `data/outputs/heatmaps/floor_b_heatmap.jpg`

## Conversion Metrics

- [ ] Conversion pipeline has been run or conversion metrics are embedded in analytics summaries.
- [ ] `_conversion_metrics.total_visitors` exists when conversion data is available.
- [ ] `_conversion_metrics.converted_visitors` exists.
- [ ] `_conversion_metrics.conversion_rate` exists.
- [ ] Staff visitors are excluded from conversion counts.

API check:

```bash
curl http://127.0.0.1:8000/metrics/conversion/summary
```

## Queue Metrics

- [ ] Queue metrics are embedded in floor analytics summaries or available through the queue endpoint.
- [ ] `queue_joins` exists.
- [ ] `queue_abandons` exists.
- [ ] `abandonment_rate` or `abandonment_rate_percent` exists.
- [ ] Staff visitors are excluded from queue sessions.

API check:

```bash
curl http://127.0.0.1:8000/metrics/queue/summary
```

## Funnel Metrics

- [ ] Funnel metrics are embedded in analytics summaries.
- [ ] Funnel response includes `entry`, `zone_visit`, `billing_queue`, and `purchase`.
- [ ] Funnel response includes dropoffs and rates.
- [ ] Staff visitors are excluded from funnel stages.

API check:

```bash
curl http://127.0.0.1:8000/funnel
```

## API Responses

- [ ] API server starts with `uvicorn app.main:app --reload`.
- [ ] `GET /health` returns operational status.
- [ ] `GET /metrics` returns analytics summaries.
- [ ] `GET /kpis` returns visitor and dwell KPIs.
- [ ] `GET /recommendations` returns recommendation list.
- [ ] `GET /heatmap/floor-a` or `GET /heatmap/floor-b` returns an image response.

## Dashboard Rendering

- [ ] Dashboard starts with `streamlit run dashboard/streamlit_app.py`.
- [ ] Video upload control renders.
- [ ] Processed video selector renders when outputs exist.
- [ ] KPI row renders.
- [ ] Zone engagement chart renders.
- [ ] Heatmap section renders.
- [ ] Executive summary renders.
- [ ] Recommendations render.

## Automated Smoke Test

- [ ] Run `python run_smoke_test.py`.
- [ ] Review PASS/FAIL summary.
- [ ] Resolve any FAIL items before demo.

Current known failure mode:

- If `events.json` exists but contains `[]`, rerun event generation for a floor video before the final demo:

```bash
python data/pipeline/events/run_events.py --video-name floor_a --track-file data/outputs/tracking/floor_a_tracks.json
```
