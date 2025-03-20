import pytest
import asyncio
from pathlib import Path
from core.import_consolidator import ImportConsolidator
from utils.template_management.system_integrator import SystemIntegrator

class TestIntegration:
    @pytest.fixture
    async def setup(self):
        self.integrator = SystemIntegrator()
        self.consolidator = ImportConsolidator()
        yield
        # Limpieza después de las pruebas
        await self.integrator.cleanup()

    @pytest.mark.asyncio
    async def test_document_processing(self, setup):
        try:
            result = await self.integrator.process_document(
                pdf_path=Path("test_data/sample.pdf"),
                template_id="template_001"
            )
            assert result['validation']['is_valid']
            assert result['metadata']['confidence'] > 0.8
        except Exception as e:
            pytest.fail(f"Error en el procesamiento del documento: {str(e)}")

    @pytest.mark.asyncio
    async def test_patient_consolidation(self, setup):
        try:
            status = await self.consolidator.process_patient(
                patient_id="TEST001",
                clinic_code="CLINIC001"
            )
            assert status['success']
        except Exception as e:
            pytest.fail(f"Error en la consolidación de paciente: {str(e)}")

    @pytest.mark.asyncio
    async def test_step_by_step_processing(self, setup):
        try:
            # Paso 1: Inicialización
            await self.integrator.initialize_processing()
            
            # Paso 2: Carga de documento
            doc_loaded = await self.integrator.load_document("test_data/sample.pdf")
            assert doc_loaded
            
            # Paso 3: Procesamiento
            processing_result = await self.integrator.process_loaded_document()
            assert processing_result['status'] == 'success'
            
            # Paso 4: Validación
            validation = await self.integrator.validate_results(processing_result)
            assert validation['is_valid']
            
        except Exception as e:
            pytest.fail(f"Error en el procesamiento paso a paso: {str(e)}")

    @pytest.mark.asyncio
    async def test_error_handling(self, setup):
        with pytest.raises(FileNotFoundError):
            await self.integrator.process_document(
                pdf_path=Path("nonexistent.pdf"),
                template_id="template_001"
            )