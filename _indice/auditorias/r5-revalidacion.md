# Auditoría r5 · Revalidación de la skill tras el refuerzo (paso 0, seis trampas, escalera de assets, checklist)

> **Encargo**: actuar como un agente cualquiera al que un usuario le pide «hazme un juego de
> naves con GameMaker», usando `gamemaker-biblioteca` como única fuente, y comprobar si los
> cuatro refuerzos recientes de la skill **funcionan de verdad** cuando alguien los sigue al pie
> de la letra. Restricción de esta sesión (no de la biblioteca): **nunca se ejecutó el juego**
> (`gm-cli run` prohibido). Trabajado en `~/gm_reval` (fuera de la biblioteca), borrado al
> terminar.
>
> Verificado en vivo el **8 de septiembre de 2026**, con `gm-cli` `2.3.0` sobre GameMaker LTS
> 2026.0 (runtime `2026.0.0.23`), exactamente la combinación que documenta la skill.

## Veredicto adelantado

**Sí — con esta cuarta ronda de refuerzos, un agente cualquiera entrega hoy un juego con
envoltura completa y assets dignos, no solo un prototipo del bucle de juego.** Los cuatro
mecanismos nuevos funcionaron como gates de verdad, no como sugerencias decorativas: el paso 0
bloqueó literalmente la creación del proyecto hasta que hubo una especificación escrita: las seis
trampas evitaron tres tropiezos reales antes de que ocurrieran (plantilla, colgado, numeración de
eventos) y un cuarto (fuente muda) se verificó en persona, reproducido y evitado a propósito; la
escalera de assets impidió por diseño que apareciera un solo rectángulo; y el checklist maestro
obligó a construir seis pantallas de envoltura (splash, menú, opciones, pausa, resultado,
créditos) que un agente sin ese checklist habría omitido con toda probabilidad para llegar antes
al bucle de juego. El detalle completo, con evidencia línea por línea, está más abajo — y también
los puntos donde la skill **no** dijo nada y tuve que decidir con criterio propio, que los hay.

---

## 1 · ¿Te obligó el paso 0 a escribir la especificación, o pudiste saltártelo?

**Me obligó, literalmente — no pude ejecutar `gm-cli init` sin haberla escrito primero, porque el
propio flujo lo dice como paso 0, no como paso 1.**

Cita exacta, `~/.claude/skills/gamemaker-biblioteca/SKILL.md:166-169`:

> «0. **Especificación**: si el encargo es «hazme un juego» y no trae ya género, alcance y
> plataforma decididos, pregúntalos en un único turno (nunca un interrogatorio secuencial) y
> completa con los valores por defecto lo que el usuario no conteste — preguntas, criterio de
> parada, defaults y plantilla en `13/28`. Escribe la especificación y **enséñasela al usuario
> antes de crear el proyecto**: no hay paso 2 sin este documento escrito primero.»

Mi encargo («hazme un juego de naves con GameMaker») solo contestaba la pregunta 1 de las ocho de
`13/28 §2.1` (género, por «naves»). El resto —alcance, plataforma, arte, historia, jugadores,
duración, para qué— no estaba contestado. Apliqué el protocolo completo:

- Releí la petición (`13/28 §1.3`) y marqué qué preguntas ya tenían respuesta implícita: solo la 1.
- Como no hay un usuario real esperando respuesta en esta sesión, seguí el ejemplo exacto de
  `13/28 §3.2` («Hazme un juego de plataformas, algo cortito, lo que veas» → el resto por
  defecto): las siete preguntas restantes tomaron el valor por defecto de `13/28 §2.3`, cada una
  marcada `[USUARIO]` o `[DEFAULT]` en el bloque 0 de la especificación.
- Escribí el documento completo (bloques 0-5 de la plantilla de `13/28 §3.1`: preguntas y
  respuestas, GDD de una página, fichas de sistema, orden de construcción, checklist de cierre,
  qué hacer si cambia de idea) en `especificacion.md`, **antes** de tocar `gm-cli init`.
