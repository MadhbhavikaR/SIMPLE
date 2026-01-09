import unittest
import json
from pathlib import Path
from simple.config.config_reader import ConfigReader, ConfigResult

class TestConfigReader(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp())
        self.reader = ConfigReader(
            config_dir=self.temp_dir / "config",
            template_dir=self.temp_dir / "templates"
        )
        self.reader.config_dir.mkdir(parents=True)
        self.reader.template_dir.mkdir(parents=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_yaml_to_dict(self):
        # Create test config
        (self.reader.config_dir / "test.yaml").write_text("""
test: value
nested:
  key: value
""")
        
        result = self.reader.read_yaml_config("test")
        self.assertTrue(result.success)
        self.assertEqual(result.data["test"], "value")
    
    def test_yaml_to_json(self):
        (self.reader.config_dir / "test.yaml").write_text("""
test: value
nested:
  key: value
""")
        result = self.reader.read_yaml_config("test", as_json=True)
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, str)
        self.assertIn('"test": "value"', result.data)
    
    def test_template_rendering(self):
        # Create test template
        template_path = self.reader.template_dir / "test.yaml"
        template_path.write_text("Hello {{ name }}!")
        
        result = self.reader.read_template("test", {"name": "World"})
        self.assertTrue(result.success)
        self.assertIn("Hello World!", result.data)
