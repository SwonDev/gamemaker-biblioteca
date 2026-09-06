# Auditoría de cobertura · Feedback, game feel, UI/UX, onboarding y accesibilidad

**Dominio auditado:** feedback y *game feel*, feedback de UI, feedback de progreso y de fracaso,
onboarding y tutorial, transiciones y carga, HUD y pantallas, entrada multi-dispositivo, texto,
accesibilidad y UX de sistema (guardado, errores, telemetría, *quality of life*).

**Biblioteca auditada:** `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`
(carpetas 01, 02, 04, 05, 06, 07, 08, 10, 12, 13 + `RUTA.md`; excluidos `Lumbre/`,
`GameMaker_Fuentes/`, `09 - Manual oficial/` salvo consulta puntual y `11 - Código descargado/`).

**Método:** `python3 _indice/buscar.py --texto/--listar`, `grep -rli` con ~90 términos en español
e inglés, y **apertura y lectura directa** de los documentos que salieron en los resultados para
juzgar profundidad (no solo presencia). Contraste externo con Game Accessibility Guidelines
(lista completa), Steam Deck Verified (Steamworks), Xbox Accessibility Guidelines (citadas ya
dentro de la biblioteca), Swink *Game Feel*, «Juice it or lose it» (Nijman/Jonasson), Vlambeer
*The art of screenshake*, Hodent *The Gamer's Brain*, Fagerholt & Lorentzon *Beyond the HUD*.

---

## Veredicto de conjunto

**Este dominio es, con diferencia, el mejor cubierto de la biblioteca.** Dos documentos hacen casi
todo el trabajo y lo hacen a nivel profesional:

- `13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md` — **1 832 líneas**, con la
  taxonomía diegética original de seis categorías (no la simplificación de cuatro que circula),
  cifras de las Xbox Accessibility Guidelines, las cinco leyes del foco, detección del último
  dispositivo usado con heurística de familia de mando, y **nueve componentes con código
  completo** (botón de cuatro estados, barra fantasma, texto flotante, tooltip, inventario con
  arrastrar y soltar, diálogo, minimapa con *surface*, marcador con temblor, *toasts*).
- `04 - Recetas por género/15 - Game feel y juice.md` — **1 208 líneas**, con *screen shake* por
  trauma al cuadrado, *hit stop*, *time scale*, *squash & stretch*, *knockback*, partículas,
  flash, texto flotante y el «golpe completo» que lo junta todo.

De **55 temas canónicos**, **34 están CUBIERTOS con código verificado**, **12 PARCIALES** y
**9 FALTAN**. Los huecos reales no están en el *game feel* de combate —eso está resuelto— sino en
**cuatro sitios concretos**:

1. **Accesibilidad** (137 líneas frente a un dominio que tiene 100+ pautas canónicas).
2. **El tutorial como sistema en GML** (el diseño está; el código no).
3. **Transiciones, carga real y menú de pausa** (existe el fundido a negro y poco más).
4. **La celebración y el fracaso** (el juego sabe hacer daño; no sabe premiar ni consolar).

---

## 1 · Tabla completa

Leyenda: ✅ CUBIERTO · 🟡 PARCIAL · ❌ FALTA

