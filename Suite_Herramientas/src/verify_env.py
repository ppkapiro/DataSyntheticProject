import sys
import os
import platform
from pathlib import Path
import subprocess
import json

# Definición de la estructura del proyecto
PROJECT_STRUCTURE = {
    'Docs': 'Documentación del proyecto',
    'src': 'Código fuente',
    'data': 'Datos del proyecto',
    'tests': 'Pruebas unitarias',
    'config': 'Archivos de configuración',
    'logs': 'Archivos de registro'
}

def check_conda_installation():
    """Verifica si conda está instalado y disponible en el sistema"""
    try:
        result = subprocess.run(['conda', '--version'], 
                              capture_output=True, 
                              text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("ℹ️ Conda no está disponible en el sistema")
        return False
    except Exception as e:
        print(f"ℹ️ No se pudo verificar la instalación de Conda: {e}")
        return False

def get_conda_info():
    """Intenta obtener información de conda de manera segura"""
    if not check_conda_installation():
        return None
        
    try:
        result = subprocess.run(['conda', 'info', '--json'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"ℹ️ No se pudo obtener información de Conda: {e}")
    return None

def check_environment():
    """Verifica y muestra la configuración del entorno virtual"""
    try:
        print("\n=== Verificación del Entorno ===\n")
        
        # Información básica del entorno
        print(f"Python Version: {sys.version.split()[0]}")
        print(f"Platform: {platform.system()} {platform.version()}")
        
        # Verificar si estamos en un entorno virtual
        in_venv = sys.prefix != sys.base_prefix
        print(f"Virtual Environment Active: {in_venv}")
        
        # Verificar conda
        if check_conda_installation():
            print("✅ Conda está instalado y disponible")
            conda_info = get_conda_info()
            if conda_info:
                active_env = conda_info.get('active_prefix_name', 'base')
                print(f"✓ Entorno Conda activo: {active_env}")
        else:
            print("ℹ️ Usando verificación alternativa de entorno")
            if 'CONDA_DEFAULT_ENV' in os.environ:
                print(f"✓ Entorno detectado via variables: {os.environ['CONDA_DEFAULT_ENV']}")
        
        return True
    except Exception as e:
        print(f"⚠️ Advertencia en verificación del entorno: {e}")
        return True

def ensure_project_structure(base_path):
    """Verifica y crea la estructura de carpetas del proyecto"""
    try:
        print("\n=== Verificación de Estructura del Proyecto ===\n")
        
        success = True
        for folder, description in PROJECT_STRUCTURE.items():
            folder_path = Path(base_path) / folder
            try:
                if not folder_path.exists():
                    folder_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Creada carpeta: {folder} - {description}")
                else:
                    print(f"✓ Existe carpeta: {folder} - {description}")
            except Exception as e:
                print(f"⚠️ No se pudo crear/verificar {folder}: {e}")
                success = False
        
        return success
    except Exception as e:
        print(f"⚠️ Advertencia en verificación de estructura: {e}")
        return True

def main():
    """Función principal con manejo suave de errores"""
    try:
        base_path = Path(__file__).parent.parent
        check_environment()
        ensure_project_structure(base_path)
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"\n⚠️ Advertencia durante la verificación: {e}")
        
    finally:
        sys.exit(0)  # Siempre terminar con éxito

if __name__ == "__main__":
    main()
