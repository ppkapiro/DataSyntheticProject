from typing import Dict, Any, List, Tuple
from datetime import datetime
import difflib
from .logging_config import setup_logging

class DataReconciliator:
    """Sistema de reconciliación de datos entre fuentes"""
    
    def __init__(self):
        self.logger = setup_logging('reconciliator')
        self.similarity_threshold = 0.85
        self.reconciliation_history = []

    def reconcile_data(self, source_data: Dict[str, Any], 
                      target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcilia datos entre dos fuentes"""
        try:
            # Detectar campos comunes
            common_fields = self._find_common_fields(source_data, target_data)
            
            # Resolver conflictos
            resolved = self._resolve_conflicts(
                source_data, 
                target_data, 
                common_fields
            )
            
            # Consolidar datos
            result = self._consolidate_data(resolved)
            
            # Registrar reconciliación
            self._record_reconciliation(result)
            
            return result

        except Exception as e:
            self.logger.error(f"Error en reconciliación: {str(e)}")
            return {'error': str(e)}

    def _find_common_fields(self, source: Dict[str, Any], 
                          target: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Encuentra campos comunes entre fuentes"""
        matches = []
        
        for source_field in source.keys():
            best_match = self._find_best_match(source_field, target.keys())
            if best_match[1] >= self.similarity_threshold:
                matches.append((source_field, best_match[0]))
                
        return matches

    def _find_best_match(self, field: str, candidates: List[str]) -> Tuple[str, float]:
        """Encuentra mejor coincidencia para un campo"""
        if not candidates:
            return ('', 0.0)
            
        similarities = [
            (candidate, difflib.SequenceMatcher(None, field, candidate).ratio())
            for candidate in candidates
        ]
        
        return max(similarities, key=lambda x: x[1])

    def _resolve_conflicts(self, source: Dict[str, Any],
                         target: Dict[str, Any],
                         common_fields: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Resuelve conflictos entre campos comunes"""
        resolved = {}
        
        for source_field, target_field in common_fields:
            source_value = source[source_field]
            target_value = target[target_field]
            
            if source_value == target_value:
                resolved[target_field] = source_value
            else:
                resolved[target_field] = self._select_best_value(
                    source_value,
                    target_value,
                    source_field
                )

        return resolved

    def _select_best_value(self, value1: Any, value2: Any, 
                          field_name: str) -> Any:
        """Selecciona el mejor valor entre dos opciones"""
        # Implementar lógica específica por tipo de campo
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            return max(value1, value2)
        elif isinstance(value1, str) and isinstance(value2, str):
            return value1 if len(value1) > len(value2) else value2
        return value1  # Default a primer valor

    def _consolidate_data(self, resolved: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida datos reconciliados"""
        return {
            'reconciled_data': resolved,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'field_count': len(resolved),
                'confidence': self._calculate_confidence(resolved)
            }
        }

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calcula nivel de confianza de reconciliación"""
        if not data:
            return 0.0
        
        # Base confidence starts at 0.5
        confidence = 0.5
        
        # Adjust based on field count
        field_count = len(data)
        if field_count > 5:
            confidence += 0.1
        if field_count > 10:
            confidence += 0.1
            
        # Cap at 1.0
        return min(confidence, 1.0)

    def _record_reconciliation(self, result: Dict[str, Any]) -> None:
        """Registra resultado de reconciliación"""
        self.reconciliation_history.append({
            'timestamp': datetime.now().isoformat(),
            'fields_reconciled': len(result['reconciled_data']),
            'confidence': result['metadata']['confidence']
        })
