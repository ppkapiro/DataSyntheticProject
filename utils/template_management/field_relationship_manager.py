from typing import Dict, Any, List, Optional, Set
from .logging_config import setup_logging

class FieldRelationshipManager:
    """Gestor de relaciones entre campos"""

    def __init__(self):
        self.logger = setup_logging('field_relationships')
        self.relationship_types = {
            'parent_child': 'Relación jerárquica entre campos',
            'dependent': 'Un campo depende de otro',
            'mutually_exclusive': 'Campos mutuamente excluyentes',
            'required_together': 'Campos que deben aparecer juntos',
            'calculated': 'Campo calculado basado en otros'
        }
        self.detected_relationships = {}

    def analyze_relationships(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza y detecta relaciones entre campos"""
        self.logger.info("Analizando relaciones entre campos")
        
        relationships = {
            'hierarchical': self._detect_hierarchical_relationships(fields),
            'dependencies': self._detect_dependencies(fields),
            'mutual_exclusions': self._detect_mutual_exclusions(fields),
            'required_groups': self._detect_required_groups(fields),
            'calculated_fields': self._detect_calculated_fields(fields)
        }

        self.detected_relationships = relationships
        return relationships

    def _detect_hierarchical_relationships(self, fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta relaciones jerárquicas entre campos"""
        hierarchies = []
        processed = set()

        for field_name, field_info in fields.items():
            if field_name in processed:
                continue

            if parent := self._find_parent_field(field_name, fields):
                hierarchies.append({
                    'parent': parent,
                    'child': field_name,
                    'type': 'hierarchical',
                    'confidence': 0.9
                })
                processed.add(field_name)

        return hierarchies

    def _detect_dependencies(self, fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta dependencias entre campos"""
        dependencies = []

        for field_name, field_info in fields.items():
            if depends_on := field_info.get('depends_on'):
                dependencies.append({
                    'field': field_name,
                    'depends_on': depends_on,
                    'type': 'dependent',
                    'required': field_info.get('required', False)
                })

        return dependencies

    def _detect_mutual_exclusions(self, fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta campos mutuamente excluyentes"""
        exclusions = []
        processed_pairs = set()

        for field_name, field_info in fields.items():
            if excludes := field_info.get('excludes', []):
                for excluded_field in excludes:
                    pair = tuple(sorted([field_name, excluded_field]))
                    if pair not in processed_pairs:
                        exclusions.append({
                            'field1': pair[0],
                            'field2': pair[1],
                            'type': 'mutually_exclusive',
                            'reason': field_info.get('exclusion_reason', 'No especificada')
                        })
                        processed_pairs.add(pair)

        return exclusions

    def _find_parent_field(self, field_name: str, fields: Dict[str, Any]) -> Optional[str]:
        """Encuentra el campo padre de un campo dado"""
        parts = field_name.split('_')
        if len(parts) > 1:
            potential_parent = '_'.join(parts[:-1])
            if potential_parent in fields:
                return potential_parent
        return None

    def validate_relationships(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida las relaciones detectadas en los datos"""
        if not self.detected_relationships:
            return {'error': 'No hay relaciones detectadas para validar'}

        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Validar jerarquías
        for hierarchy in self.detected_relationships['hierarchical']:
            if not self._validate_hierarchy(hierarchy, data):
                validation_results['valid'] = False
                validation_results['errors'].append(
                    f"Error en jerarquía: {hierarchy['parent']} -> {hierarchy['child']}"
                )

        # Validar dependencias
        for dependency in self.detected_relationships['dependencies']:
            if not self._validate_dependency(dependency, data):
                validation_results['valid'] = False
                validation_results['errors'].append(
                    f"Error en dependencia: {dependency['field']} depende de {dependency['depends_on']}"
                )

        return validation_results

    def _validate_hierarchy(self, hierarchy: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Valida una relación jerárquica"""
        parent = data.get(hierarchy['parent'])
        child = data.get(hierarchy['child'])

        if parent is None:
            return False
        if parent and child is None:
            return False
            
        return True

    def _validate_dependency(self, dependency: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Valida una dependencia entre campos"""
        dependent_field = data.get(dependency['field'])
        required_field = data.get(dependency['depends_on'])

        if dependent_field is not None:
            return required_field is not None
            
        return True
