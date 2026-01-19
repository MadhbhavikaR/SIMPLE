import pytest
from unittest.mock import MagicMock, patch
from src.simple.detectors.prerequisite import PrerequisiteAppsDetector
from src.simple.config.config_reader import ConfigReader

class TestPrerequisiteAppsDetector:
    """Test cases for the PrerequisiteAppsDetector class."""

    @pytest.fixture
    def mock_config_reader(self):
        """Create a mock ConfigReader for testing."""
        return MagicMock(spec=ConfigReader)

    @pytest.fixture
    def prerequisite_detector(self, mock_config_reader):
        """Create a PrerequisiteAppsDetector instance for testing."""
        return PrerequisiteAppsDetector(mock_config_reader)

    def test_init(self, prerequisite_detector, mock_config_reader):
        """Test PrerequisiteAppsDetector initialization."""
        assert prerequisite_detector.config_reader == mock_config_reader
        assert hasattr(prerequisite_detector, 'logger')

    @patch('src.simple.detectors.prerequisite.PrereqConfig')
    def test_detect(self, mock_prereq_config, prerequisite_detector):
        """Test detection method."""
        # Mock system detection
        with patch.object(prerequisite_detector, '_detect_system') as mock_system_detect:
            mock_system_detect.return_value = {'os': 'linux', 'distro': 'ubuntu'}

            # Mock individual app detection
            with patch.object(prerequisite_detector, '_detect_single') as mock_single_detect:
                mock_single_detect.return_value = MagicMock()

                result = prerequisite_detector.detect()
                assert isinstance(result, dict)
                mock_system_detect.assert_called_once()
                mock_single_detect.assert_called()

    def test_get_missing_install_command(self, prerequisite_detector):
        """Test getting install command for missing apps."""
        # Mock detection results with missing apps
        prerequisite_detector.detection_results = {
            'app1': MagicMock(is_satisfied=lambda: True),
            'app2': MagicMock(is_satisfied=lambda: False, install_command='apt install app2')
        }

        result = prerequisite_detector.get_missing_install_command()
        assert 'apt install app2' in result

    def test_print_summary(self, prerequisite_detector):
        """Test printing summary."""
        # Mock detection results
        prerequisite_detector.detection_results = {
            'app1': MagicMock(is_satisfied=lambda: True),
            'app2': MagicMock(is_satisfied=lambda: False)
        }

        with patch('builtins.print') as mock_print:
            result = prerequisite_detector.print_summary()
            assert result is True
            assert mock_print.call_count > 0
