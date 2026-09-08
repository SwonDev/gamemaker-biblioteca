# Mapa por disciplina — qué leer, en qué orden

Rutas relativas a la raíz de la biblioteca, la que resuelve `$BIB` (ver la cabecera de la skill).
Cada bloque va del **principio** (por qué) al **código** (cómo en GameMaker). Lee lo primero
antes de escribir nada; lo demás, cuando la tarea lo pida. `_indice/sincronizar-skill.py`
comprueba que todas estas rutas existen: si una falla, el documento se renombró y hay que
actualizar este mapa.

---

## Diseño de juego (mecánicas, core loop, balance, dificultad, GDD)

1. `13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md`
2. `04 - Recetas por género/00 - Anatomía de un juego completo.md` — el arco entero y el checklist de «juego completo»
3. `04 - Recetas por género/15 - Game feel y juice.md` — desde el primer día, no al final
4. `04 - Recetas por género/_INDICE-RECETAS.md` — qué receta de género aplica y en qué orden aprenderlas

## Diseño de niveles

1. `13 - Diseño y producción de videojuegos/02 - Diseño de niveles.md`
2. `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md` — el Room Editor, tiles, capas, cámaras
3. `12 - Utilidades e integraciones/05 - Pipeline de arte, audio y niveles.md` — LDtk y Tiled → GameMaker
4. `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` §4 — el flujo Tiled → GameMaker que funciona
5. Cursos: `03 - Cursos (YouTube)/16 - DragoniteSpam - Getting Started - Editor de Rooms, Tiles y Tile Sets.md`, `03 - Cursos (YouTube)/17 - DragoniteSpam - Getting Started - Autotiles.md`

## Generación procedural

1. `04 - Recetas por género/05 - Roguelike y generación procedural.md` — semillas, BSP, random walk, flood fill, loot
2. `13 - Diseño y producción de videojuegos/07 - Generación procedural avanzada.md` — ruido, autómatas celulares, Poisson, WFC, gramáticas, piezas
3. `06 - Assets y Scripts/scr_grid_pathfinding.gml` — A* para validar conectividad

## Pixel art, resolución y escalado

1. `13 - Diseño y producción de videojuegos/03 - Pixel art y resolución.md`
2. `03 - Cursos (YouTube)/41 - PixelatedPope - Cámaras y Resolución 2026 - Parte 1 - Principiante.md` (y partes 2–4: `42`, `43`, `44`) — la referencia de cámaras y resolución
3. `03 - Cursos (YouTube)/36 - DragoniteSpam - Getting Started - Por Qué Todo se ve Borroso.md`
4. `08 - Referencia GML completa/08 - Texturas y grupos de texturas.md` — texture pages, filtrado
5. `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` — assets libres, herramientas, paletas

## Animación (sprites, Sequences, Animation Curves, tweens)

1. `13 - Diseño y producción de videojuegos/04 - Animación de sprites, Sequences y Animation Curves.md`
2. `06 - Assets y Scripts/scr_tween.gml` — tweens y easings listos
3. `04 - Recetas por género/15 - Game feel y juice.md` §4.3–4.4 — squash & stretch, easing
4. `08 - Referencia GML completa/22 - Animación esqueletal (Spine).md` — si hay huesos

## UI y UX de juego (HUD, menús, opciones, accesibilidad)

1. `13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md`
2. `02 - Novedades 2026/04 - UI Layers y Flexpanels.md` — el sistema de UI de 2026
3. `04 - Recetas por género/18 - Menús con scroll y navegación.md`
4. `04 - Recetas por género/25 - Menú de opciones y ajustes.md`
5. `04 - Recetas por género/27 - Accesibilidad.md`
6. `07 - Ecosistema/18 - Scribble - texto rico (guía en español).md` — texto con formato
7. `04 - Recetas por género/21 - Localización e idiomas (con traducción por IA).md`

## Arquitectura y estructura del proyecto

1. `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md`
2. `05 - Referencia/04 - Convenciones y estilo GML.md` — nombres, carpetas, JSDoc, checklist
3. `04 - Recetas por género/16 - Señales y desacoplamiento.md`
4. `01 - Fundamentos/04 - Structs y constructores (POO en GML).md`
5. `01 - Fundamentos/06 - Eventos y ciclo del juego.md` — orden de eventos, delta_time, time sources
6. `06 - Assets y Scripts/README.md` — los 9 scripts base (estado, tween, pool, guardado, cámara, input, A*, debug, matemáticas)
7. `07 - Ecosistema/15 - Qué hacen de verdad los proyectos reales.md`

## Físicas (a mano, Box2D, fluidos)

1. `13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md` — cinemática, salto por diseño, muelles, Verlet, agua
2. `01 - Fundamentos/08 - Movimiento y colisiones.md` — `move_and_collide` y colisiones del motor
3. `04 - Recetas por género/01 - Plataformas 2D.md` — la física de plataformas que sí funciona
4. `04 - Recetas por género/22 - Físicas con Box2D.md` — cuándo Box2D, joints y partículas de fluido
5. `04 - Recetas por género/12 - Carreras y vehículos.md` — física arcade de vehículos

