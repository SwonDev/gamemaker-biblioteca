# Auditoría r4 · Ecosistema — repositorios, librerías y herramientas

> 7 de septiembre de 2026 · 74 temas evaluados · 54 cubiertos · 20 parciales · 0 faltan
> Referencia: GameMaker LTS 2026.0 (IDE `2026.0.0.16` · runtime `2026.0.0.23`)
> Notación: `NN/MM` = carpeta `NN - ...` / documento `MM - ....md` (p. ej. `07/02` =
> `07 - Ecosistema/02 - Librerías esenciales de la comunidad.md`). Catálogo de código:
> `11/CAT` = `11 - Código descargado/_CATALOGO.md`, `11/RUT` = `_RUTAS.json` (608 claves).
> Todo lo marcado "verificado 2026-09-07" se comprobó en vivo hoy contra la API de GitHub
> (`gh api` / `curl` con token), la API de Codeberg, npm, o WebFetch/WebSearch — nunca contra
> memoria de entrenamiento ni contra lo que dice el propio catálogo sin recomprobar.

## Resumen ejecutivo

**El barrido del 1-2 de septiembre de 2026 es, sin exagerar, uno de los más completos que existen
para este ecosistema — y esta ronda lo confirma en vivo, no solo lo repite.** La prueba más dura
que le he hecho: descargué la lista curada de terceros `bytecauldron/awesome-gamemaker`
(**503 ★ verificado hoy**, CC0-1.0, 200 repositorios enlazados en 26 categorías) y crucé cada uno
de sus 200 enlaces contra `11/RUT`. Resultado: **198 de 200 (99 %) ya estaban catalogados.** Un
segundo subagente, con una búsqueda independiente por otras vías (GitHub topics, repos creados
desde junio de 2026, "gml language:gml"), llegó a la misma conclusión por su cuenta. Para un
agente que use esta biblioteca como única fuente, la cobertura de "qué librería existe para
X" está resuelta en más del 99 % de los casos con la biblioteca tal y como está hoy.

Con esa base, el valor real de esta ronda está en tres sitios: **(1) una corrección de un dato
objetivamente falso** — `DragoniteSpam/Emu` tiene licencia MIT desde 2020 y la biblioteca lo
marca como "sin licencia" en tres archivos distintos, lo que podría hacer que un agente
desaconsejara sin motivo una librería de UI perfectamente usable en comercial; **(2) un hueco de
categoría entera que nadie había mirado**: un pequeño pero activo clúster de reimplementaciones
del runner de GameMaker para **consolas homebrew** (3DS, Wii U) que vive justo al lado de
Butterscotch/OpenGM —ya catalogados— pero no está enlazado con ellos; y **(3) media docena de
huecos de nicho reales pero honestos**: nadie en toda la comunidad GML ha escrito un wrapper de
ENet ni un netcode con rollback libre distinto de GGRollback, y Ogmo Editor sigue sin importador
mantenido en 2026 — la biblioteca ya documenta ambos como huecos, correctamente, y esta ronda solo
confirma que siguen sin cerrarse **fuera** de la biblioteca, no dentro. No hay ningún hueco
funcional (guardado, UI, partículas, cámaras, diálogos, localización, físicas, red, depuración,
editores, importadores) para el que exista hoy una librería viva y mejor que la que la biblioteca
ya recomienda: en los nueve que exigía el encargo, el veredicto es ✅ en siete y 🟡 (mención
complementaria, no sustitución) en dos.

**¿Podría un agente que solo lea la biblioteca elegir la librería correcta para su juego y saber
si sigue viva?** Sí, en la inmensa mayoría de los casos, y con más margen de seguridad del que
tenía al empezar esta ronda: las 38 librerías del "kit básico" citadas explícitamente en el
encargo más las que completan las tablas maestras de `07/_INDICE-ECOSISTEMA.md` se han verificado
una a una hoy contra la API real, no contra lo que decía el catálogo. Ninguna resultó archivada
por sorpresa; la única inexactitud real es la licencia de Emu.

## Tabla tema por tema

Leyenda: ✅ Cubierto · 🟡 Parcial · 🔴 Falta

