#!/bin/bash
set -e

# Script to bump version using uv and update CHANGELOG.md
#
# Usage:
#   ./scripts/update-version.sh major|minor|patch|alpha|beta|rc

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Project root is the parent of the scripts directory
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <bump-level>"
    echo "Bump levels: major, minor, patch, alpha, beta, rc"
    echo "Example: $0 beta"
    exit 1
fi

BUMP_LEVEL=$1

# Run uv version bump
echo "Running: uv version --bump $BUMP_LEVEL"
(cd "$PROJECT_ROOT" && uv version --bump "$BUMP_LEVEL")

# Extract new version from pyproject.toml
NEW_VERSION=$(grep '^version = ' "$PROJECT_ROOT/pyproject.toml" | sed 's/version = "\(.*\)"/\1/')
echo "New version: $NEW_VERSION"

# Update CHANGELOG.md
TODAY=$(date +%Y-%m-%d)
if grep -q "## \[$NEW_VERSION\]" "$PROJECT_ROOT/CHANGELOG.md"; then
    echo "⚠ Version $NEW_VERSION already exists in CHANGELOG.md - skipping"
else
    sed -i "/## \[Unreleased\]/a\\
\\
## [$NEW_VERSION] - $TODAY" "$PROJECT_ROOT/CHANGELOG.md"
    echo "✓ Added $NEW_VERSION to CHANGELOG.md"
fi

echo ""
echo "✅ Successfully bumped version to $NEW_VERSION"
