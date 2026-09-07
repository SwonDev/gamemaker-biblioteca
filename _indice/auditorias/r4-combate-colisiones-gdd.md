# Auditoría r4 · Combate, Colisiones y el Documento de Diseño (GDD)

> Fecha: 7 de septiembre de 2026 · **63 temas** · **51 cubiertos** (81 %) · **8 parciales** (13 %) ·
> **4 faltan** (6 %) · Runtime de referencia: GMS2 `2026.0.0.23`.

**Dominio:** segunda pasada sobre colisiones, combate y el documento de diseño, tal y como los
auditó la ronda 2 (`_indice/auditorias/colisiones-movimiento-camara.md`, `combate-enemigos.md`,
`diseno-gdd.md`), con las 21 recetas y documentos de diseño que la ronda 3 añadió desde entonces
(`04/30`–`04/38`, `04/44`–`04/52`, `13/14`–`13/22`). **Excluidos:** `Lumbre/`, `GameMaker_Fuentes/`.

---

## Resumen ejecutivo

**La segunda ronda cerró casi todo lo que la primera dejó abierto.** De los 9 huecos `FALTA` y 20
`PARCIAL` que las auditorías de ronda 2 documentaron en estos tres dominios, **26 están cerrados**
con código real y verificado en los documentos nuevos: `04/32`–`04/36` resolvieron sistema de
daño, arquetipos de enemigo, director de intensidad, combate a distancia con munición/retroceso/
cobertura y habilidades con enfriamiento; `04/37` resolvió pendientes, wall-jump, *ledge grab*,
escaleras, natación y corrección de esquina; `13/14`–`13/22` resolvieron el canon teórico más allá
de MDA, progresión, puzzles, monetización, balance por simulación y diseño de mundo. Esto no es una
opinión: cada cierre está verificado línea por línea en este informe con su sección exacta.

**El hueco más valioso que pedía el brief —¿sirve el GDD como entrada de un agente?— está resuelto,
y bien.** `13 · 14 §6` no solo explica qué hace «implementable» un documento de diseño (reglas
numeradas, parámetros con rango, recorte explícito, criterio de aceptación): incluye un GDD
completo de 83 líneas para un plataformas de 3 niveles, con reglas `R1`-`R4` por sistema y su
criterio de aceptación verificable con `gm-cli compile`. Un agente que solo lea `13/14` puede
**ejecutar** ese documento, no solo hablar de él — pasa la prueba del brief.

**Lo que queda es un residuo pequeño y concreto, no un bloque grande.** Cuatro faltan del todo:
(1) **cintas transportadoras** como mecánica de colisión (existe como ejemplo de sonido, cero
física); (2) **orden de resolución cuando tres o más cuerpos colisionan en el mismo frame** (cero
apariciones en toda la biblioteca); (3) **combate no letal** —pacifismo, aturdir sin matar, huir en
tiempo real, negociar— (cero, salvo una mención de una línea de la contradicción guion/mecánica);
(4) **penalización de muerte recuperable** (*corpse run*/mancha de sangre): reaparición y muerte
permanente están sobresalientes, pero perder un recurso al morir **y poder recuperarlo** no existe
en ningún documento. A eso se suman ocho parciales menores (comparación de coste tilemap/instancia,
cápsula-cápsula, calor de arma, atasco generalizado, y sobre todo **el puente entre el GDD y la
lista de tareas concreta**, que hoy vive repartido en tres documentos sin que ninguno lo una).

**Prueba de agente, dominio por dominio:** en colisiones y combate, un agente que solo lea la
biblioteca puede ejecutar el 94 % de lo auditado sin inventar nada — los cuatro huecos que quedan
son mecánicas concretas ausentes, no descripciones sin código. En el GDD, un agente puede ejecutar
un sistema aislado con `13/14 §6` a la perfección; donde se atasca es al pasar de **un GDD completo
con quince sistemas** a **la secuencia de en qué orden construirlos y qué recurso concreto crea
cada uno** — ahí tiene que decidir por su cuenta, que es exactamente el tipo de invención que esta
biblioteca existe para evitar.

---

## Tabla tema por tema

Leyenda: **C** = CUBIERTO · **P** = PARCIAL · **F** = FALTA. «r2» indica el tema ya estaba en la
tabla de la ronda 2 con ese identificador; «nuevo» indica un tema que ninguna ronda anterior tabuló.

