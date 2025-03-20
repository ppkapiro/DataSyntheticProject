import pandas as pd
import numpy as np
from pathlib import Path
from faker import Faker
from datetime import datetime, timedelta
import yaml
import random
import json  # Añadimos la importación de json
from utils.file_naming import FileNamingConvention
from utils.exportador_base import ExportadorBase
from typing import Dict, List, Any, Optional, Union

class GeneradorPacientes:
    """Clase para generar datos sintéticos de pacientes"""
    
    def __init__(self):
        self.fake = Faker(['es_ES'])  # Configurado para español
        self._configurar_generadores()

    def _configurar_generadores(self):
        """Configura los generadores específicos para cada tipo de campo"""
        self.generadores = {
            'id': lambda x: random.randint(1, 99999),  # Cambiado para no depender del valor anterior
            'nombre': lambda _: self.fake.first_name(),
            'apellido': lambda _: self.fake.last_name(),
            'genero': lambda _: random.choice(['Masculino', 'Femenino']),
            'fecha_nacimiento': lambda _: self.fake.date_of_birth(minimum_age=18, maximum_age=90),
            'telefono': lambda _: self.fake.phone_number(),
            'email': lambda _: self.fake.email(),
            'direccion': lambda _: self.fake.address(),
            'pais': lambda _: 'Cuba',
            'ciudad': lambda _: 'Miami, FL',
            'estado_civil': lambda _: random.choice(['Single', 'Married', 'Divorced', 'Widowed', 'Separated', 'Cohabitating']),
            'educacion': lambda _: random.choice([
                'Ninguno', 'Asociado (Carrera técnica)', 'Doctorado', 
                'Maestría', 'Postdoctorado'
            ])
        }

    def generar_valor(self, campo, tipo, ejemplo=None, valores_unicos=None):
        """Genera un valor sintético basado en el tipo de campo y ejemplo"""
        # Si el ejemplo es nulo y el campo permite nulos, retornar nulo ocasionalmente
        if pd.isna(ejemplo) and random.random() < 0.2:  # 20% de probabilidad de nulo
            return None

        # Si tenemos valores únicos limitados, usar esos
        if valores_unicos and len(valores_unicos) <= 5:
            valor = random.choice(valores_unicos)
            return None if pd.isna(valor) else valor

        # Buscar generador específico
        campo_lower = campo.lower()
        for key, gen in self.generadores.items():
            if key in campo_lower:
                return gen(None)

        # Si no hay generador específico, usar generadores por tipo
        tipo = str(tipo).lower()
        if 'int' in tipo:
            return random.randint(1, 1000)
        elif 'float' in tipo:
            return round(random.uniform(0, 1000), 2)
        elif 'datetime' in tipo or 'date' in tipo or 'time' in tipo:
            return self.fake.date_between(start_date='-30y', end_date='today')
        elif 'bool' in tipo:
            return random.choice([True, False])
        else:
            return ejemplo if pd.notna(ejemplo) else self.fake.word()

class ExportadorBase:
    FORMATOS_SOPORTADOS = {
        'csv': ('CSV', lambda df, path: df.to_csv(path, index=False)),
        'xlsx': ('Excel (XLSX)', lambda df, path: df.to_excel(path, index=False)),
        'json': ('JSON', lambda df, path: df.to_json(path, orient='records')),
        'html': ('HTML', lambda df, path: df.to_html(path, index=False)),
        'yaml': ('YAML', lambda df, path: yaml.dump(df.to_dict('records'), open(path, 'w'))),
        'tsv': ('TSV', lambda df, path: df.to_csv(path, sep='\t', index=False)),
        'ods': ('ODS', lambda df, path: df.to_excel(path, engine='odf', index=False))
    }

    def preguntar_formato(self):
        """Solicita al usuario el formato de exportación"""
        while True:
            print("\nFormatos disponibles:")
            for idx, (key, (nombre, _)) in enumerate(self.FORMATOS_SOPORTADOS.items(), 1):
                print(f"{idx}. {nombre} (.{key})")
            
            try:
                opcion = int(input("\nSeleccione formato (número): ")) - 1
                if 0 <= opcion < len(self.FORMATOS_SOPORTADOS):
                    return list(self.FORMATOS_SOPORTADOS.keys())[opcion]
                print("Opción no válida")
            except ValueError:
                print("Por favor, ingrese un número válido")

    def exportar(self, df, clinic_initials, output_dir, modulo):
        """Exporta el DataFrame usando la convención de nombres estándar"""
        while True:
            formato = self.preguntar_formato()
            
            # Determinar si es un solo paciente o varios
            num_records = len(df)
            patient_name = None
            
            if num_records == 1:
                # Intentar obtener el nombre del paciente
                nombre_cols = [col for col in df.columns if 'nombre' in col.lower()]
                if nombre_cols:
                    patient_name = str(df[nombre_cols[0]].iloc[0])
            
            # Usar la convención estándar para nombrar el archivo
            nombre_archivo = FileNamingConvention.generate_filename(
                clinic_initials=clinic_initials,
                module=modulo,
                extension=formato,
                num_records=num_records if num_records > 1 else None,
                patient_name=patient_name
            )
            
            ruta_salida = FileNamingConvention.get_export_path(output_dir, nombre_archivo)
            
            try:
                self.FORMATOS_SOPORTADOS[formato][1](df, ruta_salida)
                print(f"Archivo exportado exitosamente: {ruta_salida}")
            except Exception as e:
                print(f"Error al exportar: {str(e)}")
            
            if input("\n¿Desea exportar en otro formato? (S/N): ").upper() != 'S':
                break

