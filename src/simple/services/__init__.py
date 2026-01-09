import importlib
import pkgutil
from typing import List, Type

from simple.core.container import ServiceStrategy


def _discover_service_classes() -> List[Type[ServiceStrategy]]:
    """
    Import all service modules and return concrete ServiceStrategy subclasses.
    """
    # Use __path__ directly — do NOT import simple.services
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module_name}")

    services: List[Type[ServiceStrategy]] = []

    for cls in ServiceStrategy.__subclasses__():
        # Skip abstract base classes
        if getattr(cls, "__abstractmethods__", None):
            continue
        services.append(cls)

    return services


# Instantiate all discovered services
AVAILABLE_SERVICES = [
    service_cls()
    for service_cls in _discover_service_classes()
]


__all__ = [
    "ServiceStrategy",
    "AVAILABLE_SERVICES",
]
