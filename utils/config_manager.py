import os
import json
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Union

# Importación condicional de yaml
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logging.warning("pyyaml no está instalado. Se usará JSON como formato alternativo.")
    logging.warning("Para habilitar YAML ejecute: pip install pyyaml")

class ConfigManager:
    """
    Gestor centralizado de configuración para el sistema Notefy IA.
    
    Esta clase maneja todas las configuraciones del sistema, incluyendo rutas,
    parámetros y ajustes de los diferentes módulos. Permite cargar configuraciones
    desde un archivo YAML o utilizar valores predeterminados.
    """
    
    # Instancia singleton
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el gestor de configuración si aún no ha sido inicializado"""
        if self._initialized:
            return
            
        # Configurar logging
        self._configure_logging()
        
        # Ruta base del proyecto
        self.project_root = Path(os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'
        )))
        
        # Ruta al archivo de configuración
        self.config_file = self.project_root / 'config.yaml'
        
        # Cargar configuración
        self.config = self._load_config()
        
        # Flag de inicialización
        self._initialized = True
        
        # Log de inicialización
        logging.info(f"ConfigManager inicializado. Ruta base: {self.project_root}")
    
    def _configure_logging(self):
        """Configura el sistema de logging"""
        log_dir = Path(os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'logs'
        )))
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"notefy_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde archivo"""
        default_config = self._get_default_config()
        
        # Si YAML está disponible, intentar cargar .yaml
        if YAML_AVAILABLE:
            yaml_path = self.project_root / 'config.yaml'
            if yaml_path.exists():
                try:
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f)
                except Exception as e:
                    logging.error(f"Error cargando YAML: {e}")

        # Intentar JSON como respaldo
        json_path = self.project_root / 'config.json'
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error cargando JSON: {e}")

        return default_config
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Combina dos diccionarios de manera recursiva"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Define la configuración predeterminada"""
        return {
            'paths': {
                'data': str(self.project_root / 'Data'),
                'templates': {
                    'base': str(self.project_root / 'templates'),
                    'campos_global': str(self.project_root / 'templates' / 'Campos Master Global'),
                    'campos_codigos': str(self.project_root / 'templates' / 'Campos Codigos'),
                    'archivos_campos': str(self.project_root / 'templates' / 'archivos de campos')
                },
                'output': str(self.project_root / 'output'),
                'temp': str(self.project_root / 'temp'),
                'logs': str(self.project_root / 'logs')
            },
            'pdf_extractor': {
                'use_ai': True,
                'min_quality_threshold': 80,
                'ocr_language': 'spa+eng',
                'ocr_config': '--psm 1 --oem 3',
                'cache_results': True
            },
            'data_generation': {
                'default_records': 10,
                'max_records': 1000,
                'locale': 'es_ES',
                'seed': None  # Aleatorio por defecto
            },
            'template_manager': {
                'validate_on_load': True,
                'auto_fix_templates': True,
                'supported_formats': ['json', 'yaml', 'yml']
            },
            'system': {
                'debug_mode': False,
                'term_width': 80,
                'use_colors': True,
                'auto_backup': True,
                'backup_interval_days': 7
            }
        }
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Carga la configuración utilizando una instancia (método de conveniencia)"""
        instance = ConfigManager()
        return instance.config
    
    @staticmethod
    def check_credentials(service_name='google_cloud_vision') -> bool:
        """Verifica si las credenciales para un servicio específico están configuradas"""
        instance = ConfigManager()
        
        if service_name == 'google_cloud_vision':
            if 'ai_services' in instance.config and 'google_cloud_vision' in instance.config['ai_services']:
                credentials_file = instance.config['ai_services']['google_cloud_vision']['credentials_file']
                credentials_path = instance.project_root / credentials_file
                return credentials_path.exists()
        
        elif service_name == 'amazon_textract':
            # Verificar credenciales de AWS para Textract
            if 'ai_services' in instance.config and 'amazon_textract' in instance.config['ai_services']:
                return instance.config['ai_services']['amazon_textract']['enabled']
            
            # Verificar variables de entorno de AWS como alternativa
            aws_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
            return all(var in os.environ for var in aws_env_vars)
            
        return False
    
    @staticmethod
    def check_cloud_vision_configuration():
        """Verifica y valida la configuración de Google Cloud Vision"""
        config = ConfigManager.load_config()
        
        # Verificar que el config tiene la estructura correcta
        if not config:
            print("Error: No se pudo cargar la configuración")
            return False
            
        # Verificar que la sección de AI services existe
        if 'ai_services' not in config:
            print("Error: Sección 'ai_services' no encontrada en la configuración")
            return False
            
        # Verificar que la configuración de Google Cloud Vision existe
        if 'google_cloud_vision' not in config['ai_services']:
            print("Error: Configuración de Google Cloud Vision no encontrada")
            return False
        
        gcv_config = config['ai_services']['google_cloud_vision']
        
        # Verificar que Google Cloud Vision está habilitado
        if not gcv_config.get('enabled', False):
            print("Error: Google Cloud Vision no está habilitado")
            return False
            
        # Verificar que existe el archivo de credenciales
        if 'credentials_file' not in gcv_config:
            print("Error: No se especificó archivo de credenciales para Google Cloud Vision")
            return False
            
        # Lista de posibles ubicaciones para el archivo de credenciales
        credentials_file = gcv_config['credentials_file']
        project_root = Path(__file__).parent.parent
        
        possible_paths = [
            Path(credentials_file),
            project_root / credentials_file,
            project_root / "config" / credentials_file,
            project_root / "credentials" / credentials_file
        ]
        
        for path in possible_paths:
            if path.exists():
                # Verificar formato del archivo JSON
                try:
                    with open(path, 'r') as f:
                        import json
                        credentials = json.load(f)
                        
                        # Verificar campos mínimos
                        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
                        if all(field in credentials for field in required_fields):
                            print(f"✅ Archivo de credenciales de Google Cloud Vision válido: {path}")
                            return True
                        else:
                            print(f"❌ Archivo de credenciales inválido (faltan campos requeridos): {path}")
                            return False
                            
                except Exception as e:
                    print(f"❌ Error al leer archivo de credenciales: {str(e)}")
                    return False
        
        print("❌ No se encontró archivo de credenciales de Google Cloud Vision")
        return False
    
    def get_config(self) -> Dict[str, Any]:
        """Devuelve la configuración completa"""
        return self.config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración mediante una ruta de claves separadas por puntos.
        
        Ejemplo:
        get('paths.data') -> devuelve el valor de self.config['paths']['data']
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logging.warning(f"Configuración no encontrada: {key_path}, usando valor predeterminado: {default}")
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Establece un valor de configuración mediante una ruta de claves separadas por puntos.
        Devuelve True si se estableció correctamente, False en caso contrario.
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navegar hasta el penúltimo nivel
        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        
        # Establecer el valor
        try:
            config[keys[-1]] = value
            return True
        except Exception as e:
            logging.error(f"Error al establecer configuración {key_path}: {str(e)}")
            return False
    
    def save_config(self) -> bool:
        """Guarda la configuración actual en el archivo YAML"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logging.info(f"Configuración guardada en {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"Error al guardar configuración: {str(e)}")
            return False
    
    def get_base_path(self) -> Path:
        """Devuelve la ruta base del proyecto"""
        return Path(self.get('paths.data', str(self.project_root / 'Data')))
    
    def get_templates_path(self) -> Path:
        """Devuelve la ruta base de plantillas"""
        return Path(self.get('paths.templates.base', str(self.project_root / 'templates')))
    
    def get_output_path(self) -> Path:
        """Devuelve la ruta de salida"""
        return Path(self.get('paths.output', str(self.project_root / 'output')))
    
    def get_global_templates_path(self) -> Path:
        """Devuelve la ruta de plantillas globales"""
        return Path(self.get('paths.templates.campos_global', 
                            str(self.project_root / 'templates' / 'Campos Master Global')))
    
    def get_code_templates_path(self) -> Path:
        """Devuelve la ruta de plantillas de código"""
        return Path(self.get('paths.templates.campos_codigos',
                            str(self.project_root / 'templates' / 'Campos Codigos')))
    
    def get_template_fields_path(self) -> Path:
        """Devuelve la ruta de archivos de campos"""
        return Path(self.get('paths.templates.archivos_campos',
                            str(self.project_root / 'templates' / 'archivos de campos')))
    
    def create_path(self, key_path: str) -> Path:
        """
        Obtiene una ruta de configuración y crea el directorio si no existe.
        Devuelve la ruta como objeto Path.
        """
        path = Path(self.get(key_path, ''))
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logging.info(f"Directorio creado: {path}")
            except Exception as e:
                logging.error(f"Error al crear directorio {path}: {str(e)}")
        
        return path
    
    def get_data_path(self):
        """Obtiene la ruta al directorio de datos del proyecto"""
        # Por defecto, usar la carpeta Data en la raíz del proyecto
        data_path = self.project_root / "Data"
        
        # Si existe una configuración específica para data_path, usarla
        if hasattr(self, 'config') and self.config and 'paths' in self.config and 'data_path' in self.config['paths']:
            custom_path = self.config['paths']['data_path']
            # Si es una ruta relativa, basarla en la raíz del proyecto
            if not Path(custom_path).is_absolute():
                data_path = self.project_root / custom_path
            else:
                data_path = Path(custom_path)
        
        # Asegurar que el directorio exista
        data_path.mkdir(exist_ok=True, parents=True)
        return data_path