class GestorMasterData:
    """Gestiona la lectura y carga de archivos master"""
    
    @staticmethod
    def obtener_ruta_master(clinic_path):
        """Obtiene la ruta de la carpeta master de la clínica"""
        return clinic_path / "lector_archivos" / "output"

    @staticmethod
    def listar_archivos_master(clinic_path):
        """Lista los archivos master disponibles en la carpeta de la clínica"""
        master_path = GestorMasterData.obtener_ruta_master(clinic_path)
        
        if not master_path.exists():
            print(f"\nNo se encontró la carpeta master: {master_path}")
            return None
            
        # Buscar archivos master
        archivos = list(master_path.glob("*DataMasterData*"))
        
        if not archivos:
            print(f"\nNo se encontraron archivos master en: {master_path}")
            return None
        
        print(f"\n=== ARCHIVOS MASTER DISPONIBLES EN {master_path} ===")
        for idx, archivo in enumerate(archivos, 1):
            print(f"{idx}. {archivo.name}")
        
        while True:
            try:
                opcion = int(input("\nSeleccione el archivo master a utilizar (0 para cancelar): ")) - 1
                if opcion == -1:
                    return None
                if 0 <= opcion < len(archivos):
                    return archivos[opcion]
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

    @staticmethod
    def cargar_estructura_master(file_path):
        """Carga la estructura desde un archivo master"""
        extension = file_path.suffix.lower()
        try:
            if extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return pd.DataFrame(data['campos'])
            elif extension == '.csv':
                return pd.read_csv(file_path)
            elif extension in ['.xlsx', '.xls', '.ods']:
                return pd.read_excel(file_path)
            else:
                raise ValueError(f"Formato no soportado: {extension}")
        except Exception as e:
            print(f"Error al cargar archivo master: {e}")
            return None