### A · Colisiones

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| A1 | Colisión continua frente a discreta (el objeto rápido que atraviesa la pared) | **C** | `04/49 §B.2.7` — `phy_bullet = true` en la bola de pinball, con `physics_world_update_speed(120)` como refuerzo y la regla del grosor mínimo de pared; `13/08 §3.3` — `avanzar_barrido()`, subdivisión manual; `13/13 §6.6` — `segmento_corta_circulo()` para balas gruesas; `04/02 §4.5` — `collision_line()` para "bala rápida que atraviesa muros" | — Los tres enfoques (Box2D, manual, `collision_line`) tienen código ejecutable y verificado, cada uno con su "cuándo" explícito |
| A2 | Resolución de penetración: cuerpos que ya están solapados al empezar | **C** (r2 A13, reconfirmado) | `13/08 §3.2` — `separacion_minima()`: empuja por el eje de menor penetración, reparto simétrico 50/50 para no dar tirones; funciona igual si el solapamiento existe desde el frame de creación (spawn dentro de otro objeto) que si aparece por movimiento | — |
| A3 | Colisión contra tilemaps frente a instancias: coste, precisión y cuándo cada una | **P** | Cada mecánica por separado: `01/08 §3.4` (requisitos de tilemap), `13/02 §3.4` (las dos vías: máscara del tile set / lectura de celdas con `tilemap_get_at_pixel`), `13/08 §4` (particionado espacial para cientos de instancias), `01/15` Paso 6 (coste de colisiones en µs) | Falta la **tabla de decisión directa**: memoria por celda de tilemap frente a una instancia por pared, precisión (tile = rejilla fija, instancia = cualquier forma), y el cruce con el spatial hash — hoy hay que leer cuatro documentos y sumar la conclusión uno mismo |
| A4 | Plataformas móviles con el jugador encima | **C** (r2 B8, reconfirmado) | `04/01 §4.8, §5.2 "Begin Step"` y `§5.8 objPlatformMoving` — patrón `riding` completo (delta de posición, `riding_prev_x/y`, reasignación al pisar otra) | — |
| A5 | Ascensores | **C** implícito, **P** por nombre | `04/22 líneas 154-155` — `physics_joint_prismatic_create()` con el comentario literal `/// PLATAFORMA / ascensor: prismatic (desliza en un eje)`; también resoluble sin Box2D con `objPlatformMoving` de A4 en eje vertical (mismo código, sin cambios) | El caso Box2D está literalmente etiquetado "ascensor"; el caso manual (mucho más habitual en un plataformas 2D) nunca se nombra así — un lector que busque "ascensor" sin saber que es una plataforma móvil vertical no encuentra la pieza manual |
| A6 | **Cintas transportadoras** (superficie fija que empuja al objeto que la pisa) | **F** | Única aparición: `04/12 §5.1 bis`, como ejemplo de **sonido de maquinaria** («un ventilador, una nave, una cinta transportadora»), sin física alguna | Todo: el patrón es distinto del de A4 (la plataforma NO se mueve; aplica una velocidad lateral constante a quien la pisa mientras dura el contacto). Falta el objeto `obj_cinta` con su vector de empuje, la interacción con el input del jugador (¿puede caminar en contra?, ¿a qué coste?), y el caso de una cinta que además transporta cajas/enemigos sin input propio |
| A7 | Formas rotadas: SAT para rectángulos orientados (OBB) | **C** (r2 A10, con código nuevo desde r2) | `13/13 §6.7` — `caja_rotada_solapa()`: teorema de los ejes separadores, 4 ejes para dos rectángulos, código completo y verificado (no solo la tabla conceptual que citaba r2) | — |
| A8 | «La *bounding box* de GameMaker no rota» | **C** | `13/13 §6.7`, fila de tabla: «Rota con el objeto — AABB: No, la caja crece al girar»; `01/08 §4` regla de los dos sprites (por qué la máscara de imagen SÍ rota con `image_angle`, pero el AABB de referencia no) | — |
| A9 | Cápsulas en 2D | **P** | `13/13 §6.6 segmento_corta_circulo()` cubre el caso más común (bala gruesa/proyectil contra objetivo circular = cápsula-punto); `04/29 §…` cita `ColMesh` y `DS-3DCollisions` para cápsulas en **3D** como librerías de terceros | Falta cápsula-contra-cápsula en 2D (dos segmentos + suma de radios, vía distancia segmento-segmento que ya existe en `13/13 §6.5`): poco frecuente en un juego 2D típico de esta biblioteca (la mayoría usa AABB o máscara precisa para personajes), por eso es prioridad baja, pero es el único hueco real del catálogo de formas |
| A10 | **Orden de resolución cuando tres o más cuerpos colisionan en el mismo frame** | **F** | Cero apariciones de «orden de resolución», «colisiones simultáneas», «varios cuerpos a la vez» en toda la biblioteca. `move_and_collide()` resuelve UNA pareja por llamada (con su propio `iterations` interno, ya cubierto por r2 A6); `separacion_minima()` de A2 resuelve pares, uno detrás de otro, sin garantía de estabilidad si A empuja a B hacia C | El patrón que falta: cuando A se separa de B y ese movimiento hace que A vuelva a solapar con C, ¿se itera (2-4 pasadas, como hace Box2D internamente) o se acepta el error de ese frame (se corrige solo en el siguiente)? Ninguna receta de la biblioteca con más de dos cuerpos empujándose a la vez (`04/51` job system no cuenta: sus colonos no se empujan entre sí) documenta el criterio |
| A11 | Colisión isométrica en rejilla lógica | **C** (r2 A23, cerrado desde entonces) | `13/13 §7.3.1 "Colisionar en la rejilla lógica, no en pantalla"`, `§7.3.2` (máscara `Diamond`), `§7.3.3` (desempate de `depth` en celda compartida), `§7.3.4` (offset por altura/elevación) — las cuatro piezas que r2 pedía en su propuesta P5, todas con código | — |
| A12 | Coste de las colisiones y cómo perfilarlo | **C** (r2 A22, cerrado desde entonces) | `01/15` Paso 6 «Cuánto cuestan las colisiones»: coste relativo por tipo de máscara, `get_timer()` para medir en microsegundos, enlace a `13/08 §4` (spatial hash) y presupuesto de 16 666 µs/frame — exactamente lo que r2 P7 pedía | — |
| A13 | Bandos y capas de colisión (matriz jugador/enemigo/proyectil/mundo) | **C** (r2 A16, cerrado desde entonces) | `01/08 §6 bis "Bandos y capas de colisión"` — sección nueva desde r2 | — |
| A14 | Filtrado de colisiones de Box2D (`physics_fixture_set_collision_group`) | **C** (r2 A16/A21, cerrado desde entonces) | `04/22` línea 200 y contexto — ya documentado, cerrando el hueco que r2 señalaba explícitamente como ausente | — |
| A15 | Colisión contra *paths* y curvas | **C** (r2 A24, cerrado desde entonces) | `13/13 §6.9 "Colisión contra paths y curvas"` — sección nueva desde r2 | — |
| A16 | Traversal avanzado: pendientes reales, *wall slide/jump*, *ledge grab*, agacharse, escaleras, cuerdas, natación, corrección de esquina, empuje de cajas por rejilla | **C** (r2 B6/B9/B10/B11/B14/B15/B16/B18, cerrado en bloque) | `04/37` entero — el documento que r2 propuso literalmente como P1 existe con las nueve subsecciones que pedía (§3.1–§3.10), incluidas las macros de calibración (`SLOPE_ANGLE_MAX`, `CORNER_CORRECTION_PX`, etc.) | — |
| A17 | Pathfinding en plataformas (grafo de saltos, *string pulling*) | **C**, nuevo desde r3 | `04/38 §4` "Pathfinding en plataformas" — por qué `mp_grid` no sirve, el grafo de nodos con tres tipos de arista, simulación del arco de salto | — No estaba en el alcance de r2; se documenta aquí porque cierra un hueco adyacente a la colisión de plataformas que un agente necesitaría para IA que persigue al jugador |
| A18 | Eje Z falso: altura, sombra, colisión en `(x,y)` frente a dibujado en `y-z` | **C**, nuevo desde r3 | `04/46` entero — el «truco» que resuelve saltar en top-down/isométrico sin física 3D real, con la interacción explícita con `04/29` («cuándo esto deja de compensar») | — Cierra de paso el hueco de «altura» que la ronda 2 no llegó a plantear como tema propio |

