# Auditoría · Colisiones, movimiento, controladores de personaje y cámara

**Dominio:** máscaras y funciones de colisión · colisión con tilemaps · plataformas (pendientes,
one-way, móviles, escaleras, paredes, bordes) · movimiento top-down y en rejilla · vehículos ·
knockback y hit stun · controlador de personaje completo · cámara (seguimiento, deadzone,
look-ahead, zonas, multijugador, shake, zoom, pixel-perfect, 3D).

**Biblioteca auditada:** `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`
(carpetas 01–13 salvo `Lumbre/` y `GameMaker_Fuentes/`).
**Fecha:** 6 de septiembre de 2026. **Runtime de referencia:** GMS2 `2026.0.0.23`.

**Veredicto en una línea:** el dominio está **muy bien cubierto en su núcleo** —la API de
colisión, `move_and_collide`, tilemaps, el controlador de plataformas y de top-down, la cámara
con deadzone/look-ahead/trauma y el pixel-perfect están escritos con código completo y
verificado—. Lo que falta se concentra en **dos bolsas claras**: (a) el *traversal* avanzado de
plataformas (pendientes de verdad, paredes, escaleras, bordes, agua, corrección de esquina) y
(b) la **cámara como disciplina** (el marco de Itay Keren, zonas por región, transición entre
zonas, multijugador con zoom dinámico, cinemáticas).

---

## 1. Tabla completa

Leyenda: **C** = CUBIERTO · **P** = PARCIAL · **F** = FALTA.

