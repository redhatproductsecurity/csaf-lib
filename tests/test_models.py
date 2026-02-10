"""Tests for CSAF VEX model serialization and deserialization."""

from deepdiff import DeepDiff

from csaf_lib.models import CSAFVEX


class TestModelRoundTrip:
    """Test round-trip serialization: dict -> model -> dict."""

    def test_minimal_vex_roundtrip(self, minimal_vex):
        """Test round-trip with minimal VEX document."""
        csafvex = CSAFVEX.from_dict(minimal_vex)

        assert csafvex.document is not None
        assert csafvex.document.category == "csaf_vex"

        result = csafvex.to_dict()

        assert result["document"]["category"] == minimal_vex["document"]["category"]
        assert result["document"]["title"] == minimal_vex["document"]["title"]

    def test_sample_vex_roundtrip(self, sample_vex):
        """Test round-trip with sample VEX document."""
        csafvex = CSAFVEX.from_dict(sample_vex)

        assert csafvex.document is not None

        result = csafvex.to_dict()

        assert result["document"]["category"] == sample_vex["document"]["category"]

        if sample_vex.get("product_tree"):
            assert "product_tree" in result or csafvex.product_tree is None

        if csafvex.vulnerabilities:
            assert "vulnerabilities" in result
            assert len(result["vulnerabilities"]) == len(csafvex.vulnerabilities)

    def test_cve_2023_20593_roundtrip(self, cve_2023_20593):
        """Test round-trip with real-world CVE document using DeepDiff."""
        csafvex = CSAFVEX.from_dict(cve_2023_20593)
        result = csafvex.to_dict()

        diff = DeepDiff(
            cve_2023_20593, result, ignore_order=False, exclude_regex_paths=[r".*date.*"]
        )

        assert not diff, f"Diff should be empty: {diff}"


class TestEmptyListFiltering:
    """Test that empty lists are filtered out during serialization."""

    def test_empty_product_status_lists_omitted(self):
        """Test that empty product_status lists are omitted."""
        data = {
            "document": {
                "category": "csaf_vex",
                "csaf_version": "2.0",
                "title": "Test",
                "publisher": {
                    "category": "vendor",
                    "name": "Test",
                    "namespace": "https://test.com",
                },
                "tracking": {
                    "id": "TEST-001",
                    "status": "final",
                    "version": "1",
                    "initial_release_date": "2025-01-01T00:00:00Z",
                    "current_release_date": "2025-01-01T00:00:00Z",
                },
            },
            "vulnerabilities": [
                {
                    "cve": "CVE-2025-0001",
                    "product_status": {
                        "known_affected": ["PROD-001"],
                        "fixed": [],  # This should be omitted
                        "under_investigation": [],  # This should be omitted
                    },
                }
            ],
        }

        csafvex = CSAFVEX.from_dict(data)
        result = csafvex.to_dict()

        product_status = result["vulnerabilities"][0]["product_status"]
        assert "known_affected" in product_status
        assert "fixed" not in product_status
        assert "under_investigation" not in product_status

    def test_empty_vulnerabilities_omitted(self):
        """Test that empty vulnerabilities list is omitted."""
        data = {
            "document": {
                "category": "csaf_vex",
                "csaf_version": "2.0",
                "title": "Test",
                "publisher": {
                    "category": "vendor",
                    "name": "Test",
                    "namespace": "https://test.com",
                },
                "tracking": {
                    "id": "TEST-001",
                    "status": "final",
                    "version": "1",
                    "initial_release_date": "2025-01-01T00:00:00Z",
                    "current_release_date": "2025-01-01T00:00:00Z",
                },
            },
            "vulnerabilities": [],
        }

        csafvex = CSAFVEX.from_dict(data)
        result = csafvex.to_dict()

        assert "vulnerabilities" not in result


