# Conversion Rate Analytics Implementation

## Overview

Implemented visitor-to-purchase conversion tracking and analytics exposure through the existing pipeline and API.

## Definition of Conversion

A visitor is considered **converted** if:
1. **Billing Zone Entry**: Visitor's track position entered the billing zone (configurable rectangle)
2. **POS Transaction**: A POS transaction occurred within the correlation window (configurable frames)
3. **Same Store**: Data from the same video/camera session

**Important Design Notes:**
- Timestamp-based correlation is preferred when `video_start_time` is provided.
- If only frame data is available, a frame-order fallback is used.
- Conversion is intentionally one-to-one: a single POS transaction may convert at most one visitor.
- `is_staff: true` visitors are excluded from all conversion metrics.

**Formula:**
```
conversion_rate = (converted_visitors / total_visitors) × 100
```

## Architecture

### 1. Data Flow

```
Visitor Tracks (JSON)
    ↓
[Conversion Tracker]
    ↓ correlates with ↓
POS Transactions (JSON/CSV)
    ↓
Conversion Statistics
    ↓
Updated Analytics Summary JSON
    ↓
REST API Endpoints
```

### 2. New Modules

#### `data/pipeline/conversion/pos_ingestion.py`
- **Purpose**: Ingest POS transaction data
- **Key Classes**:
  - `POSTransaction`: Represents a single transaction
  - `POSIngestionLayer`: Handles JSON/CSV import
- **Supported Formats**:
  - JSON: Array of transaction objects
  - CSV: Columns (transaction_id, timestamp, amount, payment_method)

#### `data/pipeline/conversion/conversion_tracker.py`
- **Purpose**: Correlate visitor billing zone visits with POS transactions
- **Key Classes**:
  - `VisitorSession`: Tracks individual visitor's session data
  - `ConversionTracker`: Main orchestrator
- **Key Methods**:
  - `load_tracks()`: Load visitor tracking data
  - `load_pos_data()`: Load POS transactions
  - `correlate_conversions()`: Run correlation algorithm
  - `get_conversion_stats()`: Calculate metrics
  - `export_sessions()`: Save visitor sessions with conversion flags

#### `data/pipeline/conversion/run_conversion.py`
- **Purpose**: Orchestrate full conversion analysis pipeline
- **CLI Arguments**:
  - `--video-name`: Video identifier (floor_a, floor_b)
  - `--tracks-file`: Path to tracking JSON
  - `--pos-file`: Path to POS transactions
  - `--dwell-file`: Path to dwell time data
  - `--summary-file`: Output analytics summary path
  - `--sessions-output`: Output visitor sessions path
  - `--video-start-time`: Video start timestamp (ISO 8601)

### 3. Updated Modules

#### `data/pipeline/analytics/analytics_report.py`
- **Change**: Added optional `conversion_stats` parameter to `generate()` method
- **Behavior**: Appends conversion metrics to analytics summary under `_conversion_metrics` key

#### `app/services/metrics_service.py`
- **Added Functions**:
  - `load_conversion_metrics()`: Extract conversion stats from analytics
  - `get_conversion_summary()`: High-level conversion summary
- **Behavior**: Aggregates floor-level conversion data

#### `app/metrics.py`
- **New Endpoints**:
  - `GET /metrics/conversion`: Detailed conversion metrics by floor
  - `GET /metrics/conversion/summary`: High-level conversion summary

## Configuration

### Constants (in `conversion_tracker.py`)

```python
CORRELATION_WINDOW_FRAMES = 1500  # ~50 seconds at 30fps
DEFAULT_FPS = 30

BILLING_ZONE = {
    "name": "BILLING_ZONE",
    "x1": 0,
    "y1": 0,
    "x2": 1920,
    "y2": 300  # Configurable
}
```

## Data Structures

### POS Transaction Input (JSON)
```json
[
    {
        "transaction_id": "TXN_001",
        "timestamp": "2026-05-30T10:05:30Z",
        "amount": 150.50,
        "payment_method": "credit_card"
    }
]
```

### Visitor Session (Output)
```json
{
    "1": {
        "visitor_id": 1,
        "first_frame": 10,
        "last_frame": 500,
        "billing_zone_entry_frame": 250,
        "zones_visited": ["PREMIUM_SKINCARE", "BILLING_ZONE"],
        "converted": true,
        "transaction_id": "TXN_001",
        "dwell_time_seconds": 45.5
    }
}
```

