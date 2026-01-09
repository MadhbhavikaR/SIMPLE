from simple.core.container import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path


class SwagService(ServiceStrategy):
    """SWAG reverse proxy service."""
    name = "swag"
    category = "gateway"
    
    @property
    def networks(self) -> List[str]:
        return ["edge", "app"]
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        return [context['VOLUMES_DIR'] / 'swag']
