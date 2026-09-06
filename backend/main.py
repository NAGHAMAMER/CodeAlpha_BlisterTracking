from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from routes import router
from services.streaming import CameraStream


def load_detector():
    from services.detector import Detector
    return Detector()


def create_app(detector_factory=load_detector, camera_factory=None):
    @asynccontextmanager
    async def lifespan(app):
        app.state.detector = await run_in_threadpool(detector_factory)
        options = {"camera_factory": camera_factory} if camera_factory else {}
        app.state.camera = CameraStream(app.state.detector, **options)
        try:
            yield
        finally:
            await run_in_threadpool(app.state.camera.stop, None, True)

    app = FastAPI(
        title="CodeAlpha Blister Detection and Tracking",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"])
    app.include_router(router)
    return app


app = create_app()
