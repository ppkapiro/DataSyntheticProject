from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import yaml
import csv
from datetime import datetime
from .logging_config import setup_logging

class ExportManager:
    """Gestor de exportación multi-formato"""
    
    def __init__(self):
        self.logger = setup_logging('exporter')
        self.exporters = {
            'json': self._export_json,
            'yaml': self._export_yaml,
            'csv': self._export_csv,
            'notify': self._export_notify
        }
        self.export_history = []

    def export_data(self, data: Dict[str, Any], 
                   format_type: str,
                   output_path: Path) -> Dict[str, Any]:
        """Exporta datos al formato especificado"""
        try:
            if exporter := self.exporters.get(format_type):
                result = exporter(data, output_path)
                self._record_export(format_type, result)
                return result
            raise ValueError(f"Formato no soportado: {format_type}")
        except Exception as e:
            self.logger.error(f"Error en exportación: {str(e)}")
            return {'error': str(e)}

    def _export_json(self, data: Dict[str, Any], 
                    output_path: Path) -> Dict[str, Any]:
        """Exporta a JSON"""
        output_file = output_path / f"export_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {'file': str(output_file), 'format': 'json'}

    def _export_yaml(self, data: Dict[str, Any], 
                    output_path: Path) -> Dict[str, Any]:
        """Exporta a YAML"""
        output_file = output_path / f"export_{datetime.now():%Y%m%d_%H%M%S}.yaml"
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)
        return {'file': str(output_file), 'format': 'yaml'}

    def _export_csv(self, data: Dict[str, Any], 
                   output_path: Path) -> Dict[str, Any]:
        """Exporta a CSV"""
        output_file = output_path / f"export_{datetime.now():%Y%m%d_%H%M%S}.csv"
        
        # Aplanar datos jerárquicos
        flat_data = self._flatten_dict(data)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
            writer.writeheader()
            writer.writerows(flat_data)
            
        return {'file': str(output_file), 'format': 'csv'}

    def _export_notify(self, data: Dict[str, Any], 
                      output_path: Path) -> Dict[str, Any]:
        """Exporta en formato Notify"""
        output_file = output_path / f"notify_{datetime.now():%Y%m%d_%H%M%S}.ntf"
        
        notify_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0'
            },
            'content': data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(notify_data, f, indent=2, ensure_ascii=False)
            
        return {'file': str(output_file), 'format': 'notify'}

    def _flatten_dict(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplana diccionario jerárquico para CSV"""
        flattened = []
        
        def flatten(d, parent_key=''):
            items = {}
            for k, v in d.items():
                key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.update(flatten(v, key))
                else:
                    items[key] = v
            return items

        if isinstance(data, list):
            for item in data:
                flattened.append(flatten(item))
        else:
            flattened.append(flatten(data))
            
        return flattened

    def _record_export(self, format_type: str, result: Dict[str, Any]) -> None:
        """Registra exportación"""
        self.export_history.append({
            'timestamp': datetime.now().isoformat(),
            'format': format_type,
            'success': 'error' not in result,
            'file': result.get('file')
        })
