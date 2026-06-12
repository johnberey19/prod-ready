# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Placeholder for next release changes.

## [0.1.0] - 2026-06-12

### Added
- Initial release.
- CLI with `assess`, `list-types`, and `info` commands.
- Deterministic scoring engine with rubric-based assessment.
- Web API rubric (v1.0) with 5 categories and 19 checks.
- Output formats: table (rich), JSON, YAML.
- Audit logging to `~/.prod-ready/audit/`.
- Plugin interface contract for custom app types.
- Test suite: unit tests, integration tests, validation fixtures.
- CI pipeline: lint (ruff, mypy), test (3.10-3.13, ubuntu/macos/windows), validation suite.
- CD pipeline: GitHub Release, PyPI publish, Homebrew formula update.
- Version tagging via git tags (`v*.*.*`).

[Unreleased]: https://github.com/johnberey19/prod-ready/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/johnberey19/prod-ready/releases/tag/v0.1.0
