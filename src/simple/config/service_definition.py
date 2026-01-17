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

class ServiceDefinition:
    """Immutable service definition loaded from about.yaml"""

    def __init__(self, name: str, meta: Dict[str, Any]):
        self.service_name = name
        self.display_name = meta.get("name", name)
        self.description = meta.get("description", "")
        self.url = meta.get("url", "")
        self.version = meta.get("version", "latest")
        self.category = meta.get("category", "misc")
        self.enforced = bool(meta.get("enforced", False))
        self.docker_image = meta.get("docker_image", "")
        self.dependencies = meta.get("dependencies", [])
        self.ports = meta.get("ports", {})
        self.alternatives = meta.get("alternatives", ["default"])

    def to_selection_label(self) -> str:
        return f"{self.display_name} ({self.version}) — {self.description}"
