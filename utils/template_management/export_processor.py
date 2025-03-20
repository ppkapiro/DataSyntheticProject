from pathlib import Path
from typing import Dict, Any, Optional
import json
import yaml
from datetime import datetime
from .pdf_template_connector import PDFTemplateConnector
from .logging_config import setup_logging

class ExportProcessor:
    """Procesa y exporta datos mapeados según la plantilla"""

    def __init__(self):
        self.logger = setup_logging('export_processor')
        self.connector = PDFTemplateConnector()
        self.last_export = None

    def process_export(self, 
                      pdf_data: Dict[str, Any], 
                      template: Dict[str, Any],
                      output_path: Optional[Path] = None,
                      format: str = 'json') -> Dict[str, Any]:
        """
        Procesa datos del PDF y genera archivo de exportación
        según la plantilla proporcionada
        """
        self.logger.info(f"Iniciando procesamiento de exportación en formato {format}")

        # Conectar datos con plantilla
        mapped_data = self.connector.connect_data(pdf_data, template)
        
        # Generar estructura de exportación
        export_data = self._prepare_export_data(mapped_data, template)
        
        # Guardar si se especifica ruta
        if output_path:
            self._save_export(export_data, output_path, format)
            
        self.last_export = export_data
        return export_data

    def _prepare_export_data(self, mapped_data: Dict[str, Any], 
                           template: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara los datos para exportación"""
        return {
            'template_info': {
                'name': template.get('nombre_archivo'),
                'type': template.get('tipo_documento'),
                'version': template.get('version', '1.0.0')
            },
            'data': {
                'fields': mapped_data.get('campos', {}),
                'metadata': mapped_data.get('metadata', {}),
                'validation': self._get_validation_info(mapped_data)
            },
            'export_info': {
                'date': datetime.now().isoformat(),
                'format_version': '1.0',
                'status': 'complete'
            }
        }

    def _save_export(self, data: Dict[str, Any], path: Path, format: str) -> None:
        """Guarda los datos exportados en el formato especificado"""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format == 'yaml':
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
        else:
            raise ValueError(f"Formato no soportado: {format}")

    def _get_validation_info(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene información de validación"""
        campos = mapped_data.get('campos', {})
        total = len(campos)
        validos = sum(1 for c in campos.values() if c.get('validated', False))
        
        return {
            'total_fields': total,
            'valid_fields': validos,
            'invalid_fields': total - validos,
            'confidence_avg': self._calculate_confidence(campos)
        }

    def _calculate_confidence(self, campos: Dict[str, Any]) -> float:
        """Calcula promedio de confianza"""
        if not campos:
            return 0.0
        confidences = [c.get('confidence', 0) for c in campos.values()]
        return round(sum(confidences) / len(confidences), 2)
