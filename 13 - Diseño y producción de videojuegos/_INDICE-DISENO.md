# Diseño y producción de videojuegos — índice

> **El oficio que va antes y alrededor del código.** 24 documentos. Las otras carpetas explican el motor;
> esta explica cómo se diseña, se estructura, se prueba y se lanza un juego, y cómo cada
> decisión se traduce a GameMaker LTS 2026 con GML verificado contra el runtime
> `2026.0.0.23`. Cada documento va del principio (por qué) al método (cómo) y al código
> (en GameMaker), y termina con un checklist y los errores clásicos.
>
> Ninguno repite lo que ya está en otra carpeta: cuando un tema vive en `01`, `04` u `08`,
> el documento lo enlaza y dedica el espacio a lo que faltaba.

---

## Tabla de documentos

| # | Documento | Qué resuelve | Léelo cuando… |
|---|---|---|---|
| [01](<./01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md>) | **Diseño de juego** | MDA, core loop y bucles anidados, mecánicas frente a sistemas, curva de dificultad y flow, economía y balance por fórmulas, onboarding sin texto, prototipado, playtesting, GDD de una página; balance modificable en caliente con `dbg_*` y telemetría a JSON | tienes una idea y no sabes qué programar primero, o el juego «no divierte» y no sabes por qué |
| [02](<./02 - Diseño de niveles.md>) | **Diseño de niveles** | Kishōtenketsu, pacing, legibilidad y landmarks, gating, riesgo/recompensa, checkpoints; métricas del jugador, caja gris → arte, Room Editor, tiles y autotiles, triggers, niveles como datos (JSON), editor in-game, hoja de nivel | vas a construir salas y quieres que enseñen, tensen y descansen a propósito |
| [03](<./03 - Pixel art y resolución.md>) | **Pixel art y resolución** | Resolución base y escalado entero, paletas, clusters, dithering, animación en pixel art, Aseprite → GameMaker, y los ajustes del motor que emborronan un sprite (interpolación, texture pages, cámara a píxel entero) | eliges resolución, dibujas sprites o «todo se ve borroso» |
| [04](<./04 - Animación de sprites, Sequences y Animation Curves.md>) | **Animación** | Los 12 principios traducidos a sprites, `image_index`/`image_speed`, frame data (hit frames), animación procedural, **Animation Curves** y **Sequences** por código, timing en dobles | animas un personaje, montas una cinemática o una UI animada |
| [05](<./05 - UI y UX de juego.md>) | **UI y UX de juego** | Jerarquía, legibilidad (26 px a 1080p en consola), taxonomía diegética, mapa de pantallas, navegación con mando, anclas y zonas seguras, nine-slice, componentes (botón, barra de vida, tooltip, inventario, minimapa, toasts), Draw GUI frente a UI Layers | haces HUD, menús u opciones y quieres que se usen bien con cualquier dispositivo |
| [06](<./06 - Arquitectura de un proyecto GameMaker.md>) | **Arquitectura del proyecto** | Asset Browser por dominio, gestores y Service Locator ligero, arranque, lógica/dibujo/datos, composición frente a herencia, patrón comando, datos dirigidos, tiempo y paso fijo, guardado versionado, Configs y macros, Git (`.gmcache/` no está en el `.gitignore` que genera `gm-cli`), anti-patrones | el proyecto va a crecer más allá de un prototipo |
| [07](<./07 - Generación procedural avanzada.md>) | **Generación procedural avanzada** | Ruido (value, Perlin, fBm, warping: GameMaker no trae ninguno), autómatas celulares, Poisson-disc, Wave Function Collapse, L-systems y Markov, ensamblaje por piezas, niveles por ritmo, terreno destructible, validación y depuración | el roguelike de `04 · 05` se te queda corto |
| [08](<./08 - Físicas a mano y fluidos.md>) | **Físicas a mano y fluidos** | Integrador semi-implícito y paso fijo, salto derivado de altura y tiempo, colisiones propias, **particionado espacial**, muelles, Verlet (cuerdas, tela, cuerpos blandos), flotabilidad, agua con muelles, líquido por celdas, metaballs, viento | quieres sensaciones afinables sin Box2D, o agua de verdad |
| [09](<./09 - Diseño de sonido y mezcla.md>) | **Diseño de sonido y mezcla** | Categorías y presupuesto de sonido, capas de un SFX y variaciones, mezcla por buses (solo procesan emisores), ducking y compresor, sonido posicional, ambiente, formatos, LUFS de referencia, hoja de sonido | tu juego suena «a tutorial» o la música tapa los efectos |
| [10](<./10 - Testing y QA.md>) | **Testing y QA** | Pirámide adaptada, GML testeable, mini-framework de pruebas que compila y corre con `gm-cli run --config`, GM-TestFramework y crispy, regresión y golden files, rendimiento, modo QA, plan de pruebas manual, informes de bug | antes de publicar, o cuando un bug vuelve por tercera vez |
| [11](<./11 - Producción, alcance y lanzamiento.md>) | **Producción, alcance y lanzamiento** | Alcance y vertical slice, fases con criterios de salida, kanban de una persona, versiones y builds, assets y licencias, página de Steam y wishlists, press kit, post-lanzamiento y postmortem, legal mínimo, plantillas | empiezas un juego que quieres terminar de verdad |
| [12](<./12 - Diseño narrativo y diálogos.md>) | **Diseño narrativo y diálogos** | Narrativa embebida y emergente, estructura, contar sin cinemáticas, escribir diálogo, ramificación y flags, Yarn/Chatterbox, Ink (solo escritorio), Twine, gestor de misiones, cinemáticas saltables, fichas y biblia de una página | el juego tiene historia, personajes o elecciones |
| [13](<./13 - Matemáticas aplicadas al juego.md>) | **Matemáticas aplicadas** | Por problema: vectores, ángulos, lerp independiente del framerate, easings y Bézier, probabilidad justa (bolsa, piedad), geometría de colisión, rejillas isométricas y hexagonales, curvas de crecimiento, trigonometría, matrices 2D, precisión y tiempo | «¿está detrás de mí?», «¿por qué el suavizado va distinto a 144 fps?», «¿cuánta XP en el nivel 10?» |
| [14](<./14 - El documento de diseño - del one-pager al GDD completo.md>) | **El documento de diseño** | Cuándo el one-pager no basta, plantilla completa por secciones (qué va y qué NO va en cada una), pilares, elevator pitch, wiki viva, catálogo de diagramas, y **la versión para LLM** con un ejemplo real | tienes que escribir el GDD, o que otro (o un agente) lo pueda implementar |
| [15](<./15 - Teoría del diseño - el canon en una tarde.md>) | **Teoría del diseño** | Koster, Salen & Zimmerman, las lentes de Schell, autodeterminación, Bartle y Quantic Foundry, Costikyan sobre incertidumbre, emergencia frente a progresión, dominancia estratégica, Fullerton — cada uno con «qué te hace hacer distinto mañana» | el juego no engancha y no sabes por qué; quieres vocabulario para pensarlo |
| [16](<./16 - Progresión - árboles de habilidades, desbloqueos y meta-progresión.md>) | **Progresión** | Topologías de árbol, prerrequisitos y respec, el grafo como datos con validación de ciclos y alcanzabilidad, UI navegable con mando, desbloqueos, meta-progresión de roguelite y monedas múltiples | hay que decidir cómo crece el jugador |
| [17](<./17 - Diseño de puzzles.md>) | **Diseño de puzzles** | Taxonomía, el momento «ajá» y qué lo mata, enseñar la regla sin enunciarla, medir la dificultad, pistas graduadas; y la ingeniería: validar por búsqueda (BFS/A* con Sokoban completo), generar con validación, deshacer | el juego tiene puzzles de verdad, no solo match-3 |
| [18](<./18 - Diseño de combate y de jefes.md>) | **Diseño de combate y de jefes** | El oficio, no el código: qué hace legible un combate, el kit del jugador, el vocabulario del *tell* con su duración mínima en fotogramas, enemigos como preguntas, jefes por fases, dificultad y balance | decides el combate; `04/30`–`04/36` lo implementan |
| [19](<./19 - Cámaras de juego - encuadre, seguimiento y control.md>) | **Cámaras de juego** | El marco de Itay Keren traducido a GML (camera window, snapping, atracción, zonas, cue y projection focus), transición pantalla-a-pantalla, cámara multijugador con zoom, cinemáticas, y qué cámara pide cada género | la cámara marea, va a tirones o no enseña lo que debe |
| [20](<./20 - Modelo de negocio, monetización y ética del diseño.md>) | **Negocio, monetización y ética** | Elegir modelo y su efecto en el diseño, qué se vende y qué no, economía dual, catálogo de patrones oscuros con su alternativa honesta, cajas de botín y su situación legal, juego responsable, retención y KPIs | hay que decidir cómo se paga el juego, sin vender el alma |
| [21](<./21 - Balance por simulación - Monte Carlo, Machinations y estrategias dominantes.md>) | **Balance por simulación** | La notación de Machinations, 10 000 combates en GML sobre el framework de pruebas, percentiles en vez de medias, y cazar dominancia y varianza sin gastar playtests | las fórmulas de `01` §4 dicen que está equilibrado y no te fías |
| [22](<./22 - Diseño de mundo y exploración.md>) | **Diseño de mundo y exploración** | Densidad y distribución de puntos de interés, el bucle curiosidad → navegación → recompensa, mapa y brújula como decisión, viaje rápido, el grafo de bloqueos validado con BFS, señalización a distancia | el juego tiene mundo, no solo niveles |
| [23](<./23 - Catálogo de patrones en GML.md>) | **Catálogo de patrones en GML** | Los patrones de Nystrom que faltaban, traducidos y medidos: Flyweight, Prototype, Subclass Sandbox, Data Locality (con benchmark real), Dirty Flag, Event Queue, Bytecode, y el veredicto sobre ECS | el proyecto pide una solución conocida y quieres la versión GML |
| [24](<./24 - Voz, diálogo y localización de audio.md>) | **Voz y localización de audio** | Proceso de grabación, convención de nombres que encaja con la clave de localización, audio groups por idioma, subtítulos de efectos con dirección, lip-sync básico, voces procedurales, QA de voz | el juego tiene voces, o subtítulos que van más allá del diálogo |

