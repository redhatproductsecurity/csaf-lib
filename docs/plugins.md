# Validation Plugins

This project supports external validation plugins discovered at runtime via Python entry points. Use the `csaf-lib validate` CLI command to run all installed plugins against a CSAF VEX document.

## How it works
- Entry point group: `csaf_lib.validators`
- Discovery: plugins are loaded using `importlib.metadata.entry_points`, sorted by entry point name.
- Runtime: the manager instantiates each plugin and calls `validate(document)`.
- Output: each plugin returns a pass/fail `ValidationResult` with any `ValidationError`s; the CLI exits with code 1 if any plugin fails.

CLI:
```bash
csaf-lib validate <file>
csaf-lib validate --json <file>
```

## Authoring a plugin
1) Create a package with a `pyproject.toml`.
2) Implement a subclass of `ValidationPlugin` that returns a list of `ValidationError`s from `_run_validation`.
3) Register the plugin via the `csaf_lib.validators` entry point group.

Minimal example
```python
# my_vex_plugin/plugin.py
from csaf_lib.validation.base import ValidationPlugin, ValidationError
from csaf_lib.models import CSAFVEXDocument

class MyPlugin(ValidationPlugin):
    name = "my_plugin"
    description = "Checks that document.title is present."

    def _run_validation(self, document: CSAFVEXDocument) -> list[ValidationError]:
        errors: list[ValidationError] = []
        title = document.document.title if document.document else None
        if not title or not title.strip():
            errors.append(ValidationError(message="document.title missing"))
        return errors
```

`pyproject.toml` registration
```toml
[build-system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-vex-plugin"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["csaf-lib>=0.1.0b1"]

[project.entry-points."csaf_lib.validators"]
my_plugin = "my_vex_plugin.plugin:MyPlugin"
```

Install locally for testing
```bash
pip install -e /path/to/my-vex-plugin
csaf-lib validate examples/sample-vex.json
```

## Programmatic use
```python

from csaf_lib.validation import Validator

# Create a validator for a VEX file and run all installed plugins
validator = Validator.from_file("path/to/vex.json")
report = validator.run_all()

# Check if all plugins passed
if report.passed:
    print("All validation plugins passed!")
else:
    for result in report.results:
        if not result.success:
            print(f"{result.validator_name}:")
            for err in result.errors:
                print(f"  - {err.message}")
```
