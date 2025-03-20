from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
from .logging_config import setup_logging
from .content_validator import ContentValidator

class ValidationReporter:
    """Sistema de generación y control de reportes de validación"""

    def __init__(self):
        self.logger = setup_logging('validation_reporter')
        self.validator = ContentValidator()
        self.reports_history = []
        self.current_report = None

    def generate_report(self, mapping_data: Dict[str, Any], 
                       template: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un reporte detallado de validación"""
        self.logger.info("Generando reporte de validación")

        try:
            # Validar datos
            validation_result = self.validator.validate_content(
                mapping_data, 
                template
            )

            # Construir reporte
            report = {
                'validation': validation_result,
                'analysis': self._analyze_validation(validation_result),
                'recommendations': self._generate_recommendations(validation_result),
                'summary': self._create_summary(validation_result),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'template': template.get('nombre_archivo'),
                    'fields_count': len(template.get('campos', {}))
                }
            }

            # Almacenar reporte
            self._store_report(report)
            self.current_report = report

            return report

        except Exception as e:
            self.logger.error(f"Error generando reporte: {str(e)}")
            return {'error': str(e)}

    def _analyze_validation(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza resultados de validación"""
        fields = validation.get('fields', {})
        
        return {
            'field_stats': {
                'total': len(fields),
                'valid': sum(1 for f in fields.values() if f.get('is_valid')),
                'invalid': sum(1 for f in fields.values() if not f.get('is_valid')),
                'warnings': sum(len(f.get('warnings', [])) for f in fields.values())
            },
            'error_types': self._categorize_errors(fields),
            'quality_metrics': self._calculate_quality_metrics(fields)
        }

    def _generate_recommendations(self, validation: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en la validación"""
        recommendations = []
        fields = validation.get('fields', {})

        # Analizar campos inválidos
        invalid_fields = [
            name for name, data in fields.items() 
            if not data.get('is_valid')
        ]
        if invalid_fields:
            recommendations.append(
                f"Revisar campos inválidos: {', '.join(invalid_fields)}"
            )

        # Analizar campos con advertencias
        fields_with_warnings = [
            name for name, data in fields.items() 
            if data.get('warnings')
        ]
        if fields_with_warnings:
            recommendations.append(
                f"Atender advertencias en: {', '.join(fields_with_warnings)}"
            )

        return recommendations

    def _create_summary(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        """Crea resumen ejecutivo de validación"""
        return {
            'status': 'valid' if validation.get('is_valid') else 'invalid',
            'error_count': len(validation.get('errors', [])),
            'warning_count': len(validation.get('warnings', [])),
            'critical_issues': self._identify_critical_issues(validation)
        }

    def _identify_critical_issues(self, validation: Dict[str, Any]) -> List[str]:
        """Identifica problemas críticos en la validación"""
        critical = []
        fields = validation.get('fields', {})

        # Campos requeridos faltantes
        missing_required = [
            name for name, data in fields.items()
            if data.get('required') and not data.get('value')
        ]
        if missing_required:
            critical.append(f"Campos requeridos faltantes: {', '.join(missing_required)}")

        # Errores de tipo críticos
        type_errors = [
            name for name, data in fields.items()
            if data.get('type_error') and data.get('required')
        ]
        if type_errors:
            critical.append(f"Errores de tipo en campos críticos: {', '.join(type_errors)}")

        return critical

    def _store_report(self, report: Dict[str, Any]) -> None:
        """Almacena el reporte en el historial"""
        self.reports_history.append({
            'timestamp': report['metadata']['timestamp'],
            'template': report['metadata']['template'],
            'status': report['summary']['status'],
            'error_count': report['summary']['error_count']
        })

    def get_validation_trends(self) -> Dict[str, Any]:
        """Obtiene tendencias de validación"""
        if not self.reports_history:
            return {'status': 'No hay historial de validaciones'}

        total = len(self.reports_history)
        successful = sum(1 for r in self.reports_history if r['status'] == 'valid')
        
        return {
            'total_validations': total,
            'successful': successful,
            'success_rate': round((successful / total) * 100, 2),
            'average_errors': sum(r['error_count'] for r in self.reports_history) / total
        }
