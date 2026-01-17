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

class ServiceRepository:
    """Service discovery and metadata loader"""

    def __init__(self, config_reader: ConfigReader, templates_dir: Path = Path("templates")):
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

            rel_path = about_file.relative_to(self.services_dir.parent)
            result = self.config_reader.read_yaml_config(str(rel_path)) #FIXME: do ot pass .yaml here

            if not result.success or not result.data:
                continue

            services.append(ServiceDefinition(service_dir.name, result.data))

        return services
