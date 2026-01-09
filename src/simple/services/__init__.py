"""Service registry and exports."""

from .base import ServiceStrategy
from .core.core import NetworkManager, SocketProxyService
from .gateways import CloudflaredService, SwagService
from .database import MariaDBService
from .apps import NextcloudService, CalibreWebService, PhotoprismService, AutheliaService, DIUNService
from .security import CrowdSecService

# Registry of all available services
AVAILABLE_SERVICES = [
    NetworkManager(),
    SocketProxyService(),
    CloudflaredService(),
    SwagService(),
    CrowdSecService(),
    MariaDBService(),
    NextcloudService(),
    CalibreWebService(),
    PhotoprismService(),
    AutheliaService(),
    DIUNService(),
]

__all__ = [
    'ServiceStrategy',
    'AVAILABLE_SERVICES',
    'NetworkManager',
    'SocketProxyService',
    'CloudflaredService',
    'SwagService',
    'CrowdSecService',
    'MariaDBService',
    'NextcloudService',
    'CalibreWebService',
    'PhotoprismService',
    'AutheliaService',
    'DIUNService',
]
