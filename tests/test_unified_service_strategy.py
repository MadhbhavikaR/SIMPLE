import pytest
from unittest.mock import MagicMock, patch
from src.simple.services.unified_service import UnifiedServiceStrategy

class TestUnifiedServiceStrategy:
    """Test cases for the UnifiedServiceStrategy class."""

    @pytest.fixture
    def mock_about_data(self):
        """Create mock about data for testing."""
        return {
            'name': 'test-service',
            'category': 'test-category',
            'description': 'Test service description',
            'alternatives': [
                {
                    'name': 'default',
                    'value': 'default',
                    'description': 'Default configuration',
                    'prompts': [
                        {'name': 'port', 'type': 'text', 'default': '8080'}
                    ]
                },
                {
                    'name': 'alternative',
                    'value': 'alt',
                    'description': 'Alternative configuration',
                    'prompts': [
                        {'name': 'port', 'type': 'text', 'default': '9090'}
                    ]
                }
            ],
            'secrets': ['secret1', 'secret2'],
            'networks': ['network1'],
            'dependencies': ['dep1', 'dep2']
        }

    @pytest.fixture
    def unified_service(self, mock_about_data):
        """Create a UnifiedServiceStrategy instance for testing."""
        return UnifiedServiceStrategy('test-service', mock_about_data)

    def test_init(self, unified_service, mock_about_data):
        """Test UnifiedServiceStrategy initialization."""
        assert unified_service.service_name == 'test-service'
        assert unified_service.about_data == mock_about_data
        assert unified_service.current_alternative == 'default'
        assert hasattr(unified_service, 'logger')

    def test_parse_alternatives(self, unified_service):
        """Test parsing alternatives."""
        alternatives = unified_service._parse_alternatives(mock_about_data['alternatives'])
        assert len(alternatives) == 2
        assert alternatives[0]['name'] == 'default'
        assert alternatives[1]['name'] == 'alternative'

    def test_validate_alternatives(self, unified_service):
        """Test validating alternatives."""
        # Test with valid alternatives
        unified_service._validate_alternatives()
        # Should not raise an exception

        # Test with invalid alternatives (no alternatives)
        invalid_about_data = {
            'name': 'test-service',
            'category': 'test-category',
            'alternatives': []
        }
        invalid_service = UnifiedServiceStrategy('test-service', invalid_about_data)

        with pytest.raises(ValueError):
            invalid_service._validate_alternatives()

    def test_set_alternative(self, unified_service):
        """Test setting alternative."""
        unified_service.set_alternative('alternative')
        assert unified_service.current_alternative == 'alternative'

        # Test with invalid alternative
        with pytest.raises(ValueError):
            unified_service.set_alternative('invalid')

    def test_get_available_alternatives(self, unified_service):
        """Test getting available alternatives."""
        alternatives = unified_service.get_available_alternatives()
        assert len(alternatives) == 2
        assert alternatives[0]['name'] == 'default'
        assert alternatives[1]['name'] == 'alternative'

    def test_name(self, unified_service):
        """Test getting service name."""
        assert unified_service.name() == 'test-service'

    def test_category(self, unified_service):
        """Test getting service category."""
        assert unified_service.category() == 'test-category'

    def test_networks(self, unified_service):
        """Test getting service networks."""
        assert unified_service.networks() == ['network1']

    def test_get_required_secrets(self, unified_service):
        """Test getting required secrets."""
        assert unified_service.get_required_secrets() == ['secret1', 'secret2']

    def test_get_required_prompts_for_alternative(self, unified_service):
        """Test getting required prompts for alternative."""
        prompts = unified_service.get_required_prompts_for_alternative()
        assert len(prompts) == 1
        assert prompts[0]['name'] == 'port'

        # Test with alternative
        unified_service.set_alternative('alternative')
        prompts_alt = unified_service.get_required_prompts_for_alternative()
        assert len(prompts_alt) == 1
        assert prompts_alt[0]['name'] == 'port'

    @patch('src.simple.services.unified_service.jinja2.Template')
    def test_generate_service_yaml(self, mock_template, unified_service):
        """Test generating service YAML."""
        mock_template.return_value.render.return_value = "service_yaml_content"

        context = {'key': 'value'}
        result = unified_service.generate_service_yaml(context)
        assert result == "service_yaml_content"

    def test_get_volume_paths(self, unified_service):
        """Test getting volume paths."""
        context = {'base_path': '/test'}
        result = unified_service.get_volume_paths(context)
        assert isinstance(result, list)

    def test_get_metadata(self, unified_service):
        """Test getting metadata."""
        metadata = unified_service.get_metadata()
        assert metadata['name'] == 'test-service'
        assert metadata['category'] == 'test-category'
        assert metadata['description'] == 'Test service description'
