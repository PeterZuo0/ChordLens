from pathlib import Path

from app.core.config import PROJECTS_DIR


def project_dir(project_id: str) -> Path:
    return PROJECTS_DIR / project_id


def ensure_project_dirs(project_id: str) -> Path:
    root = project_dir(project_id)
    for child in ("original", "stems", "analysis", "exports"):
        (root / child).mkdir(parents=True, exist_ok=True)
    return root
