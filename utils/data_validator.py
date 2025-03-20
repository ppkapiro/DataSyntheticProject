from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import yaml

class DataValidator:
    """Validador de datos y estructuras"""
    
    def __init__(self):
        self.validation_rules = {}
        self.error_messages = []

    def load_validation_rules(self, template_path: Path) -> bool:
        """Carga reglas de validación desde una plantilla"""
        try:
            if template_path.suffix == '.json':
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
            elif template_path.suffix in ['.yaml', '.yml']:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = yaml.safe_load(f)
            else:
                self.error_messages.append(f"Formato no soportado: {template_path.suffix}")
                return False

            self.validation_rules = template.get('validation_rules', {})
            return True
        except Exception as e:
            self.error_messages.append(f"Error cargando reglas: {str(e)}")
            return False

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida datos contra las reglas cargadas"""
        if not self.validation_rules:
            self.error_messages.append("No hay reglas de validación cargadas")
            return False

        is_valid = True
        for field_name, field_rules in self.validation_rules.items():
            if not self._validate_field(data.get(field_name), field_rules):
                is_valid = False

        return is_valid

    def _validate_field(self, value: Any, rules: Dict[str, Any]) -> bool:
        """Valida un campo individual contra sus reglas"""
        if rules.get('required', False) and value is None:
            self.error_messages.append(f"Campo requerido faltante")
            return False

        field_type = rules.get('type', 'string')
        validators = {
            'string': self._validate_string,
            'number': self._validate_number,
            'date': self._validate_date,
            'boolean': self._validate_boolean,
            'email': self._validate_email
        }

        validator = validators.get(field_type)
        if not validator:
            self.error_messages.append(f"Tipo de campo no soportado: {field_type}")
            return False

        return validator(value, rules)

    def get_errors(self) -> List[str]:
        """Retorna lista de errores de validación"""
        return self.error_messages

    def clear_errors(self) -> None:
        """Limpia lista de errores"""
        self.error_messages = []
