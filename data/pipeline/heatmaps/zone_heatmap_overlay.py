import cv2

from data.pipeline.analytics.zone_config import (
    FLOOR_A_ZONES,
    FLOOR_B_ZONES
)


class ZoneHeatmapOverlay:

    def draw_zones(
        self,
        image,
        zones
    ):

        for zone_name, zone in zones.items():

            x1 = zone["x1"]
            y1 = zone["y1"]
            x2 = zone["x2"]
            y2 = zone["y2"]

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (255, 255, 255),
                2
            )

            cv2.putText(
                image,
                zone_name,
                (x1 + 10, y1 + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        return image