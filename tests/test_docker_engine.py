import pytest
from unittest.mock import MagicMock, patch
from src.simple.engine import DockerEngine
from pathlib import Path

class TestDockerEngine:
    """Test cases for the DockerEngine class."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        return {
            'base_path': '/test/base',
            'volumes_path': '/test/volumes',
            'docker_files_path': '/test/docker',
            'scripts_path': '/test/scripts',
            'networks': {},
            'services': {},
            'secrets': {}
        }

    @pytest.fixture
    def docker_engine(self, mock_context):
        """Create a DockerEngine instance for testing."""
        return DockerEngine(mock_context)

    def test_init(self, docker_engine, mock_context):
        """Test DockerEngine initialization."""
        assert docker_engine.context == mock_context
        assert hasattr(docker_engine, 'logger')
        assert hasattr(docker_engine, 'config_file')
        assert hasattr(docker_engine, 'env_file')
        assert hasattr(docker_engine, 'compose_file')

    @patch('src.simple.engine.Path.mkdir')
    def test_setup_logging(self, mock_mkdir, docker_engine):
        """Test logging setup."""
        docker_engine._setup_logging()
        mock_mkdir.assert_called_once()

    @patch('src.simple.engine.yaml.safe_load')
    @patch('builtins.open')
    def test_load_existing_compose(self, mock_open, mock_yaml_load, docker_engine):
        """Test loading existing compose file."""
        mock_yaml_load.return_value = {'version': '3.8', 'services': {}}
        mock_open.return_value.__enter__.return_value = MagicMock()

        result = docker_engine._load_existing_compose()
        assert result == {'version': '3.8', 'services': {}}

    @patch('src.simple.engine.ServiceRepository')
    def test_load_dependencies(self, mock_service_repo, docker_engine):
        """Test loading service dependencies."""
        mock_repo = MagicMock()
        mock_service_repo.return_value = mock_repo
        mock_repo.discover_services.return_value = []

        docker_engine._load_dependencies()
        mock_service_repo.assert_called_once()
        mock_repo.discover_services.assert_called_once()

    def test_resolve_dependencies(self, docker_engine):
        """Test dependency resolution."""
        service_name = 'test-service'
        selected_services = {'service1', 'service2'}

        # Mock the service about data
        with patch.object(docker_engine, '_load_service_about_data') as mock_about:
            mock_about.return_value = {
                'dependencies': ['service1', 'service3']
            }

            result = docker_engine._resolve_dependencies(service_name, selected_services)
            assert 'service1' in result
            assert 'service3' in result
            assert 'service2' not in result

    def test_get_service_secrets(self, docker_engine):
        """Test getting service secrets."""
        service_name = 'test-service'

        # Mock the service about data
        with patch.object(docker_engine, '_load_service_about_data') as mock_about:
            mock_about.return_value = {
                'secrets': ['secret1', 'secret2']
            }

            result = docker_engine._get_service_secrets(service_name)
            assert result == ['secret1', 'secret2']

    @patch('src.simple.engine.questionary.select')
    def test_handle_service_with_alternatives(self, mock_select, docker_engine):
        """Test handling services with alternatives."""
        service = MagicMock()
        service.name.return_value = 'test-service'
        service.get_available_alternatives.return_value = [
            {'name': 'default', 'value': 'default'},
            {'name': 'alternative', 'value': 'alt'}
        ]

        # Mock questionary to return the first choice
        mock_select.return_value = 'default'

        docker_engine._handle_service_with_alternatives(service)
        mock_select.assert_called_once()

    @patch('src.simple.engine.questionary.confirm')
    def test_select_services(self, mock_confirm, docker_engine):
        """Test service selection."""
        # Mock user confirmation
        mock_confirm.return_value = False

        docker_engine.select_services(allow_incremental=False)
        mock_confirm.assert_called_once()

    def test_create_directories(self, docker_engine):
        """Test directory creation."""
        with patch('src.simple.engine.Path.mkdir') as mock_mkdir:
            docker_engine._create_directories()
            assert mock_mkdir.call_count == 4

    @patch('src.simple.engine.yaml.dump')
    @patch('builtins.open')
    def test_write_config_file(self, mock_open, mock_yaml_dump, docker_engine):
        """Test writing config file."""
        docker_engine._write_config_file()
        mock_yaml_dump.assert_called_once()
        mock_open.assert_called_once()

    @patch('src.simple.engine.yaml.dump')
    @patch('builtins.open')
    def test_write_env_file(self, mock_open, mock_yaml_dump, docker_engine):
        """Test writing env file."""
        docker_engine._write_env_file()
        mock_yaml_dump.assert_called_once()
        mock_open.assert_called_once()

    @patch('src.simple.engine.yaml.dump')
    @patch('builtins.open')
    def test_write_compose_file(self, mock_open, mock_yaml_dump, docker_engine):
        """Test writing compose file."""
        docker_engine._write_compose_file()
        mock_yaml_dump.assert_called_once()
        mock_open.assert_called_once()
