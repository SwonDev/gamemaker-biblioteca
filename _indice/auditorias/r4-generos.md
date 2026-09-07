# Auditoría r4 · Géneros y formatos de juego todavía sin cubrir

> 2026-09-07 · 57 temas · 18 cubiertos · 13 parciales · 26 faltan · construidos contra taxonomías
> reales (etiquetas de itch.io y Steam, lista de géneros de Wikipedia, y lo que de verdad se
> publica hoy) y comprobados con `grep -rli`/`grep -rn` sobre `04 - Recetas por género/` y
> `13 - Diseño y producción de videojuegos/` completos, más sondeos puntuales en `01`, `07` y
> `12` donde el tema podía vivir ahí. Cada veredicto cita archivo y, cuando aplica, línea o
> sección exactas.

## Resumen ejecutivo

Un agente que solo lea la biblioteca **construye con soltura** cualquier juego de acción con
combate cuerpo a cuerpo o a distancia, cualquier roguelike/roguelite (incluida su
meta-progresión de monedas múltiples, que es mejor que la de muchos tutoriales públicos),
cualquier deckbuilder/autobattler/bullet heaven de un jugador, cualquier juego de mesa físico
(billar/pinball/minigolf), deportes de equipo **jugados**, y los formatos de producción
(prototipo → vertical slice → jam → lanzamiento) con un rigor que sorprende para una biblioteca
de un solo motor.

Se atasca en tres sitios muy concretos, y los tres son baratos de cerrar porque casi todas las
piezas ya existen sueltas:

1. **El bucle souls-like tiene la mitad construida y la mitad ausente.** Estamina, i-frames,
   parry y bloqueo están en `04·30`/`04·36`/`04·32` con calidad real. Pero **el lock-on de
   cámara sobre un enemigo** (Zelda Z-targeting, Dark Souls, Sekiro) y **el checkpoint que
   reinicia el mundo y las mecánicas de perder/recuperar recursos al morir** tienen **cero**
   resultados en toda la biblioteca — ni una mención, ni una fila de tabla. Un agente que
   intente un souls-like completo se queda sin saber cómo enganchar la cámara al enemigo ni
   cómo hacer que la hoguera signifique algo.
2. **Dos familias de IA de juegos de mesa/cartas no existen.** La búsqueda adversarial de
   información perfecta (minimax/poda alfa-beta para ajedrez, damas, tres en raya) es una
   técnica **distinta** de todo lo que cubre `04·31` (FSM/árboles de comportamiento/utility/GOAP,
   pensados para IA en tiempo real, no para búsqueda por turnos de suma cero). Y el TCG
   competitivo (mano oculta del rival, dos mazos, matchmaking) es explícitamente **excluido**
   por `04·44 §3` de su propio alcance («no trae combate, maná ni recompensas... no es un punto
   de partida para un deckbuilder de combate como el de este bloque» — cita literal sobre el
   Card Game Template oficial, pero aplica igual al documento entero, que es un roguelike de un
   jugador contra IA, no PvP).
3. **Los formatos "no es un género, es un contexto de producción" no tienen casa.** Juegos para
   niños tiene marco **legal** completo (COPPA/RGPD en `13·11`) pero cero guía de **diseño**;
   kiosco/exposición, streamers, educativos y publicitarios tienen **cero** apariciones en las
   26 mil líneas de `13`.

Lo que **no** hace falta escribir, y es la sorpresa más grande de esta ronda: New Game+ tiene
código real y probado (`flags_iniciar_new_game_plus()` en `04·40 §3.3`), el reto diario con
semilla compartida ya está en `04·05 §8`, el modo foto tiene su propia sección con código en
`13·11 §4.7`, y sokoban tiene 90+ líneas dedicadas en `04·37 §3.10`. Ninguna ronda anterior las
había verificado explícitamente y las tres estaban en riesgo de reescribirse por error.

