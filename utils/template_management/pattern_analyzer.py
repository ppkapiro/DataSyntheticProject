from typing import Dict, Any, List, Optional
import re
from collections import Counter
from .logging_config import setup_logging

class PatternAnalyzer:
    """Sistema de análisis y detección de patrones"""

    def __init__(self):
        self.logger = setup_logging('pattern_analyzer')
        self.patterns = {
            'email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
            'phone': r'^\+?[\d\s-]{8,}$',
            'date': r'\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}',
            'postal_code': r'^\d{5}(?:[-\s]\d{4})?$',
            'currency': r'^\$?\d+(?:\.\d{2})?$',
            'medical_code': r'^[A-Z]\d{2}(?:\.\d{1,2})?$'
        }
        self.pattern_history = []

    def analyze_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza contenido para detectar patrones"""
        try:
            detected_patterns = {}
            for field_name, value in content.items():
                patterns = self._detect_field_patterns(str(value))
                if patterns:
                    detected_patterns[field_name] = {
                        'patterns': patterns,
                        'confidence': self._calculate_pattern_confidence(patterns),
                        'suggested_type': self._suggest_field_type(patterns)
                    }

            self._update_pattern_history(detected_patterns)
            return {
                'patterns': detected_patterns,
                'field_count': len(content),
                'pattern_count': len(detected_patterns)
            }
        except Exception as e:
            self.logger.error(f"Error en análisis: {str(e)}")
            return {'error': str(e)}

    def _detect_field_patterns(self, value: str) -> List[str]:
        """Detecta patrones en un valor"""
        matched_patterns = []
        for pattern_name, pattern in self.patterns.items():
            if re.match(pattern, value):
                matched_patterns.append(pattern_name)
        return matched_patterns

    def _calculate_pattern_confidence(self, patterns: List[str]) -> float:
        """Calcula confianza de los patrones detectados"""
        if not patterns:
            return 0.0
        # Más patrones = más confianza
        return min(1.0, len(patterns) * 0.3 + 0.4)

    def _suggest_field_type(self, patterns: List[str]) -> str:
        """Sugiere tipo de campo basado en patrones"""
        type_mapping = {
            'email': 'email',
            'phone': 'phone',
            'date': 'date',
            'currency': 'decimal',
            'medical_code': 'code'
        }
        for pattern in patterns:
            if suggested := type_mapping.get(pattern):
                return suggested
        return 'string'

    def _update_pattern_history(self, patterns: Dict[str, Any]) -> None:
        """Actualiza historial de patrones"""
        self.pattern_history.append(patterns)
        if len(self.pattern_history) > 1000:
            self.pattern_history = self.pattern_history[-1000:]
