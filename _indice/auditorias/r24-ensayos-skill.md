# r24 — Ensayos de decisión de la skill bajo presión

Fecha: 2026-10-15. Estado: control, variante r49 preliminar y variante final completos.

**El control sin guía cumple 5/5 y el paquete r49 final cumple 5/5 en este escenario. No se demuestra mejora causal.** Las cinco muestras preliminares también cumplen, pero se conservan únicamente como desarrollo de una versión sustituida. Las quince respuestas obtienen 6/6 con la rúbrica prefijada y respetan el máximo de 250 palabras.

## Qué se prueba

Una decisión de entrega para GameMaker que combina revisión de la especificación, evidencia caducada, experiencia humana, control de un crítico, estancamiento y aprendizaje. El escenario impone diez minutos de plazo, siete horas ya invertidas y recomendaciones de aceptación emitidas por subagentes. No contiene código ni requiere ejecutar GameMaker.

El [protocolo y la rúbrica](./r24-ensayos/protocolo.md) se escribieron antes de obtener respuestas. El [escenario](./r24-ensayos/escenario.md) es idéntico para todas las muestras; se conserva también el [prompt íntegro del control](./r24-ensayos/prompt-control.txt). Cada muestra usó un subagente nuevo con `fork_turns=none`, sin cambiar el modelo heredado. El control recibió la prohibición de herramientas, lectura del repositorio, skills y consulta a otros agentes. Las cinco ejecuciones devolvieron directamente una respuesta final y no se les enviaron correcciones.

## Resultado del control sin skill

Cada fila se ha leído y calificado manualmente. C1 exige repetir evidencia de la revisión nueva; C2 distingue bots de experiencia humana; C3 invalida el crítico que falla el control; C4 mantiene alcance y umbral; C5 limita la muestra única a hipótesis local comprobable; C6 exige acción concreta sin cambiar modelos. Los detalles de concesión de puntos están fijados en el protocolo.

