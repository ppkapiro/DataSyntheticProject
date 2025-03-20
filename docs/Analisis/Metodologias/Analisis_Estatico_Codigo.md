# Metodología Detallada: Análisis Estático de Código

## Introducción

El análisis estático de código es una técnica fundamental para comprender la estructura y organización de un sistema de software sin necesidad de ejecutarlo. Este documento detalla los procesos específicos para realizar un análisis estático efectivo del código fuente de Notefy IA, enfocándose en la identificación de dependencias, patrones de importación y referencias cruzadas entre módulos.

## 1. Generación de Gráficos de Dependencias

### Configuración de Herramientas

#### Pydeps

1. **Instalación**:
   ```bash
   pip install pydeps
   ```

2. **Ejecución básica**:
   ```bash
   pydeps --max-bacon=10 ruta/al/modulo_principal.py --output dependencias.svg
   ```

3. **Opciones recomendadas**:
   ```bash
   pydeps ruta/al/modulo_principal.py \
     --max-bacon=5 \             # Profundidad máxima de análisis
     --cluster \                 # Agrupar módulos por paquetes
     --show-deps \               # Mostrar texto descriptivo de dependencias
     --rankdir=LR \              # Dirección del gráfico (izquierda a derecha)
     --exclude "numpy|pandas" \  # Excluir bibliotecas externas específicas
     --output diagrama_completo.svg
   ```

#### Pyreverse (parte de Pylint)

1. **Instalación**:
   ```bash
   pip install pylint
   ```

2. **Generación de diagramas UML**:
   ```bash
   pyreverse -o png -p NotefyIA ruta/al/paquete/
   ```

3. **Opciones avanzadas**:
   ```bash
   pyreverse \
     -o svg \                     # Formato de salida
     -p NotefyIA \                # Nombre del proyecto
     -A \                         # Incluir atributos privados
     -S \                         # Incluir funciones/métodos privados
     -m y \                       # Incluir solo imports
     ruta/al/paquete/
   ```

### Interpretación de Resultados

1. **Identificación de Núcleos Funcionales**:
   - Buscar nodos con alto número de conexiones entrantes (dependencias)
   - Estos representan módulos centrales del sistema que requieren atención especial durante la refactorización

2. **Detección de Ciclos de Dependencia**:
   - Identificar ciclos (A → B → C → A) en el gráfico
   - Los ciclos indican problemas potenciales de diseño que deben resolverse

3. **Evaluación de Modularidad**:
   - Analizar la densidad de conexiones entre diferentes grupos de módulos
   - Un sistema bien modularizado muestra alta cohesión interna y bajo acoplamiento externo

4. **Documentación de Hallazgos**:

   Utilizar la siguiente plantilla para cada componente principal identificado:

   ```
   Componente: [nombre_del_componente]
   
   Dependencias entrantes: [número]
   - [modulo1.py]: [razón de dependencia]
   - [modulo2.py]: [razón de dependencia]
   
   Dependencias salientes: [número]
   - [modulo3.py]: [razón de dependencia]
   - [modulo4.py]: [razón de dependencia]
   
   Problemas identificados:
   - [Descripción del problema 1]
   - [Descripción del problema 2]
   
   Recomendaciones:
   - [Recomendación 1]
   - [Recomendación 2]
   ```

## 2. Análisis de Declaraciones de Importación

### Enfoque Automatizado

1. **Script de Extracción de Importaciones**:

   ```python
   import ast
   import os
   
   def extract_imports(file_path):
       with open(file_path, 'r', encoding='utf-8') as file:
           try:
               tree = ast.parse(file.read())
               imports = []
               
               for node in ast.walk(tree):
                   if isinstance(node, ast.Import):
                       for name in node.names:
                           imports.append({"type": "import", "name": name.name, "alias": name.asname})
                   elif isinstance(node, ast.ImportFrom):
                       module = node.module if node.module else ""
                       for name in node.names:
                           imports.append({
                               "type": "from", 
                               "module": module, 
                               "name": name.name, 
                               "alias": name.asname
                           })
               
               return {
                   "file": file_path,
                   "imports": imports
               }
           except SyntaxError:
               return {"file": file_path, "error": "Syntax error", "imports": []}
   
   def analyze_project_imports(project_dir):
       results = []
       for root, _, files in os.walk(project_dir):
           for file in files:
               if file.endswith('.py'):
                   file_path = os.path.join(root, file)
                   results.append(extract_imports(file_path))
       return results
   ```

