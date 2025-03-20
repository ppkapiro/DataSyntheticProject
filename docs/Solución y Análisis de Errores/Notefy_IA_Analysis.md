+-------------------------------------------------------------------------------+
|                       Análisis Completo de la Estructura del Proyecto          |
|                            Notefy IA - Data Synthetic                        |
+-------------------------------------------------------------------------------+

1. **Estructura General del Proyecto Completa**

Notefy IA/
└── Data synthetic/
    ├── BIO/
    │   ├── __init__.py
    │   └── bios.py
    ├── FARC/
    │   ├── __init__.py
    │   └── fars.py
    ├── MTP/
    │   ├── __init__.py
    │   └── mtp.py
    ├── Data/
    │   └── [Carpetas de clínicas]
    ├── master/
    │   ├── __init__.py
    │   └── main.py
    ├── core/
    │   ├── __init__.py
    │   └── import_consolidator.py
    ├── lector_archivos/
    │   ├── __init__.py
    │   └── lector.py
    ├── pacientes/
    │   ├── __init__.py
    │   └── pacientes.py
    ├── pdf_extractor/
    │   ├── __init__.py
    │   └── pdf_extractor.py
    ├── templates/
    │   ├── Campos Codigos/
    │   ├── Campos Master Global/
    │   └── template_generator.py
    ├── utils/
    │   ├── __init__.py
    │   ├── advanced_content_analyzer.py
    │   ├── ai_extractor.py
    │   ├── clinic_manager.py
    │   ├── config_manager.py
    │   ├── data_formats.py
    │   ├── data_validator.py
    │   ├── exportador_base.py
    │   ├── file_naming.py
    │   ├── menu_manager.py
    │   ├── template_management/
    │   │   ├── __init__.py
    │   │   ├── django_parser.py
    │   │   ├── field_analyzer.py
    │   │   ├── field_types.py
    │   │   └── template_manager.py
    │   └── template_manager.py
    ├── docs/
    │   ├── ESTRUCTURA_PROYECTO.md
    │   ├── ESTADO_ACTUAL.md
    │   └── Notefy_IA_Analysis.md
    ├── __init__.py
    ├── run.py
    ├── setup.py
    ├── main.py
    ├── DIRECTRICES.md
    ├── DIRECTRICES_IA.md
    ├── INSTRUCCIONES COPILOT.md
    └── requirements.txt

2. **Diagrama de Relaciones entre Módulos Actualizado**

graph TD
    run[run.py] --> main[master/main.py]
    
    main --> ClinicaManager[master/main.py:ClinicaManager]
    main --> DataSyntheticManager[master/main.py:DataSyntheticManager]
    main --> MainManager[master/main.py:MainManager]
    main --> SystemManager[master/main.py:SystemManager]
    
    ClinicaManager --> LectorArchivos[lector_archivos/lector.py:LectorArchivos]
    ClinicaManager --> ExportadorPacientes[pacientes/pacientes.py:ExportadorPacientes]
    ClinicaManager --> ExportadorFARC[FARC/fars.py:ExportadorFARC]
    ClinicaManager --> ExportadorBIO[BIO/bios.py:ExportadorBIO]
    ClinicaManager --> ExportadorMTP[MTP/mtp.py:ExportadorMTP]
    ClinicaManager --> PDFExtractor[pdf_extractor/pdf_extractor.py:PDFExtractor]
    
    DataSyntheticManager --> ClinicManager[utils/clinic_manager.py:ClinicManager]
    DataSyntheticManager --> ClinicaManager
    
    MainManager --> ClinicManager
    MainManager --> MenuManager[utils/menu_manager.py:MenuManager]
    
    SystemManager --> ClinicManager
    SystemManager --> MenuManager
    
    ClinicManager --> MenuManager
    ClinicManager --> TemplateManager[utils/template_manager.py:TemplateManager]
    ClinicManager --> ImportConsolidator[core/import_consolidator.py:ImportConsolidator]
    
    MenuManager --> DataFormatHandler[utils/data_formats.py:DataFormatHandler]
    MenuManager --> PDFExtractor
    
    PDFExtractor --> AIExtractor[utils/ai_extractor.py:AIExtractor]
    
    ImportConsolidator --> TemplateManager
    ImportConsolidator --> DataValidator[utils/data_validator.py:DataValidator]
    ImportConsolidator --> PDFExtractor
    ImportConsolidator --> DataFormatHandler
    
    TemplateManager --> AdvancedContentAnalyzer[utils/advanced_content_analyzer.py:AdvancedContentAnalyzer]
    TemplateManager --> FieldAnalyzer[utils/template_management/field_analyzer.py:FieldAnalyzer]
    TemplateManager --> FieldTypes[utils/template_management/field_types.py:FieldTypes]
    TemplateManager --> DataValidator
    
    AIExtractor --> ConfigManager[utils/config_manager.py:ConfigManager]
    
    ExportadorBase[utils/exportador_base.py:ExportadorBase] --> FileNaming[utils/file_naming.py:FileNaming]
    ExportadorBase --> DataFormatHandler
    
    ExportadorPacientes --> ExportadorBase
    ExportadorFARC --> ExportadorBase
    ExportadorBIO --> ExportadorBase
    ExportadorMTP --> ExportadorBase
    
    TemplateGenerator[templates/template_generator.py:TemplateGenerator] --> AdvancedContentAnalyzer

