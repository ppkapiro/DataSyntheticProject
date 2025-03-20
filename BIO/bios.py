import pandas as pd
import numpy as np
from pathlib import Path
from faker import Faker
from datetime import datetime, timedelta
import yaml
import random
import json
from utils.file_naming import FileNamingConvention
from pacientes.pacientes import ExportadorBase

class GeneradorBIO:
    """Clase para generar datos sintéticos de biografías"""
    
    def __init__(self):
        self.fake = Faker(['es_ES'])
        self._configurar_generadores()

    def _configurar_generadores(self):
        """Configura los generadores específicos para campos BIO"""
        self.generadores = {
            'id_paciente': lambda _: random.randint(1, 99999),
            'fecha_biografia': lambda _: self.fake.date_between(start_date='-1y', end_date='today'),
            'antecedentes_familiares': lambda _: self.generar_detalle_bio('antecedentes'),
            'historial_medico': lambda _: self.generar_detalle_bio('historial'),
            'situacion_actual': lambda _: random.choice([
                'Estable', 'En tratamiento', 'Mejoría significativa',
                'Seguimiento periódico', 'Necesita atención'
            ]),
            'nivel_funcionalidad': lambda _: random.choice([
                'Alto', 'Medio-alto', 'Medio', 'Medio-bajo', 'Bajo'
            ]),
            'apoyo_familiar': lambda _: random.choice([
                'Fuerte', 'Moderado', 'Limitado', 'Sin apoyo'
            ]),
            'objetivos_terapeuticos': lambda _: self.generar_detalle_bio('objetivos')
        }

    def generar_detalle_bio(self, tipo_campo, use_api=False):
        """
        Genera texto detallado para campos biográficos
        En el futuro, si use_api es True, llamará a una API externa
        """
        if use_api:
            return f"[Placeholder para API] Texto generado para {tipo_campo}"
        
        detalles = {
            'antecedentes': [
                "Sin antecedentes relevantes de enfermedades mentales en la familia.",
                "Padre diagnosticado con depresión, en tratamiento desde hace 5 años.",
                "Historial familiar de ansiedad en línea materna.",
                "Hermano mayor con trastorno bipolar controlado."
            ],
            'historial': [
                "Inicio de síntomas en adolescencia, primer tratamiento en 2019.",
                "Múltiples episodios de ansiedad tratados con terapia cognitiva.",
                "Tratamiento farmacológico previo con buenos resultados.",
                "Sin hospitalizaciones previas, seguimiento ambulatorio."
            ],
            'objetivos': [
                "Desarrollar habilidades de manejo del estrés y ansiedad.",
                "Mejorar relaciones interpersonales y comunicación familiar.",
                "Establecer rutina diaria saludable y hábitos positivos.",
                "Fortalecer estrategias de afrontamiento."
            ]
        }
        
        return random.choice(detalles.get(tipo_campo, ["No especificado"]))

    def generar_valor(self, campo, tipo, ejemplo=None, valores_unicos=None):
        """Genera un valor sintético basado en el tipo de campo y ejemplo"""
        # Si tenemos valores únicos limitados, usar esos
        if valores_unicos and len(valores_unicos) <= 5:
            return random.choice(valores_unicos)

        # Buscar generador específico
        campo_lower = campo.lower()
        for key, gen in self.generadores.items():
            if key in campo_lower:
                return gen(None)

        # Si no hay generador específico, usar generadores por tipo
        tipo = str(tipo).lower()
        if 'int' in tipo:
            return random.randint(1, 100)
        elif 'float' in tipo:
            return round(random.uniform(0, 10), 2)  # Escalas típicas de 0-10
        elif 'datetime' in tipo or 'date' in tipo:
            return self.fake.date_between(start_date='-1y', end_date='today')
        elif 'bool' in tipo:
            return random.choice([True, False])
        else:
            return ejemplo if pd.notna(ejemplo) else self.fake.text(max_nb_chars=100)

from utils.exportador_base import ExportadorBase
import pandas as pd
import json

