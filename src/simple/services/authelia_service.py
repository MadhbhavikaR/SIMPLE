from simple.core.container import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class AutheliaService(ServiceStrategy):
    """Authelia authentication service."""
    
    name = "authelia"
    category = "app"
    
    @property
    def networks(self) -> List[str]:
        return ["app"]
    
    def get_required_secrets(self) -> List[str]:
        return ["AUTHELIA_JWT_SECRET", "AUTHELIA_SESSION_SECRET", "AUTHELIA_STORAGE_PASSWORD"]
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        volumes_dir = context.get('VOLUMES_DIR', Path('/mnt/vault/volumes'))
        return [volumes_dir / 'authelia']