from loguru import logger
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter

import os
from dotenv import get_key

custom_handler = LokiLoggerHandler(
    url=os.environ.get("LOKI_URL", get_key("./.env", "LOKI_URL")),
    labels={"application": "spongiper"},
    label_keys={},
    timeout=10,
    default_formatter=LoguruFormatter()
)

class _SniperLogger:
    def __init__(self):
        self.logger: logger = logger
        self.logger.configure(handlers=[{"sink": custom_handler, "serialize": True}])
        
log: logger = _SniperLogger().logger