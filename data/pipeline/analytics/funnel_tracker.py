"""
Session-based retail funnel analytics.

Stages:
- ENTRY: visitor entered the store
- ZONE_VISIT: visitor entered at least one non-entry zone
- BILLING_QUEUE: visitor joined the billing queue
- PURCHASE: visitor converted through the conversion pipeline
"""

from typing import Any, Dict, Iterable, Optional, Set


ENTRY_ZONE_IDS = {"ENTRY", "ENTRANCE", "STORE_ENTRY", "ENTRY_ZONE"}


def _is_staff_event(event: Dict[str, Any]) -> bool:
    metadata = event.get("metadata") or {}
    return bool(metadata.get("is_staff", False))


def _visitor_id(event: Dict[str, Any]) -> Optional[int]:
    visitor_id = event.get("visitor_id")
    if visitor_id is None:
        return None
    return int(visitor_id)


class FunnelTracker:
    """Aggregates funnel stages from canonical visitor events."""

    def __init__(self, entry_zone_ids: Optional[Set[str]] = None):
        self.entry_zone_ids = entry_zone_ids or ENTRY_ZONE_IDS
        self.entry_visitors: Set[int] = set()
        self.zone_visit_visitors: Set[int] = set()
        self.billing_queue_visitors: Set[int] = set()
        self.purchase_visitors: Set[int] = set()
        self.staff_visitors: Set[int] = set()

    def add_event(self, event: Dict[str, Any]) -> None:
        visitor_id = _visitor_id(event)
        if visitor_id is None:
            return

        if _is_staff_event(event):
            self.staff_visitors.add(visitor_id)
            return
        if visitor_id in self.staff_visitors:
            return

        event_type = event.get("event_type") or event.get("event")
        zone_id = event.get("zone_id")

        if event_type == "ENTRY":
            self.entry_visitors.add(visitor_id)
        elif event_type == "ZONE_ENTER" and zone_id not in self.entry_zone_ids:
            self.zone_visit_visitors.add(visitor_id)
        elif event_type == "BILLING_QUEUE_JOIN":
            self.billing_queue_visitors.add(visitor_id)
        elif event_type in {"PURCHASE", "BILLING_QUEUE_CONVERT"}:
            self.purchase_visitors.add(visitor_id)

    def add_events(self, events: Iterable[Dict[str, Any]]) -> None:
        for event in events:
            self.add_event(event)

    def add_converted_visitors(self, visitor_ids: Iterable[int]) -> None:
        for visitor_id in visitor_ids:
            if visitor_id not in self.staff_visitors:
                self.purchase_visitors.add(int(visitor_id))

    @staticmethod
    def _rate(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 2)

    def get_metrics(self) -> Dict[str, Any]:
        entry_count = len(self.entry_visitors)
        zone_visit_count = len(self.zone_visit_visitors)
        billing_queue_count = len(self.billing_queue_visitors)
        purchase_count = len(self.purchase_visitors)

        return {
            "entry": entry_count,
            "zone_visit": zone_visit_count,
            "billing_queue": billing_queue_count,
            "purchase": purchase_count,
            "entry_count": entry_count,
            "zone_visit_count": zone_visit_count,
            "billing_queue_count": billing_queue_count,
            "purchase_count": purchase_count,
            "dropoffs": {
                "entry_to_zone": max(entry_count - zone_visit_count, 0),
                "zone_to_queue": max(zone_visit_count - billing_queue_count, 0),
                "queue_to_purchase": max(billing_queue_count - purchase_count, 0)
            },
            "rates": {
                "zone_visit_rate": self._rate(zone_visit_count, entry_count),
                "queue_rate": self._rate(billing_queue_count, entry_count),
                "purchase_rate": self._rate(purchase_count, entry_count),
                "entry_to_zone_rate": self._rate(zone_visit_count, entry_count),
                "zone_to_queue_rate": self._rate(
                    billing_queue_count,
                    zone_visit_count
                ),
                "queue_to_purchase_rate": self._rate(
                    purchase_count,
                    billing_queue_count
                )
            }
        }


def compute_funnel_metrics(
    events: Iterable[Dict[str, Any]],
    converted_visitor_ids: Optional[Iterable[int]] = None
) -> Dict[str, Any]:
    tracker = FunnelTracker()
    tracker.add_events(events)
    if converted_visitor_ids:
        tracker.add_converted_visitors(converted_visitor_ids)
    return tracker.get_metrics()
