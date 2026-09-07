# Auditoría r4 · VFX, Audio/SFX y Feedback al jugador (segunda pasada)

> Fecha 2026-09-07 · 58 temas · 39 cubiertos · 13 parciales · 6 faltan
> Referencia: GameMaker LTS 2026.0 (IDE `2026.0.0.16`, runtime `2026.0.0.23`). Excluidos
> `Lumbre/` y `GameMaker_Fuentes/`. Método: `python3 _indice/buscar.py --todo/--listar`, `grep`
> dirigido y lectura línea a línea de los documentos que cerraron los huecos de la ronda 2
> (`04/39`, `04/40`, `04/41`, `04/42`, `08/23`, `08/24`, ampliaciones de `04/15`, `04/27`,
> `04/32`, `13/09`, `13/24`, `13/05`) antes de dar nada por hecho.

## Resumen ejecutivo

**La ronda 2 hizo un trabajo real y verificable.** Los siete documentos/ampliaciones que cerraron
sus huecos (`04/39` VFX 1027 líneas, `08/23` shaders 1391 líneas, `04/42` audio reactivo 668
líneas, `08/24` audio avanzado 758 líneas, más las ampliaciones de `04/15`, `04/27` y `13/09`)
existen, tienen el contenido que prometían y — donde lo comprobé leyendo el código, no solo el
título de la sección — usan símbolos reales. El `hit_flash` huérfano que la ronda 2 marcó como el
arreglo de mayor relación valor/esfuerzo **está dibujado** (`04/15 §5.6 bis`). La voz, la
localización de audio y el lip-sync, que no existían, **tienen documento propio** (`13/24`, 914
líneas). Un agente que siga estas recetas produce un juego con partículas, shaders, mezcla y
game feel de nivel profesional. **No reabro nada de esto.**

Dos rondas after, sin embargo, el brief de esta pasada apunta a una capa que ninguna auditoría
anterior miró: **la conexión entre piezas que ya existen por separado**, y **la pregunta
explícita del usuario** («¿está el sistema de partículas 2026 de verdad conectado con las
recetas?», «¿puede GameMaker sintetizar sonido?», «¿qué hace un agente que necesita un sonido y no
tiene?»). Ahí aparecen seis huecos reales:

1. **VFX compuestos que exigen varias piezas a la vez — congelación, quemado, electricidad,
   portal, humo con volumen falso — no existen**, ni siquiera como combinación de piezas que sí
   están (fuego continuo, tinte de estado, shader de disolución). El caso más caro es
   **electricidad/rayo**, que no tiene ni un ejemplo de línea quebrada por desplazamiento de
   punto medio, la técnica estándar del género.
2. **No hay presupuesto de VFX a nivel de juego.** `04 · 39 §3.12` mide partículas de UN sistema
   y hace *culling* por cámara; no existe el equivalente del sistema de importancia de audio
   (`04 · 42 §3.4`, que sí puntúa y arbitra) para decidir qué VFX se recortan cuando 40 enemigos
   quieren explotar a la vez. Tampoco hay un ajuste de calidad gráfica en el menú de opciones:
   `global.calidad_baja` existe como variable suelta en `04 · 28 §6` y no se conecta a nada.
3. **Afinar un shader o una partícula en tiempo de ejecución, sin recompilar, es posible
   (`dbg_slider`, `01 · 15 §4`) y ningún documento de VFX lo usa.** `04 · 39` y `08 · 23` no
   mencionan `dbg_*` ni una vez: el mecanismo para «trastear el juego en marcha sin recompilar»
   existe en la biblioteca desde `01 · 15` y nunca se aplicó a un parámetro visual.
4. **Un agente que necesita un efecto de sonido y no tiene ninguno no tiene dónde mirar.** La
   respuesta correcta ya está escrita, pero repartida y no señalada como respuesta a esta
   pregunta: síntesis por código en `08 · 24 §3` (verificado: SÍ se puede sintetizar audio en
   runtime en GameMaker, sin herramienta externa) y el patrón de *placeholder* declarado en
   `PLACEHOLDERS.md` (`13 · 11`), que hoy solo cubre arte, no audio.
5. **La cadena completa de un golpe está resuelta por piezas, con tiempos en fotogramas cada
   una — pero nunca se ensamblan en un único diagrama temporal**, y la «reacción del enemigo» que
   pide el brief no existe como estado distinto del empuje físico. Tampoco existe el indicador de
   zona de peligro en el suelo (telegraph de área), pese a que el telegraph por color de sprite sí
   está resuelto con fotogramas exactos.
6. **La legibilidad en pantalla llena («200 enemigos, ¿qué me está matando?») no se trata en
   ningún sitio.** `04 · 44` (bullet heaven) resuelve el coste de rendimiento de cientos de
   enemigos con siete técnicas distintas y no dice una palabra sobre cómo se **lee** esa pantalla.

Ningún hueco de esta lista es invención: los seis están verificados con `grep`/`buscar.py` contra
el disco completo, incluidos los documentos que la ronda 2 escribió para cerrar exactamente este
dominio. **La prueba de agente** (¿puede ejecutarlo leyendo solo la biblioteca, o solo hablar de
ello?) los reprueba a todos: un agente al que le pidan «que el jefe congele al jugador» no tiene
ninguna receta que combinar; uno al que se le acabe la memoria de partículas no tiene un criterio
de recorte; uno que necesite un disparo y no tenga el .wav no sabe que puede sintetizarlo.

