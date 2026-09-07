# Auditoría r4 · Cierre

> Fecha: 07-09-2026 · Auditor de cierre de la cuarta ronda. Metodología: lectura directa en disco
> de cada documento y sección prometidos, verificación de símbolos GML con `buscar.py`, lectura
> línea a línea de las funciones "reutilizadas" en su documento de origen y en el punto de
> llamada, comprobación de enlaces internos con un script propio (no de memoria), y ejecución
> real de `_indice/actualizar.py`. Cuatro subagentes de apoyo verificaron en paralelo distintos
> lotes del encargo con el mismo criterio de evidencia — incluida una caza de defectos dedicada
> (duplicados, tildes/eñes en identificadores, enlaces y anclas rotas, restos de sesión, funciones
> inventadas) —; sus hallazgos están integrados y, donde ha sido posible, recomprobados por mí de
> forma independiente (marcado como tal).
>
> **Veredicto general: la ronda 4 es sólida.** De ~40 piezas de encargo (7 documentos nuevos + 21
> ampliaciones + ~9 correcciones de ecosistema/frescura), **ninguna está sin hacer** y solo dos
> tienen contenido real pero incompleto (🟡). El defecto más importante no está en lo que se
> escribió, sino en lo que se dejó de enlazar: el documento más valioso de la ronda (`12/09`, el
> manual del agente de IA) es excelente pero **invisible desde el `AGENTS.md` raíz y desde `07/13`**
> — los dos sitios por los que un agente que no pase primero por `SKILL.md` llegaría a él —, y la
> tabla de plantillas rotas que ese mismo documento corrigió con precisión **no se propagó** a los
> dos documentos que el encargo pedía explícitamente corregir (`07/06 §4`, `07/13 §12`), que
> siguen mostrando la tabla vieja e incompleta.

---

## 1 · Tabla de encargo → estado real

### 1.1 Documentos nuevos

| Encargo (informe origen) | Estado | Evidencia |
|---|---|---|
| `04/53` Souls-like (`r4-generos.md`) | ✅ **CERRADO** | 807 líneas. (a) `guardar_punto()` reutilizada con la firma real de `04/06:261` (`_room_id,_x,_y,_hp` con `_hp` opcional — llamada con 3 argumentos es válida en GML, verificado); (b) marca de muerte con desaparición a la 2ª muerte (§3.7-§3.9); (c) enlaza a `13/19 §3.12` sin repetir código, y `13/19` enlaza de vuelta. Cierre a `04/30 §4.5-§4.6` y `04/36` verificado línea a línea. En índice `_INDICE-RECETAS.md:87`. |
| `04/54` Metajuego transversal (`r4-generos.md`) | ✅ **CERRADO** | 978 líneas. Las 4 piezas (logros con `scr_save_load` real, galería con `flag_leer/flag_poner` de `13/12 §6.2`, cronómetro de *splits*, espectador sobre `04/14 §10.1/§5.5/§5.6`) verificadas contra el documento de origen; el `buffer_read`/`buffer_write` del nuevo mensaje de red coincide campo a campo con `04/14`. En índice `:88`. |
| `04/55` Party games (`r4-generos.md`) | ✅ **CERRADO** | 709 líneas. Orquestador con dos cartuchos jugables completos + step sequencer. **Nota**: el encargo original citaba mal la fuente del reloj rítmico (decía `13·19`, que no tiene reloj); el documento usó correctamente `04/19 §1` (`conductor_arrancar`), verificado carácter por carácter — acierto del redactor, error del encargo. En índice `:89`. |
| `04/56` Combate no letal (`r4-combate-colisiones-gdd.md`) | 🟡 **CERRADO con 2 hallazgos en una subsección** | 502 líneas. Ver hallazgos graves/medios más abajo (§3.4 «Intimidar»). En índice `:90`. |
| `05/06` Publicar en consolas (`r4-consolas.md`) | 🟡 **CERRADO, enlazado a medias** | 896 líneas, el documento más investigado de la ronda (registro real de los tres fabricantes, NDA, licencias, lotcheck, TRC/XR, porting houses). Incluso resolvió en vivo una pregunta que el propio informe dejaba pendiente (§3.5: si Switch 2 comparte nodo `switch` — sí, verificado con `resourcetool eval "options info"` sobre 6 proyectos reales). **Pero** el encargo pedía enlazar desde `13/11 §9.1` y `§12`, y desde `13/25` — **ninguno de los tres enlaza al documento nuevo** (verificado con grep; `13/11 §9.1` sigue apuntando solo a `05/02 §1.4/§3.8`). `05/02` sí quedó bien enlazado en ambos sentidos, y README/AGENTS.md/SKILL.md sí lo citan. |
| `12/09` Manual del agente de IA (`r4-agente-ia-gamemaker.md`) | 🟠 **CERRADO como documento, roto el enlazado de origen** | 660 líneas, el documento más riguroso de la ronda: tabla de 18 plantillas (9/9 verificadas hoy), tabla completa de eventos Draw/Other con los 2 bugs de numeración, inventario de 80 herramientas MCP (recontado por mí: 80 nombres únicos, exacto), receta de emergencia para el cuelgue de `resourcetool`, la promoción del hallazgo del crash de `AssetCompiler` desde `PENDIENTE-r3.md`. Ver hallazgo grave más abajo: **no está enlazado desde `07/13`, `07/14` ni desde el `AGENTS.md` raíz**, pese a que el encargo pedía explícitamente la nota en `07/13` y en `AGENTS.md §2.bis`. |
| `13/27` Formatos de producción especiales (`r4-generos.md`) | ✅ **CERRADO** | 677 líneas, las 5 secciones prometidas (kiosco, educativos, publicitarios, niños —enlaza de verdad a `13/11 §9.3` COPPA/RGPD—, *streamers*). En índice de `13`, línea 44. |

