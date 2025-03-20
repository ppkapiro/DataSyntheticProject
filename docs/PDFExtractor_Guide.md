# Guía Completa del PDFExtractor

## Descripción General
El PDFExtractor es una clase robusta diseñada para extraer y procesar contenido de archivos PDF utilizando múltiples métodos y técnicas, con capacidad de mejora mediante IA.

## Características Principales

### 1. Métodos de Extracción
- **PDFMiner**: Método principal con configuración avanzada
- **PyPDF2**: Método de respaldo
- **OCR (Tesseract)**: Para PDFs con contenido no extraíble
- **APIs de IA**: 
  - Google Cloud Vision
  - Amazon Textract (planificado)

### 2. Tipos de Documentos Soportados
```python
{
    'FARC': 'Evaluación FARC',
    'BIO': 'Historia Biográfica',
    'MTP': 'Plan de Tratamiento',
    'pdf_notas': 'Nota de Progreso',
    'pdf_otros': 'Otro documento'
}
```

### 3. Optimización de Parámetros
```python
LAParams(
    line_margin=0.1,      # Detección de líneas
    char_margin=0.2,      # Agrupación de caracteres
    word_margin=0.1,      # Separación de palabras
    boxes_flow=0.7,       # Flujo de texto
    detect_vertical=True  # Soporte texto vertical
)
```

## Proceso de Extracción

### Flujo Principal
1. **Inicialización**
   - Verificación de dependencias
   - Configuración de parámetros
   - Preparación de extractores

2. **Extracción en Cascada**
   ```python
   # Orden de métodos:
   1. PDFMiner (calidad base: 100)
   2. PyPDF2 (calidad base: 70)
   3. OCR (calidad base: 60)
   4. APIs de IA (si se requiere mejora)
   ```

3. **Evaluación de Calidad**
   - Densidad de palabras
   - Longitud promedio de palabras
   - Palabras significativas
   - Formato del texto
   - Puntuación final ponderada

### Métricas de Calidad
```python
{
    'total_words': len(words),
    'avg_word_length': promedio_longitud,
    'significant_words': palabras_significativas,
    'lines_with_content': lineas_con_contenido,
    'formatting_score': puntuacion_formato
}
```

## Integración con IA

### Google Cloud Vision
- **Proceso**:
  1. Conversión de PDF a imágenes
  2. Procesamiento página por página
  3. OCR avanzado
  4. Evaluación de calidad

### Amazon Textract (Futuro)
- Pendiente de implementación
- Requiere credenciales AWS
- Diseñado para documentos complejos

## Uso del Sistema

### Ejemplo Básico
```python
extractor = PDFExtractor()
resultado = extractor.procesar_pdf(
    file_path="documento.pdf",
    output_dir="ruta/salida",
    clinic_initials="CLC",
    tipo_pdf="FARC"
)
```

### Formatos de Salida
- JSON
- YAML
- CSV
- TXT
- Personalizable mediante DataFormatHandler

## Requerimientos

### Software
- Python 3.8+
- PDFMiner
- PyPDF2
- Poppler (pdf2image)

### Opcionales
- Tesseract-OCR
- Google Cloud Vision API
- Amazon Textract API

## Manejo de Errores
- Captura de excepciones en cada nivel
- Métodos alternativos automáticos
- Registro detallado de errores
- Mensajes informativos al usuario

## Limitaciones Conocidas
1. Dependencia de Tesseract para OCR local
2. Requiere credenciales para APIs de IA
3. Proceso más lento con PDFs extensos
4. Dificultades con formatos muy complejos

## Mejores Prácticas
1. Mantener Tesseract actualizado
2. Configurar credenciales de API correctamente
3. Usar formatos de PDF estándar
4. Revisar la calidad de extracción
5. Considerar mejora con IA si la calidad es < 80%

## Soporte y Mantenimiento
- Registro de errores
- Actualizaciones periódicas
- Configuración personalizable
- Extensible para nuevos métodos

## Roadmap
1. Implementación de Amazon Textract
2. Mejoras en el OCR local
3. Soporte para más idiomas
4. Optimización de rendimiento
5. Nuevos formatos de salida