2. **Ejecución del Análisis**:
   ```python
   project_imports = analyze_project_imports("/ruta/al/proyecto")
   
   # Exportar resultados a JSON para análisis posterior
   import json
   with open("project_imports.json", "w") as f:
       json.dump(project_imports, f, indent=2)
   ```

### Análisis Manual

1. **Categorización de Importaciones**:
   - Bibliotecas estándar de Python
   - Paquetes de terceros
   - Módulos internos del proyecto

2. **Identificación de Patrones**:
   - Módulos importados frecuentemente (alta reutilización)
   - Importaciones circulares (problemas de diseño)
   - Importaciones con alias (posibles conflictos de nombres)
   - Importaciones específicas vs. importaciones de módulos completos

3. **Documentación de Patrones**:

   ```
   Patrón de Importación: [nombre_del_patrón]
   
   Descripción:
   [Descripción del patrón observado]
   
   Ejemplos:
   1. En [archivo1.py]:
      ```python
      [ejemplo de código]
      ```
   
   2. En [archivo2.py]:
      ```python
      [ejemplo de código]
      ```
   
   Implicaciones:
   - [Implicación 1]
   - [Implicación 2]
   
   Recomendaciones:
   - [Recomendación 1]
   - [Recomendación 2]
   ```

## 3. Identificación de Referencias Cruzadas

### Metodología de Análisis

1. **Mapeo de Definiciones y Referencias**:
   - Utilizar herramientas como `jedi` o `rope` para encontrar todas las definiciones de clases y funciones
   - Identificar dónde se utilizan estas definiciones en el código

2. **Script para Análisis de Referencias Cruzadas**:

   ```python
   import jedi
   import os
   
   def find_references(project_path, symbol_name):
       references = []
       
       # Primero encontrar la definición del símbolo
       for root, _, files in os.walk(project_path):
           for file in files:
               if file.endswith('.py'):
                   file_path = os.path.join(root, file)
                   try:
                       with open(file_path, 'r', encoding='utf-8') as f:
                           source = f.read()
                           script = jedi.Script(source, path=file_path)
                           
                           # Buscar definiciones que coincidan con el nombre del símbolo
                           for name in script.get_names():
                               if name.name == symbol_name:
                                   # Para cada definición, buscar referencias
                                   for ref in name.get_references():
                                       references.append({
                                           "symbol": symbol_name,
                                           "ref_file": ref.module_path,
                                           "line": ref.line,
                                           "column": ref.column,
                                           "type": ref.type
                                       })
                   except Exception as e:
                       print(f"Error analyzing {file_path}: {e}")
                       
       return references
   ```

3. **Análisis de Flujo de Control**:
   - Construir un grafo dirigido donde los nodos son funciones/métodos
   - Las aristas representan llamadas entre funciones
   - Identificar caminos críticos y ciclos en el grafo

### Técnicas de Visualización

1. **Mapa de Calor de Referencias**:
   - Crear una matriz donde filas y columnas representan módulos
   - El color de cada celda indica la intensidad de las referencias entre módulos
   - Utilizar herramientas como matplotlib o seaborn para visualización

2. **Gráfico de Dependencias de Función**:
   - Utilizar NetworkX para crear gráficos de llamadas entre funciones
   - Resaltar funciones con alta centralidad (muchas conexiones entrantes/salientes)

3. **Plantilla para Documentar Referencias Cruzadas**:

   ```
   Entidad: [nombre_de_clase_o_función]
   Definida en: [archivo.py]
   
   Referencias:
   1. [archivo1.py]:[línea] - [contexto de uso]
   2. [archivo2.py]:[línea] - [contexto de uso]
   
   Grado de acoplamiento: [Alto/Medio/Bajo]
   
   Observaciones:
   - [Observación sobre el patrón de uso]
   - [Posibles problemas identificados]
   
   Sugerencias:
   - [Sugerencia para mejorar la modularidad]
   - [Opciones de refactorización]
   ```

## Integración de Resultados

### Creación de Matriz de Dependencias

1. **Estructura de la Matriz**:
   - Filas y columnas representan todos los módulos del sistema
   - Cada celda (i,j) indica la relación entre el módulo i y el módulo j
   - Utilizar códigos: D (dependencia directa), I (dependencia indirecta), vacío (sin dependencia)

