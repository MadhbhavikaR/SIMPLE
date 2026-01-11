from dataclasses import dataclass
from typing import Optional


@dataclass
class PrereqConfig:
    """Prerequisite configuration structure."""
    name: str
    installed: bool
    binary_path: Optional[str] = None
    config_path: Optional[str] = None
    service_path: Optional[str] = None
    version: Optional[str] = None
    install_cmd: Optional[str] = None
    keyword: Optional[str] = None