### A · Máscaras y fundamentos de colisión

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| A1 | Qué máscara usa la instancia; `mask_index`; escala y rotación de la máscara | **C** | `01 - Fundamentos/08 - Movimiento y colisiones.md` §4 «Qué máscara se usa» · `13 - .../04 - Animación de sprites…md` §3.9 «Origen y máscara de colisión» (tabla de cuándo fija / por fotograma + aviso de que `image_xscale` escala la máscara) | — | Manual, *Collision Masks* |
| A2 | **Las formas de máscara: Rectangle · Rectangle with Rotation · Ellipse · Diamond · Precise · Precise per frame**, con su coste | **P** | `01 - .../08` §4 sólo nombra Rectangle / Rectangle With Rotation / Precise (en la «regla de los dos sprites»). El enumerado completo (`bboxkind_rectangular/_ellipse/_diamond/_precise/_spine`, `sepmasks`, `tolerance`) sólo está en el espejo: `09 - Manual oficial/manual-lts-2026-es/…/Sprites/Sprite_Manipulation/sprite_collision_mask.md` | Tabla de decisión en español: qué forma para qué caso, qué cuesta cada una («cualquier cosa que no sea rectangular requiere más potencia de procesamiento» dice el manual), y que `sprite_collision_mask()` **no** admite rectángulo girado | Manual GameMaker, `sprite_collision_mask` + *The Asset Editors → Sprites → Collision Masks* |
| A3 | Bounding box inclusiva (cambio 2022.1) y la regla del centro del píxel | **C** | `01 - .../08` §4 «⚠️ Cambio de 2022.1» y «Cómo se cuenta el solapamiento», con las excepciones de `collision_point`/`collision_line` | — | Manual, *Collisions* |
| A4 | Regla de los dos sprites al rotar · Collision Compatibility Mode | **C** | `01 - .../08` §4 «Rotación: la regla de los dos sprites» y «Collision Compatibility Mode» | — | Manual, *Collision Compatibility Mode* |
| A5 | `place_meeting` / `position_meeting` / `instance_place` / `instance_position`: cuándo cada una | **C** | `01 - .../08` §3.1–3.3 + §9 «❌ Usar el retorno de `instance_place()` como booleano», «❌ No comprobar `noone` antes de `with()`» | — | Tutorial oficial *Ultimate Guide To Collision Functions* |
| A6 | `move_and_collide()`: firma, `iterations`, `xoffset/yoffset`, `max_x/max_y`, valor de retorno | **C** | `01 - .../08` §2 (5 ejemplos, incl. «evitar el bug clásico de los plataformas») · `04 - Recetas por género/01 - Plataformas 2D.md` §4.6 (tabla de argumentos) · `03 - Cursos (YouTube)/30 - DragoniteSpam - Move and Collide.md` | — | Manual `move_and_collide`; blog oficial *How To Move And Collide* |
| A7 | `collision_rectangle/circle/ellipse/point/line` y sus `_list` | **C** | `01 - .../08` §5 «Colisiones avanzadas» (tabla `obj`/`prec`/`notme` + aviso de que devuelve una instancia cualquiera) | — | Manual, *Collisions* |
| A8 | `point_in_*` / `rectangle_in_*` (sin máscara) | **C** | `01 - .../08` §5 «Colisiones SIN máscara» | — | Manual |
| A9 | Colisión con tilemaps: `tilemap_get_at_pixel`, requisitos del tile set, máscara de bits | **C** | `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md` §4 «El blob de datos de tile», «Máscara de bits personalizada», «Colisiones con tile maps» · `01 - .../08` §3.4 · `13 - .../02 - Diseño de niveles.md` §3.4 «Colisión de tiles: las dos vías» | — | Manual, *Tile Maps*; DragoniteSpam *Autotiles* |
| A10 | AABB frente a OBB frente a píxel-perfecto: coste y cuándo | **C** | `13 - .../13 - Matemáticas aplicadas al juego.md` §6.7 «AABB frente a OBB», §6.1 «Qué trae GameMaker y hasta dónde llega», §6.2 «Cuándo basta con las nativas» | — | *Real-Time Collision Detection* (Ericson) |
| A11 | Barrido («swept») y túneles a alta velocidad | **C** | `13 - .../08 - Físicas a mano y fluidos.md` §3.3 «Barrido (swept): el arreglo del túnel» · `13 - .../13` §6.6 «Segmento contra círculo» (cita el *tunneling* explícito) | — | *Game Programming Patterns* / Ericson |
| A12 | Proyectiles rápidos con `collision_line` | **C** | `13 - .../13` §6.8 «`collision_line`: cuándo basta y cuándo no» · `04 - .../02 - Top-Down _ Twin-Stick.md` §4.5 y §7 («Bala rápida que atraviesa muros → `collision_line()` entre la posición actual y la siguiente») | — | Manual `collision_line` |
| A13 | Separación mínima (resolver un solapamiento ya producido) | **C** | `13 - .../08` §3.2 «Separación mínima: resolver el solapamiento» | — | Ericson, MTV |
| A14 | Particionado espacial (spatial hash; por qué no quadtree) | **C** | `13 - .../08` §4 «Particionado espacial», §4.1 «El spatial hash», §4.2 (400 partículas), §4.3 «Cuándo compensa», §4.4 «Y el quadtree, ¿por qué no?» | — | Ericson; *Game Programming Patterns* (Spatial Partition) |
| A15 | `collision_space` (novedad 2024.14) | **C** | `01 - .../08` §6 «El collision space», con la tabla `colspace.room / ui_view / ui_display` | — | Manual `collision_space` |
| A16 | **Capas / grupos de colisión** (qué bando colisiona con qué) | **P** | Resuelto de facto por dos vías: arrays de objetos y objetos padre en `move_and_collide` (`01 - .../08` §8 versión A, `[obj_pared, obj_caja, tilemap_suelo]`) y por `collision_space` (§6). Las hurtboxes por bando están en `04 - .../30 - Combate…md` §4.1 | El patrón explícito de **matriz de capas** (jugador / enemigo / proyectil-aliado / proyectil-enemigo / mundo / trigger) con máscaras de bits, y el filtrado de Box2D: **`physics_fixture_set_collision_group` no aparece ni una vez** en `04 - .../22 - Físicas con Box2D.md` §5 «Colisiones de física» | Unity/Godot *collision layers & masks*; Box2D *filtering*; manual `physics_fixture_set_collision_group` |
| A17 | Triggers y zonas (objetos invisibles que emiten señal) | **C** | `13 - .../02 - Diseño de niveles.md` §3.6 «Triggers y zonas: objetos invisibles» — código de `obj_zona` con `una_vez`/rearmado y `senal_emitir()` | — | *Level Design* (Totten); práctica estándar |
| A18 | Hitbox distinta del sprite (máscara dedicada, *feet box*) | **C** | `13 - .../04` §3.9 (tabla: jugador/proyectil/hitbox/ítem) · `04 - .../30` §5.3 `obj_hitbox` · `04 - .../03 - Shoot em up (shmup).md` §7 («*Hitbox* del jugador = sprite completo → círculo de 4-6 px») | — | Práctica estándar (danmaku) |
| A19 | Hitboxes / hurtboxes de combate, i-frames, multi-hit | **C** | `04 - .../30 - Combate cuerpo a cuerpo…md` §1.1 «Tres cajas, no una», §4.1–4.9, §5.3–5.7, §5.10 «Dibujar las cajas (depuración)» | — | *Frame data* de lucha; Maddy Thorson |
| A20 | Colisiones en 3D (caja-caja, esfera-plano, rayo-triángulo, heightmap) | **C** | `04 - .../29 - 3D en GameMaker.md` §8 «Colisiones en 3D» (Möller–Trumbore incluido) y §8 «La decisión: la mayoría de los juegos 3D colisionan en 2D» | — | Möller–Trumbore; ColMesh |
| A21 | Físicas Box2D como alternativa: fixtures, `physics_test_overlap`, `physics_raycast` | **C** | `01 - .../08` §7 «Físicas (Physics) como alternativa» · `04 - .../22` §1–§5 | (ver A16 para el filtrado) | Manual, *Physics* |
| A22 | Coste de las colisiones y cómo perfilarlo | **P** | `13 - .../08` §14 «Rendimiento: medir antes de decidir» (microsegundos por sistema) y §4.3 | `01 - Fundamentos/15 - Depuración y rendimiento.md` **no menciona colisiones ni una vez** (0 apariciones de «colis», «precise» o «máscara»): falta la sección «cuánto cuestan las colisiones» con el Profiler y el enlace a 13·08 §4 | Manual, *Debugging / Profiler* |
| A23 | Colisiones **isométricas** | **P** | `13 - .../13` §7.3 «Isométrico (rombo 2:1)» da `iso_desde_celda`/`celda_desde_iso` y el `depth = -(col + fila)` | Falta: colisionar en **rejilla lógica** en vez de en pantalla, cuándo sirve la máscara `Diamond`, el desempate cuando dos objetos comparten celda, y el *height offset* para objetos «altos» | *Isometric Game Programming*; Godot/Tiled isometric docs |
| A24 | Colisión contra **paths y curvas** | **F** | `path_*` sólo aparece como *movimiento* (`04 - .../08 - Tower Defense.md`, `04 - .../23 - IA de enemigos…md`, `04 - .../01` §5.8 plataforma móvil). **Cero apariciones de `path_` en `01 - .../08` y `01 - .../10`** | Muestrear un path para colisionar contra él, `path_get_x/y` + `path_get_number`, «¿a qué distancia del path estoy?» (con la distancia punto-segmento que ya existe en `13 - .../13` §6.4), y colisión contra una Bézier/Catmull-Rom (§4.6/§4.7 del mismo doc) | Manual, *Paths*; Ericson (distancia a curva) |

