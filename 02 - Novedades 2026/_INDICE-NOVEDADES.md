# Índice — Novedades de GameMaker 2026

> Documentación de referencia personal sobre **GameMaker LTS 2026.0**, el **runtime GMRT** y el roadmap 2026–2028.
> Generado en **agosto de 2026**. Todo en español, archivos en UTF-8.

---

## Snapshot de versiones al generar este índice

| Concepto | Versión | Fecha |
|---|---|---|
| **LTS estable** | 2026.0.0 Minor Update 1 — IDE **2026.0.0.16**, runtime **GMS2 RT 23** | 27/05/2026 |
| **Beta más reciente** | 2026.100.0 **Release 5** — IDE **1139**, GMS2 RT **1090** | 27/08/2026 |
| **GMRT más reciente** | **0.21.0** | julio 2026 |
| **GMRT anterior** | 0.20.0 | junio 2026 |

---

## Tabla de contenidos

| # | Documento | Qué cubre | Prioridad |
|---|---|---|---|
| 01 | [Resumen LTS 2026.0](./01%20-%20Resumen%20LTS%202026.0.md) | Qué es LTS, ciclo de vida 2026.0 → 2026.4 (Q1 2028), qué pasa con el runtime GMS2 (*feature complete*), novedades de IDE y runtime agrupadas por categoría, plataformas nuevas, checklist de migración | ⭐ Empieza aquí |
| 02 | [Cambios en GML 2026](./02%20-%20Cambios%20en%20GML%202026.md) | **Handles** (reemplazan a los IDs numéricos), comprobación de tipos, JSON, template strings, `string_ext()`, structs y arrays, colisiones (bbox precisos, tilemaps y arrays), descarte de assets + `MarkTagAsUsed`, Deprecated Behaviours, literales. Con ANTES/DESPUÉS | 🔴 **Crítico** |
| 03 | [GMRT — El nuevo runtime](./03%20-%20GMRT%20-%20El%20nuevo%20runtime.md) | Qué es GMRT (Cronus), arquitectura (CMake/LLVM/Clang, Dawn + SDL2), instalación por Package Manager (dotnet 8, emsdk), sección "Changes to GML", estado 0.20 y 0.21, incompatibilidades, cuándo usarlo y cuándo NO | ⭐ Estratégico |
| 04 | [UI Layers y Flexpanels](./04%20-%20UI%20Layers%20y%20Flexpanels.md) | UI layers globales, Flexpanels (Yoga/flexbox), `layer_get_flexpanel_node()`, `layer_get_type()`, `on_ui_layer`, coordenadas GUI, orden de dibujado, receta para un HUD responsive | ⭐ Muy útil |
| 05 | [Sistema de partículas nuevo](./05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md) | Editor de partículas, asset Particle System, presets y biblioteca, `particle_add()`/`particle_delete()`, `part_emitter_delay()`/`part_emitter_interval()`, cuándo usar cada sistema | Medio |
| 06 | [Gráficos: SVG, SDF, FX y superficies](./06%20-%20Gr%C3%A1ficos%20-%20SVG,%20SDF,%20FX%20y%20superficies.md) | Sprites SVG y `vector_sprite_cache_*`, fuentes SDF y efectos de fuente, FX nuevos (Glow, Recursive Blur, Drop Shadow…), formatos de superficie (HDR, máscaras), `texturegroup_add()`, compresión GPU, `sphere_is_visible()` | Alto |
| 07 | [Audio: buses y efectos](./07%20-%20Audio%20-%20buses%20y%20efectos.md) | `audio_play_sound()` con gain/offset/pitch/listener mask, `audio_play_sound_ext()` con struct, Audio Loop Points, los 12 efectos y cómo rutearlos por buses, evento Audio Playback Ended | Alto |
| 08 | [Package Manager y Prefabs](./08%20-%20Package%20Manager%20y%20Prefabs.md) | Cómo funciona el Package Manager, sources, notificaciones, qué son los Prefabs y las Collections, sintaxis `::paquete-version::asset`, Customise vs Duplicate, cómo instalar GMRT | Alto |
| 09 | [Code Editor 2 y Feather](./09%20-%20Code%20Editor%202%20y%20Feather.md) | CE2 (eventos unificados, split views, cómo activarlo), Feather activado por defecto, renombrado de tipos, directivas con `in`, struct shorthand, colores CSS, literales binarios y guiones bajos | Medio |
| 10 | [Futuro: roadmap 2026–2028](./10%20-%20Futuro%20-%20roadmap%202026-2028.md) | Calendario LTS, plugins de IDE, GMRT fuera de Beta, JavaScript (Q2) / TypeScript (Q3) / C# (Q4), mejoras 3D, Extension Generator, extensiones nuevas, GM CLI, rediseño del Room Editor | ⭐ Estratégico |