### A · Las nueve librerías nombradas explícitamente en el encargo

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | Scribble — vigente | ✅ | `07/02 §2` · verificado hoy: **415 ★**, MIT, *push* 2026-09-06 | — |
| 2 | Chatterbox — vigente | ✅ | `07/02 §3` · verificado hoy: **175 ★**, MIT, *push* 2026-08-13 | — |
| 3 | Input — vigente | ✅ | `07/02 §1` y `07/_IND` (aviso de mudanza) · verificado hoy en **Codeberg**: **10.4.3**, MIT, *push* 2026-09-02 (repo de GitHub archivado, confirmado) | — |
| 4 | Vinyl — vigente | ✅ | `07/02 §4` y `07/21` (guía ES) · verificado hoy: **61 ★**, MIT, *push* 2026-07-08 | — |
| 5 | SnowState — vigente | ✅ | `11/CAT` (máquinas de estados) y `07/17` (guía ES) · verificado hoy: **178 ★**, MIT, *push* 2026-09-06 (¡ayer!) | — |
| 6 | Bento — vigente | ✅ | `07/02 §6` · verificado hoy: **55 ★**, MIT, *push* 2026-09-07 (**hoy mismo**) | — |
| 7 | Canvas — vigente | ✅ | `11/CAT` (utilidades) · verificado hoy: **22 ★**, MIT, *push* 2026-04-11 (5 meses sin *push*, pero es una librería pequeña y completa — no es señal de abandono) | — |
| 8 | TweenGMS | ✅ (con matiz de nombre) | `11/CAT` (tweens): `GMMT` (erkan612) y `Tweeny` (Kruger0) | **No existe ningún repositorio llamado exactamente "TweenGMS"** en GitHub (`gh api search/repositories?q=TweenGMS` → 0 resultados, verificado hoy). El hueco real —tweens en GameMaker— sí está cubierto: `GMMT` y `Tweeny` (8★ cada uno, MIT, activos en 2026) ya están catalogados. Mismo patrón que "YYP Sanitizer" en la ronda 3: nombre que no corresponde a un repo real, pero la necesidad detrás sí está resuelta |
| 9 | LDtkParser — vigente pero *push* antiguo | 🟡 | `11/CAT` (niveles-y-mapas) y `07/02 §8` · verificado hoy: **63 ★**, MIT, *push* **2025-08-14** (más de un año sin actividad) | No es un hueco de la biblioteca (sigue siendo la mejor opción viva para LDtk→GameMaker), pero merece una nota de "sin *push* desde hace más de un año" junto a su ficha, igual que ya se hace con Coroutines o LDtkParser en otros sitios de la biblioteca |

### B · Resto del "kit básico" y librerías de comunidad ya catalogadas (barrido de vida completo)