### B · Movimiento y controladores de personaje

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| B1 | Movimiento en 8 direcciones **normalizado** | **C** | `04 - .../02 - Top-Down _ Twin-Stick.md` §4.1 y §4.2 «Normalización de diagonales» · `01 - .../08` §8 versión A (paso 2) y §9 «❌ Creer que la velocidad en diagonal es igual» | — | Práctica estándar |
| B2 | Aceleración y fricción (`approach`) | **C** | `04 - .../01` §4.1 «Movimiento horizontal: aceleración y fricción» (con los valores de referencia tipo Celeste/Mario) · `04 - .../02` §5.2 · `06 - Assets y Scripts/scr_math_util.gml` (`approach`) | — | *Game Feel* (Swink) |
| B3 | `delta_time` y paso fijo (independencia del framerate) | **C** | `01 - .../08` §8 «Versión C: movimiento con delta time» · `13 - .../08` §1.3 «Independencia del framerate: `delta_time` y el paso fijo» · `13 - .../13` §12.2 «`delta_time` está en microsegundos» | — | Gaffer On Games, *Fix Your Timestep* |
| B4 | Gravedad asimétrica · salto variable · coyote time · jump buffering | **C** | `04 - .../01` §4.2–4.5 (los cuatro con código) · `06 - Assets y Scripts/scr_input_buffer.gml` | — | Maddy Thorson (*Celeste*); Kyle Pulver, *Coyote Time* |
| B5 | Subpíxel: guardar posición real y redondear al dibujar | **C** | `13 - .../03 - Pixel art y resolución.md` §4.6 «Subpíxel en el movimiento del personaje» (con el porqué de `floor()` y no `round()`) y §1.5 | — | PixelatedPope; *Celeste* source |
| B6 | **Pendientes (slopes)** | **P** | `04 - .../01` §4.6, dos párrafos: `max_x` evita que aceleres al bajar la rampa, y «`move_and_collide()` ya gestiona pendientes siempre que el sprite del suelo tenga la máscara en *Rectangle with Rotation*». El manual lo confirma («permite recorrer pendientes o escalones pequeños») | Todo lo demás: **ángulo máximo** que se puede subir, **pegarse al suelo al bajar** (si no, el personaje despega en cada cambio de pendiente), pendientes por **tile con heightmap** (45°/22,5° estilo Sonic), pendientes con velocidad conservada, y qué hacer con `image_angle` del personaje | *Sonic Physics Guide*; Shaun Spalding, *Slopes*; Higher Ground / hilo del foro oficial |
| B7 | Plataformas de un sentido (one-way) | **C** | `04 - .../01` §4.7 + §5.4 «Plataformas one-way» con `resolve_one_way()` completo y el aviso de no pasar `objPlatform` a `move_and_collide` | — | Blog oficial; Maddy Thorson |
| B8 | Plataformas móviles (que arrastran al jugador) | **C** | `04 - .../01` §4.8, §5.2 «`objPlayer` — Begin Step» (delta de `riding`) y §5.8 `objPlatformMoving` | — | Maddy Thorson, *Celeste & TowerFall physics* (Actor/Solid) |
| B9 | **Escaleras y cuerdas** | **F** | Cero. «escalera» sólo aparece como escalera de mazmorra (`04 - .../05`), como métrica de nivel (`13 - .../02`) o en apuntes de curso (`10 - .../08 - Megaman X`) | Estado `ladder`: entrar/salir, ignorar gravedad, alinearse al centro, bajar desde una one-way, subir en el borde superior; cuerdas/lianas con balanceo (que sí tienen la base de Verlet en `13 - .../08` §6.3) | Shaun Spalding, *Ladders*; *Metroidvania* design |
| B10 | Empujar cajas | **P** | `01 - .../08` §8 versión A: el bucle de `move_and_collide` detecta `object_get_parent(_col.object_index) == obj_empujable` y la empuja a media velocidad. Empuje **libre**, funcional | Falta la variante **por rejilla** (una casilla por pulsación, comprobar la casilla destino, deshacer/`undo`), que es la que pide un puzle sokoban. `04 - .../07 - Puzzle y Match-3.md` es sólo match-3 | *Sokoban* / *Baba Is You* design; Puzzlescript |
| B11 | **Wall jump y wall slide** | **P** | `04 - .../01` §8 «Cómo escalarlo», punto 3: tres líneas de prosa («detecta `place_meeting(x ± 1, y, objSolid)`; limita `vel_y` mientras estás pegado»). Sin código. `10 - .../08 - Megaman X` y `10 - .../09` los citan como temas de la serie de vídeo, no los implementan | Código real: detección de pared con margen, `wall_slide_speed`, bloqueo del input horizontal N frames tras el impulso (*wall jump lockout*), tiempo de gracia al despegarse de la pared, y no poder escalar la misma pared indefinidamente | Maddy Thorson (*Celeste* wall mechanics); Shaun Spalding, *Wall Jumping* |
| B12 | Doble salto | **C** | `04 - .../06 - Metroidvania.md` §5.4 «Habilidades en el jugador» — bloque `--- Doble salto ---` con `saltos_restantes` y reset al aterrizar · `04 - .../01` §8 punto 1 | — | Práctica estándar |
| B13 | Dash | **C** | `04 - .../06` §5.4 bloque `--- Dash ---` completo: `dash_timer`, `cooldown`, sin gravedad durante el dash, i-frames y `objAfterimage` para el rastro | — | *Celeste* / *Hollow Knight* |
| B14 | **Agarre de bordes (*ledge grab*)** | **F** | Cero. `agarrarse` aparece como nombre de habilidad-llave en `04 - .../06` §1 y `13 - .../01` §, sin implementación | Los dos sensores (mano libre, pies con pared), el *snap* a la altura del borde, el estado `hanging`, subir/soltarse, y la ventana de agarre tras el ápice del salto | *Prince of Persia*/*Hollow Knight*; Peyton Burnham, *Ledge Grab* |
| B15 | **Agacharse con cambio de máscara** | **F** | `04 - .../30` cita «agacharse» como estado de combate, y `10 - .../08` como tema del curso de Altair. El cambio de `mask_index` al agacharse y el problema de **levantarse bajo un techo** no están en ningún sitio | `mask_index = spr_mascara_agachado`, comprobación de techo con `place_meeting` antes de levantarse, y por qué no vale escalar la máscara | Manual `mask_index`; práctica estándar |
| B16 | Nadar / estar bajo el agua | **F** | `04 - .../06` §1 y §5.0 listan `nadar` como habilidad-llave del mundo, sin ninguna física. `13 - .../08` §8 cubre **flotabilidad de objetos**, no el control del jugador | Estado `swim`: gravedad reducida, velocidad terminal, impulso de brazada, entrar/salir del agua, aliento/oxígeno, y cómo se detecta el agua (tilemap con máscara de bits, ver A9) | *Metroid*/*Ecco*; Shaun Spalding, *Water* |
| B17 | Escalar / correr por paredes (*wall run*) | **F** | Cero apariciones útiles | — | *Ori*, *Katana ZERO*; práctica estándar |
| B18 | **Corrección de esquina (*corner correction* / *nudge*)** | **F** | Cero. Ni «corner correction», ni «corrección de esquina», ni ningún equivalente | El empujón de 1–3 px cuando el jugador roza una esquina al saltar o al entrar en un hueco de su mismo alto. Es la técnica que más «injusticia» quita a un plataformas y no está en la biblioteca | Maddy Thorson, *Celeste & TowerFall physics* (GDC/blog); Kyle Pulver, *Forgiveness* |
| B19 | Knockback y hit stun | **C** | `04 - .../15 - Game feel y juice.md` §4.5 «Knockback» + §5.4 (código) · `04 - .../30` §4.3 «Hitstun, blockstun y ventaja», §4.8 «Empuje, juggle y escalado de daño», §5.7 `recibir_golpe()` | — | *Frame data*; Swink, *Game Feel* |
| B20 | Movimiento en rejilla paso a paso (estilo Pokémon) | **C** | `04 - .../04 - RPG _ Action RPG.md` §5.7 «Movimiento por rejilla con tilemap de colisión» — `grid_x/grid_y`, `celda_solida()`, interpolación entre casillas | — | *Pokémon*/JRPG; DragoniteSpam |
| B21 | **Zona muerta del mando** | **P** | Umbral radial simple en `04 - .../02` §4.3 (`point_distance(0,0,_ax,_ay) > 0.3`) y §7 («ignora el stick por debajo de 0,2–0,3»); `01 - Fundamentos/12 - Input…md` lista `gamepad_get/set_axis_deadzone` y usa `abs(_eje) > 0.25` | Falta el tratamiento correcto: **axial vs radial vs radial escalada**, el **salto en el borde** de la zona muerta (a 0,26 el personaje arranca ya a un 26 % de velocidad), la curva de respuesta (cuadrática) y la zona muerta **exterior** para llegar al 100 % antes del tope físico | Josh Sutphin, *Doing Thumbstick Dead Zones Right*; manual `gamepad_set_axis_deadzone` |
| B22 | Físicas de vehículos (arcade, derrape, tracción) | **C** | `04 - .../12 - Carreras y vehículos.md` §4.1 «Física arcade vs simulación», §4.2 «La reducción lateral», §4.3 «Giro dependiente de la velocidad», §4.4 «Terreno», §5.1 (código completo) | — | Marco Monster, *Car Physics for Games* |
| B23 | Controlador de personaje completo (máquina de estados + animación) | **C** | `04 - .../01` §5.5 «Máquina de estados» (`enum PlayerState`, enter/step por estado) · `06 - Assets y Scripts/scr_state_machine.gml` · `07 - Ecosistema/17 - SnowState…md` · `13 - .../04` §3.8 «Del estado al sprite» (tabla estado→animación frente a la cascada de `if`) | — | *Game Programming Patterns* (State); SnowState |
| B24 | Profundidad por Y (*Y-sort*) en top-down | **C** | `04 - .../02` §4.4 «Depth sorting por Y» (con el porqué de `bbox_bottom` y no `y`) + §5.6 `objDepthSorter` · §7 («Actualizar `depth` en el Draw no tiene efecto») | — | Práctica estándar |

