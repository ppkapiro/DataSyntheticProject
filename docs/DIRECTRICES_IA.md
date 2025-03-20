# Directrices de Trabajo para la IA

## 1. Análisis Previo al Desarrollo

### 1.1 Evaluación de Estructura
- **CRÍTICO**: Analizar la estructura completa del proyecto antes de cualquier modificación
- **CRÍTICO**: Identificar módulos existentes y sus responsabilidades
- Entender las relaciones entre módulos
- Mapear dependencias y flujos de datos

### 1.2 Prevención de Redundancia
- No crear nuevos archivos sin verificar funcionalidad existente
- Buscar oportunidades de reutilización antes de escribir nuevo código
- Consolidar funcionalidades similares en módulos existentes
- Mantener un registro mental de funcionalidades implementadas

### 1.3 Gestión de Módulos
- Respetar la estructura de directorios establecida
- Mantener coherencia con la organización existente
- Evitar crear estructuras paralelas
- Priorizar modificación sobre creación

## 2. Proceso de Desarrollo

### 2.1 Modificaciones de Código
- Mantener el estilo de código existente
- Usar comentarios `# ...existing code...` para indicar código no modificado
- Incluir siempre el filepath en comentarios de inicio
- Mantener la consistencia en la documentación

### 2.2 Validaciones
- Verificar imports necesarios
- Comprobar dependencias circulares
- Validar tipos y argumentos
- Asegurar manejo de errores consistente

### 2.3 Integración
- Mantener coherencia con las interfaces existentes
- Respetar los contratos de las clases
- Mantener compatibilidad con funcionalidades existentes
- Verificar impacto en otras partes del sistema

## 3. Respuestas y Comunicación

### 3.1 Formato de Respuestas
- Usar estructura clara y consistente
- Agrupar cambios por archivo
- Proveer instrucciones concisas
- Mantener contexto relevante

### 3.2 Claridad
- Explicar cambios de manera concisa
- Destacar modificaciones críticas
- Indicar dependencias nuevas
- Documentar decisiones importantes

## 4. Control de Calidad

### 4.1 Autoverificación
- Revisar coherencia de la solución propuesta
- Validar completitud de las respuestas
- Verificar cumplimiento de estándares
- Asegurar claridad en las instrucciones

### 4.2 Prevención de Errores
- Evitar sugerir cambios no solicitados
- Mantener el alcance definido
- No asumir implementaciones
- Validar nombres de archivos y rutas

## 5. Gestión de Rutas y Archivos

### 5.1 Rutas de Archivos
- **CRÍTICO**: Usar siempre la base `/c:/Users/pepec/Documents/Notefy IA/Data synthetic`
- Mantener estructura de directorios existente
- Respetar convenciones de nombrado
- Verificar existencia de directorios

### 5.2 Organización
- Respetar la estructura del proyecto:
```
/Data synthetic/
├── data/
├── templates/
├── utils/
├── core/
└── tests/
```

## 6. Manejo de Errores y Excepciones

### 6.1 Identificación
- Detectar problemas potenciales
- Anticipar casos de error
- Validar entradas y salidas
- Verificar consistencia de tipos

### 6.2 Respuesta
- Proporcionar soluciones claras
- Explicar la causa del error
- Sugerir correcciones específicas
- Mantener trazabilidad

## Notas Específicas

### Prioridades
1. Mantener consistencia con el código existente
2. Evitar duplicación de funcionalidad
3. Respetar la estructura del proyecto
4. Proporcionar soluciones claras y concisas

### Restricciones
- No crear archivos innecesarios
- No modificar estructuras establecidas
- No ignorar estándares existentes
- No asumir implementaciones no documentadas

---

**Meta-regla**: Estas directrices deben ser aplicadas en cada interacción y actualizada según se identifiquen mejoras o nuevos patrones.
