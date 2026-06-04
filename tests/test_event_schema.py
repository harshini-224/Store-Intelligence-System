"""Tests for canonical event schema with backward compatibility."""

import unittest

from app.models import Event, EventBatch


class TestCanonicalEventSchema(unittest.TestCase):
    """Test the expanded 9-field canonical event schema."""

    def test_full_schema_accepted(self):
        """All 9 fields provided — should parse without error."""
        event = Event(
            event_id="abc123",
            visitor_id=1,
            store_id="STORE_001",
            camera_id="CAM_FLOOR_A",
            timestamp="2026-06-02T10:00:00Z",
            event_type="ENTRY",
            zone_id="SKINCARE_BROWSING",
            confidence=0.95,
            metadata={"source": "line_crossing"},
        )
        self.assertEqual(event.event_id, "abc123")
        self.assertEqual(event.store_id, "STORE_001")
        self.assertEqual(event.zone_id, "SKINCARE_BROWSING")
        self.assertEqual(event.confidence, 0.95)
        self.assertEqual(event.metadata, {"source": "line_crossing"})

    def test_legacy_minimal_schema_accepted(self):
        """Legacy events with only visitor_id, event_type, timestamp — should
        parse with defaults for all other fields."""
        event = Event(
            visitor_id=5,
            event_type="EXIT",
            timestamp="2026-06-02T10:05:00Z",
        )
        self.assertEqual(event.visitor_id, 5)
        self.assertEqual(event.event_type, "EXIT")
        # Defaults should be applied
        self.assertTrue(len(event.event_id) > 0)  # auto-generated
        self.assertEqual(event.store_id, "STORE_001")
        self.assertEqual(event.camera_id, "CAM_UNKNOWN")
        self.assertIsNone(event.zone_id)
        self.assertEqual(event.confidence, 1.0)
        self.assertEqual(event.metadata, {})

    def test_legacy_zone_alias_accepted(self):
        """Legacy events using 'zone' field name should map to zone_id."""
        event = Event(
            visitor_id=3,
            event_type="ZONE_ENTER",
            timestamp="2026-06-02T10:10:00Z",
            zone="SKINCARE_BROWSING",
        )
        self.assertEqual(event.zone_id, "SKINCARE_BROWSING")

    def test_zone_id_canonical_name_accepted(self):
        """Events using 'zone_id' should also work."""
        event = Event(
            visitor_id=3,
            event_type="ZONE_ENTER",
            timestamp="2026-06-02T10:10:00Z",
            zone_id="PREMIUM_SKINCARE",
        )
        self.assertEqual(event.zone_id, "PREMIUM_SKINCARE")

    def test_auto_generated_event_id(self):
        """Two events without explicit event_id get unique IDs."""
        e1 = Event(visitor_id=1, event_type="ENTRY", timestamp="t1")
        e2 = Event(visitor_id=2, event_type="ENTRY", timestamp="t2")
        self.assertNotEqual(e1.event_id, e2.event_id)

    def test_missing_required_field_raises(self):
        """Missing visitor_id should raise validation error."""
        with self.assertRaises(Exception):
            Event(event_type="ENTRY", timestamp="t1")

    def test_invalid_visitor_id_type_raises(self):
        """Non-integer visitor_id should raise validation error."""
        with self.assertRaises(Exception):
            Event(
                visitor_id="not_a_number",
                event_type="ENTRY",
                timestamp="t1",
            )

    def test_invalid_confidence_type_raises(self):
        """Non-numeric confidence should raise validation error."""
        with self.assertRaises(Exception):
            Event(
                visitor_id=1,
                event_type="ENTRY",
                timestamp="t1",
                confidence="high",
            )

    def test_event_batch_with_mixed_schemas(self):
        """Batch containing both full and legacy events should parse."""
        batch = EventBatch(
            events=[
                {
                    "event_id": "full1",
                    "visitor_id": 1,
                    "store_id": "STORE_002",
                    "camera_id": "CAM_A",
                    "timestamp": "t1",
                    "event_type": "ENTRY",
                    "zone_id": "ZONE_A",
                    "confidence": 0.9,
                    "metadata": {"key": "val"},
                },
                {
                    "visitor_id": 2,
                    "event_type": "EXIT",
                    "timestamp": "t2",
                },
                {
                    "visitor_id": 3,
                    "event_type": "ZONE_ENTER",
                    "timestamp": "t3",
                    "zone": "LEGACY_ZONE",
                },
            ]
        )
        self.assertEqual(len(batch.events), 3)
        self.assertEqual(batch.events[0].store_id, "STORE_002")
        self.assertEqual(batch.events[1].store_id, "STORE_001")  # default
        self.assertEqual(batch.events[2].zone_id, "LEGACY_ZONE")  # alias

    def test_model_dump_includes_all_fields(self):
        """model_dump should include all canonical fields."""
        event = Event(
            visitor_id=1, event_type="ENTRY", timestamp="t1"
        )
        dump = event.model_dump()
        expected_keys = {
            "event_id", "visitor_id", "store_id", "camera_id",
            "timestamp", "event_type", "zone_id", "confidence", "metadata",
        }
        self.assertEqual(set(dump.keys()), expected_keys)


if __name__ == "__main__":
    unittest.main()
