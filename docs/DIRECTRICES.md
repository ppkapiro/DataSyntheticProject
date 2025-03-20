# Directrices de Desarrollo para Notefy IA

## 1. Gestión de Código y Estructura

### 1.1 Prevención de Duplicación
- **Obligatorio**: Revisar la estructura completa del proyecto antes de crear nuevos archivos
- Verificar módulos existentes para evitar duplicación de funcionalidad
- Reutilizar código existente mediante herencia o composición
- Mantener un registro centralizado de funcionalidades implementadas

### 1.2 Estructura de Módulos
- Mantener una estructura simple y coherente:
```
notefy_ia/
├── data/                 # Datos y recursos
├── templates/            # Plantillas y configuraciones
├── utils/               # Utilidades compartidas
├── core/                # Funcionalidad principal
└── tests/               # Pruebas unitarias
```

### 1.3 Principios de Diseño
- Favorecer la cohesión alta y el acoplamiento bajo
- Seguir el principio de responsabilidad única
- Mantener interfaces claras y bien documentadas
- Evitar la creación de módulos excesivamente granulares

## 2. Estándares de Código

### 2.1 Organización
- Agrupar funcionalidades relacionadas en el mismo módulo
- Limitar el tamaño de los archivos (máximo 500 líneas)
- Mantener una jerarquía clara de imports
- Documentar dependencias entre módulos

### 2.2 Nombrado
- Usar nombres descriptivos y significativos
- Seguir convenciones PEP 8
- Mantener consistencia en el estilo de nombrado
- Documentar abreviaciones en el glosario

## 3. Gestión de Dependencias

### 3.1 Externos
- Minimizar dependencias externas
- Documentar requisitos en requirements.txt
- Mantener versiones específicas
- Evaluar impacto de nuevas dependencias

### 3.2 Internos
- Evitar dependencias circulares
- Mantener un grafo de dependencias claro
- Documentar interfaces entre módulos
- Usar inyección de dependencias cuando sea apropiado

## 4. Documentación

### 4.1 Código
- Documentar todos los módulos con docstrings
- Incluir ejemplos de uso
- Mantener la documentación actualizada
- Explicar decisiones de diseño importantes

### 4.2 Arquitectura
- Mantener diagramas de arquitectura actualizados
- Documentar flujos de datos principales
- Explicar patrones de diseño utilizados
- Mantener un registro de decisiones arquitectónicas

## 5. Pruebas

### 5.1 Cobertura
- Mantener cobertura mínima del 80%
- Probar casos límite
- Incluir pruebas de integración
- Documentar casos de prueba

### 5.2 Organización
- Mantener pruebas junto al código
- Usar fixtures y helpers compartidos
- Seguir patrón AAA (Arrange-Act-Assert)
- Mantener pruebas independientes

## 6. Control de Versiones

### 6.1 Commits
- Usar mensajes descriptivos
- Mantener commits atómicos
- Referenciar issues/tickets
- Seguir convenciones de branching

### 6.2 Revisión
- Realizar code reviews
- Verificar estándares antes del merge
- Mantener histórico limpio
- Documentar cambios importantes

## Glosario

### Términos Comunes
- **PSR**: Facilitador de Servicios Psicosociales
- **FARC**: Formulario de Análisis y Registro Clínico
- **BIO**: Biografía del paciente
- **MTP**: Master Training Plan

### Abreviaciones
- **IA**: Inteligencia Artificial
- **PDF**: Portable Document Format
- **CSV**: Comma-Separated Values
- **JSON**: JavaScript Object Notation
- **YAML**: YAML Ain't Markup Language

## Referencias

1. PEP 8 - Guía de Estilo para Python
2. Clean Code por Robert C. Martin
3. Domain-Driven Design por Eric Evans
4. The Pragmatic Programmer por Andrew Hunt y David Thomas

---

**Nota**: Este documento debe ser revisado y actualizado regularmente para mantener su relevancia y efectividad.
