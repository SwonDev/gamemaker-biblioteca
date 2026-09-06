# Auditoría r3 · Herramientas, pipeline y automatización del desarrollo

> 6 de septiembre de 2026 · 99 temas evaluados · 55 cubiertos · 33 parciales · 11 faltan
> Referencia: GameMaker LTS 2026.0 (IDE `2026.0.0.16` · runtime `2026.0.0.23`)
> Notación: `NN/MM` = carpeta `NN - ...` / documento `MM - ....md` (p. ej. `13/06` =
> `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md`).
> El espejo del manual oficial (`09 - Manual oficial/`) cuenta como biblioteca — es fuente
> primaria #2 en el orden de autoridad de `AGENTS.md` — y se cita como tal cuando es la única
> fuente de un tema.

## Resumen ejecutivo

El pipeline de **desarrollo en solitario con `gm-cli`** es el mejor documentado de toda la
biblioteca en cualquier dominio que se audite: `07/13` y `13/10` están verificados **en vivo**
(proyectos reales creados, comandos ejecutados, exit codes leídos) y contienen hallazgos que ni
siquiera están en el manual oficial —`gm-cli run` nunca propaga el código de salida del juego,
`.gmcache/` no está en el `.gitignore` generado, `resourcetool` no puede crear un asset de tipo
`extension`—. Control de versiones (Git, LFS, conflictos de `.yy`) está a un nivel que no
esperaba encontrar: `13/06 §3.13` y `13/11 §4.1` resuelven con comandos reales el problema que
de verdad rompe equipos con GameMaker (las rooms). El hueco que más duele no es de
profundidad sino de **la última milla del lanzamiento comercial**: subir a Steam
(`steamcmd`/SteamPipe) y firmar/notarizar la build de escritorio (macOS y Windows) están
reconocidos como vacíos por la propia biblioteca, y son precisamente los dos pasos que
separan "compila en mi máquina" de "un jugador de verdad lo puede instalar sin un aviso de
seguridad". El segundo patrón, más amplio, es que media docena de herramientas de terceros
(LDtk→GMS, GMLive, `gml-parser`, transpilador TS→GML, linters además de Feather) están **bien
elegidas y catalogadas pero no explicadas**: el nombre, la estrella y la licencia están, la
receta de uso no.

## Tabla tema por tema

Leyenda: ✅ Cubierto · 🟡 Parcial · 🔴 Falta

