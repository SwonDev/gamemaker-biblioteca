# Recetas por género — GameMaker LTS 2026.0 (IDE 16 / Runtime 23)

Biblioteca práctica para construir **cualquier tipo de juego** en GameMaker.
Cada archivo es autocontenido: puedes leerlo en cualquier orden, pero el
**orden recomendado** está pensado para construir fundamentos antes de
complejidad.

## Entorno asumido

| Elemento | Valor |
|---|---|
| Versión | GameMaker **LTS 2026.0** (IDE 16 / GMS2 Runtime 23), publicada el 21 de mayo de 2026 |
| Runtime | **GMS2 Runtime** (marcado como *feature complete* en LTS26; soporte hasta al menos Q1 2028) |
| GMRT | El nuevo runtime **no** se usa aquí. Está en Beta y sale de Beta para escritorio a lo largo de 2026 |
| Lenguaje | GML moderno: structs, constructores, `method()`, `static`, arrays, string templates |
| Evitar por defecto | `ds_list` / `ds_map` salvo que aporten algo claro (ordenadas, `ds_priority`, etc.) |

> **Nota importante sobre el runtime:** LTS26 marca el GMS2 Runtime como
> *feature complete*. Las funciones nuevas y las peticiones de características
> solo se consideran para GMRT. El GMS2 Runtime sigue recibiendo actualizaciones
> de SDK y correcciones críticas hasta al menos el Q1 de 2028. Todo el código de
> estas recetas está escrito para el runtime GMS2, que es el que vas a usar en
> un proyecto serio a día de hoy.

## Convenciones usadas en todos los archivos

- Prefijos de recursos: `spr_` sprites · `obj_` objetos · `rm_` rooms ·
  `scr_` scripts · `snd_` sonidos · `shd_` shaders · `fnt_` fuentes
- Nombres de recursos en `PascalCase` (`objEnemySlime`)
- Variables de instancia en `snake_case` (`move_speed`, `coyote_timer`)
- Variables locales con guion bajo: `var _speed`, `var _input_x`
- Constantes en `UPPER_SNAKE_CASE` (`GRAVITY`, `TILE_SIZE`)
- Variables pseudo-privadas de struct con doble guion bajo: `__timer`
- **Nunca** uses nombres reservados (`x`, `y`, `speed`, `direction`, `id`,
  `depth`, `score`, `health`, `gravity`). Usa `vel_x`, `vel_y`, `hp`,
  `grav`, `depth_sort`.

---

## Tabla de recetas