### A · Game feel y respuesta al jugador

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| A1 | Respuesta al input y latencia percibida | 🟡 | `13/05 §1.5 Feedback inmediato` (el umbral de 100 ms) · `04/01 §7 Errores clásicos` (leer input en Begin Step) | Medir el retardo real, coste de *vsync* y `display_reset`, animación que no debe bloquear la respuesta, la regla de Swink sobre fotogramas de retardo | Swink, *Game Feel*, cap. «Real-time control» |
| A2 | Coyote time | ✅ | `04/01 §4.3 Coyote time` · `06 - Assets y Scripts/scr_input_buffer.gml` (`CoyoteTime`) | — | «Juice it or lose it» · práctica estándar de plataformas |
| A3 | Input buffering (salto y ataque) | ✅ | `04/01 §4.4 Jump buffering` · `scr_input_buffer.gml` (`InputBuffer`) · `04/30` (buffer de ataque) | — | Ídem |
| A4 | Aceleración, fricción y «peso» del movimiento | ✅ | `04/01 §4.1 Movimiento horizontal: aceleración y fricción` | — | Swink, *Game Feel* |
| A5 | Salto variable por altura del botón | ✅ | `04/01 §4.5 Salto variable` (con el «❌ regular / ✅ mejor») | — | Ídem |
| A6 | Anticipación, acción y recuperación (*telegraph*) | ✅ | `04/15 §4.8` y `§5.8 Anticipación en un ataque enemigo` · `13/04 §1.3-1.4` | — | 12 principios de animación · Vlambeer |
| A7 | Screen shake con trauma² | ✅ | `04/15 §4.1 Screen shake` (tres niveles, cita a Squirrel Eiserloh) y `§5.1 Cámara con shake por trauma` | — | Vlambeer, *The art of screenshake* |
| A8 | Hit stop / *freeze frames* | ✅ | `04/15 §4.2` y `§5.0 Sistema de tiempo` (con el motivo de ponerlo en Begin Step) | — | Ídem · *Katana ZERO* |
| A9 | Slow motion / *time scale* / tiempo bala | ✅ | `04/15 §5.0` (`time_slow(_escala, _duracion)` con vuelta suave a 1) | — | «Juice it or lose it» |
| A10 | Squash & stretch | ✅ | `04/15 §4.3` y `§5.3 Squash & stretch reusable` (+ el aviso del origen *Bottom Centre*) | — | Ídem |
| A11 | Knockback y *hitstun* | ✅ | `04/15 §4.5` y `§5.4 Knockback` · `04/30` | — | Vlambeer |
| A12 | Flash blanco de impacto | ✅ | `04/15 §5.6 Flash de impacto y texto flotante` (+ shader de flash en `§8.2`) | — | «Juice it or lose it» |
| A13 | Partículas de impacto | ✅ | `04/15 §4.6` y `§5.5 Partículas nativas` · `02/05 Sistema de partículas nuevo` | — | Ídem |
| A14 | Sonido en capas con *pitch* aleatorio | ✅ | `04/15 §4.7 Feedback audiovisual en capas` (regla de los tres canales) · `13/09` | — | Vlambeer |
| A15 | Texto flotante de daño | ✅ | `04/15 §5.6` · `13/05 §3.5c Texto flotante de daño` (el que vive en el mundo y se lee en la GUI) | — | «Juice it or lose it» |
| A16 | Easing y *tweening* | ✅ | `04/15 §4.4` y `§5.2 Tween helper con structs` · `06 - Assets y Scripts/scr_tween.gml` | — | Swink |
| A17 | Cámara: *deadzone*, *look-ahead*, suavizado, límites | ✅ | `06 - Assets y Scripts/scr_camera.gml` (`cam_set_deadzone`, `cam_set_lookahead`) · `04/01 §End Step` | — | Itay Keren, *Scroll Back* (GDC) |
| A18 | Cámara: *zoom punch* y retroceso cinemático | 🟡 | `04/15 §8.3 Cámara cinemática` — citado como idea de una línea | `scr_camera.gml` **no tiene zoom**; no hay código de *punch* ni de retroceso al disparar | Vlambeer · *Nuclear Throne* |
| A19 | Estela por *afterimage* de sprite | ✅ | `04/06` (rastro del dash, `objAfterimage`) · `04/11 §7 Rastro` (array de posiciones con vida) | — | «Juice it or lose it» |
| A20 | **Estela de cinta con `draw_primitive` / vertex buffer** (trail de espada) | ❌ | Solo `04/15 §8.5` como bullet de una línea. `08/02` y `08/07` no la traen | Toda la técnica: dos puntos por fotograma, `pr_trianglestrip`, UV a lo largo de la cinta, atenuación por edad | Técnica estándar de acción 2D · Vlambeer |
| A21 | *Impact frames* / *smear frames* | ✅ | `13/04 §1.4 Un ataque con smear` (tabla de subimágenes) y `§ tabla de fps por tipo de efecto` | — | 12 principios · Saint11 |
| A22 | ***Permanence***: decals persistentes en *surface* | ❌ | Solo la mención «sangre que mancha» en `04/15 §4.6` | Acumular sangre, casquillos, quemaduras y cadáveres en una *surface* del tamaño de la sala, con el patrón de recreación tras `surface_exists()` falso y el presupuesto de memoria | «Juice it or lose it» (Nijman/Jonasson) lo nombra explícitamente como *permanence* |
| A23 | Aberración cromática y post-FX de impacto | 🟡 | `04/15 §9 Fuentes` cita *Post-Processing FX* de FoxyOfJungle · `07/04` lo menciona | No hay receta propia ni shader; solo la recomendación de la extensión | Vlambeer · práctica común |
| A24 | Vibración del mando como capa de feedback | 🟡 | `01/12 §4 Gamepad` lista `gamepad_set_vibration(slot, izq, der)` · `04/28 §8.2 Vibración` (móvil) | Diseño: intensidad por tipo de golpe, duración, curva de decaimiento, no vibrar en bucle, **y el toggle/slider obligatorio** | Game Accessibility Guidelines · Basic (motor): «Include toggle/slider for any haptics» |
| A25 | Presupuesto de juice: el juice es contraste | ✅ | `04/15 §8.7 Juice condicional` y `§7 Errores clásicos` (tabla de 13 fallos) | — | Vlambeer · Swink |

### B · Feedback de UI

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| B1 | Los cuatro estados de un control (normal/foco/pulsado/inactivo) | ✅ | `13/05 §1.5 Feedback inmediato: un control tiene cuatro estados, no dos` + `§3.5a) Botón, con sus cuatro estados` | — | Hodent, *The Gamer's Brain* · Nielsen |
| B2 | Sonido de UI: cuatro y solo cuatro, en el **cambio** de estado | ✅ | `13/05 §3.8 Juice de UI` (tabla `snd_ui_foco/aceptar/cancelar/error`) + `§5 Errores` («el sonido de menú es una metralleta») | — | Práctica de oficio · Game UI Database |
| B3 | *Tween* de paneles al entrar y salir | ✅ | `13/05 §3.8` (entrada 250-300 ms, **salida siempre más rápida**, nada por encima de 350 ms) · `scr_tween.gml` | — | Emil Kowalski / práctica de UI |
| B4 | Contadores que suben y tiemblan | ✅ | `13/05 §3.5h) Marcador y temporizador` (`marcador_nuevo/sumar/actualizar/dibujar`, con `reduce_motion`) | — | «Juice it or lose it» |
| B5 | Barra de vida con retardo (barra fantasma) | ✅ | `13/05 §3.5b) Barra de vida con retardo` | — | Ídem |
| B6 | Tooltips contextuales que no se salen de la pantalla | ✅ | `13/05 §3.5d) Tooltip: el que siempre se sale de la pantalla` | — | Game UI Database |
| B7 | Notificaciones apiladas (*toasts*) | ✅ | `13/05 §3.5i) Notificaciones apiladas (toasts)` | — | Ídem |
| B8 | Lienzo de GUI, anclas, nine-slice y escala | ✅ | `13/05 §3.2 El lienzo`, `§3.4 Paneles nine-slice` · `02/04 UI Layers y Flexpanels` | — | Manual GameMaker (Draw GUI) |
| B9 | Draw GUI a mano frente a UI Layers/Flexpanels | ✅ | `13/05 §3.1 Draw GUI a mano o UI Layers: la decisión` · `02/04` completo | — | Manual LTS 2026 |