3. **Descripción de los Archivos Python del Proyecto**

**3.1. Scripts de Entrada Principal**

| Script             | Descripción                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `run.py`           | Punto de entrada principal que configura el PYTHONPATH e inicia la ejecución del programa |
| `master/main.py`   | Implementa las clases principales de gestión (ClinicaManager, DataSyntheticManager, MainManager, SystemManager) y la función `main()` |
| `main.py`          | Script alternativo para ejecución con argumentos de línea de comandos |

**3.2. Módulos de Procesamiento de Datos**

| Script                    | Descripción                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `lector_archivos/lector.py` | Implementa la clase `LectorArchivos` para procesar diferentes formatos de archivo |
| `pdf_extractor/pdf_extractor.py` | Clase `PDFExtractor` para procesamiento de archivos PDF con múltiples métodos |
| `core/import_consolidator.py` | Clase `ImportConsolidator` para consolidar datos de múltiples fuentes |

**3.3. Módulos de Exportación de Datos**

| Script                    | Descripción                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `pacientes/pacientes.py`   | Clase `ExportadorPacientes` para generar datos sintéticos de pacientes |
| `FARC/fars.py`             | Clase `ExportadorFARC` para generar evaluaciones de alcohol y drogas |
| `BIO/bios.py`             | Clase `ExportadorBIO` para generar historias biográficas |
| `MTP/mtp.py`              | Clase `ExportadorMTP` para generar planes de entrenamiento |
| `utils/exportador_base.py` | Clase base `ExportadorBase` con funcionalidad común para todos los exportadores |

**3.4. Módulo de Utilidades (utils)**

| Script                    | Descripción                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `utils/menu_manager.py`    | Clase `MenuManager` para gestión de menús e interfaces de usuario |
| `utils/clinic_manager.py`  | Clase `ClinicManager` para gestión de clínicas, estructura y configuraciones |
| `utils/template_manager.py` | Gestiona las plantillas de importación y generación de datos |
| `utils/data_formats.py`    | Clase `DataFormatHandler` para manejo de múltiples formatos de datos |
| `utils/ai_extractor.py`    | Clase `AIExtractor` para extracción de contenido mediante APIs de IA |
| `utils/config_manager.py`  | Gestiona configuraciones y credenciales del sistema |
| `utils/data_validator.py`  | Clase `DataValidator` para validar datos contra reglas definidas |
| `utils/file_naming.py`     | Proporciona convenciones para nombres de archivos |
| `utils/advanced_content_analyzer.py` | Clase `AdvancedContentAnalyzer` para analizar documentos y generar plantillas |

