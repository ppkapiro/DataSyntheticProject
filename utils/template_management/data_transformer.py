from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import re
from .logging_config import setup_logging

class DataTransformer:
    """Sistema de transformación y normalización de datos"""
    
    def __init__(self):
        self.logger = setup_logging('transformer')
        self.transformers = {
            'string': self._transform_string,
            'integer': self._transform_integer,
            'float': self._transform_float,
            'date': self._transform_date,
            'boolean': self._transform_boolean
        }
        self.date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{2}/\d{2}/\d{4}$',
            r'^\d{1,2}\s+\w+\s+\d{4}$'
        ]

    def transform_field(self, value: Any, from_type: str, 
                       to_type: str) -> Tuple[Any, float]:
        """Transforma un valor al tipo especificado"""
        try:
            if transformer := self.transformers.get(to_type):
                result = transformer(value)
                confidence = self._calculate_confidence(result, to_type)
                return result, confidence
            raise ValueError(f"Tipo no soportado: {to_type}")
        except Exception as e:
            self.logger.error(f"Error transformando {value}: {str(e)}")
            return None, 0.0

    def _transform_string(self, value: Any) -> str:
        """Transforma a string"""
        return str(value).strip()

    def _transform_integer(self, value: Any) -> Optional[int]:
        """Transforma a entero"""
        try:
            if isinstance(value, str):
                value = re.sub(r'[^\d-]', '', value)
            return int(value)
        except:
            return None

    def _transform_float(self, value: Any) -> Optional[float]:
        """Transforma a float"""
        try:
            if isinstance(value, str):
                value = value.replace(',', '.')
            return float(value)
        except:
            return None

    def _transform_date(self, value: Any) -> Optional[datetime]:
        """Transforma a fecha"""
        if isinstance(value, datetime):
            return value
        for pattern in self.date_patterns:
            try:
                if re.match(pattern, str(value)):
                    return datetime.strptime(value, self._get_date_format(pattern))
            except:
                continue
        return None

    def _transform_boolean(self, value: Any) -> Optional[bool]:
        """Transforma a booleano"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            true_values = ['yes', 'true', '1', 'si', 'sí']
            false_values = ['no', 'false', '0']
            value = value.lower()
            if value in true_values:
                return True
            if value in false_values:
                return False
        return None

    def _calculate_confidence(self, result: Any, expected_type: str) -> float:
        """Calcula confianza de la transformación"""
        if result is None:
            return 0.0
        if isinstance(result, (str, int, float, bool, datetime)):
            return 1.0
        return 0.5
