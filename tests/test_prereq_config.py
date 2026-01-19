import pytest
from src.simple.config.dto.prereqquisite import PrereqConfig

class TestPrereqConfig:
    """Test cases for the PrereqConfig class."""

    @pytest.fixture
    def prereq_data(self):
        """Create sample prerequisite data."""
        return {
            'name': 'test-prereq',
            'description': 'Test prerequisite',
            'required': True,
            'installed': False,
            'version': '1.0.0',
            'install_command': 'apt install test-prereq'
        }

    @pytest.fixture
    def prereq_config(self, prereq_data):
        """Create a PrereqConfig instance for testing."""
        return PrereqConfig(prereq_data)

    def test_init(self, prereq_config, prereq_data):
        """Test PrereqConfig initialization."""
        assert prereq_config.name == prereq_data['name']
        assert prereq_config.description == prereq_data['description']
        assert prereq_config.required == prereq_data['required']
        assert prereq_config.installed == prereq_data['installed']
        assert prereq_config.version == prereq_data['version']
        assert prereq_config.install_command == prereq_data['install_command']

    def test_to_dict(self, prereq_config, prereq_data):
        """Test converting to dictionary."""
        result = prereq_config.to_dict()
        assert result == prereq_data

    def test_is_satisfied(self, prereq_config):
        """Test checking if prerequisite is satisfied."""
        assert prereq_config.is_satisfied() is False
        prereq_config.installed = True
        assert prereq_config.is_satisfied() is True

    def test_is_required(self, prereq_config):
        """Test checking if prerequisite is required."""
        assert prereq_config.is_required() is True
        prereq_config.required = False
        assert prereq_config.is_required() is False
