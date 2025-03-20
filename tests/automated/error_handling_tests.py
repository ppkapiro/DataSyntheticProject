from typing import Dict, Any, List
import unittest
from pathlib import Path
import json
from datetime import datetime
from ...utils.template_management.error_manager import ErrorManager
from ...utils.template_management.logging_config import setup_logging

class ErrorHandlingTests(unittest.TestCase):
    """Pruebas del sistema de manejo de errores"""

    def setUp(self):
        self.logger = setup_logging('error_tests')
        self.error_manager = ErrorManager()
        self.test_data_path = Path(__file__).parent / 'test_data' / 'errors'
        self.test_results = []

    def test_validation_errors(self):
        """Prueba errores de validación"""
        test_cases = self._load_test_cases('validation_errors')
        
        for case in test_cases:
            with self.subTest(case=case['name']):
                error = self._create_error(case['error_type'], case['data'])
                result = self.error_manager.handle_error(error, case['context'])

                self._validate_error_handling(result, case['expected'])
                self._record_test_result('validation', case['name'], result)

    def test_mapping_errors(self):
        """Prueba errores de mapeo"""
        test_cases = self._load_test_cases('mapping_errors')
        
        for case in test_cases:
            with self.subTest(case=case['name']):
                error = self._create_error(case['error_type'], case['data'])
                result = self.error_manager.handle_error(error, case['context'])

                self._validate_mapping_error(result, case['expected'])
                self._record_test_result('mapping', case['name'], result)

    def test_recovery_attempts(self):
        """Prueba intentos de recuperación"""
        test_cases = self._load_test_cases('recovery')
        
        for case in test_cases:
            with self.subTest(case=case['name']):
                error = self._create_error(case['error_type'], case['data'])
                result = self.error_manager.handle_error(error, case['context'])

                self._validate_recovery(result, case['expected'])
                self._record_test_result('recovery', case['name'], result)

    def test_critical_errors(self):
        """Prueba errores críticos"""
        test_cases = self._load_test_cases('critical_errors')
        
        for case in test_cases:
            with self.subTest(case=case['name']):
                with self.assertRaises(case['expected_exception']):
                    self.error_manager.handle_error(
                        self._create_error(case['error_type'], case['data']),
                        case['context']
                    )
                self._record_test_result('critical', case['name'], {
                    'status': 'passed',
                    'error_type': case['error_type']
                })

    def _create_error(self, error_type: str, data: Dict[str, Any]) -> Exception:
        """Crea una excepción para pruebas"""
        error_classes = {
            'validation': ValueError,
            'mapping': KeyError,
            'type': TypeError,
            'critical': RuntimeError
        }
        return error_classes[error_type](json.dumps(data))

    def _validate_error_handling(self, result: Dict[str, Any], 
                               expected: Dict[str, Any]) -> None:
        """Valida el manejo de errores"""
        self.assertEqual(result['error_type'], expected['type'])
        self.assertEqual(result['recoverable'], expected['recoverable'])
        if 'error_data' in expected:
            self.assertDictEqual(result['error_data'], expected['error_data'])

    def _validate_mapping_error(self, result: Dict[str, Any], 
                              expected: Dict[str, Any]) -> None:
        """Valida errores de mapeo"""
        self.assertEqual(result['error_type'], 'mapping_error')
        if expected.get('should_recover'):
            self.assertIn('recovery_attempt', result)
            self.assertEqual(
                result['recovery_attempt']['success'],
                expected['recovery_success']
            )

    def _validate_recovery(self, result: Dict[str, Any], 
                         expected: Dict[str, Any]) -> None:
        """Valida intentos de recuperación"""
        if expected['recoverable']:
            self.assertTrue(result['recovered'])
            self.assertGreaterEqual(
                result['confidence'],
                expected['min_confidence']
            )
        else:
            self.assertFalse(result.get('recovered', False))

    def _load_test_cases(self, category: str) -> List[Dict[str, Any]]:
        """Carga casos de prueba"""
        try:
            with open(self.test_data_path / f'{category}.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando casos de prueba: {str(e)}")
            return []

    def _record_test_result(self, test_type: str, case_name: str, 
                          result: Dict[str, Any]) -> None:
        """Registra resultado de prueba"""
        self.test_results.append({
            'timestamp': datetime.now().isoformat(),
            'type': test_type,
            'case': case_name,
            'status': 'passed' if not hasattr(self, '_outcome') 
                     or self._outcome.success else 'failed',
            'result': result
        })

    def tearDown(self):
        """Guarda resultados de pruebas"""
        if self.test_results:
            output_path = self.test_data_path / 'results'
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = output_path / f'error_test_results_{timestamp}.json'
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'results': self.test_results,
                    'summary': {
                        'total': len(self.test_results),
                        'passed': sum(1 for r in self.test_results if r['status'] == 'passed'),
                        'failed': sum(1 for r in self.test_results if r['status'] == 'failed')
                    }
                }, f, indent=2, ensure_ascii=False)
