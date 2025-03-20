from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import sqlite3
from datetime import datetime
import difflib
from .logging_config import setup_logging

class VersionControl:
    """Sistema de control de versiones para plantillas"""

    def __init__(self, storage_dir: Path = None):
        self.logger = setup_logging()
        self.storage_dir = storage_dir or Path("versions")
        self.storage_dir.mkdir(exist_ok=True)
        self._init_version_db()

    def _init_version_db(self):
        """Inicializa la base de datos de versiones"""
        db_path = self.storage_dir / "versions.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id TEXT PRIMARY KEY,
                    template_id TEXT,
                    version TEXT,
                    content TEXT,
                    changes TEXT,
                    created_at TEXT,
                    created_by TEXT,
                    FOREIGN KEY (template_id) REFERENCES templates(id)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_template_version ON versions(template_id, version)")

    def create_version(self, template_id: str, content: Dict[str, Any], user: str = "system") -> str:
        """Crea una nueva versión de una plantilla"""
        try:
            # Obtener última versión
            last_version = self.get_latest_version(template_id)
            new_version = self._increment_version(last_version)
            
            # Generar ID único
            version_id = f"{template_id}_{new_version}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Calcular cambios si existe versión anterior
            changes = []
            if last_version:
                changes = self._calculate_changes(
                    self.get_version_content(template_id, last_version),
                    content
                )

            # Guardar nueva versión
            self._save_version(version_id, template_id, new_version, content, changes, user)
            
            self.logger.info(f"Nueva versión creada: {new_version} para plantilla {template_id}")
            return version_id

        except Exception as e:
            self.logger.error(f"Error creando versión: {str(e)}")
            raise

    def rollback(self, template_id: str, version: str) -> Optional[Dict[str, Any]]:
        """Revierte una plantilla a una versión específica"""
        try:
            # Obtener versión objetivo
            target_version = self.get_version_content(template_id, version)
            if not target_version:
                return None

            # Crear nueva versión con el contenido anterior
            new_version_id = self.create_version(
                template_id, 
                target_version,
                "system_rollback"
            )

            self.logger.info(f"Rollback completado a versión {version}")
            return self.get_version_content(template_id, new_version_id)

        except Exception as e:
            self.logger.error(f"Error en rollback: {str(e)}")
            return None

    def compare_versions(self, template_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compara dos versiones de una plantilla"""
        content1 = self.get_version_content(template_id, version1)
        content2 = self.get_version_content(template_id, version2)

        if not content1 or not content2:
            return {'error': 'Versiones no encontradas'}

        return {
            'changes': self._calculate_changes(content1, content2),
            'version1': version1,
            'version2': version2,
            'timestamp': datetime.now().isoformat()
        }

    def get_version_history(self, template_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de versiones de una plantilla"""
        db_path = self.storage_dir / "versions.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM versions WHERE template_id = ? ORDER BY created_at DESC",
                (template_id,)
            )
            return [self._format_version_info(row) for row in cursor.fetchall()]

    def _increment_version(self, current_version: str = None) -> str:
        """Incrementa el número de versión"""
        if not current_version:
            return "1.0.0"

        major, minor, patch = map(int, current_version.split('.'))
        return f"{major}.{minor}.{patch + 1}"

    def _calculate_changes(self, old_content: Dict[str, Any], new_content: Dict[str, Any]) -> List[str]:
        """Calcula los cambios entre dos versiones"""
        changes = []
        
        # Comparar campos
        old_fields = set(old_content.get('fields', {}).keys())
        new_fields = set(new_content.get('fields', {}).keys())
        
        added = new_fields - old_fields
        removed = old_fields - new_fields
        modified = {
            field for field in old_fields & new_fields
            if old_content['fields'][field] != new_content['fields'][field]
        }

        if added:
            changes.append(f"Campos añadidos: {', '.join(added)}")
        if removed:
            changes.append(f"Campos eliminados: {', '.join(removed)}")
        if modified:
            changes.append(f"Campos modificados: {', '.join(modified)}")

        return changes

    def _save_version(self, version_id: str, template_id: str, version: str, 
                     content: Dict[str, Any], changes: List[str], user: str):
        """Guarda una versión en la base de datos"""
        db_path = self.storage_dir / "versions.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO versions (id, template_id, version, content, changes, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                template_id,
                version,
                json.dumps(content),
                json.dumps(changes),
                datetime.now().isoformat(),
                user
            ))

    def _format_version_info(self, row: tuple) -> Dict[str, Any]:
        """Formatea la información de una versión"""
        return {
            'id': row[0],
            'template_id': row[1],
            'version': row[2],
            'changes': json.loads(row[4]),
            'created_at': row[5],
            'created_by': row[6]
        }
