import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.simple.config.service_repository import ServiceRepository
from src.simple.config.service_definition import ServiceDefinition

class TestServiceRepository:
    """Test cases for the ServiceRepository class."""

    @pytest.fixture
    def mock_config_reader(self):
        """Create a mock ConfigReader for testing."""
        return MagicMock()

    @pytest.fixture
    def service_repository(self, mock_config_reader):
        """Create a ServiceRepository instance for testing."""
        return ServiceRepository(mock_config_reader)

    def test_init(self, service_repository, mock_config_reader):
        """Test ServiceRepository initialization."""
        assert service_repository.config_reader == mock_config_reader
        assert service_repository.templates_dir == Path("templates")

    @patch('src.simple.config.service_repository.Path.glob')
    @patch('src.simple.config.service_repository.yaml.safe_load')
    def test_discover_services(self, mock_yaml_load, mock_glob, service_repository):
        """Test service discovery."""
        # Mock template files
        mock_glob.return_value = [
            Path('templates/services/service1/about.yaml'),
            Path('templates/services/service2/about.yaml')
        ]

        # Mock YAML content
        mock_yaml_load.side_effect = [
            {'name': 'service1', 'category': 'category1'},
            {'name': 'service2', 'category': 'category2'}
        ]

        services = service_repository.discover_services()
        assert len(services) == 2
        assert all(isinstance(s, ServiceDefinition) for s in services)
        assert services[0].name == 'service1'
        assert services[1].name == 'service2'
