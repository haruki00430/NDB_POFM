"""Project path and logger setup for monorepo or standalone NDB_POFM layout."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]


def resolve_repo_root() -> Path:
    """Return NDB_Research_Hub root when nested; otherwise the project root."""
    for candidate in (PROJECT_DIR.parent.parent, PROJECT_DIR.parent):
        if (candidate / "src" / "ndb_library").is_dir():
            return candidate
    return PROJECT_DIR


REPO_ROOT = resolve_repo_root()


def resolve_data_root() -> Path:
    """Prefer project-local 02_Data/raw; fall back to NDB_Research_Hub root."""
    if (PROJECT_DIR / "02_Data" / "raw").exists():
        return PROJECT_DIR
    if (REPO_ROOT / "02_Data" / "raw").exists():
        return REPO_ROOT
    return PROJECT_DIR


DATA_ROOT = resolve_data_root()


def setup_project_logger(name: str, log_file: Path) -> logging.Logger:
    """Use ndb_library logger when available; fall back to stdlib logging."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    try:
        from src.ndb_library.logger import setup_logger

        return setup_logger(name, log_file=str(log_file))
    except ImportError:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)
        return logger
