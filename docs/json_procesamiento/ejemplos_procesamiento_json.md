
# Ejemplos de Procesamiento Recursivo de JSON Anidado

Este documento presenta ejemplos prácticos que ilustran cómo el algoritmo de recorrido recursivo procesaría diferentes estructuras JSON anidadas.

## Ejemplo 1: Objeto JSON con Anidamiento Simple

### JSON Original
```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "direccion": {
      "calle": "Av. Principal 123",
      "ciudad": "Madrid",
      "codigo_postal": "28001"
    },
    "activo": true
  },
  {
    "id": 2,
    "nombre": "María García",
    "direccion": {
      "calle": "Calle Secundaria 456",
      "ciudad": "Barcelona",
      "codigo_postal": "08001"
    },
    "activo": false
  }
]
```

### DataFrame Resultante (Sin Procesamiento Recursivo)
| id | nombre       | direccion                                                   | activo |
|----|--------------|-------------------------------------------------------------|--------|
| 1  | Juan Pérez   | {'calle': 'Av. Principal 123', 'ciudad': 'Madrid', ...}     | True   |
| 2  | María García | {'calle': 'Calle Secundaria 456', 'ciudad': 'Barcelona', ...} | False  |

### DataFrame Resultante (Con Procesamiento Recursivo)
| id | nombre       | direccion.calle       | direccion.ciudad | direccion.codigo_postal | activo |
|----|--------------|------------------------|-----------------|------------------------|--------|
| 1  | Juan Pérez   | Av. Principal 123     | Madrid          | 28001                  | True   |
| 2  | María García | Calle Secundaria 456  | Barcelona       | 08001                  | False  |

## Ejemplo 2: Arrays de Objetos Anidados

### JSON Original
```json
[
  {
    "id": 1,
    "nombre": "Proyecto A",
    "tareas": [
      {"id": 101, "descripcion": "Diseño", "completada": true},
      {"id": 102, "descripcion": "Desarrollo", "completada": false}
    ]
  },
  {
    "id": 2,
    "nombre": "Proyecto B",
    "tareas": [
      {"id": 201, "descripcion": "Planificación", "completada": true}
    ]
  }
]
```

### Procesamiento Recursivo (Expansión en Filas)

#### DataFrame Principal
| id | nombre     | meta_tareas_json                                            |
|----|------------|-------------------------------------------------------------|
| 1  | Proyecto A | [{"id":101,"descripcion":"Diseño"...},{"id":102,...}]       |
| 2  | Proyecto B | [{"id":201,"descripcion":"Planificación"...}]               |

#### DataFrame Expandido para "tareas"
| __original_index | id  | descripcion   | completada | meta_source_column |
|-----------------|-----|---------------|------------|-------------------|
| 0               | 101 | Diseño        | True       | tareas            |
| 0               | 102 | Desarrollo    | False      | tareas            |
| 1               | 201 | Planificación | True       | tareas            |

## Ejemplo 3: Anidamiento Profundo con Tipos Mixtos

### JSON Original
```json
[
  {
    "id": 1,
    "metadata": {
      "creado_por": "usuario1",
      "fecha": "2023-01-15",
      "etiquetas": ["importante", "urgente"],
      "detalles": {
        "version": "1.0",
        "revisiones": [
          {"numero": "r1", "cambios": "Inicial"},
          {"numero": "r2", "cambios": "Correcciones"}
        ]
      }
    },
    "valor": 100
  }
]
```

### Procesamiento Recursivo (Niveles Múltiples)

#### DataFrame Principal
| id | metadata.creado_por | metadata.fecha | metadata.etiquetas      | metadata.detalles.version | meta_metadata.detalles.revisiones_json | valor |
|----|--------------------|-----------------|--------------------------|--------------------------|------------------------------------|-------|
| 1  | usuario1           | 2023-01-15      | ["importante", "urgente"] | 1.0                      | [{"numero":"r1","cambios":"Inicial"},...] | 100   |

#### DataFrame Expandido para "metadata.detalles.revisiones"
| __original_index | numero | cambios      | meta_source_column               |
|-----------------|--------|--------------|--------------------------------|
| 0               | r1     | Inicial      | metadata.detalles.revisiones   |
| 0               | r2     | Correcciones | metadata.detalles.revisiones   |

## Ventajas Demostradas

1. **Accesibilidad de datos anidados**: Los campos de objetos anidados se vuelven columnas accesibles directamente.

2. **Preservación de relaciones**: Se mantiene la relación entre los registros originales y los datos expandidos.

3. **Flexibilidad en el procesamiento**: Se aplican diferentes estrategias según el tipo de estructura encontrada.

4. **Control sobre la expansión**: Algunos arrays se convierten a strings JSON, mientras que otros se expanden según su complejidad.

5. **Trazabilidad**: Las columnas de metadatos permiten rastrear el origen de los datos expandidos.

## Consideraciones sobre la Implementación

- La expansión de arrays puede aumentar significativamente el número de filas
- Para estructuras muy complejas, limitar la profundidad de procesamiento puede ser necesario
- El balance entre normalización completa y mantener cierta estructura JSON debe evaluarse según el caso de uso
