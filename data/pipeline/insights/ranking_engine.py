class RankingEngine:

    def top_zone(self, analytics):

        best_zone = None
        best_dwell = 0

        for zone, data in analytics.items():

            if data["total_dwell_time"] > best_dwell:

                best_dwell = data["total_dwell_time"]
                best_zone = zone

        return {
            "zone": best_zone,
            "dwell_time": best_dwell
        }