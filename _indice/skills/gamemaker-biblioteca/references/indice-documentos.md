# Índice de documentos de la biblioteca

> **Generado por `_indice/sincronizar-skill.py` desde `MAPA.json`. No lo edites a mano:**
> se reescribe en cada `python3 _indice/actualizar.py`.

Versión de referencia: LTS 2026.0.0 (IDE 2026.0.0.16 / runtime GMS2 2026.0.0.23) · Beta 2026.100.0 (IDE 1139 / runtime 1090) · GMRT 0.21.

Todas las rutas son relativas a la raíz de la biblioteca, la que resuelve `$BIB` (ver la cabecera de la skill).


## Puntos de entrada

- `RUTA.md` — **🎓 Ruta completa: de cero a experto**
  Itinerario maestro en 6 niveles (0 Cero → 5 Profesional) con competencias observables, material exacto por nivel y una prueba de nivel.
  *Úsalo cuando:* el usuario está aprendiendo y hay que situarlo; qué estudio ahora / por dónde sigo; cuánto me falta para X; no sé si estoy listo para hacer un juego comercial.
  *Para el agente:* Situar al usuario por lo que SABE HACER, no por lo que dice saber, y entregar solo material de su nivel y del siguiente.
- `README.md` — **Biblioteca GameMaker · para que tu agente de IA no invente funciones**
- `AGENTS.md` — **AGENTS.md — cómo usar esta biblioteca si eres un agente de IA**
- `_indice/COMO-BUSCAR.md` — **Árbol de decisión para encontrar cualquier cosa**
- `CLAUDE.md` — **CLAUDE.md**
  Arranque mínimo: las 5 reglas irrenunciables y el desvío a AGENTS.md (instrucciones completas) y a _indice/COMO-BUSCAR.md (cómo buscar). Deliberadamente corto: se carga en cada sesión.
  *Úsalo cuando:* empiezas una sesión en este repositorio; quieres las reglas antes de tocar nada.
- `PUBLICAR.md` — **Publicar esta biblioteca**


## `01 - Fundamentos` — Fundamentos de GML

Explicación conceptual de GameMaker desde cero, en español. El manual oficial reordenado con el «por qué» y las trampas marcadas.

**Usar cuando:** no entiendo un concepto · vengo de otro motor · por qué mi código no se ejecuta cuando espero · qué es un handle · cómo funcionan structs, arrays, eventos, colisiones, cámaras, audio, persistencia · cómo exporto o publico mi juego

**No usar para:** buscar la firma exacta de una función (usa buscar.py)

- `01 - Fundamentos/01 - El IDE y el flujo de trabajo.md` — 01 · El IDE y el flujo de trabajo
- `01 - Fundamentos/02 - Tipos de datos y variables.md` — 02 · Tipos de datos y variables
- `01 - Fundamentos/03 - Handles - el cambio clave de 2026.md` — 03 · Handles — el cambio clave de 2026
- `01 - Fundamentos/04 - Structs y constructores (POO en GML).md` — 04 · Structs y constructores (POO en GML)
- `01 - Fundamentos/05 - Arrays y estructuras de datos.md` — 05 · Arrays y estructuras de datos
- `01 - Fundamentos/06 - Eventos y ciclo del juego.md` — 06 · Eventos y ciclo del juego
- `01 - Fundamentos/07 - Funciones, métodos y ámbito.md` — 07 · Funciones, métodos y ámbito
- `01 - Fundamentos/08 - Movimiento y colisiones.md` — 08 · Movimiento y colisiones
- `01 - Fundamentos/09 - Instancias, objetos y herencia.md` — 09 · Instancias, objetos y herencia
- `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md` — 10 · Rooms, capas, cámaras y viewports
- `01 - Fundamentos/11 - Dibujo y renderizado.md` — 11 · Dibujo y renderizado
- `01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md` — 12 · Input — teclado, ratón y gamepad
- `01 - Fundamentos/13 - Audio.md` — 13 · Audio
- `01 - Fundamentos/14 - Persistencia y archivos.md` — 14 · Persistencia y archivos
- `01 - Fundamentos/15 - Depuración y rendimiento.md` — 15 · Depuración y rendimiento
- `01 - Fundamentos/16 - Exportar y publicar.md` — 16 · Exportar y publicar
- `01 - Fundamentos/17 - GML Visual (Drag and Drop).md` — 17 · GML Visual (Drag and Drop)
- `01 - Fundamentos/_INDICE-FUNDAMENTOS.md` — Índice · Fundamentos de GML (GameMaker LTS 2026)


## `02 - Novedades 2026` — Novedades de 2026

Qué cambió en LTS 2026 y qué rompe el código antiguo. Handles, GMRT, UI Layers, Flexpanels, partículas nuevas, buses de audio, Package Manager, Code Editor 2, roadmap.

**Usar cuando:** portar un proyecto antiguo · el código de un tutorial no compila · quiero usar algo nuevo del motor · qué es GMRT

- `02 - Novedades 2026/01 - Resumen LTS 2026.0.md` — Resumen ejecutivo: GameMaker LTS 2026.0
- `02 - Novedades 2026/02 - Cambios en GML 2026.md` — Cambios en GML en 2026 (LTS 2026.0)
- `02 - Novedades 2026/03 - GMRT - El nuevo runtime.md` — GMRT — El nuevo runtime de GameMaker (codename Cronus)
- `02 - Novedades 2026/04 - UI Layers y Flexpanels.md` — UI Layers y Flexpanels (LTS 2026.0)
- `02 - Novedades 2026/05 - Sistema de partículas nuevo.md` — El nuevo sistema de partículas (LTS 2026.0)
- `02 - Novedades 2026/06 - Gráficos - SVG, SDF, FX y superficies.md` — Gráficos: SVG, SDF, FX, superficies y texturas (LTS 2026.0)
- `02 - Novedades 2026/07 - Audio - buses y efectos.md` — Audio: buses, efectos y nuevas funciones (LTS 2026.0)
- `02 - Novedades 2026/08 - Package Manager y Prefabs.md` — Package Manager y Prefabs (LTS 2026.0)
- `02 - Novedades 2026/09 - Code Editor 2 y Feather.md` — Code Editor 2 y Feather (LTS 2026.0)
- `02 - Novedades 2026/10 - Futuro - roadmap 2026-2028.md` — Futuro de GameMaker: roadmap 2026–2028
- `02 - Novedades 2026/_INDICE-NOVEDADES.md` — Índice — Novedades de GameMaker 2026


