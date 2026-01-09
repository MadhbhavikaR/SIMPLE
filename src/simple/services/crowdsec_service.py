from simple.core.container import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class CrowdSecService(ServiceStrategy):
    """CrowdSec security service."""
    
    name = "crowdsec"
    category = "security"
    
    @property
    def networks(self) -> List[str]:
        return ["app"]  # Needs access to SWAG logs
    
    def get_required_secrets(self) -> List[str]:
        return ["CROWDSEC_API_KEY"]
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        volumes_dir = context.get('VOLUMES_DIR', Path('/mnt/vault/volumes'))
        return [
            volumes_dir / 'crowdsec' / 'config',
            volumes_dir / 'crowdsec' / 'data'
        ]
