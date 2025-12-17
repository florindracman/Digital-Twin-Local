import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vehicle_digital_twin"))

# Mock psycopg2 before importing db
sys.modules['psycopg2'] = MagicMock()

import db


class TestVehicleDatabase(unittest.TestCase):
    
    @patch('db.psycopg2.connect')
    def test_init_db(self, mock_connect):
        """Test database initialization."""
        mock_conn = Mock()
        mock_cur = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_connect.return_value = mock_conn
        
        db.init_db()
        
        mock_connect.assert_called_once_with(
            host="db",
            dbname="vehicles",
            user="user",
            password="pass"
        )
        mock_cur.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('db.psycopg2.connect')
    def test_write_vehicle_data(self, mock_connect):
        """Test writing vehicle data."""
        mock_conn = Mock()
        mock_cur = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_connect.return_value = mock_conn
        
        db.write_vehicle_data("VIN123", 45.5, -73.6, 90.0)
        
        mock_cur.execute.assert_called_once()
        args = mock_cur.execute.call_args[0]
        self.assertIn("INSERT INTO vehicle_data", args[0])
        self.assertEqual(args[1], ("VIN123", 45.5, -73.6, 90.0))
        mock_conn.commit.assert_called_once()
    
    @patch('db.psycopg2.connect')
    def test_read_all_vehicle_data(self, mock_connect):
        """Test reading all vehicle data."""
        mock_conn = Mock()
        mock_cur = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_connect.return_value = mock_conn
        
        expected_data = [
            ("VIN123", 45.5, -73.6, 90.0),
            ("VIN456", 46.5, -74.6, 180.0)
        ]
        mock_cur.fetchall.return_value = expected_data
        
        result = db.read_all_vehicle_data()
        
        mock_cur.execute.assert_called_once()
        self.assertEqual(result, expected_data)
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('db.psycopg2.connect')
    def test_read_last_vehicle_data(self, mock_connect):
        """Test reading last vehicle data."""
        mock_conn = Mock()
        mock_cur = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_connect.return_value = mock_conn
        
        expected_data = ("VIN123", 45.5, -73.6, 90.0)
        mock_cur.fetchone.return_value = expected_data
        
        result = db.read_last_vehicle_data()
        
        mock_cur.execute.assert_called_once()
        args = mock_cur.execute.call_args[0][0]
        self.assertIn("ORDER BY id DESC", args)
        self.assertIn("LIMIT 1", args)
        self.assertEqual(result, expected_data)


if __name__ == '__main__':
    unittest.main()