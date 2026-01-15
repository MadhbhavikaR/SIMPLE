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
"""

from typing import List, Dict, Any, Callable
from pathlib import Path
import yaml

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
