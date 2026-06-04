import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from data.pipeline.events.line_counter import LineCounter
from data.pipeline.events.event_generator import EventGenerator
from data.pipeline.analytics.dwell_time import DwellTimeTracker
from data.pipeline.analytics.zone_config import (
    FLOOR_A_ZONES, FLOOR_B_ZONES,
    FLOOR_A_QUEUE_ZONE, FLOOR_B_QUEUE_ZONE,
    QUEUE_CONFIG
)
from data.pipeline.analytics.zone_manager import ZoneManager
from data.pipeline.analytics.queue_tracker import QueueTracker
from data.pipeline.analytics.funnel_tracker import compute_funnel_metrics
from data.pipeline.tracking.group_detector import detect_groups_from_tracks

LINE_DEFINITIONS = {
    "entrance": ((850, 1080), (1550, 0)),
    "floor_a": ((0, 1080), (1920, 0)),
    "floor_b": ((0, 1080), (1920, 0)),
    "billing": ((0, 1080), (1920, 0)),
    "corner": ((0, 1080), (1920, 0))
}

ZONE_DEFINITIONS = {
    "floor_a": FLOOR_A_ZONES,
    "floor_b": FLOOR_B_ZONES
}

QUEUE_ZONE_DEFINITIONS = {
    "floor_a": FLOOR_A_QUEUE_ZONE,
    "floor_b": FLOOR_B_QUEUE_ZONE
}

FPS = 30
DWELL_INTERVAL_SECONDS = 30


def parse_video_start_time(
    start_time: Optional[str]
) -> Optional[datetime]:
    if not start_time:
        return None

    return datetime.fromisoformat(
        start_time.replace("Z", "+00:00")
    )


def build_default_camera_id(video_name: str) -> str:
    return f"CAM_{video_name.upper()}"


def load_converted_visitor_ids(sessions_file: Optional[str]) -> Set[int]:
    if not sessions_file:
        return set()

    path = Path(sessions_file)
    if not path.exists():
        return set()

    with open(path, "r") as file:
        sessions = json.load(file)

    converted_ids = set()
    if isinstance(sessions, dict):
        iterable = sessions.values()
    else:
        iterable = sessions

    for session in iterable:
        if session.get("converted"):
            converted_ids.add(int(session["visitor_id"]))

    return converted_ids


