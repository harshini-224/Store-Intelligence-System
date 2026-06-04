# 17. Real-time Video Processing

## Goal
To move from offline batch processing to live, real-time analytics as video feeds are ingested.

## Components

### 1. Ingestion Worker (`video_ingest.py`)
- Manages the asynchronous upload of video clips.
- Triggers the processor upon successful file receipt.
- Provides status updates via the `/videos` endpoint.

### 2. Orchestration Engine (`video_processor.py`)
- **Isolation**: Runs each processing task in a separate background thread or process.
- **Sequential Execution**: Ensures that Detection → Tracking → Events → Analytics run in the correct dependency order.
- **Progress Tracking**: Maintains a persistent state of which "Stage" a video is in (e.g., `Processing Detection: 45%`).

### 3. Real-time Feedback
The Next.js dashboard polls these endpoints to provide the user with a live progress bar and terminal logs during the initial data ingestion phase.

## Technical Stack
- **Thread Management**: Python's `concurrent.futures`.
- **Status Persistence**: In-memory state (upgradable to Redis).
- **Artifact Refresh**: Automatically re-loads the `metrics_service` cache once a processing job is finalized.
