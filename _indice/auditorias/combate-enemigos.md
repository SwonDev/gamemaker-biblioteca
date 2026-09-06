# Auditoría de cobertura · Combate, enemigos, jefes y sistemas de daño

**Biblioteca auditada:** `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`
**Fecha:** 2026-09-06 · **Auditor:** agente de dominio «combate»
**Excluidos del barrido:** `Lumbre/`, `GameMaker_Fuentes/`, `09 - Manual oficial/`, `11 - Código descargado/`
**Contadas como existentes:** carpeta `13`, y recetas `04/28`–`04/31`.

---

## 0 · Resumen ejecutivo

La biblioteca está **muy fuerte en el combate cuerpo a cuerpo y en el «cómo se siente»**, y
**débil en el combate como sistema de datos**: no hay motor de efectos de estado, ni tipos de
daño con resistencias, ni escudos, ni un sistema de habilidades con enfriamiento, ni
arquetipos de enemigo, ni director de encuentros, ni combate táctico en rejilla, ni cartas.

De 50 temas canónicos:

| Estado | Nº | % |
|---|---|---|
| `CUBIERTO` | 23 | 46 % |
| `PARCIAL` | 14 | 28 % |
| `FALTA` | 13 | 26 % |

Las tres piezas que más rendimiento darían, por orden: **(1)** un documento de *sistema de daño
y efectos de estado*, **(2)** un documento de *diseño de enemigos, encuentros y director*, y
**(3)** un documento de *combate a distancia* que cierre munición/recarga/retroceso/hitscan/cobertura.

Dos observaciones de higiene, aparte del hueco de contenido:

- **Referencia cruzada falsa.** `04 · 30 §Ver también` dice que `04 · 04 — RPG / Action RPG`
  cubre «stats, **resistencias** y la decisión por turnos frente a acción». `04/04` no tiene
  resistencias: su `Stats` sólo tiene `attack`/`defense` y la mitigación es
  `max(1, daño − defensa*0.5)`. Conviene corregir el enlace o cubrir el hueco.
- **Lo mismo con «armadura».** `04/30 §4.7` documenta *poise*/super armor (armadura de
  aguante), pero **armadura como reducción de daño** (plana frente a porcentual, penetración)
  no está en ninguna parte.

---

## 1 · Tabla de cobertura

Rutas relativas a la raíz de la biblioteca. «Encabezado» es literal del documento.

### A · Combate a distancia, proyectiles y armas

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| A1 | Apuntado con ratón y con stick derecho (prioridad del último dispositivo) | `CUBIERTO` | `04 - Recetas por género/02 - Top-Down _ Twin-Stick.md` → §4.3 «Rotación hacia el ratón» y §5.2 bloque «5. Apuntado» (ratón + `gp_axisrx/ry`, zona muerta 0.3) | — | *Twin-stick* como género base; convención de Nuclear Throne / Enter the Gungeon |
| A2 | Asistencia de puntería (*aim assist*, imantado, corrección de ángulo) | `FALTA` | — | Todo. `grep` de «asistencia de puntería», «auto-aim», «imantado» → 0 resultados | Ver la charla de accesibilidad/asistencia en juegos de disparos (GDC, *Accessibility* track) y la práctica estándar en mandos ⚠ |
| A3 | Proyectil básico: creación, velocidad, vida, *culling* fuera de pantalla | `CUBIERTO` | `04/02 §5.4 objBullet (sin pool)`; `04/03 §4.5 Object pooling: obligatorio` (con *culling* en End Step) | — | Manual GameMaker (`instance_create_layer`) |
| A4 | *Object pooling* de balas | `CUBIERTO` | `04/02 §5.5 Object pooling de balas`; `04/03 §5.4 Pool de balas enemigas`; `06 - Assets y Scripts/scr_pool.gml` | — | Práctica estándar de *bullet hell* |
| A5 | Patrones de balas base: anillo, abanico, espiral (*danmaku*) | `CUBIERTO` | `04/03 §4.4 Patrones de balas (danmaku)` (tabla con fórmulas) + `§5.5 Patrones de balas` (código) | — | Convención del género; ZUN / Touhou como canon |
| A6 | *Bullet hell* avanzado: hueco de seguridad, patrón compuesto, bala que muta, retardo | `PARCIAL` | `04/03 §4.4` (menciona «la combinación temporizada») y `§7 Errores clásicos` («deja un hueco (gap) en el anillo») | El hueco se menciona como error clásico, no se implementa; faltan balas con cambio de comportamiento a mitad de vuelo, patrones anidados y curvas de bala | Práctica del género |
| A7 | *Grazing* (rozar balas suma puntos) | `FALTA` | Sólo citado en `04/03 §8 Cómo escalarlo` punto 4 como idea futura | Todo | Mecánica canónica de Touhou / DoDonPachi |
| A8 | Bombas / limpiapantallas y vidas-continues del shmup | `PARCIAL` | `04/03 §5.8 Jugador` tiene un «limpia balas cercanas (bomba de emergencia gratuita)»; `§6` gestiona vidas; `§8` propone el `objBomb` como escalado | El sistema de bomba como recurso (stock, invulnerabilidad durante, daño masivo, recuperación) no está | Convención del género |
| A9 | Munición: cargador, reserva y **recarga** (tiempo, cancelación, recarga activa) | `PARCIAL` | `04/02 §6 PlayerStateTopDown` → `ammo`, `has_ammo()`, `consume_ammo()`, `unlock()` | Sólo hay un contador plano por arma. No hay cargador vs reserva, ni estado de recarga, ni cancelación, ni recarga activa (*Gears of War*), ni HUD de recarga | *Designing Games*, Sylvester — la recarga como «ritmo impuesto»; convención de shooters |
| A10 | Retroceso (*recoil*) y dispersión creciente por ráfaga (*bloom*) | `PARCIAL` | `04/02 §5.0 WeaponDef` → `spread_deg` fijo + `get_angles()`; `§5.3 Disparar` empuja al jugador con `weapon.knockback * 0.3` | La dispersión es constante: no crece al mantener el gatillo ni se recupera al soltar. No hay retroceso de cámara ni *kick* del arma | Práctica estándar de shooters (patrón de retroceso aprendible) |
| A11 | Proyectil teledirigido (*homing*) con giro limitado y predicción | `CUBIERTO` | `13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md` → §9.4 «Misil teledirigido: girar limitado + avanzar» (con predicción de intercepción y tabla de palancas de diseño); `04/08 §5.4 Proyectil con homing` | — | Trigonometría de persecución; convención de juegos de misiles |
| A12 | *Hitscan* instantáneo con `collision_line` (trazador, penetración, caída por distancia) | `PARCIAL` | `04/08 §4.5 Proyectiles vs hitscan` (tabla conceptual, 8 líneas); `13/13 §6.8 collision_line: cuándo basta y cuándo no` (los tres límites de la función y sus alternativas) | Ninguna receta de arma hitscan: falta el trazador dibujado, el impacto en pared, la penetración de varios objetivos (recorrer y ordenar por `u` menor) y la caída de daño por distancia | Manual GameMaker `collision_line`; convención de FPS/top-down |
| A13 | Cobertura (*cover*), líneas de tiro y disparo desde parapeto | `FALTA` | — | Todo. Las 15 coincidencias de «cobertura» son de *cobertura de tests*, *cobertura de mapa* o *cobertura periodística* | *Game AI Pro* — capítulos de *tactical position selection*; XCOM / Gears como canon |
| A14 | Armas dirigidas por datos: catálogo, cambio de arma, estadísticas | `CUBIERTO` | `04/02 §5.0 Definición de arma con structs` (`WeaponDef` + `global.weapons`) y `§6` (`unlocked`, `current_weapon`); `04/30 §4.10 Armas con alcance distinto` (el arma como **multiplicadores**, no como ataques nuevos) | Nota menor: no hay input ni HUD de cambio de arma, pero el modelo de datos está | Convención de diseño dirigido por datos |
| A15 | Torretas: selección de objetivo (*targeting*) y prioridades | `CUBIERTO` | `04/08 §4.4 Targeting de torres` (First/Last/Strongest/Closest) + `§5.3 Torre: targeting y disparo` | — | Convención del género TD |

