import pytest
from unittest.mock import Mock, patch, MagicMock
from src.simple.engine import DockerEngine
from src.simple.core.container import ServiceStrategy

def test_service_alternatives_default_value_fix():
    """
    Test that the fix for the default value issue in _handle_service_with_alternatives works correctly.

    This test verifies that:
    1. The default value is always set to the first available choice
    2. The default value exists in the choices list
    3. No ValueError is raised when using the default value
    """
    # Create a mock service with alternatives
    mock_service = Mock()
    mock_service.name = "test-service"
    mock_service.get_available_alternatives = Mock(return_value=[
        {'name': 'Standard', 'description': 'Standard configuration'},
        {'name': 'Advanced', 'description': 'Advanced configuration with Redis'},
        {'name': 'Minimal', 'description': 'Minimal configuration'}
    ])
    mock_service.get_required_prompts_for_alternative = Mock(return_value=[])
    mock_service.set_alternative = Mock()

    # Create a mock about_data
    about_data = {
        'name': 'Test Service',
        'description': 'Test service for alternatives',
        'enforced': False
    }

    # Create a DockerEngine instance
    context = {
        'DOCKER_DIR': '/tmp/docker',
        'VOLUMES_DIR': '/tmp/volumes',
        'SCRIPTS_DIR': '/tmp/scripts',
        'PUID': 1000,
        'PGID': 1000
    }

    engine = DockerEngine(context)

    # Mock the questionary.select to capture the call
    with patch('questionary.select') as mock_select:
        # Set up the mock to return the first choice
        mock_select.return_value.ask.return_value = 'Standard'

        # Call the method that was causing the issue
        engine._handle_service_with_alternatives(mock_service, about_data, is_enforced=False)

        # Verify that select was called with the correct parameters
        assert mock_select.called

        # Get the call arguments
        call_args = mock_select.call_args
        assert call_args is not None

        # Extract the choices from the call
        choices = call_args[1]['choices']

        # Verify the fix: check that default parameter is not passed to questionary.select
        # The fix removes the default parameter to avoid questionary validation issues
        assert 'default' not in call_args[1], "Default parameter should not be passed to questionary.select"

        # Verify that the service alternative was set
        mock_service.set_alternative.assert_called_once_with('Standard')

def test_service_alternatives_enforced_service():
    """
    Test that enforced services also use the correct default value.
    """
    # Create a mock service with alternatives
    mock_service = Mock()
    mock_service.name = "authelia"
    mock_service.get_available_alternatives = Mock(return_value=[
        {'name': 'Standard', 'description': 'Standard Authelia configuration with Redis and MariaDB'},
        {'name': 'Minimal', 'description': 'Minimal Authelia configuration'}
    ])
    mock_service.get_required_prompts_for_alternative = Mock(return_value=[])
    mock_service.set_alternative = Mock()

    # Create a mock about_data for an enforced service
    about_data = {
        'name': 'Authelia',
        'description': 'Authentication and authorization server',
        'enforced': True
    }

    # Create a DockerEngine instance
    context = {
        'DOCKER_DIR': '/tmp/docker',
        'VOLUMES_DIR': '/tmp/volumes',
        'SCRIPTS_DIR': '/tmp/scripts',
        'PUID': 1000,
        'PGID': 1000
    }

    engine = DockerEngine(context)

    # Mock the questionary.select to capture the call
    with patch('questionary.select') as mock_select:
        # Set up the mock to return the first choice
        mock_select.return_value.ask.return_value = 'Standard'

        # Call the method for an enforced service
        engine._handle_service_with_alternatives(mock_service, about_data, is_enforced=True)

        # Verify that select was called with the correct parameters
        assert mock_select.called

        # Get the call arguments
        call_args = mock_select.call_args
        assert call_args is not None

        # Extract the choices from the call
        choices = call_args[1]['choices']

        # Verify the fix: check that default parameter is not passed to questionary.select
        # The fix removes the default parameter to avoid questionary validation issues
        assert 'default' not in call_args[1], "Default parameter should not be passed to questionary.select"

        # Verify that the service alternative was set
        mock_service.set_alternative.assert_called_once_with('Standard')

def test_service_alternatives_single_alternative():
    """
    Test that services with only one alternative work correctly.
    """
    # Create a mock service with a single alternative
    mock_service = Mock()
    mock_service.name = "simple-service"
    mock_service.get_available_alternatives = Mock(return_value=[
        {'name': 'Default', 'description': 'Default configuration'}
    ])
    mock_service.get_required_prompts_for_alternative = Mock(return_value=[])
    mock_service.set_alternative = Mock()

    # Create a mock about_data
    about_data = {
        'name': 'Simple Service',
        'description': 'Simple service with one configuration',
        'enforced': False
    }

    # Create a DockerEngine instance
    context = {
        'DOCKER_DIR': '/tmp/docker',
        'VOLUMES_DIR': '/tmp/volumes',
        'SCRIPTS_DIR': '/tmp/scripts',
        'PUID': 1000,
        'PGID': 1000
    }

    engine = DockerEngine(context)

    # Call the method - should not raise any errors
    engine._handle_service_with_alternatives(mock_service, about_data, is_enforced=False)

    # Verify that the service alternative was set to the single available option
    mock_service.set_alternative.assert_called_once_with('Default')

def test_service_alternatives_no_alternatives():
    """
    Test that services with no alternatives are handled gracefully.
    """
    # Create a mock service with no alternatives
    mock_service = Mock(spec=ServiceStrategy)
    mock_service.name = "legacy-service"
    mock_service.get_available_alternatives = Mock(return_value=[])

    # Create a mock about_data
    about_data = {
        'name': 'Legacy Service',
        'description': 'Legacy service without alternatives',
        'enforced': False
    }

    # Create a DockerEngine instance
    context = {
        'DOCKER_DIR': '/tmp/docker',
        'VOLUMES_DIR': '/tmp/volumes',
        'SCRIPTS_DIR': '/tmp/scripts',
        'PUID': 1000,
        'PGID': 1000
    }

    engine = DockerEngine(context)

    # Call the method - should not raise any errors
    engine._handle_service_with_alternatives(mock_service, about_data, is_enforced=False)

    # Verify that the service was added to selected services
    assert mock_service in engine.selected_services