## `03 - Cursos (YouTube)` — Cursos de YouTube transcritos (origen en inglés)

44 capítulos de curso transcritos, traducidos y reescritos: Sky LaRell Anderson (12), DragoniteSpam (26), PixelatedPope cámaras (4), plataformas oficial.

**Usar cuando:** aprender haciendo, paso a paso · seguir un proyecto acumulativo · cámaras y resolución en profundidad

- `03 - Cursos (YouTube)/01 - Curso 2026 - Sky LaRell Anderson - Parte 1 - El Espacio de Trabajo.md` — 01 · El espacio de trabajo
- `03 - Cursos (YouTube)/02 - Curso 2026 - Sky LaRell Anderson - Parte 2 - Objetos, Sprites y Rooms.md` — 02 · Objetos, sprites y rooms
- `03 - Cursos (YouTube)/03 - Curso 2026 - Sky LaRell Anderson - Parte 3 - Movimiento Básico y Colisiones.md` — 03 · Movimiento básico y colisiones
- `03 - Cursos (YouTube)/04 - Curso 2026 - Sky LaRell Anderson - Parte 4 - Movimiento de Plataformas.md` — 04 · Movimiento de plataformas
- `03 - Cursos (YouTube)/05 - Curso 2026 - Sky LaRell Anderson - Parte 5 - Raton y Menus.md` — 05 · Ratón y menús
- `03 - Cursos (YouTube)/06 - Curso 2026 - Sky LaRell Anderson - Parte 6 - Disparar Proyectiles.md` — 06 · Disparar proyectiles
- `03 - Cursos (YouTube)/07 - Curso 2026 - Sky LaRell Anderson - Parte 7 - Cámaras.md` — 07 · Cámaras
- `03 - Cursos (YouTube)/08 - Curso 2026 - Sky LaRell Anderson - Parte 8 - Enemigos y Vida.md` — 08 · Enemigos y puntos de vida
- `03 - Cursos (YouTube)/09 - Curso 2026 - Sky LaRell Anderson - Parte 9 - Sonidos y Música.md` — 09 · Crear tus propios sonidos y música
- `03 - Cursos (YouTube)/10 - Curso 2026 - Sky LaRell Anderson - Parte 10 - Recursos de Arte.md` — 10 · Crear tus propios recursos de arte
- `03 - Cursos (YouTube)/11 - Curso 2026 - Sky LaRell Anderson - Parte 11 - Animaciones y Tile Sets.md` — 11 · Animaciones y conjuntos de baldosas (tile sets)
- `03 - Cursos (YouTube)/12 - Curso 2026 - Sky LaRell Anderson - Parte 12 - Exportar y Publicar.md` — 12 · Exportar y publicar
- `03 - Cursos (YouTube)/13 - DragoniteSpam - Getting Started - Primeros Pasos con GameMaker.md` — 13 · DragoniteSpam — Primeros pasos con GameMaker (2025/2026)
- `03 - Cursos (YouTube)/14 - DragoniteSpam - Getting Started - Fundamentos del Código.md` — 14 · DragoniteSpam — Los fundamentos del código
- `03 - Cursos (YouTube)/15 - DragoniteSpam - Getting Started - Sprites y Objetos.md` — 15 · DragoniteSpam — Sprites y objetos
- `03 - Cursos (YouTube)/16 - DragoniteSpam - Getting Started - Editor de Rooms, Tiles y Tile Sets.md` — 16 · DragoniteSpam — El editor de rooms: tiles, tile sets y capas de sprites
- `03 - Cursos (YouTube)/17 - DragoniteSpam - Getting Started - Autotiles.md` — 17 · DragoniteSpam — Autotiles
- `03 - Cursos (YouTube)/18 - DragoniteSpam - Getting Started - Baldosas Animadas.md` — 18 · DragoniteSpam — Baldosas animadas
- `03 - Cursos (YouTube)/19 - DragoniteSpam - Getting Started - Pinceles de Baldosas.md` — 19 · DragoniteSpam — Pinceles de baldosas (tile brushes)
- `03 - Cursos (YouTube)/20 - DragoniteSpam - Getting Started - Viewports y Cámaras.md` — 20 · DragoniteSpam — Viewports y cámaras
- `03 - Cursos (YouTube)/21 - DragoniteSpam - Getting Started - Crear Instancias de Objetos.md` — 21 · DragoniteSpam — Crear instancias de objetos por código
- `03 - Cursos (YouTube)/22 - DragoniteSpam - Getting Started - Numeros Aleatorios.md` — 22 · DragoniteSpam — Generar números aleatorios
- `03 - Cursos (YouTube)/23 - DragoniteSpam - Getting Started - Respaldos con YYZ.md` — 23 · DragoniteSpam — Copias de seguridad con archivos YYZ
- `03 - Cursos (YouTube)/24 - DragoniteSpam - Getting Started - Control de Versiones con Git.md` — 24 · DragoniteSpam — Control de versiones con Git
- `03 - Cursos (YouTube)/25 - DragoniteSpam - Getting Started - Bucle Repeat.md` — 25 · DragoniteSpam — El bucle `repeat`
- `03 - Cursos (YouTube)/26 - DragoniteSpam - Getting Started - Bucle While.md` — 26 · DragoniteSpam — El bucle `while`
- `03 - Cursos (YouTube)/27 - DragoniteSpam - Getting Started - Bucle For.md` — 27 · DragoniteSpam — El bucle `for`
- `03 - Cursos (YouTube)/28 - DragoniteSpam - Getting Started - Bucle Do Until.md` — 28 · DragoniteSpam — El bucle `do / until`
- `03 - Cursos (YouTube)/29 - DragoniteSpam - Getting Started - Colisiones Básicas.md` — 29 · DragoniteSpam — Colisiones básicas
- `03 - Cursos (YouTube)/30 - DragoniteSpam - Getting Started - Move and Collide.md` — 30 · DragoniteSpam — `move_and_collide()`
- `03 - Cursos (YouTube)/31 - DragoniteSpam - Getting Started - Dibujar Sprites.md` — 31 · DragoniteSpam — Dibujar sprites
- `03 - Cursos (YouTube)/32 - DragoniteSpam - Getting Started - Dibujar Formas.md` — 32 · DragoniteSpam — Dibujar formas
- `03 - Cursos (YouTube)/33 - DragoniteSpam - Getting Started - Dibujar Texto.md` — 33 · DragoniteSpam — Dibujar texto
- `03 - Cursos (YouTube)/34 - DragoniteSpam - Getting Started - Usar Fuentes.md` — 34 · DragoniteSpam — Usar fuentes
- `03 - Cursos (YouTube)/35 - DragoniteSpam - Getting Started - Evento Draw GUI.md` — 35 · DragoniteSpam — El evento Draw GUI
- `03 - Cursos (YouTube)/36 - DragoniteSpam - Getting Started - Por Qué Todo se ve Borroso.md` — 36 · DragoniteSpam — ¿Por qué todo se ve borroso?
- `03 - Cursos (YouTube)/37 - DragoniteSpam - Getting Started - Error Variable No Definida.md` — 37 · DragoniteSpam — El temido «Variable Not Set Before Reading It»
- `03 - Cursos (YouTube)/38 - DragoniteSpam - Getting Started - Fechas y Horas.md` — 38 · DragoniteSpam — Fechas y horas
- `03 - Cursos (YouTube)/39 - GameMaker Oficial - Tu Primer Plataformas en 15 Minutos.md` — 39 · GameMaker oficial — Tu primer plataformas en 15 minutos
- `03 - Cursos (YouTube)/40 - GameMaker LTS 2026 - Novedades e Instalación.md` — 40 · GameMaker LTS 2026 ya está aquí
- `03 - Cursos (YouTube)/41 - PixelatedPope - Cámaras y Resolución 2026 - Parte 1 - Principiante.md` — 41 · Cámaras y resolución I — principiante (sin escribir código)
- `03 - Cursos (YouTube)/42 - PixelatedPope - Cámaras y Resolución 2026 - Parte 2 - Intermedio.md` — 42 · Cámaras y resolución II — intermedio (la cámara por código)
- `03 - Cursos (YouTube)/43 - PixelatedPope - Cámaras y Resolución 2026 - Parte 3 - Avanzado.md` — 43 · Cámaras y resolución III — avanzado (objetivos dinámicos, sacudida, zoom, pantalla completa)
- `03 - Cursos (YouTube)/44 - PixelatedPope - Cámaras y Resolución 2026 - Parte 4 - Experto.md` — 44 · Cámaras y resolución IV — experto (la capa GUI, dibujar en una caja, filtrado bilineal y el mito del escalado perfecto)
- `03 - Cursos (YouTube)/_DESCUBIERTAS.md` — Descubiertas — más cursos, canales y series de GameMaker
- `03 - Cursos (YouTube)/_ENLACES-ORIGINALES.md` — Índice maestro de enlaces originales
- `03 - Cursos (YouTube)/_INDICE-CURSOS.md` — Índice de cursos de GameMaker (YouTube)


