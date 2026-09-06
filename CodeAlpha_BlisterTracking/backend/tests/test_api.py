import time

import numpy as np
import pytest
from fastapi.testclient import TestClient

from main import create_app


class FakeDetector:
    names = {1: "blister"}
    sha256 = "test-model"

    def __init__(self):
        self.frames = []
        self.resets = 0

    def start_tracking_session(self):
        self.resets += 1

    def track(self, frame, confidence):
        self.frames.append((frame.copy(), confidence))
        return [{
            "id": 1,
            "class_id": 1,
            "label": "blister",
            "confidence": 0.9,
            "box": [20, 20, 60, 60],
            "trail": [],
        }]


class FakeCamera:
    def __init__(self):
        self.released = False

    def set(self, *_):
        return True

    def read(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[:, :10] = 255
        return True, frame

    def release(self):
        self.released = True


def wait_for(client, session_id, predicate):
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        response = client.get(
            "/tracking/status",
            params={"session_id": session_id},
        )
        assert response.status_code == 200
        data = response.json()
        if predicate(data):
            return data
        time.sleep(0.02)
    raise AssertionError("Session did not reach the expected state.")


@pytest.fixture
def system():
    detector = FakeDetector()
    camera = FakeCamera()
    with TestClient(
        create_app(lambda: detector, lambda _: camera)
    ) as client:
        yield client, detector, camera


def test_health_is_blister_only(system):
    client, _, _ = system
    data = client.get("/health").json()
    assert data["object"] == "blister"
    assert data["tracker"] == "BoT-SORT with ReID"


def test_camera_session_processes_and_stops(system):
    client, detector, camera = system
    response = client.post("/tracking/start", json={"confidence": 0.35})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert "/api/camera/stream?" in response.json()["stream_url"]
    data = wait_for(client, session_id, lambda item: item["frame"] >= 2)
    assert data["tracks"][0]["id"] == 1
    assert data["tracks"][0]["label"] == "blister"
    assert detector.resets == 1

    assert client.post(
        "/tracking/stop", params={"session_id": session_id}
    ).status_code == 200
    wait_for(client, session_id, lambda item: not item["active"])
    assert camera.released


@pytest.mark.parametrize("mirror", [True, False])
def test_mirror_is_applied_before_detection(mirror):
    detector = FakeDetector()
    camera = FakeCamera()
    with TestClient(
        create_app(lambda: detector, lambda _: camera)
    ) as client:
        started = client.post(
            "/tracking/start", json={"mirror": mirror}
        ).json()
        wait_for(client, started["session_id"], lambda item: item["frame"] >= 1)
        frame = detector.frames[0][0]
        assert frame[:, -10:].mean() == (255 if mirror else 0)
        client.post(
            "/tracking/stop",
            params={"session_id": started["session_id"]},
        )


def test_second_session_is_rejected(system):
    client, _, _ = system
    started = client.post("/tracking/start", json={}).json()
    assert client.post("/tracking/start", json={}).status_code == 409
    client.post("/tracking/stop", params={"session_id": started["session_id"]})


@pytest.mark.parametrize(
    "payload",
    [
        {"confidence": 0.1},
        {"confidence": 0.9},
        {"camera_index": 4},
        {"camera_fps": 0},
        {"unexpected": True},
    ],
)
def test_invalid_configuration_is_rejected(system, payload):
    client, _, _ = system
    assert client.post("/tracking/start", json=payload).status_code == 422


def test_unknown_session_returns_not_found(system):
    client, _, _ = system
    unknown = "a" * 32
    assert client.get(
        "/tracking/status", params={"session_id": unknown}
    ).status_code == 404
    assert client.get(
        "/camera/stream", params={"session_id": unknown}
    ).status_code == 404


def test_cross_site_start_is_rejected(system):
    client, _, _ = system
    response = client.post(
        "/tracking/start",
        json={},
        headers={"origin": "https://example.com"},
    )
    assert response.status_code == 403
