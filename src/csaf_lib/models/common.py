"""Common data models shared across CSAF VEX sections."""

from datetime import datetime
from enum import Enum
from typing import Any

import attrs
from cvss import CVSS2, CVSS3
from packageurl import PackageURL

from csaf_lib.models.enums import NoteCategory, ReferenceCategory
from csaf_lib.utils import format_datetime


class CVSSVerbosity(Enum):
    """CVSS output verbosity levels."""

    FULL = "full"  # All fields from as_json()
    MINIMAL = "minimal"  # Fields from as_json(minimal=True)
    REQUIRED = "required"  # Only fields required by the CVSS schema


_CVSS_REQUIRED_FIELDS = {"version", "vectorString", "baseScore", "baseSeverity"}

# Sort keys for list sorting during serialization
# Maps class name to (primary_key, fallback_key) or just primary_key
_LIST_SORT_KEYS: dict[str, str | tuple[str, str]] = {
    "Flag": "label",
    "Note": ("title", "category"),  # title first, category as fallback
    "Reference": "url",
    "Remediation": "category",
    "ID": "system_name",
    "Score": "products",  # First element of products list
    "Threat": "category",
    "Relationship": "product_reference",
    "Vulnerability": "cve",
    "Revision": "number",
    "Acknowledgment": "organization",
}


def _branch_sort_key(branch: Any) -> tuple[str, str]:
    """Sort key for Branch: sort by category first, then by product_id (leaf) or name."""
    category_val = branch.category.value if branch.category else ""
    if branch.product and branch.product.product_id:
        name_val = branch.product.product_id.lower()
    else:
        name_val = branch.name.lower() if branch.name else ""
    return (category_val, name_val)


# Custom sort key functions for types that need multi-field or conditional sorting.
# Maps class name to a callable that returns a sort key.
_CUSTOM_SORT_KEYS: dict[str, Any] = {
    "Branch": _branch_sort_key,
}


def _get_sort_key(item: Any) -> Any:
    """Extract a sort key from an item for list sorting."""
    # Plain strings - case-insensitive
    if isinstance(item, str):
        return item.lower()

    if item is None:
        return ""

    # Check for custom sort key function first
    class_name = type(item).__name__
    custom_fn = _CUSTOM_SORT_KEYS.get(class_name)
    if custom_fn is not None:
        return custom_fn(item)

    # Look up sort key by class name
    sort_config = _LIST_SORT_KEYS.get(class_name)

    if sort_config is None:
        return ""

    # Handle tuple (primary, fallback) config
    if isinstance(sort_config, tuple):
        primary_key, fallback_key = sort_config
        value = getattr(item, primary_key, None)
        if value is None:
            value = getattr(item, fallback_key, None)
    else:
        value = getattr(item, sort_config, None)

    if value is None:
        return ""

    # Enum -> extract value
    if isinstance(value, Enum):
        return value.value

    # List -> first element
    if isinstance(value, list):
        return value[0].lower() if value and isinstance(value[0], str) else ""

    # String -> lowercase
    if isinstance(value, str):
        return value.lower()

    return str(value)


def serialize_value(inst: type, field: attrs.Attribute, value: Any) -> Any:
    """Custom value serializer for attrs.asdict().

    Handles special types like datetime, CVSS objects, PackageURL, and Enum.
    """
    if value is None:
        return None

    # Handle Enum objects - convert to their string value
    if isinstance(value, Enum):
        return value.value

    # Handle datetime objects
    if isinstance(value, datetime):
        return format_datetime(value)

    # Handle PackageURL objects
    if isinstance(value, PackageURL):
        return value.to_string()

    # Handle CVSS objects - verbosity controlled by inst.cvss_verbosity
    if isinstance(value, (CVSS2, CVSS3)):
        verbosity = getattr(inst, "cvss_verbosity", CVSSVerbosity.MINIMAL)
        if verbosity == CVSSVerbosity.FULL:
            return value.as_json()
        result = value.as_json(minimal=True)
        if verbosity == CVSSVerbosity.REQUIRED:
            return {k: v for k, v in result.items() if k in _CVSS_REQUIRED_FIELDS}
        return result

    # Handle lists - sort and recursively process items
    if isinstance(value, list):
        if not value:
            return []

        # Plain string list - lexicographic case-insensitive sort
        if all(isinstance(x, str) for x in value):
            return sorted(value, key=lambda x: x.lower() if x else "")

        # Object list - sort by configured key, then serialize
        sorted_items = sorted(value, key=_get_sort_key)
        return [item.to_dict() if hasattr(item, "to_dict") else item for item in sorted_items]

    # Handle nested attrs objects
    if attrs.has(type(value)):
        return value.to_dict()

    # Handle plain dicts - sort keys recursively
    if isinstance(value, dict):
        return dict(sorted((key, serialize_value(inst, field, val)) for key, val in value.items()))

    # Return as-is for other types (str, int, etc.)
    return value


@attrs.define
class SerializableModel:
    """Base class for CSAF VEX models with serialization support."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, excluding None values and empty lists.

        Keys are sorted alphabetically for consistent output.
        """
        result = attrs.asdict(
            self,
            filter=lambda attr, value: value is not None
            and value != []
            and attr.metadata.get("export", True),
            value_serializer=serialize_value,
        )
        return dict(sorted(result.items()))


@attrs.define
class Note(SerializableModel):
    """Represents a note in the document or vulnerability."""

    # Required fields per CSAF spec (nullable to allow parsing invalid documents)
    category: NoteCategory | None = attrs.field(default=None)
    text: str | None = attrs.field(default=None)

    # Optional fields (CSAF spec order)
    title: str | None = attrs.field(default=None)

    # audience: str | None = attrs.field(default=None)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        """Create a Note from a dictionary."""
        category_str = data.get("category")
        return cls(
            category=NoteCategory(category_str) if category_str is not None else None,
            text=data.get("text"),
            title=data.get("title"),
            # audience=data.get("audience"),
        )


@attrs.define
class Reference(SerializableModel):
    """Represents a reference to external resources."""

    # Required fields per CSAF spec (nullable to allow parsing invalid documents)
    summary: str | None = attrs.field(default=None)
    url: str | None = attrs.field(default=None)

    # Optional fields (CSAF spec order)
    category: ReferenceCategory | None = attrs.field(default=None)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Reference":
        """Create a Reference from a dictionary."""
        category_str = data.get("category")
        return cls(
            summary=data.get("summary"),
            url=data.get("url"),
            category=ReferenceCategory(category_str) if category_str is not None else None,
        )


@attrs.define
class Acknowledgment(SerializableModel):
    """Represents an acknowledgment of contributors."""

    names: list[str] = attrs.field(factory=list)
    organization: str | None = attrs.field(default=None)
    summary: str | None = attrs.field(default=None)
    urls: list[str] = attrs.field(factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Acknowledgment":
        """Create an Acknowledgment from a dictionary."""
        return cls(
            names=data.get("names", []),
            organization=data.get("organization"),
            summary=data.get("summary"),
            urls=data.get("urls", []),
        )
