from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from io import StringIO
import tempfile  # Añadido para manejar archivos temporales

# Verificación de dependencias e importación condicional
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

# Importar Google Cloud Vision
try:
    from google.cloud import vision
    CLOUD_VISION_AVAILABLE = True
except ImportError:
    CLOUD_VISION_AVAILABLE = False
    vision = None

# Importar pdfminer de forma condicional
try:
    from pdfminer.high_level import extract_text, extract_pages
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
    from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar, LTFigure
    from pdfminer.converter import TextConverter, PDFPageAggregator
    from pdfminer.pdfdevice import PDFDevice
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

# Importar PyPDF2
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# Importar OCR y herramientas de imagen
try:
    from PIL import Image
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

import os
import warnings
import sys
from utils.file_naming import FileNamingConvention
from utils.data_formats import DataFormatHandler
from utils.config_manager import ConfigManager

missing_dependencies = []
optional_dependencies = []

# Mostrar advertencias de dependencias faltantes
if not PDFMINER_AVAILABLE:
    missing_dependencies.append('pdfminer.six')

if not PYPDF2_AVAILABLE:
    optional_dependencies.append('PyPDF2')

if not OCR_AVAILABLE:
    optional_dependencies.append('pytesseract')
    optional_dependencies.append('Pillow')
    optional_dependencies.append('pdf2image')

if missing_dependencies:
    print("⚠️ ADVERTENCIA: Faltan dependencias críticas para el procesamiento de PDFs:")
    print(f"Por favor, instale: pip install {' '.join(missing_dependencies)}")

if optional_dependencies:
    print("ℹ️ Información: Algunas funcionalidades opcionales no estarán disponibles.")
    print(f"Para funcionalidad completa, instale: pip install {' '.join(optional_dependencies)}")

