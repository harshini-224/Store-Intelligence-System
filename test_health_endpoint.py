import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.health import build_health_payload, health


class TestHealthEndpoint(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.analytics_dir = self.root / "analytics"
        self.tracking_dir = self.root / "tracking"
        self.events_dir = self.root / "events"
        self.now = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def seed_healthy_outputs(self, event_timestamp=None):
        event_timestamp = event_timestamp or (
            self.now - timedelta(minutes=5)
        ).isoformat().replace("+00:00", "Z")
        self.write_json(
            self.analytics_dir / "floor_a_summary.json",
            {"SKINCARE_BROWSING": {"visitors": 1, "total_dwell_time": 2.0}}
        )
        self.write_json(
            self.tracking_dir / "floor_a_tracks.json",
            [{"frame": 1, "track_id": 1}]
        )
        self.write_json(
            self.events_dir / "events.json",
            [
                {
                    "event_type": "ENTRY",
                    "visitor_id": 1,
                    "camera_id": "CAM_FLOOR_A",
                    "timestamp": event_timestamp
                }
            ]
        )

    def build_payload(self, threshold=15):
        return build_health_payload(
            analytics_dir=self.analytics_dir,
            tracking_dir=self.tracking_dir,
            events_dir=self.events_dir,
            current_time=self.now,
            stale_threshold_minutes=threshold
        )

    def test_healthy_state(self):
        self.seed_healthy_outputs()

        payload = self.build_payload()

        self.assertEqual(payload["status"], "healthy")
        self.assertEqual(payload["event_count"], 1)
        self.assertEqual(payload["last_event_timestamp"], "2026-06-02T11:55:00Z")
        self.assertFalse(payload["stale_feed"])
        self.assertEqual(payload["active_cameras"], 1)
        self.assertTrue(payload["analytics_available"])
        self.assertTrue(payload["tracking_available"])
        self.assertTrue(payload["events_available"])

    def test_stale_feed(self):
        stale_timestamp = (
            self.now - timedelta(minutes=16)
        ).isoformat().replace("+00:00", "Z")
        self.seed_healthy_outputs(stale_timestamp)

        payload = self.build_payload(threshold=15)

        self.assertEqual(payload["status"], "degraded")
        self.assertTrue(payload["stale_feed"])
        self.assertEqual(payload["last_event_timestamp"], "2026-06-02T11:44:00Z")

    def test_missing_analytics(self):
        self.seed_healthy_outputs()
        for path in self.analytics_dir.glob("*"):
            path.unlink()

        payload = self.build_payload()

        self.assertEqual(payload["status"], "degraded")
        self.assertFalse(payload["analytics_available"])
        self.assertTrue(payload["tracking_available"])
        self.assertTrue(payload["events_available"])

    def test_missing_tracking_output(self):
        self.seed_healthy_outputs()
        for path in self.tracking_dir.glob("*"):
            path.unlink()

        payload = self.build_payload()

        self.assertEqual(payload["status"], "degraded")
        self.assertTrue(payload["analytics_available"])
        self.assertFalse(payload["tracking_available"])
        self.assertTrue(payload["events_available"])

    def test_no_events(self):
        self.seed_healthy_outputs()
        self.write_json(self.events_dir / "events.json", [])

        payload = self.build_payload()

        self.assertEqual(payload["status"], "degraded")
        self.assertEqual(payload["event_count"], 0)
        self.assertIsNone(payload["last_event_timestamp"])
        self.assertTrue(payload["stale_feed"])
        self.assertFalse(payload["events_available"])

    def test_route_keeps_health_endpoint(self):
        payload = health()

        self.assertIn("status", payload)
        self.assertIn("event_count", payload)
        self.assertIn("analytics_available", payload)


if __name__ == "__main__":
    unittest.main()
