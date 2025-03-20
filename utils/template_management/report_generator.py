from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
from .logging_config import setup_logging
from .validation_pipeline import ValidationPipeline
from .performance_monitor import PerformanceMonitor

class ReportGenerator:
    """Generador de reportes del sistema"""

    def __init__(self):
        self.logger = setup_logging('report_generator')
        self.validation_pipeline = ValidationPipeline()
        self.performance_monitor = PerformanceMonitor()
        self.report_history = []
        self.report_types = {
            'validation': self._generate_validation_report,
            'performance': self._generate_performance_report,
            'error': self._generate_error_report,
            'summary': self._generate_summary_report
        }

    def generate_report(self, data: Dict[str, Any], 
                       report_type: str = 'summary') -> Dict[str, Any]:
        """Genera un reporte según el tipo especificado"""
        self.logger.info(f"Generando reporte tipo: {report_type}")
        
        try:
            if generator := self.report_types.get(report_type):
                report = generator(data)
                self._record_report_generation(report_type, report)
                return report
            else:
                raise ValueError(f"Tipo de reporte no soportado: {report_type}")

        except Exception as e:
            self.logger.error(f"Error generando reporte: {str(e)}")
            return {
                'error': str(e),
                'type': report_type,
                'timestamp': datetime.now().isoformat()
            }

    def _generate_validation_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de validación"""
        validation_result = self.validation_pipeline.run_validation(
            data.get('content', {}),
            data.get('template', {})
        )

        return {
            'validation_status': validation_result['is_valid'],
            'fields_analyzed': len(data.get('content', {})),
            'error_count': len(validation_result['errors']),
            'warning_count': len(validation_result['warnings']),
            'validation_details': validation_result['stages'],
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'report_type': 'validation'
            }
        }

    def _generate_performance_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de rendimiento"""
        performance_metrics = self.performance_monitor.get_performance_report()

        return {
            'processing_time': performance_metrics['processing_time'],
            'memory_usage': performance_metrics['memory_usage'],
            'operation_counts': performance_metrics['operation_counts'],
            'recommendations': self._generate_performance_recommendations(
                performance_metrics
            ),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'report_type': 'performance'
            }
        }

    def _generate_error_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de errores"""
        errors = data.get('errors', [])
        categorized_errors = self._categorize_errors(errors)

        return {
            'error_count': len(errors),
            'error_categories': categorized_errors,
            'critical_errors': self._identify_critical_errors(errors),
            'recommendations': self._generate_error_recommendations(
                categorized_errors
            ),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'report_type': 'error'
            }
        }

    def _generate_summary_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte resumido"""
        return {
            'validation_summary': self._generate_validation_summary(data),
            'performance_metrics': self._generate_performance_summary(data),
            'error_overview': self._generate_error_summary(data),
            'recommendations': self._generate_general_recommendations(data),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'report_type': 'summary'
            }
        }

    def _categorize_errors(self, errors: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categoriza errores por tipo"""
        categories = {
            'validation': [],
            'processing': [],
            'system': []
        }

        for error in errors:
            error_type = error.get('type', 'unknown')
            if 'validation' in error_type.lower():
                categories['validation'].append(error)
            elif 'process' in error_type.lower():
                categories['processing'].append(error)
            else:
                categories['system'].append(error)

        return categories

    def save_report(self, report: Dict[str, Any], 
                   output_path: Optional[Path] = None) -> None:
        """Guarda el reporte en disco"""
        if not output_path:
            output_path = Path('reports')
        
        output_path.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = output_path / f'report_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def _record_report_generation(self, report_type: str, 
                                report: Dict[str, Any]) -> None:
        """Registra generación de reporte"""
        self.report_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': report_type,
            'success': 'error' not in report
        })

    def get_report_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de generación de reportes"""
        if not self.report_history:
            return {'status': 'No hay historial de reportes'}

        total = len(self.report_history)
        successful = sum(1 for r in self.report_history if r['success'])
        
        return {
            'total_reports': total,
            'successful': successful,
            'success_rate': round((successful / total) * 100, 2),
            'by_type': self._calculate_type_stats()
        }

    def _calculate_type_stats(self) -> Dict[str, int]:
        """Calcula estadísticas por tipo de reporte"""
        stats = {}
        for report in self.report_history:
            report_type = report['type']
            if report_type not in stats:
                stats[report_type] = 0
            stats[report_type] += 1
        return stats
