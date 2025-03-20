from pathlib import Path
from typing import Dict, Any, Union, List, Optional
import pandas as pd
import json
import yaml
import re

class AdvancedContentAnalyzer:
    """Analizador avanzado de contenido para generación de plantillas"""

    def __init__(self):
        self.supported_extensions = {
            '.txt': self._analyze_text,  # Agregar soporte para TXT
            '.csv': self._analyze_csv,
            '.xlsx': self._analyze_excel,
            '.xls': self._analyze_excel,
            '.json': self._analyze_json,
            '.yaml': self._analyze_yaml,
            '.yml': self._analyze_yaml
        }

    def analyze_document(self, file_path: Path) -> Dict[str, Any]:
        """Analiza un documento y retorna su estructura"""
        if not file_path.exists():
            raise FileNotFoundError(f"No se encuentra el archivo: {file_path}")

        extension = file_path.suffix.lower()
        if extension not in self.supported_extensions:
            raise ValueError(f"Extensión no soportada: {extension}")

        return self.supported_extensions[extension](file_path)

    def suggest_template_structure(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Genera una estructura de plantilla basada en el análisis"""
        template = {
            'fields': {},
            'validation_rules': {}
        }

        for field_name, field_data in analysis_results.items():
            field_type = self._infer_field_type(field_data)
            
            template['fields'][field_name] = {
                'type': field_type,
                'description': f'Campo para {field_name.lower().replace("_", " ")}',
                'required': self._is_field_required(field_data)
            }

            template['validation_rules'][field_name] = self._generate_validation_rules(
                field_type, field_data
            )

        return template

    def _analyze_csv(self, file_path: Path) -> Dict[str, Any]:
        """Analiza archivo CSV"""
        df = pd.read_csv(file_path)
        return self._analyze_dataframe(df)

    def _analyze_excel(self, file_path: Path) -> Dict[str, Any]:
        """Analiza archivo Excel"""
        df = pd.read_excel(file_path)
        return self._analyze_dataframe(df)

    def _analyze_json(self, file_path: Path) -> Dict[str, Any]:
        """Analiza archivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self._analyze_dict(data)

    def _analyze_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Analiza archivo YAML"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return self._analyze_dict(data)

    def _analyze_text(self, file_path: Path) -> Dict[str, Any]:
        """Analiza archivo de texto plano"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar campos en el texto
        fields = {}
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Buscar patrones de campo
            if ':' in line:
                name, value = line.split(':', 1)
                name = name.strip()
                value = value.strip()
                
                fields[name] = {
                    'type': self._infer_type(value),
                    'sample': value,
                    'required': '!' in line or '*' in line
                }
            elif '=' in line:
                name, value = line.split('=', 1)
                name = name.strip()
                value = value.strip()
                
                fields[name] = {
                    'type': self._infer_type(value),
                    'sample': value,
                    'required': True
                }
                
        return fields

    def _analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza un DataFrame y extrae información relevante"""
        analysis = {}
        
        for column in df.columns:
            analysis[column] = {
                'sample_values': df[column].dropna().head(5).tolist(),
                'unique_values': df[column].nunique(),
                'null_count': df[column].isnull().sum(),
                'stats': self._get_column_stats(df[column])
            }

        return analysis

    def _analyze_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza un diccionario y extrae información relevante"""
        if isinstance(data, list) and len(data) > 0:
            data = data[0]  # Analizar primer elemento si es lista

        analysis = {}
        for key, value in data.items():
            analysis[key] = {
                'sample_values': [value],
                'type': type(value).__name__,
                'nested': isinstance(value, (dict, list))
            }

        return analysis

    def _infer_field_type(self, field_data: Dict[str, Any]) -> str:
        """Infiere el tipo de campo basado en los datos"""
        sample_values = field_data.get('sample_values', [])
        if not sample_values:
            return 'string'

        # Intentar inferir el tipo basado en las muestras
        sample = sample_values[0]
        if isinstance(sample, (int, float)):
            return 'number'
        elif isinstance(sample, bool):
            return 'boolean'
        elif isinstance(sample, (dict, list)):
            return 'object'
        else:
            # Intentar detectar fechas o tipos especiales
            str_sample = str(sample)
            if self._looks_like_date(str_sample):
                return 'date'
            elif str_sample.count(':') == 2:
                return 'time'
            return 'string'

    def _is_field_required(self, field_data: Dict[str, Any]) -> bool:
        """Determina si un campo debe ser requerido"""
        null_count = field_data.get('null_count', 0)
        return null_count == 0

    def _generate_validation_rules(self, field_type: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reglas de validación basadas en el tipo y datos del campo"""
        rules = {'type': field_type}
        
        if field_type == 'string':
            rules.update({
                'minLength': 1,
                'maxLength': 255
            })
        elif field_type == 'number':
            stats = field_data.get('stats', {})
            rules.update({
                'minimum': stats.get('min', 0),
                'maximum': stats.get('max', 999999)
            })
        elif field_type == 'date':
            rules.update({
                'format': 'YYYY-MM-DD'
            })

        return rules

    def _get_column_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Obtiene estadísticas básicas de una columna"""
        try:
            return {
                'min': series.min(),
                'max': series.max(),
                'mean': series.mean() if pd.api.types.is_numeric_dtype(series) else None,
                'unique': series.nunique()
            }
        except:
            return {}

    def _looks_like_date(self, value: str) -> bool:
        """Verifica si una cadena parece ser una fecha"""
        common_separators = ['/', '-', '.']
        parts = []
        
        for sep in common_separators:
            if sep in value:
                parts = value.split(sep)
                break
                
        return len(parts) == 3 and all(part.isdigit() for part in parts)

    def analyze_text_content(self, content: str) -> List[Dict[str, Any]]:
        """Analiza contenido de texto para identificar campos"""
        fields = []
        
        # Dividir en líneas y analizar cada una
        lines = content.split('\n')
        for line in lines:
            # Buscar definiciones de campos
            field = self._extract_field_from_line(line)
            if field:
                fields.append(field)
                
        return fields

    def _extract_field_from_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Extrae información de campo de una línea de texto"""
        patterns = [
            # Patrón tipo clase/propiedad
            (r'(?:public|private)?\s*(?:class|property)\s+(\w+)\s*:\s*(\w+)', 
             lambda m: {'name': m.group(1), 'type': m.group(2)}),
            
            # Patrón tipo variable
            (r'(?:var|let|const)\s+(\w+)\s*(?::\s*(\w+))?',
             lambda m: {'name': m.group(1), 'type': m.group(2) or 'string'}),
             
            # Patrón tipo campo/valor
            (r'["\']([\w_]+)["\']\s*:\s*["\']([\w_]+)["\']',
             lambda m: {'name': m.group(1), 'type': self._infer_type(m.group(2))})
        ]
        
        for pattern, extractor in patterns:
            match = re.search(pattern, line)
            if match:
                field_info = extractor(match)
                field_info['required'] = 'required' in line.lower() or '!' in line
                return field_info
                
        return None

    def _infer_type(self, value: str) -> str:
        """Infiere el tipo de un valor"""
        if value.lower() in ['true', 'false']:
            return 'boolean'
        elif value.isdigit():
            return 'number'
        elif self._looks_like_date(value):
            return 'date'
        return 'string'

    def _looks_like_date(self, value: str) -> bool:
        """Verifica si un valor parece una fecha"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}\.\d{2}\.\d{4}'
        ]
        return any(re.match(pattern, value) for pattern in date_patterns)
