def iter_zone_metrics(analytics):
    for zone, data in analytics.items():
        if zone.startswith("_"):
            continue
        if not isinstance(data, dict):
            continue
        if "visitors" not in data or "total_dwell_time" not in data:
            continue
        yield zone, data


class RankingEngine:

    def top_zone(self, analytics):

        best_zone = None
        best_dwell = 0

        for zone, data in iter_zone_metrics(analytics):

            if data["total_dwell_time"] > best_dwell:

                best_dwell = data["total_dwell_time"]
                best_zone = zone

        return {
            "zone": best_zone,
            "dwell_time": best_dwell
        }
