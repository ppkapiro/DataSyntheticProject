import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

def generate_dependency_matrix(import_data):
    all_files = [item["file"] for item in import_data if "error" not in item]
    file_to_idx = {file: idx for idx, file in enumerate(all_files)}
    n = len(all_files)
    matrix = np.zeros((n, n))
    for item in import_data:
        if "error" in item:
            continue
        source_file = item["file"]
        if source_file not in file_to_idx:
            continue
        source_idx = file_to_idx[source_file]
        for imp in item["imports"]:
            if imp["type"] == "from":
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
    short_names = [os.path.basename(f) for f in files]
    plt.figure(figsize=(12, 10))
    sns.heatmap(matrix, xticklabels=short_names, yticklabels=short_names, cmap='Blues', cbar_kws={'label': 'Dependencia'})
    plt.title('Matriz de Dependencias')
    plt.tight_layout()
    
    # Definir la ruta de destino para los archivos de resultados
    output_dir = r"C:\Users\pepec\Documents\Notefy IA\Data synthetic\Analisis_Detallado\Reportes"
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar la imagen en la ubicación especificada
    plt.savefig(os.path.join(output_dir, 'dependency_matrix.png'), dpi=300)
    plt.close()

    ca = np.sum(matrix, axis=0)
    ce = np.sum(matrix, axis=1)
    instability = ce / (ca + ce + 1e-6)

    # Guardar las métricas en la ubicación especificada
    metrics_file = os.path.join(output_dir, 'dependency_metrics.txt')
    with open(metrics_file, 'w', encoding='utf-8') as f:
        f.write("Archivo,Ca,Ce,Inestabilidad\n")
        for i, file in enumerate(files):
            f.write(f"{os.path.basename(file)},{ca[i]},{ce[i]},{instability[i]:.2f}\n")
    
    return ca, ce, instability

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dependency_matrix.py <ruta_project_imports.json>")
        sys.exit(1)
    
    import_file = sys.argv[1]
    with open(import_file, 'r', encoding='utf-8') as f:
        import_data = json.load(f)
        
    matrix, files = generate_dependency_matrix(import_data)
    ca, ce, instability = plot_dependency_matrix(matrix, files)
    
    output_dir = r"C:\Users\pepec\Documents\Notefy IA\Data synthetic\Analisis_Detallado\Reportes"
    print(f"Matriz de dependencias generada en {os.path.join(output_dir, 'dependency_matrix.png')}")
    print(f"Métricas guardadas en {os.path.join(output_dir, 'dependency_metrics.txt')}")
