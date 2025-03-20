import os
import sys
from datetime import datetime
from pathlib import Path

# Configurar path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Ahora importar los módulos
from utils.clinic_manager import ClinicManager
from pdf_extractor.pdf_extractor import PDFExtractor

class ClinicaManager:
    BASE_PATH = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")
    MODULES = ["pacientes", "FARC", "BIO", "MTP", "lector_archivos"]

    def __init__(self):
        self.BASE_PATH.mkdir(exist_ok=True)
        self.lector = None
        self.exportadores = {}

    def inicializar_modulos(self):
        """Importa e inicializa los módulos necesarios"""
        try:
            from lector_archivos.lector import LectorArchivos
            from pacientes.pacientes import ExportadorPacientes
            from FARC.fars import ExportadorFARC
            from BIO.bios import ExportadorBIO
            from MTP.mtp import ExportadorMTP
            from pdf_extractor.pdf_extractor import PDFExtractor  # Nuevo módulo
            
            self.lector = LectorArchivos()
            self.exportadores = {
                'pacientes': ExportadorPacientes(),
                'FARC': ExportadorFARC(),
                'BIO': ExportadorBIO(),
                'MTP': ExportadorMTP(),
                'pdf_extractor': PDFExtractor()  # Añadido al diccionario
            }
        except ImportError as e:
            print(f"Error al importar módulos: {str(e)}")
            print(f"PYTHONPATH actual: {sys.path}")
            raise

    def get_time_identifier(self):
        """Genera identificador de tiempo en formato HHMM_DDMM"""
        now = datetime.now()
        return f"{now.hour:02d}{now.minute:02d}_{now.day:02d}{now.month:02d}"

    def setup_clinic_structure(self, clinic_name):
        """Crea o verifica la estructura de carpetas para una clínica"""
        clinic_path = self.BASE_PATH / clinic_name
        clinic_path.mkdir(exist_ok=True)

        # Crear estructura para cada módulo
        for module in self.MODULES:
            module_path = clinic_path / module
            module_path.mkdir(exist_ok=True)
            (module_path / "input").mkdir(exist_ok=True)
            (module_path / "output").mkdir(exist_ok=True)

        return clinic_path

    def procesar_modo_extraccion(self, clinic_path):
        """Procesa el modo de extracción de información"""
        print("\nModo: Extracción de información")
        
        file_path = input("Ingrese la ruta del archivo a procesar: ")
        output_dir = clinic_path / "lector_archivos" / "output"
        
        try:
            df = self.lector.procesar_archivo(file_path, output_dir)
            print("Archivo procesado exitosamente")
            return df
        except Exception as e:
            print(f"Error al procesar archivo: {e}")
            return None

    def procesar_modo_generacion(self, clinic_path, clinic_name):
        """Procesa el modo de generación de archivos sintéticos"""
        print("\nModo: Generación de archivos sintéticos")
        
        exportadores_map = {
            'pacientes': ('exportar_pacientes', 'pacientes'),
            'FARC': ('exportar_fars', 'FARC'),  # Cambiado de 'exportar_farc' a 'exportar_fars'
            'BIO': ('exportar_bios', 'BIO'),
            'MTP': ('exportar_mtp', 'MTP')
        }
        
        for modulo, (metodo, carpeta) in exportadores_map.items():
            if modulo in self.exportadores:
                print(f"\nProcesando módulo {modulo}...")
                output_dir = clinic_path / carpeta / "output"
                try:
                    getattr(self.exportadores[modulo], metodo)(
                        None, clinic_name[:3].upper(), output_dir
                    )
                except Exception as e:
                    print(f"Error en módulo {modulo}: {str(e)}")
            else:
                print(f"Módulo {modulo} no implementado")

    def mostrar_menu_principal(self):
        """Muestra el menú principal simplificado"""
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Procesar archivo")
        print("2. Generar datos sintéticos")
        print("3. Salir")
        return input("\nSeleccione una opción (1-3): ")

    def mostrar_menu_procesamiento(self):
        """Muestra el menú inicial de procesamiento"""
        print("\n=== TIPO DE PROCESAMIENTO ===")
        print("1. Procesar archivos de datos")
        print("   • CSV, Excel (XLS, XLSX)")
        print("   • TSV, ODS (OpenDocument)")
        print("   • JSON, YAML")
        print("   • HTML, otros formatos tabulares")
        print("2. Procesar archivos PDF")
        print("3. Volver al menú principal")
        return input("\nSeleccione el tipo de procesamiento (1-3): ")

    def mostrar_menu_tipos_archivo_datos(self):
        """Muestra el menú de selección de tipo de archivo de datos"""
        print("\n=== TIPOS DE ARCHIVO DE DATOS ===")
        print("1. Pacientes")
        print("2. FARC (Alcohol y drogas)")
        print("3. BIO (Biografía)")
        print("4. MTP (Master Training Plan)")
        return input("\nSeleccione el tipo de archivo (1-4): ")

    def mostrar_menu_tipos_pdf(self):
        """Muestra el menú de selección de tipo de archivo PDF"""
        print("\n=== TIPOS DE ARCHIVO PDF ===")
        print("1. FARC (Evaluaciones)")
        print("2. BIO (Historiales)")
        print("3. MTP (Planes de tratamiento)")
        print("4. Notas de Progreso")
        print("5. Otro tipo de documento")
        return input("\nSeleccione el tipo de PDF (1-5): ")

    def seleccionar_modulo(self):
        """Permite al usuario seleccionar un módulo específico"""
        print("\n=== MÓDULOS DISPONIBLES ===")
        for idx, modulo in enumerate(self.MODULES[:-1], 1):  # Excluimos lector_archivos
            print(f"{idx}. {modulo}")
        
        while True:
            try:
                opcion = int(input("\nSeleccione el módulo (1-4): ")) - 1
                if 0 <= opcion < len(self.MODULES) - 1:
                    return self.MODULES[opcion]
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

    def validar_nombre_clinica(self):
        """Solicita y valida el nombre de la clínica"""
        while True:
            clinic_name = input("\n¿Con qué nombre vamos a identificar la clínica?: ")
            confirmacion = input(f"¿Está seguro que '{clinic_name}' es el nombre correcto? (S/N): ").upper()
            if confirmacion == 'S':
                return clinic_name
            print("Por favor, ingrese el nombre nuevamente.")

    def procesar_archivo_por_tipo(self, tipo, clinic_path, clinic_name):
        """Procesa un archivo según el tipo seleccionado"""
        # Primero preguntamos tipo de procesamiento
        tipo_proc = self.mostrar_menu_procesamiento()
        
        if tipo_proc == "1":  # Archivos de datos (CSV, Excel, etc.)
            tipo_archivo = self.mostrar_menu_tipos_archivo_datos()
            modulos = {
                "1": ("pacientes", "Pacientes"),
                "2": ("FARC", "FARC"),
                "3": ("BIO", "Biografía"),
                "4": ("MTP", "Master Training Plan")
            }
        elif tipo_proc == "2":  # PDF
            tipo_archivo = self.mostrar_menu_tipos_pdf()
            modulos = {
                "1": ("FARC", "FARC - PDF"),
                "2": ("BIO", "BIO - PDF"),
                "3": ("MTP", "MTP - PDF"),
                "4": ("pdf_notas", "Notas de Progreso"),
                "5": ("pdf_otros", "Otro documento")
            }
        else:
            return

        if tipo_archivo not in modulos:
            print("Tipo de archivo no válido")
            return
        
        modulo, nombre = modulos[tipo_archivo]
        print(f"\nProcesando archivo de {nombre}")
        
        output_dir = clinic_path / "lector_archivos" / "output"
        clinic_initials = clinic_name[:3].upper()
        
        try:
            if tipo_proc == "2":  # Si es PDF
                extractor = PDFExtractor()
                resultado = extractor.procesar_pdf(
                    file_path=None, 
                    output_dir=output_dir, 
                    clinic_initials=clinic_initials,
                    tipo_pdf=modulo  # Pasamos el tipo de PDF
                )
                if resultado:
                    print(f"Archivo PDF procesado exitosamente")
                    print(f"El análisis se ha guardado en: {output_dir}")
            else:  # Si es CSV/Excel
                df, estructura = self.lector.procesar_archivo(None, output_dir, clinic_initials)
                if df is not None:
                    print(f"Archivo {nombre} procesado exitosamente")
                    print(f"El análisis se ha guardado en: {output_dir}")
                    
                    if input("\n¿Desea generar datos sintéticos con esta estructura? (S/N): ").upper() == 'S':
                        output_dir_modulo = clinic_path / modulo / "output"
                        if modulo in self.exportadores:
                            metodo = f"exportar_{modulo.lower()}"
                            try:
                                getattr(self.exportadores[modulo], metodo)(
                                    df_estructura=estructura,
                                    clinic_initials=clinic_initials,
                                    output_dir=output_dir_modulo
                                )
                            except Exception as e:
                                print(f"Error al generar datos sintéticos: {e}")
        except Exception as e:
            print(f"Error al procesar archivo: {e}")

