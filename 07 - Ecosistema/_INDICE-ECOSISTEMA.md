# Índice del ecosistema GameMaker

> Documentado el **31 de agosto de 2026**.
> Contexto: **GameMaker LTS 2026.0** (IDE 2026.0.0.16 · runtime GMS2 2026.0.0.23) · **GMRT** en Beta · `gm-cli` 2.3.0 (verificado 07-09-2026, al día con la publicada).
> **Todo lo que aparece aquí se ha verificado contra la API de GitHub, la API de Codeberg, los READMEs de los repos o el manual oficial (`gm-cli manual read`).**

---

## Archivos de esta carpeta

| # | Archivo | Contenido | Elementos |
|---:|---|---|---:|
| 01 | [GitHub — organización YoYoGames](./01%20-%20GitHub%20-%20organización%20YoYoGames.md) | Los 96 repos de la org: GMRT, GameMaker-Bugs, gm-cli, GM-TestFramework, Extension Generator, manual, las 44 `GMEXT-*` y los proyectos de ejemplo oficiales | ~70 repos |
| 02 | [Librerías esenciales de la comunidad](./02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md) | Input, Scribble, Chatterbox, Vinyl, Bento, Bonk, db, Snitch, iota, GMRoomLoader, GMEdit… con ejemplos GML | ~55 repos |
| 03 | [Extensiones oficiales y de terceros](./03%20-%20Extensiones%20oficiales%20y%20de%20terceros.md) | Catálogo de las 44 `GMEXT-*` + Extension Generator + terceros | ~50 |
| 04 | [Proyectos de ejemplo para estudiar](./04%20-%20Proyectos%20de%20ejemplo%20para%20estudiar.md) | Frameworks, juegos completos y herramientas; ruta de aprendizaje por niveles | ~30 repos |
| 05 | [Scripts y utilidades GML](./05%20-%20Scripts%20y%20utilidades%20GML.md) | 12 utilidades con código completo: easing, tween, rejilla, A*, FSM, pooling, cámara con shake, guardado, input buffer, diálogo, Perlin, tilemaps | 12 scripts |
| 06 | [Plantillas y starters](./06%20-%20Plantillas%20y%20starters.md) | Las 31 plantillas oficiales, `gm-cli init`, andamiaje IA/CI y estructura de proyecto | 31 plantillas |
| 07 | [Foro oficial — hilos clave](./07%20-%20Foro%20oficial%20-%20hilos%20clave.md) | Estructura del foro, hilos «OFFICIAL», hilos técnicos de LTS 2026/GMRT, sección de tutoriales, cómo preguntar bien | — |
| 08 | [itch.io — jams, assets y juegos](./08%20-%20itch.io%20-%20jams,%20assets%20y%20juegos.md) | Publicar con `butler`, jams (gm(48), GMTK, Ludum Dare, GMC Jam), assets y juegos que estudiar | ~17 enlaces |
| 09 | [Asset packs y recursos gráficos](./09%20-%20Asset%20packs%20y%20recursos%20gráficos.md) | Licencias, bancos de assets, herramientas de pixel art, Tiled → GameMaker, audio y fuentes | — |
| 10 | [Comunidades y dónde preguntar](./10%20-%20Comunidades%20y%20dónde%20preguntar.md) | Discord oficial, r/gamemaker, comunidades **en español**, redes oficiales, normas de cortesía | — |
| 11 | [Blogs, newsletters y podcasts](./11%20-%20Blogs,%20newsletters%20y%20podcasts.md) | Fuentes oficiales, blogs de desarrolladores, YouTube, newsletters, veredicto honesto sobre podcasts | — |
| 12 | [Aprendizaje estructurado](./12%20-%20Aprendizaje%20estructurado%20-%20cursos%20de%20pago%20y%20libros.md) | Tutoriales oficiales gratis (primera opción), cursos de pago valorados, libros, ruta 2026 | — |
| 13 | [GM CLI — la línea de comandos](./13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md) | Referencia completa: `init`, `run`, `compile`, `package`, `manual`, `resourcetool`, `login`, `gxgames`, `cache` | — |
| 14 | [IA y GameMaker](./14%20-%20IA%20y%20GameMaker.md) | Estado real en 2026: no hay IA en el motor, `GMEXT-MLKit`, andamiaje `--ai`, MCP, roadmap | — |
| 15 | [Qué hacen de verdad los proyectos reales](./15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md) | 🆕 **Análisis de 1 333 953 líneas de GML** de los 21 juegos y motores descargados: qué técnicas se usan de verdad, funciones más llamadas y situación legal de cada proyecto | — |
| 17 | [SnowState — máquinas de estado (guía ES)](./17%20-%20SnowState%20-%20m%C3%A1quinas%20de%20estado%20%28gu%C3%ADa%20en%20espa%C3%B1ol%29.md) | **Guía traducida** de la FSM más usada: estados, transiciones, herencia, historial. API verificada contra el código | 1 |
| 18 | [Scribble — texto rico (guía ES)](./18%20-%20Scribble%20-%20texto%20rico%20%28gu%C3%ADa%20en%20espa%C3%B1ol%29.md) | **Guía traducida**: formato en línea, efectos animados, typewriter, ajuste | 1 |
| 19 | [Chatterbox — diálogos Yarn (guía ES)](./19%20-%20Chatterbox%20-%20di%C3%A1logos%20Yarn%20%28gu%C3%ADa%20en%20espa%C3%B1ol%29.md) | **Guía traducida**: diálogos ramificados con Yarn, opciones, variables, el bucle IsWaiting | 1 |
| 20 | [SNAP — datos y formatos (guía ES)](./20%20-%20SNAP%20-%20datos%20y%20formatos%20%28gu%C3%ADa%20en%20espa%C3%B1ol%29.md) | **Guía traducida**: serializar structs a/desde JSON, CSV, YAML, XML, MessagePack. API verificada | 1 |
| 21 | [Vinyl — audio avanzado (guía ES)](./21%20-%20Vinyl%20-%20audio%20avanzado%20%28gu%C3%ADa%20en%20espa%C3%B1ol%29.md) | **Guía traducida**: mezclador por etiqueta, fundidos, ducking, sincronía con el beat. API verificada | 1 |
| 23 | [Arte generado por IA](./23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md) | 🆕 Qué sirve hoy (referencia, upscalers, texturas) y qué no (consistencia de personaje, animación, pixel art real); técnicas de consistencia de estilo (seed, ControlNet, LoRA); estado legal verificado (U.S. Copyright Office, Content Survey de Steam, AI Disclosure de itch.io) | — |
| 24 | [Logotipo, icono del ejecutable y capsule de tienda](./24%20-%20Logotipo%2C%20icono%20del%20ejecutable%20y%20capsule%20de%20tienda.md) | 🆕 Logotipo con `codex exec`+`gpt-image-2`; icono del ejecutable por plataforma con `resourcetool options set` (hallazgo verificado, incluido un bug real del `.ico` de Windows) y la técnica squircle de macOS; capsule de Steam e itch.io sin artista | — |

