from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from .logging_config import setup_logging
from .field_relationship_manager import FieldRelationshipManager
from .data_transformer import DataTransformer

class ContentValidator:
    """Sistema de validación de contenido contra plantillas"""

    def __init__(self):
        self.logger = setup_logging('content_validator')
        self.relationship_manager = FieldRelationshipManager()
        self.transformer = DataTransformer()
        self.validation_history = []

    def validate_content(self, content: Dict[str, Any], 
                        template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida el contenido extraído contra una plantilla"""
        self.logger.info("Iniciando validación de contenido")
        
        validation_result = {
            'is_valid': True,
            'fields': self._validate_fields(content, template),
            'relationships': self._validate_relationships(content, template),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'template_name': template.get('nombre_archivo'),
                'content_id': content.get('id', 'unknown')
            }
        }

        # Verificar validez general
        if any(not f['is_valid'] for f in validation_result['fields'].values()):
            validation_result['is_valid'] = False

        # Registrar resultado
        self._register_validation(validation_result)
        
        return validation_result

    def _validate_fields(self, content: Dict[str, Any], 
                        template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida campos individuales"""
        validated_fields = {}
        template_fields = template.get('campos', {})
        content_fields = content.get('fields', {})

        for field_name, field_info in template_fields.items():
            field_validation = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'value': None,
                'confidence': 0.0
            }

            # Validar campo requerido
            if field_info.get('required', False):
                if field_name not in content_fields:
                    field_validation['is_valid'] = False
                    field_validation['errors'].append("Campo requerido no encontrado")
                    validated_fields[field_name] = field_validation
                    continue

            # Validar tipo y valor
            if field_value := content_fields.get(field_name):
                transformed_value, confidence = self.transformer.transform_field(
                    field_value.get('value'),
                    field_value.get('type', 'string'),
                    field_info.get('type', 'string')
                )
                
                field_validation.update({
                    'value': transformed_value,
                    'confidence': confidence,
                    'transformed': transformed_value != field_value.get('value')
                })

                # Validar contra reglas específicas
                if not self._validate_field_rules(
                    transformed_value, 
                    field_info.get('validators', [])
                ):
                    field_validation['is_valid'] = False
                    field_validation['errors'].append("No cumple reglas de validación")

            validated_fields[field_name] = field_validation

        return validated_fields

    def _validate_relationships(self, content: Dict[str, Any], 
                              template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida relaciones entre campos"""
        relationships = self.relationship_manager.analyze_relationships(
            template.get('campos', {})
        )
        
        return self.relationship_manager.validate_relationships(content)

    def _validate_field_rules(self, value: Any, rules: List[Dict[str, Any]]) -> bool:
        """Valida un valor contra reglas específicas"""
        if not rules:
            return True

        for rule in rules:
            rule_type = rule.get('type')
            rule_value = rule.get('value')

            if rule_type == 'min_length' and len(str(value)) < rule_value:
                return False
            elif rule_type == 'max_length' and len(str(value)) > rule_value:
                return False
            elif rule_type == 'pattern' and not self._validate_pattern(value, rule_value):
                return False
            elif rule_type == 'range':
                if not self._validate_range(value, rule.get('min'), rule.get('max')):
                    return False

        return True

    def _validate_pattern(self, value: str, pattern: str) -> bool:
        """Valida un valor contra un patrón regex"""
        try:
            return bool(re.match(pattern, str(value)))
        except:
            return False

    def _validate_range(self, value: Any, min_val: Any, max_val: Any) -> bool:
        """Valida un valor dentro de un rango"""
        try:
            value = float(value)
            if min_val is not None and value < float(min_val):
                return False
            if max_val is not None and value > float(max_val):
                return False
            return True
        except:
            return False

    def _register_validation(self, result: Dict[str, Any]) -> None:
        """Registra un resultado de validación"""
        self.validation_history.append({
            'timestamp': result['metadata']['timestamp'],
            'template': result['metadata']['template_name'],
            'is_valid': result['is_valid'],
            'field_count': len(result['fields']),
            'error_count': sum(
                len(f['errors']) for f in result['fields'].values()
            )
        })
