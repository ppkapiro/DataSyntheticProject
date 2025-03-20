from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Any
from utils.data_formats import DataFormatHandler
from pdf_extractor.pdf_extractor import PDFExtractor  # Añadida esta importación
from utils.menu_manager import MenuManager  # Añadida esta importación
from utils.template_manager import TemplateManager  # Añadida esta importación
from utils.config_manager import ConfigManager  # Nuevo import

class ClinicManager:
    """Gestor de estructura de clínicas y facilitadores PSR"""
    
    # Definición correcta de la ruta base - sin duplicación de "Data synthetic"
    base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")
    
    def __init__(self, base_path=None):
        # Inicializar con la ruta proporcionada o usar ConfigManager para obtenerla
        config = ConfigManager()
        
        # Si se proporciona una ruta, usarla; si no, usar la ruta de config
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Asegurar que self.base_path tenga la ruta correcta
            self.base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Data")
            
            # Verificar que la ruta exista o crearla
            if not self.base_path.exists():
                print(f"[DEBUG] Creando directorio de datos: {self.base_path}")
                self.base_path.mkdir(parents=True, exist_ok=True)
        
        print(f"[DEBUG] ClinicManager inicializado con ruta: {self.base_path}")
        
        # Estructura simplificada para facilitador
        self.psr_structure = {
            'grupos': {
                'manana': {
                    'pacientes': {}
                },
                'tarde': {
                    'pacientes': {}
                }
            }
        }

        # Estructura completa para cada paciente
        self.patient_structure = {
            'FARC': {
                'input': {},
                'output': {}
            },
            'BIO': {
                'input': {},
                'output': {}
            },
            'MTP': {
                'input': {},
                'output': {}
            },
            'notas_progreso': {
                'input': {},
                'output': {}
            },
            'Internal_Referral': {  # Nueva carpeta
                'input': {},
                'output': {}
            },
            'Intake': {  # Nueva carpeta
                'input': {},
                'output': {}
            }
        }

    def get_menu_manager(self):
        # Importación perezosa para evitar dependencias circulares
        from utils.menu_manager import MenuManager
        if not hasattr(self, '_menu_manager'):
            self._menu_manager = MenuManager(self)
        return self._menu_manager

    def get_import_consolidator(self):
        from core.import_consolidator import ImportConsolidator
        if not hasattr(self, '_import_consolidator'):
            self._import_consolidator = ImportConsolidator(self)
        return self._import_consolidator

    def gestionar_clinica(self):
        # Ejemplo de uso de los módulos inyectados
        menu_manager = self.get_menu_manager()
        consolidator = self.get_import_consolidator()
        # ...código de gestión clínica...
        print("Gestionando clínica...")

    def crear_clinica(self, nombre_clinica):
        """Crea una nueva clínica y solicita información de facilitadores PSR"""
        clinic_path = self.base_path / nombre_clinica
        
        if (clinic_path.exists()):
            print(f"\nError: La clínica '{nombre_clinica}' ya existe")
            return False
            
        # Crear directorio principal de la clínica
        clinic_path.mkdir(parents=True)
        
        # Gestionar facilitadores PSR
        facilitadores = []
        while True:
            if input("\n¿Desea agregar un facilitador PSR? (S/N): ").upper() == 'S':
                # Recolectar información del facilitador
                info_facilitador = self._solicitar_info_facilitador()
                if info_facilitador:
                    facilitador_path = clinic_path / info_facilitador['nombre']
                    
                    # Crear estructura completa del facilitador
                    if self._crear_estructura_facilitador(facilitador_path, info_facilitador):
                        facilitadores.append(info_facilitador)
                        print(f"\nFacilitador PSR '{info_facilitador['nombre']}' creado con éxito")
                        
                        # Mostrar resumen de la estructura creada
                        self._mostrar_estructura_facilitador(facilitador_path)
                        
                        # Preguntar por importación de pacientes
                        self._gestionar_importacion_inicial(nombre_clinica, info_facilitador['nombre'])
                    else:
                        print("Error al crear la estructura del facilitador")
            else:
                break

        if not facilitadores:
            print("\nAdvertencia: No se crearon facilitadores PSR en la clínica")
            return False

        # Guardar configuración de la clínica
        config = {
            'nombre_clinica': nombre_clinica,
            'facilitadores_psr': facilitadores,
            'created_at': datetime.now().isoformat()
        }
        
        config_file = clinic_path / 'clinic_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"\nClínica '{nombre_clinica}' creada exitosamente")
        print(f"Total de facilitadores PSR: {len(facilitadores)}")
        return True

    def _solicitar_info_facilitador(self):
        """Solicita información mínima del facilitador PSR"""
        print("\n=== REGISTRO DE FACILITADOR PSR ===")
        nombre = input("Nombre del facilitador: ").strip()
        if not nombre:
            print("El nombre es obligatorio")
            return None
            
        return {
            'nombre': nombre,
            'fecha_registro': datetime.now().isoformat()
        }

    def _crear_estructura_facilitador(self, facilitador_path, info_facilitador):
        """Crea estructura básica para un facilitador PSR"""
        try:
            facilitador_path.mkdir(parents=True)
            
            # Verificar estructura global de templates si no existe
            templates_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/templates")
            templates_path.mkdir(exist_ok=True)
            (templates_path / 'Campos Codigos').mkdir(exist_ok=True)
            (templates_path / 'Campos Master Global').mkdir(exist_ok=True)
            
            # Crear grupos mañana y tarde
            for turno in ['manana', 'tarde']:
                grupo_path = facilitador_path / 'grupos' / turno
                grupo_path.mkdir(parents=True)
                
                # Crear carpeta de pacientes
                (grupo_path / 'pacientes').mkdir()
                
                # Crear archivo básico de configuración
                grupo_file = grupo_path / 'grupo_config.json'
                grupo_data = {
                    'facilitador': info_facilitador['nombre'],
                    'turno': turno,
                    'pacientes': []
                }
                with open(grupo_file, 'w', encoding='utf-8') as f:
                    json.dump(grupo_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error al crear estructura: {str(e)}")
            return False

    def _crear_estructura_recursiva(self, path, estructura):
        """Crea la estructura de carpetas de forma recursiva"""
        for nombre, subestructura in estructura.items():
            subpath = path / nombre
            subpath.mkdir(exist_ok=True)
            
            if isinstance(subestructura, dict):
                self._crear_estructura_recursiva(subpath, subestructura)

    def _mostrar_estructura_facilitador(self, facilitador_path):
        """Muestra la estructura creada para el facilitador"""
        print(f"\nEstructura creada para {facilitador_path.name}:")
        self._mostrar_arbol_directorios(facilitador_path)

    def _mostrar_arbol_directorios(self, path, nivel=0):
        """Muestra el árbol de directorios de forma recursiva"""
        prefijo = "  " * nivel + ("└── " if nivel > 0 else "")
        print(f"{prefijo}{path.name}")
        
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    self._mostrar_arbol_directorios(item, nivel + 1)
        except Exception:
            pass

    def listar_clinicas(self):
        """Lista todas las clínicas y sus facilitadores PSR"""
        print(f"[DEBUG] Intentando listar clínicas desde: {self.base_path}")
        
        try:
            # Verificar que el directorio existe
            if not self.base_path.exists():
                print(f"[ERROR] El directorio base no existe: {self.base_path}")
                return None
                
            # Listar directorios de clínicas
            clinicas = [d for d in self.base_path.iterdir() if d.is_dir()]
            
            if not clinicas:
                print(f"\n[DEBUG] No se encontraron clínicas en: {self.base_path}")
                print("\nNo hay clínicas creadas")
                return None
                
            print("\n=== CLÍNICAS EXISTENTES ===")
            clinicas_dict = {}
            
            for idx, clinica_path in enumerate(clinicas, 1):
                config_file = clinica_path / 'clinic_config.json'
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    print(f"\n{idx}. Clínica: {config['nombre_clinica']}")
                    print("   Facilitadores PSR:")
                    for facilitador in config['facilitadores_psr']:
                        print(f"   - {facilitador['nombre']}")
                    clinicas_dict[idx] = config['nombre_clinica']
                else:
                    print(f"\n{idx}. Clínica: {clinica_path.name} (sin configuración)")
                    clinicas_dict[idx] = clinica_path.name
                    
            return clinicas_dict
            
        except FileNotFoundError as e:
            print(f"[ERROR] No se encuentra el directorio: {self.base_path}")
            print(f"[ERROR] Detalle: {str(e)}")
            print("Sugerencia: Verifique la configuración de rutas en el sistema.")
            return None
        except Exception as e:
            print(f"[ERROR] Error al listar clínicas: {str(e)}")
            return None

    def seleccionar_clinica(self):
        """Permite seleccionar una clínica por número"""
        clinicas_dict = self.listar_clinicas()
        
        if not clinicas_dict:
            return None
            
        while True:
            try:
                opcion = input("\nSeleccione el número de la clínica (0 para cancelar): ")
                if opcion == '0':
                    return None
                    
                opcion = int(opcion)
                if opcion in clinicas_dict:
                    return clinicas_dict[opcion]
                    
                print("Número de clínica no válido")
            except ValueError:
                print("Por favor ingrese un número válido")

    def verificar_estructura(self, nombre_clinica):
        """Verifica que la estructura de la clínica esté completa"""
        clinic_path = self.base_path / nombre_clinica
        if not clinic_path.exists():
            print(f"\nError: La clínica '{nombre_clinica}' no existe")
            return False
            
        # Verificar directorio import_data
        import_data_path = clinic_path / 'import_data'
        import_data_path.mkdir(exist_ok=True)
            
        config_file = clinic_path / 'clinic_config.json'
        if not config_file.exists():
            print(f"\nError: Configuración no encontrada para '{nombre_clinica}'")
            return False
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Verificar cada facilitador
        for facilitador in config['facilitadores_psr']:
            facilitador_path = clinic_path / facilitador['nombre']
            if not self._verificar_estructura_facilitador(facilitador_path):
                print(f"\nError: Estructura incompleta en facilitador '{facilitador['nombre']}'")
                return False
                
        return True

    def _verificar_estructura_facilitador(self, facilitador_path):
        """Verifica la estructura de carpetas de un facilitador PSR"""
        if not facilitador_path.exists():
            return False
            
        for key, value in self.psr_structure.items():
            module_path = facilitador_path / key
            if not module_path.exists():
                return False
                
            for subdir, subvalue in value.items():
                if isinstance(subvalue, dict):
                    subdir_path = module_path / subdir
                    if not subdir_path.exists():
                        return False
                    for subsubdir in subvalue:
                        if not (subdir_path / subsubdir).exists():
                            return False
                else:
                    if not (module_path / subdir).exists():
                        return False
                    
        return True

    def _crear_estructura_paciente(self, paciente_path, paciente_info):
        """Crea estructura básica de carpetas para un paciente"""
        try:
            paciente_path.mkdir(parents=True, exist_ok=True)
            
            # Crear carpetas principales actualizadas
            for carpeta in ['FARC', 'BIO', 'MTP', 'notas_progreso', 'Internal_Referral', 'Intake']:
                carpeta_path = paciente_path / carpeta
                carpeta_path.mkdir(exist_ok=True)
                
                # Crear subcarpetas input/output
                (carpeta_path / 'input').mkdir(exist_ok=True)
                (carpeta_path / 'output').mkdir(exist_ok=True)

            # Crear archivo info básico
            info_file = paciente_path / 'info_paciente.json'
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(paciente_info, f, indent=2, ensure_ascii=False)

            return True
            
        except Exception as e:
            print(f"Error creando estructura para {paciente_info['nombre']}: {str(e)}")
            return False

    def asignar_paciente_grupo(self, clinic_name, facilitador_name, turno, paciente_info):
        """Asigna un paciente a un grupo específico"""
        try:
            # Ruta al grupo y su configuración
            grupo_path = self.base_path / clinic_name / facilitador_name / 'grupos' / turno
            grupo_file = grupo_path / 'grupo_config.json'
            
            if not grupo_file.exists():
                print(f"Error: No se encontró el archivo del grupo {turno}")
                return False
            
            # Actualizar lista de pacientes del grupo
            with open(grupo_file, 'r', encoding='utf-8') as f:
                grupo_data = json.load(f)
            
            grupo_data['pacientes'].append(paciente_info)
            
            with open(grupo_file, 'w', encoding='utf-8') as f:
                json.dump(grupo_data, f, indent=2, ensure_ascii=False)
            
            # Crear estructura del paciente dentro del grupo
            paciente_path = grupo_path / 'pacientes' / str(paciente_info['id'])
            if self._crear_estructura_paciente(paciente_path, paciente_info):
                print(f"Paciente asignado exitosamente al grupo de {turno}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error al asignar paciente: {str(e)}")
            return False

    def ver_grupos_facilitador(self, clinic_name, facilitador_name):
        """Muestra los pacientes asignados a cada grupo del facilitador"""
        try:
            grupos_path = self.base_path / clinic_name / facilitador_name / 'grupos'
            
            print(f"\nGrupos del facilitador {facilitador_name}:")
            for grupo in ['manana', 'tarde']:
                grupo_file = grupos_path / grupo / 'grupo_config.json'
                if grupo_file.exists():
                    with open(grupo_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"\nGrupo {grupo.upper()}:")
                        print(f"Total pacientes: {len(data['pacientes'])}")
                        for paciente in data['pacientes']:
                            print(f"- {paciente['nombre']} ({paciente['id']})")
                else:
                    print(f"\nNo se encontró el grupo de {grupo}")
                    
        except Exception as e:
            print(f"Error al mostrar grupos: {str(e)}")

    def importar_pacientes_grupo(self, clinic_name, facilitador_name, grupo, file_path=None):
        """Importa pacientes y crea sus estructuras de carpetas usando solo los nombres"""
        try:
            # Leer archivo
            df = DataFormatHandler.read_data(file_path)
            if df is None:
                print("No se pudo leer el archivo")
                return False

            print("\nVista previa de los datos:")
            print(df.head())
            
            if input("\n¿Los datos son correctos? (S/N): ").upper() != 'S':
                print("Importación cancelada")
                return False

            # Ruta base para los pacientes del grupo
            grupo_base_path = self.base_path / clinic_name / facilitador_name / 'grupos' / grupo / 'pacientes'
            
            # Lista para guardar la información de los pacientes
            pacientes_procesados = []
            
            # Procesar cada fila, usando solo el nombre
            for idx, row in df.iterrows():
                # Obtener solo el nombre del paciente
                nombre = str(row.get('Nombre', '')).strip()
                
                if nombre:  # Si hay un nombre válido
                    # Información mínima del paciente
                    paciente_info = {
                        'id': str(idx + 1),
                        'nombre': nombre
                    }
                    
                    # Crear carpeta con nombre del paciente
                    nombre_carpeta = nombre.replace(' ', '_').lower()
                    paciente_path = grupo_base_path / nombre_carpeta
                    
                    # Crear estructura básica para el paciente
                    if self._crear_estructura_paciente(paciente_path, paciente_info):
                        pacientes_procesados.append(paciente_info)
                        print(f"Creada estructura para: {nombre}")

            # Actualizar archivo de configuración del grupo
            if pacientes_procesados:
                grupo_config = self.base_path / clinic_name / facilitador_name / 'grupos' / grupo / 'grupo_config.json'
                with open(grupo_config, 'r+', encoding='utf-8') as f:
                    config = json.load(f)
                    config['pacientes'] = pacientes_procesados  # Reemplazar lista completa
                    f.seek(0)
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    f.truncate()

            print(f"\nSe procesaron {len(pacientes_procesados)} pacientes")
            return True

        except Exception as e:
            print(f"Error en la importación: {str(e)}")
            return False

    def _gestionar_importacion_inicial(self, clinic_name, facilitador_name):
        """Gestiona la importación inicial de pacientes para un facilitador"""
        print("\n=== IMPORTACIÓN INICIAL DE PACIENTES ===")
        
        for turno in ['mañana', 'tarde']:
            if input(f"\n¿Desea importar lista de pacientes del grupo de {turno}? (S/N): ").upper() == 'S':
                print(f"\nImportando pacientes para el grupo de {turno}")
                print("Seleccione el archivo CSV con los datos de los pacientes")
                
                grupo = 'manana' if turno == 'mañana' else 'tarde'
                
                # Solicitar archivo
                file_path = input("\nIngrese la ruta del archivo CSV: ").strip()
                if file_path:
                    self.importar_pacientes_grupo(
                        clinic_name=clinic_name,
                        facilitador_name=facilitador_name,
                        grupo=grupo,
                        file_path=file_path
                    )
                else:
                    print(f"No se importaron pacientes para el grupo de {turno}")

        print("\nPuede gestionar los pacientes más tarde desde el menú principal")

    def asignar_pacientes_facilitador(self, clinic_name):
        """Asigna pacientes a grupos de facilitadores"""
        # Verificar que la clínica existe
        if not self.verificar_estructura(clinic_name):
            return False

        print("\nAsignación de pacientes a grupos")
        
        # Cargar configuración de la clínica
        config_file = self.base_path / clinic_name / 'clinic_config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Mostrar facilitadores disponibles
        print("\nFacilitadores disponibles:")
        for idx, facilitador in enumerate(config['facilitadores_psr'], 1):
            print(f"{idx}. {facilitador['nombre']}")

        # Seleccionar facilitador
        while True:
            try:
                opcion = int(input("\nSeleccione el facilitador (0 para cancelar): ")) - 1
                if opcion == -1:
                    return False
                if 0 <= opcion < len(config['facilitadores_psr']):
                    facilitador = config['facilitadores_psr'][opcion]
                    break
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

        # Seleccionar grupo
        print("\nGrupos disponibles:")
        print("1. Mañana")
        print("2. Tarde")
        
        grupo = None
        while True:
            try:
                opcion = int(input("\nSeleccione el grupo (0 para cancelar): "))
                if opcion == 0:
                    return False
                if opcion == 1:
                    grupo = 'manana'
                    break
                if opcion == 2:
                    grupo = 'tarde'
                    break
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

        # Solicitar ruta del archivo
        print("\nSeleccione el archivo con la lista de pacientes")
        file_path = input("Ingrese la ruta del archivo (CSV, Excel): ").strip()
        
        if not file_path:
            print("No se proporcionó una ruta de archivo")
            return False
            

        # Importar pacientes
        return self.importar_pacientes_grupo(
            clinic_name=clinic_name,
            facilitador_name=facilitador['nombre'],
            grupo=grupo,
            file_path=file_path
        )

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
        
        try:
            opcion = input("\nSeleccione el tipo de procesamiento (1-3): ").strip()
            if opcion == '2':
                return self._mostrar_menu_pdf()
            if opcion in ['1', '2', '3']:
                return opcion
            print("Opción no válida. Intente nuevamente.")
        except ValueError:
            print("Por favor ingrese un número válido")

    def _mostrar_menu_pdf(self):
        """Muestra las opciones para procesar PDFs"""
        print("\n=== PROCESAMIENTO DE PDF ===")
        print("1. Extraer texto")
        print("2. Extraer texto usando IA")
        print("3. Ver calidad de extracción")
        print("0. Volver")
        
        try:
            opcion = input("\nSeleccione una opción: ").strip()
            if opcion == '0':
                return self.mostrar_menu_procesamiento()
            if opcion in ['1', '2', '3']:
                return f"pdf_{opcion}"  # Retornamos identificador específico para PDF
            print("Opción no válida")
        except ValueError:
            print("Por favor ingrese un número válido")

    def menu_gestion_archivos(self):
        """Menú de gestión de archivos"""
        while True:
            print("\n=== GESTIÓN DE ARCHIVOS ===")
            print("1. Importar nuevo archivo")
            print("2. Procesar archivo existente")
            print("3. Extraer información")
            print("4. Ver archivos procesados")
            print("0. Volver")
            
            try:
                opcion = input("\nSeleccione una opción: ").strip()
                if opcion == '0':
                    return None
                if opcion in ['1', '2', '3', '4']:
                    return opcion
                print("Opción no válida. Intente nuevamente.")
            except ValueError:
                print("Por favor ingrese un número válido")

    def seleccionar_tipo_archivo(self):
        """Menú de selección de tipo de archivo"""
        print("\n=== TIPOS DE ARCHIVO DE DATOS ===")
        print("1. Pacientes")
        print("2. FARC (Alcohol y drogas)")
        print("3. BIO (Biografía)")
        print("4. MTP (Master Training Plan)")
        
        while True:
            try:
                opcion = input("\nSeleccione el tipo de archivo (1-4): ").strip()
                if opcion in ['1', '2', '3', '4']:
                    return opcion
                print("Opción no válida. Intente nuevamente.")
            except ValueError:
                print("Por favor ingrese un número válido")

    def procesar_archivo(self, tipo_archivo):
        """Procesa un archivo según su tipo"""
        tipos = {
            '1': self._procesar_archivo_pacientes,
            '2': self._procesar_archivo_farc,
            '3': self._procesar_archivo_bio,
            '4': self._procesar_archivo_mtp
        }
        
        if tipo_archivo in tipos:
            return tipos[tipo_archivo]()
        return False

    def _procesar_archivo_pacientes(self):
        """Procesa archivo de pacientes"""
        print("\nProcesando archivo de Pacientes")
        # Implementar lógica específica para pacientes
        return True

    def _procesar_archivo_farc(self):
        """Procesa archivo FARC"""
        print("\nProcesando archivo FARC")
        # Implementar lógica específica para FARC
        return True

    def _procesar_archivo_bio(self):
        """Procesa archivo BIO"""
        print("\nProcesando archivo BIO")
        # Implementar lógica específica para BIO
        return True

    def _procesar_archivo_mtp(self):
        """Procesa archivo MTP"""
        print("\nProcesando archivo MTP")
        # Implementar lógica específica para MTP
        return True

    def procesar_clinica(self, nombre_clinica):
        """Procesa una clínica seleccionada"""
        self.current_clinic = nombre_clinica
        MenuManager.set_clinica_actual(nombre_clinica)
        clinic_path = self.base_path / nombre_clinica
        
        while True:
            print(f"\n==================================================")
            print(f"CLÍNICA: {nombre_clinica}")
            print(f"==================================================")
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
            print("\n6. Importación y Consolidación de Datos")  # Opción 6 ahora (antes 7)
            print("   • Importar datos")
            print("   • Consolidar información")
            print("   • Ver resultados")
            print("\n0. Volver al menú principal")
            
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == '0':
                return None
            elif opcion == '1':
                self._procesar_extraccion_informacion()
            elif opcion == '2':
                resultado = self._procesar_pdf()
                if resultado == 'menu_principal':
                    return 'menu_principal'
            elif opcion == '3':
                self._generar_datos_sinteticos()
            elif opcion == '4':
                self._gestionar_facilitadores()
            elif opcion == '5':
                self._gestionar_reportes()
            elif opcion == '6':  # Cambiado de 7 a 6
                self._menu_importacion_consolidacion(nombre_clinica, clinic_path)

    def _procesar_extraccion_informacion(self):
        """Maneja la extracción de información de archivos"""
        while True:
            opcion = MenuManager.mostrar_menu_extraccion()
            
            if opcion == '0':
                break
            elif opcion == '1':
                file_path = MenuManager.solicitar_ruta_archivo("archivo a procesar")
                if file_path:
                    try:
                        datos = DataFormatHandler.read_data(file_path)
                        if datos is not None:
                            print("\nVista previa de los datos:")
                            print(datos.head())
                            MenuManager.mostrar_exito("Archivo procesado correctamente")
                    except Exception as e:
                        MenuManager.mostrar_error(f"Error al procesar archivo: {str(e)}")
            elif opcion == '2':
                self._ver_calidad_extraccion()
            elif opcion == '3':
                self._mejorar_extraccion_ia()

    def _procesar_pdf(self):
        """Maneja el procesamiento de PDFs"""
        return MenuManager.mostrar_menu_pdf()

    def _generar_datos_sinteticos(self):
        """Maneja la generación de datos sintéticos"""
        while True:
            opcion = MenuManager.mostrar_menu_datos_sinteticos()
            
            if opcion == '0':
                break
            elif opcion in ['1', '2', '3', '4']:
                modulo = self.MODULES[int(opcion)-1]
                try:
                    if modulo in self.exportadores:
                        self.exportadores[modulo].generar_datos()
                        MenuManager.mostrar_exito(f"Datos {modulo} generados correctamente")
                    else:
                        MenuManager.mostrar_error(f"Módulo {modulo} no implementado")
                except Exception as e:
                    MenuManager.mostrar_error(f"Error al generar datos: {str(e)}")
            elif opcion == '5':
                self._generar_todos_datos()

    def _gestionar_facilitadores(self):
        """Maneja la gestión de facilitadores PSR"""
        while True:
            opcion = MenuManager.mostrar_menu_facilitadores()
            
            if opcion == '0':
                break
            elif opcion == '1':
                self.ver_grupos_facilitador(self.current_clinic)
            elif opcion == '2':
                self.asignar_pacientes_facilitador(self.current_clinic)  # Corregido: pasar current_clinic
            elif opcion == '3':
                self._actualizar_facilitador()
            elif opcion == '4':
                self._importar_lista_pacientes()

    def _gestionar_reportes(self):
        """Maneja los reportes y análisis"""
        while True:
            opcion = MenuManager.mostrar_menu_reportes()
            
            if opcion == '0':
                break
            elif opcion == '1':
                self._ver_estadisticas()
            elif opcion == '2':
                self._generar_informe()
            elif opcion == '3':
                self._exportar_datos()
            elif opcion == '4':
                self._ver_historico()

    def _menu_gestion_plantillas(self, nombre_clinica, clinic_path):
        """Menú de gestión de plantillas de importación"""
        template_manager = TemplateManager()
        
        while True:
            opcion = MenuManager.mostrar_menu_plantillas()
            
            if opcion == '0':
                break
            elif opcion == '1':  
                # Ruta específica para documentos de importación
                docs_path = clinic_path / 'import_data'
                docs_path.mkdir(parents=True, exist_ok=True)
                
                # Ya no necesitamos solicitar la ruta del archivo, usamos la ruta fija
                plantilla = template_manager.analizar_y_generar_plantilla(
                    tipo_doc='import_template'  # Solo pasamos el tipo de documento
                )
                
                if plantilla:
                    print("\n✅ Plantilla de importación generada con éxito")
                    
                # Crear carpeta templates si no existe
                templates_path = docs_path / 'templates'
                templates_path.mkdir(parents=True, exist_ok=True)

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

            # Procesar el PDF usando el método correcto
            extractor = PDFExtractor()
            contenido, calidad = extractor.leer_pdf(info_seleccion['pdf'])  # Cambiado de extraer_texto a leer_pdf

            if not contenido:
                print("No se pudo extraer contenido del PDF")
                return False

            # Crear nombre del archivo de salida con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_salida = f"{info_seleccion['pdf'].stem}_{timestamp}.txt"
            archivo_salida = output_path / nombre_salida

            # Guardar el texto extraído
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write(contenido)

            print(f"\nTexto extraído guardado en: {archivo_salida}")
            print(f"Calidad de extracción: {calidad}%")
            return True

        except Exception as e:
            print(f"Error procesando PDF: {str(e)}")
            return False

    def _menu_importacion_consolidacion(self, nombre_clinica: str, clinic_path: Path):
        """Menú de importación y consolidación de datos"""
        from core.import_consolidator import ImportConsolidator
        consolidator = ImportConsolidator()

        while True:
            print("\n=== IMPORTACIÓN Y CONSOLIDACIÓN DE DATOS ===")
            print(f"Clínica: {nombre_clinica}")
            print("1. Seleccionar paciente para consolidar")
            print("2. Ver documentos consolidados")
            print("0. Volver")

            opcion = input("\nSeleccione una opción: ").strip()

            if opcion == '0':
                break
            elif opcion == '1':
                # Como ya sabemos la clínica, vamos directo al flujo principal
                try:
                    # 1. Seleccionar grupo primero
                    print("\n=== SELECCIÓN DE GRUPO ===")
                    print("1. Grupo Mañana")
                    print("2. Grupo Tarde")
                    print("0. Cancelar")

                    sel_grupo = input("\nSeleccione grupo: ").strip()
                    if sel_grupo == '0':
                        continue

                    grupo = 'manana' if sel_grupo == '1' else 'tarde' if sel_grupo == '2' else None
                    if not grupo:
                        print("\n❌ Grupo no válido")
                        continue

                    # 2. Obtener y mostrar pacientes del grupo
                    pacientes = self._obtener_pacientes_grupo(nombre_clinica, grupo)
                    if not pacientes:
                        print(f"\n❌ No hay pacientes en el grupo de {grupo}")
                        continue

                    print(f"\n=== PACIENTES DEL GRUPO {grupo.upper()} ===")
                    for idx, paciente in enumerate(pacientes, 1):
                        print(f"{idx}. {paciente['nombre']} (ID: {paciente['id']})")

                    # 3. Seleccionar paciente
                    sel_paciente = input("\nSeleccione paciente (0 para cancelar): ").strip()
                    if sel_paciente == '0':
                        continue

                    idx_paciente = int(sel_paciente) - 1
                    if not (0 <= idx_paciente < len(pacientes)):
                        print("\n❌ Paciente no válido")
                        continue

                    paciente = pacientes[idx_paciente]

                    # 4. Obtener y mostrar documentos
                    documentos = self._obtener_documentos_paciente(
                        nombre_clinica=nombre_clinica,
                        grupo=grupo,
                        nombre_paciente=paciente['nombre']
                    )

                    if not documentos:
                        print("\n❌ No hay documentos disponibles para este paciente")
                        continue

                    print("\n=== DOCUMENTOS DISPONIBLES ===")
                    for idx, doc in enumerate(documentos, 1):
                        print(f"{idx}. {doc.name}")
                        print(f"   Tipo: {doc.parent.parent.name}")
                        print(f"   Fecha: {datetime.fromtimestamp(doc.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")

                    # 5. Seleccionar documentos
                    docs_seleccionados = self._seleccionar_documentos(documentos)
                    if docs_seleccionados:
                        output_file = consolidator.consolidate_documents(
                            patient_name=paciente['nombre'],
                            documents=docs_seleccionados,
                            clinic_code=nombre_clinica
                        )
                        if output_file:
                            print(f"\n✅ Datos consolidados en: {output_file}")
                        else:
                            print("\n❌ Error en la consolidación")

                except ValueError:
                    print("\n❌ Selección no válida")
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")

            elif opcion == '2':
                self._mostrar_consolidaciones(nombre_clinica)

    def _seleccionar_documentos(self, documentos: List[Path]) -> List[Path]:
        """Permite seleccionar múltiples documentos"""
        seleccionados = []
        
        while True:
            try:
                entrada = input("\nSeleccione documentos (números separados por coma, 0 para cancelar): ").strip()
                if entrada == '0':
                    break

                indices = [int(x.strip()) - 1 for x in entrada.split(',')]
                for idx in indices:
                    if 0 <= idx < len(documentos):
                        seleccionados.append(documentos[idx])
                    else:
                        print(f"Índice no válido: {idx + 1}")
                
                if seleccionados:
                    return seleccionados
                
            except ValueError:
                print("Entrada no válida. Use números separados por comas")
        
        return []

    def _obtener_facilitadores_clinica(self, nombre_clinica: str) -> List[Dict[str, Any]]:
        """Obtiene lista de facilitadores de una clínica"""
        config_file = self.base_path / nombre_clinica / 'clinic_config.json'
        if not config_file.exists():
            return []

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('facilitadores_psr', [])
        except Exception:
            return []

    def _obtener_pacientes_grupo_facilitador(self, nombre_clinica: str, 
                                           facilitador: str, grupo: str) -> List[Dict[str, Any]]:
        """Obtiene pacientes de un grupo específico de un facilitador"""
        grupo_config = self.base_path / nombre_clinica / facilitador / 'grupos' / grupo / 'grupo_config.json'
        if not grupo_config.exists():
            return []

        try:
            with open(grupo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('pacientes', [])
        except Exception:
            return []

    def _obtener_documentos_paciente_facilitador(self, nombre_clinica: str, 
                                               facilitador: str, grupo: str, 
                                               nombre_paciente: str) -> List[Path]:
        """Obtiene documentos de un paciente específico"""
        documentos = []
        nombre_carpeta = nombre_paciente.replace(' ', '_').lower()
        paciente_path = (self.base_path / nombre_clinica / 
                        facilitador / 
                        'grupos' / grupo / 
                        'pacientes' / nombre_carpeta)

        if not paciente_path.exists():
            return []

        # Buscar en todas las carpetas de documentos
        for tipo_doc in ['FARC', 'BIO', 'MTP', 'notas_progreso']:
            doc_path = paciente_path / tipo_doc / 'output'
            if doc_path.exists():
                documentos.extend(doc_path.glob('*.*'))

        return sorted(documentos, key=lambda x: x.stat().st_mtime, reverse=True)

    def _obtener_pacientes_clinica(self, nombre_clinica: str) -> List[Dict[str, str]]:
        """Obtiene lista de pacientes de la clínica"""
        pacientes = []
        clinic_path = self.base_path / nombre_clinica
        
        # Buscar en grupos de todos los facilitadores
        for facilitador in clinic_path.glob("*"):
            if not facilitador.is_dir():
                continue
                
            grupos_path = facilitador / "grupos"
            if not grupos_path.exists():
                continue

            # Buscar en grupos mañana y tarde
            for grupo in ["manana", "tarde"]:
                grupo_path = grupos_path / grupo
                if not grupo_path.exists():
                    continue

                # Leer configuración del grupo
                config_file = grupo_path / "grupo_config.json"
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        for paciente in config.get('pacientes', []):
                            pacientes.append({
                                'nombre': paciente['nombre'],
                                'id': paciente['id'],
                                'grupo': grupo,
                                'facilitador': facilitador.name
                            })

        return pacientes

    def _obtener_documentos_paciente(self, nombre_clinica: str, grupo: str, nombre_paciente: str) -> List[Path]:
        """Obtiene documentos disponibles de un paciente"""
        documentos = []
        nombre_carpeta = nombre_paciente.replace(' ', '_').lower()
        
        # Obtener configuración de la clínica para encontrar el facilitador
        config_file = self.base_path / nombre_clinica / 'clinic_config.json'
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Buscar en cada facilitador
            for facilitador in config.get('facilitadores_psr', []):
                # Construir ruta al directorio del paciente
                paciente_path = (self.base_path / nombre_clinica / 
                               facilitador['nombre'] / 'grupos' / grupo /
                               'pacientes' / nombre_carpeta)
                
                if not paciente_path.exists():
                    continue

                # Buscar en todas las carpetas de documentos
                for tipo_doc in ['FARC', 'BIO', 'MTP', 'notas_progreso']:
                    doc_path = paciente_path / tipo_doc
                    
                    # Buscar en input y output
                    for subcarpeta in ['input', 'output']:
                        carpeta_docs = doc_path / subcarpeta
                        if carpeta_docs.exists():
                            # Buscar archivos con diferentes extensiones
                            for extension in ['*.pdf', '*.json', '*.txt', '*.docx']:
                                documentos.extend(carpeta_docs.glob(extension))

            return sorted(documentos, key=lambda x: x.stat().st_mtime, reverse=True)
            
        except Exception as e:
            print(f"\n❌ Error buscando documentos: {str(e)}")
            return []

    def _obtener_consolidaciones(self, nombre_clinica: str) -> List[Path]:
        """Obtiene lista de consolidaciones existentes"""
        consolidaciones_path = self.base_path / nombre_clinica / 'output' / 'consolidaciones'
        if not consolidaciones_path.exists():
            return []
            
        return list(consolidaciones_path.glob('*.json'))

    def _mostrar_consolidacion(self, consolidacion_path: Path):
        """Muestra el contenido de una consolidación"""
        try:
            with open(consolidacion_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("\n=== CONTENIDO DE LA CONSOLIDACIÓN ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"\n❌ Error al leer consolidación: {str(e)}")

    def _obtener_pacientes_grupo(self, nombre_clinica: str, grupo: str) -> List[Dict[str, Any]]:
        """Obtiene lista de pacientes de un grupo específico"""
        pacientes = []
        clinic_path = self.base_path / nombre_clinica
        
        # Obtener config de la clínica
        config_file = clinic_path / 'clinic_config.json'
        if not config_file.exists():
            return []

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Buscar en cada facilitador
            for facilitador in config.get('facilitadores_psr', []):
                grupo_path = clinic_path / facilitador['nombre'] / 'grupos' / grupo
                grupo_config = grupo_path / 'grupo_config.json'
                
                if grupo_config.exists():
                    with open(grupo_config, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for paciente in data.get('pacientes', []):
                            pacientes.append({
                                'nombre': paciente['nombre'],
                                'id': paciente['id'],
                                'facilitador': facilitador['nombre'],
                                'grupo': grupo
                            })

            return sorted(pacientes, key=lambda x: x['nombre'])  # Ordenar por nombre
            
        except Exception as e:
            print(f"\n❌ Error leyendo pacientes: {str(e)}")
            return []

    # Añadir el método que falta
    def _mostrar_consolidaciones(self, nombre_clinica: str) -> None:
        """Muestra la lista de consolidaciones para una clínica y permite seleccionar una para ver su contenido"""
        print("\n=== CONSOLIDACIONES DISPONIBLES ===")
        
        # Obtener la lista de consolidaciones
        consolidaciones = self._obtener_consolidaciones(nombre_clinica)
        
        if not consolidaciones:
            print("\n❌ No hay consolidaciones disponibles para esta clínica")
            return
            
        # Mostrar la lista de consolidaciones
        for idx, consolidacion in enumerate(consolidaciones, 1):
            fecha_mod = datetime.fromtimestamp(consolidacion.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            print(f"{idx}. {consolidacion.name}")
            print(f"   Fecha: {fecha_mod}")
            print(f"   Tamaño: {consolidacion.stat().st_size / 1024:.1f} KB")
        
        # Permitir selección
        while True:
            try:
                seleccion = input("\nSeleccione una consolidación para ver (0 para cancelar): ").strip()
                if seleccion == '0':
                    break
                    
                idx = int(seleccion) - 1
                if 0 <= idx < len(consolidaciones):
                    # Llamar al método existente para mostrar el contenido de la consolidación
                    self._mostrar_consolidacion(consolidaciones[idx])
                    break
                else:
                    print("❌ Selección no válida")
            except ValueError:
                print("❌ Por favor ingrese un número válido")
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    # ...existing code...