### C · Cámara

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| C1 | Seguir al jugador con suavizado (`lerp`) | **C** | `01 - .../10` §7 «Seguir al jugador manualmente» (con `round()` y el aviso de End Step) · `06 - Assets y Scripts/scr_camera.gml` (`cam_update`, con `lerp_dt`) · `03 - Cursos (YouTube)/42 - PixelatedPope…Parte 2` §12 «Suavizado con `lerp()`» | — | PixelatedPope; manual *Cameras And Viewports* |
| C2 | Deadzone | **C** | `04 - .../01` §4.9 y §5.7 `objCamera` · `06 - .../scr_camera.gml` (`cam_set_deadzone`) · `03 - .../41 - PixelatedPope Parte 1` §12 «Los bordes: la caja invisible» · `03 - .../20 - DragoniteSpam Viewports y Cámaras` §7 | — | Keren (*camera window*), PixelatedPope |
| C3 | Look-ahead | **C** | `04 - .../01` §5.7 (por `vel_x`) · `04 - .../02` §5.7 (hacia el ratón) · `04 - .../12` §5.6 (por ángulo del coche) · `06 - .../scr_camera.gml` (`cam_set_lookahead`, con suavizado del propio look-ahead) · `03 - .../07 - Sky LaRell Parte 7` §13 | — | Keren; PixelatedPope |
| C4 | Límites de sala y sala más pequeña que la vista | **C** | `06 - .../scr_camera.gml` `cam_set_bounds` + el caso «la sala es más estrecha que la vista: centramos» · `03 - .../43 - PixelatedPope Parte 3` §18 «Cuando la room es más pequeña que el view» · `01 - .../10` §7 | — | PixelatedPope |
| C5 | **Zonas de cámara por región dentro de una sala** | **F** | Cero: ni «zona de cámara», ni «límites de cámara», ni «camera bounds». Sólo existe el *clamp* a la room entera (C4) | El objeto `obj_camera_zone` que define un rectángulo de encuadre, la detección de en qué zona está el jugador, y el paso suave de una zona a otra. Es lo que hace que un pasillo se vea como pasillo y una sala de jefe se vea entera | Itay Keren, *Scroll Back* (region-based camera); *Hollow Knight*/*Super Metroid* |
| C6 | Transición de cámara entre salas / pantallas | **P** | `04 - .../06 - Metroidvania.md` §4.1 y §5.1 «Transiciones entre rooms» (`objTransitionZone` + `objSpawnPoint` con `entry_id` + fundido) · `01 - .../10` §9 «Transiciones entre rooms» (objeto persistente con fade) | Todo lo que no es un fundido a negro: el **desplazamiento pantalla-a-pantalla** estilo Zelda 1 / Metroid (la cámara *viaja* mientras el juego se congela), el reencuadre al cruzar de zona dentro de la misma sala, y el `snap_to_target` al reaparecer (que sí está en `03 - .../43` §5) | Keren, *Scroll Back*; *Zelda*/*Metroid* |
| C7 | Pantalla partida (split screen) | **C** | `01 - .../10` §7 «Pantalla partida (split screen)» (dos viewports + `camera_create_view` con target) · `03 - .../20 - DragoniteSpam` §10 «Varios viewports: pantalla dividida» · `04 - .../14 - Multijugador.md` §8 lo propone como siguiente paso | — | Manual, *Views And Viewports* |
| C8 | **Cámara de varios jugadores con zoom dinámico** (mantener a todos en pantalla) | **F** | Cero. Sólo hay split screen estático (C7) y zoom por velocidad en carreras (C10) | El bounding box de todos los jugadores → tamaño de vista con margen, `camera_set_view_size` suavizado, mínimo y máximo de zoom, qué hacer si un jugador se aleja demasiado (*tether* o teletransporte), y la interacción con el pixel-perfect (zoom no entero = píxeles rotos, ver `03 - .../43` §17) | *Smash Bros*/*Towerfall*; Keren |
| C9 | Screen shake por **trauma** | **C** | `04 - .../15 - Game feel y juice.md` §4.1 y §5.1 «Cámara con shake por trauma» — `trauma²`, decay, `camera_set_view_angle`, cita explícita a Squirrel Eiserloh · `06 - .../scr_camera.gml` (`cam_shake`, aleatorio en círculo con decaimiento lineal) · `03 - .../43` §12–14 (la clase `Shake`) | — | Squirrel Eiserloh, *Math for Game Programmers: Juicing Your Cameras With Math* (GDC 2016) |
| C10 | Zoom de cámara | **C** | `04 - .../15` §5.1 (`cam_zoom`/`cam_zoom_target` suavizado) · `03 - .../43` §15 «Zoom: el struct con seis propiedades», §16 «conservar el punto central», §17 «La distorsión de píxel al hacer zoom» · `04 - .../12` §5.6 (zoom por velocidad) · `04 - .../06` §5.4 (zoom al desbloquear habilidad, con el error de no restaurarlo) | — | PixelatedPope |
| C11 | **Platform snapping** (la cámara vertical se ancla al suelo) | **F** | Cero | La cámara vertical que **no** sigue el salto: se queda anclada a la última plataforma pisada y sólo se mueve al aterrizar en otra. Es el comportamiento de *Super Mario World*, *Celeste* y casi todo plataformas serio; sin él la pantalla botea con cada salto | Keren, *Scroll Back* (platform snapping); *Super Mario World* |
| C12 | **Camera window** (Keren) | **F** | El único hit de «camera window» es `__obj_camera_window` en `03 - .../43` §11, que es un **nombre de script** de PixelatedPope para los métodos de la ventana del sistema operativo — no el concepto | La ventana de encuadre asimétrica (más margen delante que detrás, distinta en X y en Y), y su relación con la deadzone simétrica que sí está documentada (C2) | Keren, *Scroll Back* |
| C13 | **El marco de Itay Keren, «Scroll Back» (GDC 2015)** | **F** | **Cero apariciones de «Keren» ni de «Scroll Back» en toda la biblioteca** | La taxonomía completa que ordena todo lo anterior: *position-locking*, *camera window*, *attraction/edge snapping*, *cue focus*, *region-based*, *projection focus*, *gesture/manual control*, *dual-forward focus*, y el marco de decisión «qué cámara pide mi juego». La biblioteca tiene las **piezas** (C1–C4, C9, C10) pero no el **mapa** que dice cuál usar | Itay Keren, *Scroll Back: The Theory and Practice of Cameras in Side-Scrollers*, GDC 2015 |
| C14 | Cinemáticas de cámara (paths, tweens, Sequences) | **P** | `04 - .../00 - Anatomía de un juego completo.md` §4 «Intro, prólogo y cinemáticas» — una línea: «Cinemática scriptada — cámara que se mueve … con Tweens sobre la cámara»; el resto de §4 es vídeo pregrabado. `04 - .../01` §8 punto 9 lo cita como siguiente paso. `13 - .../04` §6 documenta Sequences a fondo pero **la tabla `seqtracktype_*` no tiene pista de cámara** | El sistema real: encolar objetivos de cámara, mover la cámara por un `path` con `path_get_x/y`, quitar y devolver el control al jugador (`camera_set_view_target(noone)`, ver `03 - .../42` §10), barras cinematográficas, y que sea **saltable** (el propio 04·00 lo exige) | Manual *Sequences*/*Paths*; práctica estándar |
| C15 | Cámara pixel-perfect / subpíxel | **C** | `13 - .../03 - Pixel art y resolución.md` §1.5 «Pixel-perfect frente a subpíxel», §6.5 «Posiciones fraccionarias y el redondeo de la cámara» (guardar decimales, redondear sólo al entregar) · `03 - .../41`–`44` (los cuatro capítulos de PixelatedPope) · `06 - .../scr_camera.gml` (`round` final + `cam_fit_window`) | — | PixelatedPope, *Cameras and Resolution* |
| C16 | Cámaras en 3D (primera persona, orbital, tercera persona) | **C** | `04 - .../29 - 3D en GameMaker.md` §1 «La cámara 3D, completa» (`camera_set_view_mat`/`_proj_mat`, `matrix_build_lookat`) y §7 «Control de cámara» (§7 primera persona con ratón bloqueado, orbital, tercera persona con seguimiento suave) | — | Manual, *Cameras*; DragoniteSpam 3D |
| C17 | Viewport a surface / `application_surface` y escalado | **C** | `01 - .../10` §8 «Viewports a surfaces» · `03 - .../42` §7 «Superficie de aplicación: rejilla estricta frente a subpíxeles» · `03 - .../44` §8 «Dibujar tu juego en una caja» | — | PixelatedPope |
| C18 | Culling y desactivación fuera de vista | **C** | `01 - .../10` §7 «Frustum culling» (`gpu_set_sprite_cull`, `sphere_is_visible`) y §3 «Activar / desactivar instancias por capa» · `01 - .../09` y `01 - .../15` (`instance_activate_region`) | — | Manual |
| C19 | Parallax con capas | **C** | `01 - .../10` §3 «Ejemplo: parallax con capas» · `13 - .../03` §6.x (el problema del parallax con decimales) · `13 - .../02` §3.5 «Parallax: decisiones de diseño» | — | Práctica estándar |
| C20 | `camera_set_view_target` y por qué desactivarlo al ir por código | **C** | `01 - .../10` §7 «Funciones de configuración» · `03 - .../42` §10 «Por qué `camera_set_view_target(noone)` es obligatorio» | — | Manual; PixelatedPope |