## `04 - Recetas por género` — Recetas por género

46 recetas: 15 géneros destripados sistema por sistema, el plano de un juego completo (00) y 30 transversales — game feel, señales, web, menús, ritmo, servicios de plataforma, localización, Box2D, IA de movimiento y de decisión, iluminación (básica y avanzada), opciones y rebinding, música adaptativa, accesibilidad, móvil, 3D, combate cuerpo a cuerpo y a distancia, daño y efectos de estado, enemigos y director, por turnos y táctico, habilidades, traversal, pathfinding avanzado, VFX, tutorial, transiciones y pausa, audio reactivo, modding, bullet heaven/autobattler/deckbuilder y géneros sin receta propia.

**Usar cuando:** me piden hacer un juego de X género · qué sistemas necesito y en qué orden · game feel y juice · cómo publico mi juego en la web · una lista más larga que la pantalla · sincronizar la lógica con la música · un juego para móvil / táctil · hacer 3D o 2.5D en GameMaker · golpes con hitbox y hurtbox, combos · enemigos que deciden: árboles de comportamiento, utility, GOAP · daño por tipos, resistencias y efectos de estado · que los enemigos no ataquen todos a la vez · recarga, dispersión y disparo hitscan · pendientes, wall jump, escaleras, nadar · muchas unidades hacia un mismo destino · explosiones y efectos que no parezcan de asset gratis · tutorial y prompts de botón · menú de pausa y pantalla de carga · que el audio responda al mundo · permitir mods · sigilo, horror, granja o idle

