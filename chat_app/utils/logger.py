import logging
import os
from datetime import datetime

# Configurar el logger
def setup_logger():
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Crear nombre de archivo con fecha
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Configurar el logger
    logger = logging.getLogger('ChatApp')
    logger.setLevel(logging.DEBUG)
    
    # Crear manejador de archivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Crear manejador de consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Crear formato
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar manejadores al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Crear instancia global del logger
logger = setup_logger()