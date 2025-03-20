# INSTRUCCIONES FINALES PARA LA IMPLEMENTACIÓN DEL PROYECTO

# CONTEXTO:
El proyecto se ha estructurado de acuerdo a la "GUÍA MAESTRA" entregada, con la siguiente organización en:
  C:\Users\pepec\Documents\Notefy IA\Data synthetic\
La carpeta "Data" contiene subcarpetas por clínica (ej. Data/ClinicaABC), y dentro de cada clínica se encuentran:
  - pacientes/ (con input/ y output/)
  - FARC/ (con input/ y output/)
  - BIO/ (con input/ y output/)
  - MTP/ (con input/ y output/)
  - lector_archivos/ (con input/ y output/)
Además, existe el script maestro (master/main.py) y un archivo CSV en datos_csv/pacientes_ss.csv.

# OBJETIVO:
Integrar los siguientes módulos y funcionalidades:
1. **Módulo Lector de Archivos (lector_archivos/lector.py)**
   - **Lectura de Archivo:**
     - Implementar `leer_archivo(file_path)` que detecte la extensión (CSV, XLS, XLSX, TSV, ODS, JSON, YAML, HTML) y use pandas (o pyyaml para YAML) para leer el archivo en un DataFrame. Manejar excepciones y retornar (df, extensión).
   - **Análisis y Presentación de Estructura:**
     - Implementar `analizar_estructura(df)` que recorra cada columna y extraiga: 
         • Nombre del campo  
         • Tipo de dato (por ejemplo, usando df.dtypes)  
         • Un ejemplo representativo (primer valor no nulo)
     - Presentar la estructura en dos vistas:
         a) **Vertical:** Cada línea con formato:  
            `Campo: <Nombre>  |  Tipo: <Tipo>  |  Ejemplo: <Valor>`
         b) **Horizontal:** Una cabecera con los nombres de todas las columnas alineadas.
   - **Validación Interactiva:**
     - Implementar `validar_campos(df)` que, tras mostrar la estructura, pregunte:  
       "¿Desea modificar o ajustar alguno de los campos? (S/N)".  
       Si el usuario responde "S", permitir seleccionar el número del campo y solicitar nuevos valores para el nombre, tipo y ejemplo (o aceptar los valores actuales si se presiona Enter).  
       Repetir hasta que el usuario confirme que la estructura es correcta.
   - **Generación de Informe:**
     - Implementar `generar_informe_estructura(estructura, output_path)` que genere un archivo (TXT o CSV) con la estructura final, siguiendo la convención:  
       `<InicialesClinica>_<TipoArchivo>_DataMasterData_<HHMM>_<DDMM>.<ext>`  
       y que se guarde en la carpeta "output" del módulo lector_archivos de la clínica.
   - **Función Principal:**
     - Implementar `procesar_archivo(file_path, output_dir)` que combine la lectura, validación interactiva y generación del informe, mostrando un resumen final en consola.

2. **Módulos de Generación de Datos Sintéticos (pacientes, FARC, BIO, MTP)**
   - Cada módulo estará en su carpeta (por ejemplo, pacientes/pacientes.py) y deberá incluir una función principal de exportación, por ejemplo:
       • `exportar_pacientes(df_estructura, cantidad, clinic_initials, output_dir, formato="csv", use_api=False)`
       • Funciones similares en fars.py, bios.py, mtp.py (usando nombres: `exportar_fars()`, `exportar_bios()`, `exportar_mtp()`).
   - **Funcionalidad de Exportación:**
       - La función debe preguntar al usuario qué formato desea (CSV, XLSX, JSON, HTML, YAML, TSV, ODS).
       - Exportar el DataFrame (generado a partir de la estructura validada) en el formato seleccionado, usando la convención de nombres:  
         `<clinic_initials>_<modulo>_DataMasterData_<HHMM>_<DDMM>.<ext>`
       - Preguntar si se desea exportar en otro formato; repetir hasta que la respuesta sea "No".
       - Si no se dispone de lógica real de generación, se puede utilizar un DataFrame de ejemplo o mostrar el mensaje "Módulo [X] no implementado en su totalidad".
  
3. **Integración en el Script Maestro (master/main.py)**
   - Debe presentar un menú o interfaz de selección que permita al usuario elegir qué proceso ejecutar:
       1. Procesar archivo (lectura, análisis, validación y generación del informe).
       2. Generar datos sintéticos (preguntar qué módulo: pacientes, FARC, BIO, o MTP).
   - Al iniciar, preguntar:
       - "¿Desea extraer información de archivos exportados o generar archivos sintéticos?"
       - "¿Con qué nombre vamos a identificar la clínica?" y confirmar inmediatamente:  
         "¿El nombre [NombreClinica] es correcto?"
   - Según la respuesta, crear (o reutilizar) la carpeta de la clínica en Data y las subcarpetas de cada módulo (input y output).
   - Invocar las funciones correspondientes en cada módulo según la opción seleccionada.
   - Mostrar mensajes claros en caso de que algún módulo no esté implementado.

# REQUERIMIENTOS DE DEPENDENCIAS:
Asegurarse de que en requirements.txt se incluyan:
  - pandas
  - openpyxl
  - xlrd
  - odfpy
  - pyyaml
  - tabulate
  - faker (para la generación de datos sintéticos)

# NOTAS FINALES:
- Cada función debe tener comentarios que expliquen su propósito, entradas y salidas.
- El manejo de errores debe ser robusto, mostrando mensajes claros al usuario.
- La interacción debe ser modular e independiente: el usuario podrá ejecutar solo el módulo que necesite en cada momento.
- La presentación de la estructura de datos (en el módulo lector_archivos) se debe hacer de forma organizada, permitiendo la validación interactiva sin exportar datos de forma inmediata.

Favor de generar o actualizar los archivos correspondientes con la lógica mínima descrita para:
  - Lector de archivos: leer, analizar, validar y generar el informe.
  - Módulos de datos sintéticos: exportar datos en múltiples formatos siguiendo la nomenclatura uniforme.
  - Script maestro: integrar el flujo y ofrecer un menú de opciones.

