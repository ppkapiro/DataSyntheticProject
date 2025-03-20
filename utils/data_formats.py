import pandas as pd
import json
import yaml
from pathlib import Path
import numpy as np
from utils.ai_extractor import AIExtractor
from typing import Any, Dict, Optional, Union

class DataFormatHandler:
    """Manejador de formatos de datos para entrada/salida"""
    
    SUPPORTED_FORMATS = {
        'txt': {'ext': '.txt', 'desc': 'TXT (Texto plano)', 'priority': 1},  # Prioridad alta
        'csv': {'ext': '.csv', 'desc': 'CSV (Comma Separated Values)', 'priority': 2},
        'xlsx': {'ext': '.xlsx', 'desc': 'Excel Workbook', 'priority': 3},
        'json': {'ext': '.json', 'desc': 'JSON (JavaScript Object Notation)', 'priority': 4},
        'html': {'ext': '.html', 'desc': 'HTML (HyperText Markup Language)', 'priority': 5},
        'yaml': {'ext': '.yaml', 'desc': 'YAML Ain\'t Markup Language', 'priority': 6},
        'tsv': {'ext': '.tsv', 'desc': 'TSV (Tab Separated Values)', 'priority': 7},
        'ods': {'ext': '.ods', 'desc': 'ODS (OpenDocument Spreadsheet)', 'priority': 8}
    }

    @staticmethod
    def read_file(file_path: Union[str, Path]) -> Optional[str]:
        """Lee el contenido de un archivo en varios formatos"""
        file_path = Path(file_path)
        
        try:
            # Determinar formato basado en extensión
            ext = file_path.suffix.lower()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if ext == '.json':
                    # Leer JSON y convertirlo a string
                    data = json.load(f)
                    return json.dumps(data, indent=2, ensure_ascii=False)
                elif ext == '.yaml' or ext == '.yml':
                    # Leer YAML y convertirlo a string
                    data = yaml.safe_load(f)
                    return yaml.dump(data, allow_unicode=True)
                else:
                    # Para otros formatos, leer como texto plano
                    return f.read()

        except Exception as e:
            print(f"\n❌ Error leyendo archivo {file_path.name}: {str(e)}")
            return None

    @staticmethod
    def read_data(file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Lee datos en formato tabular"""
        try:
            file_path = Path(file_path)
            ext = file_path.suffix.lower()
            
            if ext == '.csv':
                return pd.read_csv(file_path)
            elif ext in ['.xls', '.xlsx']:
                return pd.read_excel(file_path)
            elif ext == '.json':
                return pd.read_json(file_path)
            else:
                print(f"\n❌ Formato no soportado: {ext}")
                return None
                
        except Exception as e:
            print(f"\n❌ Error leyendo datos: {str(e)}")
            return None

    @staticmethod
    def save_data(data: Any, output_path: Path, format: str = 'json') -> bool:
        """Guarda datos en el formato especificado"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'csv':
                if isinstance(data, pd.DataFrame):
                    data.to_csv(output_path, index=False)
                else:
                    pd.DataFrame(data).to_csv(output_path, index=False)
            elif format == 'yaml':
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True)
            else:
                print(f"\n❌ Formato no soportado: {format}")
                return False
                
            return True
            
        except Exception as e:
            print(f"\n❌ Error guardando datos: {str(e)}")
            return False

    @staticmethod
    def prompt_format_selection() -> Optional[str]:
        """Solicita al usuario seleccionar un formato de salida"""
        print("\nFormatos disponibles:")
        for idx, (format_key, format_info) in enumerate(DataFormatHandler.SUPPORTED_FORMATS.items(), 1):
            print(f"{idx}. {format_info['desc']}")
        
        while True:
            try:
                opcion = int(input("\nSeleccione formato (0 para cancelar): ")) - 1
                if opcion == -1:
                    return None
                if 0 <= opcion < len(DataFormatHandler.SUPPORTED_FORMATS):
                    return list(DataFormatHandler.SUPPORTED_FORMATS.keys())[opcion]
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")
