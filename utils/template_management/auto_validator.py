from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from collections import Counter
from .logging_config import setup_logging
from .content_validator import ContentValidator
from .pattern_analyzer import PatternAnalyzer
from .data_transformer import DataTransformer

class AutoValidator:
    """Sistema de validación automática con aprendizaje"""

    def __init__(self):
        self.logger = setup_logging('auto_validator')
        self.content_validator = ContentValidator()
        self.pattern_analyzer = PatternAnalyzer()
        self.transformer = DataTransformer()
        self.validation_history = []
        self.learned_patterns = {}
        self.confidence_threshold = 0.8

    def auto_validate(self, data: Dict[str, Any], 
                     template: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza validación automática con mejora continua"""
        self.logger.info("Iniciando validación automática")

        try:
            # Analizar patrones
            patterns = self.pattern_analyzer.analyze_content(data)
            
            # Aprender de nuevos patrones
            self._learn_patterns(patterns)
            
            # Aplicar validaciones aprendidas
            enhanced_validation = self._enhance_validation(data, template)
            
            # Validar contenido
            validation_result = self.content_validator.validate_content(
                enhanced_validation,
                template
            )

            # Registrar resultados
            self._record_validation(validation_result)
            
            return {
                'validation': validation_result,
                'patterns': patterns,
                'learned_rules': self._get_learned_rules(),
                'suggestions': self._generate_suggestions(validation_result)
            }

        except Exception as e:
            self.logger.error(f"Error en validación: {str(e)}")
            return {'error': str(e)}

    def _learn_patterns(self, patterns: Dict[str, Any]) -> None:
        """Aprende de patrones detectados"""
        for field_name, pattern_info in patterns.get('patterns', {}).items():
            if pattern_info['confidence'] >= self.confidence_threshold:
                if field_name not in self.learned_patterns:
                    self.learned_patterns[field_name] = {
                        'patterns': [],
                        'type_suggestions': set(),
                        'validation_count': 0
                    }
                
                learned = self.learned_patterns[field_name]
                learned['patterns'].extend(pattern_info['patterns'])
                learned['type_suggestions'].add(pattern_info['suggested_type'])
                learned['validation_count'] += 1

    def _enhance_validation(self, data: Dict[str, Any], 
                          template: Dict[str, Any]) -> Dict[str, Any]:
        """Mejora datos usando patrones aprendidos"""
        enhanced = data.copy()
        
        for field_name, value in data.items():
            if learned := self.learned_patterns.get(field_name):
                if learned['validation_count'] >= 5:  # Mínimo de aprendizaje
                    suggested_type = self._get_most_common_type(
                        learned['type_suggestions']
                    )
                    
                    # Transformar si es necesario
                    if suggested_type:
                        transformed, confidence = self.transformer.transform_field(
                            value,
                            'string',
                            suggested_type
                        )
                        if confidence > self.confidence_threshold:
                            enhanced[field_name] = transformed

        return enhanced

    def _get_most_common_type(self, type_suggestions: set) -> Optional[str]:
        """Obtiene el tipo más común sugerido"""
        if not type_suggestions:
            return None
        return max(type_suggestions, key=list(type_suggestions).count)

    def _get_learned_rules(self) -> Dict[str, Any]:
        """Obtiene reglas aprendidas"""
        rules = {}
        for field_name, learned in self.learned_patterns.items():
            if learned['validation_count'] >= 5:
                rules[field_name] = {
                    'suggested_type': self._get_most_common_type(
                        learned['type_suggestions']
                    ),
                    'common_patterns': self._get_common_patterns(
                        learned['patterns']
                    ),
                    'confidence': learned['validation_count'] / 10  # Max 1.0
                }
        return rules

    def _get_common_patterns(self, patterns: List[str]) -> List[str]:
        """Obtiene patrones más comunes"""
        if not patterns:
            return []
        return [
            pattern for pattern, count in Counter(patterns).items()
            if count >= 3  # Mínimo de ocurrencias
        ]

    def _generate_suggestions(self, validation_result: Dict[str, Any]) -> List[str]:
        """Genera sugerencias basadas en validación"""
        suggestions = []
        
        # Sugerencias por tipo
        for field, result in validation_result.get('fields', {}).items():
            if not result.get('is_valid'):
                if learned := self.learned_patterns.get(field):
                    suggested_type = self._get_most_common_type(
                        learned['type_suggestions']
                    )
                    if suggested_type:
                        suggestions.append(
                            f"Campo {field}: Considerar tipo {suggested_type}"
                        )

        # Sugerencias generales
        if validation_result.get('error_count', 0) > 3:
            suggestions.append(
                "Considerar revisión manual de validaciones"
            )

        return suggestions

    def _record_validation(self, result: Dict[str, Any]) -> None:
        """Registra resultado de validación"""
        self.validation_history.append({
            'timestamp': datetime.now().isoformat(),
            'success': result.get('is_valid', False),
            'error_count': len(result.get('errors', [])),
            'learned_rules': len(self.learned_patterns)
        })

    def get_validation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de validación"""
        if not self.validation_history:
            return {'status': 'No hay historial de validaciones'}

        total = len(self.validation_history)
        successful = sum(1 for v in self.validation_history if v['success'])
        
        return {
            'total_validations': total,
            'successful': successful,
            'success_rate': round((successful / total) * 100, 2),
            'learned_patterns': len(self.learned_patterns),
            'average_errors': sum(
                v['error_count'] for v in self.validation_history
            ) / total
        }
