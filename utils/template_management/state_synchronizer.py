from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json
from .logging_config import setup_logging
from .operation_router import OperationRouter

class StateSynchronizer:
    """Sistema de sincronización de estado y datos"""

    def __init__(self):
        self.logger = setup_logging('state_sync')
        self.operation_router = OperationRouter()
        self.current_state = {
            'active_operations': {},
            'pending_changes': [],
            'last_sync': None
        }
        self.state_history = []

    def update_state(self, operation_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza el estado del sistema y sincroniza datos"""
        self.logger.info(f"Actualizando estado: {operation_type}")
        
        try:
            # Registrar operación
            operation_id = self._register_operation(operation_type)
            
            # Procesar operación
            result = self.operation_router.route_operation(operation_type, data)
            
            # Actualizar estado
            state_update = self._process_state_update(operation_id, result)
            
            # Sincronizar cambios
            self._synchronize_changes(state_update)
            
            return {
                'operation_id': operation_id,
                'result': result,
                'state': state_update
            }

        except Exception as e:
            self.logger.error(f"Error en sincronización: {str(e)}")
            return {'error': str(e)}

    def _register_operation(self, operation_type: str) -> str:
        """Registra una nueva operación"""
        operation_id = f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_state['active_operations'][operation_id] = {
            'type': operation_type,
            'status': 'started',
            'timestamp': datetime.now().isoformat()
        }
        
        return operation_id

    def _process_state_update(self, operation_id: str, 
                            result: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa actualización de estado"""
        # Actualizar operación activa
        self.current_state['active_operations'][operation_id]['status'] = (
            'completed' if 'error' not in result else 'failed'
        )

        # Registrar cambios pendientes
        if changes := self._extract_changes(result):
            self.current_state['pending_changes'].extend(changes)

        return {
            'operation_status': self.current_state['active_operations'][operation_id],
            'pending_changes': len(self.current_state['pending_changes']),
            'timestamp': datetime.now().isoformat()
        }

    def _synchronize_changes(self, state_update: Dict[str, Any]) -> None:
        """Sincroniza cambios pendientes"""
        if self.current_state['pending_changes']:
            self.logger.info(f"Sincronizando {len(self.current_state['pending_changes'])} cambios")
            
            # Procesar cambios pendientes
            for change in self.current_state['pending_changes']:
                self._apply_change(change)
            
            # Limpiar cambios procesados
            self.current_state['pending_changes'] = []
            
            # Actualizar timestamp de sincronización
            self.current_state['last_sync'] = datetime.now().isoformat()
            
            # Registrar en historial
            self._record_sync(state_update)

    def _apply_change(self, change: Dict[str, Any]) -> None:
        """Aplica un cambio pendiente"""
        try:
            if change.get('type') == 'template_update':
                self._update_template(change['data'])
            elif change.get('type') == 'processing_result':
                self._store_processing_result(change['data'])
            elif change.get('type') == 'validation_update':
                self._update_validation(change['data'])
                
        except Exception as e:
            self.logger.error(f"Error aplicando cambio: {str(e)}")
            # Mantener el cambio en la cola para reintento
            self.current_state['pending_changes'].append(change)

    def _extract_changes(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrae cambios de un resultado"""
        changes = []
        
        # Detectar cambios en plantillas
        if 'template_changes' in result:
            changes.append({
                'type': 'template_update',
                'data': result['template_changes']
            })
            
        # Detectar cambios en validación
        if 'validation_changes' in result:
            changes.append({
                'type': 'validation_update',
                'data': result['validation_changes']
            })
            
        return changes

    def _record_sync(self, state_update: Dict[str, Any]) -> None:
        """Registra una sincronización en el historial"""
        self.state_history.append({
            'timestamp': datetime.now().isoformat(),
            'changes_processed': len(self.current_state['pending_changes']),
            'state_update': state_update
        })

    def get_sync_status(self) -> Dict[str, Any]:
        """Obtiene estado actual de sincronización"""
        return {
            'active_operations': len(self.current_state['active_operations']),
            'pending_changes': len(self.current_state['pending_changes']),
            'last_sync': self.current_state['last_sync'],
            'sync_history': len(self.state_history)
        }
