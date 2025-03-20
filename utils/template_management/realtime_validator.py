from typing import Dict, Any, List, Callable
from .validators import FieldValidator
from .error_messages import ValidationMessages

class RealtimeValidator:
    """Sistema de validación en tiempo real"""

    def __init__(self):
        self.validator = FieldValidator()
        self.validation_cache = {}
        self.validation_callbacks = {}

    def validate(self, field_name: str, value: Any, field_config: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza validación en tiempo real de un campo"""
        # Usar caché si el valor no ha cambiado
        cache_key = f"{field_name}:{str(value)}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]

        # Realizar validación
        is_valid = self.validator.validate_field(value, field_config)
        result = {
            'is_valid': is_valid,
            'errors': self.validator.get_errors(),
            'warnings': [],
            'timestamp': self._get_timestamp()
        }

        # Almacenar en caché
        self.validation_cache[cache_key] = result

        # Ejecutar callbacks de validación
        self._execute_callbacks(field_name, result)

        return result

    def register_callback(self, field_name: str, callback: Callable) -> None:
        """Registra una función callback para un campo específico"""
        if field_name not in self.validation_callbacks:
            self.validation_callbacks[field_name] = []
        self.validation_callbacks[field_name].append(callback)

    def clear_cache(self, field_name: str = None) -> None:
        """Limpia la caché de validación"""
        if field_name:
            keys_to_remove = [k for k in self.validation_cache if k.startswith(f"{field_name}:")]
            for key in keys_to_remove:
                self.validation_cache.pop(key)
        else:
            self.validation_cache.clear()

    def _execute_callbacks(self, field_name: str, validation_result: Dict[str, Any]) -> None:
        """Ejecuta los callbacks registrados para un campo"""
        callbacks = self.validation_callbacks.get(field_name, [])
        for callback in callbacks:
            try:
                callback(validation_result)
            except Exception as e:
                print(f"Error en callback de validación: {str(e)}")

    def _get_timestamp(self) -> float:
        """Obtiene el timestamp actual"""
        from time import time
        return time()
