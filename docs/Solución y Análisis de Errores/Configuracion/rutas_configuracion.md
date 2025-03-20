# Resumen de Gestión de Rutas y Configuración

## Cambios Realizados

1. **Creación del Módulo de Configuración**
   - Se creó el archivo `utils/config_manager.py` que centraliza la definición de rutas base, directorios de datos, plantillas y otros parámetros globales.
   - Se implementa la carga de un archivo YAML (`config.yaml`) y, en caso de no existir, se usan valores por defecto.

2. **Actualización de Módulos Existentes**
   - En `clinic_manager.py` y `import_consolidator.py` se eliminaron rutas absolutas codificadas (por ejemplo,  
     `"C:/Users/pepec/Documents/Notefy IA/Data synthetic"`) y se sustituyeron por llamadas a `ConfigManager.get_base_path()`.
   - De esta forma, cualquier cambio en la estructura de directorios solo se deberá actualizar en el archivo de configuración.

3. **Validación de Configuración**
   - Se incluye una validación básica para verificar la existencia del archivo de configuración al iniciar la aplicación,
     lo cual permite personalizar el entorno sin modificar el código fuente.

## Ventajas de la Centralización

- **Mantenibilidad:** Todos los parámetros y rutas del sistema están definidos en un único lugar, facilitando cambios futuros.
- **Flexibilidad:** Se pueden proporcionar diferentes archivos de configuración para distintos entornos sin tocar el código.
- **Consistencia:** Se asegura que todos los módulos usen las mismas rutas base y configuraciones, reduciendo posibles errores.

Esta centralización simplifica la gestión del sistema y mejora la coherencia de la estructura de archivos y directorios.
