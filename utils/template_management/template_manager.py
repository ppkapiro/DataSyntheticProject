from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import yaml
from datetime import datetime
import shutil
from .logging_config import setup_logging

class TemplateManager:
    """Gestor de plantillas con operaciones CRUD básicas"""

    def __init__(self, templates_dir: Path = None):
        self.logger = setup_logging()
        self.templates_dir = templates_dir or Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        self.cache = {}

    def create_template(self, name: str, fields: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Crea una nueva plantilla"""
        template_id = self._generate_template_id(name)
        template = {
            'id': template_id,
            'name': name,
            'fields': fields,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        # Guardar en disco
        template_path = self.templates_dir / f"{template_id}.json"
        self._save_template(template_path, template)
        
        # Actualizar caché
        self.cache[template_id] = template
        
        self.logger.info(f"Plantilla creada: {name}")
        return template

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Recupera una plantilla por su ID"""
        # Intentar obtener de caché
        if template_id in self.cache:
            return self.cache[template_id]

        # Buscar en disco
        template_path = self.templates_dir / f"{template_id}.json"
        if not template_path.exists():
            self.logger.warning(f"Plantilla no encontrada: {template_id}")
            return None

        template = self._load_template(template_path)
        self.cache[template_id] = template
        return template

    def update_template(self, template_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza una plantilla existente"""
        template = self.get_template(template_id)
        if not template:
            return None

        # Actualizar campos
        template['fields'].update(updates.get('fields', {}))
        template['metadata'].update(updates.get('metadata', {}))
        template['updated_at'] = datetime.now().isoformat()

        # Guardar cambios
        template_path = self.templates_dir / f"{template_id}.json"
        self._save_template(template_path, template)
        
        # Actualizar caché
        self.cache[template_id] = template
        
        self.logger.info(f"Plantilla actualizada: {template_id}")
        return template

    def delete_template(self, template_id: str) -> bool:
        """Elimina una plantilla"""
        template_path = self.templates_dir / f"{template_id}.json"
        if not template_path.exists():
            return False

        # Crear respaldo antes de eliminar
        backup_path = self.templates_dir / "backups" / f"{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path.parent.mkdir(exist_ok=True)
        shutil.copy2(template_path, backup_path)

        # Eliminar archivo
        template_path.unlink()
        
        # Limpiar caché
        self.cache.pop(template_id, None)
        
        self.logger.info(f"Plantilla eliminada: {template_id}")
        return True

    def _generate_template_id(self, name: str) -> str:
        """Genera un ID único para la plantilla"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{name.lower().replace(' ', '_')}_{timestamp}"

    def _save_template(self, path: Path, template: Dict[str, Any]) -> None:
        """Guarda una plantilla en disco"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

    def _load_template(self, path: Path) -> Dict[str, Any]:
        """Carga una plantilla desde disco"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_templates(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Lista todas las plantillas disponibles"""
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            template = self._load_template(template_file)
            if self._matches_criteria(template, filter_criteria):
                templates.append(template)
        return templates

    def _matches_criteria(self, template: Dict[str, Any], criteria: Dict[str, Any] = None) -> bool:
        """Verifica si una plantilla cumple con los criterios de filtrado"""
        if not criteria:
            return True
        
        return all(
            template.get(key) == value
            for key, value in criteria.items()
        )