class TestEmptyDictHandling:
    """Test that empty dicts are not treated as None/falsy."""

    def test_empty_product_tree_dict_creates_object(self):
        """Empty product_tree dict should create object, not be skipped as None."""
        data = {
            "document": {
                "category": "csaf_vex",
                "csaf_version": "2.0",
                "title": "Test",
                "publisher": {
                    "category": "vendor",
                    "name": "Test",
                    "namespace": "https://test.com",
                },
                "tracking": {
                    "id": "TEST-001",
                    "status": "final",
                    "version": "1",
                    "initial_release_date": "2025-01-01T00:00:00Z",
                    "current_release_date": "2025-01-01T00:00:00Z",
                },
            },
            "product_tree": {},  # Empty dict should be processed, not treated as falsy
        }
        csafvex = CSAFVEX.from_dict(data)
        assert csafvex.product_tree is not None

    def test_missing_product_tree_is_none(self):
        """Missing product_tree key should result in None."""
        data = {
            "document": {
                "category": "csaf_vex",
                "csaf_version": "2.0",
                "title": "Test",
                "publisher": {
                    "category": "vendor",
                    "name": "Test",
                    "namespace": "https://test.com",
                },
                "tracking": {
                    "id": "TEST-001",
                    "status": "final",
                    "version": "1",
                    "initial_release_date": "2025-01-01T00:00:00Z",
                    "current_release_date": "2025-01-01T00:00:00Z",
                },
            },
            # product_tree key is missing
        }
        csafvex = CSAFVEX.from_dict(data)
        assert csafvex.product_tree is None

    def test_empty_product_status_dict_creates_object(self):
        """Empty product_status dict should create object, not be skipped."""
        from csaf_lib.models.vulnerability import Vulnerability

        data = {"cve": "CVE-2025-0001", "product_status": {}}
        vuln = Vulnerability.from_dict(data)
        assert vuln.product_status is not None

    def test_missing_product_status_is_none(self):
        """Missing product_status key should result in None."""
        from csaf_lib.models.vulnerability import Vulnerability

        data = {"cve": "CVE-2025-0001"}
        vuln = Vulnerability.from_dict(data)
        assert vuln.product_status is None


class TestBranchesFieldOrdering:
    """Test that branches field appears last in Branch objects for better readability."""

    def test_branch_branches_after_name(self):
        """Test that branches comes after name in Branch objects."""
        from csaf_lib.models.product_tree import Branch

        branch = Branch.from_dict(
            {
                "name": "ACME",
                "category": "vendor",
                "branches": [{"category": "product_name", "name": "Widget"}],
            }
        )
        result = branch.to_dict()
        keys = list(result.keys())

        assert keys == ["category", "name", "branches"]

    def test_product_tree_alphabetical_order(self):
        """Test that ProductTree uses alphabetical order (branches before relationships)."""
        from csaf_lib.models.product_tree import ProductTree

        tree = ProductTree.from_dict(
            {
                "branches": [{"category": "vendor", "name": "ACME"}],
                "relationships": [
                    {
                        "category": "default_component_of",
                        "product_reference": "PROD-1",
                        "relates_to_product_reference": "PROD-2",
                        "full_product_name": {"product_id": "PROD-3", "name": "Test"},
                    }
                ],
            }
        )
        result = tree.to_dict()
        keys = list(result.keys())

        assert keys == ["branches", "relationships"]


