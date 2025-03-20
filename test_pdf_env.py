from pathlib import Path
import sys
import importlib.util
import os

def check_dependency(package_name, display_name=None):
    """Verifica si una dependencia está instalada"""
    if display_name is None:
        display_name = package_name
        
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ {display_name} no está instalado")
        return False
    else:
        try:
            module = importlib.import_module(package_name)
            print(f"✅ {display_name} está instalado (versión: {getattr(module, '__version__', 'desconocida')})")
            return True
        except:
            print(f"⚠️ {display_name} está instalado pero hay problemas al importarlo")
            return False

def check_tesseract():
    """Verifica si Tesseract está instalado"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract está instalado (versión: {version})")
        return True
    except Exception as e:
        print(f"❌ Tesseract no está disponible: {str(e)}")
        print("   Instala Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def check_poppler():
    """Verifica si Poppler está instalado"""
    try:
        from pdf2image import convert_from_path
        from pdf2image.exceptions import PDFInfoNotInstalledError
        
        # Crear un archivo PDF básico para probar
        test_path = Path("test_poppler.pdf")
        if not test_path.exists():
            import fpdf
            pdf = fpdf.FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Test PDF", ln=True)
            pdf.output(test_path)
        
        # Intentar convertir
        convert_from_path(test_path, first_page=1, last_page=1)
        print("✅ Poppler está instalado y funcionando correctamente")
        return True
    except PDFInfoNotInstalledError:
        print("❌ Poppler no está instalado o no está en el PATH")
        return False
    except Exception as e:
        print(f"⚠️ Error al verificar Poppler: {str(e)}")
        return False

def check_credentials():
    """Verifica si las credenciales de Google Cloud están configuradas"""
    results = {}
    try:
        # Intentar importar ConfigManager
        try:
            from utils.config_manager import ConfigManager
            results['config_manager'] = True
        except ImportError:
            print("⚠️ No se pudo importar ConfigManager, verificando manualmente")
            results['config_manager'] = False
            
        # Verificar archivo de configuración
        config_paths = [
            Path(__file__).parent / 'config.yaml',
            Path(__file__).parent / 'config.yml',
            Path(__file__).parent / 'configs/config.yaml',
            Path(__file__).parent / 'utils/config.yaml'
        ]
        
        config_found = False
        for config_path in config_paths:
            if config_path.exists():
                print(f"✅ Archivo de configuración encontrado en: {config_path}")
                config_found = True
                break
                
        if not config_found:
            print("⚠️ No se encontró archivo de configuración")
            
        # Verificar credenciales de Google Cloud
        credential_paths = [
            Path(__file__).parent / 'credentials.json',
            Path(__file__).parent / 'google_credentials.json',
            Path(__file__).parent / 'configs/credentials.json',
            Path(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', ''))
        ]
        
        credentials_found = False
        for cred_path in credential_paths:
            if cred_path.exists():
                print(f"✅ Credenciales de Google Cloud encontradas en: {cred_path}")
                credentials_found = True
                break
                
        if not credentials_found:
            if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                print(f"⚠️ Variable GOOGLE_APPLICATION_CREDENTIALS definida ({os.environ['GOOGLE_APPLICATION_CREDENTIALS']}), pero el archivo no existe")
            else:
                print("❌ No se encontraron credenciales de Google Cloud")
        
        # Verificar credenciales específicas si ConfigManager está disponible
        if results['config_manager']:
            config = ConfigManager.load_config()
            if not config:
                print("❌ No se pudo cargar la configuración")
                return False
                
            if 'ai_services' in config and 'google_cloud_vision' in config['ai_services']:
                credentials_file = config['ai_services']['google_cloud_vision']['credentials_file']
                credentials_path = Path(__file__).parent / credentials_file
                
                if credentials_path.exists():
                    print(f"✅ Credenciales especificadas en config encontradas en: {credentials_path}")
                    return True
                else:
                    print(f"❌ Credenciales especificadas en config no encontradas en: {credentials_path}")
            else:
                print("⚠️ No se encontró configuración de Google Cloud Vision en el archivo de configuración")
        
        return credentials_found
    except Exception as e:
        print(f"⚠️ Error al verificar credenciales: {str(e)}")
        return False

def check_file_system():
    """Verifica que el sistema de archivos esté configurado correctamente"""
    required_folders = [
        "templates",
        "Data",
        "utils",
        "core"
    ]
    
    missing_folders = []
    for folder in required_folders:
        folder_path = Path(__file__).parent / folder
        if not folder_path.exists():
            missing_folders.append(folder)
    
    if missing_folders:
        print(f"❌ Faltan carpetas requeridas: {', '.join(missing_folders)}")
        return False
    else:
        print("✅ Estructura de carpetas básica verificada")
        return True

def check_core_modules():
    """Verifica que los módulos core del sistema estén disponibles"""
    core_modules = [
        ("utils.config_manager", "ConfigManager"),
        ("lector_archivos.lector", "LectorArchivos"),
        ("utils.template_management.template_manager", "TemplateManager")
    ]
    
    all_available = True
    for module_path, class_name in core_modules:
        try:
            spec = importlib.util.find_spec(module_path)
            if spec is None:
                print(f"❌ Módulo {module_path} no encontrado")
                all_available = False
                continue
                
            module = importlib.import_module(module_path)
            if hasattr(module, class_name):
                print(f"✅ Clase {class_name} disponible en {module_path}")
            else:
                print(f"❌ Clase {class_name} no encontrada en {module_path}")
                all_available = False
        except Exception as e:
            print(f"❌ Error al verificar {module_path}: {str(e)}")
            all_available = False
    
    return all_available

def test_pdf_extractor():
    """Realiza una prueba básica del PDFExtractor"""
    try:
        # Comprobar si PDFExtractor está disponible
        spec = importlib.util.find_spec("pdf_extractor.pdf_extractor")
        if spec is None:
            print("⚠️ Módulo PDFExtractor no encontrado, omitiendo prueba")
            return False
            
        # Importar PDFExtractor
        try:
            from pdf_extractor.pdf_extractor import PDFExtractor
            print("✅ PDFExtractor importado correctamente")
        except ImportError as e:
            print(f"❌ Error al importar PDFExtractor: {str(e)}")
            return False
            
        # Crear un PDF de prueba si no existe
        test_path = Path("test_pdf_extractor.pdf")
        if not test_path.exists():
            try:
                import fpdf
                pdf = fpdf.FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Test PDF Extractor", ln=True)
                pdf.output(test_path)
                print(f"✅ PDF de prueba creado en: {test_path}")
            except Exception as e:
                print(f"❌ Error al crear PDF de prueba: {str(e)}")
                return False
        
        # Intentar extraer texto del PDF (sin OCR para evitar dependencias)
        try:
            extractor = PDFExtractor()
            text = extractor.extract_text_from_pdf(test_path, use_ocr=False)
            if text and len(text) > 0:
                print(f"✅ PDFExtractor extrajo texto correctamente ({len(text)} caracteres)")
                return True
            else:
                print("⚠️ PDFExtractor extrajo texto vacío")
                return False
        except Exception as e:
            print(f"❌ Error al extraer texto con PDFExtractor: {str(e)}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error al probar PDFExtractor: {str(e)}")
        return False

def check_aws_credentials():
    """Verifica si hay credenciales de AWS configuradas"""
    try:
        # Verificar archivo de credenciales de AWS
        home = Path.home()
        aws_cred_path = home / '.aws' / 'credentials'
        aws_config_path = home / '.aws' / 'config'
        
        if aws_cred_path.exists():
            print(f"✅ Archivo de credenciales AWS encontrado en: {aws_cred_path}")
            has_creds = True
        else:
            print(f"⚠️ No se encontró archivo de credenciales AWS en: {aws_cred_path}")
            has_creds = False
            
        if aws_config_path.exists():
            print(f"✅ Archivo de configuración AWS encontrado en: {aws_config_path}")
            has_config = True
        else:
            print(f"⚠️ No se encontró archivo de configuración AWS en: {aws_config_path}")
            has_config = False
            
        # Verificar variables de entorno
        aws_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
        env_vars_found = [var for var in aws_env_vars if var in os.environ]
        
        if env_vars_found:
            print(f"✅ Variables de entorno AWS encontradas: {', '.join(env_vars_found)}")
            has_env = True
        else:
            print("⚠️ No se encontraron variables de entorno AWS")
            has_env = False
            
        # Si tenemos credenciales, intentar hacer una prueba simple con boto3
        if has_creds or has_config or has_env:
            if check_dependency("boto3"):
                try:
                    import boto3
                    # Intenta una operación simple (listar buckets de S3)
                    s3 = boto3.client('s3')
                    s3.list_buckets()
                    print("✅ Conexión a AWS exitosa (se pudo listar buckets S3)")
                    return True
                except Exception as e:
                    print(f"⚠️ Credenciales AWS configuradas pero hay un error: {str(e)}")
                    return False
        
        return has_creds or has_config or has_env
        
    except Exception as e:
        print(f"⚠️ Error al verificar credenciales AWS: {str(e)}")
        return False

def main():
    """Función principal de verificación"""
    print("\n=== VERIFICACIÓN DE ENTORNO PARA NOTEFY IA DATA SYNTHETIC ===\n")
    
    results = {}
    
    print("\n--- Dependencias Python ---")
    results['PyPDF2'] = check_dependency("PyPDF2")
    results['PDFMiner'] = check_dependency("pdfminer.six", "PDFMiner")
    results['pytesseract'] = check_dependency("pytesseract")
    results['pdf2image'] = check_dependency("pdf2image")
    results['Pillow'] = check_dependency("PIL", "Pillow")
    results['GCV'] = check_dependency("google.cloud.vision", "Google Cloud Vision")
    results['pandas'] = check_dependency("pandas")
    results['numpy'] = check_dependency("numpy")
    
    # Añadir verificación de boto3 y otras dependencias de AWS
    print("\n--- Dependencias Adicionales ---")
    results['boto3'] = check_dependency("boto3", "AWS SDK (boto3)")
    results['botocore'] = check_dependency("botocore")
    results['fpdf'] = check_dependency("fpdf")
    results['yaml'] = check_dependency("yaml")
    results['jsonschema'] = check_dependency("jsonschema")
    results['openpyxl'] = check_dependency("openpyxl")  # Para Excel
    
    print("\n--- Software Externo ---")
    results['tesseract'] = check_tesseract()
    results['poppler'] = check_poppler()
    
    print("\n--- Estructura del Sistema ---")
    results['file_system'] = check_file_system()
    results['core_modules'] = check_core_modules()
    
    print("\n--- Configuración de APIs ---")
    results['google_credentials'] = check_credentials()
    results['aws_credentials'] = check_aws_credentials()
    
    print("\n--- Prueba de Funcionalidad ---")
    results['pdf_extractor'] = test_pdf_extractor()
    
    # Resumen de resultados
    print("\n=== RESUMEN DE VERIFICACIÓN ===")
    
    categories = {
        "Dependencias Python": ['PyPDF2', 'PDFMiner', 'pytesseract', 'pdf2image', 'Pillow', 'GCV', 'pandas', 'numpy'],
        "Dependencias AWS/Cloud": ['boto3', 'botocore'],
        "Dependencias Adicionales": ['fpdf', 'yaml', 'jsonschema', 'openpyxl'],
        "Software Externo": ['tesseract', 'poppler'],
        "Estructura del Sistema": ['file_system', 'core_modules'],
        "Configuración": ['google_credentials', 'aws_credentials'],
        "Funcionalidad": ['pdf_extractor']
    }
    
    for category, items in categories.items():
        success = sum(1 for item in items if item in results and results[item])
        total = len(items)
        print(f"{category}: {success}/{total} verificaciones exitosas")
    
    # Verificación general
    total_success = sum(1 for result in results.values() if result)
    total_items = len(results)
    print(f"\nVerificación general: {total_success}/{total_items} ({(total_success/total_items)*100:.1f}%)")
    
    if total_success == total_items:
        print("\n✅ ENTORNO COMPLETAMENTE CONFIGURADO")
    elif total_success >= total_items * 0.8:
        print("\n⚠️ ENTORNO PARCIALMENTE CONFIGURADO (funcionalidad básica disponible)")
    else:
        print("\n❌ ENTORNO INSUFICIENTEMENTE CONFIGURADO (se requiere atención)")
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()