from typing import Dict, Any, List
from pathlib import Path
import asyncio
from .logging_config import setup_logging
from .performance_monitor import PerformanceMonitor

class BatchProcessor:
    """Procesador de documentos en lote"""

    def __init__(self):
        self.logger = setup_logging('batch_processor')
        self.monitor = PerformanceMonitor()
        self.batch_size = 50
        self.results = []

    async def process_batch(self, files: List[Path], template_id: str) -> Dict[str, Any]:
        """Procesa un lote de documentos"""
        self.logger.info(f"Procesando lote de {len(files)} archivos")
        self.monitor.start_monitoring()

        tasks = [self._process_file(file, template_id) for file in files]
        results = await asyncio.gather(*tasks)
        
        stats = self._generate_batch_stats(results)
        self.monitor.stop_monitoring()
        
        return {
            'processed': len(results),
            'successful': stats['successful'],
            'failed': stats['failed'],
            'results': results,
            'stats': stats
        }

    async def _process_file(self, file: Path, template_id: str) -> Dict[str, Any]:
        """Procesa un archivo individual"""
        try:
            # Procesamiento asíncrono
            return {
                'file': str(file),
                'status': 'success',
                'template': template_id,
                'timestamp': self.monitor.get_timestamp()
            }
        except Exception as e:
            self.logger.error(f"Error procesando {file}: {str(e)}")
            return {'file': str(file), 'error': str(e)}

    def _generate_batch_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera estadísticas del lote"""
        return {
            'successful': sum(1 for r in results if 'error' not in r),
            'failed': sum(1 for r in results if 'error' in r),
            'total_time': self.monitor.get_total_time()
        }
