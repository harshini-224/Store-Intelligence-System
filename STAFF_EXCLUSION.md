# Staff Exclusion Audit

## Staff Representation

Status: PASS

Location: `data/outputs/tracking/*_tracks.json`, `data/pipeline/events/run_events.py`, `data/pipeline/conversion/conversion_tracker.py`

Logic:

Staff is represented as `is_staff: true` on tracking rows. Event generation carries this into `event.metadata.is_staff`. Conversion sessions aggregate the flag on `VisitorSession.is_staff` so a visitor remains staff if any row marks them as staff.

---

## Visitor Count

Status: PASS

Location: `data/pipeline/analytics/run_zone_analytics.py`, `data/pipeline/conversion/conversion_tracker.py`, `app/kpis.py`, `dashboard/streamlit_app.py`

Logic:

Zone visitor counts skip tracking rows where `is_staff` is true before dwell and visitor aggregation. Conversion visitor counts filter out `VisitorSession.is_staff`. KPI and dashboard visitor totals now iterate only real zone metrics and consume the staff-excluded zone summaries.

---

## Conversion Analytics

Status: PASS

Location: `data/pipeline/conversion/conversion_tracker.py`, `data/pipeline/conversion/run_conversion.py`, `app/services/metrics_service.py`, `app/metrics.py`

Logic:

Conversion correlation only considers non-staff sessions for frame-based and timestamp-based POS matching. Conversion stats compute `total_visitors`, `billing_zone_visitors`, and `converted_visitors` from non-staff sessions only. API conversion responses load these pre-filtered `_conversion_metrics`.

---

## Queue Metrics

Status: PASS

Location: `data/pipeline/events/run_events.py`, `data/pipeline/analytics/queue_tracker.py`, `app/services/metrics_service.py`, `app/metrics.py`

Logic:

`run_events.py` tracks canonical visitor staff state and bypasses queue tracking for staff visitors. Queue join, abandon, depth, wait, and conversion metrics are therefore built only from non-staff queue sessions. API queue responses load the pre-filtered `_queue_metrics`.

---

## Funnel Metrics

Status: PASS

Location: `data/pipeline/analytics/funnel_tracker.py`, `data/pipeline/events/run_events.py`, `app/services/metrics_service.py`, `app/funnel.py`

Logic:

Funnel events with `metadata.is_staff = true` add the visitor to the staff set and are ignored. Later events for a known staff visitor are also ignored. Purchase events emitted from conversion sessions are skipped when the visitor is known staff. API funnel responses load the pre-filtered `_funnel_metrics`.

---

## Zone Dwell Metrics

Status: PASS

Location: `data/pipeline/analytics/run_zone_analytics.py`, `data/pipeline/analytics/dwell_time.py`, `data/pipeline/analytics/analytics_report.py`

Logic:

Staff tracking rows are skipped before zone lookup and dwell updates. `DwellTimeTracker` and `AnalyticsReport` then only see customer dwell records, so zone `visitors` and `total_dwell_time` exclude staff.

---

## Heatmaps

Status: PASS

Location: `data/pipeline/heatmaps/run_heatmap.py`, `app/heatmap.py`

Logic:

Heatmap generation now uses the existing tracking JSON when available and skips `is_staff: true` rows before updating heatmap density. The API serves the generated heatmap image. Direct raw-video fallback remains available for missing track files, but raw video has no staff flag to filter.

---

## Recommendations

Status: PASS

Location: `data/pipeline/insights/recommendation_engine.py`, `app/recommendation.py`

Logic:

Recommendations consume staff-excluded zone summaries and now ignore reserved analytics blocks such as `_conversion_metrics`, `_queue_metrics`, and `_funnel_metrics`. A staff-only zone summary produces no recommendations.

---

## Insights

Status: PASS

Location: `app/insights.py`, `app/ai_insights.py`, `data/pipeline/insights/ranking_engine.py`

Logic:

Insight and ranking code now iterates only zone records with `visitors` and `total_dwell_time`, skipping reserved analytics metadata blocks. The underlying zone summaries exclude staff before these insights run.

---

## KPIs

Status: PASS

Location: `app/kpis.py`, `dashboard/streamlit_app.py`

Logic:

KPIs use only real zone metric records and consume staff-excluded zone summaries. Reserved analytics blocks are no longer treated as zones.

---

## API Responses

Status: PASS

Location: `app/main.py`, `app/metrics.py`, `app/funnel.py`, `app/kpis.py`, `app/insights.py`, `app/anomalies.py`, `app/recommendation.py`, `app/ai_insights.py`, `app/heatmap.py`

Logic:

Metric APIs expose pre-filtered conversion, queue, funnel, and zone summaries. Derived APIs now use zone-only iteration where they calculate from summaries. Heatmap APIs return images generated from staff-aware track data in the normal pipeline.

---

## Gaps Fixed

Status: PASS

Location: `data/pipeline/analytics/run_zone_analytics.py`, `data/pipeline/heatmaps/run_heatmap.py`, `app/analytics_utils.py`, `app/kpis.py`, `app/insights.py`, `app/anomalies.py`, `app/ai_insights.py`, `dashboard/streamlit_app.py`, `data/pipeline/insights/recommendation_engine.py`, `data/pipeline/insights/ranking_engine.py`

Logic:

Fixed staff leakage in zone dwell aggregation, heatmap density generation, and derived analytics consumers that treated embedded `_..._metrics` blocks as zones.

---

## Validation Tests

Status: PASS

Location: `test_staff_exclusion.py`

Logic:

Regression tests verify that staff visitors are not counted in zone visitors, not converted, not included in queue joins, not included in funnel stages, and not included in recommendations.