def process_tracks(
    tracks: List[Dict[str, Any]],
    video_name: str = "entrance",
    store_id: str = "STORE_001",
    camera_id: Optional[str] = None,
    fps: int = FPS,
    video_start_time: Optional[datetime] = None,
    line_start: Optional[Tuple[int, int]] = None,
    line_end: Optional[Tuple[int, int]] = None,
    reentry_time_window_seconds: int = 10,
    reentry_position_threshold_pixels: int = 1000,
    reentry_size_threshold_ratio: float = 0.5,
    converted_visitor_ids: Optional[Set[int]] = None,
    group_assignments: Optional[Dict[int, str]] = None
) -> EventGenerator:

    camera_id = camera_id or build_default_camera_id(video_name)

    if line_start is None or line_end is None:
        line_start, line_end = LINE_DEFINITIONS.get(
            video_name,
            LINE_DEFINITIONS["entrance"]
        )

    zone_manager = None
    if video_name in ZONE_DEFINITIONS:
        zone_manager = ZoneManager(ZONE_DEFINITIONS[video_name])

    line_counter = LineCounter(
        line_start=tuple(line_start),
        line_end=tuple(line_end)
    )

    event_generator = EventGenerator(
        store_id=store_id,
        camera_id=camera_id,
        fps=fps,
        video_start_time=video_start_time
    )
    event_generator.group_assignments = group_assignments or {}
    dwell_tracker = DwellTimeTracker(fps)
    queue_tracker = QueueTracker(
        fps=fps,
        queue_zone_id=QUEUE_ZONE_DEFINITIONS.get(video_name, {}).get("zone_id", "BILLING_QUEUE"),
        abandon_window_seconds=QUEUE_CONFIG["QUEUE_ABANDON_WINDOW_SECONDS"],
        min_queue_wait_seconds=QUEUE_CONFIG["MIN_QUEUE_WAIT_SECONDS"]
    )
    converted_visitor_ids = converted_visitor_ids or set()
    
    visitor_zones: Dict[int, str] = {}
    visitor_id_map: Dict[int, int] = {}
    exit_history: Dict[int, Dict[str, Any]] = {}
    active_visitors: Dict[int, bool] = {}
    visitor_is_staff: Dict[int, bool] = {}  # Track staff visitors

    def get_canonical_id(raw_id: int) -> int:
        return visitor_id_map.get(raw_id, raw_id)

    def register_canonical_id(raw_id: int, canonical_id: int):
        visitor_id_map[raw_id] = canonical_id

    def compute_area(record: Dict[str, Any]) -> Optional[float]:
        bbox = record.get("bbox")
        if not bbox or len(bbox) != 4:
            return None
        x1, y1, x2, y2 = bbox
        return abs((x2 - x1) * (y2 - y1))

    def is_in_queue_zone(center_x: int, center_y: int) -> bool:
        """Check if position is in queue zone."""
        if video_name not in QUEUE_ZONE_DEFINITIONS:
            return False
        
        queue_zone = QUEUE_ZONE_DEFINITIONS[video_name]
        x1 = queue_zone.get("x1", 0)
        y1 = queue_zone.get("y1", 0)
        x2 = queue_zone.get("x2", 1920)
        y2 = queue_zone.get("y2", 1080)
        
        return x1 <= center_x <= x2 and y1 <= center_y <= y2

    def infer_reentry_candidate(
        raw_id: int,
        point: Tuple[int, int],
        frame_no: int
    ) -> Optional[int]:
        current_side = line_counter.get_side(point)
        current_area = compute_area(record)
        best_candidate = None
        best_score = None

        for canonical_id, exit_info in exit_history.items():
            if active_visitors.get(canonical_id, False):
                continue

            age_frames = frame_no - exit_info["frame"]
            if age_frames < 0:
                continue

            if age_frames > reentry_time_window_seconds * fps:
                continue

            exit_side = exit_info["side"]
            if exit_side * current_side >= 0:
                continue

            dx = point[0] - exit_info["point"][0]
            dy = point[1] - exit_info["point"][1]
            distance = (dx * dx + dy * dy) ** 0.5
            if distance > reentry_position_threshold_pixels:
                continue

            if current_area is not None and exit_info["area"] is not None:
                area_ratio = min(current_area, exit_info["area"]) / max(current_area, exit_info["area"])
                if area_ratio < reentry_size_threshold_ratio:
                    continue

            score = (age_frames, distance)
            if best_score is None or score < best_score:
                best_score = score
                best_candidate = canonical_id

        return best_candidate

    for record in tracks:
        raw_id = record.get("track_id")
        point = (
            record.get("center_x"),
            record.get("center_y")
        )
        frame_no = record.get("frame")
        confidence = record.get("confidence", 1.0)
        is_staff = bool(record.get("is_staff", False))

        canonical_id = get_canonical_id(raw_id)
        metadata = {
            "source": "line_crossing",
            "is_staff": is_staff
        }
        reentry_candidate = None

        if canonical_id == raw_id:
            reentry_candidate = infer_reentry_candidate(
                raw_id,
                point,
                frame_no
            )

            if reentry_candidate is not None:
                register_canonical_id(raw_id, reentry_candidate)
                canonical_id = reentry_candidate
                metadata = {
                    "source": "reentry_inference",
                    "raw_track_id": raw_id,
                    "is_staff": is_staff
                }

        if canonical_id != raw_id and "raw_track_id" not in metadata:
            metadata["raw_track_id"] = raw_id

        line_event = line_counter.check_crossing(
            canonical_id,
            point
        )

        event_type = None
        if line_event == "ENTRY" and reentry_candidate is not None:
            event_type = "REENTRY"
        elif reentry_candidate is not None and line_event is None:
            event_type = "REENTRY"
        else:
            event_type = line_event

        if event_type:
            event_generator.add_event(
                canonical_id,
                event_type,
                frame_no,
                confidence=confidence,
                metadata=metadata
            )

            if event_type == "EXIT":
                exit_history[canonical_id] = {
                    "frame": frame_no,
                    "point": point,
                    "side": line_counter.get_side(point),
                    "area": compute_area(record)
                }
                active_visitors[canonical_id] = False

            if event_type in {"ENTRY", "REENTRY"}:
                active_visitors[canonical_id] = True
                if event_type == "REENTRY" and canonical_id in exit_history:
                    exit_history.pop(canonical_id, None)
        else:
            active_visitors[canonical_id] = True

        current_zone = "UNKNOWN"
        if zone_manager is not None:
            current_zone = zone_manager.get_zone(
                point[0],
                point[1]
            )

        previous_zone = visitor_zones.get(canonical_id, "UNKNOWN")

        if current_zone != previous_zone:
            if previous_zone != "UNKNOWN":
                event_generator.add_event(
                    canonical_id,
                    "ZONE_EXIT",
                    frame_no,
                    zone_id=previous_zone,
                    confidence=confidence,
                    metadata={
                        "source": "zone_transition",
                        "is_staff": is_staff
                    }
                )

            if current_zone != "UNKNOWN":
                event_generator.add_event(
                    canonical_id,
                    "ZONE_ENTER",
                    frame_no,
                    zone_id=current_zone,
                    confidence=confidence,
                    metadata={
                        "source": "zone_transition",
                        "is_staff": is_staff
                    }
                )

            visitor_zones[canonical_id] = current_zone

        dwell_events = dwell_tracker.update(
            canonical_id,
            current_zone
        )

        for _ in range(dwell_events):
            event_generator.add_event(
                canonical_id,
                "ZONE_DWELL",
                frame_no,
                zone_id=current_zone,
                confidence=confidence,
                metadata={
                    "source": "zone_dwell",
                    "is_staff": is_staff
                }
            )

        # Queue tracking
        if canonical_id not in visitor_is_staff:
            visitor_is_staff[canonical_id] = is_staff
        else:
            visitor_is_staff[canonical_id] = visitor_is_staff[canonical_id] or is_staff
        
        # Skip queue tracking for staff
        if not visitor_is_staff[canonical_id]:
            in_queue = is_in_queue_zone(point[0], point[1])
            if in_queue and canonical_id not in queue_tracker.active_sessions:
                # Visitor entering queue
                timestamp = event_generator.frame_to_timestamp(frame_no)
                if queue_tracker.visitor_enters_queue(canonical_id, frame_no, timestamp):
                    # Emit JOIN event
                    queue_depth = queue_tracker.get_current_queue_depth()
                    if queue_depth >= QUEUE_CONFIG["MIN_QUEUE_DEPTH_FOR_JOIN"]:
                        event_generator.add_event(
                            canonical_id,
                            "BILLING_QUEUE_JOIN",
                            frame_no,
                            zone_id=queue_tracker.queue_zone_id,
                            confidence=confidence,
                            metadata={
                                "source": "queue_entry",
                                "queue_depth": queue_depth,
                                "is_staff": False
                            }
                        )
            
            elif not in_queue and canonical_id in queue_tracker.active_sessions:
                # Visitor exiting queue
                timestamp = event_generator.frame_to_timestamp(frame_no)
                if queue_tracker.visitor_exits_queue(canonical_id, frame_no, timestamp):
                    # Will emit ABANDON event later after conversion check
                    pass

            queue_tracker.update_queue_depth(
                frame_no,
                set(queue_tracker.active_sessions.keys())
            )
    
    # Post-processing: mark conversions and emit abandon events.
    for visitor_id in converted_visitor_ids:
        queue_tracker.mark_session_converted(visitor_id)

    final_frame = max(
        [record.get("frame", 0) for record in tracks],
        default=0
    )
    abandon_check_frame = final_frame + int(
        QUEUE_CONFIG["QUEUE_ABANDON_WINDOW_SECONDS"] * fps
    )
    abandoned_ids = queue_tracker.finalize_abandonment_checks(
        abandon_check_frame
    )

    abandoned_sessions = [
        session for session in queue_tracker.get_sessions()
        if session.abandoned and session.visitor_id in abandoned_ids
    ]

    for session in abandoned_sessions:
        event_generator.add_event(
            session.visitor_id,
            "BILLING_QUEUE_ABANDON",
            session.queue_exit_frame or final_frame,
            zone_id=queue_tracker.queue_zone_id,
            confidence=1.0,
            metadata={
                "source": "queue_abandonment",
                "queue_entry_frame": session.queue_entry_frame,
                "queue_exit_frame": session.queue_exit_frame,
                "queue_wait_duration": session.wait_time_seconds,
                "is_staff": False
            }
        )

    for visitor_id in converted_visitor_ids:
        if visitor_is_staff.get(visitor_id, False):
            continue
        event_generator.add_event(
            visitor_id,
            "PURCHASE",
            final_frame,
            confidence=1.0,
            metadata={
                "source": "conversion_correlation",
                "is_staff": False
            }
        )
    
    # Store queue tracker reference on event generator for later access
    event_generator.queue_tracker = queue_tracker
    event_generator.funnel_metrics = compute_funnel_metrics(
        event_generator.events
    )
    
    return event_generator


