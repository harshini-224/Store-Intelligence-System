def iter_zone_metrics(analytics):
    for zone, data in analytics.items():
        if zone.startswith("_"):
            continue
        if not isinstance(data, dict):
            continue
        if "visitors" not in data or "total_dwell_time" not in data:
            continue
        yield zone, data
