# Contributing to prod-ready

## Ways to Contribute

- **New app type**: Define a rubric and plugin for an unserved application type.
- **New checks**: Add checks to existing rubrics (new rubric version).
- **Remediation improvements**: Make gap guidance more actionable.
- **Validation fixtures**: Add known-project test fixtures.
- **Bug fixes**: Scoring errors, edge cases, output formatting.
- **Documentation**: This is a docs-first project. Improvements always welcome.

## Development Setup

```bash
git clone https://github.com/johnberey19/prod-ready.git
cd prod-ready
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
# All tests
pytest tests/ -v --cov=prod_ready --cov-report=term-missing

# Unit tests only
pytest tests/unit/ -v

# Integration tests (includes validation fixtures)
pytest tests/integration/ -v

# Specific app type
pytest tests/ -v -k web_api
```

### Linting

```bash
ruff check .
mypy prod_ready/
```

## Adding a New App Type

### 1. Define the Rubric

Create `rubrics/<type>/v1.0.yaml`:

```yaml
version: "1.0.0"
last_reviewed: "YYYY-MM-DD"
app_type: <type>
categories:
  - name: <category>
    weight: 0.20
    checks:
      - id: XXX-001
        description: "Human-readable check description"
        check_type: file_scan  # file_scan | command | prompt | config
        targets: []             # file patterns for file_scan
        assertion: ""           # check-specific
        severity: high          # critical | high | medium | low
        remediation: |
          Step-by-step fix instructions.
        docs_url: ""
```

**Rules:**
- IDs must be unique within the rubric (format: `CAT-NNN`).
- Every check must have remediation text.
- Weights across categories must sum to 1.0.
- Never modify an existing rubric version — create a new one.

### 2. Create the Plugin

Create `prod_ready/plugins/<type>/`:

```
prod_ready/plugins/<type>/
├── __init__.py       # Plugin class + registration
├── checks/           # Custom check implementations
│   └── ...
└── README.md         # App-type-specific documentation
```

The plugin must implement `AppTypePlugin` (see [Architecture](#architecture) in
the README).

### 3. Add Validation Fixtures

Create a known-project fixture in `tests/fixtures/<type>/`:

```
tests/fixtures/<type>/
├── project/          # Minimal project that triggers known gaps
│   └── ...
└── expected.json     # Expected scores per category
```

### 4. Register the Plugin

Add to `prod_ready/plugins/loader.py`:

```python
PLUGINS = [
    ...
    ("<type>", "prod_ready.plugins.<type>:Plugin"),
]
```

### 5. Submit the PR

Include:
- [ ] Rubric YAML (`rubrics/<type>/v1.0.yaml`)
- [ ] Plugin module (`prod_ready/plugins/<type>/`)
- [ ] Validation fixture (`tests/fixtures/<type>/`)
- [ ] Tests (unit + integration)
- [ ] Updated `prod-ready list-types` output in docs
- [ ] This checklist completed

## Adding a New Check to an Existing Rubric

1. **Bump the rubric version** (semver: minor for new checks, patch for
   remediation text changes).
2. **Add the check** to the new rubric version YAML.
3. **Update affected fixtures** — recalculate expected scores.
4. **Add a test** that verifies the check against the fixture.

Example PR title: `[rubric] web-api v1.2 -> v1.3: add SEC-008 (CSP headers)`

## Governance Requirements

The following changes require **council approval** before merging:

| Change Type                | Approval Required |
|----------------------------|-------------------|
| New app type               | Full council vote |
| Scoring algorithm changes  | CTO + CEO         |
| Rubric weight changes      | CTO               |
| Kill gate threshold change | CEO + COO         |
| Disclaimer text changes    | Legal + CEO       |
| Adding/removing categories | Full council vote |

Routine changes (remediation text, new checks within existing categories, bug
fixes, documentation) can be merged by any maintainer with 1 review.

## Code Standards

### TDD — Non-Negotiable

1. Write the failing test first.
2. Implement until it passes.
3. Refactor.
4. Never merge code without a corresponding test.

### Rubric Changes

- Append-only: new version, never modify old.
- Every check needs a test fixture that exercises it.
- Severity changes require recalculating all fixture expectations.

### Commits

Conventional commits:

```
feat(rubric): add SEC-008 (CSP headers) to web-api v1.3
fix(scorer): correct weight normalization when checks are excluded
docs: Update getting-started with CI/CD example
test(fixture): add data-pipeline low-score fixture
```

## Release Process

1. Bump version in `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Tag: `git tag v0.5.0`.
4. Build: `python -m build`.
5. Publish: `twine upload dist/*`.
6. Update Homebrew formula (if applicable).

## Questions?

Open an issue with the `question` label, or reach out in the project Discord.
