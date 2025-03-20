from pathlib import Path
import pandas as pd
import json
import yaml
import re
import ast
from typing import Dict, Any, List, Optional, Tuple, Union
from .advanced_content_analyzer import AdvancedContentAnalyzer
from datetime import datetime
from google.cloud import vision
from google.oauth2 import service_account
import os
from typing import get_type_hints
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import tempfile

class TemplateManager:
    """Gestor de plantillas de importación con validación estricta"""

    def __init__(self):
        self.base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic")
        self.templates_base = self.base_path / "templates"  # Añadir esta línea
        self.campos_path = self.base_path / "templates/archivos de campos"
        self.output_path = self.base_path / "templates/Campos Master Global"
        self.content_analyzer = AdvancedContentAnalyzer()

        # Añadir estos atributos para evitar errores
        self.global_templates = self.templates_base / "Campos Master Global"
        self.code_templates = self.templates_base / "Campos Codigos"

        # Definir métodos de extracción con sus calidades base
        self.extraction_methods = {
            'basic_text': (self._analyze_text_file, 80),
            'json': (self._analyze_json_file, 90),
            'yaml': (self._analyze_yaml_file, 85),
            'excel': (self._analyze_excel_file, 85),
            'regex': (self._analyze_with_regex, 75),
            'django': (self._analyze_django_model, 95),
            'ast': (self._analyze_with_ast, 90)
        }

    def analyze_and_create_template(self, source_file: Path, template_type: str) -> Dict[str, Any]:
        """Analiza archivo fuente y crea plantilla de importación"""
        print(f"\nGenerando plantilla de importación para: {template_type}")
        print(f"Archivo fuente: {source_file}")

        # 1. Extraer campos usando el mejor método disponible
        fields = self._extract_fields_with_cascade(source_file)
        if not fields:
            print("\n❌ No se pudieron extraer campos del archivo")
            return None

        # 2. Validar campos obligatorios según tipo
        missing_fields = self._validate_required_fields(fields, template_type)
        if (missing_fields):
            print("\n⚠️ Campos obligatorios faltantes:")
            for field in missing_fields:
                print(f"  • {field}")

        # 3. Enriquecer definiciones de campos
        enriched_fields = self._enrich_field_definitions(fields)

        # 4. Generar plantilla final
        template = {
            'type': template_type,
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'fields': enriched_fields,
            'validation': {
                'required_fields': self._get_required_fields(template_type),
                'optional_fields': self._get_optional_fields(template_type),
                'missing_fields': missing_fields
            },
            'examples': self._generate_examples(enriched_fields)
        }

        # 5. Guardar plantilla
        self._save_template(template, template_type)
        return template

    def _extract_fields_with_cascade(self, source_file: Path) -> Dict[str, Any]:
        """Extrae campos usando múltiples métodos en cascada"""
        methods = [
            (self._extract_from_django_model, 'Django Model'),
            (self._extract_from_json_schema, 'JSON Schema'),
            (self._extract_from_text, 'Text File'),
            (self._extract_with_ai, 'AI Analysis')
        ]

        for extractor, method_name in methods:
            print(f"\nIntentando extracción con: {method_name}")
            try:
                fields = extractor(source_file)
                if fields:
                    print(f"✅ Extracción exitosa con {method_name}")
                    return fields
            except Exception as e:
                print(f"❌ Error en {method_name}: {str(e)}")
                continue

        return None

    def _enrich_field_definitions(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece las definiciones de campos con validadores y ejemplos"""
        enriched = {}
        
        for field_name, field_info in fields.items():
            base_type = field_info.get('type', 'string')
            
            # Obtener validadores predeterminados para el tipo
            type_config = self.field_types.get(base_type, self.field_types['string'])
            
            enriched[field_name] = {
                'type': base_type,
                'required': field_info.get('required', False),
                'validators': self._get_field_validators(field_info, type_config),
                'description': field_info.get('description', f"Campo para {field_name}"),
                'examples': self._generate_field_examples(field_info),
                'metadata': {
                    'source_name': field_name,
                    'db_field': self._normalize_field_name(field_name),
                    'translations': self._get_field_translations(field_name)
                }
            }

        return enriched

    def _get_field_validators(self, field_info: Dict[str, Any], type_config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene y combina validadores para un campo"""
        validators = type_config['default_validations'].copy()
        
        # Agregar o sobrescribir con validadores específicos del campo
        field_validators = field_info.get('validators', {})
        validators.update(field_validators)
        
        # Agregar validadores especiales según el contenido
        if field_info.get('choices'):
            validators['allowed_values'] = [choice['value'] for choice in field_info['choices']]
        
        if field_info.get('pattern'):
            validators['pattern'] = field_info['pattern']
            
        return validators

    def _generate_field_examples(self, field_info: Dict[str, Any]) -> List[str]:
        """Genera ejemplos para un campo basado en su tipo y validadores"""
        examples = []
        field_type = field_info.get('type', 'string')
        
        if (field_type == 'string'):
            if field_info.get('choices'):
                examples.extend(choice['value'] for choice in field_info['choices'][:3])
            else:
                examples.append("Ejemplo texto")
                
        elif (field_type == 'number'):
            examples.extend(['0', '42', '3.14'])
            
        elif (field_type == 'date'):
            examples.extend(['2024-01-01', '2024-12-31'])
            
        elif (field_type == 'boolean'):
            examples.extend(['true', 'false'])
            
        return examples[:3]  # Limitar a 3 ejemplos

    def _validate_required_fields(self, fields: Dict[str, Any], template_type: str) -> List[str]:
        """Valida campos obligatorios según el tipo de plantilla"""
        required_fields = self._get_required_fields(template_type)
        return [field for field in required_fields if field not in fields]

    def _get_required_fields(self, template_type: str) -> List[str]:
        """Obtiene lista de campos obligatorios según tipo"""
        # Definiciones de campos obligatorios por tipo
        required_by_type = {
            'pacientes': ['nombre', 'apellido', 'fecha_nacimiento', 'genero'],
            'FARC': ['paciente_id', 'fecha_evaluacion', 'tipo_evaluacion'],
            'BIO': ['paciente_id', 'fecha_historia'],
            'MTP': ['paciente_id', 'fecha_plan', 'objetivos']
        }
        return required_by_type.get(template_type, [])

    def _get_optional_fields(self, template_type: str) -> List[str]:
        """Obtiene lista de campos opcionales según tipo"""
        # Definiciones de campos opcionales por tipo
        optional_by_type = {
            'pacientes': ['telefono', 'email', 'direccion', 'notas'],
            'FARC': ['comentarios', 'siguiente_evaluacion'],
            'BIO': ['antecedentes', 'observaciones'],
            'MTP': ['notas', 'fecha_revision']
        }
        return optional_by_type.get(template_type, [])

    def analizar_y_generar_plantilla(self, tipo_doc: str) -> Optional[Dict[str, Any]]:
        """Analiza archivo usando cascada de métodos"""
        file_path = self._seleccionar_archivo_campos()
        if not file_path:
            return None

        resultados = []
        
        # 1. Intentar cada método de extracción básica
        print("\nAnalizando archivo...")
        for method_name, (analyzer, base_quality) in self.extraction_methods.items():
            print(f"\nProbando método: {method_name}")
            try:
                fields, quality = analyzer(file_path)
                if fields:
                    quality = self._evaluate_extraction_quality(fields, base_quality)
                    resultados.append((fields, method_name, quality))
                    print(f"Calidad: {quality:.1f}%")
            except Exception as e:
                print(f"Error en {method_name}: {str(e)}")
                continue

        if not resultados:
            print("\n❌ No se pudo analizar con ningún método")
            return None

        # 2. Seleccionar mejor resultado
        mejor_resultado = max(resultados, key=lambda x: x[2])
        campos, metodo, calidad = mejor_resultado
        
        print(f"\n✅ Método más efectivo: {metodo}")
        print(f"Calidad de análisis: {calidad:.1f}%")

        # 3. Solo inicializar y usar IA si la calidad es baja
        if calidad < 80:
            print("\n⚠️ La calidad del análisis es baja")
            if input("¿Desea mejorar el análisis con IA? (S/N): ").upper() == 'S':
                campos_mejorados, nueva_calidad = self._mejorar_con_ia(campos, file_path)
                if campos_mejorados and nueva_calidad > calidad:
                    campos = campos_mejorados
                    calidad = nueva_calidad
                    metodo = "IA-mejorado"

        # 4. Generar plantilla final
        template = {
            'version': '1.0',
            'tipo': tipo_doc,
            'fecha_generacion': datetime.now().isoformat(),
            'metodo_analisis': metodo,
            # Asegúrate de que todos los campos necesarios estén presentes
            'campos': campos,
            'calidad': calidad
        }

        # 5. Guardar resultado
        self._guardar_plantilla(template, tipo_doc)
        return template

    def _seleccionar_archivo_campos(self) -> Optional[Path]:
        """Lista y permite seleccionar archivos de campos"""
        try:
            # Buscar todos los archivos en la carpeta
            archivos = []
            for ext in ['*.txt', '*.csv', '*.xlsx', '*.xls', '*.json', '*.yaml', '*.yml']:
                archivos.extend(self.campos_path.glob(ext))

            if not archivos:
                print("\n❌ No se encontraron archivos en:")
                print(f"   {self.campos_path}")
                return None

            # Mostrar archivos encontrados
            print("\n=== ARCHIVOS DE CAMPOS DISPONIBLES ===")
            for idx, archivo in enumerate(archivos, 1):
                # Obtener tamaño y última modificación
                stats = archivo.stat()
                tamano = stats.st_size / 1024  # KB
                modificado = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                
                # Mostrar información del archivo
                print(f"{idx}. {archivo.name}")
                print(f"   Tamaño: {tamano:.1f} KB")
                print(f"   Modificado: {modificado}")
                print(f"   Tipo: {self._detectar_tipo_archivo(archivo)}")
                print()

            print("0. Cancelar")

            # Solicitar selección
            while True:
                try:
                    opcion = input("\nSeleccione el archivo a analizar (0 para cancelar): ").strip()
                    if opcion == '0':
                        return None
                        
                    num_opcion = int(opcion)
                    if 1 <= num_opcion <= len(archivos):
                        archivo_seleccionado = archivos[num_opcion - 1]
                        print(f"\nArchivo seleccionado: {archivo_seleccionado.name}")
                        return archivo_seleccionado

                    print("\n❌ Opción no válida")
                except ValueError:
                    print("\n❌ Por favor ingrese un número válido")

        except Exception as e:
            print(f"\n❌ Error al listar archivos: {str(e)}")
            return None

    def _detectar_tipo_archivo(self, archivo: Path) -> str:
        """Detecta el tipo de contenido del archivo"""
        extension = archivo.suffix.lower()
        
        if extension == '.txt':
            # Analizar primeras líneas para determinar tipo
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read(1000)  # Leer primeros 1000 caracteres
                    
                # Detectar si parece código
                if any(patron in contenido for patron in ['class ', 'def ', 'function']):
                    return 'Código fuente'
                    
                # Detectar si parece tabla
                if any(line.count('\t') > 1 or line.count(',') > 1 
                      for line in contenido.split('\n')[:5]):
                    return 'Datos tabulares'
                    
                return 'Texto plano'
                
            except:
                return 'Texto (formato desconocido)'
                
        elif extension in ['.csv', '.xlsx', '.xls']:
            return 'Tabla de datos'
        elif extension == '.json':
            return 'Estructura JSON'
        elif extension in ['.yaml', '.yml']:
            return 'Estructura YAML'
        else:
            return 'Archivo desconocido'

    def _guardar_plantilla(self, template: Dict[str, Any], tipo_doc: str) -> None:
        """Guarda la plantilla directamente en Campos Master Global"""
        # Obtener nombre base del archivo original usando el nombre guardado en el template
        nombre_base = template.get('nombre', '').split('.')[0]  # Quitar extensión
        
        # Limpiar nombre
        nombre_base = nombre_base.replace(' ', '_').replace('(', '').replace(')', '')
        
        # Agregar información de campos al nombre
        num_campos = len(template.get('campos', {}))
        nombre_archivo = f"{nombre_base}_{num_campos}_campos"
        
        # Guardar directamente en output_path sin crear subdirectorios
        for formato, config in [
            ('json', {
                'extension': '.json',
                'modo': 'w',
                'guardar': lambda t, f: json.dump(t, f, indent=2, ensure_ascii=False)
            }),
            ('yaml', {
                'extension': '.yaml',
                'modo': 'w',
                'guardar': lambda t, f: yaml.dump(t, f, allow_unicode=True)
            })
        ]:
            try:
                output_path = self.output_path / f"{nombre_archivo}{config['extension']}"
                with open(output_path, config['modo'], encoding='utf-8') as f:
                    config['guardar'](template, f)
                print(f"\n✅ Plantilla guardada en: {output_path}")
            except Exception as e:
                print(f"\n❌ Error guardando formato {formato}: {str(e)}")

        # Guardar metadata junto a la plantilla
        metadata_path = self.output_path / f"{nombre_archivo}_metadata.json"
        try:
            metadata = {
                'nombre_archivo': nombre_archivo,
                'tipo_documento': template['tipo'],
                'fecha_generacion': template['fecha_generacion'],
                'num_campos': num_campos,
                'campos': list(template.get('campos', {}).keys()),
                'calidad_extraccion': template.get('calidad', 0),
                'metodo_analisis': template.get('metodo_analisis', 'desconocido'),
                'indices_busqueda': self._generar_indices_busqueda(template)
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"\n❌ Error guardando metadata: {str(e)}")

    def _get_template_name(self, tipo_doc: str, archivo_origen: Optional[str] = None) -> str:
        """Genera nombre base para la plantilla basado en archivo origen"""
        if archivo_origen:
            # Limpiar nombre de archivo
            nombre_base = archivo_origen.split('.')[0]  # Quitar extensión
            nombre_base = nombre_base.replace(' ', '_').replace('(', '').replace(')', '')
            return f"{nombre_base}_template"
            
        # Fallback a nombres predeterminados si no hay archivo origen
        nombre_tipos = {
            'pacientes': 'pacientes_plantilla',
            'FARC': 'farc_evaluacion',
            'BIO': 'bio_historial',
            'MTP': 'mtp_plan'
        }
        return nombre_tipos.get(tipo_doc, f"{tipo_doc.lower()}_template")

    def _guardar_metadata(self, template: Dict[str, Any], nombre_archivo: str, output_path: Path) -> None:
        """Guarda metadata para búsqueda posterior"""
        metadata = {
            'nombre_archivo': nombre_archivo,
            'tipo_documento': template['tipo'],
            'fecha_generacion': template['fecha_generacion'],
            'num_campos': len(template.get('campos', {})),
            'campos': list(template.get('campos', {}).keys()),
            'calidad_extraccion': template.get('calidad', 0),
            'metodo_analisis': template.get('metodo_analisis', 'desconocido'),
            'indices_busqueda': self._generar_indices_busqueda(template)
        }

        # Guardar metadata
        metadata_path = output_path / f"{nombre_archivo}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _generar_indices_busqueda(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Genera índices para búsqueda posterior"""
        campos = template.get('campos', {})
        indices = {
            'por_tipo': {},
            'requeridos': [],
            'opcionales': [],
            'con_validacion': []
        }

        # Agrupar campos por tipo
        for nombre, info in campos.items():
            tipo = info.get('type', 'string')
            if tipo not in indices['por_tipo']:
                indices['por_tipo'][tipo] = []
            indices['por_tipo'][tipo].append(nombre)

            # Clasificar campos
            if info.get('required', False):
                indices['requeridos'].append(nombre)
            else:
                indices['opcionales'].append(nombre)

            if info.get('validators'):
                indices['con_validacion'].append(nombre)

        return indices

    def _analyze_with_standard(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Análisis usando métodos estándar según el tipo de archivo"""
        extension = file_path.suffix.lower()
        
        handlers = {
            '.txt': self._analyze_text_file,
            '.csv': self._analyze_csv_file,
            '.xlsx': self._analyze_excel_file,
            '.json': self._analyze_json_file,
            '.yaml': self._analyze_yaml_file,
            '.yml': self._analyze_yaml_file
        }

        if extension not in handlers:
            print(f"\n⚠️ Extensión no soportada: {extension}")
            return {}, 0

        try:
            print(f"\nAnalizando archivo con método estándar para {extension}")
            fields = handlers[extension](file_path)
            quality = self._evaluate_standard_quality(fields)
            return fields, quality
        except Exception as e:
            print(f"Error en análisis estándar: {str(e)}")
            return {}, 0

    def _analyze_with_regex(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Análisis usando expresiones regulares avanzadas"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Patrones de extracción mejorados
            patterns = [
                # Patrón para campos Django
                (r'(\w+)\s*=\s*models\.(\w+)Field\((.*?)\)', self._extract_django_field),
                
                # Patrón para variables y tipos
                (r'(?:var|let|const)?\s*(\w+)\s*:\s*(\w+)', self._extract_typed_field),
                
                # Patrón para definiciones de clases
                (r'class\s+(\w+).*?{(.*?)}', self._extract_class_fields),
                
                # Patrón para campos JSON/YAML
                (r'["\']([\w_]+)["\']:\s*({[^}]+}|\[[^\]]+\]|"[^"]*"|\'[^\']*\'|\d+)', self._extract_json_field)
            ]

            campos = {}
            for pattern, extractor in patterns:
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in matches:
                    field_info = extractor(match)
                    if field_info:
                        name, info = field_info
                        campos[name] = info

            quality = self._evaluate_regex_quality(campos)
            return campos, quality

        except Exception as e:
            print(f"Error en análisis regex: {str(e)}")
            return {}, 0

    def _analyze_with_ocr(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Análisis usando OCR (Tesseract)"""
        try:
            # Verificar si es un archivo de imagen o PDF
            if file_path.suffix.lower() not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff']:
                return {}, 0

            print("\nPreparando análisis OCR...")
            
            # Convertir a imagen si es PDF
            if file_path.suffix.lower() == '.pdf':
                images = convert_from_path(file_path)
                print(f"Convertido PDF a {len(images)} imágenes")
            else:
                images = [Image.open(file_path)]

            campos = {}
            confidences = []

            # Procesar cada imagen
            for idx, image in enumerate(images, 1):
                print(f"Procesando página/imagen {idx}/{len(images)}...")
                
                # Preprocesar imagen para mejor OCR
                image = self._preprocess_image(image)
                
                # Extraer texto con Tesseract
                texto = pytesseract.image_to_string(
                    image, 
                    lang='spa+eng',
                    config='--psm 1 --oem 3'
                )

                # Obtener datos de confianza
                datos = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                confidences.extend([float(conf) for conf in datos['conf'] if conf != '-1'])

                # Analizar texto extraído
                campos_pagina = self._extract_fields_from_text(texto)
                campos.update(campos_pagina)

            # Calcular calidad
            if confidences:
                confidence_avg = sum(confidences) / len(confidences)
                quality = min(85, confidence_avg)  # Máximo 85% para OCR
            else:
                quality = 0

            return campos, quality

        except Exception as e:
            print(f"Error en OCR: {str(e)}")
            return {}, 0

    def _preprocess_image(self, image: Image) -> Image:
        """Preprocesa imagen para mejor OCR"""
        # Convertir a escala de grises
        image = image.convert('L')
        
        # Binarización
        image = image.point(lambda x: 0 if x < 128 else 255, '1')
        
        # Escalar si es necesario
        if image.size[0] > 2000 or image.size[1] > 2000:
            image.thumbnail((2000, 2000))
            
        return image

    def _extract_fields_from_text(self, text: str) -> Dict[str, Any]:
        """Extrae campos del texto reconocido"""
        campos = {}
        lines = text.split('\n')
        
        for line in lines:
            # Buscar patrones de campo
            if ':' in line:
                name, value = line.split(':', 1)
                name = name.strip()
                value = value.strip()
                
                # Inferir tipo y metadata
                field_type = self._infer_type_from_value(value)
                campos[name] = {
                    'type': field_type,
                    'value': value,
                    'required': self._infer_required(line),
                    'description': self._generate_field_description(name, value)
                }

        return campos

    def _analyze_django_model(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Analiza código de modelo Django"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Detectar si es un modelo Django
            if not ('models.Model' in content or 'models.CharField' in content):
                return {}, 0

            campos = {}
            quality_metrics = {
                'field_detection': 0,
                'type_inference': 0,
                'choices_detection': 0,
                'metadata_extraction': 0
            }

            # Detectar campos del modelo
            field_patterns = [
                (r'(\w+)\s*=\s*models\.(\w+)Field\((.*?)\)', 0.9),  # Campo estándar
                (r'CHOICES\s*=\s*\[(.*?)\]', 0.8),  # Choices
                (r'help_text=_\([\'"](.+?)[\'"]\)', 0.7),  # Help text
            ]

            for pattern, base_quality in field_patterns:
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in matches:
                    if 'Field' in match.group(0):
                        # Extraer nombre y tipo
                        name = match.group(1)
                        field_type = match.group(2)
                        options = match.group(3)

                        campos[name] = {
                            'type': self._map_django_type(field_type),
                            'required': 'null=True' not in options,
                            'choices': self._extract_choices(options) if 'choices=' in options else None,
                            'help_text': self._extract_help_text(options)
                        }
                        
                        quality_metrics['field_detection'] += 1
                        if campos[name]['choices']:
                            quality_metrics['choices_detection'] += 1
                        if campos[name]['help_text']:
                            quality_metrics['metadata_extraction'] += 1

            # Calcular calidad
            total_fields = len(campos)
            if total_fields > 0:
                quality = (
                    quality_metrics['field_detection'] / total_fields * 0.4 +
                    quality_metrics['choices_detection'] / total_fields * 0.3 +
                    quality_metrics['metadata_extraction'] / total_fields * 0.3
                ) * 100
            else:
                quality = 0

            return campos, quality

        except Exception as e:
            print(f"Error en análisis Django: {str(e)}")
            return {}, 0

    def _map_django_type(self, django_type: str) -> str:
        """Mapea tipos de Django a tipos genéricos"""
        type_mapping = {
            'Char': 'string',
            'Text': 'text',
            'Integer': 'number',
            'Float': 'float',
            'Boolean': 'boolean',
            'Date': 'date',
            'DateTime': 'datetime',
            'ForeignKey': 'relation',
            'OneToOne': 'relation',
            'ManyToMany': 'relation'
        }
        return type_mapping.get(django_type, 'string')

    def _extract_choices(self, options: str) -> List[Dict[str, str]]:
        """Extrae opciones de choices"""
        choices = []
        matches = re.finditer(r'\([\'"](.*?)[\'"],\s*_([\'"](.*?)[\'"]\))', options)
        for match in matches:
            choices.append({
                'value': match.group(1),
                'label': match.group(3)
            })
        return choices

    def _extract_help_text(self, options: str) -> Optional[str]:
        """Extrae el texto de ayuda"""
        match = re.search(r'help_text=_\([\'"](.+?)[\'"]\)', options)
        return match.group(1) if match else None

    def _analyze_basic(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Análisis básico del archivo de campos"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            campos = {}
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Analizar línea por línea
                if ':' in line:
                    name, value = line.split(':', 1)
                    name = name.strip()
                    value = value.strip()
                    
                    campos[name] = {
                        'type': self._infer_basic_type(value),
                        'required': '*' in line or '!' in line,
                        'description': self._generate_description(name, value)
                    }
                elif '=' in line:
                    name, value = line.split('=', 1)
                    name = name.strip()
                    value = value.strip()
                    
                    campos[name] = {
                        'type': self._infer_basic_type(value),
                        'required': True,
                        'default': value,
                        'description': self._generate_description(name, value)
                    }

            # Calcular calidad del análisis
            if not campos:
                return {}, 0
                
            quality = min(100, (
                len([f for f in campos.values() if f.get('type')]) / len(campos) * 60 +
                len([f for f in campos.values() if f.get('description')]) / len(campos) * 20 +
                len([f for f in campos.values() if f.get('required') is not None]) / len(campos) * 20
            ))
            
            return campos, quality

        except Exception as e:
            print(f"Error en análisis básico: {str(e)}")
            return {}, 0

    def _infer_basic_type(self, value: str) -> str:
        """Infiere el tipo básico de un valor"""
        value = value.strip().lower()
        
        # Tipos numéricos
        if value.isdigit():
            return 'integer'
        if value.replace('.', '').isdigit() and value.count('.') == 1:
            return 'float'
            
        # Booleanos
        if value in ['true', 'false', 'yes', 'no', '1', '0']:
            return 'boolean'
            
        # Fechas
        if self._looks_like_date(value):
            return 'date'
            
        # Email
        if '@' in value and '.' in value.split('@')[1]:
            return 'email'
            
        # Teléfono
        if value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            return 'phone'
            
        return 'string'

    def _generate_description(self, name: str, value: str) -> str:
        """Genera una descripción para el campo"""
        name = name.replace('_', ' ').title()
        tipo = self._infer_basic_type(value)
        
        if tipo == 'string':
            return f"Campo de texto para {name}"
        elif tipo in ['integer', 'float']:
            return f"Valor numérico para {name}"
        elif tipo == 'boolean':
            return f"Indicador booleano de {name}"
        elif tipo == 'date':
            return f"Fecha de {name}"
        elif tipo == 'email':
            return f"Dirección de correo electrónico"
        elif tipo == 'phone':
            return f"Número de teléfono"
            
        return f"Campo para {name}"

    def _analyze_with_ai(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Análisis usando Google Cloud Vision"""
        if not self.vision_client:
            print("\n⚠️ Vision API no disponible")
            return {}, 0

        try:
            print("\nIniciando análisis con Google Cloud Vision...")
            with open(file_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.vision_client.document_text_detection(image=image)

            if not response.text_annotations:
                print("\n❌ No se detectó texto en el archivo")
                return {}, 0

            print("\n✅ Texto detectado correctamente")
            # Procesar resultados
            campos = self._process_vision_results(response.text_annotations)
            calidad = self._calculate_vision_quality(response)

            print(f"\nSe encontraron {len(campos)} campos")
            print(f"Calidad del análisis: {calidad:.1f}%")

            return campos, calidad

        except Exception as e:
            print(f"\n❌ Error en análisis con IA: {str(e)}")
            return {}, 0

    def _process_vision_results(self, annotations) -> Dict[str, Any]:
        """Procesa resultados de Vision API"""
        campos = {}
        
        # El primer elemento contiene el texto completo
        full_text = annotations[0].description if annotations else ""
        lines = full_text.split('\n')

        for line in lines:
            # Buscar patrones de campo
            if ':' in line:
                name, value = line.split(':', 1)
                name = name.strip()
                value = value.strip()
                
                campos[name] = {
                    'type': self._infer_type_with_ai(value),
                    'value': value,
                    'confidence': self._get_text_confidence(name, annotations[1:])
                }

        return campos

    def _calculate_vision_quality(self, response) -> float:
        """Calcula la calidad del análisis de Vision"""
        if not response.text_annotations:
            return 0

        # Calcular calidad basada en confianza y estructura
        confidence_scores = []
        for page in response.pages:
            for block in page.blocks:
                confidence_scores.append(block.confidence)

        if not confidence_scores:
            return 0

        # Calidad base en confianza de detección
        base_quality = sum(confidence_scores) / len(confidence_scores) * 100

        # Factores adicionales
        structure_bonus = 10 if len(response.text_annotations) > 1 else 0
        format_penalty = -20 if base_quality < 50 else 0

        final_quality = min(100, base_quality + structure_bonus + format_penalty)
        return final_quality

    def _infer_type_with_ai(self, value: str) -> str:
        """Infiere tipo de dato usando análisis avanzado"""
        # Primero intentar tipos básicos
        basic_type = self._infer_basic_type(value)
        if (basic_type != 'string'):
            return basic_type

        # Análisis avanzado para strings
        value_lower = value.lower()
        
        # Patrones específicos
        if any(word in value_lower for word in ['nombre', 'apellido', 'name']):
            return 'name'
        elif any(word in value_lower for word in ['fecha', 'date']):
            return 'date'
        elif any(word in value_lower for word in ['correo', 'email']):
            return 'email'
        elif any(word in value_lower for word in ['teléfono', 'phone']):
            return 'phone'
        elif len(value.split()) > 10:
            return 'text'
            
        return 'string'

    def _get_text_confidence(self, text: str, annotations) -> float:
        """Obtiene la confianza de detección para un texto específico"""
        for annotation in annotations:
            if text.lower() in annotation.description.lower():
                return annotation.confidence * 100
        return 0.0

    def _find_credentials(self) -> Optional[Path]:
        """Busca el archivo de credenciales de Google Cloud"""
        base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic")
        try:
            # Buscar archivo de credenciales por patrón
            credentials_file = next(base_path.glob("*-86851702569b.json"), None)
            if credentials_file:
                return credentials_file
        except Exception:
            pass
        return None

    def _mejorar_con_ia(self, campos: Dict[str, Any], file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Mejora los campos detectados usando IA"""
        try:
            # Usar el analizador avanzado para mejorar
            enhanced_fields = self.content_analyzer.analyze_document(file_path)
            
            # Combinar resultados
            campos_mejorados = campos.copy()
            for name, info in enhanced_fields.items():
                if name in campos_mejorados:
                    # Mejorar campo existente
                    campos_mejorados[name].update(info)
                else:
                    # Agregar nuevo campo detectado
                    campos_mejorados[name] = info
            
            # Recalcular calidad
            quality = min(100, (
                len([f for f in campos_mejorados.values() if f.get('type')]) / len(campos_mejorados) * 50 +
                len([f for f in campos_mejorados.values() if f.get('description')]) / len(campos_mejorados) * 30 +
                len([f for f in campos_mejorados.values() if f.get('validation_rules')]) / len(campos_mejorados) * 20
            ))
            
            return campos_mejorados, quality
            
        except Exception as e:
            print(f"Error al mejorar con IA: {str(e)}")
            return campos, 0

    def _evaluate_extraction_quality(self, fields: Dict[str, Any], base_quality: float) -> float:
        """Evalúa la calidad de la extracción similar a PDFExtractor"""
        if not fields:
            return 0

        # Métricas de calidad
        metrics = {
            'field_count': len(fields) / 10,  # Normalizado a 10 campos esperados
            'type_quality': sum(1 for f in fields.values() if f.get('type')) / len(fields),
            'description_quality': sum(1 for f in fields.values() if f.get('description')) / len(fields),
            'validation_quality': sum(1 for f in fields.values() if f.get('validation_rules')) / len(fields),
            'base_adjustment': base_quality / 100
        }

        # Calcular calidad final
        quality_score = sum(metrics.values()) / len(metrics) * 100
        return min(100, quality_score)

    def _mejorar_con_vision_api(self, campos: Dict[str, Any], file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Mejora usando Google Cloud Vision, similar a PDFExtractor"""
        if not self.vision_client:
            return campos, 0

        try:
            with open(file_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.vision_client.document_text_detection(image=image)

            if not response.text_annotations:
                return campos, 0

            # Procesar resultados de Vision
            campos_mejorados = self._process_vision_results(response.text_annotations)
            
            # Combinar resultados originales con mejoras
            for name, info in campos_mejorados.items():
                if name in campos:
                    campos[name].update(info)
                else:
                    campos[name] = info

            # Calcular nueva calidad
            nueva_calidad = self._calculate_vision_quality(response)
            return campos, nueva_calidad

        except Exception as e:
            print(f"\n❌ Error en Vision API: {str(e)}")
            return campos, 0

    def _analyze_with_ast(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Análisis usando AST (Abstract Syntax Tree) de Python"""
        try:
            import ast
            from typing import get_type_hints
            
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            campos = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extraer campos del modelo
                    for subnode in node.body:
                        if isinstance(subnode, ast.Assign):
                            field_info = self._extract_field_from_ast(subnode)
                            if field_info:
                                name, info = field_info
                                campos[name] = info

            quality = self._evaluate_ast_quality(campos)
            return campos, quality

        except Exception as e:
            print(f"Error en análisis AST: {str(e)}")
            return {}, 0

    def _extract_field_from_ast(self, node: ast.Assign) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Extrae información detallada de un campo desde AST"""
        try:
            field_name = node.targets[0].id
            field_info = {
                'type': None,
                'required': True,
                'validators': [],
                'choices': None,
                'help_text': None,
                'db_index': False,
                'unique': False,
                'default': None
            }

            # Analizar llamada al campo
            if isinstance(node.value, ast.Call):
                call = node.value
                field_info['type'] = self._get_field_type(call)
                
                # Analizar kwargs
                for keyword in call.keywords:
                    if keyword.arg == 'null' and keyword.value.value is True:
                        field_info['required'] = False
                    elif keyword.arg == 'blank' and keyword.value.value is True:
                        field_info['required'] = False
                    elif keyword.arg == 'choices':
                        field_info['choices'] = self._extract_choices_from_ast(keyword.value)
                    elif keyword.arg == 'help_text':
                        field_info['help_text'] = self._extract_help_text_from_ast(keyword.value)
                    elif keyword.arg == 'db_index':
                        field_info['db_index'] = keyword.value.value
                    elif keyword.arg == 'unique':
                        field_info['unique'] = keyword.value.value
                    elif keyword.arg == 'default':
                        field_info['default'] = self._extract_default_from_ast(keyword.value)
                    elif keyword.arg == 'validators':
                        field_info['validators'] = self._extract_validators_from_ast(keyword.value)

            return field_name, field_info

        except Exception as e:
            print(f"Error extrayendo campo: {str(e)}")
            return None

    def _get_field_type(self, call_node: ast.Call) -> str:
        """Determina el tipo exacto del campo Django"""
        try:
            field_class = call_node.func.attr  # Ej: CharField, IntegerField, etc.
            return {
                'CharField': {'type': 'string', 'max_length': self._get_max_length(call_node)},
                'TextField': {'type': 'text'},
                'IntegerField': {'type': 'integer', 'min_value': None, 'max_value': None},
                'FloatField': {'type': 'float'},
                'BooleanField': {'type': 'boolean'},
                'DateField': {'type': 'date'},
                'DateTimeField': {'type': 'datetime'},
                'ForeignKey': {'type': 'relation', 'model': self._get_related_model(call_node)},
                'ManyToManyField': {'type': 'relation', 'model': self._get_related_model(call_node), 'multiple': True},
                'OneToOneField': {'type': 'relation', 'model': self._get_related_model(call_node), 'unique': True}
            }.get(field_class, {'type': 'unknown'})

        except Exception:
            return {'type': 'unknown'}

    def _extract_choices_from_ast(self, node: ast.AST) -> List[Dict[str, str]]:
        """Extrae opciones de choices con toda la información"""
        choices = []
        if isinstance(node, ast.List):
            for elt in node.elts:
                if isinstance(elt, ast.Tuple):
                    try:
                        value = elt.elts[0].value
                        label = self._extract_translated_string(elt.elts[1])
                        choices.append({
                            'value': value,
                            'label': label,
                            'translated': True if 'gettext' in label or '_(' in label else False
                        })
                    except:
                        continue
        return choices

    def _extract_help_text_from_ast(self, node: ast.AST) -> Optional[str]:
        """Extrae y procesa el texto de ayuda"""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == '_':  # Texto traducible
                return {
                    'text': node.args[0].value,
                    'translatable': True
                }
        elif isinstance(node, ast.Str):
            return {
                'text': node.value,
                'translatable': False
            }
        return None

    def _extract_validators_from_ast(self, node: ast.AST) -> List[Dict[str, Any]]:
        """Extrae validadores y sus parámetros"""
        validators = []
        if isinstance(node, ast.List):
            for validator in node.elts:
                if isinstance(validator, ast.Call):
                    validator_info = {
                        'name': validator.func.id,
                        'params': {}
                    }
                    for kw in validator.keywords:
                        validator_info['params'][kw.arg] = self._extract_validator_param(kw.value)
                    validators.append(validator_info)
        return validators

    def _evaluate_ast_quality(self, campos: Dict[str, Any]) -> float:
        """Evalúa la calidad del análisis AST"""
        if not campos:
            return 0

        metrics = {
            'field_count': len(campos),
            'type_detection': sum(1 for f in campos.values() if f['type']),
            'choices_detection': sum(1 for f in campos.values() if f.get('choices')),
            'help_text_detection': sum(1 for f in campos.values() if f.get('help_text')),
            'validators_detection': sum(1 for f in campos.values() if f.get('validators')),
            'metadata_detection': sum(1 for f in campos.values() if f.get('db_index') or f.get('unique'))
        }

        weights = {
            'field_count': 0.2,
            'type_detection': 0.3,
            'choices_detection': 0.15,
            'help_text_detection': 0.1,
            'validators_detection': 0.15,
            'metadata_detection': 0.1
        }

        quality = sum(
            (metrics[key] / metrics['field_count']) * weight 
            for key, weight in weights.items() 
            if metrics['field_count'] > 0
        ) * 100

        return min(95, quality)  # Máximo 95% para AST

    def _extract_from_django_model(self, content: str) -> Dict[str, Any]:
        """Extrae definición de campos desde modelo Django"""
        campos = {}
        
        # Analizar campos básicos
        first_name = {
            'nombre': 'first_name',
            'tipo': 'string',
            'max_length': 50,
            'required': True,
            'validators': [{
                'type': 'regex',
                'pattern': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]{2,}$',
                'message': 'Solo se permiten letras, guiones y apóstrofes, mínimo 2 caracteres.'
            }],
            'db_index': True,
            'description': 'Nombre del Paciente'
        }

        last_name = {
            'nombre': 'last_name',
            'tipo': 'string',
            'max_length': 50,
            'required': True,
            'validators': [{
                'type': 'regex',
                'pattern': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]{2,}$',
                'message': 'Solo se permiten letras, guiones y apóstrofes, mínimo 2 caracteres.'
            }],
            'db_index': True,
            'description': 'Apellidos del Paciente'
        }

        gender = {
            'nombre': 'gender',
            'tipo': 'choice',
            'required': True,
            'choices': [
                {'value': 'M', 'label': 'Masculino'},
                {'value': 'F', 'label': 'Femenino'}
            ],
            'db_index': True,
            'description': 'Género del Paciente'
        }

        # Y así sucesivamente para cada campo...

        # Agregar todos los campos al diccionario
        campos['first_name'] = first_name
        campos['last_name'] = last_name
        campos['gender'] = gender
        # etc...

        return campos

    def _evaluate_quality(self, campos: Dict[str, Any]) -> float:
        """Evalúa la calidad de la extracción"""
        if not campos:
            return 0

        metrics = {
            'field_completeness': len(campos) / 10,  # Esperamos al menos 10 campos
            'validation_rules': sum(1 for f in campos.values() if f.get('validators')) / len(campos),
            'descriptions': sum(1 for f in campos.values() if f.get('description')) / len(campos),
            'choices': sum(1 for f in campos.values() if f.get('choices')) / len(campos)
        }

        quality = sum(metrics.values()) / len(metrics) * 100
        return min(100, quality)

    def _analyze_text_file(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Analiza archivo de texto plano"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            campos = {}
            quality_metrics = {
                'field_detection': 0,
                'type_inference': 0,
                'metadata_extraction': 0
            }
            
            # Analizar línea por línea
            for line in content.splitlines():
                if ':' in line or '=' in line:
                    # Extraer nombre y valor
                    separator = ':' if ':' in line else '='
                    name, value = line.split(separator, 1)
                    name = name.strip()
                    value = value.strip()
                    
                    # Inferir tipo y validaciones
                    field_type = self._infer_basic_type(value)
                    campos[name] = {
                        'type': field_type,
                        'required': '*' in line or '!' in line,
                        'description': self._generate_description(name, value)
                    }
                    
                    # Actualizar métricas
                    quality_metrics['field_detection'] += 1
                    if field_type != 'string':
                        quality_metrics['type_inference'] += 1
                    if campos[name]['description']:
                        quality_metrics['metadata_extraction'] += 1
            
            # Calcular calidad
            if campos:
                quality = (
                    quality_metrics['field_detection'] * 0.4 +
                    quality_metrics['type_inference'] * 0.3 +
                    quality_metrics['metadata_extraction'] * 0.3
                ) * 100 / max(1, len(campos))
            else:
                quality = 0
                
            return campos, quality
            
        except Exception as e:
            print(f"Error en análisis de texto: {str(e)}")
            return {}, 0

    def _analyze_json_file(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Analiza archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            campos = {}
            quality_metrics = {
                'field_detection': 0,
                'type_inference': 0,
                'validation_rules': 0
            }
            
            def process_dict(d: dict, prefix=''):
                for key, value in d.items():
                    field_name = f"{prefix}{key}" if prefix else key
                    
                    if isinstance(value, dict):
                        if 'type' in value:  # Es una definición de campo
                            campos[field_name] = {
                                'type': value.get('type', 'string'),
                                'required': value.get('required', True),
                                'description': value.get('description', ''),
                                'validators': value.get('validators', [])
                            }
                            
                            # Actualizar métricas
                            quality_metrics['field_detection'] += 1
                            if value.get('type'):
                                quality_metrics['type_inference'] += 1
                            if value.get('validators'):
                                quality_metrics['validation_rules'] += 1
                        else:
                            process_dict(value, f"{field_name}.")
                    else:
                        # Inferir tipo para valores simples
                        campos[field_name] = {
                            'type': self._infer_basic_type(str(value)),
                            'required': True,
                            'description': self._generate_description(field_name, str(value))
                        }
                        quality_metrics['field_detection'] += 1
            
            process_dict(data)
            
            # Calcular calidad
            if campos:
                quality = (
                    quality_metrics['field_detection'] * 0.4 +
                    quality_metrics['type_inference'] * 0.3 +
                    quality_metrics['validation_rules'] * 0.3
                ) * 100 / max(1, len(campos))
            else:
                quality = 0
                
            return campos, quality
            
        except Exception as e:
            print(f"Error en análisis JSON: {str(e)}")
            return {}, 0

    def _analyze_yaml_file(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Analiza archivo YAML"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Usar el mismo procesamiento que JSON
            return self._process_structured_data(data)
            
        except Exception as e:
            print(f"Error en análisis YAML: {str(e)}")
            return {}, 0

    def _process_structured_data(self, data: Dict) -> Tuple[Dict[str, Any], float]:
        """Procesa datos estructurados (común para JSON y YAML)"""
        campos = {}
        quality_metrics = {
            'field_detection': 0,
            'type_inference': 0,
            'validation_rules': 0
        }
        
        def process_dict(d: dict, prefix=''):
            for key, value in d.items():
                field_name = f"{prefix}{key}" if prefix else key
                
                if isinstance(value, dict):
                    if 'type' in value:  # Es una definición de campo
                        campos[field_name] = {
                            'type': value.get('type', 'string'),
                            'required': value.get('required', True),
                            'description': value.get('description', ''),
                            'validators': value.get('validators', [])
                        }
                        
                        # Actualizar métricas
                        quality_metrics['field_detection'] += 1
                        if value.get('type'):
                            quality_metrics['type_inference'] += 1
                        if value.get('validators'):
                            quality_metrics['validation_rules'] += 1
                    else:
                        process_dict(value, f"{field_name}.")
                else:
                    # Inferir tipo para valores simples
                    campos[field_name] = {
                        'type': self._infer_basic_type(str(value)),
                        'required': True,
                        'description': self._generate_description(field_name, str(value))
                    }
                    quality_metrics['field_detection'] += 1
        
        process_dict(data)
        
        # Calcular calidad
        if campos:
            quality = (
                quality_metrics['field_detection'] * 0.4 +
                quality_metrics['type_inference'] * 0.3 +
                quality_metrics['validation_rules'] * 0.3
            ) * 100 / max(1, len(campos))
        else:
            quality = 0
            
        return campos, quality

    def _analyze_excel_file(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Analiza archivo Excel"""
        try:
            df = pd.read_excel(file_path)
            
            campos = {}
            quality_metrics = {
                'field_detection': 0,
                'type_inference': 0,
                'metadata_extraction': 0
            }
            
            # Analizar cada columna
            for column in df.columns:
                # Inferir tipo basado en los datos
                col_data = df[column].dropna()
                if len(col_data) > 0:
                    sample = str(col_data.iloc[0])
                    field_type = self._infer_basic_type(sample)
                    
                    campos[column] = {
                        'type': field_type,
                        'required': df[column].notna().all(),
                        'description': self._generate_description(column, sample),
                        'examples': col_data.head(3).tolist()
                    }
                    
                    # Actualizar métricas
                    quality_metrics['field_detection'] += 1
                    if field_type != 'string':
                        quality_metrics['type_inference'] += 1
                    if campos[column]['description']:
                        quality_metrics['metadata_extraction'] += 1
            
            # Calcular calidad
            if campos:
                quality = (
                    quality_metrics['field_detection'] * 0.4 +
                    quality_metrics['type_inference'] * 0.3 +
                    quality_metrics['metadata_extraction'] * 0.3
                ) * 100 / max(1, len(campos))
            else:
                quality = 0
                
            return campos, quality
            
        except Exception as e:
            print(f"Error en análisis Excel: {str(e)}")
            return {}, 0

    def crear_nueva_plantilla(self) -> Optional[Dict[str, Any]]:
        """Crea una nueva plantilla desde un archivo base"""
        try:
            # 1. Mostrar y seleccionar archivo base
            archivo_base = self._mostrar_archivos_codigos()
            if not archivo_base:
                return None

            # 2. Analizar archivo
            print(f"\nAnalizando archivo: {archivo_base.name}")
            campos, tipo_inferido = self._analizar_archivo(archivo_base)
            if not campos:
                return None

            # 3. Generar plantilla
            nueva_plantilla = {
                'nombre': archivo_base.stem,
                'tipo': tipo_inferido,
                'fecha_generacion': datetime.now().isoformat(),
                'campos': campos
            }

            # 4. Guardar plantilla
            self._guardar_plantilla(nueva_plantilla, tipo_inferido)  # <-- Agregado tipo_doc
            return nueva_plantilla

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return None

    def _mostrar_archivos_codigos(self) -> Optional[Path]:
        """Muestra y permite seleccionar archivos de la carpeta Campos Codigos"""
        try:
            print("\n=== ARCHIVOS BASE DISPONIBLES ===")
            archivos = list(self.campos_path.glob('*.*'))
            
            if not archivos:
                print(f"\n❌ No se encontraron archivos en {self.campos_path}")
                return None

            # Mostrar archivos
            for idx, archivo in enumerate(archivos, 1):
                print(f"{idx}. {archivo.name}")

            # Seleccionar archivo
            while True:
                try:
                    idx = int(input("\nSeleccione archivo (0 para cancelar): ")) - 1
                    if idx == -1:
                        return None
                    if 0 <= idx < len(archivos):
                        return archivos[idx]
                    print("Opción no válida")
                except ValueError:
                    print("Por favor ingrese un número")

        except Exception as e:
            print(f"\n❌ Error listando archivos: {str(e)}")
            return None

    def _analizar_archivo(self, archivo_base: Path) -> Tuple[Dict[str, Any], str]:
        """Analiza el archivo base y extrae campos y tipo inferido"""
        resultados = []
        
        # 1. Leer contenido del archivo
        try:
            with open(archivo_base, 'r', encoding='utf-8') as f:
                contenido = f.read()
        except Exception as e:
            print(f"\n❌ Error leyendo archivo: {str(e)}")
            return {}, ""

        # 2. Intentar cada método de análisis
        for method_name, (analyzer, base_quality) in self.extraction_methods.items():
            print(f"\nProbando método: {method_name}")
            try:
                fields, quality = analyzer(archivo_base)
                if fields:
                    resultados.append((fields, method_name, quality))
                    print(f"✓ {len(fields)} campos encontrados (calidad: {quality:.1f}%)")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                continue

        if not resultados:
            print("\n❌ No se pudo extraer estructura del archivo")
            return {}, ""

        # 3. Seleccionar mejor resultado
        campos, metodo, calidad = max(resultados, key=lambda x: x[2])
        print(f"\n✅ Método más efectivo: {metodo} ({calidad:.1f}%)")
        
        # 4. Inferir tipo de documento
        tipo_inferido = self._inferir_tipo_documento(campos)
        print(f"✅ Tipo inferido: {tipo_inferido}")

        return campos, tipo_inferido

    def _inferir_tipo_documento(self, campos: Dict[str, Any]) -> str:
        """Infiere el tipo de documento basado en los campos"""
        campos_lower = [k.lower() for k in campos.keys()]
        
        if 'paciente_id' in campos_lower or 'patient_id' in campos_lower:
            if any(f in campos_lower for f in ['evaluacion', 'evaluation', 'farc']):
                return 'FARC'
            elif any(f in campos_lower for f in ['historia', 'bio', 'biography']):
                return 'BIO'
            elif any(f in campos_lower for f in ['plan', 'mtp', 'training']):
                return 'MTP'
                
        return 'import_template'  # Tipo por defecto

    def _generar_indices_busqueda(self, campos: Dict[str, Any]) -> Dict[str, Any]:
        """Genera índices de búsqueda para los campos"""
        indices = {
            'por_tipo': {
                'string': [],
                'relation': [],
                'date': []
            },
            'requeridos': campos.copy(),  # Por defecto todos son requeridos
            'opcionales': [],
            'con_validacion': []
        }

        # Clasificar campos por tipo basado en nombres comunes
        for campo in campos:
            if any(date_hint in campo.lower() 
                  for date_hint in ['date', 'fecha', 'born', 'death']):
                indices['por_tipo']['date'].append(campo)
            elif any(rel_hint in campo.lower() 
                    for rel_hint in ['_id', 'relation', 'foreign']):
                indices['por_tipo']['relation'].append(campo)
            else:
                indices['por_tipo']['string'].append(campo)

        return indices

    def _looks_like_date(self, value: str) -> bool:
        """Verifica si un valor parece ser una fecha"""
        import re
        
        # Patrones comunes de fecha
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',                    # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',                    # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}',                    # DD-MM-YYYY
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'  # 1 Jan 2024
        ]
        
        return any(re.match(pattern, value.strip()) for pattern in date_patterns)

    def _extract_django_field(self, match: re.Match) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Extrae información de un campo Django"""
        try:
            name = match.group(1)
            field_type = match.group(2)
            options = match.group(3)

            field_info = {
                'type': self._map_django_type(field_type),
                'required': 'null=True' not in options,
                'description': f"Campo {name} de tipo {field_type}"
            }

            # Extraer opciones adicionales
            if 'choices=' in options:
                field_info['choices'] = self._extract_choices(options)
            if 'help_text=' in options:
                field_info['help_text'] = self._extract_help_text(options)

            return name, field_info
        except Exception:
            return None

    def listar_plantillas(self, tipo: str = "global") -> List[Dict[str, Any]]:
        """Lista las plantillas disponibles del tipo especificado"""
        plantillas = []
        
        try:
            # Definir la ruta base para buscar plantillas según el tipo
            if tipo == "global":
                base_dir = self.templates_base / "Campos Master Global"
            elif tipo == "codigo":
                base_dir = self.templates_base / "Campos Codigos"
            else:
                print(f"[DEBUG-PLANTILLAS] Tipo de plantilla no reconocido: {tipo}")
                return plantillas
            
            # Verificar que el directorio existe
            if not base_dir.exists():
                print(f"[DEBUG-PLANTILLAS] Directorio no encontrado: {base_dir}")
                return plantillas
            
            print(f"[DEBUG-PLANTILLAS] Buscando plantillas en: {base_dir}")
            
            # Listar todos los archivos en el directorio para diagnóstico
            todos_archivos = list(base_dir.iterdir())
            print(f"[DEBUG-PLANTILLAS] Total de archivos en directorio: {len(todos_archivos)}")
            for archivo in todos_archivos:
                print(f"[DEBUG-PLANTILLAS] Archivo detectado: {archivo.name} (Extensión: {archivo.suffix})")
            
            # Buscar archivos con extensiones compatibles (.json, .yaml, .yml)
            archivos_template = []
            for extension in ["*.json", "*.yaml", "*.yml"]:
                archivos_template.extend(base_dir.glob(extension))
            
            print(f"[DEBUG-PLANTILLAS] Archivos con extensión compatible: {len(archivos_template)}")
            
            # Procesar cada archivo compatible
            for archivo in archivos_template:
                try:
                    # Cargar datos según la extensión del archivo
                    data = None
                    if archivo.suffix.lower() == '.json':
                        with open(archivo, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    elif archivo.suffix.lower() in ['.yaml', '.yml']:
                        with open(archivo, 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f)
                    
                    if data is None:
                        print(f"[DEBUG-PLANTILLAS] No se pudo cargar archivo: {archivo.name}")
                        continue
                        
                    # Procesar los datos de la plantilla
                    num_campos = 0
                    campos = data.get('campos', {})
                    
                    # Contar campos según formato (pueden ser dict o list)
                    if isinstance(campos, dict):
                        num_campos = len(campos)
                    elif isinstance(campos, list):
                        num_campos = len(campos)
                    
                    # Extraer información relevante para la lista
                    plantillas.append({
                        'nombre': archivo.stem,
                        'ruta': archivo,
                        'fecha_creacion': datetime.fromtimestamp(archivo.stat().st_ctime).strftime('%Y-%m-%d %H:%M'),
                        'num_campos': num_campos,
                        'descripcion': data.get('descripcion', 'Sin descripción')
                    })
                    print(f"[DEBUG-PLANTILLAS] Plantilla procesada: {archivo.name} ({num_campos} campos)")
                except Exception as e:
                    print(f"[DEBUG-ERROR] Error procesando plantilla {archivo.name}: {e}")
                    continue
            
            print(f"[DEBUG-PLANTILLAS] Total de plantillas procesadas correctamente: {len(plantillas)}")
            
        except Exception as e:
            print(f"[DEBUG-ERROR] Error general al listar plantillas: {e}")
        
        return plantillas

    def _load_master_template(self) -> Optional[Dict[str, Any]]:
        """Carga la plantilla master de importación"""
        # Directorio específico de templates (ahora solo Campos Master Global)
        template_base = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/templates/Campos Master Global")
        
        print(f"\n[DEBUG] Buscando templates en: {template_base}")
        
        if not template_base.exists():
            print(f"\n❌ No se encontró el directorio de templates: {template_base}")
            return None

        # Listar todos los archivos en el directorio para diagnóstico
        try:
            todos_archivos = list(template_base.iterdir())
            print(f"\n[DEBUG] Total archivos en directorio: {len(todos_archivos)}")
            for archivo in todos_archivos:
                print(f"[DEBUG] Archivo en directorio: {archivo.name}")
        except Exception as e:
            print(f"\n[DEBUG] Error al listar archivos: {e}")

        # Buscar archivos compatibles (JSON, YAML, YML)
        templates_encontrados = []
        for extension in ["*.json", "*.yaml", "*.yml"]:
            for template_path in template_base.glob(extension):
                try:
                    print(f"\n[DEBUG] Intentando procesar: {template_path.name}")
                    
                    # Cargar datos según extensión
                    metadata = None
                    if template_path.suffix.lower() == '.json':
                        with open(template_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    elif template_path.suffix.lower() in ['.yaml', '.yml']:
                        with open(template_path, 'r', encoding='utf-8') as f:
                            metadata = yaml.safe_load(f)
                            
                    if metadata is None:
                        print(f"[DEBUG] No se pudo cargar {template_path.name}")
                        continue
                    
                    # Determinar cantidad de campos
                    campos = metadata.get('campos', {})
                    num_campos = 0
                    if isinstance(campos, dict):
                        num_campos = len(campos)
                    elif isinstance(campos, list):
                        num_campos = len(campos)
                    
                    # Solo los archivos que tienen la estructura esperada
                    templates_encontrados.append({
                        'path': template_path,
                        'nombre': template_path.name,
                        'tipo': metadata.get('tipo', metadata.get('type', 'desconocido')),
                        'num_campos': num_campos,
                        'fecha': metadata.get('fecha_generacion', ''),
                        'campos': list(campos.keys()) if isinstance(campos, dict) else [c.get('nombre', f'campo_{i}') for i, c in enumerate(campos)] if isinstance(campos, list) else []
                    })
                    print(f"[DEBUG] Template procesado: {template_path.name} ({num_campos} campos)")
                except Exception as e:
                    print(f"\n⚠️ Error procesando template {template_path.name}: {str(e)}")
                    continue

        if not templates_encontrados:
            print("\n❌ No se encontraron templates disponibles")
            return None

        # Ordenar por nombre para mejor organización
        templates_encontrados.sort(key=lambda x: x['nombre'])

        # Mostrar templates disponibles
        print(f"\n=== TEMPLATES DISPONIBLES ({len(templates_encontrados)}) ===")
        for idx, template in enumerate(templates_encontrados, 1):
            print(f"\n{idx}. {template['nombre']}")
            print(f"   Tipo: {template['tipo']}")
            print(f"   Campos: {template['num_campos']}")
            if template['campos']:
                print("   Campos principales:")
                # Mostrar los primeros 5 campos como preview
                for i, campo in enumerate(template['campos'][:5]):
                    print(f"    - {campo}")
                if len(template['campos']) > 5:
                    print(f"    ... y {len(template['campos']) - 5} campos más")

        # Permitir selección
        while True:
            try:
                seleccion = input("\nSeleccione el template a usar (0 para cancelar): ").strip()
                if seleccion == '0':
                    return None

                idx = int(seleccion) - 1
                if 0 <= idx < len(templates_encontrados):
                    template_seleccionado = templates_encontrados[idx]
                    print(f"\n✅ Template seleccionado: {template_seleccionado['nombre']}")
                    
                    # Cargar template completo según su extensión
                    template_path = template_seleccionado['path']
                    if template_path.suffix.lower() == '.json':
                        with open(template_path, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    elif template_path.suffix.lower() in ['.yaml', '.yml']:
                        with open(template_path, 'r', encoding='utf-8') as f:
                            return yaml.safe_load(f)
                else:
                    print("❌ Selección no válida")
            except ValueError:
                print("❌ Por favor ingrese un número válido")
            except Exception as e:
                print(f"❌ Error cargando template: {str(e)}")
                return None

    def listar_plantillas(self, tipo: str = "global") -> List[Dict[str, Any]]:
        """Lista las plantillas disponibles del tipo especificado"""
        plantillas = []
        
        try:
            # Definir la ruta base para buscar plantillas según el tipo
            if (tipo == "global"):
                base_dir = self.templates_base / "Campos Master Global"
            elif (tipo == "codigo"):
                base_dir = self.templates_base / "Campos Codigos"
            else:
                print(f"[DEBUG-PLANTILLAS] Tipo de plantilla no reconocido: {tipo}")
                return plantillas
            
            # Verificar que el directorio existe
            if not base_dir.exists():
                print(f"[DEBUG-PLANTILLAS] Directorio no encontrado: {base_dir}")
                return plantillas
            
            print(f"[DEBUG-PLANTILLAS] Buscando plantillas en: {base_dir}")
            
            # Buscar archivos .json en el directorio
            for archivo in base_dir.glob("*.json"):
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Extraer información relevante para la lista
                    plantillas.append({
                        'nombre': archivo.stem,
                        'ruta': archivo,
                        'fecha_creacion': datetime.fromtimestamp(archivo.stat().st_ctime).strftime('%Y-%m-%d %H:%M'),
                        'num_campos': len(data.get('campos', [])),
                        'descripcion': data.get('descripcion', 'Sin descripción')
                    })
                    print(f"[DEBUG-PLANTILLAS] Plantilla encontrada: {archivo.name}")
                except Exception as e:
                    print(f"[DEBUG-ERROR] Error leyendo plantilla {archivo.name}: {e}")
                    continue
            
            print(f"[DEBUG-PLANTILLAS] Total de plantillas encontradas: {len(plantillas)}")
            
        except Exception as e:
            print(f"[DEBUG-ERROR] Error al listar plantillas: {e}")
        
        return plantillas

    def crear_plantilla(self, nombre: str, tipo: str, campos: List[Dict[str, Any]], 
                       descripcion: str = "") -> Optional[Path]:
        """Crea una nueva plantilla con los campos especificados"""
        # Determinar directorio de destino
        if tipo == "global":
            destino = self.global_templates
        elif tipo == "codigo":
            destino = self.code_templates
        else:
            print(f"Tipo de plantilla no válido: {tipo}")
            return None
        
        # Validar nombre
        if not nombre:
            print("El nombre de la plantilla no puede estar vacío")
            return None
            
        # Construir nombre de archivo
        archivo = destino / f"{nombre}.json"
        
        # Verificar si ya existe
        if archivo.exists():
            if input(f"La plantilla {nombre} ya existe. ¿Sobrescribir? (S/N): ").upper() != 'S':
                return None
        
        # Crear contenido de la plantilla
        plantilla = {
            'nombre': nombre,
            'tipo': tipo,
            'descripcion': descripcion,
            'fecha_generacion': datetime.now().isoformat(),
            'campos': campos
        }
        
        # Guardar la plantilla
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(plantilla, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Plantilla '{nombre}' guardada exitosamente")
            return archivo
        except Exception as e:
            print(f"\n❌ Error al guardar la plantilla: {str(e)}")
            return None

    def cargar_plantilla(self, nombre: str, tipo: str = "global") -> Optional[Dict[str, Any]]:
        """Carga una plantilla existente por nombre y tipo"""
        # Determinar directorio
        if tipo == "global":
            base_dir = self.global_templates
        elif tipo == "codigo":
            base_dir = self.code_templates
        else:
            print(f"Tipo de plantilla no reconocido: {tipo}")
            return None
        
        # Buscar archivo
        archivo = base_dir / f"{nombre}.json"
        if not archivo.exists():
            print(f"Plantilla '{nombre}' no encontrada")
            return None
        
        # Cargar contenido
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar plantilla: {str(e)}")
            return None

    def seleccionar_plantilla(self, tipo: str = "global") -> Optional[Dict[str, Any]]:
        """Muestra un menú para seleccionar una plantilla existente"""
        plantillas = self.listar_plantillas(tipo)
        
        if not plantillas:
            print(f"\nNo hay plantillas {tipo} disponibles")
            return None
            
        print(f"\n=== PLANTILLAS {tipo.upper()} DISPONIBLES ===")
        for idx, plantilla in enumerate(plantillas, 1):
            print(f"\n{idx}. {plantilla['nombre']}")
            print(f"   Descripción: {plantilla['descripcion']}")
            print(f"   Campos: {plantilla['num_campos']}")
            print(f"   Fecha: {plantilla['fecha_creacion']}")
        
        try:
            seleccion = input("\nSeleccione la plantilla (0 para cancelar): ")
            if seleccion == '0':
                return None
                
            idx = int(seleccion) - 1
            if 0 <= idx < len(plantillas):
                return self.cargar_plantilla(plantillas[idx]['nombre'], tipo)
            else:
                print("Selección no válida")
                return None
        except ValueError:
            print("Por favor ingrese un número válido")
            return None

    def solicitar_campos_plantilla(self) -> List[Dict[str, Any]]:
        """Solicita al usuario los campos para una nueva plantilla"""
        campos = []
        print("\n=== DEFINICIÓN DE CAMPOS ===")
        print("Ingrese datos de cada campo. Deje el nombre en blanco para finalizar.")
        
        while True:
            nombre = input("\nNombre del campo: ").strip()
            if not nombre:
                break
                
            tipo = input("Tipo de dato (texto, numero, fecha): ").strip().lower()
            requerido = input("¿Es requerido? (S/N): ").upper() == 'S'
            descripcion = input("Descripción: ").strip()
            
            campos.append({
                'nombre': nombre,
                'tipo': tipo,
                'requerido': requerido,
                'descripcion': descripcion
            })
        
        return campos

    def analizar_y_generar_plantilla(self, tipo_doc: str) -> Optional[Path]:
        """Analiza estructura de un tipo de documento y genera plantilla"""
        print("\n=== GENERACIÓN DE PLANTILLA ===")
        
        if tipo_doc == 'import_template':
            # Generar plantilla para importación
            nombre = input("\nNombre para la plantilla: ").strip()
            if not nombre:
                print("Nombre requerido")
                return None
                
            descripcion = input("Descripción: ").strip()
            
            # Solicitar campos
            print("\nDefina los campos a incluir en la plantilla:")
            campos = self.solicitar_campos_plantilla()
            
            if not campos:
                print("No se definieron campos")
                return None
                
            # Crear la plantilla
            return self.crear_plantilla(nombre, "global", campos, descripcion)
        else:
            print(f"Tipo de documento no soportado: {tipo_doc}")
            return None

    def _validate_template_structure(self, template: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Valida la estructura de una plantilla y devuelve (es_valido, lista_errores)"""
        errores = []
        
        # 1. Verificar campos obligatorios a nivel de plantilla
        campos_requeridos = ['nombre', 'tipo', 'campos', 'fecha_generacion']
        for campo in campos_requeridos:
            if campo not in template:
                errores.append(f"Falta campo requerido '{campo}' en la plantilla")
        
        # 2. Verificar que campos sea un diccionario
        if 'campos' in template and not isinstance(template['campos'], dict):
            errores.append("El campo 'campos' debe ser un diccionario")
            return False, errores  # Error crítico, terminamos aquí
        
        # 3. Verificar estructura de cada campo
        if 'campos' in template and isinstance(template['campos'], dict):
            for nombre_campo, datos_campo in template['campos'].items():
                # Verificar que cada campo sea un diccionario
                if not isinstance(datos_campo, dict):
                    errores.append(f"El campo '{nombre_campo}' debe ser un diccionario")
                    continue
                    
                # Verificar que tenga un tipo definido
                if 'type' not in datos_campo and 'tipo' not in datos_campo:
                    errores.append(f"El campo '{nombre_campo}' debe tener un tipo definido")
                
                # Si tiene validadores, verificar que sean correctos
                if 'validators' in datos_campo and not isinstance(datos_campo['validators'], list):
                    errores.append(f"Los validadores del campo '{nombre_campo}' deben ser una lista")
        
        # 4. Determinar resultado
        es_valido = len(errores) == 0
        return es_valido, errores

    def create_empty_template(self, tipo: str = "import_template") -> Dict[str, Any]:
        """Crea una plantilla vacía pero válida"""
        return {
            'nombre': f"plantilla_vacia_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'tipo': tipo,
            'fecha_generacion': datetime.now().isoformat(),
            'campos': {},  # Diccionario vacío pero válido
            'descripcion': 'Plantilla generada automáticamente'
        }
    
    def fix_template_structure(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta corregir problemas estructurales en una plantilla"""
        plantilla_corregida = template.copy() if template else {}
        
        # Corregir campos obligatorios faltantes
        if 'nombre' not in plantilla_corregida:
            plantilla_corregida['nombre'] = f"plantilla_corregida_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        if 'tipo' not in plantilla_corregida:
            plantilla_corregida['tipo'] = "import_template"
            
        if 'fecha_generacion' not in plantilla_corregida:
            plantilla_corregida['fecha_generacion'] = datetime.now().isoformat()
            
        if 'descripcion' not in plantilla_corregida:
            plantilla_corregida['descripcion'] = 'Plantilla corregida automáticamente'
        
        # Asegurar que 'campos' sea un diccionario
        if 'campos' not in plantilla_corregida or not isinstance(plantilla_corregida['campos'], dict):
            # Si existe pero no es un diccionario, intentamos convertirlo
            if 'campos' in plantilla_corregida and isinstance(plantilla_corregida['campos'], list):
                # Convertir lista de campos a diccionario
                campos_dict = {}
                for idx, campo in enumerate(plantilla_corregida['campos']):
                    if isinstance(campo, dict) and 'nombre' in campo:
                        campos_dict[campo['nombre']] = campo
                    else:
                        campos_dict[f"campo_{idx+1}"] = campo if isinstance(campo, dict) else {'valor': campo}
                plantilla_corregida['campos'] = campos_dict
            else:
                # Si no existe o no se puede convertir, creamos un diccionario vacío
                plantilla_corregida['campos'] = {}
        
        return plantilla_corregida

    def modificar_plantilla(self) -> None:
        """Permite modificar una plantilla existente"""
        print("\n=== MODIFICACIÓN DE PLANTILLA ===")
        
        # 1. Seleccionar tipo de plantilla a modificar
        print("\nSeleccione el tipo de plantilla:")
        print("1. Plantilla global")
        print("2. Plantilla de código")
        print("0. Cancelar")
        
        tipo_opcion = input("\nSeleccione opción: ").strip()
        if tipo_opcion == "0":
            return
        
        tipo = "global" if tipo_opcion == "1" else "codigo" if tipo_opcion == "2" else None
        if not tipo:
            print("Opción no válida")
            return
        
        # 2. Cargar la plantilla existente
        plantilla = self.seleccionar_plantilla(tipo)
        if not plantilla:
            print("\n❌ No se seleccionó ninguna plantilla.")
            return
            
        # 3. Verificar estructura de la plantilla
        es_valido, errores = self._validate_template_structure(plantilla)
        if not es_valido:
            print("\n⚠️ La plantilla tiene problemas estructurales:")
            for error in errores:
                print(f"  • {error}")
            
            if input("¿Desea intentar corregir la estructura automáticamente? (S/N): ").upper() != 'S':
                return
                
            # Intentar corregir estructura
            plantilla = self.fix_template_structure(plantilla)
            print("\n✅ Estructura corregida.")
        
        # 4. Menú de modificación
        while True:
            print("\n=== OPCIONES DE MODIFICACIÓN ===")
            print(f"Plantilla: {plantilla.get('nombre', 'Sin nombre')}")
            print(f"Tipo: {plantilla.get('tipo', 'No especificado')}")
            print(f"Campos: {len(plantilla.get('campos', {}))}")
            
            print("\n1. Modificar metadatos (nombre, descripción)")
            print("2. Añadir nuevo campo")
            print("3. Modificar campo existente")
            print("4. Eliminar campo existente")
            print("5. Ver todos los campos")
            print("0. Guardar y salir")
            
            opcion = input("\nSeleccione opción: ").strip()
            
            if opcion == "0":
                # Guardar cambios
                tipo_guardado = plantilla.get('tipo', tipo)
                nombre = plantilla.get('nombre', 'plantilla_modificada')
                
                ruta = self._guardar_plantilla_modificada(plantilla, tipo_guardado, nombre)
                if ruta:
                    print(f"\n✅ Plantilla guardada en: {ruta}")
                return
            
            elif opcion == "1":
                # Modificar metadatos
                plantilla = self._modificar_metadatos(plantilla)
                
            elif opcion == "2":
                # Añadir nuevo campo
                plantilla = self._anadir_campo(plantilla)
                
            elif opcion == "3":
                # Modificar campo existente
                plantilla = self._modificar_campo(plantilla)
                
            elif opcion == "4":
                # Eliminar campo existente
                plantilla = self._eliminar_campo(plantilla)
                
            elif opcion == "5":
                # Ver todos los campos
                self._mostrar_campos(plantilla)
                
            else:
                print("Opción no válida")
    
    def _modificar_metadatos(self, plantilla: Dict[str, Any]) -> Dict[str, Any]:
        """Modifica los metadatos básicos de la plantilla"""
        print("\n=== MODIFICACIÓN DE METADATOS ===")
        
        # Mostrar metadatos actuales
        print(f"Nombre actual: {plantilla.get('nombre', 'No definido')}")
        print(f"Tipo actual: {plantilla.get('tipo', 'No definido')}")
        print(f"Descripción actual: {plantilla.get('descripcion', 'Sin descripción')}")
        
        # Solicitar nuevos valores
        nuevo_nombre = input("\nNuevo nombre (Enter para mantener): ").strip()
        if nuevo_nombre:
            plantilla['nombre'] = nuevo_nombre
            
        nuevo_tipo = input("Nuevo tipo (Enter para mantener): ").strip()
        if nuevo_tipo:
            plantilla['tipo'] = nuevo_tipo
            
        nueva_desc = input("Nueva descripción (Enter para mantener): ").strip()
        if nueva_desc:
            plantilla['descripcion'] = nueva_desc
        
        # Actualizar fecha de generación
        plantilla['fecha_generacion'] = datetime.now().isoformat()
        
        print("\n✅ Metadatos actualizados")
        return plantilla
    
    def _anadir_campo(self, plantilla: Dict[str, Any]) -> Dict[str, Any]:
        """Añade un nuevo campo a la plantilla"""
        print("\n=== AÑADIR NUEVO CAMPO ===")
        
        # Verificar que existe la sección de campos
        if 'campos' not in plantilla or not isinstance(plantilla['campos'], dict):
            plantilla['campos'] = {}
            
        # Solicitar datos del nuevo campo
        nombre = input("\nNombre del campo: ").strip()
        if not nombre:
            print("❌ El nombre del campo no puede estar vacío")
            return plantilla
            
        if nombre in plantilla['campos']:
            print(f"⚠️ El campo '{nombre}' ya existe. Use la opción modificar para cambiarlo.")
            return plantilla
            
        tipo = input("Tipo de dato (texto, numero, fecha, booleano...): ").strip()
        requerido = input("¿Es requerido? (S/N): ").upper() == 'S'
        descripcion = input("Descripción: ").strip()
        
        # Crear estructura del campo
        campo_nuevo = {
            'type': tipo,
            'required': requerido,
            'description': descripcion
        }
        
        # Validadores opcionales
        if input("¿Desea añadir validadores? (S/N): ").upper() == 'S':
            campo_nuevo['validators'] = self._solicitar_validadores(tipo)
            
        # Añadir a la plantilla
        plantilla['campos'][nombre] = campo_nuevo
        
        print(f"\n✅ Campo '{nombre}' añadido correctamente")
        return plantilla
    
    def _modificar_campo(self, plantilla: Dict[str, Any]) -> Dict[str, Any]:
        """Modifica un campo existente en la plantilla"""
        print("\n=== MODIFICAR CAMPO EXISTENTE ===")
        
        # Verificar que existen campos
        if 'campos' not in plantilla or not plantilla['campos']:
            print("❌ La plantilla no tiene campos definidos")
            return plantilla
            
        # Mostrar campos disponibles
        self._mostrar_campos(plantilla)
        
        # Seleccionar campo a modificar
        nombre_campo = input("\nNombre del campo a modificar (Enter para cancelar): ").strip()
        if not nombre_campo:
            return plantilla
            
        if nombre_campo not in plantilla['campos']:
            print(f"❌ El campo '{nombre_campo}' no existe")
            return plantilla
            
        campo = plantilla['campos'][nombre_campo]
        
        # Mostrar opciones de modificación
        print("\n=== OPCIONES DE MODIFICACIÓN ===")
        print("1. Cambiar tipo")
        print("2. Cambiar estado requerido")
        print("3. Cambiar descripción")
        print("4. Modificar validadores")
        print("0. Volver")
        
        opcion = input("\nSeleccione opción: ").strip()
        
        if opcion == "1":
            nuevo_tipo = input(f"Tipo actual: {campo.get('type', 'No definido')}\nNuevo tipo: ").strip()
            if nuevo_tipo:
                campo['type'] = nuevo_tipo
                print("✅ Tipo actualizado")
                
        elif opcion == "2":
            estado_actual = "Sí" if campo.get('required', False) else "No"
            nuevo_estado = input(f"¿Requerido? (actual: {estado_actual}) (S/N): ").upper() == 'S'
            campo['required'] = nuevo_estado
            print("✅ Estado requerido actualizado")
            
        elif opcion == "3":
            desc_actual = campo.get('description', '')
            nueva_desc = input(f"Descripción actual: {desc_actual}\nNueva descripción: ").strip()
            if nueva_desc:
                campo['description'] = nueva_desc
                print("✅ Descripción actualizada")
                
        elif opcion == "4":
            if 'validators' in campo:
                print("Validadores actuales:")
                print(campo['validators'])
                
            if input("¿Desea redefinir los validadores? (S/N): ").upper() == 'S':
                campo['validators'] = self._solicitar_validadores(campo.get('type', 'string'))
                print("✅ Validadores actualizados")
        
        return plantilla
    
    def _eliminar_campo(self, plantilla: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un campo existente de la plantilla"""
        print("\n=== ELIMINAR CAMPO ===")
        
        # Verificar que existen campos
        if 'campos' not in plantilla or not plantilla['campos']:
            print("❌ La plantilla no tiene campos definidos")
            return plantilla
            
        # Mostrar campos disponibles
        self._mostrar_campos(plantilla)
        
        # Seleccionar campo a eliminar
        nombre_campo = input("\nNombre del campo a eliminar (Enter para cancelar): ").strip()
        if not nombre_campo:
            return plantilla
            
        if nombre_campo not in plantilla['campos']:
            print(f"❌ El campo '{nombre_campo}' no existe")
            return plantilla
            
        # Confirmar eliminación
        if input(f"¿Está seguro de eliminar el campo '{nombre_campo}'? (S/N): ").upper() != 'S':
            print("Operación cancelada")
            return plantilla
            
        # Eliminar campo
        del plantilla['campos'][nombre_campo]
        print(f"✅ Campo '{nombre_campo}' eliminado correctamente")
        
        return plantilla
    
    def _mostrar_campos(self, plantilla: Dict[str, Any]) -> None:
        """Muestra todos los campos de la plantilla"""
        if 'campos' not in plantilla or not plantilla['campos']:
            print("\n❌ La plantilla no tiene campos definidos")
            return
            
        print("\n=== CAMPOS DISPONIBLES ===")
        for nombre, info in plantilla['campos'].items():
            tipo = info.get('type', 'No definido')
            requerido = "Sí" if info.get('required', False) else "No"
            descripcion = info.get('description', 'Sin descripción')
            
            print(f"\n• {nombre}")
            print(f"  Tipo: {tipo}")
            print(f"  Requerido: {requerido}")
            print(f"  Descripción: {descripcion}")
            
            # Mostrar validadores si existen
            if 'validators' in info and info['validators']:
                print("  Validadores:")
                for validador, valor in info['validators'].items():
                    print(f"    - {validador}: {valor}")
    
    def _solicitar_validadores(self, tipo: str) -> Dict[str, Any]:
        """Solicita validadores según el tipo de campo"""
        validadores = {}
        
        print("\n=== CONFIGURACIÓN DE VALIDADORES ===")
        print(f"Configurando validadores para tipo: {tipo}")
        
        if tipo in ['texto', 'string', 'text']:
            min_length = input("Longitud mínima (Enter para omitir): ").strip()
            if min_length.isdigit():
                validadores['min_length'] = int(min_length)
                
            max_length = input("Longitud máxima (Enter para omitir): ").strip()
            if max_length.isdigit():
                validadores['max_length'] = int(max_length)
                
            pattern = input("Patrón regex (Enter para omitir): ").strip()
            if pattern:
                validadores['pattern'] = pattern
                
        elif tipo in ['numero', 'number', 'integer', 'float']:
            min_value = input("Valor mínimo (Enter para omitir): ").strip()
            if min_value:
                try:
                    validadores['min_value'] = float(min_value)
                except ValueError:
                    print("⚠️ Valor no válido, se omitirá")
                    
            max_value = input("Valor máximo (Enter para omitir): ").strip()
            if max_value:
                try:
                    validadores['max_value'] = float(max_value)
                except ValueError:
                    print("⚠️ Valor no válido, se omitirá")
                    
        elif tipo in ['fecha', 'date']:
            min_date = input("Fecha mínima (YYYY-MM-DD) (Enter para omitir): ").strip()
            if min_date:
                validadores['min_date'] = min_date
                
            max_date = input("Fecha máxima (YYYY-MM-DD) (Enter para omitir): ").strip()
            if max_date:
                validadores['max_date'] = max_date
                
        # Opción para valores permitidos (cualquier tipo)
        if input("¿Desea especificar valores permitidos? (S/N): ").upper() == 'S':
            valores = input("Ingrese valores separados por coma: ").strip()
            if valores:
                validadores['allowed_values'] = [v.strip() for v in valores.split(',')]
                
        return validadores
    
    def _guardar_plantilla_modificada(self, plantilla: Dict[str, Any], tipo: str, nombre: str) -> Optional[Path]:
        """Guarda la plantilla modificada en el directorio correspondiente"""
        # Determinar directorio
        if tipo == "global":
            destino = self.global_templates
        elif tipo == "codigo":
            destino = self.code_templates
        else:
            print(f"❌ Tipo de plantilla no válido: {tipo}")
            return None
        
        # Verificar que el directorio existe
        if not destino.exists():
            try:
                destino.mkdir(parents=True)
            except Exception as e:
                print(f"❌ Error al crear directorio: {str(e)}")
                return None
        
        # Construir nombre de archivo
        archivo = destino / f"{nombre}.json"
        
        # Verificar si existe y confirmar sobrescritura
        if archivo.exists():
            if input(f"La plantilla '{nombre}' ya existe. ¿Sobrescribir? (S/N): ").upper() != 'S':
                nuevo_nombre = input("Ingrese un nuevo nombre: ").strip()
                if not nuevo_nombre:
                    return None
                archivo = destino / f"{nuevo_nombre}.json"
                plantilla['nombre'] = nuevo_nombre
        
        # Guardar plantilla
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(plantilla, f, indent=2, ensure_ascii=False)
            return archivo
        except Exception as e:
            print(f"❌ Error al guardar plantilla: {str(e)}")
            return None

    def validar_plantilla(self) -> None:
        """Valida la estructura de una plantilla existente"""
        print("\n=== VALIDACIÓN DE PLANTILLA ===")
        
        # Seleccionar tipo de plantilla a validar
        print("\nSeleccione el tipo de plantilla:")
        print("1. Plantilla global")
        print("2. Plantilla de código")
        print("0. Cancelar")
        
        tipo_opcion = input("\nSeleccione opción: ").strip()
        if tipo_opcion == "0":
            return
        
        tipo = "global" if tipo_opcion == "1" else "codigo" if tipo_opcion == "2" else None
        if not tipo:
            print("Opción no válida")
            return
        
        # Cargar la plantilla existente
        plantilla = self.seleccionar_plantilla(tipo)
        if not plantilla:
            print("\n❌ No se seleccionó ninguna plantilla.")
            return
            
        # Validar estructura
        es_valido, errores = self._validate_template_structure(plantilla)
        
        if es_valido:
            print("\n✅ La plantilla tiene una estructura válida.")
        else:
            print("\n❌ Se encontraron problemas en la estructura:")
            for error in errores:
                print(f"  • {error}")
                
            # Ofrecer corrección automática
            if input("\n¿Desea intentar corregir la estructura? (S/N): ").upper() == 'S':
                plantilla_corregida = self.fix_template_structure(plantilla)
                
                # Verificar si la corrección fue exitosa
                es_valido, errores = self._validate_template_structure(plantilla_corregida)
                if es_valido:
                    print("\n✅ Se corrigió exitosamente la estructura.")
                    
                    # Guardar plantilla corregida
                    if input("\n¿Desea guardar la plantilla corregida? (S/N): ").upper() == 'S':
                        tipo_guardado = plantilla_corregida.get('tipo', tipo)
                        nombre = plantilla_corregida.get('nombre', 'plantilla_corregida')
                        
                        ruta = self._guardar_plantilla_modificada(plantilla_corregida, tipo_guardado, nombre)
                        if ruta:
                            print(f"\n✅ Plantilla corregida guardada en: {ruta}")
                else:
                    print("\n❌ No se pudo corregir completamente la estructura.")
                    for error in errores:
                        print(f"  • {error}")
