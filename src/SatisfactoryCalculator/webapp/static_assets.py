from __future__ import annotations

import mimetypes
from importlib.resources import files
from pathlib import PurePosixPath

STATIC_ROOT = files(__package__).joinpath("static")


def _normalize_asset_path(path: str) -> PurePosixPath:
    candidate = PurePosixPath(path.lstrip("/"))
    if not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"Invalid static asset path: {path}")
    return candidate


def static_asset_bytes(path: str) -> bytes:
    asset_path = _normalize_asset_path(path)
    asset = STATIC_ROOT.joinpath(*asset_path.parts)
    if not asset.is_file():
        raise FileNotFoundError(path)
    return asset.read_bytes()


def static_asset_text(path: str) -> str:
    return static_asset_bytes(path).decode("utf-8")


def static_asset_content_type(path: str) -> str:
    asset_path = _normalize_asset_path(path)
    content_type, _ = mimetypes.guess_type(asset_path.name)
    return content_type or "application/octet-stream"
