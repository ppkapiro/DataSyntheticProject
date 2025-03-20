from typing import Dict, Any, List
from datetime import datetime
from .logging_config import setup_logging
from .data_transformer import DataTransformer

class PDFTemplateValidator:
    """Sistema de validación entre PDF y plantillas"""

    def __init__(self):
        self.logger = setup_logging('pdf_validator')
        self.transformer = DataTransformer()
        self.validation_history = []

    def validate_mapping(self, mapped_data: Dict[str, Any], 
                        template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida el mapeo entre datos PDF y plantilla"""
        
        validation_result = {
            'is_valid': True,
            'fields': {},
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'template': template.get('nombre_archivo'),
                'total_fields': len(template.get('campos', {}))
            },
            'errors': [],
            'warnings': []
        }

        # Validar cada campo
        template_fields = template.get('campos', {})
        mapped_fields = mapped_data.get('fields', {})

        for field_name, field_info in template_fields.items():
            field_result = self._validate_field(
                field_name,
                field_info,
                mapped_fields.get(field_name)
            )
            
            validation_result['fields'][field_name] = field_result
            
            if not field_result['is_valid']:
                validation_result['is_valid'] = False
                validation_result['errors'].extend(field_result['errors'])

            if field_result['warnings']:
                validation_result['warnings'].extend(field_result['warnings'])

        # Registrar resultado
        self._register_validation(validation_result)
        
        return validation_result

    def _validate_field(self, field_name: str, template_info: Dict[str, Any], 
                       mapped_value: Any) -> Dict[str, Any]:
        """Valida un campo individual"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'confidence': 0.0
        }

        # Validar campo requerido
        if template_info.get('required', False) and not mapped_value:
            result['is_valid'] = False
            result['errors'].append(f"Campo requerido '{field_name}' no encontrado")
            return result

        if not mapped_value:
            result['warnings'].append(f"Campo opcional '{field_name}' no encontrado")
            return result

        # Validar tipo de dato
        if not self._validate_type(mapped_value.get('value'), template_info.get('type')):
            result['is_valid'] = False
            result['errors'].append(
                f"Tipo inválido para '{field_name}': esperado {template_info.get('type')}"
            )

        # Validar restricciones específicas
        self._validate_constraints(result, field_name, mapped_value, template_info)

        # Calcular confianza
        result['confidence'] = self._calculate_confidence(mapped_value, template_info)

        return result

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Valida el tipo de un valor"""
        try:
            transformed, confidence = self.transformer.transform_field(
                value, 
                'string',  # Asumimos que viene como string del PDF
                expected_type
            )
            return confidence > 0.5
        except:
            return False

    def _validate_constraints(self, result: Dict[str, Any], field_name: str,
                            value: Dict[str, Any], template_info: Dict[str, Any]):
        """Valida restricciones específicas del campo"""
        constraints = template_info.get('constraints', {})
        
        if 'min_length' in constraints:
            if len(str(value.get('value', ''))) < constraints['min_length']:
                result['is_valid'] = False
                result['errors'].append(
                    f"Longitud mínima no alcanzada para '{field_name}'"
                )

        if 'max_length' in constraints:
            if len(str(value.get('value', ''))) > constraints['max_length']:
                result['is_valid'] = False
                result['errors'].append(
                    f"Longitud máxima excedida para '{field_name}'"
                )

        if 'pattern' in constraints:
            if not self._validate_pattern(value.get('value'), constraints['pattern']):
                result['warnings'].append(
                    f"Patrón no coincide para '{field_name}'"
                )

    def _calculate_confidence(self, mapped_value: Dict[str, Any], 
                            template_info: Dict[str, Any]) -> float:
        """Calcula nivel de confianza para un campo"""
        confidence = mapped_value.get('confidence', 0.0)
        
        # Ajustar según tipo
        if self._validate_type(mapped_value.get('value'), template_info.get('type')):
            confidence *= 1.2
        else:
            confidence *= 0.5

        # Ajustar según validaciones
        if mapped_value.get('validated', False):
            confidence *= 1.1

        return min(1.0, confidence)

    def _register_validation(self, validation_result: Dict[str, Any]):
        """Registra resultado de validación"""
        self.validation_history.append({
            'timestamp': datetime.now().isoformat(),
            'template': validation_result['metadata']['template'],
            'is_valid': validation_result['is_valid'],
            'error_count': len(validation_result['errors']),
            'warning_count': len(validation_result['warnings'])
        })
