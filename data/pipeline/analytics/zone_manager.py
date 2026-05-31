class ZoneManager:

    def __init__(self, zones):

        self.zones = zones

    def get_zone(self, center_x, center_y):

        for zone_name, zone in self.zones.items():

            if (
                zone["x1"] <= center_x <= zone["x2"]
                and
                zone["y1"] <= center_y <= zone["y2"]
            ):

                return zone_name

        return "UNKNOWN"