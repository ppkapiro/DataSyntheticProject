from typing import Dict, Any, Optional, List
from pathlib import Path
from .field_matcher import FieldMatcher
from .logging_config import setup_logging

class PDFTemplateConnector:
    """Conecta los datos extraídos del PDF con las plantillas existentes"""

    def __init__(self):
        self.logger = setup_logging()
        self.field_matcher = FieldMatcher()
        self.last_result = None

    def connect_data(self, pdf_data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Conecta los datos del PDF con una plantilla específica"""
        self.logger.info(f"Conectando datos con plantilla: {template.get('nombre_archivo', 'Unknown')}")
        
        # Encontrar coincidencias entre campos
        matches = self.field_matcher.find_matches(
            pdf_data.get('fields', {}),
            template.get('campos', {})
        )

        # Generar estructura según plantilla
        result = self._generate_template_structure(matches, template)
        self.last_result = result
        return result

    def get_validation_report(self) -> Dict[str, Any]:
        """Genera reporte de validación del último mapeo"""
        if not self.last_result:
            return {'status': 'No hay datos procesados'}

        campos = self.last_result.get('campos', {})
        total_campos = len(campos)
        campos_validos = sum(1 for c in campos.values() if c['validated'])
        
        return {
            'total_campos': total_campos,
            'campos_validos': campos_validos,
            'campos_invalidos': total_campos - campos_validos,
            'confianza_promedio': self._calculate_average_confidence(campos),
            'campos_faltantes': self._get_missing_fields(campos),
            'campos_baja_confianza': self._get_low_confidence_fields(campos)
        }

    def _generate_template_structure(self, matches: Dict[str, Any], 
                                  template: Dict[str, Any]) -> Dict[str, Any]:
        """Genera la estructura final según la plantilla"""
        return {
            'nombre_archivo': template.get('nombre_archivo'),
            'tipo_documento': template.get('tipo_documento'),
            'campos': self._map_fields(matches, template),
            'metadata': {
                'confidence': matches.get('stats', {}).get('confidence_avg', 0),
                'campos_mapeados': len(matches.get('matches', {})),
                'campos_totales': len(template.get('campos', {}))
            }
        }

    def _map_fields(self, matches: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Mapea los campos según las coincidencias encontradas"""
        campos = {}
        template_fields = template.get('campos', {})
        match_data = matches.get('matches', {})

        for field_name, field_info in template_fields.items():
            if match := match_data.get(field_name):
                campos[field_name] = {
                    'value': match['value'],
                    'confidence': match['confidence'],
                    'type': field_info.get('type'),
                    'validated': match['type_match']
                }
            else:
                campos[field_name] = {
                    'value': None,
                    'confidence': 0,
                    'type': field_info.get('type'),
                    'validated': False
                }

        return campos

    def _calculate_average_confidence(self, campos: Dict[str, Any]) -> float:
        """Calcula la confianza promedio de los campos"""
        if not campos:
            return 0.0
        return round(sum(c['confidence'] for c in campos.values()) / len(campos), 2)

    def _get_missing_fields(self, campos: Dict[str, Any]) -> List[str]:
        """Obtiene lista de campos faltantes"""
        return [name for name, data in campos.items() if data['value'] is None]

    def _get_low_confidence_fields(self, campos: Dict[str, Any]) -> List[str]:
        """Obtiene lista de campos con baja confianza"""
        return [name for name, data in campos.items() if data['confidence'] < 70]
