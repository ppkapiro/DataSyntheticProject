# Manual de Usuario - Sistema de Menús Notefy IA

## 1. Inicio del Sistema
Para iniciar el sistema, ejecute en la terminal:
```bash
python run.py
```

## 2. Menú Principal
El menú principal muestra las siguientes opciones:
1. Gestión de Clínicas
2. Procesamiento de Documentos
3. Gestión de Facilitadores
4. Generación de Datos
5. Reportes y Análisis
6. Herramientas de Desarrollo
0. Salir

### Navegación Básica
- Ingrese el número de la opción deseada y presione Enter
- Use '0' para volver al menú anterior o salir
- Los números deben estar entre los mostrados en el menú

## 3. Gestión de Clínicas
### 3.1 Crear Nueva Clínica
1. Seleccione opción '1' en el menú principal
2. Ingrese el nombre de la clínica cuando se solicite
3. El sistema creará automáticamente la estructura de carpetas necesaria

### 3.2 Seleccionar Clínica
1. Seleccione opción '2' en el menú principal
2. Elija la clínica de la lista mostrada
3. La clínica seleccionada quedará activa y mostrará su menú específico con las siguientes opciones:
   - Extracción de información
   - Gestión de PDF
   - Generación de datos sintéticos
   - Gestión de facilitadores
   - Reportes y análisis

### 3.3 Listar Clínicas
- Muestra todas las clínicas existentes en el sistema

## 4. Procesamiento de Documentos
### 4.1 Importar Documentos
Formatos soportados:
- CSV, Excel (XLS, XLSX)
- TSV, ODS (OpenDocument)
- JSON, YAML
- HTML y otros formatos tabulares

### 4.2 Procesar PDF
Tipos de documentos PDF soportados:
1. FARC (Evaluaciones)
2. BIO (Historiales)
3. MTP (Planes de tratamiento)
4. Notas de Progreso
5. Internal Referral
6. Intake

## 5. Gestión de Facilitadores
### 5.1 Ver Grupos y Pacientes
- Muestra la estructura de grupos
- Lista pacientes asignados a cada grupo
- Permite ver detalles de cada paciente

### 5.2 Asignar Pacientes
1. Seleccione el facilitador
2. Elija el turno (mañana/tarde)
3. Seleccione los pacientes a asignar

### 5.3 Actualizar Información
- Permite modificar datos de facilitadores
- Actualiza asignaciones de grupos

## 6. Generación de Datos
Tipos de datos que se pueden generar:
1. Pacientes
2. FARC
3. BIO
4. MTP

Para cada tipo:
1. Seleccione el tipo de datos
2. Configure cantidad de registros
3. Elija formato de salida
4. Confirme la generación

## 7. Reportes y Análisis
### 7.1 Ver Estadísticas
- Muestra métricas generales del sistema
- Presenta estadísticas por tipo de documento

### 7.2 Generar Informes
1. Seleccione tipo de informe
2. Configure período
3. Elija formato de salida

### 7.3 Exportar Datos
Formatos de exportación disponibles:
1. TXT (Texto plano)
2. JSON (Estructurado)
3. YAML (Legible)
4. CSV (Tabular)
5. XLSX (Excel)
6. HTML (Web)
7. TSV (Tabulado)
8. ODS (OpenDocument)

## 8. Consejos y Solución de Problemas

### 8.1 Problemas Comunes
- Si una opción no responde: Verifique que haya seleccionado una clínica
- Error de archivos: Revise permisos de carpetas
- Datos no visibles: Actualice la vista con la opción correspondiente

### 8.2 Mejores Prácticas
- Siempre seleccione una clínica antes de procesar documentos
- Valide los datos generados antes de exportar
- Mantenga una estructura organizada de carpetas
- Haga respaldos regulares de los datos importantes

### 8.3 Atajos y Tips
- Use '0' para volver al menú anterior en cualquier momento
- Confirme siempre los cambios cuando se solicite
- Verifique las rutas de archivos antes de procesar
- Mantenga actualizadas las plantillas de documentos

## 9. Notas Importantes
- Las operaciones de procesamiento pueden tomar tiempo según el volumen de datos
- Los archivos se guardan automáticamente en las carpetas correspondientes
- Los errores se registran en el archivo de log del sistema
- Mantenga actualizado el software para acceder a nuevas funcionalidades
