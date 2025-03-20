from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .logging_config import setup_logging
from .data_transformer import DataTransformer
from .mapping_quality_detector import MappingQualityDetector

class FieldReconciliation:
    """Sistema de reconciliación entre campos PDF y plantillas"""

    def __init__(self):
        self.logger = setup_logging('field_reconciliation')
        self.transformer = DataTransformer()
        self.quality_detector = MappingQualityDetector()
        self.reconciliation_history = []

    def reconcile_fields(self, pdf_fields: Dict[str, Any], 
                        template_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcilia campos entre PDF y plantilla"""
        self.logger.info("Iniciando reconciliación de campos")
        
        try:
            # Identificar campos coincidentes y no coincidentes
            matching_result = self._find_matching_fields(pdf_fields, template_fields)
            
            # Procesar coincidencias
            reconciled_fields = self._process_matches(
                matching_result['matches'],
                template_fields
            )

            # Intentar resolver campos no coincidentes
            resolved_fields = self._resolve_unmatched_fields(
                matching_result['unmatched'],
                template_fields
            )

            # Combinar resultados
            reconciliation_result = {
                'reconciled_fields': {**reconciled_fields, **resolved_fields},
                'stats': self._calculate_reconciliation_stats(
                    reconciled_fields,
                    resolved_fields,
                    template_fields
                ),
                'quality': self._assess_reconciliation_quality(
                    reconciled_fields,
                    template_fields
                )
            }

            # Registrar resultado
            self._register_reconciliation(reconciliation_result)
            
            return reconciliation_result

        except Exception as e:
            self.logger.error(f"Error en reconciliación: {str(e)}")
            return {'error': str(e)}

    def _find_matching_fields(self, pdf_fields: Dict[str, Any], 
                            template_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Encuentra campos coincidentes y no coincidentes"""
        matches = {}
        unmatched = {}

        for field_name, field_info in template_fields.items():
            if match := self._find_best_match(field_name, field_info, pdf_fields):
                matches[field_name] = match
            else:
                unmatched[field_name] = field_info

        return {
            'matches': matches,
            'unmatched': unmatched
        }

    def _find_best_match(self, field_name: str, field_info: Dict[str, Any], 
                        pdf_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Encuentra la mejor coincidencia para un campo"""
        best_match = None
        highest_score = 0.0

        for pdf_name, pdf_info in pdf_fields.items():
            score = self._calculate_match_score(
                field_name, field_info,
                pdf_name, pdf_info
            )
            
            if score > highest_score and score > 0.7:  # Umbral mínimo
                highest_score = score
                best_match = {
                    'pdf_field': pdf_name,
                    'match_score': score,
                    'pdf_info': pdf_info
                }

        return best_match

    def _process_matches(self, matches: Dict[str, Any], 
                        template_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa los campos coincidentes"""
        processed = {}
        
        for field_name, match_info in matches.items():
            processed[field_name] = {
                'value': match_info['pdf_info'].get('value'),
                'confidence': match_info['match_score'],
                'source': match_info['pdf_field'],
                'type': template_fields[field_name].get('type'),
                'validated': True
            }

        return processed

    def _resolve_unmatched_fields(self, unmatched: Dict[str, Any], 
                                template_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta resolver campos no coincidentes"""
        resolved = {}
        
        for field_name, field_info in unmatched.items():
            # Intentar inferir valor
            if inferred := self._infer_field_value(field_name, field_info):
                resolved[field_name] = {
                    'value': inferred['value'],
                    'confidence': inferred['confidence'],
                    'source': 'inferred',
                    'type': field_info.get('type'),
                    'validated': False
                }
            # Campo requerido sin valor
            elif field_info.get('required', False):
                self.logger.warning(f"Campo requerido no resuelto: {field_name}")
                resolved[field_name] = {
                    'value': None,
                    'confidence': 0.0,
                    'source': 'missing',
                    'type': field_info.get('type'),
                    'validated': False
                }

        return resolved

    def _infer_field_value(self, field_name: str, 
                          field_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Intenta inferir el valor de un campo"""
        # Implementar lógica de inferencia específica del dominio
        return None

    def _register_reconciliation(self, result: Dict[str, Any]) -> None:
        """Registra un resultado de reconciliación"""
        self.reconciliation_history.append({
            'timestamp': datetime.now().isoformat(),
            'stats': result['stats'],
            'quality': result['quality']
        })
