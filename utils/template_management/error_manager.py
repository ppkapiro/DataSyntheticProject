from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import traceback
from .logging_config import setup_logging

class ErrorManager:
    """Sistema de gestión de errores y recuperación"""

    def __init__(self):
        self.logger = setup_logging('error_manager')
        self.error_history = []
        self.recovery_attempts = {}
        self.error_patterns = {
            'validation_error': self._handle_validation_error,
            'mapping_error': self._handle_mapping_error,
            'type_error': self._handle_type_error,
            'missing_field': self._handle_missing_field
        }

    def handle_error(self, error: Exception, 
                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja un error del sistema"""
        self.logger.error(f"Error detectado: {str(error)}")
        
        try:
            # Identificar tipo de error
            error_type = self._identify_error_type(error)
            
            # Registrar error
            error_record = self._record_error(error, error_type, context)
            
            # Intentar recuperación
            if handler := self.error_patterns.get(error_type):
                recovery_result = handler(error, context)
                if recovery_result.get('recovered'):
                    self._record_recovery(error_record['id'], recovery_result)
                    return recovery_result

            # Si no hay recuperación, retornar error formateado
            return {
                'error': str(error),
                'type': error_type,
                'recoverable': False,
                'context': self._sanitize_context(context),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.critical(f"Error en gestión de errores: {str(e)}")
            return {'error': 'Error crítico en sistema'}

    def _identify_error_type(self, error: Exception) -> str:
        """Identifica el tipo de error"""
        error_str = str(error).lower()
        
        if 'validation' in error_str:
            return 'validation_error'
        elif 'mapping' in error_str:
            return 'mapping_error'
        elif isinstance(error, TypeError):
            return 'type_error'
        elif 'missing' in error_str:
            return 'missing_field'
            
        return 'unknown_error'

    def _handle_validation_error(self, error: Exception, 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja errores de validación"""
        try:
            field = self._extract_field_from_error(str(error))
            template = context.get('template', {})
            
            if field and template:
                # Intentar corrección automática
                if fixed_value := self._attempt_field_fix(field, template):
                    return {
                        'recovered': True,
                        'field': field,
                        'fixed_value': fixed_value,
                        'confidence': 0.8
                    }

        except Exception as e:
            self.logger.error(f"Error en recuperación: {str(e)}")
            
        return {'recovered': False}

    def _handle_mapping_error(self, error: Exception, 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja errores de mapeo"""
        try:
            if 'mapped_fields' in context:
                # Intentar mapeo alternativo
                if alternative := self._find_alternative_mapping(
                    context['mapped_fields']
                ):
                    return {
                        'recovered': True,
                        'alternative_mapping': alternative,
                        'confidence': 0.7
                    }

        except Exception as e:
            self.logger.error(f"Error en recuperación de mapeo: {str(e)}")
            
        return {'recovered': False}

    def _record_error(self, error: Exception, error_type: str, 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Registra un error en el historial"""
        error_record = {
            'id': f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': error_type,
            'message': str(error),
            'stack_trace': traceback.format_exc(),
            'context': self._sanitize_context(context),
            'timestamp': datetime.now().isoformat()
        }
        
        self.error_history.append(error_record)
        return error_record

    def _record_recovery(self, error_id: str, 
                        recovery_result: Dict[str, Any]) -> None:
        """Registra un intento de recuperación"""
        self.recovery_attempts[error_id] = {
            'timestamp': datetime.now().isoformat(),
            'success': recovery_result.get('recovered', False),
            'method': recovery_result.get('method', 'unknown'),
            'confidence': recovery_result.get('confidence', 0)
        }

    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza el contexto para registro seguro"""
        sanitized = {}
        
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_context(value)
            elif isinstance(value, list):
                sanitized[key] = [str(v) for v in value]
            else:
                sanitized[key] = str(value)
                
        return sanitized

    def get_error_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de errores"""
        if not self.error_history:
            return {'status': 'No hay historial de errores'}

        total_errors = len(self.error_history)
        recovered = sum(
            1 for err_id in self.recovery_attempts 
            if self.recovery_attempts[err_id]['success']
        )
        
        return {
            'total_errors': total_errors,
            'recovered': recovered,
            'recovery_rate': round((recovered / total_errors) * 100, 2),
            'error_types': self._count_error_types()
        }

    def _count_error_types(self) -> Dict[str, int]:
        """Cuenta ocurrencias por tipo de error"""
        counts = {}
        
        for error in self.error_history:
            error_type = error['type']
            counts[error_type] = counts.get(error_type, 0) + 1
            
        return counts
