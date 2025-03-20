import unittest
from ..utils.template_management.field_matcher import FieldMatcher

class TestFieldMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = FieldMatcher()
        self.template_fields = {
            "first_name": {
                "type": "string",
                "required": True,
                "description": "Nombre del paciente"
            },
            "date_of_birth": {
                "type": "date",
                "required": True
            }
        }
        
        self.pdf_fields = {
            "nombre": {
                "value": "John Doe",
                "type": "string",
                "confidence": 0.95
            },
            "fecha_nacimiento": {
                "value": "1990-01-01",
                "type": "date",
                "confidence": 0.90
            }
        }

    def test_find_matches(self):
        """Prueba la búsqueda básica de coincidencias"""
        result = self.matcher.find_matches(self.pdf_fields, self.template_fields)
        
        self.assertIn('matches', result)
        self.assertIn('stats', result)
        self.assertEqual(len(result['matches']), 2)
        
        # Verificar estadísticas
        self.assertEqual(result['stats']['total_template_fields'], 2)
        self.assertEqual(result['stats']['total_pdf_fields'], 2)
        self.assertEqual(result['stats']['matched_fields'], 2)

    def test_name_similarity(self):
        """Prueba la similitud de nombres"""
        similarities = [
            ("first_name", "nombre", True),
            ("date_of_birth", "fecha_nacimiento", True),
            ("address", "direccion_postal", True),
            ("phone", "email", False)
        ]

        for template_name, pdf_name, should_match in similarities:
            score = self.matcher._calculate_name_similarity(template_name, pdf_name)
            if should_match:
                self.assertGreater(score, 0.3)
            else:
                self.assertLess(score, 0.3)

    def test_type_matching(self):
        """Prueba la coincidencia de tipos"""
        test_cases = [
            ({"type": "string"}, {"type": "string"}, True),
            ({"type": "date"}, {"type": "date"}, True),
            ({"type": "number"}, {"type": "string"}, False)
        ]

        for template_info, pdf_info, should_match in test_cases:
            score = self.matcher._calculate_match_score(
                "test", template_info,
                "test", pdf_info
            )
            if should_match:
                self.assertGreater(score, 0.3)
            else:
                self.assertLess(score, 0.3)

if __name__ == '__main__':
    unittest.main()