def main(
    track_file,
    video_name="entrance",
    store_id="STORE_001",
    camera_id=None,
    video_start_time=None,
    line_start=None,
    line_end=None,
    reentry_time_window_seconds: int = 10,
    reentry_position_threshold_pixels: int = 1000,
    reentry_size_threshold_ratio: float = 0.5,
    conversion_sessions_file: Optional[str] = None
):

    track_path = Path(track_file)
    if not track_path.exists():
        raise FileNotFoundError(
            f"Track file not found: {track_path}"
        )

    with open(track_path, "r") as file:
        tracks = json.load(file)

    conversion_sessions_file = conversion_sessions_file or (
        f"data/outputs/conversion/{video_name}_sessions.json"
    )
    converted_visitor_ids = load_converted_visitor_ids(
        conversion_sessions_file
    )

    # Priority 4: Run Group Detection from tracks
    group_detector = detect_groups_from_tracks(tracks)
    group_assignments = group_detector.get_group_assignments()
    
    # Collect all unique track IDs for solo/group counts
    all_vids = {r.get("track_id") for r in tracks}
    group_stats = group_detector.get_group_analytics(all_vids)

    event_generator = process_tracks(
        tracks,
        video_name=video_name,
        store_id=store_id,
        camera_id=camera_id,
        fps=FPS,
        video_start_time=video_start_time,
        line_start=line_start,
        line_end=line_end,
        reentry_time_window_seconds=reentry_time_window_seconds,
        reentry_position_threshold_pixels=reentry_position_threshold_pixels,
        reentry_size_threshold_ratio=reentry_size_threshold_ratio,
        converted_visitor_ids=converted_visitor_ids,
        group_assignments=group_assignments
    )
    event_generator.group_stats = group_stats

    if not event_generator.events and tracks:
        first_frame_by_visitor: Dict[int, int] = {}
        confidence_by_visitor: Dict[int, float] = {}
        for record in tracks:
            visitor_id = int(record.get("track_id"))
            frame_no = int(record.get("frame", 1))
            first_frame_by_visitor[visitor_id] = min(
                frame_no,
                first_frame_by_visitor.get(visitor_id, frame_no)
            )
            confidence_by_visitor[visitor_id] = max(
                float(record.get("confidence", 1.0)),
                confidence_by_visitor.get(visitor_id, 0.0)
            )

        for visitor_id, frame_no in sorted(first_frame_by_visitor.items()):
            event_generator.add_event(
                visitor_id=visitor_id,
                event_type="TRACK_OBSERVED",
                frame_no=frame_no,
                confidence=confidence_by_visitor.get(visitor_id, 1.0),
                metadata={
                    "source": "tracking_fallback",
                    "reason": "No line-crossing event detected"
                }
            )

    event_generator.save_all()

    if hasattr(event_generator, "queue_tracker") and video_name in QUEUE_ZONE_DEFINITIONS:
        summary_path = Path(
            f"data/outputs/analytics/{video_name}_summary.json"
        )
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        if summary_path.exists():
            with open(summary_path, "r") as file:
                summary = json.load(file)
        else:
            summary = {}

        summary["_queue_metrics"] = event_generator.queue_tracker.get_queue_stats()
        summary["_funnel_metrics"] = event_generator.funnel_metrics
        summary["_group_metrics"] = getattr(event_generator, "group_stats", {})

        with open(summary_path, "w") as file:
            json.dump(summary, file, indent=4)

        print(f"Queue and funnel analytics updated: {summary_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate events from tracked visitor paths."
    )
    parser.add_argument(
        "--track-file",
        default=None,
        help="Path to the tracking JSON file."
    )
    parser.add_argument(
        "--video-name",
        default="entrance"
    )
    parser.add_argument(
        "--store-id",
        default="STORE_001"
    )
    parser.add_argument(
        "--camera-id",
        default=None
    )
    parser.add_argument(
        "--video-start-time",
        default=None,
        help="ISO timestamp of the first frame, e.g. 2026-05-30T10:05:00Z"
    )
    parser.add_argument(
        "--line-start",
        nargs=2,
        type=int,
        default=None
    )
    parser.add_argument(
        "--line-end",
        nargs=2,
        type=int,
        default=None
    )
    parser.add_argument(
        "--reentry-window-seconds",
        type=int,
        default=10,
        help="Maximum seconds after EXIT to infer a REENTRY for a canonical visitor."
    )
    parser.add_argument(
        "--reentry-position-threshold",
        type=int,
        default=1000,
        help="Maximum pixel distance from the last EXIT position to infer a REENTRY."
    )
    parser.add_argument(
        "--reentry-size-threshold",
        type=float,
        default=0.5,
        help="Minimum ratio of bbox area similarity between EXIT and REENTRY to infer the same visitor."
    )
    parser.add_argument(
        "--conversion-sessions-file",
        default=None,
        help="Path to conversion sessions JSON exported by run_conversion.py."
    )
    args = parser.parse_args()

    track_file = args.track_file or (
        f"data/outputs/tracking/{args.video_name}_tracks.json"
    )
    line_start = tuple(args.line_start) if args.line_start else None
    line_end = tuple(args.line_end) if args.line_end else None
    video_start = parse_video_start_time(args.video_start_time)

    main(
        track_file,
        video_name=args.video_name,
        store_id=args.store_id,
        camera_id=args.camera_id,
        video_start_time=video_start,
        line_start=line_start,
        line_end=line_end,
        reentry_time_window_seconds=args.reentry_window_seconds,
        reentry_position_threshold_pixels=args.reentry_position_threshold,
        reentry_size_threshold_ratio=args.reentry_size_threshold,
        conversion_sessions_file=args.conversion_sessions_file
    )
