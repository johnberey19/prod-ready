"""Output formatters for assessment results."""

from __future__ import annotations

import json
from typing import Any


def to_json(result, pretty: bool = True) -> str:
    """Serialize result to JSON string."""
    from prod_ready.cli.main import _result_to_dict
    data = _result_to_dict(result)
    indent = 2 if pretty else None
    return json.dumps(data, indent=indent)


def to_yaml(result) -> str:
    """Serialize result to YAML string."""
    import yaml
    from prod_ready.cli.main import _result_to_dict
    data = _result_to_dict(result)
    return yaml.dump(data, default_flow_style=False)


def to_dict(result) -> dict[str, Any]:
    """Convert result to a plain dict."""
    from prod_ready.cli.main import _result_to_dict
    return _result_to_dict(result)
