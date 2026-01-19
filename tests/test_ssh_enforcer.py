import pytest
from unittest.mock import MagicMock, patch
from src.simple.native.ssh_harden import SSHEnforcer

class TestSSHEnforcer:
    """Test cases for the SSHEnforcer class."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        return {
            'base_path': '/test/base',
            'dry_run': False
        }

    @pytest.fixture
    def ssh_enforcer(self, mock_context):
        """Create an SSHEnforcer instance for testing."""
        return SSHEnforcer(mock_context)

    def test_init(self, ssh_enforcer, mock_context):
        """Test SSHEnforcer initialization."""
        assert ssh_enforcer.context == mock_context
        assert hasattr(ssh_enforcer, 'logger')

    def test_detect(self, ssh_enforcer):
        """Test detection method."""
        # Mock the detection logic
        with patch('src.simple.native.ssh_harden.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = ssh_enforcer.detect()
            assert result is True

            mock_exists.return_value = False
            result = ssh_enforcer.detect()
            assert result is False

    def test_process(self, ssh_enforcer):
        """Test process method."""
        # Mock the process logic
        with patch('src.simple.native.ssh_harden.yaml.safe_load') as mock_yaml_load:
            mock_yaml_load.return_value = {
                'ssh_config': {
                    'Port': 22,
                    'PermitRootLogin': 'no',
                    'PasswordAuthentication': 'no'
                }
            }

            result = ssh_enforcer.process()
            assert isinstance(result, dict)
            assert 'Port' in result

    def test_detect_ssh_port(self, ssh_enforcer):
        """Test SSH port detection."""
        # Mock the port detection logic
        with patch('src.simple.native.ssh_harden.socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_socket_instance
            mock_socket_instance.getsockname.return_value = ('0.0.0.0', 22)

            result = ssh_enforcer._detect_ssh_port()
            assert result == 22

    @patch('src.simple.native.ssh_harden.subprocess.run')
    def test_apply(self, mock_subprocess_run, ssh_enforcer):
        """Test apply method."""
        payload = {
            'Port': 22,
            'PermitRootLogin': 'no',
            'PasswordAuthentication': 'no'
        }

        result = ssh_enforcer.apply(payload)
        assert result is True
        mock_subprocess_run.assert_called()

    @patch('src.simple.native.ssh_harden.subprocess.run')
    def test_apply_error(self, mock_subprocess_run, ssh_enforcer):
        """Test apply method with error."""
        mock_subprocess_run.side_effect = Exception("Test error")
        payload = {'Port': 22, 'PermitRootLogin': 'no'}

        result = ssh_enforcer.apply(payload)
        assert result is False
