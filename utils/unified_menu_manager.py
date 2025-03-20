from enum import Enum, auto
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MenuType(Enum):
    """Tipos de menús disponibles en el sistema"""
    PRINCIPAL = auto()
    CLINICA = auto()
    DOCUMENTOS = auto()
    FACILITADORES = auto()
    DATOS = auto()
    REPORTES = auto()
    DESARROLLO = auto()
    PDF = auto()
    PLANTILLAS = auto()
    IMPORTACION = auto()

class UnifiedMenuManager:
    """Gestor unificado de menús del sistema"""

    def __init__(self):
        self.current_clinic: Optional[str] = None
        self._initialize_menus()

    def _initialize_menus(self):
        """Inicializa la estructura de menús"""
        self.menus: Dict[MenuType, Dict[str, Any]] = {
            MenuType.PRINCIPAL: {
                'title': 'SISTEMA NOTEFY IA',
                'options': [
                    ('1', 'Gestión de Clínicas'),
                    ('2', 'Procesamiento de Documentos'),
                    ('3', 'Gestión de Facilitadores'),
                    ('4', 'Generación de Datos'),
                    ('5', 'Reportes y Análisis'),
                    ('6', 'Herramientas de Desarrollo'),
                    ('0', 'Salir')
                ]
            },
            MenuType.CLINICA: {
                'title': 'GESTIÓN DE CLÍNICAS',
                'options': [
                    ('1', 'Crear nueva clínica'),
                    ('2', 'Seleccionar clínica existente'),
                    ('3', 'Listar clínicas'),
                    ('0', 'Volver')
                ]
            },
            # ... más definiciones de menús
        }

    def show_menu(self, menu_type: MenuType, **kwargs) -> str:
        """Muestra un menú específico y retorna la opción seleccionada"""
        if menu_type not in self.menus:
            logger.error(f"Tipo de menú no encontrado: {menu_type}")
            raise ValueError(f"Menú no válido: {menu_type}")

        menu = self.menus[menu_type]
        
        # Mostrar título del menú
        title = menu['title']
        if menu_type == MenuType.CLINICA and self.current_clinic:
            title = f"{title} - Clínica: {self.current_clinic}"
        
        print(f"\n=== {title} ===")

        # Mostrar opciones específicas según el contexto
        if 'pre_options' in kwargs:
            self._show_pre_options(kwargs['pre_options'])

        # Mostrar opciones del menú
        for option, description in menu['options']:
            if 'submenu' in kwargs and option != '0':
                print(f"\n{option}. {description}")
                for sub in kwargs['submenu'].get(option, []):
                    print(f"   • {sub}")
            else:
                print(f"{option}. {description}")

        # Opciones válidas
        valid_options = [opt[0] for opt in menu['options']]
        
        return self._get_option(valid_options)

    def _show_pre_options(self, pre_options: List[str]):
        """Muestra información adicional antes de las opciones"""
        for line in pre_options:
            print(line)
        print()

    def _get_option(self, valid_options: List[str]) -> str:
        """Solicita y valida una opción del usuario"""
        while True:
            option = input("\nSeleccione una opción: ").strip()
            if option in valid_options:
                return option
            print("Opción no válida")

    def show_confirmation(self, message: str) -> bool:
        """Solicita confirmación al usuario"""
        response = input(f"\n{message} (S/N): ").upper()
        return response == 'S'

    def show_error(self, message: str):
        """Muestra un mensaje de error"""
        print(f"\nError: {message}")

    def show_success(self, message: str):
        """Muestra un mensaje de éxito"""
        print(f"\nÉxito: {message}")

    def request_input(self, prompt: str, required: bool = True) -> Optional[str]:
        """Solicita entrada al usuario"""
        while True:
            value = input(f"\n{prompt}: ").strip()
            if value or not required:
                return value
            print("Este campo es obligatorio")

    def set_current_clinic(self, clinic_name: Optional[str]):
        """Establece la clínica actual"""
        self.current_clinic = clinic_name
        if clinic_name:
            logger.info(f"Clínica actual establecida: {clinic_name}")
        else:
            logger.info("Clínica actual eliminada")
