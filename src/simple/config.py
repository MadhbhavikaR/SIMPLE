import os
import pwd
import grp
import time
import socket
from pathlib import Path
from typing import Dict, Any
import questionary
from cryptography.fernet import Fernet

class ConfigManager:
    """Detects system parameters and manages configuration context."""
    
    def __init__(self):
        self.context: Dict[str, Any] = {}
    
    def detect_system(self) -> None:
        """Auto-detects all system parameters."""
        uid = os.getuid()
        gid = os.getgid()
        user_info = pwd.getpwuid(uid)
        group_info = grp.getgrgid(gid)
        
        self.context.update({
            "PUID": str(uid),
            "PGID": str(gid),
            "PUSER": user_info.pw_name,
            "PGROUP": group_info.gr_name,
            "TZ": self._detect_timezone(),
            "HOSTNAME": socket.gethostname(),
            "BASE_DIR": Path.cwd(),
            "UMASK": "0022",
            "SWAG_STAGING": "false"
        })
    
    def wizard(self) -> Dict[str, Any]:
        """Interactive configuration wizard."""
        print("🔍 System detected:", f"{self.context['PUSER']}:{self.context['PUID']}:{self.context['PGID']}")
        
        # Path selection
        base_path = questionary.path(
            "Installation directory",
            default=str(self.context["BASE_DIR"]),
            only_directories=True
        ).ask()
        self.context.update({
            "BASE_DIR": Path(base_path).resolve(),
            "DOCKER_DIR": Path(base_path) / "docker",
            "VOLUMES_DIR": Path(base_path) / "volumes",
            "SCRIPTS_DIR": Path(base_path) / "scripts"
        })
        
        # Network configuration
        self.context["DOMAIN"] = questionary.text("Domain name (e.g., example.com):").ask()
        self.context["EMAIL"] = questionary.text("SSL Email:").ask()
        
        # Cloudflare token
        self.context["CF_DOCKER_TOKEN"] = questionary.password("Cloudflare Tunnel Token:").ask()
        
        return self.context
    
    def _detect_timezone(self) -> str:
        """Auto-detect timezone."""
        try:
            return time.tzname[0]
        except:
            return "UTC"
