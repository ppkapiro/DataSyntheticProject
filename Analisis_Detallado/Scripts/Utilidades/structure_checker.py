import os
from pathlib import Path
import json

def check_structure():
    base_path = Path(__file__).parent
    structure = {
        "root": str(base_path),
        "directories": {},
        "files": []
    }
    
    for root, dirs, files in os.walk(base_path):
        rel_path = os.path.relpath(root, base_path)
        if rel_path == ".":
            structure["files"] = [f for f in files if f.endswith('.py')]
        else:
            structure["directories"][rel_path] = {
                "files": [f for f in files if f.endswith('.py')],
                "subdirs": dirs
            }
    
    # Guardar resultado
    output_path = base_path.parent / "Reportes" / "estructura_scripts.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    return structure

def suggest_reorganization(structure):
    """Sugiere una reorganización de la estructura"""
    suggested = {
        "Analizadores": {
            "description": "Scripts para análisis de datos y código",
            "modules": ["analysis_manager.py", "cross_references.py", "dependency_analyzer.py"]
        },
        "Utilidades": {
            "description": "Herramientas y utilidades generales",
            "modules": ["dependency_matrix.py", "file_helpers.py", "logger.py"]
        },
        "Importadores": {
            "description": "Scripts para importación y procesamiento de datos",
            "modules": ["import_analyzer.py", "data_importer.py"]
        },
        "Localizadores": {
            "description": "Scripts para localización y mapeo de código",
            "modules": ["code_locator.py", "module_mapper.py"]
        },
        "core": {
            "description": "Funcionalidad central y clases base",
            "modules": ["analysis_base.py", "config_manager.py"]
        }
    }
    
    return suggested

if __name__ == "__main__":
    current_structure = check_structure()
    suggested = suggest_reorganization(current_structure)
    
    print("\nEstructura actual:")
    print(json.dumps(current_structure, indent=2))
    
    print("\nEstructura sugerida:")
    print(json.dumps(suggested, indent=2))
