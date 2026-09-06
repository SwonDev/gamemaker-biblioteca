# 01 · GitHub — Organización YoYoGames

> Verificado el **31 de agosto de 2026** contra la API de GitHub (`gh api orgs/YoYoGames/repos`) y la web de Codeberg.
> Contexto: GameMaker LTS 2026.0 (IDE 2026.0.0.16 · runtime GMS2 2026.0.0.23) y GMRT en Beta.
> La organización tiene **96 repositorios públicos**, de los cuales **44 son extensiones `GMEXT-*`**.

---

## Índice rápido

| Repo | Estrellas | Último push | Licencia | ¿Te interesa en 2026? |
|---|---:|---|---|---|
| [GameMaker-HTML5](#gamemaker-html5) | 324 | 2026-08-27 | NOASSERTION | Sí (runtime web) |
| [GameMaker-Bugs](#gamemaker-bugs) | 82 | 2026-08-27 | — | **Sí, imprescindible** |
| [gm-cli](#gm-cli) | 39 | 2026-08-17 | Apache-2.0 | **Sí, imprescindible** |
| [GMRT-Beta](#gmrt-beta) | 33 | 2026-05-01 | — | **Sí (el futuro runtime)** |
| [GM-TestFramework](#gm-testframework) | 25 | 2026-08-25 | NOASSERTION | Sí (tests unitarios) |
| [GM-ExtensionGenerator](#gm-extensiongenerator) | 26 | 2026-08-27 | Apache-2.0 | Sí (extensiones nativas) |
| [GameMaker-Manual](#gamemaker-manual-y-traducciones) | 58 | 2026-08-27 | — | Sí (contribuir a la doc) |
| [GMEXT-Steamworks](#3-las-extensiones-gmext-) | 123 | 2026-08-25 | NOASSERTION | Sí (publicar en Steam) |
| [GM3D-Samples](#gm3d-samples) | 13 | 2026-08-20 | MIT | Sí (si haces 3D) |

---

## 1. Repositorios de la plataforma (núcleo)

### GMRT-Beta

- **Enlace:** <https://github.com/YoYoGames/GMRT-Beta>
- **Qué hace:** Seguimiento público del nuevo runtime **GMRT** (nombre en clave «Cronus»), junto con guías de instalación. **No contiene el código del runtime**, solo *issues* y documentación.
- **Documentación incluida:** [`docs/introduction/GMRT-intro-and-setup-instructions.md`](https://github.com/YoYoGames/GMRT-Beta/blob/main/docs/introduction/GMRT-intro-and-setup-instructions.md)
- **Licencia:** sin licencia declarada (es un repo de seguimiento, no de código).
- **Última actividad:** push 2026-05-01 · 33 ★.
- **Relevancia 2026: máxima.** GMRT es el runtime que sustituirá al VM y al YYC.

Lo que dice la guía oficial (resumen verificado):

1. Instalar el IDE de GameMaker.
2. Instalar **.NET 8.0** (dependencia obligatoria).
3. Abrir cualquier proyecto → *Tools > Package Manager* (**GMPM**).
4. Instalar el metapaquete **GMRT - &lt;Plataforma&gt;**.
5. Compilar con el destino **Windows > GMRT VM** (o **GMRT** para compilación nativa).

Detalles técnicos confirmados en la documentación:

- GMRT rompe el runtime monolítico: solo enlaza las librerías que tu proyecto usa (ejecutables más pequeños, a cambio de más tiempo de enlazado).
- Usa **CMake + LLVM/Clang**, **SDL2** y **Dawn** (el proyecto de Google) para el pipeline de render.
- Para **WebAssembly** hace falta además **EMSDK 5.0.4**.
- Limitación actual importante: **el depurador del IDE no está completo** (solo *breakpoints* básicos y «step»).
- Entre los objetivos declarados está «*provide tools to easily convert a native library into an extension using a single IDL declaration file*» — eso es exactamente el [GM-ExtensionGenerator](#gm-extensiongenerator).

> ⚠️ Nota: la propia guía enlaza a `github.com/GMExternal/NewRuntimeBeta/issues`. Esa dirección **redirige a `YoYoGames/GMRT-Beta`** (verificado). Usa siempre la URL canónica de arriba.

### GameMaker-HTML5

- **Enlace:** <https://github.com/YoYoGames/GameMaker-HTML5>
- **Qué hace:** El código del runtime HTML5 de GameMaker. Es el repo más popular de la organización, y el más útil si exportas a web/GX.games y quieres entender (o parchear) el comportamiento del runtime.
- **Rama por defecto:** `develop`.
- **Licencia:** NOASSERTION (licencia propia de YoYoGames, **no es software libre**).
- **Última actividad:** push 2026-08-27 · 324 ★.
- **Relevancia 2026: alta** si exportas a HTML5; baja si solo haces escritorio/consola.

### GameMaker-Bugs

- **Enlace:** <https://github.com/YoYoGames/GameMaker-Bugs>
- **Qué hace:** Seguimiento público de bugs de GameMaker. Es el canal oficial para reportar: tiene plantillas predefinidas y el propio «bug reporter» del menú *Help* del IDE envía ahí los informes.
- **Licencia:** sin licencia declarada.
- **Última actividad:** push 2026-08-27 · 82 ★.
- **Relevancia 2026: imprescindible.** Antes de pelearte con un comportamiento raro, busca aquí. Es la primera parada del flujo de diagnóstico.

### gm-cli

- **Enlace:** <https://github.com/YoYoGames/gm-cli>
- **Qué hace:** Interfaz de línea de comandos oficial. Crea, edita, compila, empaqueta y ejecuta proyectos sin abrir el IDE.
- **Licencia:** Apache-2.0.
- **Última actividad:** push 2026-08-17 · 39 ★. Creado en 2026-03-25, así que es **una herramienta nueva de 2026**.
- **Instalado en este Mac:** versión **2.2.0** (la última publicada es **2.3.0**; actualiza con `npm install -g @gamemaker/gm-cli`).

Comandos (verificados con `gm-cli --help`):

```sh
gm-cli init                 # crea un proyecto nuevo desde plantilla
gm-cli run                  # ejecuta el proyecto
gm-cli compile              # compila
gm-cli package              # empaqueta
gm-cli manual read|open …   # consulta el manual oficial (¡admite --language=es!)
gm-cli resourcetool mcp|eval|repl|script …
gm-cli login <access-key>   # sesión con clave propia (si no, licencia guest)
gm-cli gxgames link|upload|meta|publish …
gm-cli cache info|clean …
```

Puntos clave confirmados:

- `gm-cli init` soporta `--no-interactive`, `-n <nombre>`, `-t <plantilla>`, `--ai/--no-ai` (genera `AGENTS.md`, config MCP, etc.), `--actions/--no-actions` (workflows de GitHub) y `--toolchain` (ej. `GMS2@2024.14.4` o `GMRT@0.18`).
- Las plantillas se descargan de `https://api.gamemaker.io/api/gamemaker/project-templates` (31 plantillas disponibles; ver el archivo `06 - Plantillas y starters.md`).
- `gm-cli resourcetool mcp` expone el proyecto por **MCP** para agentes de IA. El MCP es **por proyecto** (exige un `.yyp`).
- **No hace falta iniciar sesión**: otorga licencia *guest* automáticamente.

### GM-TestFramework

- **Enlace:** <https://github.com/YoYoGames/GM-TestFramework>
- **Qué hace:** El framework de pruebas unitarias que YoYoGames ejecuta internamente en cada build de GameMaker, abierto a la comunidad para que aporte tests.
- **Wiki:** <https://github.com/YoYoGames/GM-TestFramework/wiki>
- **Rama por defecto:** `develop`.
- **Licencia:** NOASSERTION.
- **Última actividad:** push 2026-08-25 · 25 ★.
- **Relevancia 2026: alta.** Es la base sobre la que se construye el testing en GameMaker; aportando tests puedes demostrar bugs y que se arreglen antes del release.

### GM-ExtensionGenerator

- **Enlace:** <https://github.com/YoYoGames/GM-ExtensionGenerator>
- **Qué hace:** Generador de código (**`extgen`**) que produce bindings GML, *glue* C++ nativo, código Android (Java/Kotlin/JNI), iOS/tvOS (ObjC/Swift), consolas (Xbox, PS4, PS5, Switch), proyectos CMake y documentación — todo a partir de **un único fichero de esquema GMIDL**.
- **Licencia:** Apache-2.0.
- **Última actividad:** push 2026-08-27 · 26 ★. Creado en 2026-01-15: **es la herramienta nueva de 2026**.
- **Binarios:** <https://github.com/YoYoGames/GM-ExtensionGenerator/releases/tag/nightly>
- **Requisitos:** .NET 9 SDK · Windows, macOS o Linux.
- **Documentación:** en la Wiki del repo.

```sh
extgen --init ./mi-extension       # crea el esqueleto
extgen --config ./mi-extension/config.json   # genera todo
```

### GameMaker-Manual y traducciones

- **Enlace:** <https://github.com/YoYoGames/GameMaker-Manual> (rama `develop`, 58 ★, push 2026-08-27)
- **Qué hace:** El código fuente del manual oficial. Se puede contribuir con correcciones.
- **Licencia:** sin licencia declarada (contenido documental propietario).

Traducciones mantenidas, **todas con actividad de julio de 2026** (verificado):

| Idioma | Repo | Último push |
|---|---|---|
| Español | [GameMaker-Manual-ES](https://github.com/YoYoGames/GameMaker-Manual-ES) | 2026-07-28 |
| Francés | [GameMaker-Manual-FR](https://github.com/YoYoGames/GameMaker-Manual-FR) | 2026-07-28 |
| Alemán | [GameMaker-Manual-DE](https://github.com/YoYoGames/GameMaker-Manual-DE) | 2026-07-28 |
| Italiano | [GameMaker-Manual-IT](https://github.com/YoYoGames/GameMaker-Manual-IT) | 2026-07-28 |
| Japonés | [GameMaker-Manual-JA](https://github.com/YoYoGames/GameMaker-Manual-JA) | 2026-07-28 |
| Coreano | [GameMaker-Manual-KO](https://github.com/YoYoGames/GameMaker-Manual-KO) | 2026-07-28 |
| Polaco | [GameMaker-Manual-PL](https://github.com/YoYoGames/GameMaker-Manual-PL) | 2026-07-28 |
| Portugués (BR) | [GameMaker-Manual-PT-BR](https://github.com/YoYoGames/GameMaker-Manual-PT-BR) | 2026-07-28 |
| Ruso | [GameMaker-Manual-RU](https://github.com/YoYoGames/GameMaker-Manual-RU) | 2026-07-01 |
| Chino | [GameMaker-Manual-ZH](https://github.com/YoYoGames/GameMaker-Manual-ZH) | 2026-07-28 |

También existen repos de localización del propio IDE (`IDE_Localisation_Spanish`, `_French`, `_German`, `_Italian`, `_Japanese`, `_Korean`, `_Polish`, `_PortugueseBrazilian`, `_Russian`, `_Chinese`), con actividad en abril–julio de 2026.

### GM-OpenAPIGenerator

- **Enlace:** <https://github.com/YoYoGames/GM-OpenAPIGenerator>
- **Qué hace:** Genera código de cliente GML a partir de una especificación **OpenAPI** (REST).
- **Licencia:** Apache-2.0 · push 2026-08-26 · 0 ★.
- **Relevancia 2026:** media-alta si tu juego consume una API REST con muchas rutas. Muy nuevo, así que espera cambios.

---

## 2. Proyectos de ejemplo y prefabs oficiales

| Repo | Qué es | Licencia | Último push | ★ |
|---|---|---|---:|---:|
| [GM3D-Samples](https://github.com/YoYoGames/GM3D-Samples) | Proyectos de ejemplo de **GM3D** (el sistema 3D de GameMaker). Incluye `shaders/`, `scripts/`, `objects/`, `rooms/` y notas | MIT | 2026-08-20 | 13 |
| [pfb-UserInterface](https://github.com/YoYoGames/pfb-UserInterface) | Colección de **prefabs de UI**: Button, Checkbox, Dropdown, Infobox, ProgressBar, ScrollBar, Slider, Spinner, Textbox, Toggle, Slot. Con soporte de localización, prevención de *clickthrough* y escalado de sprites | MIT | 2026-07-02 | 3 |
| [pfb-Inventory](https://github.com/YoYoGames/pfb-Inventory) | Prefab de **sistema de inventario** básico | MIT | 2026-06-03 | 0 |
| [pfb-MiniMap](https://github.com/YoYoGames/pfb-MiniMap) | Prefab de **minimapa** | MIT | 2026-05-12 | 0 |
| [ImGUI-Sample](https://github.com/YoYoGames/ImGUI-Sample) | Demo del **módulo de compatibilidad ImGui de GMRT**: `ImGui` expuesto a GML como clase estática global. Ventanas, *docking*, tablas, gráficos, drag & drop, *draw lists*, multi-selección, TTF y rangos Unicode | MIT | 2026-07-30 | 0 |
| [GM-GPUTextureCompression](https://github.com/YoYoGames/GM-GPUTextureCompression) | Demo de **compresión de texturas en GPU** | Apache-2.0 | 2025-07-14 | 11 |
| [GM-RedditDemo](https://github.com/YoYoGames/GM-RedditDemo) | Demo de integración con **Reddit / Devvit** | Apache-2.0 | 2026-02-09 | 4 |
| [GameMakerRedditTemplate](https://github.com/YoYoGames/GameMakerRedditTemplate) | Plantilla para publicar en Reddit | NOASSERTION | 2026-01-14 | 1 |
| [Guides](https://github.com/YoYoGames/Guides) | Guías para **contribuir** a los repos de GameMaker (manual, extensiones, localización, bugs) | — | 2024-08-20 | 0 |

> **Sobre ImGUI-Sample:** requiere GMRT (proyecto construido contra IDE `2026.0.0.16`). El repo **no incluye la extensión**: `ImGui` lo resuelve el propio GMRT. Todo el módulo es **experimental**.

---

## 3. Las extensiones `GMEXT-*` (44 en total)

Todas siguen el mismo patrón, según sus README: *«repositorio creado para presentar a los usuarios la última versión disponible de la extensión (incluso antes de que se actualice en el marketplace) y ofrecer a la comunidad una vía de contribuir con correcciones y funcionalidades»*.

**Licencia:** la mayoría figura como `NOASSERTION` en GitHub (licencia propia de YoYoGames que hay que leer dentro del repo). Las que sí tienen licencia abierta se marcan explícitamente abajo.

### Plataformas de escritorio y PC

| Repo | Qué hace | Plataformas | Último push | ★ |
|---|---|---|---:|---:|
| [GMEXT-Steamworks](https://github.com/YoYoGames/GMEXT-Steamworks) | Logros, leaderboards, estadísticas, workshop, autenticación **Steam**. La extensión estrella para publicar en Steam | Windows, macOS, Linux | 2026-08-25 | 123 |
| [GMEXT-GDK](https://github.com/YoYoGames/GMEXT-GDK) | Soporte de **GDK** (Microsoft Store y **Xbox Live**) en destino Windows | Windows / Xbox | 2026-08-14 | 20 |
| [GMEXT-EpicOnlineServices](https://github.com/YoYoGames/GMEXT-EpicOnlineServices) | **Epic Online Services**: sesiones, *matchmaking*, logros | Windows, macOS | 2026-08-25 | 16 |
| [GMEXT-GOG](https://github.com/YoYoGames/GMEXT-GOG) | **GOG Galaxy** (logros, estadísticas, *overlay*) | Windows, macOS | 2026-04-24 | 10 |
| [GMEXT-Discord](https://github.com/YoYoGames/GMEXT-Discord) | **Discord Social SDK** / Rich Presence | Windows, macOS, Linux, iOS, Android | 2026-08-25 | 13 |
| [GMEXT-FMOD](https://github.com/YoYoGames/GMEXT-FMOD) | Integración con el motor de audio **FMOD**. Apache-2.0 | Escritorio, móvil y **consolas** | 2026-08-12 | 74 |
| [GMEXT-Photon](https://github.com/YoYoGames/GMEXT-Photon) | **Multijugador en tiempo real**, chat y voz vía Photon Cloud (envuelve el Photon C++ SDK: Realtime/LoadBalancing, Chat, Voice). **Nueva en 2026** | Windows, macOS, Linux, Android, iOS | 2026-08-25 | 8 |
| [GMEXT-mod.io](https://github.com/YoYoGames/GMEXT-mod.io) | **Modding** alojado en mod.io (REST, multiplataforma) | Todas vía REST | 2026-04-24 | 12 |
| [GMEXT-Twitch](https://github.com/YoYoGames/GMEXT-Twitch) | Integración con **Twitch** vía REST. Apache-2.0 | Todas vía REST | 2025-12-29 | 21 |
| [GMEXT-GameJolt](https://github.com/YoYoGames/GMEXT-GameJolt) | API de **GameJolt**. Apache-2.0 | Todas vía REST | 2025-11-20 | 7 |
| [GMEXT-Bluetooth](https://github.com/YoYoGames/GMEXT-Bluetooth) | **Bluetooth** (winrt en Windows 10+) | Windows, macOS, iOS, Android | 2025-06-20 | 8 |
| [GMEXT-WebView](https://github.com/YoYoGames/GMEXT-WebView) | Visor **web** incrustado | Android, iOS, Windows, macOS, Linux | 2026-08-04 | 7 |
| [GMEXT-Interhaptics-Main](https://github.com/YoYoGames/GMEXT-Interhaptics-Main) | **Háptica** (Interhaptics). Apache-2.0 | Windows (más plataformas «más adelante») | 2026-04-24 | 5 |
| [GMEXT-Medal](https://github.com/YoYoGames/GMEXT-Medal) | Reporta eventos a la app **Medal** para guardar clips. **Puro GML**, sin librerías nativas. **Nueva en 2026** | Todas | 2026-08-26 | 0 |
| [GMEXT-Elements](https://github.com/YoYoGames/GMEXT-Elements) | Extensión **Elements** (multiplataforma). **Nueva en 2026** | Todas | 2026-08-26 | 7 |

### Monetización y publicidad

| Repo | Qué hace | Plataformas | Último push | ★ |
|---|---|---|---:|---:|
| [GMEXT-AdMob](https://github.com/YoYoGames/GMEXT-AdMob) | Anuncios de **Google AdMob** (envuelve Mobile Ads SDK: `play-services-ads` 25.4.0 + `user-messaging-platform` 4.x) | Android, iOS | 2026-08-25 | 14 |
| [GMEXT-LevelPlay](https://github.com/YoYoGames/GMEXT-LevelPlay) | **LevelPlay** (mediación de anuncios de ironSource/unity LevelPlay). **Nueva en 2026** | Android, iOS | 2026-08-26 | 0 |
| [GMEXT-IronSource](https://github.com/YoYoGames/GMEXT-IronSource) | ironSource (versión anterior; **LevelPlay es la sucesora**) | Android, iOS | 2025-06-13 | 2 |
| [GMEXT-OperaAds](https://github.com/YoYoGames/GMEXT-OperaAds) | **Opera Ads**. **Nueva en 2026** | Android, iOS | 2026-08-25 | 0 |
| [GMEXT-H5GamesAds](https://github.com/YoYoGames/GMEXT-H5GamesAds) | Anuncios para juegos **HTML5** | HTML5 | 2025-06-20 | 2 |
| [GMEXT-CrazyGames](https://github.com/YoYoGames/GMEXT-CrazyGames) | Publicar en la plataforma **CrazyGames** | HTML5 | 2026-04-24 | 2 |
| [GMEXT-Adjust](https://github.com/YoYoGames/GMEXT-Adjust) | Atribución y analítica **Adjust**. Apache-2.0 | iOS, Android | 2025-08-26 | 1 |

### Pagos (IAP)

| Repo | Qué hace | Plataformas | Último push | ★ |
|---|---|---|---:|---:|
| [GMEXT-AppleIAP](https://github.com/YoYoGames/GMEXT-AppleIAP) | **Compras integradas de Apple**. Apache-2.0 | macOS, iOS/tvOS | 2026-08-25 | 5 |
| [GMEXT-GooglePlayBilling](https://github.com/YoYoGames/GMEXT-GooglePlayBilling) | **Google Play Billing** | Android | 2026-08-28 | 12 |
| [GMEXT-GooglePlayLicensing](https://github.com/YoYoGames/GMEXT-GooglePlayLicensing) | Verificación de licencia (LVL) de Google Play | Android | 2026-05-04 | 5 |
| [GMEXT-GooglePlayPassLicensing](https://github.com/YoYoGames/GMEXT-GooglePlayPassLicensing) | Licencia de **Google Play Pass** | Android | 2026-04-24 | 4 |
| [GMEXT-HuaweiPaidApps](https://github.com/YoYoGames/GMEXT-HuaweiPaidApps) | **Huawei AppGallery**. Apache-2.0 | Android | 2026-06-19 | 1 |

### Backend y analítica

| Repo | Qué hace | Plataformas | Último push | ★ |
|---|---|---|---:|---:|
| [GMEXT-Firebase](https://github.com/YoYoGames/GMEXT-Firebase) | **Firebase**: Analytics, Auth, Firestore, Remote Config, Crashlytics… (SDK nativo en Android/iOS/Web; en el resto, REST) | Android, iOS, Web (+ REST en todas) | 2026-08-27 | 20 |
| [GMEXT-Facebook](https://github.com/YoYoGames/GMEXT-Facebook) | SDK de **Facebook**. Apache-2.0 | Android, iOS, HTML5 | 2026-08-27 | 0 |

### Móvil

| Repo | Qué hace | Plataformas | Último push | ★ |
|---|---|---|---:|---:|
| [GMEXT-MobileUtils](https://github.com/YoYoGames/GMEXT-MobileUtils) | Utilidades móviles (permisos, estado del dispositivo…) | Android, iOS | 2026-08-25 | 13 |
| [GMEXT-GooglePlayServices](https://github.com/YoYoGames/GMEXT-GooglePlayServices) | **Google Play Services** | Android | 2026-08-25 | 10 |
| [GMEXT-GameCenter](https://github.com/YoYoGames/GMEXT-GameCenter) | **Game Center** de Apple (logros, leaderboards) | iOS, macOS | 2026-08-25 | 7 |
| [GMEXT-GoogleSignIn](https://github.com/YoYoGames/GMEXT-GoogleSignIn) | Inicio de sesión con **Google** | Android, iOS/tvOS, HTML5 | 2026-06-30 | 3 |
| [GMEXT-AppleSignIn](https://github.com/YoYoGames/GMEXT-AppleSignIn) | Inicio de sesión con **Apple** | macOS, iOS/tvOS | 2026-06-30 | 2 |
| [GMEXT-InAppUpdate](https://github.com/YoYoGames/GMEXT-InAppUpdate) | **Actualizaciones in-app** de Google Play. Apache-2.0 | Android | 2026-07-31 | 3 |
| [GMEXT-GooglePlayInstant](https://github.com/YoYoGames/GMEXT-GooglePlayInstant) | **Google Play Instant**. Apache-2.0 | Android | 2025-10-01 | 2 |
| [GMEXT-GooglePlayIntegrity](https://github.com/YoYoGames/GMEXT-GooglePlayIntegrity) | **Play Integrity API** (anti-trampas). **Nueva en 2026** | Android | 2026-08-25 | 0 |
| [GMEXT-PlayAgeSignals](https://github.com/YoYoGames/GMEXT-PlayAgeSignals) | Señales de **edad** de Google Play. **Nueva en 2026** | Android | 2026-08-25 | 0 |
| [GMEXT-DeclaredAgeRange](https://github.com/YoYoGames/GMEXT-DeclaredAgeRange) | Rango de edad declarado (normativa de **iOS**). **Nueva en 2026** | iOS | 2026-08-25 | 0 |
| [GMEXT-MLKit](https://github.com/YoYoGames/GMEXT-MLKit) | **ML Kit** de Google: traducción de texto e identificación de idioma en el dispositivo. Apache-2.0 | Android, iOS (en el resto, no-op) | 2026-08-25 | 2 |
| [GMEXT-MobileReview](https://github.com/YoYoGames/GMEXT-MobileReview) | Pide al jugador que valore la app con el flujo **nativo** del sistema | Android, iOS | 2026-08-25 | 7 |
| [GMEXT-AppTrackingTransparency](https://github.com/YoYoGames/GMEXT-AppTrackingTransparency) | **ATT** de Apple. Requisito para que AdMob funcione correctamente | iOS | 2026-06-18 | 3 |

### Web / GX.games / Reddit

| Repo | Qué hace | Plataformas | Último push | ★ |
|---|---|---|---:|---:|
| [GMEXT-GX.games](https://github.com/YoYoGames/GMEXT-GX.games) | Funciones de la plataforma **GX.games** | GX.games | 2025-06-20 | 8 |
| [GMEXT-Reddit](https://github.com/YoYoGames/GMEXT-Reddit) | **Reddit / Devvit**. Apache-2.0. Requiere **node.js** instalado | WASM (GX.games) | 2026-08-14 | 0 |

> ⚠️ **Extensiones de consola (PlayStation, Nintendo Switch):** los repos de consola **no son públicos** en la organización. Se distribuyen bajo NDA a través del programa de desarrolladores de cada fabricante. Si los ves mencionados en foros, desconfía.

---

## 4. Repos abandonados o históricos (verificado)

Estos repos **siguen en la organización pero no deberías usarlos en 2026**:

| Repo | Último push | ★ | Estado |
|---|---:|---:|---|
| [YourWorld](https://github.com/YoYoGames/YourWorld) | 2017-05-04 | 45 | **Abandonado.** Proyecto de mundo *top-down* de la era GameMaker: Studio. Solo valor histórico. |
| [3D-2D](https://github.com/YoYoGames/3D-2D) | 2023-03-27 | 48 | **Abandonado.** Usa [GM3D-Samples](https://github.com/YoYoGames/GM3D-Samples) en su lugar. |
| [GameMakerStudio_ExtensionExample](https://github.com/YoYoGames/GameMakerStudio_ExtensionExample) | 2023-03-29 | 34 | **Obsoleto.** Usa [GM-ExtensionGenerator](https://github.com/YoYoGames/GM-ExtensionGenerator). |
| [Guides](https://github.com/YoYoGames/Guides) | 2024-08-20 | 0 | Prácticamente inactivo, pero el contenido sigue siendo válido como guía de contribución. |
| `GMS_Language_*` (ES, FR, DE, ZH, RU, PT-BR, PL) | 2021 | 0–2 | **Abandonados.** Sustituidos por los repos `IDE_Localisation_*`. |
| `dpdeploy` | 2020-03-16 | 2 | **Abandonado.** |
| `SPIRV-Tools`, `abseil-cpp`, `SDL`, `FNA3D`, `freetype`, `yoga`, `xwin`, `FFmpeg`, `SharpFont`, `spine-runtimes`, `verdaccio` | 2023–2026 | 0–3 | **Forks internos** de dependencias de terceros que GameMaker usa para compilar. No son código que debas importar. |

---

## 5. Dónde mirar primero según tu necesidad

| Necesidad | Repo |
|---|---|
| Algo no funciona y no sé por qué | [GameMaker-Bugs](https://github.com/YoYoGames/GameMaker-Bugs) |
| Quiero compilar sin abrir el IDE / en CI | [gm-cli](https://github.com/YoYoGames/gm-cli) |
| Quiero probar el nuevo runtime | [GMRT-Beta](https://github.com/YoYoGames/GMRT-Beta) |
| Quiero escribir tests | [GM-TestFramework](https://github.com/YoYoGames/GM-TestFramework) |
| Necesito una librería nativa en mi juego | [GM-ExtensionGenerator](https://github.com/YoYoGames/GM-ExtensionGenerator) |
| Quiero publicar en Steam | [GMEXT-Steamworks](https://github.com/YoYoGames/GMEXT-Steamworks) |
| Quiero multijugador | [GMEXT-Photon](https://github.com/YoYoGames/GMEXT-Photon) o [GMEXT-EpicOnlineServices](https://github.com/YoYoGames/GMEXT-EpicOnlineServices) |
| Quiero anuncios | [GMEXT-AdMob](https://github.com/YoYoGames/GMEXT-AdMob) / [GMEXT-LevelPlay](https://github.com/YoYoGames/GMEXT-LevelPlay) |
| Hago 3D | [GM3D-Samples](https://github.com/YoYoGames/GM3D-Samples) + [GMEXT-Elements](https://github.com/YoYoGames/GMEXT-Elements) |
| Quiero UI lista para usar | [pfb-UserInterface](https://github.com/YoYoGames/pfb-UserInterface) |
| Quiero corregir un error del manual | [GameMaker-Manual](https://github.com/YoYoGames/GameMaker-Manual) |