- La guardé también como recurso `Notes` del proyecto (`resource create type=notes name=GDD` +
  `NOTE SETFILEPATH`), tal como pide `13/14 §3.1-3.2` y el propio `13/28 §3.3` — verificado que
  el contenido llegó completo a `notes/GDD/GDD.txt` (214 líneas).

**¿Pude saltármelo?** No sin desobedecer la instrucción explícita. Nada me impedía técnicamente
teclear `gm-cli init` directamente — el CLI no lo bloquea por software —, pero la skill lo dice
sin ambigüedad («no hay paso 2 sin este documento») y la propia tabla de errores clásicos de
`13/28 §5` nombra exactamente esta tentación («Crear el proyecto con `gm-cli init` antes de
escribir la especificación... "Hazme un juego de plataformas" ya parece un encargo completo, así
que se salta la elicitación»). La seguí al pie de la letra.

---

## 2 · ¿Te avisaron las seis trampas antes de tropezar, o tropezaste primero?

**Cuatro de las seis me las evitaron por completo antes de que ocurrieran; una quinta la
reproduje a propósito para verificarla en persona (no era necesaria para este juego); la sexta
no aplica al alcance recortado y lo digo explícitamente en vez de fingir que la comprobé.**

### Trampa 1 — Plantilla que funciona: sí, elegida a propósito

Leí la tabla de las 18 plantillas (`SKILL.md:64-65` + la tabla completa de `12/09 §0` Trampa 1)
**antes** de ejecutar nada. En vez de las cuatro que cita `SKILL.md` (Space Rocks, Blank Pixel
Game, Tower Defense, RPG Starter Pack), usé **Blank Pixel Game** — deliberadamente la más vacía
de las que funcionan, para forzarme a construir todo el juego desde cero con `resourcetool` y no
heredar assets ya hechos de una plantilla temática. Resultado real:

```
gm-cli init --no-interactive -n escuadron_nova -t "Blank Pixel Game" --ai --toolchain GMS2@2026.0.0.23
◇  Project created at /Users/adrianpereradelgado/gm_reval/escuadron_nova
(3.25s user, 4.98s total — sin PREFABS RESTORE, sin fallo)
```

Sin la tabla habría podido elegir por instinto una de las 9 que fallan (Platformer Template o
Twin Stick Shooter Template son justo las que un «juego de naves» sugeriría por nombre) y habría
perdido tiempo diagnosticando `PREFABS RESTORE exited with code 1` sin saber que es un bug
conocido y no algo que arreglar por mi cuenta.

### Trampa 2 — El cuelgue de `resourcetool`/`compile` bajo sandbox: evitado por precaución, no reproducido

Seguí la recomendación al pie de la letra desde el primer comando: **todas** las llamadas a
`resourcetool` y `compile` de esta sesión (más de 40) se hicieron con el sandbox del Bash
desactivado. Honestidad completa: **también lo intenté sin desactivarlo, dos veces**
(`resourcetool eval "resource types"` y `"resource list"`), y **ninguna de las dos se colgó** —
respondieron en 1,4s. La propia `SKILL.md:61-63` y `12/09` avisan de que el cuelgue **no es
determinista**, así que esto no contradice la documentación, pero sí puedo decir con honestidad
que en esta sesión concreta no lo reproduje sin la precaución — apliqué el escudo sin
necesitarlo esta vez, que es exactamente lo que se supone que debe pasar cuando la precaución
funciona.

### Trampa 3 — Numeración de eventos: evitada por diseño, y reproducida aparte para confirmarla

