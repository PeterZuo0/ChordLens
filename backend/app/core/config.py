from pathlib import Path


APP_NAME = "ChordLens"
APP_VERSION = "0.1.0"

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
PROJECTS_DIR = DATA_DIR / "projects"
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a"}
