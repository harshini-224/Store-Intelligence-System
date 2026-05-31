class DwellTimeTracker:

    def __init__(self):

        self.zone_time = {}

    def update(self, visitor_id, zone_name):

        key = (visitor_id, zone_name)

        if key not in self.zone_time:
            self.zone_time[key] = 0

        self.zone_time[key] += 1

    def get_results(self):

        results = []

        for key, frames in self.zone_time.items():

            visitor_id, zone_name = key

            results.append(
                {
                    "visitor_id": visitor_id,
                    "zone": zone_name,
                    "frames": frames
                }
            )

        return results