2. **Cálculo de Métricas**:
   - **Acoplamiento aferente (Ca)**: Suma de dependencias entrantes (otras clases que dependen de esta)
   - **Acoplamiento eferente (Ce)**: Suma de dependencias salientes (clases de las que depende esta)
   - **Inestabilidad (I)**: Ce / (Ce + Ca), donde 0 representa máxima estabilidad y 1 máxima inestabilidad
   - **Abstracción (A)**: Proporción de interfaces y clases abstractas en relación con clases concretas
   - **Distancia de la secuencia principal**: |A + I - 1|, donde valores cercanos a 0 indican balance adecuado

3. **Visualización de Resultados**:
   - Crear un mapa de calor para visualizar la matriz
   - Utilizar colores para indicar la intensidad de las dependencias
   - Identificar clusters de módulos altamente interconectados

### Documentación de Hallazgos

1. **Informe de Dependencias**:
   - Resumen ejecutivo de los principales hallazgos
   - Lista de módulos centrales con alto grado de dependencia
   - Identificación de problemas arquitectónicos (ciclos, alta inestabilidad)
   - Recomendaciones para mejorar la estructura

2. **Formato de Informe**:

   ```markdown
   # Informe de Análisis Estático: Dependencias en Notefy IA
   
   ## Resumen Ejecutivo
   
   [Resumen de principales hallazgos y conclusiones]
   
   ## Métricas Globales
   
   - Número total de módulos: [número]
   - Densidad de dependencias: [porcentaje]
   - Módulos con mayor acoplamiento entrante: [lista]
   - Módulos con mayor acoplamiento saliente: [lista]
   - Ciclos de dependencia identificados: [número]
   
   ## Problemas Arquitectónicos Identificados
   
   1. [Problema 1]
      - Impacto: [Alto/Medio/Bajo]
      - Módulos afectados: [lista]
      - Descripción: [descripción]
   
   2. [Problema 2]
      - Impacto: [Alto/Medio/Bajo]
      - Módulos afectados: [lista]
      - Descripción: [descripción]
   
   ## Recomendaciones
   
   1. [Recomendación 1]
      - Prioridad: [Alta/Media/Baja]
      - Esfuerzo estimado: [Alto/Medio/Bajo]
      - Beneficio esperado: [Alto/Medio/Bajo]
      - Descripción: [descripción]
   
   2. [Recomendación 2]
      - Prioridad: [Alta/Media/Baja]
      - Esfuerzo estimado: [Alto/Medio/Bajo]
      - Beneficio esperado: [Alto/Medio/Bajo]
      - Descripción: [descripción]
   
   ## Anexos
   
   - [Enlace a matriz de dependencias completa]
   - [Enlace a visualizaciones generadas]
   - [Enlace a datos brutos del análisis]
   ```

## Herramientas Adicionales Recomendadas

1. **Pylint**: Además de la calidad del código, proporciona información sobre dependencias y complejidad
   ```bash
   pylint --reports=y --enable=similarities ruta/al/paquete/
   ```

2. **Radon**: Análisis de complejidad ciclomática y mantenibilidad
   ```bash
   radon cc -a ruta/al/paquete/
   radon mi ruta/al/paquete/
   ```

3. **Snakeviz**: Visualización de perfiles de ejecución
   ```bash
   python -m cProfile -o programa.prof ruta/al/script.py
   snakeviz programa.prof
   ```

4. **Dependency-check**: Verificar dependencias externas y vulnerabilidades
   ```bash
   dependency-check --scan ruta/al/proyecto --format JSON --out informe_dependencias.json
   ```

## Integración en el Flujo de Trabajo de Análisis

El análisis estático de código debe realizarse como primer paso en la Fase 1, ya que proporciona la base para los análisis posteriores de redundancias y patrones. Los resultados de este análisis deben guiar:

1. La selección de módulos para análisis manual detallado
2. La identificación preliminar de candidatos para refactorización
3. La comprensión de la arquitectura general para establecer una línea base

El proceso completo debería seguir este flujo:

1. Ejecutar análisis automatizado con las herramientas mencionadas
2. Revisar y documentar resultados iniciales
3. Seleccionar áreas críticas para análisis manual detallado
4. Integrar hallazgos en la matriz de dependencias
5. Calcular métricas y generar visualizaciones
6. Documentar problemas y recomendaciones en el informe final

## Conclusión

El análisis estático de código, cuando se realiza de manera sistemática utilizando la combinación adecuada de herramientas automatizadas y revisión manual, proporciona una base sólida para comprender la estructura actual del sistema. Esta comprensión es esencial para tomar decisiones informadas durante las fases posteriores de refactorización y rediseño arquitectónico de Notefy IA.
