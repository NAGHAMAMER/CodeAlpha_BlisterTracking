from pydantic import BaseModel, ConfigDict, Field


class CameraConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    confidence: float = Field(default=0.35, ge=0.25, le=0.80)
    camera_index: int = Field(default=0, ge=0, le=3)
    camera_fps: int = Field(default=10, ge=1, le=20)
    mirror: bool = True
    trails: bool = True