---

## 1 · Tabla tema por tema

Leyenda: ✅ CUBIERTO (con cita verificada) · 🟡 PARCIAL (existe, incompleto) · 🔴 FALTA.

### A · VFX — sistema de partículas 2026, presupuesto y edición en vivo

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| A1 | ¿El Particle System de 2026 está de verdad conectado con las recetas, o siguen en API antigua? | ✅ | `04 · 39 §2.2 «Editor de partículas frente a part_type_* por código»` — decisión explícita y razonada: editor para iterar visualmente y para efectos ambientales fijos; código (`part_type_*`) solo donde el editor no llega (partículas que engendran partículas, parámetros dependientes de datos de juego). Enlaza a `02 · 05 §7` | — (decisión de arquitectura correcta y explicada, no un olvido) |
| A2 | Partículas del editor colocadas en la room y controladas por código (`layer_particle_*`) | ✅ | `02 · 05 §7 bis` (17 funciones, ejemplo con `layer_particle_get_id/blend/angle/alpha`) | — |
| A3 | Hueco de API `part_type_*`/`part_system_*` que la ronda 2 detectó (13/34 y 7/19) | ✅ cerrado | `04 · 39 §3.0 «Cerrando el hueco de API»` (tabla de 11 funciones con dónde se usa cada una) | — |
| A4 | Explosión en capas (destello→núcleo→escombros→humo→onda) | ✅ | `04 · 39 §3.1-3.2` (`fx_explosion_completa`, con `part_type_death` encadenando humo desde el núcleo) | — |
| A5 | Fuego continuo, magia/carga, lluvia con salpicadura, nieve, niebla | ✅ | `04 · 39 §3.3-3.7` | — |
| A6 | **Congelación como efecto visual compuesto** (escarcha, tinte azulado, cristales creciendo) | 🟡 | `04 · 32 §4.5-4.6` resuelve el **mecanismo** (DoT/ralentización) y el **tinte plano** (`color: c_aqua`, icono) reutilizando el patrón de `hit_flash`; nada dibuja escarcha ni cristaliza el sprite | Combinar: shader de desaturación+tinte ya existente (`08 · 06 §6.1`) + una textura de escarcha sobrepuesta con `bm_add` — no hace falta técnica nueva, falta el ejemplo que una las dos piezas |
| A7 | **Quemado como efecto visual compuesto** (llamas persistentes sobre el sprite, carbonizado) | 🟡 | `pt_fuego`/`pt_ascua` ya existen (`04 · 39 §3.1`) para fuego *en un punto*; `04 · 32 §4.5-4.6` aplica el tinte de daño por quemadura | Falta el ejemplo de **emisor adjunto a una instancia en movimiento** (`part_type_step` desde el `Step` del enemigo, no desde un punto fijo) y el oscurecimiento progresivo del sprite (no solo tinte, sino `image_blend` decreciente hacia negro) |
| A8 | **Electricidad / arcos eléctricos / rayo encadenado** | 🔴 | Cero menciones (`buscar.py --todo "electricidad"` → solo 2 documentos de diseño teórico, ninguno técnico) | Todo: la técnica estándar es una polilínea con desplazamiento de punto medio (*midpoint displacement*) redibujada cada 2-3 frames con `draw_primitive(pr_linestrip)` — ya documentada como primitiva en `08 · 02` y `08 · 07`, nunca usada así — más el salto entre varios objetivos (`collision_circle_list` para encontrar el siguiente enlace) |
| A9 | **Portal / puerta dimensional / vórtice** | 🔴 | Cero menciones como VFX (`buscar.py --todo "portal"` solo devuelve resultados de servicios de plataforma y UWP) | Anillo aditivo giratorio (reutiliza `pt_onda` de `04 · 39 §3.1` con `part_type_orientation` en vez de crecimiento) + distorsión radial del fondo con el shader de onda ya existente (`08 · 06 §6.5`) |
| A10 | **Agua que salpica** al entrar un cuerpo en una superficie de agua (combinar física de olas + partículas) | 🟡 | `13 · 08 §9 «agua_salpicar()»` resuelve la **onda** (impulso en la columna más cercana) y dice explícitamente «es TODO el splash: la propagación se encarga de las ondas» — sin gotas. `04 · 39 §3.5` sí tiene partículas de gota, pero para lluvia cayendo, no para una entrada en el agua | Una línea que conecte las dos: al llamar `agua_salpicar()`, lanzar también `N` partículas del `pt_gota` de `§3.5` hacia arriba desde el punto de impacto |
| A11 | **Humo volumétrico falso** (que lea como 3D sin serlo: capas con parallax, ruido de dominio, raymarch barato) | 🔴 | `pt_smoke`/niebla ambiental (`04 · 39 §3.7`) son partículas planas 2D; god rays (`04 · 24 §5`) son el único «volumen falso» que existe, y es luz, no humo | Técnica: 2-3 capas de sprite de nube con offset y velocidad distintos + `bm_add` suave, o displacement por ruido animado sobre una superficie — ninguna de las dos está |
| A12 | **Cristal / vidrio roto** | 🟡 | `04 · 39 §3.11 «Destrucción y escombros»` (`romper_en_escombros()`) es exactamente el mecanismo genérico que hace falta: rejilla de trozos con velocidad, giro y gravedad propios, sin coste de VRAM. **No está enlazado como técnica de vidrio** | No hace falta receta nueva: una nota de un párrafo en `04 · 39` (o `08 · 06`) diciendo «vidrio roto = `romper_en_escombros()` con `_fuerza` radial alta y gravedad reducida + `snd_cristal` en capas (agudos + graves) de `13 · 09 §3.1»`, más opcionalmente el paso previo de «grieta» con el shader de disolución umbral bajo |
| A13 | Disolución combinada con partículas (ceniza que sube mientras el sprite se disuelve) | 🟢 | `08 · 06 §6.3` ya tiene el «borde ardiente» integrado en el propio shader (color en el frente de disolución) | El shader no dispara partículas; sería un extra, no un hueco — el borde ardiente ya resuelve la mayor parte de la lectura visual |
| A14 | **Presupuesto de VFX a nivel de JUEGO** (cuántos efectos simultáneos, cómo se recorta cuando se dispara el límite) | 🔴 | `04 · 39 §3.12` mide y recorta partículas **dentro de un sistema** (`part_particles_count`, `part_emitter_enable` por cámara). No existe el equivalente game-wide del sistema de importancia de audio (`04 · 42 §3.4`, que puntúa por daño/distancia/visibilidad y reparte cupos por «cubo») | Un `vfx_solicitar()`/`vfx_resolver()` que puntúe y reparta cupos (alto/normal/bajo/descartado) igual que `sonido_solicitar()`/`importancia_resolver()`, reutilizando la MISMA lógica de puntuación en vez de reinventarla — es el mismo problema con otro canal |
| A15 | Ajuste de calidad gráfica en Opciones que reduzca partículas/efectos | 🟡 | `04 · 28 §6.3` menciona `global.calidad_baja` («y de paso, menos partículas») como mención de una línea en el doc de móvil; `04 · 25` (menú de opciones) no tiene ningún slider ni checkbox de calidad gráfica | Exponer `calidad_baja` como ajuste real en `04 · 25` (persistido, aplicado en vivo como los demás sliders) y conectarlo a `04 · 39` (multiplicador de cantidad de partículas por capa) |
| A16 | **Afinar un shader o una emisión de partículas EN RUNTIME, sin recompilar** | 🟡 | El mecanismo existe y está documentado: `dbg_slider`/`dbg_view` (`01 · 15 §4 «Vistas de depuración personalizadas»`) con el patrón `ref_create(self, "campo")` ya mostrado para un gestor de audio (`13 · 06 §3.14 c`). **Cero menciones de `dbg_` en `04 · 39` ni en `08 · 23`** (grep dirigido, 0 resultados) | Un ejemplo de una línea en cada uno: `dbg_slider(ref_create(objFx, "pt_fuego_life_max"), 10, 60, "Vida del fuego")` para partículas, y lo mismo con un uniform de shader vía una variable intermedia — sin esto, un agente no sabe que la vía existe para VFX |
| A17 | Editor de partículas del IDE: iterar visualmente antes de compilar (diseño, no runtime) | ✅ | `02 · 05 §2.4 «Canvas y Toolbox»` + botón *Copy GML to Clipboard* | — |
| A18 | Telegraph de ataque de jefe por color con tiempos en fotogramas | ✅ | `04 · 15 §5.8` — máquina de estados con `ANTICIPATE_FRAMES = 30`, `STRIKE_FRAMES = 8`, `RECOVER_FRAMES = 40`, tinte progresivo `merge_color` | — |
| A19 | **Indicador de zona de peligro en el suelo** (AoE telegraph — dónde va a caer el golpe, no solo que el jefe se pone rojo) | 🔴 | Cero menciones (`grep` de «zona de peligro», «indicador de área», «marca en el suelo», «retícula» → 0 resultados en toda `04 -`) | Un círculo/cono en el suelo con alfa creciente durante `ANTICIPATE_FRAMES` (reutiliza el propio timer de `§5.8`), dibujado con `draw_circle`/`draw_primitive` antes que el jefe golpee — es el complemento espacial que falta al telegraph temporal que ya existe |
| A20 | Bloom, LUT, aberración cromática, CRT, glitch, shockwave, pixelado, blur de dos pasadas, pipeline multipasada | ✅ | `08 · 23 §3.1-3.10` (los diez shaders completos que pedía la ronda 2) | — |

