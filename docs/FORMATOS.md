# Guía de Formatos de Archivo

## Formatos Soportados

### 1. TXT (Texto Plano)
- Codificación: UTF-8
- Uso: Contenido textual simple
- Ventajas: Fácil lectura, universal
- Ejemplo:
```
Contenido: texto extraído
Fecha: 2024-02-24
Calidad: 95%
```

### 2. CSV (Comma Separated Values)
- Delimitador: coma (,)
- Encabezados: primera fila
- Escape: comillas dobles (")
- Ejemplo:
```csv
id,nombre,fecha,valor
1,"Texto, con coma",2024-02-24,95
```

### 3. XLSX (Excel)
- Versión: Excel 2007+
- Hojas: datos en primera hoja
- Formatos: texto y numérico
- Ejemplo: Ver plantillas/

### 4. JSON
- Estructura: objetos anidados
- Codificación: UTF-8
- Identación: 2 espacios
- Ejemplo:
```json
{
  "contenido": "texto extraído",
  "fecha": "2024-02-24",
  "calidad": 95
}
```

### 5. HTML
- DOCTYPE: HTML5
- Tablas: bootstrap-style
- Responsive: sí
- Ejemplo: Ver plantillas/

### 6. YAML
- Versión: YAML 1.2
- Identación: 2 espacios
- Listas: guión (-)
- Ejemplo:
```yaml
contenido: texto extraído
fecha: 2024-02-24
calidad: 95
```

### 7. TSV
- Delimitador: tabulación
- Encabezados: requeridos
- Escape: comillas dobles
- Ejemplo:
```tsv
id  nombre  fecha valor
1   texto   2024  95
```

### 8. ODS
- Versión: OpenDocument 1.2
- Estructura: similar a Excel
- Compatible: LibreOffice
- Ejemplo: Ver plantillas/

# Formatos Soportados para Documentos

## 1. Procesamiento de PDF
Los PDFs se pueden procesar y exportar en los siguientes formatos:

### Formatos de Texto
- **TXT** (por defecto)
  - Codificación: UTF-8
  - Uso: Contenido textual simple
  - Extensión: `.txt`

### Formatos Estructurados
- **JSON**
  ```json
  {
    "fecha_extraccion": "2024-02-24T17:32:57",
    "tipo_documento": "FARC",
    "facilitador": "Nombre PSR",
    "paciente": "Nombre Paciente",
    "calidad_extraccion": 85,
    "contenido": "texto extraído...",
    "estadisticas": {
      "caracteres": 1500,
      "palabras": 300,
      "lineas": 50
    }
  }
  ```

- **YAML**
  ```yaml
  fecha_extraccion: 2024-02-24T17:32:57
  tipo_documento: FARC
  facilitador: Nombre PSR
  paciente: Nombre Paciente
  calidad_extraccion: 85
  contenido: texto extraído...
  estadisticas:
    caracteres: 1500
    palabras: 300
    lineas: 50
  ```

### Formatos Tabulares
- **CSV**
  ```csv
  fecha,tipo,facilitador,paciente,calidad,caracteres,palabras,lineas
  2024-02-24,FARC,"Nombre PSR","Nombre Paciente",85,1500,300,50
  ```

- **Excel (XLSX)**
  - Hojas: Metadata, Contenido, Estadísticas
  - Formatos: Texto y numérico
  - Fórmulas: No incluidas

## 2. Convenciones de Nombres
Los archivos exportados siguen el formato:
```
[nombre_original]_[YYYYMMDD_HHMMSS].[extension]
```
Ejemplo: `FARC-1234_20240224_173257.txt`

## 3. Ubicación de Archivos
```
clinica/
└── facilitador/
    └── grupos/
        └── turno/
            └── pacientes/
                └── nombre_paciente/
                    └── tipo_doc/
                        ├── input/
                        └── output/
```

## 4. Uso del DataFormatHandler
```python
from utils.data_formats import DataFormatHandler

# Exportar en múltiples formatos
formatos = ['txt', 'json', 'yaml', 'csv', 'xlsx']
for formato in formatos:
    DataFormatHandler.save_data(datos, ruta_salida, formato)
```

## Uso del Manejador de Formatos

```python
from utils.data_formats import DataFormatHandler

# Leer datos
data = DataFormatHandler.read_data("archivo.csv")

# Guardar datos
DataFormatHandler.save_data(
    data,
    "salida.json",
    formato="json"
)
```

## Notas Importantes
1. Siempre usar codificación UTF-8
2. Verificar permisos de archivo
3. Manejar errores de formato
4. Validar datos antes de guardar