## Matemáticas para juegos

1. `13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md` — por problema
2. `08 - Referencia GML completa/10 - Matemáticas.md` y `08 - Referencia GML completa/11 - Vectores, matrices y ángulos.md` — por función
3. `06 - Assets y Scripts/scr_math_util.gml`

## IA de enemigos y comportamiento

1. `04 - Recetas por género/23 - IA de enemigos y steering behaviors.md` — movimiento: seek, flee, wander, paths, flocking
2. `04 - Recetas por género/31 - IA de decisión - árboles de comportamiento, utility y GOAP.md` — decisión: FSM → BT → utility → GOAP
3. `06 - Assets y Scripts/scr_state_machine.gml` y `07 - Ecosistema/17 - SnowState - máquinas de estado (guía en español).md`
4. `06 - Assets y Scripts/scr_grid_pathfinding.gml`

## Combate

1. `13 - Diseño y producción de videojuegos/18 - Diseño de combate y de jefes.md` — **decide primero**: legibilidad, kit, tells, jefes por fases
2. `04 - Recetas por género/30 - Combate cuerpo a cuerpo - hitboxes, hurtboxes y combos.md` — frame data, cajas, combos, i-frames
3. `04 - Recetas por género/32 - Sistema de daño y efectos de estado.md` — tipos de daño, resistencias, escudos, veneno y aturdimiento
4. `04 - Recetas por género/34 - Combate a distancia - armas, munición y balística.md` — cargador, dispersión, hitscan, cobertura
5. `04 - Recetas por género/33 - Diseño de enemigos, encuentros y director de combate.md` — el grupo: arquetipos, fichas de ataque, amenaza, director
6. `04 - Recetas por género/36 - Habilidades, enfriamientos y recursos de combate.md` — habilidades como datos, estamina y maná
7. `04 - Recetas por género/35 - Combate por turnos y táctico en rejilla.md` — si el combate no es en tiempo real
8. `04 - Recetas por género/15 - Game feel y juice.md` — hit stop, shake, knockback, y el flash al recibir daño
9. `06 - Assets y Scripts/scr_input_buffer.gml` y `06 - Assets y Scripts/scr_state_machine.gml`

## Sonido y música

1. `13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md` — el oficio
2. `01 - Fundamentos/13 - Audio.md` — la API
3. `02 - Novedades 2026/07 - Audio - buses y efectos.md` — buses y efectos (son structs)
4. `04 - Recetas por género/26 - Música adaptativa por capas.md`
5. `04 - Recetas por género/19 - Programación rítmica (juegos de ritmo).md`
6. `07 - Ecosistema/21 - Vinyl - audio avanzado (guía en español).md`

## Gráficos avanzados (dibujo, shaders, superficies, luz, partículas)

1. `01 - Fundamentos/11 - Dibujo y renderizado.md`
2. `08 - Referencia GML completa/05 - Superficies.md`, `08 - Referencia GML completa/06 - Shaders.md`, `08 - Referencia GML completa/04 - Color y blending.md`
3. `04 - Recetas por género/24 - Iluminación 2D.md`
4. `02 - Novedades 2026/05 - Sistema de partículas nuevo.md` y `02 - Novedades 2026/06 - Gráficos - SVG, SDF, FX y superficies.md`
5. `04 - Recetas por género/29 - 3D en GameMaker.md` — si el juego es 3D o 2.5D

## Narrativa, diálogos y cinemáticas

1. `13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md`
2. `04 - Recetas por género/10 - Visual Novel y narrativa.md`
3. `07 - Ecosistema/19 - Chatterbox - diálogos Yarn (guía en español).md`
4. `04 - Recetas por género/00 - Anatomía de un juego completo.md` §4 — intro, prólogo, vídeo, cinemáticas

## Input (teclado, ratón, mando, táctil)

1. `01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md`
2. `10 - Cursos en español/10 - Herramientas de la comunidad - Input y Scribble.md` — la librería Input (API en PascalCase)
3. `06 - Assets y Scripts/scr_input_buffer.gml`
4. `04 - Recetas por género/28 - Juegos para móvil (táctil).md`

## Guardado, datos y persistencia

1. `01 - Fundamentos/14 - Persistencia y archivos.md`
2. `06 - Assets y Scripts/scr_save_load.gml`
3. `07 - Ecosistema/20 - SNAP - datos y formatos (guía en español).md`
4. `08 - Referencia GML completa/16 - Buffers.md` y `08 - Referencia GML completa/17 - Ficheros y directorios.md`

## Multijugador y red

1. `04 - Recetas por género/14 - Multijugador.md`
2. `12 - Utilidades e integraciones/04 - Multijugador y red.md` — Photon, Colyseus, estado real
3. `04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md`

## Móvil

1. `04 - Recetas por género/28 - Juegos para móvil (táctil).md`
2. `01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md` §5 y §8 bis — táctil, gestos, teclado virtual
3. `04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md`

## Rendimiento y depuración

