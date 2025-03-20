from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
from .logging_config import setup_logging
from .pattern_detector import PatternDetector
from .data_transformer import DataTransformer

class ComplexFieldProcessor:
    """Procesador de campos complejos y relaciones"""

    def __init__(self):
        self.logger = setup_logging('complex_processor')
        self.pattern_detector = PatternDetector()
        self.data_transformer = DataTransformer()
        self.processing_history = {}

    def process_complex_fields(self, fields: Dict[str, Any], 
                             template_info: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa campos complejos y sus relaciones"""
        self.logger.info("Iniciando procesamiento de campos complejos")
        
        try:
            # Detectar grupos de campos relacionados
            field_groups = self._detect_field_groups(fields)
            
            # Procesar cada grupo
            processed_fields = {}
            for group_name, group_fields in field_groups.items():
                processed_group = self._process_field_group(
                    group_fields,
                    template_info.get('campos', {})
                )
                processed_fields.update(processed_group)

            # Validar coherencia
            validation_result = self._validate_processed_fields(processed_fields)

            return {
                'processed_fields': processed_fields,
                'field_groups': field_groups,
                'validation': validation_result,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'groups_detected': len(field_groups),
                    'fields_processed': len(processed_fields)
                }
            }

        except Exception as e:
            self.logger.error(f"Error en procesamiento: {str(e)}")
            return {'error': str(e)}

    def _detect_field_groups(self, fields: Dict[str, Any]) -> Dict[str, List[str]]:
        """Detecta grupos de campos relacionados"""
        groups = {
            'personal_info': [],
            'medical_data': [],
            'contact_info': [],
            'assessment': []
        }

        for field_name, field_info in fields.items():
            # Agrupar por prefijo común
            prefix = self._get_field_prefix(field_name)
            if prefix:
                group_name = self._map_prefix_to_group(prefix)
                if group_name:
                    groups[group_name].append(field_name)
                    continue

            # Agrupar por tipo de contenido
            content_group = self._detect_content_group(field_info)
            if content_group:
                groups[content_group].append(field_name)

        return {k: v for k, v in groups.items() if v}

    def _process_field_group(self, group_fields: List[str], 
                           template_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un grupo de campos relacionados"""
        processed = {}

        # Ordenar campos por dependencia
        sorted_fields = self._sort_by_dependency(group_fields, template_fields)

        for field_name in sorted_fields:
            if template_info := template_fields.get(field_name):
                processed[field_name] = self._process_single_field(
                    field_name,
                    template_info
                )

        return processed

    def _process_single_field(self, field_name: str, 
                            template_info: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un campo individual"""
        processors = {
            'date': self._process_date_field,
            'address': self._process_address_field,
            'name': self._process_name_field,
            'medical_code': self._process_medical_code
        }

        field_type = template_info.get('type', 'string')
        processor = processors.get(field_type, self._process_default_field)

        result = processor(field_name, template_info)
        self._record_processing(field_name, result)

        return result

    def _record_processing(self, field_name: str, result: Dict[str, Any]) -> None:
        """Registra el procesamiento de un campo"""
        self.processing_history[field_name] = {
            'timestamp': datetime.now().isoformat(),
            'success': bool(result),
            'errors': result.get('errors', []),
            'warnings': result.get('warnings', [])
        }

    def _get_field_prefix(self, field_name: str) -> Optional[str]:
        """Extrae el prefijo de un nombre de campo"""
        parts = field_name.split('_')
        return parts[0] if len(parts) > 1 else None

    def _map_prefix_to_group(self, prefix: str) -> Optional[str]:
        """Mapea prefijos a grupos de campos"""
        prefix_mappings = {
            'pat': 'personal_info',
            'med': 'medical_data',
            'cont': 'contact_info',
            'eval': 'assessment'
        }
        return prefix_mappings.get(prefix[:3].lower())

    def _detect_content_group(self, field_info: Dict[str, Any]) -> Optional[str]:
        """Detecta el grupo basado en el contenido del campo"""
        value = str(field_info.get('value', '')).lower()
        
        if any(w in value for w in ['@', 'phone', 'tel', 'email']):
            return 'contact_info'
        elif any(w in value for w in ['dx', 'diagnosis', 'treatment']):
            return 'medical_data'
        elif any(w in value for w in ['score', 'test', 'eval']):
            return 'assessment'
            
        return None