---

## Orden de lectura recomendado

```
1. 01 - Resumen LTS 2026.0        → panorama general y ciclo de vida
2. 02 - Cambios en GML 2026       → lo que te va a romper el código  ← IMPRESCINDIBLE
3. 10 - Futuro - roadmap          → hacia dónde va GameMaker
4. 03 - GMRT                      → el runtime que viene
5. 04 - UI Layers y Flexpanels    → la forma nueva de hacer interfaces
6. 06, 07                         → gráficos y audio según necesidad
7. 05, 08, 09                     → consulta puntual
```

---

## Los 10 cambios que más te van a afectar

1. **Los Handles sustituyen a los IDs numéricos.** No puedes incrementar un ID de asset; las funciones validan tipos. → Doc 02
2. **El runtime GMS2 está *feature complete*.** Lo nuevo va a GMRT. → Docs 01 y 03
3. **UI Layers y Flexpanels**: se acabó el Draw GUI para HUDs y menús. → Doc 04
4. **Colisiones con bounding boxes precisos e inclusivos**; hay modo de compatibilidad. → Doc 02
5. **Descarte automático de assets sin referenciar**: puede romper carga dinámica. → Doc 02
6. **Feather activado por defecto** y Code Editor 2 disponible (opt-in). → Doc 09
7. **Prefabs y Package Manager**: la IDE se vuelve modular. → Doc 08
8. **Nuevos targets**: Nintendo Switch 2, Reddit (Devvit), Game Strips y Live Wallpapers en GX.games. → Doc 01
9. **Buses y efectos de audio**, más nuevos argumentos en `audio_play_sound()`. → Doc 07
10. **Betas continuas** durante todo el ciclo LTS26. → Docs 01 y 10

---

## Fuentes primarias

### Blogs oficiales

| Fuente | URL |
|---|---|
| GameMaker LTS 2026.0: New Features, GMRT and Much More (21/05/2026) | https://gamemaker.io/en/blog/lts-2026-release |
| GameMaker Update Spring 2026: LTS Roadmap, GMRT, and the Future (30/04/2026) | https://gamemaker.io/en/blog/update-spring-2026 |

### Release notes

| Fuente | URL |
|---|---|
| Índice de todas las versiones | https://releases.gamemaker.io/ |
| Release notes completos de 2026.0.0 | https://releases.gamemaker.io/release-notes/2026/0 |
| Release notes de la Beta 2026.100 | https://releases.gamemaker.io/release-notes/2026/100 |
| Release notes de GMRT 0.20.0 | https://releases.gamemaker.io/release-notes/2026/GMRT_MS_20.html |
| Release notes de GMRT 0.21.0 | https://releases.gamemaker.io/release-notes/2026/GMRT_MS_21 |

### GMRT

| Fuente | URL |
|---|---|
| Intro y setup de GMRT (incluye "Changes to GML") | https://github.com/YoYoGames/GMRT-Beta/blob/main/docs/introduction/GMRT-intro-and-setup-instructions.md |
| Ejemplo GM3D | https://github.com/YoYoGames/GM3D-Samples |
| Ejemplo ImGUI | https://github.com/YoYoGames/ImGUI-Sample |
| GameMaker Source Code License Agreement | https://gamemaker.io/en/legal/sourcecode |

### Manual oficial (LTS)

| Tema | URL |
|---|---|
| Data Types (Handles, int64, literales, colores hex) | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Data_Types.htm |
| `is_handle()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/is_handle.htm |
| `handle_parse()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/handle.htm |
| Variable Functions (structs) | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm |
| Array Functions | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm |
| Strings (template strings, toString) | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/Strings.htm |
| `string_ext()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/string_ext.htm |
| Collisions | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/Collisions.htm |
| Collision Compatibility Mode | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/Collision_Compatibility_Mode.htm |
| `gml_pragma()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/OS_And_Compiler/gml_pragma.htm |
| GMRT (GameMaker Runtime) | https://manual.gamemaker.io/lts/en/Settings/Runner_Details/GMRT_(GameMaker_Runtime).htm |
| UI Layers | https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/UI_Layers.htm |
| UI Layers At Runtime | https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/UI_Layers_At_Runtime.htm |
| Flex Panels | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Flex_Panels/Flex_Panels.htm |
| `layer_get_flexpanel_node()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/UI_Layers/layer_get_flexpanel_node.htm |
| The Particle System Editor | https://manual.gamemaker.io/lts/en/The_Asset_Editors/Particle_Systems.htm |
| `particle_add()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Particles/particle_add.htm |
| `font_enable_sdf()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_enable_sdf.htm |
| `font_enable_effects()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_enable_effects.htm |
| `surface_create()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_create.htm |
| `texturegroup_add()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_add.htm |
| `sphere_is_visible()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Viewports/sphere_is_visible.htm |
| FX Types & Parameters | https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/FX/All_Filter_Effect_Types.htm |
| Audio Effects | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Effects/Audio_Effects.htm |
| `AudioEffectType` Enum | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Effects/AudioEffectType.htm |
| `audio_play_sound()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_play_sound.htm |
| `audio_play_sound_ext()` | https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_play_sound_ext.htm |
| Package Manager | https://manual.gamemaker.io/lts/en/IDE_Tools/Package_Manager.htm |
| Prefab Library | https://manual.gamemaker.io/lts/en/IDE_Tools/Prefab_Library.htm |
| Code Editor 2 (Beta) | https://manual.gamemaker.io/lts/en/The_Asset_Editors/The_Text_Editor.htm |

