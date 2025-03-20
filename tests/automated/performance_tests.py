from typing import Dict, Any, List
from pathlib import Path
import unittest
import time
import psutil
import json
from datetime import datetime
from ...utils.template_management.processing_coordinator import ProcessingCoordinator
from ...utils.template_management.performance_monitor import PerformanceMonitor
from ...utils.template_management.logging_config import setup_logging

class PerformanceTests(unittest.TestCase):
    """Pruebas de rendimiento del sistema"""

    def setUp(self):
        self.logger = setup_logging('performance_tests')
        self.coordinator = ProcessingCoordinator()
        self.monitor = PerformanceMonitor()
        self.test_data_path = Path(__file__).parent / 'test_data' / 'performance'
        self.performance_metrics = []

    def test_processing_time(self):
        """Prueba tiempos de procesamiento"""
        test_files = self._load_test_files('processing')
        self.monitor.start_monitoring()

        for test_file in test_files:
            with self.subTest(file=test_file['name']):
                start_time = time.time()
                result = self.coordinator.process_document(
                    test_file['pdf_path'],
                    test_file['template_id']
                )
                processing_time = time.time() - start_time

                self._record_metric('processing_time', {
                    'file': test_file['name'],
                    'time': processing_time,
                    'success': 'error' not in result
                })

                self.assertLess(processing_time, 5.0)  # Max 5 segundos

    def test_memory_usage(self):
        """Prueba uso de memoria"""
        large_files = self._load_test_files('memory')
        initial_memory = psutil.Process().memory_info().rss

        for test_file in large_files:
            with self.subTest(file=test_file['name']):
                before_mem = psutil.Process().memory_info().rss
                result = self.coordinator.process_document(
                    test_file['pdf_path'],
                    test_file['template_id']
                )
                after_mem = psutil.Process().memory_info().rss
                
                memory_used = after_mem - before_mem
                self._record_metric('memory_usage', {
                    'file': test_file['name'],
                    'memory_mb': memory_used / (1024 * 1024),
                    'success': 'error' not in result
                })

                self.assertLess(memory_used, 500 * 1024 * 1024)  # Max 500MB

    def test_concurrent_processing(self):
        """Prueba procesamiento concurrente"""
        import threading
        test_batch = self._load_test_files('concurrent')
        results = []
        threads = []

        start_time = time.time()

        for test_file in test_batch:
            thread = threading.Thread(
                target=self._process_in_thread,
                args=(test_file, results)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        total_time = time.time() - start_time
        
        self._record_metric('concurrent_processing', {
            'total_files': len(test_batch),
            'total_time': total_time,
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success'])
        })

        self.assertLess(total_time, len(test_batch) * 2)  # Max 2s por archivo

    def test_load_handling(self):
        """Prueba manejo de carga"""
        iterations = 50  # Número de iteraciones
        test_file = self._load_test_files('load')[0]
        timings = []

        for i in range(iterations):
            start_time = time.time()
            result = self.coordinator.process_document(
                test_file['pdf_path'],
                test_file['template_id']
            )
            processing_time = time.time() - start_time
            timings.append(processing_time)

        avg_time = sum(timings) / len(timings)
        max_time = max(timings)
        min_time = min(timings)

        self._record_metric('load_handling', {
            'iterations': iterations,
            'avg_time': avg_time,
            'max_time': max_time,
            'min_time': min_time,
            'std_dev': self._calculate_std_dev(timings, avg_time)
        })

        self.assertLess(avg_time, 1.0)  # Promedio < 1s
        self.assertLess(max_time, 2.0)  # Máximo < 2s

    def _process_in_thread(self, test_file: Dict[str, Any], 
                          results: List[Dict[str, Any]]) -> None:
        """Procesa documento en un thread"""
        try:
            result = self.coordinator.process_document(
                test_file['pdf_path'],
                test_file['template_id']
            )
            results.append({
                'file': test_file['name'],
                'success': 'error' not in result
            })
        except Exception as e:
            results.append({
                'file': test_file['name'],
                'success': False,
                'error': str(e)
            })

    def _calculate_std_dev(self, values: List[float], mean: float) -> float:
        """Calcula desviación estándar"""
        return (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5

    def _record_metric(self, test_type: str, data: Dict[str, Any]) -> None:
        """Registra métrica de rendimiento"""
        self.performance_metrics.append({
            'timestamp': datetime.now().isoformat(),
            'type': test_type,
            'data': data
        })

    def tearDown(self):
        """Finaliza monitoreo y guarda resultados"""
        if hasattr(self, 'monitor'):
            report = self.monitor.stop_monitoring()
            self.performance_metrics.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'system_metrics',
                'data': report
            })

        if self.performance_metrics:
            output_path = self.test_data_path / 'results'
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = output_path / f'performance_results_{timestamp}.json'
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metrics': self.performance_metrics,
                    'summary': {
                        'total_tests': len(self.performance_metrics),
                        'timestamp': datetime.now().isoformat()
                    }
                }, f, indent=2, ensure_ascii=False)
