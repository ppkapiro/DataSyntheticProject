import unittest
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from utils.template_management.pdf_template_connector import PDFTemplateConnector

class TestPDFTemplateConnector(unittest.TestCase):
    def setUp(self):
        self.connector = PDFTemplateConnector()
        
        # Datos de prueba: PDF
        self.pdf_data = {
            'fields': {
                'name': {
                    'value': 'John Doe',
                    'type': 'string',
                    'confidence': 0.95
                },
                'birth_date': {
                    'value': '1990-01-01',
                    'type': 'date',
                    'confidence': 0.90
                }
            }
        }
        
        # Datos de prueba: Plantilla
        self.template = {
            'nombre_archivo': 'test_template',
            'tipo_documento': 'patient_record',
            'campos': {
                'nombre': {
                    'type': 'string',
                    'required': True
                },
                'fecha_nacimiento': {
                    'type': 'date',
                    'required': True
                }
            }
        }

    def test_basic_connection(self):
        """Prueba la conexión básica entre PDF y plantilla"""
        result = self.connector.connect_data(self.pdf_data, self.template)
        self.assertIn('campos', result)
        self.assertIn('metadata', result)
        self.assertEqual(result['nombre_archivo'], 'test_template')

    def test_field_mapping(self):
        """Prueba el mapeo de campos"""
        result = self.connector.connect_data(self.pdf_data, self.template)
        
        # Verificar mapeo de campos
        self.assertIn('nombre', result['campos'])
        self.assertIn('fecha_nacimiento', result['campos'])

    def test_validation_report(self):
        """Prueba la generación del reporte de validación"""
        self.connector.connect_data(self.pdf_data, self.template)
        report = self.connector.get_validation_report()
        
        self.assertIn('total_campos', report)
        self.assertIn('campos_validos', report)
        self.assertIn('confianza_promedio', report)

    def test_missing_fields(self):
        """Prueba el manejo de campos faltantes"""
        # PDF sin todos los campos
        incomplete_pdf = {
            'fields': {
                'name': {
                    'value': 'John Doe',
                    'type': 'string',
                    'confidence': 0.95
                }
            }
        }
        
        result = self.connector.connect_data(incomplete_pdf, self.template)
        self.assertIsNone(result['campos']['fecha_nacimiento']['value'])
        
        # Verificar reporte
        report = self.connector.get_validation_report()
        self.assertGreater(len(report['campos_faltantes']), 0)

    def test_confidence_scores(self):
        """Prueba los niveles de confianza"""
        result = self.connector.connect_data(self.pdf_data, self.template)
        
        # Verificar confianza en metadata
        self.assertIn('confidence', result['metadata'])
        self.assertGreater(result['metadata']['confidence'], 0)
        
        # Verificar reporte
        report = self.connector.get_validation_report()
        self.assertGreater(report['confianza_promedio'], 0)

if __name__ == '__main__':
    unittest.main()
