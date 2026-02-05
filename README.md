# csaf-lib

[![Tests](https://github.com/RedHatProductSecurity/csaf-lib/actions/workflows/tests.yml/badge.svg)](https://github.com/RedHatProductSecurity/csaf-lib/actions/workflows/tests.yml)
[![Lint](https://github.com/RedHatProductSecurity/csaf-lib/actions/workflows/lint.yml/badge.svg)](https://github.com/RedHatProductSecurity/csaf-lib/actions/workflows/lint.yml)

A Python library for generating, parsing, and validating CSAF documents (VEX and Advisory).

## Installation

```bash
pip install csaf-lib
```

For development setup, see [DEVELOP.md](DEVELOP.md).

## Usage

### CLI

Read and parse a CSAF VEX file (with verification):

```bash
csaf-lib read tests/test_files/sample-vex.json
```

Read with verbose verification output:

```bash
csaf-lib read -v tests/test_files/sample-vex.json
```

Disable verification:

```bash
csaf-lib read --no-verify tests/test_files/minimal-vex.json
```

Verify a CSAF VEX file:

```bash
# Run all verification tests
csaf-lib verify tests/test_files/sample-vex.json

# Run only CSAF compliance tests (Test Set 1)
csaf-lib verify tests/test_files/sample-vex.json --test-set csaf

# Run only data type checks (Test Set 2)
csaf-lib verify tests/test_files/sample-vex.json --test-set data

# Run specific tests by ID
csaf-lib verify tests/test_files/sample-vex.json -t 1.1 -t 2.5
```

Validate with plugins:

```bash
csaf-lib validate tests/test_files/sample-vex.json
```

See docs/plugins.md for authoring and how the plugin system works.

### Python API - Reading Documents

```python
from csaf_lib.models import CSAFVEX

# Load from file
csafvex = CSAFVEX.from_file("path/to/document.json")

# Or load from dictionary
import json
with open("vex-file.json") as f:
    data = json.load(f)
csafvex = CSAFVEX.from_dict(data)

# Access document metadata
print(csafvex.document.title)
print(csafvex.document.publisher.name)
print(csafvex.document.tracking.id)

# Access vulnerabilities
for vuln in csafvex.vulnerabilities:
    print(f"CVE: {vuln.cve}")
    if vuln.cwe:
        print(f"  CWE: {vuln.cwe.id}")

# Access product tree
if csafvex.product_tree:
    for branch in csafvex.product_tree.branches:
        print(f"Branch: {branch.name}")

# Serialize back to dictionary
data = csafvex.to_dict()
```

### Python API - Creating Documents

```python
from csaf_lib.models import (
    CSAFVEX, Document, ProductTree, Vulnerability,
    CSAFVersion, PublisherCategory, TrackingStatus,
    BranchCategory, RelationshipCategory, RemediationCategory
)
from datetime import datetime, timezone

# Create document with fluent API
doc = Document(
    category="csaf_vex",
    csaf_version=CSAFVersion.VERSION_2_0,
    title="Security Advisory for CVE-2025-0001"
)

doc.with_publisher(
    name="Red Hat Product Security",
    namespace="https://redhat.com",
    category=PublisherCategory.VENDOR
).with_tracking(
    id="CVE-2025-0001",
    status=TrackingStatus.FINAL,
    version="1",
    initial_release_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    generator_engine_name="csaf-lib",
    generator_engine_version="0.1.0"
).add_tracking_revision(
    number="1",
    date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    summary="Initial version"
)

# Create product tree
tree = ProductTree()
vendor = tree.add_branch(BranchCategory.VENDOR, "Red Hat")
vendor.add_product_branch(
    category=BranchCategory.PRODUCT_VERSION,
    name="curl-1.0",
    product_name="curl version 1.0",
    product_id="curl-1.0",
    helper_purl="pkg:rpm/redhat/curl@1.0"
)

# Create vulnerability
vuln = Vulnerability(cve="CVE-2025-0001", title="Security Advisory")
vuln.with_product_status(known_affected=["curl-1.0"])
vuln.add_remediation(
    category=RemediationCategory.VENDOR_FIX,
    details="Update to version 1.1",
    product_ids=["curl-1.0"]
)

# Combine and save
vex = CSAFVEX(document=doc, product_tree=tree, vulnerabilities=[vuln])
with open("vex.json", "w") as f:
    json.dump(vex.to_dict(), f, indent=2)
```

### Validation (Plugins) - Python API

```python
import logging
from csaf_lib.models import CSAFVEX
from csaf_lib.validation.validator import Validator

csafvex = CSAFVEX.from_file("path/to/document.json")

# Create validator; default log level is WARNING
validator = Validator(csafvex, log_level=logging.INFO)

# Run all installed validation plugins
report = validator.run_all()
print(f"Plugins: total={report.total}, passed={report.passed_count}, failed={report.failed_count}")
for r in report.results:
    if not r.success:
        print(f"[{r.validator_name}]")
        for e in r.errors:
            print(f"  - {e.message}")

# Run a subset of plugins by name
subset = validator.run_plugins(["<PLUGIN-NAME>"])
print(f"Subset failed: {subset.failed_count}")

# List available plugin names
from csaf_lib.validation.validator import Validator
print(Validator.get_available_plugins())
```

**Documentation:**
- [Reading Documents](docs/csafvex-usage.md) - Detailed guide for parsing and accessing CSAF VEX data
- [Creating Documents](docs/creating-documents.md) - Complete guide for creating CSAF VEX documents with the fluent API

## Verification

The library provides comprehensive verification of CSAF VEX documents through two test sets:

- **Test Set 1 (CSAF Compliance)**: 14 tests verifying VEX Profile conformance and CSAF mandatory requirements
- **Test Set 2 (Data Type Checks)**: 16 tests verifying data format compliance, patterns, and schema constraints

### Using the Verifier

```python
from csaf_lib.verification import Verifier

# Create verifier from a file
verifier = Verifier.from_file("path/to/vex.json")

# Run all verification tests
report = verifier.run_all()

# Check results
if report.passed:
    print("All verification tests passed!")
else:
    print(f"Failed: {report.failed_count}/{report.total_tests}")
    for failure in report.failures:
        print(f"  {failure.test_id}: {failure.message}")

# Run specific test sets
csaf_report = verifier.run_csaf_compliance()   # Test Set 1 only
data_report = verifier.run_data_type_checks()  # Test Set 2 only

# Run individual tests
result = verifier.run_test("1.1")  # VEX Profile Conformance
result = verifier.run_test("2.5")  # CVE ID Format

# Get available tests
tests = Verifier.get_available_tests()
for test_id, test_name in tests.items():
    print(f"{test_id}: {test_name}")
```

### Verification Test Reference

| ID | Test Name | Description |
|----|-----------|-------------|
| 1.1 | VEX Profile Conformance | Document must have csaf_vex category and required sections |
| 1.2 | Base Mandatory Fields | Required tracking, publisher, and title fields |
| 1.3 | VEX Product Status Existence | Each vulnerability must have a product status |
| 1.4 | Vulnerability ID Existence | Each vulnerability must have CVE or IDs |
| 1.5 | Vulnerability Notes Existence | Each vulnerability must have notes |
| 1.6 | Product ID Definition (Missing) | All referenced product_ids must be defined |
| 1.7 | Product ID Definition (Multiple) | No duplicate product_id definitions |
| 1.8 | Circular Reference Check | No circular dependencies in relationships |
| 1.9 | Contradicting Product Status | Products cannot have conflicting statuses |
| 1.10 | Action Statement Requirement | known_affected products need remediations |
| 1.11 | Impact Statement Requirement | known_not_affected products need justification |
| 1.12 | Remediation Product Reference | Remediations must reference products |
| 1.13 | Flag Product Reference | Flags must reference products |
| 1.14 | Unique VEX Justification | Products can only have one VEX justification |
| 2.1 | JSON Schema Validation | Validates against CSAF 2.0 JSON schema |
| 2.2 | PURL Format | Package URL format validation |
| 2.3 | CPE Format | CPE 2.2 and 2.3 format validation |
| 2.4 | Date-Time Format | ISO 8601/RFC 3339 format validation |
| 2.5 | CVE ID Format | CVE identifier format validation |
| 2.6 | CWE ID Format | CWE identifier format validation |
| 2.7 | Language Code Format | BCP 47/RFC 5646 language code validation |
| 2.8 | Version Range Prohibition | No version ranges in product_version names |
| 2.9 | Mixed Versioning Prohibition | Consistent versioning scheme |
| 2.10 | CVSS Syntax | CVSS object schema validation |
| 2.11 | CVSS Calculation | CVSS score range validation |
| 2.12 | CVSS Vector Consistency | CVSS properties must match vectorString |
| 2.13 | File Size Soft Limit | Document should not exceed 15 MB |
| 2.14 | Array Length Soft Limit | Arrays should not exceed 100,000 items |
| 2.15 | String Length Soft Limit | Strings should not exceed field-specific limits |

## Contributing

Interested in contributing? Check out:
- [DEVELOP.md](DEVELOP.md) - Development setup, workflow, and contribution guidelines
- [RELEASE.md](RELEASE.md) - Release process for maintainers

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Authors

- Jakub Frejlach (jfrejlac@redhat.com)
- Juan Perez de Algaba (jperezde@redhat.com)
- George Vauter (gvauter@redhat.com)
- Daniel Monzonis (dmonzoni@redhat.com)

Developed by Red Hat Product Security.