### C · Feedback de progreso

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| C1 | Curvas de XP y de nivel (matemática) | ✅ | `04/04 §XP y niveles` · `13/13 §XP para subir de nivel: cuadrática` · `13/01 §4.4 Balance por fórmulas` | — | Schell, *The Art of Game Design* |
| C2 | **Celebración de recompensa** (subida de nivel, desbloqueo, fanfarria, confeti, pose de objeto conseguido, pantalla de resultados) | ❌ | `buscar.py --texto "celebración"` → **sin resultados**. `04/00 §6` solo trae créditos | Todo: la coreografía de una recompensa (parón, sonido ascendente, texto que entra con *ease out back*, pausa antes de devolver el control), la pantalla de resultados y el desbloqueo diferido | Hodent, *The Gamer's Brain* (bucles de recompensa) · «Juice it or lose it» |
| C3 | Logros: llamada a la plataforma | ✅ | `04/20 §1 Logros y estadísticas (Steam)` (con el aviso de que `steam_set_achievement` **no existe** con ese nombre en el runtime 2026) | — | Steamworks |
| C4 | Política del *toast* de logro (cuándo, cuánto, no tapar la acción) | 🟡 | El widget genérico existe (`13/05 §3.5i`); la política no está escrita | Qué logros se anuncian en pantalla y cuáles no, duración, cola, no solaparse con el HUD crítico | Xbox / PlayStation UX guidelines |

### D · Feedback negativo

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| D1 | Daño al jugador: i-frames, parpadeo, viñeta | ✅ | `04/30 §i-frames` · `04/02` y `04/03 §invulnerabilidad` · `04/15 §Draw GUI: flashes y viñeta` | — | Práctica de acción 2D |
| D2 | Muerte, Game Over y reintentar | ✅ | `04/00 §6 Muerte, Game Over y endgame` (`room_restart()`, «Reintentar / Menú») | — | — |
| D3 | **Fracaso sin humillar**: fricción de reintento, no castigar, autoguardado en el punto | ❌ | No hay sección. `13/01 §3.1 Flow` roza el tema desde la dificultad, no desde el fracaso | El coste del reintento en segundos, reaparecer donde estaba, no repetir cinemáticas, no culpar al jugador con el texto, el «casi lo tenías» | Diseño de *Celeste* y *Super Meat Boy* · Hodent (motivación) |

### E · Onboarding, tutorial y curva

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| E1 | Una idea nueva cada vez: presentar → ampliar → combinar → examinar | ✅ | `13/01 §5.1 La regla de «una idea nueva cada vez»` (con la lectura crítica de Mario 1-1, marcada como tal) | — | Lectura crítica de 1-1 · Hodent (3 elementos en memoria de trabajo) |
| E2 | Enseñar con el nivel: encuadre, camino único, demostración segura, repetición con variación, recompensa por curiosidad | ✅ | `13/01 §5.2 Las cinco herramientas para enseñar con el nivel` | — | GDC · diseño de niveles |
| E3 | *Gating* por progreso, en datos | ✅ | `13/01 §5.3 Gating` (`global.progreso` + `contenido_permitido()`) | — | — |
| E4 | El examen de los primeros 60 segundos | ✅ | `13/01 §5.4` (quién soy · qué puedo hacer · adónde voy · qué me mata) | — | Hodent |
| E5 | Curva de dificultad y *flow* | ✅ | `13/01 §3.1 Flow`, `§3.2 Las cuatro formas de curva`, `§3.4 Medir la dificultad con datos` | — | Csikszentmihalyi · Chen (2006), citado |
| E6 | Dificultad dinámica frente a asistencia explícita | ✅ (diseño) | `13/01 §3.3 Dificultad dinámica: las dos familias` (con el testimonio de Maddy Thorson sobre el modo asistido de *Celeste*) | Le falta el puente a la implementación → ver J8 | Chen · Celeste |
| E7 | **Sistema de tutorial en GML** | ❌ | No existe. `13/12 §3.6 Diálogo de sistema: el tutorial con voz de personaje` cubre el **tono**, no el sistema | Disparadores por zona, «mostrar una sola vez» persistido en el guardado, escalado de pistas tras N fallos, recordatorio de objetivo y de controles, saltar el tutorial, no repetirlo en New Game+ | Game Accessibility Guidelines · Cognitive Basic: «Include interactive tutorials»; Intermediate: «Indicate / allow reminder of controls / of current objectives during gameplay» |
| E8 | *Prompts* de botón contextuales por dispositivo | 🟡 | `13/05 §2.3` da `icono_boton(_accion)` y `marca_de_mando()` con la advertencia honesta de que es heurística | Falta el **widget** de prompt (icono + verbo, medido, con panel), que lea la asignación **real** tras el rebinding, y la política de cuándo desaparece (después de N usos) | Xbox Accessibility Guidelines · práctica de consola |
| E9 | La primera sesión / la primera hora (retención más allá del minuto 1) | 🟡 | `13/01 §5.4` cubre los 60 s; `13/10 §10.2` mide «momento del abandono» | El arco de la primera hora: cuándo llega la primera decisión, el primer desbloqueo, el primer fracaso barato | Hodent, *The Gamer's Brain* |

