from pathlib import Path
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import json
import yaml
from tabulate import tabulate
import numpy as np

class AnalysisManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def analyze_structure(self, 
                         module: str, 
                         filename: str, 
                         output_format: str = 'json') -> Optional[Path]:
        """
        Analiza la estructura de un archivo y genera reporte
        """
        try:
            input_path = Path(self.config['paths']['base_dir']) / module / 'input' / filename
            analysis_path = Path(self.config['paths']['analysis_dir']) / module
            
            # Crear directorios si no existen
            analysis_path.mkdir(parents=True, exist_ok=True)
            
            # Realizar análisis y generar reporte
            report = self._generate_analysis_report(input_path)
            
            # Guardar reporte
            output_file = analysis_path / f"analysis_{Path(filename).stem}.{output_format}"
            self._save_report(report, output_file, output_format)
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error analizando {filename}: {str(e)}")
            return None

    def _generate_analysis_report(self, file_path: Path) -> Dict[str, Any]:
        """
        Implementa la lógica de análisis específica
        """
        try:
            df = pd.read_csv(file_path) if file_path.suffix == '.csv' else pd.read_excel(file_path)
            
            report = {
                "filename": file_path.name,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns_analysis": {},
                "null_analysis": {},
                "sample_data": {}
            }
            
            for column in df.columns:
                col_data = df[column]
                col_analysis = {
                    "dtype": str(col_data.dtype),
                    "unique_values": len(col_data.unique()),
                    "null_count": col_data.isnull().sum(),
                    "null_percentage": (col_data.isnull().sum() / len(df)) * 100,
                }
                
                # Análisis específico por tipo de dato
                if pd.api.types.is_numeric_dtype(col_data):
                    col_analysis.update({
                        "min": float(col_data.min()) if not col_data.empty else None,
                        "max": float(col_data.max()) if not col_data.empty else None,
                        "mean": float(col_data.mean()) if not col_data.empty else None,
                        "std": float(col_data.std()) if not col_data.empty else None
                    })
                
                report["columns_analysis"][column] = col_analysis
                report["sample_data"][column] = col_data.head(5).tolist()
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error en el análisis: {str(e)}")
            raise

    def _save_report(self, report: Dict[str, Any], output_file: Path, format: str):
        """
        Guarda el reporte en el formato especificado
        """
        try:
            if format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
            
            elif format == 'html':
                html_content = self._generate_html_report(report)
                with open(output_file.with_suffix('.html'), 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            elif format == 'xlsx':
                self._save_excel_report(report, output_file.with_suffix('.xlsx'))
            
            self.logger.info(f"Reporte guardado en: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error guardando reporte: {str(e)}")
            raise

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """
        Genera un reporte HTML formateado
        """
        html = f"""
        <html>
        <head>
            <title>Análisis de Estructura - {report['filename']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .section {{ margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>Análisis de Estructura: {report['filename']}</h1>
            <div class="section">
                <h2>Información General</h2>
                <p>Total de filas: {report['total_rows']}</p>
                <p>Total de columnas: {report['total_columns']}</p>
            </div>
            <div class="section">
                <h2>Análisis por Columna</h2>
                {self._generate_columns_table(report['columns_analysis'])}
            </div>
        </body>
        </html>
        """
        return html

    def _save_excel_report(self, report: Dict[str, Any], output_file: Path):
        """
        Guarda el reporte en formato Excel
        """
        with pd.ExcelWriter(output_file) as writer:
            # Información general
            pd.DataFrame({
                'Métrica': ['Total Filas', 'Total Columnas'],
                'Valor': [report['total_rows'], report['total_columns']]
            }).to_excel(writer, sheet_name='General', index=False)
            
            # Análisis por columna
            columns_df = pd.DataFrame.from_dict(report['columns_analysis'], orient='index')
            columns_df.to_excel(writer, sheet_name='Análisis por Columna')
            
            # Datos de ejemplo
            samples_df = pd.DataFrame(report['sample_data'])
            samples_df.to_excel(writer, sheet_name='Datos de Ejemplo', index=False)