### B · Sistema de daño

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| B1 | Aplicar daño y mitigar por defensa | `CUBIERTO` | `04/04 §5.0 Estadísticas` → `take_damage()` y `calcular_daño()` (`max(1, (atk − def*0.5) * random_range(0.90,1.10))`) | — | Fórmulas clásicas de JRPG |
| B2 | **Tipos de daño y resistencias / debilidades** | `FALTA` | Sólo dos menciones como trabajo futuro: `04/08 §8 Cómo escalarlo` punto 2 (`resistencias: { area: 0.5, hielo: 0 }`) y la referencia cruzada errónea de `04/30` | Todo: enum de tipos, tabla de multiplicadores, cómo se lee desde datos, cómo se comunica al jugador (color, icono, texto), inmunidad y absorción (curarse con un elemento) | *Designing Games*, Sylvester (cap. sobre decisiones significativas: el triángulo elemental como generador de decisiones); convención de RPG |
| B3 | Críticos: probabilidad, multiplicador y **piedad** (*pity* / PRD) | `CUBIERTO` | `13/13 §5.7 Crítico con piedad (pity)` — `critico_tirar()`, constantes verificadas contra Dota 2 (25 % → C=0,0847), aviso de que no hay fórmula cerrada, y `§5.8` para medirlo con histograma | Nota: falta el enlace desde una receta de combate; hoy vive sólo en el documento de matemáticas | Distribución pseudoaleatoria de Warcraft III / Dota 2 |
| B4 | Armadura como reducción (plana vs porcentual) y penetración | `FALTA` | — | Todo. `04/30 §4.7` es *poise*, no reducción de daño; `04/04` sólo tiene `defense` restada a medias | Fórmulas de reducción `armadura/(armadura+K)`; práctica de ARPG |
| B5 | Escudos: absorción, regeneración con retardo, *overshield* | `FALTA` | Sólo ideas sueltas: `04/03 §8` («escudo de 3 golpes»), `04/11 §8` («power-ups: imán, escudo») | Todo: capa de absorción delante de la vida, retardo antes de regenerar, ruptura y su feedback, barra dedicada | Halo (escudo recargable) como canon; *Designing Games* sobre bucles de recuperación |
| B6 | Daño con el tiempo (DoT): tics, acumulación, fuente del daño | `FALTA` | — | Todo. `grep` «daño con el tiempo», «sangrado» (1 hit, sobre pixel art), «veneno» (ninguno es un sistema) | Convención de RPG/ARPG; *Game AI Pro* sobre la contabilidad de fuentes de daño |
| B7 | Curación, límites y sobrecuración | `PARCIAL` | `04/01 §6 PlayerStats.heal()` (`min(hp+n, hp_max)`); `04/04 §5.6` (poción en el menú de batalla); `13/01 §4` trata la economía de curación | Falta la curación como sistema: curación con el tiempo, curación por porcentaje, la decisión de diseño «cuándo se cura» (poción vs regeneración vs *estus*), y el temporizador de combate que la bloquea | *Designing Games*, Sylvester — la curación como regulador de tensión |
| B8 | Escalado de daño en combo y *hit stun deterioration* | `CUBIERTO` | `04/30 §4.8 Empuje, juggle y escalado de daño` (tabla de multiplicadores por número de golpe, `elevacion * power(0.75, juggles)`), con la cita literal del glosario de Infil | — | **The Fighting Game Glossary**, Infil — entradas *Damage Scaling*, *Hit Stun Deterioration*, *Juggle* (verificado alcanzable en esta sesión) |

