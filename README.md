# CodeAlpha Blister Detection and Tracking

A focused real-time computer vision project developed for **Task 4 of the CodeAlpha Artificial Intelligence Internship**.

OpenCV captures frames from a local webcam, a fine-tuned YOLO model detects medicine blister packs, and BoT-SORT assigns tracking IDs and movement trails. The frontend is built with React and Material UI, while FastAPI manages the camera session and streams annotated frames to the interface.

## Features

- Real-time webcam capture using OpenCV.
- YOLO-based blister pack detection.
- BoT-SORT tracking with ReID and camera-motion compensation.
- Bounding boxes, labels, confidence scores, tracking IDs, and optional movement trails.
- Camera selection, mirrored preview, and an adjustable confidence threshold.
- Responsive English interface built with React and Material UI.
- Local operation without Docker, cloud inference, or API keys.
- Automated backend and frontend API-client tests.

## Assignment Coverage

| Requirement | Implementation |
| --- | --- |
| Real-time input | Local webcam opened with OpenCV |
| Object detection | Fine-tuned YOLO model in `backend/models/best.pt` |
| Frame processing | YOLO inference and OpenCV annotation |
| Object tracking | BoT-SORT with ReID |
| Visual output | Box, `blister` label, confidence, track ID, and optional trail |

The assignment allows webcam or video input. This implementation intentionally uses the webcam only to keep the project focused. It does not upload media, recognize medicine brands, or evaluate medicine quality.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, Material UI, Vite |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Computer Vision | Ultralytics YOLO, OpenCV |
| Tracking | BoT-SORT with ReID |
| Testing | pytest, FastAPI TestClient, Node test runner |

## Project Structure

```text
backend/
  config/botsort_blister.yaml
  models/best.pt
  models/model_info.json
  services/
  tests/
  main.py
  routes.py
  schemas.py
  settings.py
  requirements.txt
  requirements-dev.txt
frontend/
  src/components/
  src/hooks/
  src/services/
  src/App.jsx
  src/main.jsx
  src/theme.js
  index.html
  package.json
  package-lock.json
  vite.config.js
.gitignore
README.md
```

## Installation on Windows

Python 3.11 and a supported Node.js version are recommended.

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

## Running the Project

Run the backend and frontend in two separate PowerShell terminals.

### Terminal 1 — Backend

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\backend
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8003
```

Wait until the backend displays `Application startup complete`.

### Terminal 2 — Frontend

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\frontend
npm run dev
```

Open http://127.0.0.1:5173 in the browser.

Backend health endpoint: http://127.0.0.1:8003/health

## How to Use

1. Select the correct camera index. Start with **Camera 0**.
2. Keep **Mirror camera** enabled for a mirror-style preview.
3. Start with a detection threshold of **0.35**.
4. Enable **Show movement trail** if desired.
5. Click **Start tracking**.
6. Place one complete blister pack clearly inside the frame.
7. Move it slowly to demonstrate the box, track ID, and trail.
8. Click **Stop** to release the camera.

Increasing the threshold reduces weak detections but may lose the object during blur or fast movement. IDs are temporary and may change after a long occlusion or after leaving and re-entering the frame.

## Testing

### Backend

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q --run-model
```

### Frontend

```powershell
cd D:\AI_Projects\CodeAlpha_BlisterTracking\frontend
npm test
npm run build
```

## Detection and Tracking Pipeline

1. OpenCV captures a frame from the selected webcam.
2. The frame is resized and optionally mirrored.
3. YOLO detects visible blister packs.
4. The application keeps only the `blister` class.
5. BoT-SORT associates detections across consecutive frames.
6. Each confirmed track receives a temporary ID.
7. OpenCV draws the box, label, confidence, ID, and trail.
8. FastAPI streams the annotated frame to React using MJPEG.

## Model and Tracking Notes

- The application requests only model class `1: blister`.
- ReID supports track association but does not identify the medicine or brand.
- Track IDs and trail history are held temporarily in memory.
- Tracking cannot correct a missed or inaccurate detector result.
- Fast movement, reflections, blur, poor lighting, and occlusion can reduce stability.

## Privacy and Limitations

- Camera frames are processed locally and are not recorded or uploaded.
- The project does not capture audio.
- Detection confidence is not a medicine-quality or safety score.
- The backend is intended for local educational use and should not be exposed publicly.

## Repository

[GitHub — CodeAlpha BlisterTracking](https://github.com/NAGHAMAMER/CodeAlpha_BlisterTracking)

## Author

Developed by **Nagham Amer** as part of the CodeAlpha Artificial Intelligence Internship.
