from loguru import logger

# TODO

class _SniperLogger:
    def __init__(self):
        self.logger: logger = logger
        
log: logger = logger