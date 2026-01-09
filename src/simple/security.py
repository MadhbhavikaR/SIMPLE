import subprocess
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path

class SecurityEnforcer:
    """Applies system-level security hardening."""
    
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.ufw_rules: List[str] = []
    
    def preview_ufw_rules(self) -> List[str]:
        """Generate UFW rules preview without applying."""
        if not shutil.which('ufw'):
            return []
        
        # Detect SSH port
        ssh_port = self._detect_ssh_port()
        
        # Get network interfaces for LAN detection
        interfaces = self.context.get('NETWORK_INTERFACES', [])
        lan_subnet = self._detect_lan_subnet(interfaces)
        
        rules = [
            'ufw default deny incoming',
            'ufw default allow outgoing',
            f'ufw allow {ssh_port}/tcp comment "SSH"',
        ]
        
        if lan_subnet:
            rules.extend([
                f'ufw allow 80/tcp from {lan_subnet} comment "LAN HTTP"',
                f'ufw allow 443/tcp from {lan_subnet} comment "LAN HTTPS"',
            ])
        
        self.ufw_rules = rules
        return rules
    
    def apply_ufw(self, dry_run: bool = False) -> bool:
        """
        Configure UFW firewall.
        
        Args:
            dry_run: If True, only preview rules without applying
            
        Returns:
            True if successful, False otherwise
        """
        if not shutil.which('ufw'):
            print("⚠️  UFW not installed. Skipping.")
            return False
        
        if not self.ufw_rules:
            self.preview_ufw_rules()
        
        if dry_run:
            print("🔍 DRY-RUN: Would apply the following UFW rules:")
            for rule in self.ufw_rules:
                print(f"  {rule}")
            return True
        
        print("🔒 Applying UFW firewall rules...")
        
        # Check if SSH is currently active to avoid lockout
        if not self._check_ssh_active():
            print("⚠️  WARNING: No active SSH session detected. Skipping UFW enable to prevent lockout.")
            print("   Apply rules manually after verifying SSH access.")
            return False
        
        for rule in self.ufw_rules:
            try:
                result = subprocess.run(
                    rule.split(),
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                print(f"✅ {rule.split()[0]} applied")
            except subprocess.CalledProcessError as e:
                print(f"❌ {rule}: {e.stderr}")
                return False
            except subprocess.TimeoutExpired:
                print(f"❌ {rule}: Timeout")
                return False
        
        return True
    
    def _detect_ssh_port(self) -> int:
        """Detect SSH port from systemd or default."""
        try:
            result = subprocess.run(
                ['ss', '-tlnp'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'ssh' in line.lower() or ':22 ' in line:
                        # Extract port from line
                        parts = line.split()
                        if parts:
                            addr = parts[3]
                            if ':' in addr:
                                port = int(addr.split(':')[-1])
                                return port
        except:
            pass
        return 22  # Default SSH port
    
    def _detect_lan_subnet(self, interfaces: List[str]) -> Optional[str]:
        """Detect LAN subnet from network interfaces."""
        if not interfaces:
            return None
        
        try:
            # Try to get IP and subnet from first non-loopback interface
            for iface in interfaces:
                result = subprocess.run(
                    ['ip', 'addr', 'show', iface],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'inet ' in line and '/24' in line:
                            # Extract subnet (e.g., 192.168.1.0/24)
                            parts = line.split()
                            for part in parts:
                                if '/24' in part:
                                    ip = part.split('/')[0]
                                    # Convert to subnet (e.g., 192.168.1.0/24)
                                    subnet_parts = ip.split('.')
                                    if len(subnet_parts) == 4:
                                        return f"{subnet_parts[0]}.{subnet_parts[1]}.{subnet_parts[2]}.0/24"
        except:
            pass
        
        return None
    
    def _check_ssh_active(self) -> bool:
        """Check if there's an active SSH session to avoid lockout."""
        try:
            result = subprocess.run(
                ['who'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                # Check if any session is SSH
                for line in result.stdout.split('\n'):
                    if 'pts' in line or 'tty' in line:
                        return True
        except:
            pass
        return False
    
    def detect_apparmor(self) -> bool:
        """Detect if AppArmor is available."""
        return shutil.which('aa-status') is not None
    
    def install_apparmor_profile(self, profile_path: Path, dry_run: bool = False) -> bool:
        """
        Install AppArmor profile.
        
        Args:
            profile_path: Path to AppArmor profile file
            dry_run: If True, only preview without installing
            
        Returns:
            True if successful, False otherwise
        """
        if not self.detect_apparmor():
            print("⚠️  AppArmor not available. Skipping.")
            return False
        
        if not profile_path.exists():
            print(f"❌ Profile not found: {profile_path}")
            return False
        
        if dry_run:
            print(f"🔍 DRY-RUN: Would install AppArmor profile: {profile_path}")
            return True
        
        try:
            # Load profile
            result = subprocess.run(
                ['apparmor_parser', '-r', str(profile_path)],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"✅ AppArmor profile installed: {profile_path.name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install AppArmor profile: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout installing AppArmor profile")
            return False
