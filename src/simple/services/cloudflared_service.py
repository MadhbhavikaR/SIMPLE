from simple.core.container import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class CloudflaredService(ServiceStrategy):
    """Cloudflared tunnel service."""
    name = "cloudflared"
    category = "gateway"
    
    @property
    def networks(self) -> List[str]:
        return ["edge"]
    
    def get_required_secrets(self) -> List[str]:
        return ["CF_DOCKER_TOKEN"]
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        return [context['VOLUMES_DIR'] / 'cloudflared']
