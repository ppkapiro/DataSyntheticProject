from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from .logging_config import setup_logging

class PatternDetector:
    """Sistema de detección de patrones para mapeo PDF-Plantilla"""

    def __init__(self):
        self.logger = setup_logging('pattern_detector')
        self.known_patterns = {
            'patient_info': {
                'name': [
                    r'(?:nombre|name)[:]\s*([^\n]+)',
                    r'(?:paciente|patient)[:]\s*([^\n]+)'
                ],
                'dob': [
                    r'(?:fecha[_ ]nac|birth[_ ]date|dob)[:]\s*([^\n]+)',
                    r'(?:nacimiento|birth)[:]\s*([^\n]+)'
                ],
                'id': [
                    r'(?:id|número|code|identifier)[:]\s*([^\n]+)',
                    r'(?:documento|document)[:]\s*([^\n]+)'
                ]
            },
            'contact_info': {
                'phone': [
                    r'(?:teléfono|phone|tel)[:]\s*([^\n]+)',
                    r'(?:móvil|mobile|cel)[:]\s*([^\n]+)'
                ],
                'email': [
                    r'(?:email|correo|e-mail)[:]\s*([^\s@]+@[^\s@]+\.[^\s@]+)',
                    r'(?:mail)[:]\s*([^\s@]+@[^\s@]+\.[^\s@]+)'
                ]
            },
            'medical_info': {
                'diagnosis': [
                    r'(?:diagnóstico|diagnosis)[:]\s*([^\n]+)',
                    r'(?:condición|condition)[:]\s*([^\n]+)'
                ],
                'medications': [
                    r'(?:medicación|medication)[:]\s*([^\n]+)',
                    r'(?:medicamentos|medicines)[:]\s*([^\n]+)'
                ]
            }
        }

    def detect_patterns(self, content: str, template_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta patrones en el contenido basado en campos de la plantilla"""
        self.logger.info("Iniciando detección de patrones")
        
        results = {}
        for field_name, field_info in template_fields.items():
            # Buscar coincidencias basadas en tipo y nombre
            matches = self._find_field_matches(field_name, field_info, content)
            
            if matches:
                best_match = self._select_best_match(matches)
                results[field_name] = {
                    'value': best_match['value'],
                    'confidence': best_match['confidence'],
                    'pattern_used': best_match['pattern'],
                    'type': field_info.get('type', 'string')
                }
            else:
                self.logger.debug(f"No se encontraron coincidencias para: {field_name}")

        return {
            'detected_fields': results,
            'metadata': {
                'total_fields': len(template_fields),
                'matched_fields': len(results),
                'timestamp': datetime.now().isoformat()
            }
        }

    def _find_field_matches(self, field_name: str, field_info: Dict[str, Any], 
                           content: str) -> List[Dict[str, Any]]:
        """Encuentra todas las posibles coincidencias para un campo"""
        matches = []
        
        # Buscar en patrones conocidos
        category = self._determine_field_category(field_name)
        if category in self.known_patterns:
            for field_type, patterns in self.known_patterns[category].items():
                for pattern in patterns:
                    if found := re.search(pattern, content, re.IGNORECASE):
                        matches.append({
                            'value': found.group(1).strip(),
                            'confidence': self._calculate_match_confidence(
                                found.group(0),
                                field_info
                            ),
                            'pattern': pattern
                        })

        return matches

    def _determine_field_category(self, field_name: str) -> str:
        """Determina la categoría de un campo basado en su nombre"""
        field_name = field_name.lower()
        
        if any(word in field_name for word in ['name', 'nombre', 'patient', 'paciente', 'birth', 'id']):
            return 'patient_info'
        elif any(word in field_name for word in ['phone', 'email', 'contact', 'tel']):
            return 'contact_info'
        elif any(word in field_name for word in ['diagnosis', 'medication', 'treatment']):
            return 'medical_info'
            
        return 'general'

    def _calculate_match_confidence(self, match_text: str, field_info: Dict[str, Any]) -> float:
        """Calcula la confianza de una coincidencia"""
        confidence = 0.5  # Base confidence
        
        # Ajustar por longitud del texto
        if len(match_text) > 5:
            confidence += 0.1
            
        # Ajustar por tipo de campo
        if self._validate_field_type(match_text, field_info.get('type', 'string')):
            confidence += 0.2
            
        # Ajustar por formato esperado
        if field_format := field_info.get('format'):
            if self._validate_format(match_text, field_format):
                confidence += 0.2

        return min(confidence, 1.0)

    def _select_best_match(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Selecciona la mejor coincidencia basada en confianza"""
        return max(matches, key=lambda x: x['confidence'])