### F · Transiciones, carga y pausa

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| F1 | Fundido a negro entre salas | ✅ | `04/00 §2 El gestor de escenas` (`ir_a_escena()` + `obj_fundido`, con el aviso de que `transition_define` **no existe** en este runtime) | — | Manual GameMaker |
| F2 | **Repertorio de transiciones**: wipe, iris, cortinas, disolución por shader, barrido de píxeles | ❌ | `grep "wipe"` → cero. `04/03` menciona «cortina» en otro sentido | Las cinco o seis transiciones clásicas con código, la máquina de estados «salida → cambio → entrada», y cómo esconde la carga | Práctica de oficio · Game UI Database |
| F3 | **Pantalla de carga real** (asíncrona, con progreso que no miente) | 🟡 | `08/08 §texturegroup_get_status` trae el `switch` de estados y `texture_prefetch` · `12/02` cita la extensión de barra de carga para HTML5 | Falta la receta de UX: sala de carga dedicada, barra que refleja el progreso real, duración mínima para que no parpadee, consejos rotativos, y qué hacer si tarda más de lo previsto | Manual LTS 2026 (`texturegroup_load`) · Deck/consola |
| F4 | Pausa que congela el mundo | ✅ | `04/00 §5` (`instance_deactivate_all(true)` con la explicación del `true`, `audio_pause_all()`) | — | Manual GameMaker |
| F5 | **Menú de pausa completo** | 🟡 | El mapa de pantallas está en `13/05 §2.1` (Opciones única, salida visible, confirmación con «No» por defecto); la pausa técnica en `04/00 §5` | Falta la receta: reanudar / opciones / salir con confirmación, *ducking* o filtro de la música, oscurecer el fondo, momentos en que no se puede pausar, y volver al foco donde estaba | Game Accessibility Guidelines · práctica de certificación |

### G · Pantallas y componentes

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| G1 | HUD: jerarquía de tres niveles, taxonomía diegética, cuándo ocultarla | ✅ | `13/05 §1.1`, `§1.8 La HUD es game feel`, `§1.9 La taxonomía diegética` (seis categorías, con la corrección del mito de las cuatro), `§1.10 Cuándo ocultar la HUD` | — | Fagerholt & Lorentzon (2009), Chalmers/EA DICE — citada con PDF |
| G2 | Menús con scroll y navegación de listas | ✅ | `04/18` completo (datos, saltar inactivas, scroll, dibujar solo lo visible, barra) | — | — |
| G3 | Menú de opciones y persistencia de ajustes | ✅ | `04/25 §1-4` (widgets, aplicar en vivo, dibujar, guardar/cargar) | — | Game Accessibility Guidelines · General Basic: «Ensure that all settings are saved/remembered» |
| G4 | Inventario en cuadrícula con arrastrar y soltar | ✅ | `13/05 §3.5e) Inventario en cuadrícula con arrastrar y soltar` + `foco_rejilla()` en `§2.2` | — | Game UI Database |
| G5 | Caja de diálogo | ✅ | `13/05 §3.5f) Diálogo: la caja, no el texto` · `04/10 §4.2` (typewriter) · `13/12 §6` | — | — |
| G6 | Minimapa con *surface* y patrón «sucio» | ✅ | `13/05 §3.5g) Minimapa con surface` | — | — |
| G7 | **Pantalla de mapa completa** (zoom, marcadores, niebla, viaje rápido) | ❌ | `grep "pantalla de mapa"` y `"mapa completo"` → cero. Solo el minimapa y la niebla de guerra de estrategia (`04/13`) | La pantalla de mapa como modo: desplazamiento y zoom, marcadores del jugador, iconos de sala, salas visitadas frente a descubiertas, viaje rápido | Metroidvania de referencia · Game UI Database |
| G8 | **Tienda / UI de compra** | 🟡 | `04/04 §Tienda` (dos líneas: «reutiliza el inventario, dos `Inventory`») · `04/08`, `04/06` la citan de pasada | Precio y moneda visibles, estado «no te lo puedes permitir» (botón inactivo **con motivo**, según `13/05 §1.5`), confirmación de compra, comparación con lo equipado, vender | Game UI Database · práctica de RPG |
| G9 | Marcador, temporizador y HUD de puntuación | ✅ | `13/05 §3.5h` | — | — |

### H · Entrada multi-dispositivo

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| H1 | Manda el último dispositivo usado (ratón/teclado/mando) | ✅ | `13/05 §2.3 Ratón, táctil y mando a la vez` (`dispositivo_actualizar()`, cursor que aparece y desaparece) | — | Práctica de PC moderna |
| H2 | Glifos por familia de mando con `gamepad_get_description` | ✅ | `13/05 §2.3` (`marca_de_mando()`), **con el aviso explícito de que es heurística y no API**, y el reenvío a la librería Input | — | Manual GameMaker · librería Input (JujuAdams) |
| H3 | Foco: las cinco leyes, rejilla, envolvente, repetición 0,4 s + 0,1 s | ✅ | `13/05 §2.2 Navegación con mando y teclado` (`repeticion_paso()`, `foco_rejilla()`, tabla de envolvente por tipo de elemento) | — | Xbox Accessibility Guidelines · «Designing for TV» (Microsoft) |
| H4 | Táctil: tamaño mínimo, tres estados, joystick virtual, gestos | ✅ | `04/28 §5.1-5.4` · `01/12 §8bis Gestos táctiles` · `13/05 §2.3` (≈9 mm ≈ 90-100 px de GUI) | — | Guías de iOS/Android |
| H5 | Teclado virtual del sistema (móvil) | ✅ | `01/12 §8bis Teclado virtual` (`keyboard_virtual_*`) · `04/28 §5.5` | — | Manual GameMaker |
| H6 | Zonas seguras: *notch* de móvil y *overscan* de TV | ✅ | `13/05 §3.3 Zonas seguras` · `04/28 §4.2 Zonas seguras: el notch y la barra de gestos` | — | «Designing for TV» · guías de plataforma |
| H7 | **Steam Deck y consola: requisitos de UX** | ❌ | `05/02 §3.6 Steam Deck` cubre **solo el build** (Linux nativo o Windows+Proton, y que no hay target oficial). `13/05 §1.2` avisa del tamaño de texto en Deck | Los criterios Deck Verified: **fuente ≥ 9 px a 1280×800**, glifos que coincidan con la entrada activa (no mostrar teclado si manda el mando), configuración de mando por defecto que dé acceso a todo, teclado en pantalla de Steam para cualquier entrada de texto, suspender/reanudar | Steamworks, *Steam Deck Compatibility Review* (partner.steamgames.com/doc/steamdeck/compat) |

