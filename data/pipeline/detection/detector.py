from ultralytics import YOLO


class PersonDetector:
    """
    Detects people using YOLO.
    """

    def __init__(self, model_name="yolo11n.pt"):
        self.model = YOLO(model_name)

    def detect(self, frame):
        results = self.model(frame)

        detections = []

        for result in results:
            for box in result.boxes:

                class_id = int(box.cls[0])

                # COCO class 0 = person
                if class_id != 0:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                confidence = float(box.conf[0])

                detections.append(
                    {
                        "bbox": [
                            int(x1),
                            int(y1),
                            int(x2),
                            int(y2)
                        ],
                        "confidence": confidence
                    }
                )

        return detections
