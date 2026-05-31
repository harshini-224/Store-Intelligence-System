from ultralytics import YOLO


class VisitorTracker:

    def __init__(self):
        self.model = YOLO("yolo11n.pt")

    def track(self, frame):

        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        tracks = []

        result = results[0]

        if result.boxes.id is None:
            return tracks

        for box, track_id in zip(
            result.boxes,
            result.boxes.id
        ):

            class_id = int(box.cls[0])

            # Person only
            if class_id != 0:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            tracks.append(
                {
                    "track_id": int(track_id),

                    "bbox": [
                        int(x1),
                        int(y1),
                        int(x2),
                        int(y2)
                    ],

                    "center_x": center_x,
                    "center_y": center_y,

                    "confidence": float(box.conf[0])
                }
            )           

        return tracks