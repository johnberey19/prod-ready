"""Core data models for prod-ready."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class Severity(enum.Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class Category(enum.Enum):
    OBSERVABILITY = "observability"
    SECURITY = "security"
    CICD = "ci-cd"
    DATA_INTEGRITY = "data-integrity"
    ROLLBACK = "rollback"


@dataclass
class CheckResult:
    check_id: str
    name: str
    category: Category
    severity: Severity
    score: float  # 0-100
    message: str
    remediation: str | None = None
    evidence: str | None = None


@dataclass
class CategoryScore:
    category: Category
    score: float  # 0-100
    max_score: float
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def severity(self) -> Severity:
        pct = self.score / self.max_score if self.max_score else 0
        if pct >= 0.8:
            return Severity.PASS
        if pct >= 0.5:
            return Severity.WARN
        return Severity.FAIL


@dataclass
class AssessmentResult:
    app_type: str
    project_path: str
    overall_score: float  # 0-100
    categories: list[CategoryScore]
    rubric_version: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def severity(self) -> Severity:
        if self.overall_score >= 80:
            return Severity.PASS
        if self.overall_score >= 50:
            return Severity.WARN
        return Severity.FAIL

    @property
    def critical_gaps(self) -> int:
        return sum(
            1
            for cat in self.categories
            for c in cat.checks
            if c.severity == Severity.FAIL
        )

    @property
    def high_gaps(self) -> int:
        return sum(
            1
            for cat in self.categories
            for c in cat.checks
            if c.severity == Severity.WARN
        )

    @property
    def total_gaps(self) -> int:
        return sum(
            1
            for cat in self.categories
            for c in cat.checks
            if c.severity != Severity.PASS
        )
