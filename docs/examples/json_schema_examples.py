"""
Ejemplos de esquemas JSON y su uso con el método leer_json()

Este archivo contiene ejemplos de esquemas JSON y cómo utilizarlos
para validar archivos JSON al cargarlos con LectorArchivos.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from lector_archivos.lector import LectorArchivos

# Ejemplo 1: Esquema para datos de pacientes
ESQUEMA_PACIENTES = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "nombre", "edad"],
        "properties": {
            "id": {"type": "string", "pattern": "^PAC[0-9]{6}$"},
            "nombre": {"type": "string", "minLength": 2},
            "apellido": {"type": "string", "minLength": 2},
            "edad": {"type": "integer", "minimum": 0, "maximum": 120},
            "genero": {"type": "string", "enum": ["M", "F", "Otro"]},
            "fechaNacimiento": {"type": "string", "format": "date"},
            "contacto": {
                "type": "object",
                "properties": {
                    "telefono": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "direccion": {"type": "string"}
                }
            },
            "historial": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fecha": {"type": "string", "format": "date"},
                        "diagnostico": {"type": "string"},
                        "tratamiento": {"type": "string"}
                    }
                }
            }
        }
    }
}

# Ejemplo 2: Esquema para datos de análisis clínicos
ESQUEMA_ANALISIS = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["muestra_id", "paciente_id", "fecha", "resultados"],
        "properties": {
            "muestra_id": {"type": "string"},
            "paciente_id": {"type": "string"},
            "fecha": {"type": "string", "format": "date-time"},
            "tipo_analisis": {"type": "string"},
            "resultados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["parametro", "valor", "unidad"],
                    "properties": {
                        "parametro": {"type": "string"},
                        "valor": {"type": ["number", "string"]},
                        "unidad": {"type": "string"},
                        "rango_referencia": {
                            "type": "object",
                            "properties": {
                                "min": {"type": "number"},
                                "max": {"type": "number"}
                            }
                        }
                    }
                }
            }
        }
    }
}

# Ejemplo 3: Esquema para datos de medicamentos
ESQUEMA_MEDICAMENTOS = {
    "type": "object",
    "properties": {
        "medicamentos": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "nombre", "principio_activo"],
                "properties": {
                    "id": {"type": "string"},
                    "nombre": {"type": "string"},
                    "principio_activo": {"type": "string"},
                    "dosis": {"type": "string"},
                    "forma": {"type": "string"},
                    "contraindicaciones": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    },
    "required": ["medicamentos"]
}

def ejemplo_validacion_basica():
    """Ejemplo básico de validación de un archivo JSON"""
    lector = LectorArchivos()
    
    try:
        # Cargar un archivo JSON con validación de esquema
        ruta_archivo = "./data/pacientes.json"
        df = lector.leer_json(
            ruta_archivo=ruta_archivo,
            schema=ESQUEMA_PACIENTES,
            orient="records"
        )
        print(f"Validación exitosa. Se cargaron {len(df)} registros.")
        print(df.head())
        return True
    except Exception as e:
        print(f"Error en la validación: {str(e)}")
        return False

def ejemplo_cargar_esquema_desde_archivo():
    """Ejemplo de carga de esquema desde un archivo"""
    lector = LectorArchivos()
    
    try:
        # Cargar el esquema desde un archivo
        ruta_esquema = "./schemas/analisis_schema.json"
        schema = lector.cargar_esquema_json(ruta_esquema=ruta_esquema)
        
        # Usar el esquema para validar
        df = lector.leer_json(
            ruta_archivo="./data/analisis.json",
            schema=schema,
            orient="records"
        )
        print(f"Validación con esquema desde archivo exitosa. {len(df)} registros.")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def ejemplo_validacion_jsonlines():
    """Ejemplo de validación de un archivo JSON Lines"""
    lector = LectorArchivos()
    
    try:
        # Validar un archivo de formato JSON Lines
        df = lector.leer_json(
            ruta_archivo="./data/medicamentos.jsonl",
            schema=ESQUEMA_MEDICAMENTOS["properties"]["medicamentos"],
            lines=True,
            orient="records"
        )
        print(f"Validación de JSON Lines exitosa. {len(df)} registros.")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def ejemplo_normalizacion_json():
    """Ejemplo de normalización de datos JSON anidados"""
    lector = LectorArchivos()
    
    try:
        # Cargar y normalizar datos anidados
        df = lector.leer_json(
            ruta_archivo="./data/pacientes_complejos.json",
            schema=ESQUEMA_PACIENTES,
            normalize=True  # Activar la normalización
        )
        print("Datos normalizados:")
        print(df.columns.tolist())  # Mostrar columnas resultantes
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n1. Validación básica de JSON")
    ejemplo_validacion_basica()
    
    print("\n2. Carga de esquema desde archivo")
    ejemplo_cargar_esquema_desde_archivo()
    
    print("\n3. Validación de JSON Lines")
    ejemplo_validacion_jsonlines()
    
    print("\n4. Normalización de datos JSON anidados")
    ejemplo_normalizacion_json()
