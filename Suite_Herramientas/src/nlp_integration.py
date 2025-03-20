import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from functools import lru_cache
from google.cloud import language_v1
from google.cloud import translate_v2 as translate
from google.api_core.exceptions import GoogleAPIError
import sys

# Forzar UTF-8 en la salida estándar
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPAnalyzer:
    """Clase para manejar el análisis de texto usando Google Cloud Natural Language API"""
    
    # Constantes de la clase
    MIN_TOKENS_FOR_CLASSIFICATION = 20
    MIN_TOKENS_REQUIRED = 20
    
    def __init__(self, credentials_path: Optional[str] = None):
        # Configurar logging antes de cualquier otra operación
        self._setup_logging()
        
        try:
            if credentials_path:
                credentials_path = self._resolve_credentials_path(credentials_path)
            else:
                credentials_path = self._get_default_credentials()
                
            if not credentials_path:
                raise ValueError("No se encontró archivo de credenciales válido")
                
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)
            self.logger.info(f"Usando credenciales de: {credentials_path}")
            
            self.client = language_v1.LanguageServiceClient()
            self.translate_client = translate.Client()
            self.is_available = True
            self.logger.info("Cliente NLP inicializado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al inicializar el cliente NLP: {e}")
            self.is_available = False
            self.client = None

    def _get_project_root(self) -> Path:
        """Obtiene la ruta raíz del proyecto"""
        return Path(__file__).resolve().parent.parent

    def _setup_logging(self):
        """Configura el logging para la clase y se asegura de que el directorio de logs exista"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configurar directorio de logs
        logs_dir = self._get_project_root() / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar archivo de log
        log_file = logs_dir / "nlp_analysis.log"
        
        # Verificar si ya existe un handler para este archivo
        if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(log_file) 
                  for h in self.logger.handlers):
            handler = logging.FileHandler(str(log_file))
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
        
        self.logger.info(f"Logging configurado en: {log_file}")

    def _resolve_credentials_path(self, credentials_path: str) -> Optional[Path]:
        """Resuelve la ruta del archivo de credenciales"""
        path = Path(credentials_path)
        if not path.is_absolute():
            # Probar diferentes ubicaciones relativas
            locations = [
                Path(__file__).parent.parent / credentials_path,
                Path(__file__).parent.parent / 'config' / credentials_path,
                Path.cwd() / credentials_path
            ]
            
            for loc in locations:
                if loc.exists():
                    self.logger.info(f"Credenciales encontradas en: {loc}")
                    return loc
            
            self.logger.error(f"No se encontró el archivo de credenciales en ninguna ubicación")
            return None
        
        return path if path.exists() else None

    def _get_default_credentials(self) -> Optional[Path]:
        """Busca el archivo de credenciales por defecto"""
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'nlp_config.json'
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    if cred_path := config.get('credentials_path'):
                        return self._resolve_credentials_path(cred_path)
        except Exception as e:
            self.logger.error(f"Error al cargar configuración: {e}")
        return None

    def _validate_text_length(self, text: str) -> bool:
        """
        Valida si el texto tiene suficientes tokens para análisis.
        
        Args:
            text: Texto a validar
            
        Returns:
            bool: True si el texto tiene suficientes tokens
        """
        tokens = text.split()
        token_count = len(tokens)
        self.logger.info(f"Texto contiene {token_count} tokens")
        return token_count >= self.MIN_TOKENS_REQUIRED

    @lru_cache(maxsize=100)
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analiza el texto y retorna resultados del análisis"""
        if not self.is_available:
            self.logger.warning("Cliente NLP no disponible - retornando resultado vacío")
            return {}
            
        try:
            document = self._create_document(text)
            
            # Realizar análisis básicos siempre
            results = {
                'entities': self._analyze_entities(document),
                'sentiment': self._analyze_sentiment(document),
                'syntax': self._analyze_syntax(document)
            }
            
            # Verificar longitud para clasificación
            if self._validate_text_length(text):
                results['categories'] = self._classify_content(document)
            else:
                self.logger.warning(
                    f"Texto demasiado corto para clasificación (mínimo {self.MIN_TOKENS_REQUIRED} tokens). "
                    "Se omitirá la clasificación de contenido."
                )
                results['categories'] = []
            
            return results
            
        except GoogleAPIError as e:
            self.logger.error(f"Error en el análisis NLP: {e}")
            return {}

    def _create_document(self, text: str) -> language_v1.Document:
        """Crea un documento para análisis"""
        return language_v1.Document(
            content=text, 
            type_=language_v1.Document.Type.PLAIN_TEXT
        )

    def _analyze_entities(self, document: language_v1.Document) -> List[Dict[str, Any]]:
        """Analiza las entidades en el documento"""
        try:
            response = self.client.analyze_entities(request={'document': document})
            return [
                {
                    'name': entity.name,
                    'type': language_v1.Entity.Type(entity.type_).name,
                    'salience': entity.salience,
                    'metadata': dict(entity.metadata)
                } 
                for entity in response.entities
            ]
        except GoogleAPIError as e:
            self.logger.error(f"Error en análisis de entidades: {e}")
            return []

    def _analyze_sentiment(self, document: language_v1.Document) -> Dict[str, float]:
        """Analiza el sentimiento del documento"""
        try:
            response = self.client.analyze_sentiment(request={'document': document})
            return {
                'score': response.document_sentiment.score,
                'magnitude': response.document_sentiment.magnitude
            }
        except GoogleAPIError as e:
            self.logger.error(f"Error en análisis de sentimiento: {e}")
            return {'score': 0.0, 'magnitude': 0.0}

    def _analyze_syntax(self, document: language_v1.Document) -> List[Dict[str, str]]:
        """Analiza la sintaxis del texto"""
        try:
            response = self.client.analyze_syntax(request={'document': document})
            return [
                {
                    'text': token.text.content,
                    'part_of_speech': language_v1.PartOfSpeech.Tag(token.part_of_speech.tag).name,
                    'dependency_edge': token.dependency_edge.label.name
                }
                for token in response.tokens
            ]
        except GoogleAPIError as e:
            self.logger.error(f"Error en análisis de sintaxis: {e}")
            return []

    def _translate_text(self, text: str, target_language: str = 'en') -> Tuple[str, bool]:
        """
        Traduce el texto al idioma especificado.
        
        Returns:
            Tuple[str, bool]: (texto traducido, éxito de la traducción)
        """
        try:
            result = self.translate_client.translate(
                text,
                target_language=target_language
            )
            translated_text = result['translatedText']
            self.logger.info(f"Texto traducido a '{target_language}' correctamente")
            return translated_text, True
        except Exception as e:
            self.logger.error(f"Error al traducir el texto: {e}")
            return text, False

    def _has_sufficient_tokens(self, text: str) -> bool:
        """
        Verifica si el texto tiene suficientes tokens para clasificación.
        
        Args:
            text: Texto a verificar
            
        Returns:
            bool: True si hay suficientes tokens, False en caso contrario
        """
        tokens = text.split()
        token_count = len(tokens)
        self.logger.info(f"Número de tokens en el texto: {token_count}")
        return token_count >= self.MIN_TOKENS_FOR_CLASSIFICATION

    def _classify_content(self, document: language_v1.Document) -> List[Dict[str, Any]]:
        """Clasifica el contenido del documento, traduciendo si es necesario"""
        try:
            # Verificar tokens antes del primer intento
            if not self._has_sufficient_tokens(document.content):
                self.logger.warning("Texto original demasiado corto para clasificación")
                return []
                
            response = self.client.classify_text(request={'document': document})
            return [
                {
                    'name': category.name,
                    'confidence': category.confidence,
                    'translated': False
                }
                for category in response.categories
            ]
        except GoogleAPIError as e:
            error_msg = str(e).lower()
            if "language is not supported" in error_msg or "not supported" in error_msg:
                self.logger.info("Idioma no soportado, intentando traducción al inglés")
                translated_text, success = self._translate_text(document.content)
                
                if success and self._has_sufficient_tokens(translated_text):
                    try:
                        new_document = language_v1.Document(
                            content=translated_text,
                            type_=language_v1.Document.Type.PLAIN_TEXT
                        )
                        response = self.client.classify_text(request={'document': new_document})
                        return [
                            {
                                'name': category.name,
                                'confidence': category.confidence,
                                'translated': True
                            }
                            for category in response.categories
                        ]
                    except GoogleAPIError as e2:
                        self.logger.error(f"Error en clasificación tras traducción: {e2}")
                else:
                    self.logger.warning(
                        "El texto traducido no tiene suficientes tokens para clasificación"
                        if success else "No se pudo traducir el texto"
                    )
            
            self.logger.error(f"Error en clasificación de contenido: {e}")
            return []

