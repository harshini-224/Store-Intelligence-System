from pathlib import Path
import cv2

from tracker import VisitorTracker


# =====================================================
# SELECT VIDEO HERE
# =====================================================

#INPUT_VIDEO = "data/raw/entrance.mp4"
INPUT_VIDEO = "data/raw/floor_a.mp4"
#INPUT_VIDEO = "data/raw/floor_b.mp4"
# INPUT_VIDEO = "data/raw/billing.mp4"

# =====================================================
# CAMERA CONFIGURATION
# =====================================================

CAMERA_CONFIG = {
    "entrance": {
        "draw_entry_line": True,
        "entry_line_start": (640, 1080),
        "entry_line_end": (1530, 0)
    },

    "floor_a": {
        "draw_entry_line": False
    },

    "floor_b": {
        "draw_entry_line": False
    },

    "billing": {
        "draw_entry_line": False
    },

    "corner": {
        "draw_entry_line": False
    }
}


def main():

    tracker = VisitorTracker()

    video_name = Path(INPUT_VIDEO).stem

    output_video = (
        f"data/outputs/tracking/{video_name}_tracked.mp4"
    )

    cap = cv2.VideoCapture(INPUT_VIDEO)

    if not cap.isOpened():
        print(f"Error opening video: {INPUT_VIDEO}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Width = {width}")
    print(f"Height = {height}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    Path("data/outputs/tracking").mkdir(
        parents=True,
        exist_ok=True
    )

    writer = cv2.VideoWriter(
        output_video,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    frame_number = 0

    camera_cfg = CAMERA_CONFIG.get(
        video_name,
        {"draw_entry_line": False}
    )

    print("\nStarting Tracking Pipeline...\n")
    print(f"Video : {video_name}")
    print(f"Frames: {total_frames}\n")

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_number += 1

        # =================================================
        # DRAW ENTRY LINE ONLY FOR ENTRANCE CAMERA
        # =================================================

        if camera_cfg.get("draw_entry_line", False):

            start_point = camera_cfg["entry_line_start"]
            end_point = camera_cfg["entry_line_end"]

            cv2.line(
                frame,
                start_point,
                end_point,
                (0, 0, 255),
                3
            )

            cv2.putText(
                frame,
                "ENTRY LINE",
                (
                    end_point[0] - 150,
                    max(40, end_point[1] + 40)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # =================================================
        # TRACK PEOPLE
        # =================================================

        tracks = tracker.track(frame)

        for track in tracks:

            x1, y1, x2, y2 = track["bbox"]
            track_id = track["track_id"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"VIS_{track_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        writer.write(frame)

        # =================================================
        # CLEAN PROGRESS LOG
        # =================================================

        if frame_number % 100 == 0:

            percent = (
                frame_number / total_frames
            ) * 100

            print(
                f"[{percent:.2f}%] "
                f"Frame {frame_number}/{total_frames}"
            )

    cap.release()
    writer.release()

    print("\nTracking Completed")
    print(f"Output: {output_video}")


if __name__ == "__main__":
    main()