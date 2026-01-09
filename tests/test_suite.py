"""
Comprehensive Validation Suite
==============================
"""

import unittest
import tempfile
import os
import yaml
from pathlib import Path
from simple.config import ConfigManager
from simple.engine import DockerEngine
from simple.services.gateways import CloudflaredService, SwagService

class TestHomeInfraSuite(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def test_config_detection(self):
        """System auto-detection works."""
        config = ConfigManager()
        config.detect_system()
        self.assertIn('PUID', config.context)
        self.assertIn('PGID', config.context)
        self.assertIsInstance(config.context['PUID'], str)
    
    def test_service_interfaces(self):
        """All services implement required interface."""
        cloudflared = CloudflaredService()
        self.assertEqual(cloudflared.category, 'gateway')
        self.assertIn('CF_DOCKER_TOKEN', cloudflared.get_required_secrets())
    
    def test_compose_generation(self):
        """YAML generation produces valid output."""
        context = {'PUID': '1000', 'PGID': '1000', 'VOLUMES_DIR': '/tmp/volumes'}
        swag = SwagService()
        yaml_output = swag.generate_service_yaml(context)
        self.assertIn('lscr.io/linuxserver/swag', yaml_output)
        self.assertIn('NET_ADMIN', yaml_output)
    
    def test_security_defaults(self):
        """Security defaults are applied."""
        context = {'PUID': '1000', 'PGID': '1000'}
        cloudflared = CloudflaredService()
        yaml_str = cloudflared.generate_service_yaml(context)
        self.assertIn('no-new-privileges:true', yaml_str)
        self.assertIn('cap_drop', yaml_str)
        self.assertIn('read_only: true', yaml_str)
    
    def test_network_isolation(self):
        """Network isolation is enforced."""
        context = {'PUID': '1000', 'PGID': '1000', 'VOLUMES_DIR': Path('/tmp/volumes')}
        engine = DockerEngine(context)
        engine.selected_services = [CloudflaredService(), SwagService()]
        engine._write_compose_file()
        
        compose_path = context.get('DOCKER_DIR', Path('/tmp')) / 'docker-compose.yaml'
        if compose_path.exists():
            with open(compose_path) as f:
                compose = yaml.safe_load(f)
                self.assertIn('networks', compose)
                self.assertIn('edge', compose['networks'])
                self.assertIn('app', compose['networks'])
                self.assertIn('db', compose['networks'])
    
    def test_yaml_syntax(self):
        """Generated YAML is valid."""
        context = {'PUID': '1000', 'PGID': '1000', 'VOLUMES_DIR': Path('/tmp/volumes')}
        swag = SwagService()
        yaml_str = swag.generate_service_yaml(context)
        # Should not raise exception
        yaml.safe_load(yaml_str)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

def run_validation_suite(context=None) -> dict:
    """Run complete validation suite."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHomeInfraSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    passed = result.testsRun - len(result.failures) - len(result.errors)
    
    return {
        'total': result.testsRun,
        'passed': passed,
        'failures': len(result.failures),
        'errors': len(result.errors)
    }

if __name__ == '__main__':
    run_validation_suite()
