import subprocess
import shutil
from typing import Dict, Any

class SecurityEnforcer:
    """Applies system-level security hardening."""
    
    def __init__(self, context: Dict[str, Any]):
        self.context = context
    
    def apply_ufw(self) -> None:
        """Configure UFW firewall."""
        if not shutil.which('ufw'):
            print("⚠️  UFW not installed. Skipping.")
            return
        
        rules = [
            'ufw default deny incoming',
            'ufw default allow outgoing',
            'ufw allow 22/tcp comment "SSH"',
            'ufw allow 80/tcp from 192.168.100.0/24 comment "LAN HTTP"',
            'ufw allow 443/tcp from 192.168.100.0/24 comment "LAN HTTPS"',
            'ufw --force enable',
            'ufw reload'
        ]
        
        for rule in rules:
            try:
                subprocess.run(rule.split(), check=True, capture_output=True)
                print(f"✅ {rule.split()[0]} applied")
            except subprocess.CalledProcessError as e:
                print(f"❌ {rule}: {e}")
