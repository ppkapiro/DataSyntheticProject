from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from .logging_config import setup_logging
from .error_manager import ErrorManager
from .field_reconciliation import FieldReconciliation

class DataIntegrator:
    """Sistema de integración de datos de múltiples fuentes"""

    def __init__(self):
        self.logger = setup_logging('data_integrator')
        self.error_manager = ErrorManager()
        self.reconciliation = FieldReconciliation()
        self.integration_history = []
        self.conflict_resolution_strategies = {
            'field_mismatch': self._resolve_field_mismatch,
            'type_conflict': self._resolve_type_conflict,
            'value_conflict': self._resolve_value_conflict,
            'missing_data': self._resolve_missing_data
        }

    def integrate_data(self, sources: List[Dict[str, Any]], 
                      template: Dict[str, Any]) -> Dict[str, Any]:
        """Integra datos de múltiples fuentes según plantilla"""
        self.logger.info(f"Iniciando integración de {len(sources)} fuentes")
        
        try:
            # Validar fuentes
            validated_sources = self._validate_sources(sources)
            
            # Detectar conflictos
            conflicts = self._detect_conflicts(validated_sources)
            
            # Resolver conflictos
            resolved_data = self._resolve_conflicts(conflicts, template)
            
            # Consolidar datos
            integrated_data = self._consolidate_data(resolved_data, template)
            
            # Registrar integración
            self._record_integration(integrated_data)
            
            return {
                'integrated_data': integrated_data,
                'metadata': {
                    'sources': len(sources),
                    'conflicts_resolved': len(conflicts),
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            self.logger.error(f"Error en integración: {str(e)}")
            return self.error_manager.handle_error(e, {
                'sources': len(sources),
                'template': template.get('name')
            })

    def _validate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida las fuentes de datos"""
        validated = []
        
        for source in sources:
            try:
                # Validar estructura básica
                if self._validate_source_structure(source):
                    # Validar tipos de datos
                    validated_data = self._validate_source_data(source)
                    validated.append(validated_data)
                else:
                    self.logger.warning(f"Fuente inválida: {source.get('id', 'unknown')}")
            except Exception as e:
                self.error_manager.handle_error(e, {'source': source})
                
        return validated

    def _detect_conflicts(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detecta conflictos entre fuentes"""
        conflicts = []
        fields_map = {}

        # Mapear campos por fuente
        for source in sources:
            for field, value in source.get('fields', {}).items():
                if field not in fields_map:
                    fields_map[field] = []
                fields_map[field].append({
                    'source': source.get('id'),
                    'value': value,
                    'confidence': source.get('confidence', {}).get(field, 0.0)
                })

        # Detectar conflictos
        for field, values in fields_map.items():
            if len(values) > 1:
                conflicts.extend(
                    self._analyze_field_conflicts(field, values)
                )

        return conflicts

    def _resolve_conflicts(self, conflicts: List[Dict[str, Any]], 
                         template: Dict[str, Any]) -> Dict[str, Any]:
        """Resuelve conflictos usando estrategias definidas"""
        resolved = {}
        
        for conflict in conflicts:
            if resolver := self.conflict_resolution_strategies.get(conflict['type']):
                resolution = resolver(conflict, template)
                if resolution:
                    field_name = conflict['field']
                    resolved[field_name] = resolution

        return resolved

    def _consolidate_data(self, resolved_data: Dict[str, Any], 
                         template: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida datos resueltos según plantilla"""
        consolidated = {
            'fields': {},
            'metadata': {
                'template': template.get('name'),
                'timestamp': datetime.now().isoformat()
            }
        }

        # Aplicar estructura de plantilla
        for field_name, field_info in template.get('fields', {}).items():
            if field_name in resolved_data:
                consolidated['fields'][field_name] = {
                    'value': resolved_data[field_name]['value'],
                    'confidence': resolved_data[field_name].get('confidence', 1.0),
                    'source': resolved_data[field_name].get('source', 'resolved'),
                    'type': field_info.get('type', 'string')
                }

        return consolidated

    def _record_integration(self, result: Dict[str, Any]) -> None:
        """Registra resultado de integración"""
        self.integration_history.append({
            'timestamp': datetime.now().isoformat(),
            'fields_integrated': len(result.get('fields', {})),
            'template': result.get('metadata', {}).get('template')
        })

    def get_integration_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de integración"""
        if not self.integration_history:
            return {'status': 'No hay historial de integraciones'}

        total = len(self.integration_history)
        fields = sum(r['fields_integrated'] for r in self.integration_history)
        
        return {
            'total_integrations': total,
            'total_fields': fields,
            'avg_fields_per_integration': fields / total,
            'last_integration': self.integration_history[-1]['timestamp']
        }
