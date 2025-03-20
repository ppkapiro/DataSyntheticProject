from typing import Dict, Any, List, Optional
from pathlib import Path
import fitz  # PyMuPDF
from datetime import datetime
from .logging_config import setup_logging

class PDFBuilder:
    """Constructor inteligente de estructuras PDF"""
    
    def __init__(self):
        self.logger = setup_logging('pdf_builder')
        self.structure_cache = {}
        self.max_cache_size = 100

    def build_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """Construye estructura jerárquica del PDF"""
        self.logger.info(f"Analizando estructura de {pdf_path}")
        
        try:
            doc = fitz.open(str(pdf_path))
            structure = {
                'metadata': self._extract_metadata(doc),
                'pages': self._analyze_pages(doc),
                'fields': self._detect_fields(doc),
                'hierarchy': self._build_hierarchy(doc),
                'stats': self._generate_stats(doc)
            }
            doc.close()
            return structure
        except Exception as e:
            self.logger.error(f"Error construyendo estructura: {str(e)}")
            return {'error': str(e)}

    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Extrae metadata del PDF"""
        return {
            'title': doc.metadata.get('title', ''),
            'author': doc.metadata.get('author', ''),
            'subject': doc.metadata.get('subject', ''),
            'keywords': doc.metadata.get('keywords', ''),
            'created': doc.metadata.get('creationDate', ''),
            'modified': doc.metadata.get('modDate', ''),
            'page_count': len(doc)
        }

    def _analyze_pages(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """Analiza estructura de páginas"""
        return [self._analyze_single_page(page) for page in doc]

    def _detect_fields(self, doc: fitz.Document) -> Dict[str, Any]:
        """Detecta campos y su tipo"""
        fields = {}
        for page in doc:
            text_fields = self._find_text_fields(page)
            form_fields = self._find_form_fields(page)
            fields.update(text_fields)
            fields.update(form_fields)
        return fields

    def _build_hierarchy(self, doc: fitz.Document) -> Dict[str, Any]:
        """Construye jerarquía de documento"""
        hierarchy = {'sections': []}
        current_section = None

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if self._is_heading(block):
                    current_section = {
                        'title': block['text'],
                        'level': self._get_heading_level(block),
                        'content': []
                    }
                    hierarchy['sections'].append(current_section)
                elif current_section:
                    current_section['content'].append(block['text'])

        return hierarchy

    def _generate_stats(self, doc: fitz.Document) -> Dict[str, Any]:
        """Genera estadísticas del documento"""
        stats = {
            'page_count': len(doc),
            'text_blocks': 0,
            'images': 0,
            'forms': 0,
            'fields': 0
        }

        for page in doc:
            stats['text_blocks'] += len(page.get_text_blocks())
            stats['images'] += len(page.get_images())
            stats['forms'] += len(page.get_forms())
            stats['fields'] += len(self._find_form_fields(page))

        return stats