class DataSyntheticManager:
    def __init__(self):
        self.base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")
        self.clinic_manager = ClinicManager(self.base_path)
        self.clinic_processor = ClinicaManager()
        self.clinic_processor.inicializar_modulos()

    def procesar_clinica(self, nombre_clinica):
        """Procesa una clínica específica"""
        clinic_path = self.clinic_manager.base_path / nombre_clinica
        
        while True:
            print("\n=== MENÚ DE PROCESAMIENTO DE CLÍNICA ===")
            print(f"Clínica actual: {nombre_clinica}")
            print("\n1. Gestión de Archivos")
            print("   - Importar archivos (CSV, Excel, PDF)")
            print("   - Procesar documentos existentes")
            print("   - Extraer información")
            
            print("\n2. Generación de Datos Sintéticos")
            print("   - Pacientes")
            print("   - Evaluaciones FARC")
            print("   - Historias BIO")
            print("   - Planes MTP")
            
            print("\n3. Gestión de PDF")
            print("   - Procesar PDFs")
            print("   - Extraer texto con IA")
            print("   - Convertir formatos")
            
            print("\n4. Gestión de Facilitadores PSR")
            print("   - Ver grupos")
            print("   - Asignar pacientes")
            print("   - Actualizar información")
            
            print("\n5. Reportes y Análisis")
            print("   - Ver estadísticas")
            print("   - Generar informes")
            print("   - Exportar datos")
            
            print("\n0. Volver al menú principal")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == "1":
                self._menu_gestion_archivos(nombre_clinica, clinic_path)
            elif opcion == "2":
                self._menu_datos_sinteticos(nombre_clinica, clinic_path)
            elif opcion == "3":
                self._menu_gestion_pdf(nombre_clinica, clinic_path)
            elif opcion == "4":
                self._menu_facilitadores(nombre_clinica)
            elif opcion == "5":
                self._menu_reportes(nombre_clinica, clinic_path)
            elif opcion == "0":
                break
            else:
                print("Opción no válida")

    def _menu_gestion_archivos(self, nombre_clinica, clinic_path):
        """Menú de gestión de archivos"""
        while True:
            print("\n=== GESTIÓN DE ARCHIVOS ===")
            print("1. Importar nuevo archivo")
            print("2. Procesar archivo existente")
            print("3. Extraer información")
            print("4. Ver archivos procesados")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == "1":
                tipo_archivo = self.clinic_processor.mostrar_menu_tipos_archivo_datos()
                self.clinic_processor.procesar_archivo_por_tipo(tipo_archivo, clinic_path, nombre_clinica)
            elif opcion == "2":
                self._procesar_archivos(nombre_clinica, clinic_path)
            elif opcion == "3":
                self.clinic_processor.procesar_modo_extraccion(clinic_path)
            elif opcion == "4":
                self._mostrar_archivos_procesados(clinic_path)
            elif opcion == "0":
                break

    def _menu_datos_sinteticos(self, nombre_clinica, clinic_path):
        """Menú de generación de datos sintéticos"""
        while True:
            print("\n=== GENERACIÓN DE DATOS SINTÉTICOS ===")
            print("1. Generar datos de pacientes")
            print("2. Generar evaluaciones FARC")
            print("3. Generar historias BIO")
            print("4. Generar planes MTP")
            print("5. Generar todos los tipos")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion in ["1", "2", "3", "4"]:
                modulo = self.clinic_processor.MODULES[int(opcion)-1]
                self.clinic_processor.procesar_modo_generacion(clinic_path, nombre_clinica, [modulo])
            elif opcion == "5":
                self.clinic_processor.procesar_modo_generacion(clinic_path, nombre_clinica)
            elif opcion == "0":
                break

    def _menu_gestion_pdf(self, nombre_clinica, clinic_path):
        """Menú de gestión de PDFs"""
        while True:
            print("\n=== GESTIÓN DE PDF ===")
            print("1. Procesar nuevo PDF")
            print("2. Usar IA para mejorar extracción")
            print("3. Convertir PDF a otros formatos")
            print("4. Ver PDFs procesados")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == "1":
                tipo_pdf = self.clinic_processor.mostrar_menu_tipos_pdf()
                self.clinic_processor.procesar_archivo_por_tipo(tipo_pdf, clinic_path, nombre_clinica)
            elif opcion == "2":
                # Procesar con IA (Google Vision/Amazon Textract)
                self._procesar_pdf_con_ia(clinic_path, nombre_clinica)
            elif opcion == "3":
                self._convertir_pdf(clinic_path, nombre_clinica)
            elif opcion == "4":
                self._mostrar_pdfs_procesados(clinic_path)
            elif opcion == "0":
                break

    def _menu_facilitadores(self, nombre_clinica):
        """Menú de gestión de facilitadores"""
        while True:
            print("\n=== GESTIÓN DE FACILITADORES PSR ===")
            print("1. Ver grupos y pacientes")
            print("2. Asignar pacientes a grupos")
            print("3. Actualizar información de facilitador")
            print("4. Importar lista de pacientes")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == "1":
                self._ver_grupos_facilitadores(nombre_clinica)
            elif opcion == "2":
                self._asignar_pacientes_grupos(nombre_clinica)
            elif opcion == "3":
                self._actualizar_facilitador(nombre_clinica)
            elif opcion == "4":
                self.clinic_manager.asignar_pacientes_facilitador(nombre_clinica)
            elif opcion == "0":
                break

    def _menu_reportes(self, nombre_clinica, clinic_path):
        """Menú de reportes y análisis"""
        while True:
            print("\n=== REPORTES Y ANÁLISIS ===")
            print("1. Ver estadísticas generales")
            print("2. Generar informe de actividad")
            print("3. Exportar datos")
            print("4. Ver histórico de procesamiento")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == "1":
                self._mostrar_estadisticas(clinic_path)
            elif opcion == "2":
                self._generar_informe(clinic_path, nombre_clinica)
            elif opcion == "3":
                self._exportar_datos(clinic_path, nombre_clinica)
            elif opcion == "4":
                self._mostrar_historico(clinic_path)
            elif opcion == "0":
                break

    def _procesar_archivos(self, nombre_clinica, clinic_path):
        """Maneja el procesamiento de archivos"""
        while True:
            tipo_proc = self.clinic_processor.mostrar_menu_procesamiento()
            
            if tipo_proc == "1":  # Archivos de datos
                tipo_archivo = self.clinic_processor.mostrar_menu_tipos_archivo_datos()
                self.clinic_processor.procesar_archivo_por_tipo(tipo_archivo, clinic_path, nombre_clinica)
            elif tipo_proc == "2":  # PDFs
                tipo_pdf = self.clinic_processor.mostrar_menu_tipos_pdf()
                self.clinic_processor.procesar_archivo_por_tipo(tipo_pdf, clinic_path, nombre_clinica)
            elif tipo_proc == "3":
                break
            else:
                print("Opción no válida")

    def _generar_datos_sinteticos(self, nombre_clinica, clinic_path):
        """Maneja la generación de datos sintéticos"""
        print("\n=== GENERACIÓN DE DATOS SINTÉTICOS ===")
        print("1. Pacientes")
        print("2. Evaluaciones FARC")
        print("3. Historias BIO")
        print("4. Planes MTP")
        print("5. Todos los módulos")
        
        opcion = input("\nSeleccione el tipo de datos a generar: ")
        
        if opcion in ["1", "2", "3", "4"]:
            modulo = self.clinic_processor.MODULES[int(opcion)-1]
            self.clinic_processor.procesar_modo_generacion(clinic_path, nombre_clinica, [modulo])
        elif opcion == "5":
            self.clinic_processor.procesar_modo_generacion(clinic_path, nombre_clinica)
        else:
            print("Opción no válida")

    def _ver_grupos_facilitadores(self, nombre_clinica):
        """Muestra los grupos de cada facilitador"""
        config = self.clinic_manager.get_clinic_config(nombre_clinica)
        if not config:
            return
            
        print("\nFacilitadores disponibles:")
        for idx, facilitador in enumerate(config['facilitadores_psr'], 1):
            print(f"\n{idx}. {facilitador['nombre']} ({facilitador['rol']})")
            self.clinic_manager.ver_grupos_facilitador(nombre_clinica, facilitador['nombre'])

    def _asignar_pacientes_grupos(self, nombre_clinica):
        """Gestiona la asignación de pacientes a grupos"""
        self.clinic_manager.asignar_pacientes_facilitador(nombre_clinica)

    def _actualizar_facilitador(self, nombre_clinica):
        """Permite actualizar información del facilitador"""
        config = self.clinic_manager.get_clinic_config(nombre_clinica)
        if not config:
            return
            
        print("\nFacilitadores disponibles:")
        for idx, facilitador in enumerate(config['facilitadores_psr'], 1):
            print(f"{idx}. {facilitador['nombre']} ({facilitador['rol']})")
            
        try:
            opcion = int(input("\nSeleccione el facilitador a actualizar (0 para cancelar): ")) - 1
            if opcion == -1:
                return
            if 0 <= opcion < len(config['facilitadores_psr']):
                self.clinic_manager.actualizar_facilitador(nombre_clinica, opcion)
            else:
                print("Opción no válida")
        except ValueError:
            print("Por favor ingrese un número válido")

    def run(self):
        """Punto de entrada principal"""
        print("\n=== Sistema de Generación de Datos Sintéticos ===")
        
        while True:
            print("\n1. Crear nueva clínica")
            print("2. Seleccionar clínica existente")
            print("3. Listar clínicas")
            print("0. Salir")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == "1":
                nombre = input("\nIngrese el nombre de la nueva clínica: ").strip()
                if nombre and self.clinic_manager.crear_clinica(nombre):
                    self.procesar_clinica(nombre)
            elif opcion == "2":
                # Usar el nuevo método de selección por número
                nombre_clinica = self.clinic_manager.seleccionar_clinica()
                if nombre_clinica and self.clinic_manager.verificar_estructura(nombre_clinica):
                    self.procesar_clinica(nombre_clinica)
            elif opcion == "3":
                self.clinic_manager.listar_clinicas()
            elif opcion == "0":
                break
            else:
                print("Opción no válida")

