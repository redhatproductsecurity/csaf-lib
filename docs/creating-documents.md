# Creating CSAF VEX Documents

This guide shows how to create CSAF VEX documents using the fluent API.

## Quick Start

```python
from csaf_lib.models import (
    CSAFVEX,
    Document,
    ProductTree,
    Vulnerability,
    CSAFVersion,
    PublisherCategory,
    TrackingStatus,
    BranchCategory,
    RelationshipCategory,
    RemediationCategory,
    Revision,
)
from datetime import datetime, timezone

# Create document
doc = Document(
    category="csaf_vex",
    csaf_version=CSAFVersion.VERSION_2_0,
    title="Security Advisory for CVE-2025-0001"
)

doc.with_publisher(
    name="Red Hat Product Security",
    namespace="https://redhat.com",
    category=PublisherCategory.VENDOR,
    contact_details="security@redhat.com"
).with_tracking(
    id="CVE-2025-0001",
    status=TrackingStatus.FINAL,
    version="1",
    initial_release_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    current_release_date=datetime.now(timezone.utc),
    generator_engine_name="csaf-lib",
    generator_engine_version="0.1.0",
    generator_date=datetime.now(timezone.utc)
).add_tracking_revision(
    number="1",
    date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    summary="Initial version"
)

# Create product tree
tree = ProductTree()
vendor = tree.add_branch(BranchCategory.VENDOR, "Red Hat")

vendor.add_product_branch(
    category=BranchCategory.PRODUCT_NAME,
    name="RHEL-8",
    product_name="Red Hat Enterprise Linux 8",
    product_id="RHEL-8",
    helper_cpe="cpe:/o:redhat:enterprise_linux:8"
)

vendor.add_product_branch(
    category=BranchCategory.PRODUCT_VERSION,
    name="curl-1.0",
    product_name="curl version 1.0",
    product_id="curl-1.0",
    helper_purl="pkg:rpm/redhat/curl@1.0"
)

tree.add_relationship(
    category=RelationshipCategory.DEFAULT_COMPONENT_OF,
    product_reference="curl-1.0",
    relates_to_product_reference="RHEL-8",
    full_product_name="curl-1.0 as a component of RHEL-8",
    full_product_id="RHEL-8:curl-1.0"
)

# Create vulnerability
vuln = Vulnerability(
    cve="CVE-2025-0001",
    title="Security Advisory for CVE-2025-0001",
    discovery_date=datetime(2025, 1, 1, tzinfo=timezone.utc)
)

vuln.with_cwe(
    id="CWE-79",
    name="Cross-site Scripting"
).with_product_status(
    known_affected=["RHEL-8:curl-1.0"]
).add_remediation(
    category=RemediationCategory.VENDOR_FIX,
    details="Update to curl version 1.1",
    product_ids=["RHEL-8:curl-1.0"]
).add_score(
    products=["RHEL-8:curl-1.0"],
    cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N"
)

# Combine into CSAFVEX
vex = CSAFVEX(
    document=doc,
    product_tree=tree,
    vulnerabilities=[vuln]
)

# Save to file
import json
with open("vex.json", "w") as f:
    json.dump(vex.to_dict(), f, indent=2)
```

## Building Documents

### Document

The `Document` class represents the document metadata section.

#### Creating a Document

```python
from csaf_lib.models import Document, CSAFVersion

doc = Document(
    category="csaf_vex",
    csaf_version=CSAFVersion.VERSION_2_0,
    title="Security Advisory"
)
```

#### Setting Publisher

```python
from csaf_lib.models import PublisherCategory

doc.with_publisher(
    name="Red Hat Product Security",
    namespace="https://redhat.com",
    category=PublisherCategory.VENDOR,
    contact_details="security@redhat.com",
    issuing_authority="Red Hat Product Security is responsible..."
)
```

All parameters except `name` and `namespace` are optional.

#### Setting Tracking Information

