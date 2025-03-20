from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .error_messages import ValidationMessages

class FieldValidator:
    """Sistema de validación de campos"""

    def __init__(self):
        self.error_messages = []
        self.validation_rules = {
            'string': self._validate_string,
            'number': self._validate_number,
            'date': self._validate_date,
            'email': self._validate_email,
            'boolean': self._validate_boolean
        }

    def validate_field(self, value: Any, field_config: Dict[str, Any]) -> bool:
        """Valida un valor según la configuración del campo"""
        self.error_messages = []
        
        # Añadir validación en tiempo real
        if field_config.get('realtime', False):
            return self._validate_realtime(value, field_config)
            
        field_type = field_config.get('type', 'string')

        if field_config.get('required', False) and value is None:
            self.error_messages.append(
                ValidationMessages.get_message(field_type, 'required')
            )
            return False

        if value is None:
            return True

        validator = self.validation_rules.get(field_type)
        if not validator:
            self.error_messages.append(f"Tipo de campo no soportado: {field_type}")
            return False

        return validator(value, field_config)

    def _validate_string(self, value: str, config: Dict[str, Any]) -> bool:
        if not isinstance(value, str):
            self.error_messages.append(
                ValidationMessages.get_message('string', 'type')
            )
            return False

        min_length = config.get('min_length', 0)
        max_length = config.get('max_length', float('inf'))
        pattern = config.get('pattern')

        if len(value) < min_length:
            self.error_messages.append(
                ValidationMessages.get_message('string', 'min_length', 
                                            min_length=config['min_length'])
            )
            return False

        if len(value) > max_length:
            self.error_messages.append(f"Longitud máxima permitida: {max_length}")
            return False

        if pattern and not re.match(pattern, value):
            self.error_messages.append("El valor no cumple con el formato requerido")
            return False

        return True

    def _validate_number(self, value: Any, config: Dict[str, Any]) -> bool:
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            self.error_messages.append("El valor debe ser un número")
            return False

        min_value = config.get('min_value')
        max_value = config.get('max_value')
        is_integer = config.get('is_integer', False)

        if is_integer and not float(num_value).is_integer():
            self.error_messages.append("El valor debe ser un número entero")
            return False

        if min_value is not None and num_value < min_value:
            self.error_messages.append(f"Valor mínimo permitido: {min_value}")
            return False

        if max_value is not None and num_value > max_value:
            self.error_messages.append(f"Valor máximo permitido: {max_value}")
            return False

        return True

    def get_errors(self) -> List[str]:
        """Retorna los mensajes de error de la última validación"""
        return self.error_messages

    def get_validation_rules(self, field_type: str) -> Dict[str, Any]:
        """Retorna las reglas de validación para un tipo de campo"""
        base_rules = {
            'string': {
                'min_length': 0,
                'max_length': None,
                'pattern': None
            },
            'number': {
                'min_value': None,
                'max_value': None,
                'is_integer': False
            },
            'date': {
                'format': '%Y-%m-%d',
                'min_date': None,
                'max_date': None
            },
            'email': {
                'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'
            },
            'boolean': {
                'true_values': ['true', '1', 'yes', 'si'],
                'false_values': ['false', '0', 'no']
            }
        }
        return base_rules.get(field_type, {})

    def _validate_realtime(self, value: Any, config: Dict[str, Any]) -> bool:
        """Realiza validación optimizada para tiempo real"""
        field_type = config.get('type', 'string')
        validator = self.validation_rules.get(field_type)
        
        if not validator:
            return False
            
        try:
            return validator(value, config)
        except Exception:
            return False
