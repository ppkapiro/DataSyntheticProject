import sys
import logging
from pathlib import Path
from typing import Dict, Any
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notefy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar módulos del sistema
from utils.menu_manager import MenuManager, MenuType
from utils.clinic_manager import ClinicManager
from utils.template_manager import TemplateManager
from core.import_consolidator import ImportConsolidator
from pdf_extractor.pdf_extractor import PDFExtractor
from tools.codebase_analyzer import CodebaseAnalyzer
from utils.event_bus import EventBus, SystemEvent

class NotefySystem:
    """Sistema unificado de Notefy"""
    
    def __init__(self):
        # Configuración base
        self.base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")
        self.templates_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/templates")
        self.output_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/output")
        
        # Verificar directorios
        for path in [self.base_path, self.templates_path, self.output_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Componentes principales
        self.event_bus = EventBus()
        self.menu_manager = MenuManager()
        self.clinic_manager = ClinicManager(self.base_path)
        self.template_manager = TemplateManager()
        self.pdf_extractor = PDFExtractor()
        self.import_consolidator = ImportConsolidator()
        
        # Estado del sistema
        self.current_clinic = None
        
        # Suscribirse a eventos relevantes
        self.event_bus.subscribe(SystemEvent.CLINIC_SELECTED, self._handle_clinic_selected)
        self.event_bus.subscribe(SystemEvent.CLINIC_CREATED, self._handle_clinic_created)
        self.event_bus.subscribe(SystemEvent.ERROR_OCCURRED, self._handle_error)
        
        logger.info("Sistema Notefy inicializado correctamente")
    
    def _handle_clinic_selected(self, data: Dict[str, Any]):
        """Maneja el evento de selección de clínica"""
        self.current_clinic = data['name']
        logger.info(f"Clínica seleccionada: {self.current_clinic}")
    
    def _handle_clinic_created(self, data: Dict[str, Any]):
        """Maneja el evento de creación de clínica"""
        self.current_clinic = data['name']
        logger.info(f"Nueva clínica creada: {self.current_clinic}")
    
    def _handle_error(self, data: Dict[str, Any]):
        """Maneja errores del sistema"""
        logger.error(f"Error del sistema: {data['message']}")
    
    def run(self):
        """Punto de entrada principal del sistema"""
        try:
            logger.info("Iniciando sistema Notefy")
            self._show_welcome_message()
            
            while True:
                try:
                    option = self.menu_manager.show_menu(MenuType.PRINCIPAL)
                    
                    if option == '0':
                        logger.info("Finalizando sistema")
                        self._show_goodbye_message()
                        break
                    
                    self._process_main_option(option)
                    
                except Exception as e:
                    error_msg = f"Error en el sistema: {str(e)}"
                    logger.error(error_msg)
                    self.event_bus.emit(SystemEvent.ERROR_OCCURRED, {'message': error_msg})
                    input("\nPresione Enter para continuar...")
        
        except KeyboardInterrupt:
            logger.info("Sistema interrumpido por el usuario")
            self._show_goodbye_message()
    
    def _show_welcome_message(self):
        """Muestra mensaje de bienvenida"""
        print("\n" + "="*50)
        print("      Sistema de Gestión de Datos Notefy IA")
        print("="*50)
    
    def _show_goodbye_message(self):
        """Muestra mensaje de despedida"""
        print("\n" + "="*50)
        print("      Gracias por usar Notefy IA")
        print("="*50)
    
    def _process_main_option(self, option: str):
        """Procesa la opción del menú principal"""
        if option == '1':  # Gestión de Clínicas
            self._menu_clinics()
        elif option == '2':  # Procesamiento de Documentos
            self._menu_documents()
        elif option == '3':  # Gestión de Facilitadores
            self._menu_facilitators()
        elif option == '4':  # Generación de Datos
            self._menu_data_generation()
        elif option == '5':  # Reportes y Análisis
            self._menu_reports()
        elif option == '6':  # Herramientas de Desarrollo
            self._menu_development()
    
    def _menu_clinics(self):
        """Menú de gestión de clínicas"""
        while True:
            option = self.menu_manager.show_menu(MenuType.CLINICA)
            
            if option == '0':  # Volver
                break
            elif option == '1':  # Crear nueva clínica
                clinic_name = input("\nIngrese el nombre de la nueva clínica: ").strip()
                if clinic_name:
                    self.clinic_manager.crear_clinica(clinic_name)
            elif option == '2':  # Seleccionar clínica existente
                clinic_name = self.clinic_manager.seleccionar_clinica()
                if clinic_name:
                    self._process_clinic(clinic_name)
            elif option == '3':  # Listar clínicas
                self.clinic_manager.listar_clinicas()
    
    def _process_clinic(self, clinic_name: str):
        """Procesa las operaciones de una clínica seleccionada"""
        # Configuramos el menú para la clínica actual
        self.menu_manager.clinica_actual = clinic_name
        
        while True:
            # Menú de clínica personalizado con submenús
            option = self.menu_manager.show_menu(MenuType.CLINICA, 
                submenu={
                    '1': ['Importar archivos', 'Procesar documentos', 'Consolidar información'],
                    '2': ['Extraer texto', 'Procesar con IA', 'Convertir formatos'],
                    '3': ['Ver grupos', 'Asignar pacientes', 'Actualizar información']
                }
            )
            
            if option == '0':
                break
                
            # Implementar resto de opciones...
    
    def _menu_documents(self):
        """Menú de procesamiento de documentos"""
        if not self.current_clinic:
            self.menu_manager.show_error("Debe seleccionar una clínica primero")
            return
            
        while True:
            option = self.menu_manager.show_menu(MenuType.DOCUMENTOS)
            
            if option == '0':
                break
                
            # Implementar opciones...

    def _menu_facilitators(self):
        """Menú de gestión de facilitadores"""
        if not self.current_clinic:
            self.menu_manager.show_error("Debe seleccionar una clínica primero")
            return
            
        while True:
            option = self.menu_manager.show_menu(MenuType.FACILITADORES)
            
            if option == '0':
                break
                
            # Implementar opciones...
    
    def _menu_data_generation(self):
        """Menú de generación de datos sintéticos"""
        if not self.current_clinic:
            self.menu_manager.show_error("Debe seleccionar una clínica primero")
            return
            
        while True:
            option = self.menu_manager.show_menu(MenuType.DATOS)
            
            if option == '0':
                break
                
            # Implementar opciones...
    
    def _menu_reports(self):
        """Menú de reportes y análisis"""
        if not self.current_clinic:
            self.menu_manager.show_error("Debe seleccionar una clínica primero")
            return
            
        while True:
            option = self.menu_manager.show_menu(MenuType.REPORTES)
            
            if option == '0':
                break
                
            # Implementar opciones...
    
    def _menu_development(self):
        """Menú de herramientas de desarrollo"""
        while True:
            option = self.menu_manager.show_menu(MenuType.DESARROLLO)
            
            if option == '0':
                break
            elif option == '1':  # Ejecutar pruebas
                self._run_automated_tests()
            elif option == '2':  # Optimizar plantillas
                self._optimize_templates()
            elif option == '3':  # Ver reportes
                self._show_validation_reports()
            elif option == '4':  # Analizar código
                self._analyze_codebase()
    
    def _run_automated_tests(self):
        """Ejecuta pruebas automatizadas"""
        print("\nEjecutando pruebas automatizadas...")
        try:
            import pytest
            import asyncio
            
            # Ejecutar pruebas
            pytest.main(['tests/automated'])
            
            print("\nEjecución de pruebas completada")
            input("\nPresione Enter para continuar...")
            
        except Exception as e:
            self.event_bus.emit(SystemEvent.ERROR_OCCURRED, 
                {'message': f"Error ejecutando pruebas: {str(e)}"})
    
    def _optimize_templates(self):
        """Optimiza las plantillas existentes"""
        print("\nOptimizando plantillas...")
        try:
            if self.current_clinic:
                self.template_manager.optimizar_plantillas(self.current_clinic)
            else:
                print("\nDebe seleccionar una clínica primero")
        except Exception as e:
            self.event_bus.emit(SystemEvent.ERROR_OCCURRED, 
                {'message': f"Error optimizando plantillas: {str(e)}"})
        
        input("\nPresione Enter para continuar...")
    
    def _show_validation_reports(self):
        """Muestra reportes de validación"""
        print("\nGenerando reportes de validación...")
        # Implementar funcionalidad...
        input("\nPresione Enter para continuar...")
    
    def _analyze_codebase(self):
        """Analiza la estructura del código"""
        print("\nAnalizando el código base...")
        
        try:
            analyzer = CodebaseAnalyzer(Path(__file__).parent)
            analyzer.analyze_project()
            report = analyzer.generate_report()
            print(report)
            
            if self.menu_manager.show_confirmation("¿Desea guardar el reporte?"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"code_analysis_{timestamp}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                print(f"\nReporte guardado como {filename}")
            
        except Exception as e:
            self.event_bus.emit(SystemEvent.ERROR_OCCURRED, 
                {'message': f"Error analizando código: {str(e)}"})
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    system = NotefySystem()
    system.run()
