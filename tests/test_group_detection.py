"""Tests for heuristic group detection."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.pipeline.tracking.group_detector import (
    GroupDetector,
    detect_groups_from_tracks,
)


class TestGroupDetector(unittest.TestCase):
    """Test lightweight group detection heuristics."""

    def test_two_visitors_walking_together(self):
        """Two visitors close together for enough frames → same group."""
        tracks = []
        for frame in range(1, 25):
            # Visitor 1 and 2 walk side by side, 50px apart
            tracks.append({
                "frame": frame,
                "track_id": 1,
                "center_x": 100 + frame * 5,
                "center_y": 500,
            })
            tracks.append({
                "frame": frame,
                "track_id": 2,
                "center_x": 140 + frame * 5,
                "center_y": 500,
            })

        detector = detect_groups_from_tracks(
            tracks,
            distance_threshold=150,
            frame_threshold=15,
            velocity_threshold=50.0,
        )
        assignments = detector.get_group_assignments()

        # Both should be in the same group
        self.assertIn(1, assignments)
        self.assertIn(2, assignments)
        self.assertEqual(assignments[1], assignments[2])

    def test_temporary_crossing_paths(self):
        """Two visitors crossing paths briefly should NOT form a group."""
        tracks = []
        for frame in range(1, 25):
            # Visitor 1 moves right
            tracks.append({
                "frame": frame,
                "track_id": 1,
                "center_x": 100 + frame * 20,
                "center_y": 500,
            })
            # Visitor 2 moves left — they briefly cross around frame 12
            tracks.append({
                "frame": frame,
                "track_id": 2,
                "center_x": 600 - frame * 20,
                "center_y": 500,
            })

        detector = detect_groups_from_tracks(
            tracks,
            distance_threshold=150,
            frame_threshold=15,
            velocity_threshold=50.0,
        )
        assignments = detector.get_group_assignments()

        # Opposing velocities → should NOT be grouped
        grouped_together = (
            1 in assignments
            and 2 in assignments
            and assignments[1] == assignments[2]
        )
        self.assertFalse(grouped_together)

    def test_diverging_trajectories(self):
        """Visitors start together then diverge → should NOT form a group
        (not enough co-movement frames before diverging)."""
        tracks = []
        for frame in range(1, 8):
            # Together for 7 frames (below threshold of 15)
            tracks.append({
                "frame": frame,
                "track_id": 1,
                "center_x": 100 + frame * 5,
                "center_y": 500,
            })
            tracks.append({
                "frame": frame,
                "track_id": 2,
                "center_x": 120 + frame * 5,
                "center_y": 500,
            })

        for frame in range(8, 25):
            # Diverge
            tracks.append({
                "frame": frame,
                "track_id": 1,
                "center_x": 100 + frame * 5,
                "center_y": 500,
            })
            tracks.append({
                "frame": frame,
                "track_id": 2,
                "center_x": 120 + frame * 5,
                "center_y": 500 + (frame - 7) * 30,
            })

        detector = detect_groups_from_tracks(
            tracks,
            distance_threshold=150,
            frame_threshold=15,
            velocity_threshold=50.0,
        )
        assignments = detector.get_group_assignments()

        # Should not be grouped
        grouped_together = (
            1 in assignments
            and 2 in assignments
            and assignments[1] == assignments[2]
        )
        self.assertFalse(grouped_together)

    def test_single_visitor_is_solo(self):
        """A single visitor should not be assigned to any group."""
        tracks = [
            {
                "frame": frame,
                "track_id": 1,
                "center_x": 100 + frame * 5,
                "center_y": 500,
            }
            for frame in range(1, 30)
        ]

        detector = detect_groups_from_tracks(tracks)
        assignments = detector.get_group_assignments()

        self.assertNotIn(1, assignments)

    def test_group_analytics(self):
        """Group analytics should report correct counts."""
        tracks = []
        for frame in range(1, 25):
            tracks.append({
                "frame": frame,
                "track_id": 1,
                "center_x": 100 + frame * 5,
                "center_y": 500,
            })
            tracks.append({
                "frame": frame,
                "track_id": 2,
                "center_x": 140 + frame * 5,
                "center_y": 500,
            })
            # Visitor 3 is far away — solo
            tracks.append({
                "frame": frame,
                "track_id": 3,
                "center_x": 1500,
                "center_y": 100,
            })

        detector = detect_groups_from_tracks(
            tracks,
            distance_threshold=150,
            frame_threshold=15,
            velocity_threshold=50.0,
        )
        analytics = detector.get_group_analytics({1, 2, 3})

        self.assertEqual(analytics["group_visitors"], 2)
        self.assertEqual(analytics["solo_visitors"], 1)
        self.assertEqual(analytics["total_groups"], 1)


if __name__ == "__main__":
    unittest.main()
