# Guía de Instalación - Sistema de Generación de Datos Sintéticos

## 1. Requisitos del Sistema

### 1.1 Python
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### 1.2 Software Adicional
- Tesseract-OCR (para procesamiento de PDFs)
  - Windows: [Tesseract-OCR para Windows](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
  - Mac: `brew install tesseract`

### 1.3 Bibliotecas y Dependencias
```bash
# Procesamiento de datos
pandas>=2.0.0
numpy>=1.24.0

# Manejo de archivos
python-dateutil>=2.8.2
openpyxl>=3.1.0
xlrd>=2.0.1
odfpy>=1.4.1
pyyaml>=6.0
tabulate>=0.9.0

# Generación de datos
faker>=19.0.0

# Procesamiento de PDFs
pdfminer.six>=20221105
pytesseract>=0.3.10
Pillow>=10.0.0
pdf2image>=1.16.3
PyPDF2>=3.0.0
```

## 2. Instalación Paso a Paso

### 2.1 Preparación del Entorno

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd Data synthetic
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2.2 Instalación de Dependencias

1. Actualizar pip:
```bash
python -m pip install --upgrade pip
```

2. Instalar requerimientos:
```bash
pip install -r requirements.txt
```

### 2.3 Configuración de Tesseract

1. **Windows**:
   - Instalar desde el instalador oficial
   - Agregar al PATH: `C:\Program Files\Tesseract-OCR`

2. **Linux/Mac**:
   - La instalación vía apt/brew configura automáticamente

3. Verificar instalación:
```bash
tesseract --version
```

## 3. Verificación de la Instalación

1. Ejecutar pruebas:
```bash
python -m pytest tests/
```

2. Verificar módulos:
```bash
python master/main.py --test
```

## 4. Solución de Problemas

### 4.1 Errores Comunes

1. **Error: Tesseract no encontrado**
   ```
   pytesseract.pytesseract.TesseractNotFoundError
   ```
   Solución: Verificar instalación y PATH de Tesseract

2. **Error: No se pueden procesar PDFs**
   ```
   ModuleNotFoundError: No module named 'pdfminer'
   ```
   Solución: `pip install pdfminer.six`

3. **Error: Problemas con formatos de archivo**
   ```
   ImportError: Missing optional dependency 'openpyxl'
   ```
   Solución: Instalar bibliotecas opcionales:
   ```bash
   pip install openpyxl odfpy
   ```

### 4.2 Verificación de Componentes

Ejecutar el script de diagnóstico:
```bash
python utils/verify_installation.py
```

## 5. Actualizaciones

Para actualizar el sistema:
```bash
git pull
pip install -r requirements.txt --
