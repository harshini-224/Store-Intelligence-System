import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from data.pipeline.events.event_generator import EventGenerator
from data.pipeline.events.run_events import process_tracks


class TestEventGeneration(unittest.TestCase):

    def test_first_zone_entry_emits_zone_enter(self):
        tracks = [
            {"frame": 1, "track_id": 1, "center_x": 100, "center_y": 100}
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1
        )

        self.assertEqual(len(generator.events), 1)
        self.assertEqual(generator.events[0]["event_type"], "ZONE_ENTER")
        self.assertEqual(generator.events[0]["zone_id"], "SKINCARE_BROWSING")

    def test_zone_exit_emits_zone_exit(self):
        tracks = [
            {"frame": 1, "track_id": 1, "center_x": 100, "center_y": 100},
            {"frame": 2, "track_id": 1, "center_x": -100, "center_y": 100}
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1
        )

        event_types = [e["event_type"] for e in generator.events]
        self.assertEqual(event_types, ["ZONE_ENTER", "ZONE_EXIT"])
        self.assertEqual(generator.events[1]["zone_id"], "SKINCARE_BROWSING")

    def test_zone_transition_emits_exact_sequence(self):
        tracks = [
            {"frame": 1, "track_id": 1, "center_x": 100, "center_y": 100},
            {"frame": 2, "track_id": 1, "center_x": 1000, "center_y": 100}
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1
        )

        self.assertEqual(
            [e["event_type"] for e in generator.events],
            ["ZONE_ENTER", "ZONE_EXIT", "ZONE_ENTER"]
        )
        self.assertEqual(generator.events[0]["zone_id"], "SKINCARE_BROWSING")
        self.assertEqual(generator.events[1]["zone_id"], "SKINCARE_BROWSING")
        self.assertEqual(generator.events[2]["zone_id"], "PREMIUM_SKINCARE")

    def test_30_second_dwell_emits_dwell_event(self):
        tracks = [
            {"frame": i, "track_id": 1, "center_x": 100, "center_y": 100}
            for i in range(1, 31)
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1
        )

        event_types = [e["event_type"] for e in generator.events]
        self.assertEqual(event_types, ["ZONE_ENTER", "ZONE_DWELL"])
        self.assertEqual(generator.events[-1]["zone_id"], "SKINCARE_BROWSING")

    def test_60_second_dwell_emits_two_dwell_events(self):
        tracks = [
            {"frame": i, "track_id": 1, "center_x": 100, "center_y": 100}
            for i in range(1, 61)
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1
        )

        event_types = [e["event_type"] for e in generator.events]
        self.assertEqual(event_types, ["ZONE_ENTER", "ZONE_DWELL", "ZONE_DWELL"])

    def test_no_duplicate_dwell_events(self):
        tracks = [
            {"frame": i, "track_id": 1, "center_x": 100, "center_y": 100}
            for i in range(1, 62)
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1
        )

        self.assertEqual(
            [e["event_type"] for e in generator.events].count("ZONE_DWELL"),
            2
        )

    def test_no_duplicate_enter_exit_events_on_zone_change(self):
        tracks = [
            {"frame": 1, "track_id": 1, "center_x": 100, "center_y": 100},
            {"frame": 2, "track_id": 1, "center_x": 1000, "center_y": 100},
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1
        )

        event_types = [e["event_type"] for e in generator.events]
        self.assertEqual(event_types.count("ZONE_ENTER"), 2)
        self.assertEqual(event_types.count("ZONE_EXIT"), 1)
        self.assertEqual(generator.events[1]["event_type"], "ZONE_EXIT")
        self.assertEqual(generator.events[2]["event_type"], "ZONE_ENTER")

    def test_reentry_reuses_canonical_visitor_id(self):
        tracks = [
            {"frame": 1, "track_id": 1, "center_x": 1600, "center_y": 100},
            {"frame": 2, "track_id": 1, "center_x": 900, "center_y": 1000},
            {"frame": 5, "track_id": 2, "center_x": 1600, "center_y": 100},
        ]

        generator = process_tracks(
            tracks,
            video_name="entrance",
            fps=1,
            reentry_time_window_seconds=10,
            reentry_position_threshold_pixels=1500
        )

        event_types = [e["event_type"] for e in generator.events]
        self.assertEqual(event_types, ["EXIT", "REENTRY"])
        self.assertEqual(generator.events[1]["visitor_id"], 1)
        self.assertEqual(generator.events[1]["metadata"].get("raw_track_id"), 2)

    def test_reentry_does_not_inflate_funnel_counts(self):
        tracks = [
            {"frame": 1, "track_id": 1, "center_x": 1600, "center_y": 100},
            {"frame": 2, "track_id": 1, "center_x": 900, "center_y": 1000},
            {"frame": 5, "track_id": 2, "center_x": 1600, "center_y": 100},
        ]

        generator = process_tracks(
            tracks,
            video_name="entrance",
            fps=1,
            reentry_time_window_seconds=10,
            reentry_position_threshold_pixels=1500
        )

        unique_visitors = {e["visitor_id"] for e in generator.events}
        self.assertEqual(len(unique_visitors), 1)

        entry_stage_visitors = {
            e["visitor_id"]
            for e in generator.events
            if e["event_type"] in {"ENTRY", "REENTRY"}
        }
        self.assertEqual(len(entry_stage_visitors), 1)

    def test_events_have_full_schema(self):
        tracks = [
            {"frame": 1, "track_id": 1, "center_x": 100, "center_y": 100}
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1,
            store_id="STORE_123",
            camera_id="CAM_FLOOR_A"
        )

        event = generator.events[0]
        self.assertIn("event_id", event)
        self.assertEqual(event["store_id"], "STORE_123")
        self.assertEqual(event["camera_id"], "CAM_FLOOR_A")
        self.assertEqual(event["event_type"], "ZONE_ENTER")
        self.assertEqual(event["zone_id"], "SKINCARE_BROWSING")
        self.assertEqual(event["confidence"], 1.0)
        self.assertIsInstance(event["metadata"], dict)

    def test_timestamp_conversion_with_video_start_time(self):
        from datetime import datetime

        generator = EventGenerator(
            fps=15,
            video_start_time=datetime.fromisoformat("2026-03-03T14:00:00+00:00")
        )

        event = generator.create_event(
            visitor_id=1,
            event_type="ZONE_ENTER",
            frame_no=450,
            zone_id="SKINCARE_BROWSING"
        )

        self.assertEqual(
            event["timestamp"],
            "2026-03-03T14:00:30Z"
        )

    def test_queue_join_and_abandon_events_respect_conversions(self):
        tracks = [
            {"frame": 1, "track_id": 1, "center_x": 100, "center_y": 1020},
            {"frame": 1, "track_id": 2, "center_x": 200, "center_y": 1020},
            {"frame": 5, "track_id": 1, "center_x": 100, "center_y": 900},
            {"frame": 5, "track_id": 2, "center_x": 200, "center_y": 900},
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1,
            converted_visitor_ids={1}
        )

        queue_events = [
            e for e in generator.events
            if e["event_type"].startswith("BILLING_QUEUE_")
        ]

        self.assertEqual(
            [e["event_type"] for e in queue_events],
            [
                "BILLING_QUEUE_JOIN",
                "BILLING_QUEUE_JOIN",
                "BILLING_QUEUE_ABANDON"
            ]
        )
        self.assertEqual(queue_events[2]["visitor_id"], 2)

        stats = generator.queue_tracker.get_queue_stats()
        self.assertEqual(stats["queue_joins"], 2)
        self.assertEqual(stats["queue_abandons"], 1)
        self.assertEqual(stats["abandonment_rate"], 0.5)

    def test_staff_visitor_excluded_from_queue_events(self):
        tracks = [
            {
                "frame": 1,
                "track_id": 1,
                "center_x": 100,
                "center_y": 1020,
                "is_staff": True
            },
            {
                "frame": 5,
                "track_id": 1,
                "center_x": 100,
                "center_y": 900,
                "is_staff": True
            }
        ]

        generator = process_tracks(
            tracks,
            video_name="floor_a",
            fps=1
        )

        self.assertFalse(
            any(
                e["event_type"].startswith("BILLING_QUEUE_")
                for e in generator.events
            )
        )
        self.assertEqual(generator.queue_tracker.get_queue_stats()["queue_joins"], 0)


if __name__ == "__main__":
    unittest.main()