## Recetas hermanas en `04 - Recetas por género`

Cuatro recetas nacieron en la misma revisión y completan lo transversal:

- [28 · Juegos para móvil (táctil)](<../04 - Recetas por género/28 - Juegos para móvil (táctil).md>) — orientación, escalado y zonas seguras, joystick virtual, rendimiento y batería, sandbox, sensores, pruebas en dispositivo.
- [29 · 3D en GameMaker](<../04 - Recetas por género/29 - 3D en GameMaker.md>) — cámara y matrices, vertex buffers, OBJ, iluminación, billboards, colisiones 3D, rendimiento.
- [30 · Combate cuerpo a cuerpo](<../04 - Recetas por género/30 - Combate cuerpo a cuerpo - hitboxes, hurtboxes y combos.md>) — hitbox ≠ hurtbox ≠ máscara, frame data, cola de golpes, combos, i-frames, parry.
- [31 · IA de decisión](<../04 - Recetas por género/31 - IA de decisión - árboles de comportamiento, utility y GOAP.md>) — FSM → árbol de comportamiento → utility → GOAP, blackboard, percepción, tick escalonado.

## Orden sugerido para un juego nuevo

```
11 Producción (alcance)  →  01 Diseño de juego (core loop, GDD)  →  06 Arquitectura
      →  02 Niveles · 03 Pixel art · 04 Animación · 05 UI · 09 Sonido · 12 Narrativa (según el juego)
      →  07 Procedural · 08 Físicas · 13 Matemáticas (cuando el sistema lo pida)
      →  10 Testing y QA  →  11 Producción (lanzamiento)
```

El plano de escenas de un juego completo sigue siendo
[04 · 00 — Anatomía de un juego completo](<../04 - Recetas por género/00 - Anatomía de un juego completo.md>);
esta carpeta le pone el oficio alrededor.

## Cómo se verificó cada documento

- Todo símbolo de GML pasó por `python3 "_indice/buscar.py"` antes de escribirse; el paso 9 de
  `actualizar.py` (`validar-codigo-gml.py`) vigila que siga siendo así.
- Varios redactores extrajeron el código a un proyecto de prueba y lo compilaron con `gm-cli`
  contra el runtime `2026.0.0.23` (documentos 07, 08, 10, 11 y 13 lo declaran en sus notas).
- Las fuentes son primarias y llevan fecha de consulta; lo que no se pudo verificar está
  marcado con ⚠️ en el propio texto.
- Lo que un redactor **quiso escribir y no existe** (`smoothstep`, `array_fill`, `assert`,
  `display_set_orientation`, `texture_set_interpolation`, `dbg_graph`, `buffer_write_to_surface`…)
  quedó anotado en cada documento: es la lista de alucinaciones que estos textos evitan.
