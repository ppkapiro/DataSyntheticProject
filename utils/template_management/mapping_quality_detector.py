from typing import Dict, Any, List, Optional
from datetime import datetime
from .logging_config import setup_logging
from .field_relationship_manager import FieldRelationshipManager

class MappingQualityDetector:
    """Sistema de detección y gestión de calidad en el mapeo"""

    def __init__(self):
        self.logger = setup_logging('quality_detector')
        self.relationship_manager = FieldRelationshipManager()
        self.quality_thresholds = {
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5
        }

    def analyze_mapping_quality(self, mapped_data: Dict[str, Any], 
                              template: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la calidad del mapeo realizado"""
        self.logger.info("Analizando calidad del mapeo")
        
        quality_analysis = {
            'overall_quality': 0.0,
            'field_quality': {},
            'issues': [],
            'recommendations': [],
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'template': template.get('nombre_archivo'),
                'total_fields': len(template.get('campos', {}))
            }
        }

        # Analizar calidad por campo
        field_scores = self._analyze_field_quality(mapped_data, template)
        quality_analysis['field_quality'] = field_scores
        
        # Calcular calidad general
        quality_analysis['overall_quality'] = self._calculate_overall_quality(field_scores)
        
        # Detectar problemas
        quality_analysis['issues'] = self._detect_quality_issues(field_scores)
        
        # Generar recomendaciones
        quality_analysis['recommendations'] = self._generate_recommendations(
            field_scores,
            quality_analysis['issues']
        )

        return quality_analysis

    def _analyze_field_quality(self, mapped_data: Dict[str, Any], 
                             template: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la calidad de cada campo mapeado"""
        field_quality = {}
        template_fields = template.get('campos', {})
        mapped_fields = mapped_data.get('fields', {})

        for field_name, field_info in template_fields.items():
            if mapped_field := mapped_fields.get(field_name):
                field_quality[field_name] = self._calculate_field_quality(
                    mapped_field,
                    field_info
                )
            else:
                field_quality[field_name] = {
                    'quality': 0.0,
                    'issues': ['Campo no mapeado'],
                    'status': 'missing'
                }

        return field_quality

    def _calculate_field_quality(self, mapped_field: Dict[str, Any], 
                               template_field: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula la calidad de un campo específico"""
        quality_scores = []
        issues = []

        # Validar tipo de dato
        if mapped_field.get('type') == template_field.get('type'):
            quality_scores.append(1.0)
        else:
            quality_scores.append(0.5)
            issues.append('Tipo de dato no coincide')

        # Validar confianza del mapeo
        confidence = mapped_field.get('confidence', 0)
        quality_scores.append(confidence)
        
        if confidence < self.quality_thresholds['medium']:
            issues.append('Baja confianza en el mapeo')

        # Validar transformaciones
        if mapped_field.get('transformed', False):
            quality_scores.append(0.8)
            issues.append('Requirió transformación')

        # Calcular calidad final
        quality = sum(quality_scores) / len(quality_scores)
        
        return {
            'quality': round(quality, 2),
            'issues': issues,
            'status': self._determine_quality_status(quality)
        }

    def _calculate_overall_quality(self, field_scores: Dict[str, Any]) -> float:
        """Calcula la calidad general del mapeo"""
        if not field_scores:
            return 0.0
            
        qualities = [
            score['quality'] for score in field_scores.values()
        ]
        return round(sum(qualities) / len(qualities), 2)

    def _detect_quality_issues(self, field_scores: Dict[str, Any]) -> List[str]:
        """Detecta problemas generales de calidad"""
        issues = []
        low_quality_fields = [
            name for name, data in field_scores.items()
            if data['quality'] < self.quality_thresholds['medium']
        ]
        
        if low_quality_fields:
            issues.append(
                f"Campos con baja calidad: {', '.join(low_quality_fields)}"
            )

        missing_fields = [
            name for name, data in field_scores.items()
            if data['status'] == 'missing'
        ]
        
        if missing_fields:
            issues.append(
                f"Campos no mapeados: {', '.join(missing_fields)}"
            )

        return issues

    def _determine_quality_status(self, quality: float) -> str:
        """Determina el estado de calidad basado en el puntaje"""
        if quality >= self.quality_thresholds['high']:
            return 'high'
        elif quality >= self.quality_thresholds['medium']:
            return 'medium'
        elif quality >= self.quality_thresholds['low']:
            return 'low'
        return 'critical'

    def _generate_recommendations(self, field_scores: Dict[str, Any], 
                                issues: List[str]) -> List[str]:
        """Genera recomendaciones para mejorar la calidad"""
        recommendations = []

        # Recomendar revisión manual
        low_quality_fields = [
            name for name, data in field_scores.items()
            if data['quality'] < self.quality_thresholds['medium']
        ]
        if low_quality_fields:
            recommendations.append(
                f"Revisar manualmente: {', '.join(low_quality_fields)}"
            )

        # Recomendar validaciones adicionales
        fields_needing_validation = [
            name for name, data in field_scores.items()
            if 'Tipo de dato no coincide' in data.get('issues', [])
        ]
        if fields_needing_validation:
            recommendations.append(
                f"Validar tipos de datos en: {', '.join(fields_needing_validation)}"
            )

        return recommendations