- `04 - Recetas por género/00 - Anatomía de un juego completo.md` — 00 · Anatomía de un juego completo — de principio a fin
- `04 - Recetas por género/01 - Plataformas 2D.md` — 01 — Plataformas 2D
- `04 - Recetas por género/02 - Top-Down _ Twin-Stick.md` — 02 — Top-Down / Twin-Stick
- `04 - Recetas por género/03 - Shoot em up (shmup).md` — 03 — Shoot 'em up (shmup)
- `04 - Recetas por género/04 - RPG _ Action RPG.md` — 04 — RPG / Action RPG
- `04 - Recetas por género/05 - Roguelike y generación procedural.md` — 05 — Roguelike y generación procedural
- `04 - Recetas por género/06 - Metroidvania.md` — 06 — Metroidvania
- `04 - Recetas por género/07 - Puzzle y Match-3.md` — 07 — Puzzle / Match-3
- `04 - Recetas por género/08 - Tower Defense.md` — 08 — Tower Defense
- `04 - Recetas por género/09 - Survival y crafting.md` — 09 — Survival y crafting
- `04 - Recetas por género/10 - Visual Novel y narrativa.md` — 10 — Visual Novel y narrativa
- `04 - Recetas por género/11 - Arcade y juegos de un botón.md` — 11 — Arcade y juegos de un botón
- `04 - Recetas por género/12 - Carreras y vehículos.md` — 12 — Carreras y vehículos
- `04 - Recetas por género/13 - Estrategia y gestión.md` — 13 — Estrategia y gestión
- `04 - Recetas por género/14 - Multijugador.md` — 14 — Multijugador
- `04 - Recetas por género/15 - Game feel y juice.md` — 15 — Game feel y juice
- `04 - Recetas por género/16 - Señales y desacoplamiento.md` — 16 · Señales y desacoplamiento
- `04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md` — 17 · Interoperabilidad con la web (HTML5)
- `04 - Recetas por género/18 - Menús con scroll y navegación.md` — 18 · Menús con scroll y navegación
- `04 - Recetas por género/19 - Programación rítmica (juegos de ritmo).md` — 19 · Programación rítmica (juegos de ritmo)
- `04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md` — 20 · Servicios de plataforma: logros, anuncios, compras, leaderboards y nube
- `04 - Recetas por género/21 - Localización e idiomas (con traducción por IA).md` — 21 · Localización e idiomas — con traducción por IA
- `04 - Recetas por género/22 - Físicas con Box2D.md` — 22 · Físicas con Box2D
- `04 - Recetas por género/23 - IA de enemigos y steering behaviors.md` — 23 · IA de enemigos y steering behaviors
- `04 - Recetas por género/24 - Iluminación 2D.md` — 24 · Iluminación 2D
- `04 - Recetas por género/25 - Menú de opciones y ajustes.md` — 25 · Menú de opciones y ajustes
- `04 - Recetas por género/26 - Música adaptativa por capas.md` — 26 · Música adaptativa por capas
- `04 - Recetas por género/27 - Accesibilidad.md` — 27 · Accesibilidad
- `04 - Recetas por género/28 - Juegos para móvil (táctil).md` — 28 · Juegos para móvil (táctil)
- `04 - Recetas por género/29 - 3D en GameMaker.md` — 29 · 3D en GameMaker
- `04 - Recetas por género/30 - Combate cuerpo a cuerpo - hitboxes, hurtboxes y combos.md` — 30 · Combate cuerpo a cuerpo — hitboxes, hurtboxes y combos
- `04 - Recetas por género/31 - IA de decisión - árboles de comportamiento, utility y GOAP.md` — 31 · IA de decisión — árboles de comportamiento, utility y GOAP
- `04 - Recetas por género/32 - Sistema de daño y efectos de estado.md` — 32 · Sistema de daño y efectos de estado
- `04 - Recetas por género/33 - Diseño de enemigos, encuentros y director de combate.md` — 33 · Diseño de enemigos, encuentros y director de combate
- `04 - Recetas por género/34 - Combate a distancia - armas, munición y balística.md` — 34 · Combate a distancia — armas, munición y balística
- `04 - Recetas por género/35 - Combate por turnos y táctico en rejilla.md` — 35 · Combate por turnos y táctico en rejilla
- `04 - Recetas por género/36 - Habilidades, enfriamientos y recursos de combate.md` — 36 · Habilidades, enfriamientos y recursos de combate
- `04 - Recetas por género/37 - Traversal en plataformas - pendientes, paredes, escaleras y bordes.md` — 37 — Traversal en plataformas: pendientes, paredes, escaleras y bordes
- `04 - Recetas por género/38 - Pathfinding avanzado - flow fields, JPS y plataformas.md` — 38 · Pathfinding avanzado — flow fields, JPS y plataformas
- `04 - Recetas por género/39 - VFX - diseño y catálogo de efectos.md` — 39 · VFX — diseño y catálogo de efectos
- `04 - Recetas por género/40 - Tutorial, onboarding y prompts en pantalla.md` — 40 · Tutorial, onboarding y prompts en pantalla
- `04 - Recetas por género/41 - Transiciones, carga y pausa.md` — 41 · Transiciones, carga y pausa
- `04 - Recetas por género/42 - Audio reactivo al mundo - materiales, zonas y estados de mezcla.md` — 42 · Audio reactivo al mundo — materiales, zonas y estados de mezcla
- `04 - Recetas por género/43 - Modding y contenido externo.md` — 43 · Modding y contenido externo
- `04 - Recetas por género/44 - Bullet heaven, autobattler y deckbuilder.md` — 44 · Bullet heaven, autobattler y deckbuilder
- `04 - Recetas por género/45 - Géneros sin receta propia - sigilo, horror, táctica, granja y idle.md` — 45 · Géneros sin receta propia — sigilo, horror, táctica, granja y idle
- `04 - Recetas por género/46 - Eje Z falso - altura, sombras y profundidad en un juego 2D.md` — 46 · Eje Z falso — altura, sombras y profundidad en un juego 2D
- `04 - Recetas por género/47 - Beat em up y brawler.md` — 47 · Beat 'em up y brawler
- `04 - Recetas por género/48 - Aventura gráfica y point and click.md` — 48 · Aventura gráfica y point and click
- `04 - Recetas por género/49 - Deportes y física de mesa.md` — 49 · Deportes y física de mesa
- `04 - Recetas por género/50 - Juego de lucha.md` — 50 · Juego de lucha
- `04 - Recetas por género/51 - Colonia y constructor de bases - trabajadores autónomos.md` — 51 · Colonia y constructor de bases — trabajadores autónomos
- `04 - Recetas por género/52 - Live-ops técnico (config remota, versión mínima, mensajes del juego).md` — 52 · Live-ops técnico (config remota, versión mínima, mensajes del juego)
- `04 - Recetas por género/53 - Souls-like - lock-on, hoguera y pérdida de recursos al morir.md` — 53 · Souls-like — hoguera y pérdida de recursos al morir
- `04 - Recetas por género/54 - Metajuego transversal - logros, galería, speedrun y espectador.md` — 54 · Metajuego transversal — logros, galería, speedrun y espectador
- `04 - Recetas por género/55 - Party games, minijuegos y creación casual.md` — 55 · Party games, minijuegos y creación casual
- `04 - Recetas por género/56 - Combate no letal - pacifismo, aturdir, huir y negociar.md` — 56 · Combate no letal — pacifismo, aturdir, huir y negociar
- `04 - Recetas por género/57 - Selección de nivel y capítulo.md` — 57 · Selección de nivel y capítulo
- `04 - Recetas por género/58 - El nivel como mapa de texto - construir sin abrir el editor de salas.md` — 58 · El nivel como mapa de texto — construir sin abrir el editor de salas
- `04 - Recetas por género/_INDICE-RECETAS.md` — Recetas por género — GameMaker LTS 2026.0 (IDE 16 / Runtime 23)


