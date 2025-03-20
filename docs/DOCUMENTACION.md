# Sistema de Generación de Datos Sintéticos para Clínicas

## 1. Descripción General
Sistema integral para analizar estructuras de datos clínicos y generar datos sintéticos para clínicas de rehabilitación psicosocial, garantizando la consistencia y validez de los datos generados.

## 2. Estructura del Proyecto
```
Data/
└── [CLINICA]/
    ├── pacientes/
    │   ├── input/               # Archivos originales
    │   └── output/              # Datos sintéticos de pacientes
    ├── FARC/                    # Módulo de alcohol y drogas
    │   ├── input/              
    │   └── output/             # Evaluaciones FARC sintéticas
    ├── BIO/                     # Módulo de biografías
    │   ├── input/              
    │   └── output/             # Historiales biográficos sintéticos
    ├── MTP/                     # Master Training Plan
    │   ├── input/              
    │   └── output/             # Planes de entrenamiento sintéticos
    └── lector_archivos/         
        ├── input/              # Archivos a analizar
        └── output/             # Archivos master (estructuras validadas)
```

## 3. Flujo de Trabajo

### 3.1 Análisis de Estructuras
1. **Lectura de Archivo Original**
   - Ubicación: `[CLINICA]/lector_archivos/input/`
   - Formatos soportados: CSV, XLS, XLSX, TSV, ODS, JSON, YAML, HTML
   - Detección automática del tipo de archivo

2. **Validación de Estructura**
   - Análisis de tipos de datos
   - Detección de valores nulos y su representación
   - Identificación de valores únicos
   - Ejemplos representativos

3. **Generación de Master Data**
   - Archivo de estructura validada
   - Ubicación: `[CLINICA]/lector_archivos/output/`
   - Nombre: `<CLINICA>_<TIPO>_DataMasterData_<HHMM>_<DDMM>.<ext>`

### 3.2 Generación de Datos Sintéticos

#### Módulo Pacientes
- Datos personales y demográficos
- Información de contacto
- Relaciones familiares
- Documentación legal

#### Módulo FARC (Alcohol y Drogas)
- Evaluaciones de uso de sustancias
- Frecuencia y patrones de uso
- Niveles de riesgo
- Tratamientos asignados
- Estado y progreso

#### Módulo BIO (Biografías)
- Antecedentes familiares
- Historial médico
- Situación actual
- Nivel de funcionalidad
- Apoyo familiar
- Objetivos terapéuticos

#### Módulo MTP (Master Training Plan)
- Planes de tratamiento
- Fechas de inicio y revisión
- Estado del plan
- Tipo de intervención
- Frecuencia de sesiones
- Objetivos y actividades
- Progreso y notas

## 4. Características Técnicas

### 4.1 Generación de Datos
- Valores numéricos: Distribución normal
- Fechas: Rangos específicos por módulo
- Textos: Faker + opciones predefinidas
- Preparado para integración con APIs

### 4.2 Manejo de Tipos
- Preservación de tipos originales
- Conversión automática según estructura
- Validación de formatos

### 4.3 Valores Nulos
- Respeto de campos opcionales
- Tipos específicos por campo:
  - Números: NaN
  - Textos: NULL/Vacío
  - Fechas: NULL
  - Booleanos: None

### 4.4 Nombrado de Archivos
- **Master Data**: 
  ```
  ABC_pacientes_DataMasterData_1330_0220.csv
  ```
- **Datos Sintéticos**: 
  ```
  ABC_Juan_Perez_pacientes_1330_0220.csv    # Un registro
  ABC_15p_pacientes_1330_0220.csv           # Múltiples registros
  ```

## 5. Uso del Sistema

### 5.1 Preparación
1. Crear estructura de carpetas
2. Colocar archivos originales en carpetas input
3. Validar nombre de clínica

### 5.2 Análisis
1. Seleccionar módulo
2. Elegir archivo a procesar
3. Revisar y validar estructura
4. Generar archivo master

### 5.3 Generación
1. Seleccionar módulo
2. Cargar estructura master
3. Especificar cantidad de registros
4. Seleccionar formato de salida
5. Exportar datos sintéticos

## 6. Formatos Soportados

### 6.1 Entrada
- CSV, XLS, XLSX, TSV
- ODS (OpenDocument)
- JSON, YAML
- HTML

### 6.2 Salida
- CSV (valores separados por comas)
- Excel (XLSX)
- JSON (con indentación)
- HTML (tabla formateada)
- YAML
- TSV
- ODS

## 7. Consideraciones
- Sin validación cruzada entre módulos
- Sin persistencia de configuraciones
- Sin interfaz gráfica
- Preparado para futura integración con APIs
