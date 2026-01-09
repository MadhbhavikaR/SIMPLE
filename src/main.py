#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from simple.native.apparmor_harden import AppArmorEnforcer
from simple.native.ufw_harden import UfwEnforcer
from simple.native.ssh_harden import SSHEnforcer
from simple.prereq_detector import PrerequisiteDetector

import questionary
from simple.config import ConfigManager
from simple.engine import DockerEngine

from simple.notifier import Notifier
# from tests.suite_test import run_validation_suite

def main():
    
    print("🚀 === S.I.M.P.L.E (Self-hosted Infrastructure Made Painless with Linux & Engineering) ===\n")
    # Parse command line arguments
    validation_only = '--validate' in sys.argv or '-v' in sys.argv
    dev_mode = '--dev' in sys.argv or '-d' in sys.argv
    
    if dev_mode:
        print("🔍 Dev mode enabled")

    # Security check: Validate environment (only for non-validation mode)
    if not validation_only and os.geteuid() != 0 and not dev_mode:
        print("❌ CRITICAL: Must run as root (sudo python main.py)")
        sys.exit(1)
    
    # Step 1: System Detection [Single Responsibility]
    config = ConfigManager()
    config.detect_system()
    
    print("🔍 Checking prerequisites...")
    detector = PrerequisiteDetector()
    detector.detect_all()
    
    if not detector.print_summary():
        print("❌ Install missing prerequisites first:")
        print("  sudo apt install ufw fail2ban apparmor-utils")
        if not validation_only:
            sys.exit(1)

    if validation_only:
        # Validation-only mode
        print("\n🔍 VALIDATION MODE - Checking existing configuration...")
        config_path = Path("docker/docker-compose.yaml")
        if not config_path.exists():
            print(f"❌ Configuration not found at {config_path}")
            sys.exit(1)
        
        # Load context from existing .env if available
        env_path = Path("docker/.env")
        context = config.context
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        context[key] = value
        
        # results = run_validation_suite(context)
        # print(f"\n📊 Validation Results:")
        # print(f"   Total: {results['total']}")
        # print(f"   Passed: {results['passed']}")
        # print(f"   Failures: {results['failures']}")
        # print(f"   Errors: {results['errors']}")
        
        # if results['passed'] == results['total']:
        #     print("\n✅ All validations passed!")
        #     sys.exit(0)
        # else:
        #     print("\n❌ Some validations failed")
        #     sys.exit(1)

    # Step 2: Interactive Wizard
    # Check if this is a regeneration (existing compose file)
    docker_dir = context.get('BASE_DIR', Path.cwd()) / 'docker'
    compose_path = docker_dir / 'docker-compose.yaml'
    is_regeneration = compose_path.exists()
    
    context = config.wizard(load_existing=is_regeneration)
    
    # Step 3: Service Selection
    engine = DockerEngine(context)
    
    if is_regeneration:
        print("\n🔄 Regeneration mode detected")
        if questionary.confirm("Add new services to existing setup?", default=True).ask():
            engine.select_services(allow_incremental=True)
        else:
            print("Starting fresh setup...")
            engine.select_services(allow_incremental=False)
    else:
        engine.select_services(allow_incremental=False)
    
    # Step 4: Generate Infrastructure
    engine.generate()
    
    # Step 5: Validation
    # if questionary.confirm("Run validation suite?").ask():
    #     results = run_validation_suite(context)
    #     print(f"\n✅ Validation: {results['passed']}/{results['total']} passed")
    
    # Step 6: Security Hardening (optional)
    
    # wire context and DI
    context['ssh_enforcer'] = SSHEnforcer(context)

    if questionary.confirm("Apply firewall rules?").ask():
        ufw = UfwEnforcer(context)
        rules = ufw.process()
        print("\n📋 UFW Rules Preview:")
        for rule in rules:
            print(f"   {rule}")

        if questionary.confirm("Apply these rules?").ask():
            success = ufw.apply(rules, dry_run=False)
            if not success:
                print("❌ Failed to apply UFW rules")
        else:
            print("⚠️  Skipping UFW configuration")

    # AppArmor (optional)
    apparmor = AppArmorEnforcer(context)
    if apparmor.detect():
        if questionary.confirm("Install AppArmor profiles?").ask():
            plan = apparmor.process()
            success = apparmor.apply(plan, dry_run=False)
            if not success:
                print("❌ Failed to install AppArmor profile")
    else:
        print("⚠️  AppArmor not available; skipping.")
    
    # Step 8: Notifications
    notifier = Notifier(context)
    notifier.send("Setup completed successfully!")
    
    print(f"\n🎉 SUCCESS! Infrastructure ready at: {context['BASE_DIR']}")
    print("Next steps:")
    print("  1. cd docker && docker compose up -d")
    print("  2. Monitor: docker compose logs -f")

if __name__ == "__main__":
    main()
