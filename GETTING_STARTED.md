# Getting Started with prod-ready

## 5-Minute Walkthrough

### Step 1: Install

```bash
pip install prod-ready
```

Verify:

```bash
prod-ready version
```

### Step 2: Initialize Your Project

Navigate to your project root and run:

```bash
cd /path/to/your-project
prod-ready init
```

This creates a `prod-ready.yaml` config file:

```yaml
# prod-ready.yaml
project:
  name: "my-service"
  type: web-api

# Override rubric weights (optional)
weights:
  security: 0.30
  observability: 0.25
  ci-cd: 0.20
  data-integrity: 0.15
  rollback: 0.10

# Exclude specific checks (optional)
exclude_checks:
  - SEC-007    # Skip a check that doesn't apply to your context

# Custom paths (optional)
paths:
  dockerfile: deploy/Dockerfile
  ci_config: .github/workflows/ci.yml
```

### Step 3: Run Your First Assessment

```bash
prod-ready assess --type web-api --path .
```

### Step 4: Review the Gaps

```bash
prod-ready gaps --guidance
```

This shows each gap with specific remediation steps.

### Step 5: Re-Assess After Fixes

```bash
# After fixing gaps...
prod-ready assess --type web-api --path .
# Score should improve
```

## Common Workflows

### CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
# .github/workflows/prod-ready.yml
name: Production Readiness
on:
  pull_request:
    branches: [main]

jobs:
  assess:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install prod-ready
        run: pip install prod-ready
      - name: Run assessment
        run: |
          prod-ready assess --type web-api --path . --format json --output report.json
      - name: Check score threshold
        run: |
          SCORE=$(jq '.overall_score' report.json)
          if [ "$SCORE" -lt 70 ]; then
            echo "Score $SCORE is below threshold (70). Review gaps:"
            prod-ready gaps --severity critical
            exit 1
          fi
```

### Tracking Scores Over Time

```bash
# Save dated reports
prod-ready assess --type web-api --path . --format json \
  --output reports/prod-ready-$(date +%Y%m%d).json

# Compare scores
prod-ready diff reports/prod-ready-20260601.json reports/prod-ready-20260612.json
```

### Team Onboarding

```bash
# Interactive mode is best for first-time users
prod-ready interactive
```

The interactive mode explains each check and why it matters.

## Configuration Reference

### prod-ready.yaml

| Field              | Type     | Default | Description                          |
|--------------------|----------|---------|--------------------------------------|
| `project.name`     | string   | dir name| Project display name                 |
| `project.type`     | enum     | —       | Required. App type.                  |
| `weights`          | map      | rubric  | Override category weights            |
| `exclude_checks`   | list     | []      | Check IDs to skip                    |
| `paths`            | map      | auto    | Override auto-detected file paths    |
| `custom_rubric`    | string   | —       | Path to a custom rubric YAML         |

### Environment Variables

| Variable              | Description                          |
|-----------------------|--------------------------------------|
| `PROD_READY_CONFIG`   | Path to prod-ready.yaml              |
| `PROD_READY_OFFLINE`  | Set to `1` to skip network checks    |
| `PROD_READY_NO_COLOR` | Set to `1` to disable ANSI colors    |

## Troubleshooting

### "No rubric found for type X"

The app type isn't installed. Check available types:

```bash
prod-ready list-types
```

Install the plugin:

```bash
pip install prod-ready-plugin-<type>
```

### Score seems wrong

1. Check the rubric version: `prod-ready version`
2. Review excluded checks in `prod-ready.yaml`
3. Run with `--strict` to surface warnings as failures
4. Check the audit log: `cat .prod-ready/audit.jsonl`

### Interactive mode hangs

Ensure your terminal supports interactive input. Use `--offline` flag if network
checks are timing out.
