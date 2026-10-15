# Especificación viva y aprendizaje

Lee al cambiar requisitos, gobernar un gauntlet, incorporar aprendizajes o evaluar la skill.
Con biblioteca completa, abre `13/30`; el flujo inicial sigue en `13/28` y la coordinación,
crítica, recursos y recibos en `13/29`. Esta referencia conserva el procedimiento para un
paquete sin biblioteca, sin requerir Matt, Gentle, ECC ni sus ejecutores.

## Elegir el tamaño y la evidencia

Reutiliza la spec, tareas y sistemas actuales. Un bug acotado necesita reproducción,
criterio, cambio y prueba; no otro GDD. Un sistema nuevo añade contratos y dependencias.
Cada tarea entrega un recorrido completo observable, con errores y prueba de su unión.

La trazabilidad usa ID y versión de requisito → tarea → casos → recibos → decisión.
Distingue revisión del requisito de revisión del producto/WIP. Cuenta casos previstos,
ejecutados, fallidos, omitidos e inválidos; un caso favorable no cierra los demás.

| Criterio | Qué necesita demostrar |
|---|---|
| Comportamiento | Acción/estado en runtime; persistencia exige cerrar y reabrir |
| Experiencia | Hipótesis y conducta de jugadores observada; bots no prueban diversión |
| Presentación/fidelidad | Fuente y ejes fijados, comparación equivalente y crítica válida |
| Presupuesto | Escenario y medidas completas según el contrato del proyecto |

La aceptación corresponde a la autoridad vigente y se registra separada del estado técnico.
No se arrastra una aprobación de un eje a otro. Si no se puede observar un sentido o un
target, permanece pendiente con su límite. Un resultado del componente no aprueba la unión.

## Cambio de requisito

1. Registra ID/versión anterior → nueva, motivo, criterio y autoridad. Un ajuste dentro del
   encargo continúa con su autorización; un cambio de alcance conserva la decisión del usuario.
2. Recorre consumidores, escenas, guardado, datos/derivados, pruebas y requisitos vecinos.
   Marca evidencia afectada como histórica y casos pendientes; justifica lo que sigue vigente.
3. Actualiza casos y tareas dependientes. Reserva fronteras compartidas con dueño/integrador.
4. Construye y prueba en el conjunto integrado; registra resultado por caso, versión, huellas
   y entorno. Una compilación nueva no refresca baterías anteriores.

Una rúbrica, referencia o instrumento corregido también tiene versión y efecto en evidencia.
Si el control falla, invalida la medición y diagnostica el medidor antes de modificar el producto.
Una fuente exigida por fidelidad no debe ser forzada a recibir mala nota para validar el juicio.
Identifica al principio la regla vigente y marca como historia las instrucciones sustituidas.

Ejemplo GameMaker: `R-OP-01@1` cambia volumen en memoria; `@2` añade confirmar/persistir.
Una tarea recorre opciones → ajustar → cancelar; otra, tras acordar la frontera, confirmar →
guardar → cerrar → reabrir → mostrar/aplicar. Para concretar el oráculo del ejemplo:
valor previo 0,8, edición 0,3, default 0,8 y copia de recuperación 0,6. Los estados son cerrada →
editando → confirmando → cerrada; cancelar no aplica ni escribe; fallo de escritura deja
editando con aviso y valor previo. Todos estos casos son obligatorios para aceptar @2:

| Caso | Resultado esperado |
|---|---|
| C-OP-01 Cancelar | Valor aplicado/archivo permanecen en 0,8 |
| C-OP-02 Confirmar y reabrir | UI y mezcla recuperan 0,3 tras cerrar el proceso |
| C-OP-03 Archivo ausente | Default 0,8 y menú accesible, sin error de script |
| C-OP-04 Corrupción | Recuperar copia 0,6; sin copia, default 0,8 con aviso; conservar archivo defectuoso hasta confirmar |
| C-OP-05 Perder foco al editar | Sin aplicar/guardar; requiere pulsación nueva para confirmar |
| C-OP-06 Mando y reconexión | Mismos recorridos, sin confirmar solo ni duplicar escritura |
| C-OP-07 Desde pausa | Volver a pausa; mundo detenido mientras se edita; confirmar/cancelar conserva la semántica anterior |
| C-OP-08 Escritura fallida | Con previo 0,8: aviso, pantalla editable y aplicado 0,8; sin recibo de éxito |

Estas políticas son didácticas, no defaults para todos los juegos. Usa fixtures recuperables;
no dañes la partida real para construirlos. Omitir escritura en una copia de prueba debe
fallar C-OP-02. La aceptación exige ocho casos aprobados y control válido en la unión, sin
omisiones; la hipótesis de experiencia permanece separada. El recibo de @1 no aprueba @2.
Reutiliza entrada y guardado; recursos por
ResourceTool/MCP/IDE con un escritor, y exclusión para `.gmcache` y guardado efectivo.

## Rondas y promoción

Antes de iterar fija criterio, referencia, regresiones y presupuesto autorizado. Registra
fallos, empates, controles inválidos y cancelaciones. Mejora integrable y aceptación final
siguen puertas distintas. Sin progreso válido, diagnostica otra hipótesis; agotar intentos
no autoriza promover un rechazo, bajar umbrales o sustituir modelos.

Pausa o cuota agotada bloquean despachos y reintentos afectados, también después de esperas
y en descendientes desacoplados. Atribuye procesos y recursos antes de cerrar o declarar
recuperación. Un nombre de reserva no demuestra ausencia de contendientes reales.

## Promover un aprendizaje

1. Conserva hecho esperado/real, contexto y evidencia; separa hipótesis de causa comprobada.
2. Reproduce con un control que detecte el defecto. Revisa primero comprobación y ejemplo
   existentes. Un fallo mecánico pide control automatizable; uno de juicio, regla y ejemplo.
3. Acota motor/versión/target/género, contraejemplo y condición de retirada. Corrige el ejemplo
   que se copia antes de añadir advertencias a su lado.
4. Evalúa casos conocidos y otros independientes; preserva resultados negativos. Un revisor
   contrasta la propuesta antes de consolidar el método compartido.
5. Versiona el cambio y actualiza rutas, ejemplos y consejos sustituidos; verifica el paquete.
   Instalar hooks, escribir memoria global, cambiar modelos o publicar mantiene sus permisos.

Para evaluar la guía fija escenario/rúbrica/repeticiones antes; compara control sin guía
y variante con paquete/referencias en contextos frescos y condiciones comparables. Conserva
respuestas y calificación manual. Si ambos cumplen, informa ausencia de mejora causal
demostrada. Enlaces/YAML/compilación y búsqueda estática prueban propiedades distintas del
comportamiento de un agente; una respuesta tampoco demuestra ejecución real.

## Registros mínimos

Se añaden al tracker o documentos actuales; no requieren crear carpetas nuevas.

```text
CAMBIO: ID@anterior → ID@nueva; motivo/autoridad/criterio:
Impacto: consumidores, tareas, casos y evidencia histórica; lo conservado y por qué:
Integración: dueño/fronteras/controles; recibo por caso:
Decisión: estado técnico, aceptación y límites:

APRENDIZAJE: hecho/evidencia; hipótesis causal; reproducción/control:
Destino: ejemplo, comprobación o regla; versión/target/contraejemplo:
Evaluación: control/variante, casos independientes y resultados completos:
Promoción: revisar/aceptar/hipótesis; consejo sustituido y revisión:
```
