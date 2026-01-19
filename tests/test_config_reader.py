import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.simple.config.config_reader import ConfigReader, TemplateType
from src.simple.config.dto.configuration import Configuration

class TestConfigReader:
    """Test cases for the ConfigReader class."""

    @pytest.fixture
    def config_reader(self):
        """Create a ConfigReader instance for testing."""
        return ConfigReader()

    def test_init(self, config_reader):
        """Test ConfigReader initialization."""
        assert config_reader.config_dir == Path("config")
        assert hasattr(config_reader, 'logger')

    @patch('src.simple.config.config_reader.yaml.safe_load')
    @patch('builtins.open')
    def test_read_yaml_config(self, mock_open, mock_yaml_load, config_reader):
        """Test reading YAML configuration."""
        mock_yaml_load.return_value = {'key': 'value'}
        mock_open.return_value.__enter__.return_value = MagicMock()

        result = config_reader.read_yaml_config('test')
        assert isinstance(result, Configuration)
        assert result.data == {'key': 'value'}

    @patch('src.simple.config.config_reader.jinja2.Template')
    @patch('src.simple.config.config_reader.Path.read_text')
    def test_read_template(self, mock_read_text, mock_template, config_reader):
        """Test reading and rendering template."""
        mock_read_text.return_value = "Hello {{ name }}"
        mock_template.return_value.render.return_value = "Hello World"

        result = config_reader.read_template('test', {'name': 'World'})
        assert result == "Hello World"

    def test_read_all_configs(self, config_reader):
        """Test reading all configurations."""
        with patch('src.simple.config.config_reader.Path.glob') as mock_glob:
            mock_glob.return_value = [Path('config1.yaml'), Path('config2.yaml')]
            with patch.object(config_reader, 'read_yaml_config') as mock_read:
                mock_read.side_effect = [
                    Configuration({'key1': 'value1'}),
                    Configuration({'key2': 'value2'})
                ]

                result = config_reader.read_all_configs()
                assert len(result) == 2
                assert 'config1' in result
                assert 'config2' in result

    def test_validate_template_vars(self, config_reader):
        """Test template variable validation."""
        template_content = "Hello {{ name }}"
        vars_dict = {'name': 'World'}

        result = config_reader.validate_template_vars('test', template_content, vars_dict)
        assert result is True

        # Test with missing variable
        template_content_missing = "Hello {{ name }} {{ missing }}"
        result_missing = config_reader.validate_template_vars('test', template_content_missing, vars_dict)
        assert result_missing is False

    def test_template_type_enum(self):
        """Test TemplateType enum."""
        assert TemplateType.NETWORK.value == "network"
        assert TemplateType.SERVICE.value == "service"
        assert TemplateType.ANCHOR.value == "anchor"
        assert TemplateType.NATIVE.value == "native"
