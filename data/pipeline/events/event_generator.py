# pipeline/events/event_generator.py

import json
import csv
from pathlib import Path


class EventGenerator:

    def __init__(self):

        self.events = []

        self.output_dir = Path("data/outputs/events")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def add_event(self, visitor_id, event_type, frame_no):

        event = {
            "visitor_id": visitor_id,
            "event": event_type,
            "frame": frame_no
        }

        self.events.append(event)

        print(
            f"[EVENT] {event_type} | "
            f"{visitor_id} | "
            f"Frame {frame_no}"
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
                    "visitor_id",
                    "event",
                    "frame"
                ]
            )

            writer.writeheader()

            for event in self.events:
                writer.writerow(event)

    def save_all(self):

        self.save_json()
        self.save_csv()

        print("\nEvents Saved Successfully")