import logging
import sys
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler

# Directorio de logs
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "civilprotect.json")

def setup_logging():
    """Configura el logger estructurado en JSON con rotación de archivos"""
    logger = logging.getLogger("civilprotect")
    logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger

    # Formato JSON
    # Se pueden incluir campos custom como 'user_id', 'request_id' dinámicamente
    format_str = '%(asctime)s %(levelname)s %(name)s %(message)s'
    formatter = jsonlogger.JsonFormatter(format_str)

    # File Handler (500MB max per file, 10 files kept)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=500 * 1024 * 1024, # 500 MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler (Stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Instancia global del logger
logger = setup_logging()
