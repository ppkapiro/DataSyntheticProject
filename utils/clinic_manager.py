from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Any
# Agregar importación de pandas con manejo de errores
try:
    import pandas as pd
except ImportError:
    pd = None

from utils.data_formats import DataFormatHandler
from pdf_extractor.pdf_extractor import PDFExtractor  # Añadida esta importación
from utils.menu_manager import MenuManager  # Añadida esta importación
from utils.template_manager import TemplateManager  # Añadida esta importación
from utils.config_manager import ConfigManager  # Nuevo import

class ClinicManager:
    """Gestor de estructura de clínicas y facilitadores PSR"""
    
    def __init__(self, base_path=None):
        # Obtener configuración usando ConfigManager
        config = ConfigManager()
        
        # Si se proporciona una ruta, usarla; si no, usar la ruta de config
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Usar la ruta proporcionada por ConfigManager
            data_path = config.get_data_path()
            self.base_path = data_path
            
        # Verificar que la ruta exista o crearla
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
            
        try:
            # Crear directorio principal de la clínica
            clinic_path.mkdir(parents=True, exist_ok=True)
            
            # Crear configuración básica de la clínica antes de cualquier otra operación
            config = {
                'nombre_clinica': nombre_clinica,
                'facilitadores_psr': [],
                'created_at': datetime.now().isoformat()
            }
            
            config_file = clinic_path / 'clinic_config.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"\nCreada clínica '{nombre_clinica}' con configuración básica")
            
            print("\n¿Desea agregar facilitadores a la clínica? (S/N): ")
            if input().upper() != 'S':
                print("\nCreada clínica sin facilitadores.")
                print("Puede agregar facilitadores más tarde desde el menú de gestión.")
                return True
            
            # Gestionar facilitadores PSR si se desea agregarlos
            return self._gestionar_facilitadores_inicial(clinic_path, nombre_clinica)
            
        except Exception as e:
            print(f"\nError al crear clínica: {str(e)}")
            import traceback
            traceback.print_exc()  # Esto mostrará la traza completa del error
            return False

    def _gestionar_facilitadores_inicial(self, clinic_path, nombre_clinica):
        """Gestiona la creación inicial de facilitadores"""
        facilitadores = []
        while True:
            info_facilitador = self._solicitar_info_facilitador()
            if info_facilitador:
                facilitador_path = clinic_path / info_facilitador['nombre']
                
                if self._crear_estructura_facilitador(facilitador_path, info_facilitador):
                    facilitadores.append(info_facilitador)
                    print(f"\nFacilitador PSR '{info_facilitador['nombre']}' creado con éxito")
                    
                    # Importar pacientes directamente aquí
                    print(f"\nGestión de pacientes para {info_facilitador['nombre']}")
                    
                    # Grupo mañana
                    print("\nGrupo MAÑANA")
                    if input("¿Desea importar lista de pacientes? (S/N): ").upper() == 'S':
                        file_path = input("\nIngrese la ruta del archivo: ").strip()
                        if file_path:
                            self.importar_pacientes_grupo(
                                clinic_name=nombre_clinica,
                                facilitador_name=info_facilitador['nombre'],
                                grupo='manana',
                                file_path=file_path
                            )
                    
                    # Grupo tarde
                    print("\nGrupo TARDE")
                    if input("¿Desea importar lista de pacientes? (S/N): ").upper() == 'S':
                        file_path = input("\nIngrese la ruta del archivo: ").strip()
                        if file_path:
                            self.importar_pacientes_grupo(
                                clinic_name=nombre_clinica,
                                facilitador_name=info_facilitador['nombre'],
                                grupo='tarde',
                                file_path=file_path
                            )
                else:
                    print("Error al crear la estructura del facilitador")
            
            print("\n¿Desea agregar otro facilitador? (S/N): ")
            if input().upper() != 'S':
                break

        # Guardar configuración de la clínica
        config = {
            'nombre_clinica': nombre_clinica,
            'facilitadores_psr': facilitadores,
            'created_at': datetime.now().isoformat()
        }
        
        config_file = clinic_path / 'clinic_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

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
            # Crear directorio del facilitador
            facilitador_path.mkdir(parents=True)
            
            # Crear estructura de grupos (mañana y tarde)
            for turno in ['manana', 'tarde']:
                grupo_path = facilitador_path / 'grupos' / turno
                grupo_path.mkdir(parents=True)
                
                # Crear carpeta de pacientes
                pacientes_path = grupo_path / 'pacientes'
                pacientes_path.mkdir()
                
                # Crear archivo de configuración del grupo
                grupo_config = {
                    'facilitador': info_facilitador['nombre'],
                    'turno': turno,
                    'pacientes': []
                }
                
                config_file = grupo_path / 'grupo_config.json'
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(grupo_config, f, indent=2, ensure_ascii=False)
                
                print(f"\nCreado grupo de {turno} para el facilitador {info_facilitador['nombre']}")
                
                # Preguntar si desea importar pacientes para este grupo
                print(f"\n¿Desea importar pacientes para el grupo de {turno}? (S/N): ")
                if input().upper() == 'S':
                    print("\nSeleccione el archivo con la lista de pacientes (CSV, Excel):")
                    file_path = input("Ruta del archivo: ").strip()
                    
                    if file_path:
                        self.importar_pacientes_grupo(
                            clinic_name=facilitador_path.parent.name,
                            facilitador_name=info_facilitador['nombre'],
                            grupo=turno,
                            file_path=file_path
                        )
                    else:
                        print(f"No se importaron pacientes para el grupo de {turno}")
            
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
        """Muestra la estructura creada para el facilitador de forma simplificada"""
        print(f"\nEstructura creada para {facilitador_path.name}")
        print("✅ Grupos y carpetas de documentos creados correctamente")

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
            
        # Verificar que existe el archivo de configuración
        config_file = clinic_path / 'clinic_config.json'
        if not config_file.exists():
            print(f"\nError: No se encontró el archivo de configuración para '{nombre_clinica}'")
            return False
            
        # Intentar leer el archivo para verificar su integridad
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Verificar campos mínimos
            if 'nombre_clinica' not in config or 'facilitadores_psr' not in config:
                print(f"\nError: El archivo de configuración de '{nombre_clinica}' está incompleto")
                return False
                
        except json.JSONDecodeError:
            print(f"\nError: El archivo de configuración de '{nombre_clinica}' tiene un formato JSON inválido")
            return False
        except Exception as e:
            print(f"\nError al leer la configuración de '{nombre_clinica}': {str(e)}")
            return False
            
        # Crear directorio import_data si no existe
        import_data_path = clinic_path / 'import_data'
        import_data_path.mkdir(exist_ok=True)
        
        # El resto de la estructura se puede verificar si hay facilitadores
        if config.get('facilitadores_psr'):
            # Verificar que existe cada facilitador
            for facilitador in config['facilitadores_psr']:
                facilitador_path = clinic_path / facilitador['nombre']
                if not facilitador_path.exists():
                    print(f"\nAdvertencia: No se encontró el directorio para el facilitador '{facilitador['nombre']}'")
                    # No devolvemos False aquí porque queremos permitir corregir esto más tarde
        
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
        """Importa pacientes y crea sus estructuras de carpetas"""
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
            
            # Intentar diferentes nombres de columnas para el Seguro Social
            posibles_columnas_ss = ['Seguro Social', 'Social Security', 'SSN', 'Número de Seguro Social', 'Patient Social Security']
            columna_ss = None
            
            # Detectar qué columna contiene el Seguro Social
            for col in posibles_columnas_ss:
                if col in df.columns:
                    columna_ss = col
                    print(f"Detectada columna de Seguro Social: '{col}'")
                    break
            
            # Procesar cada fila
            for idx, row in df.iterrows():
                # Obtener nombre del paciente
                nombre = None
                for col in ['Nombre', 'Nombre Completo', 'Patient Name', 'Nombre Paciente', 'Name']:
                    if col in df.columns and not pd.isna(row.get(col, '')):
                        nombre = str(row.get(col, '')).strip()
                        break
                
                # Si no hay nombre en las columnas comunes, intentar con la primera columna
                if not nombre and len(df.columns) > 0:
                    nombre = str(row.get(df.columns[0], '')).strip()
                
                # Verificar que tenemos un nombre válido
                if not nombre:
                    print(f"Advertencia: Fila {idx+1} sin nombre válido, ignorando")
                    continue
                
                # Obtener seguro social (usar la columna detectada o buscar en varias columnas)
                seguro_social = ""
                if columna_ss and columna_ss in df.columns:
                    # Obtener el valor y convertirlo a string
                    valor_ss = row.get(columna_ss, "")
                    
                    # Manejar valores NaN, None o vacíos
                    if pd.isna(valor_ss) or valor_ss is None:
                        seguro_social = "NO_SS_DISPONIBLE"
                    else:
                        seguro_social = str(valor_ss).strip()
                
                # Si no se encontró el seguro social, marcarlo
                if not seguro_social:
                    seguro_social = "NO_SS_DISPONIBLE"
                
                # Información del paciente con nombre y seguro social
                paciente_info = {
                    'id': str(idx + 1),
                    'nombre': nombre,
                    'seguro_social': seguro_social
                }
                
                # Crear carpeta con nombre del paciente
                nombre_carpeta = nombre.replace(' ', '_').lower()
                paciente_path = grupo_base_path / nombre_carpeta
                
                # Crear estructura básica para el paciente
                if self._crear_estructura_paciente(paciente_path, paciente_info):
                    pacientes_procesados.append(paciente_info)
                    print(f"Creada estructura para: {nombre} (SS: {seguro_social})")

            # Actualizar archivo de configuración del grupo
            if pacientes_procesados:
                grupo_config = self.base_path / clinic_name / facilitador_name / 'grupos' / grupo / 'grupo_config.json'
                with open(grupo_config, 'r+', encoding='utf-8') as f:
                    config = json.load(f)
                    config['pacientes'] = pacientes_procesados
                    f.seek(0)
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    f.truncate()

            print(f"\nSe procesaron {len(pacientes_procesados)} pacientes")
            return True

        except Exception as e:
            print(f"Error en la importación: {str(e)}")
            import traceback
            traceback.print_exc()  # Mostrar el error detallado
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
            print(f"\nError: La estructura de la clínica '{clinic_name}' no es válida")
            return False

        print("\nAsignación de pacientes a grupos")
        
        # Cargar configuración de la clínica
        config_file = self.base_path / clinic_name / 'clinic_config.json'
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"\nError: No se encontró el archivo de configuración para la clínica '{clinic_name}'")
            input("\nPresione Enter para continuar...")
            return False
        except json.JSONDecodeError:
            print(f"\nError: El archivo de configuración de la clínica '{clinic_name}' está dañado")
            input("\nPresione Enter para continuar...")
            return False

        # Verificar si hay facilitadores
        if not config['facilitadores_psr']:
            print("\nNo hay facilitadores registrados en esta clínica.")
            print("Primero debe agregar facilitadores usando la opción 'Agregar nuevo facilitador'.")
            input("\nPresione Enter para continuar...")
            return False

        # Mostrar facilitadores disponibles
        print("\nFacilitadores disponibles:")
        for idx, facilitador in enumerate(config['facilitadores_psr'], 1):
            print(f"{idx}. {facilitador['nombre']}")

        # Seleccionar facilitador
        while True:
            try:
                opcion = input("\nSeleccione el facilitador (0 para cancelar): ").strip()
                if opcion == '0':
                    return False
                
                opcion = int(opcion) - 1
                if 0 <= opcion < len(config['facilitadores_psr']):
                    facilitador = config['facilitadores_psr'][opcion]
                    break
                print("Opción no válida. Ingrese un número entre 1 y", len(config['facilitadores_psr']))
            except ValueError:
                print("Por favor ingrese un número válido")

        # Seleccionar grupo
        print("\nGrupos disponibles:")
        print("1. Mañana")
        print("2. Tarde")
        print("0. Cancelar")
        
        while True:
            try:
                opcion = input("\nSeleccione el grupo (0 para cancelar): ").strip()
                if opcion == '0':
                    return False
                if opcion == '1':
                    grupo = 'manana'
                    break
                if opcion == '2':
                    grupo = 'tarde'
                    break
                print("Opción no válida. Ingrese 1 para Mañana, 2 para Tarde, o 0 para Cancelar")
            except ValueError:
                print("Por favor ingrese un número válido")

        # Solicitar ruta del archivo
        print("\nSeleccione el archivo con la lista de pacientes")
        print("El archivo debe ser CSV o Excel con al menos una columna 'Nombre'")
        file_path = input("Ingrese la ruta del archivo (0 para cancelar): ").strip()
        
        if file_path == '0':
            return False
            
        if not file_path:
            print("No se proporcionó una ruta de archivo")
            input("\nPresione Enter para continuar...")
            return False
            
        # Comprobar si el archivo existe
        if not Path(file_path).exists():
            print(f"\nError: El archivo '{file_path}' no existe")
            input("\nPresione Enter para continuar...")
            return False

        # Importar pacientes
        resultado = self.importar_pacientes_grupo(
            clinic_name=clinic_name,
            facilitador_name=facilitador['nombre'],
            grupo=grupo,
            file_path=file_path
        )
        
        if resultado:
            print(f"\n✅ Pacientes asignados exitosamente al facilitador {facilitador['nombre']} en el grupo de {grupo}")
        else:
            print(f"\n❌ Error al asignar pacientes al facilitador {facilitador['nombre']}")
        
        input("\nPresione Enter para continuar...")
        return resultado

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
            opcion = MenuManager.mostrar_menu_extr

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
            info_facilitador = self._solicitar_info_facilitador()
            if not info_facilitador:
                return False
            
            # Verificar que no existe
            facilitador_path = clinic_path / info_facilitador['nombre']
            if facilitador_path.exists():
                print(f"\nError: Ya existe un facilitador con el nombre '{info_facilitador['nombre']}'")
                return False
            
            # Crear estructura del facilitador
            if self._crear_estructura_facilitador(facilitador_path, info_facilitador):
                # Actualizar configuración de la clínica
                config['facilitadores_psr'].append(info_facilitador)
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Facilitador '{info_facilitador['nombre']}' agregado exitosamente")
                return True
            else:
                print(f"\nError: No se pudo crear la estructura del facilitador")
                return False
                
        except Exception as e:
            print(f"\nError al agregar facilitador: {str(e)}")
            import traceback
            traceback.print_exc()  # Esto mostrará la traza completa del error
            return False

    def eliminar_facilitador(self, clinic_name):
        """Elimina un facilitador existente y todos sus datos"""
        try:
            # Verificar que la clínica existe
            clinic_path = self.base_path / clinic_name
            if not clinic_path.exists():
                print(f"\nError: La clínica '{clinic_name}' no existe")
                return False
            
            # Leer configuración de la clínica
            config_file = clinic_path / 'clinic_config.json'
            if not config_file.exists():
                print(f"\nError: No se encontró el archivo de configuración para '{clinic_name}'")
                return False
                
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verificar si hay facilitadores
            if not config.get('facilitadores_psr', []):
                print("\nNo hay facilitadores registrados en esta clínica")
                return False
            
            # Mostrar lista de facilitadores
            print("\nFacilitadores disponibles:")
            for idx, facilitador in enumerate(config['facilitadores_psr'], 1):
                print(f"{idx}. {facilitador['nombre']}")
            
            # Solicitar selección
            try:
                idx = int(input("\nSeleccione el número del facilitador a eliminar (0 para cancelar): ")) - 1
                if idx == -1:  # Cancelar
                    return False
                    
                if not (0 <= idx < len(config['facilitadores_psr'])):
                    print("Selección no válida")
                    return False
                    
                facilitador = config['facilitadores_psr'][idx]
                nombre_facilitador = facilitador['nombre']
                
                # Confirmar eliminación
                print(f"\n⚠️ ADVERTENCIA: Está a punto de eliminar al facilitador '{nombre_facilitador}'")
                print("Esta acción eliminará TODOS los datos asociados y NO puede deshacerse")
                confirmacion = input(f"\n¿Está seguro? (escriba 'ELIMINAR' para confirmar): ")
                
                if confirmacion != "ELIMINAR":
                    print("\nOperación cancelada")
                    return False
                
                # Eliminar directorio
                import shutil
                facilitador_path = clinic_path / nombre_facilitador
                if facilitador_path.exists():
                    shutil.rmtree(facilitador_path)
                
                # Actualizar configuración
                config['facilitadores_psr'].pop(idx)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Facilitador '{nombre_facilitador}' eliminado exitosamente")
                return True
                
            except ValueError:
                print("Por favor ingrese un número válido")
                return False
                
        except Exception as e:
            print(f"\nError al eliminar facilitador: {str(e)}")
            return False

    def actualizar_facilitador(self, clinic_name):
        """Actualiza información de un facilitador existente"""
        try:
            # Verificar que la clínica existe
            clinic_path = self.base_path / clinic_name
            if not clinic_path.exists():
                print(f"\nError: La clínica '{clinic_name}' no existe")
                return False
            
            # Leer configuración de la clínica
            config_file = clinic_path / 'clinic_config.json'
            if not config_file.exists():
                print(f"\nError: No se encontró el archivo de configuración para '{clinic_name}'")
                return False
                
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verificar si hay facilitadores
            if not config.get('facilitadores_psr', []):
                print("\nNo hay facilitadores registrados en esta clínica")
                return False
            
            # Mostrar lista de facilitadores
            print("\nFacilitadores disponibles:")
            for idx, facilitador in enumerate(config['facilitadores_psr'], 1):
                print(f"{idx}. {facilitador['nombre']}")
            
            # Solicitar selección
            try:
                idx = int(input("\nSeleccione el número del facilitador a actualizar (0 para cancelar): ")) - 1
                if idx == -1:  # Cancelar
                    return False
                    
                if not (0 <= idx < len(config['facilitadores_psr'])):
                    print("Selección no válida")
                    return False
                    
                facilitador = config['facilitadores_psr'][idx]
                
                # Mostrar información actual
                print("\nInformación actual:")
                for key, value in facilitador.items():
                    print(f"{key}: {value}")
                
                # Solicitar nuevos valores
                print("\nIntroduzca los nuevos valores (deje vacío para mantener el valor actual):")
                nuevo_nombre = input(f"Nombre [{facilitador['nombre']}]: ").strip()
                
                if nuevo_nombre and nuevo_nombre != facilitador['nombre']:
                    # Verificar que no exista otro facilitador con ese nombre
                    if (clinic_path / nuevo_nombre).exists():
                        print(f"\nError: Ya existe un facilitador con el nombre '{nuevo_nombre}'")
                        return False
                    
                    # Renombrar directorio
                    old_path = clinic_path / facilitador['nombre']
                    new_path = clinic_path / nuevo_nombre
                    if old_path.exists():
                        old_path.rename(new_path)
                    
                    # Actualizar nombre en grupos
                    for turno in ['manana', 'tarde']:
                        grupo_config = new_path / 'grupos' / turno / 'grupo_config.json'
                        if grupo_config.exists():
                            with open(grupo_config, 'r', encoding='utf-8') as f:
                                grupo_data = json.load(f)
                            
                            grupo_data['facilitador'] = nuevo_nombre
                            
                            with open(grupo_config, 'w', encoding='utf-8') as f:
                                json.dump(grupo_data, f, indent=2, ensure_ascii=False)
                    
                    # Actualizar configuración
                    facilitador['nombre'] = nuevo_nombre
                
                # Actualizar fecha
                facilitador['ultima_actualizacion'] = datetime.now().isoformat()
                
                # Guardar cambios
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Facilitador actualizado correctamente")
                return True
                
            except ValueError:
                print("Por favor ingrese un número válido")
                return False
                
        except Exception as e:
            print(f"\nError al actualizar facilitador: {str(e)}")
            return False

    # Método auxiliar para obtener la lista de facilitadores de una clínica
    def _obtener_facilitadores_clinica(self, clinic_name):
        """Obtiene la lista de facilitadores de una clínica"""
        try:
            config_file = self.base_path / clinic_name / 'clinic_config.json'
            if not config_file.exists():
                return []
                
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            return config.get('facilitadores_psr', [])
        except Exception:
            return []
