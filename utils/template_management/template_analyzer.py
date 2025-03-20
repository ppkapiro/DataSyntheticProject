from typing import Dict, Any, Tuple, List
from pathlib import Path
import logging

class TemplateAnalyzer:
    """Gestor mejorado de análisis de plantillas"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analysis_methods = {
            'basic_text': self._analyze_basic_text,
            'json': self._analyze_json,
            'yaml': self._analyze_yaml,
            'django': self._analyze_django,
            'excel': self._analyze_excel,
            'regex': self._analyze_regex,
            'ast': self._analyze_ast
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analiza un archivo usando todos los métodos disponibles"""
        results = []
        best_result = None
        max_quality = 0

        for method_name, method in self.analysis_methods.items():
            try:
                fields, quality = method(file_path)
                self.logger.info(f"✓ {method_name}: {len(fields)} campos (calidad: {quality}%)")
                
                results.append({
                    'method': method_name,
                    'fields': fields,
                    'quality': quality
                })

                if quality > max_quality:
                    max_quality = quality
                    best_result = results[-1]
            except Exception as e:
                self.logger.error(f"Error en {method_name}: {str(e)}")
                continue

        if not best_result:
            raise ValueError("No se pudo analizar el archivo con ningún método")

        return {
            'fields': best_result['fields'],
            'metadata': {
                'method_used': best_result['method'],
                'quality_score': best_result['quality'],
                'alternative_methods': [r['method'] for r in results if r != best_result],
                'total_fields': len(best_result['fields'])
            }
        }

    def _calculate_quality_score(self, fields: Dict[str, Any], method: str) -> float:
        """Calcula la puntuación de calidad del análisis"""
        score = 100.0
        penalties = {
            'missing_type': 10,
            'missing_description': 5,
            'invalid_type': 15,
            'incomplete_validation': 8
        }

        for field in fields.values():
            if 'type' not in field:
                score -= penalties['missing_type']
            if 'description' not in field:
                score -= penalties['missing_description']
            if not self._validate_field_structure(field):
                score -= penalties['incomplete_validation']

        return max(0, min(score, 100))

    def _validate_field_structure(self, field: Dict[str, Any]) -> bool:
        """Valida la estructura básica de un campo"""
        required_keys = {'type', 'required'}
        return all(key in field for key in required_keys)

    def _enhance_field_metadata(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Mejora la metadata de los campos con información adicional"""
        for field_name, field in fields.items():
            field['validation_rules'] = self._generate_validation_rules(field)
            field['suggestions'] = self._generate_field_suggestions(field_name, field)

        return fields

    def _generate_validation_rules(self, field: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera reglas de validación basadas en el tipo de campo"""
        rules = []
        
        if field.get('type') == 'string':
            rules.extend([
                {'type': 'length', 'min': 1, 'max': 255},
                {'type': 'pattern', 'value': self._infer_pattern(field)}
            ])
        elif field.get('type') == 'number':
            rules.extend([
                {'type': 'range', 'min': None, 'max': None},
                {'type': 'type', 'value': 'numeric'}
            ])

        return rules

    def _generate_field_suggestions(self, name: str, field: Dict[str, Any]) -> List[str]:
        """Genera sugerencias de mejora para el campo"""
        suggestions = []
        
        if not field.get('description'):
            suggestions.append(f"Añadir descripción para el campo '{name}'")
        if not field.get('validation_rules'):
            suggestions.append(f"Definir reglas de validación para '{name}'")

        return suggestions