### I · Texto

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| I1 | Tamaño mínimo de texto por distancia de visionado | ✅ | `13/05 §1.2 Legibilidad` — cita literal de XAG 101: **26 px a 1080p en consola, 18 px en escritorio**, medido como altura de cuerpo, con el truco de `string_height("Ag")` | — | Xbox Accessibility Guidelines 101 «Text Display» · «Designing for TV» |
| I2 | Contraste: nunca texto sobre el mundo (el *scrim*) | ✅ | `13/05 §1.3 Contraste` (tres capas, suelo WCAG 4,5:1 / 3:1) | — | WCAG 2.2 |
| I3 | Bitmap frente a TTF frente a SDF | ✅ | `13/05 §3.6 Tipografía` (tabla de decisión + `font_enable_sdf`/`font_sdf_spread`, con el aviso de que no funciona en HTML5) · `08/03` | — | Manual LTS 2026 |
| I4 | Alfabetos no latinos y las constantes `*_CHARSET` | ✅ | `13/05 §3.6 Alfabetos no latinos` · `04/21 §4` · `08/20 Lo que el manual no documenta` (las 19 `*_CHARSET` que existen en el runtime y no en `GmlSpec.xml`) | — | `fnames` del runtime instalado |
| I5 | Crecimiento del texto al traducir (30 %) e interlineado | ✅ | `13/05 §3.6 Tamaño y espaciado` · `04/21` | — | Práctica de localización |
| I6 | Scribble: texto rico, efectos, *typewriter* | ✅ | `07/18 Scribble (guía en español)` · `10/10 Herramientas de la comunidad` · `13/12 §6.9` | — | Repositorio de JujuAdams |

### J · Accesibilidad

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| J1 | Ajustes de accesibilidad como datos (`global.a11y`) | ✅ | `04/27 §La regla: cada ajuste es una opción` | — | GAG General Basic: «Ensure that all settings are saved/remembered» |
| J2 | No comunicar solo con color: forma + icono | ✅ | `04/27 §1 Daltonismo` · `13/05 §3.7 punto 4` (los iconos de estado llevan forma) | — | GAG Vision Basic |
| J3 | Filtros o simulación de daltonismo por shader | 🟡 | `04/27 §1` remite a `08/06`; `08/06 §Palette swap` remite de vuelta a `04/27` — **ninguno trae el shader** | La matriz de daltonización (protan/deutan/tritan), el simulador para probar, y el aviso de que aplicarlo sobre `application_surface` cuesta un *pass* | GAG Vision Basic · Xbox Accessibility Guidelines 106 |
| J4 | Subtítulos: activables, con caja, escalables, para SFX | ✅ (base) | `04/27 §2 Subtítulos y texto legible` · `13/12 §6.9 Subtítulos, velocidad de texto y voces` (con `subtitulo_duracion()` y la regla «manda el audio») | — | GAG Hearing Basic |
| J5 | Subtítulos avanzados: nombre del hablante, indicador direccional, personalización, activos antes del primer sonido | ❌ | No están en `04/27` ni en `13/12` | Las cuatro cosas | GAG Hearing Intermediate: «Provide a visual indication of who is currently speaking» · «Allow subtitle/caption presentation to be customised» · «Ensure subtitles are or can be turned on before any sound is played» · «information conveyed by audio is replicated in text/visuals» |
| J6 | *Reduce motion*, tope de flashes (<3/s) y desactivar shake | ✅ | `04/27 §3 Reduce motion` (con el umbral WCAG de 3 destellos/s) · `13/05 §3.8` (todo el juice de UI pasa por `reduce_motion`) · `04/15 §6 FeelSettings` | — | WCAG 2.3.1 · GAG Cognitive Basic |
| J7 | Escala de texto y layout que se mide en vez de fijarse | ✅ | `04/27 §2` · `13/05 §3.7 punto 1-2` (probar al 150 %) | — | XAG 101 (escalado hasta el 200 %) |
| J8 | **Dificultad ajustable / modo asistido como ajuste real** | 🟡 | `13/01 §3.3` lo razona muy bien a nivel de diseño | Falta la implementación: qué variables expone el modo asistido, poder cambiarlo **durante** la partida, no bloquear logros, y presentarlo sin culpabilizar | GAG General Basic «Offer a wide choice of difficulty levels»; Intermediate «Include assist modes such as auto-aim»; «Allow difficulty level to be altered during gameplay» |
| J9 | Hold-to-toggle y evitar machaqueo/QTE imposibles | ✅ | `04/27 §4 Accesibilidad motriz` (con el código que respeta `hold_para_toggle`) | — | GAG Motor Intermediate «Avoid / provide alternatives to requiring buttons to be held down» y «Avoid repeated inputs» |
| J10 | **Remapeo completo de controles** | 🟡 | `04/25 §5 Reasignar controles` — **esbozo de 12 líneas** que delega en la librería Input | Detección de conflictos, captura de botón y de eje de mando, restablecer con confirmación, perfiles, y que los prompts de la UI lean la asignación real | GAG Motor Basic: «Allow controls to be remapped / reconfigured» — es además requisito de certificación |
| J11 | Volúmenes separados (música / efectos / voz) | ✅ | `04/25 §2` (`audio_group_set_gain` por grupo, con el aviso contra `audio_master_gain`) · `01/13` | La pista de **voz** como grupo aparte no aparece explícitamente | GAG Hearing Basic |
| J12 | **Lector de pantalla y TTS de menús** | ❌ | Cero cobertura. Verificado con `buscar.py --listar`: **no existe ningún símbolo `speech_*`, `tts_*`, `accessib*` ni `narrator*` en el runtime 2026.0.0.23**, y `07/03` / `12/02` no listan ninguna extensión que lo aporte | Documentar honestamente el techo: en GameMaker **no se puede** sin una extensión nativa por plataforma; qué se puede hacer en su lugar (voz pregrabada de menús, iconos grandes, alto contraste) | GAG Vision Advanced: «Ensure screen reader support, including menus & installers» · GAG General Advanced: «Realtime text ↔ speech transcription» |
| J13 | **Mono/estéreo e indicación visual de la dirección del sonido** | ❌ | No aparece en `04/27` ni en `13/09` | El toggle mono (crítico para sordera unilateral) y el indicador de dirección del daño | GAG Hearing Intermediate: «Provide a stereo/mono toggle» · «all important supplementary information conveyed by audio is replicated in text/visuals» |
| J14 | **Recordatorio de controles y de objetivo durante la partida** | ❌ | No hay nada. `13/12 §6.5` tiene un gestor de misiones, pero no como ayuda cognitiva | Un panel de «¿qué estaba haciendo?» y de controles, accesible en cualquier momento | GAG Cognitive Intermediate: «Indicate / allow reminder of controls / of current objectives during gameplay» |
| J15 | Declarar las funciones de accesibilidad y probar con personas con discapacidad | ❌ | `04/27` cierra con un checklist mínimo de 7 puntos; no menciona ni la declaración ni el playtesting inclusivo | La sección de accesibilidad de la ficha de Steam, el listado dentro del juego, y añadir participantes con discapacidad al playtesting de `13/10 §10` | GAG General Basic «Provide details of accessibility features in-game / on website» · Intermediate «Include some people with impairments amongst play-testing participants» |

