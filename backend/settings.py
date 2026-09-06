import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best.pt"
TRACKER_CONFIG_PATH = BASE_DIR / "config" / "botsort_blister.yaml"
DEVICE = os.getenv("TRACKING_DEVICE", "cpu")
ALLOWED_ORIGINS = {
    "http://127.0.0.1:5173", "http://localhost:5173",
    "http://127.0.0.1:4173", "http://localhost:4173",
    "http://127.0.0.1:8003", "http://localhost:8003",
}