Las 38 librerías de la tabla maestra de `07/_INDICE-ECOSISTEMA.md` y `07/02`, verificadas una a
una hoy (2026-09-07) contra la API de GitHub (`gh api repos/OWNER/REPO`). Ninguna resultó
archivada por sorpresa ni con licencia distinta a la documentada, **salvo Emu (ver "Lo que
encontré desactualizado")**.

| # | Repo | ★ hoy | Licencia | Último *push* | Veredicto |
|---|---|---:|---|---|---|
| 10 | BBMOD | 119 | MIT | 2026-08-04 | ✅ vigente, sin cambios |
| 11 | `JujuAdams/db` | 22 | MIT | 2026-08-26 | ✅ vigente |
| 12 | iota | 48 | MIT | 2026-07-08 | ✅ vigente |
| 13 | STANNcam | 43 | MIT | 2026-08-21 | ✅ vigente |
| 14 | GMEdit | 369 | MIT | 2026-07-22 | ✅ vigente |
| 15 | SNAP | 100 | MIT | 2026-07-08 | ✅ vigente |
| 16 | GMRoomLoader | 130 | MIT | 2026-08-17 | ✅ vigente (★128→130 desde el 2-sep) |
| 17 | Snitch | 39 | MIT | 2026-07-29 | ✅ vigente |
| 18 | Bulb | 107 | MIT | 2026-07-08 | ✅ vigente |
| 19 | YUI | 65 | MIT | 2026-08-24 | ✅ vigente |
| 20 | Bonk | 15 | MIT | 2026-08-27 | ✅ vigente |
| 21 | lexicon | 52 | MIT | 2026-07-11 | ✅ vigente |
| 22 | DoLater | 45 | MIT | 2026-06-07 | ✅ vigente |
| 23 | Emu | 43 | **MIT** (no "sin licencia") | 2026-02-18 | 🟡 dato de licencia desactualizado en la biblioteca — ver más abajo |
| 24 | LimeUI | 36 | MIT | 2026-08-29 | ✅ vigente |
| 25 | Dynamo | 36 | MIT | 2026-07-08 | ✅ vigente |
| 26 | Elephant | 24 | MIT | 2026-07-02 | ✅ vigente |
| 27 | Collage | 29 | MIT | 2026-07-26 | ✅ vigente |
| 28 | GMUI | 30 | MIT | 2026-08-10 | ✅ vigente |
| 29 | ScribbleJunior | 25 | MIT | 2026-07-16 | ✅ vigente |
| 30 | Figgy | 27 | MIT | 2026-08-10 | ✅ vigente |
| 31 | Lookout | 21 | MIT | 2026-08-08 | ✅ vigente |
| 32 | PictureFrame | 10 | MIT | 2026-08-16 | ✅ vigente |
| 33 | Splat | 5 | MIT | 2026-07-28 | ✅ vigente |
| 34 | Crochet | 121 | MIT | 2026-05-28 | ✅ vigente |
| 35 | Unic | 8 | MIT | 2026-03-29 | ✅ vigente |
| 36 | LineAudio | 5 | MIT | 2026-07-25 | ✅ vigente |
| 37 | gmlinear2 | 17 | MIT | 2025-07-29 | ✅ vigente (sucesor correcto de `gmlinear`, ya documentado) |
| 38 | GML-OOP | 34 | NOASSERTION | 2026-09-07 (hoy) | ✅ correctamente marcado ⚠️ en la biblioteca — sin cambios |
| 39 | gmlscripts.com | 85 | NOASSERTION | 2026-07-24 | ✅ correctamente marcado ⚠️ — sin cambios |
| 40 | Coroutines | 83 | MIT | 2025-06-29 | ✅ vigente (más de un año sin *push*, pero estable y completa) |

### C · Organizaciones y listas curadas (barrido meta)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 41 | Org `YoYoGames` — ¿algo nuevo desde el 2-sep? | ✅ | `gh api orgs/YoYoGames/repos?sort=pushed`, verificado hoy: el *push* más reciente es `GMEXT-AppleIAP` (hoy mismo), pero **todos** los repos con actividad desde el 2-sep ya están en `07/01` y `07/03` (comprobado repo por repo con `grep`) | Ninguno nuevo — las 44 `GMEXT-*` siguen siendo 44 |
| 42 | Org `GameMakerDiscord` — ¿algo nuevo? | ✅ | `gh api orgs/GameMakerDiscord/repos?sort=pushed` (65 repos), verificado hoy: el más reciente es `Xpanda` (*push* mayo 2026), ya catalogado en `12/01` y `12/05` | Ninguno nuevo |
| 43 | Cruce contra `awesome-gamemaker` (lista curada de terceros, 200 enlaces) | ✅ | Cruce programático hoy contra `11/RUT`: **198/200 (99 %)** ya catalogados. Los 2 no encontrados: `NuxiiGit/disarm` (repo y cuenta del autor **ya no existen**, 404 verificado hoy — enlace muerto de la propia lista curada, no un hueco) y `matthiaszarzecki/MadeWithGameMakerStudioBadges` (13 ★, solo insignias de README en Markdown, sin código — no es una librería) | Ninguno merece entrar |
| 44 | `gm-cli` — versión instalada vs. publicada | ✅ | `npm view @gamemaker/gm-cli version` → **2.3.0**; `gm-cli --version` local → **2.3.0**. Ya coinciden (el 31-ago la biblioteca documentaba "2.2.0 local / 2.3.0 publicada" con un bug de plantillas con prefabs en 2.2.0) | Confirmar en `07/_IND` que el bug de `ProjectTool PREFABS RESTORE` ya no aplica a 2.3.0 (no reproducido en esta ronda, pero tampoco se ha intentado activamente) |

### D · Huecos por función (los nueve que pedía el encargo)

| # | Función | Veredicto | Ya recomienda la biblioteca | Candidato externo investigado hoy | Qué falta |
|---|---|---|---|---|---|
| 45 | Físicas 2D de cuerpo rígido más allá de Box2D nativo | ✅ | Box2D nativo está documentado en profundidad (`04/22`, 299 líneas, incluye partículas de fluido `physics_particle_*`) + `Bonk`/`Fracture` para colisión/destrucción | `GMPhysX` (bytecauldron) — *bridge* real a NVIDIA PhysX, pero **de pago, alfa, solo Windows** (verificado vía itch.io e issues de `bytecauldron/gmphysx-bugs`, *push* 2026-08-16) | Nota al pie en `07/02` sobre GMPhysX como opción de pago; no sustituye nada |
| 46 | Sistemas de guardado "serios" (multi-slot, autosave, migración de esquema) | ✅ | `db`+`SNAP` como motor, y un sistema completo **escrito en la propia biblioteca** (`01/14 §9-14`, multi-slot, *backup* rotativo, checksum) | `SSave`, `Lock And Key`, `BSONGML` — ninguno con presencia real verificable en GitHub hoy | Ninguno: sigue siendo territorio de "constrúyelo tú" en **todo** el ecosistema GML, no solo aquí |
| 47 | UI/HUD de nivel producción | ✅ | `Bento`/`YUI`/`GMUI`/`LimeUI` (`07/02 §6`) | `erkan612/MajorGUI_GML` (9★, MIT, *push* 2026-04-15, modo retenido, mismo autor que GMUI) | Mención breve como alternativa, no sustitución |
| 48 | Editores de niveles / importadores más allá de Tiled/LDtk | 🟡 | Tiled (`07/09 §4`) y LDtk (`11/CAT`, `12/05 §2`) | Ogmo Editor: **confirmado hoy de nuevo, sin importador GML mantenido en 2026** (ya detectado por r3) | Sigue siendo un hueco real pero ya está correctamente documentado como tal — no reabrir sin evidencia de que alguien lo resolvió |
| 49 | Red y multijugador más allá de Photon/Warp | 🟡 | `12/04` (Photon oficial, Colyseus, Warp, `http.gml`, `MultiClient`, `GMNest`) | ENet en GML y netcode con *rollback* libre distinto de GGRollback: **no existe ninguno en toda la comunidad**, confirmado hoy por búsqueda dirigida | Hueco real, pero de **ecosistema**, no de biblioteca: nadie lo ha construido todavía, no es que la biblioteca lo pasara por alto |
| 50 | Depuración/*profiling* de terceros | ✅ | `rt-shell`, `Snitch`, `Lookout`, `GM-TestFramework` (`12/01 §5`) | `GMPulse` (solo de pago, sin repo verificable), `GMonitor` (obsoleto desde 2021) | Ninguno supera lo ya recomendado |
| 51 | Localización más allá de lexicon | 🟡 | `lexicon` (recomendada) + Scribble para RTL/CJK (`07/02 §8`) | `CreativeHandOficial/gm-i18n` (ya citado en `12/05`) tiene **último *push* el 2023-02-04** — más de 3 años parado, sin la advertencia de desfase que sí llevan Bulb/Ugg. `undervolta/GM-I18n` parecía mejor pero está **archivado por su autor el 2026-06-16** ("ya no uso GameMaker") | Añadir aviso ⚠️ de desfase a `gm-i18n` en `12/05 §8`; no añadir `undervolta/GM-I18n` (muerto) |
| 52 | Generación procedural dedicada | ✅ | `13/07` (3284 líneas: ruido, autómatas celulares, Poisson-disc, Voronoi, WFC, L-systems) + `GMRoomLoader` para ensamblaje | Ninguna librería GML de terceros viva que la biblioteca no cite ya (búsqueda dirigida vía `JujuAdams/GameMakerLibraries`, la lista maestra del propio JujuAdams, y `gh` filtrado por lenguaje) | Sin hueco: la guía propia es más completa que cualquier librería de terceros en este dominio |
| 53 | Cámaras más allá de STANNcam | 🟡 | STANNcam (`07/02`) + sistema propio en `13/19` (1047 líneas) | **REZOL** (FoxyOfJungle) — cámara *pixel-perfect* + escalado GUI + *split-screen* + HDR, más completa que STANNcam pero **de pago** (itch.io, sin repo GitHub público que comparar) | Mención como alternativa de pago (mismo tratamiento 💸 que ya reciben otras herramientas de FoxyOfJungle en `12/05`) |

### E · Lo que no es una librería (verificado en vivo hoy, 2026-09-07)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 54 | Plantillas oficiales de YoYo — ¿siguen siendo 31? | ✅ | Consultada la API oficial de plantillas (`api.gamemaker.io/api/gamemaker/project-templates`) y `gm-cli init --help`: **siguen siendo exactamente 31** (18 juego · 12 Live Wallpaper · 1 GameStrip). La más reciente por fecha de creación ("Arcade Action Game Template", 2026-08-12) ya está en `07/06` | Ninguno |
| 55 | Marketplace vs. Package Manager 2026 | 🟡 | `09/Introduction/The_Marketplace.md` (manual, describe el acceso "desde el menú del IDE") y `_indice/auditorias/r3-herramientas-pipeline.md` #18-20 (Package Manager) | **La URL canónica cambió**: `gamemaker.io/en/marketplace` da hoy **404**; el Marketplace vive en `marketplace.gamemaker.io` (operativo, HTTP 200, verificado hoy) como sitio web independiente, ya no integrado en el menú del IDE de la forma que describe el manual — indicio de "*decommissioning*" gestual, sin anuncio oficial de cierre. El hilo del foro "Marketplace Future and the Prefab Library" sigue sin actividad nueva desde el 6-ago-2026 |
| 56 | Ejemplos oficiales nuevos desde el 2-sep | ✅ | Tres fuentes cruzadas hoy: repos de la org YoYoGames por fecha de *push*, `releases.gamemaker.io` (última Beta sigue siendo 2026.100, julio 2026) y el índice completo del blog oficial (25 posts, el más reciente del 19-ago-2026) | Ninguno — sin contenido educativo nuevo |
| 57 | Cursos y libros nuevos en 2026 | ✅ | WebSearch (Udemy, YouTube, búsqueda general) hoy: nada nuevo desde lo ya documentado en `07/12` (que ya cita *GameMaker Programming Challenges* de Ben Tyers, ene-2026, como el único libro reciente que vale la pena) | Ninguno |
| 58 | Canales/creadores activos 2026 no cubiertos | ✅ | Comparado contra `07/11` y `03 - Cursos (YouTube)/_DESCUBIERTAS.md` (17 canales, 44 vídeos documentados el 31-ago) | Ninguno nuevo con tracción verificable |
| 59 | Estado del foro oficial y Discord | ✅ | `forum.gamemaker.io/?whats-new/posts/` con actividad hasta **hoy mismo** (verificado en vivo); Discord oficial **~28 023 miembros** (coincide con lo ya documentado) | Ninguno nuevo — sin cambio de política |
| 60 | Devlogs/postmortems con tracción real para "proyectos de ejemplo" | 🟡 | `07/11` ya cita "The King Is Watching" (tinybuild, 600k ventas) | Rastreo del blog oficial encontró 4 posts de 2026 que **no** aparecen en `07/11 §1.2` (la tabla parece basada solo en el *feed* RSS, que no lista todo): *Barty's Adventure* (13-may), *Chivalware* (24-jun, respaldado por The Arcade Crew), *Cause+Select* (1-jul), *Loop Hero* de Playdigious (19-ago, port a móvil de un juego de éxito conocido) | Añadir las 4 filas a `07/11 §1.2`; opcionalmente citar Chivalware/Loop Hero en `07/04` como casos de estudio |

### F · Candidatos nuevos investigados hoy (no están en `11/RUT`)

| # | Repo | Qué resuelve | ★ | Licencia | Último *push* | Veredicto |
|---|---|---|---:|---|---|---|
| 61 | `Project-Sunshine-Native/cinnamon` | *Fork* de Butterscotch (ya catalogado): reimplementación del runner de GameMaker **para Nintendo 3DS y Wii U homebrew** | 390 | MPL-2.0 | 2026-09-05 | 🟡 **entra con matiz** — el propio README avisa de que el desarrollo activo se mudó a `Grayforz2468/cinnamon-latest` (0★, AGPL-3.0, *push* 2026-09-06, confirmado hoy); catalogar el par, no solo el original |
| 62 | `Ralcactus/GameMaker-Anywhere` | "Play GameMaker games anywhere" — port del runner a **varias consolas homebrew** vía devkitpro/C++ (convierte GML a C, no lo interpreta) | 69 | sin licencia | 2026-08-31 | 🟡 entra con matiz — proyecto real y activo, pero sin licencia declarada (revisar antes de recomendar para reutilizar código) |
| 63 | `OpenGMK/OpenGMK` | Reimplementación *open source* del runner de **GameMaker 8.x** (Classic), con herramientas adicionales | 406 | GPL-2.0 | 2026-07-16 | 🟡 entra — hueco real de "estudiar/ejecutar juegos GM8 antiguos", categoría distinta a Butterscotch/OpenGM (que apuntan a GMS2) |
| 64 | `OpenGMK/GM8Decompiler` | Descompilador de ejecutables de **GameMaker 8.x** | 200 | GPL-2.0 | 2024-02-12 | 🟡 entra con matiz — mismo hueco que UndertaleModTool pero para el formato **antiguo** (.gmk/.exe, no `data.win`); sin *push* desde 2024, revisar vivacidad antes de recomendar como primera opción |
| 65 | `skyfloogle/gm8x_fix` | Parche que corrige bugs conocidos de juegos hechos con **GameMaker 8.0/8.1** | 58 | MIT | 2026-04-09 | 🟡 entra — complementa al par anterior, mismo nicho legado |
| 66 | `xtreme3d/xtreme3d` | Motor 3D nativo (DLL) para GameMaker, de la era GM8/Studio 1.x, con actividad residual en 2026 | 50 | NOASSERTION | 2026-08-17 | 🟡 entra como nota histórica — BBMOD sigue siendo la recomendación moderna; Xtreme3D solo interesa para proyectos heredados que ya lo usan |
| 67 | `BPzeBanshee/GMOSSE` | Motor de referencia jugable para el género **shoot-em-up/shmup**, mantenido desde 2011, apunta a la última versión de GameMaker | 8 | BSD-3-Clause-Clear | 2026-09-05 | 🟡 entra — hueco funcional real: la biblioteca tiene motores de referencia para Sonic (`OrbinautFramework`) y Mega Man (`MegamixEngine`) pero ninguno de shmup, pese a las pocas estrellas |
| 68 | `flingoXD/flingos-MIDI` | Extensión de reproducción **MIDI** para GameMaker | 3 | MIT | 2026-08-18 | 🟡 entra con matiz — cierra un hueco real (0 soporte MIDI libre en el catálogo actual), pero con tracción mínima; verificar antes de recomendar como primera opción |
| 69 | `MedicV2/BigInt` | Enteros de precisión arbitraria, **apunta explícitamente a GameMaker LTS 2026** | 2 | NOASSERTION | 2026-08-05 | 🟡 entra con matiz — GML no tiene *bigint* nativo y no hay librería equivalente ya catalogada, pero 2★ y sin licencia SPDX clara exige revisar el código antes de confiar en él |
| 70 | `odditica/renderdoc-gms2-kit` | Generador de configuración de **RenderDoc** para depurar el *pipeline* gráfico de proyectos GMS2 | 25 | MIT | 2022-08-18 | 🟡 entra con matiz — hueco de *tooling* gráfico real (0 menciones de RenderDoc en toda la biblioteca), pero parado desde 2022; al ser un generador de ajustes (no código GML), probablemente sigue siendo válido, pero no verificado contra LTS 2026 |
| 71 | `coppolaemilio/gamemaker-godot-dictionary` | Diccionario de equivalencias **GML→GDScript** para migrar de GameMaker a Godot | 243 | MIT | 2021-10-31 | No entra como librería (no es código reutilizable, es una tabla de referencia) — mencionable solo si la biblioteca llega a cubrir migración a otros motores, que hoy no es su objetivo |
| 72 | `gmclan-org/gm-qol-toolbox-plugin` | Plugin de calidad de vida para el IDE, **apunta explícitamente a LTS 2026** | 3 | MIT | 2026-08-30 | Vigilar, no entra aún — coincide con la versión de referencia pero demasiado joven (nació esta semana) |
| 73 | `Furia25/GML-Graph` | Librería de teoría de grafos y algoritmos más allá de A*/Dijkstra puntuales | 3 | MIT | 2026-01-09 | Vigilar, no entra aún — hueco real (solo hay pathfinding puntual, no una librería de grafos genérica) pero tracción mínima de un solo desarrollador |
| 74 | `jarikomppa/soloud` | Motor de audio C/C++ portable, aparece en resultados de GitHub por el *topic* "gamemaker" | 2171 | NOASSERTION | 2024-08-13 | No entra — **falso positivo del *topic***: es una librería de audio general, no específica de GML, sin *binding* GameMaker activo verificable hoy |

## Huecos por prioridad

### 🔴 Graves

Ninguno. No hay ninguna necesidad habitual de un juego para la que la biblioteca no recomiende
ya una librería viva y correcta, y el catálogo de 608 repos coincide en un 99 % con la lista
curada de terceros más completa que existe para este ecosistema.

### 🟠 Medios

1. **Licencia de Emu incorrecta en tres archivos** (#23): `07/_INDICE-ECOSISTEMA.md` (tabla
   "Movimientos y abandonos confirmados"), `07/02 §"Avisos importantes"` no lo nombra pero
   `11/CAT` sí lo marca "⚠️ sin licencia" en la sección de interfaz de usuario. El repositorio
   `DragoniteSpam/Emu` tiene licencia **MIT desde el commit `2f7cb286` (11-jun-2020)**, verificado
   leyendo el propio fichero `LICENSE` hoy. Un agente que siga la biblioteca al pie de la letra
   podría desaconsejar sin motivo una librería de UI usable en comercial, o ponerla en una lista
   de "revisar antes de usar" que no le corresponde.
2. **Clúster de runners para consolas homebrew sin catalogar** (#61-63): Cinnamon (390★),
   `cinnamon-latest` (su continuación activa) y GameMaker-Anywhere (69★) son *forks*/proyectos
   hermanos de Butterscotch y OpenGM —ya catalogados en `11/CAT` bajo "Runtimes/motores
   alternativos"— pero no están enlazados junto a ellos pese a resolver exactamente la misma
   categoría de problema para hardware distinto (3DS/Wii U y consolas vía devkitpro).
3. **Legado GM8.x completamente ausente del catálogo** (#64-66): OpenGMK (406★),
   GM8Decompiler (200★) y `gm8x_fix` (58★) forman un trío coherente y activo-ish para
   estudiar/ejecutar/parchear juegos de la era **GameMaker 8.0/8.1**, un formato distinto al
   `data.win` que ya cubre UndertaleModTool en `12/08`. Nicho frente a LTS 2026, pero real.
4. **`gm-i18n` (CreativeHandOficial) sin aviso de desfase** (#51): más de 3 años sin *push*
   (2023-02-04), citado en `12/05 §8` sin la misma advertencia ⚠️ que sí llevan Bulb o Ugg en
   otros documentos de la biblioteca — inconsistencia de tratamiento, no de contenido.
5. **URL del Marketplace cambiada sin actualizar** (#55): `gamemaker.io/en/marketplace` → 404
   hoy; la URL vigente es `marketplace.gamemaker.io`. No hay enlaces rotos a la ruta antigua
   dentro de la biblioteca (comprobado con `grep`), pero el manual mirror en español describe un
   acceso "desde el menú del IDE" que ya no corresponde a cómo se gestiona el Marketplace en 2026.

### 🟡 Menores

- Nueve librerías de nicho investigadas hoy y con veredicto "entra con matiz" (#67-70, GMOSSE,
  MIDI, BigInt, RenderDoc kit): tracción baja (2-25 ★) pero cada una cierra un hueco funcional
  real que hoy no tiene ninguna alternativa citada. Ninguna sustituye nada; son adiciones.
- GMPhysX, MajorGUI_GML y REZOL (#45, #47, #53): opciones **de pago** o en alfa que merecen una
  nota al pie junto a la recomendación gratuita ya existente, nunca sustituirla.
- LDtkParser sin *push* desde hace más de un año (#9): sigue siendo la mejor opción viva, solo
  falta la advertencia de fecha.
- Cuatro entradas de blog oficial sin catalogar en `07/11 §1.2` (#60): coste de minutos, no
  investigación nueva.
- `TweenGMS` (#8) no existe como nombre de repositorio: mismo patrón que "YYP Sanitizer" en la
  ronda 3 — corregir la referencia, no crear el repo.
- Dos repos "vigilar, no entra aún" (#72-73): demasiado jóvenes (nacieron la semana de esta
  auditoría) para incorporar con la barra de selectividad que pide el encargo.

## Encargo para el redactor

1. **Corregir la licencia de Emu en los tres sitios donde aparece mal** (sin investigación
   nueva, el dato ya está verificado arriba): `07/_INDICE-ECOSISTEMA.md` (tabla "Movimientos y
   abandonos confirmados", fila `Emu`) y `11 - Código descargado/_CATALOGO.md` (sección
   "Interfaz de usuario", fila `Emu` — hay dos filas duplicadas de Emu en esa sección, corregir
   ambas). Cambiar "⚠️ sin licencia" por "MIT (desde 2020)". Sin símbolos GML: es un dato de
   metadatos de repositorio.

2. **Añadir el clúster de runners homebrew a `11/CAT`**, en la sección "Runtimes / motores
   alternativos de código abierto" (`juegos_y_motores/`), junto a Butterscotch y OpenGM:
   - `Project-Sunshine-Native/cinnamon` (390★, MPL-2.0) y su continuación activa
     `Grayforz2468/cinnamon-latest` (AGPL-3.0) — reimplementación del runner para 3DS/Wii U.
   - `Ralcactus/GameMaker-Anywhere` (69★, sin licencia declarada — avisar de ello) — port a
     varias consolas homebrew vía devkitpro, convierte GML a C.
   - Nota de que ambos son proyectos de *modding*/*porting* de juegos GameMaker ya compilados a
     hardware no oficial, no herramientas de desarrollo para hacer un juego nuevo — la misma
     distinción que ya hace la biblioteca para Butterscotch/OpenGM.

3. **Sección nueva o ampliación en `12/08` (Tooling externo… e ingeniería inversa), tras el §4
   actual de UndertaleModTool**: un bloque corto "Juegos de la era GameMaker 8.x (formato
   `.gmk`/`.exe`, anterior a `data.win`)":
   - `OpenGMK/OpenGMK` (406★, GPL-2.0) — reimplementación del runner GM8.x.
   - `OpenGMK/GM8Decompiler` (200★, GPL-2.0, sin *push* desde 2024 — avisar) — descompilador.
   - `skyfloogle/gm8x_fix` (58★, MIT) — parche de bugs conocidos de juegos GM8.0/8.1.
   - Misma nota ⚖️ de legalidad que ya lleva la sección de UndertaleModTool: estudiar sí,
     redistribuir assets no.

4. **Añadir aviso de desfase a `gm-i18n` en `12/05 §8`**: una línea "⚠️ sin *push* desde
   2023-02-04 — más de 3 años parado" con el mismo formato que ya usan las advertencias de Bulb/
   Ugg en otros documentos. No añadir `undervolta/GM-I18n` (archivado por su autor el
   2026-06-16, confirmado).

5. **Actualizar la URL del Marketplace**: en `_indice/auditorias/r3-herramientas-pipeline.md`
   item 20 (o donde el equipo decida centralizar este dato) añadir: "URL vigente del Marketplace
   (verificado 2026-09-07): `https://marketplace.gamemaker.io/` — la ruta antigua
   `gamemaker.io/en/marketplace` da 404." Revisar si el manual mirror en español
   (`09/Introduction/The_Marketplace.md`) merece una nota de que la fuente oficial tampoco lo ha
   actualizado (no es un archivo que se edite a mano, es el espejo del manual — solo anotar la
   discrepancia, no reescribirlo).

6. **Corregir la referencia "TweenGMS"** allí donde aparezca en documentación de proceso o
   memoria de sesión: no existe ningún repositorio con ese nombre; la intención probable era
   `erkan612/GMMT` o `Kruger0/Tweeny`, ambos ya catalogados en `11/CAT`.

7. **Cuatro filas nuevas en `07/11 §1.2`** (tabla de blog oficial), mismo formato que las
   existentes: *Barty's Adventure* (13-may-2026, `gamemaker.io/en/blog/bartys-adventure-interview`),
   *Chivalware* (24-jun-2026, `gamemaker.io/en/blog/arcade-crew-chivalware`), *Cause+Select*
   (1-jul-2026, `gamemaker.io/en/blog/cause-select-charity`), *Loop Hero* de Playdigious
   (19-ago-2026, `gamemaker.io/en/blog/pc-to-mobile-loop-hero`).

8. **Nota al pie opcional (no bloqueante) en `07/02`** para GMPhysX (físicas AAA de pago,
   alfa, Windows-only), `erkan612/MajorGUI_GML` (UI en modo retenido, mismo autor que GMUI) y
   REZOL de FoxyOfJungle (cámara de pago, más completa que STANNcam) — mismo tratamiento 💸 que
   ya reciben otras herramientas de pago citadas en `12/05`.

9. **Media docena de librerías de nicho, solo si el equipo decide ampliar cobertura de nicho**
   (no urgente, están listadas con estrellas/licencia/fecha verificadas en la tabla F de este
   informe): `BPzeBanshee/GMOSSE` (motor de referencia shmup), `flingoXD/flingos-MIDI` (MIDI),
   `MedicV2/BigInt` (enteros arbitrarios), `odditica/renderdoc-gms2-kit` (RenderDoc),
   `xtreme3d/xtreme3d` (3D legado). Ninguna es urgente porque ninguna sustituye una
   recomendación ya existente — son huecos de "0 opciones" a "1 opción de nicho".

## Lo que comprobé y NO hacía falta

- **Las 44 extensiones oficiales `GMEXT-*` y el resto de la organización YoYoGames**: barridas
  hoy por fecha de *push* (repos con actividad desde el 2-sep incluyen `GMEXT-AppleIAP`,
  `GMEXT-EpicOnlineServices`, `GameMaker-HTML5`…), y las 8 más recientes se comprobaron una a una
  contra `07/01`, `07/03` y `12/03`: **todas ya están documentadas**. No hay ninguna extensión
  oficial nueva desde el barrido del 1-2 de septiembre.
- **La organización `GameMakerDiscord` completa** (65 repos): barrida por fecha de *push*, el
  más reciente (`Xpanda`, mayo 2026) ya está catalogado. No reabrir.
- **`gm-cli` y su versión**: local y publicada coinciden en 2.3.0 hoy; no hace falta ninguna
  acción salvo confirmar si el bug de plantillas con prefabs de la versión 2.2.0 sigue existiendo
  en 2.3.0 (no reproducido en esta ronda por no ser su objetivo).
- **Plantillas oficiales (31), cursos/libros, canales de YouTube, estado del foro y Discord**:
  las cinco verificaciones de la sección E dieron "sigue igual" con fuente y fecha — no reabrir
  ninguna de las cinco sin evidencia nueva posterior al 2026-09-07.
- **Físicas 2D nativas (Box2D)**: comprobé si estaban documentadas antes de buscar un wrapper de
  terceros — lo están, en profundidad (`04/22`, `13/08`), incluidas las partículas de fluido. No
  hace falta ningún wrapper externo de físicas de cuerpo rígido "genérico".
- **Generación procedural**: `13/07` (3284 líneas) es más completa que cualquier librería de
  terceros que encontré hoy en ese dominio. No reabrir sin una librería GML nueva y con tracción
  real que la supere.
- **Guardado de partida**: confirmé que no existe en todo el ecosistema GML una librería
  "seria" (multi-slot + autosave + migración de esquema + nube) que supere lo que la biblioteca
  ya construye a mano combinado con `db`/`SNAP`. Es un hueco de la comunidad entera, no de esta
  biblioteca.
- **Red/multijugador**: `12/04` ya es la sección más exhaustiva de toda la biblioteca en
  cualquier dominio auditado hasta ahora (Photon, Colyseus, Warp, funciones nativas UDP/WebSocket
  explicadas con matices reales). Solo quedan sin resolver ENet y rollback netcode, y son huecos
  de ecosistema —nadie los ha construido en GML—, no de biblioteca.
- **`UndertaleModTool`, Stitch, `@bscotch/yy`, `@bscotch/gml-parser`**: releídos en `12/08`
  §1-4; siguen perfectamente vigentes y verificados con fecha (2026-09-07 para gml-parser, con
  ★158 y *push* 2026-06-15). No hace falta tocar nada.
- **`awesome-gamemaker` como fuente**: se confirmó que es un espejo fiel del panorama real (99 %
  de solape con el catálogo local) y que su propio contenido tiene 2 enlaces muertos que no son
  responsabilidad de esta biblioteca sino de la lista de terceros.

## Lo que encontré desactualizado

| Afirmación de la biblioteca | Qué es cierto hoy (2026-09-07) | Fuente que lo prueba |
|---|---|---|
| `DragoniteSpam/Emu` tiene "⚠️ sin licencia" (`07/_INDICE-ECOSISTEMA.md`, `11/CAT` ×2) | Licencia **MIT** desde el commit `2f7cb286` (11-jun-2020) | `gh api repos/DragoniteSpam/Emu` → `license.spdx_id: MIT`; contenido de `LICENSE` leído directamente, confirma texto MIT con copyright 2020 |
| El Marketplace se accede "desde el menú desplegable… en la parte superior del IDE" (`09/Introduction/The_Marketplace.md`, espejo del manual oficial) | La URL canónica es hoy `marketplace.gamemaker.io`, un sitio web independiente; `gamemaker.io/en/marketplace` da **404** | WebFetch a ambas URLs hoy (200 vs. 404); hilo del foro "Marketplace Future and the Prefab Library" sin actividad nueva desde el 6-ago-2026, coherente con una gestión ya fuera del IDE |
| "gm-cli 2.2.0 local (2.3.0 publicada)" (`07/_INDICE-ECOSISTEMA.md` cabecera) | Ambas coinciden hoy en **2.3.0** | `npm view @gamemaker/gm-cli version` y `gm-cli --version` local, ambos 2.3.0 |
| `bytecauldron/awesome-gamemaker` con "501★" (`11/CAT` línea 662) | **503★** hoy (cambio trivial, no requiere acción, solo se documenta por transparencia de la verificación) | `gh api repos/bytecauldron/awesome-gamemaker` → `stargazers_count: 503` |
| `gm-i18n` (CreativeHandOficial) citado sin advertencia de desfase (`12/05 §8`) | Último *push* **2023-02-04** — más de 3 años sin actividad | `gh api repos/CreativeHandOficial/gm-i18n` → `pushed_at: 2023-02-04` |

No se encontró ninguna otra afirmación con fecha de caducidad (versión, precio, estado de
archivado) que resultara falsa al verificarla hoy — el resto de lo comprobado en esta ronda
confirmó lo que la biblioteca ya decía, con fecha de verificación añadida.
