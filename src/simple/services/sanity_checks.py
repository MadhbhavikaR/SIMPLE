#!/usr/bin/env python3
"""
Service Sanity Checks
=====================

This module implements extensible sanity checks for service configuration
validation. Checks are performed during startup to ensure all services
meet required criteria before the application proceeds.

Key Features:
- Chainable sanity check system
- Extensible validation framework
- Early failure detection
- Clear error reporting
- Required prompt validation for service alternatives
"""

from typing import List, Dict, Any, Callable
from pathlib import Path
import yaml
import re

from simple.config.config_reader import ConfigReader

class SanityCheck:
    """
    Base class for all sanity checks.

    Each sanity check should implement the run() method and return
    a tuple of (success: bool, message: str).
    """

    def __init__(self, name: str, description: str):
        """
        Initialize a sanity check.

        Args:
            name: Short name/identifier for the check
            description: Human-readable description of what this check validates
        """
        self.name = name
        self.description = description

    def run(self) -> tuple[bool, str]:
        """
        Run the sanity check.

        Returns:
            Tuple of (success, message) where success indicates if check passed
            and message provides details about the result
        """
        raise NotImplementedError("Subclasses must implement run() method")

class AlternativesSanityCheck(SanityCheck):
    """
    Validates that all services have proper alternatives configuration.

    This check ensures:
    1. Each service has at least one valid alternative
    2. Each service has a 'default' alternative
    3. Template files exist for all alternatives
    """

    def __init__(self):
        super().__init__(
            name="alternatives_validation",
            description="Validate service alternatives configuration"
        )
        self.config_reader = ConfigReader()
        self.services_dir = self.config_reader.template_dir / "services"

    def run(self) -> tuple[bool, str]:
        """Run the alternatives validation check."""
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
                    messages.append(f"⚠️  Service {service_dir.name}: Empty about.yaml")
                    all_valid = False
                    continue

                # Check alternatives structure - handle both old and new formats
                alternatives_data = about_data.get('alternatives', [])

                # Handle legacy format: alternatives: ["default"]
                if isinstance(alternatives_data, list) and alternatives_data and isinstance(alternatives_data[0], str):
                    # Legacy string array format
                    legacy_alternatives = []
                    for alt_name in alternatives_data:
                        template_file = service_dir / f"{alt_name}.yaml.jinja"
                        if template_file.exists():
                            legacy_alternatives.append(alt_name)
                        else:
                            messages.append(f"⚠️  Service {service_dir.name}: Legacy alternative '{alt_name}' ignored - template file not found")

                    if legacy_alternatives:
                        has_default = 'default' in legacy_alternatives
                        if not has_default:
                            messages.append(f"❌ Service {service_dir.name}: Legacy format missing required 'default' alternative")
                            all_valid = False
                        else:
                            messages.append(f"✅ Service {service_dir.name}: Using legacy format with {len(legacy_alternatives)} alternatives")
                    else:
                        messages.append(f"❌ Service {service_dir.name}: No valid legacy alternatives found")
                        all_valid = False
                    continue

                # Handle empty alternatives (no alternatives defined)
                if not alternatives_data:
                    # Check if default.yaml.jinja exists
                    default_template = service_dir / "default.yaml.jinja"
                    if default_template.exists():
                        messages.append(f"✅ Service {service_dir.name}: Using legacy format with default template")
                        continue
                    else:
                        messages.append(f"❌ Service {service_dir.name}: No alternatives defined and no default.yaml.jinja found")
                        all_valid = False
                        continue

                # New format validation
                validated_alternatives = []
                has_default = False

                for alt in alternatives_data:
                    # Handle case where alt might be a string (legacy format slipped through)
                    if isinstance(alt, str):
                        alt_name = alt
                        alt_description = "No description"
                    else:
                        alt_name = alt.get('name', 'default')
                        alt_description = alt.get('description', 'No description')

                    # Check if template file exists
                    template_file = service_dir / f"{alt_name}.yaml.jinja"

                    if template_file.exists():
                        validated_alternatives.append(alt_name)
                        if alt_name == 'default':
                            has_default = True
                    else:
                        messages.append(f"⚠️  Service {service_dir.name}: Alternative '{alt_name}' ignored - template file not found")

                if not validated_alternatives:
                    messages.append(f"❌ Service {service_dir.name}: No valid alternatives found")
                    all_valid = False
                elif not has_default:
                    messages.append(f"❌ Service {service_dir.name}: Missing required 'default' alternative")
                    all_valid = False
                else:
                    messages.append(f"✅ Service {service_dir.name}: {len(validated_alternatives)} valid alternatives ({validated_alternatives})")

            except Exception as e:
                messages.append(f"❌ Service {service_dir.name}: Error reading about.yaml - {e}")
                all_valid = False

        if all_valid:
            return (True, "All services have valid alternatives configuration")
        else:
            return (False, "\n".join(messages))

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

class SanityCheckRunner:
    """
    Runs a chain of sanity checks and reports results.

    This class implements an extensible chain-of-responsibility pattern
    for running multiple sanity checks in sequence.
    """

    def __init__(self):
        self.checks: List[SanityCheck] = []

    def add_check(self, check: SanityCheck) -> 'SanityCheckRunner':
        """
        Add a sanity check to the chain.

        Args:
            check: SanityCheck instance to add

        Returns:
            self for method chaining
        """
        self.checks.append(check)
        return self

    def run_all_checks(self) -> tuple[bool, List[tuple[bool, str]]]:
        """
        Run all registered sanity checks.

        Returns:
            Tuple of (overall_success, individual_results) where
            overall_success is True only if all checks passed,
            and individual_results contains (success, message) for each check
        """
        if not self.checks:
            return (True, [])

        results = []
        overall_success = True

        print("🔍 Running Sanity Checks")
        print("=" * 50)

        for check in self.checks:
            print(f"📋 {check.name}: {check.description}")
            success, message = check.run()
            results.append((success, message))

            if success:
                print(f"   ✅ PASS: {message}")
            else:
                print(f"   ❌ FAIL: {message}")
                overall_success = False

            print()

        return (overall_success, results)