## `05 - Referencia` — Referencia rápida

Tutoriales oficiales catalogados, publicación y exportación, glosario A-Z y convenciones de estilo GML.

**Usar cuando:** cómo se llama esto en GameMaker · cómo publico en Steam/itch/móvil · qué convención de nombres uso

- `05 - Referencia/01 - Tutoriales oficiales.md` — 01 · Tutoriales oficiales de GameMaker
- `05 - Referencia/02 - Publicar y exportar.md` — 02 · Publicar y exportar un juego de GameMaker (2026)
- `05 - Referencia/03 - Glosario GML.md` — 03 · Glosario GML (A–Z)
- `05 - Referencia/04 - Convenciones y estilo GML.md` — 04 · Convenciones y estilo GML
- `05 - Referencia/05 - Entregar el juego - firmar, notarizar y subir a las tiendas.md` — 05 · Entregar el juego: firmar, notarizar y subir a las tiendas
- `05 - Referencia/06 - Publicar en consolas - Nintendo, PlayStation y Xbox.md` — 06 · Publicar en consolas: Nintendo, PlayStation y Xbox


## `06 - Assets y Scripts` — Scripts GML propios listos para copiar

9 scripts .gml reutilizables verificados: matemáticas, cámara, máquina de estados, tweens, guardado, pooling, A*, buffer de input, debug.

**Usar cuando:** necesito un sistema base ya escrito y verificado

**No usar para:** librerías grandes de terceros (eso está en 11)

- `06 - Assets y Scripts/README.md` — 06 · Assets y Scripts — Scripts GML reutilizables
- `06 - Assets y Scripts/scr_audio.gml` — scr_audio — Gestor de audio completo: buses y emisores por categoría, mezcla
- `06 - Assets y Scripts/scr_camera.gml` — scr_camera — Cámara 2D con seguimiento, deadzone, look-ahead, límites de sala y shake
- `06 - Assets y Scripts/scr_debug.gml` — scr_debug — Utilidades de depuración: panel de variables en vivo, log en pantalla
- `06 - Assets y Scripts/scr_grid_pathfinding.gml` — scr_grid_pathfinding — Pathfinding en rejilla. Dos implementaciones
- `06 - Assets y Scripts/scr_input_buffer.gml` — scr_input_buffer — Input buffering y coyote time para juegos de plataformas
- `06 - Assets y Scripts/scr_math_util.gml` — scr_math_util — Utilidades matemáticas y funciones de easing para GameMaker LTS 2026
- `06 - Assets y Scripts/scr_pool.gml` — scr_pool — Object pooling: reutiliza instancias en vez de crearlas y destruirlas
- `06 - Assets y Scripts/scr_save_load.gml` — scr_save_load — Guardado y carga de partidas con structs + JSON, escritura segura
- `06 - Assets y Scripts/scr_state_machine.gml` — scr_state_machine — Máquina de estados finitos (FSM) implementada con structs, SIN objetos
- `06 - Assets y Scripts/scr_tiempo.gml` — scr_tiempo — Tres piezas de tiempo que se reescriben en cada receta: un `Cooldown`
- `06 - Assets y Scripts/scr_tween.gml` — scr_tween — Sistema de tweens (interpolaciones animadas) con structs, dirigido
- `06 - Assets y Scripts/scr_ui_confirmar.gml` — scr_ui_confirmar — Diálogo de confirmación genérico (Sí/No), con «No» siempre por defecto


## `07 - Ecosistema` — El ecosistema alrededor del motor

GitHub de YoYoGames, librerías, extensiones, proyectos de ejemplo, foro, itch.io, comunidades, blogs, GM CLI, estado de la IA.

**Usar cuando:** qué existe ya para X · dónde pregunto · cómo uso gm-cli · buscar un tutorial escrito por la comunidad sobre un sistema concreto

