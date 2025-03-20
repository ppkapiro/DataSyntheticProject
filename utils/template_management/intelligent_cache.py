from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import threading
from .logging_config import setup_logging

class IntelligentCache:
    """Sistema de caché inteligente con autolimpieza"""

    def __init__(self):
        self.logger = setup_logging('intelligent_cache')
        self.cache = {}
        self.access_counts = {}
        self.last_accessed = {}
        self._lock = threading.Lock()
        self.max_size = 1000
        self.cleanup_threshold = 0.8

    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché"""
        with self._lock:
            if key in self.cache:
                self._update_stats(key)
                return self.cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Almacena valor en caché"""
        with self._lock:
            self._check_size()
            self.cache[key] = value
            self.access_counts[key] = 0
            self.last_accessed[key] = datetime.now()

    def _update_stats(self, key: str) -> None:
        """Actualiza estadísticas de uso"""
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        self.last_accessed[key] = datetime.now()

    def _check_size(self) -> None:
        """Verifica y limpia caché si necesario"""
        if len(self.cache) >= self.max_size * self.cleanup_threshold:
            self._cleanup_cache()

    def _cleanup_cache(self) -> None:
        """Limpia entradas menos usadas"""
        entries = [
            (k, self.access_counts[k], self.last_accessed[k])
            for k in self.cache.keys()
        ]
        
        # Ordenar por accesos y última vez usado
        sorted_entries = sorted(
            entries,
            key=lambda x: (x[1], x[2])
        )

        # Eliminar 20% menos usado
        to_remove = sorted_entries[:int(len(sorted_entries) * 0.2)]
        for key, _, _ in to_remove:
            del self.cache[key]
            del self.access_counts[key]
            del self.last_accessed[key]
