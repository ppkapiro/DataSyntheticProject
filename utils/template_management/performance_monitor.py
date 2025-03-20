from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import psutil
import threading
from .logging_config import setup_logging

class PerformanceMonitor:
    """Sistema de monitoreo y análisis de rendimiento"""

    def __init__(self):
        self.logger = setup_logging('performance_monitor')
        self.metrics = {
            'processing_time': [],
            'memory_usage': [],
            'cpu_usage': [],
            'operation_counts': {}
        }
        self.monitoring = False
        self.monitor_thread = None
        self._lock = threading.Lock()

    def start_monitoring(self) -> None:
        """Inicia el monitoreo de rendimiento"""
        self.logger.info("Iniciando monitoreo de rendimiento")
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.start()

    def stop_monitoring(self) -> Dict[str, Any]:
        """Detiene el monitoreo y retorna resultados"""
        self.logger.info("Deteniendo monitoreo")
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        return self.get_performance_report()

    def track_operation(self, operation_name: str) -> callable:
        """Decorador para trackear operaciones"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss

                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    memory_used = psutil.Process().memory_info().rss - start_memory

                    self._record_operation_metrics(
                        operation_name,
                        execution_time,
                        memory_used
                    )

                    return result

                except Exception as e:
                    self.logger.error(f"Error en operación {operation_name}: {str(e)}")
                    raise

            return wrapper
        return decorator

    def _monitor_resources(self) -> None:
        """Monitorea recursos del sistema"""
        while self.monitoring:
            try:
                with self._lock:
                    self.metrics['cpu_usage'].append({
                        'timestamp': datetime.now().isoformat(),
                        'value': psutil.cpu_percent()
                    })
                    self.metrics['memory_usage'].append({
                        'timestamp': datetime.now().isoformat(),
                        'value': psutil.Process().memory_info().rss
                    })
                time.sleep(1)  # Intervalo de monitoreo
            except Exception as e:
                self.logger.error(f"Error en monitoreo: {str(e)}")

    def _record_operation_metrics(self, operation: str, 
                                execution_time: float,
                                memory_used: int) -> None:
        """Registra métricas de una operación"""
        with self._lock:
            if operation not in self.metrics['operation_counts']:
                self.metrics['operation_counts'][operation] = {
                    'count': 0,
                    'total_time': 0,
                    'total_memory': 0,
                    'avg_time': 0,
                    'avg_memory': 0,
                    'history': []
                }

            stats = self.metrics['operation_counts'][operation]
            stats['count'] += 1
            stats['total_time'] += execution_time
            stats['total_memory'] += memory_used
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['avg_memory'] = stats['total_memory'] / stats['count']
            
            stats['history'].append({
                'timestamp': datetime.now().isoformat(),
                'execution_time': execution_time,
                'memory_used': memory_used
            })

    def get_performance_report(self) -> Dict[str, Any]:
        """Genera reporte de rendimiento"""
        with self._lock:
            report = {
                'system_metrics': {
                    'cpu_usage': self._calculate_cpu_stats(),
                    'memory_usage': self._calculate_memory_stats()
                },
                'operations': self._calculate_operation_stats(),
                'summary': self._generate_performance_summary(),
                'recommendations': self._generate_recommendations()
            }

        return report

    def _calculate_cpu_stats(self) -> Dict[str, float]:
        """Calcula estadísticas de CPU"""
        if not self.metrics['cpu_usage']:
            return {'error': 'No hay datos de CPU'}

        cpu_values = [m['value'] for m in self.metrics['cpu_usage']]
        return {
            'average': sum(cpu_values) / len(cpu_values),
            'max': max(cpu_values),
            'min': min(cpu_values)
        }

    def _calculate_memory_stats(self) -> Dict[str, int]:
        """Calcula estadísticas de memoria"""
        if not self.metrics['memory_usage']:
            return {'error': 'No hay datos de memoria'}

        memory_values = [m['value'] for m in self.metrics['memory_usage']]
        return {
            'average': sum(memory_values) / len(memory_values),
            'peak': max(memory_values),
            'baseline': min(memory_values)
        }

    def _calculate_operation_stats(self) -> Dict[str, Any]:
        """Calcula estadísticas por operación"""
        return {
            name: {
                'calls': stats['count'],
                'avg_time': stats['avg_time'],
                'avg_memory': stats['avg_memory'],
                'total_time': stats['total_time']
            }
            for name, stats in self.metrics['operation_counts'].items()
        }

    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Genera resumen de rendimiento"""
        return {
            'total_operations': sum(
                stats['count'] 
                for stats in self.metrics['operation_counts'].values()
            ),
            'total_processing_time': sum(
                stats['total_time'] 
                for stats in self.metrics['operation_counts'].values()
            ),
            'avg_operation_time': sum(
                stats['avg_time'] 
                for stats in self.metrics['operation_counts'].values()
            ) / len(self.metrics['operation_counts']) if self.metrics['operation_counts'] else 0
        }

    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones de optimización"""
        recommendations = []
        
        # Analizar tiempos de operación
        for op_name, stats in self.metrics['operation_counts'].items():
            if stats['avg_time'] > 1.0:  # Umbral de 1 segundo
                recommendations.append(
                    f"Optimizar operación {op_name}: tiempo promedio > 1s"
                )

        # Analizar uso de memoria
        memory_stats = self._calculate_memory_stats()
        if isinstance(memory_stats, dict) and 'peak' in memory_stats:
            if memory_stats['peak'] > 500 * 1024 * 1024:  # 500MB
                recommendations.append(
                    "Alto uso de memoria: considerar optimización"
                )

        return recommendations
