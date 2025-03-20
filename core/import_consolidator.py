from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from utils.template_manager import TemplateManager
from utils.data_validator import DataValidator
from pdf_extractor.pdf_extractor import PDFExtractor
from utils.data_formats import DataFormatHandler
from datetime import datetime
import json

class ImportConsolidator:
    """Consolidador de datos para importación"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.pdf_extractor = PDFExtractor()
        self.validator = DataValidator()
        self.base_path = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic")

    def consolidate_patient_data(self, patient_name: str, clinic_code: Optional[str] = None) -> Optional[Path]:
        """Consolida datos de un paciente desde múltiples documentos"""
        # 1. Cargar plantilla master
        template = self._load_master_template()
        if not template:
            return None

        # 2. Encontrar documentos del paciente
        documents = self._find_patient_documents(patient_name, clinic_code)
        if not documents:
            print(f"\nNo se encontraron documentos para el paciente: {patient_name}")
            return None

        # 3. Seleccionar documentos a procesar
        selected_docs = self._select_documents(documents)
        if not selected_docs:
            return None

        # 4. Procesar cada documento y consolidar datos
        consolidated_data = self._process_documents(selected_docs, template)
        if not consolidated_data:
            return None

        # 5. Generar archivo de importación
        return self._generate_import_file(consolidated_data, patient_name)

    def _load_master_template(self) -> Optional[Dict[str, Any]]:
        """Carga la plantilla master de importación"""
        # Directorio específico de templates (ahora solo Campos Master Global)
        template_base = Path("C:/Users/pepec/Documents/Notefy IA/Data synthetic/templates/Campos Master Global")
        
        if not template_base.exists():
            print(f"\n❌ No se encontró el directorio de templates: {template_base}")
            return None

        # Buscar todos los archivos JSON directamente en el directorio (sin recursión)
        templates_encontrados = []
        for template_path in template_base.glob('*.json'):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    templates_encontrados.append({
                        'path': template_path,
                        'nombre': template_path.name,
                        'tipo': metadata.get('tipo_documento', 'desconocido'),
                        'num_campos': len(metadata.get('campos', [])),
                        'fecha': metadata.get('fecha_generacion', ''),
                        'campos': metadata.get('campos', [])
                    })
            except Exception as e:
                print(f"\n⚠️ Error leyendo template {template_path.name}: {str(e)}")
                continue

        if not templates_encontrados:
            print("\n❌ No se encontraron templates disponibles")
            return None

        # Ordenar por nombre para mejor organización
        templates_encontrados.sort(key=lambda x: x['nombre'])

        # Mostrar templates disponibles
        print("\n=== TEMPLATES DISPONIBLES ===")
        for idx, template in enumerate(templates_encontrados, 1):
            print(f"\n{idx}. {template['nombre']}")
            print(f"   Tipo: {template['tipo']}")
            print(f"   Campos: {template['num_campos']}")
            if template['campos']:
                print("   Campos principales:")
                # Mostrar los primeros 5 campos como preview
                for campo in template['campos'][:5]:
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
                    print(f"\n✅ Template seleccionado:")
                    print(f"   Nombre: {template_seleccionado['nombre']}")
                    print(f"   Ubicación: {template_seleccionado['subcarpeta']}")
                    
                    # Cargar template completo
                    with open(template_seleccionado['path'], 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    print("❌ Selección no válida")
            except ValueError:
                print("❌ Por favor ingrese un número válido")
            except Exception as e:
                print(f"❌ Error cargando template: {str(e)}")
                return None

    def _find_patient_documents(self, patient_name: str, clinic_code: Optional[str] = None) -> List[Path]:
        """Busca documentos relacionados con el paciente"""
        documents = []
        
        # Determinar rutas de búsqueda
        search_paths = []
        if clinic_code:
            search_paths.append(self.base_path / "data" / clinic_code / "output")
        else:
            # Buscar en todas las clínicas
            for clinic_path in (self.base_path / "data").glob("**/output"):
                search_paths.append(clinic_path)

        # Buscar documentos
        for path in search_paths:
            if path.exists():
                # Buscar por nombre de paciente en diferentes formatos
                patterns = [
                    f"*{patient_name}*.pdf",
                    f"*{patient_name}*.json",
                    f"*{patient_name}*.txt"
                ]
                
                for pattern in patterns:
                    documents.extend(path.glob(pattern))

        return documents

    def _select_documents(self, documents: List[Path]) -> List[Path]:
        """Permite al usuario seleccionar documentos a procesar"""
        if not documents:
            return []

        print("\n=== DOCUMENTOS DISPONIBLES ===")
        for idx, doc in enumerate(documents, 1):
            # Mostrar información relevante
            stats = doc.stat()
            print(f"{idx}. {doc.name}")
            print(f"   Tamaño: {stats.st_size / 1024:.1f} KB")
            print(f"   Tipo: {doc.suffix}")
            print()

        selected = []
        while True:
            try:
                entrada = input("\nSeleccione documentos (números separados por coma, 0 para finalizar): ")
                if entrada.strip() == '0':
                    break
                    
                indices = [int(x.strip()) - 1 for x in entrada.split(',')]
                for idx in indices:
                    if 0 <= idx < len(documents):
                        selected.append(documents[idx])
                    else:
                        print(f"Índice no válido: {idx + 1}")
                
                if selected:
                    break
                    
            except ValueError:
                print("Entrada no válida")

        return selected

    def _process_documents(self, documents: List[Path], template: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Procesa y consolida datos de múltiples documentos"""
        # Preparar DataFrame para consolidación
        required_fields = template['fields'].keys()
        data = {
            'campo': list(required_fields),
            'tipo': [template['fields'][f]['type'] for f in required_fields],
            'requerido': [template['fields'][f].get('required', False) for f in required_fields]
        }
        
        df = pd.DataFrame(data)
        
        # Procesar cada documento
        for doc in documents:
            values = []
            
            # Extraer contenido según tipo de archivo
            if doc.suffix == '.pdf':
                content, quality = self.pdf_extractor.leer_pdf(doc)
                if quality < 80:
                    if input("\n¿Desea mejorar la extracción con IA? (S/N): ").upper() == 'S':
                        content, quality = self.pdf_extractor.usar_api_pdf(doc)
            else:
                content = DataFormatHandler.read_file(doc)
                quality = 100  # Asumimos alta calidad para archivos no PDF

            # Extraer valores para cada campo
            for field in required_fields:
                value = self._extract_field_value(content, field, template['fields'][field])
                values.append(value)
                
            # Agregar columna al DataFrame
            df[doc.name] = values

        return df

    def _extract_field_value(self, content: str, field_name: str, field_info: Dict[str, Any]) -> Optional[str]:
        """Extrae el valor de un campo específico del contenido"""
        if not content:
            return None
            
        # Buscar valor usando reglas de la plantilla
        field_type = field_info['type']
        pattern = field_info.get('pattern')
        
        # Implementar lógica de extracción según tipo
        # ...

        return None  # Valor por defecto si no se encuentra

    def _generate_import_file(self, data: pd.DataFrame, patient_name: str) -> Optional[Path]:
        """Genera el archivo final de importación"""
        if data.empty:
            return None

        # Permitir selección de formato
        print("\nSeleccione formato de exportación:")
        print("1. JSON")
        print("2. CSV")
        
        while True:
            try:
                opcion = int(input("\nOpción (1-2): "))
                if opcion in [1, 2]:
                    break
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número")

        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"import_{patient_name}_{timestamp}"
        
        if opcion == 1:
            output_path = self.base_path / "output" / f"{base_name}.json"
            data.to_json(output_path, orient='records', indent=2)
        else:
            output_path = self.base_path / "output" / f"{base_name}.csv"
            data.to_csv(output_path, index=False)

        print(f"\n✅ Archivo de importación guardado en: {output_path}")
        return output_path

    def consolidate_documents(self, patient_name: str, documents: List[Path], clinic_code: str) -> Optional[Path]:
        """Consolida múltiples documentos en uno solo y los adapta al template"""
        # 1. Obtener template de consolidación
        template_path = self.base_path / "templates/Campos Master Global/template_consolidacion.json"
        
        if not template_path.exists():
            # Si no existe el template de consolidación, buscar otros templates
            template_path = self.base_path / "templates/Campos Master Global"
            template_files = list(template_path.glob('*.json'))
            
            if not template_files:
                print("\n❌ No se encontraron templates en Campos Master Global")
                return None

            # Mostrar templates disponibles
            print("\n=== TEMPLATES DISPONIBLES ===")
            for idx, template in enumerate(template_files, 1):
                print(f"{idx}. {template.name}")

            # Seleccionar template
            while True:
                try:
                    seleccion = input("\nSeleccione el template a usar (0 para cancelar): ").strip()
                    if seleccion == '0':
                        return None

                    idx = int(seleccion) - 1
                    if 0 <= idx < len(template_files):
                        template_path = template_files[idx]
                        break
                    print("❌ Selección no válida")
                except ValueError:
                    print("❌ Por favor ingrese un número válido")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_structure = json.load(f)
            print(f"\n✅ Template cargado: {template_path.name}")
        except Exception as e:
            print(f"\n❌ Error leyendo template: {str(e)}")
            return None

        # El resto del código sigue igual...
        # 2. Preparar directorio de salida
        output_dir = self.base_path / "data" / clinic_code / "output" / "consolidaciones"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Consolidar datos iniciales
        datos_base = {
            'paciente': patient_name,
            'fecha_consolidacion': datetime.now().isoformat(),
            'documentos': []
        }
        
        # 4. Procesar documentos y extraer datos según template
        for doc in documents:
            try:
                # Extraer contenido
                if doc.suffix.lower() == '.pdf':
                    contenido, calidad = self.pdf_extractor.leer_pdf(doc)
                else:
                    contenido = DataFormatHandler.read_file(doc)
                    calidad = 100

                # Determinar tipo de documento y aplicar mapeo correspondiente
                tipo_doc = doc.parent.parent.name  # FARC, BIO, etc.
                datos_procesados = self._mapear_datos_segun_template(
                    contenido=contenido,
                    tipo_doc=tipo_doc,
                    template_structure=template_structure,
                    doc_info={
                        'nombre': doc.name,
                        'fecha': datetime.fromtimestamp(doc.stat().st_mtime).isoformat(),
                        'calidad': calidad
                    }
                )

                if datos_procesados:
                    datos_base['documentos'].append(datos_procesados)
                
            except Exception as e:
                print(f"\n❌ Error procesando {doc.name}: {str(e)}")
                continue

        # 5. Verificar que tenemos datos para consolidar
        if not datos_base['documentos']:
            print("\n❌ No se pudo extraer contenido de ningún documento")
            return None

        # 6. Generar consolidación final
        try:
            datos_consolidados = self._generar_consolidacion_final(
                datos_base=datos_base,
                template_structure=template_structure
            )

            # 7. Guardar resultado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"consolidacion_{patient_name.replace(' ', '_')}_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(datos_consolidados, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Consolidación guardada en: {output_file}")
            return output_file

        except Exception as e:
            print(f"\n❌ Error en consolidación final: {str(e)}")
            return None

    def _mapear_datos_segun_template(self, contenido: str, tipo_doc: str, 
                                   template_structure: Dict, doc_info: Dict) -> Optional[Dict]:
        """Mapea los datos extraídos según la estructura del template"""
        try:
            # Obtener reglas de mapeo según tipo de documento
            reglas_mapeo = template_structure.get('mapeo', {}).get(tipo_doc, {})
            if not reglas_mapeo:
                print(f"\n⚠️ No hay reglas de mapeo para documento tipo: {tipo_doc}")
                return None

            # Aplicar reglas de extracción
            datos_mapeados = {
                'tipo': tipo_doc,
                'metadata': doc_info,
                'campos': {}
            }

            # Procesar cada campo según reglas
            for campo, regla in reglas_mapeo.items():
                valor = self._extraer_valor_campo(contenido, regla)
                if valor is not None:
                    datos_mapeados['campos'][campo] = valor

            return datos_mapeados

        except Exception as e:
            print(f"\n❌ Error en mapeo de datos: {str(e)}")
            return None

    def _extraer_valor_campo(self, contenido: str, regla: Dict) -> Optional[Any]:
        """Extrae el valor de un campo según las reglas definidas"""
        try:
            tipo = regla.get('tipo', 'texto')
            patron = regla.get('patron')
            
            if patron:
                import re
                match = re.search(patron, contenido)
                if match:
                    valor = match.group(1) if match.groups() else match.group(0)
                    
                    # Convertir según tipo
                    if tipo == 'numero':
                        return float(valor)
                    elif tipo == 'fecha':
                        return datetime.strptime(valor, regla.get('formato', '%Y-%m-%d')).isoformat()
                    else:
                        return valor.strip()
                        
            return None
            
        except Exception:
            return None

    def _generar_consolidacion_final(self, datos_base: Dict, template_structure: Dict) -> Dict:
        """Genera la consolidación final siguiendo la estructura del template"""
        # 1. Inicializar estructura base según template
        consolidacion = {
            'metadata': {
                'paciente': datos_base['paciente'],
                'fecha_consolidacion': datos_base['fecha_consolidacion'],
                'version': template_structure.get('version', '1.0')
            },
            'documentos_procesados': len(datos_base['documentos']),
            'datos_consolidados': {}
        }

        # 2. Consolidar datos según estructura objetivo
        estructura_objetivo = template_structure.get('estructura_consolidada', {})
        
        for seccion, config in estructura_objetivo.items():
            consolidacion['datos_consolidados'][seccion] = self._consolidar_seccion(
                datos_base['documentos'],
                config,
                seccion
            )

        return consolidacion

    def _consolidar_seccion(self, documentos: List[Dict], config: Dict, seccion: str) -> Dict:
        """Consolida una sección específica de los datos"""
        datos_seccion = {}
        
        # Procesar cada campo de la sección
        for campo, reglas in config.get('campos', {}).items():
            valores = []
            
            # Buscar en documentos relevantes
            for doc in documentos:
                if doc['tipo'] in reglas.get('fuentes', []):
                    valor = doc.get('campos', {}).get(campo)
                    if valor is not None:
                        valores.append(valor)

            # Aplicar regla de consolidación
            if valores:
                regla = reglas.get('consolidacion', 'ultimo')
                if regla == 'ultimo':
                    datos_seccion[campo] = valores[-1]
                elif regla == 'primero':
                    datos_seccion[campo] = valores[0]
                elif regla == 'todos':
                    datos_seccion[campo] = valores
                elif regla == 'promedio' and valores:
                    datos_seccion[campo] = sum(valores) / len(valores)

        return datos_seccion
