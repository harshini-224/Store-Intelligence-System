"""
Test suite for Queue Analytics.

Tests for:
1. Queue depth tracking
2. Queue JOIN/ABANDON events
3. Visitor sessions
4. Abandonment rate calculation
5. Reentry handling
6. Staff exclusion
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from data.pipeline.analytics.queue_tracker import QueueTracker, QueueSession


def test_single_visitor_enters_queue():
    """Test: Single visitor enters queue."""
    tracker = QueueTracker(fps=30)
    
    # Visitor 1 enters queue at frame 10
    result = tracker.visitor_enters_queue(visitor_id=1, frame_no=10, timestamp="2026-05-30T10:00:00Z")
    
    assert result is True, "Should emit JOIN event"
    assert tracker.get_current_queue_depth() == 1, "Queue depth should be 1"
    print("✓ Test 1: Single visitor enters queue")


def test_queue_join_emitted_once():
    """Test: Queue JOIN emitted only once per visitor."""
    tracker = QueueTracker(fps=30)
    
    # Visitor 1 enters queue
    result1 = tracker.visitor_enters_queue(visitor_id=1, frame_no=10)
    assert result1 is True, "First JOIN should emit"
    
    # Try to enter again (already in queue)
    result2 = tracker.visitor_enters_queue(visitor_id=1, frame_no=20)
    assert result2 is False, "Second JOIN should not emit (already in queue)"
    
    assert tracker.get_current_queue_depth() == 1, "Queue depth should still be 1"
    print("✓ Test 2: Queue JOIN emitted only once per visitor")


def test_multiple_visitors_in_queue():
    """Test: Multiple visitors in queue."""
    tracker = QueueTracker(fps=30)
    
    tracker.visitor_enters_queue(visitor_id=1, frame_no=10)
    tracker.visitor_enters_queue(visitor_id=2, frame_no=20)
    tracker.visitor_enters_queue(visitor_id=3, frame_no=30)
    
    assert tracker.get_current_queue_depth() == 3, "Queue depth should be 3"
    print("✓ Test 3: Multiple visitors in queue")


def test_queue_depth_increases_correctly():
    """Test: Queue depth increases as visitors enter."""
    tracker = QueueTracker(fps=30)
    
    depths = []
    for i in range(1, 6):
        tracker.visitor_enters_queue(visitor_id=i, frame_no=i*10)
        depths.append(tracker.get_current_queue_depth())
    
    assert depths == [1, 2, 3, 4, 5], "Queue depth should increase correctly"
    print("✓ Test 4: Queue depth increases correctly")


def test_queue_depth_decreases_correctly():
    """Test: Queue depth decreases as visitors exit."""
    tracker = QueueTracker(fps=30)
    
    # Add visitors
    for i in range(1, 6):
        tracker.visitor_enters_queue(visitor_id=i, frame_no=i*10)
    
    assert tracker.get_current_queue_depth() == 5, "Initial queue depth should be 5"
    
    # Remove visitors
    depths = []
    for i in range(1, 6):
        tracker.visitor_exits_queue(visitor_id=i, frame_no=i*100)
        depths.append(tracker.get_current_queue_depth())
    
    assert depths == [4, 3, 2, 1, 0], "Queue depth should decrease correctly"
    print("✓ Test 5: Queue depth decreases correctly")


def test_visitor_exits_queue():
    """Test: Visitor exits queue."""
    tracker = QueueTracker(fps=30, min_queue_wait_seconds=1, abandon_window_seconds=10)
    
    # Visitor 1 enters at frame 10, exits at frame 40 (1 second at 30fps)
    tracker.visitor_enters_queue(visitor_id=1, frame_no=10)
    result = tracker.visitor_exits_queue(visitor_id=1, frame_no=40)
    
    assert result is True, "Exit should return True for completed session"
    assert tracker.get_current_queue_depth() == 0, "Queue should be empty"
    
    # Finalize abandonment checks (10 sec * 30 fps = 300 frames after exit)
    tracker.finalize_abandonment_checks(current_frame=400)
    
    # Check session was recorded
    sessions = tracker.get_sessions()
    assert len(sessions) == 1, "Should have one session"
    assert sessions[0].visitor_id == 1, "Session should be for visitor 1"
    assert sessions[0].wait_time_seconds == 1.0, "Wait time should be 1.0 seconds"
    print("✓ Test 6: Visitor exits queue")


def test_visitor_purchases_no_abandon():
    """Test: Visitor purchases => no abandon."""
    tracker = QueueTracker(fps=30, min_queue_wait_seconds=1)
    
    # Visitor enters queue and exits
    tracker.visitor_enters_queue(visitor_id=1, frame_no=10)
    tracker.visitor_exits_queue(visitor_id=1, frame_no=40)
    
    # Mark as converted
    tracker.mark_session_converted(visitor_id=1)
    
    # Finalize abandonment check (simulate end of video)
    abandoned = tracker.finalize_abandonment_checks(current_frame=50000)
    
    assert 1 not in abandoned, "Visitor 1 should not be abandoned (converted)"
    print("✓ Test 7: Visitor purchases => no abandon")


def test_visitor_leaves_without_purchase_abandon():
    """Test: Visitor leaves without purchase => abandon."""
    tracker = QueueTracker(
        fps=30,
        min_queue_wait_seconds=1,
        abandon_window_seconds=10
    )
    
    # Visitor enters queue and exits
    tracker.visitor_enters_queue(visitor_id=1, frame_no=10)
    tracker.visitor_exits_queue(visitor_id=1, frame_no=40)
    
    # Do NOT mark as converted
    
    # Finalize abandonment check (well after abandon window: 10 sec = 300 frames)
    abandoned = tracker.finalize_abandonment_checks(current_frame=400)
    
    assert 1 in abandoned, "Visitor 1 should be abandoned (no conversion)"
    
    sessions = tracker.get_sessions()
    assert sessions[0].abandoned is True, "Session should be marked as abandoned"
    print("✓ Test 8: Visitor leaves without purchase => abandon")


def test_reentry_visitor_not_double_counted():
    """Test: Reentry visitor not double counted."""
    tracker = QueueTracker(fps=30, min_queue_wait_seconds=1, abandon_window_seconds=10)
    
    # Visitor 1 enters queue
    tracker.visitor_enters_queue(visitor_id=1, frame_no=10)
    
    # Visitor 1 exits queue
    tracker.visitor_exits_queue(visitor_id=1, frame_no=40)
    
    # Visitor 1 re-enters queue (same canonical ID)
    result = tracker.visitor_enters_queue(visitor_id=1, frame_no=100)
    assert result is True, "Should emit new JOIN for re-entering visitor"
    
    # Both visits tracked
    tracker.visitor_exits_queue(visitor_id=1, frame_no=130)
    
    # Finalize: both exits should be past the abandon window (300 frames)
    tracker.finalize_abandonment_checks(current_frame=500)
    
    sessions = tracker.get_sessions()
    assert len(sessions) >= 2, f"Should track both queue visits, got {len(sessions)}"
    print("✓ Test 9: Reentry visitor tracked separately")


def test_abandonment_rate_calculation():
    """Test: Abandonment rate calculated correctly."""
    tracker = QueueTracker(
        fps=30,
        min_queue_wait_seconds=1,
        abandon_window_seconds=10
    )
    
    # 2 visitors enter queue
    tracker.visitor_enters_queue(visitor_id=1, frame_no=10)
    tracker.visitor_enters_queue(visitor_id=2, frame_no=20)
    
    # Both exit
    tracker.visitor_exits_queue(visitor_id=1, frame_no=40)
    tracker.visitor_exits_queue(visitor_id=2, frame_no=50)
    
    # Visitor 1 converts, Visitor 2 doesn't
    tracker.mark_session_converted(visitor_id=1)
    
    # Finalize
    tracker.finalize_abandonment_checks(current_frame=400)
    
    stats = tracker.get_queue_stats()
    assert stats["queue_joins"] == 2, "Should have 2 joins"
    assert stats["queue_abandons"] == 1, "Should have 1 abandon"
    assert stats["abandonment_rate_percent"] == 50.0, "Abandonment rate should be 50%"
    print("✓ Test 10: Abandonment rate calculation")


def test_zero_queue_visitors():
    """Test: Handle zero queue visitors."""
    tracker = QueueTracker(fps=30)
    
    stats = tracker.get_queue_stats()
    assert stats["queue_joins"] == 0, "Should have 0 joins"
    assert stats["queue_abandons"] == 0, "Should have 0 abandons"
    assert stats["abandonment_rate_percent"] == 0.0, "Abandonment rate should be 0%"
    print("✓ Test 11: Zero queue visitors")


def test_multiple_simultaneous_sessions():
    """Test: Multiple simultaneous queue sessions."""
    tracker = QueueTracker(fps=30, min_queue_wait_seconds=1)
    
    # All 3 visitors in queue simultaneously
    tracker.visitor_enters_queue(visitor_id=1, frame_no=10)
    tracker.visitor_enters_queue(visitor_id=2, frame_no=10)
    tracker.visitor_enters_queue(visitor_id=3, frame_no=10)
    
    assert tracker.get_current_queue_depth() == 3, "All 3 should be in queue"
    
    # Exit in different order
    tracker.visitor_exits_queue(visitor_id=2, frame_no=40)
    assert tracker.get_current_queue_depth() == 2, "2 should remain"
    
    tracker.visitor_exits_queue(visitor_id=1, frame_no=50)
    assert tracker.get_current_queue_depth() == 1, "1 should remain"
    
    tracker.visitor_exits_queue(visitor_id=3, frame_no=60)
    assert tracker.get_current_queue_depth() == 0, "0 should remain"
    
    print("✓ Test 12: Multiple simultaneous sessions")


def test_queue_session_schema():
    """Test: Queue session schema is correct."""
    tracker = QueueTracker(fps=30, min_queue_wait_seconds=1, abandon_window_seconds=10)
    
    tracker.visitor_enters_queue(visitor_id=1, frame_no=10, timestamp="2026-05-30T10:00:00Z")
    tracker.visitor_exits_queue(visitor_id=1, frame_no=40, timestamp="2026-05-30T10:00:01Z")
    
    # Finalize to move to completed_sessions (10 sec window = 300 frames)
    tracker.finalize_abandonment_checks(current_frame=400)
    
    sessions = tracker.get_sessions()
    assert len(sessions) == 1, "Should have 1 session"
    
    session = sessions[0]
    assert session.visitor_id == 1, "Should have visitor_id"
    assert session.queue_entry_frame == 10, "Should have entry frame"
    assert session.queue_exit_frame == 40, "Should have exit frame"
    assert session.wait_time_seconds == 1.0, "Should have wait time"
    assert session.converted is False, "Should have converted flag"
    assert isinstance(session.abandoned, bool), "Should have abandoned flag"
    
    print("✓ Test 13: Queue session schema")


def test_average_and_max_queue_depth():
    """Test: Average and max queue depth calculation."""
    tracker = QueueTracker(fps=30)
    
    # Frame 1: depth 1
    tracker.update_queue_depth(1, {1})
    
    # Frame 2: depth 2
    tracker.update_queue_depth(2, {1, 2})
    
    # Frame 3: depth 3
    tracker.update_queue_depth(3, {1, 2, 3})
    
    # Frame 4: depth 2
    tracker.update_queue_depth(4, {1, 2})
    
    avg_depth = tracker.get_average_queue_depth()
    max_depth = tracker.get_max_queue_depth()
    
    assert max_depth == 3, "Max depth should be 3"
    assert avg_depth == 2.0, "Average depth should be 2.0"
    
    print("✓ Test 14: Average and max queue depth")


def run_all_tests():
    """Run all queue analytics tests."""
    print("\n" + "="*60)
    print("QUEUE ANALYTICS TEST SUITE")
    print("="*60 + "\n")
    
    test_single_visitor_enters_queue()
    test_queue_join_emitted_once()
    test_multiple_visitors_in_queue()
    test_queue_depth_increases_correctly()
    test_queue_depth_decreases_correctly()
    test_visitor_exits_queue()
    test_visitor_purchases_no_abandon()
    test_visitor_leaves_without_purchase_abandon()
    test_reentry_visitor_not_double_counted()
    test_abandonment_rate_calculation()
    test_zero_queue_visitors()
    test_multiple_simultaneous_sessions()
    test_queue_session_schema()
    test_average_and_max_queue_depth()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