### 1.2 Ampliaciones — grupo combate/colisiones/GDD (`r4-combate-colisiones-gdd.md`)

Las 9 verificadas independientemente por un subagente, con lectura de la función de origen citada
en cada caso. Todas ✅ **CERRADAS**: `04/37 §3.11` (cintas transportadoras, distingue explícitamente
de `objPlatformMoving`), `13/08` nueva §3.4 (orden de resolución con varias colisiones), `04/34 §4.6`
(calor como recurso, enlaza a `04/45 §3.2`), `13/02 §3.4` (tabla tilemap vs. instancia), `13/14 §7`
(del GDD al proyecto, 3 partes), corrección de las filas 2.16/2.8 de `13/14 §2` (ya no remiten a un
hueco de r2, enlazan a `13/16`/`13/20`), `04/01 §4.8` (ascensor = plataforma vertical), `13/19`
nuevo `§3.12 lock-on-target` (mismo formato tabla+código, no un documento aparte), `04/31` nuevo
`## 10 bis` minimax con poda alfa-beta (medición real 549 946→18 297 nodos, distingue de
FSM/BT/utility/GOAP).

### 1.3 Ampliaciones — grupo VFX/audio/feedback (`r4-vfx-audio-feedback.md`)

Las 12 verificadas independientemente por otro subagente. Todas ✅ **CERRADAS**, incluida la
reutilización de código más exigente de la ronda: `04/39 §3.14` (`vfx_solicitar()`/`vfx_resolver()`)
comparada línea a línea con `04/42 §3.4` (`importancia_calcular()`/`importancia_resolver()`) —
misma fórmula de pesos, mismos umbrales de cubo (65/35/12), mismo `array_sort` con `sign()`, mismo
aviso de truncamiento; la única diferencia (una *closure* en vez de un id de sonido) está
justificada. También verificado: `13/09 §8 bis` existe con contenido real y sustancioso (no es un
enlace roto, como podría sugerir su cita desde `12/09`), `04/25 §2 bis` conecta
`global.calidad_baja` con `04/39`, y el resto de piezas menores (congelación/quemado en `04/32`,
vidrio roto, salpicaduras de agua, *dbg_slider*, feedback táctil).

### 1.4 Ecosistema, consolas y frescura — verificadas directamente por mí

