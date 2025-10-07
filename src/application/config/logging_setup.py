import logging
from logging.handlers import RotatingFileHandler

class LoggingSetup(logging.Logger):
    def __init__(self, is_debug: bool = False):
        level = logging.DEBUG if is_debug else logging.INFO
        
        log_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(module)s Line: %(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Configure file handler
        log_handler = RotatingFileHandler(
            "logs/bot.log", 
            maxBytes=5*1024*1024, # 5 MB
            backupCount=2,
            encoding='utf-8'
        )
        log_handler.setFormatter(log_formatter)

        # Configure stream handler (console)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)

        # Get root logger and add handlers
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(log_handler)
        root_logger.addHandler(stream_handler)

        super().__init__(__name__, level)