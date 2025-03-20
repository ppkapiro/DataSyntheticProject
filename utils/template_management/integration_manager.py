from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from .pdf_structure_analyzer import PDFStructureAnalyzer
from .field_reconciliation import FieldReconciliation
from .content_validator import ContentValidator
from .mapping_quality_detector import MappingQualityDetector
from .logging_config import setup_logging

class IntegrationManager:
    """Gestor de integración entre componentes del sistema"""

    def __init__(self):
        self.logger = setup_logging('integration_manager')
        self.structure_analyzer = PDFStructureAnalyzer()
        self.field_reconciliation = FieldReconciliation()
        self.content_validator = ContentValidator()
        self.quality_detector = MappingQualityDetector()
        self.processing_history = []

    def process_document(self, pdf_content: Dict[str, Any], 
                        template: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un documento a través de todo el sistema"""
        self.logger.info("Iniciando procesamiento integrado")
        
        try:
            # 1. Analizar estructura del PDF
            structure_analysis = self.structure_analyzer.analyze_document_structure(
                pdf_content.get('raw_text', '')
            )

            # 2. Reconciliar campos
            reconciled_fields = self.field_reconciliation.reconcile_fields(
                structure_analysis['sections'],
                template.get('campos', {})
            )

            # 3. Validar contenido
            validation_result = self.content_validator.validate_content(
                reconciled_fields['reconciled_fields'],
                template
            )

            # 4. Evaluar calidad
            quality_assessment = self.quality_detector.analyze_mapping_quality(
                reconciled_fields['reconciled_fields'],
                template
            )

            # Generar resultado final
            result = self._generate_final_result(
                structure_analysis,
                reconciled_fields,
                validation_result,
                quality_assessment
            )

            # Registrar procesamiento
            self._register_processing(result)
            
            return result

        except Exception as e:
            self.logger.error(f"Error en procesamiento: {str(e)}")
            return {'error': str(e)}

    def _generate_final_result(self, 
                             structure: Dict[str, Any],
                             reconciliation: Dict[str, Any],
                             validation: Dict[str, Any],
                             quality: Dict[str, Any]) -> Dict[str, Any]:
        """Genera resultado final consolidado"""
        return {
            'document_analysis': {
                'structure': structure.get('sections', []),
                'metadata': structure.get('metadata', {})
            },
            'field_mapping': {
                'fields': reconciliation.get('reconciled_fields', {}),
                'stats': reconciliation.get('stats', {})
            },
            'validation': {
                'is_valid': validation.get('is_valid', False),
                'errors': validation.get('errors', []),
                'warnings': validation.get('warnings', [])
            },
            'quality_metrics': {
                'overall_quality': quality.get('overall_quality', 0.0),
                'field_quality': quality.get('field_quality', {}),
                'recommendations': quality.get('recommendations', [])
            },
            'processing_info': {
                'timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'success': True
            }
        }

    def _register_processing(self, result: Dict[str, Any]) -> None:
        """Registra el procesamiento realizado"""
        processing_record = {
            'timestamp': result['processing_info']['timestamp'],
            'status': result['processing_info']['status'],
            'quality_score': result['quality_metrics']['overall_quality'],
            'validation_status': result['validation']['is_valid']
        }
        
        self.processing_history.append(processing_record)
        self.logger.info(f"Procesamiento registrado: {processing_record}")

    def get_processing_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de procesamiento"""
        if not self.processing_history:
            return {'status': 'No hay registros de procesamiento'}

        total = len(self.processing_history)
        successful = sum(
            1 for record in self.processing_history 
            if record['status'] == 'completed'
        )
        
        return {
            'total_processed': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': round((successful / total) * 100, 2),
            'average_quality': self._calculate_average_quality()
        }

    def _calculate_average_quality(self) -> float:
        """Calcula la calidad promedio de procesamientos"""
        if not self.processing_history:
            return 0.0
            
        quality_scores = [
            record['quality_score'] 
            for record in self.processing_history
        ]
        
        return round(sum(quality_scores) / len(quality_scores), 2)
