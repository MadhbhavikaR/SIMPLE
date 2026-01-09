#!/usr/bin/env python3

import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from platform import platform, release, node
import questionary

@dataclass
class PrereqConfig:
    """Prerequisite configuration structure."""
    name: str
    installed: bool
    binary_path: Optional[str]
    config_path: Optional[str]
    service_path: Optional[str]
    version: Optional[str] = None

class PrerequisiteDetector:
    """Detects security prerequisites across Linux distributions."""
    
    PREREQS_CONFIG = {
        "ufw": {
            "name": "UFW (Uncomplicated Firewall)",
            "binaries": ["/usr/sbin/ufw", "/sbin/ufw", "/usr/bin/ufw"],
            "config": ["/etc/ufw/ufw.conf", "/etc/default/ufw"],
            "service": ["/lib/systemd/system/ufw.service", "/etc/init.d/ufw"],
            "check_cmd": "ufw version"
        },
        "fail2ban": {
            "name": "Fail2Ban",
            "binaries": ["/usr/bin/fail2ban-client", "/usr/sbin/fail2ban-server", 
                        "/usr/bin/fail2ban-server"],
            "config": ["/etc/fail2ban/jail.conf", "/etc/fail2ban/jail.d", 
                      "/etc/fail2ban/jail.local"],
            "service": ["/lib/systemd/system/fail2ban.service"],
            "check_cmd": "fail2ban-client --version"
        },
        "apparmor": {
            "name": "AppArmor",
            "binaries": ["/sbin/apparmor_parser", "/usr/sbin/aa-status", 
                        "/usr/sbin/aa-enforce"],
            "config": ["/etc/apparmor.d", "/etc/apparmor"],
            "service": ["/lib/systemd/system/apparmor.service"],
            "check_cmd": "aa-status"
        }
    }
    
    OS_PATH_OVERRIDES = {
        "ubuntu": {
            "ufw": {"binaries": ["/usr/sbin/ufw"], "config": ["/etc/ufw/ufw.conf"]},
            "apparmor": {"binaries": ["/sbin/apparmor_parser"], "config": ["/etc/apparmor.d"]}
        },
        "debian": {
            "ufw": {"binaries": ["/usr/sbin/ufw"], "config": ["/etc/ufw/ufw.conf"]},
            "fail2ban": {"binaries": ["/usr/bin/fail2ban-client"]}
        },
        "raspbian": {  # DietPi base
            "ufw": {"binaries": ["/usr/sbin/ufw"]},
            "apparmor": {"binaries": ["/sbin/apparmor_parser"]}
        }
    }
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("config/prereqs.yaml")
        self.system_info = self._detect_system()
        self.detected: Dict[str, PrereqConfig] = {}
    
    def _detect_system(self) -> Dict[str, str]:
        """Detect OS distribution."""
        sys_info = {
            "platform": platform().lower(),
            "release": release(),
            "hostname": node(),
            "distro": "unknown"
        }
        
        # Detect distro from os-release
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        sys_info["distro"] = line.strip().split("=")[1].strip('"')
                        break
        except FileNotFoundError:
            pass
        
        return sys_info
    
    def detect_all(self) -> Dict[str, PrereqConfig]:
        """Detect all prerequisites."""
        print(f"🔍 Detecting on {self.system_info['distro']} ({self.system_info['release']})")
        
        for prereq_name, config in self.PREREQS_CONFIG.items():
            prereq = self._detect_single(prereq_name, config)
            self.detected[prereq_name] = prereq
            
            status = "✅" if prereq.installed else "❌"
            print(f"  {status} {prereq.name}")
        
        return self.detected
    
    def _detect_single(self, name: str, config: Dict) -> PrereqConfig:
        """Detect single prerequisite."""
        # Apply OS-specific overrides
        if self.system_info['distro'] in self.OS_PATH_OVERRIDES:
            config = {**config, **self.OS_PATH_OVERRIDES[self.system_info['distro']].get(name, {})}
        
        binary_path = self._find_binary(config["binaries"])
        config_path = self._find_config(config["config"])
        service_path = self._find_service(config["service"])
        version = self._get_version(name, binary_path, config.get("check_cmd"))
        
        return PrereqConfig(
            name=config["name"],
            installed=bool(binary_path),
            binary_path=binary_path,
            config_path=config_path,
            service_path=service_path,
            version=version
        )
    
    def _find_binary(self, paths: List[str]) -> Optional[str]:
        """Find first existing binary."""
        for path in paths:
            if Path(path).exists() and os.access(path, os.X_OK):
                return path
        return None
    
    def _find_config(self, paths: List[str]) -> Optional[str]:
        """Find first existing config directory/file."""
        for path in paths:
            p = Path(path)
            if p.exists() and (p.is_dir() or p.is_file()):
                return str(p)
        return None
    
    def _find_service(self, paths: List[str]) -> Optional[str]:
        """Find first existing service file."""
        for path in paths:
            if Path(path).exists():
                return path
        return None
    
    def _get_version(self, name: str, binary: Optional[str], check_cmd: str) -> Optional[str]:
        """Get version information."""
        if not binary:
            return None
        
        try:
            result = subprocess.run(
                check_cmd.split() if check_cmd else [binary, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
    
    def interactive_override(self) -> None:
        """Interactive configuration override."""
        print("\n🔧 CUSTOM PATH OVERRIDE")
        print("=" * 50)
        
        for name, prereq in self.detected.items():
            if not prereq.installed:
                continue
                
            override = questionary.confirm(
                f"Custom path for {prereq.name}?",
                default=False
            ).ask()
            
            if override:
                new_path = questionary.path(
                    f"{prereq.name} binary:",
                    default=prereq.binary_path or "",
                    validate=lambda x: Path(x).exists()
                ).ask()
                
                if new_path and Path(new_path).exists():
                    self.detected[name].binary_path = new_path
        
        self.save_config()
    
    def save_config(self) -> Path:
        """Save detected configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "system": self.system_info,
            "timestamp": str(os.times()),
            "prereqs": {k: asdict(v) for k, v in self.detected.items()}
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        os.chmod(self.config_path, 0o0644)
        print(f"💾 Config saved: {self.config_path}")
        return self.config_path
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load existing config."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return None
    
    def print_summary(self) -> None:
        """Print colored summary."""
        print("\n📊 PREREQUISITE SUMMARY")
        print("-" * 50)
        
        ready_count = sum(1 for p in self.detected.values() if p.installed)
        total = len(self.detected)
        
        for name, prereq in self.detected.items():
            status = "✅ READY" if prereq.installed else "❌ MISSING"
            paths = f"[{prereq.binary_path or 'N/A'}]"
            print(f"{status:>8} | {prereq.name:<25} | {paths}")
        
        print(f"\n🎯 {ready_count}/{total} prerequisites ready")
        return ready_count == total

def main():
    """CLI entrypoint."""
    detector = PrerequisiteDetector()
    
    # Detect
    detector.detect_all()
    
    # Interactive override
    if questionary.confirm("Configure custom paths?").ask():
        detector.interactive_override()
    
    # Summary
    all_ready = detector.print_summary()
    
    if all_ready:
        print("🚀 System ready for Home Infra deployment!")
        sys.exit(0)
    else:
        print("⚠️  Install missing prerequisites before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()
