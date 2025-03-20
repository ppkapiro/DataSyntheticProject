from typing import Dict, Any, List, Optional
from .logging_config import setup_logging
from .field_analyzer import FieldAnalyzer

class FieldMatcher:
    """Analizador de coincidencia de campos entre PDF y plantilla"""

    def __init__(self):
        self.logger = setup_logging()
        self.field_analyzer = FieldAnalyzer()
        
    def find_matches(self, pdf_fields: Dict[str, Any], template_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encuentra coincidencias entre campos del PDF y la plantilla.
        Mantiene compatibilidad con el sistema existente.
        """
        self.logger.info("Iniciando búsqueda de coincidencias")
        
        matches = {}
        template_field_scores = {}

        # Primera pasada: coincidencias exactas
        for template_name, template_info in template_fields.items():
            for pdf_name, pdf_info in pdf_fields.items():
                score = self._calculate_field_similarity(
                    template_name, template_info,
                    pdf_name, pdf_info
                )
                template_field_scores.setdefault(template_name, []).append({
                    'pdf_field': pdf_name,
                    'score': score,
                    'info': pdf_info
                })

        # Asignar mejores coincidencias
        for template_name, scores in template_field_scores.items():
            if scores:
                best_match = max(scores, key=lambda x: x['score'])
                if best_match['score'] >= 0.5:  # Umbral mínimo de confianza
                    matches[template_name] = {
                        'pdf_field': best_match['pdf_field'],
                        'confidence': round(best_match['score'] * 100, 2),
                        'type_match': template_fields[template_name].get('type') == 
                                    best_match['info'].get('type'),
                        'value': best_match['info'].get('value')
                    }

        return {
            'matches': matches,
            'stats': {
                'total_template_fields': len(template_fields),
                'total_pdf_fields': len(pdf_fields),
                'matched_fields': len(matches),
                'confidence_avg': self._calculate_average_confidence(matches)
            },
            'unmatched_template_fields': [
                name for name in template_fields 
                if name not in matches
            ]
        }

    def _calculate_field_similarity(self, template_name: str, template_info: Dict[str, Any],
                                 pdf_name: str, pdf_info: Dict[str, Any]) -> float:
        """Calcula la similitud entre campos usando múltiples criterios"""
        # Similitud de nombre (50%)
        name_score = self._calculate_name_similarity(template_name, pdf_name) * 0.5
        
        # Similitud de tipo (30%)
        type_score = (0.3 if template_info.get('type') == pdf_info.get('type') else 0.0)
        
        # Similitud de contenido (20%)
        content_score = self._calculate_content_similarity(template_info, pdf_info) * 0.2
        
        return name_score + type_score + content_score

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calcula similitud entre nombres normalizados"""
        # Normalizar nombres
        n1 = self._normalize_field_name(name1)
        n2 = self._normalize_field_name(name2)
        
        # Coincidencia exacta
        if n1 == n2:
            return 1.0
            
        # Coincidencia parcial
        words1 = set(n1.split())
        words2 = set(n2.split())
        
        if common_words := words1.intersection(words2):
            return len(common_words) / max(len(words1), len(words2))
            
        return 0.0

    def _normalize_field_name(self, name: str) -> str:
        """Normaliza el nombre de un campo para comparación"""
        replacements = {
            'first': 'nombre',
            'last': 'apellido',
            'name': 'nombre',
            'birth': 'nacimiento',
            'date': 'fecha'
        }
        
        name = name.lower().replace('_', ' ')
        for eng, esp in replacements.items():
            name = name.replace(eng, esp)
            
        return name.strip()

    def _calculate_content_similarity(self, template_info: Dict[str, Any], 
                                   pdf_info: Dict[str, Any]) -> float:
        """Calcula similitud basada en el contenido y restricciones"""
        score = 0.0
        
        # Validar formato
        if template_info.get('format') == pdf_info.get('format'):
            score += 0.5
            
        # Validar restricciones
        template_constraints = set(str(v) for v in template_info.get('validators', []))
        pdf_constraints = set(str(v) for v in pdf_info.get('validators', []))
        
        if common_constraints := template_constraints.intersection(pdf_constraints):
            score += 0.5 * (len(common_constraints) / 
                          max(len(template_constraints), len(pdf_constraints), 1))
            
        return score

    def _calculate_average_confidence(self, matches: Dict[str, Any]) -> float:
        """Calcula la confianza promedio de las coincidencias"""
        if not matches:
            return 0.0
        return round(
            sum(match['confidence'] for match in matches.values()) / len(matches),
            2
        )
