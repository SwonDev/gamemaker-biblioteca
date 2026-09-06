# 04 · Proyectos de ejemplo para estudiar

> Verificado el **31 de agosto de 2026**. Estrellas, licencias y fechas de último *push* comprobadas contra la API de GitHub.
> Criterio: proyectos **jugables** o **frameworks completos**, con código abierto y actividad reciente.

---

## ⚠️ Aviso legal importante (léelo antes de clonar nada)

Muchos de los proyectos GameMaker más populares en GitHub son **reconstrucciones de la comunidad de juegos comerciales** (*Hotline Miami*, *Pizza Tower*, *AM2R*, *Nuclear Throne*, *Deltarune*, *Undertale*…).

- **Estudiarlos** para aprender técnicas es una práctica extendida en la comunidad.
- **Reutilizar código, arte, sonido o nivelado** de esos repos en tu propio juego es **infractor**: esos activos pertenecen a sus autores originales, y en varios casos los repos lo reconocen en el propio README.
- Varios están marcados explícitamente como *«non-profit fan project»*, *«semi-accurate decompilation»* o *«community-maintained source code»*.

**Regla práctica:** clona para **leer**, nunca para **copiar**. En la tabla siguiente marco con 🚩 los que caen en esta categoría.

---

## 1. Los que publica YoYoGames

