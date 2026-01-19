import pytest
from unittest.mock import MagicMock, patch
from src.simple.notifier import Notifier

class TestNotifier:
    """Test cases for the Notifier class."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        return {
            'base_path': '/test/base',
            'notifications': True
        }

    @pytest.fixture
    def notifier(self, mock_context):
        """Create a Notifier instance for testing."""
        return Notifier(mock_context)

    def test_init(self, notifier, mock_context):
        """Test Notifier initialization."""
        assert notifier.context == mock_context
        assert hasattr(notifier, 'logger')

    @patch('src.simple.notifier.subprocess.run')
    def test_send(self, mock_subprocess_run, notifier):
        """Test sending notifications."""
        result = notifier.send("Test message", "info")
        assert result is True
        mock_subprocess_run.assert_called_once()

    @patch('src.simple.notifier.subprocess.run')
    def test_send_error(self, mock_subprocess_run, notifier):
        """Test sending notifications with error."""
        mock_subprocess_run.side_effect = Exception("Test error")
        result = notifier.send("Test message", "error")
        assert result is False

    @patch('src.simple.notifier.Path.write_text')
    @patch('src.simple.notifier.Path.exists')
    def test_install_systemd_unit(self, mock_exists, mock_write_text, notifier):
        """Test installing systemd unit."""
        mock_exists.return_value = False
        result = notifier.install_systemd_unit()
        assert result is True
        mock_write_text.assert_called_once()