### K · UX de sistema (guardado, errores, telemetría, *quality of life*)

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| K1 | Guardado técnico: ranuras, escritura segura, versión de esquema | ✅ | `06 - Assets y Scripts/scr_save_load.gml` (temporal + validación + `game_save_id`) · `01/14` | — | Manual GameMaker |
| K2 | Autoguardado (dónde y cuándo) | ✅ (mención) | `04/00 §5` («en puntos de guardado o autoguardado al cambiar de zona») · `04/06`, `04/04` | — | GAG General Intermediate: «Provide an autosave feature» + «Provide a manual save feature» |
| K3 | **UX de guardado**: indicador de autoguardado, metadatos de ranura, confirmación de sobrescritura | ❌ | No hay sección | El icono de «guardando» que no miente, la ficha de ranura (hora, zona, tiempo jugado, miniatura), confirmar antes de sobrescribir o borrar | GAG Cognitive Intermediate: «Provide gameplay thumbnails with game saves» |
| K4 | Confirmación de acciones destructivas («¿seguro que quieres salir?») | 🟡 | La **regla** está en `13/05 §2.1 punto 3` (con «No» por defecto) y en el checklist `§4` | Falta el widget de diálogo modal reutilizable. ⚠️ Y `show_question()` **no sirve**: `01/15` avisa de que bloquea el juego y se ignora fuera de Windows | Práctica de certificación |
| K5 | Manejador de excepciones que deja informe | ✅ | `13/11 §4.5 Recoger las caídas desde el día 1` (`exception_unhandled_handler` con `longMessage`, `stacktrace`, código de salida para el CI) · `01/15` | — | Manual LTS 2026 |
| K6 | **Crash handler amable con el jugador** | 🟡 | El de `13/11 §4.5` es correcto pero **silencioso**: escribe `caida.txt` y se cierra | Mensaje al jugador en su idioma, autoguardado de emergencia dentro del propio manejador, dónde está el informe y cómo enviarlo | Práctica de producción |
| K7 | Telemetría de juego y de UX | ✅ | `13/01 §9.5 Telemetría: contar muertes por sala y volcarlas a JSON` · `13/10 §10.4 Telemetría mínima` + `§10.2` (que ya incluye la métrica de UI «menús abiertos y cerrados sin usar») | — | Valve (instrumentación de playtests), citado |
| K8 | Playtesting: protocolo, cuánta gente, observación → tarea | ✅ | `13/01 §7 Playtesting` · `13/10 §10.1-10.3` (Valve, Nielsen matizado a ~6/12/100 para juegos, criterio de aceptación, «1 de 5 es ruido, 3 de 5 es el diseño») | — | Nielsen · Games User Research · Valve |
| K9 | Playtesting específico de UI | 🟡 | `13/10 §10.2` mide «menús abiertos sin usar» y «dónde mira cuando está perdido» | Las pruebas de UI propiamente dichas: comprensión de iconos sin etiqueta, prueba de los 5 segundos, primer clic | Hodent, *The Gamer's Brain* |
| K10 | Velocidad de texto, saltar cinemática, recordar la última selección | ✅ | `13/12 §6.8 Saltar la cinemática: siempre, y la segunda vez sola` · `§6.9` (tabla lenta/normal/rápida/instantánea) · `13/05 §2.2 ley 5` (el foco vuelve donde estaba) | — | GAG Cognitive Basic: «Allow players to progress through text prompts at their own pace» · GAG General Intermediate: «Offer a means to bypass gameplay elements» |
| K11 | **Captura de pantalla del jugador, modo foto y compartir** | ❌ | `screen_save` solo aparece como API (`08/17`) y como herramienta de QA (`13/10 §7.3 Capturas automáticas`) | El modo foto (ocultar HUD, congelar, mover cámara, filtros), `screen_save_part`, dónde se guarda por plataforma, y la marca de agua | Práctica de marketing indie · `13/11` (material de prensa) |
| K12 | Checklist de UI antes de publicar | ✅ | `13/05 §4 Checklist de UI antes de publicar` — 26 casillas repartidas en legibilidad, interacción, feedback y accesibilidad | — | Compuesto de XAG + WCAG + práctica |

