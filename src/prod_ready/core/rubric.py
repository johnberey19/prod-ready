"""Rubric loader — reads versioned YAML rubric schemas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

RUBRIC_DIR = Path(__file__).parent.parent / "rubrics"


def list_app_types() -> list[str]:
    """Return available app types from the rubrics directory (hyphenated)."""
    if not RUBRIC_DIR.exists():
        return []
    return sorted(
        d.name.replace("_", "-")
        for d in RUBRIC_DIR.iterdir()
        if d.is_dir() and any(d.glob("*.yaml"))
    )


def list_versions(app_type: str) -> list[str]:
    """Return available rubric versions for an app type."""
    type_dir = RUBRIC_DIR / app_type
    if not type_dir.exists():
        return []
    return sorted(f.stem for f in type_dir.glob("*.yaml"))


def load_rubric(app_type: str, version: str | None = None) -> dict[str, Any]:
    """Load a rubric YAML for the given app type and optional version.

    If version is None, loads the highest versioned rubric available.
    Accepts both hyphenated (web-api) and underscored (web_api) app type names.
    """
    # Normalize: web-api -> web_api
    normalized = app_type.replace("-", "_")
    type_dir = RUBRIC_DIR / normalized
    if not type_dir.exists():
        raise FileNotFoundError(f"No rubric found for app type: {app_type}")

    if version:
        path = type_dir / f"{version}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Rubric {app_type} v{version} not found at {path}")
    else:
        # Pick the highest version (v1.0 < v1.1 < v2.0, etc.)
        versions = sorted(type_dir.glob("*.yaml"), key=lambda p: _version_key(p.stem))
        if not versions:
            raise FileNotFoundError(f"No rubric files found for app type: {app_type}")
        path = versions[-1]

    with open(path) as f:
        rubric = yaml.safe_load(f)

    rubric["_resolved_version"] = path.stem
    rubric["_resolved_path"] = str(path)
    return rubric


def _version_key(version_str: str) -> tuple[int, ...]:
    """Parse v1.0, v2.1.3 etc into a sortable tuple."""
    clean = version_str.lstrip("v")
    try:
        return tuple(int(p) for p in clean.split("."))
    except ValueError:
        return (0,)


def get_categories(rubric: dict[str, Any]) -> list[str]:
    """Extract category keys from a rubric dict."""
    reserved = {
        "version",
        "last_reviewed",
        "app_type",
        "weights",
        "metadata",
        "_resolved_version",
        "_resolved_path",
    }
    return [k for k in rubric if k not in reserved]


def get_category_weight(rubric: dict[str, Any], category: str) -> float:
    """Get the weight for a category (default 1.0)."""
    weights = rubric.get("weights", {})
    return float(weights.get(category, 1.0))
