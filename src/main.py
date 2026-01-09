#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import questionary
from simple.config import ConfigManager
from simple.engine import DockerEngine
from simple.security import SecurityEnforcer
from simple.notifier import Notifier
from tests.test_suite import run_validation_suite

def main():
    # Security check: Validate environment
    if os.geteuid() != 0:
        print("❌ CRITICAL: Must run as root (sudo python main.py)")
        sys.exit(1)
    
    print("🚀 === S.I.M.P.L.E (Self-hosted Infrastructure Made Painless with Linux & Engineering) ===\n")
    
    # Step 1: System Detection [Single Responsibility]
    config = ConfigManager()
    config.detect_system()
    
    # Step 2: Interactive Wizard
    context = config.wizard()
    
    # Step 3: Service Selection
    engine = DockerEngine(context)
    engine.select_services()
    
    # Step 4: Generate Infrastructure
    engine.generate()
    
    # Step 5: Validation
    if questionary.confirm("Run validation suite?").ask():
        results = run_validation_suite(context)
        print(f"\n✅ Validation: {sum(results.values())}/{len(results)} passed")
    
    # Step 6: Security Hardening (optional)
    if questionary.confirm("Apply firewall rules?").ask():
        security = SecurityEnforcer(context)
        security.apply_ufw()
    
    # Step 7: Notifications
    notifier = Notifier(context)
    notifier.send("Setup completed successfully!")
    
    print(f"\n🎉 SUCCESS! Infrastructure ready at: {context['BASE_DIR']}")
    print("Next steps:")
    print("  1. cd docker && docker compose up -d")
    print("  2. Monitor: docker compose logs -f")

if __name__ == "__main__":
    main()