---

## 2 · Propuestas priorizadas

### 🔴 Prioridad alta

**P1 · Ampliar `04 - Recetas por género/27 - Accesibilidad.md`** (de 137 líneas a documento completo)

Es el documento más corto del dominio y el que más lejos queda de su fuente canónica: cubre 7 de
las ~100 pautas de las Game Accessibility Guidelines, y él mismo admite en la cabecera que nació
para tapar un hueco. Añadir: el shader de daltonización real (matrices protan/deutan/tritan) y su
simulador; subtítulos con nombre del hablante, indicador direccional y personalización de
presentación; toggle mono/estéreo; slider de haptics; recordatorio de controles y de objetivo; el
modo asistido como ajuste con las variables que expone y cambiable en caliente; y una sección
honesta **«Lo que GameMaker no puede hacer»** con el lector de pantalla y el TTS, verificada
contra el índice de símbolos (no hay `speech_*` ni `tts_*` en el runtime 2026.0.0.23). Cerrar con
el checklist por niveles Basic/Intermediate/Advanced y cómo declararlo en la ficha de Steam.
*Cubre J3, J5, J8, J12, J13, J14, J15 y A24.*

**P2 · Documento nuevo: `04 - Recetas por género/32 - Tutorial, onboarding y prompts en pantalla.md`**

El diseño del onboarding está resuelto en `13/01 §5`; el **código** no existe en ninguna parte.
Este documento pone el puente: disparadores por zona de tutorial, «mostrar una sola vez»
persistido en el guardado (y qué pasa en New Game+), escalado de pistas tras N fallos, el widget
de *prompt* de botón que lee el dispositivo activo de `13/05 §2.3` **y la asignación real** tras
el rebinding, el recordatorio de objetivo y de controles, y el ajuste «saltar tutorial». Debe
empezar remitiendo a `13/01 §5` para no duplicar la teoría.
*Cubre E7, E8, E9 y parte de J14.*

**P3 · Documento nuevo: `04 - Recetas por género/33 - Transiciones, carga y pausa.md`**

Hoy la biblioteca sabe hacer un fundido a negro (`04/00 §2`) y congelar el mundo
(`04/00 §5`), y ahí se acaba. Este documento trae: el repertorio de transiciones (fundido, wipe,
iris, cortinas, disolución con shader y ruido) sobre una máquina de estados «salida → cambio →
entrada»; la pantalla de carga real con `texturegroup_load` / `texturegroup_get_status`, barra que
refleja el progreso de verdad, duración mínima y consejos rotativos; y el menú de pausa completo
(reanudar / opciones / salir con confirmación de «No» por defecto, *ducking* de la música,
oscurecido del fondo, momentos en que no se puede pausar, y el foco que vuelve donde estaba).
*Cubre F2, F3, F5 y K4.*

### 🟠 Prioridad media

**P4 · Ampliar `04 - Recetas por género/25 - Menú de opciones y ajustes.md` §5 (rebinding)**

Los 12 renglones actuales son un esbozo que delega en la librería Input. El remapeo es pauta
**Basic** de las GAG y requisito de certificación: merece una sección de verdad con captura de
tecla y de botón de mando, ejes, detección y resolución de conflictos, restablecer valores con
confirmación, perfiles guardados, y el enganche con `icono_boton()` de `13/05 §2.3` para que los
prompts muestren lo que el jugador ha asignado y no lo que venía de fábrica. Puede seguir
recomendando Input al final, pero después de enseñar el mecanismo.
*Cubre J10 y cierra E8.*

**P5 · Secciones nuevas en `04 - Recetas por género/15 - Game feel y juice.md`**

Cuatro huecos del catálogo clásico de «Juice it or lose it» y Vlambeer que el documento nombra en
`§8` como ideas de una línea y nunca desarrolla: **(a)** estela de cinta con
`draw_primitive_begin_texture` / `pr_trianglestrip` a partir de un historial de dos puntos por
fotograma, que es *el* trail de espada; **(b)** *permanence*: sangre, casquillos y quemaduras
acumulados en una *surface* del tamaño de la sala, con el patrón de recreación tras
`surface_exists()` falso y su presupuesto de memoria; **(c)** *zoom punch* y retroceso de cámara
—`scr_camera.gml` hoy no tiene zoom—; **(d)** la vibración del mando como quinta capa de feedback,
con intensidad por tipo de golpe, curva de decaimiento y su toggle obligatorio.
*Cubre A18, A20, A22 y A24.*

**P6 · Dos componentes nuevos en `13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md` §3.5**

