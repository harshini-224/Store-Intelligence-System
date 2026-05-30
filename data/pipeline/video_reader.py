from pathlib import Path
import cv2
import json


class VideoMetadataExtractor:
    """
    Extracts metadata from CCTV videos.
    """

    def __init__(self, video_path: str):
        self.video_path = Path(video_path)

    def extract(self):
        cap = cv2.VideoCapture(str(self.video_path))

        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        duration = frame_count / fps if fps > 0 else 0

        cap.release()

        return {
            "video_name": self.video_path.name,
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "duration_seconds": round(duration, 2),
            "resolution": f"{width}x{height}"
        }


def analyze_dataset(video_directory: str):
    video_directory = Path(video_directory)

    results = []

    for video_file in video_directory.glob("*.mp4"):
        metadata = VideoMetadataExtractor(video_file).extract()
        results.append(metadata)

    return results


if __name__ == "__main__":
    videos_folder = "data/raw"

    metadata = analyze_dataset(videos_folder)

    print(json.dumps(metadata, indent=4))

    output_dir = Path("outputs/metadata")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "video_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print(
        "\nMetadata saved to outputs/metadata/video_metadata.json"
    )