```python
from csaf_lib.models import TrackingStatus, Revision
from datetime import datetime, timezone

doc.with_tracking(
    id="CVE-2025-0001",
    status=TrackingStatus.FINAL,
    version="1",
    initial_release_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    current_release_date=datetime.now(timezone.utc),
    generator_engine_name="csaf-lib",
    generator_engine_version="0.1.0",
    generator_date=datetime.now(timezone.utc),
    revision_history=[
        Revision(
            number="1",
            date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            summary="Initial version"
        )
    ]
)
```

Parameters with `generator_` prefix are flattened from the nested `Generator` object for transparency.

**Note on datetime parameters:** All datetime parameters accept either `datetime` objects or ISO 8601 format strings:

```python
# Using datetime objects
doc.with_tracking(
    initial_release_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    current_release_date=datetime.now(timezone.utc)
)

# Using ISO format strings
doc.with_tracking(
    initial_release_date="2025-01-01T00:00:00+00:00",
    current_release_date="2025-02-09T12:30:00Z"
)
```

#### Adding Revisions Incrementally

```python
doc.add_tracking_revision(
    number="2",
    date=datetime(2025, 2, 1, tzinfo=timezone.utc),
    summary="Updated version"
)
```

#### Setting Aggregate Severity

```python
doc.with_aggregate_severity(
    text="Critical",
    namespace="https://redhat.com/security/severity"
)
```

#### Setting Distribution

```python
from csaf_lib.models import TLPLabel

doc.with_distribution(
    text="Distribution is unlimited",
    tlp_label=TLPLabel.WHITE,
    tlp_url="https://www.first.org/tlp/"
)
```

The `tlp_` prefix shows these fields belong to the nested TLP object.

#### Adding Notes

```python
from csaf_lib.models import NoteCategory

doc.add_note(
    category=NoteCategory.GENERAL,
    text="This advisory covers multiple products",
    title="General Information"
)
```

#### Adding References

```python
from csaf_lib.models import ReferenceCategory

doc.add_reference(
    url="https://access.redhat.com/security/cve/CVE-2025-0001",
    summary="CVE details on Red Hat Security Portal",
    category=ReferenceCategory.EXTERNAL
)
```

### Product Tree

The `ProductTree` class represents the product tree structure.

#### Creating a Product Tree

```python
from csaf_lib.models import ProductTree

tree = ProductTree()
```

#### Adding Top-Level Branches

```python
from csaf_lib.models import BranchCategory

# Returns the branch for chaining
vendor = tree.add_branch(BranchCategory.VENDOR, "Red Hat")
```

#### Adding Product Branches (Leaf Nodes)

```python
# Add a product branch directly - creates a leaf node
vendor.add_product_branch(
    category=BranchCategory.PRODUCT_NAME,
    name="RHEL-8",  # Branch name
    product_name="Red Hat Enterprise Linux 8",  # Product name (can differ)
    product_id="RHEL-8",
    helper_cpe="cpe:/o:redhat:enterprise_linux:8"
)

vendor.add_product_branch(
    category=BranchCategory.PRODUCT_VERSION,
    name="curl-1.0",
    product_name="curl version 1.0",
    product_id="curl-1.0",
    helper_purl="pkg:rpm/redhat/curl@1.0"
)
```

#### Adding Nested Branches

For more complex hierarchies:

```python
# Add intermediate branch
family = vendor.add_branch(BranchCategory.PRODUCT_FAMILY, "RHEL")

# Add products under family
family.add_product_branch(
    category=BranchCategory.PRODUCT_VERSION,
    name="RHEL 8",
    product_name="Red Hat Enterprise Linux 8",
    product_id="RHEL-8",
    helper_cpe="cpe:/o:redhat:enterprise_linux:8"
)
```

#### Setting Product on Existing Branch

```python
# Create branch first
branch = vendor.add_branch(BranchCategory.PRODUCT_NAME, "RHEL-8")

# Later set product (makes it a leaf)
branch.with_product(
    name="Red Hat Enterprise Linux 8",
    product_id="RHEL-8",
    helper_cpe="cpe:/o:redhat:enterprise_linux:8"
)
```