El catálogo de componentes tiene nueve piezas y le faltan las dos pantallas de consulta más
repetidas del oficio: **la pantalla de mapa completa** (desplazamiento y zoom, marcadores,
salas visitadas frente a descubiertas, viaje rápido — hoy solo existe el minimapa de `§3.5g`) y
**la UI de tienda** (precio, estado «no te lo puedes permitir» resuelto con el botón inactivo
*con motivo* de `§1.5`, confirmación, comparación con lo equipado, vender). Encajan como `§3.5j`
y `§3.5k` sin tocar nada de lo existente.
*Cubre G7 y G8.*

**P7 · Sección nueva: «La recompensa y el fracaso» en `04 - Recetas por género/15` §4bis o en `13/05`**

La biblioteca sabe hacer sentir un golpe y no sabe hacer sentir un premio: `buscar.py --texto
"celebración"` devuelve cero. Falta la coreografía de una recompensa (parón corto, sonido
ascendente, el número que entra con *ease out back*, pausa antes de devolver el control), la
subida de nivel y el desbloqueo, la pantalla de resultados — y su reverso: el fracaso sin
humillar (coste del reintento medido en segundos, reaparecer donde estaba, no repetir la
cinemática, no culpar al jugador con el texto). Es la mitad que falta del bucle de feedback.
*Cubre C2, C4 y D3.*

### 🟡 Prioridad baja

**P8 · UX de guardado** — sección en `13/05 §3.5` o cabecera ampliada de `scr_save_load.gml`:
indicador de autoguardado que no miente, ficha de ranura con hora / zona / tiempo jugado /
miniatura (`screen_save_part` sobre la `application_surface`), y confirmación antes de
sobrescribir o borrar. *Cubre K3.*

**P9 · Crash handler amable** — ampliar `13/11 §4.5`: mensaje al jugador en su idioma en vez del
cierre mudo, autoguardado de emergencia dentro del propio manejador, y decirle dónde está
`caida.txt` y cómo enviarlo. *Cubre K6.*

**P10 · Steam Deck y consola: los criterios de UX** — sección en `05 - Referencia/02 §3.6` y
cruce desde `13/05 §3.3`: fuente ≥ 9 px a 1280×800, glifos que coincidan con la entrada activa
(no enseñar teclado si manda el mando), configuración de mando por defecto que dé acceso a todo
el contenido, teclado en pantalla de Steam para cualquier entrada de texto, y suspender/reanudar.
Hoy `05/02 §3.6` solo cubre cómo se construye el binario. *Cubre H7.*

**P11 · Captura, modo foto y compartir** — sección en `13/05` o en `13/11`: `screen_save` /
`screen_save_part` para el jugador (no solo para QA como en `13/10 §7.3`), modo foto con HUD
oculto y cámara libre, dónde se guarda en cada plataforma y la marca de agua. Enlaza con el
material de prensa de `13/11`. *Cubre K11.*

**P12 · Latencia de entrada** — sección corta en `01 - Fundamentos/15` o en `04/15 §4bis`: medir
el retardo real con `get_timer()`, por qué el input se lee en Begin Step, el coste de *vsync* y
`display_reset`, y la regla de Swink sobre cuántos fotogramas de retardo se perciben. Existen
piezas sueltas en `04/01 §7` y `13/05 §1.5`, pero nadie lo trata como tema. *Cubre A1.*

---

## 3 · Limitaciones de esta auditoría

1. **No compilé nada ni ejecuté GML.** El veredicto sobre la profundidad del código sale de
   leerlo, no de probarlo. Los documentos afirman estar verificados con `gm-cli manual read` y
   `validar-codigo-gml.py`, y no lo he re-verificado.
2. **No abrí `11 - Código descargado/_CATALOGO.md`.** `13/05 §3.9` cita cinco librerías de UI
   (YUI, Bento, gooey, Emu, Scribble) del catálogo; es posible que algún hueco que marco como
   FALTA (mapa completo, tienda, transiciones) esté resuelto por una de esas librerías. Lo que
   audité es la **documentación propia** de la biblioteca, no lo que resuelve un tercero.
3. **`09 - Manual oficial/` solo se consultó de forma puntual** (por `grep` de símbolos). Las
   3 033 páginas del espejo español pueden documentar detalles de API que aquí doy por no
   cubiertos a nivel de *receta* — la distinción que uso es: la API documentada no equivale a la
   técnica explicada (es exactamente el caso de F3, pantalla de carga).
4. **`03 - Cursos (YouTube)` y `10 - Cursos en español` se revisaron solo por `grep`.** Ambas
   carpetas llevan el aviso de que pueden estar desfasadas y ocupan el puesto 6 en el orden de
   autoridad, así que no las conté como cobertura para ningún tema.
5. **Fuentes externas consultadas en vivo el 2026-09-06:** `gameaccessibilityguidelines.com`
   (lista completa por categoría y nivel) y `partner.steamgames.com/doc/steamdeck/compat`
   (criterios Deck Verified). Ambas se leyeron con éxito. Las Xbox Accessibility Guidelines y la
   tesis *Beyond the HUD* no se re-consultaron: la biblioteca ya las cita con cifras literales y
   URL en `13/05 §1.2` y `§1.9`, y las di por buenas.
6. **La ausencia de API de lector de pantalla (J12) sí está verificada**, con
   `buscar.py --listar` sobre `accessib`, `speech`, `narrator`, `tts`, `screenreader` y `voice`:
   cero símbolos en el runtime `2026.0.0.23`. Lo que no pude verificar es si existe alguna
   extensión de terceros no catalogada en `07/03` ni en `12/02` que lo aporte.
