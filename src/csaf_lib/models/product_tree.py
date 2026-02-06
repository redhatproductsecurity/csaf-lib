"""Data models for the CSAF VEX product tree section."""

from typing import Any

import attrs
from packageurl import PackageURL

from csaf_lib.models.common import SerializableModel
from csaf_lib.models.enums import BranchCategory, RelationshipCategory

# @attrs.define
# class FileHash:
#     """Represents a cryptographic hash of a file."""
#     algorithm: str | None = attrs.field(default=None)
#     value: str | None = attrs.field(default=None)
#
#     @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "FileHash":
#         return cls(
#             algorithm=data.get("algorithm"),
#             value=data.get("value"),
#         )


# @attrs.define
# class CryptographicHashes:
#     """Contains cryptographic hashes to identify a file."""
#     file_hashes: list[FileHash] = attrs.field(factory=list)
#     filename: str | None = attrs.field(default=None)
#
#     @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "CryptographicHashes":
#         file_hashes_data = data.get("file_hashes", [])
#         return cls(
#             file_hashes=[FileHash.from_dict(h) for h in file_hashes_data],
#             filename=data.get("filename"),
#         )


# @attrs.define
# class GenericURI:
#     """Represents a generic URI identifier."""
#     namespace: str | None = attrs.field(default=None)
#     uri: str | None = attrs.field(default=None)
#
#     @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "GenericURI":
#         return cls(
#             namespace=data.get("namespace"),
#             uri=data.get("uri"),
#         )


@attrs.define
class ProductIdentificationHelper(SerializableModel):
    """Helper to identify a product using CPE or PURL."""

    # Fields we're currently using (all optional per CSAF spec)
    cpe: str | None = attrs.field(default=None)

    # Can be either a parsed PackageURL object or raw string (if parsing failed)
    purl: PackageURL | str | None = attrs.field(default=None)

    # hashes: list[CryptographicHashes] = attrs.field(factory=list)
    # model_numbers: list[str] = attrs.field(factory=list)
    # sbom_urls: list[str] = attrs.field(factory=list)
    # serial_numbers: list[str] = attrs.field(factory=list)
    # skus: list[str] = attrs.field(factory=list)
    # x_generic_uris: list[GenericURI] = attrs.field(factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProductIdentificationHelper":
        """Create a ProductIdentificationHelper from a dictionary.

        Attempts to parse purl strings using the packageurl library. If parsing fails,
        preserves the raw string data so validation can catch it later.
        """

        purl_data = data.get("purl")

        if purl_data and isinstance(purl_data, str):
            try:
                # Try to parse the purl string
                purl_value = PackageURL.from_string(purl_data)
            except Exception:
                # Parsing failed - keep raw string for validation to catch
                purl_value = purl_data
        else:
            purl_value = purl_data

        # hashes_data = data.get("hashes", [])
        # x_generic_uris_data = data.get("x_generic_uris", [])

        return cls(
            cpe=data.get("cpe"),
            purl=purl_value,
            # hashes=[CryptographicHashes.from_dict(h) for h in hashes_data],
            # model_numbers=data.get("model_numbers", []),
            # sbom_urls=data.get("sbom_urls", []),
            # serial_numbers=data.get("serial_numbers", []),
            # skus=data.get("skus", []),
            # x_generic_uris=[GenericURI.from_dict(u) for u in x_generic_uris_data],
        )


@attrs.define
class FullProductName(SerializableModel):
    """Specifies information about a product."""

    # Required fields per CSAF spec (nullable to allow parsing invalid documents)
    name: str | None = attrs.field(default=None)
    product_id: str | None = attrs.field(default=None)

    # Optional fields (CSAF spec order)
    product_identification_helper: ProductIdentificationHelper | None = attrs.field(default=None)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FullProductName":
        """Create a FullProductName from a dictionary."""
        helper_data = data.get("product_identification_helper")

        return cls(
            name=data.get("name"),
            product_id=data.get("product_id"),
            product_identification_helper=ProductIdentificationHelper.from_dict(helper_data)
            if helper_data is not None
            else None,
        )


