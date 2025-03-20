from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import re
from .logging_config import setup_logging
from .field_matcher import FieldMatcher

class TemplateTransformer:
    """Sistema de transformación entre PDF y plantillas"""

    def __init__(self):
        self.logger = setup_logging('template_transformer')
        self.field_matcher = FieldMatcher()
        self.transformations_applied = []

    def transform_document(self, pdf_content: Dict[str, Any], 
                         target_template: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma contenido PDF según la plantilla objetivo"""
        self.logger.info("Iniciando transformación de documento")

        # Obtener campos mapeados
        mapped_fields = self._map_fields_to_template(pdf_content, target_template)
        
        # Validar y transformar valores
        transformed_data = self._transform_values(mapped_fields, target_template)

        return {
            'transformed_data': transformed_data,
            'metadata': {
                'template_name': target_template.get('nombre_archivo'),
                'transformation_date': datetime.now().isoformat(),
                'fields_transformed': len(transformed_data),
                'transformations': self.transformations_applied
            }
        }

    def _map_fields_to_template(self, content: Dict[str, Any], 
                              template: Dict[str, Any]) -> Dict[str, Any]:
        """Mapea campos del PDF a la estructura de la plantilla"""
        mapped_fields = {}
        template_fields = template.get('campos', {})
        content_fields = content.get('fields', {})

        for template_field, template_info in template_fields.items():
            if match := self.field_matcher.find_matches(
                {template_field: template_info}, 
                content_fields
            ).get('matches', {}).get(template_field):
                mapped_fields[template_field] = {
                    'value': match['value'],
                    'source_type': match.get('type', 'string'),
                    'target_type': template_info.get('type', 'string'),
                    'confidence': match.get('confidence', 0)
                }

        return mapped_fields

    def _transform_values(self, mapped_fields: Dict[str, Any], 
                         template: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma los valores según los requisitos de la plantilla"""
        transformed = {}
        self.transformations_applied = []

        for field_name, field_info in mapped_fields.items():
            template_field = template.get('campos', {}).get(field_name, {})
            
            # Aplicar transformación
            transformed_value = self._apply_transformation(
                field_info['value'],
                field_info['source_type'],
                template_field.get('type', 'string'),
                template_field.get('format')
            )

            transformed[field_name] = {
                'value': transformed_value,
                'type': template_field.get('type', 'string'),
                'confidence': field_info['confidence'],
                'validated': self._validate_transformed_value(
                    transformed_value,
                    template_field
                )
            }

        return transformed

    def _apply_transformation(self, value: Any, source_type: str, 
                            target_type: str, target_format: Optional[str] = None) -> Any:
        """Aplica transformación específica a un valor"""
        if source_type == target_type and not target_format:
            return value

        try:
            # Registrar transformación
            self.transformations_applied.append({
                'from_type': source_type,
                'to_type': target_type,
                'format': target_format,
                'timestamp': datetime.now().isoformat()
            })

            # Aplicar transformación según tipo
            if target_type == 'date':
                return self._transform_date(value, target_format)
            elif target_type == 'number':
                return self._transform_number(value)
            elif target_type == 'boolean':
                return self._transform_boolean(value)
            else:
                return str(value)

        except Exception as e:
            self.logger.error(f"Error en transformación: {str(e)}")
            return None

    def _transform_date(self, value: str, target_format: Optional[str]) -> Optional[str]:
        """Transforma valor a formato de fecha"""
        if not value:
            return None

        # Patrones comunes de fecha
        formats = [
            ('%Y-%m-%d', r'\d{4}-\d{2}-\d{2}'),
            ('%d/%m/%Y', r'\d{2}/\d{2}/\d{4}'),
            ('%Y/%m/%d', r'\d{4}/\d{2}/\d{2}')
        ]

        for date_format, pattern in formats:
            if re.match(pattern, str(value)):
                try:
                    date_obj = datetime.strptime(value, date_format)
                    return date_obj.strftime(target_format or '%Y-%m-%d')
                except:
                    continue

        return None