**Recuento:** 62 temas · **CUBIERTO 42** (68 %) · **PARCIAL 11** (18 %) · **FALTA 9** (14 %).

---

## 2. Propuestas priorizadas

### 🔴 ALTA

**P1 · `04 - Recetas por género/32 - Traversal en plataformas - pendientes, paredes, escaleras y bordes.md`**
Cierra B6, B9, B11, B14, B15, B16, B17, B18 y B10 (variante rejilla) — el mayor agujero del
dominio, y el que más se nota al hacer un juego real. Contenido: pendientes de verdad (ángulo
máximo, pegado al suelo en bajada, heightmap por tile estilo Sonic, qué hace y qué no hace
`move_and_collide`); wall slide y wall jump con código, *lockout* del input y anti-escalada;
*ledge grab* con los dos sensores y el *snap* al borde; agacharse cambiando `mask_index` y la
comprobación de techo antes de levantarse; escaleras y cuerdas (estado, entrada/salida,
alineado, bajar desde una one-way); nadar (gravedad reducida, brazada, entrada/salida, aliento);
corrección de esquina de 1–3 px; y empuje de cajas por rejilla con deshacer. Se apoya en el
`objPlayer` y la máquina de estados que ya existen en `04 · 01` §5.5 — **extiende, no duplica**.