- `07 - Ecosistema/01 - GitHub - organización YoYoGames.md` — 01 · GitHub — Organización YoYoGames
- `07 - Ecosistema/02 - Librerías esenciales de la comunidad.md` — 02 · Librerías esenciales de la comunidad
- `07 - Ecosistema/03 - Extensiones oficiales y de terceros.md` — 03 · Extensiones oficiales y de terceros
- `07 - Ecosistema/04 - Proyectos de ejemplo para estudiar.md` — 04 · Proyectos de ejemplo para estudiar
- `07 - Ecosistema/05 - Scripts y utilidades GML.md` — 05 · Scripts y utilidades GML
- `07 - Ecosistema/06 - Plantillas y starters.md` — 06 · Plantillas y starters
- `07 - Ecosistema/07 - Foro oficial - hilos clave.md` — Foro oficial de GameMaker — estructura e hilos clave
- `07 - Ecosistema/08 - itch.io - jams, assets y juegos.md` — itch.io — jams, assets y juegos hechos con GameMaker
- `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` — Asset packs y recursos gráficos, de audio y de niveles
- `07 - Ecosistema/10 - Comunidades y dónde preguntar.md` — Comunidades y dónde preguntar
- `07 - Ecosistema/11 - Blogs, newsletters y podcasts.md` — Blogs, newsletters y fuentes de información continua
- `07 - Ecosistema/12 - Aprendizaje estructurado - cursos de pago y libros.md` — Aprendizaje estructurado — cursos de pago y libros
- `07 - Ecosistema/13 - GM CLI - la línea de comandos.md` — 13 · GM CLI — la línea de comandos de GameMaker
- `07 - Ecosistema/14 - IA y GameMaker.md` — 14 · IA y GameMaker (estado real en agosto de 2026)
- `07 - Ecosistema/15 - Qué hacen de verdad los proyectos reales.md` — 15 · Qué hacen de verdad los proyectos reales
- `07 - Ecosistema/16 - Catálogo de la sección Tutorials del foro.md` — 16 · Catálogo de la sección Tutorials del foro oficial
- `07 - Ecosistema/17 - SnowState - máquinas de estado (guía en español).md` — 17 · SnowState — máquinas de estado (guía en español)
- `07 - Ecosistema/18 - Scribble - texto rico (guía en español).md` — 18 · Scribble — texto rico y con efectos (guía en español)
- `07 - Ecosistema/19 - Chatterbox - diálogos Yarn (guía en español).md` — 19 · Chatterbox — diálogos ramificados con Yarn (guía en español)
- `07 - Ecosistema/20 - SNAP - datos y formatos (guía en español).md` — 20 · SNAP — convertir datos entre formatos (guía en español)
- `07 - Ecosistema/21 - Vinyl - audio avanzado (guía en español).md` — 21 · Vinyl — audio avanzado (guía en español)
- `07 - Ecosistema/22 - Crear una extensión nativa (guía en español).md` — 22 · Crear una extensión nativa (guía en español)
- `07 - Ecosistema/23 - Arte generado por IA (pixel art y assets 2D).md` — 23 · Arte generado por IA (pixel art y assets 2D)
- `07 - Ecosistema/24 - Logotipo, icono del ejecutable y capsule de tienda.md` — 24 · Logotipo, icono del ejecutable y capsule de tienda
- `07 - Ecosistema/_INDICE-ECOSISTEMA.md` — Índice del ecosistema GameMaker


## `08 - Referencia GML completa` — Referencia técnica de GML en español + la API completa

19 documentos temáticos en español (dibujo, shaders, buffers, DS, strings, matemáticas...) MÁS el catálogo completo de la API extraído del GmlSpec.xml del runtime instalado.

**Usar cuando:** la referencia técnica de un área completa · listar todas las funciones de una familia · comprobar si algo existe · una función no está en el manual: ¿existe o me la estoy inventando? · qué funciones del runtime están obsoletas o sin documentar

- `08 - Referencia GML completa/01 - Dibujo básico y sprites.md` — 01 — Dibujo básico y sprites
- `08 - Referencia GML completa/02 - Dibujo de formas y primitivas.md` — 02 — Dibujo de formas y primitivas
- `08 - Referencia GML completa/03 - Texto y fuentes.md` — 03 — Texto y fuentes
- `08 - Referencia GML completa/04 - Color y blending.md` — 04 — Color y blending
- `08 - Referencia GML completa/05 - Superficies.md` — 05 — Superficies
- `08 - Referencia GML completa/06 - Shaders.md` — 06 — Shaders
- `08 - Referencia GML completa/07 - Vertex buffers y formatos.md` — 07 — Vertex buffers y formatos
- `08 - Referencia GML completa/08 - Texturas y grupos de texturas.md` — 08 — Texturas y grupos de texturas
- `08 - Referencia GML completa/09 - Dibujo de tiles y tilemaps.md` — 09 — Dibujo de tiles y tilemaps
- `08 - Referencia GML completa/10 - Matemáticas.md` — 10 · Matemáticas y números en GML
- `08 - Referencia GML completa/11 - Vectores, matrices y ángulos.md` — 11 · Vectores, matrices y ángulos en GML
- `08 - Referencia GML completa/12 - Strings.md` — 12 · Strings en GML
- `08 - Referencia GML completa/13 - Estructuras de datos (DS).md` — 13 · Estructuras de datos (DS) en GML
- `08 - Referencia GML completa/14 - Arrays.md` — 14 · Arrays en GML
- `08 - Referencia GML completa/15 - Structs - funciones.md` — 15 · Structs y funciones de variables en GML
- `08 - Referencia GML completa/16 - Buffers.md` — 16 · Buffers en GML
- `08 - Referencia GML completa/17 - Ficheros y directorios.md` — 17 · Ficheros y directorios en GML
- `08 - Referencia GML completa/18 - Fecha y hora.md` — 18 · Fecha y hora en GML
- `08 - Referencia GML completa/19 - Sistema, compilador y entorno.md` — 19 · Sistema, compilador y entorno en GML
- `08 - Referencia GML completa/20 - Lo que el manual no documenta.md` — 20 · Lo que existe en el runtime y el manual no documenta
- `08 - Referencia GML completa/21 - Constantes que el manual abrevia.md` — 21 · Constantes que el manual abrevia
- `08 - Referencia GML completa/22 - Animación esqueletal (Spine).md` — 22 · Animación esqueletal (Spine)
- `08 - Referencia GML completa/23 - Recetario de shaders de efecto.md` — 23 — Recetario de shaders de efecto
- `08 - Referencia GML completa/24 - Audio avanzado - buffers, colas, sincronía y grabación.md` — 24 · Audio avanzado — buffers, colas, sincronía y grabación
- `08 - Referencia GML completa/_API del runtime/API-constantes.md` — Referencia de la API de GML — constantes y enumeraciones
- `08 - Referencia GML completa/_API del runtime/API-funciones.md` — Referencia de la API de GML — funciones
- `08 - Referencia GML completa/_API del runtime/API-variables.md` — Referencia de la API de GML — variables y structs incorporados


