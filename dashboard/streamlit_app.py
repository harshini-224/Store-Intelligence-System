import subprocess
from subprocess import Popen, PIPE, STDOUT
import sys
import re
import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import json
from pathlib import Path

API = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(
    page_title="Store Intelligence Dashboard",
    layout="wide"
)

st.title("🛍 Store Intelligence Dashboard")
st.caption("AI Powered Retail Analytics")

# ==========================
# FLOOR SELECTOR
# ==========================

st.sidebar.header("Video Upload")

Path("data/uploads").mkdir(parents=True, exist_ok=True)

with st.sidebar.form("video_form"):
    uploaded_file = st.file_uploader("Upload Store Video", type=["mp4"]) 

    process = st.form_submit_button("Process Video")

    # when form is submitted we'll handle saving and running

save_path = None
if uploaded_file is not None:
    save_path = f"data/uploads/{uploaded_file.name}"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"Uploaded: {uploaded_file.name}")

# Build a selector for processed analytics (available summaries)
analytics_dir = Path("data/outputs/analytics")
available_analytics = []
if analytics_dir.exists():
    for p in analytics_dir.glob("*_summary.json"):
        available_analytics.append(p.stem.replace("_summary", ""))

selected_processed = None
if available_analytics:
    selected_processed = st.sidebar.selectbox("Select Processed Video", available_analytics)

if save_path:
    input_video = save_path
else:
    # default to first available processed video raw file if present
    raw_dir = Path("data/raw")
    default_raw = None
    if raw_dir.exists():
        mp4s = list(raw_dir.glob("*.mp4"))
        if mp4s:
            default_raw = str(mp4s[0])
    input_video = save_path or default_raw or ""

# infer a default video_key (used for determining whether analytics apply)
if save_path:
    name = Path(save_path).stem.lower()
    if "entrance" in name:
        video_key = "entrance"
    elif "billing" in name:
        video_key = "billing"
    elif "corner" in name:
        video_key = "corner"
    elif "floor_a" in name:
        video_key = "floor_a"
    elif "floor_b" in name:
        video_key = "floor_b"
    else:
        video_key = Path(save_path).stem
elif selected_processed:
    video_key = selected_processed
elif input_video:
    video_key = Path(input_video).stem
else:
    video_key = ""


def run_pipeline(video_path, video_name, progress_bar=None, status_placeholder=None):
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
    # For analytics, only run for floor videos
    allowed_analytics = ["floor_a", "floor_b"]
    filtered_scripts = []
    for script_path, args in scripts:
        if "run_zone_analytics.py" in str(script_path) and video_name not in allowed_analytics:
            continue
        filtered_scripts.append((script_path, args))

    logs = []

    # allow caller-provided placeholders so they survive reruns
    sidebar_status = status_placeholder or st.sidebar.empty()
    progress_bar = progress_bar or st.sidebar.progress(0)

    for script_path, args in filtered_scripts:
        command = [sys.executable, str(script_path)] + args

        # show clean stage names
        stage = "Detection"
        if "tracking" in str(script_path):
            stage = "Tracking"
        elif "events" in str(script_path):
            stage = "Events"
        elif "zone_analytics" in str(script_path) or "analytics" in str(script_path):
            stage = "Analytics"
        elif "heatmap" in str(script_path):
            stage = "Heatmap"

        sidebar_status.info(f"Stage: {stage}")

        proc = Popen(
            command,
            cwd=str(ROOT),
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            bufsize=1
        )

        script_stdout = []

        total_percent = 0

        for raw_line in proc.stdout:
            line = raw_line.rstrip()
            script_stdout.append(line)
            # show only the line as context, without file names
            sidebar_status.text(f"{line}")

            # parse percent patterns like [12.34%] or 123/456
            m = re.search(r"\[(\d+\.?\d*)%\]", line)
            if m:
                try:
                    pct = float(m.group(1))
                    total_percent = max(total_percent, pct)
                    progress_bar.progress(min(100, int(total_percent)))
                except Exception:
                    pass
            else:
                m2 = re.search(r"(\d+)/(\d+)", line)
                if m2:
                    try:
                        a = int(m2.group(1))
                        b = int(m2.group(2))
                        pct = (a / b) * 100 if b > 0 else 0
                        total_percent = max(total_percent, pct)
                        progress_bar.progress(min(100, int(total_percent)))
                    except Exception:
                        pass

        ret = proc.wait()

        logs.append(
            {
                "script": script_path.name,
                "command": " ".join(command),
                "returncode": ret,
                "stdout": "\n".join(script_stdout),
                "stderr": "",
            }
        )

        if ret != 0:
            sidebar_status.error(f"{script_path.name} failed (code {ret})")
            raise RuntimeError(f"{script_path.name} failed (code {ret})")

        progress_bar.progress(100)
        sidebar_status.success(f"Completed: {script_path.name}")

    return logs

