import os
import pwd
import grp
import socket
import subprocess
import secrets
import string
import yaml
from pathlib import Path
from typing import Dict, Any, List
import questionary
# from cryptography.fernet import Fernet

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
        
        # Detect filesystem
        vault_path, filesystem = self._detect_filesystem()
        
        # Detect network interfaces
        network_interfaces = self._detect_network_interfaces()
        
        self.context.update({
            "PUID": str(uid),
            "PGID": str(gid),
            "PUSER": user_info.pw_name,
            "PGROUP": group_info.gr_name,
            "TZ": self._detect_timezone(),
            "HOSTNAME": socket.gethostname(),
            "BASE_DIR": Path.cwd(),
            "VAULT_PATH": vault_path or "/mnt/vault",
            "FILESYSTEM": filesystem or "unknown",
            "NETWORK_INTERFACES": network_interfaces,
            "UMASK": "0022",
            "SWAG_STAGING": "false"
        })
    
    def wizard(self, load_existing: bool = True) -> Dict[str, Any]:
        """
        Interactive configuration wizard.
        
        Args:
            load_existing: If True, try to load existing config.yaml
        """
        # Try to load existing config
        existing_config = {}
        docker_dir = self.context.get("BASE_DIR", Path.cwd()) / "docker"
        if load_existing:
            config_path = docker_dir / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    existing_config = yaml.safe_load(f) or {}
                    print("📋 Loaded existing configuration")
        
        print("🔍 System detected:", f"{self.context['PUSER']}:{self.context['PUID']}:{self.context['PGID']}")
        
        # Path selection
        base_path = questionary.path(
            "Installation directory",
            default=str(existing_config.get("BASE_DIR", self.context["BASE_DIR"])),
            only_directories=True
        ).ask()
        self.context["BASE_DIR"] = Path(base_path).resolve()
        
        # Filesystem configuration
        vault_path = existing_config.get("VAULT_PATH") or self.context.get("VAULT_PATH", "/mnt/vault")
        detected_vault = questionary.path(
            "Vault storage path (where volumes will be stored):",
            default=str(vault_path),
            only_directories=True
        ).ask()
        self.context["VAULT_PATH"] = Path(detected_vault).resolve()
        
        # Set paths based on vault location (SRS requirement: /mnt/vault)
        self.context["VOLUMES_DIR"] = self.context["VAULT_PATH"] / "volumes"
        self.context["DOCKER_DIR"] = self.context["BASE_DIR"] / "docker"
        self.context["SCRIPTS_DIR"] = self.context["BASE_DIR"] / "scripts"
        
        # Network configuration
        self.context["DOMAIN"] = questionary.text(
            "Domain name (e.g., example.com):",
            default=existing_config.get("DOMAIN", "")
        ).ask()
        self.context["EMAIL"] = questionary.text(
            "SSL Email:",
            default=existing_config.get("EMAIL", "")
        ).ask()
        
        # Subdomains (configurable, not hardcoded)
        subdomains = questionary.text(
            "Subdomains (comma-separated, e.g., drive,books,memories):",
            default=existing_config.get("SUBDOMAINS", "drive,books,memories")
        ).ask()
        self.context["SUBDOMAINS"] = subdomains
        
        # Cloudflare token (only ask if not in existing config)
        if "CF_DOCKER_TOKEN" not in existing_config:
            self.context["CF_DOCKER_TOKEN"] = questionary.password("Cloudflare Tunnel Token:").ask()
        else:
            self.context["CF_DOCKER_TOKEN"] = existing_config["CF_DOCKER_TOKEN"]
        
        # Ask about password generation for services
        if questionary.confirm("Auto-generate secure passwords for services?", default=True).ask():
            self.context["AUTO_GENERATE_PASSWORDS"] = True
        else:
            self.context["AUTO_GENERATE_PASSWORDS"] = False
        
        return self.context
    
    def _detect_timezone(self) -> str:
        """Auto-detect timezone."""
        try:
        # Try reading from /etc/timezone
            with open("/etc/timezone", "r") as f:
                return f.read().strip()
        except (FileNotFoundError, PermissionError, OSError):
            return os.environ.get("TZ", "UTC")
    
    def _detect_filesystem(self) -> tuple:
        """
        Detect mounted filesystem, specifically looking for /mnt/vault.
        
        Returns:
            Tuple of (mount_path, filesystem_type)
        """
        try:
            result = subprocess.run(
                ['findmnt', '-n', '-o', 'TARGET,FSTYPE', '/mnt/vault'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split()
                if len(parts) >= 2:
                    return parts[0], parts[1]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback: check if /mnt/vault exists
        vault_path = Path('/mnt/vault')
        if vault_path.exists() and vault_path.is_mount():
            try:
                result = subprocess.run(
                    ['stat', '-f', '-c', '%T', str(vault_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return str(vault_path), result.stdout.strip()
            except (subprocess.TimeoutExpired, OSError):
                pass
        
        return None, None
    
    def _detect_network_interfaces(self) -> List[str]:
        """Detect available network interfaces."""
        interfaces = []
        try:
            result = subprocess.run(
                ['ip', '-o', 'link', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        ifname = parts[1].strip().split()[0]
                        if ifname and ifname != 'lo':
                            interfaces.append(ifname)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return interfaces
    
    def generate_password(self, length: int = 32, include_special: bool = True) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Password length (default 32)
            include_special: Include special characters (default True)
            
        Returns:
            Generated password string
        """
        alphabet = string.ascii_letters + string.digits
        if include_special:
            alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def validate_password(self, password: str, min_length: int = 16) -> tuple:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            min_length: Minimum length requirement
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        return True, ""