| Encargo | Estado | Evidencia |
|---|---|---|
| Licencia de Emu corregida (3 sitios) | ✅ | `07/_INDICE-ECOSISTEMA.md:123` y las 2 filas de `11/CAT` (`:280`, `:292`) dicen "MIT" |
| Clúster runners homebrew (`cinnamon`, `GameMaker-Anywhere`) | ✅ | `11/CAT:693-695` |
| Tooling GM8.x (`OpenGMK`, `GM8Decompiler`, `gm8x_fix`) | ✅ | `12/08:218-220` |
| Aviso de desfase de `gm-i18n` | ✅ | `12/05:333` |
| URL vigente del Marketplace | ✅ | `r3-herramientas-pipeline.md:67` |
| 4 filas nuevas en el blog oficial (`07/11`) | ✅ | 4 filas confirmadas con sus URL |
| Notas 💸 de GMPhysX/MajorGUI_GML/REZOL en `07/02` | ✅ | líneas 257, 279, 354 |
| Regla del tema 20 (consola sin detalle → decirlo, no inventar) | ✅ | En el preámbulo de `05/06` (alternativa que el propio encargo permitía) |
| `gmtkgamejam.com` marcado como caído | ✅ | `07/_INDICE-ECOSISTEMA.md:334` y `07/08:249` |
| Resto de `r4-frescura.md` (precios itch.io, versiones de Snitch/db/iota, re-ejecutar validador con metodología fiable) | ⏳ **Pendiente, tal y como el propio informe ya avisaba** | El informe los marca explícitamente como "no urgente"/trabajo futuro, no como parte del encargo de esta ronda — no cuenta como incumplimiento |

---

## 2 · Prueba de agente, pregunta por pregunta

Leído `_indice/skills/gamemaker-biblioteca/SKILL.md` como si fuera un agente sin más contexto.