@attrs.define
class Branch(SerializableModel):
    """Represents a branch in the hierarchical product tree structure."""

    # Required fields per CSAF spec (nullable to allow parsing invalid documents)
    category: BranchCategory | None = attrs.field(default=None)
    name: str | None = attrs.field(default=None)

    # Optional fields - note: must have either branches OR product (not both)
    branches: list["Branch"] = attrs.field(factory=list)
    product: FullProductName | None = attrs.field(default=None)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Branch":
        """Create a Branch from a dictionary."""
        branches_data = data.get("branches", [])
        product_data = data.get("product")
        category_str = data.get("category")

        return cls(
            category=BranchCategory(category_str) if category_str is not None else None,
            name=data.get("name"),
            branches=[Branch.from_dict(b) for b in branches_data],
            product=FullProductName.from_dict(product_data) if product_data is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict with branches field always last for better readability."""
        result = super().to_dict()
        if "branches" in result:
            branches_value = result.pop("branches")
            result["branches"] = branches_value
        return result

    def add_branch(self, category: BranchCategory, name: str) -> "Branch":
        """Add a nested branch and return it for chaining.

        Args:
            category: Branch category
            name: Branch name

        Returns:
            The created branch

        Raises:
            ValueError: If product is already set
        """
        if self.product is not None:
            raise ValueError(
                "Cannot add branches: this branch already has a product. "
                "Branch must have either branches OR product, not both."
            )
        branch = Branch(category=category, name=name)
        self.branches.append(branch)
        return branch

    def with_product(
        self,
        name: str,
        product_id: str,
        helper_cpe: str | None = None,
        helper_purl: str | None = None,
    ) -> "Branch":
        """Set the product for this branch (makes it a leaf node).

        Args:
            name: Product name
            product_id: Product ID
            helper_cpe: CPE identifier
            helper_purl: PURL identifier

        Returns:
            Self for method chaining

        Raises:
            ValueError: If branches already exist
        """
        if self.branches:
            raise ValueError(
                "Cannot set product: this branch already has nested branches. "
                "Branch must have either branches OR product, not both."
            )

        helper = None
        if helper_cpe is not None or helper_purl is not None:
            helper = ProductIdentificationHelper(cpe=helper_cpe, purl=helper_purl)

        self.product = FullProductName(
            name=name,
            product_id=product_id,
            product_identification_helper=helper,
        )
        return self

    def add_product_branch(
        self,
        category: BranchCategory,
        name: str,
        product_name: str,
        product_id: str,
        helper_cpe: str | None = None,
        helper_purl: str | None = None,
    ) -> "Branch":
        """Create and add a nested branch with a product (creates leaf node).

        Args:
            category: Branch category
            name: Branch name
            product_name: Product name
            product_id: Product ID
            helper_cpe: CPE identifier
            helper_purl: PURL identifier

        Returns:
            Self for method chaining

        Raises:
            ValueError: If product is already set
        """
        if self.product is not None:
            raise ValueError(
                "Cannot add branches: this branch already has a product. "
                "Branch must have either branches OR product, not both."
            )

        branch = Branch(category=category, name=name).with_product(
            name=product_name,
            product_id=product_id,
            helper_cpe=helper_cpe,
            helper_purl=helper_purl,
        )
        self.branches.append(branch)
        return self


@attrs.define
class Relationship(SerializableModel):
    """Establishes a relationship between two products."""

    # Required fields per CSAF spec (nullable to allow parsing invalid documents)
    category: RelationshipCategory | None = attrs.field(default=None)
    full_product_name: FullProductName | None = attrs.field(default=None)
    product_reference: str | None = attrs.field(default=None)
    relates_to_product_reference: str | None = attrs.field(default=None)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relationship":
        """Create a Relationship from a dictionary."""
        full_product_name_data = data.get("full_product_name")
        category_str = data.get("category")

        return cls(
            category=RelationshipCategory(category_str) if category_str is not None else None,
            full_product_name=FullProductName.from_dict(full_product_name_data)
            if full_product_name_data is not None
            else None,
            product_reference=data.get("product_reference"),
            relates_to_product_reference=data.get("relates_to_product_reference"),
        )


# @attrs.define
# class ProductGroup:
#     """Defines a logical group of products."""
#     group_id: str | None = attrs.field(default=None)
#     product_ids: list[str] = attrs.field(factory=list)
#     summary: str | None = attrs.field(default=None)
#
#     @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "ProductGroup":
#         return cls(
#             group_id=data.get("group_id"),
#             product_ids=data.get("product_ids", []),
#             summary=data.get("summary"),
#         )


@attrs.define
class ProductTree(SerializableModel):
    """Container for all fully qualified product names.

    Note: Validation of product tree structure is handled by the Verifier class
    which validates against the CSAF JSON schema.
    """

    # Fields we're currently using
    branches: list[Branch] = attrs.field(factory=list)
    relationships: list[Relationship] = attrs.field(factory=list)

    # full_product_names: list[FullProductName] = attrs.field(factory=list)
    # product_groups: list[ProductGroup] = attrs.field(factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProductTree":
        """Create a ProductTree from a dictionary.

        Args:
            data: The 'product_tree' section from parsed JSON
        """
        branches_data = data.get("branches", [])
        relationships_data = data.get("relationships", [])
        # full_product_names_data = data.get("full_product_names", [])
        # product_groups_data = data.get("product_groups", [])

        return cls(
            branches=[Branch.from_dict(b) for b in branches_data],
            relationships=[Relationship.from_dict(r) for r in relationships_data],
            # full_product_names=[FullProductName.from_dict(p) for p in full_product_names_data],
            # product_groups=[ProductGroup.from_dict(g) for g in product_groups_data],
        )

    def add_branch(self, category: BranchCategory, name: str) -> Branch:
        """Add a branch to the product tree and return it for chaining.

        Args:
            category: Branch category
            name: Branch name

        Returns:
            The created branch
        """
        branch = Branch(category=category, name=name)
        self.branches.append(branch)
        return branch

    def add_relationship(
        self,
        category: RelationshipCategory,
        product_reference: str,
        relates_to_product_reference: str,
        full_product_name: str,
        full_product_id: str,
        helper_cpe: str | None = None,
        helper_purl: str | None = None,
    ) -> "ProductTree":
        """Add a relationship between two products.

        Args:
            category: Relationship category
            product_reference: Product reference (component product ID)
            relates_to_product_reference: Related product reference (parent product ID)
            full_product_name: Full product name for the relationship
            full_product_id: Full product ID for the relationship
            helper_cpe: CPE identifier for the relationship product
            helper_purl: PURL identifier for the relationship product

        Returns:
            Self for method chaining
        """
        helper = None
        if helper_cpe is not None or helper_purl is not None:
            helper = ProductIdentificationHelper(cpe=helper_cpe, purl=helper_purl)

        relationship = Relationship(
            category=category,
            product_reference=product_reference,
            relates_to_product_reference=relates_to_product_reference,
            full_product_name=FullProductName(
                name=full_product_name,
                product_id=full_product_id,
                product_identification_helper=helper,
            ),
        )
        self.relationships.append(relationship)
        return self