#### Adding Relationships

```python
from csaf_lib.models import RelationshipCategory

tree.add_relationship(
    category=RelationshipCategory.DEFAULT_COMPONENT_OF,
    product_reference="curl-1.0",
    relates_to_product_reference="RHEL-8",
    full_product_name="curl-1.0 as a component of RHEL-8",
    full_product_id="RHEL-8:curl-1.0"
)
```

#### Branch/Product Mutual Exclusion

Branches enforce mutual exclusion between nested branches and products:

```python
branch = vendor.add_branch(BranchCategory.PRODUCT_FAMILY, "RHEL")

# This works - adding nested branches
branch.add_branch(BranchCategory.PRODUCT_VERSION, "RHEL 8")

# This will raise ValueError - cannot set product after adding branches
branch.with_product(name="...", product_id="...")  # Error!

# Similarly
leaf = vendor.add_branch(BranchCategory.PRODUCT_NAME, "RHEL-8")
leaf.with_product(name="...", product_id="...")  # OK - leaf node

# This will raise ValueError - cannot add branches after setting product
leaf.add_branch(BranchCategory.PRODUCT_VERSION, "8.0")  # Error!
```

### Vulnerability

The `Vulnerability` class represents vulnerability information.

#### Creating a Vulnerability

```python
from csaf_lib.models import Vulnerability
from datetime import datetime, timezone

vuln = Vulnerability(
    cve="CVE-2025-0001",
    title="Security Advisory for CVE-2025-0001",
    discovery_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    release_date=datetime(2025, 1, 15, tzinfo=timezone.utc)
)
```

#### Setting CWE

```python
vuln.with_cwe(
    id="CWE-79",
    name="Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')"
)
```

#### Setting Product Status

```python
vuln.with_product_status(
    known_affected=["RHEL-8:curl-1.0", "RHEL-9:curl-1.0"],
    fixed=["RHEL-8:curl-1.1", "RHEL-9:curl-1.1"],
    known_not_affected=["RHEL-7:curl-0.9"],
    under_investigation=["RHEL-10:curl-2.0"]
)
```

All parameters are optional - only provide the statuses you need.

#### Adding Remediations

```python
from csaf_lib.models import RemediationCategory
from datetime import datetime, timezone

vuln.add_remediation(
    category=RemediationCategory.VENDOR_FIX,
    details="Update to curl version 1.1 or later",
    date=datetime(2025, 1, 15, tzinfo=timezone.utc),
    product_ids=["RHEL-8:curl-1.0"],
    url="https://access.redhat.com/errata/RHSA-2025:0001"
)

vuln.add_remediation(
    category=RemediationCategory.MITIGATION,
    details="Disable network access for affected systems",
    product_ids=["RHEL-8:curl-1.0"]
)
```

#### Adding CVSS Scores

```python
vuln.add_score(
    products=["RHEL-8:curl-1.0"],
    cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N"
)

# Can also add CVSS v2
vuln.add_score(
    products=["RHEL-8:curl-1.0"],
    cvss_v2_vector="AV:N/AC:M/Au:N/C:P/I:P/A:N"
```

