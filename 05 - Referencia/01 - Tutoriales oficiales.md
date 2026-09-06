# 01 · Tutoriales oficiales de GameMaker

> ✅ **Reverificado el 2 de septiembre de 2026** abriendo la web con navegador (la página se
> renderiza con JavaScript, así que `curl` no sirve):
>
> | Comprobación | Resultado |
> |---|---|
> | Contador oficial de la web | **(106)** — el catálogo de abajo **sigue completo y vigente** |
> | ¿Existe `gamemaker.io/es/tutorials`? | **Sí** |
> | ¿Están los tutoriales traducidos al español? | **No.** Solo se traduce la interfaz (botones, niveles). **Los títulos y el contenido siguen en inglés** |
>
> ⚠️ **Ojo con la versión `/es/`:** puede llevar a pensar que hay tutoriales oficiales en
> castellano. No los hay: el catálogo es el mismo, en inglés. Para material en español ve a
> [10 · Cursos en español](../10%20-%20Cursos%20en%20español/_INDICE-CURSOS-ES.md).

> **Catálogo completo verificado el 31 de agosto de 2026.**
> Se han recorrido las 9 páginas del listado oficial <https://gamemaker.io/en/tutorials> y se han
> extraído **106 tutoriales** con su título, nivel y sabor (GML Code / GML Visual).
> El número coincide con el contador «Filter Tutorials (106)» que muestra la propia web.

---

## 0. Índice rápido

