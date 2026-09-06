import base64
from collections import defaultdict, deque

import cv2

from services.media import annotate


class TrackingSession:
    def __init__(self, detector, config):
        self.detector = detector
        self.config = config
        self.frame_index = 0
        self.output_size = None
        self.trails = defaultdict(lambda: deque(maxlen=40))
        detector.start_tracking_session()

    def process(self, frame):
        height, width = frame.shape[:2]
        size = (width, height)
        if self.output_size is None:
            self.output_size = size
        elif self.output_size != size:
            raise ValueError("Camera dimensions changed. Restart the session.")

        tracks = self.detector.track(frame, self.config.confidence)
        self.frame_index += 1

        for track in tracks:
            track["box"] = [
                max(0.0, min(float(value), width - 1 if index % 2 == 0 else height - 1))
                for index, value in enumerate(track["box"])
            ]
            x1, y1, x2, y2 = track["box"]
            center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            self.trails[track["id"]].append(center)
            track["trail"] = list(self.trails[track["id"]])

        annotated = annotate(frame, tracks, self.config.trails)
        encoded, jpeg = cv2.imencode(
            ".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 84]
        )
        if not encoded:
            raise RuntimeError("Could not encode the processed camera frame.")

        return {
            "frame": self.frame_index,
            "image": base64.b64encode(jpeg).decode("ascii"),
            "tracks": tracks,
        }
