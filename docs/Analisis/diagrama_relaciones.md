# Diagrama de Relaciones entre Módulos

## Relaciones de Importación y Dependencia

```mermaid
graph TD
    %% Módulos de entrada y control
    run[run.py] --> main[master/main.py]
    main --> GestorSistema[GestorSistema]
    
    %% Componentes principales
    GestorSistema --> MenuManager[utils/menu_manager.py]
    GestorSistema --> ClinicManager[utils/clinic_manager.py]
    GestorSistema --> ImportConsolidator[core/import_consolidator.py]
    
    %% Gestión de plantillas y configuración
    ClinicManager --> TemplateManager[utils/template_manager.py]
    ImportConsolidator --> TemplateManager
    ImportConsolidator --> ConfigManager[utils/config_manager.py]
    
    %% Procesamiento de formatos
    ImportConsolidator --> DataFormatHandler[utils/data_formats.py]
    ClinicManager --> DataFormatHandler
    MenuManager --> DataFormatHandler
    
    %% Procesamiento PDF
    ImportConsolidator --> PDFExtractor[pdf_extractor/pdf_extractor.py]
    ClinicManager --> PDFExtractor
    
    %% Validación de datos
    ImportConsolidator ---> DataValidator[utils/data_validator.py]
    TemplateManager --> DataValidator
    
    %% Módulos de generación de datos
    ClinicManager --> ExportadorPacientes[pacientes/pacientes.py]
    ClinicManager --> ExportadorFARC[FARC/fars.py]
    ClinicManager --> ExportadorBIO[BIO/bios.py]
    ClinicManager --> ExportadorMTP[MTP/mtp.py]
    
    %% Relaciones de herencia
    ExportadorBase[utils/exportador_base.py] <-- ExportadorPacientes
    ExportadorBase <-- ExportadorFARC
    ExportadorBase <-- ExportadorBIO
    ExportadorBase <-- ExportadorMTP
    
    %% Utilidades de exportación
    ExportadorBase --> FileNaming[utils/file_naming.py]
    ExportadorBase --> DataFormatHandler
    
    %% Extracción avanzada y análisis de contenido
    PDFExtractor --> AIExtractor[utils/ai_extractor.py]
    TemplateManager --> AdvancedContentAnalyzer[utils/advanced_content_analyzer.py]
    
    %% Leyenda
    class run,GestorSistema,MenuManager fill:#f9f,stroke:#333,stroke-width:1px
    class ImportConsolidator,ClinicManager,TemplateManager fill:#bbf,stroke:#333,stroke-width:1px
    class DataFormatHandler,PDFExtractor,AIExtractor fill:#bfb,stroke:#333,stroke-width:1px
    class ExportadorBase,ExportadorPacientes,ExportadorFARC,ExportadorBIO,ExportadorMTP fill:#ffb,stroke:#333,stroke-width:1px
```

## Notas sobre las Relaciones

1. **Relaciones con Importación Perezosa**:
   - `ClinicManager` → `MenuManager`: Se utiliza importación perezosa para evitar referencias circulares.
   - `ImportConsolidator` → `DataValidator`: La validación se importa solo cuando es necesaria.

2. **Inyección de Dependencias**:
   - `GestorSistema` inyecta dependencias en los componentes como `ClinicManager`.
   - `ImportConsolidator` recibe instancias de `ClinicManager` para acceder a datos contextuales.

3. **Jerarquía de Exportadores**:
   - Todos los exportadores de datos específicos heredan de `ExportadorBase`.
   - Esta herencia proporciona funcionalidad común como exportación en múltiples formatos.

4. **Configuración Centralizada**:
   - `ConfigManager` gestiona rutas y configuraciones que son utilizadas por varios componentes.
   - Evita rutas absolutas codificadas directamente en los módulos.
