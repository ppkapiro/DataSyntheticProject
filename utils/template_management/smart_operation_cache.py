from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import threading
from .logging_config import setup_logging

class SmartOperationCache:
    """Sistema de caché inteligente para operaciones frecuentes"""
    
    def __init__(self):
        self.logger = setup_logging('smart_cache')
        self.cache = {}
        self.metrics = {}
        self._lock = threading.Lock()
        self.max_entries = 1000
        self.default_ttl = 3600  # 1 hora

    def get_operation_result(self, operation_id: str, params: Dict[str, Any]) -> Optional[Any]:
        """Obtiene resultado cacheado de una operación"""
        cache_key = self._generate_key(operation_id, params)
        with self._lock:
            if cached := self.cache.get(cache_key):
                if not self._is_expired(cached['timestamp']):
                    self._update_metrics(cache_key, 'hit')
                    return cached['value']
                self._remove_entry(cache_key)
        return None

    def store_operation_result(self, operation_id: str, params: Dict[str, Any], 
                             result: Any, ttl: Optional[int] = None) -> None:
        """Almacena resultado de operación"""
        cache_key = self._generate_key(operation_id, params)
        with self._lock:
            self._cleanup_if_needed()
            self.cache[cache_key] = {
                'value': result,
                'timestamp': datetime.now(),
                'ttl': ttl or self.default_ttl
            }
            self._update_metrics(cache_key, 'store')

    def _generate_key(self, operation_id: str, params: Dict[str, Any]) -> str:
        """Genera clave única para operación"""
        param_str = str(sorted(params.items()))
        return f"{operation_id}:{hash(param_str)}"

    def _is_expired(self, timestamp: datetime) -> bool:
        """Verifica si una entrada está expirada"""
        return datetime.now() - timestamp > timedelta(seconds=self.default_ttl)

    def _cleanup_if_needed(self) -> None:
        """Limpia caché si es necesario"""
        if len(self.cache) >= self.max_entries:
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: self.metrics.get(x[0], {}).get('hits', 0)
            )
            for key, _ in sorted_entries[:int(len(self.cache) * 0.2)]:
                self._remove_entry(key)

    def _remove_entry(self, key: str) -> None:
        """Elimina entrada del caché"""
        self.cache.pop(key, None)
        self.metrics.pop(key, None)

    def _update_metrics(self, key: str, action: str) -> None:
        """Actualiza métricas de uso"""
        if key not in self.metrics:
            self.metrics[key] = {'hits': 0, 'stores': 0}
        if action == 'hit':
            self.metrics[key]['hits'] += 1
        elif action == 'store':
            self.metrics[key]['stores'] += 1