### Analytics Summary (Updated JSON)
```json
{
    "PREMIUM_SKINCARE": {
        "visitors": 40,
        "total_dwell_time": 162.36
    },
    "BEAUTY_CONSULTATION": {
        "visitors": 78,
        "total_dwell_time": 326.42
    },
    "_conversion_metrics": {
        "total_visitors": 150,
        "converted_visitors": 45,
        "billing_zone_visitors": 60,
        "conversion_rate": 30.0,
        "billing_zone_rate": 40.0
    }
}
```

## API Responses

### GET `/metrics/conversion`
```json
{
    "floor_a": {
        "total_visitors": 150,
        "converted_visitors": 45,
        "billing_zone_visitors": 60,
        "conversion_rate": 30.0,
        "billing_zone_rate": 40.0
    },
    "floor_b": {
        "total_visitors": 120,
        "converted_visitors": 36,
        "billing_zone_visitors": 48,
        "conversion_rate": 30.0,
        "billing_zone_rate": 40.0
    },
    "_aggregate": {
        "total_visitors": 270,
        "total_converted_visitors": 81,
        "aggregate_conversion_rate": 30.0
    }
}
```

### GET `/metrics/conversion/summary`
```json
{
    "status": "success",
    "summary": {
        "total_visitors": 270,
        "converted_visitors": 81,
        "conversion_rate_percent": 30.0
    },
    "by_floor": {
        "floor_a": {
            "total_visitors": 150,
            "converted_visitors": 45,
            "conversion_rate_percent": 30.0,
            "billing_zone_visitors": 60
        },
        "floor_b": {
            "total_visitors": 120,
            "converted_visitors": 36,
            "conversion_rate_percent": 30.0,
            "billing_zone_visitors": 48
        }
    }
}
```

## Usage

### 1. Ingest POS Data
```bash
python data/pipeline/conversion/run_conversion.py \
    --video-name floor_a \
    --pos-file data/raw/transactions.json
```

### 2. Full Conversion Analysis Pipeline
```bash
python data/pipeline/conversion/run_conversion.py \
    --video-name floor_a \
    --tracks-file data/outputs/tracking/floor_a_tracks.json \
    --pos-file data/raw/transactions.json \
    --dwell-file data/outputs/analytics/floor_a_dwell.csv \
    --summary-file data/outputs/analytics/floor_a_summary.json \
    --sessions-output data/outputs/conversion/floor_a_sessions.json
```

### 3. With Video Timestamp
```bash
python data/pipeline/conversion/run_conversion.py \
    --video-name floor_a \
    --video-start-time "2026-05-30T10:00:00Z"
```

### 4. Query API
```bash
curl http://localhost:8000/metrics/conversion
curl http://localhost:8000/metrics/conversion/summary
```

## Integration with Existing Pipeline

The conversion module **does not modify** existing functionality:

- ✅ Detection pipeline unchanged
- ✅ Tracking pipeline unchanged
- ✅ Zone analytics unchanged
- ✅ Existing API endpoints preserved
- ✅ Event generation unaffected

**Enhancement points:**
- Analytics summary now includes `_conversion_metrics`
- New API endpoints for conversion data
- Metrics service extended with conversion functions

## Tests

Run conversion tests:
```bash
pytest data/pipeline/conversion/test_conversion.py -v
```

### Test Coverage
- ✅ POS transaction creation and ingestion (JSON/CSV)
- ✅ Visitor billing zone detection
- ✅ Conversion calculation
- ✅ Empty POS files (no conversions)
- ✅ Zero visitors (edge case)
- ✅ Multiple transactions
- ✅ Multiple visitors with mixed conversions
- ✅ Conversion rate accuracy

## Files Changed

### New Files
- `data/pipeline/conversion/__init__.py`
- `data/pipeline/conversion/pos_ingestion.py`
- `data/pipeline/conversion/conversion_tracker.py`
- `data/pipeline/conversion/run_conversion.py`
- `data/pipeline/conversion/test_conversion.py`

### Modified Files
- `data/pipeline/analytics/analytics_report.py`
- `app/services/metrics_service.py`
- `app/metrics.py`

## Constraints & Design Decisions

1. **No Hardcoding**: All values (correlation window, billing zone coords) are configurable constants
2. **Preserves Existing**: No changes to core detection, tracking, or zone analytics
3. **Optional POS Data**: System continues to work if POS file missing (0 conversions)
4. **Frame-Based Correlation**: Default approach uses frame numbers (no video timestamp needed)
5. **Timestamp-Based Alternative**: Supports ISO 8601 timestamps for precise time-based correlation
6. **JSON Storage**: Conversion data embedded in analytics summaries for easy persistence

## Future Enhancements

- Multi-camera visitor re-identification
- Time-series conversion trending
- Predictive conversion modeling
- Queue impact on conversion analysis
- Basket size analysis
- Payment method insights
- Hourly/daily conversion patterns
