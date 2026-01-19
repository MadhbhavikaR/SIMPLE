import pytest
from unittest.mock import MagicMock, patch
from src.simple.native.apparmor_harden import AppArmorEnforcer

class TestAppArmorEnforcer:
    """Test cases for the AppArmorEnforcer class."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        return {
            'base_path': '/test/base',
            'dry_run': False
        }

    @pytest.fixture
    def apparmor_enforcer(self, mock_context):
        """Create an AppArmorEnforcer instance for testing."""
        return AppArmorEnforcer(mock_context)

    def test_init(self, apparmor_enforcer, mock_context):
        """Test AppArmorEnforcer initialization."""
        assert apparmor_enforcer.context == mock_context
        assert hasattr(apparmor_enforcer, 'logger')

    def test_detect(self, apparmor_enforcer):
        """Test detection method."""
        # Mock the detection logic
        with patch('src.simple.native.apparmor_harden.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = apparmor_enforcer.detect()
            assert result is True

            mock_exists.return_value = False
            result = apparmor_enforcer.detect()
            assert result is False

    def test_process(self, apparmor_enforcer):
        """Test process method."""
        # Mock the process logic
        with patch('src.simple.native.apparmor_harden.yaml.safe_load') as mock_yaml_load:
            mock_yaml_load.return_value = {
                'profiles': {
                    'test_profile': {
                        'name': 'test_profile',
                        'content': 'test_content'
                    }
                }
            }

            result = apparmor_enforcer.process()
            assert isinstance(result, dict)
            assert 'test_profile' in result

    @patch('src.simple.native.apparmor_harden.subprocess.run')
    def test_apply(self, mock_subprocess_run, apparmor_enforcer):
        """Test apply method."""
        payload = {
            'test_profile': {
                'name': 'test_profile',
                'content': 'test_content'
            }
        }

        result = apparmor_enforcer.apply(payload)
        assert result is True
        mock_subprocess_run.assert_called()

    @patch('src.simple.native.apparmor_harden.subprocess.run')
    def test_apply_error(self, mock_subprocess_run, apparmor_enforcer):
        """Test apply method with error."""
        mock_subprocess_run.side_effect = Exception("Test error")
        payload = {'test_profile': {'name': 'test_profile', 'content': 'test_content'}}

        result = apparmor_enforcer.apply(payload)
        assert result is False
