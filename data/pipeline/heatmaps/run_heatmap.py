from pathlib import Path
import argparse
import json
import sys

import cv2

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from data.pipeline.tracking.tracker import VisitorTracker
from heatmap_generator import HeatmapGenerator
from zone_heatmap_overlay import ZoneHeatmapOverlay

from data.pipeline.analytics.zone_config import (
    FLOOR_A_ZONES,
    FLOOR_B_ZONES
)

ZONE_DEFINITIONS = {
    "floor_a": FLOOR_A_ZONES,
    "floor_b": FLOOR_B_ZONES
}


def main(input_video, video_name=None, output_file=None, tracks_file=None):

    tracker = VisitorTracker()

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {input_video}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    heatmap = HeatmapGenerator(width, height)
    video_key = video_name or Path(input_video).stem
    tracks_path = Path(
        tracks_file or f"data/outputs/tracking/{video_key}_tracks.json"
    )
    use_tracks_file = tracks_path.exists()

    last_frame = None
    frame_number = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        last_frame = frame.copy()
        frame_number += 1

        if use_tracks_file:
            if frame_number % 100 == 0:
                print(f"{frame_number}/{total_frames}")
            continue

        tracks = tracker.track(frame)

        for track in tracks:
            x1, y1, x2, y2 = track["bbox"]
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            heatmap.update(center_x, center_y)

        if frame_number % 100 == 0:
            print(f"{frame_number}/{total_frames}")

    cap.release()

    if last_frame is None:
        print("No frame available.")
        return

    if use_tracks_file:
        with open(tracks_path, "r") as file:
            tracks = json.load(file)

        for track in tracks:
            if track.get("is_staff", False):
                continue
            heatmap.update(
                int(track["center_x"]),
                int(track["center_y"])
            )

    result = heatmap.generate_overlay(last_frame)

    overlay = ZoneHeatmapOverlay()

    if video_key in ZONE_DEFINITIONS:
        result = overlay.draw_zones(
            result,
            ZONE_DEFINITIONS[video_key]
        )

    output_file = output_file or (
        f"data/outputs/heatmaps/{video_key}_heatmap.jpg"
    )

    Path(Path(output_file).parent).mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(output_file, result)

    print(f"Saved: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a heatmap image for a video."
    )
    parser.add_argument(
        "--input-video",
        default="data/raw/floor_b.mp4"
    )
    parser.add_argument(
        "--video-name",
        default=None,
        choices=["floor_a", "floor_b", "entrance", "billing", "corner"]
    )
    parser.add_argument(
        "--output-file",
        default=None
    )
    parser.add_argument(
        "--tracks-file",
        default=None
    )
    args = parser.parse_args()

    main(
        args.input_video,
        args.video_name,
        args.output_file,
        args.tracks_file
    )
