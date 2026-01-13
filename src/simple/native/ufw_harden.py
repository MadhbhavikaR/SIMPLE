# simple/native/ufw_app.py
import shutil
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml  # pyyaml required
from simple.config import ConfigReader
from simple.core.os_hardening import SecurityEnforcerBase
from simple.config.dto.configuration import Configuration


TEMPLATES_DIR = Path(__file__).parent.parent.joinpath("templates", "native")
UFW_TEMPLATE_NAME = "ufw"  # will resolve to templates/native/ufw.yaml or .yaml.jinja

class UfwEnforcer(SecurityEnforcerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use ConfigReader pointed at the native templates dir
        self.config_reader = ConfigReader(config_dir=Path("config"), template_dir=TEMPLATES_DIR)

    def detect(self) -> bool:
        return shutil.which('ufw') is not None

    def _load_config(self) -> Dict[str, Any]:
        """
        Try to render the ufw template (Jinja2) with available context,
        then parse the resulting YAML. If rendering or parsing fails,
        fall back to built-in defaults.
        """
        # Prepare variables for template rendering from self.context
        # reasonable defaults assumed
        vars_dict = {
            "UFW_SERVICES": self.context.get("UFW_SERVICES", []),
            "UFW_EXTRA_RULES": self.context.get("UFW_EXTRA_RULES", []),
            "SSH_PORT": self.context.get("SSH_PORT", None),
            **(self.context.get("TEMPLATE_VARS", {}))
        }

        # Attempt to read/render template
        result: Configuration = self.config_reader.read_template(UFW_TEMPLATE_NAME, vars_dict)
        if result.success and result.data:
            try:
                # result.data is the rendered YAML text
                rendered_yaml = result.data if isinstance(result.data, str) else str(result.data)
                parsed = yaml.safe_load(rendered_yaml) or {}
                return parsed
            except Exception:
                # fall through to defaults on parse error
                pass

        # fallback defaults
        return {
            "base": [
                "ufw default deny incoming",
                "ufw default allow outgoing"
            ],
            "services": {
                "http": [
                    'ufw allow 80/tcp comment "HTTP"',
                    'ufw allow 443/tcp comment "HTTPS"'
                ]
            }
        }

    def process(self) -> List[str]:
        cfg = self._load_config()
        base_rules: List[str] = cfg.get("base", [])
        services_cfg: Dict[str, List[str]] = cfg.get("services", {})

        # SSH port
        ssh_enforcer = self.context.get('ssh_enforcer')
        if ssh_enforcer:
            ssh_data = ssh_enforcer.process()
            ssh_port = ssh_data.get('port', 22)
        else:
            # allow overriding via context or detection
            ssh_port = self.context.get("SSH_PORT") or self._detect_ssh_port()

        rules: List[str] = list(base_rules)
        # inject SSH rule after base rules
        rules.append(f'ufw allow {ssh_port}/tcp comment "SSH"')

        # Add rules for services declared in context (e.g., enabled services list)
        enabled_services = self.context.get("UFW_SERVICES", [])  # list of service keys
        for svc in enabled_services:
            svc_rules = services_cfg.get(svc)
            if svc_rules:
                rules.extend(svc_rules)

        # also include any additional rules from context
        extra_rules = self.context.get("UFW_EXTRA_RULES", [])
        if extra_rules:
            rules.extend(extra_rules)

        return rules

    def apply(self, payload: Optional[List[str]] = None, dry_run: bool = False) -> bool:
        if not self.detect():
            return False

        rules = payload if payload is not None else self.process()
        if dry_run:
            for r in rules:
                print("DRY-RUN:", r)
            return True

        ssh_enforcer = self.context.get('ssh_enforcer')
        has_ssh = ssh_enforcer.process().get('has_active_session') if ssh_enforcer else self._has_active_ssh_session()
        if not has_ssh:
            print("No active SSH session detected; skipping apply to avoid lockout.")
            return False

        for rule in rules:
            try:
                subprocess.run(rule.split(), check=True, capture_output=True, text=True, timeout=10)
            except subprocess.CalledProcessError as e:
                print(f"Failed to apply '{rule}': {e.stderr}")
                return False
            except subprocess.TimeoutExpired:
                print(f"Timeout applying '{rule}'")
                return False
        return True


    def _has_active_ssh_session(self) -> bool:
        try:
            result = subprocess.run(['who'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.splitlines():
                    if 'pts' in line or 'tty' in line:
                        return True
        except Exception:
            pass
        return False

    def _detect_lan_subnet(self, interfaces: List[str]) -> Optional[str]:
        import subprocess
        if not interfaces:
            return None
        try:
            for iface in interfaces:
                result = subprocess.run(['ip', 'addr', 'show', iface],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    continue
                for line in result.stdout.splitlines():
                    if 'inet ' in line and '/24' in line:
                        for part in line.split():
                            if '/24' in part:
                                ip = part.split('/')[0]
                                sp = ip.split('.')
                                if len(sp) == 4:
                                    return f"{sp[0]}.{sp[1]}.{sp[2]}.0/24"
        except Exception:
            pass
        return None
