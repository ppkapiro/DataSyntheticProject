from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import yaml
from datetime import datetime
from .logging_config import setup_logging
from .pdf_template_connector import PDFTemplateConnector

class DataExporter:
    """Sistema de exportación de datos mapeados"""

    def __init__(self):
        self.logger = setup_logging('data_exporter')
        self.supported_formats = ['json', 'yaml', 'notify']
        self.template_connector = PDFTemplateConnector()
        self.export_history = []

    def export_mapped_data(self, 
                         mapped_data: Dict[str, Any],
                         output_format: str = 'json',
                         output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Exporta datos mapeados al formato especificado"""
        self.logger.info(f"Iniciando exportación en formato: {output_format}")

        # Validar formato solicitado
        if output_format not in self.supported_formats:
            raise ValueError(f"Formato no soportado: {output_format}")

        try:
            # Preparar datos para exportación
            export_data = self._prepare_export_data(mapped_data)

            # Exportar según formato
            if output_path:
                success = self._save_to_format(export_data, output_path, output_format)
                if not success:
                    raise Exception("Error al guardar archivo")

            # Registrar exportación
            self._register_export(mapped_data, output_format)

            return export_data

        except Exception as e:
            self.logger.error(f"Error en exportación: {str(e)}")
            raise

    def _prepare_export_data(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara los datos para exportación"""
        return {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'format_version': '1.0'
            },
            'template_info': mapped_data.get('template_info', {}),
            'data': {
                'fields': mapped_data.get('fields', {}),
                'metadata': mapped_data.get('metadata', {})
            },
            'validation': {
                'status': 'valid' if self._validate_export(mapped_data) else 'invalid',
                'errors': self._get_validation_errors(mapped_data)
            }
        }

    def _save_to_format(self, data: Dict[str, Any], path: Path, format: str) -> bool:
        """Guarda los datos en el formato especificado"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'yaml':
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True)
            elif format == 'notify':
                self._export_notify_format(data, path)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando archivo: {str(e)}")
            return False

    def _export_notify_format(self, data: Dict[str, Any], path: Path) -> None:
        """Exporta en formato específico para Notify"""
        notify_data = {
            'template_version': '1.0',
            'export_date': datetime.now().isoformat(),
            'fields': {
                name: {
                    'value': field.get('value'),
                    'type': field.get('type', 'string'),
                    'validated': field.get('validated', False)
                }
                for name, field in data['data']['fields'].items()
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(notify_data, f, indent=2, ensure_ascii=False)

    def _register_export(self, data: Dict[str, Any], format: str) -> None:
        """Registra una exportación realizada"""
        self.export_history.append({
            'timestamp': datetime.now().isoformat(),
            'format': format,
            'fields_count': len(data.get('fields', {})),
            'template': data.get('template_info', {}).get('name')
        })

    def _validate_export(self, data: Dict[str, Any]) -> bool:
        """Valida los datos antes de exportar"""
        required_keys = ['fields', 'template_info']
        return all(key in data for key in required_keys)

    def _get_validation_errors(self, data: Dict[str, Any]) -> List[str]:
        """Obtiene errores de validación"""
        errors = []
        
        if not data.get('fields'):
            errors.append("No hay campos para exportar")
            
        if not data.get('template_info'):
            errors.append("Falta información de la plantilla")
            
        return errors