# Definir la ruta base como constante global
BASE_PATH = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")

from pathlib import Path
from utils.menu_manager import MenuManager
from utils.clinic_manager import ClinicManager
from utils.template_manager import TemplateManager

BASE_PATH = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")

class MainManager:
    def __init__(self):
        self.clinic_manager = ClinicManager(BASE_PATH)
        self.menu_manager = MenuManager()

    def run(self):
        """Ejecuta el flujo principal del programa"""
        while True:
            opcion = MenuManager.mostrar_menu_principal()
            
            if opcion == '0':
                break
            elif opcion == '1':
                nombre = input("\nIngrese el nombre de la clínica: ").strip()
                self.clinic_manager.crear_clinica(nombre)
            elif opcion == '2':
                nombre_clinica = self.clinic_manager.seleccionar_clinica()
                if nombre_clinica:
                    self.clinic_manager.procesar_clinica(nombre_clinica)
            elif opcion == '3':
                self.clinic_manager.listar_clinicas()

    # ...rest of existing code...

class SystemManager:
    def __init__(self):
        self.clinic_manager = ClinicManager(BASE_PATH)
        self.running = True

    def run(self):
        while self.running:
            opcion = MenuManager.mostrar_menu_principal()
            
            if opcion == '0':
                self.running = False
            elif opcion == '1':
                self.clinic_manager.crear_clinica()
            elif opcion == '2':
                nombre_clinica = self.clinic_manager.seleccionar_clinica()
                if nombre_clinica:
                    resultado = self.clinic_manager.procesar_clinica(nombre_clinica)
                    if resultado == 'menu_principal':  # Nuevo: manejar el retorno al menú principal
                        continue
            elif opcion == '3':
                self.clinic_manager.listar_clinicas()

