from typing import Dict, Any, List
from pathlib import Path
import unittest
import json
from datetime import datetime
from ...utils.template_management.content_validator import ContentValidator
from ...utils.template_management.field_reconciliation import FieldReconciliation
from ...utils.template_management.logging_config import setup_logging

class DataValidationTests(unittest.TestCase):
    """Pruebas de validación de datos contra plantillas"""

    def setUp(self):
        self.logger = setup_logging('validation_tests')
        self.validator = ContentValidator()
        self.reconciliation = FieldReconciliation()
        self.test_data_path = Path(__file__).parent / 'test_data' / 'validation'
        self.results = []

        # Cargar datos de prueba
        self.test_cases = self._load_test_cases()
        self.template_examples = self._load_templates()

    def test_required_fields(self):
        """Prueba validación de campos requeridos"""
        test_data = self.test_cases.get('required_fields', [])
        
        for case in test_data:
            with self.subTest(case=case['name']):
                result = self.validator.validate_content(
                    case['content'],
                    case['template']
                )
                self.assertEqual(
                    result['is_valid'],
                    case['expected_valid']
                )
                self._record_result('required_fields', case['name'], result)

    def test_data_types(self):
        """Prueba validación de tipos de datos"""
        test_data = self.test_cases.get('type_validation', [])
        
        for case in test_data:
            with self.subTest(case=case['name']):
                result = self.validator.validate_content(
                    case['content'],
                    case['template']
                )
                self._validate_types(result, case['expected_types'])
                self._record_result('type_validation', case['name'], result)

    def test_field_formats(self):
        """Prueba validación de formatos de campo"""
        test_data = self.test_cases.get('format_validation', [])
        
        for case in test_data:
            with self.subTest(case=case['name']):
                result = self.validator.validate_content(
                    case['content'],
                    case['template']
                )
                self._validate_formats(result, case['expected_formats'])
                self._record_result('format_validation', case['name'], result)

    def test_field_relationships(self):
        """Prueba validación de relaciones entre campos"""
        test_data = self.test_cases.get('field_relationships', [])
        
        for case in test_data:
            with self.subTest(case=case['name']):
                result = self.validator.validate_content(
                    case['content'],
                    case['template']
                )
                self._validate_relationships(result, case['expected_relations'])
                self._record_result('relationship_validation', case['name'], result)

    def test_validation_errors(self):
        """Prueba manejo de errores de validación"""
        test_data = self.test_cases.get('validation_errors', [])
        
        for case in test_data:
            with self.subTest(case=case['name']):
                result = self.validator.validate_content(
                    case['content'],
                    case['template']
                )
                self.assertEqual(
                    len(result['errors']),
                    len(case['expected_errors'])
                )
                self._validate_error_messages(result['errors'], case['expected_errors'])
                self._record_result('error_handling', case['name'], result)

    def _validate_types(self, result: Dict[str, Any], 
                       expected_types: Dict[str, str]) -> None:
        """Valida tipos de datos"""
        for field_name, expected_type in expected_types.items():
            self.assertIn(field_name, result['fields'])
            self.assertEqual(
                result['fields'][field_name]['type'],
                expected_type
            )

    def _validate_formats(self, result: Dict[str, Any], 
                         expected_formats: Dict[str, bool]) -> None:
        """Valida formatos de campos"""
        for field_name, should_be_valid in expected_formats.items():
            self.assertIn(field_name, result['fields'])
            self.assertEqual(
                result['fields'][field_name]['format_valid'],
                should_be_valid
            )

    def _validate_relationships(self, result: Dict[str, Any], 
                              expected_relations: List[Dict[str, Any]]) -> None:
        """Valida relaciones entre campos"""
        self.assertEqual(
            len(result.get('relationships', [])),
            len(expected_relations)
        )
        for relation in expected_relations:
            self.assertTrue(
                any(r['type'] == relation['type'] and 
                    r['fields'] == relation['fields']
                    for r in result.get('relationships', []))
            )

    def _validate_error_messages(self, errors: List[str], 
                               expected: List[str]) -> None:
        """Valida mensajes de error"""
        for expected_error in expected:
            self.assertTrue(
                any(expected_error in error for error in errors)
            )

    def _load_test_cases(self) -> Dict[str, Any]:
        """Carga casos de prueba"""
        try:
            with open(self.test_data_path / 'test_cases.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando casos de prueba: {str(e)}")
            return {}

    def _load_templates(self) -> Dict[str, Any]:
        """Carga plantillas de ejemplo"""
        try:
            with open(self.test_data_path / 'templates.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando plantillas: {str(e)}")
            return {}

    def _record_result(self, test_type: str, case_name: str, 
                      result: Dict[str, Any]) -> None:
        """Registra resultado de prueba"""
        self.results.append({
            'timestamp': datetime.now().isoformat(),
            'type': test_type,
            'case': case_name,
            'status': 'passed' if not hasattr(self, '_outcome') 
                     or self._outcome.success else 'failed',
            'result': result
        })

    def tearDown(self):
        """Guarda resultados de pruebas"""
        if self.results:
            output_path = self.test_data_path / 'results'
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = output_path / f'validation_test_results_{timestamp}.json'
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'results': self.results,
                    'summary': {
                        'total': len(self.results),
                        'passed': sum(1 for r in self.results if r['status'] == 'passed'),
                        'failed': sum(1 for r in self.results if r['status'] == 'failed')
                    }
                }, f, indent=2, ensure_ascii=False)
