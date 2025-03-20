from pathlib import Path
import json
import yaml
from datetime import datetime
from pdfminer.high_level import extract_text
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from utils.file_naming import FileNamingConvention
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from io import StringIO
import traceback
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import tempfile
import os
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar, LTFigure
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfdevice import PDFDevice
from pdfminer.high_level import extract_pages
import warnings
from contextlib import contextmanager
from utils.data_formats import DataFormatHandler
from utils.config_manager import ConfigManager
from google.cloud import vision
import os

try:
    import PyPDF2
except ImportError:
    print("Advertencia: No se encontró PyPDF2. Instálalo con: pip install PyPDF2")
    PyPDF2 = None

class PDFExtractor:
    """Clase para extraer y procesar contenido de archivos PDF"""
    
    def __init__(self):
        self.current_content = None
        self.content_quality = 0
        self.tipos_pdf = {
            'FARC': 'Evaluación FARC',
            'BIO': 'Historia Biográfica',
            'MTP': 'Plan de Tratamiento',
            'pdf_notas': 'Nota de Progreso',
            'pdf_otros': 'Otro documento'
        }
        self.ocr_enabled = self._check_tesseract()
        self.configurar_parametros_extraccion()
        self.suppress_warnings = True  # Añadido para controlar advertencias
        self.ignore_extraction_restrictions = True  # Añadido para ignorar restricciones
        self.optimize_params()
        self.rsrcmgr = PDFResourceManager(caching=True)
        self.extraction_methods = {
            'pdfminer': lambda x: self.extract_with_pdfminer(x),
            'pypdf2': lambda x: (self.extract_text_with_pypdf2(x), 'pypdf2', 70),
            'ocr': lambda x: (self.extract_text_with_ocr(x), 'ocr', 60)
        }

    @contextmanager
    def warning_handler(self):
        """Maneja las advertencias de PDFMiner"""
        if self.suppress_warnings:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                yield
        else:
            yield

    def configurar_parametros_extraccion(self):
        """Configura parámetros optimizados para extracción"""
        self.laparams = LAParams(
            line_margin=0.3,        # Menor margen para líneas más cercanas
            char_margin=1.0,        # Margen entre caracteres
            word_margin=0.1,        # Margen entre palabras
            boxes_flow=0.5,         # Control de flujo de texto
            detect_vertical=True    # Detectar texto vertical
        )

    def _check_tesseract(self):
        """Verifica si Tesseract está instalado y disponible"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            print("\nAdvertencia: Tesseract no está disponible.")
            print("Para habilitar OCR, instale Tesseract-OCR y asegúrese de que esté en el PATH")
            print("https://github.com/UB-Mannheim/tesseract/wiki")
            return False

    def optimize_params(self):
        """Optimiza parámetros para mejor extracción"""
        self.laparams = LAParams(
            line_margin=0.1,      # Reducido para mejor detección de líneas
            char_margin=0.2,      # Reducido para mejor agrupación de caracteres
            word_margin=0.1,      # Mantiene palabras juntas
            boxes_flow=0.7,       # Aumentado para mejor flujo de texto
            detect_vertical=True   # Necesario para formularios
        )

    def extract_text_with_pypdf2(self, pdf_path):
        """Extrae texto usando PyPDF2 como respaldo"""
        try:
            text_parts = []
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)  # Se utiliza PyPDF2.PdfReader en lugar de PdfReader
                for page in reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
            return "\n".join(text_parts) if text_parts else None
        except Exception:
            return None

    def extract_text_with_check(self, pdf_path):
        """Extrae texto con verificación mejorada"""
        try:
            with open(pdf_path, 'rb') as file:
                # Configuración inicial
                parser = PDFParser(file)
                document = PDFDocument(parser)
                
                # Verificar si el documento permite extracción
                if not document.is_extractable:
                    print("PDF protegido contra extracción. Intentando forzar...")
                    parser._check_extractable = False
                
                # Primer intento: extracción directa
                text = extract_text(pdf_path)
                if text and text.strip():
                    return text, "direct_extraction"

                # Segundo intento: extracción página por página
                text_parts = []
                output = StringIO()
                converter = TextConverter(self.rsrcmgr, output, laparams=self.laparams)
                interpreter = PDFPageInterpreter(self.rsrcmgr, converter)
                
                for page in PDFPage.get_pages(file, check_extractable=False):
                    interpreter.process_page(page)
                    text = output.getvalue()
                    if text.strip():
                        text_parts.append(text)
                    output.seek(0)
                    output.truncate(0)
                
                converter.close()
                output.close()
                
                if text_parts:
                    return "\n".join(text_parts), "page_by_page"

                # Tercer intento: PyPDF2 como respaldo
                return self.extract_text_with_pypdf2(pdf_path), "pypdf2"

        except Exception as e:
            print(f"Error en extracción: {str(e)}")
            if self.ocr_enabled:
                print("Intentando OCR como último recurso...")
                return self.extract_text_with_ocr(pdf_path), "ocr"
            return None, None

    def extract_pdfminer_advanced(self, pdf_path):
        """Extracción avanzada usando PDFMiner"""
        try:
            with self.warning_handler():
                text_parts = []
                with open(pdf_path, 'rb') as file:
                    # Configuración para PDFs protegidos
                    parser = PDFParser(file)
                    parser._check_extractable = False  # Forzar extracción
                    document = PDFDocument(parser)
                    
                    # Configurar extractor mejorado
                    rsrcmgr = PDFResourceManager(caching=True)
                    retstr = StringIO()
                    
                    # Parámetros optimizados para mejor extracción
                    laparams = LAParams(
                        line_margin=0.2,        # Reducido para capturar líneas más cercanas
                        char_margin=0.5,        # Reducido para mejor detección de caracteres
                        word_margin=0.1,        # Ajustado para mejor separación de palabras
                        boxes_flow=0.5,         # Mantiene un buen flujo de texto
                        detect_vertical=True,    # Importante para formularios
                    )
                    
                    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    
                    # Procesar cada página con parámetros mejorados
                    for page in PDFPage.get_pages(file, check_extractable=False):
                        interpreter.process_page(page)
                        
                    text = retstr.getvalue()
                    device.close()
                    retstr.close()
                    
                    if text.strip():
                        text_parts.append(text)
                
                return '\n'.join(text_parts) if text_parts else None
                
        except Exception as e:
            print(f"\nError en extracción avanzada PDFMiner: {str(e)}")
            return None

    def extract_page_by_page(self, pdf_path):
        """Extrae texto página por página"""
        try:
            with self.warning_handler():
                text_parts = []
                with open(pdf_path, 'rb') as file:
                    parser = PDFParser(file)
                    document = PDFDocument(parser, password='')
                    rsrcmgr = PDFResourceManager()
                    
                    for page in PDFPage.create_pages(document):
                        output = StringIO()
                        converter = TextConverter(
                            rsrcmgr, 
                            output, 
                            laparams=self.laparams
                        )
                        interpreter = PDFPageInterpreter(rsrcmgr, converter)
                        interpreter.process_page(page)
                        
                        text = output.getvalue()
                        if text.strip():
                            text_parts.append(text)
                            
                        converter.close()
                        output.close()

                return "\n".join(text_parts) if text_parts else None

        except Exception as e:
            print(f"\nError en extracción página por página: {str(e)}")
            return None

    def extract_text_with_ocr(self, pdf_path):
        """Extrae texto usando OCR (Tesseract)"""
        if not self.ocr_enabled:
            print("\nOCR no disponible. Por favor instale Tesseract.")
            return None

        try:
            print("\nConvirtiendo PDF a imágenes...")
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convertir PDF a imágenes
                images = convert_from_path(pdf_path)
                text_parts = []

                print(f"Procesando {len(images)} páginas con OCR...")
                for i, image in enumerate(images, 1):
                    print(f"Procesando página {i}/{len(images)}...")
                    # Mejorar imagen para OCR
                    image = image.convert('L')  # Convertir a escala de grises
                    text = pytesseract.image_to_string(
                        image, 
                        lang='spa+eng',  # Usar modelos español e inglés
                        config='--psm 1'  # Page segmentation mode: Automatic page segmentation with OSD
                    )
                    if text.strip():
                        text_parts.append(text)

                return "\n".join(text_parts) if text_parts else None

        except Exception as e:
            print(f"\nError en OCR: {str(e)}")
            return None

    def leer_pdf(self, file_path, use_ocr=True, max_intentos_ai=1):
        """Lee un PDF y extrae su texto utilizando diferentes métodos"""
        if PyPDF2 is None:
            print("No se puede procesar PDF. PyPDF2 no está disponible.")
            return "", 0

        resultados = []
        
        # 1. Intentar cada método disponible
        for method_name, extractor in self.extraction_methods.items():
            print(f"\nIntentando extracción con {method_name}...")
            try:
                content, method, base_quality = extractor(file_path)
                if content and content.strip():
                    # 2. Evaluar calidad del contenido extraído
                    quality = self._evaluate_content_quality(content, base_quality)
                    resultados.append((content, method, quality))
            except Exception as e:
                print(f"Error al procesar archivo con {method_name}: {str(e)}")
                continue
        
        if not resultados:
            print("\nNo se pudo extraer contenido con ningún método.")
            return None, 0

        # 3. Seleccionar el mejor resultado
        mejor_resultado = max(resultados, key=lambda x: x[2])
        contenido, metodo, calidad = mejor_resultado
        
        print(f"\nMétodo más efectivo: {metodo}")
        print(f"Calidad de extracción: {calidad}%")
        
        # Verificar si la calidad es muy baja y podemos mejorarla con IA
        if calidad < self.min_quality_threshold and self.use_ai:
            intentos_ai = 0
            while calidad < self.min_quality_threshold and intentos_ai < max_intentos_ai:
                print(f"\nLa calidad de extracción es baja.")
                if input("\n¿Desea intentar mejorar la extracción usando IA? (S/N): ").upper() == 'S':
                    # Seleccionar API
                    print("\nSeleccione la API a usar:")
                    print("1) Google Cloud Vision")
                    print("2) Amazon Textract")
                    
                    api_seleccion = input("\nIngrese opción (0 para cancelar): ")
                    
                    if api_seleccion == '0':
                        break
                        
                    if api_seleccion == '1':
                        # Google Cloud Vision
                        contenido_mejorado, nueva_calidad = self._extract_with_google_vision(file_path)
                    elif api_seleccion == '2':
                        # Amazon Textract
                        contenido_mejorado, nueva_calidad = self._extract_with_amazon_textract(file_path)
                    else:
                        print("Opción no válida")
                        continue
                        
                    # Si la calidad mejoró, actualizamos el resultado
                    if nueva_calidad > calidad:
                        print(f"\nCalidad mejorada: {nueva_calidad}% (anterior: {calidad}%)")
                        calidad = nueva_calidad
                        mejor_contenido = contenido_mejorado
                        
                        # Mostrar vista previa
                        print("\nVista previa del contenido extraído:")
                        print("-" * 80)
                        preview = mejor_contenido[:500] + "..." if len(mejor_contenido) > 500 else mejor_contenido
                        print(preview)
                        print("-" * 80)
                    else:
                        print(f"\nNo se logró mejorar la calidad de extracción con IA")
                else:
                    break  # El usuario no quiere usar IA
                    
                intentos_ai += 1
        
        print(f"\nCalidad estimada de extracción: {calidad}%")
        return mejor_contenido, calidad

    def _evaluate_content_quality(self, content, base_quality):
        """Evaluación mejorada de la calidad del contenido"""
        if not content:
            return 0

        # Análisis detallado del contenido
        lines = content.split('\n')
        words = content.split()
        
        # Métricas de calidad
        metrics = {
            'total_words': len(words),
            'avg_word_length': sum(len(w) for w in words) / len(words if words else 0),
            'significant_words': len([w for w in words if len(w) > 3]),
            'lines_with_content': sum(1 for l in lines if l.strip()),
            'formatting_score': sum(1 for l in lines if l.strip() and len(l) > 30) / len(lines) if lines else 0
        }
        
        # Puntuación basada en métricas
        quality_scores = {
            'word_density': min(metrics['total_words'] / 100, 1.0),
            'word_quality': metrics['significant_words'] / max(metrics['total_words'], 1),
            'formatting': metrics['formatting_score'],
            'base_adjustment': base_quality / 100
        }
        
        # Calidad final
        final_quality = sum(quality_scores.values()) / len(quality_scores) * 100
        return int(final_quality)

    def extract_with_pdfminer(self, pdf_path):
        """Extractor principal usando PDFMiner con configuración avanzada"""
        try:
            with self.warning_handler():
                text_parts = []
                with open(pdf_path, 'rb') as file:
                    parser = PDFParser(file)
                    document = PDFDocument(parser)
                    extractable = document.is_extractable
                    
                    if not extractable:
                        print("\nPDF protegido. Intentando extracción forzada...")
                        parser._check_extractable = False
                    
                    rsrcmgr = PDFResourceManager(caching=True)
                    output = StringIO()
                    device = TextConverter(
                        rsrcmgr, 
                        output, 
                        laparams=self.laparams
                    )
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    
                    for page in PDFPage.get_pages(
                        file,
                        check_extractable=False,
                        caching=True,
                        maxpages=0
                    ):
                        interpreter.process_page(page)
                    
                    text = output.getvalue()
                    device.close()
                    output.close()
                    
                    if text.strip():
                        text_parts.append(text)
                    
                    final_text = '\n'.join(text_parts) if text_parts else None
                    quality = 100 if extractable else 70
                    
                    return final_text, 'pdfminer', quality

        except Exception as e:
            print(f"\nError en PDFMiner: {e}")
            return None, None, 0

    def usar_api_pdf(self, file_path):
        """Mejora la extracción usando APIs de IA"""
        print("\nSeleccione la API a usar:")
        print("1) Google Cloud Vision")
        print("2) Amazon Textract")
        
        while True:
            try:
                opcion = int(input("\nIngrese opción (0 para cancelar): "))
                if opcion == 0:
                    return None, 0
                if opcion in [1, 2]:
                    break
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

        if opcion == 1:
            return self.usar_api_pdf_cloud_vision(file_path)
        else:
            return self.usar_api_pdf_textract(file_path)

    def usar_api_pdf_cloud_vision(self, file_path):
        """Usa Google Cloud Vision para mejorar la extracción"""
        config = ConfigManager.load_config()
        if not config or not config['ai_services']['google_cloud_vision']['enabled']:
            print("\nError: Google Cloud Vision no está habilitado")
            return None, 0

        try:
            # Configurar credenciales
            credentials_file = config['ai_services']['google_cloud_vision']['credentials_file']
            credentials_path = Path(__file__).parent.parent / credentials_file
            
            if not credentials_path.exists():
                print(f"\nError: Archivo de credenciales no encontrado en: {credentials_path}")
                return None, 0

            # Establecer variable de entorno para las credenciales
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)
            
            # Inicializar cliente
            client = vision.ImageAnnotatorClient()
            
            # Resto del código de extracción...
            # Convertir PDF a imágenes y procesar
            text_parts = []
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(file_path)
                
                for i, image in enumerate(images, 1):
                    print(f"\nProcesando página {i}/{len(images)}...")
                    
                    # Preparar imagen para Google Cloud Vision
                    img_path = f"{temp_dir}/page_{i}.png"
                    image.save(img_path)
                    
                    with open(img_path, 'rb') as image_file:
                        content = image_file.read()
                    
                    image = vision.Image(content=content)
                    response = client.document_text_detection(image=image)
                    text = response.full_text_annotation.text
                    
                    if text.strip():
                        text_parts.append(text)

            final_text = "\n".join(text_parts)
            quality = self._evaluate_content_quality(final_text, base_quality=90)  # Base quality alta para OCR
            return final_text, quality

        except Exception as e:
            print(f"\nError en Google Cloud Vision: {str(e)}")
            return None, 0

    def usar_api_pdf_textract(self, file_path):
        """Placeholder para Amazon Textract"""
        if not ConfigManager.check_credentials('amazon_textract'):
            print("\nError: Credenciales de Amazon Textract no configuradas")
            print("Configure las variables de entorno:")
            print("- AWS_ACCESS_KEY_ID")
            print("- AWS_SECRET_ACCESS_KEY")
            return None, 0

        # TODO: Implementar integración con Amazon Textract
        print("\nIntegración con Amazon Textract - No implementada")
        print("Se requiere:")
        print("1. Configurar credenciales AWS")
        print("2. Implementar lógica de extracción")
        print("3. Manejar respuesta y calidad")
        
        return None, 0

    def procesar_pdf(self, file_path=None, output_dir=None, clinic_initials="XX", tipo_pdf="FARC"):
        """
        Procesa un archivo PDF y genera un informe estructurado
        
        Args:
            file_path: Ruta al archivo PDF
            output_dir: Directorio de salida
            clinic_initials: Iniciales de la clínica
            tipo_pdf: Tipo de documento PDF (FARC, BIO, MTP, pdf_notas, pdf_otros)
        """
        # Si no se proporciona ruta, buscar PDFs en la carpeta input y en ubicaciones alternativas
        if not file_path:
            # Definir posibles ubicaciones donde buscar PDFs
            search_locations = [
                # Ruta principal: carpeta input específica
                Path(output_dir).parent.parent / "lector_archivos" / "input",
                # Ruta alternativa 1: carpeta input específica del tipo de documento
                Path(output_dir).parent.parent / tipo_pdf.lower() / "input",
                # Ruta alternativa 2: carpeta general de inputs
                Path(output_dir).parent.parent / "input",
                # Ruta alternativa 3: raíz del proyecto
                Path(__file__).parent.parent / "input"
            ]
            
            # Buscar PDFs en todas las ubicaciones
            all_pdfs = []
            for location in search_locations:
                if location.exists():
                    location_pdfs = list(location.glob("*.pdf"))
                    if location_pdfs:
                        print(f"\nEncontrados {len(location_pdfs)} archivos PDF en: {location}")
                        all_pdfs.extend([(pdf, location) for pdf in location_pdfs])
            
            if not all_pdfs:
                print("\nNo se encontraron archivos PDF en ninguna ubicación conocida")
                print("Realizando búsqueda recursiva desde la raíz del proyecto...")
                
                # Búsqueda recursiva como último recurso
                project_root = Path(__file__).parent.parent
                recursion_limit = 3  # Limitar profundidad de recursión
                
                for root, dirs, files in os.walk(project_root):
                    current_depth = len(Path(root).relative_to(project_root).parts)
                    if current_depth > recursion_limit:
                        continue
                        
                    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
                    if pdf_files:
                        location = Path(root)
                        all_pdfs.extend([(location / pdf, location) for pdf in pdf_files])
            
            if not all_pdfs:
                print("\nNo se encontraron archivos PDF en el sistema")
                return None
                
            # Mostrar todos los PDFs encontrados
            print(f"\n=== ARCHIVOS PDF DISPONIBLES ({self.tipos_pdf.get(tipo_pdf, 'Documento')}) ===")
            for idx, (pdf, location) in enumerate(all_pdfs, 1):
                rel_path = pdf.relative_to(location.parent.parent) if location else pdf.name
                print(f"{idx}. {rel_path}")
            
            while True:
                try:
                    opcion = int(input("\nSeleccione el archivo a procesar (0 para cancelar): ")) - 1
                    if opcion == -1:
                        return None
                    if 0 <= opcion < len(all_pdfs):
                        file_path = all_pdfs[opcion][0]
                        break
                    print("Opción no válida")
                except ValueError:
                    print("Por favor ingrese un número válido")

        print(f"\nProcesando PDF: {file_path}")
        
        # Extraer texto del PDF
        contenido, calidad = self.leer_pdf(file_path)
        if not contenido:
            print("No se pudo extraer contenido del PDF")
            return None

        # Mostrar vista previa
        print("\nVista previa del contenido extraído:")
        print("-" * 80)
        preview = contenido[:500] + "..." if len(contenido) > 500 else contenido
        print(preview)
        print("-" * 80)
        print(f"\nCalidad estimada de extracción: {calidad}%")

        # Preguntar si se requiere mejorar la extracción
        if calidad < 80:
            if input("\n¿Desea intentar mejorar la extracción usando IA? (S/N): ").upper() == 'S':
                contenido_mejorado, nueva_calidad = self.usar_api_pdf(file_path)
                if contenido_mejorado and nueva_calidad > calidad:  # Corregido && por and
                    contenido = contenido_mejorado
                    calidad = nueva_calidad

        # Generar informe
        self.current_content = contenido
        return self.generar_informe_pdf(contenido, clinic_initials, output_dir, tipo_pdf)

    def generar_informe_pdf(self, contenido, clinic_initials, output_dir, tipo_pdf):
        """Genera un informe estructurado del contenido extraído"""
        if not contenido:
            return None

        # Preparar datos para el informe
        datos = {
            'fecha_extraccion': datetime.now().isoformat(),
            'calidad_extraccion': self.content_quality,
            'contenido': contenido,
            'estadisticas': {
                'caracteres': len(contenido),
                'palabras': len(contenido.split()),
                'lineas': len(contenido.splitlines())
            }
        }

        while True:
            # Solicitar formato de salida
            formato = DataFormatHandler.prompt_format_selection()
            if not formato:
                break

            # Generar nombre de archivo
            nombre_archivo = FileNamingConvention.generate_filename(
                clinic_initials=clinic_initials,
                module=tipo_pdf,
                extension=DataFormatHandler.SUPPORTED_FORMATS[formato]['ext'].lstrip('.')
            )
            
            ruta_salida = Path(output_dir) / nombre_archivo
            
            # Guardar archivo usando el manejador de formatos
            if DataFormatHandler.save_data(datos, ruta_salida, formato):
                print(f"\nInforme guardado en: {ruta_salida}")
            else:
                print(f"Error al guardar en formato {formato}")

            if input("\n¿Desea exportar en otro formato? (S/N): ").upper() != 'S':
                break

        return ruta_salida
