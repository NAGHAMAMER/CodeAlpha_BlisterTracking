from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from schemas import CameraConfig
from settings import ALLOWED_ORIGINS

router = APIRouter()


def check_origin(request):
    origin = request.headers.get("origin")
    if origin not in ALLOWED_ORIGINS | {None}:
        raise HTTPException(403, "Untrusted browser origin.")
    if request.headers.get("sec-fetch-site") == "cross-site":
        raise HTTPException(403, "Cross-site requests are not allowed.")


@router.get("/health")
def health(request: Request):
    detector = request.app.state.detector
    return {
        "status": "ok",
        "object": "blister",
        "tracker": "BoT-SORT with ReID",
        "model_sha256": detector.sha256,
        "busy": request.app.state.camera.running,
    }


@router.post("/tracking/start")
def start_tracking(config: CameraConfig, request: Request):
    check_origin(request)
    try:
        return request.app.state.camera.start(config)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/tracking/status")
def tracking_status(
    request: Request,
    session_id: str = Query(pattern=r"^[0-9a-f]{32}$"),
):
    try:
        return request.app.state.camera.status(session_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/tracking/stop")
def stop_tracking(
    request: Request,
    session_id: str = Query(pattern=r"^[0-9a-f]{32}$"),
):
    check_origin(request)
    request.app.state.camera.stop(session_id)
    return {"status": "stop_requested"}


@router.get("/camera/stream")
def camera_stream(
    request: Request,
    session_id: str = Query(pattern=r"^[0-9a-f]{32}$"),
):
    check_origin(request)
    manager = request.app.state.camera
    try:
        manager.status(session_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

    return StreamingResponse(
        manager.mjpeg(session_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )
