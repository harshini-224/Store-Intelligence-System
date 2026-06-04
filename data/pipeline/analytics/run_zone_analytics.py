import argparse
import json
from pathlib import Path

from dwell_time import DwellTimeTracker
from zone_manager import ZoneManager
from zone_config import FLOOR_A_ZONES, FLOOR_B_ZONES

from analytics_report import AnalyticsReport
from export_csv import export_dwell_csv

ZONE_DEFINITIONS = {
    "floor_a": FLOOR_A_ZONES,
    "floor_b": FLOOR_B_ZONES
}

FPS = 30


def main(
    video_name="floor_b",
    tracks_file=None,
    summary_file=None,
    dwell_csv_file=None
):

    if video_name not in ZONE_DEFINITIONS:
        raise ValueError(
            f"Unsupported video name: {video_name}"
        )

    tracks_file = tracks_file or (
        f"data/outputs/tracking/{video_name}_tracks.json"
    )
    summary_file = summary_file or (
        f"data/outputs/analytics/{video_name}_summary.json"
    )
    dwell_csv_file = dwell_csv_file or (
        f"data/outputs/analytics/{video_name}_dwell.csv"
    )

    Path("data/outputs/analytics").mkdir(
        parents=True,
        exist_ok=True
    )

    zone_manager = ZoneManager(
        ZONE_DEFINITIONS[video_name]
    )

    dwell_tracker = DwellTimeTracker(
        FPS
    )

    with open(tracks_file, "r") as file:
        tracks = json.load(file)

    for track in tracks:
        if track.get("is_staff", False):
            continue

        zone = zone_manager.get_zone(
            track["center_x"],
            track["center_y"]
        )

        dwell_tracker.update(
            track["track_id"],
            zone
        )

    dwell_results = dwell_tracker.get_results()

    export_dwell_csv(
        dwell_results,
        dwell_csv_file
    )

    report = AnalyticsReport()
    report.generate(
        dwell_results,
        summary_file
    )

    print(f"Summary saved to {summary_file}")
    print(f"Dwell CSV saved to {dwell_csv_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run zone analytics on tracked data."
    )
    parser.add_argument(
        "--video-name",
        default="floor_b"
    )
    parser.add_argument(
        "--tracks-file",
        default=None
    )
    parser.add_argument(
        "--summary-file",
        default=None
    )
    parser.add_argument(
        "--dwell-csv-file",
        default=None
    )
    args = parser.parse_args()

    main(
        args.video_name,
        args.tracks_file,
        args.summary_file,
        args.dwell_csv_file
    )
