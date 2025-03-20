#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analizador de referencias cruzadas para Notefy IA.

Este script analiza las referencias entre clases, funciones y métodos
a través del código fuente, identificando patrones de uso y dependencias
que no son evidentes a través del análisis de importaciones.
"""

import jedi
import os
import json
import sys
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from collections import defaultdict
import argparse

class CrossReferenceAnalyzer:
    def __init__(self, project_path, localization_report=None):
        """
        Inicializa el analizador con la ruta al proyecto.
        
        Args:
            project_path (str): Ruta al directorio raíz del proyecto
            localization_report (str, optional): Ruta al informe de localización de código
        """
        self.project_path = Path(project_path)
        self.symbol_definitions = {}  # {symbol_name: {file, line, column}}
        self.symbol_references = {}   # {symbol_name: [{file, line, column}]}
        self.module_references = defaultdict(lambda: defaultdict(int))  # {module1: {module2: count}}
        self.call_graph = nx.DiGraph()
        self.excluded_dirs = ['env', 'venv', '__pycache__', '.git', '.idea', '.vscode']
        self.focus_files = []  # Lista de archivos para enfocar el análisis
        
        # Cargar informe de localización si se proporciona
        if localization_report:
            self.load_localization_report(localization_report)

    def load_localization_report(self, report_path):
        """
        Carga el informe de localización de código para enfocar el análisis.
        
        Args:
            report_path (str): Ruta al archivo JSON con el informe de localización
        """
        try:
            print(f"Cargando informe de localización desde: {report_path}")
            with open(report_path, 'r', encoding='utf-8') as f:
                localization_data = json.load(f)
            
            # Obtener la lista de archivos de aplicación (no herramientas/scripts)
            self.focus_files = localization_data.get('potential_app_modules', [])
            
            if self.focus_files:
                print(f"Se encontraron {len(self.focus_files)} archivos de aplicación para análisis prioritario")
                print(f"Ejemplos: {', '.join(self.focus_files[:3])}")
            else:
                print("No se encontraron archivos de aplicación en el informe de localización")
                
            # Obtener información de clases/funciones si está disponible
            self.predefined_classes = localization_data.get('class_definitions', {})
            self.predefined_functions = localization_data.get('function_definitions', {})
            
            # Obtener información de estructura de módulos
            self.module_structure = localization_data.get('module_structure', {})
            
            # Definir módulos principales y centrales
            self.main_candidates = localization_data.get('main_candidates', [])
            self.core_modules = localization_data.get('core_modules', [])
            
        except Exception as e:
            print(f"Error al cargar informe de localización: {e}")
            self.focus_files = []

    def find_all_definitions(self):
        """
        Encuentra todas las definiciones de clases y funciones en el proyecto.
        """
        print("Buscando todas las definiciones en el proyecto...")
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                    script = jedi.Script(source, path=str(py_file))
                    
                    # Buscar todas las definiciones en el archivo
                    for name in script.get_names(all_scopes=True):
                        if name.type in ('function', 'class'):
                            qualified_name = f"{py_file.stem}:{name.name}"
                            self.symbol_definitions[qualified_name] = {
                                'file': str(py_file),
                                'line': name.line,
                                'column': name.column,
                                'type': name.type,
                                'module': py_file.stem
                            }
            except Exception as e:
                print(f"Error al analizar {py_file}: {e}")
        
        print(f"Se encontraron {len(self.symbol_definitions)} definiciones en el proyecto")
        return self.symbol_definitions

    def find_references_for_all_symbols(self):
        """
        Encuentra todas las referencias para cada símbolo definido.
        """
        print("Buscando referencias para todos los símbolos...")
        
        # Primero aseguramos que tenemos las definiciones
        if not self.symbol_definitions:
            self.find_all_definitions()
        
        # Contadores para estadísticas
        symbols_with_refs = 0
        symbols_without_refs = 0
        
        total_symbols = len(self.symbol_definitions)
        for i, (symbol_name, definition) in enumerate(self.symbol_definitions.items(), 1):
            if i % 10 == 0:
                print(f"Progreso: {i}/{total_symbols} símbolos analizados")
            
            try:
                file_path = definition['file']
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                    script = jedi.Script(source, path=file_path)
                    
                    # Obtener la línea y columna de la definición
                    line, column = definition['line'], definition['column']
                    
                    # Buscar el objeto en esa posición
                    definitions = script.infer(line=line, column=column)
                    if definitions:
                        # Verificar si el objeto tiene el método get_references antes de llamarlo
                        if hasattr(definitions[0], 'get_references'):
                            refs = definitions[0].get_references()
                            self.symbol_references[symbol_name] = []
                            
                            for ref in refs:
                                ref_data = {
                                    'file': ref.module_path,
                                    'line': ref.line,
                                    'column': ref.column,
                                    'module': Path(ref.module_path).stem if ref.module_path else 'unknown'
                                }
                                self.symbol_references[symbol_name].append(ref_data)
                                
                                # Actualizar grafo de llamadas
                                from_module = Path(file_path).stem
                                to_module = ref_data['module']
                                
                                if from_module != to_module:
                                    self.module_references[from_module][to_module] += 1
                                    
                                    # Añadir al grafo de llamadas
                                    if not self.call_graph.has_edge(from_module, to_module):
                                        self.call_graph.add_edge(from_module, to_module, weight=0)
                                    self.call_graph[from_module][to_module]['weight'] += 1
                            symbols_with_refs += 1
                        else:
                            # Si no tiene get_references, registrar esta información sin interrumpir el análisis
                            print(f"Info: No se pueden obtener referencias para {symbol_name} - objeto no soporta get_references()")
                            self.symbol_references[symbol_name] = []
                            symbols_without_refs += 1
            
            except Exception as e:
                # Capturar cualquier excepción pero continuar con el análisis
                print(f"Error al analizar referencias para {symbol_name}: {e}")
                self.symbol_references[symbol_name] = []
                symbols_without_refs += 1
        
        print(f"Análisis completado: {symbols_with_refs} símbolos con referencias, {symbols_without_refs} símbolos sin referencias")
        return self.symbol_references
    
    def calculate_metrics(self):
        """
        Calcula métricas de acoplamiento para cada módulo.
        
        Returns:
            dict: Diccionario con métricas por módulo
        """
        metrics = {}
        
        for module in set(list(self.module_references.keys()) + 
                          [m for refs in self.module_references.values() for m in refs.keys()]):
            # Acoplamiento aferente - cuántos módulos dependen de este
            ca = sum(1 for refs in self.module_references.values() if module in refs)
            
            # Acoplamiento eferente - de cuántos módulos depende este
            ce = len(self.module_references.get(module, {}))
            
            # Inestabilidad
            instability = ce / (ce + ca) if (ce + ca) > 0 else 0
            
            metrics[module] = {
                'acoplamiento_aferente': ca,
                'acoplamiento_eferente': ce,
                'inestabilidad': instability,
                'total_referencias': ca + ce
            }
        
        return metrics
    
    def generate_reference_heatmap(self, output_path=None):
        """
        Genera un mapa de calor de las referencias entre módulos.
        
        Args:
            output_path (str, optional): Ruta para guardar el mapa de calor
        """
        # Convertir el diccionario anidado a una matriz
        modules = sorted(set(list(self.module_references.keys()) + 
                             [m for refs in self.module_references.values() for m in refs.keys()]))
        
        # Verificar si hay módulos para visualizar
        if not modules:
            print("No hay suficientes datos para generar el mapa de calor.")
            return
        
        matrix = []
        for mod_from in modules:
            row = []
            for mod_to in modules:
                row.append(self.module_references.get(mod_from, {}).get(mod_to, 0))
            matrix.append(row)
        
        # Crear DataFrame de pandas para el mapa de calor
        df = pd.DataFrame(matrix, index=modules, columns=modules)
        
        # Crear visualización
        plt.figure(figsize=(12, 10))
        sns.heatmap(df, annot=True, cmap="YlGnBu", fmt="d", linewidths=.5)
        plt.title("Referencias cruzadas entre módulos")
        plt.ylabel("Desde Módulo")
        plt.xlabel("Hacia Módulo")
        
        # Guardar o mostrar
        if output_path:
            plt.savefig(output_path)
            print(f"Mapa de calor guardado en: {output_path}")
        else:
            plt.show()
    
    def generate_call_graph(self, output_path=None):
        """
        Genera un gráfico de llamadas entre módulos.
        
        Args:
            output_path (str, optional): Ruta para guardar el gráfico
        """
        plt.figure(figsize=(12, 10))
        
        # Calcular posiciones de nodos usando layout spring
        pos = nx.spring_layout(self.call_graph)
        
        # Obtener pesos de aristas para determinar grosor
        edge_weights = [self.call_graph[u][v]['weight'] for u, v in self.call_graph.edges()]
        
        # Normalizar pesos para visualización
        max_weight = max(edge_weights) if edge_weights else 1
        normalized_weights = [1 + (w * 5 / max_weight) for w in edge_weights]
        
        # Dibujar nodos
        nx.draw_networkx_nodes(self.call_graph, pos, node_size=700, node_color="lightblue")
        
        # Dibujar aristas con grosor según peso
        nx.draw_networkx_edges(self.call_graph, pos, width=normalized_weights, 
                              edge_color="gray", arrows=True, arrowsize=20)
        
        # Dibujar etiquetas
        nx.draw_networkx_labels(self.call_graph, pos, font_size=10)
        
        plt.title("Gráfico de Llamadas Entre Módulos")
        plt.axis("off")
        
        # Guardar o mostrar
        if output_path:
            plt.savefig(output_path)
            print(f"Gráfico de llamadas guardado en: {output_path}")
        else:
            plt.show()
    
    def export_results(self, output_dir):
        """
        Exporta todos los resultados del análisis a archivos JSON.
        
        Args:
            output_dir (str): Directorio para guardar los resultados
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Exportar definiciones
        with open(output_path / "symbol_definitions.json", "w", encoding="utf-8") as f:
            json.dump(self.symbol_definitions, f, indent=2)
        
        # Exportar referencias
        with open(output_path / "symbol_references.json", "w", encoding="utf-8") as f:
            json.dump(self.symbol_references, f, indent=2)
        
        # Exportar métricas
        metrics = self.calculate_metrics()
        with open(output_path / "module_metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        
        # Exportar referencias entre módulos
        module_refs_list = []
        for mod_from, refs in self.module_references.items():
            for mod_to, count in refs.items():
                module_refs_list.append({
                    "from_module": mod_from,
                    "to_module": mod_to,
                    "references": count
                })
        
        with open(output_path / "module_references.json", "w", encoding="utf-8") as f:
            json.dump(module_refs_list, f, indent=2)
        
        print(f"Resultados exportados a: {output_dir}")
        
        # Generar visualizaciones
        self.generate_reference_heatmap(str(output_path / "reference_heatmap.png"))
        self.generate_call_graph(str(output_path / "call_graph.png"))
    
    def generate_report(self, output_path):
        """
        Genera un informe detallado de las referencias cruzadas en formato Markdown.
        
        Args:
            output_path (str): Ruta para guardar el informe
        """
        metrics = self.calculate_metrics()
        
        # Ordenar módulos por total de referencias (descendente)
        sorted_modules = sorted(metrics.items(), key=lambda x: x[1]['total_referencias'], reverse=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Informe de Análisis de Referencias Cruzadas\n\n")
            
            # Si se cargó un informe de localización, incluir información adicional
            if hasattr(self, 'main_candidates') and self.main_candidates:
                f.write("## Contexto del Análisis\n\n")
                f.write("Este análisis se ha enfocado en los componentes principales de la aplicación, ")
                f.write("identificados previamente mediante análisis de localización de código.\n\n")
                
                f.write("### Puntos de Entrada Identificados\n\n")
                for candidate in self.main_candidates[:5]:
                    f.write(f"- `{candidate}`\n")
                    
                f.write("\n### Módulos Centrales Identificados\n\n")
                for module in self.core_modules[:5]:
                    f.write(f"- `{module}`\n")
                
                f.write("\n")
            
            # Continuar con el reporte normal
            f.write("## Resumen Global\n\n")
            f.write(f"- Total de símbolos analizados: {len(self.symbol_definitions)}\n")
            f.write(f"- Total de módulos identificados: {len(metrics)}\n")
            f.write(f"- Total de relaciones entre módulos: {sum(len(refs) for refs in self.module_references.values())}\n\n")
            
            f.write("## Módulos con Mayor Acoplamiento\n\n")
            f.write("| Módulo | Acoplamiento Aferente (Ca) | Acoplamiento Eferente (Ce) | Inestabilidad | Total Referencias |\n")
            f.write("|--------|---------------------------|-----------------------------|--------------|------------------|\n")
            
            for module, metric in sorted_modules[:10]:  # Top 10
                f.write(f"| {module} | {metric['acoplamiento_aferente']} | {metric['acoplamiento_eferente']} | ")
                f.write(f"{metric['inestabilidad']:.2f} | {metric['total_referencias']} |\n")
            
            f.write("\n## Patrones de Referencias Identificados\n\n")
            
            # Identificar ciclos en el grafo
            try:
                cycles = list(nx.simple_cycles(self.call_graph))
                if cycles:
                    f.write("### Ciclos de Dependencia Detectados\n\n")
                    for i, cycle in enumerate(cycles, 1):
                        cycle_str = " → ".join(cycle) + " → " + cycle[0]
                        f.write(f"{i}. {cycle_str}\n")
                    f.write("\n")
                else:
                    f.write("### No se detectaron ciclos de dependencia\n\n")
            except:
                f.write("### Error al analizar ciclos de dependencia\n\n")
            
            # Identificar componentes altamente acoplados
            f.write("### Componentes Altamente Acoplados\n\n")
            f.write("Módulos con alto acoplamiento aferente (muchos módulos dependen de ellos):\n\n")
            
            high_ca = sorted(metrics.items(), key=lambda x: x[1]['acoplamiento_aferente'], reverse=True)[:5]
            for module, metric in high_ca:
                f.write(f"- **{module}**: {metric['acoplamiento_aferente']} módulos dependen de este\n")
            
            f.write("\nMódulos con alto acoplamiento eferente (dependen de muchos módulos):\n\n")
            high_ce = sorted(metrics.items(), key=lambda x: x[1]['acoplamiento_eferente'], reverse=True)[:5]
            for module, metric in high_ce:
                f.write(f"- **{module}**: Depende de {metric['acoplamiento_eferente']} módulos\n")
            
            f.write("\n## Recomendaciones\n\n")
            
            # Generar recomendaciones basadas en el análisis
            f.write("1. **Reestructuración de módulos altamente inestables**:\n")
            high_instability = sorted(metrics.items(), key=lambda x: x[1]['inestabilidad'], reverse=True)[:3]
            for module, metric in high_instability:
                if metric['inestabilidad'] > 0.7 and metric['total_referencias'] > 5:
                    f.write(f"   - Revisar el módulo `{module}` que tiene una inestabilidad de {metric['inestabilidad']:.2f}\n")
            
            f.write("\n2. **Romper ciclos de dependencia**:\n")
            if cycles:
                for i, cycle in enumerate(cycles[:3], 1):
                    f.write(f"   - Revisar el ciclo: {' → '.join(cycle)}\n")
            else:
                f.write("   - No se encontraron ciclos que romper\n")
            
            f.write("\n3. **Revisar módulos centrales**:\n")
            for module, metric in high_ca[:3]:
                f.write(f"   - El módulo `{module}` es utilizado por {metric['acoplamiento_aferente']} otros módulos y ")
                f.write(f"debería tener una API estable y bien documentada\n")
            
            f.write("\n## Visualizaciones\n\n")
            f.write("- [Mapa de calor de referencias](reference_heatmap.png)\n")
            f.write("- [Gráfico de llamadas](call_graph.png)\n")

    def _get_python_files(self):
        """
        Obtiene todos los archivos Python en el proyecto, excluyendo directorios específicos.
        Si hay un informe de localización cargado, prioriza los archivos de la aplicación.
        
        Returns:
            list: Lista de objetos Path para archivos Python
        """
        # Si tenemos archivos identificados como aplicación, priorizar esos
        if self.focus_files:
            # Convertir rutas relativas a absolutas
            focused_files = [self.project_path / file_path for file_path in self.focus_files]
            
            # Verificar que existen
            verified_files = [file_path for file_path in focused_files if file_path.exists()]
            
            if verified_files:
                print(f"Analizando {len(verified_files)} archivos de aplicación prioritarios")
                return verified_files
            else:
                print("No se encontraron archivos de aplicación válidos, recurriendo a búsqueda completa")
        
        # Buscar todos los archivos Python (comportamiento original)
        python_files = []
        for file_path in self.project_path.rglob("*.py"):
            # Verificar si el archivo está en un directorio excluido
            exclude_file = False
            for excluded_dir in self.excluded_dirs:
                if excluded_dir in file_path.parts:
                    exclude_file = True
                    break
            
            if not exclude_file:
                python_files.append(file_path)
        
        return python_files

def setup_argparse():
    """Configura los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description="Analizador de referencias cruzadas para proyectos Python")
    parser.add_argument("project_path", help="Ruta al directorio raíz del proyecto a analizar")
    parser.add_argument("-o", "--output-dir", 
                        default=r"C:\Users\pepec\Documents\Notefy IA\Data synthetic\Analisis_Detallado\Reportes", 
                        help="Directorio para guardar los resultados")
    parser.add_argument("--report", action="store_true", 
                        help="Generar informe en formato Markdown")
    parser.add_argument("-l", "--localization-report", 
                        help="Ruta al informe de localización de código en formato JSON")
    return parser

def main():
    parser = setup_argparse()
    args = parser.parse_args()
    
    print(f"Analizando referencias cruzadas en: {args.project_path}")
    
    # Crear analizador con informe de localización si se proporciona
    analyzer = CrossReferenceAnalyzer(
        args.project_path, 
        localization_report=args.localization_report
    )
    
    # Ejecutar análisis completo
    analyzer.find_all_definitions()
    analyzer.find_references_for_all_symbols()
    
    # Exportar resultados
    output_dir = args.output_dir
    analyzer.export_results(output_dir)
    
    # Generar informe si se solicita
    if args.report:
        report_path = Path(output_dir) / "cross_reference_report.md"
        analyzer.generate_report(str(report_path))
        print(f"Informe generado en: {report_path}")

if __name__ == "__main__":
    main()