1. `01 - Fundamentos/15 - Depuración y rendimiento.md` — Feather, debugger, Debug Overlay, GC, checklist
2. `06 - Assets y Scripts/scr_debug.gml` y `06 - Assets y Scripts/scr_pool.gml`
3. `12 - Utilidades e integraciones/01 - Herramientas del flujo de trabajo.md` §4 — GMBenchmark y frameworks de test

## Testing y QA

1. `13 - Diseño y producción de videojuegos/10 - Testing y QA.md`
2. `12 - Utilidades e integraciones/01 - Herramientas del flujo de trabajo.md` §4
3. `05 - Referencia/04 - Convenciones y estilo GML.md` §7–8 — aserciones y checklist antes de compilar

## Producción, alcance, publicación y monetización

1. `13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md`
2. `05 - Referencia/02 - Publicar y exportar.md` y `01 - Fundamentos/16 - Exportar y publicar.md`
3. `04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md`
4. `07 - Ecosistema/08 - itch.io - jams, assets y juegos.md`

## Herramientas, ecosistema y dónde preguntar

1. `12 - Utilidades e integraciones/_INDICE-UTILIDADES.md`
2. `07 - Ecosistema/13 - GM CLI - la línea de comandos.md` — `gm-cli` a fondo y sus trampas en macOS
3. `07 - Ecosistema/14 - IA y GameMaker.md` — MCP, agentes, lo que existe
4. `07 - Ecosistema/10 - Comunidades y dónde preguntar.md`
5. `11 - Código descargado/_CATALOGO.md` — 148 repositorios descritos en español

## Qué cambió en 2026 y migrar código antiguo

1. `02 - Novedades 2026/01 - Resumen LTS 2026.0.md`
2. `01 - Fundamentos/03 - Handles - el cambio clave de 2026.md` — la causa nº 1 de «no compila»
3. `02 - Novedades 2026/02 - Cambios en GML 2026.md`
4. `02 - Novedades 2026/03 - GMRT - El nuevo runtime.md` y `02 - Novedades 2026/10 - Futuro - roadmap 2026-2028.md`

## Lo que el manual no cuenta

- `08 - Referencia GML completa/20 - Lo que el manual no documenta.md` — funciones que existen sin página
- `08 - Referencia GML completa/21 - Constantes que el manual abrevia.md` — `pi`, `argument15`, `ev_*`…
- `09 - Manual oficial/README.md` — cómo está espejado el manual y qué se tradujo

## VFX y shaders de efecto

1. `04 - Recetas por género/39 - VFX - diseño y catálogo de efectos.md` — el oficio: capas, timing, recetas por efecto, trails, decals
2. `08 - Referencia GML completa/23 - Recetario de shaders de efecto.md` — hit flash, CRT, glitch, shockwave, bloom, LUT y la cadena con ping-pong
3. `04 - Recetas por género/24 - Iluminación 2D.md` — de la surface oscura a normal maps, sombras, god rays y ciclo día/noche
4. `02 - Novedades 2026/06 - Gráficos - SVG, SDF, FX y superficies.md` §4.5 — el catálogo completo de los 42 FX de capa

## Cámaras

1. `13 - Diseño y producción de videojuegos/19 - Cámaras de juego - encuadre, seguimiento y control.md` — el marco de Keren y qué cámara pide cada género
2. `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md` §5-§8 — la API
3. `06 - Assets y Scripts/scr_camera.gml` — deadzone, look-ahead, shake y zoom punch

## El documento de diseño y la teoría

1. `13 - Diseño y producción de videojuegos/14 - El documento de diseño - del one-pager al GDD completo.md` — incluida la versión que un agente puede implementar
2. `13 - Diseño y producción de videojuegos/15 - Teoría del diseño - el canon en una tarde.md`
3. `13 - Diseño y producción de videojuegos/16 - Progresión - árboles de habilidades, desbloqueos y meta-progresión.md`
4. `13 - Diseño y producción de videojuegos/17 - Diseño de puzzles.md`
5. `13 - Diseño y producción de videojuegos/22 - Diseño de mundo y exploración.md`
6. `13 - Diseño y producción de videojuegos/21 - Balance por simulación - Monte Carlo, Machinations y estrategias dominantes.md`

## Negocio, equipo y ética

1. `13 - Diseño y producción de videojuegos/20 - Modelo de negocio, monetización y ética del diseño.md`
2. `13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md` §12-§13 — encargar trabajo, derechos, crunch y salud
3. `04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md` — la API

## Patrones y extensiones

1. `13 - Diseño y producción de videojuegos/23 - Catálogo de patrones en GML.md` — los 19 de Nystrom, dónde está cada uno, y el veredicto sobre ECS
2. `07 - Ecosistema/22 - Crear una extensión nativa (guía en español).md` — ⚠️ el asset Extensión **no** se crea con `resourcetool`, solo desde el IDE
3. `04 - Recetas por género/43 - Modding y contenido externo.md` — scripts del jugador sin abrir un agujero

## Empezar sin escribir código

1. `01 - Fundamentos/17 - GML Visual (Drag and Drop).md` — las 27 familias de acciones y la tabla de equivalencias acción → GML
2. `RUTA.md` — nivel 0 → 1
