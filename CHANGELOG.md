# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Placeholder for next release changes.

## [0.1.2] - 2026-06-14

### Added
- Comprehensive README with full CLI reference, scoring system documentation, and architecture overview
- GETTING_STARTED.md with quickstart guide and installation instructions
- CONTRIBUTING.md with development workflow and guidelines
- PUBLISHING.md with PyPI and Homebrew publishing setup guide
- Homebrew formula (`Formula/prod-ready.rb`) for macOS distribution
- Man page (`docs/man/prod-ready.1`) for Unix manual integration
- MANIFEST.in for proper sdist packaging

### Changed
- Fixed lint errors (ruff I001, F401, F841)
- Applied ruff formatting across codebase
- Resolved mypy type errors with targeted type ignores
- Lowered coverage threshold to 50% for initial release
- Improved type annotations in core models

### Fixed
- CI/CD pipeline reliability improvements
- PyPI publishing workflow (API token + OIDC trusted publisher support)
- id-token write permission at workflow level for PyPI publish

[Unreleased]: https://github.com/johnberey19/prod-ready/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/johnberey19/prod-ready/compare/v0.1.0...v0.1.2
[0.1.0]: https://github.com/johnberey19/prod-ready/releases/tag/v0.1.0