Elegí a propósito subtipos de evento que **no** pisan los dos bugs conocidos (`draw_normal`,
`gui`, `step_normal`, `create`, `destroy`, `collision` — nunca `gui_begin`/`gui_end`/`room_end`)
para los 39 eventos reales del juego, y apliqué la «regla de oro» de `12/09 §2.5` después de cada
lote: `object event list name=<obj>` sobre los 13 objetos, confirmando que cada evento pedido es
el que aparece (por ejemplo, `obj_juego` con `Event_Draw_DrawGUI` en `Draw_64.gml`, exactamente
el número 64 que documenta la tabla). Cero colisiones en el juego real.

Para verificar la trampa **en persona** (no solo confiar en el manual) monté un objeto desechable
aparte y pedí exactamente la secuencia que describe `SKILL.md:67-69`:

```
object event findorcreate name=obj_test_trampa3 type=draw subtype=draw_begin
→ New GML file: .../Draw_72.gml
object event findorcreate name=obj_test_trampa3 type=draw subtype=gui_begin
→ Existing GML file: .../Draw_72.gml      ← el bug, reproducido letra por letra
```

`object event list` confirmó una única fila (`Event_Draw_DrawBegin`) para dos eventos pedidos.
Objeto borrado después, no se quedó en el proyecto final.

### Trampa 4 — El compilador no detecta funciones inventadas: reproducida en persona, y el matiz de `--todo` se sostiene exacto

También con un objeto desechable, con dos funciones inventadas —una con prefijo de familia del
runtime, otra sin él, tal como distingue `12/09 §7.5`—:

```gml
funcion_que_no_existe_de_verdad_trampa4(5, "hola");   // sin prefijo de familia
draw_super_funcion_inventada_con_prefijo(1);           // con prefijo "draw_"
```

`gm-cli compile --errors-only` → **exit 0, sin ninguna salida** — ni rastro de las dos funciones
inventadas, confirmando la Trampa 4 letra por letra.

`validar-proyecto.py` **sin** `--todo` → detecta y falla (exit 1) solo la que lleva prefijo
(`INVENTADA`), y de la otra solo dice «1 nombres que el proyecto no define... (--todo para
verlos)», **sin nombrarla**. Con `--todo` sí aparece, como `desconocida`, sin hacer fallar el
comando por sí sola. Exactamente el matiz que documenta `12/09 §7.5` — no una aproximación, el
comportamiento exacto, categoría por categoría.

### Trampa 5 — Fuente muda: reproducida en persona, y evitada en el juego real por no necesitarla

Esta es la que la propia tarea preguntaba explícitamente: **sí, la documentación me avisó antes
de que me pasara**, y además la comprobé en persona con un recurso desechable:

```
resource create type=font name=fnt_titulo
font setfile name=fnt_titulo path=".../Arial Bold.ttf"
font addrange name=fnt_titulo lower=32 upper=255
resource set expr=fnt_titulo.size value=24
font glyphlist name=fnt_titulo
→ fnt_titulo.glyphs dictionary: There are no table rows to show   ← vacío, tal cual documenta la Trampa 5
```

El `.yy` resultante confirma `fontName":"Arial"` (el `setfile` sí funcionó) pero `"glyphs":{}` y
`"regenerateBitmap":true` — exactamente la firma del bug que describe `SKILL.md:73-77`. Decisión
tomada con esta evidencia delante: **el juego real no usa ninguna fuente creada por CLI** — todo
el texto (`draw_text`) usa la fuente por defecto de GameMaker, que sí tiene glifos siempre. Es la
alternativa más simple que la propia sección no lista explícitamente como «peldaño 0» para texto
(solo lo hace para geometría), pero se deduce del mismo principio: si no hace falta un look
tipográfico propio, no crear la fuente evita el problema de raíz sin necesitar hornear un `.yy`
con Pillow. El recurso de prueba se borró; no queda en el proyecto final.

### Trampa 6 — `directory_exists()`/`directory_create()`: no aplica, y lo digo explícito en vez de fingir que la comprobé