if process:
    # infer video type from uploaded filename when available
    if save_path:
        name = Path(save_path).stem.lower()
        if "entrance" in name:
            video_key = "entrance"
        elif "billing" in name:
            video_key = "billing"
        elif "corner" in name:
            video_key = "corner"
        elif "floor_a" in name:
            video_key = "floor_a"
        elif "floor_b" in name:
            video_key = "floor_b"
        else:
            video_key = Path(save_path).stem
    elif selected_processed:
        video_key = selected_processed
    elif input_video:
        video_key = Path(input_video).stem
    else:
        video_key = ""

    st.sidebar.info("Starting pipeline execution...")
    with st.spinner("Running detection, tracking, events, analytics, and heatmap..."):
        try:
            logs = run_pipeline(input_video, video_key)
            st.sidebar.success("Pipeline completed successfully.")
            for log in logs:
                st.sidebar.subheader(log["script"])
                if log["stdout"]:
                    st.sidebar.text(log["stdout"])
                if log["stderr"]:
                    st.sidebar.error(log["stderr"])
        except Exception as exc:
            st.sidebar.error(str(exc))

allowed_analytics = ["floor_a", "floor_b"]

if video_key in allowed_analytics:
    analytics_file = f"data/outputs/analytics/{video_key}_summary.json"

    if not Path(analytics_file).exists():
        st.warning(
            "Analytics results are not available. Upload a video and click Process Video, or verify that the pipeline completed successfully."
        )
        st.stop()

    with open(analytics_file) as f:
        analytics = json.load(f)
else:
    st.info("Analytics are not available for this video type (no zone analytics). Showing available outputs.")
    st.stop()

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

# ==========================

# KPI CALCULATIONS

# ==========================

total_visitors = sum(
data["visitors"]
for _, data in zone_metrics
)

total_dwell = round(
sum(
data["total_dwell_time"]
for _, data in zone_metrics
),
2
)

top_zone = "N/A"
if zone_metrics:
    top_zone = max(
        zone_metrics,
        key=lambda x: x[1]["total_dwell_time"]
    )[0]

score = min(
100,
int(
total_visitors * 0.4 +
total_dwell * 0.1
)
)

# ==========================

# KPI ROW

# ==========================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
"Visitors",
total_visitors
)

c2.metric(
"Top Zone",
top_zone
)

c3.metric(
"Store Score",
score
)

c4.metric(
"Total Dwell (s)",
total_dwell
)

st.divider()

# ==========================

# PIE CHART

# ==========================

st.subheader("Zone Engagement Distribution")

chart_df = pd.DataFrame(
[
{
"Zone": zone,
"Dwell": data["total_dwell_time"]
}
for zone, data in analytics.items()
if (
    not zone.startswith("_")
    and isinstance(data, dict)
    and "visitors" in data
    and "total_dwell_time" in data
)
]
)

fig = px.pie(
chart_df,
names="Zone",
values="Dwell",
hole=0.4
)

st.plotly_chart(
fig,
use_container_width=True
)

# ==========================

# HEATMAPS

# ==========================
st.subheader("Customer Movement Heatmap")

heatmap_path = None
if video_key in ["floor_a", "floor_b"]:
    heatmap_path = f"data/outputs/heatmaps/{video_key}_heatmap.jpg"
else:
    # try to find a heatmap for the selected processed video
    candidate = Path(f"data/outputs/heatmaps/{video_key}_heatmap.jpg")
    if candidate.exists():
        heatmap_path = str(candidate)

if heatmap_path and Path(heatmap_path).exists():
    st.image(heatmap_path, use_container_width=True)
else:
    st.info("No heatmap available for this video type.")

# ==========================

# EXECUTIVE SUMMARY

# ==========================

st.subheader(
    "Executive Summary"
)

summary = f"""
• {total_visitors} shoppers were tracked.

• Highest engagement observed in {top_zone}.

• Total dwell time reached {total_dwell:.2f} seconds.

• This zone should be prioritized for promotions and upselling.

• Current store performance score: {score}/100.
"""

st.info(summary)


# ==========================

# RECOMMENDATIONS

# ==========================

st.subheader(
    "AI Recommendations"
)

for zone, data in zone_metrics:

    if data["visitors"] < 10:

        st.error(
            f"""
            {zone}

            Low customer engagement detected.

            Suggested actions:
            • Add promotional displays
            • Improve product visibility
            • Introduce limited-time offers
            """
        )

    elif data["total_dwell_time"] > 200:

        st.success(
            f"""
            {zone}

            High engagement area.

            Suggested actions:
            • Upsell premium products
            • Deploy brand ambassadors
            • Launch bundle offers
            """
        )
