import json
import re
import sys
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
FLOOR_CAMERAS = {"floor_a", "floor_b"}
KNOWN_CAMERAS = ("floor_a", "floor_b", "billing", "entrance", "corner")


st.set_page_config(
    page_title="Store Intelligence Dashboard",
    layout="wide"
)

st.title("Store Intelligence Dashboard")
st.caption("AI Powered Retail Analytics")


def output_path(*parts):
    return ROOT / "data" / "outputs" / Path(*parts)


def relative_output_path(*parts):
    return Path("data") / "outputs" / Path(*parts)


def infer_camera_type(video_key):
    key = (video_key or "").lower()
    for camera in KNOWN_CAMERAS:
        if camera in key:
            return camera
    return key


def normalize_video_key(video_path_or_name):
    stem = Path(video_path_or_name or "").stem
    return infer_camera_type(stem) or stem


def load_json(path, default=None):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_processing_state(**updates):
    state = st.session_state.setdefault(
        "processing",
        {
            "stage": "Idle",
            "progress": 0,
            "status": "idle",
            "message": "No active processing run.",
            "summary": None,
        }
    )
    state.update(updates)


def render_stage_checklist(container, stages, current_stage=None, completed=None, failed=None):
    completed = set(completed or [])
    lines = []
    for stage in stages:
        if stage == failed:
            marker = "x"
            label = "Failed"
        elif stage in completed:
            marker = "✓"
            label = "Complete"
        elif stage == current_stage:
            marker = "⟳"
            label = "Running"
        else:
            marker = "•"
            label = "Waiting"
        lines.append(f"{marker} {stage} {label}")

    if lines:
        container.markdown("\n".join(lines))


def get_processed_video_keys():
    candidates = {}
    output_patterns = [
        ("analytics", "*_summary.json"),
        ("tracking", "*_tracks.json"),
        ("tracking", "*_tracked.mp4"),
        ("detection", "*_detected.mp4"),
        ("heatmaps", "*_heatmap.jpg"),
    ]

    for folder, pattern in output_patterns:
        for path in output_path(folder).glob(pattern):
            key = path.stem
            key = re.sub(r"_(summary|tracks|tracked|detected|heatmap)$", "", key)
            current_mtime = candidates.get(key, 0)
            candidates[key] = max(current_mtime, path.stat().st_mtime)

    return sorted(candidates, key=lambda item: candidates[item], reverse=True)


def get_latest_processed_key():
    processed = get_processed_video_keys()
    return processed[0] if processed else None


def count_unique_visitors_from_tracks(video_key):
    tracks = load_json(output_path("tracking", f"{video_key}_tracks.json"), [])
    if not isinstance(tracks, list):
        return 0
    return len(
        {
            record.get("track_id")
            for record in tracks
            if record.get("track_id") is not None
        }
    )


def load_events_for_camera(video_key):
    events = load_json(output_path("events", "events.json"), [])
    if not isinstance(events, list):
        return []

    camera_type = infer_camera_type(video_key)
    filtered = []
    has_camera_identity = False
    for event in events:
        camera_id = str(event.get("camera_id", "")).lower()
        event_video = str(event.get("video_name", "")).lower()
        has_camera_identity = has_camera_identity or bool(camera_id or event_video)
        if camera_type in camera_id or camera_type in event_video:
            filtered.append(event)

    if filtered or has_camera_identity:
        return filtered
    return events


def event_count(events, *event_types):
    wanted = set(event_types)
    return sum(
        1
        for event in events
        if (event.get("event_type") or event.get("event")) in wanted
    )


def metric_value(data, *keys, default=0):
    for key in keys:
        if isinstance(data, dict) and key in data:
            return data[key]
    return default


def render_metric_row(metrics):
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics):
        column.metric(label, value)


def render_heatmap(video_key):
    heatmap_path = output_path("heatmaps", f"{video_key}_heatmap.jpg")
    st.subheader("Customer Movement Heatmap")
    if heatmap_path.exists():
        st.image(str(heatmap_path), use_container_width=True)
    else:
        st.info("No heatmap has been generated for this camera yet.")


