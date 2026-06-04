# Store Intelligence System (Purplle Challenge)

An end-to-end retail analytics platform that transforms raw CCTV footage into actionable business intelligence (Conversion Rate, Dwell Time, Queue Analytics, Anomaly Detection).

## 🚀 5-Command Setup

Go from `git clone` to a running system in 5 commands:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Process sample clips into events (Detection -> Tracking -> Events)
python data/pipeline/detection/run_detection.py --input-video data/raw/floor_a.mp4 --video-name floor_a
python scripts/generate_jsonl.py

# 3. Start the system (API & Dashboard) via Docker
docker compose up -d

# 4. Ingest events into the running API (Stage 3)
curl -X POST http://127.0.0.1:8000/events/ingest -H "Content-Type: application/json" -d @data/outputs/events/events.json

# 5. Access the Intelligence Dashboard
# Open http://localhost:3000 in your browser
```

## 📊 Core Deliverables

- **Event Log**: [`data/outputs/events/events.jsonl`](data/outputs/events/events.jsonl) (Canonical 9-field schema).
- **Mandatory Documentation**: [DESIGN.md](DESIGN.md) (AI-Assisted Decisions) and [CHOICES.md](CHOICES.md) (Model Selection & Architecture).
- **Compliance API**: FastAPI container serving real-time metrics and anomalies.
- **Next.js Dashboard**: Visual feedback for visitor tracks, conversion funnels, and heatmaps.

## 📡 Mandatory API Endpoints

| Endpoint | Description | Key Metric |
| :--- | :--- | :--- |
| `GET /stores/{id}/metrics` | Aggregated Store KPI | **Conversion Rate** |
| `GET /stores/{id}/funnel` | Entry → Purchase Pipeline | **Drop-off %** |
| `GET /stores/{id}/heatmap` | Zone Intensity (0-100) | **Engagement intensity** |
| `GET /stores/{id}/anomalies` | CRITICAL / WARN signals | **Queue Spikes** |
| `POST /events/ingest` | 500-batch Event Ingestion | **Idempotency** |

## 🛠️ Tech Stack & AI Usage

- **Detection**: YOLOv11n (High efficiency for 1080p/15fps retail footage).
- **Tracking**: ByteTrack (Robust motion tracking without Re-ID overhead).
- **Backend**: FastAPI (Python) with JSON Structured Logging & Pydantic validation.
- **Frontend**: Next.js 15 with TailwindCSS & Recharts.
- **AI-Assisted Engineering**: LLMs were used for event schema design, Pydantic model generation, and complex anomaly detection logic. All AI prompts and overrides are documented in `DESIGN.md` and test file headers.

## 🧪 Verification

Validate the JSONL event log schema:
```bash
python validate_jsonl.py
```

Run mandatory test suite (70% coverage):
```bash
pytest tests/ -v
```

---
*Developed for the Purplle Engineering Hiring Challenge 2026.*
