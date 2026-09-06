"""Optional real-weight loading and uniform-background smoke test."""
import numpy as np
from services.detector import Detector


def test_corrected_model_loads_and_rejects_uniform_frames():
    model = Detector()
    assert model.names[1] == 'blister'
    assert model.sha256 == 'd9d00c08345f3e666cfbb18fb9335323c976fca72e53aea01124f3e61e16ac04'
    for value in (0, 127, 255):
        frame = np.full((480, 640, 3), value, np.uint8)
        assert len(model.predict(frame, 0.10)) == 0
