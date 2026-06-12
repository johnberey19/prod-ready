"""Tests for scoring engine."""

import tempfile
from pathlib import Path

import pytest

from prod_ready.core.engine import assess
from prod_ready.core.models import Severity


class TestAssess:
    def test_assess_with_empty_project(self):
        """Assessment of a project with no files should score low."""
        with tempfile.TemporaryDirectory() as tmp:
            result = assess("web_api", tmp)
            assert result.app_type == "web_api"
            assert result.overall_score < 50.0
            assert result.severity == Severity.FAIL

    def test_assess_with_dockerfile(self):
        """Project with Dockerfile should score higher on CICD."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "Dockerfile").write_text("FROM python:3.11")
            result = assess("web_api", tmp)
            # Find the CICD category
            cicd = [c for c in result.categories if c.category.value == "ci-cd"]
            assert len(cicd) == 1
            # CICD-003 (Dockerfile check) should pass
            cicd_pass = [c for c in cicd[0].checks if c.severity == Severity.PASS]
            assert len(cicd_pass) >= 1

    def test_assess_with_tests_dir(self):
        """Project with tests/ should pass CICD-002."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "tests").mkdir()
            (Path(tmp) / "tests" / "test_dummy.py").write_text("def test_dummy(): pass")
            result = assess("web_api", tmp)
            cicd = [c for c in result.categories if c.category.value == "ci-cd"]
            assert len(cicd) == 1
            cicd_pass = [c for c in cicd[0].checks if c.severity == Severity.PASS]
            assert len(cicd_pass) >= 1

    def test_assess_exclude_checks(self):
        """Excluded checks should not appear in results."""
        with tempfile.TemporaryDirectory() as tmp:
            result = assess("web_api", tmp, config={"exclude_checks": ["OBS-001"]})
            all_check_ids = [
                c.check_id
                for cat in result.categories
                for c in cat.checks
            ]
            assert "OBS-001" not in all_check_ids

    def test_assess_returns_all_categories(self):
        """Assessment should return all 5 categories."""
        with tempfile.TemporaryDirectory() as tmp:
            result = assess("web_api", tmp)
            cat_values = {c.category for c in result.categories}
            from prod_ready.core.models import Category
            assert Category.OBSERVABILITY in cat_values
            assert Category.SECURITY in cat_values
            assert Category.CICD in cat_values
            assert Category.DATA_INTEGRITY in cat_values
            assert Category.ROLLBACK in cat_values

    def test_assess_rubric_version_in_metadata(self):
        """Result metadata should include rubric version."""
        with tempfile.TemporaryDirectory() as tmp:
            result = assess("web_api", tmp)
            assert result.rubric_version == "v1.0"
            assert result.metadata["rubric_name"] == "Web API"
