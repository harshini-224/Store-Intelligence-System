# 14. Anomaly Detection & Operational Alerts

## Goal
To transform passive metrics into active operational signals that help store managers respond to real-time events.

## Anomaly Types

### 1. Queue Spikes (CRITICAL)
- **Logic**: Detected when `average_queue_depth` exceeds 5 people or wait times exceed 2 minutes.
- **Suggested Action**: "Open additional billing counter immediately."

### 2. Low Conversion (WARN)
- **Logic**: Detected when `conversion_rate` drops below 5% despite high footfall (20+ visitors).
- **Suggested Action**: "Check if staff are assisting customers in high-dwell zones."

### 3. Stale Feed (INFO/WARN)
- **Logic**: Detected when the latest event ingested is older than 5 minutes.
- **Suggested Action**: "Check camera connectivity or ingestion health."

## Severity Levels
- **CRITICAL**: Immediate action required (Queue bottlenecks).
- **WARN**: Trends that require investigation (Engagement drops).
- **INFO**: System status and connectivity updates.

## API Integration
Anomalies are served via `GET /stores/{id}/anomalies`, allowing the dashboard to display red/yellow status indicators.
