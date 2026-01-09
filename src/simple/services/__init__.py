import importlib
import pkgutil
import inspect
from pathlib import Path
from typing import List, Type, Dict

from simple.core.container import ServiceStrategy

PACKAGE_PATH = Path(__file__).parent

def _discover_service_classes() -> List[Type[ServiceStrategy]]:
    """
    Import all service modules and return concrete ServiceStrategy subclasses.
    Enforces that each module defines exactly one concrete subclass of ServiceStrategy.
    """
    # Import each module in this package
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module_name}")

    services: List[Type[ServiceStrategy]] = []
    # Map module name -> list of discovered concrete subclasses defined in that module
    per_module: Dict[str, List[Type[ServiceStrategy]]] = {}

    for cls in ServiceStrategy.__subclasses__():
        # only consider classes defined in this package (avoid subclasses from elsewhere)
        module_name = getattr(cls, "__module__", "")
        # Filter to classes defined in modules under this package
        if not module_name.startswith(__name__ + "."):
            continue
        # Skip abstract base classes
        if getattr(cls, "__abstractmethods__", None):
            continue
        per_module.setdefault(module_name, []).append(cls)

    # Enforce one concrete subclass per module
    for module_name, cls_list in per_module.items():
        if len(cls_list) == 0:
            continue
        if len(cls_list) > 1:
            raise AssertionError(
                f"Module {module_name!r} defines multiple concrete ServiceStrategy subclasses: "
                f"{[c.__name__ for c in cls_list]}"
            )
        services.append(cls_list[0])

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
