# PyPI & Homebrew Publishing Setup Guide

The CD pipeline supports two authentication methods for PyPI publishing.

## Option A: PyPI API Token (Recommended -- Easier)

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with scope for `prod-ready`
3. Go to https://github.com/johnberey19/prod-ready/settings/secrets/actions
4. Add a new repository secret:
   - Name: `PYPI_TOKEN`
   - Value: `pypi-...` (your token)

## Option B: PyPI Trusted Publisher (OIDC)

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new pending publisher:
   - PyPI Project Name: `prod-ready`
   - Owner: `johnberey19`
   - Repository name: `prod-ready`
   - Workflow name: `cd.yml`
   - Environment name: `pypi`

## Homebrew Tap Token

Required for both options above:

1. Go to https://github.com/settings/tokens
2. Generate a Personal Access Token with `public_repo` scope
3. Go to https://github.com/johnberey19/prod-ready/settings/secrets/actions
4. Add a new repository secret:
   - Name: `HOMEBREW_TAP_TOKEN`
   - Value: `ghp_...` (your token)

## Triggering a Release

Once both secrets are configured:

```bash
git tag v0.1.2
git push origin v0.1.2
```

The CD pipeline will:
1. Create a GitHub Release with the tag
2. Publish the package to PyPI
3. Update the Homebrew formula in `johnberey19/homebrew-prod-ready`

## Verification

- PyPI: https://pypi.org/project/prod-ready/
- Homebrew: `brew install johnberey19/homebrew-prod-ready/prod-ready`
- Release: https://github.com/johnberey19/prod-ready/releases
