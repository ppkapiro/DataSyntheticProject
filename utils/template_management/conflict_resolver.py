from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from .logging_config import setup_logging
from .data_transformer import DataTransformer

class ConflictResolver:
    """Sistema de detección y resolución de conflictos"""

    def __init__(self):
        self.logger = setup_logging('conflict_resolver')
        self.transformer = DataTransformer()
        self.resolution_history = []
        self.resolution_strategies = {
            'type_mismatch': self._resolve_type_mismatch,
            'missing_required': self._resolve_missing_required,
            'validation_failed': self._resolve_validation_failure,
            'format_mismatch': self._resolve_format_mismatch
        }

    def resolve_conflicts(self, pdf_data: Dict[str, Any], 
                        template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta y resuelve conflictos entre PDF y plantilla"""
        self.logger.info("Iniciando resolución de conflictos")
        
        try:
            # Detectar conflictos
            conflicts = self._detect_conflicts(pdf_data, template_data)
            
            # Resolver cada conflicto
            resolutions = self._apply_resolutions(conflicts, pdf_data, template_data)
            
            # Validar resultado
            result = self._validate_resolutions(resolutions)
            
            # Registrar resoluciones
            self._record_resolutions(conflicts, resolutions)
            
            return {
                'resolved_data': resolutions,
                'conflicts': conflicts,
                'status': 'success' if self._is_valid(resolutions) else 'partial',
                'metadata': {
                    'total_conflicts': len(conflicts),
                    'resolved_count': len(resolutions),
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            self.logger.error(f"Error en resolución: {str(e)}")
            return {'error': str(e)}

    def _detect_conflicts(self, pdf_data: Dict[str, Any], 
                         template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta conflictos entre datos PDF y plantilla"""
        conflicts = []
        template_fields = template_data.get('campos', {})
        pdf_fields = pdf_data.get('fields', {})

        for field_name, field_info in template_fields.items():
            if pdf_value := pdf_fields.get(field_name):
                # Verificar tipo
                if not self._check_type_compatibility(
                    pdf_value.get('type'),
                    field_info.get('type')
                ):
                    conflicts.append({
                        'type': 'type_mismatch',
                        'field': field_name,
                        'expected': field_info.get('type'),
                        'found': pdf_value.get('type')
                    })
                
                # Verificar formato
                if not self._check_format_compatibility(
                    pdf_value.get('value'),
                    field_info.get('format')
                ):
                    conflicts.append({
                        'type': 'format_mismatch',
                        'field': field_name,
                        'expected_format': field_info.get('format')
                    })

            elif field_info.get('required', False):
                conflicts.append({
                    'type': 'missing_required',
                    'field': field_name
                })

        return conflicts

    def _apply_resolutions(self, conflicts: List[Dict[str, Any]],
                          pdf_data: Dict[str, Any],
                          template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica estrategias de resolución a los conflictos"""
        resolutions = {}
        
        for conflict in conflicts:
            if resolver := self.resolution_strategies.get(conflict['type']):
                resolution = resolver(
                    conflict,
                    pdf_data,
                    template_data
                )
                if resolution:
                    resolutions[conflict['field']] = resolution

        return resolutions

    def _resolve_type_mismatch(self, conflict: Dict[str, Any],
                              pdf_data: Dict[str, Any],
                              template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Resuelve conflictos de tipo de datos"""
        field = conflict['field']
        pdf_value = pdf_data['fields'][field]['value']
        expected_type = conflict['expected']
        
        try:
            transformed_value, confidence = self.transformer.transform_field(
                pdf_value,
                conflict['found'],
                expected_type
            )
            
            if confidence > 0.7:  # Umbral de confianza
                return {
                    'value': transformed_value,
                    'original': pdf_value,
                    'confidence': confidence,
                    'resolution_type': 'transformation'
                }
                
        except Exception as e:
            self.logger.warning(f"Error en transformación: {str(e)}")
            
        return None

    def _record_resolutions(self, conflicts: List[Dict[str, Any]], 
                          resolutions: Dict[str, Any]) -> None:
        """Registra resoluciones en el historial"""
        self.resolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'total_conflicts': len(conflicts),
            'resolved_count': len(resolutions),
            'success_rate': len(resolutions) / len(conflicts) if conflicts else 1.0
        })

    def get_resolution_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de resoluciones"""
        if not self.resolution_history:
            return {'status': 'No hay historial de resoluciones'}

        total_conflicts = sum(r['total_conflicts'] for r in self.resolution_history)
        total_resolved = sum(r['resolved_count'] for r in self.resolution_history)
        
        return {
            'total_conflicts': total_conflicts,
            'total_resolved': total_resolved,
            'success_rate': round(total_resolved / total_conflicts * 100, 2),
            'resolution_count': len(self.resolution_history)
        }
