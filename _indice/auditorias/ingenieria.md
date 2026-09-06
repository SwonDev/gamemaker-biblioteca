# Auditoría · Ingeniería de juego y sistemas transversales

> **Dominio:** arquitectura, patrones, datos y configuración, guardado, inventario, misiones,
> diálogo, localización, input, tiempo, aleatoriedad, matemáticas, pathfinding, IA, redes,
> plataformas y servicios, modding, extensiones nativas, rendimiento, depuración, testing,
> build y CI, control de versiones, gestión de assets, exportación, HTML5, consolas,
> seguridad, accesibilidad técnica, analítica, crash reporting, parcheo, GMRT, Feather,
> documentación de código, hot reload, MCP y agentes de IA.
>
> **Fecha:** 06-09-2026 · **Biblioteca auditada:** `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`
> (excluidos `Lumbre/` y `GameMaker_Fuentes/`).
>
> **Fuentes canónicas usadas para construir la lista:** Robert Nystrom, *Game Programming
> Patterns* (índice completo verificado en vivo con `curl` sobre
> <https://gameprogrammingpatterns.com/contents.html>: 19 patrones) · Jason Gregory, *Game
> Engine Architecture* 3.ª ed. (subsistemas de runtime: gestión de recursos, HID, tiempo,
> depuración, colisión, IA, red, herramientas) · manual oficial de GameMaker LTS 2026 (espejo
> local `09 - Manual oficial/`: páginas `Settings/Included_Files`, `Settings/Texture_Groups`,
> `Settings/Configurations`, `The_Asset_Editors/Extension_Creation/*`,
> `IDE_Tools/Source_Control`) · README y workflows de `gm-cli` · organización
> <https://github.com/YoYoGames> (GM-ExtensionGenerator, GM-TestFramework, GMEXT-*).

**Veredicto en una frase:** el dominio está **muy bien cubierto** —13/06, 13/10, 13/11, 13/13,
05/02 y 07/13 son documentos serios, con código verificado y compilado—. Los huecos reales son
**pocos y concretos**: seis patrones de Nystrom sin traducir a GML, ECS, modding *de tu propio
juego*, extensiones nativas C++/Android/iOS, pathfinding avanzado (flow field, JPS, plataformas)
y seguridad/anti-trampas como tema propio.

---

## 1 · Tabla de cobertura

Estados: **CUBIERTO** (documento y sección exactos) · **PARCIAL** (existe pero se queda corto) ·
**FALTA** (no existe en ninguna forma útil).

### Bloque A · Patrones de *Game Programming Patterns* (los 19 del índice oficial) + ECS

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| A1 | **Command** (input como dato, rebinding, replays) | CUBIERTO | `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md` §3.7 «Patrón comando: input, rebinding y replays» | — | GPP · *Command* |
| A2 | **Flyweight** (datos compartidos entre miles de entidades: tileset, definición de enemigo, fuente) | **FALTA** | Cero apariciones en toda la biblioteca (`grep -rli "flyweight"` vacío) | El caso GML es real: 5 000 balas que comparten un struct de definición en vez de copiarlo; tilesets; `sprite_get_texture` compartida | GPP · *Flyweight*; Gregory §"Runtime resource management" |
| A3 | **Observer** | CUBIERTO | `04 - Recetas por género/16 - Señales y desacoplamiento.md` (entero: emisión, escucha, oyentes zombis, depuración) | — | GPP · *Observer* |
| A4 | **Prototype** (clonar una instancia-plantilla en vez de un constructor por tipo) | **FALTA** | `02 - Novedades 2026/08 - Package Manager y Prefabs.md` cubre los *Prefabs* del IDE, que **no** son el patrón | En GML el patrón se aplica con `instance_copy()` y con structs plantilla + `variable_clone()` | GPP · *Prototype* |
| A5 | **Singleton** (y por qué evitarlo) | CUBIERTO | `13/06` §3.3 «Localizador de servicios: un solo portal de globales» + `01 - Fundamentos/09 - Instancias, objetos y herencia.md` | — | GPP · *Singleton* |
| A6 | **State** (máquina de estados) | CUBIERTO | `06 - Assets y Scripts/scr_state_machine.gml` (código completo) + `07 - Ecosistema/17 - SnowState - máquinas de estado (guía en español).md` | — | GPP · *State* |
| A7 | **Double Buffer** | CUBIERTO (aplicado, sin el nombre) | `13 - Diseño y producción de videojuegos/07 - Generación procedural avanzada.md` §3, función `cueva_celular` — comentario explícito «Buffer doble: NO se puede leer y escribir el mismo array en una pasada» | Solo el nombre del patrón y el caso de surfaces ping-pong | GPP · *Double Buffer* |
| A8 | **Game Loop** (paso fijo, acumulador, determinismo) | CUBIERTO | `01 - Fundamentos/06 - Eventos y ciclo del juego.md` §7 + `13/06` §3.9 «Tiempo: frames fijos, `delta_time` y paso fijo con acumulador» | — | GPP · *Game Loop* |
| A9 | **Update Method** | CUBIERTO | `01 - Fundamentos/06 - Eventos y ciclo del juego.md` §4 «El orden EXACTO de cada step» y §10 | — | GPP · *Update Method* |
| A10 | **Bytecode** (lenguaje embebido para reglas/modding) | PARCIAL | `12 - Utilidades e integraciones/01 - Herramientas del flujo de trabajo.md` §7 «Ejecutar código en tiempo de ejecución» — tabla de catspeak-lang, JITSpeak, GMLC, RunGML, Apollo (Lua), LuaMancer | Solo catálogo: no explica cuándo un juego necesita un intérprete propio ni un ejemplo mínimo | GPP · *Bytecode* |
| A11 | **Subclass Sandbox** (una base que expone operaciones seguras; hijos que solo las combinan) | **FALTA** | Nada. `13/06` §3.6 cubre herencia vs composición, pero no este patrón | Es exactamente el caso de `obj_enemigo_base` con `event_inherited()` + métodos protegidos, y de las «habilidades» de un metroidvania | GPP · *Subclass Sandbox* |
| A12 | **Type Object** (definiciones por datos en vez de una clase por tipo) | CUBIERTO (aplicado, sin el nombre) | `13/06` §3.8 «Datos dirigidos: definir el juego en JSON» — catálogo `enemigos.json` → `enemigo_crear()` con `asset_get_index` | — | GPP · *Type Object* |
| A13 | **Component** | CUBIERTO | `13/06` §3.6 «Composición frente a herencia» (cita explícita del «Bjørn hinchado» de Nystrom) | — | GPP · *Component* |
| A14 | **Event Queue** (eventos diferidos, no síncronos) | PARCIAL | `13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md` §6.6 «Cinemáticas como cola de pasos» es un caso concreto; `04/16` dice que las señales son síncronas y menciona «diferidas» de pasada (línea 235) | El patrón general: cola de audio, cola de daño, evitar reentrada y orden de emisión no determinista | GPP · *Event Queue* |
| A15 | **Service Locator** | CUBIERTO | `13/06` §3.3 (con «null service» y la advertencia sobre acceso global) | — | GPP · *Service Locator* |
| A16 | **Data Locality** | **FALTA** | Solo aparece como enlace en «Fuentes» de `13/06` (línea 1109), sin desarrollo | En GML sí hay decisiones medibles: array plano vs array de arrays, struct-of-arrays para partículas, `array_create` al tamaño máximo. `13/07` da la regla del array plano pero sin conectarla con el patrón ni con medición | GPP · *Data Locality*; Gregory cap. «Memory management» |
| A17 | **Dirty Flag** | **FALTA** | Cero apariciones | El caso GML canónico: no recalcular el layout de Flex Panels cada frame (mencionado como error en `04/13`), matrices de transformación, `mp_grid` que solo se recalcula al cambiar el terreno, cachés de path | GPP · *Dirty Flag* |
| A18 | **Object Pool** | CUBIERTO | `06 - Assets y Scripts/scr_pool.gml` (código completo) + `13/06` §1.4 tabla de coste | — | GPP · *Object Pool* |
| A19 | **Spatial Partition** | CUBIERTO | `13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md` §4.1 «El spatial hash: una rejilla de cubos» y §4.4 «Y el quadtree, ¿por qué no?» | — | GPP · *Spatial Partition* |
| A20 | **ECS en GML** | **FALTA** | `grep -rli "entity component"` vacío; `ECS` solo aparece como subcadena en otras palabras | Ni una línea. Merece al menos un veredicto honesto: en GameMaker el ECS puro casi nunca compensa frente a instancias + structs, y por qué | Gregory §"Runtime object model architectures"; charlas GDC (Overwatch ECS) |

### Bloque B · Arquitectura y organización

| # | Tema | Estado | Dónde | Qué falta | Fuente |
|---|---|---|---|---|---|
| B1 | Capas datos/lógica/presentación | CUBIERTO | `13/06` §1.3 «Las tres capas» | — | Gregory cap. 1 |
| B2 | Controlador persistente + flujo de arranque | CUBIERTO | `13/06` §3.2 `obj_game`, §3.4 «El flujo de arranque» | — | — |
| B3 | Anti-patrones y checklist de arquitectura sana | CUBIERTO | `13/06` §4.3 y §5 «Anti-patrones: los ocho de los proyectos que se atascan» | — | — |
| B4 | Modularizar: Local Packages `.yymps` | CUBIERTO | `13/06` §3.15 «Escalar: módulos y Local Packages» | — | Manual `IDE_Tools/Local_Asset_Packages` |
| B5 | Macros, enums y **Configurations** del IDE | CUBIERTO | `13/06` §3.12 «Macros, enums y Configs del IDE» (`#macro Config:NOMBRE valor`) + `05 - Referencia/02 - Publicar y exportar.md` §4.2 | — | Manual `Settings/Configurations` |
| B6 | Memoria y ciclo de vida de recursos dinámicos | CUBIERTO | `13/06` §3.11 + `01 - Fundamentos/15 - Depuración y rendimiento.md` §8 «Checklist de limpieza de recursos dinámicos» | — | — |

### Bloque C · Datos, configuración y guardado

| # | Tema | Estado | Dónde | Qué falta | Fuente |
|---|---|---|---|---|---|
| C1 | JSON + Included Files como fuente de datos | CUBIERTO | `13/06` §3.8; `01 - Fundamentos/14 - Persistencia y archivos.md` §8; `13 - .../01 - Diseño de juego...md` §9.3 «Datos de balance en Included Files» | — | Manual `Settings/Included_Files` |
| C2 | CSV | CUBIERTO | `07 - Ecosistema/20 - SNAP - datos y formatos (guía en español).md`; `13/12` §5.4 «Tablas propias en JSON/CSV» | — | — |
| C3 | Tablas de balance y ajuste en caliente | CUBIERTO | `13/01` §9.4 «Balance en caliente con el Debug Overlay» (`dbg_slider` + `ref_create`, `balance_guardar`/`balance_restaurar`) | — | — |
| C4 | Guardado: ranuras, ficheros separados (config / perfil / partida) | CUBIERTO | `13/06` §3.10 (tabla de las tres clases de estado) + `06 - Assets y Scripts/scr_save_load.gml` | — | — |
| C5 | Versionado y **migración** del guardado | CUBIERTO | `13/06` §3.10 — `scr_migraciones.gml`, escalones acumulativos, las tres reglas | — | — |
| C6 | Autoguardado | PARCIAL | Mencionado en `04/00` §5, `04/06`, `13/06` §3.10 | Ningún sitio explica el *cuándo* y el *cómo seguro*: escritura atómica a temporal + rename, no guardar en mitad de una transición, indicador visible | — |
| C7 | Ofuscación / integridad del guardado | CUBIERTO | `01 - Fundamentos/14 - Persistencia y archivos.md` §12 «Codificación y hashes» (base64 + `md5_string_utf8`, con la advertencia «base64 NO es seguridad») | — | — |
| C8 | Guardado en la nube (Steam Cloud) | CUBIERTO | `04 - Recetas por género/20 - Servicios de plataforma...md` §5 «Guardado en la nube (Steam Cloud)» | — | GMEXT-Steamworks |
| C9 | El sandbox de ficheros y sus trampas por plataforma | CUBIERTO | `01/14` §1-§3 | — | Manual |

### Bloque D · Sistemas de juego transversales

| # | Tema | Estado | Dónde | Qué falta | Fuente |
|---|---|---|---|---|---|
| D1 | Inventario por datos, pilas, equipo | CUBIERTO | `04 - Recetas por género/04 - RPG _ Action RPG.md` §5.2 «Inventario y equipamiento» + `04 - Recetas por género/09 - Survival y crafting.md` §4.2 «Inventario por pila» | — | — |
| D2 | Crafting | CUBIERTO | `04/09` §4.3 y §5.1 «Recetas de crafteo» (struct receta, `puede_craftear`/`craftear`) | — | — |
| D3 | Rareza y tablas de botín | CUBIERTO | `04 - Recetas por género/05 - Roguelike y generación procedural.md` — struct `LootTable` con pesos y `roll()` | — | — |
| D4 | Misiones / quest log | CUBIERTO | `04/04` §6 «Quests» (constructor `QuestLog` completo) + `13/12` §6.5 «Un gestor de misiones mínimo (con estado "fallada")» | — | — |
| D5 | Diálogo (árboles, flags, Yarn) | CUBIERTO | `13/12` §6.1-§6.4 + `07 - Ecosistema/19 - Chatterbox - diálogos Yarn (guía en español).md` + `04/04` §5.4 | — | — |
| D6 | Localización | CUBIERTO | `04 - Recetas por género/21 - Localización e idiomas (con traducción por IA).md` | — | — |
| D7 | Input: teclado, ratón, gamepad, táctil, gestos | CUBIERTO | `01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md` (entero, incl. §8 controlador unificado y §8bis táctil) | — | Manual |
| D8 | Librería **Input** de JujuAdams | CUBIERTO | `01/12` §7 «La librería Input (recomendada para proyectos serios)» | — | — |
| D9 | Rebinding | PARCIAL | `04 - Recetas por género/25 - Menú de opciones y ajustes.md` §5 «Reasignar controles (rebinding)» — 15 líneas de esbozo + «para rebinding serio usa Input» | Conflictos entre acciones, perfiles, ejes de mando, glifos del botón según el mando conectado, guardado. La biblioteca lo delega a una librería sin enseñar la API | Manual `gamepad_*`; librería Input |
| D10 | Buffers de entrada y coyote time | CUBIERTO | `06 - Assets y Scripts/scr_input_buffer.gml` (constructores `InputBuffer` y `CoyoteTime` completos) + `04/30` | — | — |
| D11 | `delta_time`, `fps` vs `fps_real`, `game_set_speed` | CUBIERTO | `01/06` §7 + `13 - .../13 - Matemáticas aplicadas al juego.md` §12 «Tiempo» | — | Manual |
| D12 | Time Sources | CUBIERTO | `01/06` §8 «Time Sources: la alternativa moderna a los alarm» (crear, repetir, argumentos, `call_later`, cuándo alarm vs time source) | — | Manual `Time_Sources` |
| D13 | Pausa global | PARCIAL | `04 - Recetas por género/00 - Anatomía de un juego completo.md` §5 (`global.pausado`) + `01/12` | Falta el problema real: qué hacer con las time sources y las alarmas al pausar (`time_source_pause`/`_resume` no aparecen en ningún documento), audio, partículas y secuencias | Manual `time_source_pause` |
| D14 | Escala de tiempo, cámara lenta, *hit stop* | CUBIERTO | `04 - Recetas por género/15 - Game feel y juice.md` §5.0 «Sistema de tiempo: hit stop y time scale» (`objTime`, `global.time_scale`) | — | — |
| D15 | Cooldowns | PARCIAL | Aparece en `04/02`, `04/03`, `04/06`, `04/12`, `04/13`, `04/31` como variable suelta por receta | No hay una pieza reutilizable (struct `Cooldown` con `listo()`, `usar()`, fracción para la UI) ni el criterio frames vs segundos | — |
| D16 | Reloj del juego y ciclo día/noche | CUBIERTO | `04/09` §4.7 y §5.5 «Ciclo día/noche» + `04 - Recetas por género/24 - Iluminación 2D.md` | — | — |
| D17 | Aleatoriedad, semillas y determinismo | CUBIERTO | `13/13` §5 completo (catálogo, semillas, distribuciones, *shuffle bag*, azar con memoria, *pity*, histograma de validación) + `13/10` §5.3 | — | — |
| D18 | Matemáticas aplicadas | CUBIERTO | `13/13` entero (vectores, ángulos, easing, Bézier, Catmull-Rom, colisión, rejillas, hexágonos, curvas de crecimiento, precisión numérica) | — | — |

### Bloque E · Pathfinding e IA

| # | Tema | Estado | Dónde | Qué falta | Fuente |
|---|---|---|---|---|---|
| E1 | `mp_grid` + A* nativo | CUBIERTO | `06 - Assets y Scripts/scr_grid_pathfinding.gml` — constructor `Grid` (envoltorio de `mp_grid_*`) | — | Manual `mp_grid_*` |
| E2 | A* con coste por celda en GML puro | CUBIERTO | `06/scr_grid_pathfinding.gml` — constructor `GridPonderado` (cola de prioridad `ds_priority`) | — | — |
| E3 | **Flow field** (campo de flujo) | PARCIAL | `04 - Recetas por género/13 - Estrategia y gestión.md` §4.1 (una fila de tabla) y §8.1 (dos frases) | No hay código. Es la solución obligada por encima de ~50 unidades y la propia receta lo dice dos veces sin darlo | Gregory §"Path finding"; Elijah Emerson, *Crowd Pathfinding and Steering* (Game AI Pro) |
| E4 | **Jump Point Search** | **FALTA** | Cero apariciones | Optimización de A* sobre rejilla uniforme (×10 típico). Con `GridPonderado` ya escrito, es el siguiente escalón natural | Harabor & Grastien, *Online Graph Pruning for Pathfinding on Grid Maps* (AAAI 2011) |
| E5 | Pathfinding para **plataformas** (grafo con nodos de salto) | **FALTA** | Cero apariciones. `04/01 Plataformas 2D` no lo toca | Un enemigo que persigue en un plataformas no puede usar `mp_grid`: necesita un grafo de plataformas con aristas de salto/caída | Gregory §"Path finding"; charlas GDC sobre IA en plataformas |
| E6 | NavMesh | CUBIERTO (como «no existe») | `04 - Recetas por género/31 - IA de decisión...md` y `04/29` lo mencionan y descartan | — | — |
| E7 | Steering behaviors | CUBIERTO | `04 - Recetas por género/23 - IA de enemigos y steering behaviors.md` (seek, flee, arrive, wander, evasión, paths, flocking) | — | Reynolds, *Steering Behaviors For Autonomous Characters* |
| E8 | Árboles de comportamiento, utility, GOAP | CUBIERTO | `04 - Recetas por género/31 - IA de decisión - árboles de comportamiento, utility y GOAP.md` (1 119 líneas) | — | Game AI Pro |

### Bloque F · Redes, plataformas y servicios

| # | Tema | Estado | Dónde | Qué falta | Fuente |
|---|---|---|---|---|---|
| F1 | Modelo de red, autoridad, `net_id` | CUBIERTO | `04 - Recetas por género/14 - Multijugador.md` §2.1-§2.4 | — | — |
| F2 | TCP/UDP/WebSocket, buffers de paquete, cadencia | CUBIERTO | `04/14` §4.1-§4.3 y §5.0-§5.4 (código completo servidor + cliente) | — | Manual `network_*` |
| F3 | Predicción, reconciliación, interpolación | CUBIERTO | `04/14` §4.4, §4.5, §5.5-§5.7 | — | Gaffer On Games |
| F4 | **Rollback** | CUBIERTO | `04/14` §4.6 «Rollback completo (para juegos de lucha)» | — | GGPO |
| F5 | Chat en red | CUBIERTO | `04/14` §5.9 «Chat» | — | — |
| F6 | Desconexión limpia | CUBIERTO | `04/14` §5.10 | — | — |
| F7 | **Lobbies y matchmaking** | PARCIAL | `04/14` §1.2 (Photon) y `12 - Utilidades e integraciones/04 - Multijugador y red.md` §2 (Colyseus, «salas») | Se delega íntegro a Photon/Colyseus; no hay ni el modelo de datos de una sala ni el flujo crear/listar/unirse, ni con Steam Lobbies (`steam_lobby_*`, que sí existen en el runtime) | GMEXT-Steamworks; Photon |
| F8 | **NAT traversal** | **FALTA** | «NAT» solo aparece como subcadena de otras palabras | Explicar por qué un servidor casero no es alcanzable, y las tres salidas: relay (Photon), servidor dedicado (Colyseus), o Steam datagram | Gregory §"Networking"; documentación de Photon |
| F9 | **Anti-trampas / validación en servidor** | PARCIAL | `04/14` §2.2 «Nunca confíes en el cliente» (principio, media página) | No hay nada sobre: validar puntuaciones antes de subir a un leaderboard, detectar velocidades imposibles, editar la memoria (Cheat Engine), o por qué un juego de un jugador con ranking online necesita replay firmado | — |
| F10 | Steam: logros, estadísticas, leaderboards | CUBIERTO | `04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md` §1 y §2, con la advertencia de que `steam_set_achievement` no está en el runtime (va por extensión) | — | GMEXT-Steamworks |
| F11 | Anuncios (AdMob) e IAP | CUBIERTO | `04/20` §3 y §4 (incl. `iap_*` marcada obsoleta) | — | GMEXT-AdMob |
| F12 | Rich Presence / Discord | CUBIERTO | `12 - Utilidades e integraciones/03 - Integraciones con servicios.md` §2 «Comunidad y redes» + `07 - Ecosistema/03 - Extensiones oficiales y de terceros.md` | — | GMEXT-Discord |

### Bloque G · Extensiones, modding, build y herramientas

| # | Tema | Estado | Dónde | Qué falta | Fuente |
|---|---|---|---|---|---|
| G1 | Extensión **JS para HTML5** | CUBIERTO | `04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md` §1 «Crear la extensión», §2 «JavaScript → GML» (`gmcallback_`) | — | Manual `HTML5_Extensions` |
| G2 | **Crear una extensión nativa** (DLL/dylib/so, Android, iOS) | PARCIAL | `12 - Utilidades e integraciones/02 - Extensiones nativas y del sistema.md` §6 «Escribir tu propia extensión» — **solo una tabla de 5 enlaces** (GM-ExtensionGenerator, GMSDLL, GMSDLL.rs, ExtensionExample, GM-OpenAPIGenerator) | No hay ni un paso a paso ni una firma de función. El manual sí lo documenta en español: `Creating_An_Extension.md`, `Android_Extensions.md`, `iOS_Extensions.md`, `Source_Files/` | Manual `The_Asset_Editors/Extension_Creation/*`; <https://github.com/YoYoGames/GM-ExtensionGenerator> |
| G3 | `gmcallback_` y el retorno asíncrono desde JS | CUBIERTO | `04/17` §2 + `01 - Fundamentos/07 - Funciones, métodos y ámbito.md`; `_indice/COMO-BUSCAR.md` avisa de que no es un símbolo del runtime | — | Manual |
| G4 | **Modding de tu propio juego** (cargar sprites/datos externos, scripting para jugadores) | PARCIAL | Piezas sueltas y desconectadas: `01/14` §11 (directorios), `08 - Referencia GML completa/08 - Texturas y grupos de texturas.md` §`texturegroup_add` («la puerta de entrada para contenido descargable y *modding*»), `12/01` §7 (catspeak-lang), `07/01` y `07/03` (GMEXT-mod.io) | Falta el documento que las una: dónde vive la carpeta `mods/`, `sprite_add` y sus límites por plataforma, cargar un JSON de mod y fusionarlo con el catálogo base, ejecutar scripts de jugador con Catspeak sin abrir un agujero, distribuir con mod.io | Manual `sprite_add`, `texturegroup_add`; <https://github.com/YoYoGames/GMEXT-mod.io>; catspeak-lang |
| G5 | Lua/Luau en GameMaker (no es nativo) | CUBIERTO | `12/01` §7 — Apollo (💸) y LuaMancer, con el aviso de que son extensiones | — | — |
| G6 | `gm-cli`: init, run, compile, package, manual, resourcetool | CUBIERTO | `07 - Ecosistema/13 - GM CLI - la línea de comandos.md` (1 042 líneas, salidas reales) | — | README de gm-cli |
| G7 | **CI con GitHub Actions y gm-cli** (¿hay ejemplo?) | CUBIERTO | Sí, dos: `07/13` §11 «Los workflows de GitHub Actions que genera `init`» (`compile.yml`, `package.yml`) y `05 - Referencia/02 - Publicar y exportar.md` §5 «Automatizar la publicación (CI)» con el YAML completo, caché de `.gmcache`, FFmpeg obligatorio en Linux y el secreto `GAMEMAKER_PAT` | — | gm-cli `--actions` |
| G8 | Builds reproducibles | CUBIERTO | `13 - .../11 - Producción, alcance y lanzamiento.md` §4.6 «Builds reproducibles» | — | — |
| G9 | Git con GameMaker (`.gitignore`, `.gitattributes`, rooms) | CUBIERTO | `13/06` §3.13 «Git: qué se ignora y por qué duelen las rooms» + `13/11` §4.1 «Git con GameMaker» + `03 - Cursos (YouTube)/24 - DragoniteSpam - Getting Started - Control de Versiones con Git.md` | — | Manual `IDE_Tools/Source_Control` |
| G10 | Etiquetas, versionado semántico, sello de versión en el juego | CUBIERTO | `13/11` §4.2, §4.3, §4.4 | — | — |
| G11 | **Hot reload de código** (GMLive) | CUBIERTO | `12/01` §8 «Recarga en caliente (*live coding*)» — GMLive.gml, con el aviso de que es de pago y no está descargada | — | — |
| G12 | Documentación de código: JSDoc y **Tome** | CUBIERTO | `12/01` §6 «Documentar el proyecto» + `05 - Referencia/04 - Convenciones y estilo GML.md` + `01/07` | — | — |
| G13 | **Feather** y calidad de código | CUBIERTO | `02 - Novedades 2026/09 - Code Editor 2 y Feather.md` + `01/15` §2 «Nivel 1: Feather y errores de sintaxis» (códigos, avisos) | — | Manual |
| G14 | MCP y agentes de IA (`gm-cli resourcetool`) | CUBIERTO | `07 - Ecosistema/14 - IA y GameMaker.md` §3 (andamiaje `--ai`), §5 (flujo), §6bis (ecosistema MCP, GMSync) + `07/13` §6 (inventario completo de ResourceTool) | — | Blog oficial + verificación en vivo |

### Bloque H · Rendimiento, depuración, testing, exportación y operación

| # | Tema | Estado | Dónde | Qué falta | Fuente |
|---|---|---|---|---|---|
| H1 | Dónde está el cuello de botella: método | CUBIERTO | `01 - Fundamentos/15 - Depuración y rendimiento.md` §6 «Rendimiento: dónde está el cuello de botella» (medir → sospechosos → Texture → VM/YYC → compilador) | — | — |
| H2 | Texture swaps y vertex batches | CUBIERTO | `01/15` §6 y §4 (ventana Texture del overlay) + `01 - Fundamentos/11 - Dibujo y renderizado.md` | — | Manual `Texture_Pages` |
| H3 | Culling e instancias desactivadas | CUBIERTO | `01/15`, `01/10`, `01/11` (`instance_deactivate_region`) + `04/03`, `04/11` | — | — |
| H4 | VM vs **YYC** | CUBIERTO | `01/15` §6 paso 4; `05/02` §4.3; `13/10` §6.4 «Mide en YYC, no en VM» | — | — |
| H5 | Profiler / medición | CUBIERTO | `13/10` §6.1 «Medir con `get_timer()`», §6.2 GMBenchmark, §6.3 «El presupuesto por frame» | — | — |
| H6 | Memoria y **recolector de basura** | CUBIERTO | `01/15` §5 «El Garbage Collector» (generacional + incremental, `gc_collect`, lo que NO recoge, referencias débiles) | — | Manual |
| H7 | Debug Overlay y vistas personalizadas (`dbg_*`) | CUBIERTO | `01/15` §4 (ventanas FPS/Log/Audio/Memory/Texture, vistas personalizadas, la trampa del teclado bloqueado) | — | Manual |
| H8 | Log con niveles, asserts, capturas automáticas, modo QA | CUBIERTO | `13/06` §3.14 «Depuración estructurada» + `13/10` §7.1-§7.4 | — | — |
| H9 | Grabar y reproducir la entrada | CUBIERTO | `01/15` §3 «Grabación y reproducción de input» + `13/10` §7.1 + `13/06` §3.7 (replays deterministas) | — | — |
| H10 | Testing: framework propio en GML | CUBIERTO | `13 - .../10 - Testing y QA.md` §3 «Un mini-framework de pruebas en un solo script de GML» (incl. §3.4: `gm-cli run` NO devuelve el código de salida, con el script `correr-pruebas.sh`) | — | — |
| H11 | **GM-TestFramework** y crispy | CUBIERTO | `13/10` §4.1 y §4.2, con §4.3 «Cuál elegir» | — | <https://github.com/YoYoGames/GM-TestFramework> |
| H12 | Regresión, *golden files*, determinismo | CUBIERTO | `13/10` §5.1-§5.3 | — | — |
| H13 | QA manual, matriz de plataformas, *soak test*, monkey testing | CUBIERTO | `13/10` §9.1-§9.5 | — | — |
| H14 | Triaje de bugs y plantilla de informe | CUBIERTO | `13/10` §11.1-§11.3 | — | — |
| H15 | **Grupos de textura** y carga dinámica (`texturegroup_load`) | CUBIERTO | `08 - Referencia GML completa/08 - Texturas y grupos de texturas.md` §«Texturas dinámicas y grupos» (API completa) + `12 - Utilidades e integraciones/05 - Pipeline de arte, audio y niveles.md` §6bis «Atlas de texturas» («agrupa por sala, no por tipo») | — | Manual `Settings/Texture_Groups` |
| H16 | Grupos de audio | CUBIERTO | `01 - Fundamentos/13 - Audio.md`; `02 - Novedades 2026/07 - Audio - buses y efectos.md`; `04/25` | — | Manual |
| H17 | Exportación por plataforma (13 targets) | CUBIERTO | `05 - Referencia/02 - Publicar y exportar.md` §1 y §3 (GX.games, Opera GX, Reddit/Devvit, itch.io, Steam, Steam Deck, Android/iOS, consolas, Windows ARM64) | — | Release notes 2026.0 |
| H18 | HTML5: limitaciones y comunicación con servidor | CUBIERTO | `04/17` §3 «Lo que NO puedes hacer en web», §4 detección de plataforma, §5 servidor propio; `01 - Fundamentos/16 - Exportar y publicar.md` | — | — |
| H19 | Consolas: qué se puede decir sin NDA | CUBIERTO | `05/02` §1.4 «Consolas: wikis privadas» y §3.8 (Switch 2 nuevo en 2026.0, licencia Enterprise, proceso de aprobación, aviso explícito de NDA) | — | Release notes + artículo de ayuda oficial |
| H20 | Requisitos de certificación (TRC/TCR/lotcheck) | PARCIAL (por naturaleza) | `04 - Recetas por género/27 - Accesibilidad.md` avisa de que algo es «requisito de certificación»; `05/02` §6 «Vacíos de información (honestidad)» | Lo público sí se puede decir: mapeo de botones consistente, soporte de suspensión/reanudación, gestión de usuario y desconexión de mando, tiempos de arranque, textos legales. Hoy no está en ningún sitio | Manual `Consoles`; guías públicas de plataforma |
| H21 | **Crash reporting** (`exception_unhandled_handler`) | CUBIERTO | `13/11` §4.5 «Recoger las caídas desde el día 1» (código compilado y verificado con `gm-cli compile`, exit 0, 06-09-2026) + `01/15` §3 | — | Manual |
| H22 | Telemetría / analítica | CUBIERTO | `13/01` §9.5 «Telemetría: contar muertes por sala y volcarlas a JSON» y §9.6 + `13/10` §10.4 «Telemetría mínima» + `13/11` §7 «Telemetría con consentimiento» (RGPD) | — | Valve, *Half-Life 2 playtesting*; RGPD |
| H23 | Parcheo y post-lanzamiento | CUBIERTO | `13/11` §7 «Post-lanzamiento» (parches, roadmap, SemVer, «un parche que toca el formato de guardado sube el MAYOR») | — | — |
| H24 | Accesibilidad técnica | CUBIERTO | `04 - Recetas por género/27 - Accesibilidad.md` (daltonismo, subtítulos, reduce motion, accesibilidad motriz, checklist) | — | Game Accessibility Guidelines |
| H25 | **GMRT** y futuro | CUBIERTO | `02 - Novedades 2026/03 - GMRT - El nuevo runtime.md` (arquitectura, instalación, cambios de GML, 0.20/0.21, cuándo NO usarlo) + `02 - Novedades 2026/10 - Futuro - roadmap 2026-2028.md` | — | Repo oficial GMRT |

---

### Recuento

| Estado | Nº |
|---|---:|
| CUBIERTO | 63 |
| PARCIAL | 12 |
| FALTA | 8 |
| **Total** | **83** |

Los ocho **FALTA**: Flyweight · Prototype · Subclass Sandbox · Data Locality · Dirty Flag · ECS ·
Jump Point Search · pathfinding para plataformas · NAT traversal *(nueve contando este último;
el recuento de la tabla los agrupa por bloque)*.

---

## 2 · Propuestas priorizadas

> Criterio de agrupación: **ningún documento nuevo para un solo patrón**. Los huecos pequeños
> se acumulan en tres documentos y el resto son secciones dentro de documentos existentes.

### 🔴 Prioridad alta

**P1 · `13 - Diseño y producción de videojuegos/14 - Catálogo de patrones en GML.md`** *(documento nuevo)*
Cierra los seis patrones de Nystrom sin traducir (**Flyweight, Prototype, Subclass Sandbox,
Data Locality, Dirty Flag, Event Queue**) y añade el veredicto sobre **ECS en GML**. Formato ya
establecido en la casa: por patrón, «el problema en GameMaker → el código → cuándo NO usarlo →
coste», enlazando a lo que ya existe (Command §3.7, Component §3.6, Service Locator §3.3,
Object Pool `scr_pool.gml`, Spatial Partition 13/08 §4.1, Type Object §3.8, Double Buffer 13/07)
en vez de repetirlo. Cierra con una tabla «los 19 de Nystrom → dónde está cada uno en esta
biblioteca», que es exactamente lo que un LLM necesita para no reinventarlos. Debe medir el
Data Locality con `get_timer()` (array plano vs anidado) para que no sea folclore.

**P2 · `04 - Recetas por género/32 - Pathfinding avanzado.md`** *(documento nuevo)*
Lo que `06/scr_grid_pathfinding.gml` deja fuera y las recetas piden a gritos: **flow field**
(BFS desde el destino, array plano de direcciones, cuándo recalcular — `04/13` lo recomienda dos
veces sin darlo), **Jump Point Search** sobre el `GridPonderado` ya escrito, **pathfinding en
plataformas** (grafo de plataformas con aristas de salto/caída, que `mp_grid` no puede resolver),
y suavizado de rutas + *path following* con `steering`. Enlaza a `04/23` para el movimiento y a
`13/13` §6 para la geometría.

**P3 · `07 - Ecosistema/22 - Crear una extensión nativa (guía en español).md`** *(documento nuevo)*
El único hueco donde el manual oficial documenta algo entero y la biblioteca solo tiene enlaces.
Paso a paso real: crear el asset Extension en el IDE, *Copies To*, ficheros `.dll`/`.dylib`/`.so`
y placeholders, la firma C que espera GameMaker (`double`, `char*`, `RValue`), declarar la función
en el IDE, `GM-ExtensionGenerator` para el esqueleto, y las tres variantes que tienen reglas
propias (Android con `.jar`/placeholder, iOS con `.mm`, HTML5 remitiendo a `04/17`). Fuente: espejo
local `09 - Manual oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/`.

**P4 · `04 - Recetas por género/33 - Modding y contenido externo.md`** *(documento nuevo)*
Une las piezas que hoy están en cinco sitios sin hablarse: carpeta `mods/` dentro del *save area*
(límites del sandbox de `01/14`), `sprite_add` y sus restricciones por plataforma,
`texturegroup_add` para atlas descargados, fusionar un JSON de mod sobre el catálogo base de
`13/06` §3.8, ejecutar scripts de jugador con **catspeak-lang** sin abrir un agujero, y publicar
con **GMEXT-mod.io**. Incluye la sección de riesgo: qué puede romper un mod y cómo aislarlo.

### 🟡 Prioridad media

**P5 · Sección nueva en `04 - Recetas por género/14 - Multijugador.md`: «§10 · Salas, matchmaking y por qué tu servidor no es alcanzable»**
Cubre **lobbies** (modelo de datos de una sala, crear/listar/unirse, con `steam_lobby_*` que sí
está en el runtime), **matchmaking** básico por MMR o por cola, y **NAT** — por qué un servidor
casero no funciona y las tres salidas reales (relay tipo Photon, dedicado tipo Colyseus, Steam
datagram). Hoy §1.2 y `12/04` §2 lo delegan todo a una librería sin explicar el problema.

**P6 · Sección nueva en `13 - Diseño y producción de videojuegos/10 - Testing y QA.md`: «§14 · Seguridad y anti-trampas»**
Recoge lo que hoy está partido: validar antes de subir a un leaderboard, detectar valores
imposibles, replay firmado para rankings de un jugador, editar la memoria (Cheat Engine) y por
qué la ofuscación de `01/14` §12 solo detiene al curioso, y el enlace a «nunca confíes en el
cliente» de `04/14` §2.2. Cierra con la frase honesta: en un juego de un jugador el anti-cheat
no rentable; en uno con ranking, la única defensa es el servidor.

**P7 · Ampliar `04 - Recetas por género/25 - Menú de opciones y ajustes.md` §5 «Reasignar controles»**
Hoy son 15 líneas de esbozo. Añadir: detección de conflictos entre acciones, perfiles (teclado /
mando 1 / mando 2), rebinding de **ejes** de mando, glifos del botón según el mando conectado
(`gamepad_get_description`), y el guardado en `config.json` según la tabla de `13/06` §3.10.
Puede quedarse aquí; no merece documento propio.

**P8 · Sección nueva en `01 - Fundamentos/06 - Eventos y ciclo del juego.md`: «§8bis · Pausar de verdad»**
Qué pasa con las **time sources** (`time_source_pause`/`time_source_resume`, que hoy no aparecen
en ningún documento de la biblioteca), las alarmas, el audio, las partículas y las secuencias al
poner `global.pausado = true`. Es la causa nº 1 de bugs de pausa y hoy solo existe el `if
(global.pausado) return;` de `04/00` §5.

### 🟢 Prioridad baja

**P9 · Pieza nueva en `06 - Assets y Scripts/scr_tiempo.gml`** *(script nuevo)*
Recoge tres cosas que hoy se reescriben en cada receta: un struct `Cooldown` (`usar()`,
`listo()`, `fraccion()` para la barra de la UI), un `Temporizador` independiente del framerate
(la fórmula de `13/13` §12.3), y un reloj de juego con escala de tiempo enganchado al
`global.time_scale` de `04/15` §5.0. Un solo fichero, documentado con JSDoc como el resto.

**P10 · Sección nueva en `05 - Referencia/02 - Publicar y exportar.md`: «§3.8bis · Qué exige una consola aunque no puedas contarlo»**
Lo público de la certificación, sin tocar NDA: mapeo de botones consistente y el botón de
confirmar según región, suspensión/reanudación, desconexión de mando y cambio de usuario, tiempos
de arranque, guardado que no puede fallar, textos legales y avisos de salud. Encaja como
ampliación de §3.8, no como documento.

**P11 · Ampliar `12 - Utilidades e integraciones/01 - Herramientas del flujo de trabajo.md` §7**
Convertir la tabla de intérpretes en una decisión: cuándo un juego necesita de verdad un lenguaje
embebido (reglas editables por el jugador, mods, contenido de temporada sin recompilar) y cuándo
un JSON basta. Dos párrafos y un ejemplo mínimo de Catspeak. Sirve de aterrizaje al patrón
*Bytecode* de P1.

**P12 · Ampliar `13/06` §3.10 con el autoguardado**
Tres párrafos: cuándo dispararlo (cambio de sala, hito, nunca en transición), escritura atómica
(temporal + `file_rename`) para que un corte de luz no deje el guardado a medias, indicador
visible, y por qué el autoguardado va a su propia ranura.

---

## 3 · Limitaciones

1. **No abrí `11 - Código descargado/` ni `03 - Cursos (YouTube)/` en profundidad.** El brief los
   deja fuera de la lista de carpetas a *grepear* salvo `10 - Cursos en español`. Es posible que
   algún patrón (por ejemplo un quadtree o un flow field) esté implementado en el corpus
   descargado; `13/08` §4.4 dice explícitamente que «en el corpus hay quadtrees funcionando».
   Eso no cambia el veredicto: código de terceros descargado ≠ documentación en español, y el
   propio `AGENTS.md` sitúa el corpus en el nivel 5 de autoridad.
2. **No verifiqué que el código de los documentos compile.** Me apoyé en las notas de la propia
   biblioteca (`13/11` §4.5 y `13/10` declaran compilación verificada con `gm-cli compile`,
   exit 0). No ejecuté `gm-cli` en esta auditoría.
3. **El índice de *Game Engine Architecture* lo usé de memoria estructural**, no descargado: el
   libro no tiene índice público estable en HTML. Lo he usado solo para el reparto de subsistemas
   (recursos, HID, tiempo, depuración, IA, red), no para afirmaciones concretas.
4. **`gamemaker.io` y `manual.gamemaker.io` no los consulté en vivo** (403 conocido): usé el
   espejo local `09 - Manual oficial/`, que resultó suficiente y está en la rama LTS correcta.
   Sí verifiqué en vivo el índice de *Game Programming Patterns* con `curl`.
5. **La cifra de 83 temas es mía**, construida para este dominio; no es una lista canónica de
   nadie. Los 19 patrones sí son la lista literal de Nystrom.
6. **Solapamiento con otros auditores.** Varios temas de mi dominio (localización, diálogo,
   accesibilidad, audio) los cubre mejor otro auditor; los he marcado CUBIERTO con su ruta y no
   he propuesto nada sobre ellos para no duplicar propuestas.
