import shutil
from pathlib import Path
import json
from structure_checker import check_structure, suggest_reorganization

def reorganize_scripts():
    base_path = Path(__file__).parent
    
    # Crear directorios sugeridos
    suggested = suggest_reorganization(check_structure())
    
    for dir_name in suggested.keys():
        dir_path = base_path / dir_name
        dir_path.mkdir(exist_ok=True)
        
        # Crear __init__.py en cada directorio
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
    
    print("Estructura de directorios creada correctamente")
    print("\nPor favor, mueve manualmente los archivos .py a sus carpetas correspondientes")
    print("\nReorganización sugerida:")
    for dir_name, info in suggested.items():
        print(f"\n{dir_name}/")
        print(f"  Descripción: {info['description']}")
        print("  Archivos sugeridos:")
        for module in info['modules']:
            print(f"    - {module}")

if __name__ == "__main__":
    reorganize_scripts()
