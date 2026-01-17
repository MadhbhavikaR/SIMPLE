#!/usr/bin/env python3
"""
Service Discovery and Management
================================

This module handles dynamic service discovery and provides access to all available services.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import List, Type, Dict

from simple.core.container import ServiceStrategy
from simple.services.unified_service import UnifiedServiceStrategy
from simple.services.sanity_check import SanityCheck
from simple.services.alternatives_sanity_check import AlternativesSanityCheck
from simple.services.required_prompts_sanity_check import RequiredPromptsSanityCheck
from simple.services.sanity_check_runner import SanityCheckRunner
from simple.config.config_reader import ConfigReader

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

def _discover_unified_services() -> List[ServiceStrategy]:
    """
    Discover services using the new unified approach from about.yaml files.
    
    This method scans the templates/services directory for about.yaml files
    and creates UnifiedServiceStrategy instances for each valid service.
    """
    config_reader = ConfigReader()
    services_dir = config_reader.template_dir / "services"
    
    if not services_dir.exists():
        return []
    
    unified_services = []
    
    for service_dir in services_dir.iterdir():
        if not service_dir.is_dir():
            continue
        
        about_file = service_dir / "about.yaml"
        if not about_file.exists():
            continue
        
        # Load the about.yaml file
        try:
            about_data = {}
            with open(about_file, 'r', encoding='utf-8') as f:
                import yaml
                about_data = yaml.safe_load(f)
            
            if about_data:
                # Create unified service instance
                service_instance = UnifiedServiceStrategy(
                    service_name=service_dir.name,
                    about_data=about_data,
                    config_reader=config_reader
                )
                unified_services.append(service_instance)
        
        except Exception as e:
            print(f"⚠️  Failed to load service {service_dir.name}: {e}")
            continue
    
    return unified_services

def get_available_services() -> List[ServiceStrategy]:
    """
    Get all available services, preferring the unified approach.
    
    Returns:
        List of ServiceStrategy instances
    """
    # Try unified approach first
    unified_services = _discover_unified_services()
    
    if unified_services:
        # If we found unified services, use them exclusively
        return unified_services
    
    # Fallback to legacy approach if no unified services found
    print("⚠️  No unified services found, falling back to legacy service discovery")
    legacy_services = _discover_service_classes()
    return [service_cls() for service_cls in legacy_services]


# Use the new service discovery method
AVAILABLE_SERVICES = get_available_services()


__all__ = [
    "ServiceStrategy",
    "AVAILABLE_SERVICES",
    "UnifiedServiceStrategy",
    # Sanity check classes
    "SanityCheck",
    "AlternativesSanityCheck",
    "RequiredPromptsSanityCheck",
    "SanityCheckRunner",
]
