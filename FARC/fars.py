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
from typing import Any, Dict, Union

class GeneradorFARC:
    """Clase para generar datos sintéticos de evaluaciones FARC"""
    
    def __init__(self):
        self.fake = Faker(['es_ES'])
        self._configurar_generadores()

    def _configurar_generadores(self):
        """Configura los generadores específicos para campos FARC"""
        self.generadores = {
            'id_paciente': lambda _: random.randint(1, 99999),
            'fecha_evaluacion': lambda _: self.fake.date_between(start_date='-1y', end_date='today'),
            'sustancia': lambda _: random.choice([
                'Alcohol', 'Cannabis', 'Cocaína', 'Heroína', 
                'Metanfetamina', 'Benzodiacepinas'
            ]),
            'frecuencia_uso': lambda _: random.choice([
                'Diario', 'Semanal', 'Mensual', 'Ocasional', 'En remisión'
            ]),
            'nivel_riesgo': lambda _: random.choice([
                'Bajo', 'Moderado', 'Alto', 'Severo'
            ]),
            'tratamiento': lambda _: random.choice([
                'Ambulatorio', 'Hospitalización', 'Grupo de apoyo',
                'Terapia individual', 'Programa residencial'
            ]),
            'estado': lambda _: random.choice([
                'Activo', 'En progreso', 'Completado', 'Abandonado'
            ])
        }

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
            return ejemplo if pd.notna(ejemplo) else self.fake.word()

from utils.exportador_base import ExportadorBase
import pandas as pd
import json