class ExportadorBIO(ExportadorBase):
    """
    Clase para la generación y exportación de historias biográficas.
    """
    
    def __init__(self, carpeta_base=None):
        super().__init__(carpeta_base, "BIO")
        self.generador = GeneradorBIO()

    def solicitar_cantidad_registros(self):
        """Solicita al usuario la cantidad de registros a generar"""
        while True:
            try:
                cantidad = int(input("\nIngrese la cantidad de biografías a generar: "))
                if cantidad > 0:
                    return cantidad
                print("La cantidad debe ser mayor que 0")
            except ValueError:
                print("Por favor ingrese un número válido")

    def generar_datos_sinteticos(self, estructura, cantidad, use_api=False):
        """Genera datos sintéticos basados en la estructura proporcionada"""
        datos = {}
        
        for idx, row in estructura.iterrows():
            campo = row['Campo'] if 'Campo' in row else row['nombre']
            tipo = row['Tipo'] if 'Tipo' in row else row['tipo']
            ejemplo = row.get('Ejemplo', None)
            valores_unicos = row.get('Valores_Posibles', None)
            
            # Convertir string de valores posibles a lista si es necesario
            if isinstance(valores_unicos, str):
                try:
                    valores_unicos = eval(valores_unicos)
                except:
                    valores_unicos = None
            
            # Generar valores manteniendo los tipos de datos
            valores = []
            for _ in range(cantidad):
                valor = self.generador.generar_valor(campo, tipo, ejemplo, valores_unicos)
                valores.append(valor)
            
            datos[campo] = valores
        
        # Crear DataFrame y convertir tipos según la estructura original
        df = pd.DataFrame(datos)
        for idx, row in estructura.iterrows():
            campo = row['Campo'] if 'Campo' in row else row['nombre']
            tipo = row['Tipo'] if 'Tipo' in row else row['tipo']
            try:
                df[campo] = df[campo].astype(tipo)
            except:
                print(f"Advertencia: No se pudo convertir la columna {campo} al tipo {tipo}")
        
        return df

    def validar_datos_bios(self, datos):
        """Valida que cada registro de historia biográfica contenga los campos obligatorios."""
        campos_requeridos = ['nombre', 'historia']
        for indice, registro in enumerate(datos):
            for campo in campos_requeridos:
                if campo not in registro or registro[campo] is None:
                    print(f"Registro {indice} inválido: falta {campo}")
                    return False
        return True

    def exportar_bios(self, datos, output_path):
        """
        Genera y exporta historias biográficas.
        Se valida la integridad de los datos y se maneja cualquier error durante la exportación.
        """
        try:
            # Validar datos antes de exportar
            if not self.validar_datos_bios(datos):
                raise ValueError("Datos de historias biográficas no válidos.")
            df = pd.DataFrame(datos)
            df.to_csv(output_path, index=False)
            print(f"Historias biográficas exportadas correctamente a {output_path}")
        except Exception as e:
            print(f"Error al exportar historias biográficas: {e}")
            # Opcional: se podría relanzar la excepción
            # raise

    def exportar_bios(self, df_estructura, clinic_initials, output_dir, cantidad=None, use_api=False):
        """Genera y exporta datos sintéticos de biografías"""
        print("\nMódulo BIO - Generación de Datos Sintéticos")

        # Si no se proporciona estructura, usar estructura por defecto
        if df_estructura is None:
            df_estructura = pd.DataFrame({
                'Campo': [
                    'id_paciente', 'fecha_biografia', 'antecedentes_familiares',
                    'historial_medico', 'situacion_actual', 'nivel_funcionalidad',
                    'apoyo_familiar', 'objetivos_terapeuticos'
                ],
                'Tipo': ['int64', 'datetime64[ns]'] + ['object'] * 6
            })
            print("\nUsando estructura por defecto para BIO")

        # Solicitar cantidad de registros si no se especificó
        if cantidad is None:
            cantidad = self.solicitar_cantidad_registros()

        # Generar datos sintéticos
        df = self.generar_datos_sinteticos(df_estructura, cantidad, use_api)
        
        print("\nVista previa de datos generados:")
        print(df.head())
        print(f"\nTotal de registros generados: {len(df)}")
        
        # Exportar datos
        self.exportar(df, clinic_initials, output_dir, "bios")
        return df
