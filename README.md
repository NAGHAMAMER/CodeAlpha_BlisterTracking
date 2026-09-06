# CodeAlpha Blister Detection and Tracking

A focused real-time computer-vision project for CodeAlpha Task 4. OpenCV captures a local webcam, a corrected YOLO checkpoint detects complete medicine blister packs, and BoT-SORT assigns track IDs and movement trails. The interface is built with React and Material UI; FastAPI provides local HTTP control and MJPEG streaming.

## Assignment coverage

| Requirement | Implementation |
| --- | --- |
| Real-time input | Local webcam opened by OpenCV |
| Pre-trained detector | Fine-tuned YOLO checkpoint in `backend/models/best.pt` |
| Frame processing and boxes | YOLO inference and OpenCV annotation |
| Object tracking | BoT-SORT with ReID and camera-motion compensation |
| Labels and IDs | `blister`, confidence, track ID and optional movement trail |

The assignment accepts a webcam or a video file, so this final version intentionally uses the webcam only. It does not accept media uploads, identify medicine brands, or assess medicine quality.

## Project structure

```text
backend/
  config/botsort_blister.yaml
  models/best.pt
  models/model_info.json
  services/
    detector.py
    media.py
    session.py
    streaming.py
  tests/
  main.py
  routes.py
  schemas.py
  settings.py
  requirements.txt
  requirements-dev.txt
frontend/
  src/
    components/
    hooks/
    services/
    App.jsx
    main.jsx
    theme.js
  index.html
  package.json
  package-lock.json
  vite.config.js
run.bat
```

## Installation on Windows

Python 3.11 is recommended.

### Backend

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

### Frontend

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\frontend
npm ci
```

## Run

Double-click `run.bat`, wait for both terminals, then open:

http://127.0.0.1:5173

Manual commands:

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\backend
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8003
```

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\frontend
npm run dev
```

## Use

1. Select the correct camera.
2. Keep `Mirror camera` enabled for a mirror-style preview.
3. Start with detection threshold `0.35`.
4. Enable `Show movement trail`.
5. Click `Start tracking`, then move one complete blister pack slowly.
6. Click `Stop` to release the camera.

Higher confidence reduces weak detections but can lose the object during blur. A track ID is temporary: after a long occlusion or leaving and re-entering the frame, the object can receive a new ID. Confidence is the detector score, not a medicine-safety score.

## Test

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q --run-model
```

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\frontend
npm test
npm run build
```

The supplied checkpoint is restricted by the application to model class `1: blister`. Other classes may still exist inside the immutable checkpoint metadata, but the application never requests or displays them.

## Local-only operation

Camera frames are processed locally and are not recorded or uploaded. Run one Uvicorn worker and do not expose port 8003 publicly. Close Zoom, Teams, or other camera applications if OpenCV cannot open the device.
