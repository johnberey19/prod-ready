"""Plugin interface contract.

App type modules must implement register(app) which adds rubrics
and optionally custom check handlers.
"""

from __future__ import annotations

from typing import Any, Protocol

from prod_ready.core.models import CheckResult


class CheckHandler(Protocol):
    """Protocol for custom check handlers."""

    def __call__(
        self,
        check_def: dict[str, Any],
        project_path: str,
        custom_paths: dict[str, str],
    ) -> CheckResult: ...


class AppTypePlugin(Protocol):
    """Protocol for app type plugins."""

    @property
    def app_type(self) -> str:
        """Return the app type identifier."""
        ...

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        ...

    def get_rubric_path(self) -> str:
        """Return the path to the rubric YAML directory."""
        ...

    def get_custom_checks(self) -> dict[str, CheckHandler]:
        """Return custom check handler registry."""
        ...


def discover_plugins() -> list[str]:
    """Return list of built-in app type keys with rubrics."""
    from prod_ready.core.rubric import list_app_types

    return list_app_types()
