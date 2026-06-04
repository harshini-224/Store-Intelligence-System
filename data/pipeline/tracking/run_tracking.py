from pathlib import Path
import argparse
import json

import cv2

from tracker import VisitorTracker


CAMERA_CONFIG = {
    "entrance": {
        "draw_entry_line": True,
        "entry_line_start": (640, 1080),
        "entry_line_end": (1530, 0),
    },
    "floor_a": {"draw_entry_line": False},
    "floor_b": {"draw_entry_line": False},
    "billing": {"draw_entry_line": False},
    "corner": {"draw_entry_line": False},
}


def main(input_video, output_dir="data/outputs/tracking", video_name=None, max_seconds=None):
    tracker = VisitorTracker()
    video_key = video_name or Path(input_video).stem
    output_video = Path(output_dir) / f"{video_key}_tracked.mp4"

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        print(f"Error opening video: {input_video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_to_process = total_frames
    if max_seconds is not None and fps > 0:
        frames_to_process = min(total_frames, max(1, int(float(max_seconds) * fps)))

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        str(output_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    camera_cfg = CAMERA_CONFIG.get(video_key, {"draw_entry_line": False})
    tracking_records = []
    frame_number = 0

    print("\nStarting Tracking Pipeline...\n")
    print(f"Video : {video_key}")
    print(f"Width : {width}")
    print(f"Height: {height}")
    print(f"Frames: {total_frames}")
    if frames_to_process < total_frames:
        print(f"Demo frames: {frames_to_process}")
    print()

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_number += 1
        if frame_number > frames_to_process:
            break

        if camera_cfg.get("draw_entry_line", False):
            start_point = camera_cfg["entry_line_start"]
            end_point = camera_cfg["entry_line_end"]
            cv2.line(frame, start_point, end_point, (0, 0, 255), 3)
            cv2.putText(
                frame,
                "ENTRY LINE",
                (end_point[0] - 150, max(40, end_point[1] + 40)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        tracks = tracker.track(frame)

        for track in tracks:
            x1, y1, x2, y2 = track["bbox"]
            track_id = track["track_id"]
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            tracking_records.append(
                {
                    "frame": frame_number,
                    "track_id": track_id,
                    "center_x": center_x,
                    "center_y": center_y,
                    "bbox": track["bbox"],
                    "confidence": track.get("confidence", 1.0),
                }
            )

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"VIS_{track_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        writer.write(frame)

        if frame_number % 50 == 0 or frame_number == frames_to_process:
            percent = (frame_number / frames_to_process) * 100
            print(f"[{percent:.2f}%] Frame {frame_number}/{frames_to_process}")

    cap.release()
    writer.release()

    tracks_file = Path(output_dir) / f"{video_key}_tracks.json"
    with open(tracks_file, "w") as file:
        json.dump(tracking_records, file, indent=4)

    print(f"Tracking data saved to {tracks_file}")
    print("\nTracking Completed")
    print(f"Output: {output_video}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run tracking on a video and export track data."
    )
    parser.add_argument("--input-video", default="data/raw/floor_a.mp4")
    parser.add_argument("--output-dir", default="data/outputs/tracking")
    parser.add_argument("--video-name", default=None)
    parser.add_argument("--max-seconds", type=float, default=None)
    args = parser.parse_args()
    main(args.input_video, args.output_dir, args.video_name, args.max_seconds)