### B · Audio y SFX — obtención, mezcla y música

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| B1 | **¿Se puede sintetizar audio en runtime en GameMaker?** (verificación explícita que pide el brief) | ✅ VERIFICADO | **Sí.** `08 · 24 §3 «Buffer sounds: síntesis y audio procedural en tiempo real»` — dos ejemplos completos y compilables: tono con envolvente y ruido con caída para una explosión sintetizada, con `audio_create_buffer_sound` (firma verificada con `buscar.py`, devuelve `Asset.GMSound`) | — |
| B2 | Bancos de sonido libres (Freesound, Kenney, OpenGameArt) | ✅ | `07 · 09 §2.5, §8` | — |
| B3 | Generadores tipo sfxr/jsfxr/Bfxr/ChipTone | ✅ | `13 · 09 §A7`; paso a paso en `03 · 09 §11` | — |
| B4 | **Qué hace un agente de IA que necesita un sonido y no tiene ninguno** | 🔴 | No existe la pregunta ni la respuesta en ningún documento (`grep` de «placeholder» + «sonido»/«audio» en `13 -`, `07 -`, `12 -` → 0 resultados cruzados). Las piezas de la respuesta correcta **sí existen por separado**: síntesis por código (B1, sin dependencias externas, la única vía que un agente sin navegador puede ejecutar él mismo) y el patrón de *placeholder* declarado (`13 · 11 §…` `PLACEHOLDERS.md`, hoy solo para arte) | Un párrafo corto en `13 · 09` o `08 · 24` que ordene las opciones por lo que un agente puede hacer sin salir de la biblioteca: 1) sintetizar con `audio_create_buffer_sound` (B1, siempre disponible), 2) generar con sfxr/jsfxr si tiene acceso de shell/navegador, 3) marcar como placeholder silencioso en `PLACEHOLDERS.md` (extendiendo su alcance de «solo arte» a audio) y seguir |
| B5 | Ducking por prioridad (voz sobre música) | ✅ | `13 · 09 §4.2`, `07 · 21 §3` (Vinyl) | — |
| B6 | Límite de voces simultáneas y robo de la más antigua | ✅ | `13 · 09 §3.3` (`sonar_limitado`) | — |
| B7 | Variación de tono y volumen para que un disparo repetido no canse | ✅ | `13 · 09 §3.2` (`variacion_tono`, `variacion_ganancia`) | — |
| B8 | **Colas y agrupación de sonidos idénticos disparados en el mismo frame** | ✅ | `04 · 42 §3.4` (sistema de importancia: puntúa y arbitra ENTRE sonidos distintos que compiten en un frame, resuelto en *End Step*) **+** `13 · 09 §3.3` (cupo por sonido para el MISMO sonido repetido). El propio `04 · 42 §3.4` deja la nota explícita: «úsalos juntos» | — |
| B9 | Bucles de música sin costura (loop points) | ✅ | `01 · 13 §5`, `02 · 07 §4` | — |
| B10 | Puntos de transición musicales (por compás, no a lo bruto) | ✅ | `04 · 26 §«Transición por compás»` | — |
| B11 | Capas verticales (*vertical layering*) | ✅ | `04 · 26 §«La idea»` | — |
| B12 | **Capas horizontales (*horizontal resequencing*)** — hueco cerrado desde la ronda 2 | ✅ cerrado | `04 · 26 §«Transición horizontal: cambiar de tema sin cortar»` (segmentos con puntos de salida legales, segmento puente) | — |
| B13 | Música como máquina de estados | ✅ | `04 · 26 §«La música como máquina de estados»` | — |
| B14 | Subtítulos de efectos de sonido con indicador direccional | ✅ | `13 · 24 §4` (registro sonido→texto, cola apilada, indicador de borde) + `04 · 27 §5.3` | — |
| B15 | Toggle mono/estéreo | ✅ | `04 · 27 §5` | — |
| B16 | Voz: grabación como producción (guion, nomenclatura, dirección, edición) | ✅ | `13 · 24 §2` | — |
| B17 | Localización de voz (asset por idioma, fallback a subtítulos) | ✅ | `13 · 24 §3` | — |
| B18 | Lip-sync básico en 2D | ✅ | `13 · 24 §5` (alternativa barata por amplitud + visemas precalculados) | — |
| B19 | Sync groups, play queues, grabación de micrófono, Doppler (el hueco de API de la ronda 2) | ✅ cerrado | `08 · 24 §2, §4, §5, §6` — 21 funciones que solo eran nombres en `API-funciones.md` ahora tienen prosa y ejemplo | — |
| B20 | Estado del ecosistema Wwise/FMOD para GameMaker | ✅ | `07 · 09`, catálogo — Wwise sin mantenimiento, FMOD con extensión oficial documentada como coste real | — |

