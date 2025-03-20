# Documentación del Sistema de Generación de Datos Sintéticos

## Índice de Contenidos

1. [Visión General](#visión-general)
2. [Módulos del Sistema](#módulos-del-sistema)
3. [Formatos Soportados](#formatos-soportados)
4. [Guías de Uso](#guías-de-uso)

## Visión General

El sistema está diseñado para generar y procesar datos sintéticos para historias clínicas, con especial énfasis en:
- Extracción inteligente de PDFs
- Generación de datos sintéticos realistas
- Soporte para múltiples formatos
- Validación y control de calidad

## Módulos del Sistema

### 1. PDF Extractor
- Extracción de texto de PDFs protegidos
- OCR integrado con Tesseract
- Evaluación de calidad de extracción
- Múltiples métodos de respaldo

### 2. FARC (Formulario de Evaluación)
- Generación de evaluaciones sintéticas
- Validación de campos requeridos
- Cálculos automáticos de puntajes

### 3. BIO (Historias Biográficas)
- Generación de historiales médicos
- Datos coherentes y realistas
- Relaciones familiares consistentes

### 4. MTP (Planes de Tratamiento)
- Generación de planes terapéuticos
- Objetivos y metas realistas
- Seguimiento temporal coherente

## Formatos Soportados

### Entrada/Salida
1. TXT - Texto plano
2. CSV - Valores separados por comas
3. XLSX - Excel
4. JSON - JavaScript Object Notation
5. HTML - HyperText Markup Language
6. YAML - YAML Ain't Markup Language
7. TSV - Tab Separated Values
8. ODS - OpenDocument Spreadsheet

### Características de Formato
- Codificación UTF-8
- Soporte multilingüe
- Preservación de estructura
- Validación de formato

## Guías de Uso

### PDF Extractor
```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor()
resultado = extractor.procesar_pdf(
    "archivo.pdf",
    "ruta/salida",
    clinic_initials="MI"
)
```

### FARC
```python
from FARC import GeneradorFARC

generador = GeneradorFARC()
farc = generador.generar_evaluacion(
    cantidad=1,
    use_api=False
)
```

### BIO
```python
from BIO import GeneradorBIO

generador = GeneradorBIO()
bio = generador.generar_historia(
    cantidad=1,
    use_api=False
)
```

### MTP
```python
from MTP import GeneradorMTP

generador = GeneradorMTP()
mtp = generador.generar_plan(
    cantidad=1,
    use_api=False
)
```

## Integración con APIs
El sistema está preparado para integración con:
- Google Cloud Vision API
- Amazon Textract
- Azure Computer Vision

## Notas de Desarrollo
- Versión mínima de Python: 3.8
- Tesseract-OCR requerido para OCR
- Dependencias en requirements.txt
