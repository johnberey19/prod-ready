"""Tests for rubric loader."""

import pytest

from prod_ready.core.rubric import (
    get_categories,
    get_category_weight,
    list_app_types,
    list_versions,
    load_rubric,
)


class TestListAppTypes:
    def test_returns_web_api(self):
        types = list_app_types()
        assert "web-api" in types


class TestListVersions:
    def test_web_api_has_v1(self):
        versions = list_versions("web_api")
        assert "v1.0" in versions


class TestLoadRubric:
    def test_load_web_api(self):
        rubric = load_rubric("web_api")
        assert rubric["app_type"] == "Web API"
        assert rubric["version"] == "1.0"
        assert "_resolved_version" in rubric

    def test_load_with_version(self):
        rubric = load_rubric("web_api", "v1.0")
        assert rubric["_resolved_version"] == "v1.0"

    def test_load_nonexistent_type_raises(self):
        with pytest.raises(FileNotFoundError):
            load_rubric("nonexistent")

    def test_load_nonexistent_version_raises(self):
        with pytest.raises(FileNotFoundError):
            load_rubric("web_api", "v99.0")


class TestGetCategories:
    def test_returns_all_categories(self):
        rubric = load_rubric("web_api")
        cats = get_categories(rubric)
        assert "observability" in cats
        assert "security" in cats
        assert "ci_cd" in cats
        assert "data_integrity" in cats
        assert "rollback" in cats


class TestGetCategoryWeight:
    def test_default_weight(self):
        rubric = load_rubric("web_api")
        # All categories have explicit weights
        w = get_category_weight(rubric, "observability")
        assert w == 0.25

    def test_missing_category_defaults(self):
        rubric = load_rubric("web_api")
        w = get_category_weight(rubric, "nonexistent")
        assert w == 1.0
