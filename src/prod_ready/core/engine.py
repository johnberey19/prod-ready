"""Scoring engine — deterministic rubric-based assessment."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from prod_ready.core.models import (
    AssessmentResult,
    Category,
    CategoryScore,
    CheckResult,
    Severity,
)
from prod_ready.core.rubric import (
    get_categories,
    get_category_weight,
    load_rubric,
)


def assess(
    app_type: str,
    project_path: str,
    rubric_version: str | None = None,
    config: dict[str, Any] | None = None,
) -> AssessmentResult:
    """Run a production-readiness assessment.

    Args:
        app_type: Application type key (e.g. "web-api").
        project_path: Path to the project root to assess.
        rubric_version: Optional rubric version override.
        config: Optional config overrides (excluded checks, custom paths, etc.).

    Returns:
        AssessmentResult with per-category scores and gap details.
    """
    import datetime as dt

    config = config or {}
    rubric = load_rubric(app_type, rubric_version)
    resolved_version = rubric.get("_resolved_version", "unknown")
    exclude_checks = set(config.get("exclude_checks", []))
    custom_paths = config.get("paths", {})

    categories = _score_all_categories(
        rubric=rubric,
        project_path=project_path,
        exclude_checks=exclude_checks,
        custom_paths=custom_paths,
    )

    # Weighted overall score
    total_weight = sum(get_category_weight(rubric, cat.category.value) for cat in categories)
    overall = (
        sum(
            cat.score * get_category_weight(rubric, cat.category.value) / total_weight
            for cat in categories
        )
        if total_weight
        else 0.0
    )

    return AssessmentResult(
        app_type=app_type,
        project_path=str(project_path),
        overall_score=round(overall, 1),
        categories=categories,
        rubric_version=resolved_version,
        timestamp=dt.datetime.utcnow().isoformat() + "Z",
        metadata={
            "rubric_name": rubric.get("app_type", app_type),
            "last_reviewed": rubric.get("last_reviewed", "unknown"),
            "excluded_checks": sorted(exclude_checks),
        },
    )


def _score_all_categories(
    rubric: dict[str, Any],
    project_path: str,
    exclude_checks: set[str],
    custom_paths: dict[str, str],
) -> list[CategoryScore]:
    """Score each category in the rubric."""
    results: list[CategoryScore] = []
    for cat_key in get_categories(rubric):
        cat_data = rubric[cat_key]
        if not isinstance(cat_data, dict) or "checks" not in cat_data:
            continue
        category = _parse_category(cat_key)
        if category is None:
            continue
        checks, score, max_score = _evaluate_checks(
            cat_data["checks"],
            project_path,
            exclude_checks,
            custom_paths,
            cat_key,
        )
        results.append(
            CategoryScore(
                category=category,
                score=round(score, 1),
                max_score=max_score,
                checks=checks,
            )
        )
    return results


def _evaluate_checks(
    checks: list[dict[str, Any]],
    project_path: str,
    exclude_checks: set[str],
    custom_paths: dict[str, str],
    cat_key: str,
) -> tuple[list[CheckResult], float, float]:
    """Evaluate all checks in a category.

    Returns (check_results, earned_score, max_score).
    """
    results: list[CheckResult] = []
    earned = 0.0
    max_score = 0.0

    for check_def in checks:
        check_id = check_def.get("id", "UNKNOWN")
        if check_id in exclude_checks:
            continue

        weight = float(check_def.get("weight", 1.0))
        max_score += weight

        result = _run_single_check(check_def, project_path, custom_paths, cat_key)
        if result.severity == Severity.PASS:
            earned += weight
        results.append(result)

    return results, earned, max_score


def _run_single_check(
    check_def: dict[str, Any],
    project_path: str,
    custom_paths: dict[str, str],
    cat_key: str,
) -> CheckResult:
    """Run a single check against the project.

    The check definition must have a 'type' field:
      - 'file_exists': Checks if a file exists at the given 'path'.
      - 'file_contains': Checks if a file contains a given 'pattern'.
      - 'path_exists': Checks if any path in a list exists.
      - 'custom': Reserved for plugin checks (default fail with message).
    """
    check_id = check_def.get("id", "UNKNOWN")
    name = check_def.get("name", check_id)
    check_type = check_def.get("type", "file_exists")
    remediation = check_def.get("remediation")
    category = _parse_category(cat_key)
    if category is None:
        category = Category.OBSERVABILITY

    p = Path(project_path)

    if check_type == "file_exists":
        # Check a single file, with optional custom path override
        rel_path = custom_paths.get(check_id, check_def.get("path", ""))
        exists = (p / rel_path).exists() if rel_path else False
        if exists:
            return CheckResult(
                check_id=check_id,
                name=name,
                category=category,
                severity=Severity.PASS,
                score=100.0,
                message=f"{rel_path} found",
            )
        return CheckResult(
            check_id=check_id,
            name=name,
            category=category,
            severity=Severity.FAIL,
            score=0.0,
            message=f"{rel_path} not found",
            remediation=remediation,
        )

    elif check_type == "file_contains":
        rel_path = custom_paths.get(check_id, check_def.get("path", ""))
        pattern = check_def.get("pattern", "")
        target = p / rel_path
        if target.exists() and pattern.lower() in target.read_text().lower():
            return CheckResult(
                check_id=check_id,
                name=name,
                category=category,
                severity=Severity.PASS,
                score=100.0,
                message=f"{rel_path} contains required pattern",
            )
        return CheckResult(
            check_id=check_id,
            name=name,
            category=category,
            severity=Severity.FAIL,
            score=0.0,
            message=f"Pattern not found in {rel_path}",
            remediation=remediation,
        )

    elif check_type == "path_exists":
        paths = check_def.get("paths", [])
        for rel_path in paths:
            override = custom_paths.get(check_id)
            check_path = override if override else rel_path
            if (p / check_path).exists():
                return CheckResult(
                    check_id=check_id,
                    name=name,
                    category=category,
                    severity=Severity.PASS,
                    score=100.0,
                    message=f"Found: {check_path}",
                )
        return CheckResult(
            check_id=check_id,
            name=name,
            category=category,
            severity=Severity.FAIL,
            score=0.0,
            message=f"None of required paths found: {paths}",
            remediation=remediation,
        )

    elif check_type == "custom":
        return CheckResult(
            check_id=check_id,
            name=name,
            category=category,
            severity=Severity.WARN,
            score=50.0,
            message=f"Custom check '{check_id}' not yet implemented (plugin required)",
            remediation=remediation,
        )

    # Unknown check type
    return CheckResult(
        check_id=check_id,
        name=name,
        category=category,
        severity=Severity.WARN,
        score=0.0,
        message=f"Unknown check type: {check_type}",
    )


def _parse_category(key: str) -> Category | None:
    """Parse a category key string into a Category enum."""
    mapping = {
        "observability": Category.OBSERVABILITY,
        "security": Category.SECURITY,
        "ci_cd": Category.CICD,
        "ci-cd": Category.CICD,
        "cicd": Category.CICD,
        "data_integrity": Category.DATA_INTEGRITY,
        "data-integrity": Category.DATA_INTEGRITY,
        "rollback": Category.ROLLBACK,
    }
    return mapping.get(key.lower().replace(" ", "_"))
