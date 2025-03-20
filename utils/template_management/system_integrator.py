from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import asyncio
from .pdf_builder import PDFBuilder
from .data_transformer import DataTransformer
from .pattern_analyzer import PatternAnalyzer
from .data_reconciliator import DataReconciliator
from .business_rules_validator import BusinessRulesValidator
from .smart_operation_cache import SmartOperationCache
from .export_manager import ExportManager
from .logging_config import setup_logging

class SystemIntegrator:
    """Integrador principal del sistema"""

    def __init__(self):
        self.logger = setup_logging('system_integrator')
        # Inicializar componentes
        self.pdf_builder = PDFBuilder()
        self.transformer = DataTransformer()
        self.pattern_analyzer = PatternAnalyzer()
        self.reconciliator = DataReconciliator()
        self.validator = BusinessRulesValidator()
        self.cache = SmartOperationCache()
        self.exporter = ExportManager()

    async def process_document(self, pdf_path: Path, 
                             template_id: str) -> Dict[str, Any]:
        """Procesa un documento completo"""
        try:
            # 1. Construir estructura PDF
            pdf_structure = await self._build_pdf_structure(pdf_path)
            if 'error' in pdf_structure:
                return pdf_structure

            # 2. Analizar patrones
            patterns = self.pattern_analyzer.analyze_content(pdf_structure)
            
            # 3. Transformar datos
            transformed_data = self._transform_data(patterns)
            
            # 4. Reconciliar con plantilla
            reconciled = self.reconciliator.reconcile_data(
                transformed_data,
                {'template_id': template_id}
            )

            # 5. Validar reglas de negocio
            validation = self.validator.validate_data(reconciled['reconciled_data'])
            
            # 6. Generar resultado final
            result = self._generate_result(
                pdf_structure,
                patterns,
                reconciled,
                validation
            )

            # 7. Exportar si es válido
            if validation['valid']:
                await self._export_result(result)

            return result

        except Exception as e:
            self.logger.error(f"Error en procesamiento: {str(e)}")
            return {'error': str(e)}

    async def _build_pdf_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """Construye estructura del PDF de forma asíncrona"""
        cache_key = f"pdf_structure_{pdf_path.stem}"
        
        # Verificar caché
        if cached := self.cache.get_operation_result(cache_key, {'path': str(pdf_path)}):
            return cached

        # Construir estructura
        structure = self.pdf_builder.build_structure(pdf_path)
        
        # Guardar en caché
        if 'error' not in structure:
            self.cache.store_operation_result(cache_key, {'path': str(pdf_path)}, structure)
        
        return structure

    def _transform_data(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma datos según patrones detectados"""
        transformed = {}
        
        for field_name, pattern_info in patterns.get('patterns', {}).items():
            if pattern_info['confidence'] > 0.8:
                transformed[field_name] = self.transformer.transform_field(
                    pattern_info['value'],
                    'text',
                    pattern_info['suggested_type']
                )

        return transformed

    def _generate_result(self, pdf_structure: Dict[str, Any],
                        patterns: Dict[str, Any],
                        reconciled: Dict[str, Any],
                        validation: Dict[str, Any]) -> Dict[str, Any]:
        """Genera resultado final del procesamiento"""
        return {
            'document': {
                'structure': pdf_structure,
                'patterns': patterns,
                'reconciled_data': reconciled['reconciled_data']
            },
            'validation': {
                'is_valid': validation['valid'],
                'errors': validation.get('errors', []),
                'warnings': validation.get('warnings', [])
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'confidence': reconciled['metadata']['confidence'],
                'processing_time': self._calculate_processing_time()
            }
        }

    async def _export_result(self, result: Dict[str, Any]) -> None:
        """Exporta resultado en diferentes formatos"""
        export_path = Path('exports')
        
        # Exportar como JSON
        await asyncio.gather(
            self.exporter.export_data(result, 'json', export_path),
            self.exporter.export_data(result, 'notify', export_path)
        )

    def _calculate_processing_time(self) -> float:
        """Calcula tiempo de procesamiento"""
        # Implementar cálculo real de tiempo
        return 0.0

    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del sistema"""
        return {
            'components': {
                'pdf_builder': 'active',
                'transformer': 'active',
                'analyzer': 'active',
                'reconciliator': 'active',
                'validator': 'active',
                'cache': 'active',
                'exporter': 'active'
            },
            'cache_status': {
                'size': len(self.cache.cache),
                'hit_rate': self._calculate_cache_hit_rate()
            },
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_cache_hit_rate(self) -> float:
        """Calcula tasa de aciertos del caché"""
        # Implementar cálculo real
        return 0.0
