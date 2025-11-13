# ZenMarket AI - Release Checklist

This checklist ensures a smooth and reliable release process for ZenMarket AI.

---

## Pre-Release (1 Week Before)

### Code Quality

- [ ] All tests pass (`pytest`)
- [ ] Test coverage ≥ 70% (`pytest --cov=src --cov-report=term`)
- [ ] Code formatted (`black . && isort .`)
- [ ] Linting clean (`ruff check .`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Security scan clean (`bandit -r src/`)
- [ ] No critical code smells or technical debt

### Documentation

- [ ] README.md updated with latest features
- [ ] CHANGELOG.md updated with all changes
- [ ] context.md updated if architecture changed
- [ ] API documentation current
- [ ] User guides reflect new features
- [ ] Migration guide created (if breaking changes)

### Dependencies

- [ ] All dependencies up to date
- [ ] No known vulnerabilities (`pip-audit`)
- [ ] requirements.txt pinned to stable versions
- [ ] License compliance checked

### Testing

- [ ] Unit tests updated for new features
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance benchmarks run
- [ ] Edge cases tested
- [ ] Error handling verified

---

## Release Preparation (3 Days Before)

### Version Management

- [ ] Version number decided (follows Semantic Versioning)
  - MAJOR.MINOR.PATCH (e.g., 1.2.0)
  - Breaking changes → MAJOR
  - New features → MINOR
  - Bug fixes → PATCH
- [ ] Version updated in `pyproject.toml`
- [ ] Version updated in `src/__init__.py` (if exists)
- [ ] Version updated in documentation

### CHANGELOG.md Update

```markdown
## [1.2.0] - 2025-01-XX

### Added
- New position sizing method: Volatility-adjusted
- Support for additional technical indicators (VWAP, OBV)
- Performance metrics dashboard

### Changed
- Improved backtest engine performance (30% faster)
- Updated risk management limits
- Enhanced logging with structured output

### Fixed
- Incorrect ATR calculation in volatile markets
- Memory leak in long-running backtests
- Order execution slippage edge case

### Deprecated
- Old CSV export format (will be removed in 2.0)

### Removed
- Legacy API endpoints
```

### Git Preparation

- [ ] All feature branches merged
- [ ] Branch cleanup completed
- [ ] No uncommitted changes
- [ ] Working tree clean

---

## Release Day

### Final Checks

- [ ] Run full test suite one last time
  ```bash
  pytest --cov=src --cov-report=html
  make precommit
  ```

- [ ] Run maintenance check
  ```bash
  python scripts/maintenance_check.py --verbose
  ```

- [ ] Verify documentation builds
  ```bash
  mkdocs build
  ```

### Create Release

#### 1. Tag the Release

```bash
# Ensure you're on main/master branch
git checkout main
git pull origin main

# Create annotated tag
git tag -a v1.2.0 -m "Release version 1.2.0

Major features:
- Volatility-adjusted position sizing
- Enhanced performance metrics
- 30% faster backtest engine

Full changelog: https://github.com/TechNatool/zenmarket-ai/blob/main/CHANGELOG.md#120
"

# Push tag to remote
git push origin v1.2.0
```

#### 2. Create GitHub Release

1. Go to: https://github.com/TechNatool/zenmarket-ai/releases/new
2. Select tag: `v1.2.0`
3. Release title: `ZenMarket AI v1.2.0`
4. Copy release notes from CHANGELOG.md
5. Check "Create a discussion for this release" (if applicable)
6. Click "Publish release"

#### 3. Build Distribution (if publishing to PyPI)

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build

# Verify the build
twine check dist/*

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ zenmarket-ai==1.2.0

# If all good, upload to production PyPI
twine upload dist/*
```

**Note:** For ZenMarket AI, we do NOT publish to PyPI (private project).

---

## Post-Release (Same Day)

### Verification

- [ ] GitHub release created successfully
- [ ] Tag pushed to repository
- [ ] CI/CD pipeline passed on tag
- [ ] Documentation deployed (if auto-deploy enabled)
- [ ] Release announcement draft prepared

### Monitoring (First 24 Hours)

- [ ] Monitor for bug reports
- [ ] Check CI/CD for any failures
- [ ] Review any user feedback
- [ ] Verify installation works as expected

### Communication

- [ ] Update project status (if public)
- [ ] Notify team of release
- [ ] Update roadmap with completed features

---

## Post-Release (First Week)

### Follow-up

- [ ] Address any critical bugs immediately
- [ ] Create hotfix release if necessary (1.2.1)
- [ ] Update project board with completed items
- [ ] Archive old branches
- [ ] Start planning next release

### Metrics Review

- [ ] Test coverage maintained or improved
- [ ] Performance benchmarks stable
- [ ] No new security vulnerabilities
- [ ] Documentation feedback reviewed

---

## Hotfix Release Process

If a critical bug is found after release:

### 1. Create Hotfix Branch

```bash
git checkout -b hotfix/1.2.1 v1.2.0
```

### 2. Fix the Bug

- Make minimal changes
- Add/update tests
- Update CHANGELOG.md

### 3. Test Thoroughly

```bash
pytest
make precommit
```

### 4. Merge and Tag

```bash
git checkout main
git merge --no-ff hotfix/1.2.1
git tag -a v1.2.1 -m "Hotfix: Critical bug in ATR calculation"
git push origin main v1.2.1
```

### 5. Deploy Immediately

Follow same release process but expedited.

---

## Version Numbering Guide

### Semantic Versioning (MAJOR.MINOR.PATCH)

**MAJOR (X.0.0)**
- Breaking changes
- Complete architecture redesign
- Major feature overhaul
- Example: 1.0.0 → 2.0.0

**MINOR (1.X.0)**
- New features (backward compatible)
- New indicators/strategies
- Enhanced functionality
- Example: 1.2.0 → 1.3.0

**PATCH (1.2.X)**
- Bug fixes
- Minor improvements
- Documentation updates
- Example: 1.2.0 → 1.2.1

### Pre-release Versions

- **Alpha:** `1.3.0-alpha.1` (Early testing, unstable)
- **Beta:** `1.3.0-beta.1` (Feature complete, testing)
- **RC:** `1.3.0-rc.1` (Release candidate)

---

## Release Schedule (Recommended)

### Regular Releases
- **Major:** Once a year (January)
- **Minor:** Quarterly (January, April, July, October)
- **Patch:** As needed (within 1-2 weeks of bugs discovered)

### Emergency Hotfixes
- Released immediately for critical security issues
- Within 24-48 hours for critical bugs

---

## Rollback Procedure

If a release has critical issues:

### 1. Immediate Actions

```bash
# Revert to previous stable version
git revert <bad-commit-sha>

# Or reset to previous tag (use with caution)
git reset --hard v1.1.0
git push --force origin main

# Tag the rollback
git tag -a v1.2.0-rollback -m "Rollback due to critical issue"
```

### 2. Communication

- Notify all users immediately
- Document the issue
- Provide workaround if possible
- Set timeline for fix

### 3. Fix and Re-release

- Fix the issue properly
- Extra testing
- Release as hotfix (1.2.1)

---

## Automation Opportunities

Consider automating:

- [ ] Version bumping (e.g., `bump2version`)
- [ ] CHANGELOG generation (e.g., `auto-changelog`)
- [ ] GitHub release creation (GitHub Actions)
- [ ] Tag creation on merge
- [ ] Documentation deployment

### Example GitHub Action (Future Enhancement)

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

---

## Checklist Summary

**Pre-Release:**
- ✅ All tests pass
- ✅ Documentation updated
- ✅ CHANGELOG.md complete
- ✅ Version numbers updated
- ✅ Dependencies reviewed

**Release:**
- ✅ Tag created and pushed
- ✅ GitHub release published
- ✅ CI/CD passes

**Post-Release:**
- ✅ Monitoring active
- ✅ Team notified
- ✅ Roadmap updated

---

**Maintained by:** TechNatool Development Team
**Last Updated:** 2025-01-13
**Template Version:** 1.0.0
