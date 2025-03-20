import unittest
from pathlib import Path
from ..utils.template_management.field_analyzer import FieldAnalyzer
from ..utils.template_management.validators import FieldValidator
from ..utils.template_management.realtime_validator import RealtimeValidator

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.analyzer = FieldAnalyzer()
        self.validator = FieldValidator()
        self.realtime_validator = RealtimeValidator()

    def test_analyzer_validator_integration(self):
        """Prueba la integración entre el analizador y el validador"""
        # Simular análisis de campo
        field_config = {
            'type': 'string',
            'required': True,
            'min_length': 3,
            'max_length': 10
        }

        # Verificar que el validador acepta la configuración del analizador
        self.assertTrue(self.validator.validate_field("Test", field_config))
        self.assertFalse(self.validator.validate_field("Ab", field_config))

    def test_realtime_validation_flow(self):
        """Prueba el flujo completo de validación en tiempo real"""
        validation_results = []
        
        def validation_callback(result):
            validation_results.append(result)

        # Registrar callback
        self.realtime_validator.register_callback('test_field', validation_callback)

        # Realizar validación
        result = self.realtime_validator.validate('test_field', "Test", {
            'type': 'string',
            'required': True,
            'min_length': 3
        })

        # Verificar resultado y callback
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(validation_results), 1)
        self.assertTrue(validation_results[0]['is_valid'])

    def test_error_message_integration(self):
        """Prueba la integración de mensajes de error personalizados"""
        field_config = {
            'type': 'number',
            'required': True,
            'min_value': 0,
            'max_value': 100
        }

        self.validator.validate_field(-1, field_config)
        errors = self.validator.get_errors()

        self.assertTrue(any("valor mínimo" in error.lower() for error in errors))
