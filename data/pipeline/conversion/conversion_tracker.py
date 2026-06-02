"""
Conversion Tracker

Correlates visitor billing zone visits with POS transactions to determine
conversion status.

Definition:
A visitor is converted if:
1. Visitor entered the billing zone (detected via track position)
2. A POS transaction occurred within CORRELATION_WINDOW_FRAMES of the zone entry
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from datetime import datetime, timedelta

# Configuration
CORRELATION_WINDOW_FRAMES = 1500  # ~50 seconds at 30fps
DEFAULT_FPS = 30
BILLING_ZONE = {
    "name": "BILLING_ZONE",
    "x1": 0,
    "y1": 0,
    "x2": 1920,
    "y2": 300  # Top portion of frame is typically checkout
}


class VisitorSession:
    """Represents a visitor's session in the store."""

    def __init__(self, visitor_id: int):
        self.visitor_id = visitor_id
        self.first_frame = None
        self.last_frame = None
        self.billing_zone_entry_frame: Optional[int] = None
        self.zones_visited: Set[str] = set()
        self.converted = False
        self.transaction_id: Optional[str] = None
        self.dwell_time_seconds = 0
        self.is_staff = False

    def to_dict(self) -> Dict:
        return {
            "visitor_id": self.visitor_id,
            "first_frame": self.first_frame,
            "last_frame": self.last_frame,
            "billing_zone_entry_frame": self.billing_zone_entry_frame,
            "zones_visited": list(self.zones_visited),
            "converted": self.converted,
            "transaction_id": self.transaction_id,
            "dwell_time_seconds": self.dwell_time_seconds
        }