**P2 · `13 - Diseño y producción de videojuegos/14 - Cámaras de juego - encuadre, seguimiento y control.md`**
Cierra C5, C8, C11, C12, C13 y completa C6 y C14. Es la pieza que falta como **disciplina**: la
biblioteca tiene la API (`01 · 10`), el script (`06/scr_camera.gml`), el shake (`04 · 15`) y el
pixel-perfect (`13 · 03` + `03 · 41–44`), pero nadie dice **qué cámara pide cada juego**.
Contenido: el marco de Itay Keren (*Scroll Back*, GDC 2015) traducido y aplicado a GML —
position-locking, camera window, attraction/edge snapping, region-based, cue focus, projection
focus, dual-forward focus—; **platform snapping** vertical; **zonas de cámara** por región con
`obj_camera_zone` y transición entre zonas; **transición pantalla-a-pantalla** estilo Zelda/Metroid;
**cámara multijugador** con bounding box y zoom dinámico (y su choque con el pixel-perfect);
cinemáticas con objetivos encolados, `path`, barras y salto. Enlaza a lo existente en vez de
reescribirlo.

**P3 · Sección nueva en `01 - Fundamentos/08 - Movimiento y colisiones.md` §4: «Elegir la forma de la máscara»**
Cierra A2. Media página: tabla de las seis opciones (Rectangle · Rectangle with Rotation ·
Ellipse · Diamond · Precise · Precise per frame / `sepmasks`) con qué usar para qué y qué cuesta
cada una, las constantes `bboxkind_*`, `sprite_collision_mask()` en tiempo de ejecución y su
limitación documentada (no admite rectángulo girado), y el enlace al espejo del manual. Hoy el
dato existe **sólo** en el manual espejado y en inglés conceptual, no en la explicación propia.

