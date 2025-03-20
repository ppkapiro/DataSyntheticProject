from pathlib import Path
import shutil
import logging

class FileOrganizer:
    """Organizador de archivos de scripts"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.logger = logging.getLogger(__name__)
        
        # Definir estructura esperada
        self.expected_structure = {
            'Analizadores': {
                'files': [
                    'analysis_manager.py',
                    'cross_references.py',
                    'code_analyzer.py',
                    'pattern_analyzer.py',
                    'metrics_calculator.py'
                ]
            },
            'Localizadores': {
                'files': [
                    'code_locator.py',
                    'file_finder.py',
                    'pattern_locator.py',
                    'structure_locator.py',
                    'import_locator.py'
                ]
            },
            'Importadores': {
                'files': [
                    'import_analyzer.py',
                    'data_importer.py',
                    'template_importer.py',
                    'field_mapper.py',
                    'content_processor.py'
                ]
            },
            'Utilidades': {
                'files': [
                    'file_organizer.py',
                    'dependency_matrix.py',
                    'logger_config.py',
                    'path_manager.py',
                    'validation_utils.py'
                ]
            },
            'core': {
                'files': [
                    'analysis_manager.py',
                    'config_manager.py',
                    'data_manager.py'
                ]
            }
        }

    def analyze_current_structure(self):
        """Analiza la estructura actual y reporta diferencias"""
        current_structure = {}
        missing_files = {}
        misplaced_files = []

        # Analizar estructura actual
        for dir_path in self.base_dir.glob('**/'):
            if dir_path.is_dir() and dir_path.name in self.expected_structure:
                current_structure[dir_path.name] = {
                    'files': [f.name for f in dir_path.glob('*.py')]
                }

        # Encontrar archivos faltantes y mal ubicados
        for dir_name, expected in self.expected_structure.items():
            current_files = current_structure.get(dir_name, {}).get('files', [])
            missing = [f for f in expected['files'] if f not in current_files]
            if missing:
                missing_files[dir_name] = missing

        # Buscar archivos Python fuera de la estructura
        for py_file in self.base_dir.glob('*.py'):
            if py_file.name != '__init__.py':
                suggested_location = self._suggest_location(py_file.name)
                if suggested_location:
                    misplaced_files.append({
                        'file': py_file.name,
                        'suggested_location': suggested_location
                    })

        return {
            'current_structure': current_structure,
            'missing_files': missing_files,
            'misplaced_files': misplaced_files
        }

    def _suggest_location(self, filename: str) -> str:
        """Sugiere la ubicación correcta para un archivo"""
        for dir_name, content in self.expected_structure.items():
            if filename in content['files']:
                return dir_name
        
        # Si no está en la estructura, hacer sugerencia basada en el nombre
        keywords = {
            'Analizadores': ['analysis', 'analyzer', 'metric'],
            'Localizadores': ['locator', 'finder', 'search'],
            'Importadores': ['import', 'data', 'template'],
            'Utilidades': ['util', 'helper', 'tool'],
            'core': ['manager', 'core', 'base']
        }

        for dir_name, words in keywords.items():
            if any(word in filename.lower() for word in words):
                return dir_name
        
        return 'Utilidades'  # Por defecto

    def organize_files(self, dry_run=True):
        """Organiza los archivos según la estructura esperada"""
        analysis = self.analyze_current_structure()
        actions = []

        # Crear directorios faltantes
        for dir_name in self.expected_structure.keys():
            dir_path = self.base_dir / dir_name
            if not dir_path.exists():
                actions.append(('create_dir', dir_path))

        # Mover archivos mal ubicados
        for misplaced in analysis['misplaced_files']:
            source = self.base_dir / misplaced['file']
            dest = self.base_dir / misplaced['suggested_location'] / misplaced['file']
            actions.append(('move_file', source, dest))

        # Ejecutar acciones
        if not dry_run:
            for action in actions:
                if action[0] == 'create_dir':
                    action[1].mkdir(exist_ok=True)
                    # Crear __init__.py
                    (action[1] / '__init__.py').touch()
                elif action[0] == 'move_file':
                    action[1].parent.mkdir(exist_ok=True)
                    shutil.move(str(action[1]), str(action[2]))

        return actions

def main():
    base_dir = Path(__file__).parent.parent
    organizer = FileOrganizer(base_dir)
    
    print("\n=== Análisis de Estructura de Scripts ===")
    analysis = organizer.analyze_current_structure()
    
    print("\nArchivos faltantes por directorio:")
    for dir_name, missing in analysis['missing_files'].items():
        print(f"\n{dir_name}:")
        for file in missing:
            print(f"  - {file}")
    
    print("\nArchivos mal ubicados:")
    for misplaced in analysis['misplaced_files']:
        print(f"  - {misplaced['file']} → {misplaced['suggested_location']}/")
    
    choice = input("\n¿Desea reorganizar los archivos? (s/N): ").lower()
    if choice == 's':
        actions = organizer.organize_files(dry_run=False)
        print("\nAcciones realizadas:")
        for action in actions:
            if action[0] == 'create_dir':
                print(f"  - Creado directorio: {action[1]}")
            elif action[0] == 'move_file':
                print(f"  - Movido: {action[1].name} → {action[2].parent.name}/")
    else:
        print("\nNo se realizaron cambios.")

if __name__ == "__main__":
    main()
