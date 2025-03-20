from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from .logging_config import setup_logging

class DataNormalizer:
    """Normalizador de datos para consistencia"""
    
    def __init__(self):
        self.logger = setup_logging('normalizer')
        self.rules = {
            'text': self._normalize_text,
            'date': self._normalize_date,
            'number': self._normalize_number,
            'code': self._normalize_code
        }
        self.date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']

    def normalize_field(self, value: Any, field_type: str) -> Any:
        """Normaliza un valor según su tipo"""
        if normalizer := self.rules.get(field_type):
            return normalizer(value)
        return value

    def normalize_document(self, data: Dict[str, Any], 
                         field_types: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza todos los campos de un documento"""
        return {
            field: self.normalize_field(value, field_types.get(field, 'text'))
            for field, value in data.items()
        }

    def _normalize_text(self, value: str) -> str:
        """Normaliza texto"""
        if not isinstance(value, str):
            return str(value)
        return ' '.join(value.strip().split())

    def _normalize_date(self, value: str) -> Optional[str]:
        """Normaliza fechas a formato ISO"""
        for fmt in self.date_formats:
            try:
                return datetime.strptime(value, fmt).isoformat()[:10]
            except:
                continue
        return None

    def _normalize_number(self, value: Any) -> Optional[float]:
        """Normaliza números"""
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(re.sub(r'[^\d.-]', '', str(value)))
        except:
            return None

    def _normalize_code(self, value: str) -> str:
        """Normaliza códigos"""
        return re.sub(r'\s+', '', str(value)).upper()
