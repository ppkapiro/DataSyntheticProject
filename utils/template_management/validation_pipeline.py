from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from .content_validator import ContentValidator
from .data_transformer import DataTransformer
from .error_manager import ErrorManager
from .logging_config import setup_logging

class ValidationPipeline:
    """Pipeline de validación que coordina el proceso completo"""

    def __init__(self):
        self.logger = setup_logging('validation_pipeline')
        self.content_validator = ContentValidator()
        self.transformer = DataTransformer()
        self.error_manager = ErrorManager()
        self.validation_history = []
        self.validation_stages = [
            self._validate_structure,
            self._validate_types,
            self._validate_content,
            self._validate_relationships,
            self._validate_business_rules
        ]

    def run_validation(self, data: Dict[str, Any], 
                      template: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el pipeline completo de validación"""
        self.logger.info("Iniciando pipeline de validación")
        
        pipeline_result = {
            'is_valid': True,
            'stages': [],
            'errors': [],
            'warnings': [],
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'template': template.get('nombre_archivo')
            }
        }

        try:
            # Ejecutar cada etapa de validación
            for stage in self.validation_stages:
                stage_result = stage(data, template)
                pipeline_result['stages'].append(stage_result)
                
                # Acumular errores y advertencias
                pipeline_result['errors'].extend(stage_result.get('errors', []))
                pipeline_result['warnings'].extend(stage_result.get('warnings', []))
                
                # Actualizar estado de validación
                if not stage_result.get('is_valid', True):
                    pipeline_result['is_valid'] = False
                    
                # Detener si hay errores críticos
                if stage_result.get('critical_error'):
                    break

            # Registrar resultado
            self._record_validation(pipeline_result)
            
            return pipeline_result

        except Exception as e:
            error_result = self.error_manager.handle_error(e, {
                'data': data,
                'template': template
            })
            pipeline_result['errors'].append(error_result)
            pipeline_result['is_valid'] = False
            return pipeline_result

    def _validate_structure(self, data: Dict[str, Any], 
                          template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida estructura básica de datos"""
        result = {
            'stage': 'structure',
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        required_keys = template.get('required_keys', [])
        for key in required_keys:
            if key not in data:
                result['is_valid'] = False
                result['errors'].append(f"Campo requerido faltante: {key}")

        return result

    def _validate_types(self, data: Dict[str, Any], 
                       template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida tipos de datos"""
        result = {
            'stage': 'types',
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        for field_name, field_info in template.get('campos', {}).items():
            if field_value := data.get(field_name):
                transformed, confidence = self.transformer.transform_field(
                    field_value,
                    'string',
                    field_info.get('type', 'string')
                )
                
                if confidence < 0.8:
                    result['warnings'].append(
                        f"Baja confianza en tipo de {field_name}: {confidence}"
                    )

        return result

    def _validate_content(self, data: Dict[str, Any], 
                         template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida contenido específico"""
        result = {
            'stage': 'content',
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        validation_result = self.content_validator.validate_content(
            data,
            template
        )

        if not validation_result.get('is_valid', False):
            result['is_valid'] = False
            result['errors'].extend(validation_result.get('errors', []))

        return result

    def _validate_relationships(self, data: Dict[str, Any], 
                              template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida relaciones entre campos"""
        result = {
            'stage': 'relationships',
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        relationships = template.get('relationships', [])
        for rel in relationships:
            if not self._check_relationship(rel, data):
                result['is_valid'] = False
                result['errors'].append(f"Relación inválida: {rel['description']}")

        return result

    def _validate_business_rules(self, data: Dict[str, Any], 
                               template: Dict[str, Any]) -> Dict[str, Any]:
        """Valida reglas de negocio"""
        result = {
            'stage': 'business_rules',
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        rules = template.get('business_rules', [])
        for rule in rules:
            if not self._check_business_rule(rule, data):
                result['is_valid'] = False
                result['errors'].append(f"Regla de negocio violada: {rule['description']}")

        return result

    def _record_validation(self, result: Dict[str, Any]) -> None:
        """Registra resultado de validación"""
        self.validation_history.append({
            'timestamp': result['metadata']['timestamp'],
            'template': result['metadata']['template'],
            'is_valid': result['is_valid'],
            'error_count': len(result['errors']),
            'warning_count': len(result['warnings'])
        })

    def get_validation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de validación"""
        if not self.validation_history:
            return {'status': 'No hay historial de validaciones'}

        total = len(self.validation_history)
        successful = sum(1 for v in self.validation_history if v['is_valid'])
        
        return {
            'total_validations': total,
            'successful': successful,
            'success_rate': round((successful / total) * 100, 2),
            'average_errors': sum(v['error_count'] for v in self.validation_history) / total
        }