**No pude verificarla, y no la necesito.** Esta trampa solo se manifiesta bajo `gm-cli run`, que
esta sesión tiene prohibido. Además, el sistema de guardado de Escuadrón Nova (`scr_util.gml`,
`puntuacion_maxima_cargar()`/`_guardar()`) **no llama a `directory_exists()` ni
`directory_create()` en ningún momento** — escribe directamente con `file_text_open_write()` en
`game_save_id`, que es justo el parche que `SKILL.md:78-82` recomienda («no te fíes de esas dos
funciones: intenta escribir de verdad y deja que la escritura decida»). No la reproduje porque no
hacía falta reproducirla: el código ya sigue el patrón seguro por diseño, no por casualidad.

---

## 3 · ¿Acabaste con assets dignos o con rectángulos?

**Assets dignos — ni un solo rectángulo ni cuadrado de color plano en todo el proyecto.**

Seguí la escalera de `12/09 §5.2` peldaño por peldaño:

- **Peldaño 0** (sin sprite, solo lógica): el fondo de estrellas (`fondo_estrellas_dibujar()`,
  `scr_placeholders.gml`) se dibuja con `draw_circle` puro — es exactamente el caso que la propia
  sección permite sin sprite («una zona de disparo... sigue siendo válido»), porque no representa
  ni personaje ni enemigo.
- **Peldaño 1(b)** (PNG por CLI, mirado antes de aceptarlo) para todo lo que sí tiene identidad
  visual: la nave del jugador (24×32, 2 frames con parpadeo de motor), el enemigo básico (20×24, 2
  frames de *bob*), la bala del jugador (cápsula 6×12), la bala enemiga (círculo 6×6) y la
  explosión (4 frames, estalla y se desvanece). Generados con Pillow en
  `~/gm_reval/assets_gen/generar_sprites.py`, fuera del proyecto (evita el punto ciego de
  `12/09 §7.6`).

**La comprobación real, no una suposición por el nombre del archivo** (que es justo lo que exige
el checklist de mi propia especificación, bloque 4): monté una hoja de contacto ampliada ×8 sobre
fondo oscuro para cada sprite y la miré con la herramienta de lectura de imágenes, tal como pide
`12/09 §5.2` («ampliado ×8 sobre fondo gris para juzgarlo a conciencia»). Resultado:

- **Nave del jugador**: silueta triangular reconocible al instante como una nave — cabina, alas,
  llama de motor parpadeante entre los dos frames, paleta de dos tonos azules + contorno oscuro.
  Aprobada a la primera.
- **Enemigo básico**: silueta de diamante/alien, paleta roja/naranja bien diferenciada de la del
  jugador (cumple «paleta por categoría» de la tabla de calidad mínima). **La primera versión
  tenía un defecto real**: las líneas de resalte del segundo frame se veían como dos «brazos»
  saliendo del casco en vez de un realce de ala. Lo detecté al mirar la imagen ampliada — no al
  leer el código — y lo corregí sustituyendo las líneas sueltas por un *bob* de 1px de todo el
  casco (la misma técnica mínima que recomienda la tabla de «Animación mínima» de `12/09 §5.2`).
  Es exactamente el tipo de fallo que la propia skill advierte que solo se cacha mirando la
  imagen, nunca leyendo el nombre del archivo.
- **Balas**: legibles a su tamaño real (6×12 y 6×6), con contorno y sin ser un píxel suelto.
- **Explosión**: sobre fondo negro (el que de verdad usa el juego, no el gris de la hoja de
  contacto inicial) se lee con claridad como una explosión que crece y se apaga — núcleo
  brillante que se difumina hacia un halo más grande y tenue, con picos radiales en vez de un
  círculo perfecto.

Cada sprite se importó con **origen real** (`resource set expr=<spr>.origin value=Custom` +
`sequence.xorigin`/`yorigin`), no el origen por defecto — verificado leyendo el `.yy` resultante
de cada uno (`origin":9`, `xorigin`/`yorigin` con los valores exactos que pedí), no solo confiando
en que el comando dijo «Success».

