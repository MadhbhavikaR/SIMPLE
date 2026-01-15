#!/usr/bin/env python3
"""
Unified Service Strategy with Alternatives Support
==================================================

This module implements a single unified service strategy class that supports
multiple configuration alternatives for each service. The class dynamically
loads service metadata from about.yaml files and handles alternative template
selection based on user preferences.

Key Features:
- Single class for all services (replaces individual service classes)
- Dynamic loading from about.yaml files
- Support for multiple configuration alternatives
- Template-based configuration generation
- SOLID principle compliant design
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from simple.core.container import ServiceStrategy
from simple.config.config_reader import ConfigReader, TemplateType


class UnifiedServiceStrategy(ServiceStrategy):
    """
    Unified service strategy that supports multiple configuration alternatives.
    
    This class replaces individual service classes and provides a flexible,
    template-driven approach to service configuration.
    """
    
    def __init__(self, service_name: str, about_data: Dict[str, Any], 
                 config_reader: Optional[ConfigReader] = None):
        """
        Initialize the unified service strategy.
        
        Args:
            service_name: The service identifier (e.g., 'authelia')
            about_data: Service metadata loaded from about.yaml
            config_reader: Optional ConfigReader instance for template loading
        """
        super().__init__()
        self.service_name = service_name
        self.about_data = about_data
        self.config_reader = config_reader or ConfigReader()
        
        # Set properties from about.yaml data
        self._name = service_name
        self._category = about_data.get('category', {}).get('enum', 'app')
        self._networks = about_data.get('networks', {}).get('enum', ['app'])
        
        # Initialize alternatives from about.yaml
        self._alternatives = self._parse_alternatives(about_data.get('alternatives', []))
        
        # Validate that we have at least one valid alternative
        self._validate_alternatives()
        
        # Default to the first valid alternative
        self.selected_alternative = self._alternatives[0]['name']
    
    def _parse_alternatives(self, alternatives_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and validate alternatives from about.yaml.
        Handles both new format and legacy format.
        
        Args:
            alternatives_data: Raw alternatives data from about.yaml
            
        Returns:
            List of validated alternatives with file existence checks
        """
        if not alternatives_data:
            # Fallback to legacy format: alternatives: []
            return [{'name': 'default', 'description': 'Default configuration'}]
        
        # Handle legacy string array format: alternatives: ["default"]
        if isinstance(alternatives_data, list) and alternatives_data and isinstance(alternatives_data[0], str):
            validated_alternatives = []
            for alt_name in alternatives_data:
                # Check if the alternative template file exists
                template_path = self.config_reader.template_dir / 'services' / self.service_name / f'{alt_name}.yaml.jinja'
                
                if template_path.exists():
                    validated_alternatives.append({
                        'name': alt_name,
                        'description': f'Legacy {alt_name} configuration',
                        'template_path': template_path
                    })
                else:
                    print(f"⚠️  Legacy alternative '{alt_name}' for {self.service_name} ignored: template file not found")
            
            return validated_alternatives
        
        # Handle new format: alternatives: [{name: "default", description: "..."}]
        validated_alternatives = []
        
        for alt in alternatives_data:
            # Handle case where alt might be a string (legacy format slipped through)
            if isinstance(alt, str):
                alt_name = alt
                alt_description = f'Legacy {alt_name} configuration'
            else:
                alt_name = alt.get('name', 'default')
                alt_description = alt.get('description', 'No description')
            
            # Check if the alternative template file exists
            template_path = self.config_reader.template_dir / 'services' / self.service_name / f'{alt_name}.yaml.jinja'
            
            if template_path.exists():
                validated_alternatives.append({
                    'name': alt_name,
                    'description': alt_description,
                    'template_path': template_path
                })
            else:
                print(f"⚠️  Alternative '{alt_name}' for {self.service_name} ignored: template file not found")
        
        return validated_alternatives
    
    def _validate_alternatives(self) -> None:
        """
        Validate that at least one alternative exists and includes a 'default' option.
        
        Raises:
            ValueError: If no valid alternatives are found or no default alternative exists
        """
        if not self._alternatives:
            raise ValueError(
                f"Service {self.service_name} has no valid alternatives. "
                f"Check that template files exist for all alternatives defined in about.yaml"
            )
        
        # Check for default alternative
        has_default = any(alt['name'] == 'default' for alt in self._alternatives)
        if not has_default:
            raise ValueError(
                f"Service {self.service_name} must have a 'default' alternative. "
                f"Available alternatives: {[alt['name'] for alt in self._alternatives]}"
            )
    
    def set_alternative(self, alternative_name: str) -> None:
        """
        Set the active alternative for this service.
        
        Args:
            alternative_name: Name of the alternative to activate
            
        Raises:
            ValueError: If the alternative doesn't exist
        """
        valid_names = [alt['name'] for alt in self._alternatives]
        if alternative_name not in valid_names:
            raise ValueError(
                f"Alternative '{alternative_name}' not found for {self.service_name}. "
                f"Valid alternatives: {valid_names}"
            )
        
        self.selected_alternative = alternative_name
        print(f"✅ Set {self.service_name} to use '{alternative_name}' alternative")
    
    def get_available_alternatives(self) -> List[Dict[str, str]]:
        """
        Get available alternatives for this service.
        
        Returns:
            List of dictionaries containing alternative name and description
        """
        return [
            {
                'name': alt['name'],
                'description': alt['description']
            }
            for alt in self._alternatives
        ]
    
    # ServiceStrategy interface implementation
    @property
    def name(self) -> str:
        """Unique service identifier."""
        return self._name
    
    @property
    def category(self) -> str:
        """Service category."""
        return self._category
    
    @property
    def networks(self) -> List[str]:
        """Required networks."""
        return self._networks
    
    def get_required_secrets(self) -> List[str]:
        """Secrets this service needs from user."""
        secrets = []

        # Extract secrets from prompts in about.yaml
        prompts = self.about_data.get('prompts', [])
        for prompt in prompts:
            prompt_type_str = prompt.get('type', {}).get('enum', ['STRING'])[0]
            if prompt_type_str in ['PASSWORD', 'SECRET']:
                secrets.append(prompt['name'])

        return secrets

    def get_required_prompts_for_alternative(self) -> List[Dict[str, Any]]:
        """
        Get prompts required for the currently selected alternative.
        Scans the selected template file for required variables and filters
        the about.yaml prompts accordingly.

        Returns:
            List of prompt dictionaries that are required for this alternative
        """
        # Get all prompts from about.yaml
        all_prompts = self.about_data.get('prompts', [])

        # Load the selected template to scan for required variables
        template_path = self.config_reader.template_dir / 'services' / self.service_name / f'{self.selected_alternative}.yaml.jinja'

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Scan template for variable usage patterns
            import re
            used_variables = set()

            # Look for Jinja2 variable patterns: {{ VAR_NAME }} or {{ VAR_NAME|filter }}
            variable_pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)(?:\|[^}}]*)?\s*\}\}'
            matches = re.findall(variable_pattern, template_content)

            # Also look for environment variable patterns: ${{ VAR_NAME }}
            env_pattern = r'\{\{\s*\$\{([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
            env_matches = re.findall(env_pattern, template_content)

            used_variables.update(matches)
            used_variables.update(env_matches)

            # Filter prompts to only those used in the selected template
            required_prompts = []
            for prompt in all_prompts:
                if prompt['name'] in used_variables:
                    required_prompts.append(prompt)

            return required_prompts

        except FileNotFoundError:
            print(f"⚠️  Template file not found: {template_path}")
            return all_prompts
        except Exception as e:
            print(f"⚠️  Error scanning template for required prompts: {e}")
            return all_prompts
    
    def generate_service_yaml(self, context: Dict[str, Any], dependencies: List[str] = None) -> str:
        """
        Generates Docker Compose service YAML from the selected alternative template.
        
        Args:
            context: Configuration context
            dependencies: List of dependency service names
            
        Returns:
            Rendered YAML string
        """
        # Convert Path objects to strings for template rendering
        template_context = {}
        for key, value in context.items():
            if isinstance(value, Path):
                template_context[key] = str(value)
            else:
                template_context[key] = value
        
        # Add dependencies to context
        if dependencies:
            template_context['DEPENDENCIES'] = dependencies
        
        # Load the lsio-defaults template first
        lsio_defaults_result = self.config_reader.read_template(
            "anchors/x-lsio-defaults.yaml",
            template_context
        )
        
        if lsio_defaults_result.success:
            template_context['lsio_defaults'] = lsio_defaults_result.data
        
        # Load the selected alternative template
        template_path = f"{self.service_name}/{self.selected_alternative}.yaml.jinja"
        result = self.config_reader.read_template(
            template_path,
            template_context,
            template_type=TemplateType.SERVICE
        )
        
        if not result.success:
            raise ValueError(
                f"Failed to load template for {self.service_name} "
                f"(alternative: {self.selected_alternative}): {result.error}"
            )
        
        # Combine with lsio-defaults if available
        if lsio_defaults_result.success:
            return f"{lsio_defaults_result.data}\n{result.data}"
        else:
            return result.data
    
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        """Returns volume directories to create."""
        volumes_dir = context.get('VOLUMES_DIR', Path('/mnt/vault/volumes'))
        return [volumes_dir / self.service_name]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get complete service metadata."""
        return {
            'name': self.name,
            'display_name': self.about_data.get('name', self.name),
            'description': self.about_data.get('description', ''),
            'version': self.about_data.get('version', 'latest'),
            'category': self.category,
            'networks': self.networks,
            'docker_image': self.about_data.get('docker_image', ''),
            'dependencies': self.about_data.get('dependencies', {}).get('services', []),
            'ports': self.about_data.get('ports', {}),
            'alternatives': self.get_available_alternatives(),
            'selected_alternative': self.selected_alternative,
            'enforced': self.about_data.get('enforced', False)
        }
