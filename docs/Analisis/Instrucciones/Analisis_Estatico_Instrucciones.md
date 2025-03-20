# Instrucciones para el Análisis Estático de Código - Notefy IA

## Comandos Esenciales

### Instalación de Herramientas
```bash
pip install pydeps pylint jedi radon snakeviz networkx matplotlib seaborn
```

### Generación de Diagramas de Dependencias
```bash
# Diagrama básico
pydeps c:/Users/pepec/Documents/Notefy\ IA/main.py --output dependencias.svg

# Diagrama con opciones avanzadas
pydeps c:/Users/pepec/Documents/Notefy\ IA/main.py --max-bacon=5 --cluster --show-deps --rankdir=LR --exclude "numpy|pandas" --output diagrama_completo.svg

# Diagrama UML con Pyreverse
pyreverse -o svg -p NotefyIA c:/Users/pepec/Documents/Notefy\ IA/
```

### Análisis de Código Duplicado
```bash
# Usando Pylint
pylint --disable=all --enable=similarities c:/Users/pepec/Documents/Notefy\ IA/

# Análisis de complejidad
radon cc -a c:/Users/pepec/Documents/Notefy\ IA/
radon mi c:/Users/pepec/Documents/Notefy\ IA/
```

### Análisis de Importaciones
```bash
# Ejecutar script de análisis (guardar como import_analyzer.py)
python import_analyzer.py c:/Users/pepec/Documents/Notefy\ IA/
```

### Perfil de Ejecución
```bash
python -m cProfile -o programa.prof c:/Users/pepec/Documents/Notefy\ IA/main.py
snakeviz programa.prof
```

## Lista de Verificación para el Análisis

1. **Dependencias**
   - Generar diagrama completo de dependencias
   - Identificar ciclos de dependencia
   - Crear matriz de acoplamiento
   - Documentar módulos centrales

2. **Código Duplicado**
   - Identificar funciones/clases redundantes
   - Categorizar redundancias (A-D)
   - Listar oportunidades de refactorización
   - Priorizar consolidaciones

3. **Patrones y Convenciones**
   - Documentar patrones recurrentes
   - Evaluar consistencia de implementaciones
   - Identificar desviaciones del patrón
   - Recomendar estándares

4. **Entregables Finales**
   - Matriz de dependencias
   - Catálogo de redundancias
   - Informe de problemas arquitectónicos
   - Recomendaciones priorizadas

## Scripts Listos para Usar

### Analizador de Importaciones
```python
# import_analyzer.py
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
            
            return {
                "file": file_path,
                "imports": imports
            }
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
    
    with open("project_imports.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Análisis completado. Resultados guardados en project_imports.json")
```

### Generador de Matriz de Dependencias
```python
# dependency_matrix.py
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

def generate_dependency_matrix(import_data):
    # Extraer todos los archivos Python
    all_files = [item["file"] for item in import_data if "error" not in item]
    file_to_idx = {file: idx for idx, file in enumerate(all_files)}
    
    # Crear matriz vacía
    n = len(all_files)
    matrix = np.zeros((n, n))
    
    # Llenar matriz con dependencias
    for item in import_data:
        if "error" in item:
            continue
            
        source_file = item["file"]
        if source_file not in file_to_idx:
            continue
            
        source_idx = file_to_idx[source_file]
        
        for imp in item["imports"]:
            if imp["type"] == "from":
                # Convertir el módulo importado a una ruta de archivo
                module_parts = imp["module"].split('.')
                for i in range(len(module_parts), 0, -1):
                    potential_module = '.'.join(module_parts[:i])
                    for target_file in all_files:
                        if potential_module in target_file:
                            target_idx = file_to_idx[target_file]
                            matrix[source_idx, target_idx] = 1
                            break
    
    return matrix, all_files

def plot_dependency_matrix(matrix, files):
    # Simplificar nombres de archivo para visualización
    short_names = [os.path.basename(f) for f in files]
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(matrix, xticklabels=short_names, yticklabels=short_names, 
                cmap='Blues', cbar_kws={'label': 'Dependencia'})
    plt.title('Matriz de Dependencias')
    plt.tight_layout()
    plt.savefig('dependency_matrix.png', dpi=300)
    plt.close()
    
    # Calcular métricas
    ca = np.sum(matrix, axis=0)  # Acoplamiento aferente (columnas)
    ce = np.sum(matrix, axis=1)  # Acoplamiento eferente (filas)
    instability = ce / (ca + ce + 0.000001)  # Evitar división por cero
    
    # Guardar métricas en un archivo
    with open('dependency_metrics.txt', 'w') as f:
        f.write("Archivo,Ca,Ce,Inestabilidad\n")
        for i, file in enumerate(files):
            f.write(f"{os.path.basename(file)},{ca[i]},{ce[i]},{instability[i]:.2f}\n")
    
    return ca, ce, instability

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dependency_matrix.py <project_imports.json>")
        sys.exit(1)
    
    import_file = sys.argv[1]
    with open(import_file, 'r') as f:
        import_data = json.load(f)
    
    matrix, files = generate_dependency_matrix(import_data)
    ca, ce, instability = plot_dependency_matrix(matrix, files)
    
    print("Matriz de dependencias generada en dependency_matrix.png")
    print("Métricas guardadas en dependency_metrics.txt")
```

## Formatos para Documentación de Resultados

### Informe de Dependencias
```
# Informe de Análisis Estático: Notefy IA

## Métricas Globales
- Número total de módulos: XX
- Densidad de dependencias: XX%
- Módulos críticos:
  1. [módulo1.py] - Ca: XX, Ce: XX
  2. [módulo2.py] - Ca: XX, Ce: XX

## Problemas Identificados
1. [Problema] - Impacto: [Alto/Medio/Bajo]
2. [Problema] - Impacto: [Alto/Medio/Bajo]

## Recomendaciones Prioritarias
1. [Recomendación] - Esfuerzo: [XX] - Beneficio: [XX]
2. [Recomendación] - Esfuerzo: [XX] - Beneficio: [XX]
```

---

Las herramientas y scripts proporcionados en este documento son suficientes para realizar un análisis estático completo del código fuente de Notefy IA. Ejecute los comandos en secuencia y consolide los resultados según los formatos provistos.
