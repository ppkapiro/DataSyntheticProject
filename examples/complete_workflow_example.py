from pathlib import Path
import asyncio
from rich.console import Console
from utils.template_management.system_integrator import SystemIntegrator
from utils.template_management.data_normalizer import DataNormalizer
from utils.template_management.pdf_builder import PDFBuilder
from utils.template_management.export_manager import ExportManager

async def main():
    # Inicializar componentes
    console = Console()
    integrator = SystemIntegrator()
    normalizer = DataNormalizer()
    pdf_builder = PDFBuilder()
    exporter = ExportManager()

    # Configurar rutas
    pdf_path = Path('samples/historial_medico.pdf')
    output_path = Path('output')
    output_path.mkdir(exist_ok=True)

    try:
        with console.status("[bold green]Procesando documento..."):
            # 1. Procesar documento PDF
            console.print("\n1. Analizando PDF...")
            result = await integrator.process_document(
                pdf_path=pdf_path,
                template_id="template_001"
            )

            if 'error' in result:
                raise Exception(f"Error en procesamiento: {result['error']}")

            # 2. Normalizar datos
            console.print("2. Normalizando datos...")
            normalized_data = normalizer.normalize_document(
                data=result['document']['reconciled_data'],
                field_types={
                    'nombre': 'text',
                    'fecha': 'date',
                    'edad': 'number'
                }
            )

            # 3. Validar y exportar
            console.print("3. Validando y exportando...")
            if result['validation']['is_valid']:
                # Exportar en múltiples formatos
                await asyncio.gather(
                    exporter.export_data(normalized_data, 'json', output_path),
                    exporter.export_data(normalized_data, 'notify', output_path)
                )

            # 4. Mostrar resultado
            console.print("\n[bold]Resultado del Procesamiento:[/bold]")
            console.print(f"Estado: {'✓' if result['validation']['is_valid'] else '✗'}")
            console.print(f"Confianza: {result['metadata']['confidence']*100:.1f}%")
            
            if warnings := result['validation'].get('warnings', []):
                console.print("\n[yellow]Advertencias:[/yellow]")
                for warning in warnings:
                    console.print(f"- {warning}")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        return

    console.print("\n[bold green]¡Procesamiento completado![/bold green]")

if __name__ == "__main__":
    # Ejemplo de uso:
    # python complete_workflow_example.py
    asyncio.run(main())
