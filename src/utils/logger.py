import logging
import queue
from logging.handlers import QueueListener, QueueHandler

import logging_loki

from src.config.settings import settings


def setup_app_logger():
    logger_settings = settings.logger
    loki_handler = logging_loki.LokiHandler(
        url=logger_settings.LOKI_URL,
        tags={"app": logger_settings.APP_NAME, "env": logger_settings.ENV},
        version="1",
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)
    logger = logging.getLogger("app")
    logger.setLevel(logger_settings.LEVEL)
    logger.addHandler(queue_handler)
    listener = QueueListener(log_queue, loki_handler, console_handler, respect_handler_level=True)
    listener.start()
    return logger


app_logger = setup_app_logger()