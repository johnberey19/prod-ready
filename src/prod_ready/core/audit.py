"""Audit logging — records all assessments for compliance and trend tracking."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_AUDIT_DIR = Path.home() / ".prod-ready" / "audit"


def log_assessment(result, audit_dir: str | Path | None = None) -> Path:
    """Write an assessment result to the audit log.

    Returns the path to the written audit entry.
    """
    audit_dir = Path(audit_dir) if audit_dir else DEFAULT_AUDIT_DIR
    audit_dir.mkdir(parents=True, exist_ok=True)

    timestamp = result.timestamp.replace(":", "-").replace(".", "-")
    filename = f"{result.app_type}_{timestamp}.json"
    path = audit_dir / filename

    entry = {
        "app_type": result.app_type,
        "project_path": result.project_path,
        "overall_score": result.overall_score,
        "severity": result.severity.value,
        "rubric_version": result.rubric_version,
        "timestamp": result.timestamp,
        "total_gaps": result.total_gaps,
        "critical_gaps": result.critical_gaps,
        "high_gaps": result.high_gaps,
        "metadata": result.metadata,
    }

    path.write_text(json.dumps(entry, indent=2))
    return path


def list_audits(
    audit_dir: str | Path | None = None,
    app_type: str | None = None,
) -> list[dict[str, Any]]:
    """List audit log entries, optionally filtered by app type."""
    audit_dir = Path(audit_dir) if audit_dir else DEFAULT_AUDIT_DIR
    if not audit_dir.exists():
        return []

    entries = []
    for f in sorted(audit_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            if app_type is None or data.get("app_type") == app_type:
                data["_file"] = str(f)
                entries.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return entries
