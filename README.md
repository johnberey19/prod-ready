# prod-ready — Dynamic Production-Readiness Assessment Framework

`prod-ready` is a CLI tool that assesses the production-readiness of applications
using deterministic scoring rubrics. It produces structured gap reports with
severity tiers and actionable remediation guidance.

**This is an assessment tool, not a certification engine.** It surfaces gaps and
recommends fixes — the decisions are yours.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [How It Works](#how-it-works)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [CLI Reference](#cli-reference)
6. [Output Format](#output-format)
7. [App Types](#app-types)
8. [Scoring System](#scoring-system)
9. [Rubric Schema](#rubric-schema)
10. [Interactive Mode](#interactive-mode)
11. [Audit Trail](#audit-trail)
12. [Adding Custom App Types](#adding-custom-app-types)
13. [Validation & Testing](#validation--testing)
14. [Adoption & Kill Gate](#adoption--kill-gate)
15. [Architecture](#architecture)
16. [Development Roadmap](#development-roadmap)
17. [Contributing](#contributing)
18. [License](#license)

---

## Problem Statement

Teams ship to production without a consistent readiness checklist. Critical gaps
in observability, security, CI/CD, and rollback procedures surface only after
incidents. Existing frameworks (AWS Well-Architected, Google PRR) provide
principles but lack automated, opinionated tooling tailored to specific app
types.

`prod-ready` fills this gap:

- **Opinionated**, not open-ended. It tells you what to fix, not just what to
  think about.
- **App-type aware**. A data pipeline has different readiness requirements than
  a web frontend.
- **Deterministic**. Same inputs always produce the same score.
- **Actionable**. Every gap comes with remediation guidance.

---

## How It Works

```
Input Assessment          Scoring Engine          Output
─────────────            ──────────────          ──────
App type ──┐
           ├──▶  Rubric Selector  ──▶  Gap Report (JSON/YAML)
Project  ──┤       │                    ├── Per-category scores
           │       ├── Criteria Eval    ├── Severity tiers
Config  ───┘       │                    ├── Remediation steps
                   └── Weighted Scoring └── Audit log entry
```

1. **Select** an app type (web-api, data-pipeline, ml-serving, web-frontend,
   mobile-backend).
2. **Supply** project metadata (config files, repo structure, manifest paths).
3. **Evaluate** against a versioned YAML rubric of weighted criteria.
4. **Score** each category (observability, security, CI/CD, data integrity,
   rollback) with pass/warn/fail per check.
5. **Report** gaps with severity tiers and actionable remediation templates.
6. **Audit** — all assessments are logged for compliance and trend tracking.

---

## Installation

### pip

```bash
pip install prod-ready
```

### Homebrew (macOS/Linux)

```bash
brew tap johnberey19/prod-ready
brew install prod-ready
```

### From Source

```bash
git clone https://github.com/johnberey19/prod-ready.git
cd prod-ready
pip install -e .
```

### Requirements

- Python 3.10+
- (Optional) Docker — for containerized assessment of target projects
- (Optional) `git` — for analyzing repository structure

---

## Quick Start

### 1. Assess a web API project

```bash
prod-ready assess --type web-api --path ./my-service
```

Output:

```
prod-ready Assessment — web-api
──────────────────────────────
Overall Score: 67/100  [WARN]

  CI/CD          90/100  ✅  All checks pass
  Observability  70/100  ⚠️  Missing distributed tracing
  Security       60/100  ⚠️  Rate limiting not configured
  Rollback       40/100  ❌  No documented rollback procedure
  Data Integrity 75/100  ⚠️  Migrations not versioned

Gaps Found: 8  |  Critical: 2  |  High: 3  |  Medium: 3

Run `prod-ready gaps --format yaml` for full detail.
Run `prod-ready fix --guidance` for remediation steps.
```

### 2. Get a machine-readable report

```bash
prod-ready assess --type web-api --path ./my-service --format json > report.json
```

### 3. Use interactive mode

```bash
prod-ready interactive
```

Guided prompts walk you through app type selection, project configuration, and
gap review.

---

## CLI Reference

### `prod-ready assess`

Run a production-readiness assessment.

```
prod-ready assess --type <app-type> --path <project-path> [OPTIONS]

Options:
  --type <TYPE>          App type: web-api | data-pipeline | ml-serving |
                         web-frontend | mobile-backend
  --path <PATH>          Path to the project root directory
  --format <FORMAT>      Output format: text (default) | json | yaml
  --output <FILE>        Write report to file instead of stdout
  --rubric <VERSION>     Use a specific rubric version (default: latest)
  --strict               Treat all warnings as failures
  --no-color             Disable ANSI color output
  --offline              Skip network checks (no dependency scanning)
  --config <FILE>        Path to prod-ready.yaml project config
```

### `prod-ready gaps`

Show detailed gap report from the last assessment.

```
prod-ready gaps [OPTIONS]

Options:
  --format <FORMAT>      text | json | yaml | csv
  --severity <LEVEL>     Filter: critical | high | medium | low | all
  --category <NAME>      Filter: ci-cd | observability | security |
                         data-integrity | rollback
  --guidance             Include remediation guidance for each gap
```

### `prod-ready list-types`

List all supported app types and their rubric versions.

```
prod-ready list-types

Output:
  web-api          rubric v1.2  (2026-06-01)
  data-pipeline    rubric v1.1  (2026-05-15)
  ml-serving       rubric v1.0  (2025-12-01)
  web-frontend     rubric v1.0  (2025-11-20)
  mobile-backend   rubric v1.0  (2025-11-10)
```

### `prod-ready init`

Create a `prod-ready.yaml` configuration file in the target project.

```
prod-ready init --path ./my-service

Creates:
  prod-ready.yaml    — Project metadata, rubric overrides, excluded checks
```

### `prod-ready version`

Print version information.

```
prod-ready version

Output:
  prod-ready v0.4.0
  Rubric schema v2.1.0
  Last updated: 2026-06-01
```

---

## Output Format

### Text (default)

Human-readable table output with color-coded severity. Suitable for terminal
reading and CI logs.

### JSON

Structured JSON with the following schema:

```json
{
  "tool": "prod-ready",
  "version": "0.4.0",
  "rubric_version": "2.1.0",
  "app_type": "web-api",
  "timestamp": "2026-06-12T19:30:00Z",
  "project_path": "/home/user/my-service",
  "overall_score": 67,
  "overall_rating": "warn",
  "categories": [
    {
      "name": "security",
      "score": 60,
      "rating": "warn",
      "checks": [
        {
          "id": "SEC-003",
          "description": "Rate limiting configured on all ingress endpoints",
          "result": "fail",
          "severity": "high",
          "remediation": "Configure rate limiting via nginx/envoy middleware. See docs/rate-limiting.md."
        }
      ]
    }
  ],
  "gaps_total": 8,
  "gaps_by_severity": { "critical": 2, "high": 3, "medium": 3, "low": 0 },
  "disclaimer": "This is an assessment, not a certification."
}
```

### YAML

Same structure as JSON, in YAML format. Suitable for version-controlled assessment
records.

---

## App Types

### web-api (First-class, v1.2)

REST, gRPC, or GraphQL APIs. Checks: authentication, authorization, input
validation, rate limiting, CORS, error handling, health checks, logging,
monitoring, CI/CD pipeline, rollback, database migrations, API documentation.

### data-pipeline (v1.1)

Batch or streaming data pipelines. Checks: schema validation, dead-letter
processing, idempotency, backfill capability, data freshness monitoring,
partition strategy, resource quotas, lineage tracking.

### ml-serving (v1.0)

ML model serving endpoints. Checks: model versioning, A/B testing infra,
prediction logging, drift detection, resource scaling, shadow deployment,
reproducibility, feature store consistency.

### web-frontend (v1.0)

SPAs and server-rendered web apps. Checks: CSP headers, build optimization,
error boundaries, accessibility, performance budgets, CDN configuration,
environment variable hygiene.

### mobile-backend (v1.0)

Backend-for-frontend (BFF) and mobile API services. Checks: device-aware
auth, push notification handling, API versioning, payload optimization,
offline sync support.

---

## Scoring System

### Rating Scale

| Score  | Rating   | Icon | Meaning                              |
|--------|----------|------|--------------------------------------|
| 90-100 | pass     | ✅   | Production-ready                     |
| 60-89  | warn     | ⚠️   | Gaps exist — remediate before launch |
| 0-59   | fail     | ❌   | Critical gaps — do not ship          |

### Weights

Each category contributes a configurable weight to the overall score:

| Category        | Weight | Focus Areas                                  |
|-----------------|--------|----------------------------------------------|
| CI/CD           | 20%    | Automated testing, deployment, rollback      |
| Observability   | 25%    | Logging, monitoring, alerting, tracing       |
| Security        | 25%    | Auth, input validation, secrets, scanning    |
| Data Integrity  | 15%    | Migrations, schema validation, backups       |
| Rollback        | 15%    | Rollback procedures, blue/green, canary      |

Weights are defined per-app-type in the rubric YAML schema and can be overridden
in `prod-ready.yaml`.

### Severity Tiers

- **Critical**: Immediate production risk. Blocks deployment.
- **High**: Significant risk. Should be fixed before launch.
- **Medium**: Moderate risk. Fix in the next sprint.
- **Low**: Best practice gap. Fix when convenient.

### Determinism Guarantee

Same project + same rubric version = same score, always. No human judgment
calls in the scoring path. Rubric changes are versioned and explicitly opted
into.

---

## Rubric Schema

Rubrics are versioned YAML files. Example (abbreviated):

```yaml
# rubrics/web-api/v1.2.yaml
version: "1.2.0"
last_reviewed: "2026-06-01"
app_type: web-api
categories:
  - name: security
    weight: 0.25
    checks:
      - id: SEC-001
        description: "HTTPS enforced on all endpoints"
        check_type: file_scan                 # file_scan | command | prompt
        targets: ["docker-compose.yml", "nginx.conf"]
        assertion: "ssl_enabled"
        severity: critical
        remediation: |
          1. Configure TLS termination at the load balancer
          2. Add HSTS header
          3. Redirect HTTP → HTTPS
        docs_url: "https://github.com/yourorg/prod-ready/wiki/SEC-001"

      - id: SEC-003
        description: "Rate limiting configured on all ingress endpoints"
        check_type: prompt
        prompt: "Is rate limiting configured on all public endpoints? (yes/no/partial)"
        if_yes: pass
        if_no: { result: fail, severity: high }
        if_partial: { result: warn, severity: medium }
        remediation: "Configure rate limiting via middleware. See docs/SEC-003.md"
```

### Check Types

| Type         | How it works                                           |
|--------------|--------------------------------------------------------|
| `file_scan`  | Scan project files for patterns (regex, AST, config)   |
| `command`    | Run a shell command, check exit code / output          |
| `prompt`     | Ask the user a question (interactive mode only)        |
| `config`     | Read a config file and validate fields                 |

---

## Interactive Mode

Interactive mode (`prod-ready interactive`) walks through an assessment with
guided prompts:

```
$ prod-ready interactive

▸ Select your app type:
    1. web-api
    2. data-pipeline
    3. ml-serving
    4. web-frontend
    5. mobile-backend
  Choice: 1

▸ Project path: ./my-service

▸ CI/CD Pipeline
  ✓ Automated tests on PR? (yes) 
  ✓ Deploy on merge to main? (yes)
  ✓ Health check endpoint exists? (no)
    → [WARN] No /health endpoint detected
    Remediation: Add a /health endpoint that returns 200 when ready.
    Acknowledge? (yes/no/postpone): yes

...

▸ Assessment complete.
  Overall: 72/100 [WARN]
  Export report? (json/yaml/print/discard): json
  Saved to: ./prod-ready-report-20260612.json
```

**Graceful handling of unsupported types**: If an app type isn't listed, the
tool prompts for manual criteria selection and saves the configuration for
future runs.

---

## Audit Trail

Every assessment run produces an audit log entry:

```json
{
  "timestamp": "2026-06-12T19:30:00Z",
  "tool_version": "0.4.0",
  "rubric_version": "1.2.0",
  "app_type": "web-api",
  "project_path": "/home/user/my-service",
  "overall_score": 67,
  "user_acknowledgments": [
    {"gap_id": "SEC-003", "acknowledged": true, "decision": "fix_next_sprint"},
    {"gap_id": "OBS-001", "acknowledged": true, "decision": "accepted_risk"}
  ]
}
```

Audit logs are stored in `.prod-ready/audit.jsonl` in the project directory.
They are append-only and tamper-evident (checksummed).

---

## Adding Custom App Types

### 1. Define a rubric YAML

Create `rubrics/my-type/v1.0.yaml` following the schema above.

### 2. Register the type

Add to `prod-ready.yaml`:

```yaml
custom_types:
  my-type:
    rubric: rubrics/my-type/v1.0.yaml
    description: "Description of my custom app type"
```

### 3. Share as a plugin

```bash
prod-ready plugin create my-type
# Creates a distributable plugin package
pip install prod-ready-plugin-my-type
```

Plugins are self-contained modules with: rubric schema, scoring criteria, gap
categories, recommendation templates, and validation fixtures.

---

## Validation & Testing

The framework itself is validated against 3-5 known projects with expected scores:

```bash
# Run the validation suite
prod-ready validate

# Run with verbose output
prod-ready validate --verbose
```

### Test Fixtures

| Project            | App Type   | Expected Score | Purpose                   |
|--------------------|------------|----------------|---------------------------|
| fixture-good       | web-api    | 92             | High-score baseline       |
| fixture-average    | web-api    | 65             | Medium-score baseline     |
| fixture-bad        | web-api    | 30             | Low-score baseline        |
| fixture-pipeline   | data-pipeline | 78         | Cross-type validation     |
| fixture-legacy     | web-api    | 45             | Legacy project patterns   |

### Integration Tests

```bash
cd /path/to/prod-ready
pytest tests/ -v --cov=prod_ready --cov-report=term-missing
```

---

## Adoption & Kill Gate

This tool follows a strict adoption model:

- **Launch requirement**: Used by 3+ teams within 60 days of release.
- **Kill criterion**: If not adopted by 3+ teams within 60 days, the tool is
  sunset. No zombie tools.
- **Reporting**: Adoption metrics reported to governance at 2-week and 60-day
  marks with go/no-go recommendation.
- **ROI tracking**: Baseline production incidents related to readiness gaps;
  measure reduction post-deployment.

---

## Architecture

```
prod-ready/
├── prod_ready/
│   ├── cli/                  # Click-based CLI entry points
│   │   ├── __init__.py
│   │   ├── assess.py          # `prod-ready assess`
│   │   ├── gaps.py            # `prod-ready gaps`
│   │   ├── interactive.py     # `prod-ready interactive`
│   │   └── init.py            # `prod-ready init`
│   ├── engine/
│   │   ├── scorer.py          # Deterministic scoring engine
│   │   ├── rubric.py          # Rubric loading, validation, versioning
│   │   ├── checker/
│   │   │   ├── file_scan.py   # File-based checks
│   │   │   ├── command.py     # Shell command checks
│   │   │   ├── prompt.py      # Interactive prompt checks
│   │   │   └── config.py      # Config file checks
│   │   └── audit.py           # Audit trail writer (append-only JSONL)
│   ├── plugins/
│   │   ├── web_api/
│   │   ├── data_pipeline/
│   │   ├── ml_serving/
│   │   ├── web_frontend/
│   │   ├── mobile_backend/
│   │   └── loader.py          # Plugin discovery and loading
│   ├── output/
│   │   ├── formatter.py       # Text/JSON/YAML/CSV formatters
│   │   └── report.py          # Report structure
│   └── config.py              # prod-ready.yaml loading
├── rubrics/
│   ├── web-api/
│   │   ├── v1.0.yaml
│   │   ├── v1.1.yaml
│   │   └── v1.2.yaml
│   ├── data-pipeline/
│   │   └── v1.1.yaml
│   └── ...                    # Other app types
├── tests/
│   ├── fixtures/              # Known-project test fixtures
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml
├── tox.ini
└── README.md
```

### Plugin Interface Contract

Each app type plugin must implement:

```python
class AppTypePlugin(ABC):
    @property
    def name(self) -> str: ...
    
    @property
    def rubric_version(self) -> str: ...
    
    def load_rubric(self) -> Rubric: ...
    
    def evaluate(self, project_path: Path, context: dict) -> list[CheckResult]: ...
    
    def get_remediation(self, check_id: str) -> str: ...
```

---

## Development Roadmap

### Phase 1 — CLI MVP + First App Type: web-api
- [x] Rubric criteria definition (5 app types designed)
- [ ] Scoring engine core + CLI scaffolding
- [ ] Plugin interface contract (locked)
- [ ] Interactive mode shell

### Phase 2 — Decision Engine + Audit Logging
- [ ] Confirmation gate for critical gaps
- [ ] Audit trail (append-only JSONL)
- [ ] Validation suite + known-project fixtures

### Phase 3 — Type Expansion + Interactive Mode (Full)
- [ ] Remaining 4 app types (data-pipeline, ml-serving, web-frontend, mobile-backend)
- [ ] Full interactive mode with prompts
- [ ] Compliance mapping layer (SOC2, HIPAA, PCI-DSS) — stretch

### Phase 4 — Documentation + Distribution
- [x] README (this file)
- [ ] Getting-started guide
- [ ] CI/CD pipeline for the tool itself
- [ ] pip/homebrew packaging
- [ ] Version tagging + changelog
- [ ] Contribution guide for adding new app types

### Phase 5 — Adoption Tracking + Kill Gate
- [ ] Usage survey design
- [ ] Analytics/metrics collection
- [ ] Kill gate: 3+ teams / 60 days
- [ ] ROI tracking

### Council Conditions (MANDATORY)
- Hard scope cap: No workflow/approval chains in v1
- Maintenance owner assigned before Phase 2 begins
- Validation fixtures for every app type before Phase 3
- Phase 1 adoption gate: 3+ teams / 2 weeks before Phase 2 proceeds

---

## Contributing

### Adding a New App Type

1. Create `rubrics/<type>/v1.0.yaml` (see [Rubric Schema](#rubric-schema)).
2. Create `prod_ready/plugins/<type>/` with plugin module.
3. Add validation fixture in `tests/fixtures/<type>/`.
4. Register in `prod_ready/plugins/loader.py`.
5. Submit a PR with rubric + plugin + fixture + tests.

### Adding a New Check to an Existing Rubric

1. Add the check to the appropriate `rubrics/<type>/v<N>.yaml`.
2. Bump the rubric version (semver).
3. Add or update validation fixtures.
4. Update tests.

### Code Standards

- **TDD enforced**: Write the failing test first, then implement.
- All rubric changes require a pull request with validation evidence.
- Rubric changes are versioned — never modify an existing version, create a
  new one.

### Governance

This project follows the C-Suite Council model. Significant changes (new app
types, rubric weight changes, scoring algorithm changes) require council review.
See `GOVERNANCE.md` for details.

---

## License

MIT License. See `LICENSE` for full text.

---

*This tool is an assessment aid, not a certification authority. Always apply
engineering judgment. The gap report surfaces what the rubric checks — it cannot
catch every context-specific risk.*