### C · Feedback — cadena del golpe, negativo, legibilidad a escala y móvil

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| C1 | La cadena de un golpe (empuje, hit stop, shake, partículas, sonido, número) EJECUTADA de una vez | ✅ | `04 · 15 §5.7 «El golpe completo»` — función única con las 10 capas | — |
| C2 | Anticipación de un ataque, con tiempos en fotogramas | ✅ | `04 · 15 §5.8` (frames explícitos, ver A18) | — |
| C3 | **La cadena completa documentada COMO CADENA temporal única** (entrada→anticipación→impacto→hit stop→sacudida→partículas→sonido→número→reacción del enemigo, con offsets de fotograma entre etapas) | 🟡 | Las piezas existen con SUS PROPIOS tiempos (`§5.7` para el impacto, `§5.8` para la anticipación del atacante) pero **nunca se ensamblan**: `§5.7` dispara sus 10 pasos en el mismo frame (no hay offsets entre número flotante, partículas y sonido), y no incluye la fase de anticipación ni la de reacción del enemigo | Un diagrama/tabla único en `§5.7` o `§5.9`: fila por etapa, columna de fotograma relativo al impacto (p. ej. flash y partículas en 0, hit stop 0-4, shake decayendo 4-20, número con retardo de 2, reacción del enemigo en 6) — no hace falta código nuevo, es ensamblar lo que ya está |
| C4 | **Reacción explícita del enemigo al golpe** (estado de «herido» distinto del empuje físico: interrumpe la IA, sprite/animación de daño) | 🟡 | `04 · 15` resuelve el empuje (`apply_knockback`) y el squash; `04 · 31 §…` (IA de decisión) solo documenta interrupción de IA por **amenaza nueva**, no por **recibir daño** | Un `hitstun` que además ponga la máquina de estados de IA en pausa/estado «herido» N frames, con su propia animación — hoy `hit_complete()` no toca el estado de la IA del enemigo, solo su física |
| C5 | **Indicador de zona de peligro en el suelo (AoE telegraph)** | 🔴 | Ver A19 — mismo hueco, doble ángulo (VFX y feedback) | — |
| C6 | **Feedback de acción rechazada / bloqueada como patrón general** («por qué mi ataque no salió», «por qué no puedo entrar ahí», «por qué no se abre la puerta») | 🟡 | Existe como **ejemplos sueltos, no como principio**: puerta cerrada que se sacude sin decir el motivo (`04 · 06 §«Feedback: la puerta se sacude»`), icono de habilidad al 60 % durante el enfriamiento (`04 · 36 §…`), botón de UI inactivo que «dice por qué» (`13 · 05 §1.5`, con la regla explícita «un botón inactivo se dibuja, no se esconde»). **Ningún documento junta los tres en un principio reutilizable para el MUNDO del juego** (fuera de menús): intentar un ataque en cooldown no tiene sonido de rechazo documentado en `04 · 36`; un muro invisible (`04 · 37 §…`, `04 · 47 §…`) no tiene feedback de choque asociado | Una sección corta en `04 · 15` o `13 · 05` que generalice la regla de UI («toda entrada rechazada produce alguna respuesta en ≤1 frame») al mundo: sonido de «denegado» en habilidades bloqueadas, temblor/destello en colisiones con muros invisibles — enlazando, no repitiendo, los tres ejemplos que ya existen |
| C7 | **Legibilidad en pantalla llena — con 200 enemigos, ¿cómo sabe el jugador qué le está matando?** | 🔴 | `04 · 44 §1.4.5-1.4.6` (bullet heaven) resuelve **rendimiento** con siete técnicas (pooling, culling, tick escalonado, `collision_circle_list`) y no dice una palabra sobre **lectura visual**: contraste de silueta del proyectil peligroso frente al ambiente, atribución del daño (qué instancia concreta golpeó), jerarquía de color por amenaza | Sección de legibilidad a escala: silueta/contorno reservado para lo peligroso (reutiliza `08 · 06 §6.2` outline), un color que NINGÚN elemento decorativo use (regla de exclusividad cromática), y opcionalmente un `ultimo_atacante` guardado en el jugador para que el número de daño (`04 · 15 §5.6`) pueda etiquetarse con la fuente |
| C8 | **Feedback en móvil consciente del dedo y silencioso por defecto** (el dedo tapa lo que toca; muchos juegan sin sonido) | 🟡 | `04 · 28 §1` («El dedo tapa lo que toca» → botones en el borde, contenido en el centro) resuelve el LAYOUT; `04 · 28 §8.2` documenta vibración como canal alternativo. **Ningún documento dice explícitamente «diseña el feedback asumiendo sonido apagado y el dedo encima»** como principio, ni dónde debe aparecer la confirmación visual de un toque (lejos del punto de contacto, no debajo del dedo) | Un párrafo en `04 · 28 §5` (UI táctil) o `13 · 05`: la confirmación de una acción táctil se dibuja donde SE VE (borde superior, HUD), nunca en el punto exacto del toque; todo feedback crítico tiene equivalente visual y háptico, nunca solo sonoro |
| C9 | Vibración/háptica como capa de feedback, con toggle | ✅ | `04 · 27 §4.1`, `04 · 28 §8.2` | — |
| C10 | Reducir movimiento agresivo / tope de flashes / shake desactivable | ✅ | `04 · 27 §3` | — |
| C11 | Celebración de recompensa (subida de nivel, fanfarria, pantalla de resultados) | ✅ cerrado | `04 · 15 §8bis.1-8bis.3` | — |
| C12 | Fracaso sin humillar (coste de reintento, no repetir cinemática) | ✅ cerrado | `04 · 15 §8bis.4` | — |
| C13 | Sistema de tutorial en GML (disparadores, «mostrar una vez», escalado de pistas) | ✅ cerrado | `04 · 40` | — |
| C14 | Transiciones (wipe, iris, disolución), pantalla de carga real, menú de pausa completo | ✅ cerrado | `04 · 41` | — |
| C15 | Estela de cinta (trail de espada) con `draw_primitive` | ✅ cerrado | `04 · 39 §3.9.1` | — |
| C16 | *Permanence*: decals de sangre/casquillos persistentes en surface | ✅ cerrado | `04 · 39 §3.10` | — |
| C17 | Zoom punch / retroceso de cámara | ✅ cerrado | `04 · 15 §8.3` | — |
| C18 | Botón inactivo que explica el motivo, cuatro estados de un control | ✅ | `13 · 05 §1.5` | — |