class ConversionTracker:
    """
    Tracks visitor conversions by correlating:
    - Visitor track data
    - Billing zone entries
    - POS transactions
    """

    def __init__(self, fps: int = DEFAULT_FPS):
        """
        Initialize conversion tracker.
        
        Args:
            fps: Video frame rate (default 30 fps)
        """
        self.fps = fps
        self.sessions: Dict[int, VisitorSession] = {}
        self.pos_transactions: List[Dict] = []

    def load_tracks(self, tracks_file: str) -> None:
        """
        Load visitor track data from JSON file.
        
        Expected format:
        [
            {"frame": 1, "track_id": 1, "center_x": 100, "center_y": 200},
            ...
        ]
        """
        path = Path(tracks_file)
        if not path.exists():
            raise FileNotFoundError(f"Tracks file not found: {tracks_file}")

        with open(path, "r") as f:
            tracks = json.load(f)

        # Initialize sessions and process tracks
        for track in tracks:
            visitor_id = track["track_id"]
            frame = track["frame"]
            center_x = track["center_x"]
            center_y = track["center_y"]

            is_staff = bool(track.get("is_staff", False))
            if visitor_id not in self.sessions:
                self.sessions[visitor_id] = VisitorSession(visitor_id)

            session = self.sessions[visitor_id]
            session.is_staff = session.is_staff or is_staff
            session.first_frame = min(
                session.first_frame or frame, frame
            )
            session.last_frame = max(
                session.last_frame or frame, frame
            )

            # Check if visitor entered billing zone
            if self._is_in_billing_zone(center_x, center_y):
                if session.billing_zone_entry_frame is None:
                    session.billing_zone_entry_frame = frame

        print(
            f"Loaded {len(self.sessions)} visitor sessions "
            f"from {tracks_file}"
        )

    def load_zone_analytics(self, analytics_file: str) -> None:
        """
        Load zone analytics to track which zones visitors entered.
        
        Expected format:
        {
            "ZONE_NAME": {
                "visitors": 10,
                "total_dwell_time": 100.5
            },
            ...
        }
        """
        path = Path(analytics_file)
        if not path.exists():
            print(f"Warning: Analytics file not found: {analytics_file}")
            return

        with open(path, "r") as f:
            analytics = json.load(f)

        # For now, we'll track billing zone separately
        # In a full implementation, we'd cross-reference with dwell data

    def load_dwell_data(self, dwell_file: str) -> None:
        """
        Load dwell time data to update visitor session times.
        
        Expected format (CSV):
        visitor_id,zone,frames,dwell_time_seconds
        """
        path = Path(dwell_file)
        if not path.exists():
            print(f"Warning: Dwell file not found: {dwell_file}")
            return

        import csv
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                visitor_id = int(row["visitor_id"])
                dwell_seconds = float(row["dwell_time_seconds"])

                if visitor_id in self.sessions:
                    self.sessions[visitor_id].dwell_time_seconds = max(
                        self.sessions[visitor_id].dwell_time_seconds,
                        dwell_seconds
                    )

    def add_pos_transaction(
        self,
        transaction_id: str,
        timestamp: datetime
    ) -> None:
        """Add a POS transaction for correlation."""
        self.pos_transactions.append({
            "transaction_id": transaction_id,
            "timestamp": timestamp
        })

    def load_pos_data(self, pos_file: str) -> None:
        """Load POS transaction data from JSON or CSV."""
        from data.pipeline.conversion.pos_ingestion import POSIngestionLayer

        ingestion = POSIngestionLayer()
        try:
            transactions = ingestion.ingest(pos_file)
            self.pos_transactions = [
                {
                    "transaction_id": txn.transaction_id,
                    "timestamp": txn.timestamp
                }
                for txn in transactions
            ]
            print(f"Loaded {len(transactions)} POS transactions")
        except Exception as e:
            print(f"Warning: Could not load POS data: {e}")

    def frame_to_seconds(self, frame: int) -> float:
        """Convert frame number to seconds."""
        return frame / self.fps

    def correlate_conversions(
        self,
        video_start_time: Optional[datetime] = None
    ) -> None:
        """
        Correlate visitor billing zone visits with POS transactions.
        
        A visitor is converted if:
        1. They entered the billing zone
        2. A POS transaction occurred within correlation window
        
        Args:
            video_start_time: Start timestamp of the video
                              (default: None, no time-based correlation)
        """
        if not self.pos_transactions:
            print("No POS transactions loaded. Skipping conversion correlation.")
            return

        # If no video start time, use frame-based fallback correlation only
        if video_start_time is None:
            self._correlate_frame_based()
        else:
            self._correlate_timestamp_based(video_start_time)

    def _correlate_frame_based(self) -> None:
        """Correlate using frame numbers in a fallback mode."""
        if not self.pos_transactions:
            return

        ordered_sessions = sorted(
            [s for s in self.sessions.values()
             if not s.is_staff and s.billing_zone_entry_frame is not None],
            key=lambda s: s.billing_zone_entry_frame
        )
        ordered_txns = sorted(
            self.pos_transactions,
            key=lambda txn: txn["timestamp"]
        )

        # Assign at most one transaction per visitor and one visitor per transaction.
        for session, txn in zip(ordered_sessions, ordered_txns):
            session.converted = True
            session.transaction_id = txn["transaction_id"]

    def _correlate_timestamp_based(self, video_start_time: datetime) -> None:
        """Correlate using frame timestamps converted to actual times."""
        if not self.pos_transactions:
            return

        ordered_sessions = sorted(
            [s for s in self.sessions.values()
             if not s.is_staff and s.billing_zone_entry_frame is not None],
            key=lambda s: s.billing_zone_entry_frame
        )
        ordered_txns = sorted(
            self.pos_transactions,
            key=lambda txn: txn["timestamp"]
        )

        for txn in ordered_txns:
            txn_time = txn["timestamp"]
            window_start = txn_time - timedelta(
                seconds=self.frame_to_seconds(CORRELATION_WINDOW_FRAMES)
            )
            window_end = txn_time + timedelta(
                seconds=self.frame_to_seconds(CORRELATION_WINDOW_FRAMES)
            )

            for session in ordered_sessions:
                if session.converted:
                    continue

                frame_seconds = self.frame_to_seconds(
                    session.billing_zone_entry_frame
                )
                billing_entry_time = video_start_time + timedelta(
                    seconds=frame_seconds
                )

                if window_start <= billing_entry_time <= window_end:
                    session.converted = True
                    session.transaction_id = txn["transaction_id"]
                    break

    def get_conversion_stats(self) -> Dict:
        """Calculate and return conversion statistics."""
        sessions = [
            s for s in self.sessions.values() if not s.is_staff
        ]
        total_visitors = len(sessions)
        converted_visitors = sum(1 for s in sessions if s.converted)
        billing_zone_visitors = sum(
            1 for s in sessions if s.billing_zone_entry_frame is not None
        )

        conversion_rate = 0.0
        if total_visitors > 0:
            conversion_rate = (converted_visitors / total_visitors) * 100

        billing_zone_rate = 0.0
        if total_visitors > 0:
            billing_zone_rate = (billing_zone_visitors / total_visitors) * 100

        return {
            "total_visitors": total_visitors,
            "converted_visitors": converted_visitors,
            "billing_zone_visitors": billing_zone_visitors,
            "conversion_rate": round(conversion_rate, 2),
            "billing_zone_rate": round(billing_zone_rate, 2)
        }

    def get_sessions(self) -> Dict[int, VisitorSession]:
        """Return all visitor sessions."""
        return self.sessions

    def export_sessions(self, output_file: str) -> None:
        """Export sessions to JSON."""
        sessions_data = {
            vid: session.to_dict()
            for vid, session in self.sessions.items()
        }

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(sessions_data, f, indent=4)

        print(f"Exported {len(sessions_data)} sessions to {output_file}")

    def _is_in_billing_zone(self, center_x: int, center_y: int) -> bool:
        """Check if a point is within the billing zone."""
        return (
            BILLING_ZONE["x1"] <= center_x <= BILLING_ZONE["x2"]
            and
            BILLING_ZONE["y1"] <= center_y <= BILLING_ZONE["y2"]
        )