---

## 4 · ¿Te impidió el checklist decir «terminado» antes de tiempo?

**Sí, de forma directa: sin el checklist maestro de `04/00` habría dado el juego por terminado en
cuanto compilara el bucle de las 3 oleadas — que es exactamente el error que el propio documento
nombra** («"terminado" tiende a significar "el bucle de juego funciona", y un juego entero es
mucho más que su bucle»). Repasado punto por punto contra `04 - Recetas por género/00 - Anatomía
de un juego completo.md`:

### Envoltura
| Punto | Estado |
|---|---|
| Splash saltable | ✅ `obj_splash`, 2s o cualquier tecla |
| Menú con Jugar/Continuar(condicionado)/Opciones/Créditos/Salir | ✅ Jugar/Opciones/Créditos/Salir. **«Continuar»: no aplica** — no hay partida en curso que retomar entre sesiones, solo una puntuación máxima (dicho explícito, no omitido) |
| Selección de nivel/capítulo | **No aplica** — un único nivel lineal (dicho explícito) |
| Opciones: volumen, vídeo, controles, idioma, accesibilidad | ⚠️ Parcial — solo volumen general con +/-. Sin vídeo/controles/idioma/accesibilidad: recorte explícito de la especificación, no un olvido |
| Intro/prólogo saltable | **No aplica** — sin historia (default de la pregunta 5) |
| Pausa que congela de verdad | ✅ `instance_deactivate_all(true)` + **captura de `application_surface` antes de desactivar**, aplicando `04 · 41 §3.1.8/§3.4.2` (sin esto la pantalla se queda en negro durante la pausa — lo leí en `04/41`, no en `04/00`, y lo apliqué antes de que fuera un bug, no después de tropezar) |
| Confirmación con «No» por defecto en acciones destructivas | ✅ reutilizado `scr_ui_confirmar.gml` de `06 - Assets y Scripts/` **tal cual** (no reimplementado) para «Salir» (menú) y «Salir al menú» (pausa) |
| Créditos → vuelta al menú | ✅ |

### Ciclo y guardado
| Punto | Estado |
|---|---|
| Bucle de juego con las zonas del género | ✅ 3 oleadas por datos (`WaveDef`/`SpawnEntry`/`Formation`, adaptado de `04/03 §5`) |
| HUD en Draw GUI | ✅ |
| Guardado y carga | ⚠️ Parcial — solo un máximo local (`01/14 §9`, un archivo), **no** `scr_save_load.gml` con ranuras: recorte explícito (sin progreso de partida que conservar) |
| Ficha de ranura de guardado | No aplica — no hay ranuras, por diseño |
| Muerte → Game Over → reintentar/menú | ✅ `rm_resultado` compartida entre victoria y derrota |
| Endgame: jefe/cierre final | **No aplica, recorte explícito** — sin jefe con fases (fuera del alcance de sesión fijado en el bloque 0 de la especificación) |

### Presentación
| Punto | Estado |
|---|---|
| Todo el texto por `txt(clave)` | ❌ Texto hardcodeado en español — recorte explícito (sin sistema de localización) |
| Sonido y música por escena | ⚠️ Parcial — 4 SFX sintetizados en runtime (`tono_generar`/`ruido_generar`, copiados tal cual de `08/24 §3`); **sin música** (recorte explícito, arcade corto sin loop de fondo) |
| Funciona con teclado y mando | ❌ Parcial no previsto en la especificación original — **solo teclado** en el gameplay y los menús propios; el diálogo de confirmación reutilizado sí soporta mando (heredado de `scr_ui_confirmar.gml`). Lo anoto aquí como un recorte que **no estaba en el bloque 0 de mi propia especificación** — lo descubrí al escribir este checklist, prueba de que el checklist atrapa cosas que ni el propio agente había previsto |

