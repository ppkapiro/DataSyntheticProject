import os
from pathlib import Path
import json
import datetime
import logging
from typing import Dict, List, Optional
import importlib.util
import sys

# Asegurar que existe el directorio de logs
def setup_logging():
    """Configura el sistema de logging y asegura que existe el directorio"""
    base_path = Path(__file__).parent.parent
    logs_dir = base_path / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / "report_generator.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Configurar logging
logger = setup_logging()

class ProjectReportGenerator:
    """Generador de informes del estado del proyecto"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(__file__).parent.parent
        self.project_structure = {
            'Docs': 'Documentación del proyecto',
            'src': 'Código fuente',
            'config': 'Archivos de configuración',
            'tests': 'Pruebas unitarias',
            'logs': 'Archivos de registro'
        }

    def check_structure(self) -> str:
        """Verifica la estructura del proyecto"""
        report = "## Estructura del Proyecto\n\n"
        for folder, description in self.project_structure.items():
            folder_path = self.base_path / folder
            status = "✓" if folder_path.exists() else "❌"
            report += f"{status} **{folder}**: {description}\n"
            if folder_path.exists():
                files = list(folder_path.glob('*.py')) + list(folder_path.glob('*.json'))
                if files:
                    report += "   - Archivos principales:\n"
                    for file in files[:5]:  # Limitar a 5 archivos
                        report += f"     - {file.name}\n"
        return report + "\n"

    def get_module_status(self) -> str:
        """Analiza el estado de los módulos implementados"""
        report = "## Módulos Implementados\n\n"
        
        # Verificar módulos principales
        modules_to_check = {
            'nlp_integration.py': 'Integración con Google Cloud NLP',
            'verify_env.py': 'Verificación de Entorno',
            'credentials_manager.py': 'Gestión de Credenciales'
        }
        
        src_path = self.base_path / 'src'
        for module_file, description in modules_to_check.items():
            module_path = src_path / module_file
            if module_path.exists():
                try:
                    spec = importlib.util.spec_from_file_location(
                        module_file.replace('.py', ''), 
                        module_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[spec.name] = module
                        spec.loader.exec_module(module)
                        report += f"✓ **{description}**: Implementado y funcional\n"
                    else:
                        report += f"⚠️ **{description}**: No se pudo cargar\n"
                except Exception as e:
                    report += f"❌ **{description}**: Error al cargar - {str(e)}\n"
            else:
                report += f"❌ **{description}**: No implementado\n"
        
        return report + "\n"

    def get_test_status(self) -> str:
        """Analiza el estado de las pruebas"""
        report = "## Estado de Pruebas\n\n"
        tests_path = self.base_path / 'tests'
        
        if not tests_path.exists():
            return report + "❌ Carpeta de pruebas no encontrada\n\n"
            
        test_files = list(tests_path.glob('test_*.py'))
        if not test_files:
            return report + "⚠️ No se encontraron archivos de prueba\n\n"
            
        report += f"✓ **{len(test_files)} archivos de prueba encontrados**\n\n"
        for test_file in test_files:
            report += f"- {test_file.name}\n"
            
        return report + "\n"

    def get_config_status(self) -> str:
        """Analiza la configuración del proyecto"""
        report = "## Configuración\n\n"
        config_path = self.base_path / 'config'
        
        if not config_path.exists():
            return report + "❌ Carpeta de configuración no encontrada\n\n"
            
        config_files = list(config_path.glob('*.json'))
        for config_file in config_files:
            try:
                with open(config_file) as f:
                    config = json.load(f)
                report += f"✓ **{config_file.name}**:\n"
                if isinstance(config, dict):
                    for key in config.keys():
                        report += f"   - {key}\n"
            except Exception as e:
                report += f"❌ Error en {config_file.name}: {str(e)}\n"
                
        return report + "\n"

    def generate_report(self) -> None:
        """Genera el informe completo"""
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_content = [
                f"# Informe del Estado del Proyecto\n\n**Fecha:** {now}\n",
                self.check_structure(),
                self.get_module_status(),
                self.get_test_status(),
                self.get_config_status()
            ]
            
            output_file = self.base_path / "Docs" / "project_status_report.md"
            output_file.parent.mkdir(exist_ok=True)
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(report_content))
                
            logger.info(f"Informe generado exitosamente en: {output_file}")
            
        except Exception as e:
            logger.error(f"Error al generar el informe: {e}")
            raise

def main():
    generator = ProjectReportGenerator()
    generator.generate_report()

if __name__ == "__main__":
    main()