**1. ¿Sabría crear un proyecto y no elegir una de las 9 plantillas rotas?**
**Sí, por la vía de la skill.** `SKILL.md:64-66` da la lista completa y correcta ("usa una de las
que funcionan —*Space Rocks*, *Blank Pixel Game*, *Tower Defense*, *RPG Starter Pack*—; la tabla
completa está en `12/09`") y `12/09` tiene las 9 con evidencia. **Pero no por la vía del `AGENTS.md`
raíz**: su único aviso (`AGENTS.md:202`, "Usa *Space Rocks* o *Blank Pixel Game*, o crea el proyecto
desde el IDE. Detalle en `07 - Ecosistema/13`") apunta a `07/13 §12`, que **sigue teniendo la tabla
vieja de solo 3 filas** (Space Rocks, Blank Pixel Game, Platformer) — de las 7 plantillas que
funcionan sin estar documentadas ahí (Tower Defense, RPG Starter Pack, Scrolling Shooter, Survivor,
Brick Breaker, Puzzle Slider, Fire Jump), un agente que solo lea `AGENTS.md`→`07/13` no las conoce,
y de las 6 que fallan sin aviso ahí (Endless Runner, Idle Game, Twin Stick Shooter, Match 3, Card
Game, Cover Assault, Arcade Action Game) tampoco sabe que están rotas.

**2. ¿Sabría en qué archivo va el evento Step de un objeto, con su nombre exacto?**
**Sí.** `12/09 §2.2`: `step_normal`→`Step_0.gml`, `step_begin`→`Step_1.gml`, `step_end`→`Step_2.gml`.
Verificado que la tabla existe con ese contenido exacto.

**3. ¿Sabría qué hacer si `resourcetool` se queda colgado?**
**Sí.** `SKILL.md:60-63` da la respuesta accionable en la propia skill (desactivar el sandbox, o
invocar el binario `ResourceTool` cacheado directamente) y remite a `12/09` para la receta completa
con el comando `find` exacto. Suficiente sin necesidad de abrir `12/09`.

**4. ¿Sabría que compilar limpio no basta, y qué comando hay que pasar además?**
**Sí, con claridad.** `SKILL.md` dedica media página a esto («Trampa 4», línea 70) y el flujo
(línea 161-162) lo repite: "compilar limpio **no** significa que el código sea correcto". El
comando (`validar-proyecto.py --todo`, con el matiz de que sin `--todo` una función `desconocida`
no falla el comando) está explicado con el mismo ejemplo mínimo reproducible en las dos fuentes.

**5. ¿Sabría dónde mirar para publicar en Steam, y dónde para Nintendo?**
**Sí.** Tabla "Qué leer según la tarea" (`SKILL.md:116-117`): Steam/tiendas → `05/02`→`05/05`;
consola → `05/06`, con una frase que distingue trámite público de NDA.

**6. ¿Sabría qué hacer si necesita un sonido y no tiene ningún archivo?**
**Sí.** `SKILL.md:119` remite a `13/09 §8 bis`, que existe de verdad (confirmado, no es un enlace
roto) con una escalera de prioridad completa y código funcional (`tono_generar()`/`ruido_generar()`
de `08/24 §3`, ambas verificadas con `buscar.py` junto con `audio_create_buffer_sound`,
`audio_free_buffer_sound`, `buffer_delete`, `audio_sound_pitch`).

**Conclusión de la prueba**: las 6 respuestas son «sí» **por la vía de la skill**, que es el
escenario exacto del brief («un agente carga la skill `gamemaker-biblioteca`»). El único matiz es
la pregunta 1 cuando el camino es `AGENTS.md` en vez de `SKILL.md` — un escenario real (cualquier
agente trabajando ya dentro de este repo, o cualquier CLI que use `AGENTS.md` sin pasar por
`SKILL.md`), pero no el que el brief pide comprobar en primer lugar.

---

## 3 · Defectos, por gravedad

### 🔴 Graves

Ninguno que bloquee a un agente que siga la skill de principio a fin. El más cercano a esta
categoría es el siguiente, rebajado a 🟠 porque tiene una vía de éxito real (la skill) aunque la
vía secundaria (`AGENTS.md`/`07/13`) esté rota:

### 🟠 Medios

1. **`07/06 §4` y `07/13 §12` no se corrigieron pese a que el encargo #1 de
   `r4-agente-ia-gamemaker.md` lo pedía explícitamente** ("corregir `07/06 §4` con la tabla
   completa de las 18 plantillas... sustituir la recomendación por «usa cualquiera de estas 9»").
   Ambos documentos siguen con la matriz vieja de solo 3 plantillas (`07/13:184-186`: Space Rocks
   ✅, Blank Pixel Game ✅, Platformer ❌). La información correcta y completa **sí existe**, pero
   solo en `12/09` — y ningún hilo de vuelta conecta `07/06`/`07/13` con `12/09`. Resultado: el
   mismo hecho (qué plantillas funcionan) tiene dos versiones contradictorias vivas a la vez en la
   biblioteca, y la desactualizada es la que encuentra un agente que llegue por el camino más
   obvio (`AGENTS.md` → "Detalle en `07 - Ecosistema/13`").
   *Corrección de una línea que apliqué*: ninguna — no es una corrección trivial de una línea,
   requiere pegar una tabla de 9 filas en dos sitios; queda para el redactor.

2. **`12/09` no está enlazado desde `07/13`, `07/14` ni desde el `AGENTS.md` raíz.** El encargo #2
   de `r4-agente-ia-gamemaker.md` pedía "nota... en `07/13` (junto a §6) y en `AGENTS.md §2.bis`"
   sobre el cuelgue de `resourcetool` bajo sandbox. Verificado con grep: `07/13` no contiene
   "sandbox"/"colgar"/"fetch failed" en ningún sitio, y `AGENTS.md` no tiene ninguna sección
   "2.bis" (sus subsecciones son `1.bis`, `3 bis`, `5 bis`, `5 ter` — ninguna nueva). `07/14`
   tampoco enlaza a `12/09` pese a que `12/09` dice explícitamente que lo complementa. **Mitigado**:
   `SKILL.md` sí enlaza a `12/09` seis veces y de forma correcta (líneas 58, 65, 76, 115, 633 y la
   tabla de rutas), que es la vía que exige el criterio de éxito del brief — por eso esto es 🟠 y
   no 🔴. Pero un agente (o una persona) que trabaje en este repo por la vía documentada en
   `CLAUDE.md` ("las instrucciones completas están en `AGENTS.md`. Léelo antes de actuar") no se
   entera de que `12/09` existe.

3. **`README.md` con conteos obsoletos y contradictorios entre sí, sin actualizar en las 3
   carpetas que la ronda tocó.** La tabla "Mapa de la biblioteca" (§3) da: `04 - Recetas por
   género` → **53** (real: **57**, faltan los 4 nuevos), `12 - Utilidades e integraciones` → **8**
   (real: **9**, falta `12/09`), `13 - Diseño y producción` → **26** (real: **27**, falta `13/27`)
   — y ninguna de las tres descripciones de fila menciona los documentos nuevos por nombre. Solo
   `05 - Referencia` se actualizó bien (dice 6, son 6, con insignia 🆕 y mención explícita a
   "publicar en consolas"). Además el propio README trae **tres cifras de "documentos totales" que
   no coinciden entre sí ni con el conteo real**: "244" (línea 36), "160" (línea 74, claramente
   arrastrado de una versión mucho más vieja del documento — no es atribuible a esta ronda), "256"
   (línea 158) — frente a los **251** que da `_indice/actualizar.py` en vivo ahora mismo. La ronda
   4 tenía la responsabilidad directa de, como mínimo, sumar 4+1+1 a los tres conteos de carpeta
   que sí tocó; no lo hizo.

### 🟡 Menores

4. **`04/56 §3.4 "Intimidar"` cita un campo, `valentia_inversa`, como si ya existiera en
   `ArquetipoDef`/`04·33 §1`, y no existe en ningún otro documento de la biblioteca** (confirmado
   con grep en toda la carpeta `04 - Recetas por género/`; el constructor real de `04/33` no lo
   declara y ninguna de las 6 entradas de `global.arquetipos` lo asigna). Es exactamente el patrón
   de error que la propia biblioteca prohíbe con más fuerza — asumir que algo existe sin
   verificarlo —, aplicado aquí a un campo de datos propio en vez de a una función del runtime, así
   que `buscar.py` no lo puede cazar. En la misma sección, `_pizarra.aliados_noqueados_o_muertos`
   se dice "incrementado por 'enemigo_noqueado'/'muerto' (`senal_escuchar`)" pero ese *listener*
   nunca se escribe en el documento: un mecanismo prometido, no implementado. El resto de `04/56`
   (§3.1, §3.2, §3.3, §3.5, §3.6) está limpio y con citas verbatim correctas contra `04/30`, `04/35`,
   `13/12`, `04/31`.

5. **`04/56 §3.1`**: el estado "noqueado" se implementó como un estado de la FSM de combate, no
   como una entrada de `MotorEfectos` de `04/32 §4.4`, tal y como pedía la redacción literal del
   encargo ("como instancia del motor de efectos"). Es una decisión de diseño razonada y explicada
   en el propio texto (💡, línea 180), no un descuido — pero diverge del encargo sin decirlo con
   esas palabras. No requiere cambio de código, solo una frase que conecte la decisión con el
   porqué de apartarse del encargo.

6. **Enlaces cruzados faltantes hacia `05/06`** desde `13/11 §9.1`, `13/11 §12` y `13/25`, pedidos
   explícitamente por el encargo #1 de `r4-consolas.md`. `13/11 §9.1` sigue enlazando solo a
   `05/02`. No bloquea a un agente (que llegaría a `05/06` por `SKILL.md` o por el propio `05/02`),
   pero dos de los tres puntos de entrada prometidos no se cerraron.

7. **Colisión de numeración `04/56` entre dos informes de auditoría — investigada y resuelta sin
   dejar rastro en disco.** El brief avisaba de una colisión "entre dos agentes en paralelo" esta
   ronda: confirmé que `r4-combate-colisiones-gdd.md` (encargo 5) y `r4-generos.md` (encargo 10)
   proponían **el mismo número, `04/56`, para dos documentos distintos** (combate no letal vs.
   gestión deportiva/manager). Se resolvió bien: `04/56` quedó para "Combate no letal", y "gestión
   deportiva/manager" se integró como `§7.4` dentro de `04/45` — con código funcional completo
   (`scr_manager_partido`, `scr_manager_liga`), no solo una fila de tabla. **No hay colisión activa
   en el disco** (verificado: ningún número de documento duplicado en ninguna de las 13 carpetas
   numeradas de la biblioteca). Se anota como hallazgo cerrado, no como defecto pendiente.

8. **Tres anclas de sección (`#...`) rotas en los documentos nuevos, de una familia de fallo que
   ningún verificador del proyecto detecta.** Verificado que `_indice/verificar-enlaces.py` —el
   que ejecuta `actualizar.py` y el que reportó "0 rutas rotas"— descarta el fragmento con
   `u.split("#")[0]` en las dos líneas donde arma la lista de destinos (`verificar-enlaces.py:41`
   y `:46`): **nunca ha comprobado anclas, en esta ronda ni en ninguna anterior**. Un subagente las
   verificó a mano contra los encabezados reales y encontré, recomprobando dos de los tres yo
   mismo:
   - `04/53:635` enlaza a `04/36#32--recursocombate-...` (doble guion). El encabezado real de
     `04/36` es `### 3.2 \`RecursoCombate\`: el pool genérico...`, cuyo ancla real lleva **un solo
     guion** (`#32-recursocombate-...`) — confirmado porque `04/34:264`, de esta misma ronda,
     enlaza *el mismo epígrafe* con un guion y sí resuelve. El de `04/53` está mal.
   - `04/56:57` y `:61` — dos autoenlaces `[§9](#9-fuentes)`. El documento **no tiene** un
     encabezado `## 9 · Fuentes`: su sección de fuentes es `## Fuentes` a secas (línea 473, sin
     numerar). El ancla real es `#fuentes`. Estos dos son el hallazgo más limpio: rotos con
     total independencia de cualquier ambigüedad de algoritmo de *slug*, dentro del propio
     documento que los declara.
   - `05/06:29` y `:255` enlazan a `05/02#38-bis-qué-exige-...` (un guion) cuando el patrón que
     usan decenas de enlaces correctos de esta misma ronda para secciones "N bis" (p. ej.
     `12/09 → 13/09#8-bis--un-agente-sin-archivo-de-audio...`) usa doble guion — aquí la
     ambigüedad es de qué algoritmo de *slug* asume el repositorio, así que este tercer caso se
     reporta con menos confianza que los dos anteriores, pero apunta en la misma dirección: `05/06`
     también repite mal un patrón de anclaje que ya existía antes de esta ronda.
   Ninguno de los tres impide a un agente encontrar el contenido citado (está a un scroll de
   distancia en el mismo documento), pero rompe el enlace directo que el propio texto promete.

---

## 4 · Reutilización de código entre documentos — 6 casos verificados

| # | Función reutilizada | Origen (firma real) | Uso | Veredicto |
|---|---|---|---|---|
| 1 | `guardar_punto()` | `04/06:261` — `function(_room_id,_x,_y,_hp)`, `_hp` opcional | `04/53:416` — llamada con 3 argumentos (`_hp` queda `undefined`, la función lo maneja) | ✅ Correcta — GML permite omitir argumentos finales |
| 2 | `RecursoCombate` | `04/36 §3.2` | `04/34 §4.6` (calor como recurso de disparo) | ✅ Correcta (verificado por subagente) |
| 3 | `vfx_solicitar()`/`vfx_resolver()` ← patrón de `importancia_calcular()`/`importancia_resolver()` | `04/42 §3.4` | `04/39 §3.14` | ✅ Correcta — comparación línea a línea: misma fórmula de pesos, mismos umbrales, mismo `array_sort` |
| 4 | `separacion_minima()` | `13/08 §3.2` | `13/08` nueva §3.4 (resolución iterativa) | ✅ Correcta (verificado por subagente) |
| 5 | Lock-on de cámara | `13/19 §3.12` | `04/53` (enlaza, no repite código) | ✅ Correcta — cero código de lock-on duplicado en `04/53` |
| 6 | `CartaDef`/`CartaInstancia` | `04/44 §3` | `04/44 §4` (TCG competitivo) | ✅ Correcta — línea 1445 declara explícitamente "esta subsección NO reescribe `Mazo()`, `CartaDef`, `CartaInstancia`, `resolver_efecto()`" |

Ningún caso de función inventada o de reutilización con firma incompatible. El único fallo de
reutilización real de la ronda no es de firma sino de **existencia**: `valentia_inversa` en
`04/56` (hallazgo 4).

---

## 5 · Ejecución de `python3 _indice/actualizar.py`

Salida real, completa (guardada también en el propio proceso de esta auditoría):

```
1. Enlaces internos
1986 rutas correctas · 0 rotas

2. Índices y MAPA.json
documentos en español : 251
manual (inglés)       : 3119
manual (español)      : 3142
archivos .gml          : 61824
símbolos explicados    : 2387  (cruce símbolo → documento)
símbolos de la API     : 3486  (de ellos 34 solo en fnames)
runtime leído          : 2026.0.0.23
MAPA.json sincronizado con el disco.

3. Coherencia de MAPA.json y del catálogo de código con el disco
263 entradas, todas existen en el disco.

4. Ortografía española
Sin palabras españolas escritas sin tilde.

5. Cobertura de la API
3213 de 3213 símbolos vigentes son localizables (100 %).

6. Nombres de archivo
Todos los nombres de archivo están bien escritos.

7. Prueba de descubrimiento (¿un LLM encuentra lo que necesita?)
Las 49 tareas se resuelven. Un LLM encuentra lo que necesita con las herramientas del proyecto.

8. Cobertura por familias de símbolos (dónde falta doc didáctico)
Todas las familias grandes de símbolos tienen algún documento propio.

9. Código GML (¿inventa alguna función del runtime?)
106 funciones propias de ejemplo (informativo) · 0 posibles funciones del runtime INVENTADAS
Ningún nombre con prefijo del runtime sin resolver: el código no inventa funciones.

10. Compilación real del GML de los documentos (¿es sintaxis válida?)
3347 bloques se van a compilar; 302 se saltan:
✓ Los 3347 bloques compilables de los documentos compilan sin errores de sintaxis.
Tiempo total: 16.8s

11. Skill para agentes (gamemaker-biblioteca): índice generado y rutas citadas
references/indice-documentos.md regenerado: 263 documentos.
AGENTS.md regenerado desde SKILL.md: _indice/skills/gamemaker-biblioteca/AGENTS.md
Todas las rutas que cita la skill existen.
  ✓ Claude Code, Codex (pool/activa), ~/.agents genérico, opencode, Qwen Code, Kimi Code CLI: enlazados
  ✗ Gemini CLI / GitHub Copilot CLI / Cursor CLI / Cline: falta el enlace (CLIs no instalados en esta máquina, no es una regresión de esta ronda)

12. Espejo español del manual (¿va a la par del inglés?)
3119 páginas comparadas · 0 ausentes · 0 incompletas · 0 con literales traducidos

Biblioteca coherente. Índices al día y sin deuda pendiente.
EXIT_CODE=0
```

**Código de salida: 0.** Sin deuda pendiente según la propia herramienta. La cifra "251 documentos
en español" de la sección 2 es la fuente de verdad — y no coincide con ninguna de las tres que trae
`README.md` (ver hallazgo 🟠 #3), lo que confirma independientemente que ese conteo es manual y no
se resincroniza con este comando.

No hay ningún proceso de `validar-enlaces-externos.py` en marcha en este momento (comprobado con
`ps aux`); el fichero `_indice/enlaces-externos-muertos.txt` ya se regeneró en vivo dentro de esta
misma ronda (ver `r4-frescura.md`, sección de metodología) y no está pendiente.

---

## 6 · Caza de defectos conocidos — resultado

Un subagente dedicado, más mi propia recomprobación directa sobre los 28 archivos que la ronda
tocó (7 nuevos + 21 ampliados), buscó específicamente los fallos que rondas anteriores encontraron:

| Comprobación | Resultado |
|---|---|
| Números de documento duplicados (las 13 carpetas numeradas) | **Limpio** — verificado por mí y por el subagente, dos veces |
| `MAPA.json` sincronizado con el disco (04, 05, 12, 13) | **Limpio** — recuento exacto en las 4 carpetas, verificado por mí de forma independiente |
| Identificadores GML con tilde/eñe en los 28 documentos tocados | **Limpio** — verificado por mí (28 archivos) y por el subagente (26); solo aparecen tildes en cadenas de texto en español, nunca en nombres de función/variable |
| Enlaces internos rotos (ruta de archivo) en los 28 documentos | **Limpio** — verificado por mí con script propio y por el subagente, 0 rutas rotas |
| **Anclas de sección (`#...`) en los 7 documentos nuevos** | **3 rotas** — ver hallazgo 8 arriba. Ningún verificador del proyecto las comprueba (`verificar-enlaces.py` descarta el fragmento con `.split("#")[0]`, confirmado leyendo el código) |
| Escrituras accidentales en `working_directory` / restos de sesión | **Limpio** — `git status` limpio, sin `.yyp` sueltos fuera de `11 - Código descargado`, sin residuos de las pruebas de `12/09` (que se hicieron bajo `~`, tal y como declara) |
| Funciones de GML inventadas en los 7 documentos nuevos | **Limpio** — 44 candidatas con prefijo de familia nativa, verificadas una a una con `buscar.py`; el único "falso positivo" (`draw_super_mega_sprite`) es un ejemplo deliberado en `12/09` para ilustrar cómo se ve una función inventada, no una invención real (confirmado leyendo esa misma línea del documento) |

La única familia de fallo nueva que ninguna ronda anterior había cazado es la de las anclas: no
porque nadie las rompiera antes, sino porque **nunca hubo una herramienta que las comprobara**. Es
la misma clase de problema que motivó la memoria «los índices se regeneran» de rondas pasadas — un
verificador que da 0 incidencias no es lo mismo que 0 incidencias reales si el verificador no mira
donde hace falta.

---

## 7 · Lo que queda — lista corta y honesta

1. Pegar la tabla completa de 18 plantillas (9 funcionan / 9 fallan) de `12/09 §0` en `07/06 §4` y
   en la matriz de `07/13 §12`, sustituyendo la tabla vieja de 3 filas. Sin esto, dos rutas de
   entrada distintas a la biblioteca dan información incompleta sobre el mismo hecho.
2. Enlazar `12/09` desde `07/13` (junto a §6), `07/14` y desde el `AGENTS.md` raíz (una sección
   nueva, con o sin el número "2.bis" exacto que proponía el encargo).
3. Actualizar en `README.md` los tres conteos de fila (`04`→57, `12`→9, `13`→27) y mencionar los 7
   documentos nuevos en sus descripciones; reconciliar (o eliminar) las cifras "160" y "244" que
   compiten con el "256"/"251" real.
4. En `04/56 §3.4`: marcar `valentia_inversa` explícitamente como campo nuevo a añadir a
   `ArquetipoDef` (con el mismo criterio "NUEVO" que usa el resto de la biblioteca, por ejemplo en
   `04/53`), o quitar la cita a `04·33 §1` como si ya existiera; y escribir el código real del
   `senal_escuchar` que faltaba, o retirar la frase que lo da por hecho.
5. Enlazar `05/06` desde `13/11 §9.1`, `§12` y desde `13/25`, tal y como pedía el encargo.
6. Corregir las 3 anclas rotas del hallazgo 8 (`04/53:635`, `04/56:57`/`:61`, `05/06:29`/`:255`) y,
   como mejora de tooling de una sola función, enseñar a `_indice/verificar-enlaces.py` a comprobar
   también el fragmento `#ancla` contra los encabezados reales del archivo de destino — hoy lo
   descarta por completo, así que "0 rutas rotas" nunca ha significado "0 enlaces rotos".
7. Trabajo ya identificado como no urgente por `r4-frescura.md` y no exigido a esta ronda: recomprobar
   precios de itch.io, versiones de Snitch/db/iota/STANNcam/GMRoomLoader, y re-ejecutar el validador
   de enlaces externos con concurrencia baja desde un entorno con red fiable.

Nada de lo anterior impide que un agente que cargue la skill `gamemaker-biblioteca` lleve un juego
de la idea a la tienda sin inventarse nada — el camino que exige el brief funciona de principio a
fin, verificado pregunta por pregunta en la §2. Los defectos encontrados están todos en las rutas
*secundarias* de descubrimiento (el `AGENTS.md` del propio repo, `README.md`, y una subsección de
un documento por lo demás sólido), no en el camino principal.
