"""Integration tests — validation fixtures with known projects."""


import pytest

from prod_ready.core.engine import assess
from prod_ready.core.models import Severity


@pytest.fixture
def well_prepared_project(tmp_path):
    """Create a project that should score well on file-based checks."""
    # Dockerfile
    (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")
    # Tests
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("def test_ok(): pass\n")
    # CI
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "workflows").mkdir()
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n")
    # README with health + rollback mentions
    (tmp_path / "README.md").write_text(
        "# My Service\n\n"
        "Health Check\nGET /health\n\n"
        "rollback\nRun `kubectl rollout undo`\n"
    )
    # Migrations
    (tmp_path / "migrations").mkdir()
    (tmp_path / "migrations" / "001_init.sql").write_text("CREATE TABLE test;\n")
    # pyproject.toml
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    # Deploy automation
    (tmp_path / "deploy").mkdir()
    (tmp_path / "deploy" / "k8s.yaml").write_text("apiVersion: v1\n")
    return tmp_path


@pytest.fixture
def minimal_project(tmp_path):
    """Create a minimal project that should score low."""
    (tmp_path / "README.md").write_text("# Minimal\n")
    return tmp_path


class TestValidationSuite:
    """Validation gate: framework must score known projects correctly."""

    def test_well_prepared_cicd_perfect(self, well_prepared_project):
        """Well-prepared project should get perfect CICD score."""
        result = assess("web_api", str(well_prepared_project))
        cicd = [c for c in result.categories if c.category.value == "ci-cd"][0]
        assert cicd.score == cicd.max_score, (
            f"Expected perfect CICD score, got {cicd.score}/{cicd.max_score}"
        )

    def test_minimal_scores_low(self, minimal_project):
        result = assess("web_api", str(minimal_project))
        assert result.overall_score < 5.0, (
            f"Expected score < 5 for minimal project, got {result.overall_score}"
        )

    def test_well_prepared_cicd_higher_than_minimal(self, tmp_path):
        """Well-prepared project should have higher CICD score than minimal."""
        # Create well-prepared project in one dir
        good_dir = tmp_path / "good"
        good_dir.mkdir()
        (good_dir / "Dockerfile").write_text("FROM python:3.11\n")
        (good_dir / "tests").mkdir()
        (good_dir / "tests" / "test_app.py").write_text("def test_ok(): pass\n")
        (good_dir / ".github").mkdir()
        (good_dir / ".github" / "workflows").mkdir()
        (good_dir / ".github" / "workflows" / "ci.yml").write_text("name: CI\n")
        (good_dir / "README.md").write_text("# Service\nhealth\nrollback\n")
        (good_dir / "migrations").mkdir()
        (good_dir / "pyproject.toml").write_text("[project]\n")
        (good_dir / "deploy").mkdir()

        # Create minimal project in another dir
        bad_dir = tmp_path / "bad"
        bad_dir.mkdir()
        (bad_dir / "README.md").write_text("# Minimal\n")

        good = assess("web_api", str(good_dir))
        bad = assess("web_api", str(bad_dir))
        good_cicd = [c for c in good.categories if c.category.value == "ci-cd"][0]
        bad_cicd = [c for c in bad.categories if c.category.value == "ci-cd"][0]
        assert good_cicd.score > bad_cicd.score

    def test_dockerfile_check_passes(self, well_prepared_project):
        result = assess("web_api", str(well_prepared_project))
        cicd = [c for c in result.categories if c.category.value == "ci-cd"][0]
        dockerfile_check = [c for c in cicd.checks if c.check_id == "CICD-003"]
        assert len(dockerfile_check) == 1
        assert dockerfile_check[0].severity == Severity.PASS

    def test_tests_dir_check_passes(self, well_prepared_project):
        result = assess("web_api", str(well_prepared_project))
        cicd = [c for c in result.categories if c.category.value == "ci-cd"][0]
        tests_check = [c for c in cicd.checks if c.check_id == "CICD-002"]
        assert len(tests_check) == 1
        assert tests_check[0].severity == Severity.PASS

    def test_health_check_detected(self, well_prepared_project):
        result = assess("web_api", str(well_prepared_project))
        obs = [c for c in result.categories if c.category.value == "observability"][0]
        health_check = [c for c in obs.checks if c.check_id == "OBS-002"]
        assert len(health_check) == 1
        assert health_check[0].severity == Severity.PASS

    def test_rollback_detected(self, well_prepared_project):
        result = assess("web_api", str(well_prepared_project))
        roll = [c for c in result.categories if c.category.value == "rollback"][0]
        rollback_check = [c for c in roll.checks if c.check_id == "ROLL-001"]
        assert len(rollback_check) == 1
        assert rollback_check[0].severity == Severity.PASS

    def test_migrations_detected(self, well_prepared_project):
        result = assess("web_api", str(well_prepared_project))
        data = [c for c in result.categories if c.category.value == "data-integrity"][0]
        mig_check = [c for c in data.checks if c.check_id == "DATA-001"]
        assert len(mig_check) == 1
        assert mig_check[0].severity == Severity.PASS
