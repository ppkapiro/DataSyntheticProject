from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import unittest
import json
from ...utils.template_management.processing_coordinator import ProcessingCoordinator
from ...utils.template_management.error_manager import ErrorManager
from ...utils.template_management.logging_config import setup_logging

class AutomatedTestSuite:
    """Sistema de pruebas automatizadas"""

    def __init__(self):
        self.logger = setup_logging('test_suite')
        self.coordinator = ProcessingCoordinator()
        self.error_manager = ErrorManager()
        self.test_results = {}
        self.test_data_path = Path(__file__).parent / 'test_data'
        self.test_cases = self._load_test_cases()

    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecuta todas las suites de pruebas"""
        self.logger.info("Iniciando ejecución de pruebas automatizadas")
        
        results = {
            'mapping_tests': self._run_mapping_tests(),
            'validation_tests': self._run_validation_tests(),
            'integration_tests': self._run_integration_tests(),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_count': len(self.test_cases),
                'duration': 0
            }
        }

        self._save_test_results(results)
        return results

    def _load_test_cases(self) -> Dict[str, Any]:
        """Carga casos de prueba desde archivos"""
        try:
            test_cases = {}
            for test_file in self.test_data_path.glob('*.json'):
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_cases[test_file.stem] = json.load(f)
            return test_cases
        except Exception as e:
            self.logger.error(f"Error cargando casos de prueba: {str(e)}")
            return {}

    def _run_mapping_tests(self) -> Dict[str, Any]:
        """Ejecuta pruebas de mapeo"""
        mapping_results = {
            'passed': [],
            'failed': [],
            'errors': []
        }

        test_cases = self.test_cases.get('mapping', {})
        for case_name, case_data in test_cases.items():
            try:
                result = self.coordinator.process_document(
                    case_data['input'],
                    case_data['template']
                )
                
                if self._validate_mapping_result(result, case_data['expected']):
                    mapping_results['passed'].append(case_name)
                else:
                    mapping_results['failed'].append({
                        'case': case_name,
                        'reason': 'Resultado no coincide con esperado'
                    })
            except Exception as e:
                mapping_results['errors'].append({
                    'case': case_name,
                    'error': str(e)
                })

        return mapping_results

    def _run_validation_tests(self) -> Dict[str, Any]:
        """Ejecuta pruebas de validación"""
        test_cases = self.test_cases.get('validation', {})
        validation_results = {
            'passed': [],
            'failed': [],
            'errors': []
        }

        for case_name, case_data in test_cases.items():
            try:
                result = self.coordinator.content_validator.validate_content(
                    case_data['content'],
                    case_data['rules']
                )
                
                if self._compare_validation_results(result, case_data['expected']):
                    validation_results['passed'].append(case_name)
                else:
                    validation_results['failed'].append({
                        'case': case_name,
                        'details': 'Validación no coincide'
                    })
            except Exception as e:
                validation_results['errors'].append({
                    'case': case_name,
                    'error': str(e)
                })

        return validation_results

    def _run_integration_tests(self) -> Dict[str, Any]:
        """Ejecuta pruebas de integración"""
        test_flows = self.test_cases.get('integration', {})
        integration_results = {
            'passed': [],
            'failed': [],
            'errors': []
        }

        for flow_name, flow_data in test_flows.items():
            try:
                result = self._execute_test_flow(flow_data['steps'])
                if result['success']:
                    integration_results['passed'].append(flow_name)
                else:
                    integration_results['failed'].append({
                        'flow': flow_name,
                        'step': result['failed_step']
                    })
            except Exception as e:
                integration_results['errors'].append({
                    'flow': flow_name,
                    'error': str(e)
                })

        return integration_results

    def _execute_test_flow(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ejecuta un flujo de prueba completo"""
        context = {}
        
        for step in steps:
            try:
                result = self._execute_step(step, context)
                if not result['success']:
                    return {
                        'success': False,
                        'failed_step': step['name'],
                        'error': result['error']
                    }
                context.update(result['context'])
            except Exception as e:
                return {
                    'success': False,
                    'failed_step': step['name'],
                    'error': str(e)
                }

        return {'success': True, 'context': context}

    def _save_test_results(self, results: Dict[str, Any]) -> None:
        """Guarda resultados de pruebas"""
        output_path = self.test_data_path / 'results'
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = output_path / f'test_results_{timestamp}.json'
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
