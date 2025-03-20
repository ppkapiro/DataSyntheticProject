import sys
import os
import importlib
from pathlib import Path
import logging
from enum import Enum, auto

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
    
    def main():
        """Función principal del sistema Notefy IA"""
        try:
            from utils.config_manager import ConfigManager
            
            # Obtener la configuración
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
                    clinic_manager.crear_clinica(name)
                    
            elif option == '2':  # Seleccionar clínica
                clinica = clinic_manager.seleccionar_clinica()
                if clinica:
                    menu_manager.clinica_actual = clinica
                    print(f"\nClínica seleccionada: {clinica}")
                    # Mostrar el menú de la clínica seleccionada
                    gestionar_clinica_seleccionada(clinic_manager, menu_manager)
                    # Cuando vuelva, romper el ciclo para volver al menú principal
                    break
                
            elif option == '3':  # Listar clínicas
                clinic_manager.listar_clinicas()
    
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
            from pdf_extractor.pdf_extractor import PDFExtractor
            from utils.search_visualizer import SearchVisualizer
            
            print("\n=== PROCESAMIENTO DE PDF ===")
            
            # Configurar ruta de salida basada en la clínica seleccionada
            clinica_path = Path(os.path.join(data_path, menu_manager.clinica_actual))
            output_dir = clinica_path / "output"
            output_dir.mkdir(exist_ok=True, parents=True)
            
            # Tipos de documentos PDF soportados
            tipos = {
                '1': 'FARC',
                '2': 'BIO',
                '3': 'MTP',
                '4': 'pdf_notas',
                '5': 'pdf_otros'
            }
            
            print("\nTipos de documentos PDF disponibles:")
            for key, value in tipos.items():
                print(f"{key}. {value}")
            print("0. Volver")
            
            opcion = input("\nSeleccione el tipo de documento: ")
            if opcion == '0' or opcion not in tipos:
                return
            
            tipo_seleccionado = tipos[opcion]
            
            print(f"\nHa seleccionado: {tipo_seleccionado}")
            
            # Preguntar si se desea buscar automáticamente o proporcionar una ruta
            file_path = input("\nIngrese la ruta del archivo PDF (dejar en blanco para buscar automáticamente): ").strip()
            
            if not file_path:
                # Mostrar visualización de búsqueda
                visualizer = SearchVisualizer(project_root=Path(__file__).parent)
                print("\nIniciando búsqueda de documentos PDF...")
                
                # Primero buscar en ubicaciones específicas
                search_locations = [
                    clinica_path / tipo_seleccionado.lower() / "input",
                    clinica_path / "input",
                    Path(__file__).parent / "input"
                ]
                
                found_files = []
                for location in search_locations:
                    if location.exists():
                        print(f"\nBuscando en: {location}")
                        location_files = visualizer.visualize_search(
                            location, 
                            pattern="*.pdf", 
                            max_depth=1,
                            interactive=False
                        )
                        found_files.extend(location_files)
                
                # Si no se encuentra nada, hacer una búsqueda más amplia
                if not found_files:
                    print("\nNo se encontraron archivos en ubicaciones predefinidas.")
                    print("Realizando búsqueda en estructura completa de la clínica...")
                    found_files = visualizer.visualize_search(
                        clinica_path,
                        pattern="*.pdf",
                        max_depth=3,
                        interactive=True
                    )
                
                if found_files:
                    print("\nSeleccione un archivo de la lista:")
                    for idx, file in enumerate(found_files, 1):
                        print(f"{idx}. {file.name}")
                    
                    while True:
                        try:
                            selection = int(input("\nSeleccione archivo (0 para cancelar): "))
                            if selection == 0:
                                return
                            if 1 <= selection <= len(found_files):
                                file_path = str(found_files[selection - 1])
                                break
                            print("Opción no válida")
                        except ValueError:
                            print("Por favor ingrese un número válido")
                else:
                    print("\nNo se encontraron archivos PDF en el sistema.")
                    return
            
            # Usar el PDFExtractor existente
            extractor = PDFExtractor()
            
            # Procesar el PDF con la implementación existente
            resultado = extractor.procesar_pdf(
                file_path=file_path,
                output_dir=str(output_dir),
                clinic_initials=menu_manager.clinica_actual[:2].upper(),
                tipo_pdf=tipo_seleccionado
            )
            
            if resultado:
                print(f"\n✅ PDF procesado correctamente: {resultado}")
            else:
                print("\n❌ Error al procesar el PDF")
            
            input("\nPresione Enter para continuar...")
            
        except ImportError as e:
            print(f"\nEl módulo no está disponible: {str(e)}")
            print("Esta funcionalidad está en desarrollo.")
            input("\nPresione Enter para continuar...")
        except Exception as e:
            print(f"\nError al procesar PDF: {str(e)}")
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
            
            # Usar el extractor existente
            extractor = PDFExtractor()
            
            # Preguntar si se debe usar OCR
            usar_ocr = input("\n¿Desea utilizar OCR para la extracción? (S/N): ").upper() == 'S'
            
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
                    output_path = input("\nIngrese la ruta de salida (o presione Enter para usar la predeterminada): ").strip()
                    
                    if not output_path:
                        output_path = f"{os.path.splitext(file_path)[0]}_texto.txt"
                        
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
                return
        
        try:
            # Intentar importar la clase para gestión de facilitadores
            from utils.clinic_manager import ClinicManager
            
            # Se crea una instancia temporal para acceder a las funciones
            clinic_mgr = ClinicManager()
            clinic_mgr.current_clinic = menu_manager.clinica_actual
            
            while True:
                option = menu_manager.show_menu(MenuType.FACILITADORES)
                
                if option == '0':  # Volver
                    break
                    
                elif option == '1':  # Ver grupos
                    clinic_mgr.ver_grupos_facilitador(menu_manager.clinica_actual)
                    
                elif option == '2':  # Asignar pacientes
                    clinic_mgr.asignar_pacientes_facilitador(menu_manager.clinica_actual)
                    
                elif option == '3':  # Actualizar información
                    clinic_mgr._actualizar_facilitador()
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