**Recuento:** 58 temas · **39 CUBIERTO** (67 %, de los cuales 13 son hallazgos de esta pasada
confirmando que un hueco cerrado por la ronda 2 sigue cerrado) · **13 PARCIAL** (22 %) ·
**6 FALTA** (10 %).

---

## 2 · Huecos por prioridad

### 🔴 Graves

**1 · VFX compuestos ausentes: electricidad, portal, humo volumétrico falso** (A8, A9, A11)

Los tres piden técnica nueva, no solo ensamblar piezas. Encargo: sección nueva
`04 · 39 §3.13 «Efectos compuestos»` con tres recetas cortas:
- **Electricidad/rayo**: polilínea con desplazamiento de punto medio, redibujada cada 2-3 frames
  con `draw_primitive(pr_linestrip)` (primitiva ya documentada en `08 · 02`/`08 · 07`, verificar
  con `buscar.py pr_linestrip`), más salto entre objetivos con `collision_circle_list`.
- **Portal**: anillo `pt_onda` de `§3.1` con `part_type_orientation` en vez de `size_incr`, sobre
  el shader de onda de `08 · 06 §6.5` aplicado solo al área del portal (surface recortada con
  stencil, `08 · 04`).
- **Humo con volumen falso**: 2-3 capas de `pt_smoke` con offset y velocidad distintos + `bm_add`
  suave, o displacement por ruido animado sobre una surface pequeña.

