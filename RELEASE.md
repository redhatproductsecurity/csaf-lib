# Release Guide

This guide describes the release process for the csaf-vex project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Version Numbering](#version-numbering)
- [Release Process](#release-process)
- [Publishing to PyPI](#publishing-to-pypi)

## Prerequisites

- Maintainer access to the repository
- PyPI publish credentials configured
- All tests passing on `main` branch

## Version Numbering

This project follows [PEP 440](https://peps.python.org/pep-0440/) versioning (required for PyPI) with semantic versioning principles:

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

Pre-release versions:
- **beta** (e.g., `0.1.0b1`, `0.1.0b2`) - Used before the project is considered stable

## Release Process

### 1. Create Release Branch

Create a new branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b release-X.Y.Z
```

### 2. Update Version

Use the version bump script to update the version in `pyproject.toml` and `CHANGELOG.md`:

```bash
# For beta releases
./scripts/update-version.sh beta    # Bump to next beta version

# For production releases
./scripts/update-version.sh patch   # Bump patch version (0.1.0 -> 0.1.1)
./scripts/update-version.sh minor   # Bump minor version (0.1.0 -> 0.2.0)
./scripts/update-version.sh major   # Bump major version (0.1.0 -> 1.0.0)
```

The script will:
- Update the version in `pyproject.toml`
- Update the lock file `uv.lock`
- Add a new version entry in `CHANGELOG.md` with the current date

### 3. Review CHANGELOG.md

Review the `CHANGELOG.md` and manually organize entries if needed. The changelog follows [Keep a Changelog](https://keepachangelog.com/) format with sections:
- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security fixes

### 4. Commit and Push

Commit the version bump and push the release branch:

```bash
git add pyproject.toml uv.lock CHANGELOG.md
git commit -S -m "Release version X.Y.Z"
git push origin release-X.Y.Z
```

### 5. Create Pull Request and Get Approval

1. Create a pull request from `release-X.Y.Z` to `main`
2. Wait for CI checks to pass
3. Get approval from maintainers

### 6. Tag the Release

After approval, tag the release commit on the release branch:

```bash
git tag -s X.Y.Z -m "Release version X.Y.Z"
git push origin X.Y.Z
```

### 7. Merge Pull Request

Merge the PR to `main` (use regular merge commit, not squash and merge).

### 8. Create GitHub Release

Create a release on GitHub:

1. Go to https://github.com/RedHatProductSecurity/csaf-vex/releases/new
2. Select the tag you just pushed
3. Use "Release X.Y.Z" as the title
4. Copy the relevant section from CHANGELOG.md as the description
5. Mark as pre-release if it's a beta version
6. Publish the release

## Publishing to PyPI

After creating the GitHub release, the package can be published to PyPI.

### Build the Distribution

```bash
uv build
```

This creates distribution files in the `dist/` directory.

### Publish to PyPI

```bash
uv publish
```

Or using twine:

```bash
twine upload dist/*
```

### Verify the Release

Verify the package is available on PyPI:

```bash
pip install csaf-vex==X.Y.Z
```
