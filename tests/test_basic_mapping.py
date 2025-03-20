import unittest
from pathlib import Path
from ..utils.template_management.field_matcher import FieldMatcher
from ..utils.template_management.field_analyzer import FieldAnalyzer

class TestBasicMapping(unittest.TestCase):
    def setUp(self):
        self.matcher = FieldMatcher()
        self.template = {
            "nombre_archivo": "Test_Template",
            "campos": {
                "nombre": {
                    "type": "string",
                    "required": True,
                    "description": "Nombre del paciente"
                },
                "fecha_nacimiento": {
                    "type": "date",
                    "required": True
                }
            }
        }
        
        self.pdf_content = {
            "fields": {
                "name": {
                    "value": "John Doe",
                    "type": "string",
                    "confidence": 0.95
                },
                "birth_date": {
                    "value": "1990-01-01",
                    "type": "date",
                    "confidence": 0.90
                }
            }
        }

    def test_basic_field_detection(self):
        """Prueba detección básica de campos"""
        result = self.matcher.find_matches(
            self.pdf_content["fields"], 
            self.template["campos"]
        )
        
        self.assertTrue(result['matches'])
        self.assertEqual(result['stats']['total_template_fields'], 2)

    def test_name_matching(self):
        """Prueba coincidencia de nombres similares"""
        matches = result = self.matcher.find_matches(
            self.pdf_content["fields"], 
            self.template["campos"]
        )['matches']

        self.assertIn('nombre', matches)
        self.assertEqual(matches['nombre']['pdf_field'], 'name')

    def test_confidence_scores(self):
        """Prueba cálculo de confianza"""
        result = self.matcher.find_matches(
            self.pdf_content["fields"], 
            self.template["campos"]
        )
        
        for match in result['matches'].values():
            self.assertGreaterEqual(match['confidence'], 0.5)
