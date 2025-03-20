
# Plan de Integración y Validación para la Mejora de `leer_json()`

Este documento detalla cómo integrar el algoritmo recursivo propuesto en el flujo existente del método `leer_json()` y propone pruebas unitarias para validar su correcto funcionamiento.

## 1. Plan de Integración

### 1.1 Resumen del Flujo Actual

Actualmente, el método `leer_json()` tiene el siguiente flujo:

1. Se configuran opciones de validación
2. Se lee el archivo JSON como texto
3. Se parsea el contenido JSON
4. Se valida contra el esquema si se proporciona
5. Se procesa con `pandas.read_json()`
6. Si `normalize=True`, se llama a `_normalizar_dataframe_json_avanzado()`
7. Se retorna el DataFrame resultante o se maneja cualquier error

### 1.2 Pasos para la Integración

La integración del algoritmo recursivo requiere los siguientes pasos:

#### Paso 1: Implementar la función `_normalizar_dataframe_json_avanzado()`

La función ya ha sido implementada con un enfoque recursivo que:
- Detecta y clasifica estructuras anidadas (diccionarios, arrays)
- Procesa cada tipo de estructura según su naturaleza
- Utiliza configuración flexible para personalizar el comportamiento

#### Paso 2: Mejorar la documentación del parámetro `normalize_config`

Actualizar la documentación de `leer_json()` para especificar claramente las opciones disponibles en `normalize_config`:

```python
def leer_json(self, ruta_archivo, schema=None, orient='records', lines=False, 
              encoding='utf-8', convert_dates=True, normalize=False, 
              normalize_config=None, validate_options=None, **kwargs):
    """
    ...
    Args:
        ...
        normalize_config (dict, optional): Configuración avanzada para normalización:
            - max_depth (int): Profundidad máxima de normalización (por defecto 10)
            - explode_arrays (bool): Expandir arrays en múltiples filas (por defecto True)
            - sep (str): Separador para columnas anidadas (por defecto '.')
            - meta_prefix (str): Prefijo para columnas de metadatos (por defecto 'meta_')
            - handle_errors (str): Manejo de errores ('ignore', 'warn', 'raise')
            - ignore_columns (list): Lista de columnas a ignorar en normalización
            - only_columns (list): Lista de columnas a procesar (exclusiva con ignore_columns)
        ...
    """
```

#### Paso 3: Actualizar la sección de procesamiento

Modificar la sección donde se procesa el normalizado para asegurar que maneje correctamente el retorno y proporcione mensajes informativos:

```python
# Si se solicita normalización, procesar estructuras anidadas
if normalize and not df.empty:
    if normalize_config is None:
        normalize_config = {}
        
    print(f"Normalizando estructuras JSON anidadas con profundidad máxima: {normalize_config.get('max_depth', 10)}")
    return self._normalizar_dataframe_json_avanzado(df, normalize_config)
    
return df
```

#### Paso 4: Crear código auxiliar para casos especiales

Para manejar situaciones donde el resultado de la normalización produce múltiples DataFrames (como en el caso de arrays expandidos), podemos añadir una función auxiliar:

```python
def _manejar_resultado_normalizacion(self, resultado):
    """
    Procesa el resultado de la normalización para presentarlo al usuario.
    
    Args:
        resultado: Puede ser un DataFrame o un diccionario con resultados múltiples
        
    Returns:
        DataFrame o dict: Resultado procesado
    """
    if isinstance(resultado, dict) and 'main' in resultado and 'expanded' in resultado:
        print("\nSe encontraron estructuras anidadas que fueron expandidas en DataFrames adicionales:")
        for key, df in resultado['expanded'].items():
            print(f"- DataFrame expandido para '{key}': {len(df)} filas x {len(df.columns)} columnas")
        
        if input("\n¿Desea ver también los DataFrames expandidos? (S/N): ").upper() == 'S':
            return resultado
        else:
            return resultado['main']
    
    return resultado
```

#### Paso 5: Actualizar manejo de errores

Mejorar el manejo de errores específicos para la normalización:

```python
try:
    # ... código existente ...
    
    # Si se solicita normalización, procesar estructuras anidadas
    if normalize and not df.empty:
        if normalize_config is None:
            normalize_config = {}
        resultado = self._normalizar_dataframe_json_avanzado(df, normalize_config)
        return self._manejar_resultado_normalizacion(resultado)
        
    return df
    
except ValidationError as e:
    # ... código existente ...
except SchemaError as e:
    # ... código existente ...
except ValueError as e:
    if "normalizar" in str(e).lower():
        # Error específico de normalización
        if normalize_config and normalize_config.get('handle_errors') == 'ignore':
            print(f"Advertencia: Error en normalización ignorado: {str(e)}")
            return df  # Retornar el DataFrame sin normalizar
        else:
            raise
    else:
        # Otros errores de valor
        raise ValueError(f"Error al leer archivo JSON: {str(e)}")
```

### 1.3 Consideraciones Adicionales para la Integración

