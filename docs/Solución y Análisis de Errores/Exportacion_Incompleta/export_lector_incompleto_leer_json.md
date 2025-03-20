# Resumen de Mejoras en leer_json()

Se realizaron las siguientes mejoras en el método `leer_json()` del archivo `lector_archivos/lector.py`:

- Implementación de procesamiento en streaming para archivos JSON grandes utilizando la biblioteca `ijson`.
- Adición de validación contra un esquema JSON predefinido utilizando `jsonschema` cuando se proporciona el parámetro `schema`.
- Mejoras en el manejo de errores para capturar excepciones durante la lectura y validación del archivo.
- Soporte flexible para estructuras anidadas y arrays retornando el contenido del JSON sin modificaciones adicionales.

Estas mejoras permiten que el método `leer_json()` sea más robusto y adaptable a distintos formatos y tamaños de archivos JSON.
