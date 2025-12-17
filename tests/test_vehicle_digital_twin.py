import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import json

# Vehicle Digital Twin tests
# Mock all external dependencies before importing
sys.modules['paho'] = MagicMock()
sys.modules['paho.mqtt'] = MagicMock()
sys.modules['paho.mqtt.client'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vehicle_digital_twin"))


class TestVehicleDigitalTwin(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_vin = "VIN123456"
        self.test_location = {"latitude": 45.5, "longitude": -73.6}
        self.test_giro = {"giro": 90.0}
    
    def test_ensure_buffer(self):
        """Test buffer initialization for a VIN."""
        from vehicle_digital_twin import ensure_buffer, buffer
        
        buffer.clear()
        ensure_buffer(self.test_vin)
        
        self.assertIn(self.test_vin, buffer)
        self.assertIsNone(buffer[self.test_vin]["vin"])
        self.assertIsNone(buffer[self.test_vin]["location"])
        self.assertIsNone(buffer[self.test_vin]["giro"])
    
    @patch('vehicle_digital_twin.write_vehicle_data')
    def test_try_merge_complete_record(self, mock_write):
        """Test merging complete vehicle record."""
        from vehicle_digital_twin import try_merge, buffer
        
        buffer.clear()
        buffer[self.test_vin] = {
            "vin": {"vin": self.test_vin},
            "location": self.test_location,
            "giro": self.test_giro
        }
        
        try_merge(self.test_vin)
        
        mock_write.assert_called_once_with(
            self.test_vin,
            45.5,
            -73.6,
            90.0
        )
        self.assertNotIn(self.test_vin, buffer)
    
    def test_try_merge_incomplete_record(self):
        """Test merging incomplete record does nothing."""
        from vehicle_digital_twin import try_merge, buffer
        
        buffer.clear()
        buffer[self.test_vin] = {
            "vin": {"vin": self.test_vin},
            "location": None,
            "giro": self.test_giro
        }
        
        try_merge(self.test_vin)
        
        # Buffer should still contain the VIN
        self.assertIn(self.test_vin, buffer)
    
    @patch('vehicle_digital_twin.try_merge')
    @patch('vehicle_digital_twin.ensure_buffer')
    def test_on_message_vin_topic(self, mock_ensure, mock_merge):
        """Test handling VIN topic message."""
        from vehicle_digital_twin import on_message, buffer, TOPIC_VIN
        
        buffer.clear()
        
        mock_msg = Mock()
        mock_msg.topic = TOPIC_VIN
        mock_msg.payload.decode.return_value = json.dumps({"vin": self.test_vin})
        
        on_message(None, None, mock_msg)
        
        mock_ensure.assert_called_once_with(self.test_vin)
        mock_merge.assert_called_once_with(self.test_vin)
    
    @patch('vehicle_digital_twin.try_merge')
    def test_on_message_location_topic(self, mock_merge):
        """Test handling location topic message."""
        from vehicle_digital_twin import on_message, buffer, TOPIC_LOCATION
        
        buffer.clear()
        buffer[self.test_vin] = {"vin": None, "location": None, "giro": None}
        
        mock_msg = Mock()
        mock_msg.topic = TOPIC_LOCATION
        mock_msg.payload.decode.return_value = json.dumps(self.test_location)
        
        on_message(None, None, mock_msg)
        
        self.assertEqual(buffer[self.test_vin]["location"], self.test_location)
        mock_merge.assert_called_once()
    
    @patch('vehicle_digital_twin.try_merge')
    def test_on_message_giro_topic(self, mock_merge):
        """Test handling giro topic message."""
        from vehicle_digital_twin import on_message, buffer, TOPIC_GIRO
        
        buffer.clear()
        buffer[self.test_vin] = {"vin": None, "location": None, "giro": None}
        
        mock_msg = Mock()
        mock_msg.topic = TOPIC_GIRO
        mock_msg.payload.decode.return_value = json.dumps(self.test_giro)
        
        on_message(None, None, mock_msg)
        
        self.assertEqual(buffer[self.test_vin]["giro"], self.test_giro)
        mock_merge.assert_called_once()
    
    def test_cleanup_buffer_expired_entries(self):
        """Test cleanup of expired buffer entries."""
        from vehicle_digital_twin import cleanup_buffer, buffer
        from time import time
        
        buffer.clear()
        
        # Add expired entry
        old_time = time() - 100
        buffer["VIN_OLD"] = {"timestamp": old_time}
        
        # Add recent entry
        buffer["VIN_NEW"] = {"timestamp": time()}
        
        cleanup_buffer()
        
        self.assertNotIn("VIN_OLD", buffer)
        self.assertIn("VIN_NEW", buffer)


if __name__ == '__main__':
    unittest.main()