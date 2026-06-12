"""Tests for prod-ready core models."""

from prod_ready.core.models import (
    AssessmentResult,
    Category,
    CategoryScore,
    CheckResult,
    Severity,
)


class TestSeverity:
    def test_pass_threshold(self):
        assert Severity.PASS.value == "pass"

    def test_warn_threshold(self):
        assert Severity.WARN.value == "warn"

    def test_fail_threshold(self):
        assert Severity.FAIL.value == "fail"


class TestCategoryScore:
    def test_pass_severity(self):
        cs = CategoryScore(
            category=Category.OBSERVABILITY,
            score=85.0,
            max_score=100.0,
        )
        assert cs.severity == Severity.PASS

    def test_warn_severity(self):
        cs = CategoryScore(
            category=Category.SECURITY,
            score=60.0,
            max_score=100.0,
        )
        assert cs.severity == Severity.WARN

    def test_fail_severity(self):
        cs = CategoryScore(
            category=Category.CICD,
            score=30.0,
            max_score=100.0,
        )
        assert cs.severity == Severity.FAIL

    def test_boundary_pass_warn(self):
        cs = CategoryScore(
            category=Category.ROLLBACK,
            score=79.9,
            max_score=100.0,
        )
        assert cs.severity == Severity.WARN

    def test_boundary_warn_fail(self):
        cs = CategoryScore(
            category=Category.DATA_INTEGRITY,
            score=49.9,
            max_score=100.0,
        )
        assert cs.severity == Severity.FAIL


class TestAssessmentResult:
    def test_overall_pass(self):
        result = AssessmentResult(
            app_type="web-api",
            project_path="/tmp/test",
            overall_score=85.0,
            categories=[],
            rubric_version="1.0",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert result.severity == Severity.PASS

    def test_overall_warn(self):
        result = AssessmentResult(
            app_type="web-api",
            project_path="/tmp/test",
            overall_score=65.0,
            categories=[],
            rubric_version="1.0",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert result.severity == Severity.WARN

    def test_overall_fail(self):
        result = AssessmentResult(
            app_type="web-api",
            project_path="/tmp/test",
            overall_score=35.0,
            categories=[],
            rubric_version="1.0",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert result.severity == Severity.FAIL

    def test_gap_counts(self):
        checks = [
            CheckResult("C1", "Check 1", Category.OBSERVABILITY, Severity.PASS, 100.0, "ok"),
            CheckResult("C2", "Check 2", Category.OBSERVABILITY, Severity.WARN, 50.0, "warn"),
            CheckResult("C3", "Check 3", Category.SECURITY, Severity.FAIL, 0.0, "fail"),
            CheckResult("C4", "Check 4", Category.SECURITY, Severity.FAIL, 0.0, "fail"),
        ]
        cat_obs = CategoryScore(Category.OBSERVABILITY, 75.0, 100.0, checks[:2])
        cat_sec = CategoryScore(Category.SECURITY, 0.0, 100.0, checks[2:])
        result = AssessmentResult(
            app_type="web-api",
            project_path="/tmp/test",
            overall_score=37.5,
            categories=[cat_obs, cat_sec],
            rubric_version="1.0",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert result.critical_gaps == 2
        assert result.high_gaps == 1
        assert result.total_gaps == 3
