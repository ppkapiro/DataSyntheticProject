#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Localizador de código fuente en el proyecto Notefy IA.

Este script analiza recursivamente un directorio para identificar código fuente Python,
distinguiendo entre código de la aplicación y scripts de herramientas/análisis.
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
import ast
from datetime import datetime

class CodeLocator:
    def __init__(self, root_dir):
        """
        Inicializa el localizador con la ruta raíz a explorar.
        
        Args:
            root_dir (str): Ruta al directorio raíz del proyecto
        """
        self.root_dir = Path(root_dir)
        self.excluded_dirs = {'env', 'venv', '__pycache__', '.git', '.idea', '.vscode'}
        self.tool_keywords = {'test', 'script', 'util', 'tool', 'analy', 'report'}
        self.app_keywords = {'app', 'main', 'core', 'ui', 'model', 'view', 'controller', 'notefy'}
        
        # Resultados
        self.python_files = []
        self.potential_app_files = []
        self.potential_tool_files = []
        self.module_structure = defaultdict(list)
        self.class_definitions = {}
        self.function_definitions = {}
        self.imports_by_file = {}
        self.file_sizes = {}

    def locate(self):
        """Localiza todos los archivos Python en el proyecto."""
        print(f"Explorando directorio: {self.root_dir}")
        
        for root, dirs, files in os.walk(self.root_dir):
            # Excluir directorios no deseados
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            path = Path(root)
            rel_path = path.relative_to(self.root_dir)
            
            for file in files:
                if file.endswith('.py'):
                    file_path = path / file
                    rel_file_path = file_path.relative_to(self.root_dir)
                    
                    # Agregar a la lista general de archivos Python
                    self.python_files.append(str(rel_file_path))
                    
                    # Calcular tamaño del archivo
                    self.file_sizes[str(rel_file_path)] = file_path.stat().st_size
                    
                    # Categorizar el archivo
                    if self._is_likely_app_code(file_path, rel_file_path):
                        self.potential_app_files.append(str(rel_file_path))
                    else:
                        self.potential_tool_files.append(str(rel_file_path))
                    
                    # Registrar en estructura de módulos
                    module_path = str(rel_path)
                    if module_path == '.':
                        module_path = 'root'
                    self.module_structure[module_path].append(file)
                    
                    # Analizar contenido del archivo
                    self._analyze_file_content(file_path, str(rel_file_path))
        
        print(f"Se encontraron {len(self.python_files)} archivos Python.")
        print(f"- {len(self.potential_app_files)} archivos potenciales de aplicación")
        print(f"- {len(self.potential_tool_files)} archivos potenciales de herramientas/análisis")
    
    def _is_likely_app_code(self, file_path, rel_file_path):
        """
        Determina si un archivo es probablemente código de la aplicación o una herramienta/script.
        
        Args:
            file_path (Path): Ruta completa al archivo
            rel_file_path (Path): Ruta relativa al archivo desde la raíz
            
        Returns:
            bool: True si es probablemente código de la aplicación
        """
        # Verificar por palabras clave en la ruta
        path_str = str(rel_file_path).lower()
        
        # Si contiene palabras clave explícitas de herramientas/análisis
        if any(keyword in path_str for keyword in self.tool_keywords):
            return False
        
        # Si contiene palabras clave explícitas de la aplicación
        if any(keyword in path_str for keyword in self.app_keywords):
            return True
        
        # Análisis más detallado del contenido
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(4000)  # Leer solo los primeros 4000 caracteres
                
                # Verificar presencia de docstring o comentarios relacionados con la aplicación
                app_indicators = ['notefy', 'application', 'app', 'main']
                if any(indicator in content.lower() for indicator in app_indicators):
                    return True
                
                # Verificar presencia de docstring o comentarios relacionados con herramientas
                tool_indicators = ['script', 'tool', 'utility', 'analysis', 'test']
                if any(indicator in content.lower() for indicator in tool_indicators):
                    return False
                
                # Verificar si parece un módulo principal o ejecutable
                if "__main__" in content and ("app" in content.lower() or "aplicación" in content.lower()):
                    return True
        except Exception:
            pass  # Si hay error al leer, continuar con otras heurísticas
        
        # Por defecto, usar heurísticas de ubicación
        if "codigo_sintetico" in str(rel_file_path):
            return True
        if "Scripts" in str(rel_file_path) or "scripts" in str(rel_file_path):
            return False
            
        return False  # Por defecto, considerarlo una herramienta
    
    def _analyze_file_content(self, file_path, rel_path):
        """
        Analiza el contenido de un archivo Python para extraer clases, funciones e imports.
        
        Args:
            file_path (Path): Ruta al archivo
            rel_path (str): Ruta relativa para guardar en los diccionarios
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Extraer clases
            classes = {}
            functions = {}
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                    
                    classes[node.name] = {
                        'methods': methods,
                        'line': node.lineno
                    }
                elif isinstance(node, ast.FunctionDef) and node.name != '__init__':
                    # Solo funciones de nivel superior, no métodos
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.iter_child_nodes(tree)):
                        functions[node.name] = {
                            'line': node.lineno,
                            'args': [arg.arg for arg in node.args.args if arg.arg != 'self']
                        }
                elif isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append({
                            "type": "import",
                            "name": name.name,
                            "alias": name.asname
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module if node.module else ""
                    for name in node.names:
                        imports.append({
                            "type": "from",
                            "module": module,
                            "name": name.name,
                            "alias": name.asname
                        })
            
            if classes:
                self.class_definitions[rel_path] = classes
            if functions:
                self.function_definitions[rel_path] = functions
            if imports:
                self.imports_by_file[rel_path] = imports
                
        except Exception as e:
            print(f"Error al analizar {file_path}: {e}")
    
    def find_main_modules(self):
        """
        Identifica los posibles módulos principales (puntos de entrada) de la aplicación.
        
        Returns:
            list: Lista de rutas a posibles módulos principales
        """
        main_candidates = []
        
        for file_path in self.potential_app_files:
            full_path = self.root_dir / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar patrones que sugieran que es un punto de entrada
                if "__main__" in content and ("app" in content.lower() or "start" in content.lower()):
                    main_candidates.append(file_path)
                elif "main.py" in str(file_path).lower():
                    main_candidates.append(file_path)
            except Exception:
                continue
                
        return sorted(main_candidates, key=lambda x: self._score_main_candidate(x), reverse=True)
    
    def _score_main_candidate(self, file_path):
        """Calcula una puntuación para determinar qué tan probable es que sea un módulo principal."""
        score = 0
        
        # Bonificación por nombre
        if "main.py" == Path(file_path).name:
            score += 10
        elif "app.py" == Path(file_path).name:
            score += 8
        elif "start" in Path(file_path).name:
            score += 5
        
        # Bonificación por ubicación
        if str(file_path).count(os.sep) == 0:  # En el directorio raíz
            score += 3
        
        # Bonificación por tamaño (asumiendo que los archivos principales son más grandes)
        file_size = self.file_sizes.get(str(file_path), 0)
        score += min(file_size / 1000, 5)  # Máx 5 puntos por tamaño
        
        return score
    
    def find_core_modules(self):
        """
        Identifica los módulos centrales (core) de la aplicación.
        
        Returns:
            list: Lista de rutas a posibles módulos centrales
        """
        core_scores = {}
        
        for file_path in self.potential_app_files:
            # Si está en un directorio 'core'
            if 'core' in str(file_path).lower():
                core_scores[file_path] = 10
                continue
            
            # Verificar conexiones de importación
            ref_count = 0
            file_name = Path(file_path).name
            
            for imports in self.imports_by_file.values():
                for imp in imports:
                    if imp['type'] == 'from' and file_name.startswith(f"{imp['module']}."):
                        ref_count += 1
                    elif imp['type'] == 'import' and file_name == f"{imp['name']}.py":
                        ref_count += 1
            
            # Más importaciones sugiere mayor centralidad
            if ref_count > 0:
                core_scores[file_path] = ref_count
        
        # Ordenar por puntuación
        return sorted(core_scores.keys(), key=lambda x: core_scores[x], reverse=True)
    
    def _ensure_report_directory(self):
        """
        Asegura que el directorio de reportes exista.
        
        Returns:
            Path: Ruta al directorio de reportes
        """
        reports_dir = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/Analisis_Detallado/Reportes")
        localizados_dir = reports_dir / "Localizados"
        
        # Crear directorios si no existen
        reports_dir.mkdir(parents=True, exist_ok=True)
        localizados_dir.mkdir(exist_ok=True)
        
        return localizados_dir
    
    def generate_report(self, output_file=None):
        """
        Genera un reporte detallado sobre la estructura de código encontrada.
        
        Args:
            output_file (str, optional): Ruta para guardar el informe JSON
        
        Returns:
            dict: Reporte completo
        """
        report = {
            "summary": {
                "total_python_files": len(self.python_files),
                "app_code_files": len(self.potential_app_files),
                "tool_files": len(self.potential_tool_files),
                "total_classes": sum(len(classes) for classes in self.class_definitions.values()),
                "total_functions": sum(len(funcs) for funcs in self.function_definitions.values())
            },
            "module_structure": dict(self.module_structure),
            "potential_app_modules": self.potential_app_files,
            "potential_tools": self.potential_tool_files,
            "main_candidates": self.find_main_modules(),
            "core_modules": self.find_core_modules(),
            "class_definitions": self.class_definitions,
            "function_definitions": self.function_definitions
        }
        
        if output_file:
            # Si se proporciona una ruta específica, usarla
            output_path = Path(output_file)
        else:
            # Si no se proporciona ruta, usar el directorio de reportes por defecto
            report_dir = self._ensure_report_directory()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = report_dir / f"reporte_codigo_{timestamp}.json"
        
        # Asegurar que el directorio padre exista
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"Reporte guardado en {output_path}")
        
        return report
    
    def print_summary(self):
        """Imprime un resumen del análisis en la consola."""
        print("\n=== Resumen del Análisis de Código ===")
        print(f"Total de archivos Python: {len(self.python_files)}")
        print(f"Archivos de código de aplicación: {len(self.potential_app_files)}")
        print(f"Archivos de herramientas/análisis: {len(self.potential_tool_files)}")
        
        # Mostrar estructura de módulos
        print("\n--- Estructura de Módulos ---")
        for module, files in sorted(self.module_structure.items()):
            print(f"{module}: {len(files)} archivos")
        
        # Mostrar candidatos a punto de entrada
        main_candidates = self.find_main_modules()
        if main_candidates:
            print("\n--- Posibles Puntos de Entrada ---")
            for candidate in main_candidates[:5]:
                print(f"- {candidate}")
        
        # Mostrar módulos centrales
        core_modules = self.find_core_modules()
        if core_modules:
            print("\n--- Posibles Módulos Centrales ---")
            for module in core_modules[:5]:
                print(f"- {module}")
        
        # Mostrar estadísticas de clases y funciones
        print("\n--- Estadísticas de Código ---")
        total_classes = sum(len(classes) for classes in self.class_definitions.values())
        total_functions = sum(len(funcs) for funcs in self.function_definitions.values())
        print(f"Clases definidas: {total_classes}")
        print(f"Funciones definidas: {total_functions}")

def main():
    parser = argparse.ArgumentParser(description="Localizador de código en el proyecto Notefy IA")
    parser.add_argument("root_dir", nargs="?", default=os.getcwd(),
                       help="Directorio raíz a analizar (por defecto: directorio actual)")
    parser.add_argument("-o", "--output", help="Archivo para guardar el reporte JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mostrar información detallada")
    args = parser.parse_args()
    
    locator = CodeLocator(args.root_dir)
    locator.locate()
    
    if args.verbose:
        locator.print_summary()
    
    # Siempre generar un reporte, ya sea en la ubicación especificada o en la predeterminada
    locator.generate_report(args.output)
    
    if not args.output:
        locator.print_summary()

if __name__ == "__main__":
    main()
