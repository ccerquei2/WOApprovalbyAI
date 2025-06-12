import os
import unittest
from unittest.mock import MagicMock, patch
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.modules.setdefault('pyodbc', MagicMock())
sys.modules.setdefault('decrypt', MagicMock())
sys.modules.setdefault('load_environment', MagicMock())
from aiwo_logger import DBLogger


class TestDBLogger(unittest.TestCase):
    @patch('decrypt.decrypt_keys', return_value='secret')
    @patch('load_environment.ConfigLoader')
    @patch('pyodbc.connect')
    def test_log_inserts_row(self, mock_connect, mock_cfg_loader, mock_decrypt):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        cfg = MagicMock()
        cfg.get_database_config.return_value = {
            'server': 'srv',
            'database': 'db'
        }
        mock_cfg_loader.return_value = cfg

        logger = DBLogger()

        logger.log(level="INFO", step="TestStep", execution_id="1234", message="msg")

        mock_cursor.execute.assert_called_once()
        sql = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]
        assert sql.strip().startswith("INSERT INTO dbo.AIWOApproval")
        assert params[0] == "INFO"
        assert params[1] == "TestStep"
        assert params[-2] == "msg"
        mock_conn.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