## `09 - Manual oficial` — El manual oficial espejado (offline)

3119 páginas en inglés y 3033 en español, en Markdown, con la estructura idéntica al manual web. Es la FUENTE DE VERDAD.

**Usar cuando:** necesito la página oficial completa de una función · hay una contradicción entre fuentes

- `09 - Manual oficial/README.md` — 09 · Manual oficial de GameMaker (espejo offline)
- `09 - Manual oficial/manual-lts-2026-en/` — (3120 archivos)
- `09 - Manual oficial/manual-lts-2026-es/` — (3034 archivos)


## `10 - Cursos en español` — Todo el material de aprendizaje en castellano

Investigación verificada de qué existe en español, con veredicto honesto, ruta de aprendizaje, y la TRANSCRIPCIÓN ESTRUCTURADA de los dos mejores vídeos.

**Usar cuando:** aprender sin pasar por el inglés · consultar el curso de GML sin ver el vídeo

- `10 - Cursos en español/01 - Academia de Hektor Profe.md` — 01 · Academia de GameMaker — Hektor Profe (Escuela de Videojuegos)
- `10 - Cursos en español/02 - Altair AML - GameMaker 2024.md` — 02 · Altair_AML — GameMaker 2024 en español
- `10 - Cursos en español/03 - Otros canales y series.md` — 03 · Otros canales y series de GameMaker en español
- `10 - Cursos en español/04 - Recursos escritos en español.md` — 04 · Recursos escritos de GameMaker en español
- `10 - Cursos en español/05 - Ruta de aprendizaje en español.md` — 05 · Ruta de aprendizaje 100 % en español
- `10 - Cursos en español/06 - Curso de GML en vídeo - transcripción estructurada.md` — 06 · Curso de GML en vídeo (español) — transcripción estructurada
- `10 - Cursos en español/07 - Curso de eventos en vídeo - transcripción estructurada.md` — 07 · Los eventos de GameMaker, en vídeo y en español — transcripción estructurada
- `10 - Cursos en español/08 - Plataformas estilo Megaman X - apuntes de la serie de Altair.md` — 08 · Plataformas estilo Megaman X — apuntes técnicos
- `10 - Cursos en español/09 - Plataformas para principiantes - apuntes de Alas de reptil 2025.md` — 09 · Plataformas para principiantes — apuntes de la serie de Alas de reptil (2025)
- `10 - Cursos en español/10 - Herramientas de la comunidad - Input y Scribble.md` — 10 · Herramientas de la comunidad: Input y Scribble
- `10 - Cursos en español/11 - El IDE de GameMaker en español - recorrido guiado.md` — 11 · El IDE de GameMaker en español — recorrido guiado
- `10 - Cursos en español/12 - Primer contacto - decisiones al empezar (2025-2026).md` — 12 · Primer contacto: las decisiones al empezar (apuntes 2025-2026)
- `10 - Cursos en español/_INDICE-CURSOS-ES.md` — 10 · Cursos y materiales de GameMaker en español


## `11 - Código descargado` — 314 repositorios con código GML real

53569 archivos .gml de librerías, extensiones oficiales, juegos completos y plantillas. Organizado en 28 temas y catalogado en español.

**Usar cuando:** cómo resuelve esto la gente de verdad · existe ya una librería para X · ver la estructura de un juego grande

**No usar para:** copiar código de los juegos comerciales extraídos (no son libres)

- `11 - Código descargado/_CATALOGO.md` — Catálogo del código descargado
- `11 - Código descargado/extensiones_oficiales/` — (4998 archivos)
- `11 - Código descargado/herramientas/` — (247 archivos)
- `11 - Código descargado/juegos_y_motores/` — (37035 archivos)
- `11 - Código descargado/librerias/` — (25423 archivos)
- `11 - Código descargado/plantillas_y_ejemplos/` — (2257 archivos)


## `12 - Utilidades e integraciones` — Lo que rodea al motor

Herramientas de flujo de trabajo, extensiones nativas, integraciones con servicios, multijugador, pipeline de arte y audio, itch.io y dónde buscar.

**Usar cuando:** qué herramienta uso para X · cómo integro Steam/Discord/Photon/Colyseus · pipeline de Aseprite o Tiled · dónde busco algo

- `12 - Utilidades e integraciones/01 - Herramientas del flujo de trabajo.md` — 01 · Herramientas del flujo de trabajo
- `12 - Utilidades e integraciones/02 - Extensiones nativas y del sistema.md` — 02 · Extensiones nativas y del sistema
- `12 - Utilidades e integraciones/03 - Integraciones con servicios.md` — 03 · Integraciones con servicios y plataformas
- `12 - Utilidades e integraciones/04 - Multijugador y red.md` — 04 · Multijugador y red
- `12 - Utilidades e integraciones/05 - Pipeline de arte, audio y niveles.md` — 05 · Pipeline de arte, audio y niveles
- `12 - Utilidades e integraciones/06 - itch.io - assets, herramientas y jams.md` — 06 · itch.io — assets, herramientas y jams para GameMaker
- `12 - Utilidades e integraciones/07 - Dónde buscar - hubs y documentación.md` — 07 · Dónde buscar: hubs, foros y documentación
- `12 - Utilidades e integraciones/08 - Tooling externo - CLI, parsers e ingeniería inversa.md` — 08 · Tooling externo: CLI, parsers, TypeScript e ingeniería inversa
- `12 - Utilidades e integraciones/09 - Manual del agente de IA - operar GameMaker con gm-cli.md` — 09 · Manual del agente de IA — operar GameMaker con `gm-cli`
- `12 - Utilidades e integraciones/_INDICE-UTILIDADES.md` — 12 · Utilidades e integraciones para GameMaker


