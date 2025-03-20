"""
Ejemplo de uso de la validación de esquemas JSON en LectorArchivos.

Este script muestra cómo utilizar la funcionalidad de validación de esquemas 
JSON implementada en la clase LectorArchivos.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json

# Agregar el directorio raíz al path para poder importar módulos
sys.path.append(str(Path(__file__).parent.parent))

# Importar la clase LectorArchivos
from lector_archivos.lector import LectorArchivos

# Definir un esquema de ejemplo
ESQUEMA_PACIENTES = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "nombre", "edad"],
        "properties": {
            "id": {"type": "string"},
            "nombre": {"type": "string"},
            "apellido": {"type": "string"},
            "edad": {"type": "integer", "minimum": 0},
            "genero": {"type": "string", "enum": ["M", "F", "Otro"]},
            "contacto": {
                "type": "object",
                "properties": {
                    "telefono": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                }
            }
        }
    }
}

# Crear datos de ejemplo válidos
datos_validos = [
    {
        "id": "PAC001",
        "nombre": "Juan",
        "apellido": "Pérez",
        "edad": 35,
        "genero": "M",
        "contacto": {
            "telefono": "555-1234",
            "email": "juan@example.com"
        }
    },
    {
        "id": "PAC002",
        "nombre": "María",
        "apellido": "García",
        "edad": 42,
        "genero": "F",
        "contacto": {
            "telefono": "555-5678",
            "email": "maria@example.com"
        }
    }
]

# Crear datos de ejemplo inválidos
datos_invalidos = [
    {
        "id": "PAC003",
        "nombre": "Carlos",
        # Falta el campo apellido (no requerido)
        "edad": "treinta",  # Tipo incorrecto, debería ser integer
        "genero": "X",      # Valor no permitido en enum
        "contacto": {
            "telefono": "555-9876",
            "email": "correo-invalido"  # Email con formato inválido
        }
    }
]

def main():
    # Crear instancia de LectorArchivos
    lector = LectorArchivos()
    
    # Crear archivos de ejemplo temporales
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Guardar datos válidos en un archivo
    archivo_valido = temp_dir / "pacientes_validos.json"
    with open(archivo_valido, "w") as f:
        json.dump(datos_validos, f, indent=2)
    
    # Guardar datos inválidos en un archivo
    archivo_invalido = temp_dir / "pacientes_invalidos.json"
    with open(archivo_invalido, "w") as f:
        json.dump(datos_invalidos, f, indent=2)
    
    print("=== Ejemplo 1: Validación Exitosa ===")
    try:
        # Leer el archivo con validación de esquema
        df_valido = lector.leer_json(
            ruta_archivo=archivo_valido,
            schema=ESQUEMA_PACIENTES
        )
        print("✅ Validación exitosa")
        print(df_valido)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n=== Ejemplo 2: Validación Fallida ===")
    try:
        # Leer el archivo con validación de esquema
        df_invalido = lector.leer_json(
            ruta_archivo=archivo_invalido,
            schema=ESQUEMA_PACIENTES
        )
        print("Esto no debería ejecutarse si la validación falla")
    except Exception as e:
        print(f"✅ Error de validación detectado: {str(e)}")
    
    print("\n=== Ejemplo 3: Validación No Estricta ===")
    try:
        # Leer el archivo con validación de esquema en modo no estricto
        df_invalido = lector.leer_json(
            ruta_archivo=archivo_invalido,
            schema=ESQUEMA_PACIENTES,
            validate_options={'strict': False}
        )
        print("✅ Archivo cargado a pesar de no cumplir el esquema")
        print(df_invalido)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n=== Ejemplo 4: Validación de Datos en Memoria ===")
    # Validar datos directamente (sin leer de archivo)
    try:
        es_valido = lector.validar_datos_json(
            datos=datos_validos, 
            schema=ESQUEMA_PACIENTES
        )
        print(f"✅ Datos válidos: {es_valido}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    try:
        es_valido = lector.validar_datos_json(
            datos=datos_invalidos, 
            schema=ESQUEMA_PACIENTES, 
            options={'strict': False}
        )
        print(f"✅ Datos inválidos (modo no estricto): {es_valido}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Limpiar archivos temporales
    archivo_valido.unlink()
    archivo_invalido.unlink()

if __name__ == "__main__":
    main()
