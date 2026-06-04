"""Lightweight heuristic group detection from tracking output.

Detects groups of visitors who walk together based on:
- Spatial proximity (distance below threshold)
- Co-movement duration (together for N consecutive frames)
- Velocity similarity (similar speed and direction)

No deep learning or external services required.
"""

import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

# Configurable thresholds via environment or defaults
GROUP_DISTANCE_THRESHOLD = int(
    os.getenv("GROUP_DISTANCE_THRESHOLD", "150")
)
GROUP_FRAME_THRESHOLD = int(
    os.getenv("GROUP_FRAME_THRESHOLD", "15")
)
GROUP_VELOCITY_THRESHOLD = float(
    os.getenv("GROUP_VELOCITY_THRESHOLD", "50.0")
)


class GroupDetector:
    """Detect visitor groups using spatial and velocity heuristics.

    Groups are formed when two or more visitors remain within
    GROUP_DISTANCE_THRESHOLD pixels of each other for at least
    GROUP_FRAME_THRESHOLD consecutive frames, with velocity
    differences below GROUP_VELOCITY_THRESHOLD pixels/frame.
    """

    def __init__(
        self,
        distance_threshold: int = GROUP_DISTANCE_THRESHOLD,
        frame_threshold: int = GROUP_FRAME_THRESHOLD,
        velocity_threshold: float = GROUP_VELOCITY_THRESHOLD,
    ):
        self.distance_threshold = distance_threshold
        self.frame_threshold = frame_threshold
        self.velocity_threshold = velocity_threshold

        # Tracks: visitor_id -> list of (frame, x, y)
        self._positions: Dict[int, List[Tuple[int, int, int]]] = defaultdict(list)

        # Pair co-movement counters: (id_a, id_b) -> consecutive frame count
        self._pair_streak: Dict[Tuple[int, int], int] = defaultdict(int)

        # Confirmed groups: visitor_id -> group_id
        self._group_assignments: Dict[int, str] = {}

        # Group counter
        self._next_group: int = 1

    def _make_pair_key(self, a: int, b: int) -> Tuple[int, int]:
        return (min(a, b), max(a, b))

    def _distance(
        self, p1: Tuple[int, int], p2: Tuple[int, int]
    ) -> float:
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return (dx * dx + dy * dy) ** 0.5

    def _velocity(
        self, positions: List[Tuple[int, int, int]]
    ) -> Optional[Tuple[float, float]]:
        """Compute average velocity from last two positions."""
        if len(positions) < 2:
            return None
        f1, x1, y1 = positions[-2]
        f2, x2, y2 = positions[-1]
        df = f2 - f1
        if df == 0:
            return (0.0, 0.0)
        return ((x2 - x1) / df, (y2 - y1) / df)

    def _velocity_diff(
        self, v1: Tuple[float, float], v2: Tuple[float, float]
    ) -> float:
        dx = v1[0] - v2[0]
        dy = v1[1] - v2[1]
        return (dx * dx + dy * dy) ** 0.5

    def update(
        self, frame: int, active_visitors: Dict[int, Tuple[int, int]]
    ):
        """Process one frame of visitor positions.

        Args:
            frame: Frame number.
            active_visitors: Mapping of visitor_id -> (center_x, center_y)
                             for visitors visible in this frame.
        """
        # Record positions
        for vid, (x, y) in active_visitors.items():
            self._positions[vid].append((frame, x, y))

        # Compare all visitor pairs in this frame
        visitor_ids = list(active_visitors.keys())
        active_pairs = set()

        for i in range(len(visitor_ids)):
            for j in range(i + 1, len(visitor_ids)):
                a, b = visitor_ids[i], visitor_ids[j]
                pair = self._make_pair_key(a, b)
                active_pairs.add(pair)

                pos_a = active_visitors[a]
                pos_b = active_visitors[b]
                dist = self._distance(pos_a, pos_b)

                if dist > self.distance_threshold:
                    self._pair_streak[pair] = 0
                    continue

                # Check velocity similarity
                vel_a = self._velocity(self._positions[a])
                vel_b = self._velocity(self._positions[b])

                if vel_a is not None and vel_b is not None:
                    vel_diff = self._velocity_diff(vel_a, vel_b)
                    if vel_diff > self.velocity_threshold:
                        self._pair_streak[pair] = 0
                        continue

                # Increment co-movement streak
                self._pair_streak[pair] += 1

                # Check if threshold met
                if self._pair_streak[pair] >= self.frame_threshold:
                    self._assign_group(a, b)

        # Reset streaks for pairs no longer active together
        stale_pairs = [
            p for p in self._pair_streak if p not in active_pairs
        ]
        for p in stale_pairs:
            self._pair_streak[p] = 0

    def _assign_group(self, a: int, b: int):
        """Assign two visitors to the same group."""
        group_a = self._group_assignments.get(a)
        group_b = self._group_assignments.get(b)

        if group_a and group_b:
            # Both already in groups — merge if different
            if group_a != group_b:
                # Merge b's group into a's group
                for vid, gid in self._group_assignments.items():
                    if gid == group_b:
                        self._group_assignments[vid] = group_a
        elif group_a:
            self._group_assignments[b] = group_a
        elif group_b:
            self._group_assignments[a] = group_b
        else:
            group_id = f"GROUP_{self._next_group}"
            self._next_group += 1
            self._group_assignments[a] = group_id
            self._group_assignments[b] = group_id

    def get_group_assignments(self) -> Dict[int, str]:
        """Return visitor_id -> group_id mapping for grouped visitors."""
        return dict(self._group_assignments)

    def get_group_analytics(self, all_visitor_ids: set) -> Dict[str, Any]:
        """Return group analytics summary.

        Args:
            all_visitor_ids: Set of all visitor IDs seen.

        Returns:
            Dictionary with group_visitors, solo_visitors, and group details.
        """
        grouped = set(self._group_assignments.keys())
        solo = all_visitor_ids - grouped

        groups: Dict[str, List[int]] = defaultdict(list)
        for vid, gid in self._group_assignments.items():
            groups[gid].append(vid)

        return {
            "group_visitors": len(grouped),
            "solo_visitors": len(solo),
            "total_groups": len(groups),
            "groups": {
                gid: {"members": sorted(members), "size": len(members)}
                for gid, members in sorted(groups.items())
            },
        }


def detect_groups_from_tracks(
    tracks: List[Dict[str, Any]],
    distance_threshold: int = GROUP_DISTANCE_THRESHOLD,
    frame_threshold: int = GROUP_FRAME_THRESHOLD,
    velocity_threshold: float = GROUP_VELOCITY_THRESHOLD,
) -> GroupDetector:
    """Run group detection over a list of track records.

    Each record must have: track_id, frame, center_x, center_y.

    Returns:
        GroupDetector instance with results.
    """
    detector = GroupDetector(
        distance_threshold=distance_threshold,
        frame_threshold=frame_threshold,
        velocity_threshold=velocity_threshold,
    )

    # Group track records by frame
    frames: Dict[int, Dict[int, Tuple[int, int]]] = defaultdict(dict)
    for record in tracks:
        frame = record.get("frame", 0)
        track_id = record.get("track_id", 0)
        cx = record.get("center_x", 0)
        cy = record.get("center_y", 0)
        frames[frame][track_id] = (cx, cy)

    # Process frames in order
    for frame_no in sorted(frames.keys()):
        detector.update(frame_no, frames[frame_no])

    return detector
