import json
from pathlib import Path

from dwell_time import DwellTimeTracker
from zone_manager import ZoneManager
from zone_config import FLOOR_A_ZONES


OUTPUT_FILE = (
    "data/outputs/analytics/analytics_summary.json"
)


def main():

    Path(
        "data/outputs/analytics"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    zone_manager = ZoneManager(
        FLOOR_A_ZONES
    )

    dwell_tracker = DwellTimeTracker()

    #
    # DEMO DATA
    #

    sample_tracks = [
        {
            "track_id": 1,
            "center_x": 100,
            "center_y": 200
        },
        {
            "track_id": 2,
            "center_x": 300,
            "center_y": 400
        }
    ]

    for track in sample_tracks:

        zone = zone_manager.get_zone(
            track["center_x"],
            track["center_y"]
        )

        dwell_tracker.update(
            track["track_id"],
            zone
        )

    results = dwell_tracker.get_results()

    with open(
        OUTPUT_FILE,
        "w"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print(
        f"Analytics saved to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()