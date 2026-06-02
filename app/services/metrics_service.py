import json
from pathlib import Path
from typing import Dict, Any


def load_floor_metrics() -> Dict[str, Any]:
    """
    Load analytics metrics including conversion data.
    
    Returns:
        Dictionary with floor metrics and conversion statistics
    """
    result = {}

    files = [
        "data/outputs/analytics/floor_a_summary.json",
        "data/outputs/analytics/floor_b_summary.json"
    ]

    for file in files:

        try:

            with open(file) as f:

                result[file] = json.load(f)

        except:

            result[file] = {}

    queue_metrics = load_queue_metrics()
    if queue_metrics:
        result["_queue_metrics"] = queue_metrics.get("_aggregate", {})

    return result


def load_conversion_metrics() -> Dict[str, Any]:
    """
    Load conversion metrics from analytics summaries.
    
    Returns:
        Dictionary with conversion stats (conversion_rate, converted_visitors, etc.)
    """
    conversion_data = {}

    files = [
        "data/outputs/analytics/floor_a_summary.json",
        "data/outputs/analytics/floor_b_summary.json"
    ]

    for file in files:
        try:
            path = Path(file)
            if not path.exists():
                continue

            with open(path) as f:
                data = json.load(f)

            # Extract conversion metrics if present
            if "_conversion_metrics" in data:
                floor_name = Path(file).stem.replace("_summary", "")
                conversion_data[floor_name] = data["_conversion_metrics"]

        except Exception as e:
            print(f"Warning: Could not load conversion metrics from {file}: {e}")

    # Calculate aggregate metrics
    if conversion_data:
        total_visitors = sum(
            stats.get("total_visitors", 0)
            for stats in conversion_data.values()
        )
        total_converted = sum(
            stats.get("converted_visitors", 0)
            for stats in conversion_data.values()
        )

        aggregate_conversion_rate = 0.0
        if total_visitors > 0:
            aggregate_conversion_rate = (
                (total_converted / total_visitors) * 100
            )

        conversion_data["_aggregate"] = {
            "total_visitors": total_visitors,
            "total_converted_visitors": total_converted,
            "aggregate_conversion_rate": round(aggregate_conversion_rate, 2)
        }

    return conversion_data


def get_conversion_summary() -> Dict[str, Any]:
    """
    Get a summary view of conversion metrics.
    
    Returns:
        Dictionary with overall conversion performance
    """
    conversion_metrics = load_conversion_metrics()

    if not conversion_metrics:
        return {
            "status": "no_data",
            "message": "No conversion data available"
        }

    aggregate = conversion_metrics.get("_aggregate", {})

    return {
        "status": "success",
        "summary": {
            "total_visitors": aggregate.get("total_visitors", 0),
            "converted_visitors": aggregate.get("total_converted_visitors", 0),
            "conversion_rate_percent": aggregate.get(
                "aggregate_conversion_rate", 0
            )
        },
        "by_floor": {
            floor: {
                "total_visitors": stats.get("total_visitors", 0),
                "converted_visitors": stats.get("converted_visitors", 0),
                "conversion_rate_percent": stats.get("conversion_rate", 0),
                "billing_zone_visitors": stats.get("billing_zone_visitors", 0)
            }
            for floor, stats in conversion_metrics.items()
            if floor != "_aggregate"
        }
    }


def load_queue_metrics() -> Dict[str, Any]:
    """
    Load queue metrics from analytics summaries.
    
    Returns:
        Dictionary with queue stats (queue_joins, queue_abandons, abandonment_rate, etc.)
    """
    queue_data = {}

    files = [
        "data/outputs/analytics/floor_a_summary.json",
        "data/outputs/analytics/floor_b_summary.json"
    ]

    for file in files:
        try:
            path = Path(file)
            if not path.exists():
                continue

            with open(path) as f:
                data = json.load(f)

            # Extract queue metrics if present
            if "_queue_metrics" in data:
                floor_name = Path(file).stem.replace("_summary", "")
                queue_data[floor_name] = data["_queue_metrics"]

        except Exception as e:
            print(f"Warning: Could not load queue metrics from {file}: {e}")

    # Calculate aggregate metrics
    if queue_data:
        total_joins = sum(
            stats.get("queue_joins", 0)
            for stats in queue_data.values()
        )
        total_abandons = sum(
            stats.get("queue_abandons", 0)
            for stats in queue_data.values()
        )
        total_conversions = sum(
            stats.get("queue_conversions", 0)
            for stats in queue_data.values()
        )
        total_unique_visitors = sum(
            stats.get("unique_queue_visitors", 0)
            for stats in queue_data.values()
        )
        floor_count = len(queue_data)
        average_queue_depth = 0.0
        if floor_count > 0:
            average_queue_depth = round(
                sum(
                    stats.get("average_queue_depth", 0)
                    for stats in queue_data.values()
                ) / floor_count,
                2
            )
        max_queue_depth = max(
            (
                stats.get("max_queue_depth", 0)
                for stats in queue_data.values()
            ),
            default=0
        )
        average_queue_wait_time = 0.0
        if floor_count > 0:
            average_queue_wait_time = round(
                sum(
                    stats.get(
                        "average_queue_wait_time",
                        stats.get("average_wait_time_seconds", 0)
                    )
                    for stats in queue_data.values()
                ) / floor_count,
                2
            )
        max_queue_wait_time = max(
            (
                stats.get(
                    "max_queue_wait_time",
                    stats.get("max_wait_time_seconds", 0)
                )
                for stats in queue_data.values()
            ),
            default=0
        )

        aggregate_abandonment_rate = 0.0
        if total_joins > 0:
            aggregate_abandonment_rate = round(
                total_abandons / total_joins, 2
            )

        queue_data["_aggregate"] = {
            "queue_joins": total_joins,
            "queue_abandons": total_abandons,
            "queue_conversions": total_conversions,
            "unique_queue_visitors": total_unique_visitors,
            "abandonment_rate": aggregate_abandonment_rate,
            "abandonment_rate_percent": round(aggregate_abandonment_rate * 100, 2),
            "average_queue_depth": average_queue_depth,
            "max_queue_depth": max_queue_depth,
            "average_queue_wait_time": average_queue_wait_time,
            "max_queue_wait_time": max_queue_wait_time
        }

    return queue_data


