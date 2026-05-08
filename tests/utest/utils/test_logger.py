import time
from unittest.mock import patch

from src.utils.logger import setup_app_logger


def test_logger_flow():
    with patch("logging_loki.LokiHandler.emit") as mock_emit:
        logger = setup_app_logger()
        test_msg = "Hello Loki"
        logger.info(test_msg)
        time.sleep(0.1)
        assert mock_emit.called
        log_record = mock_emit.call_args[0][0]
        assert log_record.getMessage() == test_msg