## `13 - Diseño y producción de videojuegos` — Diseño y producción de videojuegos

El oficio que va antes y alrededor del código, en 24 documentos: diseño de juego, niveles, pixel art, animación, UI/UX, arquitectura, generación procedural, físicas y fluidos, sonido, testing, producción, narrativa, matemáticas, el documento de diseño (GDD), teoría del diseño, progresión, puzzles, combate y jefes, cámaras, negocio y ética, balance por simulación, mundo y exploración, patrones en GML, y voz y localización de audio.

**Usar cuando:** me piden diseñar o planificar un juego, no solo programarlo · cómo se diseña un nivel / se equilibra una mecánica / se escribe un diálogo · qué resolución y paleta uso para pixel art · cómo estructuro el proyecto para que crezca · ruido, autómatas celulares, WFC, Poisson · muelles, Verlet, agua, fluidos sin Box2D · cómo pruebo el juego y cómo lo lanzo · qué matemáticas necesito para X · escribir el GDD o un documento que un agente pueda implementar · el canon teórico del diseño · árboles de habilidades y meta-progresión · diseñar puzzles y validarlos por búsqueda · decidir el combate y los jefes · qué cámara pide mi juego · cómo se paga el juego y con qué ética · comprobar el balance sin gastar playtests · diseñar el mundo y la exploración · traducir un patrón conocido a GML · grabar y localizar voces

**No usar para:** la firma de una función (usa _indice/buscar.py) · la receta completa de un género (usa 04 - Recetas por género) · la API de un sistema del motor (usa 01 - Fundamentos y 08 - Referencia GML completa)

- `13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md` — 01 · Diseño de juego — core loop, mecánicas, balance y dificultad
- `13 - Diseño y producción de videojuegos/02 - Diseño de niveles.md` — 02 · Diseño de niveles
- `13 - Diseño y producción de videojuegos/03 - Pixel art y resolución.md` — 03 · Pixel art y resolución
- `13 - Diseño y producción de videojuegos/04 - Animación de sprites, Sequences y Animation Curves.md` — 04 · Animación de sprites, Sequences y Animation Curves
- `13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md` — 05 · UI y UX de juego
- `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md` — 06 · Arquitectura de un proyecto GameMaker
- `13 - Diseño y producción de videojuegos/07 - Generación procedural avanzada.md` — 07 · Generación procedural avanzada
- `13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md` — 08 · Físicas a mano y fluidos
- `13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md` — 09 · Diseño de sonido y mezcla
- `13 - Diseño y producción de videojuegos/10 - Testing y QA.md` — 10 · Testing y QA
- `13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md` — 11 · Producción, alcance y lanzamiento
- `13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md` — 12 · Diseño narrativo y diálogos
- `13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md` — 13 · Matemáticas aplicadas al juego
- `13 - Diseño y producción de videojuegos/14 - El documento de diseño - del one-pager al GDD completo.md` — 14 · El documento de diseño — del one-pager al GDD completo
- `13 - Diseño y producción de videojuegos/15 - Teoría del diseño - el canon en una tarde.md` — 15 · Teoría del diseño — el canon en una tarde
- `13 - Diseño y producción de videojuegos/16 - Progresión - árboles de habilidades, desbloqueos y meta-progresión.md` — 16 · Progresión: árboles de habilidades, desbloqueos y meta-progresión
- `13 - Diseño y producción de videojuegos/17 - Diseño de puzzles.md` — 17 · Diseño de puzzles
- `13 - Diseño y producción de videojuegos/18 - Diseño de combate y de jefes.md` — 18 · Diseño de combate y de jefes
- `13 - Diseño y producción de videojuegos/19 - Cámaras de juego - encuadre, seguimiento y control.md` — 19 · Cámaras de juego — encuadre, seguimiento y control
- `13 - Diseño y producción de videojuegos/20 - Modelo de negocio, monetización y ética del diseño.md` — 20 · Modelo de negocio, monetización y ética del diseño
- `13 - Diseño y producción de videojuegos/21 - Balance por simulación - Monte Carlo, Machinations y estrategias dominantes.md` — 21 · Balance por simulación: Monte Carlo, Machinations y estrategias dominantes
- `13 - Diseño y producción de videojuegos/22 - Diseño de mundo y exploración.md` — 22 · Diseño de mundo y exploración
- `13 - Diseño y producción de videojuegos/23 - Catálogo de patrones en GML.md` — 23 · Catálogo de patrones en GML
- `13 - Diseño y producción de videojuegos/24 - Voz, diálogo y localización de audio.md` — 24 · Voz, diálogo y localización de audio
- `13 - Diseño y producción de videojuegos/25 - Legal de terceros - marcas, fan games y parodia.md` — 25 · Legal de terceros: marcas, fan games y parodia
- `13 - Diseño y producción de videojuegos/26 - Comunidad propia - Discord, moderación y gestión de crisis.md` — 26 · Comunidad propia: Discord, moderación y gestión de crisis
- `13 - Diseño y producción de videojuegos/27 - Formatos de producción especiales.md` — 27 · Formatos de producción especiales
- `13 - Diseño y producción de videojuegos/28 - De hazme un juego a una especificación - el protocolo de elicitación del agente.md` — 28 · De «hazme un juego» a una especificación — el protocolo de elicitación del agente
- `13 - Diseño y producción de videojuegos/_INDICE-DISENO.md` — Diseño y producción de videojuegos — índice
