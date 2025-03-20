from pathlib import Path
import json
from datetime import datetime
from pdf_extractor.pdf_extractor import PDFExtractor
from utils.data_formats import DataFormatHandler

class MenuManager:
    """Gestor centralizado de todos los menús del sistema"""

    # Variable de clase para almacenar la clínica actual
    clinica_actual = None
    base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")

    @staticmethod
    def set_clinica_actual(nombre_clinica):
        """Establece la clínica actual para el manejo de menús"""
        MenuManager.clinica_actual = nombre_clinica

    @staticmethod
    def mostrar_menu_principal():
        """Muestra el menú principal del sistema"""
        print("\n=== Sistema de Generación de Datos Sintéticos ===")
        print("1. Crear nueva clínica")
        print("2. Seleccionar clínica existente")
        print("3. Listar clínicas")
        print("0. Salir")
        
        while True:
            try:
                opcion = input("\nSeleccione una opción: ").strip()
                if opcion in ['0', '1', '2', '3']:
                    return opcion
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

    @staticmethod
    def mostrar_menu_clinica(nombre_clinica):
        """Muestra el menú principal de una clínica"""
        print(f"\n{'='*50}")
        print(f"CLÍNICA: {nombre_clinica}")
        print(f"{'='*50}")

        print("\n=== GESTIÓN DOCUMENTAL ===")
        print("1. Extracción de información")
        print("   • Archivos CSV, Excel, TSV")
        print("   • Documentos JSON, YAML")
        print("   • Otros formatos tabulares")
        print("\n2. Gestión de PDF")
        print("   • Extraer texto")
        print("   • Procesar con IA")
        print("   • Convertir formatos")
        print("\n3. Generación de datos sintéticos")
        print("   • FARC (Evaluaciones)")
        print("   • BIO (Historiales)")
        print("   • MTP (Planes)")

        print("\n=== GESTIÓN GENERAL DE LA CLÍNICA ===")
        print("4. Gestión de facilitadores")
        print("   • Ver grupos y pacientes")
        print("   • Asignar pacientes")
        print("   • Actualizar información")
        print("\n5. Reportes y análisis")
        print("   • Estadísticas generales")
        print("   • Informes de actividad")
        print("   • Exportar datos")
        print("6. Gestión de plantillas")
        print("7. Importación y Consolidación de Datos")
        print("   • Importar datos")
        print("   • Consolidar información")
        print("   • Ver resultados")

        print("\n0. Volver al menú principal")
        
        while True:
            try:
                opcion = input("\nSeleccione una opción: ").strip()
                if opcion in ['0', '1', '2', '3', '4', '5', '6', '7']:
                    return opcion
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

    @staticmethod
    def mostrar_menu_extraccion():
        """Muestra el menú de extracción de información"""
        print("\n=== EXTRACCIÓN DE INFORMACIÓN ===")
        print("1. Seleccionar archivo")
        print("   • CSV, Excel (XLS, XLSX)")
        print("   • TSV, ODS (OpenDocument)")
        print("   • JSON, YAML")
        print("   • HTML, otros formatos tabulares")
        print("2. Ver calidad de extracción")
        print("3. Mejorar extracción con IA")
        print("0. Volver")
        
        return MenuManager._solicitar_opcion(['0', '1', '2', '3'])

    @staticmethod
    def mostrar_opciones_exportacion():
        """Muestra las opciones disponibles de exportación"""
        print("\n=== FORMATOS DE EXPORTACIÓN DISPONIBLES ===")
        print("1. TXT (Texto plano)")
        print("2. JSON (Estructurado)")
        print("3. YAML (Legible)")
        print("4. CSV (Tabular)")
        print("5. XLSX (Excel)")
        print("6. HTML (Web)")
        print("7. TSV (Tabulado)")
        print("8. ODS (OpenDocument)")
        print("0. Cancelar")
        
        while True:
            try:
                opcion = input("\nSeleccione el formato de exportación: ").strip()
                if opcion == '0':
                    return None
                    
                formatos = {
                    '1': 'txt',
                    '2': 'json',
                    '3': 'yaml',
                    '4': 'csv',
                    '5': 'xlsx',
                    '6': 'html',
                    '7': 'tsv',
                    '8': 'ods'
                }
                
                if opcion in formatos:
                    return formatos[opcion]
                    
                print("Formato no válido")
            except ValueError:
                print("Por favor ingrese un número válido")

    @staticmethod
    def mostrar_menu_pdf():
        """Muestra el menú de gestión de PDFs"""
        while True:
            print("\n=== PROCESAMIENTO DE PDF ===")
            print("1. Procesar nuevo documento")
            print("2. Ver documentos procesados")
            print("0. Volver al menú principal")
            
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == '0':
                return 'menu_principal'
            elif opcion == '1':
                # Procesar documento
                info_seleccion = MenuManager.seleccionar_documento_pdf()
                if info_seleccion is None:
                    continue

                try:
                    # Procesar el PDF directamente
                    extractor = PDFExtractor()
                    contenido, calidad = extractor.leer_pdf(info_seleccion['pdf'])

                    if contenido:
                        # Construir ruta de salida
                        output_path = MenuManager._construir_ruta_salida(info_seleccion)
                        output_path.mkdir(parents=True, exist_ok=True)

                        # Preparar y guardar datos
                        datos = MenuManager._preparar_datos_informe(info_seleccion, contenido, calidad)
                        if MenuManager._exportar_resultados(datos, output_path, info_seleccion):
                            if not MenuManager.confirmar_accion("¿Desea procesar otro documento?"):
                                return None
                        continue
                    else:
                        MenuManager.mostrar_error("No se pudo extraer contenido del PDF")
                except Exception as e:
                    MenuManager.mostrar_error(f"Error al procesar PDF: {str(e)}")
                continue
            elif opcion == '2':
                if MenuManager.ver_documentos_procesados() == 'menu_principal':
                    return 'menu_principal'

    @staticmethod
    def _construir_ruta_salida(info_seleccion):
        """Construye la ruta de salida para los archivos procesados"""
        nombre_carpeta = info_seleccion['paciente']['nombre'].replace(' ', '_').lower()
        return (MenuManager.base_path / 
                MenuManager.clinica_actual / 
                info_seleccion['facilitador'] / 
                'grupos' /
                info_seleccion['turno'] / 
                'pacientes' /
                nombre_carpeta /
                info_seleccion['tipo_doc'] /
                'output')

    @staticmethod
    def _preparar_datos_informe(info_seleccion, contenido, calidad):
        """Prepara el diccionario de datos para el informe"""
        return {
            'fecha_extraccion': datetime.now().isoformat(),
            'tipo_documento': info_seleccion['tipo_doc'],
            'facilitador': info_seleccion['facilitador'],
            'paciente': info_seleccion['paciente']['nombre'],
            'calidad_extraccion': calidad,
            'contenido': contenido,
            'estadisticas': {
                'caracteres': len(contenido),
                'palabras': len(contenido.split()),
                'lineas': len(contenido.splitlines())
            }
        }

    @staticmethod
    def _exportar_resultados(datos, output_path, info_seleccion):
        """Exporta los resultados en los formatos seleccionados"""
        print(f"\nDocumento procesado correctamente")
        print(f"Calidad de extracción: {datos['calidad_extraccion']}%")
        
        while True:
            formato = MenuManager.mostrar_opciones_exportacion()
            if not formato:
                break

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = DataFormatHandler.SUPPORTED_FORMATS[formato]['ext']
            nombre_salida = f"{info_seleccion['pdf'].stem}_{timestamp}{extension}"
            archivo_salida = output_path / nombre_salida

            if DataFormatHandler.save_data(datos, archivo_salida, formato):
                print(f"\nArchivo guardado como: {archivo_salida}")
                MenuManager.mostrar_exito(f"Documento guardado en formato {formato.upper()}")
                
                if not MenuManager.confirmar_accion("¿Desea exportar en otro formato?"):
                    break
            else:
                MenuManager.mostrar_error(f"Error al guardar en formato {formato}")
        
        return True

    @staticmethod
    def ver_documentos_procesados():
        """Permite ver los documentos procesados"""
        try:
            # 1. Seleccionar facilitador
            print("\n=== FACILITADORES DISPONIBLES ===")
            facilitadores = MenuManager.obtener_facilitadores()
            if not facilitadores:
                return None

            for idx, facilitador in enumerate(facilitadores, 1):
                print(f"{idx}. {facilitador['nombre']}")
            print("0. Volver")

            opcion = input("\nSeleccione el facilitador: ").strip()
            if opcion == '0':
                return 'menu_principal'

            try:
                idx_facilitador = int(opcion) - 1
                if not (0 <= idx_facilitador < len(facilitadores)):
                    print("Facilitador no válido")
                    return None
                facilitador = facilitadores[idx_facilitador]

                # 2. Seleccionar turno
                print("\n=== TURNOS ===")
                print("1. Mañana")
                print("2. Tarde")
                print("0. Volver")

                turno = input("\nSeleccione el turno: ").strip()
                turnos = {'1': 'manana', '2': 'tarde'}
                if turno not in ['1', '2']:
                    return None

                # 3. Obtener pacientes del turno
                pacientes = MenuManager.obtener_pacientes_turno(
                    facilitador['nombre'],
                    turnos[turno]
                )

                if not pacientes:
                    print("No hay pacientes en este turno")
                    return None

                # 4. Seleccionar paciente
                print("\n=== PACIENTES ===")
                for idx, paciente in enumerate(pacientes, 1):
                    print(f"{idx}. {paciente['nombre']}")
                print("0. Volver")

                opcion_paciente = input("\nSeleccione el paciente: ").strip()
                if opcion_paciente == '0':
                    return None

                idx_paciente = int(opcion_paciente) - 1
                if not (0 <= idx_paciente < len(pacientes)):
                    print("Paciente no válido")
                    return None

                paciente = pacientes[idx_paciente]
                nombre_carpeta = paciente['nombre'].replace(' ', '_').lower()

                # 5. Mostrar tipos de documentos disponibles
                print("\n=== TIPOS DE DOCUMENTOS ===")
                tipos_doc = ['FARC', 'BIO', 'MTP', 'notas_progreso', 'Internal_Referral', 'Intake']
                for idx, tipo in enumerate(tipos_doc, 1):
                    print(f"{idx}. {tipo}")
                print("0. Volver")

                opcion_tipo = input("\nSeleccione el tipo de documento: ").strip()
                if opcion_tipo == '0':
                    return None

                try:
                    idx_tipo = int(opcion_tipo) - 1
                    if not (0 <= idx_tipo < len(tipos_doc)):
                        print("Tipo de documento no válido")
                        return None

                    # 6. Buscar documentos procesados
                    output_path = (MenuManager.base_path / 
                                MenuManager.clinica_actual / 
                                facilitador['nombre'] / 
                                'grupos' /
                                turnos[turno] / 
                                'pacientes' /
                                nombre_carpeta /
                                tipos_doc[idx_tipo] /
                                'output')

                    if not output_path.exists():
                        print("\nNo hay documentos procesados para esta selección")
                        return None

                    # 7. Mostrar lista de documentos
                    archivos = list(output_path.glob('*.*'))
                    if not archivos:
                        print("\nNo hay documentos procesados")
                        return None

                    print("\n=== DOCUMENTOS PROCESADOS ===")
                    for idx, archivo in enumerate(archivos, 1):
                        print(f"{idx}. {archivo.name}")
                    print("0. Volver")

                    # 8. Seleccionar documento para ver
                    opcion_doc = input("\nSeleccione un documento para ver su contenido: ").strip()
                    if opcion_doc == '0':
                        return None

                    idx_doc = int(opcion_doc) - 1
                    if not (0 <= idx_doc < len(archivos)):
                        print("Documento no válido")
                        return None

                    # 9. Mostrar contenido del documento
                    archivo = archivos[idx_doc]
                    with open(archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        print("\n=== CONTENIDO DEL DOCUMENTO ===")
                        print(contenido[:1000] + "..." if len(contenido) > 1000 else contenido)
                        
                        input("\nPresione Enter para continuar...")

                except ValueError:
                    print("Opción no válida")
                except Exception as e:
                    print(f"Error al leer el archivo: {str(e)}")

            except ValueError:
                print("Opción no válida")

        except Exception as e:
            print(f"Error: {str(e)}")

        return None

    @staticmethod
    def seleccionar_documento_pdf():
        """Guía la selección del documento PDF a procesar"""
        # Primero seleccionar el tipo de documento
        print("\n=== TIPO DE DOCUMENTO PDF ===")
        print("1. FARC (Evaluación)")
        print("2. BIO (Historia clínica)")
        print("3. MTP (Plan de tratamiento)")
        print("4. Notas de progreso")
        print("5. Internal Referral")
        print("6. Intake")
        print("0. Cancelar")
        
        tipo_doc = input("\nSeleccione el tipo de documento: ").strip()
        if tipo_doc == '0' or tipo_doc not in ['1', '2', '3', '4', '5', '6']:
            return None

        tipos = {
            '1': 'FARC',
            '2': 'BIO',
            '3': 'MTP',
            '4': 'notas_progreso',
            '5': 'Internal_Referral',
            '6': 'Intake'
        }

        # 2. Seleccionar facilitador
        print("\n=== FACILITADORES DISPONIBLES ===")
        facilitadores = MenuManager.obtener_facilitadores()
        if not facilitadores:
            print("No hay facilitadores disponibles")
            return None
            
        for idx, facilitador in enumerate(facilitadores, 1):
            print(f"{idx}. {facilitador['nombre']}")
        print("0. Cancelar")

        opcion_facilitador = input("\nSeleccione el facilitador: ").strip()
        if opcion_facilitador == '0':
            return None

        try:
            idx_facilitador = int(opcion_facilitador) - 1
            if not (0 <= idx_facilitador < len(facilitadores)):
                print("Facilitador no válido")
                return None
            facilitador = facilitadores[idx_facilitador]
        except ValueError:
            print("Opción no válida")
            return None

        # 3. Seleccionar turno
        print("\n=== SELECCIÓN DE TURNO ===")
        print("1. Mañana")
        print("2. Tarde")
        print("0. Cancelar")
        
        turno = input("\nSeleccione el turno: ").strip()
        if turno == '0' or turno not in ['1', '2']:
            return None

        turnos = {
            '1': 'manana',
            '2': 'tarde'
        }

        # 4. Obtener y mostrar lista de pacientes del turno seleccionado
        try:
            pacientes = MenuManager.obtener_pacientes_turno(
                facilitador['nombre'],
                turnos[turno]
            )
            if not pacientes:
                print(f"No hay pacientes en el turno de {turnos[turno]}")
                return None

            print("\n=== PACIENTES DISPONIBLES ===")
            for idx, paciente in enumerate(pacientes, 1):
                print(f"{idx}. {paciente['nombre']} (ID: {paciente['id']})")
            print("0. Cancelar")

            opcion_paciente = input("\nSeleccione el paciente: ").strip()
            if opcion_paciente == '0':
                return None

            try:
                idx_paciente = int(opcion_paciente) - 1
                if not (0 <= idx_paciente < len(pacientes)):
                    print("Paciente no válido")
                    return None
                paciente = pacientes[idx_paciente]

                # 5. Buscar PDFs en la carpeta input del tipo de documento
                pdfs = MenuManager.obtener_pdfs_input(
                    facilitador['nombre'],
                    turnos[turno],
                    paciente['id'],
                    tipos[tipo_doc]
                )

                if not pdfs:
                    print(f"No hay archivos PDF en la carpeta input de {tipos[tipo_doc]}")
                    return None

                print("\n=== PDFs DISPONIBLES ===")
                for idx, pdf in enumerate(pdfs, 1):
                    print(f"{idx}. {pdf.name}")
                print("0. Cancelar")

                opcion_pdf = input("\nSeleccione el PDF a procesar: ").strip()
                if opcion_pdf == '0':
                    return None

                try:
                    idx_pdf = int(opcion_pdf) - 1
                    if not (0 <= idx_pdf < len(pdfs)):
                        print("PDF no válido")
                        return None
                    pdf_seleccionado = pdfs[idx_pdf]

                    return {
                        'tipo_doc': tipos[tipo_doc],
                        'facilitador': facilitador['nombre'],
                        'turno': turnos[turno],
                        'paciente': paciente,
                        'pdf': pdf_seleccionado
                    }

                except ValueError:
                    print("Opción de PDF no válida")
                    return None

            except ValueError:
                print("Opción de paciente no válida")
                return None

        except Exception as e:
            print(f"Error al obtener pacientes: {str(e)}")
            return None

    @staticmethod
    def obtener_pacientes_turno(facilitador, turno):
        """Obtiene la lista de pacientes de un turno específico"""
        try:
            # Construir ruta al archivo de configuración del grupo
            grupo_config = (MenuManager.base_path / 
                          MenuManager.clinica_actual / 
                          facilitador / 
                          'grupos' / 
                          turno / 
                          'grupo_config.json')

            if not grupo_config.exists():
                print(f"Error: No se encontró la configuración del grupo en {grupo_config}")
                return []

            # Leer archivo de configuración del grupo
            with open(grupo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('pacientes', [])

        except Exception as e:
            print(f"Error al leer pacientes del grupo: {str(e)}")
            return []

    @staticmethod
    def obtener_pdfs_input(facilitador, turno, id_paciente, tipo_doc):
        """Obtiene la lista de PDFs en la carpeta input del tipo de documento"""
        try:
            # Primero obtener el nombre formateado del paciente desde el grupo_config.json
            grupo_config = (MenuManager.base_path / 
                          MenuManager.clinica_actual / 
                          facilitador / 
                          'grupos' / 
                          turno / 
                          'grupo_config.json')

            if not grupo_config.exists():
                print(f"Error: No se encontró el archivo de configuración del grupo")
                return []

            # Leer configuración del grupo para obtener info del paciente
            with open(grupo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                pacientes = config.get('pacientes', [])
                paciente = next((p for p in pacientes if str(p['id']) == str(id_paciente)), None)
                
                if not paciente:
                    print(f"Error: No se encontró el paciente con ID {id_paciente}")
                    return []

                # Formatear nombre del paciente para la carpeta
                nombre_carpeta = paciente['nombre'].replace(' ', '_').lower()

            # Construir ruta a la carpeta input usando el nombre formateado
            input_path = (MenuManager.base_path / 
                         MenuManager.clinica_actual / 
                         facilitador / 
                         'grupos' / 
                         turno / 
                         'pacientes' / 
                         nombre_carpeta /  # Usar nombre_carpeta en lugar de id_paciente
                         tipo_doc / 
                         'input')

            if not input_path.exists():
                print(f"Error: No se encontró la carpeta input en {input_path}")
                return []

            # Buscar archivos PDF
            pdfs = list(input_path.glob('*.pdf'))
            if not pdfs:
                print(f"No hay archivos PDF en {input_path}")
                
            return pdfs

        except Exception as e:
            print(f"Error al buscar PDFs: {str(e)}")
            return []

    @staticmethod
    def obtener_facilitadores():
        """Obtiene la lista de facilitadores desde clinic_config.json"""
        if not MenuManager.clinica_actual:
            print("Error: No hay una clínica seleccionada")
            return []

        try:
            config_path = MenuManager.base_path / MenuManager.clinica_actual / 'clinic_config.json'
            if not config_path.exists():
                print(f"Error: No se encontró el archivo de configuración en {config_path}")
                return []

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('facilitadores_psr', [])

        except Exception as e:
            print(f"Error al leer facilitadores: {str(e)}")
            return []

    @staticmethod
    def mostrar_pacientes(pacientes):
        """Muestra lista de pacientes y permite seleccionar uno"""
        print("\n=== PACIENTES DISPONIBLES ===")
        for idx, paciente in enumerate(pacientes, 1):
            print(f"{idx}. {paciente['nombre']} (ID: {paciente['id']})")
        print("0. Cancelar")
        
        while True:
            try:
                opcion = int(input("\nSeleccione el paciente: "))
                if opcion == 0:
                    return None
                if 1 <= opcion <= len(pacientes):
                    return pacientes[opcion - 1]
                print("Número de paciente no válido")
            except ValueError:
                print("Por favor ingrese un número válido")

    @staticmethod
    def mostrar_pdfs_disponibles(pdfs):
        """Muestra PDFs disponibles en la carpeta input y permite seleccionar uno"""
        print("\nPDFs disponibles en input:")
        for idx, pdf in enumerate(pdfs, 1):
            print(f"{idx}. {pdf.name}")
        print("0. Cancelar")
        
        while True:
            try:
                opcion = int(input("\nSeleccione el PDF a procesar: "))
                if opcion == 0:
                    return None
                if 1 <= opcion <= len(pdfs):
                    return pdfs[opcion - 1]
                print("Número de PDF no válido")
            except ValueError:
                print("Por favor ingrese un número válido")

    @staticmethod
    def mostrar_menu_datos_sinteticos():
        """Muestra el menú de generación de datos sintéticos"""
        print("\n=== GENERACIÓN DE DATOS SINTÉTICOS ===")
        print("1. Pacientes")
        print("2. FARC (Evaluaciones)")
        print("3. BIO (Historias)")
        print("4. MTP (Planes)")
        print("5. Generar todos")
        print("0. Volver")
        
        return MenuManager._solicitar_opcion(['0', '1', '2', '3', '4', '5'])

    @staticmethod
    def mostrar_menu_facilitadores():
        """Muestra el menú de gestión de facilitadores"""
        print("\n=== GESTIÓN DE FACILITADORES PSR ===")
        print("1. Ver grupos y pacientes")
        print("2. Asignar pacientes a grupos")
        print("3. Actualizar información")
        print("4. Importar lista de pacientes")
        print("0. Volver")
        
        return MenuManager._solicitar_opcion(['0', '1', '2', '3', '4'])

    @staticmethod
    def mostrar_menu_reportes():
        """Muestra el menú de reportes y análisis"""
        print("\n=== REPORTES Y ANÁLISIS ===")
        print("1. Ver estadísticas generales")
        print("2. Generar informe de actividad")
        print("3. Exportar datos procesados")
        print("4. Ver histórico")
        print("0. Volver")
        
        return MenuManager._solicitar_opcion(['0', '1', '2', '3', '4'])

    @staticmethod
    def mostrar_menu_tipos_archivo():
        """Muestra el menú de selección de tipo de archivo"""
        print("\n=== TIPOS DE ARCHIVO ===")
        print("1. Pacientes")
        print("2. FARC (Alcohol y drogas)")
        print("3. BIO (Biografía)")
        print("4. MTP (Master Training Plan)")
        print("5. Internal Referral")
        print("6. Intake")
        print("0. Volver")
        return input("\nSeleccione el tipo de archivo: ").strip()

    @staticmethod
    def mostrar_menu_plantillas():
        """Muestra el menú de gestión de plantillas de importación"""
        print("\n=== GESTIÓN DE PLANTILLAS DE IMPORTACIÓN ===")
        print("1. Generar plantilla desde archivo de campos")
        print("   • Archivo: templates/archivos de campos/Pasientes_Campos.txt")
        print("   • Genera estructura para software máster")
        print("   • Guarda en formato compatible")
        print("0. Volver")
        
        return input("\nSeleccione una opción: ").strip()

    @staticmethod
    def mostrar_tipos_plantilla():
        """Muestra los tipos de plantilla disponibles"""
        print("\n=== TIPOS DE PLANTILLA ===")
        print("1. FARC (Evaluación)")
        print("2. BIO (Historia clínica)")
        print("3. MTP (Plan de tratamiento)")
        print("4. Notas de progreso")
        print("5. Internal Referral")
        print("6. Intake")
        print("0. Cancelar")
        
        tipos = {
            '1': 'FARC',
            '2': 'BIO',
            '3': 'MTP',
            '4': 'notas_progreso',
            '5': 'Internal_Referral',
            '6': 'Intake'
        }
        
        opcion = input("\nSeleccione el tipo de plantilla: ").strip()
        return tipos.get(opcion)

    @staticmethod
    def _solicitar_opcion(opciones_validas):
        """Método auxiliar para solicitar y validar opciones"""
        while True:
            try:
                opcion = input("\nSeleccione una opción: ").strip()
                if opcion in opciones_validas:
                    return opcion
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

    @staticmethod
    def confirmar_accion(mensaje):
        """Solicita confirmación para una acción"""
        return input(f"\n{mensaje} (S/N): ").upper() == 'S'

    @staticmethod
    def mostrar_error(mensaje):
        """Muestra un mensaje de error"""
        print(f"\nError: {mensaje}")

    @staticmethod
    def mostrar_exito(mensaje):
        """Muestra un mensaje de éxito"""
        print(f"\nÉxito: {mensaje}")

    @staticmethod
    def solicitar_ruta_archivo(tipo="archivo"):
        """Solicita la ruta de un archivo"""
        return input(f"\nIngrese la ruta del {tipo}: ").strip()

    @staticmethod
    def procesar_pdf_seleccionado(info_seleccion):
        """Procesa el PDF seleccionado y lo guarda en la carpeta output"""
        try:
            # Construir ruta de salida usando el nombre del paciente formateado
            nombre_carpeta = info_seleccion['paciente']['nombre'].replace(' ', '_').lower()
            output_path = (MenuManager.base_path / 
                          MenuManager.clinica_actual / 
                          info_seleccion['facilitador'] / 
                          'grupos' /
                          info_seleccion['turno'] / 
                          'pacientes' /
                          nombre_carpeta /
                          info_seleccion['tipo_doc'] /
                          'output')

            # Asegurar que la carpeta output existe
            output_path.mkdir(parents=True, exist_ok=True)

            # Procesar el PDF
            extractor = PDFExtractor()
            texto = extractor.extraer_texto(info_seleccion['pdf'])

            # Crear nombre del archivo de salida con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_salida = f"{info_seleccion['pdf'].stem}_{timestamp}.txt"
            archivo_salida = output_path / nombre_salida

            # Guardar el texto extraído
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write(texto)

            print(f"\nTexto extraído guardado en: {archivo_salida}")
            return True

        except Exception as e:
            print(f"Error procesando PDF: {str(e)}")
            return False
