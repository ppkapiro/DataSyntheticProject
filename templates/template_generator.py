from pathlib import Path
import json
import yaml
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from utils.advanced_content_analyzer import AdvancedContentAnalyzer
from google.cloud import vision
from google.oauth2 import service_account

class TemplateGenerator:
    """Generador avanzado de plantillas con análisis inteligente"""
    
    QUALITY_WEIGHTS = {
        'field_detection': 0.3,
        'type_inference': 0.3,
        'validation_rules': 0.2,
        'structure_quality': 0.2
    }
    
    def __init__(self):
        self.base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/templates")
        self.analyzer = AdvancedContentAnalyzer()
        self.vision_client = None
        
        # Inicializar Google Cloud Vision
        try:
            credentials_file = next(Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic").glob("*-86851702569b.json"), None)
            if credentials_file:
                credentials = service_account.Credentials.from_service_account_file(str(credentials_file))
                self.vision_client = vision.ImageAnnotatorClient(credentials=credentials)
                print("✅ Vision API inicializada")
        except Exception as e:
            print(f"⚠️ Vision API no disponible: {e}")

    def _mostrar_archivos_codigos(self) -> Optional[Path]:
        """Muestra y permite seleccionar archivos de la carpeta Campos Codigos"""
        try:
            # Ruta absoluta a la carpeta Campos Codigos
            codigos_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/templates/Campos Codigos")
            
            if not codigos_path.exists():
                print(f"\n❌ Error: No se encuentra la carpeta:")
                print(f"   {codigos_path}")
                return None

            # Buscar todos los archivos soportados recursivamente
            archivos = []
            extensiones = {
                '.xlsx': 'Excel',
                '.xls': 'Excel antiguo',
                '.csv': 'CSV',
                '.json': 'JSON',
                '.yaml': 'YAML',
                '.yml': 'YAML'
            }
            
            # Buscar en la carpeta y subcarpetas
            for ext, desc in extensiones.items():
                found = list(codigos_path.rglob(f"*{ext}"))
                archivos.extend((f, desc) for f in found)

            if not archivos:
                print("\n❌ No se encontraron archivos en la carpeta de códigos")
                print(f"   Ruta revisada: {codigos_path}")
                print("\nFormatos soportados:")
                for ext, desc in extensiones.items():
                    print(f"   • {desc} ({ext})")
                return None

            # Mostrar archivos encontrados agrupados por tipo
            print("\n=== ARCHIVOS DE CÓDIGOS DISPONIBLES ===")
            for idx, (archivo, tipo) in enumerate(archivos, 1):
                # Mostrar ruta relativa para mejor legibilidad
                ruta_relativa = archivo.relative_to(codigos_path)
                print(f"{idx}. [{tipo}] {ruta_relativa}")
            print("0. Cancelar")

            # Solicitar selección con validación
            while True:
                try:
                    opcion = input("\nSeleccione el archivo a utilizar (0 para cancelar): ").strip()
                    
                    # Validar cancelación
                    if opcion == '0':
                        return None
                        
                    # Validar número
                    num_opcion = int(opcion)
                    if 1 <= num_opcion <= len(archivos):
                        archivo_seleccionado = archivos[num_opcion - 1][0]
                        
                        # Confirmar selección
                        print(f"\nArchivo seleccionado:")
                        print(f"   • Nombre: {archivo_seleccionado.name}")
                        print(f"   • Tipo: {archivos[num_opcion - 1][1]}")
                        print(f"   • Ruta: {archivo_seleccionado}")
                        
                        if input("\n¿Confirmar selección? (S/N): ").upper() == 'S':
                            return archivo_seleccionado
                        else:
                            print("\nSelección cancelada. Por favor, elija otro archivo.")
                            continue
                            
                    print("\n❌ Opción no válida. Seleccione un número entre 0 y", len(archivos))
                    
                except ValueError:
                    print("\n❌ Por favor ingrese un número válido")
                except Exception as e:
                    print(f"\n❌ Error inesperado: {str(e)}")
                    return None

        except Exception as e:
            print(f"\n❌ Error al listar archivos: {str(e)}")
            return None

    def generate_template(self, tipo_plantilla: str = None, improve_quality: bool = True) -> Tuple[Dict[str, Any], float]:
        """Genera una plantilla basada en archivos de códigos existentes"""
        # Primero mostrar archivos disponibles
        archivo_base = self._mostrar_archivos_codigos()
        if not archivo_base:
            print("\nNo se pudo obtener archivo base de códigos")
            return self._create_base_structure(), 0.0

        print(f"\nUsando archivo base: {archivo_base.name}")
        
        # Analizar archivo seleccionado
        try:
            template_data, quality_score = self._analyze_with_cascade(archivo_base)
            
            # Mejora con IA si es necesario
            if improve_quality and quality_score < 0.8 and self.vision_client:
                template_data, quality_score = self._improve_with_ai(template_data, archivo_base)
            
            # Enriquecer con metadatos
            template = self._enrich_template(template_data, quality_score)
            
            # Guardar template en carpeta global
            self._save_global_template(template, tipo_plantilla)
            
            return template, quality_score
            
        except Exception as e:
            print(f"\nError analizando archivo: {str(e)}")
            return self._create_base_structure(), 0.0

    def _save_global_template(self, template: Dict[str, Any], tipo_plantilla: str) -> None:
        """Guarda el template en la carpeta de templates globales"""
        # Ruta absoluta a Campos Master Global
        global_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/templates/Campos Master Global")
        global_path.mkdir(parents=True, exist_ok=True)
        
        # Crear subcarpeta según tipo de plantilla
        tipo_path = global_path / tipo_plantilla.lower()
        tipo_path.mkdir(exist_ok=True)
        
        # Generar nombre del archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"template_{tipo_plantilla.lower()}_{timestamp}"
        
        # Guardar en múltiples formatos
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
            }),
            ('excel', {
                'extension': '.xlsx',
                'modo': 'wb',
                'guardar': lambda t, f: pd.DataFrame(t['fields']).to_excel(f, index=False)
            })
        ]:
            try:
                output_path = tipo_path / f"{filename}{config['extension']}"
                with open(output_path, config['modo']) as f:
                    config['guardar'](template, f)
                print(f"\n✅ Template guardado en: {output_path}")
            except Exception as e:
                print(f"\n❌ Error guardando formato {formato}: {str(e)}")
        
        # Generar archivo de metadatos
        metadata = {
            'generado': datetime.now().isoformat(),
            'tipo': tipo_plantilla,
            'campos': len(template.get('fields', {})),
            'reglas': len(template.get('validation_rules', {})),
            'formatos_guardados': ['json', 'yaml', 'excel']
        }
        
        metadata_path = tipo_path / f"{filename}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Metadatos guardados en: {metadata_path}")

    def _analyze_with_cascade(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Analiza el archivo usando una cascada de métodos"""
        methods = [
            (self._analyze_structured_file, 'Análisis estructurado'),
            (self._analyze_with_advanced_parser, 'Parser avanzado'),
            (self._analyze_with_content_analyzer, 'Análisis de contenido')
        ]

        best_result = None
        best_quality = 0.0

        for method, name in methods:
            try:
                print(f"\nIntentando {name}...")
                result, quality = method(file_path)
                print(f"Calidad: {quality:.2%}")
                
                if quality > best_quality:
                    best_result = result
                    best_quality = quality
                    
                if best_quality > 0.9:  # Si la calidad es muy buena, detenemos la cascada
                    break
            except Exception as e:
                print(f"Error en {name}: {e}")
                continue

        return best_result or self._create_base_structure(), best_quality

    def _analyze_structured_file(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Analiza archivos estructurados (CSV, Excel, etc.)"""
        try:
            if file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
                df = pd.read_csv(file_path) if file_path.suffix == '.csv' else pd.read_excel(file_path)
                
                fields = {}
                validation_rules = {}
                
                for column in df.columns:
                    # Analizar tipo y reglas de validación
                    field_info = self._analyze_column(df[column])
                    fields[column] = field_info['field']
                    validation_rules[column] = field_info['rules']
                
                return {
                    'fields': fields,
                    'validation_rules': validation_rules
                }, self._calculate_quality(fields, validation_rules)
                
        except Exception as e:
            print(f"Error en análisis estructurado: {e}")
            return self._create_base_structure(), 0.0

    def _analyze_with_advanced_parser(self, file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Analiza usando el AdvancedContentAnalyzer"""
        try:
            analysis_results = self.analyzer.analyze_document(file_path)
            template_structure = self.analyzer.suggest_template_structure(analysis_results)
            
            quality = self._calculate_quality(
                template_structure['fields'],
                template_structure['validation_rules']
            )
            
            return template_structure, quality
            
        except Exception as e:
            print(f"Error en parser avanzado: {e}")
            return self._create_base_structure(), 0.0

    def _improve_with_ai(self, template_data: Dict[str, Any], file_path: Path) -> Tuple[Dict[str, Any], float]:
        """Mejora la plantilla usando IA"""
        try:
            if not self.vision_client:
                return template_data, self._calculate_quality(
                    template_data['fields'],
                    template_data['validation_rules']
                )

            # Analizar con Vision API
            with open(file_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.vision_client.document_text_detection(image=image)
            
            if response.text_annotations:
                # Mejorar campos detectados
                enhanced_fields = self._enhance_fields_with_ai(
                    template_data['fields'],
                    response.text_annotations
                )
                
                template_data['fields'] = enhanced_fields
                template_data['validation_rules'] = self._generate_enhanced_rules(enhanced_fields)
                
                quality = self._calculate_quality(
                    template_data['fields'],
                    template_data['validation_rules']
                )
                
                return template_data, quality
                
        except Exception as e:
            print(f"Error en mejora con IA: {e}")
        
        return template_data, self._calculate_quality(
            template_data['fields'],
            template_data['validation_rules']
        )

    def _calculate_quality(self, fields: Dict[str, Any], validation_rules: Dict[str, Any]) -> float:
        """Calcula la puntuación de calidad de la plantilla"""
        scores = {
            'field_detection': len(fields) / 10,  # Normalizado a 10 campos esperados
            'type_inference': sum(1 for f in fields.values() if f.get('type')) / len(fields) if fields else 0,
            'validation_rules': len(validation_rules) / len(fields) if fields else 0,
            'structure_quality': sum(1 for f in fields.values() if f.get('description')) / len(fields) if fields else 0
        }
        
        return sum(score * weight for (metric, score), (_, weight) 
                  in zip(scores.items(), self.QUALITY_WEIGHTS.items()))

    def _enhance_fields_with_ai(self, fields: Dict[str, Any], annotations: List[Any]) -> Dict[str, Any]:
        """Mejora los campos usando análisis de IA"""
        enhanced_fields = fields.copy()
        
        # Extraer texto y confianza de las anotaciones
        text_blocks = [(ann.description, ann.confidence) for ann in annotations]
        
        for field_name, field_info in enhanced_fields.items():
            # Mejorar descripción del campo
            relevant_blocks = [block for block, conf in text_blocks 
                             if field_name.lower() in block.lower()]
            
            if relevant_blocks:
                field_info['description'] = self._generate_enhanced_description(
                    field_name, relevant_blocks
                )
            
            # Mejorar inferencia de tipo
            field_info['type'] = self._enhance_type_inference(
                field_name, field_info.get('type', 'string')
            )
            
            # Agregar ejemplos si se encuentran
            examples = self._find_examples(field_name, text_blocks)
            if examples:
                field_info['examples'] = examples

        return enhanced_fields

    def _generate_enhanced_rules(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reglas de validación mejoradas"""
        enhanced_rules = {}
        
        for field_name, field_info in fields.items():
            rules = {}
            field_type = field_info.get('type', 'string')
            
            # Reglas base según tipo
            if field_type == 'string':
                rules.update({
                    'min_length': 1,
                    'max_length': 255,
                    'pattern': self._generate_pattern(field_name, field_info)
                })
            elif field_type == 'number':
                rules.update({
                    'min_value': 0,
                    'max_value': 999999,
                    'decimals': 2
                })
            elif field_type == 'date':
                rules.update({
                    'format': 'YYYY-MM-DD',
                    'min_date': '1900-01-01',
                    'max_date': '2100-12-31'
                })
            
            # Agregar reglas específicas del campo
            if field_info.get('examples'):
                rules['examples'] = field_info['examples']
            
            enhanced_rules[field_name] = rules
            
        return enhanced_rules

    # ... (rest of existing methods) ...
