"""Application services."""

from .base import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path


class NextcloudService(ServiceStrategy):
    """Nextcloud service (LinuxServer.io)."""
    
    name = "nextcloud"
    category = "app"
    
    @property
    def networks(self) -> List[str]:
        return ["app"]
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        volumes_dir = context.get('VOLUMES_DIR', Path('/mnt/vault/volumes'))
        return [
            volumes_dir / 'nextcloud' / 'config',
            volumes_dir / 'nextcloud' / 'data',
            volumes_dir / 'nextcloud' / 'custom-cont-init.d'
        ]


class CalibreWebService(ServiceStrategy):
    """Calibre Web Automated service."""
    
    name = "calibre-web-automated"
    category = "app"
    
    @property
    def networks(self) -> List[str]:
        return ["app"]
    
    def get_required_secrets(self) -> List[str]:
        return []
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        volumes_dir = context.get('VOLUMES_DIR', Path('/mnt/vault/volumes'))
        return [
            volumes_dir / 'calibre' / 'config',
            volumes_dir / 'calibre' / 'library',
            volumes_dir / 'calibre' / 'plugins'
        ]


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
