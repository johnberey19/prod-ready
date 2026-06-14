# Distribution Status — prod-ready v0.1.2

**Last verified:** 2026-06-14

## ✅ Completed Artifacts

### Documentation (in repo)
| File | Lines | Status |
|------|-------|--------|
| README.md | ~500 | ✅ Committed, pushed to origin/main |
| GETTING_STARTED.md | ~120 | ✅ Committed, pushed to origin/main |
| CONTRIBUTING.md | ~130 | ✅ Committed, pushed to origin/main |
| PUBLISHING.md | ~60 | ✅ Committed, pushed to origin/main |
| CHANGELOG.md | ~50 | ✅ Committed, pushed to origin/main |
| docs/man/prod-ready.1 | ~80 | ✅ Committed, pushed to origin/main |

### GitHub Releases
| Tag | Assets | Status |
|-----|--------|--------|
| v0.1.0 | wheel + sdist | ✅ Published |
| v0.1.1 | wheel + sdist | ✅ Published |
| v0.1.2 | wheel + sdist | ✅ Published |

### CD Pipeline (`.github/workflows/cd.yml`)
- **Trigger:** git tags matching `v*.*.*`
- **Release job:** builds wheel + sdist, creates GitHub Release with changelog — ✅ WORKING
- **PyPI publish:** dual auth (API token + OIDC trusted publisher) — ❌ BLOCKED (no credentials)
- **Homebrew:** `dawidd6/action-homebrew-bump-formula@v3` — ❌ BLOCKED (depends on PyPI + no token)

### Homebrew Tap
- **Repo:** https://github.com/johnberey19/homebrew-prod-ready
- **Formula:** `Formula/prod-ready.rb` exists with v0.1.0 SHA256
- **Status:** ✅ Created, awaiting CD automation to update

### Local Build Artifacts (`dist/`)
- `prod_ready-0.1.0-py3-none-any.whl` (20.7 KB)
- `prod_ready-0.1.0.tar.gz` (28.4 KB)

## ❌ Blockers (Manual User Action Required)

### 1. PyPI Publishing
**Option A (easier):** Add `PYPI_TOKEN` secret
1. Go to https://pypi.org/manage/account/token/
2. Create API token for `prod-ready` project
3. Go to https://github.com/johnberey19/prod-ready/settings/secrets/actions
4. Add secret: Name=`PYPI_TOKEN`, Value=`pypi-...`

**Option B (OIDC):** Configure Trusted Publisher
1. Go to https://pypi.org/manage/account/publishing/
2. Add pending publisher:
   - PyPI Project Name: `prod-ready`
   - Owner: `johnberey19`
   - Repository name: `prod-ready`
   - Workflow name: `cd.yml`
   - Environment name: `pypi`

### 2. Homebrew Tap Token
1. Go to https://github.com/settings/tokens
2. Generate PAT with `public_repo` scope
3. Go to https://github.com/johnberey19/prod-ready/settings/secrets/actions
4. Add secret: Name=`HOMEBREW_TAP_TOKEN`, Value=`ghp_...`

## 🚀 After Both Secrets Configured

```bash
git tag v0.1.2  # or next version
git push origin v0.1.2
```

The CD pipeline will automatically:
1. Create GitHub Release with wheel + sdist
2. Publish to PyPI
3. Update Homebrew formula

## Verification Links
- Repo: https://github.com/johnberey19/prod-ready
- Releases: https://github.com/johnberey19/prod-ready/releases
- Homebrew tap: https://github.com/johnberey19/homebrew-prod-ready
- PyPI (pending): https://pypi.org/project/prod-ready/
- CD workflow: https://github.com/johnberey19/prod-ready/blob/main/.github/workflows/cd.yml
