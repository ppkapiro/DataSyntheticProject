import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

class SectionManager:
    """Gestor de secciones y consolidación de documentos"""

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)

    def setup_clinic_structure(self, clinic_name: str) -> bool:
        """Configura la estructura de carpetas para una clínica"""
        try:
            clinic_path = self.base_path / clinic_name
            if not clinic_path.exists():
                return False

            # Crear carpeta de resúmenes si no existe
            resumen_path = clinic_path / 'Resumen_Secciones'
            resumen_path.mkdir(exist_ok=True)

            # Crear estructura inicial de JSONs
            sections = ['manana', 'tarde', 'general']
            for section in sections:
                json_path = resumen_path / f'resumen_{section}.json'
                if not json_path.exists():
                    self._create_empty_json(json_path)

            return True
        except Exception as e:
            self.logger.error(f"Error configurando estructura: {str(e)}")
            return False

    def consolidate_documents(self, clinic_name: str, facilitador_name: str, 
                            doc_type: str) -> bool:
        """Consolida documentos por sección"""
        try:
            clinic_path = self.base_path / clinic_name
            facilitador_path = clinic_path / facilitador_name
            resumen_path = clinic_path / 'Resumen_Secciones'

            # Estructura para almacenar datos
            consolidation = {
                'manana': {'documentos': [], 'total': 0},
                'tarde': {'documentos': [], 'total': 0},
                'metadata': {
                    'fecha_actualizacion': datetime.now().isoformat(),
                    'facilitador': facilitador_name,
                    'tipo_documento': doc_type
                }
            }

            # Procesar grupos
            for turno in ['manana', 'tarde']:
                docs = self._get_documents_by_section(
                    facilitador_path, turno, doc_type
                )
                consolidation[turno]['documentos'] = docs
                consolidation[turno]['total'] = len(docs)

            # Guardar JSONs actualizados
            self._save_section_jsons(resumen_path, consolidation)
            return True

        except Exception as e:
            self.logger.error(f"Error en consolidación: {str(e)}")
            return False

    def _get_documents_by_section(self, facilitador_path: Path, 
                                turno: str, doc_type: str) -> List[Dict]:
        """Obtiene documentos de una sección específica"""
        documents = []
        grupo_path = facilitador_path / 'grupos' / turno / 'pacientes'

        if not grupo_path.exists():
            return documents

        for paciente_folder in grupo_path.iterdir():
            if not paciente_folder.is_dir():
                continue

            # Buscar documentos del tipo especificado
            doc_path = paciente_folder / doc_type
            if not doc_path.exists():
                continue

            for doc_folder in ['input', 'output']:
                folder_path = doc_path / doc_folder
                if not folder_path.exists():
                    continue

                for doc in folder_path.glob('*.*'):
                    doc_info = {
                        'nombre': doc.name,
                        'paciente': paciente_folder.name,
                        'ruta': str(doc.relative_to(facilitador_path)),
                        'tipo': doc_type,
                        'carpeta': doc_folder,
                        'fecha_modificacion': datetime.fromtimestamp(
                            doc.stat().st_mtime
                        ).isoformat(),
                        'tamano': doc.stat().st_size
                    }
                    documents.append(doc_info)

        return documents

    def _create_empty_json(self, json_path: Path) -> None:
        """Crea un archivo JSON vacío con estructura base"""
        empty_structure = {
            'metadata': {
                'fecha_creacion': datetime.now().isoformat(),
                'ultima_actualizacion': None,
                'total_documentos': 0
            },
            'documentos': []
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(empty_structure, f, indent=2, ensure_ascii=False)

    def _save_section_jsons(self, resumen_path: Path, 
                           consolidation: Dict) -> None:
        """Guarda los JSONs de sección actualizados"""
        # JSON de mañana
        with open(resumen_path / 'resumen_manana.json', 'w', 
                 encoding='utf-8') as f:
            json.dump({
                'metadata': consolidation['metadata'],
                'documentos': consolidation['manana']['documentos']
            }, f, indent=2, ensure_ascii=False)

        # JSON de tarde
        with open(resumen_path / 'resumen_tarde.json', 'w', 
                 encoding='utf-8') as f:
            json.dump({
                'metadata': consolidation['metadata'],
                'documentos': consolidation['tarde']['documentos']
            }, f, indent=2, ensure_ascii=False)

        # JSON general
        with open(resumen_path / 'resumen_general.json', 'w', 
                 encoding='utf-8') as f:
            json.dump(consolidation, f, indent=2, ensure_ascii=False)

    def analyze_section_data(self, clinic_name: str, section: str, 
                           field: str) -> Optional[Dict]:
        """Analiza un campo específico de los documentos de una sección"""
        try:
            resumen_path = self.base_path / clinic_name / 'Resumen_Secciones'
            json_path = resumen_path / f'resumen_{section}.json'

            if not json_path.exists():
                return None

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extraer y analizar el campo específico
            field_data = {
                'campo': field,
                'seccion': section,
                'fecha_analisis': datetime.now().isoformat(),
                'resultados': {}
            }

            for doc in data.get('documentos', []):
                if field in doc:
                    field_data['resultados'][doc['paciente']] = doc[field]

            return field_data

        except Exception as e:
            self.logger.error(f"Error analizando datos: {str(e)}")
            return None

    def force_update(self, clinic_name: str) -> bool:
        """Fuerza la actualización de todos los JSONs de la clínica"""
        try:
            clinic_path = self.base_path / clinic_name
            if not clinic_path.exists():
                return False

            # Obtener lista de facilitadores
            with open(clinic_path / 'clinic_config.json', 'r', 
                     encoding='utf-8') as f:
                config = json.load(f)

            # Actualizar documentos para cada facilitador
            for facilitador in config.get('facilitadores_psr', []):
                for doc_type in ['FARC', 'BIO', 'MTP', 'notas_progreso']:
                    self.consolidate_documents(
                        clinic_name, 
                        facilitador['nombre'], 
                        doc_type
                    )

            return True

        except Exception as e:
            self.logger.error(f"Error en actualización forzada: {str(e)}")
            return False
