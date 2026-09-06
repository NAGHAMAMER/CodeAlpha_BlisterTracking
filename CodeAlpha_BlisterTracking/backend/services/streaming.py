import base64
import logging
import sys
import threading
import time
import uuid

import cv2

from services.media import resize_frame
from services.session import TrackingSession

logger = logging.getLogger(__name__)


def open_camera(index):
    backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
    camera = cv2.VideoCapture(index, backend)
    if not camera.isOpened() and sys.platform == "win32":
        camera.release()
        camera = cv2.VideoCapture(index)
    if not camera.isOpened():
        camera.release()
        raise ValueError(
            "Could not open the camera. Close other camera apps, check Windows "
            "camera permissions, or select another camera."
        )

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return camera


class CameraStream:
    def __init__(self, detector, camera_factory=open_camera):
        self.detector = detector
        self.camera_factory = camera_factory
        self.condition = threading.Condition(threading.RLock())
        self.thread = None
        self.stop_event = threading.Event()
        self.session_id = None
        self.jpeg = None
        self.version = 0
        self.last_access = time.monotonic()
        self.info = self._idle_info()

    @staticmethod
    def _idle_info():
        return {"status": "idle", "frame": 0, "tracks": [], "error": None}

    @property
    def running(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, config):
        with self.condition:
            if self.running:
                raise ValueError("A camera session is already active.")

            self.session_id = uuid.uuid4().hex
            self.stop_event = threading.Event()
            self.jpeg = None
            self.version = 0
            self.last_access = time.monotonic()
            self.info = {
                "status": "connecting",
                "frame": 0,
                "tracks": [],
                "error": None,
            }
            self.thread = threading.Thread(
                target=self._capture_loop,
                args=(config,),
                daemon=True,
            )
            self.thread.start()
            return {
                "session_id": self.session_id,
                "stream_url": f"/api/camera/stream?session_id={self.session_id}",
            }

    def status(self, session_id):
        with self.condition:
            self._check_session(session_id)
            self.last_access = time.monotonic()
            return {
                **self.info,
                "session_id": self.session_id,
                "active": self.running,
            }

    def stop(self, session_id=None, wait=False):
        with self.condition:
            if session_id is not None and session_id != self.session_id:
                return
            self.stop_event.set()
            if self.running:
                self.info["status"] = "stopping"
            self.condition.notify_all()
            thread = self.thread
        if wait and thread is not None:
            thread.join(timeout=3)

    def _check_session(self, session_id):
        if session_id != self.session_id:
            raise ValueError("This camera session no longer exists.")

    def _capture_loop(self, config):
        camera = None
        final_status = "stopped"
        try:
            camera = self.camera_factory(config.camera_index)
            camera.set(cv2.CAP_PROP_FPS, config.camera_fps)
            session = TrackingSession(self.detector, config)
            interval = 1 / config.camera_fps

            with self.condition:
                self.info["status"] = "running"

            while not self.stop_event.is_set():
                started = time.monotonic()
                if started - self.last_access > 30:
                    break

                ok, frame = camera.read()
                if not ok or frame is None:
                    raise ValueError("The camera stopped delivering frames.")
                frame = resize_frame(frame)
                if config.mirror:
                    frame = cv2.flip(frame, 1)

                result = session.process(frame)
                jpeg = base64.b64decode(result.pop("image"))
                with self.condition:
                    self.jpeg = jpeg
                    self.version += 1
                    self.info.update(result)
                    self.info["status"] = "running"
                    self.condition.notify_all()

                self.stop_event.wait(max(0, interval - (time.monotonic() - started)))
        except Exception as exc:
            logger.exception("Camera processing failed")
            final_status = "error"
            with self.condition:
                self.info["error"] = (
                    str(exc)
                    if isinstance(exc, ValueError)
                    else "Processing failed. Check the backend terminal."
                )
        finally:
            if camera is not None:
                camera.release()
            with self.condition:
                self.info["status"] = final_status
                self.condition.notify_all()

    def mjpeg(self, session_id):
        last_version = -1
        while True:
            with self.condition:
                self._check_session(session_id)
                self.last_access = time.monotonic()
                if self.jpeg is not None and self.version != last_version:
                    jpeg = self.jpeg
                    last_version = self.version
                elif self.info["status"] in {"stopped", "error"}:
                    return
                else:
                    self.condition.wait(timeout=0.5)
                    continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: "
                + str(len(jpeg)).encode()
                + b"\r\n\r\n"
                + jpeg
                + b"\r\n"
            )
