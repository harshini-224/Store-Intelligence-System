import json

from numpy import record


class AnalyticsReport:

    def generate(
        self,
        dwell_results,
        output_file
    ):

        zone_summary = {}

        for record in dwell_results:

            zone = record["zone"]

            if zone not in zone_summary:

                zone_summary[zone] = {
                    "visitors": 0,
                    "total_dwell_time": 0
                }

            if "visitor_ids" not in zone_summary[zone]:
                zone_summary[zone]["visitor_ids"] = set()

            zone_summary[zone]["visitor_ids"].add(
                record["visitor_id"]
            )

            zone_summary[zone][
                "total_dwell_time"
            ] += record[
                "dwell_time_seconds"
            ]

        for zone in zone_summary:

            zone_summary[zone]["visitors"] = len(
                zone_summary[zone]["visitor_ids"]
            )

            del zone_summary[zone]["visitor_ids"]

        with open(
            output_file,
            "w"
        ) as file:

            json.dump(
                zone_summary,
                file,
                indent=4
            )

        return zone_summary