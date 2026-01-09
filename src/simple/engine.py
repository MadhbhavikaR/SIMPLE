import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from .services import AVAILABLE_SERVICES

class DockerEngine:
    """Generates complete Docker Compose infrastructure."""
    
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.selected_services: List[ServiceStrategy] = []
        self.secrets: Dict[str, str] = {}
    
    def select_services(self) -> None:
        """Interactive service selection."""
        print("\n🎛️  SERVICE SELECTION")
        print("-" * 50)
        
        for service in AVAILABLE_SERVICES:
            if service.category == "core":
                self.selected_services.append(service)
                print(f"✅ {service.name} (CORE - auto-enabled)")
                continue
            
            choice = questionary.checkbox(
                f"Enable {service.name}",
                choices=["enabled"],
                qmark="?",
                default=False
            ).ask()
            
            if choice:
                self.selected_services.append(service)
                self._collect_secrets(service)
    
    def _collect_secrets(self, service: ServiceStrategy) -> None:
        """Securely collect service secrets."""
        for secret_key in service.get_required_secrets():
            if secret_key not in self.secrets:
                value = questionary.password(
                    f"[{service.name}] {secret_key}:"
                ).ask()
                self.secrets[secret_key] = value
    
    def generate(self) -> None:
        """Generate complete infrastructure."""
        self._create_directories()
        self._write_env_file()
        self._write_compose_file()
    
    def _create_directories(self) -> None:
        """Create all required directories with correct permissions."""
        dirs_to_create = [
            self.context['DOCKER_DIR'],
            self.context['VOLUMES_DIR'],
            self.context['SCRIPTS_DIR']
        ]
        
        for service in self.selected_services:
            dirs_to_create.extend(service.get_volume_paths(self.context))
        
        for dir_path in set(dirs_to_create):
            dir_path.mkdir(parents=True, exist_ok=True)
            os.chmod(dir_path, 0o0755)
    
    def _write_env_file(self) -> None:
        """Write secure .env file."""
        env_path = self.context['DOCKER_DIR'] / '.env'
        env_content = {}
        
        # System variables
        for key, value in self.context.items():
            if isinstance(value, (str, int)):
                env_content[key] = str(value)
        
        # Secrets (with validation)
        env_content.update(self.secrets)
        
        with open(env_path, 'w', encoding='utf-8') as f:
            yaml.dump(env_content, f, default_flow_style=False)
        
        os.chmod(env_path, 0o0600)
    
    def _write_compose_file(self) -> None:
        """Generate docker-compose.yaml."""
        compose_path = self.context['DOCKER_DIR'] / 'docker-compose.yaml'
        
        compose = {
            'version': '3.8',
            'networks': {},
            'x-vault-app-defaults': {
                'user': f"${{{self.context['PUID']}}}:{self.context['PGID']}",
                'read_only': True,
                'cap_drop': ['ALL'],
                'security_opt': ['no-new-privileges:true'],
                'tmpfs': ['/tmp:rw,noexec,nosuid,size=64m'],
                'restart': 'unless-stopped'
            },
            'x-lsio-defaults': {
                'security_opt': ['no-new-privileges:true'],
                'tmpfs': ['/tmp:rw,noexec,nosuid,size=64m', '/run:rw,exec,nosuid,nodev,size=32m'],
                'restart': 'unless-stopped'
            },
            'services': {}
        }
        
        # Add networks from services
        for service in self.selected_services:
            for network in service.networks:
                compose['networks'][network] = {'driver': 'bridge', 'internal': network != 'net_edge'}
        
        # Generate services
        for service in self.selected_services:
            service_yaml = yaml.safe_load(service.generate_service_yaml(self.context))
            compose['services'].update(service_yaml)
        
        with open(compose_path, 'w', encoding='utf-8') as f:
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)
        
        os.chmod(compose_path, 0o0644)