CVSS output verbosity can be controlled via `CVSSVerbosity` — set it on `CSAFVEX` to apply globally, or on individual `Score` objects. See [CVSS Verbosity](csafvex-usage.md#cvss-verbosity) for details.
```

#### Adding Flags

```python
from csaf_lib.models import FlagLabel

vuln.add_flag(
    label=FlagLabel.VULNERABLE_CODE_NOT_PRESENT,
    product_ids=["RHEL-7:curl-0.9"]
)

vuln.add_flag(
    label=FlagLabel.COMPONENT_NOT_PRESENT,
    product_ids=["RHEL-6:minimal-install"]
)
```

#### Adding Threats

```python
from csaf_lib.models import ThreatCategory

vuln.add_threat(
    category=ThreatCategory.IMPACT,
    details="Successful exploitation could lead to unauthorized access",
    product_ids=["RHEL-8:curl-1.0"]
)

vuln.add_threat(
    category=ThreatCategory.EXPLOIT_STATUS,
    details="Public exploits are available",
    product_ids=["RHEL-8:curl-1.0"]
)
```

#### Adding Notes

```python
from csaf_lib.models import NoteCategory

vuln.add_note(
    category=NoteCategory.DESCRIPTION,
    text="This vulnerability affects the SSL parsing module",
    title="Technical Details"
)

vuln.add_note(
    category=NoteCategory.SUMMARY,
    text="A critical XSS vulnerability was discovered in curl"
)
```

#### Adding References

```python
from csaf_lib.models import ReferenceCategory

vuln.add_reference(
    url="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-0001",
    summary="CVE-2025-0001 at MITRE",
    category=ReferenceCategory.EXTERNAL
)
```

#### Adding IDs

```python
vuln.add_id(
    system_name="Red Hat Bugzilla",
    text="BZ#123456"
)
```

## Complete Example

Here's a complete example creating a CSAF VEX document from scratch:

```python
from csaf_lib.models import (
    CSAFVEX,
    Document,
    ProductTree,
    Vulnerability,
    CSAFVersion,
    PublisherCategory,
    TrackingStatus,
    BranchCategory,
    RelationshipCategory,
    RemediationCategory,
    FlagLabel,
    NoteCategory,
    ReferenceCategory,
)
from datetime import datetime, timezone
import json

# Create Document
doc = Document(
    category="csaf_vex",
    csaf_version=CSAFVersion.VERSION_2_0,
    title="Red Hat Security Advisory: curl security update"
)

now = datetime.now(timezone.utc)
initial_date = datetime(2025, 1, 15, tzinfo=timezone.utc)

doc.with_publisher(
    name="Red Hat Product Security",
    namespace="https://redhat.com",
    category=PublisherCategory.VENDOR,
    contact_details="https://access.redhat.com/security/team/contact/",
    issuing_authority="Red Hat Product Security is responsible for vulnerability handling across all Red Hat products."
).with_tracking(
    id="CVE-2025-12345",
    status=TrackingStatus.FINAL,
    version="1",
    initial_release_date=initial_date,
    current_release_date=now,
    generator_engine_name="csaf-lib",
    generator_engine_version="0.1.0",
    generator_date=now
).add_tracking_revision(
    number="1",
    date=initial_date,
    summary="Initial version"
).with_aggregate_severity(
    text="Important",
    namespace="https://access.redhat.com/security/updates/classification/"
).add_note(
    category=NoteCategory.GENERAL,
    text="This advisory contains information about security vulnerabilities in curl"
)

# Create Product Tree
tree = ProductTree()
vendor = tree.add_branch(BranchCategory.VENDOR, "Red Hat")

# Add products
vendor.add_product_branch(
    category=BranchCategory.PRODUCT_NAME,
    name="RHEL-8",
    product_name="Red Hat Enterprise Linux 8",
    product_id="RHEL-8",
    helper_cpe="cpe:/o:redhat:enterprise_linux:8"
)

vendor.add_product_branch(
    category=BranchCategory.PRODUCT_VERSION,
    name="curl-7.61.1-22",
    product_name="curl-7.61.1-22.el8_6.4",
    product_id="curl-7.61.1-22",
    helper_purl="pkg:rpm/redhat/curl@7.61.1-22.el8_6.4?arch=x86_64"
)

vendor.add_product_branch(
    category=BranchCategory.PRODUCT_VERSION,
    name="curl-7.61.1-25",
    product_name="curl-7.61.1-25.el8_6.5",
    product_id="curl-7.61.1-25",
    helper_purl="pkg:rpm/redhat/curl@7.61.1-25.el8_6.5?arch=x86_64"
)

# Add relationships
tree.add_relationship(
    category=RelationshipCategory.DEFAULT_COMPONENT_OF,
    product_reference="curl-7.61.1-22",
    relates_to_product_reference="RHEL-8",
    full_product_name="curl-7.61.1-22 as a component of RHEL-8",
    full_product_id="RHEL-8:curl-7.61.1-22"
)

tree.add_relationship(
    category=RelationshipCategory.DEFAULT_COMPONENT_OF,
    product_reference="curl-7.61.1-25",
    relates_to_product_reference="RHEL-8",
    full_product_name="curl-7.61.1-25 as a component of RHEL-8",
    full_product_id="RHEL-8:curl-7.61.1-25"
)

# Create Vulnerability
vuln = Vulnerability(
    cve="CVE-2025-12345",
    title="curl: buffer overflow in SSL certificate parsing",
    discovery_date=datetime(2025, 1, 10, tzinfo=timezone.utc),
    release_date=initial_date
)

vuln.with_cwe(
    id="CWE-119",
    name="Improper Restriction of Operations within the Bounds of a Memory Buffer"
).with_product_status(
    known_affected=["RHEL-8:curl-7.61.1-22"],
    fixed=["RHEL-8:curl-7.61.1-25"]
).add_remediation(
    category=RemediationCategory.VENDOR_FIX,
    details="Update to curl-7.61.1-25.el8_6.5 or later",
    date=initial_date,
    product_ids=["RHEL-8:curl-7.61.1-22"],
    url="https://access.redhat.com/errata/RHSA-2025:0001"
).add_score(
    products=["RHEL-8:curl-7.61.1-22"],
    cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
).add_note(
    category=NoteCategory.DESCRIPTION,
    text="A buffer overflow vulnerability was found in curl's SSL certificate parsing code. A remote attacker could exploit this by providing a specially crafted certificate.",
    title="Vulnerability Description"
).add_note(
    category=NoteCategory.SUMMARY,
    text="An update for curl is now available for Red Hat Enterprise Linux 8."
).add_reference(
    url="https://access.redhat.com/security/cve/CVE-2025-12345",
    summary="CVE-2025-12345 on Red Hat Security Portal",
    category=ReferenceCategory.EXTERNAL
).add_reference(
    url="https://bugzilla.redhat.com/show_bug.cgi?id=123456",
    summary="Bug 123456 - curl: buffer overflow in SSL parsing",
    category=ReferenceCategory.EXTERNAL
)

# Create CSAFVEX
vex = CSAFVEX(
    document=doc,
    product_tree=tree,
    vulnerabilities=[vuln]
)

# Save to file
with open("RHSA-2025-0001.json", "w") as f:
    json.dump(vex.to_dict(), f, indent=2)

print("Created CSAF VEX document: RHSA-2025-0001.json")
```

## Method Chaining

All `with_*` and `add_*` methods return `self` to enable method chaining:

```python
doc = (Document(category="csaf_vex", title="Advisory")
    .with_publisher(name="...", namespace="...")
    .with_tracking(id="CVE-2025-0001", status=TrackingStatus.FINAL)
    .add_note(category=NoteCategory.GENERAL, text="...")
    .add_reference(url="...", summary="..."))
```

## Validation

The mutual exclusion between branches and products is enforced at runtime:

```python
branch = vendor.add_branch(BranchCategory.VENDOR, "Red Hat")
branch.add_branch(BranchCategory.PRODUCT_FAMILY, "RHEL")  # OK

# This will raise ValueError
branch.with_product(name="...", product_id="...")  # Error: branch already has nested branches
```

Similarly:

```python
branch = vendor.add_branch(BranchCategory.PRODUCT_NAME, "RHEL-8")
branch.with_product(name="...", product_id="...")  # OK - now a leaf

# This will raise ValueError
branch.add_branch(BranchCategory.PRODUCT_VERSION, "8.0")  # Error: branch already has a product
```
