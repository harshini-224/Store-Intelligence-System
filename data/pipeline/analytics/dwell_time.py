class DwellTimeTracker:

    def __init__(self, fps):

        self.fps = fps
        self.zone_frames = {}

    def update(self, visitor_id, zone_name):

        if zone_name == "UNKNOWN":
            return

        key = (visitor_id, zone_name)

        if key not in self.zone_frames:
            self.zone_frames[key] = 0

        self.zone_frames[key] += 1

    def get_results(self):

        results = []

        for (visitor_id, zone_name), frames in self.zone_frames.items():

            dwell_seconds = round(
                frames / self.fps,
                2
            )

            results.append(
                {
                    "visitor_id": visitor_id,
                    "zone": zone_name,
                    "frames": frames,
                    "dwell_time_seconds": dwell_seconds
                }
            )

        return results