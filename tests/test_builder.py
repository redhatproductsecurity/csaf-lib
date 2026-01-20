"""Tests for CSAF VEX builder."""

import pytest

from csaf_lib.builder import CSAFVEXBuilder


class TestBuilderEmptyValues:
    """Test that builder correctly handles empty values."""

    def test_builder_handles_empty_product_status(self):
        """Builder should accept empty product_status dict without treating it as falsy."""
        vex = CSAFVEXBuilder.build(
            cve_id="CVE-2025-0001",
            title="Test Advisory",
            document_data={
                "publisher": {"name": "Test", "namespace": "https://test.com"},
                "initial_release_date": "2025-01-01T00:00:00Z",
            },
            vulnerability_data={"product_status": {}},
        )
        assert vex.vulnerabilities[0].product_status is not None

    def test_builder_handles_empty_references_list(self):
        """Builder should accept empty references list."""
        vex = CSAFVEXBuilder.build(
            cve_id="CVE-2025-0001",
            title="Test Advisory",
            document_data={
                "publisher": {"name": "Test", "namespace": "https://test.com"},
                "initial_release_date": "2025-01-01T00:00:00Z",
            },
            vulnerability_data={"references": []},
        )
        assert vex.vulnerabilities[0].references == []

    def test_builder_handles_empty_products_list(self):
        """Builder should handle empty products list in product_tree_data."""
        vex = CSAFVEXBuilder.build(
            cve_id="CVE-2025-0001",
            title="Test Advisory",
            document_data={
                "publisher": {"name": "Test", "namespace": "https://test.com"},
                "initial_release_date": "2025-01-01T00:00:00Z",
            },
            product_tree_data={
                "name": "Test Vendor",
                "components": [],
                "streams": [],
                "products": [],
            },
        )
        assert vex.product_tree is not None

    @pytest.mark.parametrize(
        "parser,version,vector",
        [
            ("cvss_v2", "V2", "AV:N/AC:H/Au:S/C:P/I:N/A:N"),
            ("cvss_v3", "V3", "CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:N/A:N/E:P/RL:T/RC:U"),
        ],
    )
    def test_builder_handles_cvss_scores(self, parser, version, vector):
        """Builder should handle different CVSS score versions."""
        vex = CSAFVEXBuilder.build(
            cve_id="CVE-2025-0001",
            title="Test Advisory",
            document_data={
                "publisher": {"name": "Test", "namespace": "https://test.com"},
                "initial_release_date": "2025-01-01T00:00:00Z",
            },
            vulnerability_data={
                "score": {
                    "version": version,
                    "vector": vector,
                }
            },
        )

        assert getattr(vex.vulnerabilities[0].scores[0], parser) is not None