- **Rendimiento**: Para archivos JSON muy grandes con estructuras profundamente anidadas, considerar añadir opciones de procesamiento por lotes.
- **Compatibilidad**: Asegurar que el código es compatible con diferentes versiones de pandas.
- **Mensajes al Usuario**: Añadir información adecuada sobre el proceso de normalización, especialmente si es computacionalmente intensivo.
- **Registro (Logging)**: Implementar logging para rastrear el proceso de normalización, especialmente útil para depuración.

## 2. Pruebas Unitarias Propuestas

Para validar la implementación del algoritmo recursivo, se proponen las siguientes pruebas unitarias.

### 2.1 Pruebas para Estructuras Básicas

```python
def test_normalizacion_objetos_simples():
    """Prueba la normalización de objetos JSON con un nivel de anidamiento simple."""
    # Crear datos de prueba
    datos = [
        {"id": 1, "info": {"nombre": "Producto A", "precio": 100}},
        {"id": 2, "info": {"nombre": "Producto B", "precio": 200}}
    ]
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Crear instancia del lector
    lector = LectorArchivos()
    
    # Normalizar
    resultado = lector._normalizar_dataframe_json_avanzado(df)
    
    # Verificaciones
    assert "info.nombre" in resultado.columns
    assert "info.precio" in resultado.columns
    assert resultado["info.nombre"].iloc[0] == "Producto A"
    assert resultado["info.precio"].iloc[1] == 200
```

### 2.2 Pruebas para Arrays

```python
def test_normalizacion_arrays_objetos():
    """Prueba la normalización de arrays de objetos."""
    # Crear datos de prueba
    datos = [
        {"id": 1, "tags": [{"key": "color", "value": "rojo"}, {"key": "tamaño", "value": "grande"}]},
        {"id": 2, "tags": [{"key": "color", "value": "azul"}]}
    ]
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Crear instancia del lector
    lector = LectorArchivos()
    
    # Normalizar
    resultado = lector._normalizar_dataframe_json_avanzado(df)
    
    # Verificar que el resultado tiene la estructura esperada (main + expanded)
    assert isinstance(resultado, dict)
    assert "main" in resultado
    assert "expanded" in resultado
    assert "tags" in resultado["expanded"]
    
    # Verificar el DataFrame principal
    assert "meta_tags_json" in resultado["main"].columns
    
    # Verificar el DataFrame expandido
    tags_df = resultado["expanded"]["tags"]
    assert len(tags_df) == 3  # 2 tags del primer registro + 1 del segundo
    assert "key" in tags_df.columns
    assert "value" in tags_df.columns
    assert "__original_index" in tags_df.columns  # Para rastrear el origen
```

### 2.3 Pruebas para Estructuras Profundamente Anidadas

```python
def test_normalizacion_anidamiento_profundo():
    """Prueba la normalización de estructuras con múltiples niveles de anidamiento."""
    # Crear datos de prueba con anidamiento profundo
    datos = [{
        "id": 1,
        "metadata": {
            "creador": {
                "nombre": "Usuario1",
                "rol": "admin"
            },
            "sistema": {
                "version": "1.0",
                "componentes": [
                    {"nombre": "core", "activo": True},
                    {"nombre": "plugins", "activo": False}
                ]
            }
        }
    }]
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Crear instancia del lector
    lector = LectorArchivos()
    
    # Normalizar con profundidad máxima 3
    resultado = lector._normalizar_dataframe_json_avanzado(
        df, {"max_depth": 3}
    )
    
    # Verificaciones
    assert "metadata.creador.nombre" in resultado.columns
    assert "metadata.sistema.version" in resultado.columns
    assert isinstance(resultado, dict)  # Debido a los arrays expandidos
    assert "expanded" in resultado
    assert "metadata.sistema.componentes" in resultado["expanded"]
```

### 2.4 Pruebas de Configuración

```python
def test_configuracion_normalizacion():
    """Prueba diferentes opciones de configuración de normalización."""
    # Crear datos de prueba
    datos = [
        {"id": 1, "datos": {"a": 1, "b": 2}, "lista": [1, 2, 3]},
        {"id": 2, "datos": {"a": 3, "b": 4}, "lista": [4, 5]}
    ]
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Crear instancia del lector
    lector = LectorArchivos()
    
    # Probar ignorar columnas
    config1 = {"ignore_columns": ["lista"]}
    resultado1 = lector._normalizar_dataframe_json_avanzado(df, config1)
    assert "datos.a" in resultado1.columns
    assert "lista" in resultado1.columns  # No normalizada, se mantiene igual
    
    # Probar separador personalizado
    config2 = {"sep": "_"}
    resultado2 = lector._normalizar_dataframe_json_avanzado(df, config2)
    assert "datos_a" in resultado2.columns
    
    # Probar no expandir arrays
    config3 = {"explode_arrays": False}
    resultado3 = lector._normalizar_dataframe_json_avanzado(df, config3)
    assert "lista" in resultado3.columns  # Se mantiene como JSON string
    assert isinstance(resultado3["lista"].iloc[0], str)  # Convertido a string JSON
```

