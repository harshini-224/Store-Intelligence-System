# Design

## Design Goals

The system is designed to turn existing CCTV footage into actionable retail intelligence without requiring specialized sensors. The design favors inspectable pipeline outputs, modular processing stages, and business-facing events over opaque end-to-end scoring.

## Why YOLO?

YOLO is used for person detection because it is fast, widely adopted, and practical for frame-by-frame video processing. It gives the system a strong baseline detector without requiring custom model training before the analytics pipeline can be evaluated.

Tradeoffs:

- YOLO is efficient enough for prototyping and near-real-time processing.
- It works well for visible people but can miss heavily occluded visitors.
- Detection quality depends on camera angle, lighting, motion blur, and crowd density.
- The current implementation uses a general model; a store-specific fine-tuned model could improve recall later.

## Why ByteTrack?

ByteTrack-style tracking is used because retail analytics depend on persistent visitor identity, not just isolated detections. Tracking enables dwell time, queue sessions, reentry handling, and funnel aggregation.

Tradeoffs:

- Tracking reduces duplicate counts across frames.
- It is more robust than treating each detection independently.
- Identity switches can still happen during occlusion or dense crowds.
- Multi-camera identity is not fully solved by tracking alone; the current system focuses on per-camera and heuristic canonical IDs.

## Why Event Architecture?

The system converts low-level movement into structured events such as `ENTRY`, `ZONE_ENTER`, `BILLING_QUEUE_JOIN`, and `PURCHASE`. This separates computer vision from business analytics.

Benefits:

- Events are easier to inspect than raw tracks.
- Metrics can be recomputed from event history.
- APIs and dashboards can use stable business concepts.
- New analytics can be added without rewriting detection or tracking.

Tradeoffs:

- Event rules need careful calibration per camera view.
- Events can be wrong if upstream tracks are noisy.
- Event schemas must remain consistent as new metrics are added.

## Why Canonical Visitor IDs?

Raw tracker IDs can fragment when a visitor exits and reappears or when tracking temporarily loses a person. Canonical visitor IDs group related raw IDs into one business visitor identity.

Benefits:

- Reentry does not inflate visitor counts.
- Funnel stages stay session-based rather than track-fragment-based.
- Queue and conversion analysis can reason about a visitor over time.

Tradeoffs:

- Canonicalization is heuristic in the current implementation.
- Aggressive matching can merge two different people.
- Conservative matching can leave one visitor split into multiple IDs.

## Why Reentry Heuristics?

Reentry is detected using time, position, line-crossing side, and bounding-box size similarity. This gives the system a lightweight way to recognize likely returning visitors without requiring a full re-identification model in the critical path.

Tradeoffs:

- It is explainable and easy to tune.
- It avoids counting brief exits as new visitors.
- It can fail when several people cross near the same place at the same time.
- It is camera-specific and should be validated against real store footage.

## Why Conversion Correlation?

The system correlates visitor billing-zone presence with POS transactions to estimate offline conversion. This bridges behavioral video data and sales data.

Definition:

A visitor is considered converted when they entered the billing zone and a POS transaction can be matched within the configured correlation window.

Tradeoffs:

- This avoids requiring direct identity linkage between a customer and a receipt.
- It gives a practical conversion estimate from available data.
- It is probabilistic, especially in busy checkout periods.
- The implementation keeps matching one-to-one so one transaction cannot convert many visitors.

## Why Separate Analytics Artifacts?

Analytics are written as JSON, CSV, and image artifacts under `data/outputs`. This makes the system easier to review, debug, and demo.

Tradeoffs:

- File artifacts are simple and transparent.
- They avoid requiring a database for every review or demo.
- They are less suitable than durable storage for high-volume production deployments.
- A production deployment can replace artifact reads with database-backed services while keeping the event and metric contracts.

## Why Staff Exclusion?

Retail metrics should describe customer behavior. Staff movement can distort dwell time, heatmaps, queues, and conversion funnels. The system carries `is_staff` through tracking and events so staff can be filtered consistently.

Tradeoffs:

- Excluding staff improves business accuracy.
- Staff identification must be reliable.
- Unknown or unmarked staff can still appear as customers.

## Why FastAPI and Streamlit?

FastAPI provides a lightweight service layer for operational and analytics endpoints. Streamlit provides a fast dashboard for processing videos, inspecting outputs, and presenting metrics.

Tradeoffs:

- FastAPI is suitable for API consumers and monitoring.
- Streamlit is effective for demos and internal tools.
- For high-scale production, dashboard execution and pipeline processing should be separated from request handling.

## Known Design Constraints

- Multi-camera re-identification is not a complete identity graph.
- Conversion is correlation-based, not receipt-level identity matching.
- Heatmaps are only staff-aware when generated from track files containing `is_staff`.
- Staleness in `/health` depends on event timestamps, so frame-only event streams cannot prove freshness.
- File-based outputs are reviewer-friendly but should be hardened for production concurrency.
