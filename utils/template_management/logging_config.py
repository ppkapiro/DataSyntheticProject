import logging
from pathlib import Path
import os
from datetime import datetime

def setup_logging():
    """Configura el sistema de logging básico"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Crear archivo de log con fecha
    log_file = log_dir / f"template_analysis_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configurar formato detallado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para archivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Configurar logger
    logger = logging.getLogger('template_analyzer')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
