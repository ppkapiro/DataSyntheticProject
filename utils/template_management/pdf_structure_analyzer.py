from typing import Dict, Any, List, Optional
from pathlib import Path
import re
from .logging_config import setup_logging
from .pattern_detector import PatternDetector

class PDFStructureAnalyzer:
    """Analizador de estructura de documentos PDF"""

    def __init__(self):
        self.logger = setup_logging('pdf_structure')
        self.pattern_detector = PatternDetector()
        self.section_markers = {
            'patient_info': [
                'información del paciente',
                'datos personales',
                'patient information'
            ],
            'medical_history': [
                'historial médico',
                'antecedentes',
                'medical history'
            ],
            'diagnosis': [
                'diagnóstico',
                'diagnosis',
                'assessment'
            ]
        }

    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analiza la estructura del documento PDF"""
        self.logger.info("Iniciando análisis de estructura")
        
        analysis = {
            'sections': self._identify_sections(content),
            'metadata': self._extract_metadata(content),
            'structure_type': self._determine_structure_type(content),
            'quality_metrics': {}
        }

        # Calcular métricas de calidad
        analysis['quality_metrics'] = self._calculate_quality_metrics(analysis)
        
        return analysis

    def _identify_sections(self, content: str) -> List[Dict[str, Any]]:
        """Identifica secciones en el documento"""
        sections = []
        current_section = None
        lines = content.split('\n')

        for idx, line in enumerate(lines):
            # Detectar inicio de sección
            if section := self._is_section_header(line):
                if current_section:
                    current_section['end_line'] = idx - 1
                    sections.append(current_section)
                
                current_section = {
                    'type': section,
                    'start_line': idx,
                    'content': [],
                    'confidence': self._calculate_section_confidence(line, section)
                }
            elif current_section:
                current_section['content'].append(line)

        # Agregar última sección
        if current_section:
            current_section['end_line'] = len(lines)
            sections.append(current_section)

        return sections

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extrae metadata del documento"""
        metadata = {
            'total_lines': len(content.split('\n')),
            'sections_detected': 0,
            'form_fields_detected': 0,
            'document_type': self._detect_document_type(content)
        }

        # Detectar campos de formulario
        form_fields = re.findall(r'[_]{3,}|[\[].+?[\]]|□|☐|▢', content)
        metadata['form_fields_detected'] = len(form_fields)

        return metadata

    def _determine_structure_type(self, content: str) -> str:
        """Determina el tipo de estructura del documento"""
        structure_indicators = {
            'form': (
                r'[_]{3,}|[\[].+?[\]]|□|☐|▢',  # Campos de formulario
                r'\d+[\.)][\s]|\*\s|\[\s\]'     # Listas y checkbox
            ),
            'report': (
                r'^[A-Z][^.!?]*[.!?]$',         # Oraciones completas
                r'\b(?:conclusion|summary)\b'    # Palabras clave de reporte
            ),
            'record': (
                r'\b(?:history|assessment|plan)\b',  # Secciones clínicas
                r'\d{1,2}/\d{1,2}/\d{2,4}'         # Fechas
            )
        }

        scores = {stype: 0 for stype in structure_indicators}
        
        for stype, patterns in structure_indicators.items():
            for pattern in patterns:
                if matches := re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    scores[stype] += sum(1 for _ in matches)

        return max(scores.items(), key=lambda x: x[1])[0]

    def _is_section_header(self, line: str) -> Optional[str]:
        """Determina si una línea es encabezado de sección"""
        line = line.strip().lower()
        
        for section_type, markers in self.section_markers.items():
            if any(marker in line for marker in markers):
                return section_type
                
        # Detectar otros posibles encabezados
        if (re.match(r'^[A-Z][^a-z]{2,}.*:?$', line) or  # MAYÚSCULAS
            re.match(r'^[\d\.]+\s+[A-Z]', line) or       # Numeración
            len(line) < 50 and line.endswith(':')):       # Corto con :
            return 'unknown'
            
        return None

    def _calculate_section_confidence(self, line: str, section_type: str) -> float:
        """Calcula la confianza en la identificación de una sección"""
        confidence = 0.5  # Base confidence
        
        # Ajustar por coincidencia exacta
        if section_type != 'unknown':
            confidence += 0.3
            
        # Ajustar por formato
        if re.match(r'^[A-Z][^a-z]{2,}.*:?$', line):  # MAYÚSCULAS
            confidence += 0.1
        if line.endswith(':'):
            confidence += 0.1
            
        return min(confidence, 1.0)

    def _calculate_quality_metrics(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calcula métricas de calidad del análisis"""
        metrics = {
            'structure_confidence': 0.0,
            'section_detection_quality': 0.0,
            'metadata_completeness': 0.0
        }

        # Calidad de detección de secciones
        if sections := analysis.get('sections', []):
            section_scores = [s.get('confidence', 0) for s in sections]
            metrics['section_detection_quality'] = sum(section_scores) / len(section_scores)

        # Completitud de metadata
        metadata = analysis.get('metadata', {})
        expected_meta = {'total_lines', 'sections_detected', 'document_type'}
        metrics['metadata_completeness'] = len(set(metadata.keys()) & expected_meta) / len(expected_meta)

        # Confianza general en la estructura
        metrics['structure_confidence'] = (
            metrics['section_detection_quality'] * 0.6 +
            metrics['metadata_completeness'] * 0.4
        )

        return metrics
