from typing import Dict, Any, List, Optional
from datetime import datetime
import psutil
import time
from .logging_config import setup_logging
from .performance_monitor import PerformanceMonitor

class PerformanceOptimizer:
    """Sistema de optimización de rendimiento"""

    def __init__(self):
        self.logger = setup_logging('performance_optimizer')
        self.monitor = PerformanceMonitor()
        self.optimization_history = []
        self.cache = {}
        self.optimization_thresholds = {
            'memory_high': 500 * 1024 * 1024,  # 500MB
            'cpu_high': 80.0,  # 80%
            'processing_time_limit': 5.0  # 5 segundos
        }

    def optimize_operation(self, operation_name: str, 
                         operation_func: callable, *args, **kwargs) -> Any:
        """Ejecuta y optimiza una operación"""
        self.logger.info(f"Optimizando operación: {operation_name}")
        
        try:
            # Verificar caché
            cache_key = self._generate_cache_key(operation_name, args, kwargs)
            if cached := self._get_from_cache(cache_key):
                return cached

            # Monitorear rendimiento
            self.monitor.start_monitoring()
            
            # Ejecutar operación
            start_time = time.time()
            result = operation_func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Detener monitoreo
            performance_data = self.monitor.stop_monitoring()
            
            # Analizar y optimizar
            optimizations = self._analyze_and_optimize(
                operation_name,
                execution_time,
                performance_data
            )

            # Guardar en caché si es apropiado
            if self._should_cache(execution_time, performance_data):
                self._store_in_cache(cache_key, result)

            # Registrar métricas
            self._record_optimization(
                operation_name,
                execution_time,
                performance_data,
                optimizations
            )

            return result

        except Exception as e:
            self.logger.error(f"Error en optimización: {str(e)}")
            return operation_func(*args, **kwargs)  # Fallback a operación normal

    def _analyze_and_optimize(self, operation_name: str, 
                            execution_time: float,
                            performance_data: Dict[str, Any]) -> List[str]:
        """Analiza rendimiento y sugiere optimizaciones"""
        optimizations = []
        
        # Analizar tiempo de ejecución
        if execution_time > self.optimization_thresholds['processing_time_limit']:
            optimizations.append({
                'type': 'processing_time',
                'message': f'Tiempo de ejecución alto: {execution_time:.2f}s',
                'suggestion': 'Considerar implementar caché'
            })

        # Analizar uso de memoria
        if mem_usage := performance_data.get('memory_usage', 0):
            if mem_usage > self.optimization_thresholds['memory_high']:
                optimizations.append({
                    'type': 'memory_usage',
                    'message': f'Alto uso de memoria: {mem_usage/1024/1024:.2f}MB',
                    'suggestion': 'Implementar limpieza de memoria'
                })

        # Analizar uso de CPU
        if cpu_usage := performance_data.get('cpu_usage', 0):
            if cpu_usage > self.optimization_thresholds['cpu_high']:
                optimizations.append({
                    'type': 'cpu_usage',
                    'message': f'Alto uso de CPU: {cpu_usage:.2f}%',
                    'suggestion': 'Considerar procesamiento por lotes'
                })

        return optimizations

    def _generate_cache_key(self, operation_name: str, 
                          args: tuple, kwargs: dict) -> str:
        """Genera clave de caché para una operación"""
        return f"{operation_name}:{hash(str(args))}-{hash(str(kwargs))}"

    def _should_cache(self, execution_time: float, 
                     performance_data: Dict[str, Any]) -> bool:
        """Determina si una operación debe ser cacheada"""
        return (
            execution_time > 1.0 or  # Más de 1 segundo
            performance_data.get('memory_usage', 0) > 100 * 1024 * 1024  # 100MB
        )

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Obtiene resultado desde caché"""
        if cache_key in self.cache:
            self.logger.info(f"Caché hit: {cache_key}")
            return self.cache[cache_key]['value']
        return None

    def _store_in_cache(self, cache_key: str, value: Any) -> None:
        """Almacena resultado en caché"""
        self.cache[cache_key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        self._cleanup_cache()

    def _cleanup_cache(self) -> None:
        """Limpia entradas antiguas del caché"""
        if len(self.cache) > 1000:  # Máximo 1000 entradas
            # Eliminar 20% más antiguo
            sorted_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k]['timestamp']
            )
            for key in sorted_keys[:200]:
                del self.cache[key]

    def _record_optimization(self, operation_name: str,
                           execution_time: float,
                           performance_data: Dict[str, Any],
                           optimizations: List[Dict[str, Any]]) -> None:
        """Registra métricas de optimización"""
        self.optimization_history.append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation_name,
            'execution_time': execution_time,
            'performance_data': performance_data,
            'optimizations': optimizations
        })

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de optimización"""
        if not self.optimization_history:
            return {'status': 'No hay historial de optimizaciones'}

        stats = {
            'total_operations': len(self.optimization_history),
            'avg_execution_time': 0.0,
            'cache_size': len(self.cache),
            'optimization_counts': {}
        }

        # Calcular estadísticas
        total_time = 0.0
        for record in self.optimization_history:
            total_time += record['execution_time']
            for opt in record['optimizations']:
                opt_type = opt['type']
                if opt_type not in stats['optimization_counts']:
                    stats['optimization_counts'][opt_type] = 0
                stats['optimization_counts'][opt_type] += 1

        stats['avg_execution_time'] = total_time / len(self.optimization_history)
        
        return stats
