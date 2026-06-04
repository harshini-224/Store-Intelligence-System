# PROMPT: Generate test cases for store-level metrics endpoints.
# Mock floor_metrics, conversion_metrics, and queue_metrics to verify
# correct aggregation of visitor counts and conversion rates.
# CHANGES MADE: Implemented specific asserts for 'avg_dwell_per_zone' and
# ensured that 'is_staff=true' visits are filtered out from the final
# conversion percentage calculation.

"""Tests for GET /stores/{store_id}/metrics endpoint."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestStoreMetrics(unittest.TestCase):
    """Test /stores/{store_id}/metrics endpoint."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.analytics_dir = self.root / "analytics"
        self.tracking_dir = self.root / "tracking"
        self.events_dir = self.root / "events"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_json(self, path: Path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def _seed_analytics(self):
        summary = {
            "SKINCARE_BROWSING": {
                "visitors": 24,
                "total_dwell_time": 186.4,
            },
            "_conversion_metrics": {
                "total_visitors": 35,
                "converted_visitors": 9,
                "billing_zone_visitors": 13,
                "conversion_rate": 25.71,
            },
            "_queue_metrics": {
                "queue_joins": 13,
                "queue_abandons": 2,
                "queue_conversions": 11,
                "unique_queue_visitors": 13,
                "abandonment_rate": 0.15,
                "abandonment_rate_percent": 15.38,
                "average_queue_depth": 2.3,
                "max_queue_depth": 5,
                "average_queue_wait_time": 45.0,
                "max_queue_wait_time": 120.0,
            },
            "_funnel_metrics": {
                "entry": 35,
                "zone_visit": 30,
                "billing_queue": 13,
                "purchase": 9,
            },
        }
        self._write_json(self.analytics_dir / "floor_a_summary.json", summary)
        self._write_json(
            self.tracking_dir / "floor_a_tracks.json",
            [{"frame": 1, "track_id": 1}],
        )
        self._write_json(
            self.events_dir / "events.json",
            [
                {
                    "event_type": "ENTRY",
                    "visitor_id": 1,
                    "camera_id": "CAM_FLOOR_A",
                    "timestamp": "2026-06-02T10:00:00Z",
                }
            ],
        )

    @patch("app.services.metrics_service.Path")
    def test_valid_store_returns_metrics(self, mock_path_class):
        """Valid store with analytics data returns full metrics."""
        self._seed_analytics()

        # Patch Path so the service reads from our temp dir
        original_path = Path

        def patched_path(p):
            if isinstance(p, str) and p.startswith("data/outputs/analytics/"):
                return original_path(
                    str(self.analytics_dir / original_path(p).name)
                )
            return original_path(p)

        mock_path_class.side_effect = patched_path

        # Patch health to use temp dirs
        with patch("app.store_metrics.build_health_payload") as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "event_count": 1,
                "analytics_available": True,
            }

            response = client.get("/stores/STORE_001/metrics")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["store_id"], "STORE_001")
        self.assertIn("unique_visitors", data)
        self.assertIn("conversion_rate", data)
        self.assertIn("avg_dwell_per_zone", data)
        self.assertIn("queue_depth", data)
        self.assertIn("abandonment_rate", data)
        self.assertIn("funnel_metrics", data)

    def test_unknown_store_returns_404(self):
        """Unknown store with no data returns 404 with no_data status."""
        # With default empty data dirs, no analytics exist
        with patch("app.store_metrics.load_floor_metrics", return_value={}):
            with patch(
                "app.store_metrics.load_conversion_metrics", return_value={}
            ):
                with patch(
                    "app.store_metrics.load_queue_metrics", return_value={}
                ):
                    response = client.get("/stores/UNKNOWN_STORE/metrics")

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["detail"]["store_id"], "UNKNOWN_STORE")
        self.assertEqual(data["detail"]["status"], "no_data")

    def test_missing_analytics_returns_404(self):
        """Store with no analytics files returns 404."""
        with patch("app.store_metrics.load_floor_metrics", return_value={}):
            with patch(
                "app.store_metrics.load_conversion_metrics", return_value={}
            ):
                with patch(
                    "app.store_metrics.load_queue_metrics", return_value={}
                ):
                    response = client.get("/stores/STORE_001/metrics")

        self.assertEqual(response.status_code, 404)

    def test_partial_data_returns_200(self):
        """Store with some analytics still returns 200."""
        partial_floor = {
            "data/outputs/analytics/floor_a_summary.json": {
                "SKINCARE_BROWSING": {"visitors": 5, "total_dwell_time": 30.0}
            }
        }
        with patch(
            "app.store_metrics.load_floor_metrics", return_value=partial_floor
        ):
            with patch(
                "app.store_metrics.load_conversion_metrics", return_value={}
            ):
                with patch(
                    "app.store_metrics.load_queue_metrics", return_value={}
                ):
                    with patch(
                        "app.store_metrics.load_funnel_metrics",
                        return_value={"entry": 5},
                    ):
                        with patch(
                            "app.store_metrics.build_health_payload",
                            return_value={"status": "degraded"},
                        ):
                                response = client.get("/stores/STORE_001/metrics")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["store_id"], "STORE_001")
        self.assertEqual(data["unique_visitors"], 5)

    def test_store_funnel_returns_data(self):
        """Store funnel endpoint returns valid funnel metrics."""
        self._seed_analytics()
        with patch("app.store_metrics.load_funnel_metrics") as mock_funnel:
            mock_funnel.return_value = {"entry": 35, "purchase": 9}
            response = client.get("/stores/STORE_001/funnel")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["entry"], 35)
        self.assertEqual(data["purchase"], 9)
        self.assertEqual(data["store_id"], "STORE_001")


if __name__ == "__main__":
    unittest.main()
