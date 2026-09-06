# Auditoría r3 · Géneros y sistemas de juego sin cubrir

> 2026-09-06 · barrido de las 46 recetas de `04` y los 24 documentos de `13` contra la lista de
> géneros del medio. Hecha con `grep -rlwi` sobre las carpetas de contenido; cada veredicto lleva
> la línea exacta donde se comprobó.

## Resumen ejecutivo

La cobertura por género es mucho mejor de lo que parecía: **RTS completo** (selección, órdenes,
niebla de guerra, IA por utilidad) está en `04/13 §5`, el ***endless runner*** en `04/11 §4`, los
***replays*** y su determinismo en `13/06 §465`, `13/10 §14.3` y `04/13 §1373`, y la **línea de
visión** en `04/45`, `04/33` y `13/13`. Nada de eso hay que escribirlo.

Lo que falta son **cinco géneros completos y una técnica transversal**. La más cara de las
ausencias no es un género: es el **eje Z falso** (altura simulada en un juego 2D), que hace falta
para beat 'em up, para saltar en top-down, para isométrico y para cualquier proyectil con arco.
Cero resultados en toda la biblioteca.

## Veredictos comprobados

| Tema | Veredicto | Evidencia |
|---|---|---|
| RTS: selección por caja, órdenes, formaciones, niebla de guerra | ✅ Cubierto | `04/13 §4.4`, `§5.0`-`§5.5` |
| Replays, *ghosts*, determinismo de repetición | ✅ Cubierto | `13/06:465`, `13/10 §14.3`, `04/11:982`, `04/13:1373` |
| Línea de visión y conos de detección | ✅ Cubierto | `04/45`, `04/33`, `04/31`, `13/13` |
| *Endless runner* | ✅ Cubierto | `04/11:33` (tabla) y `:563` (movimiento automático) |
| Rejilla hexagonal: matemáticas y generación | ✅ Cubierto | `13/13 §7.4`, `13/07`, Red Blob citado |
| *Frame data*, hitbox/hurtbox, *cancels* | 🟡 Parcial | `04/30 §1.2` y `§ tabla:116` los define, pero para *hack and slash*: dice explícitamente que el juego de lucha necesita «decenas de cajas» y no lo desarrolla |
| Terreno destructible | 🟡 Parcial | `13/07:1923` (rejilla lógica + visual sincronizadas) y `12/05`. Falta *marching squares* (0 resultados), arena/agua por autómata, minado y colocación |
| Rejilla hexagonal **como tablero jugable** | 🟡 Parcial | Las matemáticas están; falta vecindad, rango, pathfinding y línea sobre hex |
| **Eje Z falso / altura simulada** | 🔴 Falta | 0 resultados de «eje z», «falsa profundidad», «altura simulada» en toda la biblioteca |
| **Beat 'em up** | 🔴 Falta | 0 resultados |
| **Point and click / aventura gráfica** | 🔴 Falta | 0 resultados de «point and click» y «aventura gráfica» |
| **Deportes** (balón, equipo, reglas, marcador) | 🔴 Falta | 0 resultados de «deporte», «fútbol», «golf» |
| **Física de mesa** (billar, pinball, minigolf) | 🔴 Falta | Única mención: un comentario en `04/22:43` («mesa de billar») |
| **Juego de lucha** como género | 🔴 Falta | Ver *frame data*: `04/30` lo declara fuera de alcance |
| **Ficción interactiva / parser de texto** | 🔴 Falta | 0 resultados |

## Encargo para el redactor

1. **`04/46 — Eje Z falso: altura, sombras y profundidad en un juego 2D`.**
   La técnica transversal, no un género: variable `z` y `zvel` separadas de `x`/`y`, dibujar en
   `y - z`, sombra proyectada en el suelo que encoge con la altura, colisión solo en el plano del
   suelo, orden de dibujado por `y` (`depth = -y` frente a capas), saltar y aterrizar, proyectiles
   con arco, plataformas a distinta altura, y cuándo esto se rompe y toca irse a 3D real (`04/29`).
   Enlaza desde `04/02` (top-down), `04/12`, `13/19` (cámaras) y la receta de beat 'em up.
2. **`04/47 — Beat 'em up y brawler`.** Construido sobre la receta anterior: carril de profundidad,
   alineación en Z para golpear, oleadas y bloqueo de pantalla, agarres y lanzamientos, IA de turnos
   de ataque (los enemigos esperan turno), cooperativo local, armas recogibles. Remite a `04/30`
   para las cajas y a `04/33` para el director de encuentros; **no repitas hitboxes**.
3. **`04/48 — Aventura gráfica y point and click`.** Hotspots y cursor contextual, verbos (mirar,
   usar, hablar, coger) frente a interfaz de un botón, *walk-to* con pathfinding en polígono de
   suelo, escalado del personaje por profundidad, inventario combinatorio (usar A con B), estado
   del mundo como banderas, guardado de una aventura, y el diseño de puzzles de objeto: remite a
   `13/17` en vez de repetirlo. Diálogos: `13/12`.
4. **`04/49 — Deportes y física de mesa`.** Dos mitades. (a) Deportes de equipo: balón como entidad
   con posesión, pase con anticipación, tiro con efecto, IA por roles y formaciones, marcaje,
   fuera de juego y reglas, árbitro, reloj y marcador. (b) Física de mesa con y sin Box2D: colisión
   elástica de círculos y restitución (billar), *flippers*, *bumpers* y *tilt* (pinball), arrastrar
   y soltar con previsualización de trayectoria y viento (minigolf). Remite a `04/22` y a `13/08`.
5. **`04/50 — Juego de lucha`.** Motor de comandos: buffer de entrada, detección de secuencias
   (236P, 623P), ventana y prioridad entre comandos, *negative edge*. Estados por fotograma con
   *frame data* en datos (arranque, activo, recuperación, ventaja al golpe y al bloqueo), cajas por
   fotograma, *cancels* y *gatling*, *pushback*, escalado de daño y de *hitstun*, agarres y
   *tech*, levantada y presión, barra de súper. Cierra con la verdad sobre el *netcode*: por qué
   el *rollback* real es muy difícil en GML y qué alternativa queda (remite a `04/14`).
6. **Ampliar `13/07` con *marching squares* y materia granular.** Sección nueva: contorno suave de
   un terreno destructible con *marching squares*, destrucción por píxel con `surface`+máscara,
   sincronizar la rejilla lógica, chunks para no recalcular todo, y un autómata de arena/agua
   (*falling sand*) con su presupuesto de coste. Minado y colocación de bloques al estilo Terraria.
7. **Ampliar `04/35` con el tablero hexagonal.** Coordenadas cúbicas y axiales, vecinos, distancia,
   rango, línea, pathfinding sobre hex y conversión pantalla↔hex. Las fórmulas ya están en
   `13/13 §7.4`: **enlázalas, no las repitas**; aquí va el uso jugable.
8. **Fila honesta para la ficción interactiva** en `04/45` (géneros sin receta): parser de texto,
   gramática verbo-objeto, sinónimos, y la recomendación real (Ink o Yarn para narrativa
   ramificada, `13/12`); no merece receta propia.
