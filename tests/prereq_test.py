"""
Prerequisite Detector Tests
===========================
"""

import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
from pathlib import Path
from simple.prereq_detector import PrerequisiteDetector, PrereqConfig

class TestPrerequisiteDetector(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.detector = PrerequisiteDetector(self.temp_dir / "prerequisites.yaml")
    
    def test_detect_ufw_installed(self):
        """Detect UFW when binary exists."""
        with patch('shutil.which', return_value='/usr/sbin/ufw'):
            result = self.detector._detect_single("ufw", 
                {"binaries": ["/usr/sbin/ufw"], "config": [], "service": []})
            self.assertTrue(result.installed)
            self.assertEqual(result.binary_path, '/usr/sbin/ufw')
    
    def test_config_saving(self):
        """Config saves correctly."""
        self.detector.detected = {
            "ufw": PrereqConfig("UFW", True, "/usr/sbin/ufw", None, None)
        }
        config_path = self.detector.save_config()
        self.assertTrue(config_path.exists())
    
    def test_os_detection(self):
        """OS detection works."""
        with patch('platform.platform', return_value='Linux-5.15.0-rpi5-arm64'):
            with patch('builtins.open', mock_open(read_data='ID=raspbian\n')):
                detector = PrerequisiteDetector()
                sys_info = detector._detect_system()
                self.assertEqual(sys_info['distro'], 'raspbian')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
