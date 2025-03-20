# Depuración del Menú Principal

## Modificaciones Realizadas

1. **Lectura y Depuración de Entrada:**
   - Se agregó el método `strip()` para eliminar espacios en blanco de la entrada.
   - Se incluyeron mensajes de depuración (debug prints) para mostrar la opción ingresada y el estado del bucle.

2. **Variable de Control para Salida:**
   - Se introdujo la variable `salir` que controla cuándo se sale del bucle.
   - Al detectar la opción "0", se actualiza la variable para terminar el ciclo y finalizar la ejecución.

3. **Manejo de Otras Opciones:**
   - Se agregaron bloques condicionales para opciones "1", "2" y "3" con mensajes de depuración, de modo que cualquier opción inválida se identifique y se notifique al usuario.

## Resultados de las Pruebas

- **Opción "0":** Al ingresar "0" (junto con espacios posibles), el menú se cierra correctamente y muestra el mensaje "Saliendo del sistema...".
- **Opciones "1", "2" y "3":** Se muestran los mensajes de depuración indicando la función llamada correspondiente.
- **Opción no válida:** Se notifica al usuario que la opción es incorrecta y se vuelve a mostrar el menú.

Estas modificaciones aseguran que el menú responda adecuadamente a la entrada del usuario, permitiendo salir o avanzar según corresponda.
