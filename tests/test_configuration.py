import pytest
from src.simple.config.dto.configuration import Configuration

class TestConfiguration:
    """Test cases for the Configuration class."""

    @pytest.fixture
    def config_data(self):
        """Create sample configuration data."""
        return {
            'key1': 'value1',
            'key2': 'value2',
            'nested': {
                'nested_key': 'nested_value'
            }
        }

    @pytest.fixture
    def configuration(self, config_data):
        """Create a Configuration instance for testing."""
        return Configuration(config_data)

    def test_init(self, configuration, config_data):
        """Test Configuration initialization."""
        assert configuration.data == config_data

    def test_get(self, configuration):
        """Test getting configuration values."""
        assert configuration.get('key1') == 'value1'
        assert configuration.get('nested.nested_key') == 'nested_value'
        assert configuration.get('nonexistent', 'default') == 'default'

    def test_set(self, configuration):
        """Test setting configuration values."""
        configuration.set('new_key', 'new_value')
        assert configuration.get('new_key') == 'new_value'

        configuration.set('nested.new_nested', 'new_nested_value')
        assert configuration.get('nested.new_nested') == 'new_nested_value'

    def test_has(self, configuration):
        """Test checking for configuration keys."""
        assert configuration.has('key1') is True
        assert configuration.has('nested.nested_key') is True
        assert configuration.has('nonexistent') is False

    def test_remove(self, configuration):
        """Test removing configuration keys."""
        configuration.remove('key1')
        assert configuration.has('key1') is False

        configuration.remove('nested.nested_key')
        assert configuration.has('nested.nested_key') is False

    def test_to_dict(self, configuration, config_data):
        """Test converting to dictionary."""
        result = configuration.to_dict()
        assert result == config_data

    def test_merge(self, configuration):
        """Test merging configurations."""
        new_data = {'key3': 'value3', 'key1': 'updated_value'}
        configuration.merge(new_data)
        assert configuration.get('key1') == 'updated_value'
        assert configuration.get('key3') == 'value3'
