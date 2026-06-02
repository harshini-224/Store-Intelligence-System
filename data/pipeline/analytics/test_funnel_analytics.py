import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from data.pipeline.analytics.funnel_tracker import compute_funnel_metrics


def event(visitor_id, event_type, zone_id=None, is_staff=False):
    return {
        "visitor_id": visitor_id,
        "event_type": event_type,
        "zone_id": zone_id,
        "metadata": {
            "is_staff": is_staff
        }
    }


class TestFunnelAnalytics(unittest.TestCase):

    def test_full_funnel_visitor(self):
        metrics = compute_funnel_metrics([
            event(1, "ENTRY"),
            event(1, "ZONE_ENTER", "SKINCARE_BROWSING"),
            event(1, "BILLING_QUEUE_JOIN", "BILLING_QUEUE_A"),
            event(1, "PURCHASE")
        ])

        self.assertEqual(metrics["entry"], 1)
        self.assertEqual(metrics["zone_visit"], 1)
        self.assertEqual(metrics["billing_queue"], 1)
        self.assertEqual(metrics["purchase"], 1)

    def test_entry_only(self):
        metrics = compute_funnel_metrics([event(1, "ENTRY")])

        self.assertEqual(metrics["entry"], 1)
        self.assertEqual(metrics["zone_visit"], 0)
        self.assertEqual(metrics["dropoffs"]["entry_to_zone"], 1)

    def test_zone_only(self):
        metrics = compute_funnel_metrics([
            event(1, "ZONE_ENTER", "SKINCARE_BROWSING")
        ])

        self.assertEqual(metrics["entry"], 0)
        self.assertEqual(metrics["zone_visit"], 1)
        self.assertEqual(metrics["rates"]["zone_visit_rate"], 0.0)

    def test_queue_without_purchase(self):
        metrics = compute_funnel_metrics([
            event(1, "ENTRY"),
            event(1, "ZONE_ENTER", "SKINCARE_BROWSING"),
            event(1, "BILLING_QUEUE_JOIN", "BILLING_QUEUE_A")
        ])

        self.assertEqual(metrics["billing_queue"], 1)
        self.assertEqual(metrics["purchase"], 0)
        self.assertEqual(metrics["dropoffs"]["queue_to_purchase"], 1)

    def test_purchase_path(self):
        metrics = compute_funnel_metrics([
            event(1, "ENTRY"),
            event(1, "ZONE_ENTER", "SKINCARE_BROWSING"),
            event(1, "BILLING_QUEUE_JOIN", "BILLING_QUEUE_A")
        ], converted_visitor_ids=[1])

        self.assertEqual(metrics["purchase"], 1)
        self.assertEqual(metrics["rates"]["purchase_rate"], 1.0)

    def test_reentry_visitor_not_double_counted(self):
        metrics = compute_funnel_metrics([
            event(1, "ENTRY"),
            event(1, "REENTRY"),
            event(1, "ZONE_ENTER", "SKINCARE_BROWSING")
        ])

        self.assertEqual(metrics["entry"], 1)
        self.assertEqual(metrics["zone_visit"], 1)

    def test_staff_visitor_excluded(self):
        metrics = compute_funnel_metrics([
            event(1, "ENTRY", is_staff=True),
            event(1, "ZONE_ENTER", "SKINCARE_BROWSING", is_staff=True),
            event(1, "BILLING_QUEUE_JOIN", "BILLING_QUEUE_A", is_staff=True),
            event(1, "PURCHASE", is_staff=True)
        ])

        self.assertEqual(metrics["entry"], 0)
        self.assertEqual(metrics["zone_visit"], 0)
        self.assertEqual(metrics["billing_queue"], 0)
        self.assertEqual(metrics["purchase"], 0)

    def test_duplicate_queue_joins_count_once(self):
        metrics = compute_funnel_metrics([
            event(1, "ENTRY"),
            event(1, "BILLING_QUEUE_JOIN", "BILLING_QUEUE_A"),
            event(1, "BILLING_QUEUE_JOIN", "BILLING_QUEUE_A")
        ])

        self.assertEqual(metrics["billing_queue"], 1)

    def test_duplicate_zone_entries_count_once(self):
        metrics = compute_funnel_metrics([
            event(1, "ENTRY"),
            event(1, "ZONE_ENTER", "SKINCARE_BROWSING"),
            event(1, "ZONE_ENTER", "PREMIUM_SKINCARE")
        ])

        self.assertEqual(metrics["zone_visit"], 1)

    def test_zero_visitors(self):
        metrics = compute_funnel_metrics([])

        self.assertEqual(metrics["entry"], 0)
        self.assertEqual(metrics["zone_visit"], 0)
        self.assertEqual(metrics["billing_queue"], 0)
        self.assertEqual(metrics["purchase"], 0)
        self.assertEqual(metrics["rates"]["purchase_rate"], 0.0)

    def test_done_when_scenario(self):
        metrics = compute_funnel_metrics([
            event(1, "ENTRY"),
            event(1, "ZONE_ENTER", "SKINCARE_BROWSING"),
            event(1, "BILLING_QUEUE_JOIN", "BILLING_QUEUE_A"),
            event(1, "PURCHASE"),
            event(2, "ENTRY"),
            event(2, "ZONE_ENTER", "SKINCARE_BROWSING")
        ])

        self.assertEqual(metrics["entry"], 2)
        self.assertEqual(metrics["zone_visit"], 2)
        self.assertEqual(metrics["billing_queue"], 1)
        self.assertEqual(metrics["purchase"], 1)
        self.assertEqual(metrics["dropoffs"]["zone_to_queue"], 1)
        self.assertEqual(metrics["rates"]["purchase_rate"], 0.5)
        self.assertEqual(metrics["rates"]["entry_to_zone_rate"], 1.0)
        self.assertEqual(metrics["rates"]["zone_to_queue_rate"], 0.5)
        self.assertEqual(metrics["rates"]["queue_to_purchase_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
