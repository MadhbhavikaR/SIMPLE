from .base import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class NetworkManager(ServiceStrategy):
    """Defines 3-tier network isolation."""
    name = "networks"
    category = "core"
    
    @property
    def networks(self) -> List[str]:
        return ["net_edge", "net_app", "net_db"]
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def generate_service_yaml(self, context: Dict[str, Any]) -> str:
        return """networks:
  net_edge:
    driver: bridge
    internal: false
    ipam:
      config:
        - subnet: 172.20.0.0/24
  net_app:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.21.0.0/24
  net_db:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.22.0.0/24"""
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        return []

class SocketProxyService(ServiceStrategy):
    """Secure Docker socket proxy."""
    name = "socket-proxy"
    category = "core"
    
    @property
    def networks(self) -> List[str]:
        return ["net_edge"]
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def generate_service_yaml(self, context: Dict[str, Any]) -> str:
        return f"""  socket-proxy:
    image: tecnativa/docker-socket-proxy:latest
    container_name: socket-proxy
    networks:
      - net_edge
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - CONTAINERS=1
      - SERVICES=1
      - IMAGES=1
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    restart: unless-stopped"""
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        return []
