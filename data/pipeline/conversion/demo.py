"""
Conversion Analytics Demo

Quick demonstration of the conversion tracking functionality with sample data.
Run: python3 data/pipeline/conversion/demo.py
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from data.pipeline.conversion.conversion_tracker import ConversionTracker
from data.pipeline.conversion.pos_ingestion import POSIngestionLayer


def demo_basic_conversion():
    """Demo: Simple conversion scenario."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Conversion Tracking")
    print("="*70)

    # Create sample tracking data
    sample_tracks = [
        {"frame": 1, "track_id": 1, "center_x": 960, "center_y": 150},   # Visitor 1 in billing zone
        {"frame": 2, "track_id": 1, "center_x": 960, "center_y": 150},
        {"frame": 3, "track_id": 2, "center_x": 500, "center_y": 700},   # Visitor 2 outside
        {"frame": 4, "track_id": 2, "center_x": 500, "center_y": 700},
    ]

    # Create sample POS data
    sample_pos = [
        {
            "transaction_id": "TXN_001",
            "timestamp": "2026-05-30T10:05:00Z",
            "amount": 150.50,
            "payment_method": "credit_card"
        }
    ]

    # Write to temp files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_tracks, f)
        tracks_file = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_pos, f)
        pos_file = f.name

    try:
        # Run conversion tracking
        tracker = ConversionTracker(fps=30)
        tracker.load_tracks(tracks_file)
        tracker.load_pos_data(pos_file)
        tracker.correlate_conversions()

        # Get stats
        stats = tracker.get_conversion_stats()

        print("\nInput Data:")
        print(f"  - {len(sample_tracks)} tracking frames")
        print(f"  - {len(sample_pos)} POS transactions")
        print(f"  - {len(tracker.sessions)} unique visitors")

        print("\nConversion Results:")
        print(f"  - Total Visitors: {stats['total_visitors']}")
        print(f"  - Billing Zone Visitors: {stats['billing_zone_visitors']}")
        print(f"  - Converted Visitors: {stats['converted_visitors']}")
        print(f"  - Conversion Rate: {stats['conversion_rate']}%")
        print(f"  - Billing Zone Rate: {stats['billing_zone_rate']}%")

        print("\nVisitor Details:")
        for vid, session in tracker.sessions.items():
            status = "✓ CONVERTED" if session.converted else "✗ NOT CONVERTED"
            billing = f"(billing zone at frame {session.billing_zone_entry_frame})" \
                      if session.billing_zone_entry_frame else "(no billing zone visit)"
            print(f"  - Visitor {vid}: {status} {billing}")

    finally:
        Path(tracks_file).unlink()
        Path(pos_file).unlink()


def demo_pos_ingestion():
    """Demo: POS data ingestion."""
    print("\n" + "="*70)
    print("DEMO 2: POS Data Ingestion")
    print("="*70)

    # Create sample POS CSV
    csv_data = "transaction_id,timestamp,amount,payment_method\n"
    csv_data += "TXN_001,2026-05-30T10:05:00Z,150.50,credit_card\n"
    csv_data += "TXN_002,2026-05-30T10:10:00Z,75.25,cash\n"
    csv_data += "TXN_003,2026-05-30T10:15:00Z,200.00,digital_wallet\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_data)
        csv_file = f.name

    try:
        ingestion = POSIngestionLayer()
        transactions = ingestion.ingest_csv(csv_file)

        print(f"\nIngested {len(transactions)} transactions from CSV:")
        for txn in transactions:
            print(f"  - {txn.transaction_id}: ${txn.amount} ({txn.payment_method})")

    finally:
        Path(csv_file).unlink()


