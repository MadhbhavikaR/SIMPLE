import pytest
from unittest.mock import MagicMock, patch
from src.simple.detectors.detector import Detector
from src.simple.config.config_reader import ConfigReader

class TestDetector:
    """Test cases for the Detector class."""

    @pytest.fixture
    def mock_config_reader(self):
        """Create a mock ConfigReader for testing."""
        return MagicMock(spec=ConfigReader)

    @pytest.fixture
    def detector(self, mock_config_reader):
        """Create a Detector instance for testing."""
        return Detector(mock_config_reader)

    def test_init(self, detector, mock_config_reader):
        """Test Detector initialization."""
        assert detector.config_reader == mock_config_reader
        assert hasattr(detector, 'logger')

    @patch('src.simple.detectors.detector.shutil.which')
    def test_find_paths(self, mock_which, detector):
        """Test finding paths."""
        mock_which.return_value = '/usr/bin/test'
        result = detector._find_paths(['test'])
        assert result == '/usr/bin/test'

        mock_which.return_value = None
        result = detector._find_paths(['nonexistent'])
        assert result is None

    @patch('src.simple.detectors.detector.PrereqConfig')
    def test_detect(self, mock_prereq_config, detector):
        """Test detection method."""
        # Mock the prerequisites configuration
        mock_config = {
            'prerequisites': {
                'test_app': {
                    'name': 'test_app',
                    'description': 'Test application',
                    'required': True,
                    'binaries': ['test_app'],
                    'version_command': 'test_app --version'
                }
            }
        }

        with patch.object(detector.config_reader, 'read_yaml_config') as mock_read:
            mock_read.return_value = mock_config
            mock_prereq_config.return_value = MagicMock()

            result = detector.detect()
            assert isinstance(result, dict)
            assert 'test_app' in result

    def test_print_summary(self, detector):
        """Test printing summary."""
        # Mock detection results
        detector.detection_results = {
            'app1': MagicMock(is_satisfied=lambda: True),
            'app2': MagicMock(is_satisfied=lambda: False)
        }

        with patch('builtins.print') as mock_print:
            result = detector.print_summary()
            assert result is True
            assert mock_print.call_count > 0