### 2.5 Pruebas de Integración con `leer_json()`

```python
def test_integracion_leer_json_normalize():
    """Prueba la integración completa con leer_json()"""
    # Crear un archivo JSON temporal para pruebas
    import tempfile
    import json
    
    datos = [
        {"id": 1, "detalle": {"nombre": "A", "precio": 100}},
        {"id": 2, "detalle": {"nombre": "B", "precio": 200}}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(datos, f)
        temp_file = f.name
    
    try:
        # Crear instancia del lector
        lector = LectorArchivos()
        
        # Leer sin normalización
        df1 = lector.leer_json(temp_file, normalize=False)
        assert "detalle" in df1.columns
        assert isinstance(df1["detalle"].iloc[0], dict)
        
        # Leer con normalización
        df2 = lector.leer_json(temp_file, normalize=True)
        assert "detalle.nombre" in df2.columns
        assert df2["detalle.nombre"].iloc[0] == "A"
        
        # Probar configuración personalizada
        df3 = lector.leer_json(
            temp_file, 
            normalize=True, 
            normalize_config={"sep": "_", "meta_prefix": "meta."}
        )
        assert "detalle_nombre" in df3.columns
    finally:
        # Limpiar archivo temporal
        import os
        os.unlink(temp_file)
```

### 2.6 Pruebas de Manejo de Errores

```python
def test_manejo_errores_normalizacion():
    """Prueba el manejo de errores durante la normalización."""
    # Crear datos problemáticos (estructura inconsistente)
    datos = [
        {"id": 1, "info": {"nombre": "A"}},
        {"id": 2, "info": [1, 2, 3]}  # Tipo inconsistente
    ]
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Crear instancia del lector
    lector = LectorArchivos()
    
    # Probar con distintas configuraciones de manejo de errores
    
    # 1. Debe lanzar excepción
    with pytest.raises(ValueError):
        lector._normalizar_dataframe_json_avanzado(
            df, {"handle_errors": "raise"}
        )
    
    # 2. Debe mostrar advertencia pero continuar
    import warnings
    with warnings.catch_warnings(record=True) as w:
        resultado = lector._normalizar_dataframe_json_avanzado(
            df, {"handle_errors": "warn"}
        )
        assert len(w) > 0  # Debe haber alguna advertencia
        assert "id" in resultado.columns  # Debe haber procesado lo posible
    
    # 3. Debe ignorar error y continuar silenciosamente
    resultado = lector._normalizar_dataframe_json_avanzado(
        df, {"handle_errors": "ignore"}
    )
    assert "id" in resultado.columns
    assert "info" in resultado.columns  # Se mantiene la columna original
```

## 3. Recomendaciones para la Implementación

1. **Implementación Incremental**:
   - Primero implementar y probar `_normalizar_dataframe_json_avanzado()` de forma aislada
   - Luego integrar con `leer_json()` y probar la interacción
   - Finalmente añadir el manejo de casos especiales y mejoras de usabilidad

2. **Documentación Exhaustiva**:
   - Documentar cada parámetro de configuración con ejemplos
   - Incluir casos de uso comunes en la documentación
   - Explicar las limitaciones conocidas (ej. rendimiento con estructuras muy grandes)

3. **Medidas de Rendimiento**:
   - Registrar métricas de rendimiento para diferentes tamaños y complejidades de datos
   - Implementar optimizaciones si se detectan cuellos de botella con conjuntos grandes

4. **Pruebas con Datos Reales**:
   - Además de las pruebas unitarias, probar con ejemplos reales del dominio
   - Verificar la usabilidad de los DataFrames resultantes para análisis posteriores

## 4. Ejemplo de Flujo de Usuario Final

1. El usuario carga un archivo JSON con estructuras anidadas:
   ```python
   lector = LectorArchivos()
   resultado = lector.leer_json("datos_complejos.json", normalize=True)
   ```

2. Si hay estructuras expandidas, se informa al usuario y se le da la opción de verlas:
   ```
   Se encontraron estructuras anidadas que fueron expandidas en DataFrames adicionales:
   - DataFrame expandido para 'productos': 15 filas x 8 columnas
   - DataFrame expandido para 'metadata.revisiones': 3 filas x 4 columnas

   ¿Desea ver también los DataFrames expandidos? (S/N): S
   ```

3. El usuario puede entonces trabajar con el DataFrame principal y los expandidos:
   ```python
   # DataFrame principal con estructuras planas
   df_principal = resultado['main']
   
   # DataFrames expandidos para arrays
   df_productos = resultado['expanded']['productos']
   df_revisiones = resultado['expanded']['metadata.revisiones']
   ```

Este enfoque de integración no solo mejora la funcionalidad técnica de `leer_json()`, sino que también proporciona una experiencia de usuario más rica y flexible para trabajar con datos JSON complejos.
