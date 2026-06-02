import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data/pipeline/analytics"))

from data.pipeline.analytics.funnel_tracker import compute_funnel_metrics
from data.pipeline.conversion.conversion_tracker import ConversionTracker
from data.pipeline.events.run_events import process_tracks
from data.pipeline.insights.recommendation_engine import RecommendationEngine
from data.pipeline.analytics.run_zone_analytics import main as run_zone_analytics


def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


class TestStaffExclusion(unittest.TestCase):

    def test_staff_visitor_not_counted(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        tmp_path = Path(temp_dir.name)
        tracks_file = tmp_path / "tracks.json"
        summary_file = tmp_path / "summary.json"
        dwell_file = tmp_path / "dwell.csv"
        tracks = [
            {
                "frame": 1,
                "track_id": 1,
                "center_x": 100,
                "center_y": 100,
                "is_staff": True
            },
            {
                "frame": 1,
                "track_id": 2,
                "center_x": 100,
                "center_y": 100,
                "is_staff": False
            }
        ]
        write_json(tracks_file, tracks)

        run_zone_analytics(
            video_name="floor_a",
            tracks_file=str(tracks_file),
            summary_file=str(summary_file),
            dwell_csv_file=str(dwell_file)
        )

        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        self.assertEqual(summary["SKINCARE_BROWSING"]["visitors"], 1)
        self.assertEqual(
            summary["SKINCARE_BROWSING"]["total_dwell_time"],
            0.03
        )

    def test_staff_visitor_not_converted(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        tmp_path = Path(temp_dir.name)
        tracks_file = tmp_path / "tracks.json"
        tracks = [
            {
                "frame": 1,
                "track_id": 1,
                "center_x": 960,
                "center_y": 150,
                "is_staff": True
            },
            {
                "frame": 2,
                "track_id": 2,
                "center_x": 960,
                "center_y": 150,
                "is_staff": False
            }
        ]
        write_json(tracks_file, tracks)

        tracker = ConversionTracker()
        tracker.load_tracks(str(tracks_file))
        tracker.add_pos_transaction("TXN_001", datetime(2026, 5, 30, 10, 0, 0))
        tracker.correlate_conversions()

        stats = tracker.get_conversion_stats()
        self.assertEqual(stats["total_visitors"], 1)
        self.assertEqual(stats["billing_zone_visitors"], 1)
        self.assertEqual(stats["converted_visitors"], 1)
        self.assertFalse(tracker.sessions[1].converted)
        self.assertTrue(tracker.sessions[2].converted)

    def test_staff_visitor_not_included_in_queue(self):
        tracks = [
            {
                "frame": 1,
                "track_id": 1,
                "center_x": 100,
                "center_y": 1040,
                "is_staff": True
            },
            {
                "frame": 1,
                "track_id": 2,
                "center_x": 200,
                "center_y": 1040,
                "is_staff": False
            }
        ]

        event_generator = process_tracks(tracks, video_name="floor_a")
        stats = event_generator.queue_tracker.get_queue_stats()
        queue_events = [
            event for event in event_generator.events
            if event.get("event_type") == "BILLING_QUEUE_JOIN"
        ]

        self.assertEqual(stats["queue_joins"], 1)
        self.assertEqual(len(queue_events), 1)
        self.assertEqual(queue_events[0]["visitor_id"], 2)

    def test_staff_visitor_not_included_in_funnel(self):
        events = [
            {
                "visitor_id": 1,
                "event_type": "ENTRY",
                "metadata": {"is_staff": True}
            },
            {
                "visitor_id": 1,
                "event_type": "ZONE_ENTER",
                "zone_id": "SKINCARE_BROWSING",
                "metadata": {"is_staff": True}
            },
            {
                "visitor_id": 1,
                "event_type": "BILLING_QUEUE_JOIN",
                "zone_id": "BILLING_QUEUE_A",
                "metadata": {"is_staff": True}
            },
            {
                "visitor_id": 2,
                "event_type": "ENTRY",
                "metadata": {"is_staff": False}
            }
        ]

        metrics = compute_funnel_metrics(events)
        self.assertEqual(metrics["entry"], 1)
        self.assertEqual(metrics["zone_visit"], 0)
        self.assertEqual(metrics["billing_queue"], 0)
        self.assertEqual(metrics["purchase"], 0)

    def test_staff_visitor_not_included_in_recommendations(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        tmp_path = Path(temp_dir.name)
        tracks_file = tmp_path / "tracks.json"
        summary_file = tmp_path / "summary.json"
        dwell_file = tmp_path / "dwell.csv"
        tracks = [
            {
                "frame": 1,
                "track_id": 1,
                "center_x": 100,
                "center_y": 100,
                "is_staff": True
            }
        ]
        write_json(tracks_file, tracks)

        run_zone_analytics(
            video_name="floor_a",
            tracks_file=str(tracks_file),
            summary_file=str(summary_file),
            dwell_csv_file=str(dwell_file)
        )

        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        recommendations = RecommendationEngine().generate(summary)
        self.assertEqual(recommendations, [])


if __name__ == "__main__":
    unittest.main()
