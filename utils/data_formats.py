import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import csv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importaciones condicionales con manejo de errores
try:
    import pandas as pd
except ImportError:
    logger.error("pandas no está instalado. Ejecute: pip install pandas")
    pd = None

try:
    import yaml
except ImportError:
    logger.error("pyyaml no está instalado. Ejecute: pip install pyyaml")
    yaml = None

try:
    import json
except ImportError:
    logger.error("json no está disponible en Python")
    json = None

try:
    import openpyxl
except ImportError:
    logger.error("openpyxl no está instalado. Ejecute: pip install openpyxl")
    openpyxl = None

try:
    import odf
except ImportError:
    logger.error("odfpy no está instalado. Ejecute: pip install odfpy")
    odf = None

class DataFormatHandler:
    """Manejador de formatos de datos para exportación e importación"""
    
    @classmethod
    def check_dependencies(cls) -> Dict[str, bool]:
        """Verifica las dependencias necesarias"""
        dependencies = {
            'pandas': pd is not None,
            'yaml': yaml is not None,
            'json': json is not None
        }
        
        for dep, available in dependencies.items():
            if not available:
                logger.warning(f"La dependencia {dep} no está disponible")
                
        return dependencies

    # Definir formatos soportados con sus extensiones y descripciones
    SUPPORTED_FORMATS = {
        'json': {
            'ext': '.json',
            'desc': 'Formato JSON (JavaScript Object Notation)',
            'dependencies': ['json']
        },
        'yaml': {
            'ext': '.yaml',
            'desc': 'Formato YAML (YAML Ain\'t Markup Language)',
            'dependencies': ['yaml']
        },
        'txt': {
            'ext': '.txt',
            'desc': 'Texto plano',
            'dependencies': []
        },
        'csv': {
            'ext': '.csv',
            'desc': 'Valores separados por comas (CSV)',
            'dependencies': ['csv']
        },
        'xlsx': {
            'ext': '.xlsx',
            'desc': 'Microsoft Excel (formato XLSX)',
            'dependencies': ['openpyxl', 'pandas']
        },
        'html': {
            'ext': '.html',
            'desc': 'Documento HTML',
            'dependencies': []
        },
        'tsv': {
            'ext': '.tsv',
            'desc': 'Valores separados por tabulaciones (TSV)',
            'dependencies': ['csv']
        },
        'ods': {
            'ext': '.ods',
            'desc': 'Open Document Spreadsheet',
            'dependencies': ['odfpy', 'pandas']
        }
    }
    
    @classmethod
    def prompt_format_selection(cls) -> Optional[str]:
        """Muestra una lista de formatos disponibles y permite al usuario seleccionar uno"""
        print("\n=== FORMATOS DISPONIBLES ===")
        
        # Verificar qué formatos están disponibles basados en las dependencias instaladas
        available_formats = cls._get_available_formats()
        
        if not available_formats:
            print("Error: No hay formatos disponibles.")
            return None
            
        for idx, (format_key, format_info) in enumerate(available_formats.items(), 1):
            print(f"{idx}. {format_info['desc']} ({format_info['ext']})")
        print("0. Cancelar")
        
        while True:
            try:
                selection = input("\nSeleccione un formato (0 para cancelar): ").strip()
                
                if selection == '0':
                    return None
                    
                idx = int(selection) - 1
                if 0 <= idx < len(available_formats):
                    return list(available_formats.keys())[idx]
                    
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")
    
    @classmethod
    def _get_available_formats(cls) -> Dict[str, Dict[str, str]]:
        """Retorna los formatos disponibles basados en las dependencias instaladas"""
        available_formats = {}
        
        for format_key, format_info in cls.SUPPORTED_FORMATS.items():
            # Verificar si todas las dependencias están disponibles
            dependencies_available = True
            
            for dep in format_info['dependencies']:
                try:
                    if dep == 'json':
                        import json
                    elif dep == 'yaml':
                        import yaml
                    elif dep == 'csv':
                        import csv
                    elif dep == 'openpyxl':
                        import openpyxl
                    elif dep == 'pandas':
                        import pandas
                    elif dep == 'odfpy':
                        import odf
                except ImportError:
                    dependencies_available = False
                    break
            
            # Si todas las dependencias están disponibles, agregar el formato a la lista
            if dependencies_available:
                available_formats[format_key] = format_info
        
        return available_formats
    
    @classmethod
    def save_data(cls, data: Dict[str, Any], output_path: Union[str, Path], format_key: str) -> bool:
        """
        Guarda los datos en el formato especificado
        
        Args:
            data: Diccionario de datos a guardar
            output_path: Ruta completa donde guardar el archivo (incluyendo el nombre)
            format_key: Clave del formato (json, yaml, txt, etc.)
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Convertir output_path a Path
            output_path = Path(output_path)
            
            # Asegurar que el directorio padre existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Preparar datos antes de guardar (para manejar tipos no serializables como datetime)
            prepared_data = cls._prepare_data_for_export(data)
            
            # Guardar según el formato
            if format_key == 'json':
                return cls._save_json(prepared_data, output_path)
            elif format_key == 'yaml':
                return cls._save_yaml(prepared_data, output_path)
            elif format_key == 'txt':
                return cls._save_txt(prepared_data, output_path)
            elif format_key == 'csv':
                return cls._save_csv(prepared_data, output_path)
            elif format_key == 'xlsx':
                return cls._save_excel(prepared_data, output_path)
            elif format_key == 'html':
                return cls._save_html(prepared_data, output_path)
            elif format_key == 'tsv':
                return cls._save_tsv(prepared_data, output_path)
            elif format_key == 'ods':
                return cls._save_ods(prepared_data, output_path)
            else:
                logger.error(f"Formato no soportado: {format_key}")
                return False
                
        except Exception as e:
            logger.error(f"Error al guardar en formato {format_key}: {str(e)}")
            return False
    
    @classmethod
    def _prepare_data_for_export(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara los datos para exportación, convirtiendo tipos no serializables"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[key] = cls._prepare_data_for_export(value)
            return result
        elif isinstance(data, list):
            return [cls._prepare_data_for_export(item) for item in data]
        elif isinstance(data, (datetime)):
            return data.isoformat()
        elif isinstance(data, (int, float, str, bool, type(None))):
            return data
        else:
            # Para otros tipos, convertir a string
            return str(data)
    
    @classmethod
    def _save_json(cls, data: Dict[str, Any], output_path: Path) -> bool:
        """Guarda los datos en formato JSON sin truncar ningún contenido"""
        try:
            # Asegurar que todas las claves estén presentes y completas
            if 'contenido_completo' in data and isinstance(data['contenido_completo'], str):
                # Verificar que el contenido completo no esté truncado
                original_length = len(data['contenido_completo'])
                if original_length > 1000 and data['contenido_completo'].endswith('...'):
                    # Esto indicaría que el contenido fue truncado en algún punto
                    logger.warning(f"Se detectó posible truncamiento en 'contenido_completo' ({original_length} caracteres)")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Configuración mejorada para evitar problemas de serialización:
                # - ensure_ascii=False: mantiene caracteres especiales/Unicode
                # - indent=2: formato legible
                # - default=str: convierte tipos complejos como datetime a string
                # - check_circular=True: evita errores con referencias circulares
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                
            # Verificar que el archivo se escribió correctamente y tiene contenido
            if output_path.stat().st_size > 0:
                return True
            else:
                logger.error("El archivo JSON se creó pero está vacío")
                return False
        except Exception as e:
            logger.error(f"Error al guardar JSON: {str(e)}")
            return False
    
    @classmethod
    def _save_txt(cls, data: Dict[str, Any], output_path: Path) -> bool:
        """Guarda los datos en formato de texto plano con mejor formato"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Formato de secciones principal
                for key, value in data.items():
                    if key == 'paciente' and isinstance(value, dict):
                        f.write(f"=== {key} ===\n")
                        for sub_key, sub_value in value.items():
                            f.write(f"{sub_key}: {sub_value}\n")
                        f.write("\n")
                    elif key == 'archivo_original' and isinstance(value, dict):
                        f.write(f"=== {key} ===\n")
                        for sub_key, sub_value in value.items():
                            f.write(f"{sub_key}: {sub_value}\n")
                        f.write("\n")
                    elif key == 'extraccion' and isinstance(value, dict):
                        f.write(f"=== {key} ===\n")
                        for sub_key, sub_value in value.items():
                            f.write(f"{sub_key}: {sub_value}\n")
                        f.write("\n")
                    elif key == 'estadisticas' and isinstance(value, dict):
                        f.write(f"=== {key} ===\n")
                        for sub_key, sub_value in value.items():
                            f.write(f"{sub_key}: {sub_value}\n")
                        f.write("\n")
                    elif key == 'contenido_completo':
                        f.write(f"{key}: {value}\n")
                    elif not isinstance(value, dict):
                        f.write(f"{key}: {value}\n")
                
                return True
        except Exception as e:
            logger.error(f"Error al guardar TXT: {str(e)}")
            return False
    
    @classmethod
    def _save_csv(cls, data: Dict[str, Any], output_path: Path) -> bool:
        """Guarda los datos en formato CSV"""
        try:
            # Aplanar datos para estructura tabular
            flattened_data = cls._flatten_data_for_tabular(data)
            
            # Guardar como CSV
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
            return True
        except Exception as e:
            logger.error(f"Error al guardar CSV: {str(e)}")
            return False
    
    @classmethod
    def _save_tsv(cls, data: Dict[str, Any], output_path: Path) -> bool:
        """Guarda los datos en formato TSV"""
        try:
            # Aplanar datos para estructura tabular
            flattened_data = cls._flatten_data_for_tabular(data)
            
            # Guardar como TSV (CSV con delimitador de tabulación)
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys(), delimiter='\t')
                writer.writeheader()
                writer.writerows(flattened_data)
            return True
        except Exception as e:
            logger.error(f"Error al guardar TSV: {str(e)}")
            return False
    
    @classmethod
    def _save_excel(cls, data: Dict[str, Any], output_path: Path) -> bool:
        """Guarda los datos en formato Excel (XLSX)"""
        try:
            import pandas as pd
            
            # Aplanar datos para estructura tabular
            flattened_data = cls._flatten_data_for_tabular(data)
            
            # Convertir a DataFrame y guardar
            df = pd.DataFrame(flattened_data)
            
            # Si hay una clave 'contenido', crear una hoja adicional con el contenido completo
            if 'contenido' in data:
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Datos', index=False)
                    
                    # Crear una hoja con el contenido completo
                    content_df = pd.DataFrame({'Contenido': [data['contenido']]})
                    content_df.to_excel(writer, sheet_name='Contenido', index=False)
            else:
                # Solo guardar la hoja principal
                df.to_excel(output_path, index=False)
                
            return True
        except Exception as e:
            logger.error(f"Error al guardar Excel: {str(e)}")
            return False
    
    @classmethod
    def _save_ods(cls, data: Dict[str, Any], output_path: Path) -> bool:
        """Guarda los datos en formato Open Document Spreadsheet"""
        try:
            import pandas as pd
            
            # Aplanar datos para estructura tabular
            flattened_data = cls._flatten_data_for_tabular(data)
            
            # Convertir a DataFrame y guardar
            df = pd.DataFrame(flattened_data)
            df.to_excel(output_path, engine='odf', index=False)
            return True
        except Exception as e:
            logger.error(f"Error al guardar ODS: {str(e)}")
            return False
    
    @classmethod
    def _save_html(cls, data: Dict[str, Any], output_path: Path) -> bool:
        """Guarda los datos en formato HTML"""
        try:
            # Crear un HTML básico con los datos
            html_content = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                f"<title>Documento Exportado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>",
                "<style>",
                "body { font-family: Arial, sans-serif; margin: 20px; }",
                "h1 { color: #333366; }",
                "table { border-collapse: collapse; width: 100%; }",
                "th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }",
                "th { background-color: #f2f2f2; }",
                "pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }",
                "</style>",
                "</head>",
                "<body>",
                f"<h1>Documento Exportado</h1>",
                "<p><strong>Fecha de exportación:</strong> " + data.get('fecha_extraccion', datetime.now().isoformat()) + "</p>"
            ]
            
            # Crear una tabla con los metadatos
            html_content.extend([
                "<h2>Metadatos</h2>",
                "<table>",
                "<tr><th>Campo</th><th>Valor</th></tr>"
            ])
            
            # Agregar filas a la tabla
            for key, value in data.items():
                if key != 'contenido' and not isinstance(value, dict):
                    html_content.append(f"<tr><td>{key}</td><td>{value}</td></tr>")
            
            html_content.append("</table>")
            
            # Si hay estadísticas, agregarlas
            if 'estadisticas' in data and isinstance(data['estadisticas'], dict):
                html_content.extend([
                    "<h2>Estadísticas</h2>",
                    "<table>",
                    "<tr><th>Métrica</th><th>Valor</th></tr>"
                ])
                
                for key, value in data['estadisticas'].items():
                    html_content.append(f"<tr><td>{key}</td><td>{value}</td></tr>")
                
                html_content.append("</table>")
            
            # Si hay contenido, agregarlo como texto preformateado
            if 'contenido' in data:
                html_content.extend([
                    "<h2>Contenido</h2>",
                    "<pre>" + str(data['contenido']) + "</pre>"
                ])
            
            # Cerrar el HTML
            html_content.extend([
                "</body>",
                "</html>"
            ])
            
            # Escribir el archivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(html_content))
                
            return True
        except Exception as e:
            logger.error(f"Error al guardar HTML: {str(e)}")
            return False
    
    @classmethod
    def _flatten_data_for_tabular(cls, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Aplanar datos jerárquicos para formato tabular (CSV, Excel, etc.)
        
        Si hay una clave 'contenido', dividirla en líneas y crear una fila por línea
        con todos los metadatos duplicados. De lo contrario, crear una sola fila.
        """
        result = []
        
        # Crear un diccionario base con todos los metadatos excepto 'contenido'
        base_dict = {}
        for key, value in data.items():
            if key != 'contenido' and not isinstance(value, dict):
                base_dict[key] = value
                
        # Agregar estadísticas si existen, con prefijo
        if 'estadisticas' in data and isinstance(data['estadisticas'], dict):
            for key, value in data['estadisticas'].items():
                base_dict[f"estadistica_{key}"] = value
                
        # Si hay contenido, crear filas para cada línea
        if 'contenido' in data and isinstance(data['contenido'], str):
            lineas = data['contenido'].splitlines()
            
            # Si hay demasiadas líneas, limitar a un número razonable
            if len(lineas) > 1000:
                lineas = lineas[:1000]
                
            for i, linea in enumerate(lineas, 1):
                row = base_dict.copy()
                row['linea_num'] = i
                row['contenido'] = linea
                result.append(row)
        else:
            # Si no hay contenido, solo una fila con los metadatos
            result.append(base_dict)
            
        # Si no hay filas, crear una fila vacía con las claves
        if not result:
            result.append({key: "" for key in base_dict.keys()})
            
        return result

    @classmethod
    def read_data(cls, file_path):
        """
        Lee datos desde diferentes formatos de archivo (CSV, Excel, etc.)
        
        Args:
            file_path: Ruta al archivo a leer
            
        Returns:
            DataFrame de pandas con los datos del archivo, o None si hay error
        """
        try:
            # Convertir a Path si es string
            file_path = Path(file_path) if isinstance(file_path, str) else file_path
            
            if not file_path.exists():
                logger.error(f"Archivo no encontrado: {file_path}")
                return None
                
            # Determinar el formato basado en la extensión
            extension = file_path.suffix.lower()
            
            # Importar pandas para leer los datos
            try:
                import pandas as pd
            except ImportError:
                logger.error("Pandas no está instalado. No se pueden leer archivos.")
                print("Error: Para leer archivos, instale pandas con 'pip install pandas'")
                return None
                
            # Leer según el formato
            if extension in ['.csv', '.txt']:
                # Intentar detectar el delimitador
                with open(file_path, 'r', encoding='utf-8') as f:
                    sample = f.read(1024)
                    if '\t' in sample:
                        delimiter = '\t'
                    elif ';' in sample:
                        delimiter = ';'
                    else:
                        delimiter = ','
                
                return pd.read_csv(file_path, delimiter=delimiter)
                
            elif extension in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
                
            elif extension == '.json':
                return pd.read_json(file_path)
                
            elif extension in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import yaml
                    data = yaml.safe_load(f)
                return pd.DataFrame(data)
                
            elif extension == '.ods':
                return pd.read_excel(file_path, engine='odf')
                
            elif extension == '.tsv':
                return pd.read_csv(file_path, delimiter='\t')
                
            else:
                logger.error(f"Formato de archivo no soportado: {extension}")
                print(f"Error: El formato {extension} no está soportado")
                return None
                
        except Exception as e:
            logger.error(f"Error al leer archivo {file_path}: {str(e)}")
            print(f"Error al leer archivo: {str(e)}")
            return None