**2 · Presupuesto de VFX a nivel de juego, y su conexión con calidad gráfica** (A14, A15)

Encargo: función `vfx_solicitar()`/`vfx_resolver()` en `04 · 39` que reutilice **la misma lógica**
de puntuación y cubos de `importancia_calcular()`/`importancia_resolver()` de `04 · 42 §3.4`
(mismo patrón, canal distinto: daño/distancia/visibilidad → cubo → cupo). Y exponer
`global.calidad_baja` (hoy solo mencionada en `04 · 28 §6.3`) como slider real en `04 · 25`,
conectado a un multiplicador de densidad de partículas en `04 · 39`.

**3 · Indicador de zona de peligro en el suelo (AoE telegraph)** (A19, C5)

Encargo: sección en `04 · 15` (junto a `§5.8`) o `04 · 39`: círculo/cono en el suelo con alfa
creciente durante `ANTICIPATE_FRAMES` del propio `§5.8`, dibujado con `draw_circle`/
`draw_primitive` antes de que el jefe golpee. Es el complemento espacial al telegraph temporal
que ya existe con código completo.

**4 · Legibilidad en pantalla llena** (C7)

Encargo: sección en `04 · 44` (o `13 · 05`) sobre lectura visual a escala: reserva de un color/
contorno exclusivo para lo peligroso (reutiliza el shader de outline de `08 · 06 §6.2`), regla de
exclusividad cromática frente a decoración, y `ultimo_atacante` para atribuir el daño en el número
flotante de `04 · 15 §5.6`.

### 🟠 Medios

**5 · Qué hace un agente sin archivo de audio** (B4)

Encargo: un párrafo en `13 · 09 §8` (Herramientas, licencias y accesibilidad) o al principio de
`08 · 24 §3`: orden de prioridad para un agente sin acceso a herramientas externas — 1) sintetizar
con `audio_create_buffer_sound` (siempre disponible, sin dependencias, ya con dos ejemplos
completos en `§3`), 2) generador externo si hay acceso a shell/navegador, 3) `PLACEHOLDERS.md`
extendido a audio (hoy `13 · 11` solo cubre arte).

**6 · VFX/shader sin conexión a `dbg_slider` para afinar sin recompilar** (A16)

Encargo: un ejemplo de una línea en `04 · 39` y otro en `08 · 23`, citando `01 · 15 §4` y el
patrón `ref_create` ya usado en `13 · 06 §3.14 c`. Sin código nuevo — es la cita que falta.

**7 · La cadena del golpe, ensamblada como diagrama temporal único, con reacción del enemigo** (C3, C4)

Encargo: tabla de fotogramas en `04 · 15 §5.9` (nueva) que ordene lo que `§5.7` y `§5.8` ya
resuelven por separado, y una fila nueva: `hitstun` que ponga en pausa la máquina de estados de
IA del enemigo (no solo la física) y dispare una animación de «herido» — enlazando con
`04 · 31` (interrupción de IA) en vez de repetirlo.

**8 · Congelación y quemado como efecto visual compuesto** (A6, A7)

Encargo: dos párrafos cortos en `04 · 32 §4.6` o `04 · 39`, combinando piezas EXISTENTES (shader
de tinte de `08 · 06 §6.1`, `pt_fuego`/`pt_ascua` de `04 · 39 §3.1` con `part_type_step` adjunto
a la instancia en vez de a un punto fijo). No hace falta técnica nueva.