### 🟡 MEDIA

**P4 · Sección nueva en `01 - Fundamentos/08` §6 bis: «Bandos y capas de colisión»**
Cierra A16. El patrón de matriz «quién colisiona con quién» (jugador / enemigo / proyectil
aliado / proyectil enemigo / mundo / trigger) con objetos padre y arrays en `move_and_collide`,
la variante con máscara de bits cuando hay muchos bandos, cuándo `collision_space` **no** es la
respuesta, y el filtrado de Box2D (`physics_fixture_set_collision_group`) — que hoy no aparece
ni una vez en `04 · 22` §5.

**P5 · Sección nueva en `04 - Recetas por género/22 - Físicas con Box2D.md` §5 bis + ampliación de A23**
Dos añadidos pequeños que caben juntos si se prefiere: (a) filtrado de colisiones de Box2D
(grupos, categorías, sensores), que es la mitad de §5; (b) **colisiones isométricas** como
sección nueva en `13 · 13` §7.3 — colisionar en rejilla lógica, la máscara `Diamond`, el
desempate de `depth` en celda compartida y el offset por altura.

**P6 · Ampliación de `01 - Fundamentos/12 - Input…md`: «Zona muerta bien hecha»**
Cierra B21. Axial vs radial vs radial escalada, el salto en el borde de la zona muerta, la curva
de respuesta cuadrática, la zona muerta exterior, y por qué `gamepad_set_axis_deadzone()` del
motor no basta para un twin-stick. Referencia: Josh Sutphin, *Doing Thumbstick Dead Zones Right*.

