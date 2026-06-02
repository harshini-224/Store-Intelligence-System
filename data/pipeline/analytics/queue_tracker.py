"""
Queue Analytics Tracker

Tracks visitor queue sessions, depth, and abandonment.

Definitions:
- Queue Depth: Number of unique visitors currently in queue zone
- Queue Join: First entry into queue zone
- Queue Abandon: Visitor enters queue but leaves without converting
- Queue Session: Visitor's time from queue entry to exit
"""

from typing import Dict, Set, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class QueueSession:
    """Represents a visitor's session in the queue."""
    
    visitor_id: int
    queue_entry_frame: int
    queue_exit_frame: Optional[int] = None
    queue_entry_timestamp: Optional[str] = None
    queue_exit_timestamp: Optional[str] = None
    converted: bool = False
    abandoned: bool = False
    wait_time_seconds: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class QueueTracker:
    """
    Tracks queue sessions and emits queue-related events.
    
    Tracks:
    - Queue depth per frame
    - Queue sessions per visitor
    - Join/Abandon events
    - Conversions
    """

    def __init__(
        self,
        fps: int = 30,
        queue_zone_id: str = "BILLING_QUEUE",
        abandon_window_seconds: int = 600,
        min_queue_wait_seconds: int = 3
    ):
        """
        Initialize queue tracker.
        
        Args:
            fps: Video frame rate (default 30 fps)
            queue_zone_id: ID of queue zone
            abandon_window_seconds: Time window to wait for conversion (default 600 = 10 min)
            min_queue_wait_seconds: Minimum wait time to count as queue visit (default 3 sec)
        """
        self.fps = fps
        self.queue_zone_id = queue_zone_id
        self.abandon_window_seconds = abandon_window_seconds
        self.min_queue_wait_seconds = min_queue_wait_seconds
        
        # Active sessions: visitor_id -> QueueSession
        self.active_sessions: Dict[int, QueueSession] = {}
        
        # Completed sessions for analytics
        self.completed_sessions: List[QueueSession] = []
        
        # Queue depth history: frame_no -> set of visitor_ids in queue
        self.queue_depth_history: Dict[int, Set[int]] = {}
        
        # Pending abandonment checks: visitor_id -> sessions awaiting finalization
        self.pending_abandonment: Dict[int, List[QueueSession]] = {}

    def visitor_enters_queue(
        self,
        visitor_id: int,
        frame_no: int,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Record visitor entering queue.
        
        Args:
            visitor_id: Canonical visitor ID
            frame_no: Frame number
            timestamp: ISO timestamp
            
        Returns:
            True if new JOIN event should be emitted, False if already in queue
        """
        if visitor_id in self.active_sessions:
            # Already in queue, don't emit duplicate JOIN
            return False
        
        # Create new session
        session = QueueSession(
            visitor_id=visitor_id,
            queue_entry_frame=frame_no,
            queue_entry_timestamp=timestamp
        )
        self.active_sessions[visitor_id] = session
        self.update_queue_depth(frame_no, set(self.active_sessions.keys()))
        
        return True  # Emit JOIN event

    def visitor_exits_queue(
        self,
        visitor_id: int,
        frame_no: int,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Record visitor exiting queue.
        
        Args:
            visitor_id: Canonical visitor ID
            frame_no: Frame number
            timestamp: ISO timestamp
            
        Returns:
            True if session completed, False if not in queue
        """
        if visitor_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[visitor_id]
        session.queue_exit_frame = frame_no
        session.queue_exit_timestamp = timestamp
        
        # Calculate wait time
        wait_frames = frame_no - session.queue_entry_frame
        wait_seconds = wait_frames / self.fps
        session.wait_time_seconds = round(wait_seconds, 2)
        
        self.active_sessions.pop(visitor_id)
        self.update_queue_depth(frame_no, set(self.active_sessions.keys()))

        # Only count if minimum wait time exceeded
        if wait_seconds >= self.min_queue_wait_seconds:
            self.pending_abandonment.setdefault(visitor_id, []).append(session)
            return True

        # Too short, discard session
        return False

    def update_queue_depth(self, frame_no: int, visitors_in_queue: Set[int]):
        """
        Update queue depth for a frame.
        
        Args:
            frame_no: Frame number
            visitors_in_queue: Set of visitor IDs currently in queue zone
        """
        self.queue_depth_history[frame_no] = visitors_in_queue.copy()

    def get_current_queue_depth(self) -> int:
        """Get current number of visitors in queue."""
        return len(self.active_sessions)

    def get_queue_depth_at_frame(self, frame_no: int) -> int:
        """Get queue depth at specific frame."""
        return len(self.queue_depth_history.get(frame_no, set()))

    def get_average_queue_depth(self) -> float:
        """Calculate average queue depth across all frames."""
        if not self.queue_depth_history:
            return 0.0
        
        total = sum(len(visitors) for visitors in self.queue_depth_history.values())
        count = len(self.queue_depth_history)
        return round(total / count, 2) if count > 0 else 0.0

    def get_max_queue_depth(self) -> int:
        """Get maximum queue depth across all frames."""
        if not self.queue_depth_history:
            return 0
        return max(len(visitors) for visitors in self.queue_depth_history.values())

    def mark_session_converted(self, visitor_id: int) -> bool:
        """
        Mark a pending session as converted (purchased).
        
        Args:
            visitor_id: Visitor ID
            
        Returns:
            True if marked, False if not found
        """
        pending_sessions = self.pending_abandonment.get(visitor_id, [])
        if not pending_sessions:
            return False
        
        for session in pending_sessions:
            if not session.converted:
                session.converted = True
                return True

        return True

    def finalize_abandonment_checks(self, current_frame: int) -> List[int]:
        """
        Finalize abandonment checks for sessions beyond abandonment window.
        
        Args:
            current_frame: Current frame number
            
        Returns:
            List of visitor IDs that abandoned the queue
        """
        abandoned_ids = []
        to_remove = []
        
        window_frames = int(self.abandon_window_seconds * self.fps)

        for visitor_id, sessions in self.pending_abandonment.items():
            remaining = []

            for session in sessions:
                exit_frame = session.queue_exit_frame
                if exit_frame is None:
                    remaining.append(session)
                    continue

                frames_since_exit = current_frame - exit_frame

                if frames_since_exit >= window_frames:
                    if not session.converted:
                        abandoned_ids.append(visitor_id)
                        session.abandoned = True

                    self.completed_sessions.append(session)
                else:
                    remaining.append(session)

            if remaining:
                self.pending_abandonment[visitor_id] = remaining
            else:
                to_remove.append(visitor_id)
        
        for visitor_id in to_remove:
            self.pending_abandonment.pop(visitor_id, None)
        
        return abandoned_ids

    def get_queue_stats(self) -> Dict:
        """
        Calculate queue statistics.
        
        Returns:
            Dictionary with queue metrics
        """
        pending_sessions = [
            session
            for sessions in self.pending_abandonment.values()
            for session in sessions
        ]
        total_joins = (
            len(self.completed_sessions)
            + len(self.active_sessions)
            + len(pending_sessions)
        )
        total_abandons = sum(
            1 for s in self.completed_sessions if s.abandoned
        )
        converted_count = sum(
            1 for s in self.completed_sessions if s.converted
        )
        
        abandonment_rate = 0.0
        if total_joins > 0:
            abandonment_rate = round(total_abandons / total_joins, 2)
        
        wait_times = [
            s.wait_time_seconds for s in self.completed_sessions 
            if s.wait_time_seconds > 0
        ]
        avg_wait_time = round(sum(wait_times) / len(wait_times), 2) if wait_times else 0.0
        max_wait_time = round(max(wait_times), 2) if wait_times else 0.0
        
        return {
            "queue_joins": total_joins,
            "queue_abandons": total_abandons,
            "queue_conversions": converted_count,
            "abandonment_rate": abandonment_rate,
            "abandonment_rate_percent": round(abandonment_rate * 100, 2),
            "current_queue_depth": self.get_current_queue_depth(),
            "average_queue_depth": self.get_average_queue_depth(),
            "max_queue_depth": self.get_max_queue_depth(),
            "average_queue_wait_time": avg_wait_time,
            "max_queue_wait_time": max_wait_time,
            "average_wait_time_seconds": avg_wait_time,
            "max_wait_time_seconds": max_wait_time
        }

    def get_sessions(self) -> List[QueueSession]:
        """Get all completed queue sessions."""
        return self.completed_sessions.copy()

    def export_sessions(self) -> List[Dict]:
        """Export sessions as dictionaries for JSON serialization."""
        return [session.to_dict() for session in self.completed_sessions]
