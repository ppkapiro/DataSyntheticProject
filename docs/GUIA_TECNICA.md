# Guía Técnica del Sistema

## Arquitectura General

### Módulos Principales
1. **PDF Extractor**
   - Extracción de texto de PDFs
   - OCR con Tesseract
   - Evaluación de calidad
   - Múltiples formatos de salida

2. **FARC (Evaluaciones)**
   - Generación de datos sintéticos
   - Validación de formularios
   - Cálculos automáticos

3. **BIO (Historias)**
   - Generación de biografías
   - Datos consistentes
   - Relaciones lógicas

4. **MTP (Tratamientos)**
   - Planes de tratamiento
   - Seguimiento temporal
   - Objetivos realistas

### Sistema de Formatos
- Entrada/Salida universal
- Conversión automática
- Validación de datos
- Preservación de estructura

### Integración
- APIs externas
- Base de datos
- Servicios en la nube
- Sistemas legacy

## Desarrollo

### Requisitos
- Python 3.8+
- Dependencias en requirements.txt
- Tesseract-OCR (opcional)

### Estructura del Proyecto
```
Data synthetic/
├── docs/              # Documentación
│   ├── GUIA_TECNICA.md
│   ├── INSTALACION.md
│   ├── README.md
│   └── FORMATOS.md
├── master/            # Control principal
├── pdf_extractor/     # Extractor PDF
├── FARC/             # Módulo FARC
├── BIO/              # Módulo BIO
├── MTP/              # Módulo MTP
└── utils/            # Utilidades comunes
```

### Consideraciones de Diseño
1. Modularidad
   - Módulos independientes
   - Interfaces claras
   - Reutilización de código

2. Extensibilidad
   - Fácil agregar formatos
   - Nuevos tipos de datos
   - Integración de APIs

3. Mantenibilidad
   - Documentación clara
   - Tests unitarios
   - Control de versiones

## Referencias
- [Documentación Completa](README.md)
- [Guía de Instalación](INSTALACION.md)
- [Formatos Soportados](FORMATOS.md)
