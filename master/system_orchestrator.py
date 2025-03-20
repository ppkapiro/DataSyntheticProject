from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from utils.menu_manager import MenuManager, MenuType
from utils.clinic_manager import ClinicManager
from utils.template_manager import TemplateManager
from core.import_consolidator import ImportConsolidator

logger = logging.getLogger(__name__)

class SystemOrchestrator:
    """Orquestador central del sistema"""
    
    def __init__(self):
        self.menu_manager = MenuManager()
        self.clinic_manager = ClinicManager()
        self.template_manager = TemplateManager()
        self.consolidator = ImportConsolidator()
        self.current_clinic: Optional[str] = None

    def run(self):
        """Punto de entrada principal del sistema"""
        while True:
            try:
                opcion = self.menu_manager.show_menu(MenuType.PRINCIPAL)
                if opcion == '0':
                    break
                self.procesar_opcion_principal(opcion)
            except Exception as e:
                logger.error(f"Error en sistema: {str(e)}")
                self.menu_manager.show_error(str(e))

    def procesar_opcion_principal(self, opcion):
        if opcion == '1':  # Crear clínica
            nombre = input("\nIngrese el nombre de la nueva clínica: ").strip()
            if nombre and self.clinic_manager.crear_clinica(nombre):
                self.current_clinic = nombre
                self._procesar_clinica()
                
        elif opcion == '2':  # Seleccionar clínica
            nombre = self.clinic_manager.seleccionar_clinica()
            if nombre:
                self.current_clinic = nombre
                self._procesar_clinica()
                
        elif opcion == '3':  # Listar clínicas
            self.clinic_manager.listar_clinicas()
            
        elif opcion == '4':  # Gestión de plantillas
            self._gestionar_plantillas()

    def _procesar_clinica(self):
        """Procesa las operaciones de una clínica"""
        while True:
            opcion = self.menu_manager.mostrar_menu_clinica(self.current_clinic)
            
            if opcion == '0':
                break
                
            elif opcion == '1':  # Gestión documental
                self._menu_documentos()
                
            elif opcion == '2':  # Procesamiento PDF
                self._menu_pdf()
                
            elif opcion == '3':  # Gestión facilitadores
                self._menu_facilitadores()
                
            elif opcion == '4':  # Generación datos
                self._menu_datos_sinteticos()
                
            elif opcion == '5':  # Reportes
                self._menu_reportes()

    def _menu_documentos(self):
        """Gestión de documentos"""
        while True:
            opcion = self.menu_manager.mostrar_menu_documentos()
            
            if opcion == '0':
                break
            elif opcion == '1':  # Importar
                self._importar_documento()
            elif opcion == '2':  # Procesar
                self._procesar_documento()
            elif opcion == '3':  # Consolidar
                self._consolidar_documentos()
            elif opcion == '4':  # Ver procesados
                self.menu_manager.ver_documentos_procesados()

    def _menu_pdf(self):
        # ... (similar structure for PDF processing)
        pass

    def _menu_facilitadores(self):
        # ... (similar structure for facilitator management)
        pass

    def _menu_datos_sinteticos(self):
        # ... (similar structure for synthetic data generation)
        pass

    def _menu_reportes(self):
        # ... (similar structure for reports)
        pass

    def _gestionar_plantillas(self):
        # ... (similar structure for template management)
        pass

if __name__ == "__main__":
    orchestrator = SystemOrchestrator()
    orchestrator.run()
