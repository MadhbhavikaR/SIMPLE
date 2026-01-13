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


class ConfigManager:
    """Interactive configuration wizard"""

    def __init__(self, config_reader: ConfigReader):
        self.config_reader = config_reader
        self.context: Dict[str, Any] = {}
        

    def wizard(self, load_existing: bool = True) -> Dict[str, Any]:
        print("SIMPLE Configuration Wizard")
        print("=" * 60)

        self._prompt_non_root_user()
        self._prompt_storage_mount()
        self._prompt_base_path_selection()
        self._prompt_volumes_location()
        self._prompt_docker_files_location()
        self._prompt_scripts_location()
        self._prompt_network_config()
        self._prompt_services_selection()

        self.detect_system()
        self._save_settings()

        print("\nConfiguration complete.")
        print(f"Settings saved to: {self.context['SCRIPTS_DIR']}/.settings.yaml")

        return self.context

    # -------------------------------------------------------------------------
    # USER & SYSTEM PROMPTS
    # -------------------------------------------------------------------------

    def _prompt_non_root_user(self) -> None:
        uid = os.getuid()
        if uid == 0:
            print("ERROR: This script must not run as root.")
            sys.exit(1)

        gid = os.getgid()
        user_info = pwd.getpwuid(uid)
        group_info = grp.getgrgid(gid)

        self.context.update({
            "PUID": str(uid),
            "PGID": str(gid),
            "PUSER": user_info.pw_name,
            "PGROUP": group_info.gr_name,
        })

        print(f"Running as user: {user_info.pw_name} ({uid}:{gid})")

    def _prompt_storage_mount(self) -> None:
        print("\nStorage Mount Check")

        mounts = []
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.splitlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 6:
                        mounts.append({
                            "device": parts[0],
                            "mount": parts[5],
                            "free": parts[3]
                        })
        except Exception:
            pass

        for idx, m in enumerate(mounts, 1):
            print(f"{idx}. {m['device']} -> {m['mount']} ({m['free']} free)")

        if not questionary.confirm("Is your storage mounted?").ask():
            print("Please mount your storage and re-run.")
            sys.exit(1)

    def _prompt_base_path_selection(self) -> None:
        base_path = questionary.path(
            "Select BASE installation directory:",
            os.path.dirname(os.path.realpath(__file__)),
            only_directories=True
        ).ask()

        self.context["BASE_DIR"] = Path(base_path).resolve()

    def _prompt_volumes_location(self) -> None:
        default = self.context["BASE_DIR"] / "volumes"
        path = questionary.path(
            "Docker volumes directory:",
            default=str(default),
            only_directories=True
        ).ask()

        self.context["VOLUMES_DIR"] = Path(path).resolve()

    def _prompt_docker_files_location(self) -> None:
        default = self.context["BASE_DIR"] / "docker"
        path = questionary.path(
            "Docker compose directory:",
            default=str(default),
            only_directories=True
        ).ask()

        self.context["DOCKER_DIR"] = Path(path).resolve()

    def _prompt_scripts_location(self) -> None:
        default = self.context["BASE_DIR"] / "scripts"
        path = questionary.path(
            "Scripts & templates directory:",
            default=str(default),
            only_directories=True
        ).ask()

        self.context["SCRIPTS_DIR"] = Path(path).resolve()

    def _prompt_network_config(self) -> None:
        self.context["DOMAIN"] = questionary.text("Base domain name:").ask()
        self.context["EMAIL"] = questionary.text("SSL email:").ask()
        self.context["SUBDOMAINS"] = questionary.text("Subdomains (comma separated):").ask()

    # -------------------------------------------------------------------------
    # SERVICE SELECTION
    # -------------------------------------------------------------------------

    def _prompt_services_selection(self) -> None:
        print("\nService Selection")

        repository = ServiceRepository(self.config_reader)
        services = repository.discover_services()

        if not services:
            print("No services found.")
            self.context["SERVICES"] = {}
            return

        mandatory = [s for s in services if s.enforced]
        optional = [s for s in services if not s.enforced]

        print("\nMandatory Services:")
        for svc in mandatory:
            print(f"  - {svc.to_selection_label()}")

        selected_optional: List[ServiceDefinition] = []
        if optional:
            choices = [
                {
                    "name": svc.to_selection_label(),
                    "value": svc,
                    "checked": False
                }
                for svc in optional
            ]

            selected_optional = questionary.checkbox(
                "Select additional services:",
                choices=choices
            ).ask()

        final_services = mandatory + selected_optional

        self.context["SERVICES"] = self._build_service_runtime_map(final_services)

        print("\nSelected Services:")
        for name in self.context["SERVICES"]:
            print(f"  - {name}")

    def _build_service_runtime_map(self, services: List[ServiceDefinition]) -> Dict[str, Any]:
        runtime_map: Dict[str, Any] = {}

        for svc in services:
            runtime_map[svc.service_name] = {
                "display_name": svc.display_name,
                "description": svc.description,
                "url": svc.url,
                "version": svc.version,
                "category": svc.category,
                "docker_image": svc.docker_image,
                "dependencies": svc.dependencies,
                "ports": svc.ports,
                "alternatives": svc.alternatives,
                "template": f"{svc.alternatives[0]}.yaml.jinja"
            }

        return runtime_map

    # -------------------------------------------------------------------------
    # SYSTEM DETECTION
    # -------------------------------------------------------------------------

    def detect_system(self) -> None:
        self.context.update({
            "TZ": self._detect_timezone(),
            "HOSTNAME": socket.gethostname(),
            "UMASK": "0022",
            "SWAG_STAGING": "false",
            "AUTO_GENERATE_PASSWORDS": True
        })

    def _detect_timezone(self) -> str:
        try:
            with open("/etc/timezone", "r") as f:
                return f.read().strip()
        except Exception:
            return os.environ.get("TZ", "UTC")

    # -------------------------------------------------------------------------
    # UTILITIES
    # -------------------------------------------------------------------------

    def generate_password(self, length: int = 32, include_special: bool = True) -> str:
        alphabet = string.ascii_letters + string.digits
        if include_special:
            alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    # -------------------------------------------------------------------------
    # SETTINGS
    # -------------------------------------------------------------------------

    def _save_settings(self) -> None:
        settings_path = self.context["SCRIPTS_DIR"] / ".settings.yaml"

        self.context["SCRIPTS_DIR"].mkdir(parents=True, exist_ok=True)

        with open(settings_path, "w") as f:
            yaml.dump(self.context, f, default_flow_style=False, sort_keys=False)

        os.chmod(settings_path, 0o600)