### Documentos complementarios en `05 - Referencia`

| Archivo | Contenido |
|---|---|
| [01 — Tutoriales oficiales](../05%20-%20Referencia/01%20-%20Tutoriales%20oficiales.md) | Catálogo completo de los **106 tutoriales oficiales** con nivel y sabor, 6 rutas de aprendizaje ordenadas y las 7 páginas de la Quick Start Guide |
| [02 — Publicar y exportar](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md) | Publicación por plataforma (GX.games, Reddit/Devvit, itch.io, Steam, Steam Deck, móviles, consolas, Windows ARM64), licencias y Game Options de release |

---

## Hallazgos importantes (lee esto primero)

### ⚠️ Movimientos y abandonos confirmados

| Elemento | Estado real |
|---|---|
| **Input** | **Se mudó de GitHub a [Codeberg](https://codeberg.org/offalynne/Input).** El repo de GitHub está **archivado** («*Moved to Codeberg 🏔️🚚*»). Versión actual: **10.4.3** (2026-08-19), MIT. |
| **Chorus** | **No existe.** Cero resultados en GitHub y en el manual. El sistema de audio de Juju Adams es **Vinyl** (6.4.2-beta, MIT). |
| **GMLinear** | El repo original (`dicksonlaw583/gmlinear`) está **archivado** (2019, GMS 1.x). El sucesor es **`gmlinear2`**. |
| **YYToolkit** | **No es una librería GML.** Es [AurieFramework/YYToolkit](https://github.com/AurieFramework/YYToolkit), una herramienta de *modding* de juegos ya compilados. |
| **Ugg** (Juju Adams) | **Estancada**: 3 ★, último push 2025-11-13. |
| **Bulb** | Última release **septiembre de 2024**, aunque el repo recibe pushes. |
| **Bento** | Sin releases publicadas: hay que generar el `.yymps` desde el repo. |
| **PlayStation / Nintendo** | **No hay repos públicos**: se distribuyen bajo NDA. |

### ✅ Novedades de 2026 que debes conocer

| Novedad | Enlace |
|---|---|
| **`gm-cli`** — CLI oficial (marzo 2026) | [YoYoGames/gm-cli](https://github.com/YoYoGames/gm-cli) |
| **`extgen`** — generador de extensiones desde un fichero IDL (enero 2026) | [GM-ExtensionGenerator](https://github.com/YoYoGames/GM-ExtensionGenerator) |
| **GMEXT-Photon** — multijugador (julio 2026) | [GMEXT-Photon](https://github.com/YoYoGames/GMEXT-Photon) |
| **GMEXT-LevelPlay** — mediación de anuncios | [GMEXT-LevelPlay](https://github.com/YoYoGames/GMEXT-LevelPlay) |
| **GMEXT-Elements** — multiplataforma | [GMEXT-Elements](https://github.com/YoYoGames/GMEXT-Elements) |
| **GMEXT-Medal** — clips de vídeo (GML puro) | [GMEXT-Medal](https://github.com/YoYoGames/GMEXT-Medal) |
| **GM-OpenAPIGenerator** — cliente REST desde OpenAPI | [GM-OpenAPIGenerator](https://github.com/YoYoGames/GM-OpenAPIGenerator) |
| **Prefabs oficiales** (UI, inventario, minimapa) | [pfb-UserInterface](https://github.com/YoYoGames/pfb-UserInterface) |
| **ImGui sobre GMRT** | [ImGUI-Sample](https://github.com/YoYoGames/ImGUI-Sample) |
| **GM3D-Samples** — ejemplos 3D | [GM3D-Samples](https://github.com/YoYoGames/GM3D-Samples) |
| **GMEXT-PlayAgeSignals / DeclaredAgeRange / GooglePlayIntegrity** — normativa de edad y anti-trampas | ver archivo 03 |

---

## Tabla maestra · Núcleo de la plataforma

| Repo | ★ | Último push | Licencia | Para qué |
|---|---:|---|---|---|
| [YoYoGames/GMRT-Beta](https://github.com/YoYoGames/GMRT-Beta) | 33 | 2026-05-01 | — | Seguimiento y guía del nuevo runtime |
| [YoYoGames/GameMaker-HTML5](https://github.com/YoYoGames/GameMaker-HTML5) | 324 | 2026-08-27 | NOASSERTION | Runtime web |
| [YoYoGames/GameMaker-Bugs](https://github.com/YoYoGames/GameMaker-Bugs) | 82 | 2026-08-27 | — | **Reportar y buscar bugs** |
| [YoYoGames/gm-cli](https://github.com/YoYoGames/gm-cli) | 39 | 2026-08-17 | Apache-2.0 | **CLI oficial** |
| [YoYoGames/GM-TestFramework](https://github.com/YoYoGames/GM-TestFramework) | 25 | 2026-08-25 | NOASSERTION | Tests unitarios |
| [YoYoGames/GM-ExtensionGenerator](https://github.com/YoYoGames/GM-ExtensionGenerator) | 26 | 2026-08-27 | Apache-2.0 | **Crear extensiones nativas** |
| [YoYoGames/GameMaker-Manual](https://github.com/YoYoGames/GameMaker-Manual) | 58 | 2026-08-27 | — | Fuente del manual + 10 traducciones |
| [YoYoGames/GM-OpenAPIGenerator](https://github.com/YoYoGames/GM-OpenAPIGenerator) | 0 | 2026-08-26 | Apache-2.0 | Cliente REST desde OpenAPI |
| [YoYoGames/GM3D-Samples](https://github.com/YoYoGames/GM3D-Samples) | 13 | 2026-08-20 | MIT | Ejemplos 3D |
| [YoYoGames/pfb-UserInterface](https://github.com/YoYoGames/pfb-UserInterface) | 3 | 2026-07-02 | MIT | Prefabs de UI |
| [YoYoGames/ImGUI-Sample](https://github.com/YoYoGames/ImGUI-Sample) | 0 | 2026-07-30 | MIT | Dear ImGui sobre GMRT |

---

## Tabla maestra · Librerías de la comunidad

### ⭐ El «kit básico» (todo MIT, todo activo, todo para LTS 2026)

| Librería | Autor | Enlace | ★ | Versión | Resuelve |
|---|---|---|---:|---|---|
| **Input** | Juju Adams + Alynne Keith | [Codeberg](https://codeberg.org/offalynne/Input) | 312 (GH) / 16 (CB) | **10.4.3** | Entrada multiplataforma, remapeo, multijugador local |
| **Scribble** | Juju Adams | [GitHub](https://github.com/JujuAdams/Scribble) | 415 | 9.7.3 | Texto con efectos, i18n, BiDi |
| **Chatterbox** | Juju Adams | [GitHub](https://github.com/JujuAdams/Chatterbox) | 175 | 4.0.0 | Diálogo ramificado |
| **Vinyl** | Juju Adams | [GitHub](https://github.com/JujuAdams/Vinyl) | 61 | 6.4.2-beta | Audio: patrones, ducking, BPM |
| **GMRoomLoader** | GlebTsereteli | [GitHub](https://github.com/GlebTsereteli/GMRoomLoader) | 128 | 3.1.1 | Rooms modulares, procedural, chunking |
| **Snitch** | Juju Adams | [GitHub](https://github.com/JujuAdams/Snitch) | 39 | 5.0.1 | Logs y crashes (+Sentry) |
| **db** | Juju Adams | [GitHub](https://github.com/JujuAdams/db) | 22 | 3.0.0 | Guardado robusto sobre JSON |
| **iota** | Juju Adams | [GitHub](https://github.com/JujuAdams/iota) | 48 | 4.0.1 | Delta time y dilatación temporal |
| **STANNcam** | stann-co | [GitHub](https://github.com/stann-co/STANNcam) | 43 | 2.4.0 | Cámara *pixel-perfect* |
| **GMEdit** | YellowAfterlife | [GitHub](https://github.com/YellowAfterlife/GMEdit) | 369 | — | Editor de código externo |

### Resto de librerías activas

| Librería | Enlace | ★ | Licencia | Para qué |
|---|---|---:|---|---|
| Bulb | [JujuAdams/Bulb](https://github.com/JujuAdams/Bulb) | 107 | MIT | Luces y sombras 2D |
| BBMOD | [blueburncz/BBMOD](https://github.com/blueburncz/BBMOD) | 119 | MIT | Motor 3D |
| YUI | [shdwcat/YUI](https://github.com/shdwcat/YUI) | 66 | MIT | UI declarativa con live reload |
| Bonk | [JujuAdams/Bonk](https://github.com/JujuAdams/Bonk) | 15 | MIT | Colisiones 3D |
| Bento | [JujuAdams/Bento](https://github.com/JujuAdams/Bento) | 53 | MIT | UI multiplataforma |
| lexicon | [tabularelf/lexicon](https://github.com/tabularelf/lexicon) | 52 | MIT | Localización |
| DoLater | [JujuAdams/DoLater](https://github.com/JujuAdams/DoLater) | 45 | MIT | `call_later()` con argumentos |
| Emu | [DragoniteSpam/Emu](https://github.com/DragoniteSpam/Emu) | 43 | MIT (desde 2020) | UI para herramientas |
| LimeUI | [Limekys/LimeUI](https://github.com/Limekys/LimeUI) | 36 | MIT | UI con flexpanels |
| SNAP | [JujuAdams/SNAP](https://github.com/JujuAdams/SNAP) | 100 | MIT | Conversores de datos |
| Dynamo | [JujuAdams/Dynamo](https://github.com/JujuAdams/Dynamo) | 36 | MIT | Carga dinámica de datos |
| Elephant | [JujuAdams/Elephant](https://github.com/JujuAdams/Elephant) | 24 | MIT | Serialización avanzada |
| Collage | [tabularelf/Collage](https://github.com/tabularelf/Collage) | 29 | MIT | Texture pages en runtime |
| GMUI | [erkan612/GMUI](https://github.com/erkan612/GMUI) | 30 | MIT | UI en modo inmediato |
| ScribbleJunior | [JujuAdams/ScribbleJunior](https://github.com/JujuAdams/ScribbleJunior) | 25 | MIT | Texto ligero |
| Figgy | [GlebTsereteli/Figgy](https://github.com/GlebTsereteli/Figgy) | 27 | MIT | Configs en vivo |
| Lookout | [GlebTsereteli/Lookout](https://github.com/GlebTsereteli/Lookout) | 21 | MIT | Overlays de depuración |
| PictureFrame | [JujuAdams/PictureFrame](https://github.com/JujuAdams/PictureFrame) | 10 | MIT | Render pipeline |
| Splat | [JujuAdams/Splat](https://github.com/JujuAdams/Splat) | 5 | MIT | Caché de sprites |
| Crochet | [FaultyFunctions/Crochet](https://github.com/FaultyFunctions/Crochet) | 121 | MIT | Editor visual de diálogo |
| Unic | [TabularElf/Unic](https://github.com/TabularElf/Unic) | 8 | MIT | Estándar Unicode |
| LineAudio | [WangleLine/LineAudio](https://github.com/WangleLine/LineAudio) | 5 | MIT | Motor de audio pequeño |
| gmlinear2 | [dicksonlaw583/gmlinear2](https://github.com/dicksonlaw583/gmlinear2) | 17 | MIT | Matrices y vectores |
| GML-OOP | [Mtax-Development/GML-OOP](https://github.com/Mtax-Development/GML-OOP) | 34 | ⚠️ NOASSERTION | Constructores sobre GML |
| gmlscripts.com | [gmlscripts/scripts](https://github.com/gmlscripts/scripts) | 85 | ⚠️ NOASSERTION | Colección histórica de scripts |

---

## Tabla maestra · Extensiones oficiales más usadas

| Extensión | Plataformas | ★ |
|---|---|---:|
| [GMEXT-Steamworks](https://github.com/YoYoGames/GMEXT-Steamworks) | Win/mac/Linux | 123 |
| [GMEXT-FMOD](https://github.com/YoYoGames/GMEXT-FMOD) | Escritorio, móvil, consolas | 74 |
| [GMEXT-GDK](https://github.com/YoYoGames/GMEXT-GDK) | Windows / Xbox | 20 |
| [GMEXT-Firebase](https://github.com/YoYoGames/GMEXT-Firebase) | Android, iOS, Web | 20 |
| [GMEXT-EpicOnlineServices](https://github.com/YoYoGames/GMEXT-EpicOnlineServices) | Win/mac | 16 |
| [GMEXT-AdMob](https://github.com/YoYoGames/GMEXT-AdMob) | Android, iOS | 14 |
| [GMEXT-Discord](https://github.com/YoYoGames/GMEXT-Discord) | Win/mac/Linux/iOS/Android | 13 |
| [GMEXT-MobileUtils](https://github.com/YoYoGames/GMEXT-MobileUtils) | Android, iOS | 13 |
| [GMEXT-GooglePlayBilling](https://github.com/YoYoGames/GMEXT-GooglePlayBilling) | Android | 12 |
| [GMEXT-mod.io](https://github.com/YoYoGames/GMEXT-mod.io) | Todas (REST) | 12 |
| [GMEXT-GooglePlayServices](https://github.com/YoYoGames/GMEXT-GooglePlayServices) | Android | 10 |
| [GMEXT-GOG](https://github.com/YoYoGames/GMEXT-GOG) | Win/mac | 10 |
| [GMEXT-Photon](https://github.com/YoYoGames/GMEXT-Photon) | Win/mac/Linux/Android/iOS | 8 |
| [GMEXT-Elements](https://github.com/YoYoGames/GMEXT-Elements) | Todas | 7 |
| [GMEXT-GameCenter](https://github.com/YoYoGames/GMEXT-GameCenter) | iOS, macOS | 7 |
| [GMEXT-WebView](https://github.com/YoYoGames/GMEXT-WebView) | Móvil + escritorio | 7 |
| [GMEXT-MobileReview](https://github.com/YoYoGames/GMEXT-MobileReview) | Android, iOS | 7 |

> Las **44** extensiones completas, con plataformas y licencia, están en el [archivo 03](./03%20-%20Extensiones%20oficiales%20y%20de%20terceros.md).

---

## Tabla maestra · Proyectos para estudiar

### Frameworks y herramientas (los mejor valorados)

| Proyecto | ★ | Licencia | Tipo |
|---|---:|---|---|
| [Pixel Composer](https://github.com/Ttanasart-pt/Pixel-Composer) | **1353** | MIT | Editor de VFX por nodos |
| [Note Block Studio](https://github.com/OpenNBS/NoteBlockStudio) | **1013** | MIT | Creador de música |
| [Mine-imator](https://github.com/stuffbydavid/Mine-imator) | 248 | ⚠️ sin licencia | Creador de películas 3D |
| [Orbinaut Framework](https://github.com/TrianglyRU/OrbinautFramework) | 125 | ⚠️ sin licencia | Plataformas Sonic (precisión) |
| [Gang Garrison 2](https://github.com/Gang-Garrison-2/Gang-Garrison-2) | 119 | MPL 2.0 | **Multijugador con rollback** |
| [Harmony Framework](https://github.com/UltraRing/Harmony-Framework) | 81 | **MIT** | Plataformas Sonic |
| [Megamix Engine](https://github.com/MegamixEngine/MegamixEngine) | 50 | ⚠️ sin licencia | Plataformas Mega Man |
| [DyNode](https://github.com/NordLandeW/DyNode) | 30 | MIT | Editor de charts |

### Juegos completos

| Proyecto | ★ | Licencia | Género | 🚩 |
|---|---:|---|---|:--:|
| [Spelunky Classic HD](https://github.com/yancharkin/SpelunkyClassicHD) | 219 | NOASSERTION | Plataformas / roguelite | |
| [FVM-Reborn](https://github.com/Spring-SG/FVM-Reborn) | 173 | GPL-3.0 | — | |
| [Undertale Engine](https://github.com/TML233/UndertaleEngine) | 181 | MIT | RPG | 🚩 |
| [Chapter Master](https://github.com/Adeptus-Dominus/ChapterMaster) | 72 | ⚠️ sin licencia | Estrategia | |
| [tldr-engine](https://github.com/tweenko/tldr-engine) | 82 | MIT | RPG | 🚩 |
| [Nuclear Throne rebuild](https://github.com/toarch7/nt-recreated-public) | 82 | GPL-3.0 | Roguelite | 🚩 |
| [HotlineMiami.gmx](https://github.com/Pi0h1/HotlineMiami.gmx) | 82 | ⚠️ sin licencia | Acción top-down | 🚩 |
| [Kirby ~ Soft & Wet](https://github.com/MegaStrimp/Kirby-Soft-and-Wet) | 63 | ⚠️ sin licencia | Minijuego | 🚩 |
| [Pizza Tower EXtracted](https://github.com/setupwitch/Pizza-Tower-EXtracted) | 25 | ⚠️ sin licencia | Plataformas | 🚩 |
| [AM2R: ReSplashed](https://github.com/AbyssalCreature/AM2R-Re-Splashed) | 22 | NOASSERTION | Metroidvania | 🚩 |

🚩 = **reconstrucción de un juego comercial**: estudiar sí, reutilizar activos no.

---

## Tabla maestra · Plantillas oficiales

**18 de juego · 12 de Live Wallpaper · 1 GameStrip.**

| Para empezar | Para un género concreto |
|---|---|
| **Space Rocks** ⭐ | Platformer · Scrolling Shooter · Twin Stick Shooter |
| **Blank Pixel Game** (pixel art) | Tower Defense · Endless Runner · Survivor Game |
| **Hero's Trail** (GML Visual) | Idle Game · Match 3 · Card Game · Brick Breaker · Puzzle Slider |
| | Arcade Action · Fire Jump · Cover Assault |

Comando (verificado):

```sh
gm-cli init --no-interactive -n mi-juego -t "Space Rocks" --ai --actions --toolchain GMS2@2026.0.0.23
```

> ⚠️ Las plantillas que usan **prefabs** (p. ej. *Platformer Template*) fallan con `ProjectTool PREFABS RESTORE exited with code 1`. **No es un problema de versión: sigue fallando en 2.3.0**, la última publicada (reverificado 02-09-2026). Detalle y alternativas en [`07 · 13` §12](./13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md#12-bis-bug-conocido-las-plantillas-con-prefabs-fallan-al-crear-el-proyecto).

---

## Scripts incluidos (archivo 05)

| # | Script | ¿Nativo en GameMaker? |
|---:|---|---|
| 1 | Funciones de easing | ❌ No (lo más cerca: `animcurve_*`, que requiere assets) |
| 2 | Sistema de tweens | ❌ No |
| 3 | Rejilla con structs | ⚠️ Parcial (`ds_grid_*` existe, pero hay que liberarlo a mano y no se serializa) |
| 4 | Pathfinding A* | ⚠️ Parcial (`mp_grid_path()` existe, pero exige un asset *path* y no admite costes por celda) |
| 5 | Máquina de estados | ❌ No |
| 6 | Object pooling | ❌ No |
| 7 | Cámara con shake | ⚠️ Parcial (las cámaras sí; el shake no) |
| 8 | Guardado con structs | ⚠️ Parcial (`json_stringify`/`json_parse` sí; la migración de esquema no) |
| 9 | Input buffering | ❌ No |
| 10 | Sistema de diálogo | ❌ No (para algo serio: **Chatterbox**) |
| 11 | Ruido Perlin | ❌ **No** (`gm-cli manual read "noise"` → *«No results found»*) |
| 12 | Utilidades de tilemap | ⚠️ Envolturas sobre `tilemap_get`/`tilemap_set` |

**Confirmado nativo (no reimplementar):** `lerp`, `clamp`, `animcurve_*`, `ds_grid_*`, `ds_priority_*`, `mp_grid_path`, `tilemap_get/set`, `camera_create/destroy`, `instance_create_layer`, `instance_deactivate_layer`, `json_stringify`, `json_parse`, `struct_get_names`.

---

## Auditoría de verificación

### Metodología

1. **API de GitHub** (`gh api`) para metadatos de cada repositorio: estrellas, último *push*, licencia SPDX, estado de archivado.
2. **API de Codeberg** para Input (licencia, releases, scripts).
3. **Lectura de READMEs** para descripción y plataformas declaradas.
4. **Lectura del código fuente** (`.gml`) para obtener firmas reales de funciones antes de escribir ejemplos.
5. **`gm-cli manual read`** para comprobar qué funciones ya trae GameMaker.
6. **Creación de proyectos reales** con `gm-cli init` para documentar la estructura generada.

### Cifras

| Concepto | Cantidad |
|---|---:|
| Repositorios consultados vía API | **~183** |
| Repositorios documentados individualmente (con licencia + estado) | **~150** |
| Extensiones `GMEXT-*` catalogadas | **44** |
| Librerías de comunidad con licencia comprobada | **~55** |
| Proyectos de ejemplo revisados | **~30** |
| Plantillas oficiales listadas | **31** |
| Scripts GML escritos y comentados | **12** |

### ⚠️ Repositorios abandonados o inactivos

| Repo | Último push | Nota |
|---|---|---|
| [YoYoGames/YourWorld](https://github.com/YoYoGames/YourWorld) | **2017-05-04** | Era GameMaker: Studio |
| [messhof/Input-Dog](https://github.com/messhof/Input-Dog) | **2016-05-19** | Abandonada |
| [YoYoGames/dpdeploy](https://github.com/YoYoGames/dpdeploy) | **2020-03-16** | Abandonado |
| `YoYoGames/GMS_Language_*` (7 repos) | **2021** | Sustituidos por `IDE_Localisation_*` |
| [YoYoGames/3D-2D](https://github.com/YoYoGames/3D-2D) | **2023-03-27** | Sustituido por GM3D-Samples |
| [YoYoGames/GameMakerStudio_ExtensionExample](https://github.com/YoYoGames/GameMakerStudio_ExtensionExample) | **2023-03-29** | Obsoleto → usar `extgen` |
| [dicksonlaw583/gmlinear](https://github.com/dicksonlaw583/gmlinear) | **2019** | **Archivado** (GMS 1.x) |
| [YoYoGames/Guides](https://github.com/YoYoGames/Guides) | 2024-08-20 | Inactivo, contenido aún válido |
| [tabularelf/Sonus](https://github.com/tabularelf/Sonus) | 2024-05-26 | Inactiva |
| [evolutionleo/SimpleUI](https://github.com/evolutionleo/SimpleUI) | 2024-05-07 | Inactiva |
| [danielpancake/gmdialogue](https://github.com/danielpancake/gmdialogue) | 2024-06-10 | Inactiva + **sin licencia** |
| [1pxlchibs/PXLUI](https://github.com/1pxlchibs/PXLUI) | 2024-06-25 | Inactiva |
| [gl326/bard-audio](https://github.com/gl326/bard-audio) | 2024-09-16 | Inactiva |
| [JujuAdams/Ugg](https://github.com/JujuAdams/Ugg) | 2025-11-13 | Estancada (3 ★) |
| [offalynne/Input](https://github.com/offalynne/Input) | 2026-01-30 | **Archivado** → Codeberg |

### 🚫 No verificables / inexistentes

| Elemento | Resultado |
|---|---|
| **Chorus** | **No existe.** Ni en GitHub ni en el manual. Cero resultados. |
| **Extensiones de consola** (PlayStation, Nintendo Switch) | **No hay repos públicos.** Distribución bajo NDA. |
| **YYToolkit como librería GML** | Existe, pero es una herramienta de *modding* externo, no una librería importable. |
| **GMEdit en releases de GitHub** | No tiene releases (404). Los binarios se publican en [itch.io](https://yellowafterlife.itch.io/gmedit). |
| **Bento / pfb-\* / varias `GMEXT-*`** | Sin releases publicadas: hay que generar el `.yymps` desde el repositorio. |
| **Plataforma declarada de 8 extensiones** | No aparece literalmente en el README; se ha inferido y está marcado en el archivo 03. |

### ⚠️ Licencias que requieren revisión antes de uso comercial

`NOASSERTION` o sin licencia en: la mayoría de las `GMEXT-*` · `gmlscripts/scripts` · `PixelatedPope/HelpfulGMLScripts` · `Mtax-Development/GML-OOP` · `JujuAdams/Hotglue` · `JujuAdams/PNGEncoder` · `JujuAdams/Konstants` · `TrianglyRU/OrbinautFramework` · `MegamixEngine` · `Mine-imator` · todos los proyectos marcados 🚩. `DragoniteSpam/Emu` **no** entra en esta lista: es MIT desde 2020 (verificado 2026-09-07), pese a que estuvo marcada como «sin licencia» en versiones anteriores de este documento.

**GPL-3.0 (contagiosa):** `Spring-SG/FVM-Reborn` · `toarch7/nt-recreated-public`.

---

## Tabla maestra · Comunidad, aprendizaje y herramientas (archivos 07–14)

### Dónde preguntar y seguir

| Recurso | Enlace |
|---|---|
| Foro oficial | <https://forum.gamemaker.io/> |
| Nuevos mensajes del foro | <https://forum.gamemaker.io/index.php?whats-new/posts/> |
| Feed RSS del foro | <https://forum.gamemaker.io/index.php?forums/-/index.rss> |
| Web oficial | <https://gamemaker.io/> |
| Manual | <https://manual.gamemaker.io/> |
| Release notes | <https://releases.gamemaker.io/> |
| Centro de ayuda | <https://gamemaker.io/en/help> |
| Rastreador de bugs | <https://github.com/YoYoGames/GameMaker-Bugs> |
| **Roadmap público** | <https://github.com/orgs/YoYoGames/projects/17/views/48> |

### itch.io y jams

| Recurso | Enlace | Estado |
|---|---|---|
| itch.io | <https://itch.io/> | ✅ |
| Jams de itch.io | <https://itch.io/jams> | ✅ |
| butler (docs) | <https://itch.io/docs/butler/> | ✅ |
| **gm(48)** | <https://gm48.net/> | ✅ |
| gm(48) · calendario | <https://gm48.net/game-jam-schedule> | ✅ |
| gm(48) · proyectos open source | <https://gm48.net/open-source-gamemaker-projects> | ✅ |
| GMTK Game Jam (oficial) | <https://gmtkgamejam.com/> | 🔴 **no responde** (500 / timeout, comprobado 07-09-2026); usa la edición en itch.io de abajo o <https://gamemakerstoolkit.com/jam/> |
| GMTK Game Jam 2026 | <https://itch.io/jam/gmtk-jam-2026> | ✅ finalizada |
| Ludum Dare | <https://ludumdare.com/> | ✅ (fin anunciado en oct 2028) |
| ~~ldjam.com~~ | ~~<https://ldjam.com>~~ | ❌ **no responde** |
| GMC Jam (foro) | <https://forum.gamemaker.io/index.php?forums/gmc-jam.9/> | ✅ |
| Asset Bundles oficiales | <https://gamemaker.io/en/bundles> | ✅ |
| Prefab Library (manual) | <https://manual.gamemaker.io/lts/en/IDE_Tools/Prefab_Library.htm> | ✅ |
| Juegos made with GameMaker | <https://itch.io/games/made-with-gamemaker> | ✅ |
| Assets tag GameMaker | <https://itch.io/game-assets/tag-gamemaker> | ✅ |
| Herramientas tag GameMaker | <https://itch.io/tools/tag-gamemaker> | ✅ |
| ~~itch.io/jams/tag-gamemaker~~ | ~~<https://itch.io/jams/tag-gamemaker>~~ | ❌ **404** |

### Sobre IA (veredicto del archivo 14)

- **El motor NO tiene funciones de IA.**
- **`GMEXT-MLKit`** es la única IA «de verdad» que publica YoYoGames: traducción e identificación de idioma **en el dispositivo**, Android e iOS.
- El andamiaje `--ai` de `gm-cli init` **sí** funciona y es útil: genera `AGENTS.md`, `CLAUDE.md`, `.claude/` y `.mcp.json` con el servidor MCP `gamemaker-resource-tool`.

---

## Puntos de entrada rápida

| Necesito… | Voy a… |
|---|---|
| …crear un juego ahora | [Plantillas y starters](./06%20-%20Plantillas%20y%20starters.md) → `gm-cli init` |
| …saber si algo es un bug conocido | [GameMaker-Bugs](https://github.com/YoYoGames/GameMaker-Bugs) |
| …probar el nuevo runtime | [GMRT-Beta](https://github.com/YoYoGames/GMRT-Beta) |
| …compilar sin IDE / en CI | [gm-cli](https://github.com/YoYoGames/gm-cli) |
| …input, texto, audio, guardado | [Librerías de la comunidad](./02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md) |
| …publicar en Steam / móvil / consola | [Extensiones](./03%20-%20Extensiones%20oficiales%20y%20de%20terceros.md) |
| …envolver una librería nativa | [GM-ExtensionGenerator](https://github.com/YoYoGames/GM-ExtensionGenerator) |
| …aprender de código real | [Proyectos de ejemplo](./04%20-%20Proyectos%20de%20ejemplo%20para%20estudiar.md) |
| …un trozo de código concreto | [Scripts y utilidades GML](./05%20-%20Scripts%20y%20utilidades%20GML.md) |
| …usar la línea de comandos a fondo | [GM CLI](./13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md) |
| …preguntar algo / encontrar comunidad | [Comunidades](./10%20-%20Comunidades%20y%20dónde%20preguntar.md) |
| …buscar en el foro oficial | [Foro oficial](./07%20-%20Foro%20oficial%20-%20hilos%20clave.md) |
| …publicar en itch.io o una jam | [itch.io](./08%20-%20itch.io%20-%20jams,%20assets%20y%20juegos.md) |
| …assets gráficos, de audio o fuentes | [Asset packs](./09%20-%20Asset%20packs%20y%20recursos%20gráficos.md) |
| …seguir blogs y novedades | [Blogs y newsletters](./11%20-%20Blogs,%20newsletters%20y%20podcasts.md) |
| …un curso o un libro | [Aprendizaje estructurado](./12%20-%20Aprendizaje%20estructurado%20-%20cursos%20de%20pago%20y%20libros.md) |
| …saber qué hay de IA | [IA y GameMaker](./14%20-%20IA%20y%20GameMaker.md) |
