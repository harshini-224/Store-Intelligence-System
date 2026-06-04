# Deployment Guide

This project deploys as a two-container Docker stack behind one public app URL:

- `frontend`: Next.js web app, public entrypoint on port `3000`.
- `api`: FastAPI + video pipeline, private Docker service on port `8000`.

The browser never needs to call the backend port directly. Next.js proxies `/health`, `/ingest`, `/frontend-api/*`, `/recommendations`, and `/kpis` to the API container.

## Local Docker Run

```bash
docker compose up --build
```

Open:

```text
http://localhost:3000
```

Upload page:

```text
http://localhost:3000/upload
```

Health check through the public frontend URL:

```bash
curl http://localhost:3000/health
```

## Detached Mode

```bash
docker compose up --build -d
```

Stop:

```bash
docker compose down
```

## Public Deployment

Use any Docker Compose host, for example Render, Railway, Fly.io, Azure Container Apps, AWS ECS, or a VPS.

Deploy command:

```bash
docker compose up --build -d
```

Expose only the `frontend` service port:

```text
3000
```

Do not expose the `api` service publicly. The frontend reaches it internally at:

```text
http://api:8000
```

## Required Files In Image

The API image includes:

- `app/`
- `data/pipeline/`
- `requirements.txt`
- `yolo11n.pt`

The `data/` directory is mounted as a volume so uploaded videos and generated outputs persist.

## Environment Variables

| Service | Variable | Value |
|---|---|---|
| frontend | `INTERNAL_API_URL` | `http://api:8000` |
| frontend | `NEXT_PUBLIC_API_BASE_URL` | empty string |
| api | `PYTHONUNBUFFERED` | `1` |

## Hackathon Demo Behavior

Uploaded videos run in demo mode. The backend analyzes the first 20 seconds so the app produces tracking, events, and heatmaps quickly enough for a live demo.
