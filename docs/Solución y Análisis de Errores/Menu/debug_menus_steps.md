# Instrumentación de Depuración en los Menús del Sistema

Este documento detalla la implementación de mensajes de depuración en todas las interfaces de menú del sistema, mostrando los puntos específicos de instrumentación y ejemplos de la salida generada durante la ejecución.

## Módulos Instrumentados

Se han identificado e instrumentado los siguientes módulos que implementan menús:

1. `master/main.py` - Menú principal del sistema
2. `utils/menu_manager.py` - Menú de gestión centralizada 
3. `utils/clinic_manager.py` - Menú de gestión de clínicas
4. `utils/template_manager.py` - Menú de selección de plantillas

## Puntos de Instrumentación Común

En cada módulo de menú, se implementaron los siguientes puntos de instrumentación:

### 1. Marcadores de Inicio y Finalización
```python
print("[DEBUG-MENU] Iniciando menú de [nombre del menú]")
# ...código del menú...
print("[DEBUG-MENU] Finalizando menú de [nombre del menú]")
```

### 2. Lectura y Validación de Opciones
```python
print("[DEBUG-ENTRADA] Solicitando entrada al usuario")
opcion = input("Seleccione una opción: ").strip()
print(f"[DEBUG-ENTRADA] Opción ingresada: '{opcion}'")
print("[DEBUG-VALIDACION] Validando opción ingresada")
```

### 3. Ejecución de Opciones
```python
print(f"[DEBUG-ACCION] Ejecutando opción {opcion}: [descripción]")
print("[DEBUG-MODULO] Invocando módulo [nombre_módulo]")
# ...código que ejecuta la opción...
print("[DEBUG-RESULTADO] Opción ejecutada con resultado: [resultado]")
```

### 4. Resumen de Iteración
```python
print("\n[DEBUG-RESUMEN] Resumen de ciclo de menú:")
print(f"[DEBUG-RESUMEN] Opción ejecutada: {opcion}")
print(f"[DEBUG-RESUMEN] Acciones realizadas: {', '.join(acciones_realizadas)}")
print(f"[DEBUG-RESUMEN] Tiempo de ejecución: {duracion} segundos")
```

## Detalles de Implementación por Módulo

### 1. master/main.py (Menú Principal)

#### Puntos Instrumentados:
- Inicio y finalización del sistema principal
- Inicialización del MenuManager
- Ciclo principal del menú, con contador de iteraciones
- Medición de tiempo para cada operación
- Registro de pasos ejecutados en cada ciclo

#### Ejemplo de Salida:
```
[DEBUG-INICIO] Iniciando sistema principal
...
[DEBUG-MENU] Iteración #1 del menú principal iniciando
[DEBUG-MENU] Preparando para mostrar opciones del menú
...
[DEBUG-ENTRADA] Opción ingresada por usuario: '1'
[DEBUG-VALIDACION] Verificando validez de la opción '1'
[DEBUG-ACCION] Opción 1: Preparando ejecución de crear_nueva_clinica()
[DEBUG-MODULO] Invocando módulo de creación de clínica en GestorSistema
...
[DEBUG-RESULTADO] Función crear_nueva_clinica() completada
[DEBUG-RESUMEN] Resumen de iteración #1:
[DEBUG-RESUMEN] Opción seleccionada: 1
[DEBUG-RESUMEN] Pasos ejecutados: Inicio de creación de nueva clínica, Finalización de creación de clínica
[DEBUG-RESUMEN] Duración de operación: 4.32 segundos
```

### 2. utils/menu_manager.py (Gestor de Menús)

#### Puntos Instrumentados:
- Inicio y fin de cada menú específico (principal, clínica, procesamiento)
- Registro de navegación entre menús
- Validación de opciones en cada menú
- Transiciones entre diferentes niveles de menú

#### Ejemplo de Salida:
```
[DEBUG-MENU-MANAGER] Iniciando mostrar_menu_principal()
[DEBUG-ENTRADA] Solicitando opción en menú principal
...
[DEBUG-VALIDACION] Validando opción '2' en menú principal
[DEBUG-TRANSICION] Navegando desde menú principal hacia menú de clínica
...
[DEBUG-MENU-MANAGER] Finalizando mostrar_menu_principal() con selección: '2'
```

### 3. utils/clinic_manager.py (Gestor de Clínicas)

#### Puntos Instrumentados:
- Operaciones de creación, selección y gestión de clínicas
- Búsqueda de archivos y directorios
- Validación de estructuras de carpetas
- Procesamiento de archivos según tipo

#### Ejemplo de Salida:
```
[DEBUG-CLINIC] Iniciando procesar_clinica() con clínica: 'Mi_Clinica'
[DEBUG-BUSQUEDA] Verificando existencia de clínica en ruta: C:/Users/.../Data/Mi_Clinica
[DEBUG-ESTRUCTURA] Validando estructura de directorios de la clínica
...
[DEBUG-ACCION] Ejecutando opción de procesamiento de PDF
[DEBUG-MODULO] Invocando PDFExtractor para procesar documento
...
[DEBUG-CLINIC] Finalizando procesar_clinica() exitosamente
```

### 4. utils/template_manager.py (Gestor de Plantillas)

#### Puntos Instrumentados:
- Búsqueda y carga de plantillas
- Validación de estructura de plantillas
- Selección de plantillas por el usuario
- Aplicación de plantillas a datos

#### Ejemplo de Salida:
```
[DEBUG-TEMPLATE] Iniciando carga de plantillas desde: C:/Users/.../templates
[DEBUG-BUSQUEDA] Encontradas 5 plantillas disponibles
...
[DEBUG-SELECCION] Usuario seleccionó plantilla: 'plantilla_consolidacion.json'
[DEBUG-VALIDACION] Verificando estructura de la plantilla seleccionada
...
[DEBUG-TEMPLATE] Plantilla cargada exitosamente con 15 campos
```

## Resultados y Beneficios

La instrumentación de depuración en todos los menús del sistema proporciona:

1. **Trazabilidad completa**: Permite seguir el flujo de ejecución a través de todos los menús.
2. **Detección temprana de problemas**: Facilita la identificación de errores en la navegación o procesamiento.
3. **Medición de rendimiento**: Los tiempos registrados ayudan a identificar cuellos de botella.
4. **Documentación dinámica**: Los mensajes actúan como documentación en tiempo de ejecución.

La estructura jerárquica de los mensajes de depuración (con prefijos como `[DEBUG-MENU]`, `[DEBUG-ENTRADA]`, etc.) facilita el filtrado y análisis de los logs generados, permitiendo enfocarse en aspectos específicos del funcionamiento del sistema.

## Configuración del Nivel de Depuración

En una implementación futura, estos mensajes podrían canalizarse a través del módulo `logging` de Python, permitiendo:

- Activar/desactivar depuración según entorno (desarrollo/producción)
- Ajustar el nivel de detalle (INFO, DEBUG, WARNING, etc.)
- Redirigir la salida a archivos de log en lugar de la consola

Por ahora, los mensajes se implementaron usando `print()` para mantener la simplicidad y visibilidad inmediata durante el desarrollo.
