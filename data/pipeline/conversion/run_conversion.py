"""
Run Conversion Analytics

Orchestrates the full conversion rate analysis pipeline:
1. Load visitor tracking data
2. Load POS transaction data
3. Correlate billing zone visits with transactions
4. Generate conversion metrics
5. Update analytics summary with conversion data
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

from data.pipeline.conversion.conversion_tracker import ConversionTracker
from data.pipeline.analytics.analytics_report import AnalyticsReport
from data.pipeline.analytics.dwell_time import DwellTimeTracker
from data.pipeline.analytics.zone_config import FLOOR_A_ZONES, FLOOR_B_ZONES


ZONE_DEFINITIONS = {
    "floor_a": FLOOR_A_ZONES,
    "floor_b": FLOOR_B_ZONES
}

FPS = 30


def main(
    video_name: str = "floor_a",
    tracks_file: str = None,
    pos_file: str = None,
    dwell_file: str = None,
    summary_file: str = None,
    sessions_output: str = None,
    video_start_time: str = None
):
    """
    Run conversion analytics.
    
    Args:
        video_name: Video identifier (floor_a, floor_b, etc.)
        tracks_file: Path to tracking JSON
        pos_file: Path to POS transaction file (JSON or CSV)
        dwell_file: Path to dwell time CSV
        summary_file: Path to save updated analytics summary
        sessions_output: Path to save visitor sessions with conversion data
        video_start_time: Video start timestamp for time-based correlation
                         Format: ISO 8601 (e.g., "2026-05-30T10:00:00Z")
    """

    # Set defaults
    tracks_file = tracks_file or (
        f"data/outputs/tracking/{video_name}_tracks.json"
    )
    pos_file = pos_file or f"data/raw/sample_transactions.json"
    dwell_file = dwell_file or f"data/outputs/analytics/{video_name}_dwell.csv"
    summary_file = summary_file or (
        f"data/outputs/analytics/{video_name}_summary.json"
    )
    sessions_output = sessions_output or (
        f"data/outputs/conversion/{video_name}_sessions.json"
    )

    print("\n===== CONVERSION ANALYTICS =====")
    print(f"Video       : {video_name}")
    print(f"Tracks      : {tracks_file}")
    print(f"POS Data    : {pos_file}")
    print(f"Dwell Data  : {dwell_file}")
    print("================================\n")

    # Create conversion tracker
    tracker = ConversionTracker(fps=FPS)

    # Load tracking data
    try:
        tracker.load_tracks(tracks_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Load dwell data (optional)
    tracker.load_dwell_data(dwell_file)

    # Load POS data
    try:
        tracker.load_pos_data(pos_file)
    except Exception as e:
        print(f"Warning: Could not load POS data: {e}")

    # Parse video start time if provided
    start_time = None
    if video_start_time:
        try:
            start_time = datetime.fromisoformat(
                video_start_time.replace("Z", "+00:00")
            )
        except Exception as e:
            print(f"Warning: Could not parse video start time: {e}")

    # Correlate conversions
    tracker.correlate_conversions(start_time)

    # Get conversion statistics
    conversion_stats = tracker.get_conversion_stats()

    print("\n===== CONVERSION STATS =====")
    print(f"Total Visitors      : {conversion_stats['total_visitors']}")
    print(f"Billing Zone Visits : {conversion_stats['billing_zone_visitors']}")
    print(f"Converted Visitors  : {conversion_stats['converted_visitors']}")
    print(f"Conversion Rate     : {conversion_stats['conversion_rate']}%")
    print(f"Billing Zone Rate   : {conversion_stats['billing_zone_rate']}%")
    print("============================\n")

    # Load existing analytics
    summary_path = Path(summary_file)
    if summary_path.exists():
        with open(summary_path, "r") as f:
            existing_summary = json.load(f)
    else:
        existing_summary = {}

    # Update summary with conversion metrics
    existing_summary["_conversion_metrics"] = conversion_stats

    # Save updated analytics
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_file, "w") as f:
        json.dump(existing_summary, f, indent=4)

    print(f"Analytics updated: {summary_file}")

    # Export sessions
    sessions_path = Path(sessions_output)
    sessions_path.parent.mkdir(parents=True, exist_ok=True)
    tracker.export_sessions(sessions_output)

    print(f"Sessions exported: {sessions_output}")
    print("\n===== COMPLETED =====\n")

    return conversion_stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run conversion analytics on tracked visitor data."
    )
    parser.add_argument(
        "--video-name",
        default="floor_a"
    )
    parser.add_argument(
        "--tracks-file",
        default=None
    )
    parser.add_argument(
        "--pos-file",
        default=None
    )
    parser.add_argument(
        "--dwell-file",
        default=None
    )
    parser.add_argument(
        "--summary-file",
        default=None
    )
    parser.add_argument(
        "--sessions-output",
        default=None
    )
    parser.add_argument(
        "--video-start-time",
        default=None,
        help="ISO 8601 format: 2026-05-30T10:00:00Z"
    )

    args = parser.parse_args()

    main(
        args.video_name,
        args.tracks_file,
        args.pos_file,
        args.dwell_file,
        args.summary_file,
        args.sessions_output,
        args.video_start_time
    )
