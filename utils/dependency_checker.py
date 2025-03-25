import importlib
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyChecker:
    """Verificador de dependencias del sistema"""
    
    REQUIRED_PACKAGES = {
        'Core': [
            ('pandas', 'pandas'),
            ('numpy', 'numpy'),
            ('yaml', 'pyyaml'),
        ],
        'PDF': [
            ('pdfminer.six', 'pdfminer.six'),
            ('PyPDF2', 'PyPDF2'),
            ('pdf2image', 'pdf2image'),
            ('pytesseract', 'pytesseract'),
        ],
        'Image': [
            ('PIL', 'Pillow'),
        ],
        'Data': [
            ('openpyxl', 'openpyxl'),
            ('odf', 'odfpy'),
        ]
    }

    @classmethod
    def check_dependencies(cls) -> Tuple[bool, Dict[str, List[str]]]:
        """Verifica todas las dependencias del sistema"""
        missing: Dict[str, List[str]] = {}
        all_ok = True

        for category, packages in cls.REQUIRED_PACKAGES.items():
            missing_in_category = []
            for import_name, install_name in packages:
                if not cls._check_package(import_name):
                    missing_in_category.append(install_name)
                    all_ok = False
            if missing_in_category:
                missing[category] = missing_in_category

        if not all_ok:
            cls._show_installation_instructions(missing)

        return all_ok, missing

    @staticmethod
    def _check_package(package_name: str) -> bool:
        """Verifica si un paquete puede ser importado"""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False

    @staticmethod
    def _show_installation_instructions(missing: Dict[str, List[str]]) -> None:
        """Muestra instrucciones de instalación para paquetes faltantes"""
        print("\n❌ Faltan dependencias requeridas.")
        print("\nPara instalar usando conda:")
        print("conda env update -f environment.yml")
        
        print("\nO instala las dependencias faltantes manualmente:")
        for category, packages in missing.items():
            print(f"\n{category}:")
            for package in packages:
                print(f"conda install {package}")
                print(f"# o pip install {package}")

if __name__ == "__main__":
    print("Verificando dependencias del sistema...")
    all_ok, missing_deps = DependencyChecker.check_dependencies()
    
    if all_ok:
        print("\n✅ Todas las dependencias están instaladas correctamente.")
    else:
        print("\n⚠️ El sistema puede no funcionar correctamente hasta que se instalen todas las dependencias.")
