from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
from .logging_config import setup_logging
from .content_validator import ContentValidator

class MappingResultManager:
    """Gestor de resultados del mapeo PDF-Plantilla"""

    def __init__(self):
        self.logger = setup_logging('mapping_results')
        self.validator = ContentValidator()
        self.current_results = {}
        self.results_history = []

    def process_mapping_result(self, mapping_data: Dict[str, Any], 
                             template: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y valida el resultado del mapeo"""
        self.logger.info("Procesando resultado de mapeo")
        
        try:
            # Validar resultado
            validation = self.validator.validate_content(mapping_data, template)
            
            # Generar resultado procesado
            result = {
                'mapping_data': mapping_data,
                'validation': validation,
                'metadata': {
                    'template_name': template.get('nombre_archivo'),
                    'mapping_date': datetime.now().isoformat(),
                    'fields_mapped': len(mapping_data.get('fields', {})),
                    'validation_status': 'valid' if validation['is_valid'] else 'invalid'
                }
            }

            # Almacenar resultado
            self._store_result(result)
            
            return result

        except Exception as e:
            self.logger.error(f"Error procesando resultado: {str(e)}")
            return {'error': str(e)}

    def _store_result(self, result: Dict[str, Any]) -> None:
        """Almacena el resultado del mapeo"""
        result_id = f"mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_results[result_id] = result
        self.results_history.append({
            'id': result_id,
            'template': result['metadata']['template_name'],
            'status': result['metadata']['validation_status'],
            'timestamp': result['metadata']['mapping_date']
        })

    def export_result(self, result_id: str, 
                     output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Exporta un resultado específico"""
        if result := self.current_results.get(result_id):
            if output_path:
                self._save_result(result, output_path)
            return result
            
        return {'error': 'Resultado no encontrado'}

    def _save_result(self, result: Dict[str, Any], path: Path) -> None:
        """Guarda el resultado en disco"""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    def get_mapping_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de mapeos"""
        total = len(self.results_history)
        if not total:
            return {'status': 'No hay resultados registrados'}

        successful = sum(1 for r in self.results_history 
                        if r['status'] == 'valid')
        
        return {
            'total_mappings': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': round((successful / total) * 100, 2),
            'latest_mapping': self.results_history[-1] if self.results_history else None
        }

    def get_field_mapping_trends(self) -> Dict[str, Any]:
        """Analiza tendencias en el mapeo de campos"""
        field_stats = {}
        
        for result_id, result in self.current_results.items():
            fields = result.get('mapping_data', {}).get('fields', {})
            
            for field_name, field_data in fields.items():
                if field_name not in field_stats:
                    field_stats[field_name] = {
                        'total_appearances': 0,
                        'successful_mappings': 0,
                        'average_confidence': 0.0
                    }
                    
                stats = field_stats[field_name]
                stats['total_appearances'] += 1
                
                if field_data.get('validated', False):
                    stats['successful_mappings'] += 1
                    
                stats['average_confidence'] = (
                    (stats['average_confidence'] * (stats['total_appearances'] - 1) +
                     field_data.get('confidence', 0)) / stats['total_appearances']
                )

        return {
            'field_statistics': field_stats,
            'analysis_date': datetime.now().isoformat()
        }
