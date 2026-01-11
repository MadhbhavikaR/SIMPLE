# simple/native/ssh_app.py
import subprocess
from typing import Dict, Any, Optional
from simple.core.os_hardening import SecurityEnforcerBase

class SSHEnforcer(SecurityEnforcerBase):
    """
    Provides SSH-related detection and a payload describing SSH state.
    process() returns a dict: {'port': int, 'has_active_session': bool}
    """

    def detect(self) -> bool:
        # ss is used to inspect listeners; if missing still considered available
        return True

    def process(self) -> Dict[str, Any]:
        return {
            'port': self._detect_ssh_port(),
            'has_active_session': self._has_active_ssh_session()
        }

    def apply(self, payload: Optional[Dict[str, Any]] = None, dry_run: bool = False) -> bool:
        # SSH enforcer does not change system state in this design.
        # Return True if detection/process yields sensible values.
        data = payload or self.process()
        return isinstance(data.get('port'), int)

    def _detect_ssh_port(self) -> int:
        try:
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=5)
            result.check_returncode()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
            return 22

        for line in result.stdout.splitlines():
            low = line.lower()
            if 'ssh' in low or ':22 ' in line or line.strip().endswith(':22'):
                parts = line.split()
                if len(parts) >= 4:
                    addr = parts[3]
                    if addr.startswith('[') and ']' in addr:
                        addr = addr.rsplit(']', 1)[-1]
                    if ':' in addr:
                        try:
                            return int(addr.split(':')[-1])
                        except ValueError:
                            continue
        return 22
