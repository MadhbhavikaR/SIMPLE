#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Dict, Any, Optional


from simple.config.config_reader import ConfigReader
from simple.detectors import Detector
from simple.config.models.prereqquisite import PrereqConfig

class PrerequisiteAppsDetector(Detector):
    """Detects prerequisites from single YAML config."""
    
    def __init__(self, config_reader: ConfigReader):
        super().__init__(config_reader)
        self.detected: Dict[str, PrereqConfig] = {}
        self.system_info = self._detect_system()
        
        # Load single config - fixed filename
        config_result = self.config_reader.read_yaml_config("prerequisites")
        if not config_result.success:
            raise ValueError(f"Failed to load prerequisites.yaml: {config_result.error}")
        
        self.tools_config = config_result.data or {}
    
    def _detect_system(self) -> Dict[str, Any]:
        """Detect OS distro, release + privilege manager."""
        sys_info = {
            "distro": "unknown",
            "release": "unknown",
            "priv_manager": "sudo"
        }
        
        # Detect OS from /etc/os-release
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        sys_info["distro"] = line.strip().split("=")[1].strip('"')
                    elif line.startswith("VERSION_ID="):
                        sys_info["release"] = line.strip().split("=")[1].strip('"')
                    elif line.startswith("PRETTY_NAME="):
                        sys_info["release"] = line.strip().split("=")[1].strip('"')
        except FileNotFoundError:
            pass
        
        # Detect privilege manager (pkexec preceeds sudo)
        for pkexec_path in ["/usr/bin/pkexec", "/bin/pkexec"]:
            if Path(pkexec_path).exists():
                sys_info["priv_manager"] = "pkexec"
                break
        
        return sys_info
    
    def detect(self) -> Dict[str, PrereqConfig]:
        """Silent detection."""
        for tool_name, tool_config in self.tools_config.items():
            result = self._detect_single(tool_name, tool_config)
            self.detected[tool_name] = result
        return self.detected
    
    def _detect_single(self, name: str, config: Dict) -> PrereqConfig:
        """Detect single tool with OS overrides."""
        tool_config = config.copy()
        
        # Apply OS-specific override
        os_overrides = config.get("os_overrides", {})
        install_cmd = None
        keyword = None
        
        if self.system_info["distro"] in os_overrides:
            override = os_overrides[self.system_info["distro"]]
            
            # Merge locations
            if "locations" in override:
                tool_config["locations"] = {
                    **config["locations"],
                    **override["locations"]
                }
            
            # Get OS-specific install_cmd (string) and keyword
            install_cmd = override.get("install_cmd")
            keyword = override.get("keyword")
            
            # Build full command: priv_manager + install_cmd + keyword
            if install_cmd and keyword:
                full_cmd = f"{self.system_info['priv_manager']} {install_cmd} {keyword}"
            else:
                full_cmd = None
        else:
            full_cmd = None
        
        # Path detection
        locations = tool_config.get("locations", {})
        binaries = locations.get("binaries", [])
        configs = locations.get("config", [])
        services = locations.get("service", [])
        
        binary_path = self._find_paths(binaries, is_binary=True)
        config_path = self._find_paths(configs)
        service_path = self._find_paths(services)
        
        return PrereqConfig(
            name=config["name"],
            installed=bool(binary_path),
            binary_path=binary_path,
            config_path=config_path,
            service_path=service_path,
            version=None,
            install_cmd=full_cmd,
            keyword=keyword
        )
    
    def get_missing_install_command(self) -> Optional[str]:
        """Get single command to install ALL missing prerequisites."""
        missing_keywords = [
            prereq.keyword for prereq in self.detected.values() 
            if not prereq.installed and prereq.keyword
        ]
        
        if not missing_keywords:
            return None
        
        # Use first detected install_cmd as template
        for prereq in self.detected.values():
            if prereq.install_cmd and prereq.keyword:
                # Extract priv_manager + install_cmd base
                parts = prereq.install_cmd.split()
                priv_manager = parts[0]
                install_base = " ".join(parts[1:-1])  # Everything except keyword
                return f"{priv_manager} {install_base} {' '.join(missing_keywords)}"
        
        return None
    
    def print_summary(self) -> bool:
        """Summary with OS info and copy-paste install commands."""
        print(f"\n🖥️  OS: {self.system_info['distro']} ({self.system_info['release']})")
        print(f"🔐 Privilege: {self.system_info['priv_manager']}")
        print("\n📊 PREREQUISITE SUMMARY")
        print("-" * 60)
        
        ready_count = 0
        total = len(self.detected)
        
        for name, prereq in self.detected.items():
            status = "✅ READY" if prereq.installed else "❌ MISSING"
            line = f"{status:<12} | {prereq.name:<30}"
            
            if not prereq.installed and prereq.install_cmd:
                line += f" | 💾 {prereq.install_cmd}"
            
            print(line)
            
            if prereq.installed:
                ready_count += 1
        
        print(f"\n🎯 {ready_count}/{total} prerequisites ready")
        
        # Single command for ALL missing packages
        all_missing_cmd = self.get_missing_install_command()
        if all_missing_cmd:
            print(f"\n📦 COPY-PASTE ALL MISSING: {all_missing_cmd}")
        
        return ready_count == total
