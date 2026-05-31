from __future__ import annotations

import re
import secrets
import shutil
import threading
import zipfile
from pathlib import Path

from fastapi import HTTPException

from app.core.config import STEM_SESSIONS_DIR
from app.models.audio import TransientStemItem


DEMUCS_STEM_NAMES = ("vocals", "drums", "bass", "other")
DERIVED_STEM_NAMES = ("piano", "strings")
STEM_NAMES = (*DEMUCS_STEM_NAMES, *DERIVED_STEM_NAMES)
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
_RETIRED_SESSIONS: set[tuple[str, str]] = set()


def create_session_id() -> str:
    return secrets.token_urlsafe(16)


def ensure_stem_sessions_dir() -> Path:
    STEM_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return STEM_SESSIONS_DIR


def create_session_dir(session_id: str | None = None) -> tuple[str, Path]:
    next_session_id = session_id or create_session_id()
    root = ensure_stem_sessions_dir().resolve()
    session_dir = (root / next_session_id).resolve()
    if not _is_safe_session_id(next_session_id) or not _is_within(session_dir, root):
        raise HTTPException(status_code=404, detail="Stem session not found.")
    session_dir.mkdir(parents=True, exist_ok=False)
    (session_dir / "stems").mkdir()
    return next_session_id, session_dir


def resolve_session_dir(session_id: str) -> Path:
    if not _is_safe_session_id(session_id):
        raise HTTPException(status_code=404, detail="Stem session not found.")
    root = ensure_stem_sessions_dir().resolve()
    if _retired_key(root, session_id) in _RETIRED_SESSIONS:
        raise HTTPException(status_code=404, detail="Stem session not found.")
    session_dir = (root / session_id).resolve()
    if not _is_within(session_dir, root) or not session_dir.exists() or not session_dir.is_dir():
        raise HTTPException(status_code=404, detail="Stem session not found.")
    return session_dir


def resolve_stem_path(session_id: str, stem_name: str) -> Path:
    if stem_name not in STEM_NAMES:
        raise HTTPException(status_code=404, detail="Stem not found.")
    session_dir = resolve_session_dir(session_id)
    stem_path = (session_dir / "stems" / f"{stem_name}.wav").resolve()
    if not _is_within(stem_path, session_dir) or not stem_path.exists() or not stem_path.is_file():
        raise HTTPException(status_code=404, detail="Stem not found.")
    return stem_path


def find_demucs_stem_files(output_root: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for stem_name in DEMUCS_STEM_NAMES:
        matches = sorted(output_root.rglob(f"{stem_name}.wav"))
        if matches:
            found[stem_name] = matches[0]
    return found


def normalize_demucs_output(output_root: Path, session_dir: Path, session_id: str) -> list[TransientStemItem]:
    stem_files = find_demucs_stem_files(output_root)
    missing = [stem_name for stem_name in DEMUCS_STEM_NAMES if stem_name not in stem_files]
    if missing:
        raise HTTPException(status_code=500, detail=f"Demucs output missing stems: {', '.join(missing)}")

    stems_dir = session_dir / "stems"
    stems_dir.mkdir(parents=True, exist_ok=True)
    items: list[TransientStemItem] = []
    for stem_name in DEMUCS_STEM_NAMES:
        target = stems_dir / f"{stem_name}.wav"
        shutil.copyfile(stem_files[stem_name], target)
        items.append(
            TransientStemItem(
                name=stem_name,
                status="complete",
                format="wav",
                mimeType="audio/wav",
                fileSizeBytes=target.stat().st_size,
                durationSec=None,
                streamUrl=f"/api/audio/stem-sessions/{session_id}/stems/{stem_name}",
                downloadUrl=f"/api/audio/stem-sessions/{session_id}/stems/{stem_name}/download",
            )
        )
    return items


def build_stems_zip(session_id: str) -> Path:
    session_dir = resolve_session_dir(session_id)
    archive = session_dir / "stems.zip"
    with zipfile.ZipFile(archive, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for stem_name in STEM_NAMES:
            try:
                stem_path = resolve_stem_path(session_id, stem_name)
            except HTTPException:
                continue
            zip_file.write(stem_path, arcname=f"{stem_name}.wav")
    return archive


def resolve_zip_path(session_id: str) -> Path:
    session_dir = resolve_session_dir(session_id)
    archive = session_dir / "stems.zip"
    if not archive.exists():
        archive = build_stems_zip(session_id)
    return archive


def clear_session(session_id: str) -> None:
    session_dir = resolve_session_dir(session_id)
    root = ensure_stem_sessions_dir().resolve()
    if not _is_within(session_dir, root):
        raise HTTPException(status_code=404, detail="Stem session not found.")
    _RETIRED_SESSIONS.add(_retired_key(root, session_id))
    threading.Thread(target=_delete_retired_session, args=(session_id, session_dir, root), daemon=True).start()


def _delete_retired_session(session_id: str, session_dir: Path, root: Path) -> None:
    retired_dir = (root / f".deleting-{session_id}-{secrets.token_urlsafe(6)}").resolve()
    if not _is_within(retired_dir, root):
        return
    try:
        session_dir.rename(retired_dir)
    except OSError:
        retired_dir = session_dir
    try:
        shutil.rmtree(retired_dir)
    except OSError:
        pass


def _is_safe_session_id(session_id: str) -> bool:
    return bool(session_id and SESSION_ID_PATTERN.fullmatch(session_id))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _retired_key(root: Path, session_id: str) -> tuple[str, str]:
    return str(root), session_id