1. [Cómo leer este catálogo](#2-cómo-leer-este-catálogo)
2. [Orden recomendado de aprendizaje](#3-orden-recomendado-de-aprendizaje)
3. [Los 106 tutoriales, uno a uno](#4-los-106-tutoriales-oficiales)
4. [Quick Start Guides del manual](#5-quick-start-guides-del-manual)
5. [Fuentes](#6-fuentes)

---

## 1. Resumen

| Métrica | Valor |
|---|---|
| Tutoriales publicados | **106** |
| Niveles | Principiante (inmensa mayoría), Intermedio, Avanzado |
| Sabores | `GML Code`, `GML Visual` (el antiguo Drag & Drop), o ambos |
| Plataforma | Web, en <https://gamemaker.io/tutorials> |
| Precio | Gratuitos |
| Vídeos | Canal oficial de YouTube: <https://www.youtube.com/@GameMakerEngine> |

### Sobre la duración estimada

**La web oficial no publica la duración de cada tutorial.** Los únicos datos de tiempo que existen
son referencias sueltas: la portada de gamemaker.io anuncia «Make it in 15 minutes» y la ficha de
la plantilla Space Rocks dice que es un arcade shooter «that only takes 15 minutes to make».

Por tanto, en la columna **Duración** de las rutas de la sección 3 encontrarás **estimaciones
propias** (marcadas como tales), calculadas por extensión y por tipo de contenido. No son datos
oficiales de YoYo Games.

Leyenda usada en las estimaciones:

| Símbolo | Significado |
|---|---|
| ⏱ | Estimación propia: menos de 30 minutos |
| ⏱⏱ | Estimación propia: entre 30 y 90 minutos |
| ⏱⏱⏱ | Estimación propia: varias horas o un proyecto completo por entregas |

---

## 2. Cómo leer este catálogo

- **Nivel**: `Principiante` / `Intermedio` / `Avanzado`, tal y como etiqueta la web.
- **Sabor**: `GML Code` (código), `GML Visual` (nodos visuales), `GML Code + Visual` (existen
  ambas versiones) o `—` (no aplica: es contenido del IDE o de plataforma).
- Los títulos se han dejado **en inglés** tal y como los publica GameMaker, para que puedas
  buscarlos sin traducir.

---

## 3. Orden recomendado de aprendizaje

### Ruta A — «Nunca he tocado GameMaker» (la recomendada)

| Paso | Tutorial | Nivel | Duración |
|---|---|---|---|
| 1 | [How to Get Started with GameMaker in 2026](https://gamemaker.io/tutorials/get-started-gamemaker-2026) | Principiante | ⏱ |
| 2 | [How To Move And Collide In GameMaker](https://gamemaker.io/tutorials/easy-move-collide) | Principiante | ⏱⏱ |
| 3 | [How To Make Platformer Movement In GameMaker](https://gamemaker.io/tutorials/easy-platformer) | Principiante | ⏱⏱ |
| 4 | [Make Your Own Arcade Space Shooter](https://gamemaker.io/tutorials/make-arcade-space-shooter) | Principiante | ⏱⏱ |
| 5 | [Make Your First Platformer in GameMaker](https://gamemaker.io/tutorials/your-first-platformer) | Principiante | ⏱⏱⏱ |
| 6 | [Make Your Own Role-Playing Game](https://gamemaker.io/tutorials/how-to-make-an-rpg) | Principiante | ⏱⏱⏱ |
| 7 | [How To Optimise Your Games](https://gamemaker.io/tutorials/how-to-optimise-your-games) | Principiante | ⏱⏱ |
| 8 | [How To Fix Runtime Errors in GameMaker](https://gamemaker.io/tutorials/fix-runtime-errors) | Intermedio | ⏱⏱ |
| 9 | [Quickstart On Exporting And Sharing Your Game](https://gamemaker.io/tutorials/quickstart-on-exporting-and-sharing-your-game) | — | ⏱ |

> **Por qué este orden.** El paso 1 es el tutorial de 2026 (mantiene la interfaz actual del IDE).
> Los pasos 2 y 3 te dan los dos movimientos que vas a usar siempre. El 4 es el juego completo más
> corto (Space Rocks / Arcade Space Shooter), el que antes te deja «un juego acabado» en las manos.
> El 5 y el 6 ya son proyectos largos. El 7 y el 8 son higiene: uno optimiza y el otro te enseña a
> leer errores, que es lo que más tiempo ahorra a la larga. El 9 cierra el ciclo publicando.

### Ruta B — «Vengo de Unity u otro motor»

| Paso | Tutorial |
|---|---|
| 1 | [A Unity User's Guide To GameMaker](https://gamemaker.io/tutorials/moving-from-unity-to-gamemaker) |
| 2 | [The Workspace](https://gamemaker.io/tutorials/workspaces) |
| 3 | [The Object Editor - IDE Basics](https://gamemaker.io/tutorials/object-editor) |
| 4 | [The Room Editor - IDE Basics](https://gamemaker.io/tutorials/room-editor) |
| 5 | [How To Move And Collide In GameMaker](https://gamemaker.io/tutorials/easy-move-collide) |
| 6 | [Ultimate Guide To Collision Functions](https://gamemaker.io/tutorials/collision-functions) |

### Ruta C — «Quiero dominar el IDE antes de programar»

| Paso | Tutorial |
|---|---|
| 1 | [The Workspace](https://gamemaker.io/tutorials/workspaces) |
| 2 | [The Sprite Editor - IDE Basics](https://gamemaker.io/tutorials/sprite-editor) |
| 3 | [The Image Editor - IDE Basics](https://gamemaker.io/tutorials/image-editor) |
| 4 | [The Object Editor - IDE Basics](https://gamemaker.io/tutorials/object-editor) |
| 5 | [The Room Editor - IDE Basics](https://gamemaker.io/tutorials/room-editor) |
| 6 | [The Tile Set Editor](https://gamemaker.io/tutorials/tile-set-editor) |
| 7 | [The Debugger](https://gamemaker.io/tutorials/debugger) |
| 8 | [Cameras And Views](https://gamemaker.io/tutorials/cameras-and-views) |

### Ruta D — «Aprendo con GML Visual (sin código)»

| Paso | Tutorial |
|---|---|
| 1 | [How To Move And Collide In GameMaker](https://gamemaker.io/tutorials/easy-move-collide) (versión Visual) |
| 2 | [Make Your Own Endless Platformer](https://gamemaker.io/tutorials/fire-jump-dnd-1) → serie **Fire Jump** ([índice](https://gamemaker.io/tutorials/fire-jump-dnd), [parte 2](https://gamemaker.io/tutorials/fire-jump-dnd-2), [3](https://gamemaker.io/tutorials/fire-jump-dnd-3), [4](https://gamemaker.io/tutorials/fire-jump-dnd-4)) |
| 3 | [Make Your Own Action-Adventure Game](https://gamemaker.io/tutorials/heros-trail-dnd-1) → serie **Hero's Trail** ([índice](https://gamemaker.io/tutorials/heros-trail-dnd), [breakdown](https://gamemaker.io/tutorials/heros-trail-breakdown), [parte 3](https://gamemaker.io/tutorials/heros-trail-dnd-3), [4](https://gamemaker.io/tutorials/heros-trail-dnd-4), [5](https://gamemaker.io/tutorials/heros-trail-dnd-5), [6](https://gamemaker.io/tutorials/heros-trail-dnd-6)) |
| 4 | [Space Rocks \| DnD](https://gamemaker.io/tutorials/space-rocks-dnd) |
| 5 | [Make Your First Car Game \| Josia Roncancio](https://gamemaker.io/tutorials/car-parking-game-tutorial) |

### Ruta E — «Publicar y distribuir»

| Paso | Tutorial |
|---|---|
| 1 | [Quickstart On Exporting And Sharing Your Game](https://gamemaker.io/tutorials/quickstart-on-exporting-and-sharing-your-game) |
| 2 | [Publish Your Game to GX.games In 5 Minutes](https://gamemaker.io/tutorials/publish-to-gxgames-tutorial) |
| 3 | [How to Publish a Mobile Game on GX.games](https://gamemaker.io/tutorials/publish-mobile-games-for-free) |
| 4 | [How to Get Noticed on GX.games](https://gamemaker.io/tutorials/gxgames-get-noticed) |
| 5 | [GX.games: How To Create Challenges For Your Games](https://gamemaker.io/tutorials/gxgames-challenges) |
| 6 | [Making In-Game Leaderboards For GX.games Challenges](https://gamemaker.io/tutorials/gxgames-in-game-leaderboards) |
| 7 | [Displaying Player Avatar In-Game on GX.games](https://gamemaker.io/tutorials/gxgames-in-game-avatars) |

### Ruta F — «Ya sé lo básico, quiero profundidad»

| Paso | Tutorial | Nivel |
|---|---|---|
| 1 | [Ultimate Guide To Collision Functions](https://gamemaker.io/tutorials/collision-functions) | Intermedio |
| 2 | [How To Use Advanced Array Functions in GameMaker](https://gamemaker.io/tutorials/advanced-array-functions) | Avanzado |
| 3 | [Buttery Smooth Tech: Inputs](https://gamemaker.io/tutorials/buttery-smooth-tech-inputs) | Intermedio |
| 4 | [Create a Platformer Game with GML](https://gamemaker.io/tutorials/create-a-platformer-game-with-gml) | Intermedio |
| 5 | [Physics In GameMaker Studio 2](https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-1) (partes [1](https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-1)–[4](https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-4)) | — |
| 6 | [How To Use Physics Raycast In GameMaker](https://gamemaker.io/tutorials/physics-raycast) | Intermedio |
| 7 | [GameMaker Testing Library](https://gamemaker.io/tutorials/gamemaker-testing-library-tutorial) | — |
| 8 | [Beginners Guide To Networking](https://gamemaker.io/tutorials/beginners-guide-to-networking) | Principiante |
| 9 | [How to Add Multiplayer to An Existing Game In GameMaker](https://gamemaker.io/tutorials/add-multiplayer-to-gamemaker) | Intermedio |

### Los Coffee-Break (píldoras sueltas, orden libre)

Serie de tutoriales cortos, casi siempre en **dos versiones** (GML y DnD). Ideales para aprender
una técnica concreta en una sentada:

[Simple Inventory](https://gamemaker.io/tutorials/coffee-break-tutorials-simple-inventory-gml) ·
[Juicy Screenshake](https://gamemaker.io/tutorials/coffee-break-tutorials-juicy-screenshake-gml) ·
[Typewriter Dialogue](https://gamemaker.io/tutorials/coffee-break-tutorial-easy-typewriter-dialogue-gml) ·
[Simple Lighting](https://gamemaker.io/tutorials/coffee-break-tutorial-simple-lighting-gml) ·
[Gamepads](https://gamemaker.io/tutorials/coffee-break-tutorials-setting-up-and-using-gamepads-gml) ·
[Decal Effects](https://gamemaker.io/tutorials/coffee-break-tutorials-decal-effects-gml) ·
[Checkpoints Using Buffers](https://gamemaker.io/tutorials/coffee-break-tutorials-checkpoints-using-buffers-gml) ·
[Finite State Machines](https://gamemaker.io/tutorials/coffee-break-tutorials-finite-state-machines-gml) ·
[Pausing Your Game](https://gamemaker.io/tutorials/coffee-break-tutorials-pausing-your-game-gml) ·
[Parallax Scrolling](https://gamemaker.io/tutorials/coffee-break-tutorials-parallax-scrolling-gml)

---

## 4. Los 106 tutoriales oficiales

Ordenados por relevancia editorial (el orden en que los presenta la web), agrupados por tipo.

| # | Tutorial | Nivel | Sabor | Enlace |
|---|----------|-------|-------|--------|
| 1 | Make Your Own Arcade Space Shooter | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/make-arcade-space-shooter |
| 2 | Make Your First Platformer in GameMaker | Principiante | GML Code | https://gamemaker.io/tutorials/your-first-platformer |
| 3 | Make Your Own Role-Playing Game | Principiante | GML Code | https://gamemaker.io/tutorials/how-to-make-an-rpg |
| 4 | Make Your Own Endless Platformer | Principiante | GML Visual | https://gamemaker.io/tutorials/fire-jump-dnd-1 |
| 5 | Make Your Own Action-Adventure Game | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-dnd-2 |
| 6 | Make A Sprawling Adventure Game | Principiante | GML Code | https://gamemaker.io/tutorials/little-town-gamemaker-tutorial |
| 7 | How to Get Started with GameMaker in 2026 | Principiante | — | https://gamemaker.io/tutorials/get-started-gamemaker-2026 |
| 8 | How To Move And Collide In GameMaker | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/easy-move-collide |
| 9 | How To Make Platformer Movement In GameMaker | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/easy-platformer |
| 10 | A New Frontier: How To Mod Space Rocks | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/space-rocks-mods |
| 11 | How to Make a Multiplayer Game | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/easy-multiplayer-tutorial |
| 12 | Crie seu primeiro jogo \| Guselect | Principiante | GML Code | https://gamemaker.io/tutorials/primeiro-jogo |
| 13 | Make Your First Car Game \| Josia Roncancio | Principiante | GML Visual | https://gamemaker.io/tutorials/car-parking-game-tutorial |
| 14 | Beginner GameMaker Tutorial - Your Own Action-Adventure | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-start |
| 15 | Making Fire Jump \| Part 4 | Principiante | GML Visual | https://gamemaker.io/tutorials/fire-jump-dnd-4 |
| 16 | Making Fire Jump \| Part 3 | Principiante | GML Visual | https://gamemaker.io/tutorials/fire-jump-dnd-3 |
| 17 | Making Fire Jump \| Part 2 | Principiante | GML Visual | https://gamemaker.io/tutorials/fire-jump-dnd-2 |
| 18 | Hero's Trail \| Base Project Breakdown/Overview | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-breakdown |
| 19 | Make Your Own Action-Adventure Game | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-dnd-1 |
| 20 | Hero's Trail: Player Abilities & Power Ups | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-dnd-5 |
| 21 | Hero's Trail: Enemy AI, Sequence Animations & Hearts | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-dnd-4 |
| 22 | Hero's Trail: Interactive Level Design (Chests & Gates) | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-dnd-3 |
| 23 | Hero's Trail: User Interfaces, Pausing & Sound | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-dnd-6 |
| 24 | Hero's Trail \| Feature Tutorials Index | Principiante | GML Visual | https://gamemaker.io/tutorials/heros-trail-dnd |
| 25 | Fire Jump \| Beginner Tutorial \| Infinite Platformer | Principiante | GML Visual | https://gamemaker.io/tutorials/fire-jump-dnd |
| 26 | My First Arena Shooter \| GML | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/my-first-arena-shooter-gml |
| 27 | Breakthrough \| GML | Principiante | GML Code | https://gamemaker.io/tutorials/breakthrough-gml |
| 28 | Breakthrough \| DnD | Principiante | GML Visual | https://gamemaker.io/tutorials/breakthrough-dnd |
| 29 | Space Rocks \| GML | Principiante | GML Code | https://gamemaker.io/tutorials/space-rocks-gml |
| 30 | My First Arena Shooter \| DnD | Principiante | GML Visual | https://gamemaker.io/tutorials/my-first-arena-shooter-dnd |
| 31 | Space Rocks \| DnD | Principiante | GML Visual | https://gamemaker.io/tutorials/space-rocks-dnd |
| 32 | Ultimate Guide To Collision Functions | Intermedio | GML Code | https://gamemaker.io/tutorials/collision-functions |
| 33 | How To Optimise Your Games | Principiante | GML Code | https://gamemaker.io/tutorials/how-to-optimise-your-games |
| 34 | A Unity User's Guide To GameMaker | Principiante | — | https://gamemaker.io/tutorials/moving-from-unity-to-gamemaker |
| 35 | How To Change Sprite Size, Colour And Rotation in GameMaker | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/change-sprite-size-colour-rotation |
| 36 | The Tile Set Editor | Principiante | — | https://gamemaker.io/tutorials/tile-set-editor |
| 37 | The Gesture Events | Principiante | — | https://gamemaker.io/tutorials/gesture-events |
| 38 | The Workspace | Principiante | — | https://gamemaker.io/tutorials/workspaces |
| 39 | The Debugger | Principiante | — | https://gamemaker.io/tutorials/debugger |
| 40 | The Image Editor - IDE Basics | Principiante | — | https://gamemaker.io/tutorials/image-editor |
| 41 | The Object Editor - IDE Basics | Principiante | — | https://gamemaker.io/tutorials/object-editor |
| 42 | The Room Editor - IDE Basics | Principiante | — | https://gamemaker.io/tutorials/room-editor |
| 43 | The Sprite Editor - IDE Basics | Principiante | — | https://gamemaker.io/tutorials/sprite-editor |
| 44 | The Basics Of Scaling - HTML5 | Principiante | — | https://gamemaker.io/tutorials/the-basics-of-scaling-html5 |
| 45 | The Basics Of Scaling - The Game Camera | Principiante | — | https://gamemaker.io/tutorials/the-basics-of-scaling-the-game-camera |
| 46 | The Basics Of Scaling - The GUI Layer | Principiante | — | https://gamemaker.io/tutorials/the-basics-of-scaling-the-gui-layer |
| 47 | Coffee-Break Tutorials: Simple Inventory (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorials-simple-inventory-dnd |
| 48 | Coffee-Break Tutorials: Simple Inventory (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorials-simple-inventory-gml |
| 49 | Coffee-Break Tutorials: Juicy Screenshake (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorials-juicy-screenshake-gml |
| 50 | Coffee-Break Tutorials: Juicy Screenshake (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorials-juicy-screenshake-dnd |
| 51 | Coffee-Break Tutorial: Easy Typewriter Dialogue (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorial-easy-typewriter-dialogue-gml |
| 52 | Coffee-Break Tutorial: Easy Typewriter Dialogue (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorial-easy-typewriter-dialogue-dnd |
| 53 | Coffee-Break Tutorial: Simple Lighting (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorial-simple-lighting-gml |
| 54 | Coffee-Break Tutorial: Simple Lighting (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorial-simple-lighting-dnd |
| 55 | Coffee-Break Tutorials: Setting Up And Using Gamepads (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorials-setting-up-and-using-gamepads-dnd |
| 56 | Coffee-Break Tutorials: Setting Up And Using Gamepads (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorials-setting-up-and-using-gamepads-gml |
| 57 | Coffee-Break Tutorials: Decal Effects (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorials-decal-effects-dnd |
| 58 | Coffee-Break Tutorials: Decal Effects (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorials-decal-effects-gml |
| 59 | Coffee-break Tutorials: Checkpoints Using Buffers (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorials-checkpoints-using-buffers-dnd |
| 60 | Coffee-break Tutorials: Checkpoints Using Buffers (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorials-checkpoints-using-buffers-gml |
| 61 | Coffee-Break Tutorials: Finite State Machines (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorials-finite-state-machines-gml |
| 62 | Coffee-Break Tutorials: Finite State Machines (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorials-finite-state-machines-dnd |
| 63 | Coffee-break Tutorials: Pausing Your Game (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorials-pausing-your-game-gml |
| 64 | Coffee-Break Tutorials: Pausing Your Game (DnD) | Principiante | GML Visual | https://gamemaker.io/tutorials/coffee-break-tutorials-pausing-your-game-dnd |
| 65 | Coffee-Break Tutorials: Parallax Scrolling (GML) | Principiante | GML Code | https://gamemaker.io/tutorials/coffee-break-tutorials-parallax-scrolling-gml |
| 66 | How to Publish a Mobile Game on GX.games | Principiante | — | https://gamemaker.io/tutorials/publish-mobile-games-for-free |
| 67 | Publish Your Game to GX.games In 5 Minutes | Principiante | — | https://gamemaker.io/tutorials/publish-to-gxgames-tutorial |
| 68 | How to Get Noticed on GX.games | Principiante | — | https://gamemaker.io/tutorials/gxgames-get-noticed |
| 69 | GX.games: How To Create Challenges For Your Games | Principiante | — | https://gamemaker.io/tutorials/gxgames-challenges |
| 70 | Making In-Game Leaderboards For GX.games Challenges | Intermedio | — | https://gamemaker.io/tutorials/gxgames-in-game-leaderboards |
| 71 | Displaying Player Avatar In-Game on GX.games | — | — | https://gamemaker.io/tutorials/gxgames-in-game-avatars |
| 72 | How To Use Physics Raycast In GameMaker | Intermedio | GML Code | https://gamemaker.io/tutorials/physics-raycast |
| 73 | Physics In GameMaker Studio 2 - Part 4 | — | — | https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-4 |
| 74 | Physics In GameMaker Studio 2 - Part 3 | — | — | https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-3 |
| 75 | Physics In GameMaker Studio 2 - Part 2 | — | — | https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-2 |
| 76 | Physics In GameMaker Studio 2 - Part 1 | — | — | https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-1 |
| 77 | GameMaker Testing Library - Catch Bugs Early and Improve Your Game | — | — | https://gamemaker.io/tutorials/gamemaker-testing-library-tutorial |
| 78 | How To Integrate Facebook Into Your Games | — | — | https://gamemaker.io/tutorials/integrate-facebook-into-your-games |
| 79 | How to Add Multiplayer to An Existing Game In GameMaker | Intermedio | GML Code + Visual | https://gamemaker.io/tutorials/add-multiplayer-to-gamemaker |
| 80 | How To Use Advanced Array Functions in GameMaker | Avanzado | GML Code | https://gamemaker.io/tutorials/advanced-array-functions |
| 81 | How to Make Buttons in GameMaker | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/how-to-make-buttons |
| 82 | How To Fix Runtime Errors in GameMaker | Intermedio | GML Code | https://gamemaker.io/tutorials/fix-runtime-errors |
| 83 | How to Change Your Game's Resolution & Use a Mobile Aspect Ratio | Principiante | — | https://gamemaker.io/tutorials/resolution-scaling-mobile |
| 84 | How To Use Audio Effects in GameMaker | Principiante | GML Code | https://gamemaker.io/tutorials/audio-effects |
| 85 | How to Create HUD in Windy Woods | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/custom-hud-windy-woods |
| 86 | How to Add a New Enemy In Windy Woods | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/new-enemy-windy-woods |
| 87 | How to Create Pickups in GameMaker | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/pickup-objects-gamemaker |
| 88 | Create Your Own Platformer With Windy Woods | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/create-platformer-windy-woods |
| 89 | How to Create Transitions in GameMaker | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/filter-transitions |
| 90 | How to Create Checkpoints in GameMaker | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/create-checkpoints-gamemaker |
| 91 | How to Create Jump-Through Platforms | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/platformer-jump-through |
| 92 | How to Wall Jump in a Platformer | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/platformer-wall-jump |
| 93 | How to Double Jump in a Platformer | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/platformer-double-jump |
| 94 | How to Animate Objects in GameMaker | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/animate-objects-gamemaker |
| 95 | How to Add Multi-Touch and Virtual Joystick Controls | — | — | https://gamemaker.io/tutorials/multi-touch-joystick |
| 96 | Little Town \| GameMaker Studio 2 Education Tutorial Materials | Intermedio | GML Code | https://gamemaker.io/tutorials/little-town-gamemaker-education |
| 97 | Amazon Fire and GameCircle | Principiante | — | https://gamemaker.io/tutorials/amazon-fire-gamecircle |
| 98 | Cameras And Views | Principiante | — | https://gamemaker.io/tutorials/cameras-and-views |
| 99 | Education: Learning to Program | Principiante | — | https://gamemaker.io/tutorials/education-learning-to-program |
| 100 | Buttery Smooth Tech: Inputs | Intermedio | — | https://gamemaker.io/tutorials/buttery-smooth-tech-inputs |
| 101 | Space Mods: Continue Your Space Rocks Game | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/space-mods-continue-your-space-rocks-game |
| 102 | Create a Platformer Game with GML | Intermedio | GML Code | https://gamemaker.io/tutorials/create-a-platformer-game-with-gml |
| 103 | Beginners Guide To Networking | Principiante | — | https://gamemaker.io/tutorials/beginners-guide-to-networking |
| 104 | Quickstart On Exporting And Sharing Your Game | — | — | https://gamemaker.io/tutorials/quickstart-on-exporting-and-sharing-your-game |
| 105 | Arcade Game Tutorial: Make Breakthrough | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/gms2-tutorial-breakthrough |
| 106 | My First Game: Make Your Own Arcade Classic | Principiante | GML Code + Visual | https://gamemaker.io/tutorials/make-your-own-arcade-classic |

### Series que conviene seguir en orden

Algunos tutoriales son entregas de una misma serie; hacerlos sueltos descoloca:

| Serie | Orden |
|---|---|
| **Fire Jump** (GML Visual, plataformas infinitas) | [índice](https://gamemaker.io/tutorials/fire-jump-dnd) → [1](https://gamemaker.io/tutorials/fire-jump-dnd-1) → [2](https://gamemaker.io/tutorials/fire-jump-dnd-2) → [3](https://gamemaker.io/tutorials/fire-jump-dnd-3) → [4](https://gamemaker.io/tutorials/fire-jump-dnd-4) |
| **Hero's Trail** (GML Visual, acción-aventura) | [índice](https://gamemaker.io/tutorials/heros-trail-dnd) → [start](https://gamemaker.io/tutorials/heros-trail-start) → [breakdown](https://gamemaker.io/tutorials/heros-trail-breakdown) → [1](https://gamemaker.io/tutorials/heros-trail-dnd-1) → [2](https://gamemaker.io/tutorials/heros-trail-dnd-2) → [3](https://gamemaker.io/tutorials/heros-trail-dnd-3) → [4](https://gamemaker.io/tutorials/heros-trail-dnd-4) → [5](https://gamemaker.io/tutorials/heros-trail-dnd-5) → [6](https://gamemaker.io/tutorials/heros-trail-dnd-6) |
| **Físicas** | [1](https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-1) → [2](https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-2) → [3](https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-3) → [4](https://gamemaker.io/tutorials/physics-in-gamemaker-studio-2-part-4) → [Raycast](https://gamemaker.io/tutorials/physics-raycast) |
| **Escalado** | [HTML5](https://gamemaker.io/tutorials/the-basics-of-scaling-html5) → [Game Camera](https://gamemaker.io/tutorials/the-basics-of-scaling-the-game-camera) → [GUI Layer](https://gamemaker.io/tutorials/the-basics-of-scaling-the-gui-layer) |
| **Windy Woods** (sobre el proyecto base) | [Platformer](https://gamemaker.io/tutorials/create-platformer-windy-woods) → [HUD](https://gamemaker.io/tutorials/custom-hud-windy-woods) → [New Enemy](https://gamemaker.io/tutorials/new-enemy-windy-woods) |
| **Space Rocks / Space Mods** | [Space Rocks GML](https://gamemaker.io/tutorials/space-rocks-gml) o [DnD](https://gamemaker.io/tutorials/space-rocks-dnd) → [Mods](https://gamemaker.io/tutorials/space-rocks-mods) → [Space Mods: Continue](https://gamemaker.io/tutorials/space-mods-continue-your-space-rocks-game) |

---

## 5. Quick Start Guides del manual

Ruta: <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Quick_Start_Guide.htm>

> **Nota**: las URLs del manual están detrás de Cloudflare y devuelven `403 Forbidden` al
> descargarlas con `curl`/navegadores no autenticados. Las páginas de esta sección se han
> **localizado y verificado con `gm-cli manual read`**, que consulta el mismo índice y devuelve la
> URL de origen de cada artículo.

### Qué es la Quick Start Guide

Según el propio manual:

> «Welcome to the Quick Start Guide! This section of the manual is designed to familiarise you
> with the most important aspects of GameMaker […] The guide covers essential IDE functionality
> and also provides a brief introduction to programming […] whether you use GML Code or GML
> Visual.»

Y resume el flujo de trabajo en cuatro pasos:

1. Crear recursos de imagen (sprites, tilesets) y añadirlos al Asset Browser.
2. Crear objects que representen las cosas del juego y asignarles sus imágenes.
3. Programar esos objects para que hagan cosas en respuesta a eventos.
4. Colocar instancias de esos objects en una room.

### Las 7 páginas verificadas

| # | Página | Contenido | Enlace |
|---|--------|-----------|--------|
| 1 | **Quick Start Guide** | Introducción: qué es GameMaker, el game loop (60 FPS por defecto, un «step» por frame) y el flujo sprites → objects → rooms | <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Quick_Start_Guide.htm> |
| 2 | **Creating Sprites** | Crear y animar sprites | <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Creating_Sprites.htm> |
| 3 | **Objects And Instances** | Objetos e instancias, la diferencia entre ambos | <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Objects_And_Instances.htm> |
| 4 | **Rooms** | El editor de rooms: capas, instancias, vistas | <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Rooms.htm> |
| 5 | **Movement And Controls** | Movimiento y controles (teclado, gamepad, táctil) | <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Movement_And_Controls.htm> |
| 6 | **Creating Sound Effects** | Añadir efectos de sonido | <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Creating_Sound_Effects.htm> |
| 7 | **Creating Tile Sets** | Tilesets y capas de tiles | <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Creating_Tile_Sets.htm> |

### Páginas complementarias que el índice asocia a esta sección

No son parte de la Quick Start Guide pero aparecen al consultar los mismos temas:

| Tema | Enlace |
|---|---|
| Objects vs Instances | <https://manual.gamemaker.io/monthly/en/Additional_Information/Objects_vs_Instances.htm> |
| Eventos de objeto | <https://manual.gamemaker.io/monthly/en/The_Asset_Editors/Object_Properties/Object_Events.htm> |
| The Asset Editors (índice) | <https://manual.gamemaker.io/monthly/en/The_Asset_Editors/The_Asset_Editors.htm> |
| Fuentes (editor) | <https://manual.gamemaker.io/monthly/en/The_Asset_Editors/Fonts.htm> |
| Paths (editor) | <https://manual.gamemaker.io/monthly/en/The_Asset_Editors/Paths.htm> |
| Guía de partículas | <https://manual.gamemaker.io/monthly/en/Additional_Information/Guide_To_Using_Particles.htm> |
| Variables de instancia | <https://manual.gamemaker.io/monthly/en/GameMaker_Language/GML_Overview/Variables/Instance_Variables.htm> |
| Referencia de GML | <https://manual.gamemaker.io/monthly/en/GameMaker_Language.htm> |
| Compilar | <https://manual.gamemaker.io/monthly/en/Introduction/Compiling.htm> |
| Detalles del runner | <https://manual.gamemaker.io/monthly/en/Settings/Runner_Details/Runner_Details.htm> |

### Cómo consultar el manual sin salir de la terminal

```bash
# Buscar un tema y leerlo en la terminal
gm-cli manual read "creating sprites"

# Abrir la página en el navegador
gm-cli manual open "rooms"

# En otro idioma (en|ru|br|it|fr|pl|es|ko|de|ja|zh)
gm-cli manual read "movement and controls" --language es
```

Cada respuesta termina con la línea `Article source: <url>`, que es la forma más fiable de
localizar la página exacta en el manual.

---

## 6. Fuentes

- Listado oficial de tutoriales (9 páginas recorridas): <https://gamemaker.io/en/tutorials>
- Quick Start Guide del manual: <https://manual.gamemaker.io/lts/en/Quick_Start_Guide/Quick_Start_Guide.htm>
- Índice del manual: <https://manual.gamemaker.io/>
- Canal oficial de YouTube: <https://www.youtube.com/@GameMakerEngine>
- Documentación de la Testing Library: <https://github.com/YoYoGames/GM-TestFramework>
- Plantillas de proyecto descargables (muchas acompañan a los tutoriales):
  <https://api.gamemaker.io/api/gamemaker/project-templates>
- Foro oficial (dudas de los tutoriales): <https://forum.gamemaker.io/>
- Centro de ayuda: <https://gamemaker.io/en/help>
