"""Tests for CLI commands."""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from prod_ready.cli.main import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLIAssess:
    def test_assess_help(self, runner):
        result = runner.invoke(main, ["assess", "--help"])
        assert result.exit_code == 0
        assert "--type" in result.output
        assert "--path" in result.output
        assert "--format" in result.output

    def test_assess_json_output(self, runner):
        with tempfile.TemporaryDirectory() as tmp:
            result = runner.invoke(main, ["assess", "--type", "web-api", "--path", tmp, "--format", "json"])
            assert result.exit_code == 0
            assert '"app_type": "web-api"' in result.output
            assert '"overall_score"' in result.output

    def test_assess_table_output(self, runner):
        with tempfile.TemporaryDirectory() as tmp:
            result = runner.invoke(main, ["assess", "--type", "web-api", "--path", tmp])
            assert result.exit_code == 0
            assert "prod-ready Assessment" in result.output
            assert "Gaps Found" in result.output

    def test_assess_yaml_output(self, runner):
        with tempfile.TemporaryDirectory() as tmp:
            result = runner.invoke(main, ["assess", "--type", "web-api", "--path", tmp, "--format", "yaml"])
            assert result.exit_code == 0
            assert "app_type: web-api" in result.output

    def test_assess_invalid_type(self, runner):
        with tempfile.TemporaryDirectory() as tmp:
            result = runner.invoke(main, ["assess", "--type", "invalid-type", "--path", tmp])
            assert result.exit_code != 0


class TestCLIListTypes:
    def test_list_types(self, runner):
        result = runner.invoke(main, ["list-types"])
        assert result.exit_code == 0
        assert "web-api" in result.output


class TestCLIInfo:
    def test_info(self, runner):
        result = runner.invoke(main, ["info", "--type", "web-api"])
        assert result.exit_code == 0
        assert "Web API" in result.output
        assert "Categories" in result.output


class TestCLIVersion:
    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "prod-ready" in result.output