### C · Efectos de estado

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| C1 | **Motor de efectos de estado**: pila, duración, refresco frente a apilado, tics, inmunidad, disipación | `FALTA` | Sólo un puntero externo: `12 - Utilidades e integraciones/06 - itch.io - assets, herramientas y jams.md` → «**Affliction — A Status System** · efectos de estado apilables con iconos autogenerados. Para venenos, quemaduras, buffs» | Todo el sistema en GML: struct por efecto, aplicación, política de apilado (renovar / apilar / máximo), tic independiente del framerate, limpieza al morir, serialización en el guardado | Convención de RPG/MOBA; *Designing Games* sobre estados legibles |
| C2 | Efectos concretos: veneno, quemadura, congelación, aturdimiento, ralentización | `PARCIAL` | Aturdimiento y congelación existen **como hitstun**: `04/30 §4.3 Hitstun, blockstun y ventaja` y `§4.7 Aguante`. Ralentización: `04/08` cita `objTowerFrost (ralentiza, no mata)` en la jerarquía, sin implementarla | Ninguno es un efecto con duración y pila; la ralentización del TD se nombra pero no se codifica | Infil (*Hit Stun*, *Stun*); convención de TD |
| C3 | Presentación de estados: iconos, contador de pilas, tinte, orden | `FALTA` | — | Todo. `13/05` cubre botón, barra, tooltip, inventario, minimapa, toasts — no la fila de estados | *The Design of Everyday Things* aplicado a HUD; convención de MMO/ARPG |

### D · Vida, muerte, invulnerabilidad y feedback

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| D1 | Barra de vida del jugador (fantasma, temblor, accesible) | `CUBIERTO` | `13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md` → §3.5 b) «Barra de vida con retardo (la barra "fantasma")» — `barra_nueva/fijar/actualizar/dibujar`, suavizado independiente de fps, respeta `reduce_motion`, y la nota sobre `draw_healthbar` (amount 0-100) | — | Convención de HUD; el «daño diferido» de los juegos de lucha |
| D2 | Barra de vida sobre el enemigo | `PARCIAL` | `04/08 §5.5 Enemigo siguiendo un path` dibuja una «Barra de vida encima»; `04/15 §5.3` tiene una «Barra de vida que baja suave» | Es un `draw_rectangle` ad hoc por receta. Falta la decisión de diseño (cuándo mostrarla, ocultarla a vida llena, desvanecerla) y una versión reutilizable | `13/05 §1.7 Carga cognitiva` da el criterio, no se aplica a esto |
| D3 | **Barra de jefe con fases / segmentos y nombre** | `FALTA` | — | Todo. `grep "barra de jefe"` → 0. El jefe de `04/03 §5.7` tiene `hp/hp_max` y umbrales, pero nada dibuja la barra segmentada | Convención de jefes (Monster Hunter, Hollow Knight, Cuphead); GDC ⚠ sobre lectura de fases |
| D4 | Muerte del jugador, respawn y puntos de control | `CUBIERTO` | `04/01 §6 PlayerStats` → `invuln_time`, `set_spawn()`, `deaths`; `04/11 §4.7 Muerte legible` + `§5.5 Muerte y reinicio instantáneo` (congelar, cámara lenta, explosión, resaltar al asesino, reinicio); `13/02 §1.6 Puntos de control, respawn y distancia entre retos` + `§3.8 Puntos de control con guardado`; `04/00 §6 Muerte, Game Over y endgame` | — | *Designing Games* sobre coste del fracaso; Dan Taylor, «Ten Principles for Good Level Design» (citado ya en `13/02 §1.7`) |
| D5 | Muerte permanente y meta-progresión | `CUBIERTO` | `04/05 §4.7 Muerte permanente y meta-progresión` + `§5.8 Run state y meta-progresión` | — | Convención roguelike/roguelite |
| D6 | Invulnerabilidad e *i-frames* | `CUBIERTO` | `04/30 §4.5 I-frames y esquiva` (**quitar la hurtbox, no ignorar el daño**; arranque vulnerable de 2 frames); `04/01 §6` (`invuln_time = 60`); `04/02 §5.1`; `04/03 §6` | — | Infil — *Invincible*, *Strike Invincible*, *Throw Invincible* |
| D7 | *Hit stun*, *blockstun*, ventaja de fotogramas | `CUBIERTO` | `04/30 §4.3 Hitstun, blockstun y ventaja` + `§1.2 El vocabulario mínimo: frame data` | — | **The Fighting Game Glossary**, Infil; **Dustloop Wiki — Glossary** (ambas citadas en `04/30 §9 Fuentes`) |
| D8 | *Knockback* / empuje | `CUBIERTO` | `04/15 §4.5 Knockback` + `§5.4 Knockback` (`apply_knockback()` con `hitstun` y `knockback_decay`); `04/30 §4.8` remite ahí explícitamente («No lo repitas») | — | Infil — *Pushback* |
| D9 | Feedback de golpe: *hit stop*, sacudida, flash, texto flotante, partículas | `CUBIERTO` | `04/15` entero: `§4.2 Hit stop / freeze frames`, `§5.0 Sistema de tiempo`, `§5.1 Cámara con shake por trauma`, `§5.6 Flash de impacto y texto flotante`, `§5.7 El "golpe completo": una función que lo junta todo` (`hit_complete()`) | — | Steve Swink, *Game Feel*; Jan Willem Nijman, «The art of screenshake» ⚠ |
| D10 | Anticipación y recuperación del ataque enemigo (*telegrafía*) | `CUBIERTO` | `04/15 §4.8 Anticipación y recuperación` + `§5.8 Anticipación en un ataque enemigo`; `04/30 §5.12 El enemigo mínimo: patrulla → telegrafía → ataque → recuperación` | — | Los 12 principios de animación (anticipación); Infil — *Startup*, *Recovery* |

