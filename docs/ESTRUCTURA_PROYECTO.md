# Estructura del Proyecto Notefy IA

## 1. Organización de Módulos

### 1.1 Módulos Core
- **templates/**: Gestión de plantillas y estructuras
  - Campos Codigos/: Archivos base para generación
  - Campos Master Global/: Plantillas procesadas y validadas

- **utils/**: Utilidades del sistema
  - template_management/: Gestión de plantillas
  - clinic_manager.py: Gestión de clínicas
  - file_naming.py: Convenciones de nombres
  - data_formats.py: Manejo de formatos

### 1.2 Módulos de Datos
- **FARC/**: Evaluaciones y seguimiento
- **BIO/**: Historiales biográficos
- **MTP/**: Planes de tratamiento
- **Data/**: Almacenamiento de datos por clínica

## 2. Flujos Principales

### 2.1 Procesamiento de Plantillas
1. Lectura de archivo fuente (Campos Codigos)
2. Análisis y extracción de estructura
3. Validación y enriquecimiento
4. Generación de plantilla master
5. Almacenamiento en Campos Master Global

### 2.2 Generación de Datos
1. Selección de plantilla master
2. Configuración de parámetros
3. Generación de datos sintéticos
4. Validación de coherencia
5. Exportación en formato seleccionado

## 3. Convenciones

### 3.1 Nombrado de Archivos
- Plantillas: `<tipo>_<num_campos>_campos_<timestamp>`
- Datos: `<clinica>_<tipo>_<timestamp>`

### 3.2 Estructura de Carpetas
```
Data/
└── [Clínica]/
    ├── FARC/
    │   ├── input/
    │   └── output/
    ├── BIO/
    ├── MTP/
    └── templates/
```

## 4. Notas Técnicas

### 4.1 Dependencias Principales
- pandas: Procesamiento de datos
- pyyaml: Manejo de YAML
- faker: Generación de datos sintéticos
- google-cloud-vision: OCR y análisis

### 4.2 Configuración
- Credenciales en archivo JSON
- Configuraciones en YAML
- Variables de entorno para APIs
