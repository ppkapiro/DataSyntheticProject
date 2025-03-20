import os
from pathlib import Path
import time
from typing import List, Dict, Any, Optional, Tuple
import shutil
import logging

logger = logging.getLogger(__name__)

class SearchVisualizer:
    """
    Visualizador del proceso de búsqueda en el sistema de archivos.
    Proporciona representación visual del proceso de búsqueda y permite
    generar reportes sobre la estructura de archivos del proyecto.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Inicializa el visualizador de búsqueda
        
        Args:
            project_root: Ruta raíz del proyecto. Si es None, se usará el directorio actual.
        """
        self.project_root = project_root or Path.cwd()
        self.term_width = shutil.get_terminal_size().columns
        self.search_log = []
        self.highlight_color = '\033[92m'  # Verde
        self.normal_color = '\033[0m'      # Reset
        self.warning_color = '\033[93m'    # Amarillo
        self.error_color = '\033[91m'      # Rojo
        self.use_colors = True
        
    def colored_text(self, text: str, color_code: str) -> str:
        """Añade color al texto si está habilitado"""
        if self.use_colors:
            return f"{color_code}{text}{self.normal_color}"
        return text
        
    def visualize_search(self, search_path: Path, pattern: str = "*.pdf", 
                         max_depth: int = 3, interactive: bool = True) -> List[Path]:
        """
        Visualiza el proceso de búsqueda de archivos en el sistema.
        
        Args:
            search_path: Ruta donde iniciar la búsqueda
            pattern: Patrón de búsqueda (ej: "*.pdf")
            max_depth: Profundidad máxima de búsqueda
            interactive: Si es True, muestra la búsqueda paso a paso
            
        Returns:
            List[Path]: Lista de archivos encontrados
        """
        self.search_log.clear()
        found_files = []
        
        print(f"\n{'='*self.term_width}")
        print(f"BÚSQUEDA DE ARCHIVOS: {pattern}")
        print(f"{'='*self.term_width}")
        print(f"Iniciando búsqueda desde: {search_path}")
        
        # Realizar la búsqueda
        start_time = time.time()
        
        for root, dirs, files in os.walk(search_path):
            # Calcular profundidad actual
            rel_path = Path(root).relative_to(search_path)
            current_depth = len(rel_path.parts)
            
            # Limitar profundidad
            if current_depth > max_depth:
                dirs.clear()  # No seguir explorando subdirectorios
                continue
                
            # Mostrar directorio actual
            indent = "  " * current_depth
            if interactive:
                print(f"{indent}📁 {self.colored_text(Path(root).name, self.highlight_color)}")
                
            self.search_log.append({
                "type": "directory",
                "path": root,
                "depth": current_depth,
                "message": f"Explorando directorio: {root}"
            })
            
            # Filtrar archivos según el patrón
            import fnmatch
            matching_files = [f for f in files if fnmatch.fnmatch(f, pattern)]
            
            # Procesar archivos encontrados
            for file in matching_files:
                file_path = Path(root) / file
                found_files.append(file_path)
                if interactive:
                    print(f"{indent}  📄 {self.colored_text(file, self.warning_color)}")
                
                self.search_log.append({
                    "type": "file",
                    "path": str(file_path),
                    "depth": current_depth,
                    "message": f"Archivo encontrado: {file}"
                })
                
            # Pausa para visualización interactiva
            if interactive and matching_files:
                time.sleep(0.2)  # Breve pausa para mostrar progreso

        # Mostrar resumen
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*self.term_width}")
        print(f"RESUMEN DE BÚSQUEDA")
        print(f"{'='*self.term_width}")
        print(f"Patrón de búsqueda: {pattern}")
        print(f"Directorio inicial: {search_path}")
        print(f"Profundidad máxima: {max_depth}")
        print(f"Archivos encontrados: {len(found_files)}")
        print(f"Tiempo de búsqueda: {elapsed_time:.2f} segundos")
        
        if found_files:
            print("\nARCHIVOS ENCONTRADOS:")
            for idx, file in enumerate(found_files, 1):
                print(f"{idx}. {file.relative_to(search_path)}")
        else:
            print(f"\n{self.colored_text('No se encontraron archivos que coincidan con el patrón', self.error_color)}")
            
        print(f"\n{'='*self.term_width}")
        
        return found_files
        
    def generate_search_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Genera un informe de la última búsqueda realizada
        
        Args:
            output_path: Ruta donde guardar el informe. Si es None, se creará en el directorio temporal.
            
        Returns:
            Path: Ruta al informe generado
        """
        if not self.search_log:
            raise ValueError("No hay datos de búsqueda disponibles. Ejecute visualize_search primero.")
            
        # Crear informe HTML
        import tempfile
        from datetime import datetime
        
        if not output_path:
            temp_dir = Path(tempfile.gettempdir())
            output_path = temp_dir / f"search_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
        # Generar HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Informe de Búsqueda - Notefy IA</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2c3e50; }
                .directory { color: #3498db; margin-top: 10px; }
                .file { color: #e74c3c; margin-left: 20px; }
                .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>Informe de Búsqueda - Notefy IA</h1>
            <div class="summary">
                <h2>Resumen</h2>
                <p>Fecha: {date}</p>
                <p>Archivos encontrados: {file_count}</p>
                <p>Directorios explorados: {dir_count}</p>
            </div>
            <h2>Detalles de la Búsqueda</h2>
        """.format(
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            file_count=sum(1 for entry in self.search_log if entry['type'] == 'file'),
            dir_count=sum(1 for entry in self.search_log if entry['type'] == 'directory')
        )
        
        # Agregar detalles
        for entry in self.search_log:
            indent = "&nbsp;" * (entry['depth'] * 4)
            if entry['type'] == 'directory':
                html_content += f"""
                <div class="directory">{indent}📁 {Path(entry['path']).name}</div>
                """
            else:
                html_content += f"""
                <div class="file">{indent}📄 {Path(entry['path']).name}</div>
                """
        
        # Cerrar HTML
        html_content += """
        </body>
        </html>
        """
        
        # Guardar archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Informe de búsqueda generado en: {output_path}")
        return output_path
        
    def visualize_project_structure(self, max_depth: int = 3) -> None:
        """
        Visualiza la estructura completa del proyecto
        
        Args:
            max_depth: Profundidad máxima para visualizar
        """
        print(f"\n{'='*self.term_width}")
        print(f"ESTRUCTURA DEL PROYECTO: {self.project_root.name}")
        print(f"{'='*self.term_width}")
        
        def print_directory(directory, prefix="", is_last=True, depth=0):
            if depth > max_depth:
                return
                
            # Determinar prefijo para la línea actual
            current_prefix = prefix + ("└── " if is_last else "├── ")
            print(f"{current_prefix}{self.colored_text(directory.name, self.highlight_color)}")
            
            # Calcular prefijo para elementos hijos
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Obtener subdirectorios y archivos
            try:
                items = list(directory.iterdir())
                dirs = [d for d in items if d.is_dir()]
                files = [f for f in items if f.is_file()]
                
                # Ordenar directorios y archivos
                dirs.sort()
                files.sort()
                
                # Mostrar subdirectorios
                for i, d in enumerate(dirs):
                    print_directory(d, new_prefix, i == len(dirs) - 1 and not files, depth + 1)
                
                # Mostrar archivos (limitados a 10 por directorio para mayor claridad)
                max_files_to_show = 10
                for i, f in enumerate(files[:max_files_to_show]):
                    is_file_last = i == len(files) - 1 or i == max_files_to_show - 1
                    file_prefix = new_prefix + ("└── " if is_file_last else "├── ")
                    print(f"{file_prefix}{f.name}")
                
                # Indicar si hay más archivos
                if len(files) > max_files_to_show:
                    print(f"{new_prefix}└── {self.colored_text('... y más archivos', self.warning_color)}")
                    
            except PermissionError:
                print(f"{new_prefix}└── {self.colored_text('Error de permisos', self.error_color)}")
        
        # Iniciar visualización
        print_directory(self.project_root)
        
        print(f"\n{'='*self.term_width}")


if __name__ == "__main__":
    # Ejemplo de uso
    visualizer = SearchVisualizer()
    
    # 1. Visualizar estructura del proyecto
    print("\nVisualizando estructura del proyecto...")
    visualizer.visualize_project_structure(max_depth=2)
    
    # 2. Visualizar proceso de búsqueda
    print("\nBuscando archivos PDF...")
    project_root = Path(__file__).parent.parent
    found_files = visualizer.visualize_search(
        project_root, 
        pattern="*.pdf", 
        max_depth=3,
        interactive=True
    )
    
    # 3. Generar informe
    if found_files:
        print("\nGenerando informe de búsqueda...")
        report_path = visualizer.generate_search_report()
        print(f"Informe guardado en: {report_path}")
        
        # Intentar abrir el informe automáticamente
        import webbrowser
        webbrowser.open(str(report_path))
