import pytest
from src.simple.config.dto.servers import ServerDetectionResult

class TestServerDetectionResult:
    """Test cases for the ServerDetectionResult class."""

    @pytest.fixture
    def server_data(self):
        """Create sample server detection data."""
        return {
            'name': 'test-server',
            'description': 'Test server',
            'detected': True,
            'port': 8080,
            'version': '1.0.0',
            'status': 'running'
        }

    @pytest.fixture
    def server_result(self, server_data):
        """Create a ServerDetectionResult instance for testing."""
        return ServerDetectionResult(server_data)

    def test_init(self, server_result, server_data):
        """Test ServerDetectionResult initialization."""
        assert server_result.name == server_data['name']
        assert server_result.description == server_data['description']
        assert server_result.detected == server_data['detected']
        assert server_result.port == server_data['port']
        assert server_result.version == server_data['version']
        assert server_result.status == server_data['status']

    def test_to_dict(self, server_result, server_data):
        """Test converting to dictionary."""
        result = server_result.to_dict()
        assert result == server_data

    def test_is_detected(self, server_result):
        """Test checking if server is detected."""
        assert server_result.is_detected() is True
        server_result.detected = False
        assert server_result.is_detected() is False

    def test_get_status(self, server_result):
        """Test getting server status."""
        assert server_result.get_status() == 'running'
        server_result.status = 'stopped'
        assert server_result.get_status() == 'stopped'
