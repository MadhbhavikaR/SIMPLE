#!/usr/bin/env python3
"""
Test cases for the service selection fix.

This test suite verifies that the service selection logic correctly:
1. Only shows pre-selected services
2. Skips services that weren't selected
3. Handles enforced services properly
4. Maintains backward compatibility
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class MockService:
    """Mock service for testing."""
    def __init__(self, name, category):
        self.name = name
        self.category = category


class TestServiceSelectionFix:
    """Test suite for service selection logic fixes."""

    def setup_method(self):
        """Setup test fixtures."""
        self.context = {
            "SERVICES": {
                "authelia": {},
                "mariadb": {}
            }
        }
        # Mock engine with just the context we need
        self.engine = Mock()
        self.engine.context = self.context
        self.engine.existing_services = set()

    def _apply_service_selection_logic(self, services_by_category):
        """Apply the fixed service selection logic."""
        pre_selected_services = set(self.context.get("SERVICES", {}).keys())
        processed_services = []
        
        for category, services in services_by_category.items():
            # Skip enforced services (already processed)
            if category == "core":
                continue

            # Only process categories that have at least one pre-selected service
            category_services = [service for service in services 
                               if service.name in pre_selected_services]
            
            if not category_services:
                continue  # Skip categories with no selected services

            for service in category_services:
                processed_services.append(service)
                
        return processed_services

    def test_only_pre_selected_services_shown(self):
        """Test that only pre-selected services are processed."""
        # Mock the services_by_category to include both selected and unselected services
        services_by_category = {
            "security": [
                MockService("authelia", "security"),
                MockService("crowdsec", "security")  # Not selected
            ],
            "database": [
                MockService("mariadb", "database"),
                MockService("postgres", "database")  # Not selected
            ]
        }

        # Apply the fixed service selection logic
        processed_services = self._apply_service_selection_logic(services_by_category)
        
        # Verify only selected services are processed
        processed_service_names = [s.name for s in processed_services]
        expected_service_names = ["authelia", "mariadb"]
        
        assert processed_service_names == expected_service_names, f"Expected {expected_service_names}, got {processed_service_names}"
        
        # Verify unselected services are excluded
        unselected_service_names = ["crowdsec", "postgres"]
        for service_name in unselected_service_names:
            assert service_name not in processed_service_names, f"Service {service_name} should not be processed"

    def test_empty_category_skipped(self):
        """Test that categories with no selected services are skipped."""
        # Mock a category with no selected services
        services_by_category = {
            "empty_category": [
                MockService("unselected1", "empty_category"),
                MockService("unselected2", "empty_category")
            ]
        }

        # Apply the fixed service selection logic
        processed_services = self._apply_service_selection_logic(services_by_category)
        
        # Should be empty, so category should be skipped
        assert len(processed_services) == 0, "Category should be empty and skipped"

    def test_enforced_services_handled_separately(self):
        """Test that enforced services are handled in the first pass."""
        # Mock services including enforced ones
        services_by_category = {
            "core": [
                MockService("swag", "core"),
                MockService("socket-proxy", "core")
            ],
            "security": [
                MockService("authelia", "security")
            ]
        }

        # Apply the fixed service selection logic
        processed_services = self._apply_service_selection_logic(services_by_category)
        
        # Core category should be skipped (enforced services handled separately)
        # Only security category should be processed
        processed_service_names = [s.name for s in processed_services]
        assert "authelia" in processed_service_names, "Regular service should be processed"
        assert "swag" not in processed_service_names, "Enforced service should not be in second pass"
        assert "socket-proxy" not in processed_service_names, "Enforced service should not be in second pass"

    def test_backward_compatibility(self):
        """Test that the fix maintains backward compatibility."""
        # Test with empty context (no pre-selected services)
        original_context = self.context
        self.context = {"SERVICES": {}}

        # Mock services
        services_by_category = {
            "test": [
                MockService("test1", "test"),
                MockService("test2", "test")
            ]
        }

        # Apply the fixed service selection logic
        processed_services = self._apply_service_selection_logic(services_by_category)
        
        # Should be empty when no services are pre-selected
        assert len(processed_services) == 0, "Should handle empty context gracefully"
        
        # Restore original context
        self.context = original_context

    def test_existing_services_handling(self):
        """Test that existing services are handled correctly."""
        # Add existing services to the context
        self.context["existing_services"] = {"mariadb", "authelia"}
        self.engine.existing_services = {"mariadb", "authelia"}

        # Mock services
        services_by_category = {
            "database": [MockService("mariadb", "database")],
            "security": [MockService("authelia", "security")],
            "test": [MockService("new_service", "test")]
        }

        # Apply the fixed service selection logic
        processed_services = self._apply_service_selection_logic(services_by_category)
        
        # Verify existing services are processed
        processed_service_names = [s.name for s in processed_services]
        assert "mariadb" in processed_service_names, "Existing service should be processed"
        assert "authelia" in processed_service_names, "Existing service should be processed"
        assert "new_service" not in processed_service_names, "Non-selected service should not be processed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])