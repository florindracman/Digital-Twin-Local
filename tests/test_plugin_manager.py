import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from plugin_manager import load_plugins


class TestPluginManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "plugins": [
                {
                    "name": "test_plugin",
                    "module": "plugins.rpc_server_plugin",
                    "class": "RpcServerPlugin",
                    "enabled": True,
                    "config": {
                        "request_topic": "test/request",
                        "response_topic_prefix": "test/response/"
                    }
                },
                {
                    "name": "disabled_plugin",
                    "module": "plugins.trigger_listener_plugin",
                    "class": "TriggerListenerPlugin",
                    "enabled": False,
                    "config": {}
                }
            ]
        }
        self.context = {
            "broker": "test-broker",
            "read_all_vehicle_data": Mock()
        }
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('plugin_manager.importlib.import_module')
    def test_load_plugins_success(self, mock_import, mock_file):
        """Test successful plugin loading."""
        # Mock file read
        mock_file.return_value.read.return_value = json.dumps(self.test_config)
        
        # Mock plugin class
        mock_plugin_instance = Mock()
        mock_plugin_class = Mock(return_value=mock_plugin_instance)
        mock_module = Mock()
        mock_module.RpcServerPlugin = mock_plugin_class
        mock_import.return_value = mock_module
        
        # Load plugins
        with patch('json.load', return_value=self.test_config):
            instances = load_plugins("test_config.json", self.context)
        
        # Assertions
        self.assertEqual(len(instances), 1)
        mock_plugin_instance.validate.assert_called_once()
        mock_plugin_instance.start.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_load_plugins_empty_config(self, mock_file):
        """Test loading with empty plugin list."""
        empty_config = {"plugins": []}
        
        with patch('json.load', return_value=empty_config):
            instances = load_plugins("empty_config.json", self.context)
        
        self.assertEqual(len(instances), 0)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('plugin_manager.importlib.import_module')
    @patch('plugin_manager.logging')
    def test_load_plugins_handles_exception(self, mock_logging, mock_import, mock_file):
        """Test plugin loading handles exceptions gracefully."""
        mock_import.side_effect = ImportError("Module not found")
        
        with patch('json.load', return_value=self.test_config):
            instances = load_plugins("test_config.json", self.context)
        
        # Should return empty list when plugin fails to load
        self.assertEqual(len(instances), 0)
        mock_logging.exception.assert_called()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('plugin_manager.importlib.import_module')
    def test_load_plugins_skips_disabled(self, mock_import, mock_file):
        """Test that disabled plugins are skipped."""
        with patch('json.load', return_value=self.test_config):
            instances = load_plugins("test_config.json", self.context)
        
        # Only one plugin is enabled
        self.assertEqual(len(instances), 1)


if __name__ == '__main__':
    unittest.main()