import unittest
from unittest.mock import Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from listener_base import MqttListenerPlugin


class TestMqttListenerPlugin(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {"test_key": "test_value"}
        self.context = {"broker": "test-broker"}
        self.plugin = MqttListenerPlugin("test_plugin", self.config, self.context)
    
    def test_init(self):
        """Test plugin initialization."""
        self.assertEqual(self.plugin.name, "test_plugin")
        self.assertEqual(self.plugin.config, self.config)
        self.assertEqual(self.plugin.context, self.context)
    
    def test_validate_default(self):
        """Test default validate does nothing."""
        # Should not raise any exception
        try:
            self.plugin.validate()
        except Exception as e:
            self.fail(f"validate() raised {e} unexpectedly")
    
    def test_start_not_implemented(self):
        """Test that start must be implemented by subclass."""
        with self.assertRaises(NotImplementedError):
            self.plugin.start()
    
    def test_stop_default(self):
        """Test default stop does nothing."""
        try:
            self.plugin.stop()
        except Exception as e:
            self.fail(f"stop() raised {e} unexpectedly")


class ConcretePlugin(MqttListenerPlugin):
    """Concrete implementation for testing."""
    
    def start(self):
        self.started = True


class TestConcretePlugin(unittest.TestCase):
    
    def test_concrete_implementation(self):
        """Test that concrete implementation works."""
        plugin = ConcretePlugin("concrete", {}, {})
        plugin.start()
        self.assertTrue(plugin.started)


if __name__ == '__main__':
    unittest.main()