import pytest
from src.simple.config.service_definition import ServiceDefinition

class TestServiceDefinition:
    """Test cases for the ServiceDefinition class."""

    @pytest.fixture
    def service_meta(self):
        """Create sample service metadata."""
        return {
            'name': 'test-service',
            'category': 'test-category',
            'description': 'Test service description',
            'alternatives': ['default', 'alternative']
        }

    @pytest.fixture
    def service_definition(self, service_meta):
        """Create a ServiceDefinition instance for testing."""
        return ServiceDefinition('test-service', service_meta)

    def test_init(self, service_definition, service_meta):
        """Test ServiceDefinition initialization."""
        assert service_definition.name == 'test-service'
        assert service_definition.meta == service_meta

    def test_to_selection_label(self, service_definition):
        """Test conversion to selection label."""
        label = service_definition.to_selection_label()
        assert label == 'test-service (test-category)'

    def test_to_selection_label_no_category(self, service_meta):
        """Test conversion to selection label without category."""
        service_meta['category'] = None
        service_def = ServiceDefinition('test-service', service_meta)
        label = service_def.to_selection_label()
        assert label == 'test-service'
