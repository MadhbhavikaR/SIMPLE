import pytest
from unittest.mock import MagicMock, patch
from src.main import main

class TestMain:
    """Test cases for the main module."""

    @patch('src.main.DockerEngine')
    @patch('src.main.questionary.select')
    def test_main_interactive(self, mock_questionary_select, mock_docker_engine):
        """Test main function in interactive mode."""
        # Mock user input
        mock_questionary_select.return_value = 'interactive'

        # Mock DockerEngine
        mock_engine = MagicMock()
        mock_docker_engine.return_value = mock_engine

        # Mock sys.argv
        with patch('sys.argv', ['simple', '--interactive']):
            main()

        # Verify interactions
        mock_questionary_select.assert_called_once()
        mock_docker_engine.assert_called_once()

    @patch('src.main.DockerEngine')
    @patch('src.main.questionary.select')
    def test_main_non_interactive(self, mock_questionary_select, mock_docker_engine):
        """Test main function in non-interactive mode."""
        # Mock user input
        mock_questionary_select.return_value = 'non-interactive'

        # Mock DockerEngine
        mock_engine = MagicMock()
        mock_docker_engine.return_value = mock_engine

        # Mock sys.argv
        with patch('sys.argv', ['simple']):
            main()

        # Verify interactions
        mock_questionary_select.assert_called_once()
        mock_docker_engine.assert_called_once()

    @patch('src.main.DockerEngine')
    @patch('src.main.questionary.select')
    def test_main_with_config(self, mock_questionary_select, mock_docker_engine):
        """Test main function with config file."""
        # Mock user input
        mock_questionary_select.return_value = 'interactive'

        # Mock DockerEngine
        mock_engine = MagicMock()
        mock_docker_engine.return_value = mock_engine

        # Mock sys.argv with config file
        with patch('sys.argv', ['simple', '--config', 'test-config.yaml']):
            main()

        # Verify interactions
        mock_questionary_select.assert_called_once()
        mock_docker_engine.assert_called_once()

    @patch('src.main.DockerEngine')
    @patch('src.main.questionary.select')
    def test_main_with_services(self, mock_questionary_select, mock_docker_engine):
        """Test main function with specific services."""
        # Mock user input
        mock_questionary_select.return_value = 'interactive'

        # Mock DockerEngine
        mock_engine = MagicMock()
        mock_docker_engine.return_value = mock_engine

        # Mock sys.argv with services
        with patch('sys.argv', ['simple', '--services', 'service1', 'service2']):
            main()

        # Verify interactions
        mock_questionary_select.assert_called_once()
        mock_docker_engine.assert_called_once()

    @patch('src.main.DockerEngine')
    @patch('src.main.questionary.select')
    def test_main_error_handling(self, mock_questionary_select, mock_docker_engine):
        """Test main function error handling."""
        # Mock user input
        mock_questionary_select.return_value = 'interactive'

        # Mock DockerEngine to raise exception
        mock_docker_engine.side_effect = Exception("Test error")

        # Mock sys.argv
        with patch('sys.argv', ['simple']):
            with patch('src.main.logger.error') as mock_logger_error:
                main()

        # Verify error handling
        mock_questionary_select.assert_called_once()
        mock_docker_engine.assert_called_once()
        mock_logger_error.assert_called_once()
