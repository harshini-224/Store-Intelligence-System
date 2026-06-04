"""
Video processing orchestrator.

Runs the upload pipeline as a background task and updates shared job state
for the SSE progress endpoint.
"""

import asyncio
import json
import re
import subprocess
import sys
import time
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


PIPELINE_STAGES = [
    "Tracking",
    "Event Generation",
    "Zone Analytics",
    "Conversion Analytics",
    "Heatmap",
]

logger = logging.getLogger("store_intelligence")

ZONE_SUPPORTED = {"floor_a", "floor_b"}
DEMO_MAX_SECONDS = 20


@dataclass
class ProcessingJob:
    job_id: str
    video_id: str
    video_name: str
    input_path: str
    status: str = "queued"
    progress: int = 0
    current_stage: str = PIPELINE_STAGES[0]
    logs: List[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    estimated_total_seconds: int = 0
    remaining_seconds: int = 0
    error: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "video_id": self.video_id,
            "status": self.status,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "logs": self.logs[-50:],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "estimated_seconds": self.estimated_total_seconds,
            "remaining_seconds": self.remaining_seconds,
            "error": self.error,
            "summary": self.summary,
        }


_jobs: Dict[str, ProcessingJob] = {}


def get_job(job_id: str) -> Optional[ProcessingJob]:
    return _jobs.get(job_id)


async def _run_script(cmd: List[str], job: ProcessingJob, cwd: str) -> bool:
    """Run a pipeline script asynchronously and stream stdout line-by-line."""
    job.logs.append(f"$ {' '.join(cmd)}")

    stage_idx = PIPELINE_STAGES.index(job.current_stage)
    base_progress = int((stage_idx / len(PIPELINE_STAGES)) * 100)
    next_stage_progress = int(((stage_idx + 1) / len(PIPELINE_STAGES)) * 100)
    stage_weight = next_stage_progress - base_progress

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        async def read_stream(stream, is_stderr: bool):
            while True:
                line = await stream.readline()
                if not line:
                    break

                decoded_line = line.decode(errors="replace").strip()
                if not decoded_line:
                    continue

                prefix = "ERROR: " if is_stderr else ""
                job.logs.append(f"{prefix}{decoded_line}")

                if not is_stderr:
                    match = re.search(r"(\d+(?:\.\d+)?)%", decoded_line)
                    if match:
                        sub_progress = min(100.0, float(match.group(1)))
                        job.progress = base_progress + int((sub_progress / 100) * stage_weight)

                if len(job.logs) > 300:
                    job.logs = job.logs[-200:]

        await asyncio.gather(
            read_stream(process.stdout, False),
            read_stream(process.stderr, True),
        )
        await process.wait()
        return process.returncode == 0

    except Exception as exc:
        job.logs.append(f"ERROR: {exc}")
        logger.error(f"Pipeline script error: {exc}")
        return False


def _set_stage(job: ProcessingJob, stage_index: int):
    """Update job to reflect a new pipeline stage starting."""
    job.current_stage = PIPELINE_STAGES[stage_index]
    job.progress = int((stage_index / len(PIPELINE_STAGES)) * 100)
    job.logs.append(f"> Starting: {job.current_stage}")

    if job.estimated_total_seconds > 0:
        elapsed = time.time() - job.started_at
        if job.progress > 0:
            total_est = (elapsed / job.progress) * 100
            job.remaining_seconds = max(0, int(total_est - elapsed))
        else:
            job.remaining_seconds = job.estimated_total_seconds
    
    logger.info(f"Stage changed to: {job.current_stage} ({job.progress}%)")


def get_video_duration(path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ]
        output = subprocess.check_output(cmd).decode().strip()
        return float(output)
    except Exception:
        return 0.0


def _build_summary(video_id: str) -> Dict[str, Any]:
    """Read generated outputs to build a real summary."""
    summary: Dict[str, Any] = {}
    analytics_dir = Path("data/outputs/analytics")
    tracking_dir = Path("data/outputs/tracking")
    events_dir = Path("data/outputs/events")
    heatmap_dir = Path("data/outputs/heatmaps")

    events_file = events_dir / "events.json"
    events_count = 0
    if events_file.exists():
        try:
            with open(events_file) as file:
                events = json.load(file)
            if isinstance(events, list):
                events_count = len(
                    [
                        event
                        for event in events
                        if video_id in str(event.get("camera_id", "")).lower()
                        or video_id in str(event.get("video_name", "")).lower()
                        or not any(e.get("camera_id") or e.get("video_name") for e in events)
                    ]
                )
        except Exception:
            pass
    summary["events"] = events_count

    summary_file = analytics_dir / f"{video_id}_summary.json"
    visitors = 0
    if summary_file.exists():
        try:
            with open(summary_file) as file:
                data = json.load(file)
            for key, value in data.items():
                if not key.startswith("_") and isinstance(value, dict) and "visitors" in value:
                    visitors += int(value.get("visitors", 0))
        except Exception:
            pass
    summary["visitors"] = visitors

    tracks_file = tracking_dir / f"{video_id}_tracks.json"
    tracks_count = 0
    if tracks_file.exists():
        try:
            with open(tracks_file) as file:
                tracks = json.load(file)
            if isinstance(tracks, list):
                tracks_count = len(set(track.get("track_id") for track in tracks))
        except Exception:
            pass
    summary["tracks"] = tracks_count

    heatmap_file = heatmap_dir / f"{video_id}_heatmap.jpg"
    summary["heatmaps"] = 1 if heatmap_file.exists() else 0

    return summary


