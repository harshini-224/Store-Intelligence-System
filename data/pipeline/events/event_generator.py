# pipeline/events/event_generator.py

import csv
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


class EventGenerator:

    def __init__(
        self,
        store_id: str = "STORE_001",
        camera_id: str = "CAM_UNKNOWN",
        fps: int = 30,
        video_start_time: Optional[datetime] = None
    ):

        self.events = []
        self.store_id = store_id
        self.camera_id = camera_id
        self.fps = fps
        self.video_start_time = video_start_time

        self.output_dir = Path("data/outputs/events")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Optional group assignments: visitor_id -> group_id
        self.group_assignments = {}

    def frame_to_timestamp(self, frame_no: int) -> str:
        if self.video_start_time:
            timestamp = self.video_start_time + timedelta(
                seconds=frame_no / self.fps
            )
            iso = timestamp.isoformat()
            if iso.endswith("+00:00"):
                return iso[:-6] + "Z"
            return iso

        return f"frame:{frame_no}"

    def create_event(
        self,
        visitor_id: int,
        event_type: str,
        frame_no: int,
        zone_id: Optional[str] = None,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        camera_id: Optional[str] = None,
        store_id: Optional[str] = None
    ) -> Dict[str, Any]:

        metadata = metadata or {}
        metadata.setdefault("frame", frame_no)

        event = {
            "event_id": uuid.uuid4().hex,
            "visitor_id": visitor_id,
            "store_id": store_id or self.store_id,
            "camera_id": camera_id or self.camera_id,
            "timestamp": self.frame_to_timestamp(frame_no),
            "event_type": event_type,
            "zone_id": zone_id,
            "confidence": confidence,
            "metadata": metadata,
            "event": event_type
        }

        # Inject group_id if this visitor belongs to a group
        group_id = self.group_assignments.get(visitor_id)
        if group_id:
            event["metadata"]["group_id"] = group_id

        return event

    def add_event(
        self,
        visitor_id: int,
        event_type: str,
        frame_no: int,
        zone_id: Optional[str] = None,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        camera_id: Optional[str] = None,
        store_id: Optional[str] = None
    ):

        event = self.create_event(
            visitor_id=visitor_id,
            event_type=event_type,
            frame_no=frame_no,
            zone_id=zone_id,
            confidence=confidence,
            metadata=metadata,
            camera_id=camera_id,
            store_id=store_id
        )

        self.events.append(event)

        print(
            f"[EVENT] {event_type} | "
            f"{visitor_id} | "
            f"zone={zone_id} | "
            f"frame={frame_no}"
        )

    def save_json(self):

        output_file = self.output_dir / "events.json"

        with open(output_file, "w") as f:
            json.dump(self.events, f, indent=4)

    def save_csv(self):

        output_file = self.output_dir / "events.csv"

        with open(output_file, "w", newline="") as f:

            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "event_id",
                    "visitor_id",
                    "store_id",
                    "camera_id",
                    "timestamp",
                    "event_type",
                    "zone_id",
                    "confidence",
                    "metadata",
                    "event"
                ]
            )

            writer.writeheader()

            for event in self.events:
                row = event.copy()
                row["metadata"] = json.dumps(row["metadata"])
                writer.writerow(row)

    def save_all(self):

        self.save_json()
        self.save_csv()

        print("\nEvents Saved Successfully")