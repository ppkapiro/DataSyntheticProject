# Ejemplos de Estructuras JSON Anidadas y su Procesamiento

Este documento muestra ejemplos de diferentes estructuras JSON anidadas y cómo se procesan con el método `leer_json()` mejorado.

## 1. Estructuras de diccionarios anidados

### Ejemplo de entrada:
```json
[
  {
    "id": "paciente001",
    "nombre": "Juan Pérez",
    "datos": {
      "edad": 45,
      "sexo": "M",
      "contacto": {
        "telefono": "555-1234",
        "email": "juan@example.com"
      }
    }
  },
  {
    "id": "paciente002",
    "nombre": "María García",
    "datos": {
      "edad": 38,
      "sexo": "F",
      "contacto": {
        "telefono": "555-5678",
        "direccion": "Calle Principal 123"
      }
    }
  }
]
```

### Resultado normalizado:
```
| id          | nombre       | datos_edad | datos_sexo | datos_contacto_telefono | datos_contacto_email | datos_contacto_direccion |
|-------------|--------------|------------|------------|-------------------------|----------------------|--------------------------|
| paciente001 | Juan Pérez   | 45         | M          | 555-1234                | juan@example.com     | null                     |
| paciente002 | María García | 38         | F          | 555-5678                | null                 | Calle Principal 123      |
```

### Código para procesarlo:
```python
df = lector.leer_json("pacientes.json", normalize=True)
```

## 2. Arrays de primitivos

### Ejemplo de entrada:
```json
[
  {
    "id": "med001",
    "nombre": "Paracetamol",
    "dosis_recomendadas": [500, 1000, 1500],
    "incompatible_con": ["aspirina", "ibuprofeno"]
  },
  {
    "id": "med002",
    "nombre": "Amoxicilina",
    "dosis_recomendadas": [250, 500, 750, 1000],
    "incompatible_con": ["alcohol"]
  }
]
```

### Resultado normalizado:
```
| id     | nombre       | dosis_recomendadas     | incompatible_con      |
|--------|--------------|------------------------|------------------------|
| med001 | Paracetamol  | 500, 1000, 1500        | aspirina, ibuprofeno  |
| med002 | Amoxicilina  | 250, 500, 750, 1000    | alcohol               |
```

### Código para procesarlo:
```python
df = lector.leer_json("medicamentos.json", normalize=True, normalize_config={
    'arrays_to_string': True
})
```

## 3. Arrays de objetos

### Ejemplo de entrada:
```json
[
  {
    "id": "paciente001",
    "nombre": "Juan Pérez",
    "tratamientos": [
      {"medicamento": "Paracetamol", "dosis": "500mg", "frecuencia": "8h"},
      {"medicamento": "Ibuprofeno", "dosis": "400mg", "frecuencia": "12h"}
    ]
  },
  {
    "id": "paciente002",
    "nombre": "María García",
    "tratamientos": [
      {"medicamento": "Amoxicilina", "dosis": "750mg", "frecuencia": "8h"}
    ]
  }
]
```

### Resultado normalizado (con expansión):
```
| id          | nombre       | medicamento  | dosis  | frecuencia |
|-------------|--------------|--------------|--------|------------|
| paciente001 | Juan Pérez   | Paracetamol  | 500mg  | 8h         |
| paciente001 | Juan Pérez   | Ibuprofeno   | 400mg  | 12h        |
| paciente002 | María García | Amoxicilina  | 750mg  | 8h         |
```

### Código para procesarlo:
```python
# Expandir arrays de objetos en múltiples filas
df = lector.leer_json("tratamientos.json", normalize=True, normalize_config={
    'expand_arrays': True,
    'specific_paths': {
        'tratamientos': {'prefix': ''} # No añadir prefijo a las columnas expandidas
    }
})
```

## 4. Estructuras profundamente anidadas

### Ejemplo de entrada:
```json
[
  {
    "id": "paciente001",
    "historial": {
      "alergias": [
        {
          "tipo": "medicamento",
          "detalles": {
            "nombre": "penicilina",
            "severidad": "alta",
            "reacciones": ["erupciones", "dificultad respiratoria"]
          }
        },
        {
          "tipo": "alimento",
          "detalles": {
            "nombre": "maní",
            "severidad": "media",
            "reacciones": ["hinchazón"]
          }
        }
      ]
    }
  }
]