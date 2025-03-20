from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import yaml
import sqlite3
from datetime import datetime
import threading
from .logging_config import setup_logging

class StorageManager:
    """Gestor de almacenamiento para plantillas"""

    def __init__(self, base_dir: Path = None):
        self.logger = setup_logging()
        self.base_dir = base_dir or Path("storage")
        self.cache = {}
        self.cache_lock = threading.Lock()
        self._init_storage()

    def _init_storage(self):
        """Inicializa la estructura de almacenamiento"""
        # Crear directorios necesarios
        (self.base_dir / "templates").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "backups").mkdir(exist_ok=True)
        (self.base_dir / "indexes").mkdir(exist_ok=True)

        # Inicializar base de datos SQLite para índices
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos SQLite"""
        db_path = self.base_dir / "indexes" / "template_index.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    tags TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_template_name 
                ON templates(name)
            """)

    def store(self, template_id: str, data: Dict[str, Any], format: str = 'json') -> bool:
        """Almacena una plantilla en el sistema de archivos"""
        try:
            # Determinar ruta de almacenamiento
            file_path = self._get_storage_path(template_id, format)
            
            # Guardar archivo
            self._save_file(file_path, data, format)
            
            # Actualizar índice
            self._update_index(template_id, data)
            
            # Actualizar caché
            with self.cache_lock:
                self.cache[template_id] = {
                    'data': data,
                    'timestamp': datetime.now().timestamp()
                }

            self.logger.info(f"Plantilla almacenada: {template_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error almacenando plantilla {template_id}: {str(e)}")
            return False

    def retrieve(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Recupera una plantilla del almacenamiento"""
        # Verificar caché
        with self.cache_lock:
            if template_id in self.cache:
                return self.cache[template_id]['data']

        # Buscar en almacenamiento
        file_path = self._get_storage_path(template_id)
        if not file_path.exists():
            return None

        try:
            data = self._load_file(file_path)
            
            # Actualizar caché
            with self.cache_lock:
                self.cache[template_id] = {
                    'data': data,
                    'timestamp': datetime.now().timestamp()
                }
            
            return data
        except Exception as e:
            self.logger.error(f"Error recuperando plantilla {template_id}: {str(e)}")
            return None

    def _get_storage_path(self, template_id: str, format: str = 'json') -> Path:
        """Obtiene la ruta de almacenamiento para una plantilla"""
        return self.base_dir / "templates" / f"{template_id}.{format}"

    def _save_file(self, path: Path, data: Dict[str, Any], format: str):
        """Guarda datos en un archivo"""
        with open(path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'yaml':
                yaml.dump(data, f, allow_unicode=True)

    def _load_file(self, path: Path) -> Dict[str, Any]:
        """Carga datos desde un archivo"""
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix == '.json':
                return json.load(f)
            elif path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)

    def _update_index(self, template_id: str, data: Dict[str, Any]):
        """Actualiza el índice de la plantilla"""
        db_path = self.base_dir / "indexes" / "template_index.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO templates 
                (id, name, created_at, updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                template_id,
                data.get('name', ''),
                data.get('created_at', ''),
                data.get('updated_at', ''),
                json.dumps(data.get('tags', [])),
                json.dumps(data.get('metadata', {}))
            ))

    def cleanup_cache(self, max_age: int = 3600):
        """Limpia entradas antiguas del caché"""
        current_time = datetime.now().timestamp()
        with self.cache_lock:
            expired = [
                k for k, v in self.cache.items()
                if current_time - v['timestamp'] > max_age
            ]
            for k in expired:
                self.cache.pop(k)
