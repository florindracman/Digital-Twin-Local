import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Mock dependencies
sys.modules['paho'] = MagicMock()
sys.modules['paho.mqtt'] = MagicMock()
sys.modules['paho.mqtt.client'] = MagicMock()

from plugins.rpc_server_plugin import RpcServerPlugin


class TestRpcServerPlugin(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "request_topic": "rpc/request/test",
            "response_topic_prefix": "rpc/response/"
        }
        self.context = {
            "broker": "test-broker",
            "read_all_vehicle_data": Mock(return_value=[
                ("VIN123", 45.5, -73.6, 90.0)
            ])
        }
        self.plugin = RpcServerPlugin("rpc_test", self.config, self.context)
    
    def test_init(self):
        """Test plugin initialization."""
        self.assertEqual(self.plugin.name, "rpc_test")
        self.assertEqual(self.plugin.config, self.config)
        self.assertEqual(self.plugin.context, self.context)
    
    def test_validate_success(self):
        """Test validation with correct config."""
        try:
            self.plugin.validate()
        except Exception as e:
            self.fail(f"validate() raised {e} unexpectedly")
    
    def test_validate_missing_request_topic(self):
        """Test validation fails without request_topic."""
        plugin = RpcServerPlugin("test", {}, self.context)
        with self.assertRaises(ValueError) as cm:
            plugin.validate()
        self.assertIn("request_topic", str(cm.exception))
    
    def test_validate_missing_response_topic_prefix(self):
        """Test validation fails without response_topic_prefix."""
        config = {"request_topic": "test"}
        plugin = RpcServerPlugin("test", config, self.context)
        with self.assertRaises(ValueError) as cm:
            plugin.validate()
        self.assertIn("response_topic_prefix", str(cm.exception))
    
    @patch('plugins.rpc_server_plugin.threading.Thread')
    @patch('plugins.rpc_server_plugin.mqtt.Client')
    def test_start(self, mock_mqtt_client, mock_thread):
        """Test plugin start."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        self.plugin.start()
        
        mock_mqtt_client.assert_called_once()
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
    
    def test_validate_without_read_function(self):
        """Test validation warning when read function not available."""
        context = {"broker": "test-broker", "read_all_vehicle_data": None}
        plugin = RpcServerPlugin("test", self.config, context)
        
        # Should not raise, but should log warning
        with patch('plugins.rpc_server_plugin.logging') as mock_logging:
            plugin.validate()
            mock_logging.warning.assert_called()


if __name__ == '__main__':
    unittest.main()