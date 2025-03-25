import sys
import os
import importlib
import json  # Añadir esta importación
from pathlib import Path
import logging
from enum import Enum, auto
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Asegurarnos de que el directorio raíz está en el path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Definir enum MenuType para unified_main.py
class MenuType(Enum):
    PRINCIPAL = auto()
    CLINICA = auto()
    CLINICA_SELECCIONADA = auto()  # Nuevo tipo para el menú de una clínica específica
    DOCUMENTOS = auto()
    FACILITADORES = auto()
    DATOS = auto()
    REPORTES = auto()
    DESARROLLO = auto()
    SECCIONES = auto()  # Nuevo tipo para el menú de secciones

# Ahora importar los módulos necesarios
try:
    from utils.config_manager import ConfigManager
    
    # Obtener la configuración
    config = ConfigManager()
    data_path = config.get_data_path()
    
    logger.info(f"Iniciando sistema Notefy IA con ruta de datos: {data_path}")
    
    # Asegurar que el directorio de datos existe
    data_path.mkdir(parents=True, exist_ok=True)
    
    class SimpleClinicManager:
        """Versión simple del gestor de clínicas para evitar dependencias circulares"""
        
        def __init__(self, base_path):
            self.base_path = base_path
            
        def crear_clinica(self, name):
            print(f"\nCreando clínica: {name}")
            clinic_path = self.base_path / name
            
            if clinic_path.exists():
                print(f"La clínica '{name}' ya existe")
                return False
                
            clinic_path.mkdir(parents=True, exist_ok=True)
            print(f"Clínica '{name}' creada con éxito")
            return True
            
        def seleccionar_clinica(self):
            clinicas = self.listar_clinicas()
            if not clinicas:
                return None
                
            try:
                opcion = input("\nSeleccione el número de la clínica (0 para cancelar): ")
                if opcion == '0':
                    return None
                    
                idx = int(opcion) - 1
                if 0 <= idx < len(clinicas):
                    return clinicas[idx]
                    
                print("Número de clínica no válido")
            except ValueError:
                print("Por favor ingrese un número válido")
                
            return None
            
        def listar_clinicas(self):
            if not self.base_path.exists():
                print(f"\nNo se encuentra el directorio base: {self.base_path}")
                return []
                
            clinicas = [d.name for d in self.base_path.iterdir() if d.is_dir()]
            
            if not clinicas:
                print("\nNo hay clínicas creadas")
                return []
                
            print("\n=== CLÍNICAS EXISTENTES ===")
            for idx, clinica in enumerate(clinicas, 1):
                print(f"{idx}. {clinica}")
                
            return clinicas
        
        def eliminar_clinica(self, nombre_clinica):
            """Elimina una clínica existente y todos sus datos"""
            clinic_path = self.base_path / nombre_clinica
            
            if not clinic_path.exists():
                print(f"\nError: La clínica '{nombre_clinica}' no existe")
                return False
                
            # Verificar que el usuario realmente quiere eliminar la clínica
            print(f"\n⚠️ ADVERTENCIA: Está a punto de eliminar la clínica '{nombre_clinica}'")
            print("Esta acción eliminará TODOS los datos asociados y NO puede deshacerse.")
            
            confirmacion = input(f"\n¿Está seguro de eliminar la clínica '{nombre_clinica}'? (escriba 'ELIMINAR' para confirmar): ")
            if confirmacion != "ELIMINAR":
                print("\nOperación cancelada. La clínica no ha sido eliminada.")
                return False
                
            try:
                # Implementación segura para eliminar directorios con contenido
                import shutil
                shutil.rmtree(clinic_path)
                print(f"\n✅ Clínica '{nombre_clinica}' eliminada exitosamente")
                return True
                
            except Exception as e:
                print(f"\nError al eliminar la clínica: {str(e)}")
                return False
        
        def agregar_facilitador(self, clinic_name):
            """Agrega un nuevo facilitador a una clínica existente"""
            try:
                clinic_path = self.base_path / clinic_name
                
                # Verificar que la clínica existe
                if not clinic_path.exists():
                    print(f"\nError: La clínica '{clinic_name}' no existe")
                    return False
                
                # Leer configuración de la clínica
                config_file = clinic_path / 'clinic_config.json'
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    config = {
                        'nombre_clinica': clinic_name,
                        'facilitadores_psr': [],
                        'created_at': datetime.now().isoformat()
                    }
                
                # Solicitar información del facilitador
                print("\n=== REGISTRO DE FACILITADOR PSR ===")
                nombre = input("Nombre del facilitador: ").strip()
                if not nombre:
                    print("El nombre es obligatorio")
                    return False
                
                # Verificar que no existe
                facilitador_path = clinic_path / nombre
                if facilitador_path.exists():
                    print(f"\nError: Ya existe un facilitador con el nombre '{nombre}'")
                    return False
                
                # Crear estructura del facilitador
                facilitador_path.mkdir(parents=True)
                
                # Crear estructura de grupos
                for turno in ['manana', 'tarde']:
                    grupo_path = facilitador_path / 'grupos' / turno
                    grupo_path.mkdir(parents=True)
                    
                    # Crear carpeta de pacientes
                    (grupo_path / 'pacientes').mkdir()
                    
                    # Configuración del grupo
                    grupo_config = {
                        'facilitador': nombre,
                        'turno': turno,
                        'pacientes': []
                    }
                    
                    with open(grupo_path / 'grupo_config.json', 'w', encoding='utf-8') as f:
                        json.dump(grupo_config, f, indent=2, ensure_ascii=False)
                
                # Actualizar configuración de la clínica
                info_facilitador = {
                    'nombre': nombre,
                    'fecha_registro': datetime.now().isoformat()
                }
                
                config['facilitadores_psr'].append(info_facilitador)
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Facilitador '{nombre}' agregado exitosamente")
                return True
                
            except Exception as e:
                print(f"\nError al agregar facilitador: {str(e)}")
                return False
    
    class SimpleMenuManager:
        """Versión simple del gestor de menús para evitar dependencias circulares"""
        
        def __init__(self):
            self.clinica_actual = None
            
        def show_menu(self, menu_type):
            if menu_type == MenuType.PRINCIPAL:
                return self._show_menu_principal()
            elif menu_type == MenuType.CLINICA:
                return self._show_menu_clinica()
            elif menu_type == MenuType.CLINICA_SELECCIONADA:  # Nuevo menú de clínica seleccionada
                return self._show_menu_clinica_seleccionada()
            elif menu_type == MenuType.DOCUMENTOS:
                return self._show_menu_documents()
            elif menu_type == MenuType.FACILITADORES:
                return self._show_menu_facilitadores()
            elif menu_type == MenuType.DATOS:
                return self._show_menu_datos()
            elif menu_type == MenuType.REPORTES:
                return self._show_menu_reportes()
            elif menu_type == MenuType.DESARROLLO:
                return self._show_menu_desarrollo()
            elif menu_type == MenuType.SECCIONES:
                return self._show_menu_secciones()
            else:
                print("Tipo de menú no válido")
                return '0'
        
        def _show_menu_principal(self):
            print("\n=== SISTEMA NOTEFY IA ===")
            print("1. Gestión de Clínicas")
            print("2. Procesamiento de Documentos")
            print("3. Gestión de Facilitadores")
            print("4. Generación de Datos")
            print("5. Reportes y Análisis")
            print("6. Herramientas de Desarrollo")
            print("0. Salir")
            return input("\nSeleccione una opción: ").strip()
            
        def _show_menu_clinica(self):
            print("\n=== GESTIÓN DE CLÍNICAS ===")
            print("1. Crear nueva clínica")
            print("2. Seleccionar clínica")
            print("3. Listar clínicas")
            print("4. Eliminar clínica")
            print("5. Gestión de secciones")  # Nueva opción
            print("0. Volver")
            return input("\nSeleccione una opción: ").strip()
            
        def _show_menu_documents(self):
            print("\n=== PROCESAMIENTO DE DOCUMENTOS ===")
            print("1. Importar documentos")
            print("2. Procesar PDF")
            print("3. Extraer texto")
            print("0. Volver")
            return input("\nSeleccione una opción: ").strip()
            
        def _show_menu_facilitadores(self):
            print("\n=== GESTIÓN DE FACILITADORES ===")
            print("1. Ver grupos")
            print("2. Asignar pacientes")
            print("3. Actualizar información")
            print("4. Importar lista de pacientes")
            print("5. Agregar nuevo facilitador")
            print("6. Eliminar facilitador")
            print("0. Volver")
            return input("\nSeleccione una opción: ").strip()
            
        def _show_menu_datos(self):
            print("\n=== GENERACIÓN DE DATOS ===")
            print("1. Generar pacientes")
            print("2. Generar FARC")
            print("3. Generar BIO")
            print("4. Generar MTP")
            print("0. Volver")
            return input("\nSeleccione una opción: ").strip()
            
        def _show_menu_reportes(self):
            print("\n=== REPORTES Y ANÁLISIS ===")
            print("1. Ver estadísticas")
            print("2. Generar informes")
            print("3. Exportar datos")
            print("0. Volver")
            return input("\nSeleccione una opción: ").strip()
            
        def _show_menu_desarrollo(self):
            print("\n=== HERRAMIENTAS DE DESARROLLO ===")
            print("1. Ejecutar pruebas")
            print("2. Validar plantillas")
            print("3. Ver logs")
            print("0. Volver")
            return input("\nSeleccione una opción: ").strip()
            
        def _show_menu_clinica_seleccionada(self):
            """Muestra el menú de opciones para una clínica específica"""
            print(f"\n=== CLÍNICA: {self.clinica_actual} ===")
            print("1. Extracción de información")
            print("2. Gestión de PDF")
            print("3. Generación de datos sintéticos")
            print("4. Gestión de facilitadores")
            print("5. Reportes y análisis")
            print("0. Volver al menú principal")
            return input("\nSeleccione una opción: ").strip()
        
        def _show_menu_secciones(self):
            """Muestra el menú de gestión de secciones"""
            print("\n=== GESTIÓN DE SECCIONES Y DOCUMENTOS ===")
            print("1. Ver estructura de secciones")
            print("2. Consolidar documentos por sección")
            print("3. Analizar campo específico")
            print("4. Forzar actualización de JSONs")
            print("0. Volver")
            return input("\nSeleccione una opción: ").strip()
    
    def main():
        """Función principal del sistema Notefy IA"""
        try:
            from utils.config_manager import ConfigManager
            config = ConfigManager()
            
            # Verificar si se puede acceder a los atributos necesarios antes de usarlos
            if not hasattr(config, 'project_root'):
                raise AttributeError("El objeto ConfigManager no tiene el atributo 'project_root'")
                
            data_path = config.get_data_path()
            print("=== SISTEMA NOTEFY IA ===")
            print("Inicializando...")
            
            # Inicializar managers
            clinic_manager = SimpleClinicManager(data_path)
            menu_manager = SimpleMenuManager()
            
            # Bucle principal
            running = True
            while running:
                try:
                    option = menu_manager.show_menu(MenuType.PRINCIPAL)
                    
                    if option == '0':  # Salir
                        running = False
                        print("\n¡Gracias por usar Notefy IA!")
                        
                    elif option == '1':  # Gestión de Clínicas
                        gestion_clinicas(clinic_manager, menu_manager)
                        
                    elif option == '2':  # Procesamiento de Documentos
                        # Verificar si hay una clínica seleccionada
                        if menu_manager.clinica_actual:
                            gestion_documentos(clinic_manager, menu_manager)
                        else:
                            clinica = clinic_manager.seleccionar_clinica()
                            if clinica:
                                menu_manager.clinica_actual = clinica
                                print(f"\nClínica seleccionada: {clinica}")
                                gestion_documentos(clinic_manager, menu_manager)
                            else:
                                print("\nDebe seleccionar una clínica para acceder a esta opción.")
                                input("Presione Enter para continuar...")
                                
                    elif option == '3':  # Gestión de Facilitadores
                        gestion_facilitadores(clinic_manager, menu_manager)
                        
                    elif option == '4':  # Generación de Datos
                        gestion_datos(clinic_manager, menu_manager)
                        
                    elif option == '5':  # Reportes y Análisis
                        gestion_reportes(clinic_manager, menu_manager)
                        
                    elif option == '6':  # Herramientas de Desarrollo
                        gestion_desarrollo(clinic_manager, menu_manager)
                        
                except Exception as e:
                    logger.error(f"Error en el menú principal: {str(e)}")
                    print(f"\nError: {str(e)}")
                    input("Presione Enter para continuar...")
                    
        except Exception as e:
            logger.error(f"Error de inicialización: {str(e)}")
            print(f"\nError al iniciar el sistema: {str(e)}")
            print("\nVerifique las siguientes posibles causas:")
            print("1. La estructura de archivos está dañada")
            print("2. Faltan dependencias")
            print("3. La configuración es incorrecta")
            print("\nReporte este error si persiste.")
            input("Presione Enter para salir...")
            return

    def gestion_clinicas(clinic_manager, menu_manager):
        """Gestión de clínicas"""
        while True:
            option = menu_manager.show_menu(MenuType.CLINICA)
            
            if option == '0':  # Volver
                break
                
            elif option == '1':  # Crear nueva clínica
                name = input("\nIngrese el nombre de la nueva clínica: ").strip()
                if name:
                    try:
                        if clinic_manager.crear_clinica(name):
                            # Si la clínica se creó exitosamente, preguntar si quiere seleccionarla
                            if input("\n¿Desea seleccionar esta clínica ahora? (S/N): ").upper() == 'S':
                                menu_manager.clinica_actual = name
                                print(f"\nClínica seleccionada: {name}")
                                gestionar_clinica_seleccionada(clinic_manager, menu_manager)
                                break
                    except Exception as e:
                        print(f"\nError al crear la clínica: {str(e)}")
                        import traceback
                        traceback.print_exc()  # Muestra la traza completa del error
                        input("\nPresione Enter para continuar...")
                
            elif option == '2':  # Seleccionar clínica
                try:
                    clinica = clinic_manager.seleccionar_clinica()
                    if clinica:
                        # Verificar que la estructura es válida antes de seleccionarla
                        if clinic_manager.verificar_estructura(clinica):
                            menu_manager.clinica_actual = clinica
                            print(f"\nClínica seleccionada: {clinica}")
                            gestionar_clinica_seleccionada(clinic_manager, menu_manager)
                            break
                        else:
                            print(f"\nLa estructura de la clínica '{clinica}' no es válida")
                            print("Se recomienda crear una nueva clínica o revisar los archivos")
                            input("\nPresione Enter para continuar...")
                except Exception as e:
                    print(f"\nError al seleccionar la clínica: {str(e)}")
                    input("\nPresione Enter para continuar...")
                
            elif option == '3':  # Listar clínicas
                clinic_manager.listar_clinicas()
                input("\nPresione Enter para continuar...")
                
            elif option == '4':  # Eliminar clínica
                clinica = clinic_manager.seleccionar_clinica()
                if clinica:
                    clinic_manager.eliminar_clinica(clinica)
                    input("\nPresione Enter para continuar...")
                    
            elif option == '5':  # Gestión de secciones
                clinica = clinic_manager.seleccionar_clinica()
                if clinica:
                    gestion_secciones(clinic_manager, menu_manager, clinica)

    def gestion_documentos(clinic_manager, menu_manager):
        """Gestión de documentos"""
        # Verificar primero si hay una clínica seleccionada
        if not menu_manager.clinica_actual:
            menu_manager.clinica_actual = clinic_manager.seleccionar_clinica()
            if not menu_manager.clinica_actual:
                print("\nDebe seleccionar una clínica para gestionar documentos.")
                return
        
        while True:
            option = menu_manager.show_menu(MenuType.DOCUMENTOS)
            
            if option == '0':  # Volver
                break
                
            elif option == '1':  # Importar documentos
                importar_documentos(clinic_manager, menu_manager)
                
            elif option == '2':  # Procesar PDF
                procesar_pdf(clinic_manager, menu_manager)
                
            elif option == '3':  # Extraer texto
                extraer_texto_pdf(clinic_manager, menu_manager)

    def importar_documentos(clinic_manager, menu_manager):
        """Importa documentos desde diferentes formatos"""
        print("\n=== IMPORTAR DOCUMENTOS ===")
        print("Formatos soportados:")
        print("1. CSV")
        print("2. Excel (XLS, XLSX)")
        print("3. JSON")
        print("4. YAML")
        
        try:
            # Intentar importar el módulo LectorArchivos
            from lector_archivos.lector import LectorArchivos
            
            formato = input("\nSeleccione el formato (0 para volver): ")
            if formato == '0':
                return
                
            ruta = input("\nIngrese la ruta del archivo a importar: ")
            if os.path.exists(ruta):
                print(f"\n✅ Archivo encontrado: {ruta}")
                
                # Usar el módulo real de lectura de archivos
                lector = LectorArchivos()
                datos = lector.leer_archivo(ruta)
                
                if datos:
                    print(f"Importados {len(datos)} registros correctamente")
                else:
                    print("No se pudieron importar datos del archivo")
            else:
                print(f"\n❌ Archivo no encontrado: {ruta}")
                
            input("\nPresione Enter para continuar...")
            
        except ImportError:
            print("\nEl módulo de lectura de archivos no está disponible.")
            print("Esta funcionalidad está en desarrollo.")
            input("\nPresione Enter para continuar...")

    def procesar_pdf(clinic_manager, menu_manager):
        """Procesa documentos PDF utilizando el PDFExtractor"""
        try:
            # Intentar importar PDFExtractor y SearchVisualizer
            try:
                from pdf_extractor.pdf_extractor import PDFExtractor
                from utils.search_visualizer import SearchVisualizer
                from utils.menu_manager import MenuManager  # Importar MenuManager para usar sus utilidades
            except ImportError as e:
                print(f"\nError: No se pudo importar módulos necesarios: {str(e)}")
                print("Es posible que necesite instalar dependencias adicionales.")
                print("Ejecute: pip install pdfminer.six PyPDF2 pillow pdf2image pytesseract")
                input("\nPresione Enter para continuar...")
                return
            
            print("\n=== PROCESAMIENTO DE PDF ===")
            
            # Verificar si hay una clínica seleccionada
            if not menu_manager.clinica_actual:
                print("\nError: Debe seleccionar una clínica primero.")
                input("\nPresione Enter para continuar...")
                return
            
            # Configurar ruta de salida basada en la clínica seleccionada
            clinic_path = Path(os.path.join(data_path, menu_manager.clinica_actual))
            if not clinic_path.exists():
                print(f"\nError: La clínica {menu_manager.clinica_actual} no existe.")
                input("\nPresione Enter para continuar...")
                return
            
            # Actualizar MenuManager con la clínica actual
            MenuManager.clinica_actual = menu_manager.clinica_actual
            MenuManager.base_path = Path(data_path)
            
            # Mostrar el menú de procesamiento de PDF
            result = MenuManager.mostrar_menu_pdf()
            
            # Si el resultado no es None, significa que se ejecutó exitosamente
            if result is not None:
                print("\n✅ Proceso completado correctamente.")
                
        except Exception as e:
            import traceback
            print(f"\nError al procesar PDF: {str(e)}")
            traceback.print_exc()
            print("\nSe han encontrado errores en el procesamiento.")
            input("\nPresione Enter para continuar...")

    def extraer_texto_pdf(clinic_manager, menu_manager):
        """Extrae texto de documentos PDF"""
        try:
            # Intentar importar PDFExtractor
            from pdf_extractor.pdf_extractor import PDFExtractor
            
            print("\n=== EXTRACCIÓN DE TEXTO DE PDF ===")
            
            # Solicitar ruta del archivo
            file_path = input("\nIngrese la ruta del archivo PDF: ").strip()
            
            if not file_path:
                print("Debe especificar una ruta de archivo.")
                input("\nPresione Enter para continuar...")
                return
                
            if not os.path.exists(file_path):
                print(f"\n❌ Archivo no encontrado: {file_path}")
                input("\nPresione Enter para continuar...")
                return
            
            # Preguntar si se debe usar OCR
            usar_ocr = input("\n¿Desea utilizar OCR para la extracción? (S/N): ").upper() == 'S'
            
            # Usar el extractor existente
            extractor = PDFExtractor()
            
            # Mostrar métodos disponibles
            print("\nUtilizando métodos de extracción disponibles...")
            contenido, calidad = extractor.leer_pdf(file_path)
            
            if not contenido:
                print("\n❌ No se pudo extraer texto del documento")
            else:
                print(f"\n✅ Texto extraído correctamente (Calidad: {calidad}%)")
                
                # Mostrar vista previa
                print("\nVista previa:")
                print("-" * 50)
                preview = contenido[:500] + "..." if len(contenido) > 500 else contenido
                print(preview)
                print("-" * 50)
                
                # Preguntar si se quiere guardar
                if input("\n¿Desea guardar el texto extraído? (S/N): ").upper() == 'S':
                    # Definir output_path antes de usarlo
                    if not menu_manager.clinica_actual:
                        print("Error: Debe seleccionar una clínica primero.")
                        input("\nPresione Enter para continuar...")
                        return

                    # Construir ruta de salida
                    output_path = (clinic_manager.base_path / 
                                 menu_manager.clinica_actual / 
                                 'output' / 
                                 datetime.now().strftime("%Y%m%d_%H%M%S") / 
                                 os.path.splitext(file_path)[0] + "_texto.txt")
                    
                    # Asegurar que el directorio existe
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(contenido)
                        
                    print(f"\n✅ Texto guardado en: {output_path}")
            
            input("\nPresione Enter para continuar...")
            
        except ImportError:
            print("\nEl módulo PDFExtractor no está disponible.")
            print("Esta funcionalidad está en desarrollo.")
            input("\nPresione Enter para continuar...")
            
        except Exception as e:
            print(f"\nError al extraer texto: {str(e)}")
            input("\nPresione Enter para continuar...")

    def gestion_facilitadores(clinic_manager, menu_manager):
        """Gestión de facilitadores"""
        # Verificar primero si hay una clínica seleccionada
        if not menu_manager.clinica_actual:
            menu_manager.clinica_actual = clinic_manager.seleccionar_clinica()
            if not menu_manager.clinica_actual:
                print("\nDebe seleccionar una clínica para gestionar facilitadores.")
                input("\nPresione Enter para continuar...")
                return
        
        try:
            # Intentar importar la clase para gestión de facilitadores
            from utils.clinic_manager import ClinicManager
            
            # Se crea una instancia temporal para acceder a las funciones
            clinic_mgr = ClinicManager()
            clinic_mgr.current_clinic = menu_manager.clinica_actual
            
            while True:
                # Mostrar menú de gestión de facilitadores
                print("\n=== GESTIÓN DE FACILITADORES ===")
                print(f"Clínica actual: {menu_manager.clinica_actual}")
                print("1. Ver grupos")
                print("2. Asignar pacientes")
                print("3. Actualizar información")
                print("4. Importar lista de pacientes")
                print("5. Agregar nuevo facilitador")
                print("6. Eliminar facilitador")
                print("0. Volver")
                
                option = input("\nSeleccione una opción: ").strip()
                
                if option == '0':  # Volver
                    break
                    
                elif option == '1':  # Ver grupos
                    # Verificar si hay facilitadores para mostrar
                    config_file = clinic_manager.base_path / menu_manager.clinica_actual / 'clinic_config.json'
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        if not config.get('facilitadores_psr', []):
                            print("\nNo hay facilitadores registrados en esta clínica.")
                            print("Primero debe agregar facilitadores usando la opción 'Agregar nuevo facilitador'.")
                            input("\nPresione Enter para continuar...")
                            continue
                            
                        # Solicitar selección de facilitador
                        print("\nFacilitadores disponibles:")
                        for idx, facilitador in enumerate(config['facilitadores_psr'], 1):
                            print(f"{idx}. {facilitador['nombre']}")
                            
                        sel_facilitador = input("\nSeleccione un facilitador (0 para cancelar): ").strip()
                        if sel_facilitador == '0':
                            continue
                            
                        try:
                            idx_facilitador = int(sel_facilitador) - 1
                            if 0 <= idx_facilitador < len(config['facilitadores_psr']):
                                facilitador_name = config['facilitadores_psr'][idx_facilitador]['nombre']
                                clinic_mgr.ver_grupos_facilitador(menu_manager.clinica_actual, facilitador_name)
                            else:
                                print("\nSelección de facilitador no válida")
                        except ValueError:
                            print("\nPor favor ingrese un número válido")
                            
                    except (FileNotFoundError, json.JSONDecodeError):
                        print("\nError al leer la configuración de la clínica")
                        
                    input("\nPresione Enter para continuar...")
                    
                elif option == '2':  # Asignar pacientes
                    result = clinic_mgr.asignar_pacientes_facilitador(menu_manager.clinica_actual)
                    # Ya se maneja la pausa dentro de la función
                    
                elif option == '3':  # Actualizar información
                    clinic_mgr.actualizar_facilitador(menu_manager.clinica_actual)
                    input("\nPresione Enter para continuar...")
                    
                elif option == '4':  # Importar lista de pacientes
                    print("\nFuncionalidad de importación de pacientes")
                    print("Esta función permite importar listas de pacientes desde archivos CSV o Excel.")
                    print("Seleccione la opción 'Asignar pacientes' para utilizar esta funcionalidad.")
                    input("\nPresione Enter para continuar...")
                    
                elif option == '5':  # Agregar facilitador
                    result = clinic_mgr.agregar_facilitador(menu_manager.clinica_actual)
                    if not result:
                        print("\nNo se pudo agregar el facilitador. Intente nuevamente.")
                    input("\nPresione Enter para continuar...")
                    
                elif option == '6':  # Eliminar facilitador
                    clinic_mgr.eliminar_facilitador(menu_manager.clinica_actual)
                    input("\nPresione Enter para continuar...")
                    
                else:
                    print("\nOpción no válida. Por favor ingrese un número entre 0 y 6.")
                    input("\nPresione Enter para continuar...")
                    
        except ImportError:
            # Si el módulo no está disponible, mostrar mensaje de desarrollo
            print("\nEl módulo de gestión de facilitadores no está disponible.")
            print("Esta funcionalidad está en desarrollo.")
            input("\nPresione Enter para continuar...")

    def gestion_datos(clinic_manager, menu_manager):
        """Generación de datos sintéticos"""
        # Verificar primero si hay una clínica seleccionada
        if not menu_manager.clinica_actual:
            menu_manager.clinica_actual = clinic_manager.seleccionar_clinica()
            if not menu_manager.clinica_actual:
                print("\nDebe seleccionar una clínica para generar datos.")
                return
        
        # Lista de módulos exportadores y sus nombres de clase
        exportadores_info = {
            '1': {'nombre': 'pacientes', 'modulo': 'pacientes.exportador', 'clase': 'ExportadorPacientes'},
            '2': {'nombre': 'FARC', 'modulo': 'FARC.exportador', 'clase': 'ExportadorFARC'},
            '3': {'nombre': 'BIO', 'modulo': 'BIO.exportador', 'clase': 'ExportadorBIO'},
            '4': {'nombre': 'MTP', 'modulo': 'MTP.exportador', 'clase': 'ExportadorMTP'}
        }
        
        # Verificar qué módulos están disponibles
        modulos_disponibles = {}
        
        # Buscar módulos en múltiples ubicaciones posibles
        for opcion, info in exportadores_info.items():
            # Lista de posibles rutas de importación para cada módulo
            posibles_rutas = [
                info['modulo'],                      # ej: pacientes.exportador
                f"exportadores.{info['nombre']}",    # ej: exportadores.pacientes
                info['nombre'],                      # ej: pacientes
                f"{info['nombre'].lower()}"          # ej: farc (en minúsculas)
            ]
            
            # Intentar encontrar el módulo en cualquiera de las rutas
            modulo_encontrado = False
            for ruta in posibles_rutas:
                try:
                    if importlib.util.find_spec(ruta):
                        modulo = importlib.import_module(ruta)
                        # Verificar si la clase existe en el módulo
                        if hasattr(modulo, info['clase']):
                            modulos_disponibles[opcion] = {
                                'modulo': modulo,
                                'clase': getattr(modulo, info['clase']),
                                'nombre': info['nombre']
                            }
                            modulo_encontrado = True
                            break
                except (ImportError, AttributeError):
                    continue
                    
            if not modulo_encontrado:
                logger.warning(f"Módulo exportador {info['nombre']} no encontrado")
        
        # Simulador básico para módulos no disponibles
        class ExportadorSimulado:
            """Clase simulada para exportadores no disponibles"""
            def __init__(self, tipo):
                self.tipo = tipo
                
            def generar_datos_sinteticos(self, cantidad):
                print(f"\nSimulando generación de {cantidad} registros de {self.tipo}...")
                print("Esta funcionalidad no está completamente implementada.")
                print(f"Se hubieran generado {cantidad} registros en la carpeta 'Data/{menu_manager.clinica_actual}/{self.tipo.lower()}'")
        
        while True:
            option = menu_manager.show_menu(MenuType.DATOS)
            
            if option == '0':  # Volver
                break
                
            if option in exportadores_info:
                nombre_exportador = exportadores_info[option]['nombre']
                
                if option in modulos_disponibles:
                    # Usar el exportador real si está disponible
                    try:
                        clase_exportador = modulos_disponibles[option]['clase']
                        exportador = clase_exportador()
                        print(f"\n=== GENERACIÓN DE DATOS DE {nombre_exportador.upper()} ===")
                        cantidad = input("\nIngrese la cantidad de registros a generar (1-100): ")
                        
                        try:
                            cantidad = int(cantidad)
                            if 1 <= cantidad <= 100:
                                exportador.generar_datos_sinteticos(cantidad)
                                input("\nPresione Enter para continuar...")
                            else:
                                print("La cantidad debe estar entre 1 y 100")
                                input("\nPresione Enter para continuar...")
                        except ValueError:
                            print("Por favor ingrese un número válido")
                            input("\nPresione Enter para continuar...")
                    except Exception as e:
                        print(f"\nError al inicializar el exportador: {str(e)}")
                        # Usar el simulador como fallback
                        exportador_simulado = ExportadorSimulado(nombre_exportador)
                        exportador_simulado.generar_datos_sinteticos(10)
                        input("\nPresione Enter para continuar...")
                else:
                    # Usar el simulador si el módulo no está disponible
                    print(f"\n=== GENERACIÓN DE DATOS DE {nombre_exportador.upper()} (SIMULADO) ===")
                    cantidad = input("\nIngrese la cantidad de registros a generar (1-100): ")
                    
                    try:
                        cantidad = int(cantidad)
                        if not (1 <= cantidad <= 100):
                            cantidad = 10
                            print("Se usará el valor predeterminado de 10 registros")
                    except ValueError:
                        cantidad = 10
                        print("Se usará el valor predeterminado de 10 registros")
                    
                    exportador_simulado = ExportadorSimulado(nombre_exportador)
                    exportador_simulado.generar_datos_sinteticos(cantidad)
                    input("\nPresione Enter para continuar...")

    def gestion_reportes(clinic_manager, menu_manager):
        """Reportes y análisis"""
        # Verificar primero si hay una clínica seleccionada
        if not menu_manager.clinica_actual:
            menu_manager.clinica_actual = clinic_manager.seleccionar_clinica()
            if not menu_manager.clinica_actual:
                print("\nDebe seleccionar una clínica para ver reportes.")
                return
        
        option = menu_manager.show_menu(MenuType.REPORTES)
        
        # Implementación básica para mostrar progreso
        if option != '0':
            print("\nGenerando reportes...")
            print("Esta función está en desarrollo.")
            input("\nPresione Enter para continuar...")

    def gestion_desarrollo(clinic_manager, menu_manager):
        """Herramientas de desarrollo"""
        option = menu_manager.show_menu(MenuType.DESARROLLO)
        
        # Implementación básica para mostrar progreso
        if option != '0':
            print("\nEjecutando herramientas de desarrollo...")
            print("Esta función está en desarrollo.")
            input("\nPresione Enter para continuar...")

    def gestionar_clinica_seleccionada(clinic_manager, menu_manager):
        """Gestiona las opciones para una clínica específica"""
        while True:
            option = menu_manager.show_menu(MenuType.CLINICA_SELECCIONADA)
            
            if option == '0':  # Volver al menú principal
                break
                
            elif option == '1':  # Extracción de información
                gestion_documentos(clinic_manager, menu_manager)
                
            elif option == '2':  # Gestión de PDF
                procesar_pdf(clinic_manager, menu_manager)
                
            elif option == '3':  # Generación de datos sintéticos
                gestion_datos(clinic_manager, menu_manager)
                
            elif option == '4':  # Gestión de facilitadores
                gestion_facilitadores(clinic_manager, menu_manager)
                
            elif option == '5':  # Reportes y análisis
                gestion_reportes(clinic_manager, menu_manager)
                
    def gestion_secciones(clinic_manager, menu_manager, nombre_clinica):
        """Gestión de secciones y documentos"""
        from utils.section_manager import SectionManager
        
        section_manager = SectionManager(clinic_manager.base_path)
        
        # Asegurar que existe la estructura básica
        if not section_manager.setup_clinic_structure(nombre_clinica):
            print("\nError: No se pudo configurar la estructura de secciones")
            return
        
        while True:
            option = menu_manager.show_menu(MenuType.SECCIONES)
            
            if option == '0':
                break
                
            elif option == '1':  # Ver estructura
                mostrar_estructura_secciones(clinic_manager, nombre_clinica)
                
            elif option == '2':  # Consolidar documentos
                consolidar_documentos_seccion(
                    clinic_manager, 
                    section_manager, 
                    nombre_clinica
                )
                
            elif option == '3':  # Analizar campo
                analizar_campo_seccion(section_manager, nombre_clinica)
                
            elif option == '4':  # Forzar actualización
                if section_manager.force_update(nombre_clinica):
                    print("\n✅ JSONs actualizados correctamente")
                else:
                    print("\n❌ Error al actualizar JSONs")

    def mostrar_estructura_secciones(clinic_manager, nombre_clinica):
        """Muestra la estructura de carpetas y archivos"""
        clinic_path = clinic_manager.base_path / nombre_clinica
        resumen_path = clinic_path / 'Resumen_Secciones'
        
        print(f"\n=== ESTRUCTURA DE {nombre_clinica} ===")
        print("\nCarpeta de resúmenes:")
        if resumen_path.exists():
            for json_file in resumen_path.glob('*.json'):
                print(f"  └── {json_file.name}")
        else:
            print("  └── (No existe la carpeta de resúmenes)")

    def consolidar_documentos_seccion(clinic_manager, section_manager, nombre_clinica):
        """Permite consolidar documentos por sección"""
        # Seleccionar facilitador
        facilitadores = clinic_manager._obtener_facilitadores_clinica(nombre_clinica)
        if not facilitadores:
            print("\nNo hay facilitadores disponibles")
            return
            
        print("\nFacilitadores disponibles:")
        for idx, facilitador in enumerate(facilitadores, 1):
            print(f"{idx}. {facilitador['nombre']}")
            
        try:
            idx = int(input("\nSeleccione facilitador: ")) - 1
            if not (0 <= idx < len(facilitadores)):
                print("Facilitador no válido")
                return
                
            facilitador = facilitadores[idx]['nombre']
            
            # Seleccionar tipo de documento
            print("\nTipos de documento:")
            tipos_doc = ['FARC', 'BIO', 'MTP', 'notas_progreso']
            for idx, tipo in enumerate(tipos_doc, 1):
                print(f"{idx}. {tipo}")
                
            idx = int(input("\nSeleccione tipo de documento: ")) - 1
            if not (0 <= idx < len(tipos_doc)):
                print("Tipo no válido")
                return
                
            tipo_doc = tipos_doc[idx]
            
            # Consolidar documentos
            if section_manager.consolidate_documents(
                nombre_clinica, facilitador, tipo_doc
            ):
                print("\n✅ Documentos consolidados correctamente")
            else:
                print("\n❌ Error al consolidar documentos")
                
        except ValueError:
            print("\nSelección no válida")
            return

    def analizar_campo_seccion(section_manager, nombre_clinica):
        """Analiza un campo específico de los documentos"""
        print("\nSeleccione sección:")
        print("1. Mañana")
        print("2. Tarde")
        print("0. Cancelar")
        
        try:
            opcion = input("\nSeleccione sección: ").strip()
            if opcion == '0':
                return
                
            seccion = 'manana' if opcion == '1' else 'tarde' if opcion == '2' else None
            if not seccion:
                print("Sección no válida")
                return
                
            campo = input("\nIngrese el campo a analizar: ").strip()
            if not campo:
                print("Campo no válido")
                return
                
            resultados = section_manager.analyze_section_data(
                nombre_clinica, seccion, campo
            )
            
            if resultados:
                print("\nResultados del análisis:")
                print(json.dumps(resultados, indent=2, ensure_ascii=False))
            else:
                print("\nNo se encontraron datos para analizar")
                
        except ValueError:
            print("\nSelección no válida")
            return

    if __name__ == "__main__":
        main()
        
except Exception as e:
    logger.error(f"Error de inicialización: {str(e)}")
    print(f"Error al iniciar el sistema: {str(e)}")
    print("\nVerifique las siguientes posibles causas:")
    print("1. La estructura de archivos está dañada")
    print("2. Faltan dependencias")
    print("3. La configuración es incorrecta")
    print("\nReporte este error si persiste.")
    input("Presione Enter para salir...")