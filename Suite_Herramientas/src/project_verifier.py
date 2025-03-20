import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import datetime
import logging
import importlib.util
import subprocess
from dotenv import load_dotenv

def setup_logging(logs_dir: Path) -> logging.Logger:
    """Configura el sistema de logging"""
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "project_verifier.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class ProjectVerifier:
    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent
        self.logs_dir = self.base_path / "logs"
        self.logger = setup_logging(self.logs_dir)
        
        # Cargar variables de entorno
        load_dotenv(self.base_path / 'config' / '.env')
        
        # Definir estructura requerida
        self._init_requirements()

    def _init_requirements(self):
        """Inicializa los requisitos del proyecto"""
        self.required_structure = {
            'Docs': ['informe_suite_herramientas.md', 'project_status_report.md'],
            'src': ['nlp_integration.py', 'verify_env.py', 'report_generator.py', 'project_verifier.py'],
            'config': ['nlp_config.json', 'project_config.json', 'task_rules.json', '.env'],
            'tests': ['test_nlp_integration.py'],
            'logs': ['project_verifier.log', 'nlp_analysis.log'],
            'data': []
        }
        
        # Agregar definición de required_modules
        self.required_modules = [
            ('verify_env.py', 'Verificación de entorno'),
            ('nlp_integration.py', 'Integración NLP'),
            ('report_generator.py', 'Generador de informes'),
            ('project_verifier.py', 'Verificador del Proyecto')
        ]
        
        self.config_requirements = {
            "nlp_config.json": ["credentials_path", "cache_size", "language", "features", "translation", "logging"],
            "project_config.json": ["project_name", "version", "structure"],
            "task_rules.json": ["keywords", "default_due_days", "priority_levels"]
        }
        
        self.required_env_vars = [
            "GOOGLE_APPLICATION_CREDENTIALS",
            "PYTHONPATH"
        ]

    def verify_structure(self) -> Dict:
        """Verifica la estructura del proyecto y retorna resultados detallados"""
        results = {'folders': [], 'files': []}
        for folder, files in self.required_structure.items():
            folder_path = self.base_path / folder
            folder_exists = folder_path.exists()
            results['folders'].append((folder, folder_exists))
            
            if folder_exists:
                for file in files:
                    file_path = folder_path / file
                    results['files'].append((folder, file, file_path.exists()))
        
        return results

    def verify_modules(self) -> List[Tuple[str, bool, str]]:
        """Verifica la existencia y estado de los módulos principales"""
        results = []
        src_path = self.base_path / 'src'
        
        for module_file, description in self.required_modules:
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
                        results.append((module_file, True, f"Módulo {description} cargado correctamente"))
                    else:
                        results.append((module_file, False, f"No se pudo cargar el módulo {description}"))
                except Exception as e:
                    results.append((module_file, False, f"Error al cargar {description}: {str(e)}"))
            else:
                results.append((module_file, False, f"No se encuentra el módulo {description}"))
        
        return results

    def verify_configuration(self) -> Dict:
        """Verifica la configuración y retorna resultados detallados"""
        results = {'configs': []}
        config_path = self.base_path / 'config'
        
        if not config_path.exists():
            return results
            
        for config_file, required_keys in self.config_requirements.items():
            file_path = config_path / config_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    present_keys = [key for key in required_keys if key in data]
                    missing_keys = [key for key in required_keys if key not in data]
                    results['configs'].append({
                        'file': config_file,
                        'exists': True,
                        'valid_json': True,
                        'present_keys': present_keys,
                        'missing_keys': missing_keys
                    })
                except Exception as e:
                    results['configs'].append({
                        'file': config_file,
                        'exists': True,
                        'valid_json': False,
                        'error': str(e)
                    })
            else:
                results['configs'].append({
                    'file': config_file,
                    'exists': False
                })
                
        return results

    def run_verify_env(self) -> Tuple[bool, str]:
        """Ejecuta verify_env.py y captura su salida"""
        try:
            result = subprocess.run(
                [sys.executable, self.base_path / 'src' / 'verify_env.py'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, f"Error al ejecutar verify_env.py: {str(e)}"

    def verify_env_vars(self) -> Dict[str, bool]:
        """Verifica las variables de entorno requeridas"""
        results = {}
        for var in self.required_env_vars:
            value = os.environ.get(var)
            if value:
                self.logger.info(f"Variable de entorno {var} configurada: {value}")
                results[var] = True
            else:
                self.logger.warning(f"Variable de entorno {var} no encontrada")
                results[var] = False
        return results

    def _format_markdown_report(self, results: Dict) -> str:
        """Formatea los resultados en Markdown con más detalles"""
        now = datetime.datetime.now()
        
        sections = [
            "# Informe de Verificación del Proyecto\n",
            f"**Fecha:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Ruta del Proyecto:** {self.base_path}\n\n",
            
            "## 1. Estructura del Proyecto\n",
            self._format_structure_section(results['structure']),
            
            "\n## 2. Módulos del Proyecto\n",
            self._format_modules_section(results['modules']),
            
            "\n## 3. Configuración\n",
            self._format_config_section(results['config']),
            
            "\n## 4. Variables de Entorno\n",
            self._format_env_vars_section(results['env_vars']),
            
            "\n## 5. Verificación del Entorno\n",
            self._format_env_verification_section(results['env_verification'])
        ]
        
        return "\n".join(sections)

    def _format_structure_section(self, structure_results: Dict) -> str:
        """Formatea la sección de estructura del proyecto"""
        lines = []
        
        # Carpetas
        for folder, exists in structure_results['folders']:
            status = "✓" if exists else "❌"
            lines.append(f"{status} **{folder}/**")
        
        lines.append("")  # Línea en blanco
        
        # Archivos
        for folder, file, exists in structure_results['files']:
            status = "  ✓" if exists else "  ❌"
            lines.append(f"{status} {folder}/{file}")
            
        return "\n".join(lines)

    def _format_modules_section(self, modules_results: List[Tuple[str, bool, str]]) -> str:
        """Formatea la sección de módulos"""
        lines = []
        for module, success, message in modules_results:
            status = "✓" if success else "❌"
            lines.append(f"{status} {message}")
        return "\n".join(lines)

    def _format_config_section(self, config_results: Dict) -> str:
        """Formatea la sección de configuración"""
        lines = []
        for config in config_results['configs']:
            if not config['exists']:
                lines.append(f"❌ Archivo no encontrado: {config['file']}")
                continue
                
            if not config.get('valid_json', False):
                lines.append(f"❌ Error en {config['file']}: {config.get('error', 'Formato JSON inválido')}")
                continue
                
            lines.append(f"✓ **{config['file']}**")
            if config.get('present_keys'):
                lines.append("  Claves encontradas:")
                for key in config['present_keys']:
                    lines.append(f"    ✓ {key}")
            
            if config.get('missing_keys'):
                lines.append("  Claves faltantes:")
                for key in config['missing_keys']:
                    lines.append(f"    ❌ {key}")
                    
        return "\n".join(lines)

    def _format_env_vars_section(self, env_vars_results: Dict[str, bool]) -> str:
        """Formatea la sección de variables de entorno"""
        lines = []
        for var, exists in env_vars_results.items():
            status = "✓" if exists else "❌"
            value = os.environ.get(var, "no configurada")
            if exists:
                lines.append(f"{status} **{var}**: {value}")
            else:
                lines.append(f"{status} **{var}** no configurada")
        return "\n".join(lines)

    def _format_env_verification_section(self, env_verification: Tuple[bool, str]) -> str:
        """Formatea la sección de verificación del entorno"""
        success, output = env_verification
        status = "✓" if success else "❌"
        return f"{status} Resultado de verify_env.py:\n```\n{output}\n```"

    def generate_report(self) -> None:
        """Genera el informe completo de verificación"""
        try:
            # Recopilar resultados
            results = {
                'structure': self.verify_structure(),
                'modules': self.verify_modules(),
                'config': self.verify_configuration(),
                'env_vars': self.verify_env_vars(),
                'env_verification': self.run_verify_env()
            }
            
            # Generar informe
            report_content = self._format_markdown_report(results)
            
            # Guardar en logs/verification_report.md
            report_path = self.logs_dir / "verification_report.md"
            self.logs_dir.mkdir(exist_ok=True)
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
                
            self.logger.info(f"Informe de verificación generado en: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Error generando informe: {e}")
            raise

def main():
    verifier = ProjectVerifier()
    verifier.generate_report()

if __name__ == "__main__":
    main()