def mostrar_menu_principal():
    """Muestra el menú principal del sistema"""
    print("\n=== Sistema de Generación de Datos Sintéticos ===")
    print("1. Crear nueva clínica")
    print("2. Seleccionar clínica existente")
    print("3. Listar clínicas")
    print("4. Gestión de plantillas")  # Nueva opción en menú principal
    print("0. Salir")

def main():
    base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/data")
    clinic_manager = ClinicManager(base_path)
    template_manager = TemplateManager()

    while True:
        mostrar_menu_principal()
        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == '0':
            break
        elif opcion == '1':
            nombre = input("\nNombre de la nueva clínica: ").strip()
            if nombre:
                clinic_manager.crear_clinica(nombre)
        elif opcion == '2':
            clinica = clinic_manager.seleccionar_clinica()
            if clinica:
                clinic_manager.procesar_clinica(clinica)
        elif opcion == '3':
            clinic_manager.listar_clinicas()
        elif opcion == '4':
            gestionar_plantillas(template_manager)

def gestionar_plantillas(template_manager):
    """Gestión global de plantillas"""
    while True:
        print("\n=== GESTIÓN DE PLANTILLAS ===")
        print("1. Crear nueva plantilla")
        print("2. Modificar plantilla existente")
        print("3. Ver plantillas disponibles")
        print("4. Validar plantilla")
        print("0. Volver al menú principal")

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == '0':
            break
        elif opcion == '1':
            template_manager.crear_nueva_plantilla()
        elif opcion == '2':
            template_manager.modificar_plantilla()
        elif opcion == '3':
            template_manager.listar_plantillas()
        elif opcion == '4':
            template_manager.validar_plantilla()

if __name__ == "__main__":
    main()
