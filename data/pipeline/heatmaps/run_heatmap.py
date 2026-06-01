from pathlib import Path
import sys

import cv2

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))

from data.pipeline.tracking.tracker import VisitorTracker
from heatmap_generator import HeatmapGenerator
from zone_heatmap_overlay import (
    ZoneHeatmapOverlay
)

from data.pipeline.analytics.zone_config import (
    FLOOR_A_ZONES,
    FLOOR_B_ZONES
)


INPUT_VIDEO = "data/raw/floor_b.mp4"


def main():

    tracker = VisitorTracker()

    cap = cv2.VideoCapture(INPUT_VIDEO)

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    heatmap = HeatmapGenerator(
        width,
        height
    )

    last_frame = None
    frame_number = 0

    while True:

        success, frame = cap.read()

        if not success:
            break
        
        last_frame = frame.copy()

        frame_number += 1

        tracks = tracker.track(frame)

        for track in tracks:

            x1, y1, x2, y2 = track["bbox"]

            center_x = int(
                (x1 + x2) / 2
            )

            center_y = int(
                (y1 + y2) / 2
            )

            heatmap.update(
                center_x,
                center_y
            )

        if frame_number % 100 == 0:

            print(
                f"{frame_number}/{total_frames}"
            )

    cap.release()

    if last_frame is None:

        print("No frame available.")
        return

    # =====================================
    # CREATE HEATMAP IMAGE
    # =====================================

    result = heatmap.generate_overlay(
        last_frame
    )

    # =====================================
    # DRAW ZONES
    # =====================================

    overlay = ZoneHeatmapOverlay()

    video_name = Path(
        INPUT_VIDEO
    ).stem

    if video_name == "floor_a":

        result = overlay.draw_zones(
            result,
            FLOOR_A_ZONES
        )

    elif video_name == "floor_b":

        result = overlay.draw_zones(
            result,
            FLOOR_B_ZONES
        )

    Path(
        "data/outputs/heatmaps"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        "data/outputs/heatmaps/"
        "floor_b_heatmap.jpg"
    )

    cv2.imwrite(
        output_file,
        result
    )

    print(
        f"Saved: {output_file}"
    )


if __name__ == "__main__":
    main()