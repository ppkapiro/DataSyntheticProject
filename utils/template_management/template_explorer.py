from pathlib import Path
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

class TemplateExplorer:
    """Explorador de archivos de plantillas"""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path("templates")
        self.supported_extensions = ['.txt', '.json', '.yaml', '.yml', '.py']

    def list_available_files(self, directory: Path = None) -> List[Dict[str, Any]]:
        """Lista todos los archivos disponibles con metadata"""
        search_dir = directory or self.base_dir
        files = []

        try:
            for entry in os.scandir(search_dir):
                if entry.is_file() and self._is_supported_file(entry.path):
                    files.append(self._get_file_info(entry))
                elif entry.is_dir():
                    # Agregar indicador de carpeta
                    files.append({
                        'name': entry.name,
                        'path': str(entry.path),
                        'type': 'directory',
                        'size': self._get_directory_size(entry.path),
                        'modified': datetime.fromtimestamp(entry.stat().st_mtime),
                        'items': len(list(Path(entry.path).glob('*')))
                    })

        except Exception as e:
            print(f"Error listando archivos: {str(e)}")
            return []

        return sorted(files, key=lambda x: (x['type'] == 'file', x['name']))

    def select_file(self, files: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Muestra menú de selección de archivo"""
        print("\n=== ARCHIVOS DISPONIBLES ===")
        print("0. Cancelar")
        
        for idx, file_info in enumerate(files, 1):
            type_icon = "📁" if file_info['type'] == 'directory' else "📄"
            size = self._format_size(file_info['size'])
            print(f"{idx}. {type_icon} {file_info['name']} ({size})")

        try:
            choice = int(input("\nSeleccione archivo (0 para cancelar): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(files):
                return files[choice - 1]
        except ValueError:
            print("Selección inválida")
        return None

    def navigate_directory(self, current_path: Path = None) -> Optional[Dict[str, Any]]:
        """Permite navegación interactiva de directorios"""
        current = current_path or self.base_dir
        
        while True:
            print(f"\nDirectorio actual: {current}")
            files = self.list_available_files(current)
            selected = self.select_file(files)

            if not selected:
                return None

            if selected['type'] == 'directory':
                # Navegar al directorio seleccionado
                current = Path(selected['path'])
            else:
                return selected

    def _is_supported_file(self, file_path: str) -> bool:
        """Verifica si el archivo tiene una extensión soportada"""
        return any(file_path.lower().endswith(ext) for ext in self.supported_extensions)

    def _get_file_info(self, entry: os.DirEntry) -> Dict[str, Any]:
        """Obtiene información detallada de un archivo"""
        stat = entry.stat()
        return {
            'name': entry.name,
            'path': str(entry.path),
            'type': 'file',
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'extension': Path(entry.path).suffix.lower()
        }

    def _get_directory_size(self, directory: str) -> int:
        """Calcula el tamaño total de un directorio"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size

    def _format_size(self, size: int) -> str:
        """Formatea el tamaño de archivo de forma legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
