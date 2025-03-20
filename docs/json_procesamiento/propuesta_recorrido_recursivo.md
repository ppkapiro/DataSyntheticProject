
# Propuesta de Recorrido Recursivo para Procesamiento de JSON Anidado

## Introducción

El procesamiento de estructuras JSON anidadas requiere un enfoque sistemático que pueda manejar diferentes niveles de profundidad y tipos de datos. La implementación actual del método `leer_json()` no procesa adecuadamente estas estructuras complejas. Este documento propone un algoritmo recursivo para solucionar esta limitación.

## Ventajas del Enfoque Recursivo

1. **Manejo de profundidad variable**: Un enfoque recursivo permite procesar estructuras JSON independientemente de su nivel de anidamiento.

2. **Flexibilidad**: Permite aplicar diferentes estrategias de procesamiento según el tipo de estructura encontrada (objeto, array, valor simple).

3. **Control granular**: Posibilita establecer límites de profundidad y condiciones específicas para evitar procesamiento excesivo.

4. **Transparencia**: El proceso es más claro y fácil de mantener que enfoques iterativos complejos.

5. **Preservación de relaciones**: Mantiene las relaciones jerárquicas entre los datos durante la transformación.

## Algoritmo Propuesto

### Estructura General

```
función normalizar_dataframe_json_recursivo(dataframe, configuración):
    para cada columna en dataframe:
        si columna contiene objetos anidados:
            procesar_recursivamente(columna, nivel=0)
    retornar dataframe_procesado
```

### Pasos Detallados del Algoritmo

1. **Análisis inicial de columnas**
   - Recorrer todas las columnas del DataFrame
   - Identificar columnas que contienen objetos JSON anidados o arrays
   - Clasificarlas según su tipo (diccionario, array de diccionarios, array de valores)

2. **Procesamiento condicional por tipo**
   - Para columnas con diccionarios:
     - Extraer cada clave como una nueva columna
     - Añadir prefijo adecuado para mantener jerarquía
   - Para columnas con arrays de diccionarios:
     - Analizar si conviene expandir en filas ("explotar" el array)
     - O convertir a columnas separadas (si tienen estructura homogénea)
   - Para columnas con arrays simples:
     - Convertir a representación string JSON o expandir según configuración

3. **Control de profundidad**
   - Mantener contador de nivel de recursión
   - Establecer límite máximo configurable
   - Salir de la recursión cuando se alcance el límite

4. **Gestión de referencias**
   - Mantener registros de índices originales para preservar relaciones
   - Crear columnas de metadatos para indicar origen de datos expandidos

5. **Manejo de errores**
   - Implementar opciones configurables (ignorar, advertir, elevar excepción)
   - Registrar columnas problemáticas para diagnóstico posterior

6. **Reconstrucción del DataFrame**
   - Unir columnas expandidas con el DataFrame original
   - Manejar valores nulos en estructuras expandidas
   - Preservar tipos de datos cuando sea posible

## Pseudocódigo Detallado

```python
def normalizar_dataframe_json_recursivo(df, config):
    # Configuración con valores predeterminados
    max_depth = config.get('max_depth', 10)
    explode_arrays = config.get('explode_arrays', True)
    separator = config.get('separator', '.')
    
    def procesar_recursivo(df, nivel=0, parent_key=''):
        # Control de profundidad
        if nivel >= max_depth:
            return df
        
        resultado = df.copy()
        columnas_a_procesar = identificar_columnas_con_estructura(resultado)
        
        for columna, tipo in columnas_a_procesar.items():
            if tipo == 'dict':
                # Extraer campos del diccionario
                expandido = pandas.json_normalize(resultado[columna].dropna())
                # Añadir prefijos para mantener jerarquía
                prefijo = parent_key + columna + separator
                expandido = expandido.add_prefix(prefijo)
                # Unir con el DataFrame original
                resultado = unir_dataframes(resultado, expandido, columna)
                
            elif tipo == 'list_dict' and explode_arrays:
                # Expandir arrays de diccionarios en múltiples filas
                expandido = expandir_array_de_dicts(resultado, columna)
                # Procesar recursivamente el resultado expandido
                expandido_procesado = procesar_recursivo(
                    expandido, nivel + 1, parent_key + columna + separator
                )
                # Aquí se debe decidir cómo manejar el resultado expandido
                # (retornar múltiples dataframes o unirlos de alguna forma)
                
            elif tipo == 'list_simple':
                # Convertir arrays simples según configuración
                resultado[columna] = convertir_arrays_simples(resultado[columna])
        
        return resultado
    
    # Iniciar procesamiento recursivo
    return procesar_recursivo(df)
```

## Consideraciones Adicionales

1. **Configuración flexible**:
   - Permitir personalización del comportamiento mediante parámetros
   - Opciones para incluir/excluir columnas específicas
   - Control sobre el manejo de arrays y tipos de datos

2. **Rendimiento**:
   - Para conjuntos grandes, considerar procesamiento por lotes
   - Opciones para limitar la expansión de arrays muy grandes
   - Posibilidad de paralelizar el procesamiento de columnas independientes

3. **Compatibilidad**:
   - Mantener compatibilidad con pandas
   - Preservar índices y metadatos importantes
   - Asegurar que los tipos de datos sean consistentes

4. **Documentación**:
   - Documentar claramente los parámetros de configuración
   - Proporcionar ejemplos de uso para casos comunes
   - Explicar las limitaciones del enfoque recursivo

## Conclusión

El enfoque recursivo propuesto ofrece una solución robusta y flexible para el procesamiento de estructuras JSON anidadas en el método `leer_json()`. La implementación permitiría manejar adecuadamente diferentes niveles de anidamiento, arrays y tipos de datos, superando las limitaciones identificadas en la implementación actual.
