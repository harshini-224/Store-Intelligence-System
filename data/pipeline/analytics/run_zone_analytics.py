import json
from pathlib import Path

from dwell_time import DwellTimeTracker
from zone_manager import ZoneManager
from zone_config import FLOOR_B_ZONES

from analytics_report import AnalyticsReport
from export_csv import export_dwell_csv


VIDEO_NAME = "floor_b"

TRACKS_FILE = (
    f"data/outputs/tracking/{VIDEO_NAME}_tracks.json"
)

SUMMARY_FILE = (
    f"data/outputs/analytics/{VIDEO_NAME}_summary.json"
)

DWELL_CSV_FILE = (
    f"data/outputs/analytics/{VIDEO_NAME}_dwell.csv"
)

FPS = 30


def main():

    Path(
        "data/outputs/analytics"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    zone_manager = ZoneManager(
        FLOOR_B_ZONES
    )

    dwell_tracker = DwellTimeTracker(
        FPS
    )

    with open(
        TRACKS_FILE,
        "r"
    ) as file:

        tracks = json.load(file)

    for track in tracks:

        zone = zone_manager.get_zone(
            track["center_x"],
            track["center_y"]
        )

        dwell_tracker.update(
            track["track_id"],
            zone
        )

    dwell_results = (
        dwell_tracker.get_results()
    )

    export_dwell_csv(
        dwell_results,
        DWELL_CSV_FILE
    )

    report = AnalyticsReport()

    report.generate(
        dwell_results,
        SUMMARY_FILE
    )

    print(
        f"Summary saved to {SUMMARY_FILE}"
    )

    print(
        f"Dwell CSV saved to {DWELL_CSV_FILE}"
    )


if __name__ == "__main__":
    main()