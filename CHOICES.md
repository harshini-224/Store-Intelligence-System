# System Design Choices

## Conversion Metrics
- Conversion uses actual timestamps when `video_start_time` is available.
- In the timestamp-based mode, each POS transaction is matched to at most one visitor whose billing-zone entry time falls within the configured correlation window.
- Frame-only correlation is a fallback mode. It uses sequential billing-zone visitor ordering and still preserves one transaction per visitor to avoid inflated conversion counts.
- This design avoids many-to-one transaction assignment, e.g. 1 transaction → 1 converted visitor, not 10.

## Staff Exclusion
- Visitor sessions annotated with `is_staff: true` are ignored for conversion metrics.
- Staff visitors do not count toward `total_visitors`, `billing_zone_visitors`, or `converted_visitors`.

## Queue Abandonment
- Current queue abandonment uses the hackathon-friendly interpretation: a queue session is not marked abandoned if that visitor is later correlated to a purchase before the abandonment check is finalized.
- This means `JOIN -> leave queue -> walk around store -> purchase later` suppresses `BILLING_QUEUE_ABANDON` when the visitor appears in the conversion sessions output.
- A stricter retail interpretation would define abandonment as `left the queue before purchase`, even if the visitor eventually purchased elsewhere later. That would make queue abandonment higher and better isolate queue friction from overall store conversion.
- The current implementation favors tying queue abandonment to conversion outcomes because the conversion pipeline already exports visitor-level converted state, not a precise queue-session purchase moment.

## Funnel Analytics
- Funnel aggregation is session-based and uses canonical event `visitor_id`s, so `REENTRY`, duplicate `ZONE_ENTER`, and duplicate `BILLING_QUEUE_JOIN` events do not inflate stage counts.
- The funnel stages are `ENTRY`, `ZONE_VISIT`, `BILLING_QUEUE`, and `PURCHASE`.
- `PURCHASE` is derived from existing conversion output. When converted visitor IDs are supplied to event generation, a `PURCHASE` event is emitted for funnel aggregation.
- Funnel rates use `entry` as the denominator to match the requested API shape: `zone_visit_rate = zone_visit / entry`, `queue_rate = billing_queue / entry`, and `purchase_rate = purchase / entry`.
- The API also exposes step-to-step rates for retailer actionability: `entry_to_zone_rate`, `zone_to_queue_rate`, and `queue_to_purchase_rate`.
- Staff visitors are excluded when events include `metadata.is_staff = true`.

## Data Assumptions
- Billing zone visits are detected from track positions.
- POS transactions must include a timestamp to support accurate temporal correlation.

## Group Detection
- Groups are detected using a heuristic based on spatial proximity, co-movement duration, and velocity similarity.
- Default thresholds: `GROUP_DISTANCE_THRESHOLD=150` pixels, `GROUP_FRAME_THRESHOLD=15` frames, `GROUP_VELOCITY_THRESHOLD=50.0` pixels/frame.
- Thresholds are configurable via environment variables.
- Group detection runs on tracking output only — no deep learning or external services.
- Limitations: false positives in crowded scenes, no cross-camera group tracking, may miss groups with varied walking speeds.
- Each group member's events include `metadata.group_id` for downstream analysis.