def demo_multiple_conversions():
    """Demo: Multiple visitors with mixed conversions."""
    print("\n" + "="*70)
    print("DEMO 3: Multiple Visitors with Mixed Conversions")
    print("="*70)

    # Create sample data with 5 visitors
    sample_tracks = []
    visitor_frames = {
        1: (960, 150),   # In billing zone
        2: (960, 150),   # In billing zone
        3: (960, 150),   # In billing zone
        4: (500, 700),   # Outside
        5: (500, 700),   # Outside
    }

    frame = 1
    for vid, (x, y) in visitor_frames.items():
        for f in range(frame, frame + 5):
            sample_tracks.append({
                "frame": f,
                "track_id": vid,
                "center_x": x,
                "center_y": y
            })
        frame += 5

    # Create sample POS data (2 transactions)
    sample_pos = [
        {
            "transaction_id": "TXN_001",
            "timestamp": "2026-05-30T10:05:00Z",
            "amount": 100.00
        },
        {
            "transaction_id": "TXN_002",
            "timestamp": "2026-05-30T10:10:00Z",
            "amount": 150.00
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_tracks, f)
        tracks_file = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_pos, f)
        pos_file = f.name

    try:
        tracker = ConversionTracker(fps=30)
        tracker.load_tracks(tracks_file)
        tracker.load_pos_data(pos_file)
        tracker.correlate_conversions()

        stats = tracker.get_conversion_stats()

        print("\nInput Data:")
        print(f"  - 5 unique visitors")
        print(f"  - 3 visitors entered billing zone")
        print(f"  - 2 POS transactions")

        print("\nResults:")
        print(f"  - Total Visitors: {stats['total_visitors']}")
        print(f"  - Billing Zone Visitors: {stats['billing_zone_visitors']}")
        print(f"  - Converted Visitors: {stats['converted_visitors']}")
        print(f"  - Conversion Rate: {stats['conversion_rate']}%")

        print("\nBreakdown:")
        for vid, session in sorted(tracker.sessions.items()):
            if session.billing_zone_entry_frame:
                status = "CONVERTED" if session.converted else "NO PURCHASE"
                print(f"  - Visitor {vid}: In billing zone → {status}")
            else:
                print(f"  - Visitor {vid}: No billing zone visit")

    finally:
        Path(tracks_file).unlink()
        Path(pos_file).unlink()


def demo_no_conversions():
    """Demo: No conversions (visitors never enter billing zone)."""
    print("\n" + "="*70)
    print("DEMO 4: No Conversions (No Billing Zone Visits)")
    print("="*70)

    sample_tracks = [
        {"frame": 1, "track_id": 1, "center_x": 500, "center_y": 700},
        {"frame": 2, "track_id": 1, "center_x": 500, "center_y": 700},
        {"frame": 3, "track_id": 2, "center_x": 500, "center_y": 700},
        {"frame": 4, "track_id": 2, "center_x": 500, "center_y": 700},
    ]

    sample_pos = [
        {
            "transaction_id": "TXN_001",
            "timestamp": "2026-05-30T10:05:00Z",
            "amount": 100.00
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_tracks, f)
        tracks_file = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_pos, f)
        pos_file = f.name

    try:
        tracker = ConversionTracker(fps=30)
        tracker.load_tracks(tracks_file)
        tracker.load_pos_data(pos_file)
        tracker.correlate_conversions()

        stats = tracker.get_conversion_stats()

        print("\nInput Data:")
        print(f"  - 2 visitors (both outside billing zone)")
        print(f"  - 1 POS transaction")

        print("\nResults:")
        print(f"  - Total Visitors: {stats['total_visitors']}")
        print(f"  - Billing Zone Visitors: {stats['billing_zone_visitors']}")
        print(f"  - Converted Visitors: {stats['converted_visitors']}")
        print(f"  - Conversion Rate: {stats['conversion_rate']}%")

    finally:
        Path(tracks_file).unlink()
        Path(pos_file).unlink()


if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  CONVERSION RATE ANALYTICS DEMO".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)

    try:
        demo_basic_conversion()
        demo_pos_ingestion()
        demo_multiple_conversions()
        demo_no_conversions()

        print("\n" + "="*70)
        print("✓ All demos completed successfully!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Error running demo: {e}")
        import traceback
        traceback.print_exc()
