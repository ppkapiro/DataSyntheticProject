import unittest
from ..utils.template_management.validators import FieldValidator

class TestFieldValidator(unittest.TestCase):
    def setUp(self):
        self.validator = FieldValidator()

    def test_string_validation(self):
        """Prueba la validación de campos tipo string"""
        config = {
            'type': 'string',
            'required': True,
            'min_length': 3,
            'max_length': 10,
            'pattern': r'^[A-Za-z]+$'
        }

        # Pruebas válidas
        self.assertTrue(self.validator.validate_field("Test", config))
        self.assertTrue(self.validator.validate_field("Username", config))

        # Pruebas inválidas
        self.assertFalse(self.validator.validate_field("", config))
        self.assertFalse(self.validator.validate_field("Ab", config))
        self.assertFalse(self.validator.validate_field("VeryLongName", config))
        self.assertFalse(self.validator.validate_field("Test123", config))

    def test_number_validation(self):
        """Prueba la validación de campos tipo number"""
        config = {
            'type': 'number',
            'required': True,
            'min_value': 0,
            'max_value': 100,
            'is_integer': True
        }

        # Pruebas válidas
        self.assertTrue(self.validator.validate_field(50, config))
        self.assertTrue(self.validator.validate_field("75", config))

        # Pruebas inválidas
        self.assertFalse(self.validator.validate_field(-1, config))
        self.assertFalse(self.validator.validate_field(150, config))
        self.assertFalse(self.validator.validate_field(25.5, config))
        self.assertFalse(self.validator.validate_field("abc", config))

    def test_required_fields(self):
        """Prueba la validación de campos requeridos"""
        config = {'type': 'string', 'required': True}
        
        self.assertFalse(self.validator.validate_field(None, config))
        self.assertFalse(self.validator.validate_field("", config))
        self.assertTrue(self.validator.validate_field("value", config))

    def test_error_messages(self):
        """Prueba los mensajes de error generados"""
        config = {
            'type': 'string',
            'required': True,
            'min_length': 5
        }

        self.validator.validate_field("abc", config)
        errors = self.validator.get_errors()
        
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any("longitud mínima" in error.lower() for error in errors))