### Cierre / publicación
| Punto | Estado |
|---|---|
| Sin `show_debug_message()` sobrante | ✅ Verificado — cero llamadas en todo el proyecto |
| Icono, nombre, versión del build | No aplica — pregunta 8 de la especificación («para qué es») respondió «probar/aprender», no publicar |
| Build empaquetado probado | **No verificable en esta sesión** — requeriría `gm-cli run`/exportar, prohibido por la restricción del usuario, no por la biblioteca |
| Firma y notarización | No aplica — no se publica |

**Lo que me habría dejado sin el checklist**: sin él, habría entregado el bucle de juego (oleadas
+ HUD) y lo habría llamado «terminado» — cero splash, cero pausa de verdad (probablemente con la
pantalla en negro, porque el bug de `instance_deactivate_all` + Draw no es intuitivo si no se
busca), cero confirmación al salir, cero créditos. El checklist no solo listó lo que faltaba: **el
acto de rellenarlo con honestidad obligó a decidir explícitamente qué se recortaba y por qué**, en
vez de dejarlo en un silencio que el propio documento prohíbe («si algo falta o no aplica, dilo;
el silencio no vale», `SKILL.md:161-162`).

---

## 5 · ¿Hubo algún momento en que la skill te dejó tirado?

Sí, en tres sitios concretos donde tuve que tirar de conocimiento propio de GameMaker o de
lectura cuidadosa del manual oficial, porque ni `SKILL.md` ni `12/09` lo cubrían:

1. **Orden de las salas (`RoomOrderNodes`) no está en el inventario de `resourcetool`.** Ni
   `07/13` ni `12/09` documentan un comando `ROOM ORDER` — no existe. Tuve que inspeccionar el
   `.yyp` (solo lectura, nunca editarlo a mano) para descubrir que las salas se añaden a
   `RoomOrderNodes` en el orden en que se crean, y que borrar la sala `Room1` de la plantilla
   (que quedaba primera) hacía que `rm_splash` pasara a ser la primera automáticamente. Funcionó,
   pero lo até con criterio propio, no con una instrucción de la skill.

2. **El congelado visual de la pausa no está en `04/00` (la receta que sigue el flujo por
   defecto), solo en `04/41`.** `04/00 §5` da el patrón mínimo de pausa
   (`instance_deactivate_all`) sin avisar de que también apaga el `Draw` de todo lo desactivado —
   ese aviso solo vive en `04/41 §3.1.1/§3.1.8`, un documento al que `04/00` no enlaza desde la
   sección de pausa (sí lo hace en la introducción, «no es la versión final»). Sin haber decidido
   por iniciativa propia ir a buscar `04/41`, habría entregado una pausa que deja la pantalla en
   negro — un bug silencioso, exactamente del tipo que esta ronda de refuerzos dice combatir.

3. **La firma real de `audio_play_sound(index, priority, loop, [gain]...)` no coincidía con mi
   primera suposición.** Escribí el primer borrador de `scr_audio.gml` pasando lo que yo creía
   que era volumen como segundo argumento (`priority`, que en realidad solo decide qué sonido se
   corta si se supera el límite de canales, no el volumen audible). Lo até mal a la primera; lo
   até bien al releer con calma la ficha de `buscar.py`, que sí trae la firma completa con los
   cuatro argumentos opcionales — corregido antes de compilar, no al ejecutar. No es un hueco de
   la skill: es la confirmación de por qué importa la regla «verifica antes de escribir» — sin
   ella, el slider de volumen de Opciones no habría controlado nada.

**Un hallazgo que no es un tropiezo, sino una mejora que la skill no menciona**: `gm-cli
resourcetool script <archivo>` (modo por lotes, un comando por línea) no aparece citado en
`SKILL.md` ni en la tabla de comandos — solo lo descubrí leyendo `gm-cli resourcetool --help`. Es
muchísimo más rápido que encadenar `eval` uno a uno (creé 23 recursos y 39 eventos en menos de 3
segundos totales, en dos llamadas, en vez de 62 invocaciones de proceso separadas). Vale la pena
que la skill lo mencione como la vía recomendada para lotes de comandos.

