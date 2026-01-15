import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
import questionary
from .services import AVAILABLE_SERVICES
from .core.container import ServiceStrategy

class DockerEngine:
    """Generates complete Docker Compose infrastructure."""
    
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.selected_services: List[ServiceStrategy] = []
        self.secrets: Dict[str, str] = {}
        self.existing_services: set = set()  # Track existing services for merging
        self.dependencies: Dict[str, List[str]] = {}  # Service dependencies
    
    def _load_existing_compose(self) -> Dict[str, Any]:
        """Load existing compose file if it exists for regeneration."""
        compose_path = self.context['DOCKER_DIR'] / 'docker-compose.yaml'
        if compose_path.exists():
            with open(compose_path, 'r', encoding='utf-8') as f:
                existing = yaml.safe_load(f)
                if existing and 'services' in existing:
                    self.existing_services = set(existing['services'].keys())
                    print(f"📋 Found {len(self.existing_services)} existing services")
                    return existing
        return {}
    
    def _load_dependencies(self) -> None:
        """Load service dependencies from YAML file."""
        from simple.config.config_reader import ConfigReader
        config_reader = ConfigReader()
        
        deps_path = config_reader.template_dir / 'services' / 'dependencies.yaml'
        if deps_path.exists():
            with open(deps_path, 'r', encoding='utf-8') as f:
                deps_data = yaml.safe_load(f)
                self.dependencies = deps_data.get('dependencies', {})
                self.optional_dependencies = deps_data.get('optional_dependencies', {})
        else:
            self.dependencies = {}
            self.optional_dependencies = {}
    
    def _resolve_dependencies(self, service_name: str, selected_service_names: set) -> List[str]:
        """
        Resolve dependencies for a service based on selected services.
        
        Args:
            service_name: Name of the service
            selected_service_names: Set of selected service names
            
        Returns:
            List of dependency service names that are actually selected
        """
        deps = []
        
        # Check required dependencies
        if service_name in self.dependencies:
            for dep in self.dependencies[service_name]:
                if dep in selected_service_names:
                    deps.append(dep)
        
        # Check optional dependencies
        if service_name in self.optional_dependencies:
            for dep in self.optional_dependencies[service_name]:
                if dep in selected_service_names:
                    deps.append(dep)
        
        return deps
    
    def _get_service_secrets(self, service_name: str) -> List[str]:
        """
        Get list of secret names used by a service.

        Args:
            service_name: Name of the service

        Returns:
            List of secret names
        """
        # Load about.yaml data to get secrets dynamically
        about_data = self._load_service_about_data(service_name)
        prompts = about_data.get('prompts', [])

        # Extract secret names from prompts where type is PASSWORD or SECRET
        secrets = []
        for prompt in prompts:
            prompt_type_str = prompt.get('type', {}).get('enum', ['STRING'])[0]
            if prompt_type_str in ['PASSWORD', 'SECRET']:
                secrets.append(prompt['name'])

        # Filter out secrets that don't exist in self.secrets
        return [s for s in secrets if s in self.secrets]
    
    def _load_service_about_data(self, service_name: str) -> Dict[str, Any]:
        """
        Load about.yaml data for a service.

        Args:
            service_name: Name of the service

        Returns:
            Dictionary containing service metadata from about.yaml
        """
        from simple.config.config_reader import ConfigReader
        config_reader = ConfigReader()

        about_path = config_reader.template_dir / 'services' / service_name / 'about.yaml'
        if about_path.exists():
            with open(about_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _get_prompt_input(self, prompt_data: Dict[str, Any]) -> str:
        """
        Get user input based on prompt type and validation rules.

        Args:
            prompt_data: Dictionary containing prompt configuration

        Returns:
            User input value
        """
        from .core.prompt import PromptType

        prompt_name = prompt_data.get('name', '')
        description = prompt_data.get('description', '')
        prompt_type_str = prompt_data.get('type', {}).get('enum', ['STRING'])[0]
        required = prompt_data.get('required', False)

        # Convert string to enum
        try:
            prompt_type = PromptType[prompt_type_str]
        except KeyError:
            raise ValueError(f"Invalid prompt type '{prompt_type_str}' in about.yaml. Valid types: {[e.name for e in PromptType]}")

        # Use enum-based logic
        if prompt_type == PromptType.PASSWORD or prompt_type == PromptType.SECRET:
            return questionary.password(f"[{prompt_name}] {description}:").ask()
        elif prompt_type == PromptType.STRING:
            return questionary.text(f"[{prompt_name}] {description}:").ask()
        elif prompt_type == PromptType.NUMBER:
            return questionary.text(f"[{prompt_name}] {description}:", validate=lambda x: x.isdigit() or "Please enter a valid number").ask()
        elif prompt_type == PromptType.EMAIL:
            return questionary.text(f"[{prompt_name}] {description}:", validate=lambda x: '@' in x and '.' in x or "Please enter a valid email").ask()
        elif prompt_type == PromptType.DOMAIN:
            return questionary.text(f"[{prompt_name}] {description}:", validate=lambda x: '.' in x and not x.startswith('.') and not x.endswith('.') or "Please enter a valid domain").ask()
        elif prompt_type == PromptType.PATH:
            return questionary.path(f"[{prompt_name}] {description}:").ask()
        else:
            # Default to text input
            return questionary.text(f"[{prompt_name}] {description}:").ask()

    def select_services(self, allow_incremental: bool = True) -> None:
        """
        Interactive service selection with detailed information from about.yaml files.
        Now supports alternative configuration selection for services.

        Args:
            allow_incremental: If True, load existing services and allow adding new ones
        """
        # Load existing compose if regenerating
        existing_compose = {}
        if allow_incremental:
            existing_compose = self._load_existing_compose()
            if existing_compose:
                print("🔄 Regeneration mode: Found existing services")
        # Load dependencies
        self._load_dependencies()
        print("\n🎛️  SERVICE SELECTION")
        print("-" * 50)

        # Group services by category for better organization
        services_by_category = {}
        for service in AVAILABLE_SERVICES:
            category = service.category
            if category not in services_by_category:
                services_by_category[category] = []
            services_by_category[category].append(service)

        # Process services by category
        for category, services in services_by_category.items():
            print(f"\n📋 {category.upper()} SERVICES")
            print("=" * 40)

            for service in services:
                # Load about.yaml data for this service
                about_data = self._load_service_about_data(service.name)
                service_name = about_data.get('name', service.name)
                description = about_data.get('description', 'No description available')
                enforced = about_data.get('enforced', False)

                # Check if service already exists
                is_existing = service.name in self.existing_services

                if category == "core" or enforced:
                    # For enforced services, show alternative selection if available
                    self._handle_service_with_alternatives(service, about_data, is_enforced=True)
                    continue

                # Show service information
                print(f"\n📦 {service_name}")
                print(f"     {description}")

                # Ask user if they want to enable this service
                default_value = is_existing
                choice = questionary.confirm(
                    f"Enable {service_name}?" + (" (already configured)" if is_existing else ""),
                    default=default_value,
                    qmark="?"
                ).ask()

                if choice:
                    self._handle_service_with_alternatives(service, about_data, is_enforced=False)
    
    def _collect_secrets(self, service: ServiceStrategy, about_data: Dict[str, Any] = None) -> None:
        """Securely collect service secrets."""
        for secret_key in service.get_required_secrets():
            if secret_key not in self.secrets:
                # Check if auto-generation is enabled
                if self.context.get('AUTO_GENERATE_PASSWORDS', False):
                    from simple.config import ConfigManager
                    config = ConfigManager()
                    generated = config.generate_password(length=32)
                    if questionary.confirm(
                        f"[{service.name}] Auto-generate {secret_key}?",
                        default=True
                    ).ask():
                        self.secrets[secret_key] = generated
                        print(f"   ✅ Generated secure {secret_key}")
                        continue
                 
                value = questionary.password(
                    f"[{service.name}] {secret_key}:"
                ).ask()
                self.secrets[secret_key] = value

    def _handle_service_with_alternatives(self, service: ServiceStrategy,
                                         about_data: Dict[str, Any],
                                         is_enforced: bool = False) -> None:
        """
        Handle service selection with alternative configuration options.
        
        Args:
            service: ServiceStrategy instance
            about_data: Service metadata from about.yaml
            is_enforced: Whether this service is enforced/auto-enabled
        """
        service_name = about_data.get('name', service.name)
        
        # Check if the service supports alternatives (unified service approach)
        if hasattr(service, 'get_available_alternatives'):
            alternatives = service.get_available_alternatives()
            
            if len(alternatives) > 1:
                # Multiple alternatives available - let user choose
                choices = [
                    {
                        'name': f"{alt['name']}: {alt['description']}",
                        'value': alt['name']
                    }
                    for alt in alternatives
                ]
                
                if is_enforced:
                    print(f"✅ {service_name} (AUTO-ENABLED)")
                    if about_data.get('description'):
                        print(f"     {about_data['description']}")

                    # For enforced services, ask which alternative to use
                    if choices:
                        selected_alternative = questionary.select(
                            f"Select configuration alternative for {service_name}:",
                            choices=choices
                        ).ask()
                    else:
                        raise ValueError(f"No alternatives available for enforced service {service_name}")
                else:
                    # For optional services, ask which alternative to use
                    if choices:
                        selected_alternative = questionary.select(
                            f"Select configuration alternative for {service_name}:",
                            choices=choices,
                            default=choices[0]['value']
                        ).ask()
                    else:
                        selected_alternative = questionary.select(
                            f"Select configuration alternative for {service_name}:",
                            choices=choices
                        ).ask()
                
                # Set the selected alternative
                service.set_alternative(selected_alternative)
            elif len(alternatives) == 1:
                # Only one alternative (default) - use it automatically
                if is_enforced:
                    print(f"✅ {service_name} (AUTO-ENABLED)")
                    if about_data.get('description'):
                        print(f"     {about_data['description']}")
                else:
                    print(f"✅ {service_name} enabled with default configuration")

                # Use the single available alternative
                service.set_alternative(alternatives[0]['name'])
            else:
                # No valid alternatives - this shouldn't happen due to sanity checks
                print(f"⚠️  {service_name} has no valid alternatives, using default")
        else:
            # Legacy service - handle as before
            if is_enforced:
                self.selected_services.append(service)
                print(f"✅ {service_name} (AUTO-ENABLED)")
                if about_data.get('description'):
                    print(f"     {about_data['description']}")
            else:
                self.selected_services.append(service)

                # Use dynamic prompt scanning based on selected alternative
                if hasattr(service, 'get_required_prompts_for_alternative'):
                    prompts = service.get_required_prompts_for_alternative()
                else:
                    prompts = about_data.get('prompts', [])

                for prompt in prompts:
                    prompt_value = self._get_prompt_input(prompt)
                    # Store prompt values in secrets or context as appropriate
                    prompt_type_str = prompt.get('type', {}).get('enum', ['STRING'])[0]
                    if prompt_type_str in ['PASSWORD', 'SECRET']:
                        self.secrets[prompt['name']] = prompt_value
                    else:
                        self.context[prompt['name']] = prompt_value

                # Collect any additional secrets not covered by prompts
                self._collect_secrets(service, about_data)
        
        # Add to selected services if not already there
        if service not in self.selected_services:
            self.selected_services.append(service)
    
    def generate(self) -> None:
        """Generate complete infrastructure."""
        self._create_directories()
        self._write_config_file()
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
    
    def _write_config_file(self) -> None:
        """Write central config file for non-secret values."""
        config_path = self.context['DOCKER_DIR'] / 'config.yaml'
        
        # Only store non-secret configuration values
        config_data = {}
        secret_keys = set(self.secrets.keys())
        secret_keys.update(['CF_DOCKER_TOKEN', 'MARIADB_ROOT_PASSPHRASE', 'PHOTOPRISM_ADMIN_PASSWORD',
                           'AUTHELIA_JWT_SECRET', 'AUTHELIA_SESSION_SECRET', 'AUTHELIA_STORAGE_PASSWORD',
                           'CROWDSEC_API_KEY'])
        
        for key, value in self.context.items():
            if key not in secret_keys and isinstance(value, (str, int, Path)):
                # Convert Path to string
                config_data[key] = str(value) if isinstance(value, Path) else value
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        os.chmod(config_path, 0o0644)
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load existing config file if it exists."""
        config_path = self.context['DOCKER_DIR'] / 'config.yaml'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _write_env_file(self) -> None:
        """Write .env file with all non-secret variables for Docker Compose substitution."""
        env_path = self.context['DOCKER_DIR'] / '.env'
        
        # Build .env file content (key=value format)
        env_lines = []
        
        # Define which keys are secrets (should use Docker secrets)
        secret_keys = set(self.secrets.keys())
        secret_keys.update(['CF_DOCKER_TOKEN', 'MARIADB_ROOT_PASSPHRASE', 'PHOTOPRISM_ADMIN_PASSWORD',
                           'AUTHELIA_JWT_SECRET', 'AUTHELIA_SESSION_SECRET', 'AUTHELIA_STORAGE_PASSWORD',
                           'CROWDSEC_API_KEY'])
        
        # Add all non-secret variables to .env
        for key, value in self.context.items():
            if key not in secret_keys and isinstance(value, (str, int, Path)):
                # Convert Path to string
                env_value = str(value) if isinstance(value, Path) else value
                env_lines.append(f"{key}={env_value}")
        
        # Add U_ID and G_ID for consistency (mapped from PUID/PGID)
        env_lines.append(f"U_ID={self.context['PUID']}")
        env_lines.append(f"G_ID={self.context['PGID']}")
        
        # Add VOLUMES_DIR explicitly (used in templates)
        env_lines.append(f"VOLUMES_DIR={self.context['VOLUMES_DIR']}")
        
        # Note: Secrets are NOT written to .env - they use Docker secrets
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_lines) + '\n')
        
        os.chmod(env_path, 0o0644)
    
    def _write_compose_file(self) -> None:
        """Generate docker-compose.yaml using templates."""
        from simple.config.config_reader import ConfigReader
        
        compose_path = self.context['DOCKER_DIR'] / 'docker-compose.yaml'
        config_reader = ConfigReader()
        
        # Load network template
        from simple.config.config_reader import TemplateType
        networks_result = config_reader.read_template('networks.yaml.jinja', self.context, template_type=TemplateType.NETWORK)
        if not networks_result.success:
            raise ValueError(f"Failed to load networks template: {networks_result.error}")

        # Load defaults templates
        vault_defaults_result = config_reader.read_template('anchors/x-vault-app-defaults.yaml.jinja', self.context)
        if not vault_defaults_result.success:
            raise ValueError(f"Failed to load vault-app-defaults template: {vault_defaults_result.error}")

        lsio_defaults_result = config_reader.read_template('anchors/x-lsio-defaults.yaml.jinja', self.context)
        if not lsio_defaults_result.success:
            raise ValueError(f"Failed to load lsio-defaults template: {lsio_defaults_result.error}")
        
        # Parse network YAML
        networks_yaml = yaml.safe_load(networks_result.data)
        
        # Build compose structure
        compose = {
            'networks': networks_yaml.get('networks', {}),
            'services': {}
        }
        
        # Add defaults as YAML anchors (parse from template output)
        vault_defaults_yaml = yaml.safe_load(vault_defaults_result.data)
        lsio_defaults_yaml = yaml.safe_load(lsio_defaults_result.data)
        compose.update(vault_defaults_yaml)
        compose.update(lsio_defaults_yaml)
        
        # Add Docker secrets section (only if we have secrets)
        if self.secrets:
            compose['secrets'] = {}
            secrets_dir = self.context['DOCKER_DIR'] / 'secrets'
            secrets_dir.mkdir(exist_ok=True)
            os.chmod(secrets_dir, 0o0700)
            
            # Create secret files and add to compose
            for secret_name, secret_value in self.secrets.items():
                secret_file = secrets_dir / secret_name
                with open(secret_file, 'w', encoding='utf-8') as f:
                    f.write(secret_value)
                os.chmod(secret_file, 0o0600)
                
                # Add to compose secrets (relative path from docker-compose.yaml location)
                secret_relative_path = secret_file.relative_to(self.context['DOCKER_DIR'])
                compose['secrets'][secret_name] = {
                    'file': str(secret_relative_path)
                }
        
        # Get selected service names for dependency resolution
        selected_service_names = {s.name for s in self.selected_services if s.name != "networks"}
        
        # Check for Docker socket mounting (security warning)
        socket_mounts = []
        
        # Generate services (skip NetworkManager as it's just a network definition)
        for service in self.selected_services:
            if service.name == "networks":
                continue  # Networks are defined above
            
            # Resolve dependencies for this service
            resolved_deps = self._resolve_dependencies(service.name, selected_service_names)
            
            # Add dependencies to context for template rendering
            template_context = self.context.copy()
            template_context['DEPENDENCIES'] = resolved_deps
            
            service_yaml_str = service.generate_service_yaml(template_context)
            if service_yaml_str.strip():  # Only process non-empty YAML
                service_yaml = yaml.safe_load(service_yaml_str)
                if service_yaml:
                    for svc_name, svc_config in service_yaml.items():
                        # Add depends_on dynamically if dependencies exist
                        if resolved_deps:
                            svc_config['depends_on'] = resolved_deps
                        elif 'depends_on' in svc_config:
                            # Remove depends_on if no dependencies are selected
                            del svc_config['depends_on']

                        # Add Docker secrets to service if it uses any
                        service_secrets = self._get_service_secrets(service.name)
                        if service_secrets:
                            if 'secrets' not in svc_config:
                                svc_config['secrets'] = []
                            for secret_name in service_secrets:
                                if secret_name in compose.get('secrets', {}):
                                    # Add secret reference (Docker Compose format)
                                    svc_config['secrets'].append({
                                        'source': secret_name,
                                        'target': secret_name
                                    })

                        # Add network assignments from about.yaml
                        about_data = self._load_service_about_data(service.name)
                        networks_enum = about_data.get('networks', {}).get('enum', [])
                        if networks_enum:
                            svc_config['networks'] = networks_enum

                        # Check for direct docker.sock mounts
                        volumes = svc_config.get('volumes', [])
                        for vol in volumes:
                            if isinstance(vol, str) and '/var/run/docker.sock' in vol:
                                if 'socket-proxy' not in selected_service_names:
                                    socket_mounts.append(svc_name)
                    
                    compose['services'].update(service_yaml)
        
        # Merge with existing services if regenerating
        existing_compose = self._load_existing_compose()
        if existing_compose and 'services' in existing_compose:
            # Keep existing services that weren't regenerated
            for svc_name, svc_config in existing_compose['services'].items():
                if svc_name not in compose['services']:
                    compose['services'][svc_name] = svc_config
                    print(f"📦 Preserved existing service: {svc_name}")
        
        # Warn about direct socket mounts
        if socket_mounts:
            print("\n⚠️  SECURITY WARNING:")
            print("   The following services mount /var/run/docker.sock directly:")
            for svc in socket_mounts:
                print(f"     - {svc}")
            print("   This is a security risk. Consider using the socket-proxy service instead.")
            if not questionary.confirm("Continue anyway?", default=False).ask():
                raise ValueError("Aborted due to security concerns")
        
        with open(compose_path, 'w', encoding='utf-8') as f:
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)
        
        os.chmod(compose_path, 0o0644)