async def run_pipeline(job: ProcessingJob):
    """Execute the upload processing pipeline as a background task."""
    _jobs[job.job_id] = job
    job.status = "running"
    job.logs.append(f"Processing video: {job.video_name}")

    duration = get_video_duration(job.input_path)
    max_frames_arg: List[str] = []
    if duration > 0:
        analyzed_seconds = min(duration, DEMO_MAX_SECONDS)
        job.estimated_total_seconds = int(analyzed_seconds * 2.0) + 20
        job.remaining_seconds = job.estimated_total_seconds
        job.logs.append(
            f"Video duration: {duration:.1f}s. Demo mode analyzes the first "
            f"{analyzed_seconds:.1f}s for a reliable hackathon run."
        )
        logger.info(f"Video {video_id} duration: {duration:.1f}s. Demo limit: {DEMO_MAX_SECONDS}s.")
        max_frames_arg = ["--max-seconds", str(DEMO_MAX_SECONDS)]
    else:
        job.estimated_total_seconds = 90
        job.remaining_seconds = 90

    project_root = str(Path(__file__).resolve().parents[1])
    video_id = job.video_id
    input_video = job.input_path
    tracks_file = f"data/outputs/tracking/{video_id}_tracks.json"
    analytics_file = f"data/outputs/analytics/{video_id}_summary.json"

    job.logs.append("Skipped standalone detection: tracking already runs YOLO person detection.")

    _set_stage(job, 0)
    ok = await _run_script(
        [
            "data/pipeline/tracking/run_tracking.py",
            "--input-video",
            input_video,
            "--video-name",
            video_id,
            *max_frames_arg,
        ],
        job,
        project_root,
    )
    if not ok:
        job.logs.append("Tracking failed, skipping dependent stages.")
        job.status = "failed"
        job.error = "Tracking stage failed; no track data to process."
        job.progress = 100
        job.completed_at = time.time()
        return

    _set_stage(job, 1)
    ok = await _run_script(
        [
            "data/pipeline/events/run_events.py",
            "--track-file",
            tracks_file,
            "--video-name",
            video_id,
        ],
        job,
        project_root,
    )
    if not ok:
        job.logs.append("Event generation failed, continuing...")

    _set_stage(job, 2)
    if video_id in ZONE_SUPPORTED:
        ok = await _run_script(
            [
                "data/pipeline/analytics/run_zone_analytics.py",
                "--video-name",
                video_id,
                "--tracks-file",
                tracks_file,
            ],
            job,
            project_root,
        )
        if not ok:
            job.logs.append("Zone analytics failed, continuing...")
    else:
        job.logs.append(f"Skipped zone analytics (not configured for {video_id})")

    _set_stage(job, 3)
    if video_id in ZONE_SUPPORTED:
        ok = await _run_script(
            [
                "data/pipeline/conversion/run_conversion.py",
                "--video-name",
                video_id,
                "--tracks-file",
                tracks_file,
                "--summary-file",
                analytics_file,
            ],
            job,
            project_root,
        )
        if not ok:
            job.logs.append("Conversion analytics failed, continuing...")
    else:
        job.logs.append(f"Skipped conversion analytics (not configured for {video_id})")

    _set_stage(job, 4)
    ok = await _run_script(
        [
            "data/pipeline/heatmaps/run_heatmap.py",
            "--input-video",
            input_video,
            "--video-name",
            video_id,
            "--tracks-file",
            tracks_file,
        ],
        job,
        project_root,
    )
    if not ok:
        job.logs.append("Heatmap generation failed, continuing...")

    job.progress = 100
    job.status = "completed"
    job.completed_at = time.time()
    job.summary = _build_summary(video_id)
    job.logs.append("Pipeline completed successfully.")