### E · Combate cuerpo a cuerpo

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| E1 | Hitbox / hurtbox / pushbox y *frame data* | `CUBIERTO` | `04/30 §1.1 Tres cajas, no una`, `§1.2 El vocabulario mínimo: frame data`, `§5.2 Las fases del ataque`, `§5.3 obj_hitbox` | — | Infil (*Hitbox*, *Hurtbox*, *Frame Data*); Dustloop; **HitBoxes_gml** de MichelVGameMaker |
| E2 | Multi-golpe y lista de «ya golpeados» (*rehurt timing*) | `CUBIERTO` | `04/30 §4.2 Multi-hit y la lista de ya golpeados` | — | `set_rehurt_timing()` de HitBoxes_gml (citado en `04/30 §9`) |
| E3 | Combos, *cancels* y buffer de entrada | `CUBIERTO` | `04/30 §4.4 Cancels y combos por cadena de estados` + `§5.8 El jugador: combos, cancels y buffer`; `06 - Assets y Scripts/scr_input_buffer.gml` | — | Infil — *Cancel*, *Hit Confirm*, *Buffer*, *Frame Trap* |
| E4 | Bloqueo (direccional) y *parry* | `CUBIERTO` | `04/30 §4.6 Bloqueo y parry` (tabla ventana/efecto/riesgo + la nota de que el bloqueo debe ser direccional) + `§5.9 El parry, en cuatro líneas` | — | Infil — *Parry*, *Block*, *Counter Hit* |
| E5 | Esquiva (*dodge roll*) con ventana de i-frames | `CUBIERTO` | `04/30 §4.5 I-frames y esquiva` (arranque 2 / i-frames 10 / recuperación 8) | — | Convención Souls / Gungeon |
| E6 | Aguante (*poise* / super armor) | `CUBIERTO` | `04/30 §4.7 Aguante (poise / super armor)` | — | Infil — *Armor* |
| E7 | Selección de objetivo en cono para el ataque melé | `CUBIERTO` | `04/30 §4.9 Selección de objetivo en cono` (`point_direction` + `angle_difference` + `point_distance`); base matemática en `13/13 §2.4 Cono de visión, con el ángulo de verdad` | — | Práctica de action games con orientación libre |
| E8 | Dos arquitecturas de hitbox (instancia frente a datos) | `CUBIERTO` | `04/30 §2.2 Las dos arquitecturas posibles (y cuál elegir)` + `§5.11 La arquitectura B: sin instancias` | — | Comparación propia de la biblioteca, con criterio explícito |

### F · Diseño e IA de enemigos

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| F1 | *Steering*: seek, flee, arrive, wander, evasión, patrulla, *flocking* | `CUBIERTO` | `04 - Recetas por género/23 - IA de enemigos y steering behaviors.md` entero (§1–§6) | — | Craig Reynolds, «Steering Behaviors for Autonomous Characters»; *Game AI Pro* |
| F2 | IA de decisión: FSM, árbol de comportamiento, utility, GOAP | `CUBIERTO` | `04/31` entero: `§2 El árbol mínimo`, `§3 La pizarra (blackboard)`, `§4 Decoradores`, `§8 Utility AI mínimo`, `§10 GOAP en 40 líneas honestas`, `§12 Rendimiento`; `06/scr_state_machine.gml` | — | **Game AI Pro** (capítulos de BT, utility y GOAP); Jeff Orkin, *Three States and a Plan* (F.E.A.R.) |
| F3 | Percepción: ver, oír, recordar, avisar al grupo | `CUBIERTO` | `04/31 §11 Percepción: ver, oír, recordar y avisar` (cono + `collision_line`, ruido por señal, memoria de última posición, `alerta_grupo` filtrada por distancia **y** línea de visión) | — | *Game AI Pro* — *sensory systems*; F.E.A.R. / Splinter Cell como canon |
| F4 | **Arquetipos de enemigo** (rusher, ranged, tank, swarm, sniper, support) y sus roles | `PARCIAL` | Lo más cercano: `04/23 §Qué comportamiento para qué enemigo` (7 filas: zombi lento, guardia, enemigo a distancia, fantasma, murciélagos, animal inofensivo) — es una tabla de **movimiento**, no de rol de combate | Faltan los arquetipos como vocabulario de diseño: qué presión aplica cada uno, qué obliga a hacer al jugador, cómo se contrarresta, qué pasa cuando se combinan, y una tabla de estadísticas de partida (vida en «golpes», TTK objetivo, alcance, telegrafía) | GDC 2018, «Embracing Push-Forward Combat in DOOM», Jake Campbell (id Software) ⚠ · Dead Cells / Motion Twin sobre diseño de enemigos ⚠ · *Game AI Pro* |
| F5 | Composición de encuentros y sinergias entre arquetipos | `FALTA` | — | Todo: cómo se combinan tres arquetipos, la regla de «un enemigo que empuja + uno que ancla», la lectura del espacio | GDC — *Doom 2016 combat loop*, *Halo combat encounters* ⚠ |
| F6 | **Coordinación de grupo: sistema de fichas de ataque** (que no ataquen todos a la vez) | `FALTA` | Lo único parecido es la propagación de alerta de `04/31 §11`, que **comparte información** pero no reparte turnos de ataque | Todo: el gestor que concede N fichas, la cola de espera, el enemigo que rodea mientras no la tiene, el tiempo mínimo entre ataques del grupo | **Game AI Pro** — *squad coordination* / *attack tokens*; Halo y los *Arkham* como canon ⚠ |
| F7 | *Aggro* / amenaza / tabla de odio | `FALTA` en la biblioteca en español | Sólo aparece en `03 - Cursos (YouTube)/08 - Curso 2026 - Sky LaRell Anderson - Parte 8 - Enemigos y Vida.md` como `aggro_distance` (distancia de detección, no amenaza) — y la carpeta `03` está fuera del alcance del barrido y marcada como fuente de menor autoridad | Todo: amenaza acumulada por daño/curación, decaimiento, *taunt*, cambio de objetivo, y su versión ligera para un juego de un solo jugador | Convención de MMO/RPG táctico; *Game AI Pro* sobre selección de objetivo |
| F8 | Presupuesto de IA: no todos los enemigos, no cada frame | `CUBIERTO` | `04/31 §12 Rendimiento: no todos los enemigos, no cada frame` | — | *Game AI Pro* — *LOD de IA* |
| F9 | Sigilo: detección progresiva, ruido, luz, última posición conocida | `PARCIAL` | `04/31 §11` da percepción, memoria y alerta; `13/13 §2.4` y `§9.5` dan cono y campo de visión con rayos | Falta el sigilo como **sistema del jugador**: medidor de detección progresivo (sospecha → alerta → combate) con su UI, escondites, distracciones, ejecuciones por la espalda, y el indicador de «última posición conocida» que el jugador ve | Splinter Cell / Mark of the Ninja como canon; *Game AI Pro* — *stealth systems* ⚠ |

