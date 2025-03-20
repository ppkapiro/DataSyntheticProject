# Diagrama de Flujo Actualizado del Sistema

## Flujo Principal
```mermaid
flowchart TD
    A[Inicio] --> B{Menú Principal}
    B -->|1| C[Crear Clínica]
    B -->|2| D[Seleccionar Clínica]
    B -->|3| E[Listar Clínicas]
    
    C --> F[Configurar Facilitadores]
    F --> G[Crear Estructura]
    
    D --> H[Menú Clínica]
    H -->|1| I[Gestión Archivos]
    H -->|2| J[PDF Manager]
    H -->|3| K[Datos Sintéticos]
    H -->|4| L[Gestión PSR]
    H -->|5| M[Reportes]

    J --> N{Tipo PDF}
    N -->|FARC| O[Procesar FARC]
    N -->|BIO| P[Procesar BIO]
    N -->|MTP| Q[Procesar MTP]
    N -->|Notas| R[Procesar Notas]
    
    O & P & Q & R --> S[Extracción Texto]
    S -->|Calidad < 80%| T[Mejora IA]
    T --> U[Cloud Vision]
    T --> V[Textract]
```

## Estructura de Procesamiento PDF
```mermaid
flowchart TD
    A[PDF Input] --> B[PDFMiner]
    B -->|Fallo| C[PyPDF2]
    C -->|Fallo| D[OCR]
    D -->|Baja Calidad| E[IA APIs]
    E --> F[Google Vision]
    E --> G[Amazon Textract]
    
    B & C & D & E --> H[Evaluación Calidad]
    H -->|>80%| I[Guardar]
    H -->|<80%| J{Mejorar?}
    J -->|Sí| E
    J -->|No| I
```

## Nuevo Flujo de Datos
```mermaid
flowchart LR
    A[Input] --> B[Procesamiento]
    B --> C[Validación]
    C -->|OK| D[Output]
    C -->|Error| E[Mejora]
    E --> B
```

## Estructura de Carpetas Actualizada
```
Data/
├── Clínica/
│   ├── Facilitador/
│   │   ├── grupos/
│   │   │   ├── manana/
│   │   │   │   ├── pacientes/
│   │   │   │   │   └── [nombre_paciente]/
│   │   │   │   │       ├── FARC/
│   │   │   │   │       │   ├── input/
│   │   │   │   │       │   └── output/
│   │   │   │   │       ├── BIO/
│   │   │   │   │       ├── MTP/
│   │   │   │   │       ├── notas_progreso/
│   │   │   │   │       ├── Internal_Referral/
│   │   │   │   │       └── Intake/
│   │   │   └── tarde/
│   └── clinic_config.json
```
