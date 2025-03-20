# Depuración de la Búsqueda de Plantillas en "Campos Master Global"

## Problema Identificado

El sistema no estaba detectando correctamente los archivos existentes en la carpeta "Campos Master Global" (como `Bio_Assessments_Campos.yaml`, `Far_Campos_38_campos.yaml`, `Pacientes_Campos_58_campos.yaml`, etc.) y mostraba el mensaje "No se encontraron templates" a pesar de que estos archivos existían.

## Análisis del Problema

Después de revisar el código, se identificaron los siguientes problemas:

1. **Limitación en las extensiones de archivo**: El código original solo buscaba archivos con extensión `.json`, pero muchos de los archivos de plantillas tenían extensiones `.yaml` o `.yml`.

2. **Falta de depuración**: El código no proporcionaba suficiente información de diagnóstico para identificar qué estaba fallando en la detección de archivos.

3. **Inconsistencia en la estructura de datos**: El código asumía que todas las plantillas tenían el mismo formato interno, pero había plantillas con formatos ligeramente diferentes (p.ej., 'campos' como diccionario vs. como lista).

4. **Manejo inadecuado de errores**: Cuando se encontraba un error al leer una plantilla, se pasaba a la siguiente sin proporcionar suficiente información sobre el error.

## Soluciones Aplicadas

Se realizaron las siguientes modificaciones en los métodos `listar_plantillas` y `_load_master_template` de la clase `TemplateManager`:

1. **Ampliación de extensiones reconocidas**:
   - Se modificó el código para buscar archivos con extensiones `.json`, `.yaml` y `.yml`.
   - Para cada extensión, se usa la librería adecuada para leer el contenido (json.load para JSON, yaml.safe_load para YAML).

2. **Añadido de mensajes de depuración detallados**:
   - Se agregan mensajes que muestran todos los archivos en el directorio antes de aplicar filtros.
   - Se registra cada paso del proceso: detección inicial, filtrado por extensión y procesamiento de cada archivo.
   - Se incluye más información sobre errores específicos al procesar cada archivo.

3. **Mejora en el manejo de diferentes estructuras de datos**:
   - El código ahora verifica si el campo 'campos' es un diccionario o una lista y maneja cada caso adecuadamente.
   - También identifica los nombres de los campos desde diferentes formatos de estructura.

4. **Mejor manejo de errores**:
   - Se implementó un manejo más robusto de excepciones, registrando los errores sin interrumpir el proceso completo.
   - Se muestran mensajes de error más descriptivos.

## Configuración Final

### Ruta para "Campos Master Global":
```
C:/Users/pepec/Documents/Notefy IA/Data synthetic/templates/Campos Master Global
```

### Patrones de Archivo Aceptados:
- `*.json` - Archivos JSON
- `*.yaml` - Archivos YAML
- `*.yml` - Archivos YAML con extensión alternativa

### Resultados de la Prueba:

Al ejecutar el código modificado con los archivos existentes en la carpeta "Campos Master Global", ahora se detectan correctamente todos los archivos de plantilla compatibles, independientemente de su extensión (JSON o YAML). Ya no aparece el mensaje "No se encontraron templates" cuando hay archivos válidos en la carpeta.

Los mensajes de depuración ahora muestran:

1. El número total de archivos en el directorio antes de aplicar filtros.
2. El nombre y extensión de cada archivo detectado.
3. Los archivos que cumplen con las extensiones compatibles.
4. El resultado del procesamiento de cada archivo (éxito o error).
5. El número final de plantillas procesadas correctamente.

Estas mejoras hacen que el sistema sea más robusto y permiten una mejor identificación de problemas en caso de que no se detecten correctamente las plantillas.
