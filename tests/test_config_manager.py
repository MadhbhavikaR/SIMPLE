import pytest
from unittest.mock import MagicMock, patch
from src.simple.config.config_manager_main import ConfigManager
from src.simple.config.config_reader import ConfigReader

class TestConfigManager:
    """Test cases for the ConfigManager class."""

    @pytest.fixture
    def mock_config_reader(self):
        """Create a mock ConfigReader for testing."""
        return MagicMock(spec=ConfigReader)

    @pytest.fixture
    def config_manager(self, mock_config_reader):
        """Create a ConfigManager instance for testing."""
        return ConfigManager(mock_config_reader)

    def test_init(self, config_manager, mock_config_reader):
        """Test ConfigManager initialization."""
        assert config_manager.config_reader == mock_config_reader
        assert hasattr(config_manager, 'logger')

    @patch('src.simple.config.config_manager_main.questionary.text')
    def test_prompt_non_root_user(self, mock_questionary_text, config_manager):
        """Test prompting for non-root user."""
        mock_questionary_text.return_value = 'testuser'
        config_manager._prompt_non_root_user()
        mock_questionary_text.assert_called_once()

    @patch('src.simple.config.config_manager_main.questionary.path')
    def test_prompt_storage_mount(self, mock_questionary_path, config_manager):
        """Test prompting for storage mount."""
        mock_questionary_path.return_value = '/mnt/storage'
        config_manager._prompt_storage_mount()
        mock_questionary_path.assert_called_once()

    @patch('src.simple.config.config_manager_main.questionary.path')
    def test_prompt_base_path_selection(self, mock_questionary_path, config_manager):
        """Test prompting for base path selection."""
        mock_questionary_path.return_value = '/opt/simple'
        config_manager._prompt_base_path_selection()
        mock_questionary_path.assert_called_once()

    @patch('src.simple.config.config_manager_main.questionary.path')
    def test_prompt_volumes_location(self, mock_questionary_path, config_manager):
        """Test prompting for volumes location."""
        mock_questionary_path.return_value = '/opt/simple/volumes'
        config_manager._prompt_volumes_location()
        mock_questionary_path.assert_called_once()

    @patch('src.simple.config.config_manager_main.questionary.path')
    def test_prompt_docker_files_location(self, mock_questionary_path, config_manager):
        """Test prompting for docker files location."""
        mock_questionary_path.return_value = '/opt/simple/docker'
        config_manager._prompt_docker_files_location()
        mock_questionary_path.assert_called_once()

    @patch('src.simple.config.config_manager_main.questionary.path')
    def test_prompt_scripts_location(self, mock_questionary_path, config_manager):
        """Test prompting for scripts location."""
        mock_questionary_path.return_value = '/opt/simple/scripts'
        config_manager._prompt_scripts_location()
        mock_questionary_path.assert_called_once()

    @patch('src.simple.config.config_manager_main.questionary.confirm')
    @patch('src.simple.config.config_manager_main.questionary.text')
    def test_prompt_network_config(self, mock_questionary_text, mock_questionary_confirm, config_manager):
        """Test prompting for network configuration."""
        mock_questionary_confirm.return_value = True
        mock_questionary_text.return_value = '192.168.1.0/24'
        config_manager._prompt_network_config()
        mock_questionary_confirm.assert_called_once()
        mock_questionary_text.assert_called_once()

    @patch('src.simple.config.config_manager_main.questionary.checkbox')
    def test_prompt_services_selection(self, mock_questionary_checkbox, config_manager):
        """Test prompting for services selection."""
        mock_questionary_checkbox.return_value = ['service1', 'service2']
        config_manager._prompt_services_selection()
        mock_questionary_checkbox.assert_called_once()

    def test_build_service_runtime_map(self, config_manager):
        """Test building service runtime map."""
        services = [
            MagicMock(name='service1', category='category1'),
            MagicMock(name='service2', category='category2')
        ]
        result = config_manager._build_service_runtime_map(services)
        assert len(result) == 2
        assert 'service1' in result
        assert 'service2' in result

    def test_detect_system(self, config_manager):
        """Test system detection."""
        config_manager.detect_system()
        # This method should set system properties
        assert hasattr(config_manager, 'system_info')

    def test_generate_password(self, config_manager):
        """Test password generation."""
        password = config_manager.generate_password()
        assert len(password) == 32
        assert any(c in '!@#$%^&*()' for c in password)

        short_password = config_manager.generate_password(16, False)
        assert len(short_password) == 16
        assert all(c.isalnum() for c in short_password)

    @patch('src.simple.config.config_manager_main.yaml.safe_dump')
    @patch('builtins.open')
    def test_save_settings(self, mock_open, mock_yaml_dump, config_manager):
        """Test saving settings."""
        config_manager._save_settings()
        mock_yaml_dump.assert_called_once()
        mock_open.assert_called_once()
