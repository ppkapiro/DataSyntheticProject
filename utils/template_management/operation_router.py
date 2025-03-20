from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from .integration_manager import IntegrationManager
from .pdf_structure_analyzer import PDFStructureAnalyzer
from .content_validator import ContentValidator
from .logging_config import setup_logging

class OperationRouter:
    """Enrutador central de operaciones del sistema"""

    def __init__(self):
        self.logger = setup_logging('operation_router')
        self.integration_manager = IntegrationManager()
        self.structure_analyzer = PDFStructureAnalyzer()
        self.content_validator = ContentValidator()
        self.operation_history = []

    def route_operation(self, operation_type: str, 
                       data: Dict[str, Any]) -> Dict[str, Any]:
        """Enruta y ejecuta operaciones del sistema"""
        self.logger.info(f"Enrutando operación: {operation_type}")
        
        operations = {
            'analyze_pdf': self._handle_pdf_analysis,
            'validate_content': self._handle_validation,
            'process_document': self._handle_processing,
            'export_results': self._handle_export
        }

        if handler := operations.get(operation_type):
            try:
                result = handler(data)
                self._record_operation(operation_type, result)
                return result
            except Exception as e:
                error = self._handle_error(e, operation_type)
                self._record_operation(operation_type, error)
                return error
        else:
            return {'error': f'Operación no soportada: {operation_type}'}

    def _handle_pdf_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja análisis de PDF"""
        if not data.get('pdf_content'):
            return {'error': 'Contenido PDF requerido'}
            
        return self.structure_analyzer.analyze_document_structure(
            data['pdf_content']
        )

    def _handle_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja validación de contenido"""
        if not all(k in data for k in ['content', 'template']):
            return {'error': 'Contenido y plantilla requeridos'}
            
        return self.content_validator.validate_content(
            data['content'],
            data['template']
        )

    def _handle_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja procesamiento completo"""
        if not all(k in data for k in ['pdf_content', 'template']):
            return {'error': 'Contenido PDF y plantilla requeridos'}
            
        return self.integration_manager.process_document(
            data['pdf_content'],
            data['template']
        )

    def _handle_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja exportación de resultados"""
        if not data.get('processed_data'):
            return {'error': 'Datos procesados requeridos'}
            
        return self._export_results(data['processed_data'])

    def _handle_error(self, error: Exception, 
                     operation: str) -> Dict[str, Any]:
        """Maneja errores de operación"""
        self.logger.error(f"Error en {operation}: {str(error)}")
        
        return {
            'error': str(error),
            'operation': operation,
            'timestamp': datetime.now().isoformat()
        }

    def _record_operation(self, operation_type: str, 
                         result: Dict[str, Any]) -> None:
        """Registra una operación realizada"""
        record = {
            'operation': operation_type,
            'timestamp': datetime.now().isoformat(),
            'success': 'error' not in result,
            'error': result.get('error')
        }
        
        self.operation_history.append(record)
        self.logger.info(f"Operación registrada: {record}")

    def _export_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Exporta resultados procesados"""
        try:
            export_data = {
                'data': data,
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'format_version': '1.0'
                }
            }
            
            return export_data
            
        except Exception as e:
            return {'error': f'Error en exportación: {str(e)}'}

    def get_operation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de operaciones"""
        if not self.operation_history:
            return {'status': 'No hay operaciones registradas'}

        stats = {
            'total_operations': len(self.operation_history),
            'successful': sum(1 for op in self.operation_history if op['success']),
            'by_type': {}
        }
        
        for op in self.operation_history:
            op_type = op['operation']
            if op_type not in stats['by_type']:
                stats['by_type'][op_type] = {
                    'total': 0,
                    'successful': 0
                }
            
            stats['by_type'][op_type]['total'] += 1
            if op['success']:
                stats['by_type'][op_type]['successful'] += 1

        return stats
