from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from .planner import workflow_from_payload, workflow_to_payload

platformdirs_user_data_dir: Callable[..., str] | None
try:
    from platformdirs import user_data_dir as _platformdirs_user_data_dir
except ImportError:  # pragma: no cover - fallback only used without dependency installed
    platformdirs_user_data_dir = None
else:
    platformdirs_user_data_dir = _platformdirs_user_data_dir


def workflows_directory() -> Path:
    if platformdirs_user_data_dir is not None:
        base_dir = Path(
            platformdirs_user_data_dir(appname="SatisfactoryCalculator", appauthor="Burimon")
        )
    else:
        base_dir = Path.home() / "AppData" / "Local" / "Burimon" / "SatisfactoryCalculator"
    workflow_dir = base_dir / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    return workflow_dir


def list_workflows_payload() -> dict[str, object]:
    workflow_dir = workflows_directory()
    files = sorted(workflow_dir.glob("*.json"), key=lambda path: path.name.lower())
    return {
        "directory": str(workflow_dir),
        "files": [
            {
                "filename": path.name,
                "name": _workflow_name_from_file(path),
            }
            for path in files
        ],
    }


def load_workflow_payload(filename: str) -> dict[str, Any]:
    path = _workflow_path(filename)
    with path.open("r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)
    workflow = workflow_from_payload(payload)
    return workflow_to_payload(workflow)


def save_workflow_payload(payload: dict[str, object]) -> dict[str, object]:
    workflow = workflow_from_payload(payload)
    normalized_payload = workflow_to_payload(workflow)
    workflow_name = workflow.name.strip() or "Untitled Workflow"
    filename = f"{workflow_slug(workflow_name)}.json"
    path = workflows_directory() / filename
    with path.open("w", encoding="utf-8") as file_obj:
        json.dump(normalized_payload, file_obj, indent=2)
    return {
        "directory": str(workflows_directory()),
        "filename": filename,
        "name": workflow_name,
        "path": str(path),
    }


def workflow_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "untitled-workflow"


def _workflow_path(filename: str) -> Path:
    sanitized = Path(filename).name
    path = workflows_directory() / sanitized
    if not path.is_file():
        raise FileNotFoundError(f"Unknown workflow file: {filename}")
    return path


def _workflow_name_from_file(path: Path) -> str:
    try:
        payload = load_workflow_payload(path.name)
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        return path.stem
    raw_name = payload.get("name")
    if isinstance(raw_name, str) and raw_name.strip():
        return raw_name.strip()
    return path.stem
