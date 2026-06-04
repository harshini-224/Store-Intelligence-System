# Technical Choices

This document outlines the key technical decisions made during the development of the Store Intelligence System, following the Purplle Challenge requirements.

## 1. Model Selection (Detection & Tracking)

- **AI Suggestion**: Use YOLOv8 or YOLOv9 for the best balance of speed and accuracy.
- **Options Considered**: YOLOv8, YOLOv11n, RT-DETR.
- **My Choice**: **YOLOv11n with ByteTrack**.
- **Rationale**: 
    - YOLOv11n (nano) was selected for its superior efficiency in processing long 20-minute CCTV clips on standard hardware without GPU acceleration. 
    - While the AI suggested YOLOv8 as a safe default, YOLOv11 offers improved feature extraction which is critical for the "partial occlusion" edge cases mentioned in the challenge clips (e.g., people behind displays).
    - ByteTrack was chosen over DeepSORT because it avoids the computational overhead of a separate Re-ID appearance model while still providing robust track-linking using detection boxes only.

## 2. Event Schema Design

- **AI Suggestion**: A flat schema with `timestamp`, `event`, and `values`.
- **Options Considered**: Flat key-value pairs, Hierarchical JSON, 9-field Canonical Schema.
- **My Choice**: **9-field Canonical Schema** (`event_id`, `visitor_id`, `store_id`, `camera_id`, `timestamp`, `event_type`, `zone_id`, `confidence`, `metadata`).
- **Rationale**: 
    - I overrode the AI's "flat" suggestion to ensure global uniqueness and traceability. 
    - By requiring `store_id` and `camera_id` at the top level, we can partition the data easily for multi-city, multi-store queries. 
    - The `metadata` field acts as a future-proof bucket for event-specific data (like `queue_depth` for `BILLING_QUEUE_JOIN`) without breaking downstream consumers that rely on the top-level 9 fields.

## 3. API Architecture Choice

- **AI Suggestion**: Build a standard Flask or Express.js API.
- **Options Considered**: FastAPI (Python), Flask (Python), Django (Python).
- **My Choice**: **FastAPI**.
- **Rationale**: 
    - FastAPI was chosen for its native support for Pydantic (autogenerating OpenAPI/Swagger documentation) and its high-performance asynchronous capabilities. 
    - Asynchronous endpoints are critical for Stage 4 of the challenge (Real-time Dashboard), as the API needs to handle both event ingestion and live dashboard updates concurrently without blocking.
    - AI specifically recommended FastAPI for the "Production Readiness" part of the challenge due to its built-in schema validation, which I leveraged to ensure the API returns 422 errors for malformed events rather than crashing.

---

## Existing Operational Choices (Reference)

### Conversion Metrics
- Each POS transaction is matched to at most one visitor whose billing-zone entry time falls within the configured correlation window. This avoids many-to-one transaction assignment.
- Visitor sessions annotated with `is_staff: true` are ignored for conversion metrics.

### Queue Abandonment
- A visitor is NOT marked as having abandoned the queue if they later complete a purchase in the same session. This ensures that "walk-aways" who eventually return to buy are not counted as failures.

### Funnel Analytics
- Funnel aggregation is session-based and uses canonical visitor IDs, so re-entries and duplicate zone events do not inflate counts.
- Rates are exposed both from `Entry` (total capture) and step-to-step (actionable dropout).

### Group Detection
- Groups are detected using a heuristic based on spatial proximity, co-movement duration, and velocity similarity. This avoids the need for an expensive "Social Group Detection" model while meeting the challenge requirements for individual counting in groups.
