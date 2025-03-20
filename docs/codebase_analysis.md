# Análisis de la Estructura del Proyecto

## Estructura General

```
Notefy IA/
├── core/
│   ├── import_consolidator.py
│   └── processors/
├── utils/
│   ├── template_management/
│   └── helpers/
├── main.py
└── docs/
```

## Diagrama de Dependencias

![Diagrama de dependencias](dependency_graph.png)

## Componentes Principales

### Main (main.py)
- Punto de entrada principal
- Gestión de comandos CLI
- Integración de componentes

### Core
- ImportConsolidator: Gestión de importación de datos
- Processors: Procesamiento de documentos

### Utils
- Template Management: Gestión de plantillas
- Helpers: Utilidades comunes

## Análisis de Dependencias

### Dependencias Principales
1. main.py → core.import_consolidator
2. main.py → utils.template_management
3. core.import_consolidator → utils.helpers

### Ciclos de Dependencia Detectados
Los ciclos de dependencia, si existen, se listarán aquí automáticamente.

## Recomendaciones

1. Mantener la separación de responsabilidades
2. Considerar la implementación de patrones de diseño
3. Documentar interfaces públicas
4. Mantener test coverage alto

## Métricas de Código

- Número total de módulos:
- Líneas de código:
- Cobertura de pruebas:
- Complejidad ciclomática promedio:

> Este documento se genera automáticamente usando el script codebase_analyzer.py
