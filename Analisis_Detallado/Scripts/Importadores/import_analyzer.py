import ast
import os
import json
import sys

def extract_imports(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        try:
            tree = ast.parse(file.read())
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append({"type": "import", "name": name.name, "alias": name.asname})
                elif isinstance(node, ast.ImportFrom):
                    module = node.module if node.module else ""
                    for name in node.names:
                        imports.append({
                            "type": "from",
                            "module": module,
                            "name": name.name,
                            "alias": name.asname
                        })
            return {"file": file_path, "imports": imports}
        except SyntaxError:
            return {"file": file_path, "error": "Syntax error", "imports": []}

def analyze_project_imports(project_dir):
    results = []
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                results.append(extract_imports(file_path))
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python import_analyzer.py <ruta_proyecto>")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    results = analyze_project_imports(project_dir)
    
    # Definir la ruta de destino para el archivo de resultados
    output_dir = r"C:\Users\pepec\Documents\Notefy IA\Data synthetic\Analisis_Detallado\Reportes"
    
    # Asegurar que el directorio existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Crear la ruta completa del archivo
    output_file = os.path.join(output_dir, "project_imports.json")
    
    # Guardar el archivo en la ubicación especificada
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"Análisis completado. Resultados guardados en {output_file}")
