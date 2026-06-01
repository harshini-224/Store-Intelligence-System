import cv2
import numpy as np


class HeatmapGenerator:

    def __init__(self, width, height):

        self.heatmap = np.zeros(
            (height, width),
            dtype=np.float32
        )

    def update(
        self,
        center_x,
        center_y
    ):

        cv2.circle(
            self.heatmap,
            (center_x, center_y),
            25,
            1,
            -1
        )

    def generate_overlay(
        self,
        frame
    ):

        if frame is None:

            raise ValueError(
                "Frame is None."
            )

        normalized = cv2.normalize(
            self.heatmap,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        normalized = normalized.astype(
            np.uint8
        )

        colored_heatmap = cv2.applyColorMap(
            normalized,
            cv2.COLORMAP_JET
        )

        overlay = cv2.addWeighted(
            frame,
            0.6,
            colored_heatmap,
            0.4,
            0
        )

        return overlay