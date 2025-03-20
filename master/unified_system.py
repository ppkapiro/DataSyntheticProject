import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from utils.clinic_manager import ClinicManager
from utils.template_manager import TemplateManager
from core.import_consolidator import ImportConsolidator
from utils.template_management.system_integrator import SystemIntegrator
from pdf_extractor.pdf_extractor import PDFExtractor
from utils.menu_manager import MenuManager, MenuType

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedSystem:
    """Sistema unificado de Notefy IA"""
    
    def __init__(self):
        self.base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")
        self.current_clinic: Optional[str] = None
        self.menu_manager = MenuManager()
        
        # Componentes del sistema
        self.clinic_manager = ClinicManager(self.base_path)
        self.template_manager = TemplateManager()
        self.consolidator = ImportConsolidator()
        self.system_integrator = SystemIntegrator()
        self.pdf_extractor = PDFExtractor()

    def run(self):
        """Punto de entrada principal del sistema"""
        while True:
            try:
                opcion = self.menu_manager.show_menu(MenuType.PRINCIPAL)
                
                if opcion == '0':
                    logger.info("Finalizando sistema")
                    break
                    
                self.procesar_opcion_principal(opcion)
                
            except Exception as e:
                logger.error(f"Error en sistema: {str(e)}")
                self.menu_manager.show_error(str(e))

    def procesar_opcion_principal(self, opcion: str):
        """Procesa la opción seleccionada del menú principal"""
        if opcion == '1':
            self._crear_nueva_clinica()
        elif opcion == '2':
            self._seleccionar_clinica()
        elif opcion == '3':
            self.clinic_manager.listar_clinicas()
        elif opcion == '4':
            self._menu_plantillas()
        elif opcion == '5':
            self._menu_desarrollo()

    def _crear_nueva_clinica(self):
        """Gestiona la creación de una nueva clínica"""
        nombre = input("\nIngrese el nombre de la nueva clínica: ").strip()
        if nombre and self.clinic_manager.crear_clinica(nombre):
            self.current_clinic = nombre
            self._procesar_clinica()

    def _seleccionar_clinica(self):
        """Gestiona la selección de una clínica existente"""
        nombre = self.clinic_manager.seleccionar_clinica()
        if nombre:
            self.current_clinic = nombre
            self._procesar_clinica()

    def _procesar_clinica(self):
        """Menú principal de una clínica seleccionada"""
        while True:
            opcion = self.menu_manager.show_menu(MenuType.CLINICA, self.current_clinic)
            if opcion == '0':
                break
            self.procesar_opcion_clinica(opcion)

    def procesar_opcion_clinica(self, opcion: str):
        """Procesa la opción seleccionada del menú de clínica"""
        opciones = {
            '1': self._menu_documental,
            '2': self._menu_pdf,
            '3': self._menu_facilitadores,
            '4': self._menu_datos_sinteticos,
            '5': self._menu_reportes,
            '6': self._menu_importacion
        }
        
        if opcion in opciones:
            opciones[opcion]()

    def _menu_desarrollo(self):
        """Menú de herramientas de desarrollo"""
        while True:
            opcion = self.menu_manager.show_menu(MenuType.DESARROLLO)
            
            if opcion == '0':
                break
            elif opcion == '1':
                self._ejecutar_pruebas()
            elif opcion == '2':
                self._optimizar_plantillas()
            elif opcion == '3':
                self._ver_reportes_validacion()
            elif opcion == '4':
                self._analizar_codigo()

    # ... (otros métodos de menú)

    @staticmethod
    def _solicitar_opcion(opciones_validas: list) -> str:
        """Método auxiliar para solicitar y validar opciones"""
        while True:
            opcion = input("\nSeleccione una opción: ").strip()
            if opcion in opciones_validas:
                return opcion
            print("Opción no válida")

if __name__ == "__main__":
    system = UnifiedSystem()
    system.run()
