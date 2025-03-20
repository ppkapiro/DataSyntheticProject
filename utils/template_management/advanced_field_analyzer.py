from typing import Dict, Any, List, Optional
import re
from .logging_config import setup_logging

class AdvancedFieldAnalyzer:
    """Analizador avanzado de campos para mejor precisión"""

    def __init__(self):
        self.logger = setup_logging('advanced_analyzer')
        self.patterns = {
            'email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
            'phone': r'^\+?[\d\s-]{8,}$',
            'date': r'^\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}$',
            'address': r'.*(?:calle|avenida|plaza|carrera).*',
            'medical_code': r'^[A-Z]\d{2,3}(?:\.\d{1,2})?$'
        }
        self.type_validators = {
            'string': str,
            'integer': int,
            'float': float,
            'boolean': bool
        }

    def analyze_field(self, field_name: str, value: Any) -> Dict[str, Any]:
        """Analiza un campo y determina sus características"""
        try:
            field_type = self._detect_type(value)
            patterns = self._detect_patterns(str(value))
            confidence = self._calculate_confidence(field_name, value, patterns)

            return {
                'name': field_name,
                'detected_type': field_type,
                'patterns': patterns,
                'confidence': confidence,
                'suggestions': self._generate_suggestions(field_name, value, patterns)
            }
        except Exception as e:
            self.logger.error(f"Error analizando campo {field_name}: {str(e)}")
            return {'error': str(e)}

    def _detect_type(self, value: Any) -> str:
        """Detecta el tipo de dato del valor"""
        if isinstance(value, bool):
            return 'boolean'
        try:
            int(value)
            return 'integer'
        except:
            try:
                float(value)
                return 'float'
            except:
                return 'string'

    def _detect_patterns(self, value: str) -> List[str]:
        """Detecta patrones en el valor"""
        matched_patterns = []
        for pattern_name, pattern in self.patterns.items():
            if re.match(pattern, value):
                matched_patterns.append(pattern_name)
        return matched_patterns

    def _calculate_confidence(self, field_name: str, 
                            value: Any, patterns: List[str]) -> float:
        """Calcula nivel de confianza"""
        confidence = 0.5  # Base confidence

        # Ajustar por nombre de campo
        if any(keyword in field_name.lower() for keyword in patterns):
            confidence += 0.2

        # Ajustar por patrones detectados
        if patterns:
            confidence += 0.3

        return min(confidence, 1.0)

    def _generate_suggestions(self, field_name: str, 
                            value: Any, patterns: List[str]) -> List[str]:
        """Genera sugerencias de mejora"""
        suggestions = []
        
        # Sugerir validaciones
        if patterns:
            suggestions.append(f"Agregar validación de tipo {patterns[0]}")

        # Sugerir transformaciones
        if len(str(value)) > 100:
            suggestions.append("Considerar límite de longitud")

        return suggestions

    def analyze_multiple_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza múltiples campos"""
        results = {}
        for field_name, value in fields.items():
            results[field_name] = self.analyze_field(field_name, value)
        return results

    def suggest_improvements(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Sugiere mejoras basadas en análisis"""
        suggestions = []
        
        for field_name, analysis in analysis_results.items():
            if analysis.get('confidence', 0) < 0.7:
                suggestions.append(f"Revisar campo {field_name}: baja confianza")
            if analysis.get('suggestions'):
                suggestions.extend(analysis['suggestions'])

        return suggestions
