from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime
import threading
from .logging_config import setup_logging

class SmartIndexer:
    """Indexador inteligente de documentos y plantillas"""
    
    def __init__(self):
        self.logger = setup_logging('indexer')
        self.index = {}
        self.metadata = {}
        self._lock = threading.Lock()
        self.index_path = Path('indexes')
        self.max_cache = 1000

    def index_document(self, doc_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Indexa un documento"""
        try:
            with self._lock:
                # Extraer términos clave
                terms = self._extract_terms(content)
                
                # Crear índice invertido
                self._update_index(doc_id, terms)
                
                # Guardar metadata
                self._store_metadata(doc_id, content)
                
                # Limpiar caché si necesario
                self._cleanup_if_needed()
                
                return {
                    'doc_id': doc_id,
                    'terms': len(terms),
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error indexando documento: {str(e)}")
            return {'error': str(e)}

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca documentos"""
        try:
            # Tokenizar query
            terms = self._tokenize(query)
            
            # Buscar en índice
            matches = self._find_matches(terms)
            
            # Ordenar por relevancia
            ranked = self._rank_results(matches, terms)
            
            # Limitar resultados
            return ranked[:limit]

        except Exception as e:
            self.logger.error(f"Error en búsqueda: {str(e)}")
            return []

    def _extract_terms(self, content: Dict[str, Any]) -> Dict[str, float]:
        """Extrae términos relevantes"""
        terms = {}
        
        def process_value(value: Any, weight: float = 1.0):
            if isinstance(value, str):
                for term in self._tokenize(value):
                    terms[term] = terms.get(term, 0) + weight
            elif isinstance(value, dict):
                for k, v in value.items():
                    process_value(v, weight * 0.8)
            elif isinstance(value, list):
                for item in value:
                    process_value(item, weight * 0.8)

        process_value(content)
        return terms

    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza texto en términos"""
        # Normalizar
        text = text.lower().strip()
        
        # Tokenizar
        return [
            term.strip() for term in text.split()
            if len(term.strip()) > 2
        ]

    def _update_index(self, doc_id: str, terms: Dict[str, float]) -> None:
        """Actualiza índice invertido"""
        for term, weight in terms.items():
            if term not in self.index:
                self.index[term] = {}
            self.index[term][doc_id] = weight

    def _store_metadata(self, doc_id: str, content: Dict[str, Any]) -> None:
        """Almacena metadata del documento"""
        self.metadata[doc_id] = {
            'timestamp': datetime.now().isoformat(),
            'size': len(str(content)),
            'type': content.get('type', 'unknown')
        }

    def _find_matches(self, terms: List[str]) -> Dict[str, float]:
        """Encuentra documentos que coinciden"""
        matches = {}
        
        for term in terms:
            if docs := self.index.get(term):
                for doc_id, weight in docs.items():
                    matches[doc_id] = matches.get(doc_id, 0) + weight

        return matches

    def _rank_results(self, matches: Dict[str, float], 
                     terms: List[str]) -> List[Dict[str, Any]]:
        """Ordena resultados por relevancia"""
        ranked = [
            {
                'doc_id': doc_id,
                'score': score,
                'metadata': self.metadata.get(doc_id, {})
            }
            for doc_id, score in matches.items()
        ]
        
        return sorted(ranked, key=lambda x: x['score'], reverse=True)

    def _cleanup_if_needed(self) -> None:
        """Limpia caché si es necesario"""
        if len(self.metadata) > self.max_cache:
            # Eliminar 20% más antiguo
            sorted_docs = sorted(
                self.metadata.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            to_remove = sorted_docs[:int(len(sorted_docs) * 0.2)]
            for doc_id, _ in to_remove:
                self._remove_document(doc_id)

    def _remove_document(self, doc_id: str) -> None:
        """Elimina documento del índice"""
        # Limpiar índice invertido
        for term_docs in self.index.values():
            term_docs.pop(doc_id, None)
            
        # Limpiar metadata
        self.metadata.pop(doc_id, None)
