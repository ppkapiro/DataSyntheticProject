"""Script para ejecutar el programa desde la raíz del proyecto"""
import sys
from pathlib import Path

# Asegurar que los módulos del proyecto estén en el PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar el menú unificado en lugar del antiguo
from unified_main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
