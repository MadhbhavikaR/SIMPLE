from .base import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class NetworkManager(ServiceStrategy):
    """Defines 3-tier network isolation."""
    name = "networks"
    category = "core"
    
    @property
    def networks(self) -> List[str]:
        return ["edge", "app", "db"]
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def generate_service_yaml(self, context: Dict[str, Any]) -> str:
        """Generate network definitions - returns empty as networks are handled separately."""
        return ""
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        return []

class SocketProxyService(ServiceStrategy):
    """Secure Docker socket proxy."""
    name = "socket-proxy"
    category = "core"
    
    @property
    def networks(self) -> List[str]:
        return ["edge"]
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        return []
