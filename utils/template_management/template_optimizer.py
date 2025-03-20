from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from .logging_config import setup_logging
from .field_reconciliation import FieldReconciliation
from .pattern_detector import PatternDetector

class TemplateOptimizer:
    """Optimizador de plantillas que no interfiere con el sistema existente"""

    def __init__(self):
        self.logger = setup_logging('template_optimizer')
        self.field_reconciliation = FieldReconciliation()
        self.pattern_detector = PatternDetector()
        self.optimization_history = []
        
    def optimize_template(self, template: Dict[str, Any], 
                        sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimiza una plantilla basándose en datos de muestra"""
        self.logger.info(f"Iniciando optimización de plantilla: {template.get('nombre_archivo')}")
        
        try:
            # Crear copia de la plantilla original para no modificarla
            optimized = template.copy()
            
            # Analizar y mejorar campos
            improved_fields = self._analyze_and_improve_fields(
                template.get('campos', {}),
                sample_data
            )
            
            # Sugerir nuevos campos sin modificar existentes
            new_fields = self._suggest_new_fields(
                template.get('campos', {}),
                sample_data
            )
            
            # Generar recomendaciones sin cambiar configuración
            recommendations = self._generate_recommendations(
                improved_fields,
                new_fields
            )
            
            # Crear plantilla optimizada
            optimized['campos'] = improved_fields
            optimized['campos_sugeridos'] = new_fields
            optimized['recomendaciones'] = recommendations
            optimized['metadata_optimizacion'] = {
                'timestamp': datetime.now().isoformat(),
                'campos_mejorados': len(improved_fields),
                'nuevos_campos_sugeridos': len(new_fields)
            }
            
            # Registrar optimización
            self._record_optimization(template, optimized)
            
            return optimized

        except Exception as e:
            self.logger.error(f"Error en optimización: {str(e)}")
            return template  # Retornar plantilla original en caso de error

    def _analyze_and_improve_fields(self, existing_fields: Dict[str, Any],
                                  sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analiza y mejora campos existentes sin modificarlos"""
        improved = existing_fields.copy()
        
        for field_name, field_info in existing_fields.items():
            field_samples = self._extract_field_samples(field_name, sample_data)
            
            if detected_improvements := self._detect_field_improvements(
                field_info,
                field_samples
            ):
                # Agregar mejoras como sugerencias
                improved[field_name]['suggested_improvements'] = detected_improvements

        return improved

    def _suggest_new_fields(self, existing_fields: Dict[str, Any],
                          sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sugiere nuevos campos sin modificar existentes"""
        new_fields = {}
        existing_names = set(existing_fields.keys())

        # Detectar campos potenciales en datos de muestra
        detected_fields = self.pattern_detector.detect_patterns(
            sample_data
        )

        # Filtrar solo campos nuevos
        for field_name, field_info in detected_fields.items():
            if field_name not in existing_names:
                new_fields[field_name] = {
                    'type': field_info['type'],
                    'confidence': field_info['confidence'],
                    'sample_count': field_info['occurrences'],
                    'suggested': True
                }

        return new_fields

    def _generate_recommendations(self, improved_fields: Dict[str, Any],
                                new_fields: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones de optimización"""
        recommendations = []

        # Analizar mejoras sugeridas
        for field_name, field_info in improved_fields.items():
            if improvements := field_info.get('suggested_improvements'):
                for improvement in improvements:
                    recommendations.append(
                        f"Campo '{field_name}': {improvement['suggestion']}"
                    )

        # Analizar nuevos campos
        if new_fields:
            recommendations.append(
                f"Se detectaron {len(new_fields)} campos potenciales nuevos"
            )
            for field_name, field_info in new_fields.items():
                if field_info['confidence'] > 0.8:
                    recommendations.append(
                        f"Considerar agregar campo '{field_name}' "
                        f"(confianza: {field_info['confidence']})"
                    )

        return recommendations

    def _record_optimization(self, original: Dict[str, Any], 
                           optimized: Dict[str, Any]) -> None:
        """Registra resultado de optimización"""
        self.optimization_history.append({
            'timestamp': datetime.now().isoformat(),
            'template_name': original.get('nombre_archivo'),
            'original_fields': len(original.get('campos', {})),
            'improved_fields': len(optimized.get('campos', {})),
            'new_suggestions': len(optimized.get('campos_sugeridos', {}))
        })
