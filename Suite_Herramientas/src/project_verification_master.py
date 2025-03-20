import subprocess
import sys
from pathlib import Path
import datetime
import logging
import platform
import os
import json
from typing import Dict, List, Tuple, Optional, Any

def setup_logging(logs_dir: Path) -> logging.Logger:
    """Configura el sistema de logging"""
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "verification_master.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class ProjectVerificationMaster:
    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent
        self.logs_dir = self.base_path / "logs"
        self.logger = setup_logging(self.logs_dir)
        
        self.modules = {
            'verify_env': {'path': 'src/verify_env.py', 'required': True},
            'project_verifier': {'path': 'src/project_verifier.py', 'required': True},
            'nlp_integration': {'path': 'src/nlp_integration.py', 'required': False},
            'task_generator': {'path': 'src/task_generator.py', 'required': False}
        }
        
        self.critical_env_vars = [
            'GOOGLE_APPLICATION_CREDENTIALS',
            'PYTHONPATH',
            'CONDA_DEFAULT_ENV',
            'VIRTUAL_ENV'
        ]

        self.git_info = self._check_git_availability()

    def _check_git_availability(self) -> bool:
        """Verifica si Git está disponible en el sistema"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def get_git_info(self) -> Dict[str, str]:
        """Obtiene información de Git si está disponible"""
        info = {'available': self.git_info}
        if not self.git_info:
            return info
            
        try:
            # Último commit
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%h - %s (%an, %ar)'],
                capture_output=True, text=True, cwd=self.base_path
            )
            if result.returncode == 0:
                info['last_commit'] = result.stdout
            
            # Estado del repositorio
            result = subprocess.run(
                ['git', 'status', '-s'],
                capture_output=True, text=True, cwd=self.base_path
            )
            if result.returncode == 0:
                info['status'] = result.stdout or "Working tree clean"
                
        except Exception as e:
            self.logger.error(f"Error obteniendo información de Git: {e}")
            
        return info

    def get_config_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de las configuraciones"""
        configs = {}
        config_dir = self.base_path / 'config'
        
        for config_file in ['nlp_config.json', 'project_config.json', 'task_rules.json']:
            file_path = config_dir / config_file
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                    configs[config_file] = {
                        'exists': True,
                        'keys': list(data.keys()),
                        'valid': True
                    }
                except Exception as e:
                    configs[config_file] = {
                        'exists': True,
                        'error': str(e),
                        'valid': False
                    }
            else:
                configs[config_file] = {'exists': False}
                
        return configs

    def run_command(self, command: List[str]) -> Tuple[bool, str]:
        """
        Ejecuta un comando y maneja errores sin detener el informe.
        
        Args:
            command: Lista con el comando y sus argumentos
            
        Returns:
            Tuple[bool, str]: (éxito, salida o mensaje de error)
        """
        module_name = Path(command[-1]).name if len(command) > 1 else "comando desconocido"
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False  # No lanzar excepciones por códigos de error
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                error_msg = (
                    f"⚠️ El módulo {module_name} terminó con código {result.returncode}\n"
                    f"Salida de error:\n{result.stderr}\n"
                    f"Salida estándar:\n{result.stdout}"
                )
                self.logger.warning(error_msg)
                return False, error_msg
                
        except FileNotFoundError:
            error_msg = f"❌ Módulo no encontrado: {module_name}"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"❌ Error inesperado ejecutando {module_name}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def read_file(self, filepath: Path) -> Tuple[bool, str]:
        """Lee un archivo y retorna su contenido"""
        try:
            return True, filepath.read_text(encoding='utf-8')
        except Exception as e:
            return False, f"Error leyendo {filepath}: {e}"

    def get_environment_info(self) -> Dict[str, str]:
        """Recopila información detallada del entorno"""
        info = {}
        
        # Python y Sistema
        info['python_version'] = sys.version
        info['platform'] = f"{platform.system()} {platform.release()}"
        
        # Conda
        success, conda_info = self.run_command(['conda', 'info'])
        if (success):
            info['conda'] = conda_info
        
        # Dependencias
        success, pip_freeze = self.run_command([sys.executable, '-m', 'pip', 'freeze'])
        if success:
            info['dependencies'] = pip_freeze
        
        return info

    def generate_report(self) -> str:
        """Genera el informe completo"""
        now = datetime.datetime.now()
        
        # Recopilar toda la información
        env_info = self.get_environment_info()
        git_info = self.get_git_info()
        config_info = self.get_config_summary()
        
        sections = [
            "# Informe Maestro de Verificación del Proyecto\n",
            self._format_header_section(now),
            "\n## 1. Estado del Entorno\n",
            self._format_environment_section(env_info),
            "\n## 2. Control de Versiones\n",
            self._format_git_section(git_info),
            "\n## 3. Configuración del Proyecto\n",
            self._format_config_section(config_info),
            "\n## 4. Variables de Entorno\n",
            self._format_env_vars_section(),
            "\n## 5. Módulos del Proyecto\n"
        ]

        # Agregar salidas de módulos
        sections.extend(self._format_modules_section())
        
        # Agregar sección de cambios
        sections.extend([
            "\n## 6. Historial de Cambios\n",
            "### Última Ejecución\n",
            f"- Fecha: {now.strftime('%Y-%m-%d %H:%M:%S')}\n",
            "- Cambios detectados:\n",
            "  - [ ] Nuevos módulos o funcionalidades\n",
            "  - [ ] Cambios en configuración\n",
            "  - [ ] Actualizaciones de dependencias\n",
            "\n### Notas Adicionales\n",
            "*(Agregar aquí notas sobre cambios importantes o observaciones)*\n"
        ])
        
        return "\n".join(sections)

    def _format_header_section(self, timestamp: datetime.datetime) -> str:
        """Formatea la sección de encabezado"""
        return "\n".join([
            f"**Fecha:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Ruta del Proyecto:** {self.base_path}",
            f"**Python:** {sys.version.split()[0]}",
            f"**Sistema:** {platform.system()} {platform.release()}\n"
        ])

    def _format_git_section(self, git_info: Dict[str, str]) -> str:
        """Formatea la sección de información de Git"""
        if not git_info.get('available'):
            return "Git no está disponible en el sistema\n"
            
        lines = []
        if 'last_commit' in git_info:
            lines.append("### Último Commit")
            lines.append(f"```\n{git_info['last_commit']}\n```\n")
            
        if 'status' in git_info:
            lines.append("### Estado del Repositorio")
            lines.append(f"```\n{git_info['status']}\n```\n")
            
        return "\n".join(lines)

    def _format_environment_section(self, env_info: Dict[str, str]) -> str:
        """Formatea la sección de información del entorno"""
        sections = []
        
        if 'python_version' in env_info:
            sections.append("### Python y Sistema")
            sections.append(f"- Python: {env_info['python_version'].split()[0]}")
            sections.append(f"- Sistema: {env_info['platform']}\n")
        
        if 'conda' in env_info:
            sections.append("### Conda")
            sections.append("```\n" + env_info['conda'] + "\n```\n")
        
        if 'dependencies' in env_info:
            sections.append("### Dependencias")
            sections.append("```\n" + env_info['dependencies'] + "\n```\n")
        
        return "\n".join(sections)

    def _format_config_section(self, config_info: Dict[str, Any]) -> str:
        """Formatea la sección de configuración del proyecto"""
        lines = []
        for config_file, info in config_info.items():
            lines.append(f"### {config_file}")
            if info['exists']:
                if info['valid']:
                    lines.append(f"- Claves: {', '.join(info['keys'])}")
                else:
                    lines.append(f"❌ Error: {info['error']}")
            else:
                lines.append("❌ No encontrado")
            lines.append("")
        return "\n".join(lines)

    def _format_env_vars_section(self) -> str:
        """Formatea la sección de variables de entorno"""
        lines = []
        for var in self.critical_env_vars:
            value = os.environ.get(var)
            if value:
                # Ocultar valores sensibles
                if 'CREDENTIALS' in var or 'KEY' in var:
                    lines.append(f"✓ **{var}**: [VALOR OCULTO]")
                else:
                    lines.append(f"✓ **{var}**: {value}")
            else:
                lines.append(f"❌ **{var}**: No configurada")
        return "\n".join(lines) + "\n"

    def _format_modules_section(self) -> List[str]:
        """Formatea la sección de módulos del proyecto"""
        sections = []
        for module_name, config in self.modules.items():
            sections.append(f"\n### {module_name.replace('_', ' ').title()}\n")
            success, output = self.run_command(
                [sys.executable, str(self.base_path / config['path'])]
            )
            
            if success:
                sections.append("✓ Módulo ejecutado correctamente\n")
                sections.append(f"```\n{output}\n```\n")
            else:
                status = "❌" if config['required'] else "⚠️"
                sections.append(f"{status} {output}\n")
                if config['required']:
                    self.logger.error(f"Módulo requerido {module_name} falló")
                else:
                    self.logger.warning(f"Módulo opcional {module_name} falló")
        
        return sections

    def save_report(self, content: str) -> None:
        """Guarda el informe en el archivo"""
        report_path = self.logs_dir / "project_verification_master.md"
        self.logs_dir.mkdir(exist_ok=True)
        
        try:
            report_path.write_text(content, encoding='utf-8')
            self.logger.info(f"Informe maestro guardado en: {report_path}")
        except Exception as e:
            self.logger.error(f"Error guardando el informe: {e}")
            raise

def main():
    try:
        verifier = ProjectVerificationMaster()
        report_content = verifier.generate_report()
        verifier.save_report(report_content)
        print("Informe de verificación maestro generado exitosamente")
    except Exception as e:
        print(f"Error generando el informe: {e}")
        raise

if __name__ == "__main__":
    main()
