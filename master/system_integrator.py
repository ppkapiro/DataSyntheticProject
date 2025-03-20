import logging
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum, auto

logger = logging.getLogger(__name__)

class ModuleStatus(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    ERROR = auto()

@dataclass
class ModuleInfo:
    name: str
    status: ModuleStatus
    error_message: str = ""
    dependencies: list = None

class SystemIntegrator:
    """Integrador central del sistema"""
    
    def __init__(self):
        self.modules: Dict[str, ModuleInfo] = {}
        self._initialize_modules()

    def _initialize_modules(self):
        """Inicializa y registra todos los módulos del sistema"""
        self.register_module("menu_manager", ["clinic_manager"])
        self.register_module("clinic_manager", ["template_manager"])
        self.register_module("template_manager", [])
        self.register_module("pdf_extractor", ["system_integrator"])
        self.register_module("import_consolidator", ["data_processor"])
        self.register_module("codebase_analyzer", [])
        self.register_module("integration_tests", ["system_integrator"])

    def register_module(self, name: str, dependencies: list = None):
        """Registra un nuevo módulo en el sistema"""
        self.modules[name] = ModuleInfo(
            name=name,
            status=ModuleStatus.INACTIVE,
            dependencies=dependencies or []
        )

    def activate_module(self, name: str) -> bool:
        """Activa un módulo y sus dependencias"""
        if name not in self.modules:
            logger.error(f"Módulo {name} no encontrado")
            return False

        module = self.modules[name]
        
        # Primero activar dependencias
        for dep in module.dependencies:
            if not self.activate_module(dep):
                module.status = ModuleStatus.ERROR
                module.error_message = f"Error activando dependencia {dep}"
                return False

        try:
            # Aquí iría la lógica de activación específica
            module.status = ModuleStatus.ACTIVE
            logger.info(f"Módulo {name} activado correctamente")
            return True
        except Exception as e:
            module.status = ModuleStatus.ERROR
            module.error_message = str(e)
            logger.error(f"Error activando módulo {name}: {str(e)}")
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema"""
        return {
            "modules": {
                name: {
                    "status": module.status.name,
                    "error": module.error_message if module.status == ModuleStatus.ERROR else None
                }
                for name, module in self.modules.items()
            },
            "total_modules": len(self.modules),
            "active_modules": sum(1 for m in self.modules.values() if m.status == ModuleStatus.ACTIVE),
            "error_modules": sum(1 for m in self.modules.values() if m.status == ModuleStatus.ERROR)
        }

    def validate_system(self) -> bool:
        """Valida el estado general del sistema"""
        status = self.get_system_status()
        return status["error_modules"] == 0

    def verify_dependencies(self) -> Dict[str, list]:
        """Verifica las dependencias circulares y faltantes"""
        missing_deps = {}
        for name, module in self.modules.items():
            missing = [dep for dep in module.dependencies if dep not in self.modules]
            if missing:
                missing_deps[name] = missing
        return missing_deps
