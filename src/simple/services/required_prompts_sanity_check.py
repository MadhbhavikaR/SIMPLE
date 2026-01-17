#!/usr/bin/env python3
"""
Required Prompts Sanity Check
=============================

This module validates that all required prompts are present in service templates.
"""

from typing import List, Dict, Any
from pathlib import Path
import re

from simple.config.config_reader import ConfigReader
from .sanity_check import SanityCheck

class RequiredPromptsSanityCheck(SanityCheck):
    """
    Validates that all required prompts are present in service templates.

    This check ensures:
    1. All prompts marked as required in about.yaml are used in the template
    2. Reports missing required prompts for each service/alternative
    """

    def __init__(self):
        super().__init__(
            name="required_prompts_validation",
            description="Validate that required prompts are present in service templates"
        )
        self.config_reader = ConfigReader()
        self.services_dir = self.config_reader.template_dir / "services"

    def run(self) -> tuple[bool, str]:
        """Run the required prompts validation check."""
        if not self.services_dir.exists():
            return (False, "Services directory not found")

        all_valid = True
        messages = []

        for service_dir in self.services_dir.iterdir():
            if not service_dir.is_dir():
                continue

            about_file = service_dir / "about.yaml"
            if not about_file.exists():
                continue

            try:
                # Load about.yaml
                with open(about_file, 'r', encoding='utf-8') as f:
                    about_data = yaml.safe_load(f)

                if not about_data:
                    continue

                # Get all prompts from about.yaml
                prompts = about_data.get('prompts', [])
                required_prompts = [p for p in prompts if p.get('required', False)]

                if not required_prompts:
                    continue

                # Check each alternative template
                alternatives_data = about_data.get('alternatives', [])
                if not alternatives_data:
                    # Check default template
                    default_template = service_dir / "default.yaml.jinja"
                    if default_template.exists():
                        self._validate_template_against_prompts(
                            service_dir.name, "default", required_prompts,
                            default_template, messages
                        )
                    continue

                # Handle both legacy and new format alternatives
                if isinstance(alternatives_data, list) and alternatives_data and isinstance(alternatives_data[0], str):
                    # Legacy format: alternatives: ["default", "minimal"]
                    for alt_name in alternatives_data:
                        template_file = service_dir / f"{alt_name}.yaml.jinja"
                        if template_file.exists():
                            self._validate_template_against_prompts(
                                service_dir.name, alt_name, required_prompts,
                                template_file, messages
                            )
                else:
                    # New format: alternatives: [{name: "default", description: "..."}]
                    for alt in alternatives_data:
                        if isinstance(alt, str):
                            alt_name = alt
                        else:
                            alt_name = alt.get('name', 'default')

                        template_file = service_dir / f"{alt_name}.yaml.jinja"
                        if template_file.exists():
                            self._validate_template_against_prompts(
                                service_dir.name, alt_name, required_prompts,
                                template_file, messages
                            )

            except Exception as e:
                messages.append(f"❌ Service {service_dir.name}: Error during validation - {e}")
                all_valid = False

        if all_valid:
            return (True, "All required prompts are present in service templates")
        else:
            return (False, "\n".join(messages))

    def _validate_template_against_prompts(self, service_name: str, alt_name: str,
                                         required_prompts: List[Dict[str, Any]],
                                         template_file: Path, messages: List[str]) -> None:
        """
        Validate that a template contains all required prompts.

        Args:
            service_name: Name of the service
            alt_name: Name of the alternative
            required_prompts: List of required prompts from about.yaml
            template_file: Path to the template file
            messages: List to append validation messages to
        """
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Extract variable names from template
            used_variables = self._extract_variables_from_template(template_content)

            # Check if all required prompts are used in the template
            missing_prompts = []
            for prompt in required_prompts:
                prompt_name = prompt['name']
                if prompt_name not in used_variables:
                    missing_prompts.append(prompt_name)

            if missing_prompts:
                messages.append(
                    f"❌ Service {service_name} (alternative {alt_name}): "
                    f"Missing required prompts: {', '.join(missing_prompts)}"
                )
            else:
                messages.append(
                    f"✅ Service {service_name} (alternative {alt_name}): "
                    f"All {len(required_prompts)} required prompts are present"
                )

        except Exception as e:
            messages.append(
                f"⚠️  Service {service_name} (alternative {alt_name}): "
                f"Error validating template - {e}"
            )

    def _extract_variables_from_template(self, template_content: str) -> set:
        """
        Extract variable names from a Jinja2 template.

        Args:
            template_content: Content of the template file

        Returns:
            Set of variable names found in the template
        """
        variables = set()

        # Look for Jinja2 variable patterns: {{ VAR_NAME }} or {{ VAR_NAME|filter }}
        variable_pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)(?:\|[^}}]*)?\s*\}\}'
        matches = re.findall(variable_pattern, template_content)
        variables.update(matches)

        # Look for environment variable patterns: ${{ VAR_NAME }}
        env_pattern = r'\{\{\s*\$\{([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
        env_matches = re.findall(env_pattern, template_content)
        variables.update(env_matches)

        # Look for secret file references: /run/secrets/VAR_NAME
        secret_pattern = r'/run/secrets/([a-zA-Z_][a-zA-Z0-9_]*)'
        secret_matches = re.findall(secret_pattern, template_content)
        variables.update(secret_matches)

        return variables
