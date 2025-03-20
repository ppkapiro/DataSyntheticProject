from typing import Dict, Any, List
from pathlib import Path
import unittest
import json
from datetime import datetime
from ...utils.template_management.pdf_structure_analyzer import PDFStructureAnalyzer
from ...utils.template_management.field_reconciliation import FieldReconciliation
from ...utils.template_management.logging_config import setup_logging

class PDFMappingTests(unittest.TestCase):
    """Pruebas específicas para mapeo PDF-Plantilla"""

    def setUp(self):
        self.logger = setup_logging('pdf_mapping_tests')
        self.analyzer = PDFStructureAnalyzer()
        self.reconciliation = FieldReconciliation()
        self.test_data_path = Path(__file__).parent / 'test_data' / 'pdf_samples'
        self.results = []

    def load_test_data(self) -> Dict[str, Any]:
        """Carga datos de prueba"""
        try:
            with open(self.test_data_path / 'test_cases.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando datos de prueba: {str(e)}")
            return {}

    def test_structure_detection(self):
        """Prueba detección de estructura PDF"""
        test_cases = self.load_test_data()
        
        for case in test_cases.get('structure_tests', []):
            with self.subTest(case=case['name']):
                result = self.analyzer.analyze_document_structure(
                    case['input_data']
                )
                self._validate_structure(result, case['expected'])
                self._record_test_result('structure', case['name'], result)

    def test_field_mapping(self):
        """Prueba mapeo de campos"""
        test_cases = self.load_test_data()
        
        for case in test_cases.get('mapping_tests', []):
            with self.subTest(case=case['name']):
                result = self.reconciliation.reconcile_fields(
                    case['pdf_data'],
                    case['template']
                )
                self._validate_mapping(result, case['expected'])
                self._record_test_result('mapping', case['name'], result)

    def test_error_handling(self):
        """Prueba manejo de errores"""
        test_cases = self.load_test_data()
        
        for case in test_cases.get('error_tests', []):
            with self.subTest(case=case['name']):
                with self.assertRaises(case['expected_error']):
                    self.analyzer.analyze_document_structure(
                        case['invalid_data']
                    )
                self._record_test_result('error_handling', case['name'], {
                    'status': 'passed',
                    'error_type': case['expected_error'].__name__
                })

    def _validate_structure(self, result: Dict[str, Any], 
                          expected: Dict[str, Any]) -> None:
        """Valida resultado de análisis estructural"""
        self.assertEqual(
            len(result.get('sections', [])),
            len(expected.get('sections', []))
        )
        self.assertDictEqual(
            result.get('metadata', {}),
            expected.get('metadata', {})
        )

    def _validate_mapping(self, result: Dict[str, Any], 
                         expected: Dict[str, Any]) -> None:
        """Valida resultado de mapeo"""
        self.assertEqual(
            len(result.get('reconciled_fields', {})),
            len(expected.get('fields', {}))
        )
        self.assertGreaterEqual(
            result.get('quality', {}).get('confidence', 0),
            expected.get('min_confidence', 0)
        )

    def _record_test_result(self, test_type: str, case_name: str, 
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
            result_file = output_path / f'mapping_test_results_{timestamp}.json'
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'results': self.results,
                    'summary': {
                        'total': len(self.results),
                        'passed': sum(1 for r in self.results if r['status'] == 'passed'),
                        'failed': sum(1 for r in self.results if r['status'] == 'failed')
                    }
                }, f, indent=2, ensure_ascii=False)