### G · Jefes, oleadas y encuentros

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| G1 | Jefe con fases por umbral de vida y patrones | `CUBIERTO` | `04/03 §4.6 Jefes con máquina de estados` + `§5.7 Jefe con fases` (tres fases con `hp_threshold`, `on_enter`/`on_update`, transición con invulnerabilidad breve) | — | Convención de shmup; estructura de `BossPhase` |
| G2 | **Diseño de jefe como oficio**: *tells*, arena, *adds*, checkpoints, dificultad justa | `PARCIAL` | Piezas sueltas: `13/01 §4.4` da el TTK de jefe («40–150 s repartidos en 2-4 fases»); `04/00 §4` exige que toda cinemática sea saltable «para el jugador que reintenta un jefe»; `13/02 §1.6` da checkpoints | No hay ninguna sección que trate el jefe como pieza de diseño: qué enseña cada fase, cómo se lee un *tell*, cómo se usa la arena, cuándo meter *adds*, el checkpoint entre fases, la regla de «el jugador debe poder ver por qué murió» | Hollow Knight / Team Cherry sobre jefes ⚠ · *Designing Games*, Sylvester (cap. sobre desafío y flujo) · GDC — *Cuphead* boss design ⚠ |
| G3 | Oleadas dirigidas por datos | `CUBIERTO` | `04/03 §4.2 Oleadas dirigidas por datos`, `§5.2 Definición de oleadas`, `§5.3 objWaveDirector`; `04/08 §4.7 Oleadas desde datos` + `§5.8 Oleadas desde structs`; `04/11 §5.2 Spawner con patrones por nivel` | — | «El error clásico es escribir las oleadas en código» — criterio propio, alineado con la práctica de la industria |
| G4 | *Spawners* en el mundo y salas que se cierran | `CUBIERTO` | `13/02 §3.7 Spawners: enemigos que aparecen cuando toca`; `04/02 §8` describe la sala que se cierra y suelta oleadas (estructura de Gungeon) | — | Convención de *arena rooms* |
| G5 | **Director de intensidad (estilo AI Director de Left 4 Dead)** | `FALTA` | — | Todo. `grep` «director de intensidad», «AI Director», «Left 4 Dead» (en contexto de IA) → 0 resultados útiles | Michael Booth (Valve), «The AI Systems of *Left 4 Dead*» ⚠ · GDC 2009, «Replayable Cooperative Game Design: *Left 4 Dead*» ⚠ |
| G6 | *Pacing* de combate: tensión y descanso | `PARCIAL` | `13/02 §1.2 Ritmo (pacing): tensión y descanso` (a nivel de **nivel**); `13/01 §3.1 Flow` y `§3.3 Dificultad dinámica: las dos familias` | Falta bajarlo al encuentro: la curva de intensidad dentro de una arena, el respiro tras el pico, la relación con el director de G5 | *Designing Games*, Sylvester (cap. *Pacing*); Csíkszentmihályi (flow), ya citado en `13/01` |
| G7 | Dificultad dinámica (DDA) y sus dos familias | `CUBIERTO` | `13/01 §3.3 Dificultad dinámica: las dos familias, y cuál elegir` | — | Literatura de DDA; ya citada en el documento |

### H · Combate por turnos, táctico y cartas

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| H1 | Bucle de combate por turnos con máquina de estados | `PARCIAL` | `04/04 §4.4 Combate por turnos vs acción` + `§5.6 Combate por turnos` (enum `BattleState`, menú Atacar/Objeto/Defender/Huir, encolado de acciones enemigas, victoria/derrota con XP) | Es el mínimo viable: ataca siempre a `enemigos[0]`, no hay **selección de objetivo**, ni habilidades/hechizos (el `mp` existe en `Stats` pero nada lo gasta), ni efectos de estado en combate, ni dibujo del menú, ni animaciones de acción | Convención JRPG; *Designing Games* sobre decisiones significativas |
| H2 | **Iniciativa / orden de turnos / ATB** | `FALTA` | — | Todo. `grep "iniciativa"` → 0 resultados en toda la biblioteca | Convención JRPG (ATB de Final Fantasy) y de RPG de mesa; *Game AI Pro* sobre planificación por turnos |
| H3 | Menú de batalla estilo JRPG (dibujo, foco, submenús, objetivos) | `PARCIAL` | `04/04 §5.6` navega un índice; `13/05 §2.2 Navegación con mando y teclado: foco, orden, envolvente y repetición` y `§3.5 a) Botón, con sus cuatro estados` dan la mecánica de UI reutilizable; `04/18 - Menús con scroll y navegación` da la navegación | Falta juntarlo: el menú de batalla concreto (comando → submenú → objetivo → confirmación), el cursor sobre el enemigo, el retroceso con B | `13/05` es la base correcta; nadie la aplica al combate |
| H4 | **Táctica por rejilla (SRPG): movimiento, alcance, línea de tiro, terreno** | `FALTA` | Sólo se nombra como subgénero: `04/04 §1` tabla → «Táctico por turnos · Por turnos en grid · Final Fantasy Tactics». Las piezas sueltas existen (`04/08 §4.1 Grid y coordenadas`, `04/05 §5.6 Campo de visión por raycasting`, `13/13 §7 Rejillas y coordenadas`, `06/scr_grid_pathfinding.gml`) | Todo el sistema: rango de movimiento por coste (Dijkstra/BFS con puntos de acción), resaltado de casillas, rango de ataque y línea de tiro, bonus por terreno y altura, orden de turnos por unidad, IA táctica de posicionamiento | *Game AI Pro* — *tactical position selection* y *influence maps*; Fire Emblem / Into the Breach como canon |
| H5 | Táctica en tiempo real: selección, órdenes, niebla de guerra, IA por utilidad | `CUBIERTO` | `04 - Recetas por género/13 - Estrategia y gestión.md` → `§5.0 Selección`, `§5.1 Órdenes`, `§5.2 Unidad ejecutando órdenes`, `§5.4 Niebla de guerra`, `§5.5 IA estratégica por utilidad` | — | Convención RTS; utility AI de *Game AI Pro* |
| H6 | **Deckbuilding / juego de cartas**: mazo, mano, descarte, efectos por datos | `FALTA` | Sólo un puntero externo: `12/06` → «**Facet — A Card Framework** · lógica de mazo y mano con caras de carta generadas por procedimiento» | Todo: barajar (ya hay Fisher-Yates en `04/05 §5.0` y `array_shuffle` en `01/05`), robar/jugar/descartar/agotar, energía por turno, efecto de carta como dato + intención del enemigo, pila de resolución | Slay the Spire como canon ⚠; *Designing Games*, Sylvester (combinatoria) |

