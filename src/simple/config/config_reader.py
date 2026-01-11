#!/usr/bin/env python3
"""
Config Reader Utilities - YAML/JSON + Jinja2 Templates
======================================================
Single Responsibility: 
1. Read YAML config by name → Python dict/JSON
2. Render Jinja2 templates with variable substitution
"""

import os
import json
import yaml
import jinja2
from pathlib import Path
from typing import Dict, Any, Optional, List

from simple.config.models import Configuration

# Type aliases for clarity

TemplateVars = Dict[str, Any]

class ConfigReader:
    """Unified configuration reader with YAML→JSON and template rendering."""
    
    def __init__(self, config_dir: Path = Path("config"), 
                 template_dir: Path = Path("templates")):
        self.config_dir = Path(config_dir).resolve()
        self.template_dir = Path(template_dir).resolve()
        
        # Setup Jinja2 environment
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        # Custom filters
        env.filters['tojson'] = json.dumps
        self.jinja_env = env
    
    def read_yaml_config(self, config_name: str, as_json: bool = False) -> Configuration:
        """
        Read YAML config by name and return as dict or JSON string.
        
        Args:
            config_name: Filename (e.g., 'prerequisites.yaml', 'app-settings')
            as_json: Return JSON string instead of Python dict
            
        Returns:
            Config with data or error
        """
        config_path = self.config_dir / f"{config_name}.yaml"
        
        if not config_path.exists():
            return Configuration(
                success=False, 
                error=f"Config not found: {config_path}",
                path=config_path
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if as_json:
                json_str = json.dumps(data, indent=2, sort_keys=False)
                return Configuration(success=True, data=json_str, path=config_path)
            
            return Configuration(success=True, data=data, path=config_path)
            
        except yaml.YAMLError as e:
            return Configuration(
                success=False,
                error=f"YAML parsing error: {str(e)}",
                path=config_path
            )
        except Exception as e:
            return Configuration(
                success=False,
                error=f"Read error: {str(e)}",
                path=config_path
            )
    
    def read_template(self, template_name: str, vars_dict: TemplateVars, 
                     output_path: Optional[Path] = None) -> Configuration:
        """
        Render Jinja2 template with variables.
        
        Args:
            template_name: Template filename (e.g., 'docker-compose.yaml' or 'services/nextcloud/nextcloud.yaml')
                          Can include or exclude .jinja extension
            vars_dict: Variables to substitute {{ var_name }}
            output_path: Optional output file path
            
        Returns:
            Config with rendered content
        """
        # Try different template name variations
        template_variants = [
            f"{template_name}.jinja",  # services/nextcloud/nextcloud.yaml.jinja
            f"{template_name}",  # services/nextcloud/nextcloud.yaml (if .jinja is already in name)
            template_name.replace('.yaml', '.yaml.jinja'),  # Convert .yaml to .yaml.jinja
        ]
        
        template_path = None
        # template_name_to_load = None
        
        for variant in template_variants:
            test_path = self.template_dir / variant
            if test_path.exists():
                template_path = test_path
                # template_name_to_load = variant
                break
        
        if not template_path or not template_path.exists():
            return Configuration(
                success=False,
                error=f"Template not found. Tried: {', '.join([str(self.template_dir / v) for v in template_variants])}",
                path=None
            )
        
        try:
            # Jinja2 FileSystemLoader expects path relative to template_dir
            # Use the found template path relative to template_dir
            rel_path = template_path.relative_to(self.template_dir)
            template = self.jinja_env.get_template(str(rel_path))
            rendered = template.render(**vars_dict)
            
            result_data = rendered
            
            # Write to file if output_path specified
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(rendered)
                os.chmod(output_path, 0o0644)
                result_data = rendered  # Still return content
            
            return Configuration(success=True, data=result_data, path=template_path)
            
        except jinja2.TemplateError as e:
            return Configuration(
                success=False,
                error=f"Jinja2 render error: {str(e)}",
                path=template_path
            )
        except Exception as e:
            return Configuration(
                success=False,
                error=f"Template error: {str(e)}",
                path=template_path
            )
    
    def read_all_configs(self) -> Dict[str, Configuration]:
        """Read all YAML configs in config directory."""
        results = {}
        for config_file in self.config_dir.glob("*.yaml"):
            config_name = config_file.stem
            results[config_name] = self.read_yaml_config(config_name)
        return results
    
    def validate_template_vars(self, template_name: str, 
                             required_vars: List[str]) -> List[str]:
        """
        Validate required variables exist for template.
        
        Returns list of missing variables.
        """
        template_path = self.template_dir / f"{template_name}.yaml"
        if not template_path.exists():
            return [f"Template {template_name}.yaml not found"]
        
        missing = []
        with open(template_path, 'r') as f:
            content = f.read()
            for var in required_vars:
                if f"{{{{ {var} }}}}" in content or f"{{{{'{var}'}}}}" in content:
                    if var not in self.jinja_env.globals:
                        missing.append(var)
        
        return missing