### A · La IDE de GameMaker (10)

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | Preferencias del IDE que importan (rendimiento, autoguardado, rutas, tema) | 🟡 | `09/Setting_Up_And_Version_Information/IDE_Preferences/General_Preferences.md` (tema, DPI, FPS del editor), `.../General/Paths.md` (rutas de proyecto y cachés), `.../General/Power_Saving.md` | El intervalo/activación exacta del **autoguardado** no tiene nombre propio en ningún documento; solo se dice de pasada que existe |
| 2 | Atajos de teclado imprescindibles | ✅ | `01/01 §9` "Atajos que merece la pena memorizar" (curado) + `09/IDE_Navigation/Keyboard_Shortcuts.md` (lista oficial completa por editor) | — |
| 3 | Feather: qué detecta y cómo se configura | ✅ | `02/09 §2` (niveles de severidad, reglas 2026) + `05/04 §5` (JSDoc para Feather) + `09/.../Feather_Settings.md` y `.../Feather_Messages.md` (catálogo de códigos GM####) | — |
| 4 | Code Editor 2: multicursor, minimapa, snippets | ✅ | `02/09 §1` (anatomía, minimapa) + `09/.../Editing_Text.md` §"Multicursor" y §"Selección de código" | — |
| 5 | Marcadores (bookmarks) | ✅ | `02/09 §1.4` (gutter) + `09/IDE_Navigation/Bookmarks.md` (hasta 9 marcadores, atajos, no persisten entre sesiones) | — |
| 6 | Buscar y reemplazar en todo el proyecto | ✅ | `01/01 §5` y `§9` (Ctrl/Cmd+Shift+F, ventana Search Results, formato `[objeto]-[evento]-[línea]`) + `09/.../Editing_Text.md` §"Buscar y reemplazar" (regex, case-sensitive) | — |
| 7 | Refactor y renombrado seguro | ✅ | `09/.../Editing_Text.md` §"Menú contextual" ("Refactor Identifier" Ctrl/Cmd+R, "Find Usages" Shift+F1) + `.../Feather_Settings.md` (propagar renombrado de asset a las referencias en código) | — |
| 8 | Plantillas de proyecto | ✅ | `07/06` completo: 31 plantillas oficiales verificadas contra la API de GitHub, flags de `gm-cli init` | — |
| 9 | Workspaces / múltiples ventanas | ✅ | `09/Introduction/Workspaces.md` (docking, ventana propia, botones rápidos) | El documento curado `01/01 §5` se titula *"El Inspector, el Output **y los Workspaces**"* pero nunca desarrolla Workspaces — cita rota a corregir (ver Encargo #1) |
| 10 | Comparar código con control de versiones dentro del IDE | ✅ | `09/IDE_Tools/Source_Control/External_Merge_Diff_Tools.md` (herramienta Diff/Merge del IDE, macros `${scm_base}`/`${scm_theirs}`/`${scm_mine}`/`${scm_merged}`) | — |

### B · El depurador (7)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 11 | Breakpoints, incluidos condicionales | 🟡 | Breakpoints normales: `01/15 §3` + `09/IDE_Tools/The_Debugger.md` (F9, persisten con el proyecto) | **Breakpoints condicionales**: 0 menciones en toda la biblioteca ni en el manual EN/ES ni en el histórico 2022-2026 de `GameMaker-Bugs` — indicio de que la función **no existe** en el IDE, no solo que falte documentar |
| 12 | Inspección de variables en tiempo real (Watch) | ✅ | `01/15 §3` + `09/IDE_Tools/The_Debugger/Watches.md` (9 ventanas: Locals, Globals, Watches, Instance, All Instances, Render States, Surfaces/Textures, Buffer) | — |
| 13 | Paso a paso (step into/over/out) | ✅ | `09/IDE_Tools/The_Debugger.md` §"Barra de herramientas" (F11/F10/Shift+F11, diferencia explicada) | — |
| 14 | Pila de llamadas (call stack) | ✅ | `01/15 §3` (`debug_get_callstack()`) + `09/.../The_Debugger.md` §"Pila de llamadas" + tutorial de lectura de stack trace en `03/37` | — |
| 15 | La ventana de perfilado (Profiler): CPU, eventos, funciones | ✅ | `09/IDE_Tools/The_Debugger/The_Profiler.md` (página íntegra: botón activar/desactivar, tiempo medio/absoluto, Top Down) | **Ningún documento curado en español la menciona por su nombre.** `13/01` línea 12 afirma explícitamente que "el `profiler`" está explicado en `01/15`, y **no lo está** (0 apariciones de la palabra "profiler" en ese archivo) — cita rota (Encargo #1) |
| 16 | Depuración remota (dispositivo real) | 🟡 | `09/Setting_Up_And_Version_Information/The_Device_Manager.md` (conexión Android/iOS/tvOS) + excepción de firewall en `.../The_Debugger.md` | No hay un recorrido único que confirme que Watches/breakpoints funcionan igual ya conectado al dispositivo; el emparejamiento por QR (novedad 2026) solo aparece en release notes, no en el manual ni en un curado |
| 17 | Depurar HTML5 u otra exportación no-escritorio | 🟡 | "El Debug Overlay no está disponible en HTML5" (`01/15 §4` + `09/.../The_Debug_Overlay.md`) + `09/IDE_Tools/The_Micro_Web_Server.md` (servidor para probar por IP local) | No se explica si el Debug Module (breakpoints/Watches) sigue funcionando al exportar a HTML5, ni el flujo real con las devtools del navegador |

### C · Package Manager y prefabs (3)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 18 | Package Manager: instalar paquetes de la comunidad | ✅ | `02/08 §1` (interfaz, Package Sources propias/comunitarias, actualizaciones) | — |
| 19 | Crear y publicar un prefab propio | 🟡 | Prefab Builder confirmado (Beta 2026.100 R5): `02/08 §2.12` y `02/10` | Nadie explica **cómo usarlo**: es demasiado nuevo (27-ago-2026), ni el manual mirror ni la biblioteca dan pasos — pendiente hasta que YoYoGames publique la página del manual |
| 20 | Prefabs vs Local Packages vs Marketplace | ✅ | Prefabs (referencia, no copia): `02/08 §2`; Local Packages (`.yymps`, flujo completo): `09/IDE_Tools/Local_Asset_Packages.md`; Marketplace: `09/Introduction/The_Marketplace.md`; relación histórica: `07/03 §1` | No hay una tabla comparativa única — cada uno está bien explicado por separado pero hay que cruzar 3 documentos |

### D · El CLI `gm-cli` y el MCP `gamemaker-resource-tool` (10)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 21 | `gm-cli init`: opciones y plantillas de IA | ✅ | `07/13 §3` (tabla completa de flags, árbol de archivos generado, bug conocido de plantillas con prefabs y su fix en `§12`) | — |
| 22 | `gm-cli run`: ejecutar sin IDE | ✅ | `07/13 §4` + `13/10 §3.4-3.5` (**no propaga el exit code del juego**; patrón `###game_end###N`; bug de macOS con `/private/tmp`) | — |
| 23 | `gm-cli compile`: exit codes | ✅ | `13/10` líneas 1226-1249 (`echo $?`, asimetría explícita frente a `run`) + `07/13` (salida real 0 en éxito, error real al romper código a propósito) | — |
| 24 | `gm-cli package`: empaquetado | ✅ | `07/13 §4` (`-o/--output`, tamaño real de ZIP) + `§8` (`package`→`gxgames upload`→`meta`→`publish`) | — |
| 25 | `resourcetool eval` vs `repl` vs `mcp` | ✅ | `07/13 §6` (tabla: `mcp`=servidor stdio, `eval`=comando único para scripts/CI, `repl`=interactivo, `script`=batch) | — |
| 26 | `gm-cli manual read`: sintaxis y límites | ✅ | `07/13 §5` (`read`/`open`, `--language`, 11 idiomas) + `07/14` (comportamiento real sin resultados: `No results found`) | — |
| 27 | Toolchains (`--toolchain`) | ✅ | `07/13 §4` (tabla de flags) + receta "Fijar el runtime LTS 2026" | — |
| 28 | Automatizar tareas repetitivas con `gm-cli` | 🟡 | Shell wrapping (`13/10` 592-611), modo batch `resourcetool script` + `DEFAULTS SET/GET` (`07/13` 681-694), workflows de GitHub Actions (`07/13 §11`) | **Vigilancia de archivos** (watch/fswatch/entr) para disparar `gm-cli` al cambiar algo en disco: 0 menciones en toda la biblioteca |
| 29 | Catálogo MCP `gamemaker-resource-tool`: qué crea y qué no | ✅ | `07/13 §6` (inventario de comandos ResourceTool 2026.0.17, 17 tipos de recurso) + excepción de `extension` en `AGENTS.md` y `07/22` | No se ha comprobado tipo por tipo si hay otra excepción además de `extension` |
| 30 | Licencia CLI (`GAMEMAKER_CLI_LICENSE`), guest/login | ✅ | `07/13 §7` (`login`, `--print`, licencia guest automática, `--license` puntual) + `05/02` línea 625 (CI sin secreto usa guest) | — |

### E · Control de versiones (10)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 31 | `.gitignore` correcto para GameMaker | ✅ | `13/11 §4.1` (contenido real del `.gitattributes` generado por `gm-cli init`, verificado en vivo; aviso de que `.gmcache/` **no** está ignorado — 131 MB reales) + `13/06 §3.13` (plantilla oficial completa, issue `GameMaker-Bugs#2922`) | — |
| 32 | Por qué los `.yy` generan conflictos (JSON no válido, comas finales, Int64) | ✅ | `13/06 §3.13` ("Por qué no se editan los `.yy` ni el `.yyp` a mano"): cada `.yy` de room lleva la lista completa de instancias en un solo fichero | — |
| 33 | Resolver un conflicto en el `.yyp` raíz (lista de recursos) | 🟡 | `13/11 §4.1`: regla general "nunca se edita a mano; se descarta una versión (`--ours`/`--theirs`) y se rehace con `resourcetool`" | No cubre el caso concreto de **dos personas añadiendo recursos nuevos distintos**: tomar una versión entera del `.yyp` **pierde en silencio la referencia** al recurso que añadió la otra persona (el archivo queda huérfano en disco). Riesgo real de pérdida de trabajo sin error visible (Encargo #2) |
| 34 | Resolver un conflicto en un `.yy` de objeto/room/sprite | ✅ | `13/06 §3.13` tabla "Ramas y el problema de las rooms": "quédate con una versión entera (`--ours`/`--theirs`) y rehaz lo otro en el editor" + `09/IDE_Tools/Source_Control/Conflicts.md` (plugin del IDE: Usar el mío/suyo/Combinar) | — |
| 35 | Git LFS para arte y audio | ✅ | `13/11 §4.1` "Git LFS": comandos reales (`git lfs install/track`), qué NO va a LFS (`.yy`/`.yyp`), migración de historial, cuotas de GitHub verificadas, alternativas (GitLab LFS, Perforce Helix Core) | — |
| 36 | Ramas y flujo de trabajo en equipo | ✅ | `13/06 §3.13` (una room = un dueño acordado; `rebase` frecuente; reparto programación/arte) + `13/11 §4.1` (rama por feature grande, resto directo a `main`) | Solo cubre reparto a nivel de **rooms**, no de otros recursos binarios individuales |
| 37 | Revisar (code review) un diff de `.yy`/`.yyp` legible | 🔴 | — | Sin ninguna herramienta ni técnica para hacer legible un diff `.yy`/`.yyp` en un PR (visor JSON-aware, normalizador de claves antes de revisar). Solo se sabe que `linguist-generated=true` oculta el `.yy` de las estadísticas de GitHub, que no es lo mismo |
| 38 | Herramientas de merge de terceros para JSON/YY | 🟡 | `09/IDE_Tools/Source_Control/External_Merge_Diff_Tools.md`: KDiff3, Meld, TortoiseMerge, DiffMerge con las macros `${scm_*}` | Son merge tools **genéricas** (no conocen la semántica del `.yy`). `@bscotch/yy` (`12/08 §1`) sirve para leer/escribir sin corromper, no para fusionar |
| 39 | Bloqueo de recursos binarios para evitar edición simultánea | 🟡 | `13/11 §4.1` (nota final): nombra el problema y remite a Perforce Helix Core como alternativa completa de VCS | No explica **Git LFS File Locking** (`git lfs lock`/`unlock`), que resolvería esto sin cambiar de sistema de control de versiones |
| 40 | `git blame` sobre `.gml` (fácil) vs. `.yy` (inútil) | 🔴 | — | 0 menciones de `git blame` en toda la biblioteca, pese a que todo el contexto necesario ya está en `13/06 §3.13` — barato de cerrar |

### F · Compilación automatizada y CI/CD (10)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 41 | Build por CLI: exit codes y logs para CI | ✅ | `07/13 §4` (`--errors-only`, exit 0 verificado) + `13/11 §4.5` (`exception_unhandled_handler` devolviendo 1, "lo detecta el CI") | — |
| 42 | CI/CD con GitHub Actions para GameMaker | ✅ | `05/02 §5` (YAML completo: cache `.gmcache`, FFmpeg obligatorio en Linux, secreto `GAMEMAKER_PAT`, matriz runner+target) + `07/13 §11` (`compile.yml`/`package.yml` íntegros que genera `gm-cli init --actions`) | — |
| 43 | Runners self-hosted con licencia instalada | 🔴 | `07/13 §7`: la licencia *guest* automática hace que los workflows oficiales usen runners **hosted** (`ubuntu-latest`/`macos-latest`) sin problema | La premisa "GitHub-hosted no sirve" no aplica a los targets que soporta el CLI hoy. El caso real (consolas, licencia Enterprise, SDK bajo NDA) ni siquiera es un target del CLI — hueco de nicho, no de flujo general |
| 44 | Firmar y notarizar build de macOS | 🟡 | `01/16` ("hace falta firma y notarización de Apple") + novedad de inyección de código para Hardened Runtime en Beta 2026.100 (`12/02`) | Solo se dice que hace falta. **Cero comandos reales** (`codesign --sign`, `xcrun notarytool submit`, `--options runtime`, entitlements) aplicados a una build exportada de GameMaker (Encargo #3) |
| 45 | Firmar build de Windows (Authenticode) | 🔴 | Único hallazgo: `09/Settings/Game_Options/Windows_UWP.md` — certificado de la Windows Store/UWP, un caso **distinto** (no Authenticode de escritorio) | Nada sobre comprar un certificado, `signtool sign`, evitar el aviso de SmartScreen, integrarlo en `package.yml` (Encargo #3) |
| 46 | Subir a itch.io con `butler` | ✅ | `07/08 §2.2` "Subir con butler (CLI)": instalación, `butler login`, `butler push <carpeta> <usuario>/<juego>:<canal>`, `--userversion`, un canal por plataforma | — |
| 47 | Subir a Steam con `steamcmd` (VDF, depots, branches) | 🔴 | `05/02 §3.5`: una sola línea ("SteamPipe/steamcmd, fuera de GameMaker"), reconocido como vacío en `§6` del mismo documento | Cero detalle: sin `app_build.vdf`/`depot_build.vdf`, sin `steamcmd +run_app_build`, sin explicar depots ni branches de Steam. Es el storefront principal de la mayoría de juegos comerciales de GameMaker (Encargo #4) |
| 48 | Versionado automático del número de build desde CI | 🟡 | `13/11 §4.3` (semver `MAYOR.MENOR.PARCHE.BUILD`) + comando teórico `resourcetool eval "options set ... property=Version"` | El propio documento lo marca **"⚠️ no verificado"**: el CLI devolvió `No licensed options for platform 'windows'`. Sin receta de CI que incremente el build (p. ej. `${{ github.run_number }}`) antes de compilar (Encargo #5) |
| 49 | Builds paralelas multiplataforma en CI | ✅ | `07/13 §11` y `05/02 §5`: `strategy.matrix.include` (runner+target), ejemplo real con targets comentados listos para activar | — |
| 50 | Artefactos de build: dónde, retención, tamaño | 🟡 | Dónde: `actions/upload-artifact@v7` (`05/02 §5`, `07/13 §11`). Tamaño: `05/02 §4.5` (muy completo: límites de iOS/Android, cómo medir con `du -sh`) | Falta la **retención** (`retention-days`, cuota de GitHub Actions Artifacts): 0 resultados de `retention-days` en toda la biblioteca |

### G · Editores externos e importación de niveles/arte (10)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 51 | Tiled → GameMaker | ✅ | `07/09 §4`: flujo paso a paso completo (room vacía, mismos nombres, File→Export As→GameMaker, sobrescribir `.yy`), tabla de correspondencia de capas, gotchas (rotación, cambio de formato 2024, `gmParallax`) | — |
| 52 | LDtk → GameMaker | 🟡 | `12/05 §2`: solo nombra LDtkParser (★63 MIT) y "LDtk to GMS" con enlace | Sin guía propia con pasos/ejemplo GML; el README de terceros (`11/librerias/niveles-y-mapas/LDtkParser/`) sí tiene detalle pero no está traducido a prosa propia |
| 53 | Ogmo Editor → GameMaker | 🔴 | Ya detectado por otra auditoría interna: `_indice/auditorias/r3-procedural-niveles.md` fila 72, "0 menciones" | Todo: exportación, formato `.ogmo`/`.json`, importador mantenido en 2026. Nicho frente a Tiled/LDtk ya cubiertos |
| 54 | Aseprite → GameMaker | ✅ | `13/03 §5`: capas y tags, comando CLI real (`aseprite -b … --sheet-type horizontal --format json-array`), forma exacta del JSON, tres trampas al escribir un importador, código completo con `sprite_add()` | — |
| 55 | Formatos intermedios JSON/CSV | ✅ | `07/20` (SNAP: JSON/CSV/YAML/XML/VDF/QML/GML) + `13/01 §4.5` y `§9.3` (pipeline hoja→CSV/JSON→struct con código real, `load_csv`) | — |
| 56 | Escribir un importador propio (arquitectura) | 🟡 | Piezas sueltas: trampas de Aseprite (`13/03 §5.3`), patrón `json_parse`/`buffer_load` (`13/01 §9.3`), SNAP (`07/20`) | Ningún documento trata la arquitectura genérica de un importador (estructura del parser, validación de formato mal formado, dónde vive en `scripts/`, versionado del formato) |
| 57 | Regenerar assets al cambiar el original (watch/hot reload de arte) | 🟡 | AseSync/AseSync23 catalogados (`11/_CATALOGO.md`, `12/05 §1`); LDtkParser trae "Live Updating" (solo en su README de terceros) | Ningún documento propio explica el mecanismo, configuración o límites — son menciones de catálogo con un enlace |
| 58 | Hot reload de GML en runtime (GMLive) | 🟡 | `12/01 §8`: identifica GMLive.gml y lo distingue de recompilar ("coge la función al vuelo"), precio, no descargada | Sin detalle de implementación real: cómo se integra en el proyecto, límites (código en Create ya ejecutado, structs ya instanciados) |
| 59 | Pipeline de audio (edición externa → import) | ✅ | `13/09 §7` "Formatos y ajustes de importación": tabla por tipo de sonido, comandos reales de `ffmpeg`, regla pico-vs-loudness. Audacity paso a paso en `03/09` | — |
| 60 | Organización de carpetas: fuente vs. compilado | 🟡 | `12/05 §1`: recomendación puntual de guardar `.aseprite` fuera del proyecto en `arte/` | `13/06 §4.2` y `07/06 §6` solo documentan el árbol **dentro** del proyecto; ninguna guía une fuente↔asset importado a nivel de repositorio completo |

### H · Herramientas dentro del juego (runtime) (11)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 61 | Consola de comandos de trucos (texto, en runtime) | 🟡 | Consola integrada del Debug Overlay: `01/15 §4` "La ventana Log"; trucos **por tecla** con código GML completo: `13/10 §7.4` "El modo QA"; librería externa recomendada `rt-shell` (`12/01 §5`) | Ninguna receta propia en GML de una consola de **texto**: capturar `keyboard_string`, trocear con `string_split`, mapear el primer token a una tabla de comandos, volcar resultado a un log en pantalla (Encargo #6) |
| 62 | Editor de niveles in-game | ✅ | `13/02 §3.10` "Un editor de niveles dentro del juego": objeto `obj_editor` completo (Create/Step/Draw GUI), `tilemap_set_at_pixel`, F2 encender, F5/F9 guardar/cargar contra JSON | — |
| 63 | Inspector de entidades en tiempo real | ✅ | `01/15 §4` "Vistas de depuración personalizadas": `dbg_slider_int(ref_create(obj_jugador,"vida"),...)`, `dbg_checkbox(ref_create(...,"invencible"),...)` — ve y **edita** variables de una instancia en vivo | — |
| 64 | Gráficas de rendimiento en pantalla (FPS, memoria) | ✅ | Overlay incorporado: `01/15 §4` (ventana FPS "Stacked": GC/IO/Update/Draw; ventana Memory con `gc_get_stats()`). Autodibujada: `06/scr_debug.gml` → `debug_draw_fps_graph()` | La versión autodibujada solo cubre FPS, no memoria |
| 65 | Capturas de pantalla desde el juego | ✅ | `13/11 §4.7` (`captura_tomar()`/`captura_tomar_recorte()` con `screen_save`/`screen_save_part`) + `13/10 §7.3` "Capturas automáticas" + `08/05` (`surface_save`/`surface_save_part`) | — |
| 66 | Grabación de vídeo desde el juego | 🔴 | Solo `gxc_start_movie_recording`/`_stop_`/`_pause_`/`_resume_movie_recording` (`09/GXC/`) | Exclusivas del target **Opera GX** (plataforma GXC Challenges), no una API general. Riesgo de que un redactor las presente como solución universal sin esa salvedad (Encargo #7) |
| 67 | Modo foto (photo mode) | 🟡 | `13/11 §4.7`: ocultar HUD (`global.hud_visible`) antes de capturar + recorte con `screen_save_part` | Falta **cámara libre** desacoplada del jugador y **pausa** integrada; ya reconocido a medias por auditoría interna `_indice/auditorias/feedback-ux.md` (K11/P11) |
| 68 | `show_debug_message` frente a un log de verdad | ✅ | `13/06 §3.14` y `13/10 §7.2`: explican la diferencia literal ("`show_debug_message` desaparece al cerrar el juego") y dan `registro_escribir()`/`registrar()` con `file_text_open_append` | — |
| 69 | Niveles de log (debug/info/warning/error) | ✅ | `13/06 §3.14` y `13/10 §7.2`: `enum Registro/NIVEL`, macro de umbral redefinible por Config, filtrado por nivel | — |
| 70 | `debug_event` y la ventana de depuración del IDE | ✅ | `01/15 §3` (tabla de funciones de depuración) + `09/.../Debugging/debug_event.md` + `09/.../The_Debugger.md` | ⚠️ La página **española** de `debug_event.md` está desfasada frente a la inglesa: falta el segundo parámetro `[silent]` y el struct de retorno (`"ResourceCounts"`/`"DumpMemory"`); usar la firma de `buscar.py` (`debug_event(string, [param])` → `Struct`) |
| 71 | Familia `dbg_*` (paneles de depuración visual) | ✅ | `01/15 §4`: ejemplo completo (`dbg_view`, `dbg_section`, `dbg_slider_int`, `dbg_watch`, `dbg_checkbox`, `dbg_button`) con aviso del orden de argumentos; 26 símbolos `dbg_` verificados uno por uno contra `GmlSpec.xml` | — |

### I · Generación de código y datos (5)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 72 | Codegen GML desde tabla de datos (enums/structs) | 🔴 | Solo existe `extgen` (`07/03 §3.7`), pero genera *bindings* nativos de extensión desde GMIDL, no gameplay | Ningún script que lea JSON/CSV y **escriba** `.gml` de gameplay para evitar boilerplate |
| 73 | Hojas de cálculo a JSON (diseño de datos) | ✅ | `13/01 §4.5` "De la hoja de cálculo al juego" (diagrama de pipeline + 5 reglas) y `§9.3` (código real `balance_cargar/guardar/restaurar`); `07/20` (SNAP, `SnapFromCSV`) | — |
| 74 | Validación de datos de diseño antes de compilar | 🟡 | `13/01 §9.3` valida JSON malformado **en tiempo de ejecución** (try/catch al arrancar); `13/21 §3.5` "El gate de CI" valida **balance estadístico**, no estructura | Ningún validador de esquema (campos obligatorios, referencias a sprites/objetos inexistentes, IDs duplicados) que corra como paso de **build** antes de `gm-cli compile` |
| 75 | Plantillas de código (snippets) del IDE | 🟡 | `02/09 §1.6-1.7` "Snippets personalizados" (`*.tmSnippet` en el directorio de usuario, para **sobrescribir** un snippet incorporado) | No explica cómo crear un snippet **original** con disparador nuevo, ni la sintaxis interna (placeholders/tabstops) |
| 76 | Generar documentación desde comentarios GML | ✅ | `01/07 §12` y `05/04 §5` (JSDoc: `@function`/`@param`/`@return`) + `12/01 §6` "Tome" (genera sitios de documentación desde el JSDoc de GML) | Menor: falta el comando exacto para invocar Tome |

### J · Calidad (8)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 77 | Linters de GML de terceros (más allá de Feather) | 🟡 | `12/01 §2` (Gobo/GoboCat formateador; duck analizador) + `12/08 §2` (`@turlututu-games/gml-linter`) | Sin comando de instalación/ejecución, sin fichero de configuración ni salida de ejemplo para ninguno de los tres |
| 78 | Análisis estático de GML | 🟡 | `12/01 §2`: "duck... detecta errores antes de compilar. Complementa a Feather" | Dos frases sin ejemplo de qué bug detecta que Feather no detecte |
| 79 | Enforcement automatizado (pre-commit/CI que rechace estilo) | 🔴 | `13/10` línea 1234 sugiere `gm-cli compile --errors-only` como hook de pre-commit, pero solo rechaza código que **no compila** | Ningún hook ni job de CI que ejecute Gobo/duck/gml-linter y rechace el commit/PR por estilo — los workflows generados (`07/13 §11`) solo compilan y empaquetan (Encargo #8) |
| 80 | El framework de tests oficial de YoYo (GM-TestFramework) | ✅ | `13/10 §4.1`: estructura real del repo clonado, `TestSuite`/`addFact`, `assert_equals`/`assert_greater`/etc., `launcher.py igorRunTests`, aviso honesto de que el launcher oficial es solo Windows x64 con *access key* | — |
| 81 | Límites del testing automatizado de GML | ✅ | `13/10 §1.1` (tabla "se automatiza bien/mal"), `§2.3-2.4` (dibujado, eventos del motor, audio, red real quedan fuera) | — |
| 82 | Smoke tests compilando, como gate de entrega | ✅ | `13/10 §1.2` (capa "smoke test" de la pirámide) + `§8.1` "La puerta obligatoria" (`gm-cli compile --errors-only`) + `§9.5` (checklist de release) | — |
| 83 | Integración de tests automatizados en CI | 🟡 | `13/10 §3.4`: `correr-pruebas.sh` listo para CI (lee `###game_end###N`, verificado en vivo que el exit code del proceso no sirve) | Los dos únicos workflows documentados (`07/13 §11`) solo compilan y empaquetan; ninguno ejecuta la tanda de pruebas |
| 84 | Cobertura de tests: qué mide, alternativa en GameMaker | 🔴 | — | 0 menciones de "cobertura"/"code coverage" en las 1918 líneas de `13/10` ni en el resto de la biblioteca |

### K · Gestión del proyecto (6)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 85 | Issues y tableros (Trello, GitHub Projects, Jira) | 🟡 | `13/11 §3.7` "Herramientas gratuitas" (tabla: Archivos `.md`, GitHub Projects, Trello, Notion, HacknPlan, con fricción de cada una) + `§3.1` (tablero de 4 columnas) | **Jira: 0 apariciones** en toda la biblioteca; no se explica por qué encaja mal en un proyecto pequeño en vez de omitirlo sin más |
| 86 | Notas de versión / changelog | 🟡 | `13/11` línea 886: "cada parche... lleva notas, aunque sean tres líneas" | Sin plantilla ni formato (a diferencia de las plantillas sí existentes para ADR, diario, postmortem); sin categorías (añadido/corregido/cambiado) |
| 87 | Documentación interna del proyecto (wiki, README técnico) | 🟡 | Convenciones: `05/04` completo. Decisiones: `13/11 §3.5` (ADR) y `§3.6` (diario). Estructura: `13/06 §4.2` ("`notes/` ← decisiones versionadas con el código") | Disperso en 3 documentos sin punto de entrada común; ningún documento explica qué debe llevar un **README técnico** (cómo levantar el entorno, a quién preguntar); "wiki" solo aparece como herramienta externa, nunca como práctica interna |
| 88 | Onboarding de un compañero nuevo | 🔴 | — | 0 resultados reales (las 29 apariciones de "onboarding" son del *jugador*, `13/01 §5` y `04/40`, un concepto homónimo distinto). Los ingredientes ya existen dispersos (ADR, diario, `13/06`, git workflow) pero nadie los reúne en un checklist de "qué leer/saber primero" (Encargo #9) |
| 89 | Roadmap y milestones | ✅ | `13/11 §2` (puertas Prototipo→Vertical slice→Alfa→Beta→Gold, criterios de salida) + `§3.3` (un objetivo por semana) + `§7` (roadmap público, "temas no fechas") | — |
| 90 | Gestión de deuda técnica | 🟡 | `13/11 §1.4` y `§8.2`: puerta de vertical slice con tabla "Deuda técnica aceptada" (Qué/Por qué se acepta/Cuándo se paga) | Solo como puerta puntual (vertical slice→producción), no como práctica continua revisada en cada hito |

### L · Ecosistema de terceros (9)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 91 | UndertaleModTool: qué es, límites legales | ✅ | `12/08 §4` (qué abre de un `data.win`, `utmt-mcp`, nota ⚖️ de legalidad) + `§4 bis` (anatomía del binario, chunks FORM/GEN8/STRG/CODE, implicación de seguridad de no meter secretos en `STRG`) | — |
| 92 | Stitch: qué es y para qué sirve | ✅ | `12/08 §1` (tabla de los 4 paquetes: `@bscotch/stitch`, `@bscotch/yy`, `@bscotch/gml-parser`, `@bscotch/stitch-launcher`) + `12/01 §1` (Stitch for VSCode) | — |
| 93 | `gml-parser`: análisis programático de GML | 🟡 | `12/08 §1` y tabla final "Qué usar según lo que quieras hacer" (fila dedicada) | Solo una frase de catálogo — sin ejemplo de código, sin explicar qué expone la API (AST, resolución de símbolos) |
| 94 | GMEdit: editor externo, qué ofrece | ✅ | `12/01 §1` (autocompletado, navegación por definición, plegado, multicursor, plugin GMEdit-Constructor) + `07/02` (qué problema resuelve) | — |
| 95 | GMLive: hot reload real, mecanismo técnico | 🟡 | `12/01 §8` (qué hace, precio, no descargada) | Solo describe el qué, nunca el cómo (conexión IDE-extensión↔juego en ejecución, qué límites tiene: código en Create ya ejecutado, structs ya instanciados) |
| 96 | "YYP Sanitizer" o equivalente | ✅ (con matiz de nombre) | `12/01 §3` "YYP Maker · Sohom Sahaun": "reparación de proyectos: regenera y limpia el `.yyp` cuando se corrompe" | No existe una herramienta llamada literalmente "YYP Sanitizer" (0 resultados, confirmado también por WebSearch); la equivalente real y bien documentada es **YYP Maker** — discrepancia de nombre en el encargo original, no un hueco de la biblioteca |
| 97 | Herramientas de sprites de terceros (TexturePacker...) | ✅ | `12/05 §6 bis` "Atlas de texturas (TexturePacker)": diagnóstico previo con `texture_debug_messages`, cuándo compensa frente a texture groups nativos | No menciona Free Texture Packer ni otras alternativas gratuitas — cobertura sólida pero de una sola herramienta comercial |
| 98 | Transpiladores hacia GML (TypeScript→GML) | 🟡 | `12/08 §2`: `@odemian/gamemaker-typescript` (0.0.11) catalogado como "Experimental" | Una frase por documento; sin detallar qué subconjunto de TS soporta, ni ejemplo de código transpilado |
| 99 | Extensiones de editores de texto para sintaxis GML | 🟡 | `12/01 §1`: Stitch for VSCode (gestión de recursos) y vim-gml (resaltado de sintaxis para Vim/Neovim, explícito) | Para VSCode específicamente no se dice si Stitch da resaltado/snippets (su Marketplace sí los tiene); no hay reseña de una extensión centrada solo en sintaxis |

## Huecos por prioridad

### 🔴 Graves

1. **Publicar en Steam (`steamcmd`/SteamPipe) no tiene ni un comando real** (#47). Es el
   *storefront* principal de la inmensa mayoría de juegos comerciales hechos con GameMaker, y
   la propia biblioteca lo reconoce como vacío (`05/02 §6`). Sin `app_build.vdf`, sin
   `steamcmd +run_app_build`, sin depots ni branches, un agente no puede completar el último
   paso de un lanzamiento comercial siguiendo esta biblioteca.
2. **Firma y notarización de escritorio ausentes en las dos plataformas principales** (#44,
   #45). En macOS, una build sin notarizar es muy difícil de abrir para un usuario normal
   (Gatekeeper); en Windows, sin certificado Authenticode, SmartScreen asusta al jugador con
   "Windows protegió su PC". Son el paso que separa "compila en mi máquina" de "un jugador
   normal se lo instala sin miedo", y hoy son una frase suelta cada uno.

### 🟠 Medios

- **Conflicto de merge en el `.yyp` raíz puede perder un recurso en silencio** (#33): tomar
  `--ours`/`--theirs` entero sobre el `.yyp` cuando dos personas añaden recursos distintos deja
  huérfano el recurso de la otra persona, sin error visible.
- **CI que compila y empaqueta pero nunca testea ni lintea** (#79, #83): los dos únicos
  workflows de GitHub Actions documentados (`07/13 §11`) no ejecutan `correr-pruebas.sh` ni
  ningún linter, aunque ambas piezas ya existen sueltas en la biblioteca.
- **Consola de comandos de trucos por texto sin receta propia en GML** (#61): el modo QA por
  tecla y el Debug Overlay cubren parte del problema, pero no hay una receta de "capturar texto
  → parsear → ejecutar comando", pese a ser un tema nombrado explícitamente en el encargo.
- **`gxc_movie_recording` puede presentarse por error como grabación de vídeo genérica** (#66):
  son funciones reales pero exclusivas de Opera GX/GXC Challenges.
- **Onboarding de un compañero nuevo inexistente como documento** (#88): todos los ingredientes
  (ADR, diario, arquitectura, flujo de Git) ya están escritos; falta reunirlos en un checklist.
- **Versionado automático del build desde CI sin verificar** (#48): la única propiedad de CLI
  propuesta para incrementarlo devolvió un error en la propia sesión que la escribió.

### 🟡 Menores

- Revisar diffs `.yy`/`.yyp` legibles (#37) y `git blame` sobre `.yy` (#40): nicho, mitigado por
  `linguist-generated`.
- Runners self-hosted con licencia (#43): la premisa no aplica a los targets que cubre el CLI
  hoy; solo importa para consolas bajo NDA, que ya están fuera de alcance del CLI.
- Ogmo Editor (#53): ya detectado y con plan por otra auditoría interna; nicho frente a
  Tiled/LDtk, ya cubiertos.
- Codegen GML desde datos (#72) y cobertura de tests (#84): nicho, sin urgencia.
- Patrón repetido "**catalogado pero sin manual de uso**": LDtk (#52), regenerar assets al
  cambiar el original (#57), GMLive (#58, #95), `gml-parser` (#93), transpilador TS→GML (#98),
  linters y análisis estático más allá de Feather (#77, #78), snippets propios (#75),
  extensiones de editor para sintaxis (#99). En todos los casos el nombre/estrella/licencia ya
  están verificados; falta traducir el README a 2-3 párrafos de uso en español.
- Escribir un importador propio como patrón genérico (#56), organización fuente-vs-compilado a
  nivel de repositorio (#60), bloqueo de binarios con `git lfs lock` (#39), merge tools
  conscientes del formato `.yy` (#38): mejoras de proceso, no bloqueos.
- Preferencias de autoguardado sin nombre propio (#1), Prefab Builder demasiado nuevo (#19),
  depuración remota/HTML5 sin recorrido único (#16, #17): la información existe pero fragmentada
  o pendiente de que YoYoGames publique la página de manual correspondiente.
- Notas de parche sin plantilla (#86), documentación interna dispersa (#87), Jira no mencionado
  (#85), deuda técnica solo como puerta puntual (#90), validación de datos solo en runtime (#74).
- **Dos citas cruzadas rotas** dentro de documentos ya buenos: `13/01` línea 12 dice que "el
  profiler" está en `01/15` y no lo está (#15); `01/01 §5` promete Workspaces en el título y no
  los desarrolla (#9). Coste de arreglo: minutos, no investigación.

## Encargo para el redactor

1. **Arreglar dos citas rotas** (sin investigación nueva, solo enlazar bien).
   - `13/01` (línea 12): cambiar el enlace de "el `profiler`" para que apunte a
     `09 - Manual oficial/manual-lts-2026-es/IDE_Tools/The_Debugger/The_Profiler.md`, o añadir
     una sección corta "El Profiler" en `01/15 §4` (junto a las demás ventanas del Debug
     Overlay) que resuma botón activar/desactivar, tiempo medio/absoluto y Top Down, con enlace
     al manual. Sin símbolos GML nuevos (es una ventana del IDE, no una función).
   - `01/01 §5`: completar el párrafo de "Workspaces" (hoy vacío bajo ese título) con 3-4
     líneas: docking, ventana propia, *Reset Layout*, enlazando a
     `09/Introduction/Workspaces.md`.

2. **Nota de seguridad en `13/06 §3.13` o `13/11 §4.1`**: un párrafo de advertencia sobre el
   conflicto de merge en el `.yyp` raíz cuando dos ramas añaden recursos **distintos**: tomar
   `--ours`/`--theirs` entero deja el recurso de la otra rama huérfano en disco (el `.yyp` ya no
   lo referencia); la corrección es añadirlo de nuevo tras el merge con
   `gm-cli resourcetool eval "create ..."` (según el tipo de recurso) o arrastrándolo al Asset
   Browser. Sin símbolos GML nuevos.

3. **Sección nueva "Firmar y notarizar la build de escritorio" en `05/02` (junto a la §4.5 de
   presupuesto de build) o como nueva `§4.6`**: dos bloques, macOS y Windows.
   - macOS: `codesign --deep --force --options runtime --sign "<Developer ID>" MiJuego.app`,
     luego `xcrun notarytool submit MiJuego.zip --apple-id ... --team-id ... --wait`, y
     `xcrun stapler staple MiJuego.app`. Requiere una cuenta de Apple Developer y un certificado
     "Developer ID Application" — nada de esto es GML, es tooling de Xcode/Apple, así que
     enlazar en vez de traducir todo el flujo.
   - Windows: comprar un certificado de firma de código (OV o EV), `signtool sign /f cert.pfx
     /p <pass> /t http://timestamp.digicert.com MiJuego.exe`, y por qué EV evita el aviso de
     SmartScreen desde el primer día mientras OV necesita reputación acumulada.
   - Integrar ambos como paso opcional en el `package.yml` de `07/13 §11` (secretos de
     GitHub Actions para el certificado/contraseña). Sin símbolos GML: es tooling externo.

4. **Sección nueva "Publicar en Steam con `steamcmd`" en `05/02 §3.5`** (hoy una sola línea), o
   documento propio enlazado desde ahí y desde `13/11 §6`:
   - Instalar `steamcmd`, estructura mínima de `app_build.vdf` (`AppID`, `Desc`, `ContentRoot`,
     `BuildOutput`, bloque `Depots`) y `depot_build.vdf` (`DepotID`, `FileMapping`).
   - Comando de subida: `steamcmd +login <usuario> +run_app_build ../scripts/app_build.vdf
     +quit`.
   - Branches de Steam (`default` público, y una beta interna con contraseña) para probar antes
     de publicar. Enlazar con el flujo de `gm-cli package --target windows` como paso previo.
   - Sin símbolos GML: es tooling de Steamworks, no del motor.

5. **Completar `13/11 §4.3`** con la verificación pendiente del versionado automático: en vez
   del comando "no verificado", probar `gm-cli resourcetool eval "options list"` contra un
   proyecto real para encontrar el nombre exacto de la propiedad de versión por plataforma
   (o documentar honestamente que solo es editable desde el IDE si `resourcetool` no la expone),
   y añadir un paso de CI que la incremente con `${{ github.run_number }}` antes de
   `gm-cli compile`.

6. **Receta nueva "Una consola de comandos de trucos" en `13/10 §7` (junto a §7.4) o como nueva
   sección de `01/15`**: capturar `keyboard_string` en un objeto controlador (activado solo con
   `MODO_QA`/`DEV`, igual que en §7.4), trocear con `string_split` respetando comillas para
   argumentos con espacios, mapear el primer token contra un `struct` `comando → función`,
   convertir el resto de tokens según el tipo esperado, y volcar el resultado a la capa de log
   ya existente (`registrar()`, `13/10 §7.2`). Símbolos verificados con `buscar.py` para esta
   receta: `keyboard_string` (variable global, `String`), `string_split(str, delimiter,
   [remove_empty], [max_splits])` → `Array[String]`, `string_trim(str, [substrs])` → `String`.

7. **Aviso en `09/GXC/GXC_Functions.md` no se edita (es manual oficial), pero sí en cualquier
   sección nueva que mencione grabación de vídeo**: si el redactor añade una receta que cite
   `gxc_start_movie_recording`, debe llevar la advertencia explícita de que es exclusiva del
   target Opera GX (plataforma GXC Challenges) y no una API general — no presentarla nunca sin
   esa salvedad.

8. **Sección nueva en `13/10` (tras §8.4) o en `07/13 §11`: "Un paso de calidad en el pipeline
   de CI"**: extender el `package.yml`/`compile.yml` ya documentado con dos pasos opcionales —
   uno que ejecute `correr-pruebas.sh` (ya existe en `13/10 §3.4`) contra un target headless, y
   otro que corra `duck`/Gobo en modo *check* y falle el job si hay violaciones. No inventar
   flags de esas herramientas: verificar su CLI real (README en
   `11 - Código descargado/librerias/depuracion/`) antes de escribir el YAML.

9. **Documento nuevo o sección "Onboarding de un compañero nuevo" en `13/06` (final, como
   nueva §6) o en `13/11`**: checklist de 10-15 líneas que enlace lo que ya existe — leer
   `AGENTS.md`/`CLAUDE.md` del proyecto, `13/06` completo, la disciplina de ramas y rooms de
   `§3.13`, dónde están las decisiones (`notes/`, ADR), cómo se compila (`gm-cli compile
   --errors-only`) y a quién pertenece cada room. No es contenido nuevo: es un índice que reúne
   lo que ya está escrito, con el valor de que hoy no existe ese punto de entrada único.

## Lo que comprobé y NO hacía falta

- **Control de versiones con Git**: pensé que sería un hueco típico de una biblioteca en
  español y es justo lo contrario — `13/06 §3.13` y `13/11 §4.1` están entre las secciones
  mejor trabajadas de toda la biblioteca en cualquier dominio, verificadas en vivo creando un
  proyecto real el mismo día de esta auditoría. No reabrir salvo por los matices puntuales ya
  listados (#33, #37, #39, #40).
- **El CLI `gm-cli` en su conjunto** (`init`, `run`, `compile`, `package`, `resourcetool`,
  `manual read`, toolchains, licencia guest): 9 de 10 temas ✅, con hallazgos que ni el manual
  oficial tiene (`gm-cli run` no propaga el exit code del juego). No hace falta ampliar nada
  aquí; sí vale la pena que otros documentos lo citen más y dupliquen menos.
- **Testing de GML** (`13/10`, 1918 líneas): pirámide de pruebas adaptada, mini-framework
  propio, GM-TestFramework explicado con la distinción correcta (es el framework interno de
  YoYo para reportar bugs del motor, no para testear tu propio juego — muchas fuentes de
  terceros confunden esto y aquí no), regresión con *golden files*, rendimiento con
  `get_timer()`/GMBenchmark, playtesting y triaje de bugs. Es, con diferencia, el documento
  más completo de todo este dominio.
- **Tiled y Aseprite → GameMaker**: ambos tienen flujo completo paso a paso con código real;
  no hacía falta tocarlos. El contraste con LDtk/Ogmo (solo catalogados o ausentes) es el hueco
  real, no estos dos.
- **`dbg_*` y `debug_*`**: se verificaron uno por uno contra `GmlSpec.xml` (26 símbolos `dbg_` +
  9 `debug_`). Ninguno inventado; el ejemplo de vistas de depuración personalizadas en `01/15`
  es correcto y ya cubre el tema con código real.
- **UndertaleModTool, Stitch, `@bscotch/yy`**: bien explicados con el matiz legal correcto
  (estudiar sí, redistribuir no) y con análisis real del formato binario (chunks FORM/GEN8).
- **"YYP Sanitizer"**: no existe con ese nombre exacto (confirmado también por WebSearch); la
  biblioteca ya documenta su equivalente real (YYP Maker) con más detalle del que el nombre del
  encargo original hacía suponer. No es un hueco, es una discrepancia de nomenclatura.