### I · Habilidades, progresión, balance y depuración

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| I1 | **Habilidades con enfriamiento**: gestor, cargas, enfriamiento global, coste de recurso | `PARCIAL` | Enfriamientos ad hoc por receta: `04/02 §5.1` (`fire_cooldown`), `04/08 §5.3` (torre), `04/03`, `04/13`; `04/31 §4 Decoradores: Inversor y Enfriamiento` (enfriamiento **de nodo de IA**, reutilizable como idea) | Falta el sistema: struct de habilidad (coste, enfriamiento, cargas, casteo, interrupción), gestor por entidad, enfriamiento global, y el coste en recurso — porque **estamina no existe** (`grep "estamina"` → 0) y `mp` existe en `04/04 §5.0` sin que nada lo gaste | Convención de ARPG/MOBA; *Designing Games* sobre recursos como reguladores |
| I2 | Recursos de combate: estamina, maná, furia, munición como recurso | `PARCIAL` | `04/04 §5.0` declara `mp`/`mp_max`; `04/02 §6` gestiona munición; `13/01 §4 Economía y balance` da el marco (fuentes, sumideros, realimentación) | Estamina no existe en ninguna parte; no hay ningún recurso de combate que se regenere y limite acciones (la esquiva sin coste es la mitad de un sistema Souls) | *Designing Games*, Sylvester — cap. de economía |
| I3 | **Árbol de habilidades / progresión de combate** | `FALTA` | Menciones sin sistema: `04/06 §4.2 Habilidades desbloqueables` son **llaves permanentes** (doble salto, dash), no ramas con coste; `13/05 §1.1` (tabla «¿Qué hago ahora?») y `§1.7` citan el árbol de habilidades como ejemplo de pantalla diferida y de revelación progresiva | Todo: nodos con prerrequisitos y coste, puntos de habilidad, respec, serialización, y su pantalla | Convención de ARPG; *Designing Games* sobre progresión |
| I4 | Subida de nivel y curva de experiencia | `CUBIERTO` | `04/04 §4.2 Curvas de experiencia` + `§5.1 Niveles y curva de experiencia`; `13/13 §8 Curvas de crecimiento para diseño` (§8.1–§8.4, incluida la inversión de la curva) | — | Curvas de crecimiento clásicas |
| I5 | Estadísticas con modificadores y equipo | `CUBIERTO` | `04/04 §4.1 Stats con modificadores` + `§5.0 Estadísticas` (`base` + `mods` + `get_equip_bonus`, `refresh()` que conserva la proporción de vida) | — | Patrón estándar de RPG |
| I6 | **Balance de combate: TTK, DPS y tablas** | `CUBIERTO` (con un matiz) | `13/01 §4.4 Balance por fórmulas, con números` → «Daño frente a vida: el TTK (*time to kill*)» con fórmula, tabla de cuatro enemigos, heurísticas por situación (y el aviso de que son reglas de oficio, no fuente primaria) y «Balancear en múltiplos, no en absolutos»; `§4.5 De la hoja de cálculo al juego`; `§9.3 Datos de balance en Included Files`; `§9.4 Balance en caliente con el Debug Overlay` | Matiz: **DPS** como métrica no aparece con ese nombre; para un juego con cadencias distintas y DoT hace falta. Es una fila de tabla, no un documento | *Designing Games*, Sylvester; práctica de balance por hoja de cálculo |
| I7 | Depuración: dibujar hitboxes y hurtboxes | `CUBIERTO` | `04/30 §5.10 Dibujar las cajas (depuración)` — convención de color de la comunidad de lucha (rojo hitbox, verde hurtbox, azul máscara, amarillo invulnerable), condicionado por `DEPURAR_CAJAS` o `is_debug_overlay_open()` | — | Convención de la comunidad de juegos de lucha |
| I8 | Depuración: **registro de daño y DPS medido** | `PARCIAL` | La infraestructura genérica existe: `13/01 §9.5 Telemetría: contar muertes por sala y volcarlas a JSON` (`telemetria_registrar`) y `§9.4` (Debug Overlay); `13/10 §7.2 Un log con niveles que sobrevive al cierre` | Falta la especialización de combate: registrar cada golpe (fuente, tipo, bruto, mitigado, crítico), el desglose por fuente, el TTK observado frente al de diseño, y el *overlay* que lo enseña en partida | Práctica de QA de combate; `13/10 §10.2 Qué medir` da el marco |
| I9 | Determinismo del combate y pruebas | `CUBIERTO` | `13/10 §2.2 Inyecta lo que no controlas: azar, reloj y entrada`, `§5.3 Determinismo`, `§3.1 El script scr_pruebas`; `04/05 §5.0 Generador aleatorio propio` | — | Pirámide de pruebas adaptada; GM-TestFramework |
| I10 | Combate en red: rollback y determinismo | `CUBIERTO` | `04/14 - Multijugador.md` (referenciado desde `04/30 §Ver también` como «rollback y determinismo») | Fuera del núcleo de este dominio, pero existe | GGPO / rollback netcode |

