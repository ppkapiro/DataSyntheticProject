import pandas as pd
import numpy as np
from pathlib import Path
from faker import Faker
from datetime import datetime, timedelta
import yaml
import random
import json
from utils.file_naming import FileNamingConvention
from pacientes.pacientes import ExportadorBase, GestorMasterData  # Añadida importación de GestorMasterData

class GeneradorMTP:
    """Clase para generar datos sintéticos de planes de entrenamiento"""
    
    def __init__(self):
        self.fake = Faker(['es_ES'])
        self._configurar_generadores()

    def _configurar_generadores(self):
        """Configura los generadores específicos para campos MTP"""
        self.generadores = {
            'id_plan': lambda _: random.randint(1, 99999),
            'id_paciente': lambda _: random.randint(1, 99999),
            'fecha_inicio': lambda _: self.fake.date_between(start_date='-6m', end_date='today'),
            'fecha_revision': lambda _: self.fake.date_between(start_date='today', end_date='+6m'),
            'estado_plan': lambda _: random.choice([
                'Activo', 'Completado', 'En revisión', 'Suspendido', 'Pendiente'
            ]),
            'tipo_intervencion': lambda _: random.choice([
                'Individual', 'Grupal', 'Familiar', 'Mixta'
            ]),
            'frecuencia_sesiones': lambda _: random.choice([
                'Semanal', 'Quincenal', 'Mensual', 'Bisemanal'
            ]),
            'nivel_prioridad': lambda _: random.choice([
                'Alta', 'Media', 'Baja'
            ]),
            'objetivos': lambda _: self.generar_detalle_mtp('objetivos'),
            'actividades': lambda _: self.generar_detalle_mtp('actividades'),
            'progreso': lambda _: random.randint(0, 100),
            'notas_seguimiento': lambda _: self.generar_detalle_mtp('notas')
        }

    def generar_detalle_mtp(self, tipo_campo):
        """Genera texto detallado para campos del plan"""
        detalles = {
            'objetivos': [
                "Reducir niveles de ansiedad mediante técnicas de relajación",
                "Desarrollar habilidades sociales y comunicativas",
                "Establecer rutinas diarias saludables",
                "Mejorar adherencia al tratamiento farmacológico"
            ],
            'actividades': [
                "Terapia cognitivo-conductual semanal",
                "Ejercicios de mindfulness diarios",
                "Participación en grupo de apoyo",
                "Seguimiento médico mensual"
            ],
            'notas': [
                "Muestra buena disposición y participación activa",
                "Progreso consistente en objetivos establecidos",
                "Necesita refuerzo en algunas áreas",
                "Familia colaboradora con el tratamiento"
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
            return self.fake.date_between(start_date='-6m', end_date='+6m')
        elif 'bool' in tipo:
            return random.choice([True, False])
        else:
            return ejemplo if pd.notna(ejemplo) else self.fake.text(max_nb_chars=100)

class ExportadorMTP(ExportadorBase):
    def __init__(self):
        super().__init__()
        self.generador = GeneradorMTP()
        self.gestor_master = GestorMasterData()  # Añadimos el gestor de archivos master

    def solicitar_cantidad_registros(self):
        """Solicita al usuario la cantidad de registros a generar"""
        while True:
            try:
                cantidad = int(input("\nIngrese la cantidad de planes MTP a generar: "))
                if cantidad > 0:
                    return cantidad
                print("La cantidad debe ser mayor que 0")
            except ValueError:
                print("Por favor ingrese un número válido")

    def generar_datos_sinteticos(self, estructura, cantidad):
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

    def exportar_mtp(self, df_estructura, clinic_initials, output_dir, cantidad=None):
        """Genera y exporta datos sintéticos de planes MTP"""
        print("\nMódulo MTP - Generación de Datos Sintéticos")

        # Si no se proporciona estructura, buscar archivo master en la clínica
        if df_estructura is None:
            clinic_path = Path(output_dir).parent.parent
            archivo_master = self.gestor_master.listar_archivos_master(clinic_path)
            
            if (archivo_master):
                df_estructura = self.gestor_master.cargar_estructura_master(archivo_master)
                print("\nEstructura master cargada exitosamente")
                print(f"Usando archivo: {archivo_master.name}")
            else:
                print("\nNo se encontró un archivo master. Por favor, procese primero un archivo en el módulo lector.")
                return None

        # Solicitar cantidad de registros si no se especificó
        if cantidad is None:
            cantidad = self.solicitar_cantidad_registros()

        # Generar datos sintéticos
        df = self.generar_datos_sinteticos(df_estructura, cantidad)
        
        print("\nVista previa de datos generados:")
        print(df.head())
        print(f"\nTotal de registros generados: {len(df)}")
        
        # Exportar datos
        self.exportar(df, clinic_initials, output_dir, "mtp")
        return df
