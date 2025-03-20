from typing import Dict, Any, List
from pathlib import Path
from .field_analyzer import FieldAnalyzer

class TemplateImportAnalyzer:
    """Analizador de requisitos de importación"""

    def __init__(self):
        self.field_analyzer = FieldAnalyzer()

    def analyze_import_requirements(self, source: Path) -> Dict[str, Any]:
        """Analiza los requisitos de importación desde una fuente"""
        raw_analysis = self.field_analyzer.analyze_file(source)
        
        return {
            'template_info': {
                'name': source.stem,
                'format': self._detect_template_format(raw_analysis),
                'total_fields': len(raw_analysis['fields'])
            },
            'fields': self._process_fields(raw_analysis['fields']),
            'import_rules': self._extract_import_rules(raw_analysis),
            'validations': self._extract_validations(raw_analysis)
        }

    def _detect_template_format(self, analysis: Dict[str, Any]) -> str:
        """Detecta el formato esperado para importación"""
        format_hints = {
            'django': ['model', 'field', 'Meta'],
            'json': ['type', 'properties'],
            'yaml': ['fields', 'validations'],
            'csv': ['separator', 'headers']
        }
        
        scores = {fmt: 0 for fmt in format_hints}
        content_str = str(analysis)
        
        for fmt, hints in format_hints.items():
            for hint in hints:
                if hint in content_str:
                    scores[fmt] += 1
                    
        return max(scores.items(), key=lambda x: x[1])[0]

    def _process_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y enriquece la información de campos"""
        processed = {}
        
        for field_name, field_info in fields.items():
            processed[field_name] = {
                **field_info,
                'import_requirements': self._get_field_requirements(field_info),
                'validations': self._get_field_validations(field_info),
                'suggestions': self._generate_field_suggestions(field_info)
            }
            
        return processed

    def _get_field_requirements(self, field_info: Dict[str, Any]) -> Dict[str, Any]:
        """Determina requisitos de importación para un campo"""
        return {
            'required': field_info.get('required', False),
            'format': self._determine_format(field_info),
            'constraints': field_info.get('constraints', []),
            'dependencies': self._find_dependencies(field_info)
        }

    def _determine_format(self, field_info: Dict[str, Any]) -> str:
        """Determina el formato requerido para un campo"""
        type_formats = {
            'string': 'text',
            'number': 'numeric',
            'date': 'YYYY-MM-DD',
            'boolean': 'true/false',
            'email': 'email@domain.com'
        }
        return type_formats.get(field_info.get('type', 'string'), 'text')