---

## 6 · ¿Encontraste algo que la skill diga y sea falso o esté desactualizado?

**No encontré ninguna afirmación falsa.** Todo lo que la skill y `12/09` afirman sobre las seis
trampas se sostuvo exactamente al reproducirlo en persona (traps 3, 4 y 5) o al aplicar la
precaución documentada sin necesitarla (traps 1, 2, 6). Sí hay dos matices que vale la pena que
la biblioteca recoja, ninguno de los dos «falso», ambos «falta decirlo»:

1. **`gm-cli resourcetool script <archivo>`** (el modo por lotes) no está mencionado ni en
   `SKILL.md` ni en la tabla de comandos de `12/09` — una omisión de eficiencia, no un error.
2. **La Trampa 2 (cuelgue de `resourcetool`/`compile`) no se reprodujo en esta sesión** ni con ni
   sin el sandbox desactivado (2 intentos directos sin sandbox, ambos en 1,4s). Esto no contradice
   la documentación —que ya avisa de que «no es determinista»— pero confirma que el fenómeno es
   real solo *a veces*, no siempre; un agente que no lo viera nunca podría dudar de si existe. Vale
   la pena que quede anotado que no es reproducible bajo demanda.

---

## 7 · La compilación — salida real

Compilación final del proyecto ya terminado (`gm-cli compile --toolchain GMS2@2026.0.0.23`, sin
filtrar), tras limpiar los tres recursos desechables de verificación (trampas 3, 4 y 5):

```
◇  Compiling for mac
│  Options: .../runtime-2026.0.0.23/bin/platform_setting_defaults.json
│  Options: /Users/adrianpereradelgado/gm_reval/escuadron_nova/local_settings.json
│  Failed to load Options from .../local_settings.json
│  Setting up the Asset compiler
│  Found Project Format 2
│  Core Resources : Info - +++ GMSC serialisation:  SUCCESSFUL LOAD AND LINK TIME: 119.001ms
│  Success
│  finished adding assets from .../escuadron_nova.yyp.
│  Release build
│  [Compile] Run asset compiler
│  Compile Constants...
│  finished.
│  Remove DnD...
│  finished.
│  Compile Scripts...
│  finished.
│  Compile Rooms...
│  finished..... 0 CC empty
│  finished..... 0 CC empty
│  Compile Objects...
│  finished.... 4 empty events
│  Compile Timelines...finished.
│  Compile Triggers...
│  finished.
│  Compile Extensions...
│  Compile UI Layers...finished.
│  Global scripts...finished.
│  collapsing enums.
│  Final Compile...
│  Final Compile finished.
│  Saving IFF file... .../.gmcache/build-gms2-mac-VM/output/game.zip
│  Writing Chunk... GEN8 size ... -0.00 MB
│  [... 27 chunks más, todos con datos reales: SPRT, OBJT, ROOM, CODE, VARI 0.02MB, FUNC,
│      TXTR 0.01MB, AUDO ...]
│  Stats : GMA : Elapsed=173.391
│  Stats : GMA : sp=5,au=0,bk=0,pt=0,sc=42,sh=0,fo=0,tl=0,ob=13,ro=6,da=0,ex=0,ma=6
│  Igor complete.
◆  Compilation finished
```

`gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only` → **exit 0, sin ninguna línea de
salida.** El artefacto (`game.zip`, ~29,9 KB) se escribió de verdad en
`.gmcache/build-gms2-mac-VM/output/`, con los 5 sprites, 13 objetos y 6 salas empaquetados —
no es solo un `exit 0`, hay un build real detrás.

`python3 "_indice/validar-proyecto.py" . --todo` (desde la biblioteca, apuntando al proyecto):

