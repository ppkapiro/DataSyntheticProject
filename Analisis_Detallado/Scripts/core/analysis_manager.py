from pathlib import Path
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import json
import yaml
from tabulate import tabulate
import numpy as np

class AnalysisManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_path = Path(self.config['paths']['analysis_dir'])
        self.reports_path = self.base_path / 'Reportes'
        
        # Asegurar que existan los directorios necesarios
        for dir_name in ['JSON', 'HTML', 'EXCEL']:
            (self.reports_path / dir_name).mkdir(parents=True, exist_ok=True)

    # ...existing code...

    def _save_report(self, report: Dict[str, Any], output_file: Path, format: str):
        """
        Guarda el reporte en el formato especificado
        """
        try:
            # Determinar la subcarpeta correcta según el formato
            if format == 'json':
                output_file = self.reports_path / 'JSON' / output_file.name
            elif format == 'html':
                output_file = self.reports_path / 'HTML' / output_file.with_suffix('.html').name
            elif format == 'xlsx':
                output_file = self.reports_path / 'EXCEL' / output_file.with_suffix('.xlsx').name
        except Exception as e:
            self.logger.error(f"Error al preparar la ruta del archivo: {str(e)}")
            raise
        finally:
            self.logger.debug(f"Ruta final del archivo: {output_file}")

    # ...existing code...
