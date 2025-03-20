from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from .pdf_structure_analyzer import PDFStructureAnalyzer
from .field_reconciliation import FieldReconciliation
from .content_validator import ContentValidator
from .validation_reporter import ValidationReporter
from .conflict_resolver import ConflictResolver
from .state_synchronizer import StateSynchronizer
from .logging_config import setup_logging

class ProcessingCoordinator:
    """Coordinador central del sistema de procesamiento"""

    def __init__(self):
        self.logger = setup_logging('processing_coordinator')
        self.structure_analyzer = PDFStructureAnalyzer()
        self.field_reconciliation = FieldReconciliation()
        self.content_validator = ContentValidator()
        self.validation_reporter = ValidationReporter()
        self.conflict_resolver = ConflictResolver()
        self.state_sync = StateSynchronizer()
        self.processing_history = []

    def process_document(self, pdf_path: Path, 
                        template_id: str) -> Dict[str, Any]:
        """Procesa un documento PDF usando una plantilla específica"""
        self.logger.info(f"Iniciando procesamiento de {pdf_path}")
        
        try:
            # 1. Analizar estructura PDF
            structure = self.structure_analyzer.analyze_document_structure(
                pdf_path
            )

            # 2. Cargar y validar plantilla
            template = self._load_template(template_id)
            if not template:
                return {'error': 'Plantilla no encontrada'}

            # 3. Reconciliar campos
            reconciled = self.field_reconciliation.reconcile_fields(
                structure,
                template
            )

            # 4. Resolver conflictos
            resolved = self.conflict_resolver.resolve_conflicts(
                reconciled['reconciled_fields'],
                template
            )

            # 5. Validar contenido
            validation = self.content_validator.validate_content(
                resolved['resolved_data'],
                template
            )

            # 6. Generar reporte
            report = self.validation_reporter.generate_report(
                resolved['resolved_data'],
                template
            )

            # 7. Sincronizar estado
            self.state_sync.update_state('document_processing', {
                'pdf_path': str(pdf_path),
                'template_id': template_id,
                'status': 'completed'
            })

            # 8. Generar resultado final
            result = self._generate_final_result(
                structure,
                reconciled,
                resolved,
                validation,
                report
            )

            # 9. Registrar procesamiento
            self._register_processing(result)

            return result

        except Exception as e:
            self.logger.error(f"Error en procesamiento: {str(e)}")
            return {'error': str(e)}

    def _load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Carga y verifica una plantilla"""
        try:
            # Implementar carga de plantilla según sistema existente
            return {}
        except Exception as e:
            self.logger.error(f"Error cargando plantilla: {str(e)}")
            return None

    def _generate_final_result(self, structure: Dict[str, Any],
                             reconciled: Dict[str, Any],
                             resolved: Dict[str, Any],
                             validation: Dict[str, Any],
                             report: Dict[str, Any]) -> Dict[str, Any]:
        """Genera resultado final del procesamiento"""
        return {
            'structure_analysis': {
                'sections': structure.get('sections', []),
                'metadata': structure.get('metadata', {})
            },
            'field_mapping': {
                'fields': resolved.get('resolved_data', {}),
                'stats': reconciled.get('stats', {})
            },
            'validation': {
                'is_valid': validation.get('is_valid', False),
                'errors': validation.get('errors', []),
                'report': report.get('summary', {})
            },
            'processing_info': {
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'quality_score': report.get('quality_metrics', {}).get('overall_score', 0)
            }
        }

    def _register_processing(self, result: Dict[str, Any]) -> None:
        """Registra un procesamiento completado"""
        self.processing_history.append({
            'timestamp': result['processing_info']['timestamp'],
            'status': result['processing_info']['status'],
            'quality_score': result['processing_info']['quality_score']
        })

    def get_processing_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de procesamiento"""
        if not self.processing_history:
            return {'status': 'No hay historial de procesamiento'}

        total = len(self.processing_history)
        successful = sum(
            1 for p in self.processing_history 
            if p['status'] == 'success'
        )
        
        return {
            'total_processed': total,
            'successful': successful,
            'success_rate': round((successful / total) * 100, 2),
            'average_quality': sum(
                p['quality_score'] for p in self.processing_history
            ) / total
        }