def get_nlp_analyzer(config_path: str = '../config/nlp_config.json') -> Optional[NLPAnalyzer]:
    """Factory function para crear una instancia de NLPAnalyzer"""
    try:
        config_file = Path(__file__).parent.joinpath(config_path).resolve()
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                credentials_path = config.get('credentials_path')
                logger.info(f"Configuración cargada, usando credenciales: {credentials_path}")
                return NLPAnalyzer(credentials_path)
        
        # Si no hay configuración, intentar usar credenciales por defecto
        default_credentials = Path(__file__).parent.parent / "herramientas-tecnicas-15689b8346a2.json"
        if default_credentials.exists():
            logger.info(f"Usando credenciales por defecto: {default_credentials}")
            return NLPAnalyzer(str(default_credentials))
            
        return NLPAnalyzer()
    except Exception as e:
        logger.error(f"Error al inicializar NLPAnalyzer: {e}")
        return None

def test_analyzer(credentials_path: Optional[str] = None):
    """Función de prueba para el analizador NLP"""
    try:
        # Asegurar que existe la carpeta de logs
        logs_dir = Path(__file__).parent.parent / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        # Inicializar analizador
        analyzer = NLPAnalyzer(credentials_path)
        if not analyzer.is_available:
            print("[ERROR] No se pudo inicializar el analizador NLP")
            return
            
        # Texto de prueba
        test_text = "Google Cloud Natural Language API ofrece potentes herramientas de análisis de texto."
        
        # Realizar análisis
        print("\n[INFO] Realizando análisis de texto...")
        result = analyzer.analyze_text(test_text)
        
        # Mostrar resultados
        print("\n[OK] Resultados del análisis:")
        for key, value in result.items():
            print(f"\n{key.upper()}:")
            print(json.dumps(value, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"\n[ERROR] Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_analyzer()
