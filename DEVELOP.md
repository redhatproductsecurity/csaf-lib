# Developer Guide

This guide provides information for developers who want to contribute to the csaf-vex project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting Up Development Environment](#setting-up-development-environment)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Contributing](#contributing)

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Git with GPG signing configured

## Setting Up Development Environment

1. Clone the repository:

```bash
git clone https://github.com/RedHatProductSecurity/csaf-vex.git
cd csaf-vex
```

2. Install dependencies with development and test groups:

```bash
uv sync --group dev --group test
```

This will install all project dependencies, development tools (ruff), and testing dependencies (pytest, pytest-cov, deepdiff).

3. Verify installation:

```bash
uv run csaf-vex --help
```

4. Configure Git commit signing (required):

```bash
git config commit.gpgsign true
git config user.signingkey YOUR_GPG_KEY_ID
```

For more information on setting up GPG signing, see the [GitHub documentation on signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification).

## Project Structure

```
csaf-vex/
├── src/csaf_vex/          # Main package source code
│   ├── cli.py             # CLI entrypoint
│   ├── models/            # Internal representation models
│   │   ├── csafvex.py    # Root CSAFVEX document model
│   │   ├── document.py    # Document section models
│   │   ├── product_tree.py # Product tree models
│   │   ├── vulnerability.py # Vulnerability models
│   │   └── common.py      # Shared models (Note, Reference, etc.)
│   ├── validation/        # Semantic validation (external data)
│   └── verification/      # Structural and format validation
│       ├── verifier.py    # Main Verifier class
│       ├── csaf_compliance.py # Test Set 1: CSAF compliance
│       ├── data_type_checks.py # Test Set 2: Data type checks
│       ├── result.py      # Result and report classes
│       └── schemas/       # CSAF and CVSS JSON schemas
├── tests/                 # Test suite
│   ├── conftest.py       # Shared fixtures
│   ├── test_csaf_compliance.py # Tests for Test Set 1
│   ├── test_data_type_checks.py # Tests for Test Set 2
│   ├── test_models.py    # Model tests
│   └── test_files/       # Sample CSAF VEX files
├── scripts/              # Utility scripts
│   └── update-version.sh # Version bumping script
├── docs/                 # Documentation
│   ├── csafvex-usage.md # API usage documentation
│   ├── builder.md       # Builder pattern documentation
│   └── plugins.md       # Plugin system documentation
├── pyproject.toml        # Project metadata and dependencies
└── CHANGELOG.md          # Project changelog
```

## Development Workflow

1. Create a new branch from `main` with a descriptive name:

```bash
git checkout -b your-descriptive-branch-name
```

Branch names should be descriptive of the work being done (e.g., `add-cvss-v4-support`, `fix-product-id-validation`, `update-verification-docs`).

2. Make your changes to the codebase

3. Add or update tests as needed

4. Run tests and code quality checks (see sections below)

5. Commit your changes (signed commits required):

```bash
git commit -S -m "Your descriptive commit message"
```

6. Push your branch and create a pull request

## Running Tests

Run the test suite:

```bash
uv run pytest
```

Run with coverage report:

```bash
uv run pytest --cov=csaf_vex --cov-report=term-missing
```

## Code Quality

The project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting. Code style configuration is defined in `pyproject.toml`.

### Linting

```bash
# Check for linting issues
uv run ruff check .

# Auto-fix linting issues where possible
uv run ruff check --fix .
```

### Formatting

```bash
# Format code
uv run ruff format .

# Check formatting without applying changes
uv run ruff format --check .
```

## Contributing

### Submitting Pull Requests

1. Ensure all tests pass
2. Ensure code quality checks pass
3. Ensure all commits are signed
4. Update documentation if needed
5. Add entry to CHANGELOG.md under `[Unreleased]` section
6. Submit pull request to `main` branch

### Code Review Requirements

- Passing CI checks (tests and linting)
- All commits must be signed
- Code review approval from maintainers

### Adding New Features

1. Add tests covering the new functionality
2. Update documentation as needed (API docs, README, inline comments)
3. Add changelog entry describing the feature
4. Ensure backward compatibility or document breaking changes

### Fixing Bugs

1. Add a test that reproduces the bug
2. Implement the fix
3. Ensure the test now passes
4. Add changelog entry in `### Fixed` section

### Writing Tests

Test guidelines:

- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test data (see `tests/conftest.py`)
- Test both success and failure cases
- Test edge cases and boundary conditions

## Getting Help

- Report issues at: https://github.com/RedHatProductSecurity/csaf-vex/issues
- Review existing documentation in the `docs/` directory
- Check the README.md for usage examples
