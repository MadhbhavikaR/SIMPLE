from simple.core.container import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

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
