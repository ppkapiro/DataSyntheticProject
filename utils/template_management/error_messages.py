from typing import Dict, Any

class ValidationMessages:
    """Sistema de mensajes de error personalizados"""
    
    MESSAGES = {
        'string': {
            'type': "El valor debe ser texto",
            'min_length': "La longitud mínima es {min_length} caracteres",
            'max_length': "La longitud máxima es {max_length} caracteres",
            'pattern': "El formato no es válido",
            'required': "Este campo es obligatorio"
        },
        'number': {
            'type': "El valor debe ser un número",
            'min_value': "El valor mínimo es {min_value}",
            'max_value': "El valor máximo es {max_value}",
            'integer': "El valor debe ser un número entero"
        },
        'date': {
            'type': "La fecha no es válida",
            'format': "El formato debe ser {format}",
            'min_date': "La fecha debe ser posterior a {min_date}",
            'max_date': "La fecha debe ser anterior a {max_date}"
        },
        'email': {
            'type': "El email no es válido",
            'pattern': "El formato de email no es válido"
        }
    }

    @classmethod
    def get_message(cls, field_type: str, error_type: str, **kwargs) -> str:
        """Obtiene un mensaje de error formateado"""
        try:
            message = cls.MESSAGES[field_type][error_type]
            return message.format(**kwargs)
        except KeyError:
            return f"Error de validación: {error_type}"

    @classmethod
    def format_field_error(cls, field_name: str, error_info: Dict[str, Any]) -> str:
        """Formatea un error específico de campo"""
        base_message = cls.get_message(
            error_info.get('field_type', 'string'),
            error_info.get('error_type', 'type'),
            **error_info.get('params', {})
        )
        return f"Campo '{field_name}': {base_message}"
