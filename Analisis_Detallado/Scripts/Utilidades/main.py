import argparse
import yaml
import sys
from pathlib import Path
from core.analysis_manager import AnalysisManager

def load_config():
    try:
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error cargando configuración: {e}")
        sys.exit(1)

def validate_file(file_path: str) -> bool:
    """Valida que el archivo exista y tenga una extensión soportada"""
    path = Path(file_path)
    valid_extensions = {'.csv', '.xlsx', '.xls', '.json', '.yaml', '.yml'}
    return path.exists() and path.suffix.lower() in valid_extensions

def main():
    parser = argparse.ArgumentParser(
        description='Análisis de estructura de datos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --module pacientes --file datos.csv --format html
  python main.py -m pacientes -f datos.xlsx -f json
        """
    )
    
    parser.add_argument(
        '--module', '-m',
        required=True,
        help='Módulo a analizar (ej: pacientes, FARC, BIO, MTP)'
    )
    
    parser.add_argument(
        '--file', '-f',
        required=True,
        help='Archivo a analizar (debe existir en la carpeta input del módulo)'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'html', 'xlsx'],
        default='json',
        help='Formato de salida del reporte (default: json)'
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    try:
        args = parser.parse_args()
        
        if not validate_file(args.file):
            print(f"Error: El archivo '{args.file}' no existe o no tiene un formato soportado")
            sys.exit(1)
            
        config = load_config()
        analyzer = AnalysisManager(config)
        result = analyzer.analyze_structure(args.module, args.file, args.format)
        
        if result:
            print(f"Análisis completado. Reporte guardado en: {result}")
            sys.exit(0)
        else:
            print("Error durante el análisis")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
