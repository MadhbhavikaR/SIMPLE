import os
import sys
import pwd
import grp
import socket
import subprocess
import secrets
import string
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import questionary
from simple.config.config_reader import ConfigReader
from .service_definition import ServiceDefinition

class ServiceRepository:
    """Service discovery and metadata loader"""

    def __init__(self, config_reader: ConfigReader, templates_dir: Path = None):
        if templates_dir is None:
            templates_dir = config_reader.template_dir
        self.services_dir = templates_dir / "services"
        self.config_reader = config_reader

    def discover_services(self) -> List[ServiceDefinition]:
        services: List[ServiceDefinition] = []

        if not self.services_dir.exists():
            return services

        for service_dir in self.services_dir.iterdir():
            if not service_dir.is_dir():
                continue

            about_file = service_dir / "about.yaml"
            if not about_file.exists():
                continue

            # Read the about.yaml file directly instead of using config_reader
            # which is designed for config files, not template files
            try:
                with open(about_file, 'r', encoding='utf-8') as f:
                    import yaml
                    about_data = yaml.safe_load(f)
                    
                if about_data:
                    services.append(ServiceDefinition(service_dir.name, about_data))
            except Exception as e:
                print(f"⚠️  Failed to load service {service_dir.name}: {e}")
                continue

        return services
