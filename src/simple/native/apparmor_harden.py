# simple/native/apparmor_app.py
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from simple.core.os_hardening import SecurityEnforcerBase

class AppArmorEnforcer(SecurityEnforcerBase):
    """
    AppArmor enforcer:
      - detect() checks for AppArmor tooling
      - process() validates/provides the profile path (expects context['profile_path'])
      - apply(payload, dry_run) installs the profile using apparmor_parser
    """

    def detect(self) -> bool:
        return shutil.which('aa-status') is not None or shutil.which('apparmor_parser') is not None

    def process(self) -> Dict[str, Any]:
        profile = self.context.get('APPARMOR_PROFILE')  # Path or string
        if profile is None:
            return {'error': 'no_profile'}
        profile_path = Path(profile) if not isinstance(profile, Path) else profile
        if not profile_path.exists():
            return {'error': 'not_found', 'path': profile_path}
        return {'profile_path': profile_path}

    def apply(self, payload: Optional[Dict[str, Any]] = None, dry_run: bool = False) -> bool:
        if not self.detect():
            print("AppArmor tooling not available.")
            return False

        data = payload or self.process()
        if data.get('error'):
            print("AppArmor process error:", data['error'])
            return False

        profile_path: Path = data['profile_path']
        if dry_run:
            print("DRY-RUN: would install AppArmor profile:", profile_path)
            return True

        try:
            subprocess.run(['apparmor_parser', '-r', str(profile_path)],
                           check=True, capture_output=True, text=True, timeout=30)
            return True
        except subprocess.CalledProcessError as e:
            print("Failed to install AppArmor profile:", e.stderr)
            return False
        except subprocess.TimeoutExpired:
            print("Timeout installing AppArmor profile")
            return False
