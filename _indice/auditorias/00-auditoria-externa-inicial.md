# Auditoría externa de cobertura — biblioteca GameMaker en español

Fecha de la auditoría: 2026-09-06. Biblioteca generada/ampliada: 1-2 de septiembre de 2026.
Carpetas auditadas: `01`, `02`, `04`, `05`, `07`, `08`, `10`, `12` (títulos y encabezados
`^#{1,3}`, sin leer los documentos enteros). Contraste con fuentes externas vía WebSearch
(WebFetch a gamemaker.io y manual.gamemaker.io devolvió 403 en todos los intentos —incluidos
mirrors y el proxy translate.goog—, así que el TOC del manual oficial se reconstruyó a partir
del **mirror local verificado** en `09 - Manual oficial/` — es un espejo 1:1 de
`manual.gamemaker.io`, con URL de origen al pie de cada página, generado el 1-9-2026).

No se han encontrado más de 4 huecos reales que superen el listón de "necesario para
desarrollar cualquier juego, verificado por ausencia real, no ya cubierto". Se documentan
también los temas que SÍ están cubiertos (para no duplicar) y el estado de versión.

---

## 1 · Huecos reales, verificados

| Tema | Fuente externa que lo considera necesario | Evidencia de ausencia en la biblioteca | Gravedad | Propuesta |
|---|---|---|---|---|
| **Behavior Trees para IA de decisión** (además de steering behaviors y utility AI, que sí están) | Es una de las 3 arquitecturas clásicas de IA de videojuego junto a FSM y Utility AI. Múltiples repos y tutoriales específicos de GameMaker: [GamemakerCasts/behaviour-trees](https://github.com/GamemakerCasts/behaviour-trees), [Gizmo199/BehaviorTree](https://github.com/Gizmo199/BehaviorTree) (también en [GameMaker Kitchen](https://www.gamemakerkitchen.com/libraries/gizmo199/behaviour-tree/)), [VitorEstevam/GML-Behavior-Tree](https://github.com/VitorEstevam/GML-Behavior-Tree), hilo oficial del foro [«Behavior Trees AI for GML»](https://forum.gamemaker.io/index.php?threads/behavior-trees-ai-for-gml.30741/), vídeo «Easy Enemy AI: GameMaker Behavior trees» (2024) | `grep -rli "behavior tree\|árbol de comportamiento\|behaviour tree" "04 - Recetas por género" "07 - Ecosistema"` → **0 resultados**. `python3 _indice/buscar.py --todo "behavior tree"` → solo aparece 1 vez, dentro de `GameMaker_Fuentes/librerias/Gizmo199__BehaviorTree/README.md` (código de terceros sin curar, no es documentación de la biblioteca). `--todo "árbol de comportamiento"` → **0 resultados** en español. `04 - Recetas por género/23 - IA de enemigos y steering behaviors.md` cubre Seek/Flee/Arrive/Wander/evasión de obstáculos/patrullas con Paths/flocking, pero ni menciona árboles de comportamiento; `04 - Recetas por género/13 - Estrategia y gestión.md` cubre IA por utilidad (utility AI) y `07 - Ecosistema/17` cubre máquinas de estados (SnowState) — las otras dos arquitecturas clásicas sí están | **Alta** | Sección nueva en `04 - Recetas por género/23 - IA de enemigos y steering behaviors.md` (o documento nuevo `23 bis`) — cuándo usar árbol de comportamiento vs. FSM vs. utility AI, y una implementación mínima con structs (nodos Sequence/Selector/Condition/Action) |
| **Sistema de hitboxes/hurtboxes desacoplado** (frames activos/de recuperación, hit-stun, combos, bloqueo) para combate cuerpo a cuerpo / beat 'em up / lucha | Es la base técnica de cualquier juego de combate cuerpo a cuerpo. Recursos específicos de GameMaker: [MichelVGameMaker/HitBoxes_gml](https://github.com/MichelVGameMaker/HitBoxes_gml), serie «GameMaker Basics: Hitboxes and Hurtboxes» y «Combo Setup» (Amazon Appstore Devblog / Nathan Ranney-RatCasket, con [proyecto+tutorial en itch.io](https://ratcasket.itch.io/hitboxes-and-hurtboxes)), el propio catálogo de cursos en español de esta biblioteca ya cita el curso «Juego Beat'em Up» de Hektor Profe (`10 - Cursos en español/01`) como existente pero sin transcribir ni convertir en receta, y la guía de combate cuerpo a cuerpo en 2 partes de Shaun Spalding (máquina de estados + combos/cadenas de ataque) | `python3 _indice/buscar.py --todo "hurtbox"` → solo aparece en `12 - Utilidades e integraciones/06` (nombre de un asset pack de itch.io, sin explicación) y dentro de `GameMaker_Fuentes/.../Pizza-Tower-EXtracted/...` (código de un juego comercial extraído — el propio `AGENTS.md` prohíbe copiarlo, está «para leer», no es material didáctico). `grep -rli "hitbox\|hurtbox\|frame data\|parry\|beat.em.up\|fighting game" "04 - Recetas por género"` → solo 3 archivos, y en los tres es una palabra suelta en una tabla comparativa o una nota al pie (`04-04` fila «Implementación… colisiones, hitboxes», `04-03` y `04-14` mención de rollback para «juegos de lucha»), nunca una explicación del patrón. No existe receta de género para Beat 'em up / Fighting game en `04 - Recetas por género/_INDICE-RECETAS.md` (15 géneros cubiertos, ninguno es combate cuerpo a cuerpo con hitboxes propias) | **Alta** | Receta nueva `04 - Recetas por género/28 - Combate cuerpo a cuerpo y beat 'em up.md`: hitbox/hurtbox como structs independientes de la máscara de colisión del sprite, frames activos/recuperación, hit-stun, cancelación de combos, bloqueo/parry |
| **Particionado espacial (spatial partitioning) para colisiones 2D a gran escala** — grid propio / spatial hash / quadtree, más allá de `place_meeting`/`instance_place`/`mp_grid` | Es uno de los patrones clásicos de "Game Programming Patterns" (Nystrom) — capítulo [Spatial Partition](https://gameprogrammingpatterns.com/spatial-partition.html), TOC completo obtenido vía WebFetch. En el propio ecosistema GameMaker, DragoniteSpam documentó en profundidad quadtree/octree/spatial-hash como broad-phase para colisiones ([dragonite.itch.io/collisions](https://dragonite.itch.io/collisions), devlog «Major performance improvements») | `python3 _indice/buscar.py --todo "quadtree"` → aparece únicamente dentro de `GameMaker_Fuentes/librerias/blueburncz__BBMOD/...` y `11 - Código descargado/librerias/3d/...` (el quadtree interno de la librería 3D BBMOD/DS-3DCollisions, código de terceros, no una explicación didáctica). `--todo "particionado espacial"` → **0 resultados** en toda la biblioteca. `01 - Fundamentos/15 - Depuración y rendimiento.md` cubre optimización general (VM vs YYC, texture pages) pero no colisiones a escala; `04 - Recetas por género/08 - Tower Defense.md` usa `mp_grid` (pathfinding, no broad-phase de colisión); ninguna receta enseña a construir una grid/hash propios para, p. ej., un roguelike o shmup con miles de instancias | **Media** | Sección nueva en `01 - Fundamentos/15 - Depuración y rendimiento.md` (o en `07 - Ecosistema/05 - Scripts y utilidades GML.md`, que ya tiene un script de "Rejilla (grid) con structs" que podría ampliarse): grid uniforme / spatial hash con structs, cuándo compensa frente a las funciones nativas |
| **Patrón Command** (objetos-comando para reasignar controles con deshacer, sistemas de repetición/replay, colas de acciones de IA o turnos) | Capítulo [Command](https://gameprogrammingpatterns.com/command.html) de "Game Programming Patterns" (TOC verificado vía WebFetch) — uno de los 6 patrones de la sección «Design Patterns Revisited» junto a los que la biblioteca sí cubre indirectamente (State → SnowState/07-17; Observer → 04-16 Señales; Flyweight/Prototype/Singleton no evaluados por ser menos aplicables a GML) | `grep -rn -i "patrón comando\|command pattern\|objeto[- ]comando" "01 - Fundamentos" "04 - Recetas por género" "07 - Ecosistema" "08 - Referencia GML completa"` → **0 resultados**. `python3 _indice/buscar.py --todo "command pattern"` → **0 resultados** en toda la biblioteca (ni en código descargado). `04 - Recetas por género/25 - Menú de opciones y ajustes.md` sí cubre reasignar controles, pero como lectura/escritura directa de constantes de tecla, no como objetos-comando reutilizables para deshacer/repetir | **Baja-Media** — se solapa parcialmente con «arquitectura de proyecto» (ya planificado); repórtese solo si esa futura sección no lo incluye explícitamente | Mencionar como técnica dentro del futuro documento de arquitectura de proyecto, con un ejemplo concreto (deshacer un movimiento en un puzzle, o encolar acciones de una unidad en un RTS) |

---

## 2 · Temas revisados que SÍ están cubiertos (no duplicar)

Comprobado con `grep` y/o `buscar.py --todo` contra fuentes externas — están completos o
"cubiertos como sección dentro de otro documento", que por las instrucciones de esta auditoría
no cuenta como hueco:

- **Escalado de pantalla / GUI layer / relación de aspecto** (`display_set_gui_size`, opción
  *Scaling* del Game Options: *Maintain aspect ratio* vs *Full scale*) — está explicado en
  `01 - Fundamentos/06`, `01 - Fundamentos/11` y `01 - Fundamentos/16` (con un curso asociado,
  `03 - Cursos (YouTube)/42 - PixelatedPope - Cámaras y Resolución 2026`), coincide con los
  tutoriales oficiales «The Basics Of Scaling — The GUI Layer / The Game Camera»
  (gamemaker.io/en/blog).
- **Object pooling** — script dedicado en `07 - Ecosistema/05` y usado en las recetas de shmup
  y arcade.
- **Máquinas de estado (FSM)** — guía completa de SnowState en `07 - Ecosistema/17` y script
  propio en `07 - Ecosistema/05`.
- **Observer / desacoplamiento por señales** — `04 - Recetas por género/16`, que el propio
  documento dice haber añadido tras cruzar los tutoriales del foro oficial (01-09-2026) por ser
  «el único sistema sin cubrir» en ese momento.
- **Utility AI** — `04 - Recetas por género/13 - Estrategia y gestión.md` §4.6.
- **Pathfinding A\* / `mp_grid`** — `04 - Recetas por género/08 - Tower Defense.md`.
- **Vibración/rumble de mando** — `01 - Fundamentos/12 - Input`.
- **Migración/versionado de partidas guardadas** — `01 - Fundamentos/14` (hook
  `migrar_guardado()` y checklist explícito).
- **Cifrado/hash de guardados** (con el aviso honesto de que base64 no es seguridad real) —
  `01 - Fundamentos/14` §12.
- **Deshacer un intercambio inválido en Match-3** (caso concreto, no el patrón general) —
  `04 - Recetas por género/07 - Puzzle y Match-3.md`.
- **Servidor dedicado *headless*** — mencionado en `04 - Recetas por género/14 - Multijugador.md`.
- **Modding / Steam Workshop, Analítica (GameAnalytics/Firebase/Adjust), Discord Rich Presence**
  — catalogados como extensiones existentes en `07 - Ecosistema/01`, `07 - Ecosistema/03` y
  `12 - Utilidades e integraciones/03` (es un catálogo de "qué existe", coherente con el
  propósito de esas carpetas; no hay receta de "cómo instrumentar tu juego con analítica para
  balancear", pero no se reporta como hueco porque el propósito declarado de esas carpetas es
  cartografiar el ecosistema, no enseñar la técnica).
- **Post-processing (bloom, aberración cromática, vignette)** — referenciado como sección
  dentro de `04 - Recetas por género/15 - Game feel y juice.md` (apunta al asset de
  FoxyOfJungle), no es un hueco según el criterio de esta auditoría.
- **Transición Marketplace → Package Manager / Prefab Library** — completamente al día en
  `02 - Novedades 2026/08`, citando el hilo oficial del foro de agosto de 2026.
- **Bitwise operators** — mencionados de pasada en `01 - Fundamentos/02` (una línea sobre
  int64); no se reporta como hueco mayor porque el uso de banderas/bitmask no apareció como
  tema demandado explícitamente en las fuentes externas consultadas (se señala como debilidad
  menor, no como hueco).
- **Anti-cheat para leaderboards** y **editor de niveles dentro del juego (UGC)** — no están
  cubiertos, pero no se han encontrado fuentes externas que los sitúen como «necesarios para
  cualquier juego» (son de nicho/opcionales), así que no se listan como huecos, solo se anotan
  aquí para que quede constancia de que se comprobaron.

---

## 3 · Estado de versión / ecosistema: contraste con fuentes externas

No se ha encontrado ninguna contradicción de fondo. Resumen de lo verificado:

- **LTS 2026.0** (IDE `2026.0.0.16` / runtime `2026.0.0.23`), publicada el 21 de mayo de 2026,
  ciclo de 5 releases hasta ~Q1 2028: coincide con `releases.gamemaker.io/release-notes/2026/0`
  y con el blog oficial «GameMaker LTS 2026.0: New Features, GMRT and Much More»
  (gamemaker.io/en/blog/lts-2026-release).
- **GMRT Beta 0.21** (27-08-2026): no se ha encontrado un anuncio de 0.22/0.23 ni de salida de
  Beta en escritorio a fecha de esta auditoría (6-9-2026); el blog «GameMaker Update Spring
  2026» sitúa la salida de Beta de Desktop «en los próximos meses» desde primavera de 2026, sin
  fecha exacta más nueva que la que ya maneja la biblioteca. **Sin contradicción.**
- **Transición Marketplace → Package Manager**: confirmada por búsqueda externa («no hay forma
  de gestionar tu librería del Marketplace desde la IDE en 2026.0; solo permite descargar los
  archivos ya comprados desde la web») — coincide exactamente con lo que ya documenta
  `02 - Novedades 2026/08 - Package Manager y Prefabs.md`. **Sin contradicción.**
- El canal **Monthly discontinuado** y el runtime GMS2 marcado *feature complete* también
  coinciden con las fuentes oficiales citadas arriba. **Sin contradicción.**

No se han detectado, por tanto, discrepancias entre `README.md §2` / la cabecera de
`AGENTS.md` y el estado real del ecosistema a fecha de esta auditoría.

---

## 4 · Nota metodológica y limitaciones

- **WebFetch a `gamemaker.io` y `manual.gamemaker.io` devolvió HTTP 403 en todos los intentos**
  (URL directa, mirror `manual-en.yoyogames.com`, y proxy `translate.goog`) — probablemente
  protección anti-bot. Se ha compensado con `WebSearch` (fragmentos indexados) y, para el TOC
  del manual, con el mirror local verificado en `09 - Manual oficial/` (descargado 1-9-2026,
  cada página lleva la URL oficial de origen al pie).
- No se pudo confirmar el contenido exacto de los playlists de YouTube de Shaun Spalding,
  Peyton Burnham, DragoniteSpam y Friendly Cosmonaut más allá de lo que WebSearch indexa como
  fragmentos — no hay acceso a listar vídeo por vídeo. Con lo indexado no ha aparecido ningún
  tema de esos canales ausente en la biblioteca aparte de los ya reportados.
- No se ha encontrado ningún creador de referencia llamado «Samuel Vanie» relacionado con
  GameMaker (la búsqueda no devolvió resultados relevantes con ese nombre) — probable error de
  transcripción o canal muy minoritario; no se ha podido investigar más.
- Los géneros "juego de cartas / deckbuilder" y "táctica por turnos en grid" (tipo XCOM/Fire
  Emblem) no tienen receta propia en `04`, pero no se reportan como huecos porque (a) casi toda
  la evidencia externa encontrada sobre deckbuilders es específica de Unity, no de GameMaker, y
  (b) el encargo pide huecos transversales «para cualquier juego», no cobertura completa de
  géneros — que es una decisión editorial de la biblioteca, no una laguna de conocimiento.
