from pathlib import Path
from typing import Dict, Any, Optional, List
from .field_analyzer import FieldAnalyzer
from .logging_config import setup_logging

class PDFTemplateMapper:
    """Mapea contenido de PDF a plantillas existentes"""

    def __init__(self):
        self.logger = setup_logging()
        self.field_analyzer = FieldAnalyzer()
        self.current_template = None
        self.current_pdf_content = None

    def analyze_correspondence(self, pdf_content: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la correspondencia entre PDF y plantilla"""
        self.logger.info("Iniciando análisis de correspondencia")
        self.current_template = template
        self.current_pdf_content = pdf_content

        return {
            'mapping_result': self._create_initial_mapping(),
            'confidence_scores': self._calculate_confidence_scores(),
            'missing_fields': self._identify_missing_fields(),
            'metadata': {
                'template_name': template.get('nombre', 'unknown'),
                'total_fields': len(template.get('campos', {})),
                'mapped_fields': 0,  # Se actualizará durante el mapeo
                'quality_score': 0.0  # Se actualizará durante el mapeo
            }
        }

    def _create_initial_mapping(self) -> Dict[str, Any]:
        """Crea el mapeo inicial entre campos"""
        mapping = {}
        template_fields = self.current_template.get('campos', {})
        pdf_fields = self.current_pdf_content.get('fields', {})

        for template_field, template_info in template_fields.items():
            match = self._find_best_match(template_field, template_info, pdf_fields)
            if match:
                mapping[template_field] = {
                    'pdf_field': match['field'],
                    'confidence': match['confidence'],
                    'transformations': match['transformations']
                }

        return mapping

    def _find_best_match(self, template_field: str, template_info: Dict[str, Any], 
                        pdf_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Encuentra la mejor correspondencia para un campo de la plantilla"""
        best_match = None
        highest_confidence = 0.0

        for pdf_field, pdf_info in pdf_fields.items():
            confidence = self._calculate_field_similarity(
                template_field, template_info,
                pdf_field, pdf_info
            )

            if confidence > highest_confidence:
                highest_confidence = confidence
                transformations = self._identify_needed_transformations(
                    template_info, pdf_info
                )
                
                best_match = {
                    'field': pdf_field,
                    'confidence': confidence,
                    'transformations': transformations
                }

        return best_match

    def _calculate_field_similarity(self, template_field: str, template_info: Dict[str, Any],
                                 pdf_field: str, pdf_info: Dict[str, Any]) -> float:
        """Calcula la similitud entre campos"""
        # Puntaje base por coincidencia de nombres
        name_similarity = self._calculate_name_similarity(template_field, pdf_field)
        
        # Puntaje por tipo de dato
        type_match = template_info.get('type') == pdf_info.get('type')
        type_score = 0.3 if type_match else 0.0
        
        # Puntaje por validaciones similares
        validation_score = self._compare_validations(
            template_info.get('validators', []),
            pdf_info.get('validators', [])
        )

        return (name_similarity * 0.5) + type_score + (validation_score * 0.2)

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calcula la similitud entre nombres de campos"""
        # Normalizar nombres
        name1 = name1.lower().replace('_', ' ')
        name2 = name2.lower().replace('_', ' ')

        # Exacta
        if name1 == name2:
            return 1.0

        # Contiene
        if name1 in name2 or name2 in name1:
            return 0.8

        # Similitud de palabras
        words1 = set(name1.split())
        words2 = set(name2.split())
        common_words = words1.intersection(words2)
        
        if common_words:
            return len(common_words) / max(len(words1), len(words2))

        return 0.0
