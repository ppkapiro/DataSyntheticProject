# Análisis de Funciones Principales por Módulo

## GestorSistema (master/main.py)

| Función | Descripción |
|---------|-------------|
| `_inicializar_recursos()` | Configura rutas, logs y recursos del sistema |
| `ejecutar()` | Coordina el flujo principal del programa |
| `get_menu_manager()` | Crea y retorna una instancia de MenuManager |
| `crear_nueva_clinica()` | Implementa la creación de una nueva clínica |
| `seleccionar_clinica()` | Permite seleccionar una clínica existente |
| `listar_clinicas()` | Muestra la lista de clínicas disponibles |

## ImportConsolidator (core/import_consolidator.py)

| Función | Descripción |
|---------|-------------|
| `consolidate_patient_data()` | Consolida datos de un paciente desde múltiples documentos |
| `_load_master_template()` | Carga la plantilla master para consolidación |
| `_find_patient_documents()` | Busca documentos relacionados con un paciente |
| `_process_documents()` | Procesa y extrae datos de múltiples documentos |
| `_mapear_datos_segun_template()` | Mapea datos extraídos según la estructura del template |
| `_generar_consolidacion_final()` | Genera el archivo final consolidado |

## MenuManager (utils/menu_manager.py)

| Función | Descripción |
|---------|-------------|
| `mostrar_menu_principal()` | Muestra el menú principal del sistema |
| `mostrar_menu_clinica()` | Muestra menú específico para gestión de clínica |
| `mostrar_menu_procesamiento()` | Muestra opciones para procesar archivos |
| `mostrar_menu_datos_sinteticos()` | Muestra opciones para generación de datos |
| `solicitar_ruta_archivo()` | Solicita al usuario la ruta de un archivo |

## ClinicManager (utils/clinic_manager.py)

| Función | Descripción |
|---------|-------------|
| `crear_clinica()` | Crea estructura de directorios para una nueva clínica |
| `procesar_clinica()` | Gestiona las operaciones sobre una clínica seleccionada |
| `verificar_estructura()` | Valida que la estructura de directorios sea correcta |
| `asignar_paciente_grupo()` | Asigna un paciente a un grupo específico |
| `listar_clinicas()` | Lista todas las clínicas disponibles |

## PDFExtractor (pdf_extractor/pdf_extractor.py)

| Función | Descripción |
|---------|-------------|
| `leer_pdf()` | Extrae texto de un PDF y calcula calidad |
| `usar_api_pdf()` | Utiliza APIs de IA para mejorar la extracción |
| `mejorar_calidad()` | Aplica técnicas para mejorar calidad de texto extraído |
| `procesar_pdf()` | Procesa un PDF y guarda resultado |

## DataFormatHandler (utils/data_formats.py)

| Función | Descripción |
|---------|-------------|
| `read_data()` | Lee datos de distintos formatos (CSV, Excel, JSON) |
| `convert_format()` | Convierte datos entre diferentes formatos |
| `validate_data()` | Valida datos contra un esquema o reglas |
| `save_data()` | Guarda datos en formato especificado |

## Módulos de Exportación

Todos los exportadores (`ExportadorPacientes`, `ExportadorFARC`, `ExportadorBIO`, `ExportadorMTP`) siguen un patrón común:

| Función | Descripción |
|---------|-------------|
| `generar_datos_sinteticos()` | Genera datos sintéticos según estructura dada |
| `exportar_X()` (donde X es pacientes, fars, bios, mtp) | Realiza la exportación de los datos generados |
| `validar_datos_X()` | Valida integridad de los datos antes de exportar |
| `solicitar_cantidad_registros()` | Solicita al usuario cuántos registros generar |
