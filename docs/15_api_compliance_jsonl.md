# 15. API Compliance & JSONL Export

## Compliance Architecture
The system is built to meet the "Production Readiness" standards of the Purplle Challenge, emphasizing standardization and multi-store scalability.

## 1. Store-Scoped Endpoints
The API is designed for a multi-store retailer. All endpoints are scoped by `store_id` to ensure data isolation and performance.
- `GET /stores/{id}/metrics`
- `GET /stores/{id}/funnel`
- `GET /stores/{id}/heatmap`
- `GET /stores/{id}/anomalies`

## 2. Standardized Event Log (JSONL)
The primary data deliverable is a `JSONL` (JSON Lines) file containing every behavioral event detected in the store.

- **Storage**: `data/outputs/events/events.jsonl`
- **Schema**: Canonical 9-field format.
    - `event_id`, `visitor_id`, `store_id`, `camera_id`, `timestamp`, `event_type`, `zone_id`, `confidence`, `metadata`.

## 3. Robust Ingestion
The `POST /events/ingest` endpoint is built with:
- **Idempotency**: Uses a 1MB memory-cached `SEEN_EVENT_IDS` set to prevent duplicate processing.
- **Partial Success**: Malformed events in a batch do not crash the entire ingestion.
- **Batch Limit**: Enforces a 500-event limit per request to protect memory.

## 4. Operational Telemetry
Every API request is logged with structured JSON containing:
- `trace_id`: For request tracing.
- `latency_ms`: For performance monitoring.
- `status_code`: For health tracking.
