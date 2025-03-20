from typing import Dict, Any

class FieldTypes:
    """Define tipos de campos y sus validaciones predeterminadas"""
    
    TYPES = {
        'string': {
            'python_type': str,
            'default_validations': {
                'min_length': 1,
                'max_length': 255,
                'pattern': None
            }
        },
        'number': {
            'python_type': (int, float),
            'default_validations': {
                'min_value': None,
                'max_value': None,
                'is_integer': False
            }
        },
        'date': {
            'python_type': str,
            'default_validations': {
                'format': '%Y-%m-%d',
                'min_date': None,
                'max_date': None
            }
        },
        'boolean': {
            'python_type': bool,
            'default_validations': {
                'true_values': ['true', '1', 'yes', 'si'],
                'false_values': ['false', '0', 'no']
            }
        },
        'email': {
            'python_type': str,
            'default_validations': {
                'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'
            }
        }
    }

    @classmethod
    def get_type_config(cls, field_type: str) -> Dict[str, Any]:
        """Obtiene la configuración para un tipo de campo"""
        return cls.TYPES.get(field_type, cls.TYPES['string'])

    @classmethod
    def validate_value(cls, value: Any, field_type: str) -> bool:
        """Valida un valor según su tipo definido"""
        config = cls.get_type_config(field_type)
        try:
            if isinstance(config['python_type'], tuple):
                return isinstance(value, config['python_type'])
            return isinstance(value, config['python_type'])
        except:
            return False