class TestListSorting:
    """Test that lists are sorted deterministically during serialization."""

    def test_branches_sorted_by_name(self):
        """Test that branches are sorted alphabetically by name."""
        from csaf_lib.models.product_tree import ProductTree

        tree = ProductTree.from_dict(
            {
                "branches": [
                    {"category": "vendor", "name": "Zebra Corp"},
                    {"category": "vendor", "name": "Acme Inc"},
                    {"category": "vendor", "name": "MegaCorp"},
                ],
            }
        )
        result = tree.to_dict()
        names = [b["name"] for b in result["branches"]]

        assert names == ["Acme Inc", "MegaCorp", "Zebra Corp"]

    def test_string_lists_sorted(self):
        """Test that plain string lists are sorted lexicographically."""
        from csaf_lib.models.vulnerability import ProductStatus, Vulnerability

        vuln = Vulnerability(
            cve="CVE-2025-0001",
            product_status=ProductStatus(
                known_affected=["prod-c", "prod-a", "PROD-B"],
            ),
        )
        result = vuln.to_dict()
        products = result["product_status"]["known_affected"]

        # Case-insensitive sort
        assert products == ["prod-a", "PROD-B", "prod-c"]

    def test_vulnerabilities_sorted_by_cve(self):
        """Test that vulnerabilities are sorted by CVE."""
        data = {
            "document": {
                "category": "csaf_vex",
                "csaf_version": "2.0",
                "title": "Test",
                "publisher": {
                    "category": "vendor",
                    "name": "Test",
                    "namespace": "https://test.com",
                },
                "tracking": {
                    "id": "TEST-001",
                    "status": "final",
                    "version": "1",
                    "initial_release_date": "2025-01-01T00:00:00Z",
                    "current_release_date": "2025-01-01T00:00:00Z",
                },
            },
            "vulnerabilities": [
                {"cve": "CVE-2025-0003"},
                {"cve": "CVE-2025-0001"},
                {"cve": "CVE-2025-0002"},
            ],
        }

        csafvex = CSAFVEX.from_dict(data)
        result = csafvex.to_dict()
        cves = [v["cve"] for v in result["vulnerabilities"]]

        assert cves == ["CVE-2025-0001", "CVE-2025-0002", "CVE-2025-0003"]

    def test_notes_sorted_by_title_then_category(self):
        """Test that notes use title as primary sort key, category as fallback."""
        from csaf_lib.models.common import Note
        from csaf_lib.models.enums import NoteCategory

        notes = [
            Note(category=NoteCategory.DESCRIPTION, text="Text 1", title=None),
            Note(category=NoteCategory.SUMMARY, text="Text 2", title="Alpha"),
            Note(category=NoteCategory.DETAILS, text="Text 3", title=None),
            Note(category=NoteCategory.GENERAL, text="Text 4", title="Beta"),
        ]

        # Simulate serialization through a parent object
        from csaf_lib.models.document import Document

        doc = Document(
            category="csaf_vex",
            csaf_version="2.0",
            title="Test",
            notes=notes,
        )
        result = doc.to_dict()
        note_keys = [(n.get("title"), n.get("category")) for n in result["notes"]]

        # Expected order: "Alpha", "Beta", then by category (description before details)
        assert note_keys == [
            ("Alpha", "summary"),
            ("Beta", "general"),
            (None, "description"),
            (None, "details"),
        ]

    def test_nested_branches_sorted(self):
        """Test that deeply nested branches are all sorted by category then name."""
        from csaf_lib.models.product_tree import ProductTree

        tree = ProductTree.from_dict(
            {
                "branches": [
                    {
                        "category": "vendor",
                        "name": "Zebra",
                        "branches": [
                            {"category": "product_name", "name": "Widget B"},
                            {"category": "product_name", "name": "Widget A"},
                        ],
                    },
                    {
                        "category": "vendor",
                        "name": "Acme",
                        "branches": [
                            {"category": "product_name", "name": "Gadget Z"},
                            {"category": "product_name", "name": "Gadget A"},
                        ],
                    },
                ],
            }
        )
        result = tree.to_dict()

        # Top-level branches sorted (same category, so sorted by name)
        assert result["branches"][0]["name"] == "Acme"
        assert result["branches"][1]["name"] == "Zebra"

        # Nested branches sorted
        assert result["branches"][0]["branches"][0]["name"] == "Gadget A"
        assert result["branches"][0]["branches"][1]["name"] == "Gadget Z"
        assert result["branches"][1]["branches"][0]["name"] == "Widget A"
        assert result["branches"][1]["branches"][1]["name"] == "Widget B"

    def test_branches_sorted_by_category_then_name(self):
        """Test that branches are sorted by category first, then by name."""
        from csaf_lib.models.product_tree import ProductTree

        tree = ProductTree.from_dict(
            {
                "branches": [
                    {
                        "category": "vendor",
                        "name": "Acme",
                        "branches": [
                            {"category": "product_version", "name": "2.0"},
                            {"category": "product_name", "name": "Widget"},
                            {"category": "product_version", "name": "1.0"},
                            {"category": "product_name", "name": "Gadget"},
                        ],
                    },
                    {
                        "category": "product_family",
                        "name": "Enterprise",
                    },
                ],
            }
        )
        result = tree.to_dict()

        # Top-level: product_family < vendor (alphabetical category)
        assert result["branches"][0]["category"] == "product_family"
        assert result["branches"][0]["name"] == "Enterprise"
        assert result["branches"][1]["category"] == "vendor"
        assert result["branches"][1]["name"] == "Acme"

        # Nested: product_name < product_version, then by name within each category
        nested = result["branches"][1]["branches"]
        assert nested[0]["category"] == "product_name"
        assert nested[0]["name"] == "Gadget"
        assert nested[1]["category"] == "product_name"
        assert nested[1]["name"] == "Widget"
        assert nested[2]["category"] == "product_version"
        assert nested[2]["name"] == "1.0"
        assert nested[3]["category"] == "product_version"
        assert nested[3]["name"] == "2.0"

    def test_leaf_branches_sorted_by_product_id(self):
        """Test that leaf branches sort by product.product_id when available."""
        from csaf_lib.models.product_tree import ProductTree

        tree = ProductTree.from_dict(
            {
                "branches": [
                    {
                        "category": "vendor",
                        "name": "Acme",
                        "branches": [
                            {
                                "category": "product_name",
                                "name": "Widget",
                                "product": {
                                    "name": "Acme Widget",
                                    "product_id": "CSAFPID-0002",
                                },
                            },
                            {
                                "category": "product_name",
                                "name": "Gadget",
                                "product": {
                                    "name": "Acme Gadget",
                                    "product_id": "CSAFPID-0001",
                                },
                            },
                            {
                                "category": "product_name",
                                "name": "Alpha Tool",
                            },
                        ],
                    },
                ],
            }
        )
        result = tree.to_dict()
        nested = result["branches"][0]["branches"]

        # "Alpha Tool" has no product_id, sorts by name: "alpha tool"
        # "Gadget" has product_id "CSAFPID-0001", sorts by that
        # "Widget" has product_id "CSAFPID-0002", sorts by that
        # All share category "product_name", so sorted by name/product_id
        assert nested[0]["name"] == "Alpha Tool"
        assert nested[1]["name"] == "Gadget"
        assert nested[1]["product"]["product_id"] == "CSAFPID-0001"
        assert nested[2]["name"] == "Widget"
        assert nested[2]["product"]["product_id"] == "CSAFPID-0002"

    def test_revisions_sorted_by_number(self):
        """Test that revisions are sorted by number."""
        from csaf_lib.models.document import Revision, Tracking

        tracking = Tracking(
            id="TEST-001",
            status="final",
            version="3",
            revision_history=[
                Revision(date="2025-03-01T00:00:00Z", number="3", summary="Third"),
                Revision(date="2025-01-01T00:00:00Z", number="1", summary="First"),
                Revision(date="2025-02-01T00:00:00Z", number="2", summary="Second"),
            ],
        )
        result = tracking.to_dict()
        numbers = [r["number"] for r in result["revision_history"]]

        assert numbers == ["1", "2", "3"]

    def test_references_sorted_by_url(self):
        """Test that references are sorted by URL."""
        from csaf_lib.models.common import Reference

        refs = [
            Reference(summary="Third", url="https://z.example.com"),
            Reference(summary="First", url="https://a.example.com"),
            Reference(summary="Second", url="https://m.example.com"),
        ]

        from csaf_lib.models.document import Document

        doc = Document(
            category="csaf_vex",
            csaf_version="2.0",
            title="Test",
            references=refs,
        )
        result = doc.to_dict()
        urls = [r["url"] for r in result["references"]]

        assert urls == [
            "https://a.example.com",
            "https://m.example.com",
            "https://z.example.com",
        ]
