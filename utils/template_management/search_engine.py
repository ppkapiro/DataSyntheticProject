from typing import List, Dict, Any
import sqlite3
from pathlib import Path
import json
from .logging_config import setup_logging

class TemplateSearchEngine:
    """Motor de búsqueda para plantillas"""

    def __init__(self, db_path: Path):
        self.logger = setup_logging()
        self.db_path = db_path
        self._init_search_indexes()

    def _init_search_indexes(self):
        """Inicializa los índices de búsqueda"""
        with sqlite3.connect(self.db_path) as conn:
            # Índice de texto completo
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS template_fts 
                USING fts5(
                    name, 
                    content,
                    tags,
                    template_id UNINDEXED
                )
            """)
            
            # Tabla de metadatos de búsqueda
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_metadata (
                    template_id TEXT PRIMARY KEY,
                    last_accessed TEXT,
                    access_count INTEGER,
                    relevance_score REAL
                )
            """)

    def search(self, query: str, filters: Dict[str, Any] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca plantillas según criterios"""
        self.logger.info(f"Búsqueda: {query}, filtros: {filters}")
        
        sql_query = """
            SELECT 
                t.id, 
                t.name, 
                t.created_at,
                t.metadata,
                sm.relevance_score
            FROM templates t
            LEFT JOIN search_metadata sm ON t.id = sm.template_id
            WHERE 1=1
        """
        params = []

        # Aplicar búsqueda de texto
        if query:
            sql_query += """
                AND t.id IN (
                    SELECT template_id 
                    FROM template_fts 
                    WHERE template_fts MATCH ?
                )
            """
            params.append(query)

        # Aplicar filtros
        if filters:
            for key, value in filters.items():
                sql_query += f" AND {key} = ?"
                params.append(value)

        # Ordenar por relevancia
        sql_query += " ORDER BY sm.relevance_score DESC, t.created_at DESC LIMIT ?"
        params.append(limit)

        try:
            with sqlite3.connect(self.db_path) as conn:
                results = conn.execute(sql_query, params).fetchall()
                return [self._format_search_result(row) for row in results]
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {str(e)}")
            return []

    def update_search_index(self, template_id: str, content: Dict[str, Any]):
        """Actualiza el índice de búsqueda"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Actualizar índice de texto completo
                conn.execute("""
                    INSERT OR REPLACE INTO template_fts (
                        template_id, name, content, tags
                    ) VALUES (?, ?, ?, ?)
                """, (
                    template_id,
                    content.get('name', ''),
                    json.dumps(content.get('fields', {})),
                    json.dumps(content.get('tags', []))
                ))
                
                # Actualizar metadatos de búsqueda
                conn.execute("""
                    INSERT OR REPLACE INTO search_metadata (
                        template_id, last_accessed, access_count, relevance_score
                    ) VALUES (?, datetime('now'), 0, 1.0)
                """, (template_id,))
                
            self.logger.info(f"Índice actualizado: {template_id}")
        except Exception as e:
            self.logger.error(f"Error actualizando índice: {str(e)}")

    def _format_search_result(self, row: tuple) -> Dict[str, Any]:
        """Formatea un resultado de búsqueda"""
        return {
            'id': row[0],
            'name': row[1],
            'created_at': row[2],
            'metadata': json.loads(row[3]),
            'relevance': row[4]
        }