class ExportadorPacientes(ExportadorBase):
    """
    Clase para la generación y exportación de datos de pacientes.
    Proporciona métodos para crear listados de pacientes de forma aleatoria
    o basada en plantillas.
    """
    
    def __init__(self, carpeta_base: Union[str, Path] = None):
        """
        Inicializa el exportador de pacientes
        
        Args:
            carpeta_base: Carpeta base para guardar los archivos exportados
        """
        super().__init__(carpeta_base, "Pacientes")
        
        # Cargar datos para generación aleatoria
        self.nombres_masculinos = [
            "Juan", "Carlos", "Luis", "Miguel", "José", "Pedro", "Antonio", 
            "Francisco", "Manuel", "Javier", "Ricardo", "Daniel", "Alejandro", 
            "Roberto", "Fernando", "Jorge", "David", "Eduardo", "Mario", "Rafael"
        ]
        
        self.nombres_femeninos = [
            "María", "Ana", "Laura", "Carmen", "Isabel", "Patricia", "Cristina", 
            "Elena", "Rosa", "Pilar", "Marta", "Sofía", "Julia", "Paula", 
            "Teresa", "Beatriz", "Lucía", "Diana", "Silvia", "Raquel"
        ]
        
        self.apellidos = [
            "García", "Rodríguez", "González", "López", "Martínez", "Pérez", 
            "Sánchez", "Fernández", "Gómez", "Martín", "Jiménez", "Ruiz", 
            "Hernández", "Díaz", "Moreno", "Álvarez", "Romero", "Alonso", 
            "Gutiérrez", "Navarro", "Torres", "Domínguez", "Gil", "Vázquez"
        ]
        
        # Opciones para la generación
        self.opciones = {
            "edad_min": 18,
            "edad_max": 80,
            "porcentaje_femenino": 50,
            "formatos_fecha": ["%d/%m/%Y", "%Y-%m-%d"],
            "formato_telefono": "XXX-XXX-XXXX",
        }
    
    def generar_pacientes(self, cantidad: int, opciones: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Genera una lista de pacientes con datos aleatorios
        
        Args:
            cantidad: Número de pacientes a generar
            opciones: Opciones para personalizar la generación
            
        Returns:
            List[Dict]: Lista de diccionarios con datos de pacientes
        """
        # Combinar opciones predeterminadas con las proporcionadas
        if opciones:
            opciones_finales = self.opciones.copy()
            opciones_finales.update(opciones)
        else:
            opciones_finales = self.opciones
        
        pacientes = []
        
        for _ in range(cantidad):
            # Determinar género
            if random.randint(1, 100) <= opciones_finales["porcentaje_femenino"]:
                genero = "F"
                nombre = random.choice(self.nombres_femeninos)
            else:
                genero = "M"
                nombre = random.choice(self.nombres_masculinos)
            
            # Generar apellidos (dos)
            apellido1 = random.choice(self.apellidos)
            apellido2 = random.choice(self.apellidos)
            
            # Generar fecha de nacimiento
            edad = random.randint(opciones_finales["edad_min"], opciones_finales["edad_max"])
            fecha_nacimiento = datetime.now() - timedelta(days=365.25 * edad)
            formato_fecha = random.choice(opciones_finales["formatos_fecha"])
            fecha_str = fecha_nacimiento.strftime(formato_fecha)
            
            # Generar ID único
            id_paciente = f"P{random.randint(10000, 99999)}"
            
            # Generar teléfono
            telefono = self._generar_telefono(opciones_finales["formato_telefono"])
            
            # Crear paciente
            paciente = {
                "id": id_paciente,
                "nombre": nombre,
                "apellido1": apellido1,
                "apellido2": apellido2,
                "nombre_completo": f"{nombre} {apellido1} {apellido2}",
                "genero": genero,
                "fecha_nacimiento": fecha_str,
                "edad": edad,
                "telefono": telefono,
                "activo": random.choice([True, True, True, False]),  # 75% activos
                "fecha_registro": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime(formato_fecha)
            }
            
            pacientes.append(paciente)
        
        return pacientes
    
    def _generar_telefono(self, formato: str) -> str:
        """
        Genera un número de teléfono según el formato especificado
        
        Args:
            formato: Formato del teléfono (X será reemplazado por dígitos)
            
        Returns:
            str: Número de teléfono generado
        """
        resultado = ""
        for char in formato:
            if char == 'X':
                resultado += str(random.randint(0, 9))
            else:
                resultado += char
        return resultado
    
    def validar_datos_pacientes(self, datos):
        """Valida que cada registro de paciente tenga los campos obligatorios."""
        campos_requeridos = ['nombre', 'edad', 'genero']
        for indice, registro in enumerate(datos):
            for campo in campos_requeridos:
                if campo not in registro or registro[campo] is None:
                    print(f"Registro {indice} inválido: falta {campo}")
                    return False
        return True

    def exportar_pacientes(self, datos, output_path):
        """
        Genera y exporta datos sintéticos de pacientes.
        Se valida la integridad de los datos y se maneja cualquier error durante la exportación.
        """
        try:
            # Validar datos antes de exportar
            if not self.validar_datos_pacientes(datos):
                raise ValueError("Datos de pacientes no válidos.")

            # Generar DataFrame y exportar a CSV
            import pandas as pd
            df = pd.DataFrame(datos)
            df.to_csv(output_path, index=False)
            print(f"Datos exportados correctamente a {output_path}")
        except Exception as e:
            print(f"Error al exportar pacientes: {e}")
            # Opcional: se podría relanzar la excepción si se requiere detener el flujo
            # raise

    def generar_y_exportar(self, cantidad: int, formato: str, opciones: Dict[str, Any] = None) -> Optional[Path]:
        """
        Genera y exporta una lista de pacientes en una sola operación
        
        Args:
            cantidad: Número de pacientes a generar
            formato: Formato de exportación ('csv', 'json', 'excel')
            opciones: Opciones para la generación
            
        Returns:
            Optional[Path]: Ruta al archivo generado o None si falla
        """
        pacientes = self.generar_pacientes(cantidad, opciones)
        return self.exportar_pacientes(pacientes, formato)
    
    def cargar_desde_archivo(self, ruta_archivo: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Carga una lista de pacientes desde un archivo
        
        Args:
            ruta_archivo: Ruta al archivo (CSV, JSON o Excel)
            
        Returns:
            List[Dict]: Lista de pacientes cargados
        """
        if isinstance(ruta_archivo, str):
            ruta_archivo = Path(ruta_archivo)
        
        if not ruta_archivo.exists():
            print(f"❌ Error: El archivo {ruta_archivo} no existe")
            return []
        
        extension = ruta_archivo.suffix.lower()
        
        try:
            if extension == '.csv':
                df = pd.read_csv(ruta_archivo)
                return df.to_dict('records')
            
            elif extension in ['.xlsx', '.xls']:
                df = pd.read_excel(ruta_archivo)
                return df.to_dict('records')
            
            elif extension == '.json':
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            else:
                print(f"❌ Error: Formato no soportado: {extension}")
                return []
                
        except Exception as e:
            print(f"❌ Error cargando archivo: {str(e)}")
            return []