class PDFExtractor:
    """Clase para extraer y procesar contenido de archivos PDF"""
    
    def __init__(self):
        # Si faltan dependencias críticas, mostrar advertencia
        if missing_dependencies:
            print("\n⚠️ El procesador de PDF no funcionará correctamente sin las dependencias requeridas.")
            print(f"Instale: pip install {' '.join(missing_dependencies)}")
        
        self.current_content = None
        self.content_quality = 0
        self.tipos_pdf = {
            'FARC': 'Evaluación FARC',
            'BIO': 'Historia Biográfica',
            'MTP': 'Plan de Tratamiento',
            'pdf_notas': 'Nota de Progreso',
            'pdf_otros': 'Otro documento'
        }
        self.ocr_enabled = self._check_tesseract() if OCR_AVAILABLE else False
        self.use_ai = CLOUD_VISION_AVAILABLE
        self.configurar_parametros_extraccion()
        self.suppress_warnings = True  # Añadido para controlar advertencias
        self.ignore_extraction_restrictions = True  # Añadido para ignorar restricciones
        self.optimize_params()
        self.rsrcmgr = PDFResourceManager(caching=True)
        
        # Verificar disponibilidad de métodos de extracción
        self.extraction_methods = {}
        if 'extract_with_pdfminer' in dir(self):
            self.extraction_methods['pdfminer'] = lambda x: self.extract_with_pdfminer(x)
        if PyPDF2 is not None:
            self.extraction_methods['pypdf2'] = lambda x: (self.extract_text_with_pypdf2(x), 'pypdf2', 70)
        if self.ocr_enabled:
            self.extraction_methods['ocr'] = lambda x: (self.extract_text_with_ocr(x), 'ocr', 60)
            
        # Si no hay métodos disponibles, usar método de respaldo básico
        if not self.extraction_methods:
            self.extraction_methods['basic'] = lambda x: (self._basic_text_extraction(x), 'basic', 40)
            
        # Umbrales de calidad para extracción de PDF
        self.min_quality_threshold = 50  # Umbral mínimo de calidad (%)
        self.ideal_quality_threshold = 80  # Umbral ideal de calidad (%)

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

    def leer_pdf(self, file_path, use_ocr=True, max_intentos_ai=1, use_ai=False):
        """Lee un PDF y extrae su texto utilizando diferentes métodos de forma secuencial"""
        if PyPDF2 is None and not self.extraction_methods:
            print("No se puede procesar PDF. No hay métodos de extracción disponibles.")
            return "", 0

        print("\n=== PROCESAMIENTO SECUENCIAL DE PDF ===")
        print("Utilizando métodos de extracción en orden de complejidad...\n")
        
        # Verificar que el método de evaluación de calidad existe
        if not hasattr(self, '_evaluate_content_quality'):
            print("❌ Error: Método de evaluación de calidad no disponible.")
            
            # Definir el método localmente si no existe
            def evaluate_content_quality(content, base_quality):
                """Evaluación básica de la calidad del contenido"""
                if not content:
                    return 0
                
                # Métricas básicas
                words = content.split()
                word_count = len(words)
                
                # Puntuación basada en métricas simples
                quality = min(base_quality + (word_count / 50), 100)
                return int(quality)
            
            # Asignar el método a la instancia
            self._evaluate_content_quality = evaluate_content_quality
            print("✓ Se ha implementado un método de evaluación de calidad básico como respaldo.")
        
        # Ordenar métodos por complejidad y calidad esperada
        metodos_ordenados = [
            ('básico', lambda x: (self._basic_text_extraction(x), 'basic', 30)),
            ('PyPDF2', lambda x: (self.extract_text_with_pypdf2(x), 'pypdf2', 50)),
            ('PDFMiner', lambda x: self.extract_with_pdfminer(x)),
            ('PDFMiner avanzado', lambda x: (self.extract_pdfminer_advanced(x), 'pdfminer_advanced', 75)),
            ('Extracción página por página', lambda x: (self.extract_page_by_page(x), 'page_by_page', 85)),
        ]
        
        # Añadir OCR si está disponible
        if self.ocr_enabled and use_ocr:
            metodos_ordenados.append(('OCR (Tesseract)', lambda x: (self.extract_text_with_ocr(x), 'ocr', 90)))
        
        # Variables para seguimiento del mejor resultado
        mejor_contenido = None
        mejor_calidad = 0
        mejor_metodo = None
        
        # Intentar cada método y mostrar progreso
        for nombre_metodo, extractor in metodos_ordenados:
            print(f"\n📄 Intentando extracción con método: {nombre_metodo}...")
            try:
                # Obtener contenido y datos del método
                resultado = extractor(file_path)
                
                # Verificar el formato del resultado
                if resultado is None:
                    print(f"❌ No se pudo extraer contenido con {nombre_metodo}")
                    continue
                    
                if isinstance(resultado, tuple):
                    if len(resultado) == 3:
                        contenido, metodo, base_quality = resultado
                    elif len(resultado) == 2:
                        contenido, metodo = resultado
                        base_quality = 70  # Valor por defecto
                    else:
                        print(f"❌ Formato de resultado no válido para {nombre_metodo}")
                        continue
                else:
                    # Si es solo texto, usar valores por defecto
                    contenido = resultado
                    metodo = nombre_metodo
                    base_quality = 60
                
                # Si se obtuvo contenido, evaluar calidad
                if contenido and contenido.strip():
                    try:
                        calidad_actual = self._evaluate_content_quality(contenido, base_quality)
                        
                        # Mostrar calidad con barra visual
                        self._mostrar_barra_calidad(calidad_actual, nombre_metodo)
                        
                        # Actualizar mejor resultado si mejora la calidad
                        if calidad_actual > mejor_calidad:
                            mejor_contenido = contenido
                            mejor_calidad = calidad_actual
                            mejor_metodo = metodo
                            print(f"✅ Mejor resultado hasta ahora: {mejor_calidad}% de calidad")
                        else:
                            print(f"ℹ️ No mejora el resultado actual de {mejor_calidad}%")
                        
                        # Si alcanzamos 100%, no necesitamos continuar
                        if mejor_calidad >= 100:
                            print("\n🎉 Se ha logrado la máxima calidad de extracción")
                            break
                    except Exception as e:
                        print(f"❌ Error al evaluar la calidad: {str(e)}")
                        # Si hay error en la evaluación pero tenemos contenido, guardarlo con calidad base
                        if not mejor_contenido:
                            mejor_contenido = contenido
                            mejor_calidad = base_quality
                            mejor_metodo = metodo
                else:
                    print(f"❌ No se pudo extraer contenido con {nombre_metodo}")
            
            except Exception as e:
                print(f"❌ Error al procesar archivo con {nombre_metodo}: {str(e)}")
                continue
        
        # Verificar si se obtuvo algún resultado
        if mejor_contenido is None:
            print("\n❌ No se pudo extraer contenido con ningún método.")
            return None, 0

        # Mostrar resultado final
        print("\n=== RESULTADO FINAL DE EXTRACCIÓN ===")
        print(f"Método más efectivo: {mejor_metodo}")
        self._mostrar_barra_calidad(mejor_calidad, "CALIDAD FINAL")
        
        # Actualizar la calidad en la instancia
        self.content_quality = mejor_calidad
        
        # Aplicar procesamiento de texto para mejorar aún más la calidad
        if mejor_calidad < 100:
            print("\n🔍 Aplicando mejoras adicionales de texto...")
            contenido_mejorado = self._mejorar_texto(mejor_contenido)
            nueva_calidad = min(mejor_calidad + 5, 99)  # Mejora limitada al 99%
            
            if nueva_calidad > mejor_calidad:
                self._mostrar_barra_calidad(nueva_calidad, "DESPUÉS DE MEJORAS")
                mejor_contenido = contenido_mejorado
                mejor_calidad = nueva_calidad
                self.content_quality = nueva_calidad
        
        # Verificar si la calidad es muy baja y podemos mejorarla con IA
        if mejor_calidad < 100 and self.use_ai and use_ai:
            print(f"\nLa extracción ha alcanzado {mejor_calidad}% de calidad.")
            print("Se pueden obtener mejores resultados usando servicios de IA.")
            
            if input("\n¿Desea intentar mejorar la extracción usando IA? (S/N): ").upper() == 'S':
                intentos_ai = 0
                while mejor_calidad < 100 and intentos_ai < max_intentos_ai:
                    # Seleccionar API
                    print("\nSeleccione la API de IA a usar:")
                    print("1) Google Cloud Vision")
                    print("2) Amazon Textract")
                    
                    api_seleccion = input("\nIngrese opción (0 para cancelar): ")
                    
                    if api_seleccion == '0':
                        break
                        
                    if api_seleccion == '1':
                        # Google Cloud Vision
                        contenido_mejorado, nueva_calidad = self.usar_api_pdf_cloud_vision(file_path)
                    elif api_seleccion == '2':
                        # Amazon Textract
                        contenido_mejorado, nueva_calidad = self.usar_api_pdf_textract(file_path)
                    else:
                        print("Opción no válida")
                        continue
                        
                    # Si la calidad mejoró, actualizamos el resultado
                    if contenido_mejorado and nueva_calidad > mejor_calidad:
                        print(f"\n🚀 Calidad mejorada: {nueva_calidad}% (anterior: {mejor_calidad}%)")
                        self._mostrar_barra_calidad(nueva_calidad, "CON IA")
                        mejor_calidad = nueva_calidad
                        mejor_contenido = contenido_mejorado
                        self.content_quality = mejor_calidad
                        
                        # Mostrar vista previa
                        print("\nVista previa del contenido extraído:")
                        print("-" * 80)
                        preview = mejor_contenido[:500] + "..." if len(mejor_contenido) > 500 else mejor_contenido
                        print(preview)
                        print("-" * 80)
                    else:
                        print(f"\n❌ No se logró mejorar la calidad de extracción con IA")
                        
                    intentos_ai += 1
        
        print(f"\nCalidad final de extracción: {mejor_calidad}%")
        return mejor_contenido, mejor_calidad

    # Asegurar que el método _evaluate_content_quality esté correctamente definido
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
            'avg_word_length': sum(len(w) for w in words) / max(len(words), 1),
            'significant_words': len([w for w in words if len(w) > 3]),
            'lines_with_content': sum(1 for l in lines if l.strip()),
            'formatting_score': sum(1 for l in lines if l.strip() and len(l) > 30) / max(len(lines), 1)
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

    def _mostrar_barra_calidad(self, calidad, etiqueta=""):
        """Muestra una barra visual con la calidad de extracción"""
        calidad = min(int(calidad), 100)  # Asegurar que no exceda 100%
        barras = int(calidad / 2)  # Cada barra representa 2%
        espacios = 50 - barras
        
        # Determinar color según calidad
        if calidad < 50:
            color = '\033[91m'  # Rojo
            simbolo = "▓"
        elif calidad < 75:
            color = '\033[93m'  # Amarillo
            simbolo = "▓"
        else:
            color = '\033[92m'  # Verde
            simbolo = "█"
        
        reset = '\033[0m'
        
        # Intentar usar colores, si no funciona usar versión sin colores
        try:
            print(f"{etiqueta.ljust(22)} [{color}{simbolo * barras}{reset}{' ' * espacios}] {calidad}%")
        except:
            print(f"{etiqueta.ljust(22)} [{'█' * barras}{' ' * espacios}] {calidad}%")

    def _mejorar_texto(self, contenido):
        """Aplica mejoras de texto para aumentar la calidad"""
        if not contenido:
            return contenido
            
        # Eliminar caracteres no imprimibles
        lineas = contenido.split('\n')
        lineas_procesadas = []
        
        for linea in lineas:
            # Eliminar caracteres no imprimibles
            linea_limpia = ''.join(c for c in linea if c.isprintable() or c in ['\n', '\t'])
            
            # Eliminar espacios múltiples
            linea_limpia = ' '.join(linea_limpia.split())
            
            # Eliminar líneas vacías
            if linea_limpia:
                lineas_procesadas.append(linea_limpia)
                
        # Aplicar correcciones adicionales
        texto_mejorado = '\n'.join(lineas_procesadas)
        
        # Eliminar múltiples saltos de línea
        import re
        texto_mejorado = re.sub(r'\n{3,}', '\n\n', texto_mejorado)
        
        # Verificar y arreglar problemas de codificación comunes
        texto_mejorado = texto_mejorado.replace('â€™', "'")
        texto_mejorado = texto_mejorado.replace('â€œ', '"')
        texto_mejorado = texto_mejorado.replace('â€', '"')
        
        return texto_mejorado

    def mejorar_calidad(self, file_path, contenido_actual):
        """Intenta mejorar la calidad del texto extraído utilizando métodos avanzados"""
        print("\n=== MEJORANDO CALIDAD DE EXTRACCIÓN ===")
        print("1. Usar OCR avanzado")
        print("2. Usar APIs de IA")
        print("3. Aplicar procesamiento de texto")
        print("0. Cancelar")
        
        opcion = input("\nSeleccione un método: ").strip()
        
        if opcion == '0':
            return contenido_actual, self.content_quality
            
        if opcion == '1' and self.ocr_enabled:
            # Intentar con OCR más preciso
            print("\nAplicando OCR avanzado...")
            nuevo_contenido = self.extract_text_with_ocr(file_path)
            if nuevo_contenido:
                nueva_calidad = self._evaluate_content_quality(nuevo_contenido, 80)
                if nueva_calidad > self.content_quality:
                    return nuevo_contenido, nueva_calidad
                
        elif opcion == '2' and self.use_ai:
            # Usar APIs de IA
            contenido_api, calidad_api = self.usar_api_pdf(file_path)
            if contenido_api and calidad_api > self.content_quality:
                return contenido_api, calidad_api
                
        elif opcion == '3':
            # Aplicar procesamiento de texto (corrección avanzada)
            print("\nAplicando procesamiento de texto avanzado...")
            # Eliminar caracteres extraños y corregir formato
            lineas = contenido_actual.split('\n')
            lineas_procesadas = []
            for linea in lineas:
                # Eliminar caracteres no imprimibles
                linea_limpia = ''.join(c for c in linea if c.isprintable() or c in ['\n', '\t'])
                # Eliminar espacios múltiples
                linea_limpia = ' '.join(linea_limpia.split())
                if linea_limpia:
                    lineas_procesadas.append(linea_limpia)
            
            nuevo_contenido = '\n'.join(lineas_procesadas)
            # Pequeña mejora en la calidad por el procesamiento
            nueva_calidad = min(self.content_quality + 5, 95)
            return nuevo_contenido, nueva_calidad
            
        print("\nNo se pudo mejorar la calidad con el método seleccionado.")
        return contenido_actual, self.content_quality

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
        
        # Verificar que el config tiene la estructura correcta
        if not config:
            print("\nError: No se pudo cargar la configuración")
            print("Verifique que el archivo config.json existe y tiene el formato correcto")
            return None, 0
            
        # Verificar que la sección de AI services existe
        if 'ai_services' not in config:
            print("\nError: La sección 'ai_services' no existe en la configuración")
            print("Agregue una sección 'ai_services' en su archivo config.json")
            return None, 0
            
        # Verificar que la configuración de Google Cloud Vision existe
        if 'google_cloud_vision' not in config['ai_services']:
            print("\nError: La configuración para Google Cloud Vision no existe")
            print("Agregue una sección 'google_cloud_vision' dentro de 'ai_services' en su archivo config.json")
            return None, 0
            
        # Verificar que Google Cloud Vision está habilitado
        gcv_config = config['ai_services']['google_cloud_vision']
        if not gcv_config.get('enabled', False):
            print("\nError: Google Cloud Vision no está habilitado en la configuración")
            print("Establezca 'enabled': true en la sección 'google_cloud_vision'")
            return None, 0
            
        # Verificar que la ruta del archivo de credenciales existe
        if 'credentials_file' not in gcv_config:
            print("\nError: No se especificó el archivo de credenciales para Google Cloud Vision")
            print("Agregue 'credentials_file' con la ruta al archivo JSON de credenciales")
            return None, 0
            
        try:
            # Configurar credenciales
            credentials_file = gcv_config['credentials_file']
            
            # Intentar diferentes ubicaciones para el archivo de credenciales
            possible_paths = [
                Path(credentials_file),  # Ruta absoluta
                Path(__file__).parent.parent / credentials_file,  # Relativa al proyecto
                Path(__file__).parent.parent / "config" / credentials_file,  # En carpeta config
                Path(__file__).parent.parent / "credentials" / credentials_file  # En carpeta credentials
            ]
            
            credentials_path = None
            for path in possible_paths:
                if path.exists():
                    credentials_path = path
                    break
            
            if not credentials_path:
                print("\nError: Archivo de credenciales no encontrado")
                print(f"Buscado en: {', '.join(str(p) for p in possible_paths)}")
                print("\nGENERE UN ARCHIVO DE CREDENCIALES:")
                print("1. Vaya a https://console.cloud.google.com/")
                print("2. Cree un proyecto o use uno existente")
                print("3. Habilite la API de Cloud Vision")
                print("4. Cree una cuenta de servicio y descargue la llave JSON")
                print("5. Guarde el archivo y actualice la configuración")
                return None, 0

            print(f"\nUsando archivo de credenciales: {credentials_path}")
            # Establecer variable de entorno para las credenciales
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)

            # Inicializar cliente
            client = vision.ImageAnnotatorClient()

            # Convertir PDF a imágenes y procesar
            text_parts = []
            with tempfile.TemporaryDirectory() as temp_dir:
                print("\nConvirtiendo PDF a imágenes para procesamiento con Google Cloud Vision...")
                images = convert_from_path(file_path)
                
                for i, image in enumerate(images, 1):
                    print(f"\nEnviando página {i}/{len(images)} a Google Cloud Vision API...")
                    
                    # Preparar imagen para Google Cloud Vision
                    img_path = f"{temp_dir}/page_{i}.png"
                    image.save(img_path)
                    
                    with open(img_path, 'rb') as image_file:
                        content = image_file.read()
                    image = vision.Image(content=content)
                    
                    try:
                        print("Realizando reconocimiento de texto...")
                        response = client.document_text_detection(image=image)
                        text = response.full_text_annotation.text
                        
                        if text and text.strip():
                            text_parts.append(text)
                            print(f"✅ Texto extraído correctamente de la página {i}")
                        else:
                            print(f"⚠️ No se pudo extraer texto de la página {i}")
                    except Exception as page_error:
                        print(f"❌ Error procesando página {i}: {str(page_error)}")

            if not text_parts:
                print("\n❌ No se pudo extraer texto de ninguna página usando Google Cloud Vision")
                return None, 0
                
            final_text = "\n".join(text_parts)
            quality = self._evaluate_content_quality(final_text, base_quality=90)  # Base quality alta para OCR
            
            print(f"\n✅ Extracción con Google Cloud Vision completada con éxito")
            print(f"Calidad de extracción: {quality}%")
            
            return final_text, quality

        except Exception as e:
            print(f"\n❌ Error en Google Cloud Vision: {str(e)}")
            print("Verifique lo siguiente:")
            print("1. Las credenciales son válidas y tienen los permisos adecuados")
            print("2. La API de Cloud Vision está habilitada para el proyecto")
            print("3. Tiene conexión a internet")
            print("4. El PDF no está protegido o corrupto")
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
        
        # Verificar si la calidad es aceptable
        if calidad < self.ideal_quality_threshold:
            mejorar = input(f"\n¿Desea intentar mejorar la calidad de extracción? (S/N): ").strip().upper() == 'S'
            if mejorar:
                contenido, calidad = self.mejorar_calidad(file_path, contenido)
                print(f"\nCalidad después de mejora: {calidad}%")
                            
            # Si la calidad sigue siendo demasiado baja, advertir
            if calidad < self.min_quality_threshold:
                continuar = input(f"\n⚠ Advertencia: La calidad de extracción es baja ({calidad}%). ¿Desea continuar? (S/N): ").strip().upper() == 'S'
                if not continuar:
                    return None

        # Generar informe
        self.current_content = contenido
        return self.generar_informe_pdf(contenido, clinic_initials, output_dir, tipo_pdf)

    def _basic_text_extraction(self, pdf_path):
        """Método básico de extracción para casos donde no hay otras dependencias"""
        try:
            with open(pdf_path, 'rb') as file:
                # Intento básico de leer caracteres imprimibles
                content = file.read().decode('utf-8', errors='ignore')
                # Filtrar solo caracteres imprimibles
                filtered_content = ''.join(char for char in content if char.isprintable() or char in ['\n', '\r', '\t'])
                return filtered_content
        except Exception as e:
            print(f"Error en extracción básica: {str(e)}")
            return "No se pudo extraer texto. Instale dependencias adicionales para mejor funcionamiento."

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