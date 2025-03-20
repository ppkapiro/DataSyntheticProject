from typing import Dict, Any, List, Callable
from datetime import datetime
from .logging_config import setup_logging

class BusinessRulesValidator:
    """Validador de reglas de negocio para datos médicos"""
    
    def __init__(self):
        self.logger = setup_logging('rules_validator')
        self.rules = {}
        self.validation_history = []
        self._register_default_rules()

    def validate_data(self, data: Dict[str, Any], 
                     rule_set: str = 'default') -> Dict[str, Any]:
        
        """Valida datos contra conjunto de reglas"""
        try:
            # Obtener reglas aplicables
            active_rules = self._get_rule_set(rule_set)
            
            # Aplicar reglas
            validation_results = []
            for rule in active_rules:
                result = rule(data)
                validation_results.append(result)
                
                # Detener si hay error crítico
                if result.get('critical', False) and not result['valid']:
                    break
            
            # Consolidar resultados
            final_result = self._consolidate_results(validation_results)
            
            # Registrar validación
            self._record_validation(final_result)
            
            return final_result

        except Exception as e:
            self.logger.error(f"Error en validación: {str(e)}")
            return {'error': str(e)}

    def add_rule(self, rule_name: str, rule_func: Callable, 
                 rule_set: str = 'default') -> None:
        """Agrega nueva regla de negocio"""
        if rule_set not in self.rules:
            self.rules[rule_set] = []
        self.rules[rule_set].append(rule_func)

    def _register_default_rules(self) -> None:
        """Registra reglas por defecto"""
        self.rules['default'] = [
            self._validate_required_fields,
            self._validate_field_dependencies,
            self._validate_value_ranges
        ]

    def _validate_required_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida campos requeridos"""
        required_fields = {
            'patient_id', 'diagnosis', 'treatment_date'
        }
        
        missing = required_fields - set(data.keys())
        
        return {
            'rule': 'required_fields',
            'valid': len(missing) == 0,
            'missing': list(missing),
            'critical': True
        }

    def _validate_field_dependencies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dependencias entre campos"""
        dependencies = {
            'medication': ['dosage', 'frequency'],
            'surgery': ['procedure_date', 'surgeon'],
            'lab_results': ['test_date', 'parameters']
        }
        
        violations = []
        for main_field, required_fields in dependencies.items():
            if main_field in data:
                missing = [f for f in required_fields if f not in data]
                if missing:
                    violations.append({
                        'field': main_field,
                        'missing_dependencies': missing
                    })

        return {
            'rule': 'field_dependencies',
            'valid': len(violations) == 0,
            'violations': violations,
            'critical': False
        }

    def _validate_value_ranges(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida rangos de valores"""
        range_rules = {
            'age': (0, 120),
            'blood_pressure_systolic': (60, 220),
            'blood_pressure_diastolic': (40, 140),
            'heart_rate': (40, 200)
        }
        
        violations = []
        for field, (min_val, max_val) in range_rules.items():
            if field in data:
                value = data[field]
                if not min_val <= value <= max_val:
                    violations.append({
                        'field': field,
                        'value': value,
                        'range': [min_val, max_val]
                    })

        return {
            'rule': 'value_ranges',
            'valid': len(violations) == 0,
            'violations': violations,
            'critical': False
        }

    def _consolidate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolida resultados de validación"""
        return {
            'valid': all(r['valid'] for r in results),
            'results': results,
            'error_count': sum(1 for r in results if not r['valid']),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'rules_applied': len(results)
            }
        }

    def _record_validation(self, result: Dict[str, Any]) -> None:
        """Registra resultado de validación"""
        self.validation_history.append({
            'timestamp': datetime.now().isoformat(),
            'success': result['valid'],
            'error_count': result['error_count']
        })

    def _get_rule_set(self, rule_set: str) -> List[Callable]:
        """Obtiene conjunto de reglas"""
        return self.rules.get(rule_set, self.rules['default'])
