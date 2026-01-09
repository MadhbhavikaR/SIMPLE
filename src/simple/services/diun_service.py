"""Application services."""

from simple.core.container import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class DIUNService(ServiceStrategy):
    """Docker Image Update Notifier service."""
    
    name = "diun"
    category = "app"
    
    @property
    def networks(self) -> List[str]:
        return ["edge"]  # Needs access to Docker socket proxy
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        volumes_dir = context.get('VOLUMES_DIR', Path('/mnt/vault/volumes'))
        return [volumes_dir / 'diun']
