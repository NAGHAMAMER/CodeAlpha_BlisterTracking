import hashlib
from threading import Lock

import numpy as np

from settings import DEVICE, MODEL_PATH, TRACKER_CONFIG_PATH


class Detector:
    def __init__(self):
        from ultralytics import YOLO
        if not MODEL_PATH.is_file():
            raise RuntimeError("Missing backend/models/best.pt. Restore the supplied weights.")
        self.model = YOLO(str(MODEL_PATH), task="detect")
        self.names = {int(key): value for key, value in self.model.names.items()}
        if self.names.get(1) != "blister":
            raise RuntimeError(f"Expected class 1 to be blister, found {self.names}.")
        self.lock = Lock()
        self.sha256 = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()
        warmup = np.tile(np.linspace(0, 255, 640, dtype=np.uint8), (384, 1))
        self.predict(np.repeat(warmup[:, :, None], 3, axis=2), 0.35)

    def start_tracking_session(self):
        """Give every camera session a fresh BoT-SORT identity space."""
        with self.lock:
            for tracker in getattr(self.model.predictor, "trackers", []):
                tracker.reset()

    def track(self, frame, confidence):
        """Run YOLO detection and persistent BoT-SORT association once."""
        with self.lock:
            result = self.model.track(
                frame,
                persist=True,
                tracker=str(TRACKER_CONFIG_PATH),
                conf=confidence,
                iou=0.35,
                imgsz=640,
                classes=[1],
                max_det=30,
                device=DEVICE,
                verbose=False,
            )[0]
        if result.boxes is None or result.boxes.id is None:
            return []
        tracks = []
        for box, identity in zip(result.boxes, result.boxes.id):
            class_id = int(box.cls[0].item())
            tracks.append({
                "id": int(identity.item()),
                "class_id": class_id,
                "label": "blister",
                "confidence": float(box.conf[0].item()),
                "box": box.xyxy[0].cpu().tolist(),
                "trail": [],
            })
        return tracks

    def predict(self, frame, confidence):
        with self.lock:
            result = self.model.predict(frame, conf=confidence, classes=[1], iou=0.5,
                                        imgsz=640, max_det=100, device=DEVICE, verbose=False)[0]
        if result.boxes is None:
            return np.empty((0, 6))
        return result.boxes.data.cpu().numpy()[:, :6]
