import pytest
from unittest.mock import MagicMock, patch
from src.simple.native.ufw_harden import UfwEnforcer

class TestUfwEnforcer:
    """Test cases for the UfwEnforcer class."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        return {
            'base_path': '/test/base',
            'dry_run': False
        }

    @pytest.fixture
    def ufw_enforcer(self, mock_context):
        """Create an UfwEnforcer instance for testing."""
        return UfwEnforcer(mock_context)

    def test_init(self, ufw_enforcer, mock_context):
        """Test UfwEnforcer initialization."""
        assert ufw_enforcer.context == mock_context
        assert hasattr(ufw_enforcer, 'logger')

    def test_detect(self, ufw_enforcer):
        """Test detection method."""
        # Mock the detection logic
        with patch('src.simple.native.ufw_harden.subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(stdout='Status: active')

            result = ufw_enforcer.detect()
            assert result is True

            mock_subprocess.return_value = MagicMock(stdout='Status: inactive')
            result = ufw_enforcer.detect()
            assert result is False

    def test_load_config(self, ufw_enforcer):
        """Test loading configuration."""
        # Mock the config loading logic
        with patch('src.simple.native.ufw_harden.yaml.safe_load') as mock_yaml_load:
            mock_yaml_load.return_value = {
                'rules': {
                    'allow_ssh': {
                        'port': 22,
                        'protocol': 'tcp',
                        'description': 'Allow SSH'
                    }
                }
            }

            result = ufw_enforcer._load_config()
            assert isinstance(result, list)
            assert len(result) > 0

    def test_process(self, ufw_enforcer):
        """Test process method."""
        # Mock the process logic
        with patch.object(ufw_enforcer, '_load_config') as mock_load_config:
            mock_load_config.return_value = [
                {'port': 22, 'protocol': 'tcp', 'description': 'Allow SSH'}
            ]

            result = ufw_enforcer.process()
            assert isinstance(result, list)
            assert len(result) > 0

    def test_has_active_ssh_session(self, ufw_enforcer):
        """Test active SSH session detection."""
        # Mock the SSH session detection logic
        with patch('src.simple.native.ufw_harden.psutil.net_connections') as mock_connections:
            mock_connections.return_value = [
                MagicMock(laddr=('0.0.0.0', 22), status='ESTABLISHED')
            ]

            result = ufw_enforcer._has_active_ssh_session()
            assert result is True

            mock_connections.return_value = []
            result = ufw_enforcer._has_active_ssh_session()
            assert result is False

    def test_detect_lan_subnet(self, ufw_enforcer):
        """Test LAN subnet detection."""
        # Mock the LAN subnet detection logic
        with patch('src.simple.native.ufw_harden.psutil.net_if_addrs') as mock_if_addrs:
            mock_if_addrs.return_value = {
                'eth0': [
                    MagicMock(address='192.168.1.100', netmask='255.255.255.0')
                ]
            }

            result = ufw_enforcer._detect_lan_subnet(['eth0'])
            assert result == '192.168.1.0/24'

            mock_if_addrs.return_value = {}
            result = ufw_enforcer._detect_lan_subnet(['eth0'])
            assert result is None

    @patch('src.simple.native.ufw_harden.subprocess.run')
    def test_apply(self, mock_subprocess_run, ufw_enforcer):
        """Test apply method."""
        payload = [
            {'port': 22, 'protocol': 'tcp', 'description': 'Allow SSH'}
        ]

        result = ufw_enforcer.apply(payload)
        assert result is True
        mock_subprocess_run.assert_called()

    @patch('src.simple.native.ufw_harden.subprocess.run')
    def test_apply_error(self, mock_subprocess_run, ufw_enforcer):
        """Test apply method with error."""
        mock_subprocess_run.side_effect = Exception("Test error")
        payload = [{'port': 22, 'protocol': 'tcp', 'description': 'Allow SSH'}]

        result = ufw_enforcer.apply(payload)
        assert result is False
