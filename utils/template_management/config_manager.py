from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import threading
from .logging_config import setup_logging

class ConfigManager:
    """Gestor central de configuraciones del sistema"""

    def __init__(self):
        self.logger = setup_logging('config_manager')
        self.config_path = Path(__file__).parent.parent / 'config'
        self.config_cache = {}
        self._lock = threading.Lock()
        self.default_config = {
            'template_settings': {
                'max_field_length': 255,
                'allow_dynamic_fields': False,
                'cache_enabled': True,
                'cache_duration': 3600
            },
            'validation_rules': {
                'strict_mode': True,
                'allow_empty_strings': False,
                'validate_types': True,
                'max_validation_time': 5.0
            },
            'performance_settings': {
                'max_memory_usage': 500 * 1024 * 1024,  # 500MB
                'max_cpu_usage': 80.0,
                'batch_size': 100,
                'enable_caching': True
            },
            'system_paths': {
                'templates': 'templates',
                'output': 'output',
                'logs': 'logs',
                'cache': 'cache'
            }
        }

    def load_config(self, component: str) -> Dict[str, Any]:
        """Carga configuración para un componente"""
        self.logger.info(f"Cargando configuración para: {component}")
        
        try:
            with self._lock:
                # Verificar caché
                if component in self.config_cache:
                    return self.config_cache[component]

                # Cargar configuración
                config_file = self.config_path / f"{component}.json"
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    # Usar configuración por defecto
                    config = self.default_config.get(component, {})
                    self._save_config(component, config)

                # Actualizar caché
                self.config_cache[component] = config
                return config

        except Exception as e:
            self.logger.error(f"Error cargando configuración: {str(e)}")
            return self.default_config.get(component, {})

    def update_config(self, component: str, 
                     updates: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza configuración de un componente"""
        self.logger.info(f"Actualizando configuración de: {component}")
        
        try:
            with self._lock:
                current_config = self.load_config(component)
                
                # Aplicar actualizaciones
                self._deep_update(current_config, updates)
                
                # Validar configuración
                if self._validate_config(component, current_config):
                    # Guardar cambios
                    self._save_config(component, current_config)
                    self.config_cache[component] = current_config
                    return current_config
                else:
                    raise ValueError("Configuración inválida")

        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {str(e)}")
            return self.load_config(component)

    def _deep_update(self, base: Dict[str, Any], 
                    updates: Dict[str, Any]) -> None:
        """Actualiza configuración recursivamente"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict):
                if isinstance(value, dict):
                    self._deep_update(base[key], value)
                else:
                    base[key] = value
            else:
                base[key] = value

    def _validate_config(self, component: str, 
                        config: Dict[str, Any]) -> bool:
        """Valida configuración contra esquema"""
        try:
            if component in self.default_config:
                self._validate_structure(
                    config,
                    self.default_config[component]
                )
            return True
        except Exception as e:
            self.logger.error(f"Error de validación: {str(e)}")
            return False

    def _validate_structure(self, config: Dict[str, Any], 
                          schema: Dict[str, Any]) -> None:
        """Valida estructura de configuración"""
        for key, value in schema.items():
            if key not in config:
                raise ValueError(f"Falta clave requerida: {key}")
            if isinstance(value, dict):
                if not isinstance(config[key], dict):
                    raise ValueError(f"Tipo inválido para {key}")
                self._validate_structure(config[key], value)

    def _save_config(self, component: str, 
                    config: Dict[str, Any]) -> None:
        """Guarda configuración en disco"""
        try:
            self.config_path.mkdir(parents=True, exist_ok=True)
            config_file = self.config_path / f"{component}.json"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error guardando configuración: {str(e)}")
            raise

    def get_component_settings(self, component: str, 
                             setting: Optional[str] = None) -> Any:
        """Obtiene configuración específica de un componente"""
        config = self.load_config(component)
        
        if setting:
            return config.get(setting)
        return config