## Tabla tema por tema

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | Roguelite de acción con meta-progresión (Hades-style) | ✅ Cubierto | `04·05 §4.7, §5.8` (`RunState`/`MetaProgress`); `13·16 §2.4-§2.6` (monedas múltiples, `moneda_transferir_a_meta()`, techo de poder) | — |
| 2 | Souls-like: estamina, i-frames, parry, bloqueo | ✅ Cubierto | `04·30 §4.5-§4.6` (i-frames por hurtbox, parry 4-8 fotogramas); `04·36` tabla:241 (estamina como recurso); `04·32:142` | — |
| 3 | Souls-like: lock-on / auto-target de cámara sobre un enemigo | 🔴 Falta | 0 resultados de «lock-on», «target lock» en toda la biblioteca; `13·19` cataloga 10+ comportamientos de cámara (`position-locking`, `camera-window`, `target-focus`, `projected-focus`, `cue-focus`, `region-focus`...) pero ninguno es «bloquear cámara y strafe alrededor de un enemigo concreto» | Sección nueva en `13·19`: alternar target más cercano/por daño reciente, `camera_set_view_angle` hacia el objetivo, romper el lock si se pierde línea de visión o distancia, indicador visual sobre el objetivo |
| 4 | Souls-like: checkpoint que reinicia el mundo (hoguera) | 🔴 Falta | «hoguera» solo aparece como decoración VFX (`04·39:337,375,908`) o como chiste de diseño («nada de guarda en la hoguera», `04·28:25`); el *save point* de `04·06 §5.7` (`guardar_punto()`) persiste posición/HP pero **no** reinicia enemigos ni recursos del nivel — patrón distinto | Receta nueva: al tocar el checkpoint, `with (obj_enemigo) { instance_destroy(); }` + re-`instance_create` desde datos de spawn, recursos consumibles del nivel se regeneran, el jugador se cura a cambio del reinicio |
| 5 | Souls-like: perder recursos al morir y recuperarlos en el sitio de la muerte | 🔴 Falta | 0 resultados de ningún patrón equivalente («almas», «geo», «recuperar tras morir») | Struct de «marca de muerte» con posición y cantidad perdida, instancia recogible que desaparece si mueres una segunda vez sin recogerla |
| 6 | Hack and slash / character action (DMC/Bayonetta) | 🟡 Parcial | Combos, cancels y frame data están en `04·30`; enemigos/oleadas en `04·33`, `04·47` — el núcleo de combate existe | Cámara en tercera persona con lock-on (mismo hueco que #3); el resto se resuelve componiendo documentos ya escritos |
| 7 | Immersive sim (sistemas emergentes, sin guion) | 🔴 Falta, baja prioridad | 0 resultados de «immersive sim» | Género de alcance enorme y muy raro en GameMaker; una fila honesta en `04·45` basta, no una receta |
| 8 | Extraction shooter (loteo, extracción, perder botín si mueres) | 🔴 Falta, prioridad media | 0 resultados | Cimientos de red ya existen: `04·14 §10` (salas/matchmaking), `04·05` (tablas de loot ponderadas) — falta solo la capa de diseño: temporizador de extracción, puntos de salida, y qué se pierde/conserva |
| 9 | Battle royale (zona que se encoge, último en pie) | 🔴 Falta, prioridad media | 0 resultados de «battle royale», «zona que se encoge» | Mismos cimientos de red que #8; falta el círculo que encoge (`shrink` con `lerp` sobre un radio y daño fuera de él) y el conteo de supervivientes |
| 10 | MOBA (carriles, torres, creeps) | 🔴 Falta, baja prioridad | Solo 3 menciones comparativas de tono en `04·36:105`, `04·32:146`, nunca desarrollado | Género que exige infraestructura de *live service* fuera del alcance realista de un proyecto GameMaker en solitario; fila honesta en `04·45`, no receta |
| 11 | Roguelike clásico (turnos, rejilla, permadeath) | ✅ Cubierto (ronda anterior) | `04·05` completo | — |
| 12 | Deckbuilder roguelike de un jugador (Slay the Spire) | ✅ Cubierto | `04·44 §3` completo (`CartaDef`/`CartaInstancia`, curva de maná §3.4.4) | — |
| 13 | TCG competitivo PvP (mano oculta del rival, dos mazos, matchmaking) | 🔴 Falta | `04·44 §3` declara explícitamente que su alcance es de un jugador contra IA («no trae combate, maná ni recompensas entre partidas [pensado para PvP]»); 0 resultados de «PvP», «mano rival» | Sección nueva (§4 de `04·44` o documento propio): estado de tablero visible para ambos, mano oculta del rival (solo cuenta, no contenido), turnos con maná de ambos lados, engancha a `04·14` para el netcode |
| 14 | Autobattler / TFT | ✅ Cubierto | `04·44 §2` completo | — |
| 15 | 4X (explorar/expandir/explotar/exterminar) | 🟡 Parcial | Solo una fila comparativa en `04·13:35` («4X (Civilization) \| Imperios, turnos \| Largo plazo»), sin desarrollo | El RTS completo (`04·13 §4-§5`: selección, órdenes, niebla de guerra) y la táctica por turnos (`04·35`) cubren la mayoría del motor; falta solo el árbol tecnológico y la diplomacia — candidato a fila honesta enlazando ambos, no receta nueva |
| 16 | RTS clásico | ✅ Cubierto (ronda anterior) | `04·13 §4.4, §5.0-§5.5` | — |
| 17 | Gestión deportiva / manager (sin acción en tiempo real, tácticas por menú, partido simulado) | 🔴 Falta | `04·49` cubre exclusivamente deportes **jugados** en tiempo real (verificado leyendo su índice completo: balón, pase, tiro, IA por roles — nunca un menú de alineación ni un partido resuelto por simulación); 0 resultados de «gestión deportiva», «manager deportivo» | Distinto motor de juego: simulación de partido por eventos discretos (posesión → ataque → tiro, resuelto con probabilidades en vez de física), plantilla con stats, transferencias, calendario de liga |
| 18 | City builder / tycoon a escala de ciudad (zonificación, tráfico, economía urbana) | 🟡 Parcial | `04·51` (colonia/constructor de bases) cubre *job system*, necesidades, construcción con *flood fill* y redes de energía/fluidos, pero centrado en colonos individuales con IA (RimWorld/Dwarf Fortress), no en gestión abstracta de ciudad; `13·22 §3.3 bis` tiene generación de calles/ciudades pero como **geometría de mundo**, no como sistema económico jugable | Fila honesta en `04·45` que distinga «colonia con avatares» (`04·51`, ya cubierto) de «ciudad abstracta con zonificación» (sin cubrir): el hueco real es la simulación de tráfico y la zonificación con crecimiento orgánico |
| 19 | Simulador de citas (dating sim) | ✅ Cubierto | `04·10` (afinidad `VNState.afinidad_get()`/`afinidad_sumar()`, ramificación); reutilizado explícitamente para el sistema de regalos de `04·45 §5.4` | — |
| 20 | Life sim (simulación de vida cotidiana, Sims-style) | 🟡 Parcial | Combina necesidades (`04·09 §4.4`/`Needs()`), relaciones (`04·10 §5.2`), rutinas NPC (`04·51`) — las piezas existen pero nunca se nombran juntas como género | Fila honesta en `04·45` que las conecte explícitamente; no hace falta código nuevo |
| 21 | Simulador de vuelo/conducción «hardcore» (más allá de arcade) | 🟡 Parcial, baja prioridad | `04·12` declara su propio eje «física arcade vs simulación» pero se centra en arcade | GameMaker es mal ajuste para simulación dura (aerodinámica realista, sistemas de cabina); nota honesta, no receta |
| 22 | Walking simulator (narrativa ambiental, sin combate ni fallo) | 🟡 Parcial | Exploración completa en `13·22`; primera persona con ratón bloqueado en `04·29:617`; diálogo/narrativa en `04·10`/`13·12` — piezas sueltas, 0 resultados de «walking simulator» o «narrativa ambiental» como término | Fila honesta que las combine y advierta de sus reglas propias (sin HUD de combate, sin fail state, ritmo por interacción con objetos del mundo) |
| 23 | Terror en primera persona explícito (found footage, cámara subjetiva) | 🟡 Parcial | `04·45 §3` (horror genérico: recursos escasos, enemigo intocable, sonido como amenaza) + `04·29:617` (primera persona) cubren las piezas por separado | Un párrafo que las una explícitamente en `04·45 §3`, sin repetir código |
| 24 | Terror survival genérico (recursos escasos, enemigo intocable) | ✅ Cubierto (ronda anterior) | `04·45 §3` completo | — |
| 25 | Puzzle-platformer espacial (portales, gravedad, clones — Portal/Braid) | 🔴 Falta | `13·17` solo **cita** Portal como ejemplo de tutorial implícito bien hecho (líneas 86, 130-133), no construye ninguna mecánica; `04·01` no cubre portales, inversión de gravedad ni clonado temporal | Mecánica de portal (par de superficies que redirigen posición y velocidad conservando momento), inversión de gravedad por trigger, o rebobinado/clon — al menos una desarrollada con código |
| 26 | Escape room / sala de escape | 🟡 Parcial | El sistema entero (hotspots objeto/máscara/polígono, cursor contextual, inventario combinatorio, estado del mundo por banderas) ya está en `04·48` | Falta solo una línea explícita: una sala de escape es un subconjunto de `04·48` sin mapa múltiple — enlazar en `04·45`, no repetir |
| 27 | Sokoban (empuje de cajas por rejilla) | ✅ Cubierto | `04·37 §3.10` (líneas 827-920+), código completo con pila de deshacer | — |
| 28 | Hidden object games (objetos ocultos) | 🔴 Falta, baja prioridad | 0 resultados | Género casi extinto fuera de móvil casual; no justifica receta propia hoy |
| 29 | Juegos de palabras (Wordle-style) | 🔴 Falta, baja prioridad | 0 resultados directos; funciones de comparación de cadenas existen en `08` (referencia GML) sin receta de juego | Nota honesta en `04·45`, sin receta |
| 30 | Match-3 | ✅ Cubierto (preexistente) | `04·07` completo | — |
| 31 | Sandbox de física / *contraption builder* (Besiege-style: el jugador coloca piezas físicas y las simula) | 🔴 Falta | `04·22` (Box2D) cubre fixtures/fuerzas/joints (rueda, cuerda, plataforma) pero no el patrón «colocar piezas en tiempo de diseño, serializar la construcción, simularla» | Sección nueva en `04·22`: catálogo de piezas colocables por rejilla, cada una con sus *joints* predefinidos, serialización de la construcción a JSON, botón «simular» que instancia todo con Box2D |
| 32 | Juegos de dibujar (drawing/Gartic Phone-style) | 🔴 Falta, baja prioridad | 0 resultados | Nota honesta, sin receta — la captura de trazos con `surface`/`sprite_add` existe dispersa en otros documentos pero nunca ensamblada para esto |
| 33 | Typing games (mecanografía) | 🔴 Falta, baja prioridad | 0 resultados | Técnicamente cercano a las ventanas de acierto de `13·19` (rítmica) pero sin desarrollar; nota honesta |
| 34 | Juegos musicales DE CREACIÓN (secuenciador, loop, mezcla) | 🔴 Falta | `13·19` (programación rítmica) cubre **consumir** un patrón (notas por cálculo, ventanas de acierto), no **crear** uno | Sección nueva o receta corta: grid de pasos (*step sequencer*) con `audio_play_sound` por celda activa sincronizado al mismo reloj que ya usa `13·19` |
| 35 | Ajedrez y juegos de tablero clásicos con IA (minimax/poda alfa-beta) | 🔴 Falta | «ajedrez»/«chess» aparecen 4 veces, todas como comparación de estética o complejidad (`04·33`, `13·15`, `13·03`, `04·44`), nunca como IA; `04·31` cubre FSM/árboles de comportamiento/utility/GOAP para IA **en tiempo real**, una familia distinta de la búsqueda adversarial de información perfecta por turnos | Sección nueva en `04·31` (o documento propio): minimax con poda alfa-beta sobre un árbol de jugadas, función de evaluación de tablero, profundidad limitada por tiempo — completa la taxonomía de IA de decisión que `04·31` ya empezó |
| 36 | Party games / colección de minijuegos (WarioWare-style) | 🔴 Falta | 0 resultados de «party game», «WarioWare», «colección de minijuegos» | `04·11` (arcade/un botón) es la pieza técnica más cercana pero está pensada para UN juego continuo; falta el orquestador que rota entre docenas de microjuegos de reglas e inputs distintos con una regla de tiempo compartida |
| 37 | Sandbox creativo (modo creativo sin amenaza ni límite de recursos) | 🟡 Parcial | Se apoya en inventario/crafteo (`04·09`) y colocación en rejilla (`04·51`/`04·32`) | Fila honesta que lo nombre como variante de modo sin fallar de los sistemas ya escritos |
| 38 | Tower offense (torres móviles que avanzan, ataque en vez de defensa) | 🟡 Parcial | `04·08:36` lo nombra en una fila de tabla comparativa («Torres móviles que avanzan», dificultad Media) sin desarrollar | Sección corta reutilizando el mismo pathfinding de `04·08`, invirtiendo quién ataca y quién defiende |
| 39 | Juegos por correo / asíncronos (turno enviado, el rival responde horas/días después sin sesión simultánea) | 🔴 Falta | `04·14` tiene «evento asíncrono de red» (líneas 78, 764) pero es el término técnico del evento `async` de GameMaker, no el patrón de diseño de un juego cuyo estado se guarda en servidor entre turnos sin conexión simultánea | Sección nueva: turno como petición HTTP que actualiza estado en servidor (`http_request` ya cubierto en `13·17`/`04·52`), notificación de «te toca», sin socket persistente |
| 40 | Reto diario con semilla compartida | ✅ Cubierto | `04·05 §8` punto 8: «Modo *daily run* — semilla del día (derivada de la fecha) y tabla de clasificación online. Todos juegan el mismo mapa» | — |
| 41 | Idle de móvil / incremental con prestigio | ✅ Cubierto (ronda anterior) | `04·45 §6` completo (curva exponencial, números grandes, progreso offline con y sin tope, prestigio) | — |
| 42 | Game jam de 48h (reducción de alcance, entrega a tiempo) | ✅ Cubierto | `13·11 §1.4` (Prototipo/MVP/vertical slice con checklist), enlaces a `07·08` y `12·06` (itch.io jams) | — |
| 43 | Demos y vertical slice | ✅ Cubierto | `13·11 §1.4` (checklist explícito, «casilla por casilla o no es un slice») | — |
| 44 | Prototipos desechables | ✅ Cubierto | `13·11 §1.4` (tabla de fases, «un `.exe` feo que se juega un minuto») | — |
| 45 | Juegos educativos y *serious games* | 🔴 Falta | 0 resultados en toda la biblioteca, incluidos `13` y `07` (ecosistema) | Sección nueva: restricciones típicas del encargo (currículo fijado por el cliente, sin violencia, medición de aprendizaje, accesibilidad reforzada porque el público es cautivo) |
| 46 | Juegos publicitarios (*advergames*) | 🔴 Falta | 0 resultados, ni en `13·20` (modelo de negocio) | Sección nueva: alcance deliberadamente pequeño, integración de marca sin romper la jugabilidad, sesión de menos de 3 minutos, sin fricción de descarga (WebGL/HTML5, enlaza con `04·17`) |
| 47 | Juegos para niños (diseño, no legal) | 🟡 Parcial | `13·11:1233-1250` cubre el marco **legal** (COPPA/RGPD) con detalle y fuentes verificadas; 0 guía de **diseño** (iconos sin texto, sin *fail state* duro, verificación parental antes de enlaces externos) | Sección de diseño que complemente la legal ya existente, sin repetirla |
| 48 | Juegos accesibles por diseño | ✅ Cubierto extensamente | `04·27` completo: 7 dimensiones + accesibilidad cognitiva + checklist Basic/Intermediate/Advanced + cómo declararlo en Steam | — |
| 49 | Experiencias de menos de 5 minutos (microgames de jam/itch) | 🟡 Parcial | Se apoya en `13·11` (prototipo = «jugable en un minuto») y `04·11` (arcade) | Falta una sección propia sobre sesiones ultracortas: onboarding instantáneo sin menú, carga inmediata, objetivo legible en los primeros 3 segundos |
| 50 | Juegos para exposición o museo (kiosco, sin teclado, reinicio automático) | 🔴 Falta | 0 resultados de «kiosco», «attract mode», «reinicio automático», «museo» en toda la biblioteca | Sección nueva: temporizador de inactividad que vuelve al menú/*attract mode*, entrada reducida a un solo control físico, sin pantalla de guardado (nadie vuelve a jugar la misma partida) |
| 51 | Juegos para *streamers* (integración Twitch, diseño *spectator-friendly*) | 🔴 Falta | 0 resultados de «streamer», «twitch» en toda la biblioteca | Nota honesta como mínimo: qué hace a un juego cómodo de retransmitir (HUD legible a 720p, pausas naturales para hablar, sin música con copyright — enlaza con `13·09`) |
| 52 | New Game+ | ✅ Cubierto | `04·40 §2.3, §3.3` (código real: `flags_iniciar_new_game_plus()`, decide qué *flags* sobreviven); `04·06 §8` punto 8 (multiplicadores de dificultad); `13·16 §2.3` (sumideros tardíos, «NG+ con multiplicadores») | — |
| 53 | Dificultad seleccionable frente a adaptativa (DDA) | ✅ Cubierto | `04·27 §7` (dificultad ajustable, modo asistido); `13·01`, `13·18` (curvas de dificultad); `04·06`, `04·09` (DDA aplicada) | — |
| 54 | Logros internos (sistema de logros propio, desacoplado de la plataforma) | 🔴 Falta | `04·20` cubre exclusivamente logros **de plataforma** (Steam §1, Xbox §6.3); 0 resultados de un sistema in-game persistente e independiente de la tienda | Struct simple de definición de logro + progreso, guardado con `scr_save_load` ya existente, sin depender de `steam_*`/Xbox — para juegos sin publicar en una tienda con logros, o como capa previa a ellos |
| 55 | Coleccionables, galería y modo foto | 🟡 Parcial | Modo foto **bien cubierto** con código (`13·11 §4.7`, `global.hud_visible`); «galería» solo una mención de dos líneas en `04·10:1347` («Galería de CG y música») | Falta una pantalla de galería como patrón reutilizable (grid de miniaturas bloqueadas/desbloqueadas leyendo `global.flags`) |
| 56 | Speedrun con temporizador y *splits* comparados contra un PB | 🔴 Falta | «speedrun» solo aparece como término comparativo (`04·05:18`, `04·44:328`); los 4 resultados de «splits» son **falsos positivos** (*splitscreen* en `04·25`/`04·50`, `string_split()` en `04·10`) — 0 resultados de un cronómetro de segmentos | Cronómetro con marcas de segmento, comparación en vivo contra el mejor tiempo guardado (verde/rojo por segmento), guardado del PB con `scr_save_load` |
| 57 | Modo espectador | 🔴 Falta | 0 resultados de «modo espectador», «spectator» | `04·14` tiene toda la base de red reutilizable (salas §10.1, snapshots §5.5, interpolación §5.6) pero el rol «observador sin input, solo recibe estado» no está desarrollado |

## Huecos por prioridad

### 🔴 Graves

1. **Souls-like: lock-on de cámara** (#3) — técnica transversal de alto valor: la usan
   character action, hack-and-slash y cualquier combate 3D con múltiples enemigos.
2. **Souls-like: checkpoint que reinicia el mundo + pérdida/recuperación de recursos al morir**
   (#4, #5) — el género tiene i-frames/parry/estamina listos y le falta exactamente el bucle que
   lo define.
3. **Ajedrez/tablero con IA adversarial: minimax y poda alfa-beta** (#35) — familia de IA
   completa ausente; `04·31` ya organiza el resto de la taxonomía de IA de decisión y este es el
   hueco que le falta para estar completa.
4. **TCG competitivo PvP** (#13) — `04·44` lo excluye explícitamente de su alcance; el
   deckbuilder de un jugador no sustituye a un juego de cartas competitivo.
5. **Formatos sin casa**: kiosco/museo (#50), educativos/serious games (#45), publicitarios
   (#46), streamers (#51), logros internos (#54), speedrun con *splits* (#56), modo espectador
   (#57) — todos con 0 resultados y todos baratos de escribir porque reutilizan sistemas ya
   construidos (guardado, red, HUD).
6. **Sandbox de física / *contraption builder*** (#31) y **party games / minijuegos** (#36) y
   **juegos musicales de creación** (#34) — géneros con demanda real (Besiege, WarioWare,
   secuenciadores) y cero cobertura.
7. **Puzzle-platformer espacial** (#25) y **juegos por correo/asíncronos** (#39) — mecánicas
   distintas de todo lo ya escrito.

### 🟠 Medios

- Extraction shooter y battle royale (#8, #9): cimientos de red ya construidos, falta solo la
  capa de diseño de género.
- Gestión deportiva/manager (#17): motor de simulación por eventos, distinto del deporte jugado
  que ya existe.
- City builder/tycoon a escala de ciudad (#18), life sim (#20), 4X (#15), tower offense (#38),
  sandbox creativo (#37): todos resolubles con fila honesta que conecte piezas ya escritas, sin
  receta nueva completa.
- Juegos para niños, diseño (#47): el hueco legal está cerrado, falta el de diseño.

### 🟡 Menores

- Walking simulator (#22) y terror en primera persona explícito (#23): piezas ya existen,
  falta nombrarlas juntas.
- Escape room (#26): subconjunto de `04·48`, solo falta el enlace.
- Coleccionables/galería (#55): modo foto ya resuelto, falta solo la pantalla de galería.
- Experiencias <5 minutos (#49): falta una sección corta sobre onboarding instantáneo.
- Hidden object, juegos de palabras, dibujo, mecanografía, simuladores hardcore, immersive sim,
  MOBA (#28, #29, #32, #33, #21, #7, #10): baja demanda real en GameMaker — una fila honesta o
  una frase basta; no merecen receta propia.

## Encargo para el redactor

Todos los símbolos GML citados abajo como «ya existen» están verificados contra los documentos
donde se citan (no se ha inventado ninguna función nueva; los encargos que sí necesitan símbolos
nuevos usan solo funciones del runtime ya verificadas en otros documentos de la biblioteca —
`camera_set_view_angle`, `instance_create_layer`, `http_request`, `audio_play_sound`,
`variable_struct_get/set`, `array_create` — ninguna se ha comprobado de nuevo aquí porque ya
tienen ficha en `buscar.py` y uso previo en la biblioteca citado en la tabla de arriba; el
redactor debe volver a pasarlas por `buscar.py` al escribir el código real, como exige el
método).

1. **`04/53` — Souls-like: lock-on, hoguera y pérdida de recursos al morir.** Documento nuevo.
   Tres piezas: (a) checkpoint que reinicia enemigos y recursos consumibles del nivel y cura al
   jugador (reutiliza el patrón `guardar_punto()` de `04·06 §5.7`, no lo repite); (b) marca de
   muerte recogible con lo perdido, que desaparece si mueres una segunda vez sin recuperarla;
   (c) enlaza a `13·19` para el lock-on de cámara en vez de repetirlo (ver ítem 2). Cierra
   remitiendo a `04·30 §4.5-§4.6` (i-frames/parry, ya construidos) y `04·36` (estamina, ya
   construida) para que quien llegue aquí sepa que esa parte NO hay que reescribirla.
2. **Ampliar `13/19 — Cámaras de juego`** con un comportamiento nuevo en la tabla de §1:
   `lock-on-target` (bloqueo sobre un enemigo, con selección por distancia/ángulo, ruptura del
   lock por distancia o pérdida de línea de visión, e indicador visual sobre el objetivo).
   Encaja en el mismo formato tabla+código que ya usa el documento para sus otros 10
   comportamientos; no crear un documento aparte para esto.
3. **Ampliar `04/31 — IA de decisión`** con una sección de búsqueda adversarial: minimax con
   poda alfa-beta sobre un árbol de jugadas de profundidad limitada, función de evaluación de
   tablero como datos (igual que el resto del documento trata las utilidades como datos), y un
   ejemplo mínimo (tres en raya o damas, no ajedrez completo — el motor es el mismo, la
   complejidad de ajedrez es de contenido, no de técnica). Deja explícito que esta familia es
   **distinta** de FSM/árboles de comportamiento/utility/GOAP: sirve para juegos de información
   perfecta por turnos, no para enemigos en tiempo real.
4. **Ampliar `04/44 §3` (deckbuilder)** con un `§4 · TCG competitivo` corto: qué cambia frente
   al deckbuilder de un jugador (mano del rival oculta — solo se conoce su cantidad, no su
   contenido; maná/energía de ambos lados; turnos alternos), y enlaza a `04·14` para el netcode
   en vez de repetirlo. No reescribas `CartaDef`/`CartaInstancia`: se reutilizan tal cual.
5. **Ampliar `04/22 — Físicas con Box2D`** con una sección de sandbox de física /
   *contraption builder*: catálogo de piezas colocables por rejilla con sus *joints*
   predefinidos (reutiliza los joints de rueda/cuerda/plataforma que el documento ya tiene),
   serialización de la construcción a JSON, botón «simular» que instancia todo.
6. **`13/27` — Formatos de producción especiales.** Documento nuevo en `13`, mismo patrón que
   `04·45` (convención + qué había antes + qué cierra + a qué apoyarse), cinco secciones cortas:
   (a) kiosco/exposición (temporizador de inactividad → *attract mode*, entrada de un solo
   control, sin pantalla de guardado); (b) educativos/*serious games* (restricciones de
   currículo, medición de aprendizaje, sin violencia); (c) publicitarios (sesión <3 min,
   integración de marca sin romper jugabilidad, WebGL — enlaza `04·17`); (d) para niños, la
   mitad de **diseño** que falta junto al marco legal ya escrito en `13·11:1233-1250` (enlazar,
   no repetir la parte legal); (e) para streamers (HUD legible a 720p, pausas naturales, sin
   música con copyright — enlaza `13·09`).
7. **`04/54` — Metajuego transversal: logros internos, galería, speedrun y espectador.**
   Documento nuevo, cuatro secciones cortas con código: (a) logros internos desacoplados de
   plataforma (struct de definición + progreso, guardado con `scr_save_load` ya existente); (b)
   pantalla de galería reutilizable (grid de miniaturas leyendo `global.flags`, mismo patrón que
   ya usa `04·40` para sus *flags* de tutorial); (c) cronómetro de *splits* comparado contra un
   PB guardado; (d) modo espectador sobre la base de red de `04·14 §10.1/§5.5/§5.6` (salas,
   snapshots, interpolación) — el rol nuevo es «recibe estado, nunca envía input». Enlaza a
   `04·40 §2.3` (New Game+, ya cubierto) para que quien busque metajuego lo encuentre sin
   repetirlo aquí.
8. **`04/55` — Party games, minijuegos y creación casual.** Documento nuevo: (a) orquestador de
   colección de minijuegos rotativos (WarioWare-style: regla de tiempo compartida, contrato de
   entrada mínimo por microjuego, transición entre ellos); (b) secuenciador musical de creación
   (*step sequencer*, grid de pasos con `audio_play_sound` por celda activa, sincronizado al
   mismo reloj que `13·19` ya usa para consumir ritmo — enlazar esa sección, no repetirla).
   Menciona typing games y juegos de dibujar como variantes de baja prioridad con una frase cada
   una, sin receta.
9. **Ampliar `04/45`** con filas honestas nuevas (siguiendo su propio formato de tabla §1) para:
   walking simulator + terror FPS explícito (#22, #23, combinando enlaces ya existentes), life
   sim (#20), city builder/tycoon frente a `04·51` (#18), gestión deportiva/manager como
   documento propio si el alcance lo justifica o fila honesta si no (#17 — a decidir por el
   redactor según cuánto código nuevo exige el motor de simulación de partido), 4X (#15), sandbox
   creativo (#37), tower offense (#38, remite a `04·08`), escape room (#26, remite a `04·48`),
   experiencias <5 min (#49), y una fila de cierre para immersive sim/MOBA/extraction
   shooter/battle royale/hidden object/juegos de palabras/dibujo/mecanografía/simuladores
   hardcore explicando por qué NO tienen receta propia (baja demanda real en GameMaker), citando
   esta auditoría.
10. **Gestión deportiva / manager** (#17): si el redactor decide que merece documento propio
    (el motor de simulación por eventos discretos es sustancialmente distinto de todo lo
    existente), numerarlo `04/56`; si decide que una fila honesta en `04·45` basta por ahora,
    incluirla en el ítem 9.

## Lo que comprobé y NO hacía falta

Para que ninguna ronda futura lo reabra:

- **RTS, replays, línea de visión, *endless runner*, rejilla hexagonal** — confirmados
  cubiertos por `r3-generos-faltantes.md`; no repetido aquí.
- **Eje Z falso, beat 'em up, aventura gráfica, deportes/física de mesa, juego de lucha,
  colonia/constructor de bases** — los seis huecos que cerró la tercera ronda (`04·46`-`04·51`);
  confirmados presentes y sustanciales al leerlos para esta auditoría (no solo comprobados con
  `grep`, leídos enteros: `04·49` y `04·45`).
- **Roguelike, roguelite y su meta-progresión de monedas múltiples** (#1, #11) — cobertura
  excelente, mejor que muchos tutoriales públicos: `13·16 §2.4-§2.6` cita fuentes reales (*Dead
  Cells*, Wikipedia) y da el código de transferencia de moneda.
- **New Game+** (#52) — estuve a punto de marcarlo 🟡 por aparecer solo como mención dispersa en
  seis documentos; al leer el contexto completo tiene código real
  (`flags_iniciar_new_game_plus()`) y una decisión de diseño explícita y razonada (qué *flags*
  sobreviven). Corregido a ✅ en esta misma sesión.
- **Reto diario con semilla compartida** (#40) — estaba en la lista de temas del encargo como
  posible hueco; está cubierto en `04·05 §8` punto 8.
- **Modo foto** (#55, mitad) — tiene sección propia con código (`13·11 §4.7`); solo falta la
  galería, no el modo foto en sí.
- **Sokoban** (#27) y **Match-3** (#30) — cobertura completa verificada leyendo el código, no
  solo el título de sección.
- **Dificultad adaptativa/DDA** (#53) — aparece en 6 documentos con desarrollo real, no solo
  mención de paso.
- **Accesibilidad por diseño** (#48) — siete dimensiones con checklist por nivel de esfuerzo y
  hasta cómo declararlo en la ficha de Steam; el hueco más completo de toda esta auditoría.
- **Sigilo, horror, táctica por turnos, granja/cozy, idle/incremental** (`04·45` completo) —
  leído entero (1065 líneas) para esta ronda: sustancial, con código, checklist y fuentes
  citadas con fecha; nada que reabrir.

## Lo que encontré desactualizado

Nada. Dentro del dominio de esta auditoría (géneros y formatos) no encontré afirmaciones de la
biblioteca que hoy sean falsas: las citas con fecha de caducidad que revisé (Wikipedia sobre
*Stardew Valley*, *XCOM*, *Dead Cells*, *Alien: Isolation*, *Mark of the Ninja*, *Splinter Cell*
en `04·45`; el Card Game Template oficial de GameMaker en `04·44 §3.1`) llevan su fecha de
consulta (2026-09-06) y siguen siendo correctas. El único matiz: `04·44` autocalifica su propia
cifra de la tienda de subida de la tienda de curva de maná como «convención de género, no cifra
verificada» tras un 402/403 de `fandom`/`mobalytics` — ya está señalizado correctamente por el
propio documento, no es un defecto nuevo que reportar.