def render_billing_events(events):
    st.subheader("Billing Events")
    billing_events = [
        event
        for event in events
        if (event.get("event_type") or event.get("event")) in {
            "BILLING_QUEUE_JOIN",
            "BILLING_QUEUE_ABANDON",
            "BILLING_QUEUE_CONVERT",
            "PURCHASE",
        }
    ]
    if billing_events:
        st.dataframe(pd.DataFrame(billing_events), use_container_width=True)
    else:
        st.info("No billing events have been emitted for this selection yet.")


def render_floor_analytics(video_key):
    analytics_file = relative_output_path("analytics", f"{video_key}_summary.json")
    analytics = load_json(analytics_file, {})

    zone_metrics = [
        (zone, data)
        for zone, data in analytics.items()
        if (
            not zone.startswith("_")
            and isinstance(data, dict)
            and "visitors" in data
            and "total_dwell_time" in data
        )
    ]

    total_visitors = sum(data["visitors"] for _, data in zone_metrics)
    total_dwell = round(sum(data["total_dwell_time"] for _, data in zone_metrics), 2)
    top_zone = "N/A"
    if zone_metrics:
        top_zone = max(zone_metrics, key=lambda item: item[1]["total_dwell_time"])[0]
    score = min(100, int(total_visitors * 0.4 + total_dwell * 0.1))

    render_metric_row(
        [
            ("Visitors", total_visitors),
            ("Top Zone", top_zone),
            ("Store Score", score),
            ("Total Dwell (s)", total_dwell),
        ]
    )

    st.divider()
    st.subheader("Zone Engagement Distribution")
    chart_df = pd.DataFrame(
        [
            {"Zone": zone, "Dwell": data["total_dwell_time"]}
            for zone, data in zone_metrics
        ]
    )
    if not chart_df.empty:
        fig = px.pie(chart_df, names="Zone", values="Dwell", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No zone engagement rows found for this floor.")

    render_heatmap(video_key)

    st.subheader("Executive Summary")
    summary = f"""
- {total_visitors} shoppers were tracked.
- Highest engagement observed in {top_zone}.
- Total dwell time reached {total_dwell:.2f} seconds.
- This zone should be prioritized for promotions and upselling.
- Current store performance score: {score}/100.
"""
    st.info(summary)

    st.subheader("AI Recommendations")
    for zone, data in zone_metrics:
        if data["visitors"] < 10:
            st.error(
                f"""
{zone}

Low customer engagement detected.

Suggested actions:
- Add promotional displays
- Improve product visibility
- Introduce limited-time offers
"""
            )
        elif data["total_dwell_time"] > 200:
            st.success(
                f"""
{zone}

High engagement area.

Suggested actions:
- Upsell premium products
- Deploy brand ambassadors
- Launch bundle offers
"""
            )


def render_billing_analytics(video_key):
    analytics = load_json(output_path("analytics", f"{video_key}_summary.json"), {})
    queue_metrics = analytics.get("_queue_metrics", {}) if isinstance(analytics, dict) else {}
    conversion_metrics = (
        analytics.get("_conversion_metrics", {}) if isinstance(analytics, dict) else {}
    )
    funnel_metrics = analytics.get("_funnel_metrics", {}) if isinstance(analytics, dict) else {}
    events = load_events_for_camera(video_key)

    st.subheader("Queue Metrics")
    render_metric_row(
        [
            ("Queue Joins", metric_value(queue_metrics, "queue_joins")),
            ("Queue Abandons", metric_value(queue_metrics, "queue_abandons")),
            ("Queue Conversions", metric_value(queue_metrics, "queue_conversions")),
            ("Max Depth", metric_value(queue_metrics, "max_queue_depth")),
        ]
    )
    render_metric_row(
        [
            (
                "Avg Wait (s)",
                metric_value(
                    queue_metrics,
                    "average_queue_wait_time",
                    "average_wait_time_seconds",
                ),
            ),
            (
                "Max Wait (s)",
                metric_value(
                    queue_metrics,
                    "max_queue_wait_time",
                    "max_wait_time_seconds",
                ),
            ),
            (
                "Abandonment",
                metric_value(
                    queue_metrics,
                    "abandonment_rate_percent",
                    default=round(metric_value(queue_metrics, "abandonment_rate") * 100, 2),
                ),
            ),
        ]
    )

    st.subheader("Conversion Metrics")
    render_metric_row(
        [
            (
                "Visitors",
                metric_value(
                    conversion_metrics,
                    "total_visitors",
                    default=count_unique_visitors_from_tracks(video_key),
                ),
            ),
            (
                "Billing Visitors",
                metric_value(
                    conversion_metrics,
                    "billing_zone_visitors",
                    default=metric_value(funnel_metrics, "billing_queue"),
                ),
            ),
            (
                "Converted",
                metric_value(
                    conversion_metrics,
                    "converted_visitors",
                    default=metric_value(funnel_metrics, "purchase"),
                ),
            ),
            (
                "Conversion Rate",
                metric_value(conversion_metrics, "conversion_rate", default=0),
            ),
        ]
    )

    render_billing_events(events)
    render_heatmap(video_key)


def render_entrance_analytics(video_key):
    events = load_events_for_camera(video_key)
    entries = event_count(events, "ENTRY")
    exits = event_count(events, "EXIT")
    reentries = event_count(events, "REENTRY")
    footfall = max(entries + reentries - exits, 0)

    st.subheader("Entrance Flow")
    render_metric_row(
        [
            ("Entries", entries),
            ("Exits", exits),
            ("Reentries", reentries),
            ("Footfall", footfall),
        ]
    )

    if events:
        st.subheader("Entrance Events")
        st.dataframe(pd.DataFrame(events), use_container_width=True)
    render_heatmap(video_key)


def render_corner_analytics(video_key):
    events = load_events_for_camera(video_key)
    visitor_count = count_unique_visitors_from_tracks(video_key)
    total_events = len(events)

    st.subheader("Corner Activity")
    render_metric_row(
        [
            ("Visitor Count", visitor_count),
            ("Event Count", total_events),
        ]
    )

    if visitor_count == 0 and total_events == 0:
        st.info("No activity detected for this corner camera.")
    elif events:
        st.dataframe(pd.DataFrame(events), use_container_width=True)
    else:
        st.info("Visitors were tracked, but no events were emitted for this corner camera.")

    render_heatmap(video_key)


def render_processing_panel():
    processing = st.session_state.setdefault(
        "processing",
        {
            "stage": "Idle",
            "progress": 0,
            "status": "idle",
            "message": "No active processing run.",
            "summary": None,
            "stages": [],
            "completed_stages": [],
            "failed_stage": None,
        }
    )
    st.sidebar.subheader("Processing")
    st.sidebar.caption(f"Current stage: {processing['stage']}")
    progress_container = st.sidebar.empty()
    progress_container.progress(min(100, int(processing["progress"])))
    stage_container = st.sidebar.empty()
    render_stage_checklist(
        stage_container,
        processing.get("stages", []),
        current_stage=processing.get("stage"),
        completed=processing.get("completed_stages", []),
        failed=processing.get("failed_stage"),
    )

    status = processing["status"]
    message = processing["message"]
    if status == "success":
        st.sidebar.success(message)
    elif status == "failed":
        st.sidebar.error(message)
    elif status == "running":
        st.sidebar.info(message)
    else:
        st.sidebar.info(message)

    return st.sidebar.empty(), progress_container, stage_container


def render_processing_summary():
    summary = st.session_state.get("processing", {}).get("summary")
    if not summary:
        return

    st.success("Processing Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Video", summary["video_key"])
    c2.metric("Camera", summary["camera_type"])
    c3.metric("Stages", summary["stage_count"])
    c4.metric("Status", summary["status"].title())


def run_pipeline(
    video_path,
    video_name,
    progress_bar=None,
    status_placeholder=None,
    stage_placeholder=None,
):
    scripts = [
        (
            ROOT / "data/pipeline/detection/run_detection.py",
            [
                "--input-video", video_path,
                "--video-name", video_name,
            ]
        ),
        (
            ROOT / "data/pipeline/tracking/run_tracking.py",
            [
                "--input-video", video_path,
                "--video-name", video_name,
                "--output-dir", str(ROOT / "data/outputs/tracking")
            ]
        ),
        (
            ROOT / "data/pipeline/events/run_events.py",
            [
                "--video-name", video_name,
                "--track-file", str(ROOT / f"data/outputs/tracking/{video_name}_tracks.json")
            ]
        ),
        (
            ROOT / "data/pipeline/analytics/run_zone_analytics.py",
            [
                "--video-name", video_name,
                "--tracks-file", str(ROOT / f"data/outputs/tracking/{video_name}_tracks.json")
            ]
        ),
        (
            ROOT / "data/pipeline/heatmaps/run_heatmap.py",
            [
                "--input-video", video_path,
                "--video-name", video_name,
                "--output-file", str(ROOT / f"data/outputs/heatmaps/{video_name}_heatmap.jpg")
            ]
        )
    ]

    filtered_scripts = []
    for script_path, args in scripts:
        if "run_zone_analytics.py" in str(script_path) and video_name not in FLOOR_CAMERAS:
            continue
        filtered_scripts.append((script_path, args))

    logs = []
    stage_count = len(filtered_scripts)
    status_placeholder = status_placeholder or st.sidebar.empty()
    progress_bar = progress_bar or st.sidebar.progress(0)
    stage_placeholder = stage_placeholder or st.sidebar.empty()

    stage_names = []
    for script_path, _ in filtered_scripts:
        stage_name = "Detection"
        if "tracking" in str(script_path):
            stage_name = "Tracking"
        elif "events" in str(script_path):
            stage_name = "Events"
        elif "zone_analytics" in str(script_path) or "analytics" in str(script_path):
            stage_name = "Analytics"
        elif "heatmap" in str(script_path):
            stage_name = "Heatmap"
        stage_names.append(stage_name)

    completed_stages = []
    write_processing_state(
        stages=stage_names,
        completed_stages=completed_stages,
        failed_stage=None,
    )

    for index, (script_path, args) in enumerate(filtered_scripts):
        stage = stage_names[index]

        stage_start = int((index / stage_count) * 100)
        stage_end = int(((index + 1) / stage_count) * 100)
        write_processing_state(
            stage=stage,
            progress=stage_start,
            status="running",
            message=f"Running {stage.lower()}...",
        )
        render_stage_checklist(
            stage_placeholder,
            stage_names,
            current_stage=stage,
            completed=completed_stages,
        )
        status_placeholder.info(f"Stage: {stage}")
        progress_bar.progress(stage_start)

        command = [sys.executable, str(script_path)] + args
        proc = Popen(
            command,
            cwd=str(ROOT),
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            bufsize=1
        )

        script_stdout = []
        stage_percent = 0
        for raw_line in proc.stdout:
            line = raw_line.rstrip()
            script_stdout.append(line)
            status_placeholder.text(line)

            match = re.search(r"\[(\d+\.?\d*)%\]", line)
            if match:
                stage_percent = max(stage_percent, float(match.group(1)))
            else:
                ratio_match = re.search(r"(\d+)/(\d+)", line)
                if ratio_match:
                    current = int(ratio_match.group(1))
                    total = int(ratio_match.group(2))
                    stage_percent = max(
                        stage_percent,
                        (current / total) * 100 if total > 0 else 0
                    )

            overall = stage_start + int((stage_percent / 100) * (stage_end - stage_start))
            progress_bar.progress(min(100, overall))
            write_processing_state(progress=min(100, overall))

        return_code = proc.wait()
        logs.append(
            {
                "script": script_path.name,
                "command": " ".join(command),
                "returncode": return_code,
                "stdout": "\n".join(script_stdout),
                "stderr": "",
            }
        )

        if return_code != 0:
            message = f"{script_path.name} failed (code {return_code})"
            write_processing_state(status="failed", message=message, failed_stage=stage)
            render_stage_checklist(
                stage_placeholder,
                stage_names,
                current_stage=stage,
                completed=completed_stages,
                failed=stage,
            )
            status_placeholder.error(message)
            raise RuntimeError(message)

        progress_bar.progress(stage_end)
        completed_stages.append(stage)
        write_processing_state(
            progress=stage_end,
            message=f"Completed {stage.lower()}.",
            completed_stages=completed_stages,
        )
        render_stage_checklist(
            stage_placeholder,
            stage_names,
            completed=completed_stages,
        )
        status_placeholder.success(f"Completed: {script_path.name}")

    write_processing_state(
        stage="Complete",
        progress=100,
        status="success",
        message="Pipeline completed successfully.",
        completed_stages=stage_names,
        summary={
            "video_key": video_name,
            "camera_type": infer_camera_type(video_name),
            "stage_count": stage_count,
            "status": "success",
        },
    )
    return logs


st.sidebar.header("Video Upload")
Path("data/uploads").mkdir(parents=True, exist_ok=True)

status_placeholder, progress_bar, stage_placeholder = render_processing_panel()

with st.sidebar.form("video_form"):
    uploaded_file = st.file_uploader("Upload Store Video", type=["mp4"])
    process = st.form_submit_button("Process Video")

save_path = None
if uploaded_file is not None:
    save_path = str(Path("data/uploads") / uploaded_file.name)
    with open(save_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    st.sidebar.success(f"Uploaded: {uploaded_file.name}")

available_processed = get_processed_video_keys()
latest_processed = st.session_state.get("latest_processed") or get_latest_processed_key()
selected_index = 0
if latest_processed in available_processed:
    selected_index = available_processed.index(latest_processed)

selected_processed = None
if available_processed:
    selected_processed = st.sidebar.selectbox(
        "Select Processed Video",
        available_processed,
        index=selected_index,
        key="processed_select",
    )

raw_dir = Path("data/raw")
default_raw = None
if raw_dir.exists():
    mp4s = sorted(raw_dir.glob("*.mp4"))
    if mp4s:
        default_raw = str(mp4s[0])

input_video = save_path or default_raw or ""
video_key = normalize_video_key(save_path or selected_processed or input_video)

if process:
    if not input_video:
        st.sidebar.error("Upload a video before processing.")
    else:
        video_key = normalize_video_key(input_video)
        write_processing_state(
            stage="Queued",
            progress=0,
            status="running",
            message="Starting pipeline execution...",
            summary=None,
            stages=[],
            completed_stages=[],
            failed_stage=None,
        )
        with st.spinner("Running detection, tracking, events, analytics, and heatmap..."):
            try:
                logs = run_pipeline(
                    input_video,
                    video_key,
                    progress_bar=progress_bar,
                    status_placeholder=status_placeholder,
                    stage_placeholder=stage_placeholder,
                )
                st.session_state["latest_processed"] = video_key
                available_processed = get_processed_video_keys()
                for log in logs:
                    with st.sidebar.expander(log["script"]):
                        if log["stdout"]:
                            st.text(log["stdout"])
                        if log["stderr"]:
                            st.error(log["stderr"])
                st.rerun()
            except Exception as exc:
                write_processing_state(
                    stage="Failed",
                    status="failed",
                    message=str(exc),
                    failed_stage=st.session_state.get("processing", {}).get("stage"),
                    summary={
                        "video_key": video_key,
                        "camera_type": infer_camera_type(video_key),
                        "stage_count": 0,
                        "status": "failed",
                    },
                )
                st.sidebar.error(str(exc))

selected_processed = st.session_state.get("latest_processed") or selected_processed
video_key = normalize_video_key(selected_processed or save_path or input_video)
camera_type = infer_camera_type(video_key)

render_processing_summary()

if not video_key:
    st.info("Upload or select a processed video to view camera analytics.")
elif camera_type in FLOOR_CAMERAS:
    render_floor_analytics(camera_type)
elif camera_type == "billing":
    render_billing_analytics(camera_type)
elif camera_type == "entrance":
    render_entrance_analytics(camera_type)
elif camera_type == "corner":
    render_corner_analytics(camera_type)
else:
    st.subheader("Processed Outputs")
    render_metric_row(
        [
            ("Visitors", count_unique_visitors_from_tracks(video_key)),
            ("Events", len(load_events_for_camera(video_key))),
        ]
    )
    render_heatmap(video_key)
