from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import yaml
from datetime import datetime
from .template_explorer import TemplateExplorer
from .logging_config import setup_logging

class TemplateExporter:
    """Sistema de exportación de plantillas"""

    def __init__(self):
        self.logger = setup_logging()
        self.explorer = TemplateExplorer()
        self.supported_formats = {
            'json': self._export_json,
            'yaml': self._export_yaml,
            'django': self._export_django
        }

    def export_template(self, template_data: Dict[str, Any], format: str = 'json', output_path: Path = None) -> bool:
        """Exporta una plantilla al formato especificado"""
        if format not in self.supported_formats:
            self.logger.error(f"Formato no soportado: {format}")
            return False

        try:
            exporter = self.supported_formats[format]
            output_content = exporter(template_data)
            
            if output_path:
                self._save_export(output_content, output_path)
                self.logger.info(f"Plantilla exportada a: {output_path}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error exportando plantilla: {str(e)}")
            return False

    def export_interactive(self, template_data: Dict[str, Any]) -> Optional[Path]:
        """Exportación interactiva con selección de destino"""
        # Mostrar formatos disponibles
        print("\nFormatos de exportación disponibles:")
        for idx, format in enumerate(self.supported_formats.keys(), 1):
            print(f"{idx}. {format.upper()}")

        try:
            format_choice = int(input("\nSeleccione formato (0 para cancelar): ")) - 1
            if format_choice < 0:
                return None

            selected_format = list(self.supported_formats.keys())[format_choice]
            
            # Usar explorador para seleccionar destino
            print("\nSeleccione ubicación de destino:")
            destination = self.explorer.navigate_directory()
            
            if destination and destination['type'] == 'directory':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = Path(destination['path']) / f"template_export_{timestamp}.{selected_format}"
                
                if self.export_template(template_data, selected_format, output_path):
                    return output_path

        except (ValueError, IndexError):
            self.logger.error("Selección inválida")
        except Exception as e:
            self.logger.error(f"Error en exportación interactiva: {str(e)}")
        
        return None

    def _export_json(self, data: Dict[str, Any]) -> str:
        """Exporta a formato JSON"""
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _export_yaml(self, data: Dict[str, Any]) -> str:
        """Exporta a formato YAML"""
        return yaml.dump(data, allow_unicode=True, sort_keys=False)

    def _export_django(self, data: Dict[str, Any]) -> str:
        """Exporta a modelo Django"""
        model_name = data.get('name', 'CustomModel')
        fields = []

        for field_name, field_data in data.get('fields', {}).items():
            field_def = self._generate_django_field(field_name, field_data)
            fields.append(f"    {field_def}")

        return f"""from django.db import models

class {model_name}(models.Model):
{chr(10).join(fields)}

    class Meta:
        verbose_name = '{model_name}'
        verbose_name_plural = '{model_name}s'
"""

    def _generate_django_field(self, name: str, field_data: Dict[str, Any]) -> str:
        """Genera definición de campo Django"""
        field_type = self._map_to_django_type(field_data.get('type', 'string'))
        options = []

        if not field_data.get('required', True):
            options.append('null=True')
            options.append('blank=True')

        if field_data.get('description'):
            options.append(f"help_text='{field_data['description']}'")

        return f"{name} = models.{field_type}Field({', '.join(options)})"

    def _map_to_django_type(self, field_type: str) -> str:
        """Mapea tipos de plantilla a tipos Django"""
        return {
            'string': 'Char',
            'text': 'Text',
            'number': 'Integer',
            'float': 'Float',
            'boolean': 'Boolean',
            'date': 'Date',
            'datetime': 'DateTime',
            'email': 'Email'
        }.get(field_type, 'Char')

    def _save_export(self, content: str, path: Path) -> None:
        """Guarda el contenido exportado en un archivo"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