def load_funnel_metrics() -> Dict[str, Any]:
    """Load session funnel metrics from analytics summaries."""
    funnel_data = {}

    files = [
        "data/outputs/analytics/floor_a_summary.json",
        "data/outputs/analytics/floor_b_summary.json"
    ]

    for file in files:
        try:
            path = Path(file)
            if not path.exists():
                continue

            with open(path) as f:
                data = json.load(f)

            if "_funnel_metrics" in data:
                floor_name = path.stem.replace("_summary", "")
                funnel_data[floor_name] = data["_funnel_metrics"]

        except Exception as e:
            print(f"Warning: Could not load funnel metrics from {file}: {e}")

    if not funnel_data:
        return {
            "entry": 0,
            "zone_visit": 0,
            "billing_queue": 0,
            "purchase": 0,
            "dropoffs": {
                "entry_to_zone": 0,
                "zone_to_queue": 0,
                "queue_to_purchase": 0
            },
            "rates": {
                "zone_visit_rate": 0.0,
                "queue_rate": 0.0,
                "purchase_rate": 0.0,
                "entry_to_zone_rate": 0.0,
                "zone_to_queue_rate": 0.0,
                "queue_to_purchase_rate": 0.0
            }
        }

    entry = sum(stats.get("entry", stats.get("entry_count", 0)) for stats in funnel_data.values())
    zone_visit = sum(stats.get("zone_visit", stats.get("zone_visit_count", 0)) for stats in funnel_data.values())
    billing_queue = sum(stats.get("billing_queue", stats.get("billing_queue_count", 0)) for stats in funnel_data.values())
    purchase = sum(stats.get("purchase", stats.get("purchase_count", 0)) for stats in funnel_data.values())

    def rate(value: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round(value / denominator, 2)

    return {
        "entry": entry,
        "zone_visit": zone_visit,
        "billing_queue": billing_queue,
        "purchase": purchase,
        "dropoffs": {
            "entry_to_zone": max(entry - zone_visit, 0),
            "zone_to_queue": max(zone_visit - billing_queue, 0),
            "queue_to_purchase": max(billing_queue - purchase, 0)
        },
        "rates": {
            "zone_visit_rate": rate(zone_visit, entry),
            "queue_rate": rate(billing_queue, entry),
            "purchase_rate": rate(purchase, entry),
            "entry_to_zone_rate": rate(zone_visit, entry),
            "zone_to_queue_rate": rate(billing_queue, zone_visit),
            "queue_to_purchase_rate": rate(purchase, billing_queue)
        },
        "by_floor": funnel_data
    }


def get_queue_summary() -> Dict[str, Any]:
    """
    Get a summary view of queue metrics.
    
    Returns:
        Dictionary with overall queue performance
    """
    queue_metrics = load_queue_metrics()

    if not queue_metrics:
        return {
            "status": "no_data",
            "message": "No queue data available"
        }

    aggregate = queue_metrics.get("_aggregate", {})

    return {
        "status": "success",
        "summary": {
            "queue_joins": aggregate.get("queue_joins", 0),
            "queue_abandons": aggregate.get("queue_abandons", 0),
            "queue_conversions": aggregate.get("queue_conversions", 0),
            "unique_queue_visitors": aggregate.get("unique_queue_visitors", 0),
            "abandonment_rate": aggregate.get("abandonment_rate", 0),
            "abandonment_rate_percent": aggregate.get("abandonment_rate_percent", 0),
            "average_queue_depth": aggregate.get("average_queue_depth", 0),
            "max_queue_depth": aggregate.get("max_queue_depth", 0)
        },
        "by_floor": {
            floor: {
                "queue_joins": stats.get("queue_joins", 0),
                "queue_abandons": stats.get("queue_abandons", 0),
                "queue_conversions": stats.get("queue_conversions", 0),
                "unique_queue_visitors": stats.get("unique_queue_visitors", 0),
                "abandonment_rate": stats.get("abandonment_rate", 0),
                "abandonment_rate_percent": stats.get("abandonment_rate_percent", 0),
                "average_queue_depth": stats.get("average_queue_depth", 0),
                "max_queue_depth": stats.get("max_queue_depth", 0),
                "average_queue_wait_time": stats.get(
                    "average_queue_wait_time",
                    stats.get("average_wait_time_seconds", 0)
                ),
                "max_queue_wait_time": stats.get(
                    "max_queue_wait_time",
                    stats.get("max_wait_time_seconds", 0)
                )
            }
            for floor, stats in queue_metrics.items()
            if floor != "_aggregate"
        }
    }