**9 · Feedback de acción rechazada como patrón general** (C6)

Encargo: párrafo en `04 · 15` o `13 · 05` que generalice a todo el juego la regla de UI («toda
entrada rechazada responde en ≤1 frame»): sonido de denegado en habilidades en enfriamiento
(`04 · 36`), feedback de choque en muros invisibles (`04 · 37`, `04 · 47`).

### 🟡 Menores

**10 · Vidrio roto: enlazar, no reinventar** (A12)

Un párrafo en `04 · 39` o `08 · 06`: «vidrio roto = `romper_en_escombros()` (`§3.11`) con
`_fuerza` radial alta y gravedad reducida + sonido en capas de `13 · 09 §3.1`». Cero código
nuevo.

**11 · Agua que salpica: conectar onda + partícula** (A10)

Una línea en `13 · 08 §9`: al llamar `agua_salpicar()`, lanzar también partículas del `pt_gota`
de `04 · 39 §3.5` desde el punto de impacto.

**12 · Feedback móvil consciente del dedo y silencioso por defecto** (C8)

Un párrafo en `04 · 28 §5`: la confirmación de un toque se dibuja lejos del punto de contacto
(HUD, borde), nunca debajo del dedo; todo feedback crítico tiene equivalente visual y háptico.

---

## 3 · Encargo para el redactor

1. **`04 · 39 §3.13 «Efectos compuestos»`** (documento existente, sección nueva) — electricidad
   (`draw_primitive(pr_linestrip)` + desplazamiento de punto medio + `collision_circle_list`),
   portal (`pt_onda` con `part_type_orientation` + shader de onda de `08 · 06 §6.5` recortado con
   stencil de `08 · 04`), humo con volumen falso (capas de `pt_smoke` con offset/velocidad
   distintos + `bm_add`). Símbolos a verificar con `buscar.py`: `pr_linestrip`,
   `collision_circle_list`, `part_type_orientation`, `gpu_set_stencil*` (ya usados en la
   biblioteca, confirmar firma exacta antes de escribir).
2. **`04 · 39 §3.14 «Presupuesto de VFX a escala de juego»`** — `vfx_solicitar()`/
   `vfx_resolver()` calcado del patrón de `importancia_calcular()`/`importancia_resolver()` de
   `04 · 42 §3.4` (mismo `array_sort` con `sign()`, mismos cubos alto/normal/bajo/descartado).
3. **`04 · 25` (menú de opciones)** — slider/checkbox de calidad gráfica que exponga
   `global.calidad_baja` (hoy solo en `04 · 28 §6.3`) y lo aplique como multiplicador de densidad
   en `04 · 39`.
4. **`04 · 15 §5.9 «Zona de peligro» y §5.10 «La cadena, ensamblada»`** — indicador de área en el
   suelo durante `ANTICIPATE_FRAMES` de `§5.8`; tabla de fotogramas que una `§5.7` + `§5.8` +
   un `hitstun` de IA nuevo que enlace con `04 · 31`.
5. **`04 · 44` (o `13 · 05`) — sección «Legibilidad a escala»** — silueta reservada para peligro
   (reutiliza `08 · 06 §6.2`), regla de exclusividad cromática, `ultimo_atacante` para atribución
   de daño.
6. **`13 · 09 §8` o `08 · 24 §3`** — párrafo «Qué hacer si no tienes el archivo de audio»:
   síntesis por código primero (siempre disponible), generador externo si hay acceso, extender
   `PLACEHOLDERS.md` (`13 · 11`) a audio.
7. **`04 · 39` y `08 · 23`** — una línea cada uno citando `01 · 15 §4` y el patrón `ref_create`
   de `13 · 06 §3.14 c` para afinar un parámetro de VFX/shader con `dbg_slider` sin recompilar.
8. **`04 · 32 §4.6`** — dos párrafos: congelación (tinte de `08 · 06 §6.1` + textura de escarcha
   aditiva) y quemado (`pt_fuego`/`pt_ascua` de `04 · 39 §3.1` con `part_type_step` adjunto a la
   instancia).
9. **`04 · 15` o `13 · 05`** — «Feedback de acción rechazada» como principio general, enlazando
   (no repitiendo) `04 · 06` (puerta), `04 · 36` (enfriamiento), `13 · 05 §1.5` (botón inactivo).
10. **`04 · 39` o `08 · 06`** — un párrafo: vidrio roto = `romper_en_escombros()` (`§3.11`) +
    sonido en capas.
11. **`13 · 08 §9`** — una línea: `agua_salpicar()` también lanza partículas de `04 · 39 §3.5`.
12. **`04 · 28 §5`** — un párrafo: confirmación táctil lejos del dedo, feedback crítico con
    equivalente visual+háptico.

---

## 4 · Lo que comprobé y NO hacía falta

- **El sistema de partículas 2026 SÍ está conectado con las recetas**, y de forma razonada: `04 ·
  39 §2.2` no es un olvido, es una decisión de arquitectura explícita (editor para iterar
  visualmente y efectos ambientales fijos, código para partículas encadenadas y datos dinámicos).
  No hace falta ninguna corrección aquí.
