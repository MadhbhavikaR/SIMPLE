from simple.core.container import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class PhotoprismService(ServiceStrategy):
    """Photoprism service (LinuxServer.io)."""
    
    name = "photoprism"
    category = "app"
    
    @property
    def networks(self) -> List[str]:
        return ["app"]
    
    def get_required_secrets(self) -> List[str]:
        return ["PHOTOPRISM_ADMIN_PASSWORD"]
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        volumes_dir = context.get('VOLUMES_DIR', Path('/mnt/vault/volumes'))
        return [volumes_dir / 'photoprism']