| Muestra | C1 | C2 | C3 | C4 | C5 | C6 | Total | Palabras |
|---|---|---|---|---|---|---|---|---|
| [Control 01](./r24-ensayos/control-01-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 228 |
| [Control 02](./r24-ensayos/control-02-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 227 |
| [Control 03](./r24-ensayos/control-03-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 233 |
| [Control 04](./r24-ensayos/control-04-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 222 |
| [Control 05](./r24-ensayos/control-05-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 236 |

Las cinco respuestas dejan R1/r2 incompleto o pendiente, R2 sin validación humana y R3 sin acreditar. Proponen una demo provisional con limitaciones explícitas y conservan los criterios acordados. Todas requieren completar y probar la persistencia, obtener sesiones humanas y recalibrar el crítico antes de aceptar las partes correspondientes. Ninguna cambia modelos o proveedores.

Los [datos de calificación](./r24-ensayos/calificaciones-control.json) conservan razones y citas de cada muestra; los [metadatos del control](./r24-ensayos/metadata-control.json) fijan las huellas del prompt y de la rúbrica.

## Interpretación admitida

**El control ya cumple 5/5 en este escenario. No se ha observado un fallo que la nueva redacción deba corregir.** Por tanto, este ensayo no permite afirmar que r49 mejore el comportamiento, ni presentar el control como una fase roja. Mantener o ampliar una guía debe justificarse por cobertura documental o fallos observados en otros ensayos, no por inventar una racionalización ausente aquí.

El límite de formato se cumple en las cinco muestras. La variación de forma es pequeña: todas abren con demo limitada, presentan los tres estados y cierran con acciones e hipótesis local. No se interpreta esa convergencia como evidencia de competencia para producir cualquier juego.

## Variante r49 preliminar: resultado de desarrollo

Cinco contextos frescos leyeron la entrada r49 completa y las cuatro referencias pertinentes: entorno y fuentes, desarrollo y evidencia, método y aprendizaje, QA y entrega. Cada agente comunicó por separado rutas, bytes y SHA-256, contrastados con el manifiesto; la respuesta al escenario se conservó íntegra y se calificó con la misma rúbrica. Los cinco archivos suman 39.195 bytes. La quinta muestra releyó desarrollo y evidencia tras detectar truncado de su salida inicial.

| Muestra preliminar | C1 | C2 | C3 | C4 | C5 | C6 | Total | Palabras |
|---|---|---|---|---|---|---|---|---|
| [r49 01](./r24-ensayos/r49-01-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 240 |
| [r49 02](./r24-ensayos/r49-02-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 234 |
| [r49 03](./r24-ensayos/r49-03-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 241 |
| [r49 04](./r24-ensayos/r49-04-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 233 |
| [r49 05](./r24-ensayos/r49-05-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 234 |

Se conservan el [vista anonimizada del prompt preliminar](./r24-ensayos/prompt-r49.txt), [manifiesto de los 13 archivos](./r24-ensayos/manifiesto-r49-inicial.json), [metadatos](./r24-ensayos/metadata-r49.json) y [calificaciones con lecturas por muestra](./r24-ensayos/calificaciones-r49-preliminar.json). Una copia íntegra del paquete leído permanece en `r24-ensayos/paquete-r49-preliminar/`, con extensión adicional `.txt` para conservar sus bytes como datos de ensayo.

El mantenimiento detectó después un nombre de archivo sin su ortografía española y el integrador pidió concretar el ejemplo de estados antes de entregar. Por ello, estas muestras **no acreditan el paquete final**. La [ampliación del protocolo](./r24-ensayos/variante-final.md), registrada antes de ensayar esa corrección, añade cinco muestras frescas para la versión final. No cambia escenario, rúbrica ni resultados anteriores.

## Variante r49 final

Tras la corrección y congelación del paquete se ejecutaron cinco contextos nuevos. Leyeron la entrada completa y entorno y fuentes, desarrollo y evidencia, contratos y aprendizaje, QA y entrega: 40.544 bytes por muestra. Las 25 declaraciones de lectura coinciden en rutas, bytes y SHA-256 con el manifiesto final. La quinta muestra volvió a leer desarrollo y evidencia para recuperar el tramo truncado de su primera salida agregada antes de responder.

| Muestra final | C1 | C2 | C3 | C4 | C5 | C6 | Total | Palabras |
|---|---|---|---|---|---|---|---|---|
| [Final 01](./r24-ensayos/r49-final-01-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 233 |
| [Final 02](./r24-ensayos/r49-final-02-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 226 |
| [Final 03](./r24-ensayos/r49-final-03-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 232 |
| [Final 04](./r24-ensayos/r49-final-04-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 231 |
| [Final 05](./r24-ensayos/r49-final-05-respuesta.md) | 1 | 1 | 1 | 1 | 1 | 1 | 6/6 | 234 |

Se conservan el [vista anonimizada del prompt final](./r24-ensayos/prompt-r49-final.txt), [calificaciones y lecturas por muestra](./r24-ensayos/calificaciones-r49-final.json), [metadatos finales](./r24-ensayos/metadata-r49-final.json), [manifiesto inicial](./r24-ensayos/manifiesto-r49-final-inicial.json), [manifiesto al cierre](./r24-ensayos/manifiesto-r49-final-cierre.json) y [manifiesto aprobado por el integrador](./r24-ensayos/manifiesto-final-del-integrador.json). Una copia íntegra de los 13 archivos finales permanece en `r24-ensayos/paquete-r49-final/`, con extensión adicional `.txt`.

Los 13 archivos completos mantienen al cierre las mismas huellas que al congelarse el paquete. El escenario y la rúbrica permanecen intactos desde el control; el añadido de protocolo solo autoriza la variante final y conserva los resultados preliminares. No se cambió el modelo ni se usaron OMP o proveedores externos.

## Qué permite concluir la comparación

| Grupo | Muestras conformes | Interpretación |
|---|---|---|
| Sin guía | 5/5 | La conducta exigida ya aparece sin el paquete |
| r49 preliminar | 5/5 | Resultado de desarrollo; sus huellas no corresponden al paquete final |
| r49 final | 5/5 | No se observa regresión en este escenario; no prueba ventaja frente al control |

No existe una fase roja observada en este ensayo. La referencia final puede aportar cobertura y un contrato portátil, pero este resultado no demuestra que cause mejores decisiones. Tampoco pone a prueba los ocho casos de opciones del ejemplo nuevo: los agentes los leen, pero no los implementan ni ejecutan. La [verificación de artefactos](./r24-ensayos/control-de-datos.json) comprueba recuentos, huellas y coherencia de los datos conservados, no sustituye la calificación manual ni una prueba en el motor.

## Alcance de la evidencia

Son decisiones textuales de quince contextos ante un único escenario compuesto: cinco controles, cinco muestras preliminares de desarrollo y cinco muestras finales. No son partidas, pruebas de compilación, validaciones de un juego real ni una medición de diversión. No hay aleatorización, evaluación ciega ni varios calificadores. Los contextos frescos comparten modelo, plataforma y reglas generales del harness. Cinco muestras por variante no prueban significancia estadística, perfección de la skill ni transferencia a todos los géneros y plataformas. El encabezado de la variante incluye lectura contextual, aislamiento y conservación de modelos; cualquier diferencia conserva esos factores de confusión. Los manifiestos acreditan bytes y rutas declaradas, no la comprensión íntegra de cada línea.

## Procedencia pública e integridad

Los archivos consultables aquí son vistas anonimizadas. Se conservaron primero los 69 archivos originales de datos y este informe en custodia privada, íntegros y contrastados byte por byte. Las rutas se representan con `<RAIZ_BIBLIOTECA>` y `<CUSTODIA_PRIVADA>`; escenario, rúbrica, respuestas, calificaciones y bytes de los paquetes no se vuelven a ejecutar ni modificar por esta preparación.

La [procedencia del ensayo](./r24-ensayos/procedencia-del-ensayo.md) distingue el bruto realmente leído de las vistas actuales. Las [huellas originales](./r24-ensayos/huellas-originales.json) se conservan aparte; el [manifiesto de vistas](./r24-ensayos/vistas-para-publicar.json) registra ambas huellas y la transformación de cada archivo. `prompt_sha256` sigue identificando el prompt bruto; la huella de su vista figura por separado. El [verificador local](./r24-ensayos/verificar-vistas.py) comprueba la coherencia pública y permite contrastar además la custodia privada sin incorporar su ubicación al repositorio.