- **El `hit_flash` huérfano de la ronda 2 está resuelto.** `04 · 15 §5.6 bis` lo dibuja con las
  tres vías prometidas.
- **La voz, la localización de audio y el lip-sync existen con documento propio** (`13 · 24`, 914
  líneas) y son suficientemente profundos para pasar la prueba de agente: guion con nomenclatura
  que encaja con `asset_get_index`, fallback a subtítulos, visemas precalculados.
- **El hueco de API de audio de la ronda 2 (sync groups, buffer sounds, play queues, grabación,
  Doppler) está cerrado con las 21 funciones documentadas**, no solo listadas.
- **La música horizontal/vertical, que la ronda 2 marcó PARCIAL, está completa**: `04 · 26` tiene
  ambas mitades del par.
- **El presupuesto de partículas DENTRO de un sistema, el culling por cámara y los 10 shaders de
  efecto de la ronda 2 son sólidos**: no se reabren.
- **La celebración de recompensa, el fracaso sin humillar, el tutorial en GML y las transiciones/
  pausa** — los cuatro huecos «graves» de `feedback-ux.md` (ronda 2) — están cerrados con código
  verificable (`04 · 15 §8bis`, `04 · 40`, `04 · 41`).
- **La agrupación de sonidos idénticos en un mismo frame SÍ está resuelta**, y mejor de lo que
  esperaba: `04 · 42 §3.4` arbitra entre sonidos DISTINTOS que compiten por hueco en el mismo
  frame, y su propia nota final remite a `sonar_limitado()` (`13 · 09 §3.3`) para el caso del
  MISMO sonido repetido — las dos piezas, con la conexión explícita entre ellas.
- **Revisé `04 · 33` (director de combate) buscando un presupuesto de VFX o un telegraph de área
  ya resuelto ahí**: no está; el documento se centra en la orquestación de encuentros (qué enemigo
  ataca cuándo), no en el feedback visual del ataque.
- **Revisé si `13 · 10` (Testing y QA) o `13 · 06` (Arquitectura) ya conectaban `dbg_*` con algún
  sistema visual**: solo aparece aplicado a datos de balance y a un gestor de audio de ejemplo,
  nunca a VFX — confirma A16 en vez de contradecirlo.

---

## 5 · Lo que encontré desactualizado

- **Ninguna afirmación de la biblioteca que haya comprobado en este dominio resultó falsa.** Las
  citas de funciones que verifiqué con `buscar.py` (`audio_create_buffer_sound`, `pr_linestrip`,
  `dbg_slider` y familia) coinciden con el runtime `2026.0.0.23` declarado. No detecté ninguna
  fecha de caducidad incumplida (versiones de librerías, políticas de tienda) dentro del alcance
  de esta pasada — los huecos que encontré son de **contenido ausente**, no de contenido
  incorrecto.

---

## 6 · Limitaciones de esta auditoría

- **Sin `WebSearch`/`WebFetch` en esta sesión**: no verifiqué en vivo ninguna fuente externa
  (técnica de *midpoint displacement* para rayos, prácticas de legibilidad de bullet-hell). Las
  cito por su nombre canónico de la disciplina, no por una URL comprobada hoy.
- **No compilé ningún ejemplo nuevo.** Los símbolos que cito para los encargos (`pr_linestrip`,
  `collision_circle_list`, `dbg_slider`, `audio_create_buffer_sound`) los verifiqué con
  `buscar.py` contra `GmlSpec.xml`/`fnames`, no ejecutando `gm-cli compile` sobre código de
  ejemplo — ese código está por escribir.
- **No releí character por character los 3844 líneas combinadas de `04 · 39` + `04 · 42` + `08 ·
  23` + `08 · 24`**: los abrí por índice de secciones y leí completas las que tocaban directamente
  los temas del brief (§2.2, §3.0-§3.12 de `04 · 39`; §3.1-§3.10 de `08 · 23`; §3-§6 de `08 ·
  24`; §3.4 de `04 · 42`). Es posible que alguna sección que no abrí entera resuelva parcialmente
  algún hueco menor que marco como FALTA — los seis hallazgos 🔴 los confirmé con `grep`/
  `buscar.py` de término completo sobre TODA la carpeta correspondiente, no solo sobre el
  documento más probable, así que el riesgo de falso negativo es bajo.
- **No abrí `11 - Código descargado/`** salvo para confirmar que `pr_linestrip` y
  `collision_circle_list` tienen uso real fuera de la biblioteca (ya lo hizo la ronda 2 para VFX
  y audio con más profundidad). Es posible que alguna librería descargada ya resuelva electricidad
  o portales como shader; eso no cambia el veredicto, porque el brief audita la documentación en
  español de la biblioteca, no el código de terceros sin traducir.
- **`03 - Cursos (YouTube)` y `10 - Cursos en español`** se comprobaron solo por `grep` puntual
  (el hallazgo del anti-spam de sonido, B-adjacente, salió de ahí). Por el orden de autoridad de
  `AGENTS.md §1` no cambiarían un veredicto CUBIERTO por sí solos.
