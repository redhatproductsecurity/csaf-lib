"""Data models for CSAF VEX."""

from csaf_lib.models.common import Acknowledgment, Note, Reference
from csaf_lib.models.csafvex import CSAFVEX
from csaf_lib.models.document import Document
from csaf_lib.models.product_tree import (
    Branch,
    FullProductName,
    ProductTree,
    Relationship,
)
from csaf_lib.models.vulnerability import (
    CWE,
    ID,
    Flag,
    Involvement,
    ProductStatus,
    Remediation,
    Score,
    Threat,
    Vulnerability,
)

__all__ = [
    "CSAFVEX",
    "CWE",
    "ID",
    "Acknowledgment",
    "Branch",
    "Document",
    "Flag",
    "FullProductName",
    "Involvement",
    "Note",
    "ProductStatus",
    "ProductTree",
    "Reference",
    "Relationship",
    "Remediation",
    "Score",
    "Threat",
    "Vulnerability",
]
