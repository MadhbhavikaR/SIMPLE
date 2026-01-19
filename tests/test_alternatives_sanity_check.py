import pytest
from unittest.mock import MagicMock, patch
from src.simple.services.alternatives_sanity_check import AlternativesSanityCheck

class TestAlternativesSanityCheck:
    """Test cases for the AlternativesSanityCheck class."""

    @pytest.fixture
    def sanity_check(self):
        """Create an AlternativesSanityCheck instance for testing."""
        return AlternativesSanityCheck()

    def test_init(self, sanity_check):
        """Test AlternativesSanityCheck initialization."""
        assert sanity_check.name == "Alternatives Sanity Check"
        assert sanity_check.description == "Validates service alternatives configuration"

    @patch('src.simple.services.alternatives_sanity_check.ServiceRepository')
    @patch('src.simple.services.alternatives_sanity_check.UnifiedServiceStrategy')
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
            {'name': 'default', 'value': 'default'},
            {'name': 'alternative', 'value': 'alt'}
        ]

        result, message = sanity_check.run()
        assert result is True
        assert "All services have valid alternatives" in message

    @patch('src.simple.services.alternatives_sanity_check.ServiceRepository')
    @patch('src.simple.services.alternatives_sanity_check.UnifiedServiceStrategy')
    def test_run_with_invalid_alternatives(self, mock_service_strategy, mock_service_repo, sanity_check):
        """Test running the sanity check with invalid alternatives."""
        # Mock service repository
        mock_repo = MagicMock()
        mock_service_repo.return_value = mock_repo
        mock_repo.discover_services.return_value = []

        # Mock service strategy with no alternatives
        mock_service = MagicMock()
        mock_service_strategy.return_value = mock_service
        mock_service.get_available_alternatives.return_value = []

        result, message = sanity_check.run()
        assert result is False
        assert "has no alternatives" in message
