"""
Video Ingest API

Provides endpoints for uploading videos and streaming processing progress via SSE.
"""

import asyncio
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, UploadFile
from fastapi.responses import StreamingResponse

from app.video_processor import ProcessingJob, get_job, run_pipeline

router = APIRouter(tags=["ingest"])

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def _sanitize_video_name(filename: str) -> str:
    """Convert a filename into a safe video_id (lowercase, underscores)."""
    stem = Path(filename).stem
    # Replace non-alphanumeric chars with underscore, collapse multiples
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", stem).strip("_").lower()
    return clean or "video"


@router.post("/ingest")
async def ingest_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload a video file, save it to data/raw/, and kick off the full
    processing pipeline in the background.

    Returns the job_id and video_id immediately so the frontend can
    connect to the SSE progress stream.
    """
    video_id = _sanitize_video_name(file.filename or "upload")
    job_id = str(uuid.uuid4())

    # Save uploaded file
    dest = RAW_DIR / f"{video_id}.mp4"
    contents = await file.read()
    with open(dest, "wb") as f:
        f.write(contents)

    # Create the processing job
    job = ProcessingJob(
        job_id=job_id,
        video_id=video_id,
        video_name=file.filename or "upload.mp4",
        input_path=str(dest),
    )

    # Start background pipeline
    background_tasks.add_task(run_pipeline, job)

    return {
        "job_id": job_id,
        "video_id": video_id,
        "message": f"Video '{file.filename}' queued for processing.",
    }


@router.get("/ingest/{job_id}/progress")
async def stream_progress(job_id: str):
    """
    SSE endpoint that streams real-time processing progress for a given job.
    
    The frontend connects via EventSource and receives JSON updates as each
    pipeline stage progresses. The stream closes after the job completes or fails.
    """
    async def event_generator():
        last_hash = None
        max_wait = 600  # 10 minutes max
        waited = 0

        while waited < max_wait:
            job = get_job(job_id)
            if job is None:
                yield f"data: {_json_dump({'error': 'Job not found', 'status': 'failed'})}\n\n"
                return

            payload = job.to_dict()
            current_hash = (payload["status"], payload["progress"], payload["current_stage"], len(payload["logs"]), payload["remaining_seconds"])

            # Only send if something changed
            if current_hash != last_hash:
                last_hash = current_hash
                yield f"data: {_json_dump(payload)}\n\n"

            if payload["status"] in ("completed", "failed"):
                return

            await asyncio.sleep(0.8)
            waited += 0.8

        # Timeout
        yield f"data: {_json_dump({'error': 'Timeout', 'status': 'failed'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _json_dump(obj) -> str:
    import json
    return json.dumps(obj, default=str)
