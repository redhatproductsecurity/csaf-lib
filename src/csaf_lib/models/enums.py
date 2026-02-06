"""Enumerations for CSAF 2.0 specification fields.

These enums are derived from the CSAF 2.0 JSON schema and provide
type-safe, validated values for various categorical fields.
"""

from enum import Enum


class CSAFVersion(str, Enum):
    """Valid CSAF version values per CSAF 2.0 spec.

    Defines the version of the CSAF specification the document conforms to.
    """

    VERSION_2_0 = "2.0"


class PublisherCategory(str, Enum):
    """Valid publisher categories per CSAF 2.0 spec.

    Defines the category of the publisher releasing the document.
    """

    COORDINATOR = "coordinator"
    DISCOVERER = "discoverer"
    OTHER = "other"
    TRANSLATOR = "translator"
    USER = "user"
    VENDOR = "vendor"


class TrackingStatus(str, Enum):
    """Valid tracking status values per CSAF 2.0 spec.

    Defines the draft status of the document.
    """

    DRAFT = "draft"
    FINAL = "final"
    INTERIM = "interim"


class TLPLabel(str, Enum):
    """Traffic Light Protocol labels per CSAF 2.0 spec.

    Provides the TLP classification level of the document.
    See: https://www.first.org/tlp/
    """

    AMBER = "AMBER"
    GREEN = "GREEN"
    RED = "RED"
    WHITE = "WHITE"


class NoteCategory(str, Enum):
    """Valid note categories per CSAF 2.0 spec.

    Categorizes the type of note content.
    """

    DESCRIPTION = "description"
    DETAILS = "details"
    FAQ = "faq"
    GENERAL = "general"
    LEGAL_DISCLAIMER = "legal_disclaimer"
    OTHER = "other"
    SUMMARY = "summary"


class ReferenceCategory(str, Enum):
    """Valid reference categories per CSAF 2.0 spec.

    Indicates whether the reference points to the same document/vulnerability
    or to an external resource.
    """

    EXTERNAL = "external"
    SELF = "self"


class BranchCategory(str, Enum):
    """Valid branch categories per CSAF 2.0 spec.

    Describes the characteristics of the labeled branch in the product tree.
    """

    ARCHITECTURE = "architecture"
    HOST_NAME = "host_name"
    LANGUAGE = "language"
    LEGACY = "legacy"
    PATCH_LEVEL = "patch_level"
    PRODUCT_FAMILY = "product_family"
    PRODUCT_NAME = "product_name"
    PRODUCT_VERSION = "product_version"
    PRODUCT_VERSION_RANGE = "product_version_range"
    SERVICE_PACK = "service_pack"
    SPECIFICATION = "specification"
    VENDOR = "vendor"


class RelationshipCategory(str, Enum):
    """Valid relationship categories per CSAF 2.0 spec.

    Defines the category of relationship for the referenced component.
    """

    DEFAULT_COMPONENT_OF = "default_component_of"
    EXTERNAL_COMPONENT_OF = "external_component_of"
    INSTALLED_ON = "installed_on"
    INSTALLED_WITH = "installed_with"
    OPTIONAL_COMPONENT_OF = "optional_component_of"


class RemediationCategory(str, Enum):
    """Valid remediation categories per CSAF 2.0 spec.

    Specifies the category which this remediation belongs to.
    """

    MITIGATION = "mitigation"
    NO_FIX_PLANNED = "no_fix_planned"
    NONE_AVAILABLE = "none_available"
    VENDOR_FIX = "vendor_fix"
    WORKAROUND = "workaround"


class RestartCategory(str, Enum):
    """Valid restart categories per CSAF 2.0 spec.

    Specifies what category of restart is required for a remediation
    to become effective.
    """

    CONNECTED = "connected"
    DEPENDENCIES = "dependencies"
    MACHINE = "machine"
    NONE = "none"
    PARENT = "parent"
    SERVICE = "service"
    SYSTEM = "system"
    VULNERABLE_COMPONENT = "vulnerable_component"
    ZONE = "zone"


class FlagLabel(str, Enum):
    """Valid flag labels per CSAF 2.0 spec.

    Machine-readable labels for product-specific vulnerability information.
    """

    COMPONENT_NOT_PRESENT = "component_not_present"
    INLINE_MITIGATIONS_ALREADY_EXIST = "inline_mitigations_already_exist"
    VULNERABLE_CODE_CANNOT_BE_CONTROLLED_BY_ADVERSARY = (
        "vulnerable_code_cannot_be_controlled_by_adversary"
    )
    VULNERABLE_CODE_NOT_IN_EXECUTE_PATH = "vulnerable_code_not_in_execute_path"
    VULNERABLE_CODE_NOT_PRESENT = "vulnerable_code_not_present"


class ThreatCategory(str, Enum):
    """Valid threat categories per CSAF 2.0 spec.

    Categorizes the threat according to the rules of the specification.
    """

    EXPLOIT_STATUS = "exploit_status"
    IMPACT = "impact"
    TARGET_SET = "target_set"


class InvolvementParty(str, Enum):
    """Valid involvement party categories per CSAF 2.0 spec.

    Defines the category of the involved party.
    """

    COORDINATOR = "coordinator"
    DISCOVERER = "discoverer"
    OTHER = "other"
    USER = "user"
    VENDOR = "vendor"


class InvolvementStatus(str, Enum):
    """Valid involvement status values per CSAF 2.0 spec.

    Defines contact status of the involved party.
    """

    COMPLETED = "completed"
    CONTACT_ATTEMPTED = "contact_attempted"
    DISPUTED = "disputed"
    IN_PROGRESS = "in_progress"
    NOT_CONTACTED = "not_contacted"
    OPEN = "open"
