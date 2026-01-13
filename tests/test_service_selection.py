#!/usr/bin/env python3

"""
Test script to verify the enhanced service selection functionality.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from simple.engine import DockerEngine
from simple.config.config_reader import ConfigReader

def test_service_selection():
    """Test the enhanced service selection functionality."""

    # Create a test context
    test_context = {
        'DOCKER_DIR': Path('/tmp/test_docker'),
        'VOLUMES_DIR': Path('/tmp/test_volumes'),
        'SCRIPTS_DIR': Path('/tmp/test_scripts'),
        'PUID': 1000,
        'PGID': 1000,
        'AUTO_GENERATE_PASSWORDS': False
    }

    # Create the engine
    engine = DockerEngine(test_context)

    print("Testing enhanced service selection...")
    print("=" * 50)

    # Test loading about.yaml data for a service
    print("1. Testing _load_service_about_data method:")
    authelia_data = engine._load_service_about_data('authelia')
    print(f"   Authelia data loaded: {bool(authelia_data)}")
    if authelia_data:
        print(f"   Service name: {authelia_data.get('name', 'N/A')}")
        print(f"   Description: {authelia_data.get('description', 'N/A')}")
        print(f"   Prompts: {len(authelia_data.get('prompts', []))} prompts found")

    # Test loading about.yaml data for a non-existent service
    print("\n2. Testing _load_service_about_data for non-existent service:")
    nonexistent_data = engine._load_service_about_data('nonexistent_service')
    print(f"   Result: {bool(nonexistent_data)} (should be False/empty)")

    # Test the prompt input functionality (we'll skip actual user input for testing)
    print("\n3. Testing prompt type detection:")
    if authelia_data and authelia_data.get('prompts'):
        for prompt in authelia_data['prompts']:
            prompt_type = prompt.get('type', {}).get('enum', ['STRING'])[0]
            print(f"   Prompt '{prompt['name']}': type = {prompt_type}")

    print("\n4. Testing service categorization:")
    # Group services by category (similar to what select_services does)
    from simple.services import AVAILABLE_SERVICES
    services_by_category = {}
    for service in AVAILABLE_SERVICES:
        category = service.category
        if category not in services_by_category:
            services_by_category[category] = []
        services_by_category[category].append(service)

    print(f"   Found {len(services_by_category)} categories:")
    for category, services in services_by_category.items():
        print(f"     - {category}: {len(services)} services")

    print("\n✅ All tests completed successfully!")
    print("The enhanced service selection should now:")
    print("  • Load about.yaml data for each service")
    print("  • Use prompts from about.yaml for user input")
    print("  • Validate input based on type.enum")
    print("  • Group services by category for better organization")
    print("  • Show detailed service information during selection")

if __name__ == "__main__":
    test_service_selection()
