import pytest
from unittest.mock import MagicMock
from src.simple.core.container import ServiceStrategy

class TestServiceStrategy:
    """Test cases for the ServiceStrategy abstract base class."""

    class ConcreteServiceStrategy(ServiceStrategy):
        """Concrete implementation for testing."""

        def name(self) -> str:
            return "test-service"

        def category(self) -> str:
            return "test-category"

        def networks(self) -> list:
            return ["network1", "network2"]

        def get_required_secrets(self) -> list:
            return ["secret1", "secret2"]

        def generate_service_yaml(self, context: dict, dependencies: list = None) -> str:
            return "service_yaml_content"

        def get_volume_paths(self, context: dict) -> list:
            return ["/path/to/volume1", "/path/to/volume2"]

    @pytest.fixture
    def service_strategy(self):
        """Create a concrete ServiceStrategy instance for testing."""
        return self.ConcreteServiceStrategy()

    def test_abstract_methods(self, service_strategy):
        """Test that abstract methods are properly implemented."""
        assert service_strategy.name() == "test-service"
        assert service_strategy.category() == "test-category"
        assert service_strategy.networks() == ["network1", "network2"]
        assert service_strategy.get_required_secrets() == ["secret1", "secret2"]

    def test_generate_service_yaml(self, service_strategy):
        """Test service YAML generation."""
        context = {"key": "value"}
        result = service_strategy.generate_service_yaml(context)
        assert result == "service_yaml_content"

        # Test with dependencies
        result_with_deps = service_strategy.generate_service_yaml(context, ["dep1", "dep2"])
        assert result_with_deps == "service_yaml_content"

    def test_get_volume_paths(self, service_strategy):
        """Test volume path retrieval."""
        context = {"base_path": "/test"}
        result = service_strategy.get_volume_paths(context)
        assert result == ["/path/to/volume1", "/path/to/volume2"]