**3.5. Gestión de Plantillas (utils/template_management)**

| Script                         | Descripción                                                                 |
|--------------------------------|-----------------------------------------------------------------------------|
| `utils/template_management/template_manager.py` | Implementación especializada para gestión de plantillas |
| `utils/template_management/field_analyzer.py` | Clase `FieldAnalyzer` para análisis de campos de datos |
| `utils/template_management/field_types.py` | Define tipos de campos soportados y sus validaciones |
| `utils/template_management/django_parser.py` | Clase `DjangoModelParser` para generar plantillas a partir de modelos Django |

**3.6. Generación de Plantillas (templates)**

| Script                     | Descripción                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `templates/template_generator.py` | Clase `TemplateGenerator` para generación avanzada de plantillas |

4. **Problemas Identificados y Actualizados**

**4.1. Duplicación de código y archivos**

- **Problema:** Existen dos implementaciones de `template_manager.py`:
  - `/utils/template_manager.py`
  - `/utils/template_management/template_manager.py`
  
  Esto causa confusión en las importaciones y puede llevar a inconsistencias en el código.

**4.2. Referencias a módulos inexistentes en el código proporcionado**

- **Problema:** Hay importaciones de módulos que no tienen implementaciones completas:
  - En `clinic_manager.py`:
    ```python
    from pdf_extractor.pdf_extractor import PDFExtractor  # Existe pero puede estar incompleto
    from core.import_consolidator import ImportConsolidator  # Existe pero puede estar incompleto
    ```

**4.3. Módulos de exportación no implementados completamente**

- **Problema:** Se hace referencia a los siguientes módulos en `main.py` pero no están implementados completamente:
  - `from lector_archivos.lector import LectorArchivos`
  - `from pacientes.pacientes import ExportadorPacientes`
  - `from FARC.fars import ExportadorFARC`
  - `from BIO.bios import ExportadorBIO`
  - `from MTP.mtp import ExportadorMTP`

**4.4. Múltiples clases de gestión principal con funcionalidad similar**

- **Problema:** En `master/main.py` existen múltiples clases con funcionalidades similares:
  - `ClinicaManager`
  - `DataSyntheticManager`
  - `MainManager`
  - `SystemManager`
  
  Esta redundancia complica el mantenimiento del código.

**4.5. Referencias circulares en el diseño**

- **Problema:** Hay dependencias circulares potenciales:
  - `ClinicManager` importa `MenuManager`
  - `MenuManager` puede necesitar acceso a `ClinicManager`
  - `ImportConsolidator` depende de varios módulos que a su vez podrían depender de él

5. **Recomendaciones de Mejora Actualizadas**

1. **Unificar la gestión de plantillas:**
   - Mantener una única implementación de `TemplateManager`, eliminando la duplicación.
   - Decidir si usar la versión en `utils/` o la versión en `utils/template_management/`.

2. **Completar las implementaciones faltantes:**
   - Implementar los módulos de exportación (`pacientes.py`, `fars.py`, `bios.py`, `mtp.py`).
   - Completar la implementación de `lector.py` para el procesamiento de archivos.

3. **Consolidar las clases de gestión:**
   - Unificar las múltiples clases manager en `master/main.py`.
   - Definir claramente las responsabilidades de cada una.

4. **Mejorar la estructura de dependencias:**
   - Rediseñar para evitar dependencias circulares.
   - Implementar un patrón de inyección de dependencias.

5. **Estandarizar la gestión de rutas:**
   - Centralizar la definición de rutas base.
   - Usar rutas relativas cuando sea posible.

6. **Implementar gestión de configuración:**
   - Utilizar un archivo de configuración central.
   - Evitar rutas absolutas codificadas.

7. **Mejorar documentación:**
   - Completar la documentación de todas las clases y métodos.
   - Mantener diagramas UML actualizados.
