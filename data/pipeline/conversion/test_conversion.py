"""
Unit tests for conversion rate analytics

Tests:
- visitor converted (entered billing zone AND POS transaction exists)
- visitor not converted (no billing zone entry)
- multiple transactions
- empty POS file
- zero visitors
"""

import json
import csv
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import pytest

from data.pipeline.conversion.conversion_tracker import (
    ConversionTracker,
    VisitorSession,
    BILLING_ZONE
)
from data.pipeline.conversion.pos_ingestion import (
    POSTransaction,
    POSIngestionLayer
)


class TestPOSIngestion:
    """Test POS data ingestion."""

    def test_pos_transaction_creation(self):
        """Test creating a POS transaction object."""
        timestamp = datetime(2026, 5, 30, 10, 5, 0)
        txn = POSTransaction(
            transaction_id="TXN_001",
            timestamp=timestamp,
            amount=150.50,
            payment_method="credit_card"
        )

        assert txn.transaction_id == "TXN_001"
        assert txn.timestamp == timestamp
        assert txn.amount == 150.50
        assert txn.payment_method == "credit_card"

    def test_ingest_json(self):
        """Test ingesting POS data from JSON file."""
        # Create temporary JSON file
        sample_data = [
            {
                "transaction_id": "TXN_001",
                "timestamp": "2026-05-30T10:05:00Z",
                "amount": 150.50,
                "payment_method": "credit_card"
            },
            {
                "transaction_id": "TXN_002",
                "timestamp": "2026-05-30T10:10:00Z",
                "amount": 75.25,
                "payment_method": "cash"
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        ) as f:
            json.dump(sample_data, f)
            temp_file = f.name

        try:
            ingestion = POSIngestionLayer()
            transactions = ingestion.ingest_json(temp_file)

            assert len(transactions) == 2
            assert transactions[0].transaction_id == "TXN_001"
            assert transactions[0].amount == 150.50
            assert transactions[1].transaction_id == "TXN_002"
        finally:
            Path(temp_file).unlink()

    def test_ingest_csv(self):
        """Test ingesting POS data from CSV file."""
        csv_data = [
            ["transaction_id", "timestamp", "amount", "payment_method"],
            ["TXN_001", "2026-05-30T10:05:00Z", "150.50", "credit_card"],
            ["TXN_002", "2026-05-30T10:10:00Z", "75.25", "cash"]
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            temp_file = f.name

        try:
            ingestion = POSIngestionLayer()
            transactions = ingestion.ingest_csv(temp_file)

            assert len(transactions) == 2
            assert transactions[0].transaction_id == "TXN_001"
            assert float(transactions[0].amount) == 150.50
        finally:
            Path(temp_file).unlink()

    def test_ingest_nonexistent_file(self):
        """Test ingesting from non-existent file."""
        ingestion = POSIngestionLayer()
        transactions = ingestion.ingest_json("/nonexistent/path.json")

        assert len(transactions) == 0

    def test_auto_detect_format_json(self):
        """Test auto-detection of JSON format."""
        sample_data = [
            {
                "transaction_id": "TXN_001",
                "timestamp": "2026-05-30T10:05:00Z",
                "amount": 100.00
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        ) as f:
            json.dump(sample_data, f)
            temp_file = f.name

        try:
            ingestion = POSIngestionLayer()
            transactions = ingestion.ingest(temp_file)

            assert len(transactions) == 1
            assert transactions[0].transaction_id == "TXN_001"
        finally:
            Path(temp_file).unlink()


class TestConversionTracker:
    """Test conversion tracking logic."""

    def test_visitor_session_creation(self):
        """Test creating a visitor session."""
        session = VisitorSession(visitor_id=1)

        assert session.visitor_id == 1
        assert session.first_frame is None
        assert session.last_frame is None
        assert session.converted is False
        assert session.transaction_id is None

    def test_visitor_entered_billing_zone(self):
        """Test detecting when a visitor enters billing zone."""
        # Create sample tracks with billing zone entry
        sample_tracks = [
            {"frame": 1, "track_id": 1, "center_x": 960, "center_y": 150},  # In billing zone
            {"frame": 2, "track_id": 1, "center_x": 960, "center_y": 150},
            {"frame": 3, "track_id": 1, "center_x": 500, "center_y": 700}   # Outside billing zone
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        ) as f:
            json.dump(sample_tracks, f)
            temp_file = f.name

        try:
            tracker = ConversionTracker()
            tracker.load_tracks(temp_file)

            session = tracker.sessions[1]
            assert session.billing_zone_entry_frame == 1
        finally:
            Path(temp_file).unlink()

    def test_visitor_not_entered_billing_zone(self):
        """Test when visitor never enters billing zone."""
        sample_tracks = [
            {"frame": 1, "track_id": 1, "center_x": 500, "center_y": 700},
            {"frame": 2, "track_id": 1, "center_x": 500, "center_y": 700},
            {"frame": 3, "track_id": 1, "center_x": 600, "center_y": 800}
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        ) as f:
            json.dump(sample_tracks, f)
            temp_file = f.name

        try:
            tracker = ConversionTracker()
            tracker.load_tracks(temp_file)

            session = tracker.sessions[1]
            assert session.billing_zone_entry_frame is None
        finally:
            Path(temp_file).unlink()

    def test_zero_visitors(self):
        """Test with zero visitors (empty tracking data)."""
        sample_tracks = []

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        ) as f:
            json.dump(sample_tracks, f)
            temp_file = f.name

        try:
            tracker = ConversionTracker()
            tracker.load_tracks(temp_file)

            assert len(tracker.sessions) == 0
            stats = tracker.get_conversion_stats()

            assert stats["total_visitors"] == 0
            assert stats["converted_visitors"] == 0
            assert stats["conversion_rate"] == 0.0
        finally:
            Path(temp_file).unlink()

    def test_empty_pos_file(self):
        """Test with empty POS data."""
        sample_tracks = [
            {"frame": 1, "track_id": 1, "center_x": 960, "center_y": 150}  # In billing zone
        ]

        tracks_file = None
        pos_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_tracks, f)
                tracks_file = f.name

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump([], f)  # Empty transaction list
                pos_file = f.name

            tracker = ConversionTracker()
            tracker.load_tracks(tracks_file)
            tracker.load_pos_data(pos_file)
            tracker.correlate_conversions()

            stats = tracker.get_conversion_stats()
            assert stats["total_visitors"] == 1
            assert stats["billing_zone_visitors"] == 1
            assert stats["converted_visitors"] == 0  # No POS data
        finally:
            if tracks_file:
                Path(tracks_file).unlink()
            if pos_file:
                Path(pos_file).unlink()

    def test_visitor_converted(self):
        """Test successful visitor conversion (entered billing zone AND has POS transaction)."""
        sample_tracks = [
            {"frame": 1, "track_id": 1, "center_x": 960, "center_y": 150},  # In billing zone
            {"frame": 2, "track_id": 1, "center_x": 960, "center_y": 150},
        ]

        sample_pos = [
            {
                "transaction_id": "TXN_001",
                "timestamp": "2026-05-30T10:05:00Z",
                "amount": 150.50
            }
        ]

        tracks_file = None
        pos_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_tracks, f)
                tracks_file = f.name

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_pos, f)
                pos_file = f.name

            tracker = ConversionTracker()
            tracker.load_tracks(tracks_file)
            tracker.load_pos_data(pos_file)
            tracker.correlate_conversions()

            stats = tracker.get_conversion_stats()
            assert stats["total_visitors"] == 1
            assert stats["converted_visitors"] == 1
            assert stats["conversion_rate"] == 100.0

            session = tracker.sessions[1]
            assert session.converted is True
            assert session.transaction_id == "TXN_001"
        finally:
            if tracks_file:
                Path(tracks_file).unlink()
            if pos_file:
                Path(pos_file).unlink()

    def test_multiple_transactions(self):
        """Test with multiple POS transactions."""
        sample_tracks = [
            {"frame": 1, "track_id": 1, "center_x": 960, "center_y": 150},  # Visitor 1, in billing zone
            {"frame": 2, "track_id": 2, "center_x": 960, "center_y": 150},  # Visitor 2, in billing zone
            {"frame": 3, "track_id": 3, "center_x": 500, "center_y": 700},  # Visitor 3, not in billing zone
        ]

        sample_pos = [
            {
                "transaction_id": "TXN_001",
                "timestamp": "2026-05-30T10:05:00Z",
                "amount": 100.00
            },
            {
                "transaction_id": "TXN_002",
                "timestamp": "2026-05-30T10:10:00Z",
                "amount": 200.00
            },
            {
                "transaction_id": "TXN_003",
                "timestamp": "2026-05-30T10:15:00Z",
                "amount": 150.00
            }
        ]

        tracks_file = None
        pos_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_tracks, f)
                tracks_file = f.name

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_pos, f)
                pos_file = f.name

            tracker = ConversionTracker()
            tracker.load_tracks(tracks_file)
            tracker.load_pos_data(pos_file)
            tracker.correlate_conversions()

            stats = tracker.get_conversion_stats()
            assert stats["total_visitors"] == 3
            assert stats["converted_visitors"] == 2  # Visitors 1 and 2
            assert stats["conversion_rate"] == pytest.approx(66.67, 0.1)
            assert stats["billing_zone_visitors"] == 2
        finally:
            if tracks_file:
                Path(tracks_file).unlink()
            if pos_file:
                Path(pos_file).unlink()

    def test_one_transaction_matches_at_most_one_visitor(self):
        """One POS transaction should not convert multiple billing visitors."""
        sample_tracks = [
            {"frame": 1, "track_id": i, "center_x": 960, "center_y": 150}
            for i in range(1, 11)
        ]
        sample_pos = [
            {
                "transaction_id": "TXN_001",
                "timestamp": "2026-05-30T10:05:00Z",
                "amount": 100.00
            }
        ]

        tracks_file = None
        pos_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_tracks, f)
                tracks_file = f.name

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_pos, f)
                pos_file = f.name

            tracker = ConversionTracker()
            tracker.load_tracks(tracks_file)
            tracker.load_pos_data(pos_file)
            tracker.correlate_conversions()

            stats = tracker.get_conversion_stats()
            assert stats["total_visitors"] == 10
            assert stats["billing_zone_visitors"] == 10
            assert stats["converted_visitors"] == 1
        finally:
            if tracks_file:
                Path(tracks_file).unlink()
            if pos_file:
                Path(pos_file).unlink()

    def test_staff_visitors_are_excluded_from_conversion_metrics(self):
        """Staff visitors must not be counted in conversion metrics."""
        sample_tracks = [
            {"frame": 1, "track_id": 1, "center_x": 960, "center_y": 150, "is_staff": True},
            {"frame": 1, "track_id": 2, "center_x": 960, "center_y": 150, "is_staff": False}
        ]
        sample_pos = [
            {
                "transaction_id": "TXN_001",
                "timestamp": "2026-05-30T10:05:00Z",
                "amount": 100.00
            }
        ]

        tracks_file = None
        pos_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_tracks, f)
                tracks_file = f.name

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_pos, f)
                pos_file = f.name

            tracker = ConversionTracker()
            tracker.load_tracks(tracks_file)
            tracker.load_pos_data(pos_file)
            tracker.correlate_conversions()

            stats = tracker.get_conversion_stats()
            assert stats["total_visitors"] == 1
            assert stats["billing_zone_visitors"] == 1
            assert stats["converted_visitors"] == 1
        finally:
            if tracks_file:
                Path(tracks_file).unlink()
            if pos_file:
                Path(pos_file).unlink()

    def test_conversion_stats_accuracy(self):
        """Test accurate calculation of conversion statistics."""
        sample_tracks = [
            {"frame": 1, "track_id": 1, "center_x": 960, "center_y": 150},
            {"frame": 1, "track_id": 2, "center_x": 960, "center_y": 150},
            {"frame": 1, "track_id": 3, "center_x": 960, "center_y": 150},
            {"frame": 1, "track_id": 4, "center_x": 500, "center_y": 700},
        ]

        sample_pos = [
            {
                "transaction_id": "TXN_001",
                "timestamp": "2026-05-30T10:05:00Z",
                "amount": 100.00
            }
        ]

        tracks_file = None
        pos_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_tracks, f)
                tracks_file = f.name

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False
            ) as f:
                json.dump(sample_pos, f)
                pos_file = f.name

            tracker = ConversionTracker()
            tracker.load_tracks(tracks_file)
            tracker.load_pos_data(pos_file)
            tracker.correlate_conversions()

            stats = tracker.get_conversion_stats()

            # 4 total visitors
            # 3 in billing zone
            # Up to 3 could be converted (limited by POS count)
            assert stats["total_visitors"] == 4
            assert stats["billing_zone_visitors"] == 3
            assert stats["billing_zone_rate"] == 75.0
        finally:
            if tracks_file:
                Path(tracks_file).unlink()
            if pos_file:
                Path(pos_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