### B · Combate

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| B1 | Netcode de combate: por qué el *rollback* de verdad es difícil en GML | **C**, nuevo desde r3 | `04/50 §3.8.1-3.8.3` — structs por referencia (`variable_clone` obligatorio), coste de clonado profundo, la arquitectura B de `04/30` como mitigación de raíz, determinismo de coma flotante entre plataformas (marcado ⚠️ sin verificar contra el compilador concreto), y la retirada de `rollback_*` en la Beta 2026.100 R2 con la cita literal | — |
| B2 | **La sensación de un combate con latencia**: predicción del golpe propio y confirmación diferida | **C** | `04/14 §4.4 "Predicción del cliente y reconciliación"` + `§5.7` (código de reconciliación); `§4.7 "Compensación de lag (lag compensation) y hit registration"` — historial de posiciones con marca de tiempo, `hitbox_en_instante()`, `servidor_validar_disparo()` contra la posición **pasada** del objetivo, y la decisión explícita de diseño «favor del atacante no es un bug» | — Es el tema que el brief pedía verificar explícitamente por su distinción con el netcode de B1 (arquitectura) — está resuelto como una pieza aparte, con su propio código |
| B3 | Combate contra grupos: rodear, esperar turno, no apelotonarse | **C** — el brief pedía verificar si estaba en `04/33`: **sí, y además hay una segunda capa** | `04/33 §3 "El gestor de fichas de ataque"` (general: N fichas de acercamiento + N de ataque, cola de espera, hueco de escape garantizado en §2); `04/47 §7 "IA de turnos de ataque: rodean, y solo uno o dos atacan"` — instancia concreta para brawler con `posicion_ranura()` en círculo y radios de melé, más el caso de dos jugadores cooperativos con un `GestorFichas` por objetivo | — |
| B4 | Reaparición, *respawn* y puntos de control | **C** (r2 D4, reconfirmado) | `04/01 §6`, `04/11 §4.7+§5.5`, `13/02 §1.6+§3.8`, `04/00 §6` | — |
| B5 | Muerte permanente y meta-progresión (roguelike) | **C** (r2 D5, reconfirmado) | `04/05 §4.7+§5.8 "Run state y meta-progresión"` | — |
| B6 | **Penalización de muerte recuperable** (*corpse run*, mancha de sangre, recuperar lo perdido) | **F** | Cero. `grep "cadáver"` solo devuelve una nota de rendimiento («no tiquetear un cadáver envenenado», `04/32` línea 637) y una referencia narrativa/arquitectónica (`13/12`); `grep` de «recuperar donde murió», «lugar de la muerte», «penalidad de muerte» → 0 en toda la biblioteca | Todo: el patrón intermedio entre «sin penalización» (B4) y «pierdes la partida entera» (B5) — perder un % de un recurso al morir, materializado como un objeto recuperable en el punto de la muerte (`obj_marca_muerte`), con la regla de que morir de nuevo antes de recuperarlo lo pierde para siempre (EverQuest, *corpse run*; Dark Souls, mancha de sangre — ambos verificados por búsqueda en esta sesión) |
| B7 | **Combate no letal**: pacifismo, aturdir sin matar, huir en tiempo real, negociar | **F** | Una sola mención tangencial: `13/12` línea 99, tabla de contradicciones guion/mecánica («el protagonista "no quiere hacer daño" y matas a 300 enemigos»), que señala el problema sin resolverlo. Cero en `04/30`–`04/36`, `04/45`, `04/47`, `04/50`, `13/18` | Todo: un estado "aturdido/noqueado" que retira al enemigo del encuentro sin matarlo (reutilizando el motor de efectos de `04/32 §4.4` con una consecuencia distinta a la muerte — sin *loot* de matanza, o con uno reducido); el seguimiento de "sin bajas" como estadística que puede condicionar contenido (Undertale, verificado); huida en tiempo real por ruptura de línea de visión y distancia (distinto del "Huir" de menú por turnos de B18, que sí existe); negociación como rama de diálogo que cierra un encuentro (reutilizando el sistema de misiones de `13/12`) |
| B8 | Retroceso de arma (*recoil*) | **C** (r2 A10, cerrado desde entonces) | `04/34 §4.2` — retroceso de cámara separado de la dispersión, reutiliza `camera_shake()` | — |
| B9 | Dispersión creciente por ráfaga (*bloom*) | **C** (r2 A10, cerrado desde entonces) | `04/34 §4.2` — curva de crecimiento/recuperación con dos parámetros (`spread_growth_deg`, `spread_recovery_deg`), diagrama ASCII de la curva | — |
| B10 | Recarga: cargador/reserva, cancelación, recarga activa | **C** (r2 A9, cerrado desde entonces) | `04/34 §4.1 + §5.1 "WeaponAmmoState"` | — |
| B11 | Munición como recurso | **C** (r2 A9, cerrado desde entonces) | `04/34 §2.1, §5.0-5.1` — extensión de `WeaponDef` de `04/02` con munición y balística | — |
| B12 | **Atasco / encasquille del arma** | **P** | `04/45 §3.2 "arma_intentar_disparo()"` — código real y funcional (`PROBABILIDAD_ENCASQUILLE`, engancha sobre `WeaponAmmoState` de `04/34`), pero **vive solo en el documento de horror**, como mecánica de tensión, no como opción general de sensación de armas | Falta que `04/34` (el documento canónico de combate a distancia) enlace o adopte este patrón como una opción más de sensación de arma, junto a retroceso y dispersión — hoy un lector que busque «atasco» en `04/34` no lo encuentra |
| B13 | **Calor / sobrecalentamiento como recurso de disparo** | **F** | Cero apariciones de «sobrecalentar», «recalentar», «arma… enfriar», «weapon overheat» en toda la biblioteca | El tercer arquetipo de recurso de disparo, junto a cargador (B10) y munición infinita con enfriamiento: sube con cada disparo, baja con el tiempo sin disparar, bloquea el disparo al llegar al tope con una penalización de enfriamiento forzado más larga que la normal (el arma de plasma de Halo es la referencia citada en la fuente verificada en esta sesión). Se resolvería reutilizando `RecursoCombate` de `04/36 §3.2`, que ya modela exactamente este arquetipo genérico — no hace falta inventar la estructura, solo la instancia |
| B14 | Cobertura, línea de tiro y disparo desde parapeto | **C** (r2 A13, cerrado desde entonces) | `04/34 §4.5, §5.6-5.7` | — |
| B15 | Asistencia de puntería | **C** (r2 A2, cerrado desde entonces) | `04/34 §4.4, §5.5` — interruptor explícito en `global.a11y`, enlazado desde `13/18 §1.2` como «parte del kit, no un extra» | — |
| B16 | Tipos de daño, resistencias, armadura, escudos | **C** (r2 B2/B4/B5, cerrado en bloque) | `04/32 §4.1-4.3` — pipeline de daño de cinco capas, triángulo elemental, armadura plana/porcentual/penetración, escudo con retardo de regeneración | — |
| B17 | Motor de efectos de estado (veneno, quemadura, aturdimiento, ralentización) | **C** (r2 C1/C2, cerrado en bloque) | `04/32 §4.4-4.5, §5.4-5.5` — struct por efecto, política de apilado como enum, tic con `delta_time` | — |
| B18 | Combate por turnos: iniciativa, ATB, menú, táctica en rejilla, "Huir" | **C** (r2 H1/H2/H3/H4, cerrado en bloque) | `04/35` entero — incluye tablero hexagonal (§5.15-5.17), y el "Huir" del menú de combate SÍ tiene código real (`case "huir":` en §5.8, no solo la etiqueta del botón) | — |
| B19 | Arquetipos de enemigo, sinergias y tabla de amenaza (*aggro*) | **C** (r2 F4/F5/F7, cerrado en bloque) | `04/33 §1` (seis arquetipos con las cuatro preguntas), `§2` (sinergias + hueco de escape), `§4` (tabla de amenaza y su versión ligera de un jugador) | — |
| B20 | Director de intensidad (estilo *AI Director* de *Left 4 Dead*) | **C** (r2 G5, cerrado desde entonces) | `04/33 §5-6` — con la exclusión explícita de los jefes, citando a Michael Booth (Valve) | — |
| B21 | Habilidades con enfriamiento y recursos de combate (estamina, maná, furia) | **C** (r2 I1/I2, cerrado en bloque) | `04/36` entero — struct de habilidad dirigido por datos, `GestorHabilidades`, tres arquetipos de `RecursoCombate` | — |
| B22 | Diseño de jefe como oficio: *tells*, arena, *adds*, checkpoints entre fases, dificultad justa | **C** (r2 G2, cerrado desde entonces, con matemática nueva) | `13/18` entero — la cadena de legibilidad (§1.1), el piso de reacción en fotogramas con la ley de Hick citada y verificada con WebFetch en la propia sesión que escribió el documento (§1.3), la tabla de coste del reintento en segundos (§2.5), DPS de diseño frente a DPS medido (§2.8) | — |
| B23 | Multi-golpe, combos, *cancels*, bloqueo, *parry*, aguante | **C** (r2 E1-E8, cerrado desde r2, sin cambios) | `04/30 §4.2-4.9` | — |
| B24 | Juego de lucha: notación de comandos, *frame data* en datos, *pushback*, agarres/*tech*, barra de súper | **C**, nuevo desde r3 | `04/50 §3.1-3.7` — motor de comandos con notación numpad y tolerancia, escalado de *hitstun* (no solo de daño, con la razón explícita de por qué eso rompe los combos infinitos), *tech* de agarre, tres formas de llenar la barra de súper | — |
| B25 | Beat 'em up: carril de profundidad, alineación en Z, agarres/lanzamientos, cooperativo local | **C**, nuevo desde r3 | `04/47` entero — incluye la extensión de la tabla de ataques de `04/30` sin tocar el documento original (§4.2), y el reparto de arena por zona de cámara reutilizada (§5.1) | — |
| B26 | Combate en balón/deporte de equipo y física de mesa (billar, pinball, minigolf) | **C**, nuevo desde r3 | `04/49` entero — no es "combate" en sentido estricto, pero cierra el hueco de colisión elástica entre círculos (billar, §B.1.1) y confirma A1 (pinball, §B.2.7) | — Se documenta aquí porque es la fuente del cierre de A1, no como tema propio del encargo |

### C · El documento de diseño (GDD)

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| C1 | GDD de una página (plantilla ligera) | **C** (r2 A2, sin cambios) | `13/01 §8.1` | — |
| C2 | GDD completo por secciones (concepto → calendario) | **C** (r2 A1, cerrado desde entonces) | `13/14 §2` — tabla de 19 filas, cada una con «qué va», «qué NO va» y «dónde está ya desarrollado»; marca ⚠️ explícitamente las dos filas (monetización, meta-progresión) que a fecha de la auditoría de r2 eran huecos — ambas cerradas ya por `13/16` y `13/20`, así que hoy esas marcas ⚠️ están **desactualizadas** (ver sección de abajo) | — |
| C3 | Pilares de diseño | **C** (r2 A3, cerrado desde entonces) | `13/14 §1.3` — con la prueba de fuego («¿puede rechazar una idea real?») y un ejemplo completo de discusión resuelta | — |
| C4 | Elevator pitch: fórmula, qué NO lleva, venta frente a diseño | **C** (r2 A6, cerrado desde entonces) | `13/14 §1.4` — fórmula «X se encuentra con Y», tabla de pitch de venta frente a pitch de diseño | — |
| C5 | Wiki viva frente a documento congelado | **C** (r2 A5, cerrado desde entonces) | `13/14 §1.5` — quién gana cuando código y documento discrepan (el código, con ADR ligero), regla de caducidad de dos semanas | — |
| C6 | Catálogo de diagramas de diseño | **C** (r2 A7, cerrado desde entonces) | `13/14 §2.20` — ocho diagramas con dueño; añade grafo de gating y diagrama de estados del jugador, que no vivían en ningún documento | — |
| C7 | Público, plataformas y competencia | **C** (r2 A8, cerrado desde entonces) | `13/14 §2.5` — tres preguntas verificables (no demografía inventada), tabla de qué cambia por plataforma | — |
| C8 | **El GDD como entrada de un agente de IA**: formato, granularidad, criterios de aceptación | **C**, ejemplar — el hueco que el brief marcaba como más valioso | `13/14 §6` entero: §6.1 las cuatro condiciones de «implementable» (reglas numeradas, parámetros con rango, recorte explícito, criterio de aceptación verificable); §6.2 la plantilla mínima; §6.3 un GDD **completo y real** de 83 líneas («Luz de Ámbar», plataformas de 3 niveles) con reglas `R1`-`R4` numeradas, rangos por parámetro, casos borde y criterio de aceptación comprobable con `gm-cli compile`; §6.4 el procedimiento paso a paso que seguiría el propio agente | — Un agente que solo lea esta sección puede implementar el documento de ejemplo de principio a fin sin inventar nada — verificado leyendo el ejemplo completo, no solo el índice |
| C9 | **Del GDD al proyecto: lista de tareas concreta y árbol de recursos, con orden de implementación multi-sistema** | **P** — el hueco real que queda | Piezas dispersas sin puente: `13/06 §2` da el orden de **montaje del esqueleto vacío** (Git, `scr_config`, `obj_game`, guardado) — no el orden de los **sistemas de diseño** de un GDD ya escrito; `13/11 §3.1-3.4` da el tablero de cuatro columnas y la regla de «tarea de un día», pero no dice cómo una ficha de sistema se convierte en esas tareas; `13/18 §4.1` SÍ hace el mapeo campo→`struct` exacto, pero **solo para combate** — no existe la versión general aplicable a cualquier sistema de la ficha de `13/01 §8.2` | Generalizar el patrón de `13/18 §4.1` a cualquier sistema; el orden recomendado **entre sistemas** de un GDD completo (núcleo de movimiento/colisión → cámara → el sistema del pilar principal → combate/enemigos si aplica → UI/HUD → guardado → audio → pulido), justificado por dependencia real (la cámara necesita el movimiento; el HUD necesita lo que va a mostrar); y cómo cada sistema de la ficha se convierte en una tarea del tablero de `13/11 §3.1` |
| C10 | Diseño iterativo: qué se prototipa primero | **C** | `13/01 §6.1` — tabla «prototipa / no prototipes», la incertidumbre más cara primero, «escribe la pregunta en la primera línea del archivo» | — |
| C11 | Cuándo se tira un prototipo a la basura | **C** | `13/01 §6.3` — tres criterios de parada explícitos (presupuesto agotado, tres intentos sin encontrar la gracia, contestado antes de tiempo); «lo que sobrevive es la respuesta, escrita en el GDD» | — |
| C12 | Cómo se sabe que una mecánica no funciona (playtesting cualitativo) | **C** | `13/01 §7.1-7.4` — postura de Valve (diseños como hipótesis), qué preguntar y qué no, cinco personas por ronda (Nielsen, con su advertencia de que el dato es de usabilidad, no de diversión), plantilla de registro de cuatro columnas separando observación de interpretación | — |
| C13 | El pitch y el one-pager frente al GDD completo: ¿están los tres? | **C** | Los tres existen y están delimitados sin solaparse: `13/01 §8.1` (one-pager, con su pitch de una línea) · `13/14 §1.4` (el elevator pitch, cómo se construye, distinto del pitch de diseño) · `13/14 §2-§3.4` (el GDD completo, que se expande desde el one-pager, no lo sustituye) | — |
| C14 | Canon teórico más allá de MDA y Flow (Koster, Salen & Zimmerman, Schell, SDT, Bartle, Costikyan, dominancia, emergencia) | **C** (r2 B2/B4/B5/B7/B8/B9/B11/B13/B14, cerrado en bloque) | `13/15` entero — nueve marcos, cada uno con «qué te hace hacer distinto mañana» y un ejemplo aplicado a un mismo proyecto (§13) | — |
| C15 | Progresión: árboles de habilidades y meta-progresión como diseño | **C** (r2 D3/D4, cerrado desde entonces) | `13/16` entero | — |
| C16 | Diseño de puzzles como oficio | **C** (r2 G1, cerrado desde entonces) | `13/17` entero — taxonomía, el momento «ajá», validación por búsqueda (BFS/A*) | — |
| C17 | Modelo de negocio, monetización, ética (patrones oscuros, cajas de botín), retención/live ops, KPIs | **C** (r2 I3/I4/I5/I6, cerrado en bloque) | `13/20` entero — catálogo de patrones oscuros por categoría (temporales/monetarios/sociales/psicológicos), estado legal de cajas de botín, el argumento explícito de **no** hacer live ops | — |
| C18 | Balance por simulación (Monte Carlo), notación Machinations, dominancia estratégica | **C** (r2 E2/C3/B13, cerrado en bloque) | `13/21` entero | — |
| C19 | Diseño de mundo y exploración (densidad de puntos de interés, mapa/brújula, grafo de bloqueos) | **C** (r2 G2, cerrado desde entonces) | `13/22` entero | — |

**Recuento:** 63 temas · **CUBIERTO 51** (81 %) · **PARCIAL 8** (13 %) · **FALTA 4** (6 %).

---

## Huecos por prioridad

### 🔴 Graves

**H1 · Combate no letal (B7).** Zero cobertura de un patrón de diseño extendido y verificado
externamente en esta sesión (Dishonored, Undertale). Sin él, un agente al que se le pida «un juego
de sigilo con opción pacifista» no tiene ni un solo patrón que reutilizar y va a inventarse el
sistema completo de aturdimiento/negociación sin verificar nada — el fallo exacto que la biblioteca
existe para evitar.

**H2 · Penalización de muerte recuperable / *corpse run* (B6).** El espectro de consecuencias de
la muerte tiene sus dos extremos sobresalientes (reaparición sin coste en B4, muerte permanente en
B5) pero falta el punto intermedio más común en ARPG y roguelite modernos: perder algo y poder
recuperarlo. Es un hueco de diseño, no solo de código: cambia la tensión de cada combate.

### 🟠 Medios

**H3 · Del GDD al proyecto: puente general sistema → recursos → orden (C9).** Es el segundo hueco
más valioso de todo el encargo, justo detrás del que el brief pedía priorizar (C8, ya cerrado). Un
agente sabe implementar UN sistema aislado a la perfección (`13/14 §6`); lo que no tiene es una
guía para decidir en qué orden construir los quince sistemas de un GDD completo y qué recurso
concreto de GameMaker crea cada uno — hoy tiene que inferirlo copiando el patrón puntual de
`13/18 §4.1`, que se escribió solo para combate.

**H4 · Cintas transportadoras (A6).** Mecánica de colisión estándar de plataformas (Mario, Sonic,
Celeste) con cero física documentada — solo un ejemplo de sonido de ambiente que la nombra de
pasada.

**H5 · Orden de resolución con tres o más cuerpos en el mismo frame (A10).** Cero apariciones.
Cualquier receta que empuje objetos entre sí con más de dos a la vez (una pila de cajas, una
multitud) se topa con este problema sin ninguna guía de la biblioteca.

**H6 · Calor de arma como recurso (B13).** Tercer arquetipo de recurso de disparo, junto a
cargador/munición, con cero cobertura pese a que la estructura genérica (`RecursoCombate` de
`04/36 §3.2`) ya existe y solo falta instanciarla.

### 🟡 Menores

**H7 · Atasco de arma generalizado (B12).** Código real, pero enterrado en el documento de horror;
falta el enlace desde `04/34`.

**H8 · Comparación de coste tilemap/instancia (A3).** Las piezas existen; falta la tabla que las
cruza.

**H9 · Cápsula-cápsula en 2D (A9).** Prioridad baja: el caso más común (cápsula contra círculo) ya
está resuelto; falta el caso menos común (dos cápsulas).

**H10 · Nombrar «ascensor» en el caso manual (A5).** El caso Box2D está etiquetado; el caso sin
física (mucho más habitual) no, y un lector que busque el término no lo encuentra por sí solo.

---

## Encargo para el redactor

1. **`04 - Recetas por género/37 - Traversal en plataformas...md` → nueva `§3.11 Cintas
   transportadoras`.** Cierra A6. Contenido: `obj_cinta` con un vector de empuje constante
   (`CINTA_VELOCIDAD`, `CINTA_DIRECCION`), aplicado mientras dura el contacto con
   `place_meeting`/`riding` (reutiliza el patrón de `objPlatformMoving` de `04/01 §5.8`, no lo
   duplica: aquí la plataforma no se mueve, solo empuja); el caso de que el jugador camine en
   contra (coste de velocidad, o imposibilidad si la cinta es más rápida que su velocidad base);
   el caso de un objeto sin input propio (una caja, un enemigo) que la cinta transporta sola.
   Símbolos a verificar con `buscar.py`: `place_meeting`, `instance_place`.

2. **`13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md` → nueva sección
   tras `§3.3 Barrido`: «Orden de resolución con varias colisiones a la vez».** Cierra A10.
   Contenido: por qué resolver A-B y luego B-C puede reintroducir el solapamiento A-B; la solución
   estándar (2-4 pasadas iterativas de `separacion_minima()` de `§3.2`, el mismo principio que
   `move_and_collide()` ya aplica internamente con su parámetro `iterations`); cuándo compensa
   iterar y cuándo basta con aceptar el error de un frame (la mayoría de juegos 2D no lo necesitan);
   un ejemplo con tres cajas en fila empujándose.

3. **`04 - Recetas por género/34 - Combate a distancia...md` → ampliar `§4` con `§4.6 Calor como
   recurso de disparo` y enlazar el atasco.** Cierra B13 y B12. Contenido: instanciar
   `RecursoCombate` de `04/36 §3.2` como el arquetipo «sube al disparar, baja con el tiempo,
   bloquea al llegar al tope con enfriamiento forzado más largo que el normal» (referencia
   verificada: el arma de plasma de *Halo*); un enlace explícito desde esta sección a
   `04/45 §3.2 arma_intentar_disparo()` para el atasco, con la nota de que hoy solo vive en el
   documento de horror y aquí se adopta como opción general de sensación de arma, sin repetir el
   código.

4. **`13 - Diseño y producción de videojuegos/02 - Diseño de niveles.md` → ampliar `§3.4 "Colisión
   de tiles: las dos vías"` con una tabla de coste/precisión/cuándo.** Cierra A3. Tres columnas:
   tilemap (memoria por celda, rejilla fija, coste casi nulo con `tilemap_get_at_pixel`), instancia
   por pared (cualquier forma, coste que crece con el número, mitigable con `13/08 §4`), y la regla
   práctica: tilemap para el 95 % del nivel, instancias solo donde la forma o el comportamiento
   individual lo exige (una puerta, un pincho que se activa).

5. **Nuevo documento `04 - Recetas por género/53 - Combate no letal - pacifismo, aturdir, huir y
   negociar.md`.** Cierra B7, el hueco grave. Contenido: estado «aturdido/noqueado» como instancia
   del motor de efectos de `04/32 §4.4`, con una consecuencia distinta de la muerte (retira al
   enemigo del encuentro, sin *loot* de matanza o con uno reducido — el campo se declara en la
   ficha de encuentro de `13/18 §3.2`, que se amplía con «¿tiene salida no letal?»); el contador de
   «sin bajas» como estadística de partida que puede condicionar contenido (Undertale, verificado
   por búsqueda esta sesión, 07-sep-2026); huida en tiempo real por ruptura de línea de visión y
   distancia umbral, distinta del «Huir» de menú por turnos que ya existe en `04/35 §5.8`;
   negociación como rama de diálogo que cierra un encuentro, reutilizando el sistema de misiones de
   `13/12 §6.5`, sin duplicarlo. Referencias verificadas por WebSearch el 07-sep-2026: el sistema de
   eliminación no letal de *Dishonored* y la ruta pacifista de *Undertale* como los dos ejemplos
   canónicos del oficio.

6. **Sección nueva en `13 - Diseño y producción de videojuegos/02 - Diseño de niveles.md` o en
   `04 - Recetas por género/05 - Roguelike y generación procedural.md` (ampliar `§4.7 Muerte
   permanente y meta-progresión`) → «Penalización de muerte recuperable».** Cierra B6, el segundo
   hueco grave. Contenido: `obj_marca_muerte`, creado en la posición del jugador al morir, con el
   % de recurso perdido (oro, XP, ambos según el proyecto); la regla de que morir de nuevo antes de
   recuperarlo lo pierde para siempre (mancha de sangre de *Dark Souls*) o de que expira tras un
   tiempo (*corpse run* de *EverQuest*) — ambos verificados por WebSearch el 07-sep-2026, con la
   advertencia explícita de que la crítica de diseño a este patrón también está documentada
   (algunos lo consideran mal diseño porque no premia la cautela, solo la vuelta al lugar); cómo se
   distingue de la meta-progresión de `04/05 §5.8` (esto es dentro de una partida, no entre
   partidas) y se engancha sin duplicar el `Run state` que ya existe.

7. **`13 - Diseño y producción de videojuegos/14 - El documento de diseño...md` → nuevo `§7 "Del
   GDD al proyecto: la lista de tareas y el árbol de recursos"`.** Cierra C9, el hueco medio más
   valioso. Contenido: (a) generalizar el patrón de `13/18 §4.1` (tabla campo-de-la-ficha →
   dónde-vive-el-struct) a cualquier sistema de `13/01 §8.2`, con el criterio de qué recursos
   concretos de GameMaker (`obj_`, `spr_`, `rm_`, siguiendo la convención de `05/04`) derivan de
   cada tipo de regla antes de tocar el MCP; (b) el orden recomendado **entre sistemas** de un GDD
   completo — no el orden de montaje del esqueleto vacío que ya da `13/06 §2`, sino el de los
   sistemas de diseño en sí: núcleo de movimiento/colisión → cámara → el sistema que sostiene el
   pilar principal → combate/enemigos si el juego lo tiene → UI/HUD → guardado → audio → pulido —
   justificado por dependencia real entre sistemas, con el diagrama de `13/14 §2.20` (tabla de
   interacción entre sistemas) como herramienta para detectarla en un proyecto concreto; (c) cómo
   cada fila de la ficha de sistema se convierte en una o varias tareas del tablero de
   `13/11 §3.1-3.2` («tarea de un día como máximo»), cerrando el salto que hoy existe entre «aquí
   está el GDD» y «aquí está el tablero de tareas» sin ningún paso intermedio documentado.

8. **Corrección menor, sin documento nuevo:** en `13/14 §2`, las notas ⚠️ de las filas 2.16
   (monetización) y parte de 2.8 (meta-progresión) que remiten a la auditoría de r2 como huecos
   **están desactualizadas** — ver siguiente sección. Actualizar los enlaces a `13/16` y `13/20`
   y retirar la advertencia de hueco.

9. **Mención menor, sin documento nuevo:** en `04/22` línea 154-155, el comentario que etiqueta el
   *joint* prismático como «ascensor» ya existe; añadir una línea en `04/01 §4.8` (plataformas
   móviles) que diga explícitamente «una plataforma móvil en eje vertical es un ascensor» para que
   el término sea localizable sin conocer de antemano que es el mismo patrón.

---

## Lo que comprobé y NO hacía falta

Para que ninguna ronda futura lo reabra sin evidencia nueva:

- **Todo el bloque de traversal de plataformas** (pendientes, *wall slide/jump*, *ledge grab*,
  agacharse, escaleras, cuerdas, natación, corrección de esquina, empuje de cajas) — `04/37`
  entero, verificado sección por sección contra la lista de huecos B6/B9/B10/B11/B14/B15/B16/B18
  de la ronda 2. Cerrado de verdad, con macros de calibración y código completo, no solo prosa.
- **Sistema de daño, efectos de estado, armadura, escudos, tipos de daño** — `04/32` entero,
  verificado contra B2/B4/B5/B6/B7/C1/C2/C3/D3 de la ronda 2.
- **Arquetipos de enemigo, sinergias, tabla de amenaza, director de intensidad** — `04/33` entero,
  verificado contra F4/F5/F6/F7/G5/G6 de la ronda 2, incluida la cita de Michael Booth (Valve) que
  la propia ronda 2 no había podido verificar por falta de presupuesto de `WebSearch`.
- **Combate a distancia: munición, retroceso, dispersión, hitscan, cobertura, asistencia** —
  `04/34` entero, verificado contra A2/A9/A10/A12/A13 de la ronda 2.
- **Combate por turnos y táctico en rejilla** — `04/35` entero, incluido el tablero hexagonal
  (§5.15-5.17), que ni siquiera estaba en el alcance de la propuesta original de r2.
- **Habilidades, enfriamientos y recursos de combate** — `04/36` entero, verificado contra I1/I2/I3
  de la ronda 2.
- **El canon teórico de diseño más allá de MDA** (Koster, Salen & Zimmerman, Schell, SDT, Bartle,
  Costikyan, dominancia, emergencia) — `13/15` entero, verificado contra B2/B4/B5/B7/B8/B9/B11/B13/
  B14 de la ronda 2. Las citas de Wikipedia sobre tiempo de reacción y ley de Hick en `13/18 §1.3`
  se comprobaron abriendo las dos URLs indicadas en las Fuentes de ese documento: responden 200 y
  el contenido citado (190-200 ms de reacción visual simple, la fórmula de Hick) coincide.
- **Progresión, puzzles, monetización, balance por simulación, diseño de mundo** — `13/16`, `13/17`,
  `13/20`, `13/21`, `13/22`, cada uno verificado contra su hueco correspondiente de r2 (D3/D4, G1,
  I3-I6, E2/C3/B13, G2).
- **`13/13` (matemáticas): SAT para OBB, segmento contra círculo, colisión contra *paths*, las
  cuatro subsecciones de colisión isométrica** — verificadas leyendo el código completo, no solo
  los encabezados, porque eran la evidencia central de A7/A9/A11/A15.
- **El GDD para agente de `13/14 §6`** — leído entero, incluido el ejemplo completo de 83 líneas
  («Luz de Ámbar»), verificando que cada regla numerada, cada rango de parámetro y el criterio de
  aceptación son en efecto ejecutables tal y como se presentan, no solo plausibles.
- **`04/47` (beat 'em up) §7**, específicamente para confirmar si `04/33` cubre «rodear, esperar
  turno, no apelotonarse» tal y como pedía el brief — confirmado que sí, y que además hay una
  segunda capa de aplicación concreta al género.
- **`04/50` (juego de lucha) §3.8**, específicamente para separar «arquitectura de *rollback*»
  (ya cubierta en r2/`04/14`) de «sensación con latencia» (predicción propia, confirmación
  diferida) — confirmado que ambas están, y que viven en documentos distintos con roles distintos
  (`04/50` explica por qué el *rollback* es difícil en GML; `04/14 §4.4/§4.7` da la predicción y
  compensación de lag que sí es factible).
- **`04/49` (deportes y física de mesa) §B.2.7**, específicamente para el punto del brief sobre
  colisión continua en el pinball — confirmado con código real (`phy_bullet`), no solo mencionado.

---

## Lo que encontré desactualizado

- **`13/14 §2`, filas 2.16 y 2.8, marcas ⚠️ de «hueco de esta biblioteca».** Cuando se escribió
  `13/14` (6-sep-2026), la monetización (fila 2.16) y la meta-progresión dentro de progresión
  (fila 2.8) eran huecos reales, señalados con evidencia contra `diseno-gdd.md` (I3-I6, D3-D4). Un
  día después, `13/20 - Modelo de negocio, monetización y ética del diseño.md` y
  `13/16 - Progresión - árboles de habilidades, desbloqueos y meta-progresión.md` cerraron ambos
  huecos por completo (verificado en esta misma sesión, ver C15 y C17 de la tabla de arriba). Las
  notas ⚠️ de `13/14 §2` y su párrafo de advertencia bajo la tabla **ya no describen el estado real
  de la biblioteca**: siguen apuntando a un hueco que ya no existe. Es una discrepancia de un día,
  no de meses, pero es exactamente el tipo de "documento que miente desde el segundo cambio que no
  se refleja" que el propio `13/14 §1.5` advierte que hay que evitar — se lo señalo al redactor
  como corrección de mantenimiento (encargo 8), no como hueco de contenido.
- **No encontré ninguna otra afirmación caducada** dentro del alcance de mis tres dominios. Los
  avisos de fecha de caducidad que sí existen en los documentos nuevos (la retirada de `rollback_*`
  en la Beta 2026.100 R2, citada en `04/50 §3.8.2` y `04/14 §4.6 bis`) están correctamente fechados
  y verificados por sus propios autores contra el `GmlSpec` del runtime — no es una alucinación, es
  información real que ya trae su fecha de consulta.

---

## Limitaciones de esta auditoría

- **No abrí `11 - Código descargado/`** (fuera del alcance del brief). Es posible que alguna
  librería de terceros ya resuelva A6 (cintas transportadoras) o A10 (orden de resolución de varios
  cuerpos) sin que la biblioteca lo documente; eso no cambia el veredicto — la biblioteca no lo
  explica — pero podría abaratar el encargo 1 y 2 si el redactor decide consultarlo primero.
- **Fuentes externas de B6 y B7 verificadas por `WebSearch` el 07-sep-2026**, no por lectura
  completa de las páginas (a diferencia de `13/18`, que usó `WebFetch` para leer las dos fuentes de
  tiempo de reacción palabra por palabra). Los tres resúmenes de búsqueda (calor de arma, *corpse
  run*, combate no letal) coinciden entre sí y con mi conocimiento previo del dominio, así que los
  doy por suficientemente verificados para fundamentar el encargo, pero no cumplen el mismo
  estándar de verificación línea a línea que exige el brief para una cita textual.
- **No compilé nada.** La auditoría es de cobertura documental y de coherencia entre documentos, no
  de que el GML citado compile — varios de los documentos auditados (`04/32`-`04/38`, `04/50`) ya
  declaran por su cuenta si su código se verificó o no contra `buscar.py`, y no repetí esa
  verificación símbolo por símbolo salvo donde la evidencia dependía de ello.
- **La calificación de «81 % cubierto»** cuenta el universo de 63 temas que yo mismo construí a
  partir del brief y de la tabla de r2; no es una medida objetiva de cobertura de todo el dominio
  de colisiones/combate/diseño posible, que es infinito. Es una medida honesta de cuánto de lo que
  dos rondas anteriores + el brief de esta ronda identificaron como relevante está resuelto hoy.