---

## 2 · Propuestas priorizadas

Sólo para `PARCIAL` y `FALTA`. Se agrupan deliberadamente: cuatro documentos nuevos y cuatro
secciones dentro de documentos existentes, en vez de veinte fragmentos.

### 🔴 Alta

**P1 · `04 - Recetas por género/32 - Sistema de daño y efectos de estado.md`**
Cubre B2, B4, B5, B6, B7, C1, C2, C3 y D3.
El paquete de datos que hoy no existe: enum de tipos de daño y tabla de resistencias leída de
JSON; armadura plana frente a porcentual y penetración; escudo como capa de absorción con
retardo de regeneración y feedback de ruptura; motor de efectos de estado (struct por efecto,
política de apilado *renovar / apilar / máximo*, tic independiente del framerate con
`delta_time`, inmunidad, disipación, limpieza al morir, serialización en el guardado); veneno,
quemadura, congelación, aturdimiento y ralentización como instancias de ese motor; la fila de
iconos con contador de pilas y la barra de jefe segmentada por fases.
Debe **enlazar y no repetir**: críticos → `13/13 §5.7`; empuje e hitstun → `04/15 §5.4` y
`04/30 §4.3`; barra fantasma → `13/05 §3.5 b)`. Y corregir de paso la referencia cruzada falsa
de `04/30 §Ver también` sobre «resistencias» en `04/04`.

**P2 · `04 - Recetas por género/33 - Diseño de enemigos, encuentros y director de combate.md`**
Cubre F4, F5, F6, F7, G3 (consolidación), G5 y G6.
Los seis arquetipos con su ficha (presión que aplican, qué obligan a hacer, contrapartida,
vida en «golpes», TTK objetivo, alcance, fotogramas de telegrafía) y la tabla de sinergias.
El **gestor de fichas de ataque**: N fichas por grupo, cola de espera, el enemigo sin ficha
rodea o se reposiciona, tiempo mínimo entre ataques del grupo. La **tabla de amenaza**
(*aggro*): acumulación por daño y curación, decaimiento, *taunt*, cambio de objetivo, y su
versión ligera de un solo jugador. El **director de intensidad**: estimación de la tensión
actual, estados *acumular → pico → respiro → calma*, presupuesto de spawn por estado, y su
acoplamiento con las tablas de oleadas que ya existen en `04/03 §5.2` y `04/08 §5.8`.
Enlaza a `04/23` y `04/31` para el movimiento y la decisión: aquí sólo va el **grupo**.

**P3 · `04 - Recetas por género/34 - Combate a distancia - armas, munición y balística.md`**
Cubre A2, A9, A10, A12 y A13.
Cargador y reserva con estado de recarga (arranque, punto de recarga efectiva, recuperación,
cancelación y recarga activa) y su HUD; retroceso de arma y de cámara, y dispersión que crece
al mantener el gatillo y se recupera al soltar, con la curva expuesta como dato; **arma
hitscan** con `collision_line` respetando los tres límites que ya documenta `13/13 §6.8`
(recorrer y ordenar por `u` menor para penetración, muestreo contra tilemap, trazador dibujado,
impacto en pared, caída de daño por distancia); asistencia de puntería (imantado por cono y
corrección de ángulo) con su interruptor de accesibilidad, enlazando a `04/27`; y cobertura:
marcar parapetos, comprobar línea de tiro y la IA que los usa.
Extiende el `WeaponDef` de `04/02 §5.0` en vez de crear otro: es el mismo struct con más campos.

### 🟠 Media

**P4 · `04 - Recetas por género/35 - Combate por turnos y táctico en rejilla.md`**
Cubre H1 (lo que falta), H2, H3 y H4.
Orden de turnos por iniciativa **y** ATB (barra que se llena por velocidad), con la cola visible;
selección de objetivo con cursor y validación de alcance; habilidades y hechizos con coste de MP
leídos de JSON, y su enganche con el motor de estados de P1; el menú de batalla completo
(comando → submenú → objetivo → confirmación → retroceso) construido sobre la navegación de
`13/05 §2.2`. Y la mitad táctica: rango de movimiento por coste con BFS/Dijkstra sobre la rejilla
de `13/13 §7`, resaltado de casillas, alcance de ataque y línea de tiro, bonus de terreno y
altura, e IA de posicionamiento por utilidad reutilizando `04/31 §8`.
Sustituye a `04/04 §5.6` como referencia y deja allí un enlace: no se duplica el `BattleManager`.

**P5 · `13 - Diseño y producción de videojuegos/14 - Diseño de combate y de jefes.md`**
Cubre G2, G6 y el matiz de I6. **Es el documento de oficio, no de código**: la frontera con P2
es explícita — P2 implementa, P5 decide.
Qué hace legible un encuentro; el vocabulario del *tell* (anticipación visible, sonido propio,
duración mínima en fotogramas según el tiempo de reacción humano); la arena como parte del jefe;
cuándo meter *adds* y cuándo son ruido; el checkpoint entre fases y por qué reintentar debe
costar segundos, no minutos; la regla de que el jugador debe poder reconstruir por qué murió;
y la hoja de balance de combate con DPS junto al TTK que ya está en `13/01 §4.4`.