**P7 · Sección nueva en `01 - Fundamentos/15 - Depuración y rendimiento.md`: «Cuánto cuestan las colisiones»**
Cierra A22. El documento de rendimiento **no menciona las colisiones ni una vez**. Media página:
qué cuesta `precise` frente a AABB, por qué `all` es caro, cuándo el número de instancias obliga
a `instance_deactivate_region` o a una rejilla, y el enlace a `13 · 08` §4 (spatial hash) y §14
(medir en microsegundos), que ya está escrito.

### 🟢 BAJA

**P8 · Sección en `13 - .../13 - Matemáticas aplicadas al juego.md` §6.9: «Colisión contra paths y curvas»**
Cierra A24. Muestrear un `path` (`path_get_x/y`, `path_get_number`), «¿a qué distancia del path
estoy?» reutilizando la distancia punto-segmento de §6.4, y colisión contra Bézier/Catmull-Rom
reutilizando §4.6/§4.7. Todo el material auxiliar ya existe en el mismo documento: es coser, no
escribir de cero.

---

## 3. Limitaciones

- **No pude usar `WebSearch`**: la sesión había agotado su presupuesto (200/200) antes de mi
  primera consulta. La verificación de fuentes externas (Keren GDC 2015, Maddy Thorson, Josh
  Sutphin, *Sonic Physics Guide*) se apoya en mi conocimiento del dominio, **no** en una
  comprobación en vivo. Los nombres, títulos y años que cito son los que conozco como correctos,
  pero conviene revalidar las URL antes de escribirlas en un documento de la biblioteca.
- **No consulté `gamemaker.io` ni `manual.gamemaker.io` por red.** Todas las verificaciones
  contra el manual son contra el **espejo local** `09 - Manual oficial/manual-lts-2026-es/`, que
  la propia biblioteca declara completo y con fecha 1-sep-2026. Verifiqué directamente
  `sprite_collision_mask.md` (las seis formas de máscara y su coste) y `move_and_collide.md`
  («permite recorrer pendientes o escalones pequeños»), que son los dos puntos donde mi veredicto
  dependía del manual.
- **No abrí `11 - Código descargado/`** (148 repos de terceros): el brief lo excluye de la lista
  de grep y su `_CATALOGO.md` no es documentación propia. Es posible que alguna librería
  descargada resuelva B9/B11/B14 (escaleras, wall jump, ledge grab) sin que la biblioteca lo
  documente; eso no cambia el veredicto —**la biblioteca no lo explica**— pero sí podría
  abaratar P1.
- **La carpeta `03 - Cursos (YouTube)/` no estaba en el grep del brief**, pero contiene cuatro
  capítulos completos de PixelatedPope sobre cámaras y resolución (`41`–`44`) más `07` y `20`.
  Los he contado como CUBIERTO donde aportan, señalando siempre que son **transcripciones de
  curso** —autoridad 6 de 6 según `AGENTS.md` §1— y no documentación propia verificada. Si el
  criterio del proyecto es que un curso no cuenta como cobertura, C1, C2, C4, C7, C10 y C17
  bajarían a PARCIAL y P2 crecería bastante.
- **No compilé nada.** La auditoría es de cobertura documental; no verifiqué que el GML citado
  compile (la biblioteca ya tiene `validar-codigo-gml.py` y `validar-compilacion.sh` para eso).
