from typing import Dict, Any, List
from pathlib import Path
import re
from .logging_config import setup_logging

class PDFFieldAnalyzer:
    """Analizador básico de campos en PDFs"""

    def __init__(self):
        self.logger = setup_logging('pdf_analyzer')
        self.detected_fields = {}
        self.field_patterns = {
            'name': r'(?:nombre|name)[:]\s*([^\n]+)',
            'date': r'(?:fecha|date)[:]\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            'id': r'(?:id|número|code)[:]\s*([^\n]+)',
            'email': r'(?:email|correo)[:]\s*([^\s@]+@[^\s@]+\.[^\s@]+)'
        }

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analiza el contenido extraído del PDF"""
        self.logger.info("Iniciando análisis de contenido PDF")
        
        detected_fields = {}
        field_positions = {}

        # Detectar campos por patrones conocidos
        for field_type, pattern in self.field_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                field_value = match.group(1).strip()
                position = match.start()
                confidence = self._calculate_confidence(field_value, field_type)
                
                detected_fields[field_type] = {
                    'value': field_value,
                    'position': position,
                    'confidence': confidence,
                    'type': self._infer_type(field_value)
                }
                field_positions[position] = field_type

        return {
            'fields': detected_fields,
            'metadata': {
                'total_fields': len(detected_fields),
                'field_positions': field_positions,
                'analysis_quality': self._calculate_quality(detected_fields)
            }
        }

    def _infer_type(self, value: str) -> str:
        """Infiere el tipo de dato de un valor"""
        if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', value):
            return 'date'
        elif re.match(r'^\d+$', value):
            return 'number'
        elif re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
            return 'email'
        return 'string'

    def _calculate_confidence(self, value: str, field_type: str) -> float:
        """Calcula la confianza de la detección"""
        if not value:
            return 0.0

        confidence = 0.7  # Base confidence
        
        # Ajustar según tipo y valor
        type_validations = {
            'date': lambda v: bool(re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', v)),
            'email': lambda v: bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v)),
            'name': lambda v: len(v.split()) > 1,  # Nombres completos
            'id': lambda v: bool(re.match(r'^[A-Z0-9-]+$', v))  # IDs típicos
        }

        if field_type in type_validations:
            confidence += 0.2 if type_validations[field_type](value) else -0.2

        return round(min(max(confidence, 0.0), 1.0), 2)

    def _calculate_quality(self, fields: Dict[str, Any]) -> float:
        """Calcula la calidad general del análisis"""
        if not fields:
            return 0.0
            
        confidences = [field['confidence'] for field in fields.values()]
        return round(sum(confidences) / len(confidences), 2)