class ExportadorFARC(ExportadorBase):
    """
    Clase para la generación y exportación de evaluaciones FARC (Evaluación de Alcohol y Drogas).
    Proporciona métodos para crear registros de evaluaciones para pacientes.
    """
    
    def __init__(self, carpeta_base: Union[str, Path] = None):
        """
        Inicializa el exportador de evaluaciones FARC
        
        Args:
            carpeta_base: Carpeta base para guardar los archivos exportados
        """
        super().__init__(carpeta_base, "FARC")
        
        # Datos para la generación
        self.niveles_alcohol = [0, 1, 2, 3, 4, 5]
        self.niveles_drogas = [0, 1, 2, 3, 4, 5]
        
        self.recomendaciones_alcohol = {
            0: "No se requiere intervención para alcohol.",
            1: "Educación preventiva sobre consumo de alcohol.",
            2: "Intervención breve para consumo de alcohol.",
            3: "Programa de prevención de recaídas de alcohol.",
            4: "Tratamiento intensivo para dependencia alcohólica.",
            5: "Tratamiento especializado con supervisión médica para alcoholismo."
        }
        
        self.recomendaciones_drogas = {
            0: "No se requiere intervención para drogas.",
            1: "Educación preventiva sobre consumo de sustancias.",
            2: "Intervención breve para consumo de sustancias.",
            3: "Programa de prevención de recaídas de drogas.",
            4: "Tratamiento intensivo para dependencia de sustancias.",
            5: "Tratamiento especializado con supervisión médica para adicción a drogas."
        }
        
        self.niveles_tratamiento = ["Ambulatorio", "Hospitalización Parcial", "Residencial"]
        
        # Opciones para la generación
        self.opciones = {
            "formato_fecha": "%d/%m/%Y",
            "dias_seguimiento": 90,
            "frecuencia_seguimiento": "mensual"
        }
    
    def generar_evaluacion(self, paciente_id: str, datos_paciente: Dict[str, Any] = None, 
                            fecha_evaluacion: str = None, opciones: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genera una evaluación FARC para un paciente
        
        Args:
            paciente_id: ID del paciente
            datos_paciente: Datos adicionales del paciente (opcional)
            fecha_evaluacion: Fecha de la evaluación (opcional)
            opciones: Opciones para personalizar la generación
            
        Returns:
            Dict: Datos de la evaluación generada
        """
        # Configurar opciones
        if opciones:
            opciones_finales = self.opciones.copy()
            opciones_finales.update(opciones)
        else:
            opciones_finales = self.opciones
            
        # Establecer fecha de evaluación
        if not fecha_evaluacion:
            fecha_evaluacion = datetime.now().strftime(opciones_finales["formato_fecha"])
            
        # Generar niveles aleatorios
        nivel_alcohol = random.choice(self.niveles_alcohol)
        nivel_drogas = random.choice(self.niveles_drogas)
        
        # Determinar nivel global (el más alto)
        nivel_global = max(nivel_alcohol, nivel_drogas)
        
        # Determinar recomendaciones
        recomendacion_alcohol = self.recomendaciones_alcohol[nivel_alcohol]
        recomendacion_drogas = self.recomendaciones_drogas[nivel_drogas]
        
        # Determinar plan
        if nivel_global <= 1:
            nivel_tratamiento = None
            duracion_tratamiento = None
        elif nivel_global <= 3:
            nivel_tratamiento = self.niveles_tratamiento[0]  # Ambulatorio
            duracion_tratamiento = f"{random.randint(1, 3)} meses"
        elif nivel_global == 4:
            nivel_tratamiento = self.niveles_tratamiento[1]  # Hospitalización Parcial
            duracion_tratamiento = f"{random.randint(2, 8)} semanas"
        else:
            nivel_tratamiento = self.niveles_tratamiento[2]  # Residencial
            duracion_tratamiento = f"{random.randint(1, 6)} meses"
            
        # Generar fecha de seguimiento
        fecha_eval_dt = datetime.strptime(fecha_evaluacion, opciones_finales["formato_fecha"])
        
        if opciones_finales["frecuencia_seguimiento"] == "mensual":
            dias_hasta_seguimiento = 30
        elif opciones_finales["frecuencia_seguimiento"] == "trimestral":
            dias_hasta_seguimiento = 90
        else:
            dias_hasta_seguimiento = opciones_finales["dias_seguimiento"]
            
        fecha_seguimiento = (fecha_eval_dt + timedelta(days=dias_hasta_seguimiento)).strftime(opciones_finales["formato_fecha"])
        
        # Crear evaluación
        evaluacion = {
            "id": f"FARC_{paciente_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "paciente_id": paciente_id,
            "fecha_evaluacion": fecha_evaluacion,
            "evaluador": f"PSR{random.randint(1000, 9999)}",
            "evaluacion_alcohol": {
                "nivel": nivel_alcohol,
                "descripcion": self._describir_nivel_alcohol(nivel_alcohol),
                "recomendacion": recomendacion_alcohol
            },
            "evaluacion_drogas": {
                "nivel": nivel_drogas,
                "descripcion": self._describir_nivel_drogas(nivel_drogas),
                "recomendacion": recomendacion_drogas
            },
            "nivel_global": nivel_global,
            "plan_tratamiento": {
                "nivel": nivel_tratamiento,
                "duracion": duracion_tratamiento
            },
            "seguimiento": {
                "fecha": fecha_seguimiento,
                "tipo": opciones_finales["frecuencia_seguimiento"]
            },
            "notas_adicionales": self._generar_notas(nivel_alcohol, nivel_drogas)
        }
        
        # Agregar datos del paciente si se proporcionan
        if datos_paciente:
            evaluacion["datos_paciente"] = datos_paciente
            
        return evaluacion
    
    def _describir_nivel_alcohol(self, nivel: int) -> str:
        """
        Genera una descripción para un nivel de alcohol
        
        Args:
            nivel: Nivel de consumo de alcohol (0-5)
            
        Returns:
            str: Descripción del nivel
        """
        descripciones = {
            0: "Sin consumo de alcohol.",
            1: "Consumo de bajo riesgo, social u ocasional.",
            2: "Consumo regular con riesgo leve.",
            3: "Consumo problemático con posible abuso.",
            4: "Dependencia alcohólica moderada.",
            5: "Dependencia alcohólica severa que requiere intervención inmediata."
        }
        return descripciones.get(nivel, "Nivel no válido")
    
    def _describir_nivel_drogas(self, nivel: int) -> str:
        """
        Genera una descripción para un nivel de drogas
        
        Args:
            nivel: Nivel de consumo de drogas (0-5)
            
        Returns:
            str: Descripción del nivel
        """
        descripciones = {
            0: "Sin consumo de drogas.",
            1: "Consumo experimental u ocasional de bajo riesgo.",
            2: "Consumo regular con riesgo leve.",
            3: "Consumo problemático con posible abuso.",
            4: "Dependencia de sustancias moderada.",
            5: "Dependencia severa de sustancias que requiere intervención inmediata."
        }
        return descripciones.get(nivel, "Nivel no válido")
    
    def _generar_notas(self, nivel_alcohol: int, nivel_drogas: int) -> str:
        """
        Genera notas adicionales según los niveles de alcohol y drogas
        
        Args:
            nivel_alcohol: Nivel de alcohol (0-5)
            nivel_drogas: Nivel de drogas (0-5)
            
        Returns:
            str: Notas generadas
        """
        notas = f"Notas adicionales sobre el nivel de alcohol ({nivel_alcohol}) y drogas ({nivel_drogas})."
        return notas

    def validar_datos_fars(self, datos):
        """Valida que cada registro tenga los campos obligatorios para evaluaciones."""
        campos_requeridos = ['evaluacion_alcohol', 'evaluacion_drogas']
        for indice, registro in enumerate(datos):
            for campo in campos_requeridos:
                if campo not in registro or registro[campo] is None:
                    print(f"Registro {indice} inválido: falta {campo}")
                    return False
        return True

    def exportar_fars(self, datos, output_path):
        """
        Genera y exporta evaluaciones de alcohol y drogas.
        Se valida la integridad de los datos y se maneja cualquier error durante la exportación.
        """
        try:
            # Validar datos antes de exportar
            if not self.validar_datos_fars(datos):
                raise ValueError("Datos de evaluaciones no válidos.")
            df = pd.DataFrame(datos)
            df.to_csv(output_path, index=False)
            print(f"Evaluaciones exportadas correctamente a {output_path}")
        except Exception as e:
            print(f"Error al exportar evaluaciones FARC: {e}")
            # Opcional: relanzar la excepción si se requiere detener el flujo
            # raise
