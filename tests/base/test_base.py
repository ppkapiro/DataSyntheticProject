from typing import Dict, Any, Optional, List
from pathlib import Path
import unittest
import json
from datetime import datetime
from ...utils.template_management.logging_config import setup_logging

class BaseTestCase(unittest.TestCase):
    """Clase base para todas las pruebas del sistema"""

    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        self.logger = setup_logging('base_test')
        self.test_data_path = Path(__file__).parent.parent / 'test_data'
        self.results = []
        self.start_time = datetime.now()

    def load_test_data(self, category: str) -> Dict[str, Any]:
        """Carga datos de prueba por categoría"""
        try:
            file_path = self.test_data_path / f'{category}.json'
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando datos de prueba: {str(e)}")
            return {}

    def record_result(self, test_type: str, 
                     case_name: str, 
                     result: Dict[str, Any],
                     extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Registra resultado de prueba con metadata"""
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'type': test_type,
            'case': case_name,
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'status': 'passed' if not hasattr(self, '_outcome') 
                     or self._outcome.success else 'failed',
            'result': result
        }

        if extra_data:
            test_result.update(extra_data)

        self.results.append(test_result)

    def validate_result(self, result: Dict[str, Any], 
                       expected: Dict[str, Any],
                       validation_type: str = 'exact') -> None:
        """Valida resultados con diferentes estrategias"""
        if validation_type == 'exact':
            self.assertDictEqual(result, expected)
        elif validation_type == 'subset':
            for key, value in expected.items():
                self.assertIn(key, result)
                self.assertEqual(result[key], value)
        elif validation_type == 'type_check':
            for key, type_info in expected.items():
                self.assertIn(key, result)
                self.assertIsInstance(result[key], type_info['type'])
                if 'constraints' in type_info:
                    self._validate_constraints(result[key], type_info['constraints'])

    def _validate_constraints(self, value: Any, 
                            constraints: Dict[str, Any]) -> None:
        """Valida restricciones específicas de valor"""
        for constraint, expected in constraints.items():
            if constraint == 'min':
                self.assertGreaterEqual(value, expected)
            elif constraint == 'max':
                self.assertLessEqual(value, expected)
            elif constraint == 'length':
                self.assertEqual(len(value), expected)
            elif constraint == 'pattern':
                self.assertRegex(str(value), expected)

    def save_results(self, category: str) -> None:
        """Guarda resultados de pruebas"""
        if self.results:
            output_path = self.test_data_path / 'results'
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = output_path / f'{category}_test_results_{timestamp}.json'
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'results': self.results,
                    'summary': self._generate_summary()
                }, f, indent=2, ensure_ascii=False)

    def _generate_summary(self) -> Dict[str, Any]:
        """Genera resumen de resultados de pruebas"""
        return {
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r['status'] == 'passed'),
            'failed': sum(1 for r in self.results if r['status'] == 'failed'),
            'total_duration': sum(r['duration'] for r in self.results),
            'timestamp': datetime.now().isoformat()
        }

    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Guardar resultados si es la última prueba de la clase
        if not any(test.startswith('test_') for test in dir(self)):
            self.save_results(self.__class__.__name__.lower())
