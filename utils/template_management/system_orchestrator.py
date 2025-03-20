from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio
from datetime import datetime
from .batch_processor import BatchProcessor
from .content_validator import ContentValidator
from .performance_monitor import PerformanceMonitor
from .error_manager import ErrorManager
from .logging_config import setup_logging

class SystemOrchestrator:
    """Orquestador central del sistema"""

    def __init__(self):
        self.logger = setup_logging('system_orchestrator')
        self.batch_processor = BatchProcessor()
        self.validator = ContentValidator()
        self.monitor = PerformanceMonitor()
        self.error_manager = ErrorManager()
        self.processing_queue = asyncio.Queue()
        self.results_cache = {}
        
    async def process_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un flujo de trabajo completo"""
        self.logger.info("Iniciando flujo de trabajo")
        self.monitor.start_monitoring()

        try:
            # Validar entrada
            if not self._validate_workflow_input(workflow_data):
                raise ValueError("Datos de workflow inválidos")

            # Preparar procesamiento
            tasks = self._prepare_tasks(workflow_data)
            
            # Ejecutar tareas
            results = await self._execute_tasks(tasks)
            
            # Validar resultados
            validated_results = self._validate_results(results)
            
            # Generar reporte
            report = self._generate_workflow_report(validated_results)
            
            self.monitor.stop_monitoring()
            return report

        except Exception as e:
            self.logger.error(f"Error en workflow: {str(e)}")
            return self.error_manager.handle_error(e, workflow_data)

    def _validate_workflow_input(self, data: Dict[str, Any]) -> bool:
        """Valida datos de entrada del workflow"""
        required_fields = ['template_id', 'files', 'config']
        return all(field in data for field in required_fields)

    def _prepare_tasks(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepara tareas para procesamiento"""
        tasks = []
        files = workflow_data.get('files', [])
        template_id = workflow_data.get('template_id')

        for file_batch in self._create_batches(files):
            tasks.append({
                'type': 'batch_processing',
                'files': file_batch,
                'template_id': template_id,
                'config': workflow_data.get('config', {})
            })

        return tasks

    async def _execute_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ejecuta tareas en paralelo"""
        results = []
        
        for task in tasks:
            # Agregar a cola de procesamiento
            await self.processing_queue.put(task)
            
            # Procesar según tipo
            if task['type'] == 'batch_processing':
                result = await self.batch_processor.process_batch(
                    task['files'],
                    task['template_id']
                )
                results.append(result)

        return results

    def _validate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Valida resultados del procesamiento"""
        validated = {
            'successful': [],
            'failed': [],
            'warnings': []
        }

        for result in results:
            if result.get('status') == 'success':
                validated['successful'].append(result)
            else:
                validated['failed'].append(result)
                
            if warnings := result.get('warnings', []):
                validated['warnings'].extend(warnings)

        return validated

    def _generate_workflow_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte del workflow"""
        performance_metrics = self.monitor.get_performance_report()
        
        return {
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'results': {
                'successful': len(results['successful']),
                'failed': len(results['failed']),
                'warnings': len(results['warnings'])
            },
            'performance': {
                'processing_time': performance_metrics['processing_time'],
                'memory_usage': performance_metrics['memory_usage'],
                'cpu_usage': performance_metrics['cpu_usage']
            },
            'details': results
        }

    def _create_batches(self, files: List[Path], 
                       batch_size: int = 50) -> List[List[Path]]:
        """Crea lotes de archivos para procesamiento"""
        return [
            files[i:i + batch_size] 
            for i in range(0, len(files), batch_size)
        ]

    async def get_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del sistema"""
        return {
            'queue_size': self.processing_queue.qsize(),
            'processed_count': len(self.results_cache),
            'monitor_status': self.monitor.get_current_status(),
            'timestamp': datetime.now().isoformat()
        }
