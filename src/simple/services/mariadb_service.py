from simple.core.container import ServiceStrategy
from typing import Dict, List, Any
from pathlib import Path

class MariaDBService(ServiceStrategy):
    """MariaDB database service (LinuxServer.io)."""
    
    name = "mariadb"
    category = "database"
    
    @property
    def networks(self) -> List[str]:
        return ["db"]
    
    def get_required_secrets(self) -> List[str]:
        return ["MARIADB_ROOT_PASSPHRASE"]
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        volumes_dir = context.get('VOLUMES_DIR', Path('/mnt/vault/volumes'))
        return [
            volumes_dir / 'mariadb',
            volumes_dir / 'mariadb' / 'initdb.d'
        ]
