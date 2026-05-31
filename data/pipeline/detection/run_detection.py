from pathlib import Path
import cv2

from detector import PersonDetector


INPUT_VIDEO = "data/raw/entrance.mp4"
OUTPUT_VIDEO = "data/outputs/detection/entrance_detected.mp4"


def main():

    detector = PersonDetector()

    cap = cv2.VideoCapture(INPUT_VIDEO)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {INPUT_VIDEO}")

    fps = cap.get(cv2.CAP_PROP_FPS)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print("\n===== VIDEO INFO =====")
    print(f"Video       : {INPUT_VIDEO}")
    print(f"Resolution  : {width}x{height}")
    print(f"FPS         : {fps}")
    print(f"Frames      : {total_frames}")
    print("======================\n")

    Path("data/outputs/detection").mkdir(
        parents=True,
        exist_ok=True
    )

    writer = cv2.VideoWriter(
        OUTPUT_VIDEO,
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

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Person {detection['confidence']:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        writer.write(frame)

        # progress update every 100 frames
        if frame_number % 100 == 0:

            percent = (frame_number / total_frames) * 100

            print(
                f"[{percent:6.2f}%] "
                f"Frame {frame_number}/{total_frames} "
                f"| Detections: {len(detections)}"
            )

    cap.release()
    writer.release()

    print("\n===== COMPLETED =====")
    print(f"Output Video: {OUTPUT_VIDEO}")
    print("=====================\n")


if __name__ == "__main__":
    main()