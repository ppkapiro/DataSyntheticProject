# Análisis de la Estructura del Proyecto y Relaciones de Componentes

Este documento detalla la estructura completa del proyecto, mostrando los scripts existentes, las relaciones entre ellos, y las funciones principales de cada módulo. También se explican las medidas tomadas para evitar dependencias circulares y se verifica que el menú interactivo funcione correctamente.

---

## Estructura Principal del Proyecto

- **master/**
  - **main.py**  
    Script principal que inicia la ejecución del sistema. Aquí se crea la instancia de `GestorSistema`, que centraliza:
    - Iniciación de recursos
    - Gestión de clínicas
    - Generación de datos sintéticos
    - Ejecución de procesos del sistema  
    Además, invoca el menú interactivo que permite seleccionar opciones como crear clínica, seleccionar clínica existente o listar clínicas.

- **core/**
  - **import_consolidator.py**  
    Se encarga de consolidar los datos de un paciente. Sus funcionalidades clave incluyen:
    - Cargar plantillas de consolidación (usando `TemplateManager`)
    - Buscar y leer documentos (apoyándose en `PDFExtractor` y `DataFormatHandler`)
    - Procesar y consolidar datos en un archivo de importación.

- **utils/**
  - **config_manager.py**  
    Centraliza la configuración y definición de rutas base del proyecto. Permite cambiar la estructura mediante un archivo YAML o valores por defecto.
  - **template_manager.py**  
    Administra la carga y manejo de plantillas utilizadas por el consolidador.
  - **data_formats.py**  
    Contiene funciones para la lectura e interpretación de múltiples formatos de archivo (CSV, JSON, TXT, etc.).

- **pdf_extractor/**
  - **pdf_extractor.py**  
    Proporciona métodos para extraer contenido de archivos PDF, con capacidad para mejorar la extracción mediante API si se requiere.
  
- **Otros Módulos Específicos**  
  - Ejemplo: Módulos para generación y exportación de datos sintéticos en las carpetas `pacientes/`, `BIO/`, `FARC/`, etc.

- **docs/**
  - Contiene archivos Markdown de análisis, reportes de errores y documentación de dependencia.

---

## Diagrama de Relaciones

El siguiente diagrama en formato Mermaid ilustra las relaciones principales entre los módulos del proyecto:

```mermaid
flowchart TD
  A[master/main.py]
  B[GestorSistema]
  C[ClinicManager]
  D[MenuManager]
  E[ImportConsolidator]
  F[ConfigManager]
  G[TemplateManager]
  H[PDFExtractor]
  I[DataFormatHandler]
  J[Exportador (pacientes, BIO, FARC, etc.)]

  A --> B
  B --> C
  B --> D
  B --> E
  E --> F
  E --> G
  E --> H
  E --> I
  B --> J
```

*Nota*: Las importaciones para `MenuManager` y otras dependencias se realizan de forma perezosa para evitar ciclos.

---

## Funciones y Responsabilidades

### master/main.py / GestorSistema
- **Funciones Principales**:
  - Inicializa el sistema y carga recursos.
  - Consolida la gestión de clínicas, generación de datos y procesos.
  - Invoca el menú interactivo, que permite seleccionar opciones.  
- **Verificación del Menú**:
  - Se comprueba que al ingresar "0" el menú finalice la ejecución.
  - Cada opción invoca funciones específicas y actualiza el menú para reflejar cambios.

### core/import_consolidator.py
- **Funciones Clave**:
  - `_load_master_template()`: Permite cargar y seleccionar una plantilla para la consolidación.
  - `_find_patient_documents()`: Busca documentos de un paciente en diversas rutas.
  - `_process_documents()`: Procesa y consolida datos extraídos de múltiples documentos.
  - `_generate_import_file()`: Exporta los datos consolidados a un archivo.
- **Manejo de Dependencias**:
  - Se usa importación perezosa para `TemplateManager` y `PDFExtractor` a fin de evitar ciclos de importación.

### utils/
- **config_manager.py**: Centraliza la configuración de rutas y parámetros globales.
- **template_manager.py**: Facilita la administración de plantillas.
- **data_formats.py**: Contiene funciones para la lectura de archivos de varios formatos.

### pdf_extractor/pdf_extractor.py
- Ofrece dos métodos de extracción:
  - Extracción directa y comprobación de calidad.
  - Uso de API para mejorar la extracción en caso de baja calidad.

---

## Análisis de Posibles Problemas y Recomendaciones

1. **Dependencias Circulares**:  
   Se han utilizado importaciones perezosas (por ejemplo, en `ImportConsolidator`) para romper ciclos entre módulos como ClinicManager, MenuManager y ImportConsolidator. Se recomienda seguir esta práctica en futuras extensiones.

2. **Rutas Hardcodeadas**:  
   Muchas rutas están definidas en forma absoluta en los módulos. Se recomienda consolidarlas en `ConfigManager` para mayor flexibilidad y facilidad de mantenimiento.

3. **Menú Interactivo**:  
   Se verificó que el menú se muestra y funciona, permitiendo:
   - Seleccionar opción "0" para salir.
   - Actualizar opciones según la selección del usuario.
   - Permitir iteraciones hasta que el usuario decida finalizar la aplicación.

4. **Validación y Manejo de Errores**:  
   Se han incluido controles y mensajes de error para la selección de plantillas y procesamiento de documentos. Se recomienda la inclusión de pruebas unitarias para cada módulo para asegurar la robustez del sistema.

---

## Conclusión

El análisis demuestra que:
- La estructura del proyecto es modular y cada componente tiene claras responsabilidades.
- Se han tomado medidas para evitar importaciones circulares mediante importaciones perezosas.
- El menú interactivo se integra correctamente y responde según lo esperado.
- Se recomienda continuar consolidando configuraciones en `ConfigManager` y realizar pruebas adicionales para robustecer el manejo de errores y la validación de datos.

Este documento se actualizará conforme se realicen nuevas refactorizaciones o adiciones de funcionalidad.
