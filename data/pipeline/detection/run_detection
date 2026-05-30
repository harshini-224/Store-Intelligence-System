from pathlib import Path

import cv2

from detector import PersonDetector


INPUT_VIDEO = "data/raw/entrance.mp4"
OUTPUT_VIDEO = "outputs/detection/entrance_detected.mp4"


def main():

    detector = PersonDetector()

    cap = cv2.VideoCapture(INPUT_VIDEO)

    fps = cap.get(cv2.CAP_PROP_FPS)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    Path("outputs/detection").mkdir(
        parents=True,
        exist_ok=True
    )

    writer = cv2.VideoWriter(
        OUTPUT_VIDEO,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    while True:

        success, frame = cap.read()

        if not success:
            break

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
                "Person",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        writer.write(frame)

    cap.release()
    writer.release()

    print("Detection completed.")


if __name__ == "__main__":
    main()
