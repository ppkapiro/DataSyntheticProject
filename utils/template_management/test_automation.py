from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import unittest
from .processing_coordinator import ProcessingCoordinator
from .logging_config import setup_logging

class TestAutomation:
    """Sistema de automatización de pruebas"""

    def __init__(self):
        self.logger = setup_logging('test_automation')
        self.coordinator = ProcessingCoordinator()
        self.test_results = []
        self.test_suites = {
            'mapping': self._run_mapping_tests,
            'validation': self._run_validation_tests,
            'integration': self._run_integration_tests,
            'performance': self._run_performance_tests
        }

    def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Ejecuta una suite de pruebas específica"""
        self.logger.info(f"Iniciando suite de pruebas: {suite_name}")
        
        if test_runner := self.test_suites.get(suite_name):
            try:
                result = test_runner()
                self._record_test_result(suite_name, result)
                return result
            except Exception as e:
                self.logger.error(f"Error en suite {suite_name}: {str(e)}")
                return {'error': str(e)}
        
        return {'error': f'Suite no encontrada: {suite_name}'}

    def _run_mapping_tests(self) -> Dict[str, Any]:
        """Ejecuta pruebas de mapeo"""
        test_cases = self._load_test_cases('mapping')
        results = []

        for test_case in test_cases:
            try:
                # Preparar datos de prueba
                pdf_data = test_case['pdf_data']
                template = test_case['template']
                expected = test_case['expected']

                # Ejecutar mapeo
                result = self.coordinator.process_document(
                    pdf_data,
                    template
                )

                # Validar resultado
                test_result = self._validate_mapping_result(
                    result,
                    expected
                )
                results.append(test_result)

            except Exception as e:
                results.append({
                    'status': 'error',
                    'error': str(e),
                    'test_case': test_case['id']
                })

        return {
            'suite': 'mapping',
            'total_tests': len(test_cases),
            'passed': sum(1 for r in results if r['status'] == 'passed'),
            'failed': sum(1 for r in results if r['status'] == 'failed'),
            'errors': sum(1 for r in results if r['status'] == 'error'),
            'results': results
        }

    def _run_validation_tests(self) -> Dict[str, Any]:
        """Ejecuta pruebas de validación"""
        test_cases = self._load_test_cases('validation')
        results = []

        for test_case in test_cases:
            try:
                # Configurar validación
                content = test_case['content']
                rules = test_case['rules']
                expected = test_case['expected']

                # Ejecutar validación
                validation_result = self.coordinator.content_validator.validate_content(
                    content,
                    rules
                )

                # Verificar resultado
                test_result = self._validate_test_result(
                    validation_result,
                    expected
                )
                results.append(test_result)

            except Exception as e:
                results.append({
                    'status': 'error',
                    'error': str(e),
                    'test_case': test_case['id']
                })

        return {
            'suite': 'validation',
            'results': results,
            'summary': self._generate_test_summary(results)
        }

    def _run_integration_tests(self) -> Dict[str, Any]:
        """Ejecuta pruebas de integración"""
        test_flows = self._load_test_cases('integration')
        results = []

        for flow in test_flows:
            try:
                # Ejecutar flujo completo
                flow_result = self._execute_test_flow(flow['steps'])
                results.append(flow_result)

            except Exception as e:
                results.append({
                    'status': 'error',
                    'flow_id': flow['id'],
                    'error': str(e)
                })

        return {
            'suite': 'integration',
            'flows_tested': len(test_flows),
            'results': results
        }

    def _run_performance_tests(self) -> Dict[str, Any]:
        """Ejecuta pruebas de rendimiento"""
        performance_metrics = {
            'processing_time': [],
            'memory_usage': [],
            'success_rate': []
        }

        try:
            # Ejecutar pruebas de carga
            load_test_result = self._run_load_tests()
            performance_metrics['load'] = load_test_result

            # Ejecutar pruebas de estrés
            stress_test_result = self._run_stress_tests()
            performance_metrics['stress'] = stress_test_result

            return {
                'suite': 'performance',
                'metrics': performance_metrics,
                'status': 'completed'
            }

        except Exception as e:
            return {
                'suite': 'performance',
                'error': str(e),
                'status': 'failed'
            }

    def _record_test_result(self, suite_name: str, 
                           result: Dict[str, Any]) -> None:
        """Registra resultado de pruebas"""
        self.test_results.append({
            'suite': suite_name,
            'timestamp': datetime.now().isoformat(),
            'result': result
        })

    def get_test_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de pruebas"""
        if not self.test_results:
            return {'status': 'No hay resultados de pruebas'}

        stats = {
            'total_suites': len(set(r['suite'] for r in self.test_results)),
            'total_runs': len(self.test_results),
            'by_suite': {}
        }

        for result in self.test_results:
            suite = result['suite']
            if suite not in stats['by_suite']:
                stats['by_suite'][suite] = {
                    'runs': 0,
                    'passed': 0,
                    'failed': 0
                }
            
            suite_stats = stats['by_suite'][suite]
            suite_stats['runs'] += 1
            if 'error' not in result['result']:
                suite_stats['passed'] += 1
            else:
                suite_stats['failed'] += 1

        return stats
