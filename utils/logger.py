import logging
import os

def get_logger(name: str = 'ytmusicapi'):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def get_debug_mode():
    return os.getenv('DEBUG_MODE', 'false').lower() in ('1', 'true', 'yes') 