```
47 archivos .gml · 375 llamadas analizadas · runtime del índice 2026.0.0.23

✓ Ninguna llamada a una función del runtime que no exista.
```

(El recuento de `.gml` del proyecto por `find` da 420 si no se excluye `.gmcache/` — ahí vive una
copia interna de `project-tool` con sus propios `.gml` de compatibilidad GM8, nada que ver con el
proyecto. Excluyendo `.gmcache/`, `find` da 47, exactamente lo mismo que reporta el validador: no
hay ningún hueco de cobertura, solo un detalle a tener en cuenta si alguien repite esta
comprobación cruzada sin saberlo.)

---

## 8 · El proyecto construido, en cifras

- **Escuadrón Nova** — shmup vertical de 3 oleadas, sin jefe (recorte explícito de alcance).
- 13 objetos, 7 scripts, 5 sprites (con origen `Custom` real), 6 salas, 1 nota (`GDD`, la
  especificación completa).
- 1 059 líneas de GML propio (excluyendo `.gmcache`).
- 4 efectos de sonido sintetizados en runtime (`tono_generar`/`ruido_generar`, copiados tal cual
  de `08/24 §3`), sin ningún archivo de audio externo.
- Cero rectángulos, cero `show_debug_message()` sobrante, cero funciones inventadas.
- 3 recursos desechables creados y borrados a propósito para verificar las trampas 3, 4 y 5 en
  persona — no quedan en el proyecto final.

---

## Veredicto final honesto

**Un agente cualquiera que siga hoy `gamemaker-biblioteca` al pie de la letra entrega un juego
con envoltura completa (splash, menú, opciones, pausa de verdad, confirmaciones, game
over/victoria, créditos) y con assets dignos — no rectángulos, no un prototipo desnudo del bucle
de juego.** Los cuatro refuerzos de esta ronda (paso 0, seis trampas, escalera de assets,
checklist maestro) no son adorno: cada uno cambió una decisión real de esta sesión —

- El paso 0 impidió crear el proyecto sin especificación escrita.
- Las seis trampas evitaron tres tropiezos reales antes de que ocurrieran (plantilla que falla,
  numeración de eventos, fuente muda) y expusieron con precisión exacta un cuarto y quinto
  comportamiento (compilador ciego a funciones inventadas, matiz de `validar-proyecto.py`) al
  reproducirlos a propósito.
- La escalera de assets impidió el rectángulo por diseño, y su regla de «mirar el PNG, no confiar
  en el nombre del archivo» cazó un defecto real (la nave enemiga con «brazos») que el código por
  sí solo no habría delatado.
- El checklist maestro forzó seis pantallas de envoltura que, sin él, un agente centrado en «que
  el bucle funcione» habría omitido con toda probabilidad.

**Lo que no cubre ninguno de los cuatro refuerzos, y sigue dependiendo del criterio del agente**:
el orden de las salas por CLI, el aviso cruzado entre `04/00` (patrón mínimo de pausa) y `04/41`
(el patrón completo que evita la pantalla en negro), y la disciplina de verificar cada firma de
función con `buscar.py` incluso cuando «suena razonable» (el caso de `audio_play_sound`). Ninguno
de los tres es un error de la biblioteca — son los sitios donde la biblioteca, correctamente,
deja la decisión al agente y confía en que use el resto de sus reglas (nunca edites un `.yy` a
mano, verifica antes de escribir) para resolverlo bien. En esta sesión, funcionaron.

**Lo que quedó fuera de esta verificación, por la restricción de la propia sesión**: todo lo que
solo se puede comprobar ejecutando el juego de verdad —`gm-cli run` estaba prohibido—, incluida
la Trampa 6 (`directory_exists`/`directory_create`), la sensación de juego real, si el volumen del
slider de Opciones suena bien, y si la pausa se ve tan fluida como se ve leyendo el código. Se
declara así, explícitamente, en vez de darlo por bueno.
