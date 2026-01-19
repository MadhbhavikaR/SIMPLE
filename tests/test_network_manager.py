import pytest
from unittest.mock import MagicMock
from src.simple.core.network_manager import NetworkManager

class TestNetworkManager:
    """Test cases for the NetworkManager class."""

    @pytest.fixture
    def network_manager(self):
        """Create a NetworkManager instance for testing."""
        return NetworkManager()

    def test_networks(self, network_manager):
        """Test network retrieval."""
        networks = network_manager.networks()
        assert isinstance(networks, list)
        assert len(networks) > 0

    def test_get_required_secrets(self, network_manager):
        """Test required secrets retrieval."""
        secrets = network_manager.get_required_secrets()
        assert isinstance(secrets, list)

    def test_generate_service_yaml(self, network_manager):
        """Test service YAML generation."""
        context = {"networks": {"test": {"subnet": "192.168.1.0/24"}}}
        result = network_manager.generate_service_yaml(context)
        assert isinstance(result, str)
        assert "networks:" in result

    def test_get_volume_paths(self, network_manager):
        """Test volume path retrieval."""
        context = {"base_path": "/test"}
        result = network_manager.get_volume_paths(context)
        assert isinstance(result, list)
