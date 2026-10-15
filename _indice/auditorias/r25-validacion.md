# r25 · Validación de biblioteca y skill r50

15-10-2026. [Criterios](r25-plan-y-criterios.md) · [Investigación de activación](r25-investigacion-activacion.md) · [Instalación](r25-investigacion-instalacion.md).

## Cambios comprobados

Una entrada GameMaker r50 y referencias por fase; consulta asesora inicial, decisiones
costosas y atascos con encargo breve, modelos conservados y crítico final separado.
La instalación pasa a Python estándar: todos los destinos compatibles por defecto,
Codex canónico, hashes, backups, idempotencia, aliases preservados y ruta por destino.
Bootstrap r50 con comprobación previa y biblioteca anterior conservada; entradas Bash y
PowerShell delegan en el mismo código. El paquete contiene 14 archivos y su manifiesto.
Se incorpora también el trabajo r49 de especificación viva y aprendizaje validado.

## Evidencia local

Host macOS 27.0.1 arm64. Python normal 3.14.7 sin PyYAML; mantenimiento 3.12.14,
PyYAML 6.0.3 y Pillow 12.2.0. GameMaker CLI 2.4.0, GMS2 2026.0.0.23. No se actualizaron.

| Puerta | Resultado |
|---|---|
| Instalación stdlib, incluso `-I -S` | 32/32 regresiones; paquete real cotejado sin dependencias adicionales |
| Bootstrap | 11/11, incluye actualización de enlace con contenido distinto, fallo de plan y restauración |
| Resolución de biblioteca | 3/3 sobre bloques distribuidos: copia, override y alias lógico |
| Sincronizador | 19/19 con el intérprete de mantenimiento; YAML estricto y manifiesto |
| Mantenimiento completo local | Exit 0; 23 instrumentos, 80 tareas estáticas, 3.213/3.213 símbolos localizables |
| GML documental | 3.477 bloques compilados; 306 exclusiones declaradas; no prueba runtime de cada receta |
| Scripts reutilizables | 13 compilan contra el runtime declarado |
| Banco de ejecución | 205 correctas, cero fallidas |
| Trampas del CLI | Las nueve comprobables siguen vigentes |
| Manual instalado | 3.119 páginas comparadas, sin diferencias señaladas por el medidor |
| Activación nativa y controles Codex | [Ensayo y trazas](r25-ensayos.md): carga natural, un asesor real; negativos con cero asesores |
| Revisiones frescas | [Normas](r25-revision-normas.md), [Spec](r25-revision-spec.md); hallazgos originales corregidos y revalidados |

La primera pasada integral contó 2.330 rutas y 1.641 anclas. Las cifras de enlaces cambian
al añadir recibos: el resultado vigente se conserva en el recibo final. El mantenimiento
completo incluye compilación en un proyecto desechable; no se ejecutaron juegos pausados.
Las tres puertas de GameMaker adicionales se ejecutaron secuencialmente.

## Correcciones encontradas durante la revisión

- Rutas iguales se deduplicaban, pero destinos anidados podían corromper la copia padre:
  ahora se rechazan antes de escribir y hay regresión.
- Actualización con enlace comparaba el plan contra staging: valida primero el paquete,
  promueve la ubicación estable y comprueba el plan real; restaura biblioteca si ese plan falla.
- Dos bibliotecas compartían una ruta global: cada destino conserva su asociación adyacente;
  un cambio de fallback global avisa y conserva el registro anterior.
- El sondeo Bash atravesaba un alias con `../`: usa su padre léxico y el bloque real se prueba.
- El diagnóstico de copias ignoraba overrides Claude/OpenCode: reutiliza el catálogo comprobado.
- El JSONL resumido Codex V2 no observa todo spawn: el ensayo coteja padre/hijo en el rollout completo.

`--comprobar` local valida paquete y plan sin escrituras. En el bootstrap valida solamente
la distribución sin promoverla; los enlaces se comprueban en la instalación normal contra
la ubicación estable. Las dependencias YAML/Pillow siguen siendo de mantenimiento.

## Distribución y preservación

El candidato parte del historial público r48 `519b5be795a86337da309f51a1f5696241edef74`.
Se transfieren archivos públicos seleccionados; el historial distinto y WIP de la raíz no
se publican. Los ensayos r49 se distribuyen como vistas anonimizadas verificables; los nuevos
ensayos nativos omiten reglas personales, texto cifrado, credenciales y rutas de máquina.
Corpus, juegos, conversaciones y logs completos quedan fuera. La comparación contra la
instantánea inicial comprueba que el resto del WIP no se alteró.

La publicación del candidato, los runners Windows/Linux y la instalación remota se registran
en el recibo de publicación posterior. No se presentan aquí como pruebas ya ejecutadas.

## Límites

La activación y asesoría se observaron en Codex 0.162.1/gpt-6.1-sol; los demás harnesses
mantienen pruebas de destino y sus loaders históricos, no un ensayo LLM nuevo. El usuario
eligió continuar con Codex tras el error OAuth de Claude; no se atribuye un fallo de cuota.
Las reglas y el catálogo global del anfitrión confunden una comparación causal de consumo.
No hay certificación universal de calidad, diversión, compatibilidad ni ausencia de bugs.
La crítica ciega y aceptación siguen siendo puertas de cada juego concreto.