| # | Género | Dificultad | Sistemas que practica | Cuándo aprenderlo |
|---|---|---|---|---|
| [**00**](<./00 - Anatomía de un juego completo.md>) | **Anatomía de un juego completo** | — | **Léelo primero.** El arco entero: splash → menú → prólogo/vídeo → zonas → pausa → guardado → endgame → créditos, y el orden de montaje | **Antes de desarrollar un juego completo** |
| [01](<./01 - Plataformas 2D.md>) | **Plataformas 2D** | Básica | Movimiento con `move_and_collide`, gravedad, coyote time, jump buffering, salto variable, máquina de estados, cámara con deadzone | **1.º** — es la base del *game feel* |
| [02](<./02 - Top-Down _ Twin-Stick.md>) | **Top-Down / Twin-Stick** | Básica | Vector de movimiento, normalización de diagonales, rotación hacia el ratón, disparo, depth sorting por Y | **2.º** — mismo motor, otra cámara |
| [03](<./03 - Shoot em up (shmup).md>) | **Shoot 'em up** | Básica‑Media | Scroll, oleadas dirigidas por datos, patrones de balas, *object pooling*, jefes con FSM | **3.º** — tu primer sistema data-driven |
| [11](<./11 - Arcade y juegos de un botón.md>) | **Arcade / un botón** | Básica | *Juice*, screen shake, hit stop, partículas, puntuación, high scores | **4.º** (o en paralelo) — es la capa de pulido |
| [15](<./15 - Game feel y juice.md>) | **Game feel y juice** | Media | Tween helper con structs, cámara con shake, squash & stretch, knockback, capas de feedback | **Transversal** — consúltalo mientras haces los demás |
| [16](<./16 - Señales y desacoplamiento.md>) | **Señales y desacoplamiento** | Media | Patrón observador en 40 líneas: `senal_emitir`/`senal_escuchar`, oyentes zombis, cuándo NO usarlo | **Transversal** — en cuanto tengas 3+ sistemas que reaccionan a lo mismo |
| [17](<./17 - Interoperabilidad con la web (HTML5).md>) | **Interoperabilidad con la web (HTML5)** | Media | Extensiones `.js`, prefijo `gmcallback_`, `localStorage`, `http_*` y CORS, qué NO puedes hacer en web, autenticación con tokens, el techo real de memoria WASM/móvil | Antes de publicar en itch.io, GX.games o tu propia web |
| [18](<./18 - Menús con scroll y navegación.md>) | **Menús con scroll y navegación** | Baja | Menú como datos, cursor que salta inactivas sin colgarse, ventana visible + scroll suavizado, barra | En cuanto una lista no quepa en pantalla |
| [19](<./19 - Programación rítmica (juegos de ritmo).md>) | **Programación rítmica** | Alta | El reloj es la canción, no el juego; ventanas de acierto, calibración de latencia, notas por cálculo | Juegos de ritmo, o cualquier cosa sincronizada con música |
| [20](<./20 - Servicios de plataforma (logros, anuncios, compras).md>) | **Servicios de plataforma** | Alta | Logros/stats (Steam), leaderboards async, anuncios (AdMob), IAP por extensión (la nativa es obsoleta), guardado en la nube | Al publicar en Steam, móvil o consola |
| [21](<./21 - Localización e idiomas (con traducción por IA).md>) | **Localización e idiomas** | Media | `txt(clave)`, tabla JSON por idioma, plurales, fuentes por alfabeto, y traducción asistida por IA reanudable | En cuanto quieras el juego en más de un idioma |
| [22](<./22 - Físicas con Box2D.md>) | **Físicas con Box2D** | Alta | Mundo y gravedad, fixtures, fuerzas vs impulsos, variables `phy_*`, joints (rueda/cuerda/plataforma), cuándo NO usarla | Puzzles físicos, vehículos, ragdolls — NO un plataformas normal |
| [23](<./23 - IA de enemigos y steering behaviors.md>) | **IA de enemigos y steering** | Media | Seek/flee/arrive/wander, evasión con `mp_potential_step`, patrullas con Paths, flocking; qué comportamiento para qué enemigo | Cualquier juego con enemigos que se muevan con intención |
| [24](<./24 - Iluminación 2D.md>) | **Iluminación 2D** | Media | Capa oscura + agujeros de luz con surfaces y blend modes, luces de color, linterna, parpadeo de antorcha; las surfaces son volátiles | Mazmorras, linternas, día/noche, ambiente |
| [25](<./25 - Menú de opciones y ajustes.md>) | **Menú de opciones y ajustes** | Media | Widgets como datos (sliders/toggles/dropdowns), aplicar en vivo, guardar/cargar en INI, rebinding | La pantalla de Opciones de cualquier juego |
| [26](<./26 - Música adaptativa por capas.md>) | **Música adaptativa por capas** | Media | Vertical layering sincronizado, crossfade con `audio_sound_gain`, stingers, transición por compás | Música que reacciona al combate/exploración |
| [27](<./27 - Accesibilidad.md>) | **Accesibilidad** | Media | No comunicar solo por color, subtítulos, escala de texto, reduce motion (<3 flashes/s), hold-to-toggle, rebinding | Todo juego que quiera llegar a más gente (y certificar en consola) |
| [28](<./28 - Juegos para móvil (táctil).md>) | **Juegos para móvil (táctil)** | Media | Orientación (`os_set_orientation_lock`), escalado y zonas seguras por porcentaje, joystick virtual, multi-touch, rendimiento y batería, techo real de RAM (Jetsam/LMK), sandbox `game_save_id`, sensores, pruebas en dispositivo | Cualquier juego para Android/iOS |
| [29](<./29 - 3D en GameMaker.md>) | **3D en GameMaker** | Alta | Cámara y matrices (`matrix_build_lookat`, `camera_set_proj_mat`), vertex buffers y formatos, parser OBJ, z-buffer y culling, iluminación fija y por shader, billboards, raycast Möller–Trumbore, mapa de alturas | 2.5D, low-poly estilo PS1, minijuegos 3D |
| [30](<./30 - Combate cuerpo a cuerpo - hitboxes, hurtboxes y combos.md>) | **Combate cuerpo a cuerpo** | Media-alta | Hitbox ≠ hurtbox ≠ máscara, frame data (startup/active/recovery), controlador único en End Step, cola de golpes, combos con cancels, i-frames, parry, poise, multi-hit | Beat 'em up, hack and slash, action RPG, plataformas con espada |
| [31](<./31 - IA de decisión - árboles de comportamiento, utility y GOAP.md>) | **IA de decisión** | Media-alta | FSM → árbol de comportamiento (Selector/Sequence/decoradores, `Running`), blackboard, árboles como datos, utility AI con curvas, GOAP con A* sobre estados, percepción (vista, oído, memoria), tick escalonado | Enemigos que deciden, no solo se mueven (complementa a `23`) |
| [32](<./32 - Sistema de daño y efectos de estado.md>) | **Sistema de daño y efectos de estado** | Media | Tipos de daño y resistencias desde JSON, armadura y penetración, escudos con regeneración, motor de efectos (veneno, quemadura, congelación, aturdimiento), iconos con pilas, barra de jefe por fases, registro de daño y DPS medido | Cualquier juego donde el daño sea más que restar un número |
| [33](<./33 - Diseño de enemigos, encuentros y director de combate.md>) | **Enemigos, encuentros y director** | Media-alta | Los seis arquetipos con su ficha, sinergias, fichas de ataque (que no ataquen todos a la vez), tabla de amenaza, director de intensidad estilo *Left 4 Dead*, spawners y tick escalonado | Cuando el problema ya no es un enemigo, sino el grupo |
| [34](<./34 - Combate a distancia - armas, munición y balística.md>) | **Combate a distancia** | Media | Cargador y recarga (con recarga activa), retroceso y dispersión creciente, proyectiles y pooling, hitscan con `collision_line_list` ordenado, asistencia de puntería, cobertura, granadas y área | Shooters, twin-stick, cualquier arma de fuego |
| [35](<./35 - Combate por turnos y táctico en rejilla.md>) | **Por turnos y táctico** | Alta | Iniciativa y ATB con cola visible, menú de batalla como pila de contextos, rango de movimiento por Dijkstra, zona de amenaza, línea de tiro, terreno y altura, IA por utilidad | JRPG, táctico de rejilla, *Fire Emblem* / *Into the Breach* |
| [36](<./36 - Habilidades, enfriamientos y recursos de combate.md>) | **Habilidades y enfriamientos** | Media | Habilidad como datos (coste, enfriamiento, cargas, casteo, interrupción), gestor por entidad, enfriamiento global, estamina/maná/furia, barra de acción con barrido radial | Cualquier juego con más de un botón de acción |
| [37](<./37 - Traversal en plataformas - pendientes, paredes, escaleras y bordes.md>) | **Traversal en plataformas** | Media-alta | Pendientes con heightmap, corrección de esquina, wall slide y wall jump, ledge grab, agacharse, escaleras y cuerdas, nadar, empujar cajas | Extiende `01` cuando el personaje necesita moverse de verdad |
| [38](<./38 - Pathfinding avanzado - flow fields, JPS y plataformas.md>) | **Pathfinding avanzado** | Alta | Campo de flujo (muchas unidades, un destino), Jump Point Search, grafo de plataformas con aristas de salto y caída, suavizado de rutas | Cuando `mp_grid` y A* se quedan cortos |
| [39](<./39 - VFX - diseño y catálogo de efectos.md>) | **VFX: diseño y catálogo** | Media | Anatomía de un efecto en capas, recetas completas (explosión, fuego, humo, chispas, sangre, magia, lluvia, nieve, niebla), trails con `pr_trianglestrip`, decals y escombros, congelar partículas en el hit stop | El oficio del efecto, no solo la API |
| [40](<./40 - Tutorial, onboarding y prompts en pantalla.md>) | **Tutorial y onboarding** | Básica | Disparadores por zona, «mostrar una sola vez» persistido, escalado de pistas tras N fallos, prompts de botón que leen el dispositivo activo **y** la asignación real | El código del onboarding (el diseño está en `13/01` §5) |
| [41](<./41 - Transiciones, carga y pausa.md>) | **Transiciones, carga y pausa** | Básica | Máquina de estados de transición (fundido, wipe, iris, cortinas, disolución), pantalla de carga real con `texturegroup_load`, menú de pausa completo, y **pausar de verdad** (time sources, partículas, Sequences, audio) | Todo juego, desde el primer prototipo |
| [42](<./42 - Audio reactivo al mundo - materiales, zonas y estados de mezcla.md>) | **Audio reactivo al mundo** | Media | Pasos por material leyendo el tile, zonas de reverberación, estados de mezcla interpolables, sistema de importancia de *Overwatch* | Cuando el audio debe responder al mundo, no solo sonar |
| [43](<./43 - Modding y contenido externo.md>) | **Modding y contenido externo** | Alta | Carpeta `mods/` en el sandbox, `sprite_add` y `texturegroup_add`, fusión de catálogos JSON, scripts del jugador con Catspeak sin abrir un agujero, publicación con mod.io, aislamiento del riesgo | Juegos que quieren comunidad |
| [44](<./44 - Bullet heaven, autobattler y deckbuilder.md>) | **Bullet heaven, autobattler y deckbuilder** | Media-alta | Los tres géneros de moda con su esqueleto común: oleadas y build, tienda con reroll e interés, mazo/mano/descarte con semilla, escalado numérico y miles de entidades | *Vampire Survivors*, *TFT*, *Slay the Spire* |
| [45](<./45 - Géneros sin receta propia - sigilo, horror, táctica, granja y idle.md>) | **Géneros sin receta propia** | Media | Por cada uno: convenciones, sus tres sistemas críticos y a qué receta apoyarse. Medidor de detección, tensión de audio, calendario y estaciones, cosecha y ganado (`Animal`), curva exponencial y progreso offline (lineal y con rendimientos decrecientes) | Sigilo, horror, granja/cozy, idle/incremental |
| [46](<./46 - Eje Z falso - altura, sombras y profundidad en un juego 2D.md>) | **Eje Z falso** | Media | Variables `z`/`zvel` separadas de `x`/`y`, dibujar en `y - z` sin tocar la colisión, sombra que encoge y se aclara con la altura, orden de dibujado por Y con el eje Z de por medio, saltar en un top-down, proyectiles con arco, suelos a distinta altura, agua, el caso isométrico | Técnica transversal — saltos, arcos y beat 'em up en cualquier juego 2D cenital |
| [47](<./47 - Beat em up y brawler.md>) | **Beat 'em up y brawler** | Media-alta | Carril de profundidad, alineación en Z para que un golpe conecte, oleadas con bloqueo de pantalla y avance, agarres y lanzamientos, IA de turnos de ataque (`GestorFichas` de `04 · 33`), cooperativo local, armas recogibles y objetos rompibles, jefes y escenario que hace daño | *Streets of Rage*, *Final Fight*, *Fight'N Rage* — construido sobre `04 · 46` |
| [48](<./48 - Aventura gráfica y point and click.md>) | **Aventura gráfica y point and click** | Media | Hotspots (objeto/máscara/polígono) y cursor contextual, interfaz de verbos (SCUMM vs dos botones vs rueda — implementada la de dos botones), *walk-to* con *walkboxes* poligonales y BFS sobre su grafo, escalado por profundidad, inventario combinatorio con arrastrar y examinar, estado del mundo (banderas frente a registro por objeto), cinemáticas cortas y la regla de oro de no crear callejones sin salida | *Monkey Island*, *Day of the Tentacle*, *Machinarium*, *Thimbleweed Park* |
| [49](<./49 - Deportes y física de mesa.md>) | **Deportes y física de mesa** | Media-alta | Balón como entidad con estado (libre/poseído/en vuelo), pase con anticipación y pase alto, tiro con potencia/dirección/efecto sobre el arco de `04 · 46`, IA por roles y formación con desplazamiento de bloque, marcaje y desmarque, fuera de banda/fuera de juego/faltas y máquina de estados del partido, reloj con tiempo añadido — y física de mesa (billar con colisión elástica de círculos a mano, pinball con *flippers*/*bumpers*/*tilt* en Box2D, minigolf con previsualización de trayectoria, pendientes y viento) | Fútbol/deportes de equipo, billar, pinball, minigolf |
| [50](<./50 - Juego de lucha.md>) | **Juego de lucha** | Alta | Motor de comandos (buffer direccional, notación numpad, prioridad entre comandos, *negative edge*, tolerancia), *frame data* en datos con cajas por fotograma, tabla de *cancels*/*gatling* por grupo, escalado de daño Y de *hitstun* (por qué si no los combos infinitos aparecen solos), *pushback* creciente, agarres con ventana de *tech*, levantada e invulnerabilidad de despertar, guardia alta/baja y *guard crush*, barra de súper (`RecursoCombate` de `04 · 36`), y la verdad sobre el *rollback* en GML | *Street Fighter*, *Guilty Gear*, *Tekken* (plano 2D) — construido sobre `04 · 30` |
| [51](<./51 - Colonia y constructor de bases - trabajadores autónomos.md>) | **Colonia y constructor de bases** | Alta | *Job system* con cola de prioridad por tipo (`ds_priority_*`), reserva y tareas en varios pasos, rutinas y horarios de NPC sobre el reloj de `04 · 09`, necesidades de población por composición de `Needs()`, construcción con plano/soporte estructural/habitaciones por *flood fill*, redes de energía y fluidos como grafo espacial, y simulación fuera de pantalla con LOD, lotes y presupuesto real | *RimWorld*, *Dwarf Fortress*, *Oxygen Not Included*, *Factorio* — el hueco de género más grande detectado en la biblioteca |
| [52](<./52 - Live-ops técnico (config remota, versión mínima, mensajes del juego).md>) | **Live-ops técnico** | Media | Config remota vía `http_request` con valores por defecto locales, feature flags de activación gradual sin identificar al jugador, versión mínima del cliente (`GM_version`) y bloqueo de actualización obligatoria, mensaje del día sin repetirse, modo mantenimiento, eventos de temporada por fecha — todo sin publicar una actualización en la tienda | Técnica transversal — cualquier juego con backend propio, aunque sea de una persona |
| [07](<./07 - Puzzle y Match-3.md>) | **Puzzle / Match‑3** | Media | Tablero en arrays, detección de matches, cascadas, tween de piezas, shuffle | 5.º — lógica pura separada de la vista |
| [08](<./08 - Tower Defense.md>) | **Tower Defense** | Media | Grid, `mp_grid` / A*, oleadas, targeting de torres, proyectiles, economía | 6.º — IA de pathfinding |
| [04](<./04 - RPG _ Action RPG.md>) | **RPG / Action RPG** | Media‑Avanzada | Stats, curvas de experiencia, inventario, equipamiento, peso y capacidad de carga, diálogos, quests, save/load, tilemaps grandes | 7.º — primer juego con estado persistente real |
| [10](<./10 - Visual Novel y narrativa.md>) | **Visual Novel / narrativa** | Media | Diálogo con structs, retratos, ramificaciones, *typewriter*, voces, guardado | 8.º — reutiliza el save/load del RPG |
| [05](<./05 - Roguelike y generación procedural.md>) | **Roguelike / procedural** | Avanzada | RNG con semilla, BSP y *random walk*, tilemaps, FOV, muerte permanente, tablas de loot ponderadas | 9.º — junta RPG + generación |
| [06](<./06 - Metroidvania.md>) | **Metroidvania** | Avanzada | Rooms interconectadas, habilidades desbloqueables, estado persistente del mundo, puertas, minimapa | 10.º — junta plataformas + RPG |
| [09](<./09 - Survival y crafting.md>) | **Survival / crafting** | Avanzada | Recolección, inventario por pila, contenedores (`objStorageChest`), recetas con estaciones/descubrimiento/colas/lotes/árbol de dependencias, necesidades, construcción, chunking | 11.º |
| [12](<./12 - Carreras y vehículos.md>) | **Carreras / vehículos** | Media‑Avanzada | Física arcade vs simulación, terreno, IA de rivales, checkpoints, vueltas | 12.º |
| [13](<./13 - Estrategia y gestión.md>) | **Estrategia / gestión** | Avanzada | Grid, selección múltiple, órdenes, IA, economía, UI Layers + Flex Panels | 13.º |
| [14](<./14 - Multijugador.md>) | **Multijugador** | Avanzada | Red con buffers, modelos de red, predicción, interpolación, extensiones (Photon, Steamworks, Colyseus, Namazu) | 14.º — solo cuando el resto te salga solo |

---

## Ruta de aprendizaje recomendada

```
FASE 1 — Fundamentos de movimiento
  01 Plataformas  →  02 Top-Down
     (lee 15 Game feel en paralelo, desde el principio)

FASE 2 — Primeros sistemas
  03 Shmup  →  11 Arcade
     (aquí ya entiendes pooling, oleadas y feedback)

FASE 3 — Lógica separada de la vista
  07 Puzzle/Match-3  →  08 Tower Defense

FASE 4 — Estado persistente y contenido
  04 RPG  →  10 Visual Novel

FASE 5 — Escala
  05 Roguelike  →  06 Metroidvania  →  09 Survival

FASE 6 — Especialización
  12 Carreras  ·  13 Estrategia  ·  14 Multijugador
```

### Criterio para saber cuándo avanzar

No avances de fase si no puedes responder *sin mirar* a estas preguntas:

- **Fase 1**: ¿por qué el *coyote time* mejora la sensación de control? ¿Qué
  hace `move_and_collide()` con el tercer argumento y para qué sirven los
  dos últimos?
- **Fase 2**: ¿por qué un *pool* de balas evita tirones de framerate? ¿Cómo
  defines una oleada desde datos en vez de desde código?
- **Fase 3**: ¿por qué el tablero se guarda en un array y no en instancias?
- **Fase 4**: ¿cómo serializas un inventario a JSON sin perder referencias?
- **Fase 5**: ¿cómo garantiza la semilla que dos partidas generen el mismo mundo?

---

## Recursos transversales (aplican a todos los géneros)

| Herramienta | Para qué | Fuente |
|---|---|---|
| **GameMaker Testing Library** | Tests unitarios dentro del IDE | DAndrëw |
| **SnowState** | Máquina de estados jerárquica en GML | Sohom Sahaun |
| **GMRoomLoader** | Rooms infinitas / carga por regiones | Gleb Tsereteli |
| **Post-Processing FX** | Bloom, aberración, *color grading*, *vignette* | FoxyOfJungle |
| **SynthEngine** | Audio avanzado y síntesis | Topher Anselmo |
| **Templates oficiales** | Juegos completos comentados: Survivor, Tower Defence, Platformer, Card Game, Arcade Shooter, Match 3 | IDE → New → Game → Template |

---

## Fuentes

- GameMaker LTS 2026.0: New Features, GMRT and Much More (21 may 2026) —
  https://gamemaker.io/en/blog/lts-2026-release
- GameMaker Update Spring 2026: LTS Roadmap, GMRT, and the Future (30 abr 2026) —
  https://gamemaker.io/en/blog/update-spring-2026
- Release notes 2026.0 (IDE 16 / Runtime 23) —
  https://releases.gamemaker.io/release-notes/2026/0
- How to Get Started with GameMaker in 2026 (Samuel Wain, ene 2026) —
  https://gamemaker.io/tutorials/get-started-gamemaker-2026
- Índice de tutoriales oficiales — https://gamemaker.io/en/tutorials
- Manual oficial (LTS) — https://manual.gamemaker.io/lts/en/
- Manual oficial (Monthly, funciones más recientes) —
  https://manual.gamemaker.io/monthly/en/
