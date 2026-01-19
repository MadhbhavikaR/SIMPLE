import pytest
from unittest.mock import MagicMock, patch
from src.simple.detectors.server_detector import ServerDetector
from src.simple.config.config_reader import ConfigReader

class TestServerDetector:
    """Test cases for the ServerDetector class."""

    @pytest.fixture
    def mock_config_reader(self):
        """Create a mock ConfigReader for testing."""
        return MagicMock(spec=ConfigReader)

    @pytest.fixture
    def server_detector(self, mock_config_reader):
        """Create a ServerDetector instance for testing."""
        return ServerDetector(mock_config_reader)

    def test_init(self, server_detector, mock_config_reader):
        """Test ServerDetector initialization."""
        assert server_detector.config_reader == mock_config_reader
        assert hasattr(server_detector, 'logger')

    @patch('src.simple.detectors.server_detector.yaml.safe_load')
    def test_load_config(self, mock_yaml_load, server_detector):
        """Test loading configuration."""
        mock_yaml_load.return_value = {
            'servers': {
                'test_server': {
                    'name': 'test_server',
                    'description': 'Test server',
                    'keywords': ['test'],
                    'port': 8080
                }
            }
        }

        result = server_detector._load_config()
        assert 'test_server' in result
        assert result['test_server']['name'] == 'test_server'

    @patch('src.simple.detectors.server_detector.socket.socket')
    def test_get_fresh_socket_data(self, mock_socket, server_detector):
        """Test getting fresh socket data."""
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.getsockname.return_value = ('0.0.0.0', 8080)

        result = server_detector._get_fresh_socket_data()
        assert isinstance(result, list)
        assert len(result) > 0

    @patch('src.simple.detectors.server_detector.psutil.process_iter')
    def test_get_fresh_process_data(self, mock_process_iter, server_detector):
        """Test getting fresh process data."""
        mock_process = MagicMock()
        mock_process.name.return_value = 'test_process'
        mock_process.connections.return_value = [MagicMock(laddr=('0.0.0.0', 8080))]
        mock_process_iter.return_value = [mock_process]

        result = server_detector._get_fresh_process_data()
        assert isinstance(result, list)
        assert len(result) > 0

    @patch('src.simple.detectors.server_detector.ServerDetectionResult')
    def test_detect_single_server(self, mock_server_result, server_detector):
        """Test detecting single server."""
        config = {
            'name': 'test_server',
            'description': 'Test server',
            'keywords': ['test'],
            'port': 8080
        }

        mock_server_result.return_value = MagicMock()

        result = server_detector._detect_single_server('test', config, ['test_line'])
        assert isinstance(result, MagicMock)

    def test_extract_port_from_line(self, server_detector):
        """Test extracting port from line."""
        # Test valid port extraction
        port = server_detector._extract_port_from_line('0.0.0.0:8080')
        assert port == 8080

        # Test invalid port extraction
        port = server_detector._extract_port_from_line('invalid_line')
        assert port is None

    @patch('src.simple.detectors.server_detector.ServerDetectionResult')
    def test_detect(self, mock_server_result, server_detector):
        """Test detection method."""
        # Mock configuration and detection methods
        with patch.object(server_detector, '_load_config') as mock_load_config:
            mock_load_config.return_value = {
                'test_server': {
                    'name': 'test_server',
                    'description': 'Test server',
                    'keywords': ['test'],
                    'port': 8080
                }
            }

            with patch.object(server_detector, '_get_fresh_socket_data') as mock_socket_data:
                mock_socket_data.return_value = ['test_line']

                with patch.object(server_detector, '_get_fresh_process_data') as mock_process_data:
                    mock_process_data.return_value = ['test_line']

                    with patch.object(server_detector, '_detect_single_server') as mock_detect_single:
                        mock_detect_single.return_value = MagicMock()

                        result = server_detector.detect()
                        assert isinstance(result, dict)
                        assert 'test_server' in result

    def test_print_summary(self, server_detector):
        """Test printing summary."""
        # Mock detection results
        server_detector.detection_results = {
            'server1': MagicMock(is_detected=lambda: True),
            'server2': MagicMock(is_detected=lambda: False)
        }

        with patch('builtins.print') as mock_print:
            result = server_detector.print_summary()
            assert result is True
            assert mock_print.call_count > 0
