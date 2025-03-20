import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
import os
sys.path.append(str(Path(__file__).parent.parent))

from src.nlp_integration import NLPAnalyzer, get_nlp_analyzer

class MockLanguageServiceClient:
    """Cliente simulado para pruebas"""
    def analyze_entities(self, request):
        return Mock(entities=[
            Mock(
                name="Google Cloud",
                type_=1,  # ORGANIZATION en language_v1.Entity.Type
                salience=0.8,
                metadata={}
            )
        ])
    
    def analyze_sentiment(self, request):
        return Mock(
            document_sentiment=Mock(
                score=0.8,
                magnitude=0.9
            )
        )
    
    def analyze_syntax(self, request):
        return Mock(tokens=[
            Mock(
                text=Mock(content="test"),
                part_of_speech=Mock(tag=1),
                dependency_edge=Mock(label=1)
            )
        ])
    
    def classify_text(self, request):
        return Mock(categories=[
            Mock(
                name="technology",
                confidence=0.9
            )
        ])

@patch('google.cloud.language_v1.LanguageServiceClient', MockLanguageServiceClient)
class TestNLPAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = NLPAnalyzer()
        self.test_text = "Google Cloud es una plataforma excelente para NLP."

    def test_analyze_text_success(self):
        result = self.analyzer.analyze_text(self.test_text)
        
        # Verificar estructura del resultado
        self.assertIn('entities', result)
        self.assertIn('sentiment', result)
        self.assertIn('syntax', result)
        self.assertIn('categories', result)
        
        # Verificar contenido
        self.assertTrue(len(result['entities']) > 0)
        self.assertIn('score', result['sentiment'])
        self.assertIn('magnitude', result['sentiment'])

    def test_error_handling(self):
        with patch.object(self.analyzer, '_analyze_entities', side_effect=Exception('Test error')):
            result = self.analyzer.analyze_text(self.test_text)
            self.assertEqual(result, {})

    def test_missing_credentials(self):
        # Simular ausencia de credenciales
        with patch.dict(os.environ, {}, clear=True):
            analyzer = NLPAnalyzer()
            result = analyzer.analyze_text(self.test_text)
            self.assertIsInstance(result, dict)

if __name__ == '__main__':
    unittest.main()
