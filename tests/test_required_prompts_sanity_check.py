import pytest
from unittest.mock import MagicMock, patch
from src.simple.services.required_prompts_sanity_check import RequiredPromptsSanityCheck

class TestRequiredPromptsSanityCheck:
    """Test cases for the RequiredPromptsSanityCheck class."""

    @pytest.fixture
    def sanity_check(self):
        """Create a RequiredPromptsSanityCheck instance for testing."""
        return RequiredPromptsSanityCheck()

    def test_init(self, sanity_check):
        """Test RequiredPromptsSanityCheck initialization."""
        assert sanity_check.name == "Required Prompts Sanity Check"
        assert sanity_check.description == "Validates required prompts in service templates"

    @patch('src.simple.services.required_prompts_sanity_check.ServiceRepository')
    @patch('src.simple.services.required_prompts_sanity_check.UnifiedServiceStrategy')
    def test_run(self, mock_service_strategy, mock_service_repo, sanity_check):
        """Test running the sanity check."""
        # Mock service repository
        mock_repo = MagicMock()
        mock_service_repo.return_value = mock_repo
        mock_repo.discover_services.return_value = []

        # Mock service strategy
        mock_service = MagicMock()
        mock_service_strategy.return_value = mock_service
        mock_service.get_available_alternatives.return_value = [
            {'name': 'default', 'value': 'default'}
        ]

        # Mock template validation
        with patch.object(sanity_check, '_validate_template_against_prompts') as mock_validate:
            mock_validate.return_value = True

            result, message = sanity_check.run()
            assert result is True
            assert "All services have valid required prompts" in message

    @patch('src.simple.services.required_prompts_sanity_check.ServiceRepository')
    @patch('src.simple.services.required_prompts_sanity_check.UnifiedServiceStrategy')
    def test_run_with_invalid_prompts(self, mock_service_strategy, mock_service_repo, sanity_check):
        """Test running the sanity check with invalid prompts."""
        # Mock service repository
        mock_repo = MagicMock()
        mock_service_repo.return_value = mock_repo
        mock_repo.discover_services.return_value = []

        # Mock service strategy
        mock_service = MagicMock()
        mock_service_strategy.return_value = mock_service
        mock_service.get_available_alternatives.return_value = [
            {'name': 'default', 'value': 'default'}
        ]

        # Mock template validation to return False
        with patch.object(sanity_check, '_validate_template_against_prompts') as mock_validate:
            mock_validate.return_value = False

            result, message = sanity_check.run()
            assert result is False
            assert "has invalid required prompts" in message

    def test_extract_variables_from_template(self, sanity_check):
        """Test extracting variables from template."""
        template_content = "Hello {{ name }}, welcome to {{ service }}!"
        result = sanity_check._extract_variables_from_template(template_content)
        assert result == {'name', 'service'}

        # Test with no variables
        template_content_no_vars = "Hello, welcome!"
        result_no_vars = sanity_check._extract_variables_from_template(template_content_no_vars)
        assert result_no_vars == set()

    @patch('src.simple.services.required_prompts_sanity_check.Path.read_text')
    def test_validate_template_against_prompts(self, mock_read_text, sanity_check):
        """Test validating template against prompts."""
        # Mock template content
        mock_read_text.return_value = "Hello {{ name }}, welcome to {{ service }}!"

        # Mock required prompts
        required_prompts = [
            {'name': 'name', 'type': 'text'},
            {'name': 'service', 'type': 'text'}
        ]

        result = sanity_check._validate_template_against_prompts('test_service', 'default', required_prompts)
        assert result is True

        # Test with missing required prompt
        required_prompts_missing = [
            {'name': 'name', 'type': 'text'}
        ]

        result_missing = sanity_check._validate_template_against_prompts('test_service', 'default', required_prompts_missing)
        assert result_missing is False