| Proyecto | Enlace | Tipo | Licencia | Push | ★ |
|---|---|---|---|---:|---:|
| **GM3D-Samples** | [YoYoGames/GM3D-Samples](https://github.com/YoYoGames/GM3D-Samples) | Ejemplos de **3D** (GM3D), con shaders y notas | MIT | 2026-08-20 | 13 |
| **pfb-UserInterface** | [YoYoGames/pfb-UserInterface](https://github.com/YoYoGames/pfb-UserInterface) | Prefabs de **UI** (11 componentes) | MIT | 2026-07-02 | 3 |
| **pfb-Inventory** | [YoYoGames/pfb-Inventory](https://github.com/YoYoGames/pfb-Inventory) | Prefab de **inventario** | MIT | 2026-06-03 | 0 |
| **pfb-MiniMap** | [YoYoGames/pfb-MiniMap](https://github.com/YoYoGames/pfb-MiniMap) | Prefab de **minimapa** | MIT | 2026-05-12 | 0 |
| **ImGUI-Sample** | [YoYoGames/ImGUI-Sample](https://github.com/YoYoGames/ImGUI-Sample) | Demo de **Dear ImGui** sobre GMRT | MIT | 2026-07-30 | 0 |
| **GM-GPUTextureCompression** | [YoYoGames/GM-GPUTextureCompression](https://github.com/YoYoGames/GM-GPUTextureCompression) | Compresión de **texturas en GPU** | Apache-2.0 | 2025-07-14 | 11 |
| **GM-RedditDemo** | [YoYoGames/GM-RedditDemo](https://github.com/YoYoGames/GM-RedditDemo) | Integración con **Reddit / Devvit** | Apache-2.0 | 2026-02-09 | 4 |
| **GM-TestFramework** | [YoYoGames/GM-TestFramework](https://github.com/YoYoGames/GM-TestFramework) | Suite de **tests unitarios** de GameMaker | NOASSERTION | 2026-08-25 | 25 |

### Plantillas del IDE (las que ves al crear proyecto)

YoYoGames publica **31 plantillas** vía API (`https://api.gamemaker.io/api/gamemaker/project-templates`), accesibles también desde `gm-cli init`. Las de tipo *Game* verificadas:

Space Rocks · Arcade Action · Tower Defense · Hero's Trail (GML Visual) · Blank Pixel Game · Idle Game · Scrolling Shooter · Cover Assault · RPG Starter Pack · Platformer · Card Game · Endless Runner · Twin Stick Shooter · Survivor Game · Fire Jump · Match 3 · Brick Breaker · Puzzle Slider.

> Ver el archivo `06 - Plantillas y starters.md` para el detalle de cómo elegir entre ellas.

### Descartados (históricos)

| Proyecto | Último push | Motivo |
|---|---|---|
| [YoYoGames/YourWorld](https://github.com/YoYoGames/YourWorld) | **2017-05-04** | Proyecto de la era GameMaker: Studio. Solo valor arqueológico. 45 ★. |
| [YoYoGames/3D-2D](https://github.com/YoYoGames/3D-2D) | **2023-03-27** | Sustituido por GM3D-Samples. 48 ★. |

---

## 2. Frameworks de juego — nivel intermedio–avanzado

Son **bases completas** sobre las que construir. Los mejores para aprender arquitectura seria.

### Orbinaut Framework ⭐ recomendado

- **Enlace:** <https://github.com/TrianglyRU/OrbinautFramework> · **125 ★** · push 2026-08-20 · **sin licencia declarada** ⚠️ (tiene sección «Terms of Use» en el README: léela antes de usarlo).
- **Género:** plataformas **Sonic clásico** (2D).
- **Qué aprenderás:** colisiones **personaje ↔ terreno** de altísima precisión, física por *tiles*, deformación de capas, *fade* por paleta, hasta **8 jugadores en pantalla partida**, 4 personajes jugables.
- **Documentación:** <https://github.com/TrianglyRU/OrbinautFramework/wiki>
- **Estado:** el autor lo declara **completo**; los *pushes* posteriores son mejoras menores.
- **Nota:** declara explícitamente que funciona con la **última LTS** y que no garantiza compatibilidad con otras versiones.

### Harmony Framework

- **Enlace:** <https://github.com/UltraRing/Harmony-Framework> · **81 ★** · **MIT** · push 2026-08-29.
- **Género:** Sonic clásico.
- **Qué aprenderás:** alternativa a Orbinaut con licencia **limpia (MIT)**. Mismo dominio: física precisa de plataformas.

### Megamix Engine

- **Enlace:** <https://github.com/MegamixEngine/MegamixEngine> · **50 ★** · **sin licencia** ⚠️ · push 2026-07-30.
- **Género:** plataformas de acción estilo *Mega Man*.
- **Qué aprenderás:** gestión de jefes, armas desbloqueables, *stages* seleccionables.

### renex2-engine

- **Enlace:** <https://github.com/omicronrex/renex2-engine> · **36 ★** · NOASSERTION · push 2026-07-29.
- **Género:** motor tipo *I Wanna Be The Guy* (plataformas de precisión).
- **Nota:** diseñado para **GM 8.2**, no para LTS 2026. Estúdialo por las técnicas, no para usarlo tal cual.

---

## 3. Juegos completos — nivel principiante–intermedio

| Proyecto | Enlace | Género | Licencia | Push | ★ | Qué aprenderás |
|---|---|---|---|---:|---:|---|
| **Spelunky Classic HD** | [yancharkin/SpelunkyClassicHD](https://github.com/yancharkin/SpelunkyClassicHD) | Plataformas / roguelite | NOASSERTION | 2026-08-25 | 219 | **Generación procedural de niveles** sobre plantillas de sala, físicas simples, IA de enemigos. El clásico de Derek Yu, rehecho en HD. |
| **Chapter Master** | [Adeptus-Dominus/ChapterMaster](https://github.com/Adeptus-Dominus/ChapterMaster) | Estrategia / simulación | ⚠️ sin licencia | 2026-08-29 | 72 | Juego de gestión con mucha UI, datos y estados. Ideal para ver cómo estructurar un proyecto **grande y con muchos sistemas**. |
| **FVM-Reborn** | [Spring-SG/FVM-Reborn](https://github.com/Spring-SG/FVM-Reborn) | — | **GPL-3.0** | 2026-08-30 | 173 | Código activísimo (push del día anterior). ⚠️ Ojo: **GPL-3.0 es contagiosa** — si lo usas, tu proyecto derivado debe ser GPL. |
| **Kirby ~ Soft & Wet** | [MegaStrimp/Kirby-Soft-and-Wet](https://github.com/MegaStrimp/Kirby-Soft-and-Wet) 🚩 | Minijuego de pesca | ⚠️ sin licencia | 2026-08-30 | 63 | Fan project no lucrativo. Interesante por la gestión de **más de mil objetos coleccionables** con datos. |

---

## 4. Juegos completos — 🚩 reconstrucciones de juegos comerciales

**Solo para estudiar.** No reutilices arte, audio ni código.

| Proyecto | Enlace | Género | Licencia | Push | ★ | Qué aprenderás |
|---|---|---|---|---:|---:|---|
| **Undertale Engine** | [TML233/UndertaleEngine](https://github.com/TML233/UndertaleEngine) 🚩 | RPG / *fangame engine* | MIT | 2026-08-07 | 181 | Motor para *fangames* de Undertale: sistema de combate por *bullets*, diálogo ramificado, *overworld*. |
| **tldr-engine** | [tweenko/tldr-engine](https://github.com/tweenko/tldr-engine) 🚩 | RPG | MIT | 2026-08-19 | 82 | Réplica 1:1 del motor de *Deltarune*. Interesante por la fidelidad del sistema de combate. |
| **Gang Garrison 2** | [Gang-Garrison-2/Gang-Garrison-2](https://github.com/Gang-Garrison-2/Gang-Garrison-2) | **Multijugador** (demake 2D de TF2) | **MPL 2.0** (badge + `MPL-2.0.txt` en el repo; GitHub lo reporta como NOASSERTION) | 2026-07-26 | 119 | ⭐ **El mejor repo de GameMaker para aprender netcode**: *rollback*, predicción del cliente, sincronización de entidades, lag compensation, 9 clases. |
| **Nuclear Throne (rebuild)** | [toarch7/nt-recreated-public](https://github.com/toarch7/nt-recreated-public) 🚩 | Roguelite *twin-stick* | **GPL-3.0** | 2026-08-19 | 82 | Reconstrucción + port a Android. *Twin-stick shooter*, generación de niveles, armas. |
| **HotlineMiami.gmx** | [Pi0h1/HotlineMiami.gmx](https://github.com/Pi0h1/HotlineMiami.gmx) 🚩 | Acción *top-down* | ⚠️ sin licencia | 2026-07-28 | 82 | Niveles, IA de enemigos con cono de visión, sigilo. El propio repo se define como «*community-maintained source code of Dennaton's 2012 game*». |
| **Pizza Tower EXtracted** | [setupwitch/Pizza-Tower-EXtracted](https://github.com/setupwitch/Pizza-Tower-EXtracted) 🚩 | Plataformas | ⚠️ sin licencia | 2026-07-28 | 25 | «*Semi-accurate decompilation*». Muy útil para ver **máquina de estados del jugador** con mucho *momentum*. |
| **AM2R: ReSplashed** | [AbyssalCreature/AM2R-Re-Splashed](https://github.com/AbyssalCreature/AM2R-Re-Splashed) 🚩 | Metroidvania | NOASSERTION | 2026-07-22 | 22 | Mapas, *backtracking*, habilidades desbloqueables. |
| **Undertale Engine (fork Zhazha)** | [onezhazha233/Undertale-Engine-modded-by-Zhazha](https://github.com/onezhazha233/Undertale-Engine-modded-by-Zhazha) 🚩 | RPG | ⚠️ sin licencia | 2026-08-30 | 21 | *Fork* del anterior con modificaciones. |
| **Deltarune Chinese** | [gm3dr/DeltaruneChinese](https://github.com/gm3dr/DeltaruneChinese) 🚩 | Traducción | — | 2026-08-26 | 95 | Más que un juego: ejemplo de **localización** de un proyecto complejo. |

---

## 4 bis. Proyectos de tutorial de DragoniteSpam — **organización COMPLETA** (193 proyectos)

[DragoniteSpam](https://github.com/DragoniteSpam-GameMaker-Tutorials) es un tutor veterano de
GameMaker con una organización de GitHub de **193 proyectos completos**, cada uno el código real
que acompaña a un tutorial suyo. **Todos están descargados** en este repositorio y **todos son
MIT** (`Copyright (c) DragoniteSpam's Game Maker Tutorials`): puedes estudiarlos, copiar técnicas
y reutilizar código citando la fuente.

- **189 proyectos** en la carpeta `11 - Código descargado/plantillas_y_ejemplos/dragonitespam/` (una subcarpeta por tutorial, nombrada como el repo).
- **4 destacados** viven en sus carpetas temáticas con prefijo `DS-` (ver más abajo).
- Cada uno está registrado en [`_RUTAS.json`](../11%20-%20Código%20descargado/_RUTAS.json) con la
  clave `DS-<Nombre>`, así que `python3 "_indice/buscar.py" --codigo <tema>` los encuentra.

### Los 4 destacados (en carpetas temáticas)

| Proyecto | Ubicación | Qué enseña |
|---|---|---|
| **LMAGBulletHell** | `juegos_y_motores/DS-LMAGBulletHell` | **Bullet hell jugable** (202 scripts): patrones de bala, oleadas, colisión |
| **BaseProject2D** | `plantillas_y_ejemplos/DS-BaseProject2D` | Plantilla base 2D: su punto de partida en los tutoriales |
| **3DCollisions** | `librerias/3d/DS-3DCollisions` | Colisiones 3D **nativas** (sin librería), con solo el runtime |
| **TutorialSimple2DLighting** | `librerias/iluminacion/DS-TutorialSimple2DLighting` | Iluminación 2D paso a paso (acompaña a [24 · Iluminación 2D](../04%20-%20Recetas%20por%20género/24%20-%20Iluminación%202D.md)) |

### Los 189 restantes, por tema (carpeta `dragonitespam/`)

| Tema | Nº | Ejemplos clave (hay más — busca en la carpeta) |
|---|---:|---|
| **3D** (serie 1→94) | 90 | `3DTutorial1-CameraProjection` → `3DTutorial94Using2DCollisions`: vertex buffers, OBJ/MTL, first/third person, matrices, **deferred rendering** (59-84), **shadowmapping** (48-49, 82), normal mapping (71-73 TBN), **BlinnPhong** (70), toon shading (36-40), SSAO, fog, billboarding, split-screen |
| **Shaders 2D** | 22 | `TutorialBloom`, `TutorialShaderChromaticAberration`, `TutorialPaletteSwapping`, `TutorialShaderPosterization`, `TutorialShaderNoise`, `TutorialShaderOutlines`, `TutorialShaderUniformArrays`, `TutorialShaderHLSL` |
| **Gráficos 2D** | 21 | `TutorialSurfaces`, `TutorialBlendModes`, `TutorialSDFFonts`, `TutorialSpriteStacking`, `TutorialSpriteAtlasing`, `TutorialApplicationSurface`, `TutorialTextureGroupDynamic` |
| **Lenguaje GML 2.3+** | 13 | `Tutorial230StructsConstructors`, `Tutorial230StructsMethods`, `Tutorial230StructInheritance`, `230StaticVariables`, `Tutorial230TryCatch`, `230ChainedAccessors`, `ArrayLiterals`, `ConditionalOperator` — **oro para no alucinar** la sintaxis moderna |
| **Diálogo y texto** | — | `TutorialChatterboxSetup`, `TutorialSimpleDialogue`, `TutorialScribble`, `TutorialScribbleTypistEvents`, `TutorialScribbleSDF` — narrativa, cajas de diálogo, efecto máquina de escribir |
| **Audio** | 5 | `TutorialAudioBusses`, `TutorialAudioEmitters`, `TutorialAudioLoopPoints` (música con bucles perfectos) |
| **Datos / guardado** | 4 | `TutorialSNAP` (serialización), `TutorialJsonParseAndStringify`, `TutorialBufferAsyncFixed`, `InstanceVariableDefinitions` |
| **Vídeo** | — | `VideoPlaybackDemo` — reproducción de vídeo dentro del juego (cinemáticas, intros) |
| **Optimización** | 2 | `GeneralOptimization`, `HowManyTriangles` (benchmark de rendimiento 3D) |
| **Juegos / demos** | 5 | `Bombadier`, `LMAGWizards`, `make_game`, `TutorialGLSLMRTs` |
| **Varios** | 28 | `TutorialAutotiles`, `TutorialSwayingGrass`, `TutorialWeightedChance`, `TutorialTimeSources`, `TutorialDeltaTimeSlices`, `TutorialWeakReferences`, `TutorialDebugConsole`, `JSDoc`, `CompatibilityScripts` |

> 🎯 **Cómo usarlos:** ¿necesitas una técnica concreta (deferred rendering, diálogo, guardado
> con SNAP, palette swap)? En vez de partir de cero, `python3 "_indice/buscar.py" --codigo <tema>`
> o abre la carpeta `dragonitespam/` y busca el `Tutorial<Tema>` o `3DTutorial<n><Tema>`. Es
> código GML real, moderno (muchos actualizados a 2.3+) y con licencia MIT.
>
> ⚠️ **Antes de reutilizar en tu juego:** el código es de **DragoniteSpam** bajo MIT — conserva
> el aviso de copyright si copias archivos enteros. Estúdialo para aprender la técnica; adáptala.

---

## 5. Herramientas hechas en GameMaker — nivel avanzado

A veces se aprende más de una **herramienta** que de un juego: son proyectos con UI densa, gestión de ficheros y arquitectura de verdad.

| Proyecto | Enlace | Qué es | Licencia | Push | ★ |
|---|---|---|---|---:|---:|
| **Pixel Composer** ⭐ | [Ttanasart-pt/Pixel-Composer](https://github.com/Ttanasart-pt/Pixel-Composer) | Editor de VFX para *pixel art* **basado en nodos** | **MIT** | 2026-08-29 | **1353** |
| **Note Block Studio** | [OpenNBS/NoteBlockStudio](https://github.com/OpenNBS/NoteBlockStudio) | Creador de música estilo Minecraft | **MIT** | 2026-08-21 | **1013** |
| **Mine-imator** | [stuffbydavid/Mine-imator](https://github.com/stuffbydavid/Mine-imator) | Creador de películas 3D con assets de Minecraft | ⚠️ sin licencia | 2026-08-30 | 248 |
| **DyNode** | [NordLandeW/DyNode](https://github.com/NordLandeW/DyNode) | Editor de *charts* rítmicos | **MIT** | 2026-08-22 | 30 |

> **Pixel Composer** y **Note Block Studio** son, con diferencia, los proyectos GameMaker más populares de la plataforma (1353 y 1013 ★) y ambos son **MIT**. Son el mejor ejemplo de lo que se puede construir con GameMaker más allá de los juegos.

---

## 6. Ruta de aprendizaje recomendada

### Nivel 1 — Primera semana

1. Crea **Space Rocks** desde `gm-cli init` (o desde el IDE) y léelo entero. Es el «Hola mundo» jugable.
2. Abre **pfb-UserInterface** y mira cómo YoYoGames estructura un componente reutilizable (botón, slider).
3. Juega con **pfb-Inventory** y **pfb-MiniMap**: son pequeños y se leen de una sentada.

### Nivel 2 — Primer mes

4. **Spelunky Classic HD** — generación procedural de niveles con salas pre-diseñadas. Es el patrón que usarás en el 80 % de tus juegos.
5. **Undertale Engine** o **tldr-engine** — sistemas de diálogo y combate por turnos.
6. Añade **GMRoomLoader** a tu proyecto y reescribe tu generación procedural con rooms modulares.

### Nivel 3 — Proyecto serio

7. **Harmony Framework** (MIT) u **Orbinaut Framework** — física de plataformas de precisión y colisión con el terreno.
8. **Gang Garrison 2** — si vas a hacer multijugador, no hay mejor referencia en GML.
9. **Pixel Composer** — para aprender arquitectura de UI compleja y grafos de nodos.

### Nivel 4 — Especialización

10. **GM3D-Samples** + **BBMOD** si te vas al 3D.
11. **GM-TestFramework** si quieres que tu juego no se rompa en cada release.

---

## 7. Resumen de licencias (lo que puedes y no puedes hacer)

| Licencia | ¿Puedo usarlo comercialmente? | ¿Tengo que abrir mi código? |
|---|---|---|
| **MIT** | ✅ Sí | ❌ No (solo atribuir) |
| **Apache-2.0** | ✅ Sí | ❌ No (solo atribuir + aviso de cambios) |
| **MPL 2.0** (Gang Garrison 2) | ✅ Sí | ⚠️ Parcial: los ficheros MPL deben seguir siendo MPL |
| **GPL-3.0** (FVM-Reborn, Nuclear Throne rebuild) | ✅ Sí | ⚠️ **Sí**: tu obra derivada debe ser GPL-3.0 |
| **NOASSERTION** | ⚠️ **Revisa el fichero LICENSE del repo** | Depende |
| **Sin licencia declarada** | ❌ **No**: sin licencia explícita, el copyright se reserva por defecto | — |
