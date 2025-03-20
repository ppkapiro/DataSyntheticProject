from typing import Dict, Any, Optional
from pathlib import Path
import json
import yaml
from .pdf_template_connector import PDFTemplateConnector
from .logging_config import setup_logging

class TemplateExportManager:
    """Gestiona la exportación de datos mapeados a formato final"""

    def __init__(self):
        self.logger = setup_logging('template_export')
        self.connector = PDFTemplateConnector()
        self.last_export = None

    def export_mapped_data(self, 
                          mapped_data: Dict[str, Any],
                          output_format: str = 'json',
                          output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Exporta los datos mapeados al formato especificado"""
        self.logger.info(f"Iniciando exportación en formato: {output_format}")
        
        # Validar datos antes de exportar
        if not self._validate_mapped_data(mapped_data):
            return {'error': 'Datos inválidos para exportación'}

        try:
            # Preparar datos para exportación
            export_data = self._prepare_export_data(mapped_data)
            
            # Exportar según formato
            if output_path:
                self._save_to_file(export_data, output_path, output_format)
            
            self.last_export = export_data
            return export_data

        except Exception as e:
            self.logger.error(f"Error en exportación: {str(e)}")
            return {'error': str(e)}

    def _prepare_export_data(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara los datos para exportación"""
        return {
            'template_info': {
                'name': mapped_data.get('nombre_archivo'),
                'type': mapped_data.get('tipo_documento')
            },
            'fields': mapped_data.get('campos', {}),
            'metadata': {
                'export_date': self._get_timestamp(),
                'validation_status': self._get_validation_status(mapped_data),
                'confidence_scores': self._get_confidence_scores(mapped_data)
            }
        }

    def _save_to_file(self, data: Dict[str, Any], path: Path, format: str):
        """Guarda los datos en un archivo"""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format == 'yaml':
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
        else:
            raise ValueError(f"Formato no soportado: {format}")