**P6 · `04 - Recetas por género/36 - Habilidades, enfriamientos y progresión de combate.md`**
Cubre I1, I2 e I3.
Struct de habilidad dirigido por datos (coste, enfriamiento, cargas, tiempo de casteo,
interrupción, objetivo válido); gestor por entidad con enfriamiento global; recursos de combate
—estamina que se gasta al esquivar y se regenera con retardo, maná, furia que sube al golpear—
enganchados a la economía de `13/01 §4`; la barra de acción con barrido radial y contador de
cargas, construida sobre `13/05 §3.5`; y el árbol de habilidades como grafo de nodos con
prerrequisitos, coste, *respec* y serialización, distinguiéndolo explícitamente de las
habilidades-llave de `04/06 §4.2`, que son otra cosa.

**P7 · Sección nueva en `04 - Recetas por género/31 - IA de decisión...md` → «§14 · Sigilo: detección progresiva y lo que el jugador ve»**
Cubre F9. No merece documento propio: la percepción ya está resuelta en `§11`.
Medidor de detección con tres tramos (tranquilo → sospecha → combate), su velocidad de subida
según distancia, luz y movimiento, y su decaimiento; el indicador que ve el jugador (el
triángulo que se llena, el «último visto»); escondites y distracciones como señales de `04/16`;
y la ejecución por la espalda como caso de `04/30`.

### 🟢 Baja

**P8 · Secciones nuevas en `04 - Recetas por género/03 - Shoot em up (shmup).md` → «§5.9 Bombas y *grazing*» y «§4.7 Patrones con hueco de seguridad»**
Cubre A6, A7 y A8, que hoy sólo viven en `§8 Cómo escalarlo`.
La bomba como recurso (stock, invulnerabilidad mientras dura, limpieza de balas con conversión
a puntos, recuperación); el *grazing* con su radio secundario, su contador y su recompensa; y el
patrón de anillo con hueco garantizado más la bala que cambia de velocidad o dirección a mitad
de vuelo.

**P9 · Secciones nuevas en `13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md` → «§3.5 j) Barra de vida de enemigo y de jefe»**
Cubre D2 y parte de D3.
La barra sobre la cabeza reutilizando `barra_*` de `§3.5 b)`: cuándo aparece, cuándo se
desvanece, por qué no se dibuja a vida llena, cómo se ancla al sprite y se mantiene legible con
zoom; y la barra de jefe segmentada por fases con nombre y contador de fase.
Hoy cada receta la redibuja a mano (`04/08 §5.5`, `04/15 §5.3`).

**P10 · Sección nueva en `04 - Recetas por género/30 - Combate cuerpo a cuerpo...md` → «§5.13 El registro de daño: medir lo que de verdad pasa»**
Cubre I8.
Anotar cada golpe (origen, objetivo, ataque, tipo, bruto, mitigado, crítico, estados aplicados)
sobre `telemetria_registrar()` de `13/01 §9.5`; el desglose por fuente y el DPS medido; el TTK
observado frente al de diseño de `13/01 §4.4`; y el panel del Debug Overlay que lo enseña sin
salir del juego.

---

## 3 · Limitaciones de esta auditoría

1. **Sin WebSearch.** La sesión agotó su presupuesto de búsquedas web (200/200) antes de que yo
   pudiera verificar una sola URL. Las fuentes externas marcadas con **⚠** están citadas de
   memoria por título, autor y año: **no he confirmado en esta sesión que la ponencia exista con
   ese título exacto ni que la URL resuelva**. Afecta a las charlas de GDC citadas para F4, F5,
   F6, G2, G5, H6 e I-varios.
2. **GDC Vault no es rastreable con `curl`.** Probé `gdcvault.com/search.php` con
   `-A "Mozilla/5.0"`: la búsqueda es JavaScript y devuelve la página vacía. Los tres
   identificadores `play/<id>` que probé a ciegas resolvieron a charlas distintas de las
   buscadas, así que **no incluyo ninguna URL de GDC Vault**. Lo que sí verifiqué en vivo:
   `https://glossary.infil.net/` responde 200 con `<title>The Fighting Game Glossary |
   infil.net</title>`, lo que respalda las citas de Infil que ya usa `04/30`.
3. **No abrí el manual oficial espejado.** El dominio de combate es de diseño y arquitectura,
   no de API: las funciones implicadas (`collision_line`, `collision_rectangle`,
   `point_direction`, `angle_difference`, `draw_healthbar`, `instance_create_layer`) ya están
   verificadas dentro de los documentos auditados, con enlace al manual. No re-verifiqué
   símbolo por símbolo con `buscar.py`.
4. **Carpetas excluidas por el brief.** `03 - Cursos (YouTube)`, `09 - Manual oficial` y
   `11 - Código descargado` quedaron fuera del `grep` canónico. Lo señalo porque hay un caso con
   consecuencias: **`aggro` (F7) existe en `03/08`** como `aggro_distance` — es distancia de
   detección, no amenaza, y la carpeta `03` está marcada como fuente de menor autoridad en
   `AGENTS.md §1.bis`, así que mantengo el `FALTA`. Si el criterio del proyecto fuera contar la
   carpeta `03`, ese tema pasaría a `PARCIAL`.
5. **Juicio de profundidad, no ejecución.** Abrí y leí íntegras las secciones de código de
   `04/02`, `04/03`, `04/04`, `04/08`, `04/15`, `04/23`, `04/30`, `04/31`, `13/01`, `13/05` y
   `13/13` que clasifico. **No compilé nada**: la clasificación juzga la completitud del
   contenido, no que el GML corra. `04/30` avisa por su cuenta de que su código no se ha
   compilado.
6. **Ambigüedad léxica del `grep`.** Varios recuentos brutos engañan y los desglosé a mano:
   «buff» (71) es casi todo `buffer`; «pila» (91) es casi todo `compila`; «cobertura» (15) no
   tiene ni una sola aparición con el sentido de parapeto de combate; «carta» (37) es sobre todo
   `cartas de ajuste`, `descarte de assets` y nombres propios, no juego de cartas.