### Herramientas y repositorios

| Fuente | URL |
|---|---|
| GM CLI (npm) | https://www.npmjs.com/package/@gamemaker/gm-cli |
| Extension Generator | https://github.com/YoYoGames/GM-ExtensionGenerator |
| Compresión de texturas GPU | https://github.com/YoYoGames/GM-GPUTextureCompression |
| Wiki: SDKs requeridos para 2026.0 | https://github.com/YoYoGames/GameMaker-Bugs/wiki/2026.0 |
| Wiki: guía de permisos | https://github.com/YoYoGames/GameMaker-Bugs/wiki/Permissions-Guide |
| Roadmap público | https://roadmap.gamemaker.io |
| Issues y feature requests | https://github.com/YoYoGames/GameMaker-Bugs |
| Yoga (librería de Flexpanels) | https://yogalayout.dev |
| Namazu Elements (multiplayer) | https://github.com/YoYoGames/GMEXT-Elements |
| Colyseus para GameMaker | https://docs.colyseus.io/getting-started/gamemaker |
| Steamworks | https://github.com/YoYoGames/GMEXT-Steamworks |

---

## Datos NO verificados (contrastar antes de fiarte)

Esta es la lista honesta de lo que **no** he podido confirmar contra una fuente primaria. En cada documento afectado está señalado también en su sitio.

1. **Audio Loop Points** — he verificado que la página existe en el manual LTS vía el blog oficial, pero **no** las firmas concretas de sus funciones. Hay un ejemplo marcado como "conceptual" en el documento 07.
2. **`vector_sprite_cache_*`** — he verificado los **nombres** de las nueve funciones contra el índice oficial de *Sprite Manipulation*, pero **no** los tipos de argumento y retorno de cada una por separado.
3. **`sphere_is_visible()`** — función, firma y comportamiento verificados en el manual LTS, pero **no** he podido confirmar en qué versión se introdujo exactamente (el issue de petición es de marzo de 2025). Está presente en LTS 2026.0.
4. **Struct shorthand** (`{ nombre, vida }`) — no he encontrado confirmación en el manual LTS. Está marcado con aviso en el documento 09.
5. **Contenido exacto de "Deprecated Behaviours"** — el blog enumera `instance_change`/`position_change`, colisiones, JSON, conversión string→number, `other` y errores estrictos de audio, y los release notes mencionan adiciones de 2024.8 en adelante. Puede haber más opciones que no aparecen listadas públicamente.
6. **Nombres de los 12 efectos de audio** — el blog enumera 12 nombres y el enum `AudioEffectType` del manual documenta 12 entradas, pero los nombres del blog ("High Pass Filter", "Low Pass Filter"…) son descriptivos; los nombres reales de las constantes son `AudioEffectType.HPF2` y `AudioEffectType.LPF2`. Uso los del manual en el código.
7. **Subcomandos de GM CLI** — verificada su existencia, licencia Apache y URL de npm, pero no la sintaxis de cada subcomando.
8. **`sprite_is_visible` / `handle_type()`** — no existen como tales. No las uses; usa `typeof()`, `is_handle()` o `sphere_is_visible()` según el caso.
9. **Fechas concretas de los futuros releases (2026.1–2026.4)** — son las planificadas en abril de 2026 y pueden moverse.
10. **Disponibilidad del Prefab Builder** — verificado como disponible en la Beta 2026.100 R5, en fase temprana y con bugs de UI conocidos.

---

## Convenciones usadas en esta carpeta

- Todos los archivos en **UTF-8**, español con tildes, eñes y signos de apertura (¿ ¡).
- Los bloques de código van marcados como ```gml y comentados en español.
- Cada documento cierra con una sección **Fuentes** con las URLs originales.
- Lo que no está verificado se marca explícitamente con ⚠️ en el cuerpo del texto y se recopila en la sección anterior.
- Los nombres de funciones, constantes y argumentos se respetan **en inglés** (son la API real); solo las explicaciones y los comentarios están en español.
