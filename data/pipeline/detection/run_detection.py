from pathlib import Path
import argparse
import cv2

from detector import PersonDetector


def main(input_video, output_video=None, video_name=None, progress_interval=50):

    detector = PersonDetector()

    cap = cv2.VideoCapture(input_video)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {input_video}")

    fps = cap.get(cv2.CAP_PROP_FPS)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print("\n===== VIDEO INFO =====")
    print(f"Video       : {input_video}")
    print(f"Resolution  : {width}x{height}")
    print(f"FPS         : {fps}")
    print(f"Frames      : {total_frames}")
    print("======================\n")

    out_dir = Path("data/outputs/detection")
    out_dir.mkdir(parents=True, exist_ok=True)

    video_key = video_name or Path(input_video).stem
    if output_video is None:
        output_video = str(out_dir / f"{video_key}_detected.mp4")

    writer = cv2.VideoWriter(
        output_video,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    frame_number = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_number += 1

        detections = detector.detect(frame)

        for detection in detections:

            x1, y1, x2, y2 = detection["bbox"]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(
                frame,
                f"Person {detection['confidence']:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        writer.write(frame)

        # progress update at interval
        if total_frames > 0 and frame_number % progress_interval == 0:
            percent = (frame_number / total_frames) * 100
            print(f"[{percent:.2f}%] Frame {frame_number}/{total_frames} | Detections: {len(detections)}")

    cap.release()
    writer.release()

    print("\n===== COMPLETED =====")
    print(f"Output Video: {output_video}")
    print("=====================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run detection on a video and export detected video.")
    parser.add_argument("--input-video", required=False, default="data/raw/entrance.mp4")
    parser.add_argument("--output-video", required=False, default=None)
    parser.add_argument("--video-name", required=False, default=None)
    parser.add_argument("--progress-interval", type=int, default=50)
    args = parser.parse_args()
    main(args.input_video, args.output_video, args.video_name, args.progress_interval)