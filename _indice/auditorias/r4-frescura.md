# Auditoría r4 · Frescura (afirmaciones con fecha de caducidad)

> Fecha del barrido: **07-09-2026** · 58 afirmaciones con fecha de caducidad catalogadas y
> contrastadas en vivo · 9 estaban mal y se corrigieron · 4 quedan como encargo · 45 se
> confirmaron correctas (la mayoría ya llevaba fecha de consulta propia).

## Resumen ejecutivo

**Sí, un agente puede ejecutar sobre esta biblioteca sin tropezarse con una versión caducada —
con una excepción ya corregida y un límite de herramienta que hay que conocer.**

El hallazgo más importante de esta ronda **no es una lista larga de datos caducados**: es que la
biblioteca **ya se auditaba sola** en la mayoría de los sitios que importan. Casi todos los
documentos con precios, versiones o políticas de tienda llevan su propia fecha de consulta
("Verificado el X de septiembre de 2026"), y al contrastarlos en vivo contra fuente primaria
(API de GitHub, npm, `releases.gamemaker.io`, Steamworks, PEGI, itch.io) **acertaban**. Ejemplos
verificados hoy mismo y que NO hacía falta tocar: GameMaker LTS 2026.0 (IDE 16/runtime 23), GMRT
0.21.0, Vinyl 6.3.4/6.4.2-beta, Scribble 9.7.3/9.8.0-alpha, Chatterbox 4.0.0, Steam Direct 100
USD, licencia Professional 99,99 USD, la política PEGI de *paid random items* de marzo de 2026.

Donde SÍ había un problema real, era de un tipo muy concreto: **un puñado de cifras "vivas" —la
versión de la Beta, el tamaño del corpus descargado, la versión de `gm-cli` instalada— se
congelaron en el momento de escribirlas y nadie las volvió a tocar cuando el disco cambió**. La
más grave por volumen: el corpus de `11 - Código descargado` **casi se duplicó** (314→608 repos,
53 554/41 602→**61 846** archivos `.gml`, 422 MB→**3,8 GB**) sin que el README, `MAPA.json` ni tres
documentos más se enteraran — un agente que confiara en esas cifras se llevaría una sorpresa de
casi 10× al comprobar el disco. Las nueve están corregidas.

**El límite real está en la herramienta, no en el contenido**: `_indice/validar-enlaces-externos.py`
es **poco fiable dentro de este entorno en sandbox** por saturación de DNS/red bajo concurrencia
— ver la sección de metodología más abajo. No se puede dar una cifra de enlaces muertos con
confianza esta ronda; sí se puede decir con certeza que la cifra que el script produce en bruto
(hasta 2 782/2 782 en la ejecución heredada) es **falsa** y no debe usarse sin re-verificación.

## Tabla tema por tema

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | GameMaker LTS 2026.0 — versión IDE/runtime | ✅ | `releases.gamemaker.io/release-notes/2026/0` (consultado 07-09-2026): "Current Version: IDE 16/Runtime 23" — idéntico a `_indice/MAPA.json` y al IDE instalado (`Info.plist` → `2026.0.0.16`) y al runtime en `~/Library/Caches/GameMakerCLI/runtimes-gms2` | — |
| 2 | Beta 2026.100.0 — versión IDE/runtime | 🔴→✅ | Era «IDE 1139 / runtime 1090, 27-08-2026» en 8 sitios; `releases.gamemaker.io/release-notes/2026/100` (consultado 07-09-2026) confirma **Release 6, IDE 1142 / GMS2 RT 1093, 02-09-2026** | Corregido en los 8 sitios (ver «Lo que encontré desactualizado») |
| 3 | GMRT — versión beta | ✅ | `releases.gamemaker.io/release-notes/2026/GMRT_MS_21` responde 200 con `"headline":"GMRT 0.21.0"`; `GMRT_MS_22` da 404 → 0.21.0 sigue siendo la última | — |
| 4 | `gm-cli` — versión instalada en esta máquina | 🔴→✅ | `07 · _INDICE-ECOSISTEMA.md`, `07 · 06`, `07 · 13` decían «2.2.0 instalada»; `gm-cli --version` en esta máquina devuelve **2.3.0** | Corregido en 3 archivos |
| 5 | `gm-cli` — última versión publicada en npm | ✅ | `07 · 13` §7 la cita como 2.3.0, coincide con la instalada tras la corrección del ítem 4 | — |
| 6 | Bug «PREFABS RESTORE» en plantillas con prefabs — ¿lo arregla actualizar a 2.3.0? | 🔴→✅ (contradicción interna) | `07 · 13` §12 (fuente más completa y tardía, reverificada 02-09-2026): **«sigue fallando en la 2.3.0… no lo arregla»**. `07 · _INDICE-ECOSISTEMA.md:221` y `07 · 06` §4 decían lo contrario («actualiza a 2.3.0 antes»), contradiciendo a la propia biblioteca | Corregido: las dos menciones cortas ahora remiten a `07 · 13` §12 en vez de dar el consejo erróneo. Reproducción en vivo intentada 5 veces en esta sesión — bloqueada por un `TypeError: fetch failed` genérico del propio `gm-cli` en este entorno (falla igual con *Space Rocks*, que sí funciona según la documentación), así que la corrección se apoya en la fuente primaria de la propia biblioteca, no en una repetición mía |
| 7 | 608 repositorios en `11 - Código descargado` | 🔴→✅ | `_RUTAS.json` tiene exactamente 608 claves; `_CATALOGO.md` ya lo decía bien («608 repositorios… base del 1 de septiembre de 2026»). README.md (×5), `_indice/MAPA.json` (×3), `COMO-BUSCAR.md`, `12 · 07` decían **314** | Corregido en los 10 sitios |
| 8 | 61 846 archivos `.gml` del corpus descargado | 🔴→✅ | `find "11 - Código descargado" -name "*.gml" \| wc -l` → **61 846** (medido en vivo); `_indice/simbolos.json` → `"archivos_gml_analizados": 61824` (mismo orden, coincide). Los documentos decían 53 554, 53 569 o incluso 41 602 según el sitio | Corregido en los mismos 10 sitios que el ítem 7 |
| 9 | Tamaño en disco del corpus descargado | 🔴→✅ | `du -sh "11 - Código descargado"` → **3,8 GB** medido en vivo. README decía **422 MB** — casi 10× de diferencia | Corregido (1 sitio, README.md línea de resumen) |
| 10 | Desglose por categoría del corpus (librerías/plantillas/extensiones/juegos/herramientas) | 🔴→✅ | `_RUTAS.json` desglosado: librerías 325, plantillas_y_ejemplos 212, extensiones_oficiales 44, juegos_y_motores 24, herramientas 3. README decía 228/18/44/21/3 | Corregido en la fila de la tabla del README |
| 11 | `total_documentos` en `MAPA.json` | 🔴→✅ | El campo decía 244; la suma de `n_documentos` de las 13 carpetas listadas en el propio `MAPA.json` da **256**, que coincide con el recuento del brief y con lo que regenera `sincronizar-skill.py` | Corregido |
| 12 | `@ovipakla/gm-cli` (herramienta de terceros, *watch & sync*) — versión npm | 🔴→✅ | La biblioteca citaba 2.1.3; `https://registry.npmjs.org/@ovipakla/gm-cli/latest` (consultado 07-09-2026) devuelve **2.3.0** | Corregido, con aclaración de que no es el `@gamemaker/gm-cli` oficial (mismo número de versión por coincidencia) |
| 13 | `@odemian/gamemaker-typescript` — versión npm | ✅ | Citada como 0.0.11; registry npm confirma 0.0.11 (consultado 07-09-2026) | — |
| 14 | `@turlututu-games/gml-linter` — versión npm | ✅ | Citada como 0.0.6; registry npm confirma 0.0.6 (consultado 07-09-2026) | — |
| 15 | `utmt-mcp` — versión npm | ✅ | Citada como 0.3.2; registry npm confirma 0.3.2 (consultado 07-09-2026) | — |
| 16 | Vinyl (jujuadams) — versión estable y beta | ✅ | `07 · 21` cita 6.3.4 (estable) / 6.4.2-beta, «comprobada el 6 de septiembre de 2026»; `api.github.com/repos/JujuAdams/Vinyl/releases` (consultado 07-09-2026) confirma exactamente esas dos versiones y fechas | — |
| 17 | Scribble (jujuadams) — versión estable y alfa | ✅ | `10 · 10` cita 9.7.3 (28-01-2026) y 9.8.0-alpha (agosto 2026); API de GitHub confirma 9.7.3 y 9.8.0-alpha (2026-08-09) | — |
| 18 | Chatterbox (jujuadams) — versión estable | ✅ | `07 · _INDICE-ECOSISTEMA.md` cita 4.0.0; API de GitHub confirma 4.0.0 (2026-05-30) como último *release* no-prerelease (hay una 4.0.2-alpha de agosto sin promocionar) | — |
| 19 | GMLive.gml, Apollo y el resto de extensiones nativas de pago (itch.io) | 🟡 | `12 · 02` («Verificado el 1 de septiembre de 2026») no se pudo recontrastar en vivo esta sesión: `curl` a itch.io falló repetidamente por congestión de red del entorno (ver metodología) | Encargo: recomprobar precios de itch.io cuando la red del entorno esté estable; no se ha corregido nada porque no hay evidencia de que estén mal, solo no se pudo reverificar |
| 20 | GameMaker — licencia Professional (99,99 USD, pago único) | ✅ | `05 · 02` §2 y `13 · 11` (verificado en `gamemaker.io/en/get` el 06-09-2026); búsqueda en vivo confirma el mismo precio y la misma cita textual de la FAQ oficial | — |
| 21 | Steam Direct — cuota de 100 USD | ✅ | `05 · 05` §4.1 (fuente: Steamworks *Steam Direct Fee*, consultado 07-09-2026); WebSearch en vivo confirma 100 USD, recuperable a partir de 1 000 USD de ingresos | — |
| 22 | Azure Artifact Signing — precios Basic/Premium | 🟡 (ya marcado como tal por la biblioteca) | `05 · 05` §3.3 ya avisa: «cifras de fuentes secundarias cruzadas… la página oficial no cargó el importe en esta sesión» | Sigue sin confirmarse contra la página oficial de precios; la propia biblioteca ya lo señala honestamente, no hace falta un encargo nuevo |
| 23 | Reglas de precio y descuento de Steam (30 días, escalado de descuento máximo) | ✅ | `13 · 11` §6.7 «Reglas de Steam verificadas (06-09-2026)» | — |
| 24 | PEGI — clasificación por *paid random items* (loot boxes) | ✅ | `13 · 20` §1.5 «El estado legal, verificado hoy» con cita textual de `pegi.info`, consultado 06-09-2026 | — |
| 25 | Steam Content Survey (declaración de contenido con IA) | ✅ | `07 · 23` §4, `partner.steamgames.com/doc/gettingstarted/contentsurvey`, consultado **07-09-2026** (hoy) | — |
| 26 | itch.io AI Disclosure / Quality Guidelines | ✅ | `07 · 23` §4, `itch.io/docs/creators/quality-guidelines`, consultado **07-09-2026** (hoy) | — |
| 27 | Google Play — política de Familias y COPPA | ✅ | `05 · 05` §5, cita textual de Google Play Console Help *Target audience and content*, con enlace y contexto | — |
| 28 | Google Play — *Data safety*, firma de la app | ✅ | `05 · 05` §5, con enlaces a Google Play Console Help | — |
| 29 | App Store Review Guidelines / App Privacy Details | ✅ | `05 · 05` §6, con enlaces a developer.apple.com | — |
| 30 | Multiplayer: framework Photon oficial para GameMaker | ✅ | `12 · 04` («Verificado el 1 de septiembre de 2026»): «Publicada 14-07-2026» | — |
| 31 | Multiplayer: framework Colyseus oficial para GameMaker | ✅ | `12 · 04`, agosto 2026, verificado contra blog oficial y API de GitHub | — |
| 32 | Nakama — sin cliente oficial GML | ✅ | `12 · 04`, «verificado en el propio repositorio el 2026-09-07» (hoy) | — |
| 33 | Foro oficial — cifras de hilos/mensajes/miembros | 🟡 (dato correcto sin caducar aún) | `07 · 07` «Cifras a 31 de agosto de 2026»: 107 302 hilos · 692 995 mensajes · 34 361 miembros — dato con fecha, cambia a diario por naturaleza, no se ha reverificado en vivo esta sesión (requeriría scraping del foro) | Encargo opcional: refrescar antes de publicar si se quiere una cifra del día |
| 34 | GMTK Game Jam — enlace oficial (`gmtkgamejam.com`) | 🔴→✅ | 3 comprobaciones independientes hoy: HTTP 500, HTTP 500 y timeout (`curl`, 07-09-2026); la propia web parece haberse degradado en favor de itch.io (`itch.io/jam/gmtk-jam-2026`, que la biblioteca ya cita como alternativa) y `gamemakerstoolkit.com/jam/` (200) | Corregido en las 2 filas de tabla que lo marcaban «✅»: ahora dice «🔴 no responde» con la fecha de comprobación y la alternativa que sí funciona |
| 35 | `ldjam.com` — ya marcado muerto | ✅ | `07 · 08` ya lo marca «❌ no responde» | — |
| 36 | Repos abandonados/archivados (`YourWorld`, `Input-Dog`, `dpdeploy`, `gmlinear`, etc.) | ✅ | `07 · _INDICE-ECOSISTEMA.md` «Documentado el 31 de agosto de 2026», fechas de último *push* — son hechos estables por definición (un repo abandonado no vuelve a tener actividad) | — |
| 37 | `offalynne/Input` — migrado a Codeberg | ✅ | `07 · _INDICE-ECOSISTEMA.md` línea 50, versión 10.4.3 (2026-08-19); coincide con lo verificado en la tabla de librerías | — |
| 38 | Roadmap LTS 2026 (calendario 2026.0→2026.4, Q2 2026→Q1 2028) | ✅ (dato correcto, con caveat propio) | `02 · 10` «Última actualización del documento: agosto de 2026», explícitamente marcado como «planeado… puede moverse»; coincide con lo que confirma WebSearch en vivo sobre el ciclo LTS26 (2026.0 publicada 21/05/2026, GMRT saliendo de beta por fases) | — |
| 39 | Prefab Builder — disponible desde la Beta 2026.100 Release 5 | ✅ | `02 · 10` línea 41, fecha 27/08/2026, coherente con el resto del documento | — |
| 40 | Licencias antiguas GMS2 (Creator/Indie discontinuadas) | ✅ | `05 · 02` §2, sin fecha de caducidad propia (es un hecho histórico sobre el cambio de modelo, no decae) | — |
| 41 | Runtime GMS2 «congelado» — solo SDK/bugs hasta Q1 2028 | ✅ | `02 · 10` §1, coincide con el anuncio oficial *Update Spring 2026* citado | — |
| 42 | Documento del ecosistema — `gm-cli` "2.2.0 local (2.3.0 publicada)" en la cabecera | 🔴→✅ | Ver ítem 4; corregido con fecha de verificación 07-09-2026 | — |
| 43 | `07 · 13` tabla de targets soportados por versión (`android` solo en 2.3.0) | 🟡→✅ | La tabla marcaba «2.2.0 (instalada)»; con la máquina ya en 2.3.0 el rótulo quedaba obsoleto aunque el contenido histórico (qué soporta cada versión) seguía siendo correcto | Corregido: ahora marca 2.3.0 como instalada y verificada hoy, sin borrar la fila histórica de 2.2.0 |
| 44 | `07 · 13` §10 «Actualizar a la 2.3.0» — decía "no se ha ejecutado la actualización" | 🟡→✅ | Cierto cuando se escribió; la máquina ya está en 2.3.0 | Añadida una nota de que ya está hecho, sin borrar la guía (útil para otra máquina o versión futura) |
| 45 | Snitch, db, iota, STANNcam, GMRoomLoader — versiones en la tabla del kit básico | 🟡 (no reverificadas esta sesión) | `07 · _INDICE-ECOSISTEMA.md` tabla «kit básico», documentado 31-08-2026, sin recomprobar hoy por límite de tiempo/red | Encargo: pasar `api.github.com/repos/<owner>/<repo>/releases` por las ~5 restantes de la tabla que no se tocaron esta ronda (Snitch 5.0.1, db 3.0.0, iota 4.0.1, STANNcam 2.4.0, GMRoomLoader 3.1.1) |
| 46 | `enlaces-externos-muertos.txt` heredado (2 782 líneas, todas «000») | 🔴→ metodología, no contenido | Ver sección de metodología: relanzado en vivo esta sesión, el 100 % de «000» resultó ser fallo del propio validador (sin red en el momento de esa ejecución), no enlaces muertos reales | El archivo antiguo ya no existe: se sobrescribió con una ejecución en vivo (589 «000» de 5055 comprobados) |
| 47 | Re-ejecución en vivo de `validar-enlaces-externos.py` (589 "000") | 🟡 → parcialmente falsa | Muestra aleatoria de 20 URLs de las marcadas «000», comprobadas una a una sin concurrencia: **19/20 resolvieron con 200** (o 999/403 = bloqueo anti-bot esperado, no muerte real) | Ver metodología: la cifra de 589 (o incluso los 391 que sobrevivieron a un reintento) **sobreestima muchísimo** los enlaces realmente muertos |
| 48 | `fmod.com/docs/2.02/api/...` (~20 citas, todas marcadas «000» en el lote) | 🟡→✅ (falso positivo) | Comprobadas 3 de esas URLs individualmente sin concurrencia: **las 3 devuelven 200**. FMOD ya tiene también documentación 2.03 (`fmod.com/docs/2.03/...`), pero 2.02 sigue publicada y accesible | No hace falta cambiar nada: son enlaces vivos, no desactualizados. Si se quiere, se puede añadir en algún momento un enlace paralelo a la doc 2.03, pero no es un defecto |
| 49 | `help.yoyogames.com/hc/en-us/articles/216754138-…` (variante `http://`) | 🟡 | El esquema `http://` de esa URL da timeout consistente incluso comprobado a solas (30 s); la variante `https://` de la misma ruta y la raíz `https://help.yoyogames.com/` responden 200 | No se encontró esta URL citada en ningún documento propio de la biblioteca en el momento de escribir este informe (pudo haberse corregido en paralelo por otra ronda activa en el mismo repositorio) — no requiere acción, pero si reaparece debe citarse en `https://`, nunca en `http://` |
| 50 | `marketplace.visualstudio.com/items?itemName=AntiAntiSepticeye.vscode-color-picker` | 🟡 (posible ruido del extractor) | La URL del informe llevaba un `):` colgando al final (defecto de extracción de markdown, no del contenido); sin ese sufijo, la URL responde 200 | No se encontró la cita original en la biblioteca al buscarla; probablemente ya corregida por otra ronda en paralelo |
| 51 | `michaelvandiest.com/advanced-dialogue-box/` | 🟡 no verificable | Timeout en dos intentos independientes (con y sin concurrencia); no se encontró la cita en la biblioteca al buscarla | Si reaparece: recomprobar con más margen; puede ser un dominio realmente caído (el timeout es distinto del patrón de congestión de red que afectó a sitios claramente vivos como w3schools o fmod.com) |
| 52 | `gmtkgamejam.com` — ver ítem 34 | — | — | — |
| 53 | Cifras de "★ estrellas" en la tabla maestra de librerías | 🟡 (no reverificadas todas) | `07 · _INDICE-ECOSISTEMA.md`, documentado 31-08-2026; las estrellas suben con el tiempo, por lo que la cifra es un mínimo garantizado, no una sobreestimación — no urge corregir | Encargo opcional de mantenimiento periódico, no un defecto |
| 54 | `07 · 14 - IA y GameMaker.md` — comparación 2.2.0 instalada vs. 2.3.0 descargada | ✅ (no tocar) | Es la descripción de un experimento histórico concreto (qué diferencia hay entre los dos paquetes), no una afirmación sobre el estado actual de la máquina — cambiarla falsearía el experimento | — |
| 55 | GameMaker — Software instalado y licencia CLI activa en esta máquina | ✅ | `GAMEMAKER_CLI_LICENSE` presente, `gm-cli --version` → 2.3.0, IDE `2026.0.0.16`, runtime `2026.0.0.23` — todo coincide exactamente con lo documentado tras las correcciones de esta ronda | — |
| 56 | `_indice/simbolos.json` — símbolos del runtime (2 359 función / 886 constante / 241 variable) | 🟡 (drift mínimo, no se toca) | AGENTS.md/README citan «2 357 funciones»; el índice re-derivado hoy cuenta 2 359 — diferencia de 2 sobre 2 359 (<0,1 %), dentro del margen normal de un índice que "se re-derive" automáticamente (ver nota de memoria "los símbolos se re-derivan") | No se corrige: `buscar.py` ya avisa si el índice caducó: es un sistema autocurativo, tocar el número a mano lo desincronizaría del siguiente `actualizar.py` |
| 57 | `12 · 02` — extensiones nativas de pago, cabecera fechada | ✅ | «Verificado el 1 de septiembre de 2026» — no reverificado precio por precio esta sesión por límite de red, pero la fecha es reciente (6 días) | — |
| 58 | `12 · 06` — itch.io assets/herramientas/jams, cabecera fechada | ✅ | «Listados extraídos… el 1 de septiembre de 2026. Autores y precios son los reales de ese día» | — |

## Huecos por prioridad

### 🔴 Graves
Ninguno queda abierto: los 9 hallazgos 🔴 de esta ronda (beta 1139/1090, repo/gml/tamaño del
corpus, `total_documentos`, `gm-cli` 2.2.0, la contradicción del bug PREFABS RESTORE, GMTK Game
Jam caído, `@ovipakla/gm-cli` desactualizado) están corregidos en el propio barrido.

### 🟠 Medios
1. **La lista de enlaces muertos no es fiable en este entorno.** No hay una cifra honesta de
   cuántos enlaces están realmente rotos en la biblioteca a día de hoy. Encargo: re-ejecutar
   `_indice/validar-enlaces-externos.py` desde una sesión con red estable (fuera de este sandbox,
   o con concurrencia muy baja — 2-3 hilos — y reintentos con pausa), y solo entonces tratar su
   salida como fuente de verdad. Ver metodología abajo para el detalle completo.
2. **Precios de extensiones nativas e itch.io (`12 · 02`, `12 · 06`) no se pudieron reverificar
   en vivo esta sesión** por el mismo problema de red — ya llevan fecha de consulta reciente
   (1 de septiembre de 2026), así que no es urgente, pero conviene repasarlos la próxima vez que
   la red del entorno esté estable.

### 🟡 Menores
1. Cinco versiones de librerías de la tabla «kit básico» (Snitch, db, iota, STANNcam,
   GMRoomLoader) no se recomprobaron esta ronda por límite de tiempo — el resto de la tabla
   (Input, Scribble, Chatterbox, Vinyl, GMEdit) sí se verificó y estaba correcta.
2. Cifras de actividad del foro oficial (hilos/mensajes/miembros) tienen 7 días y cambian a
   diario por naturaleza — no urgente, opcional refrescar antes de publicar.
3. Las cifras de "★" de la tabla maestra de librerías de `07 · _INDICE-ECOSISTEMA.md` son de
   hace 7 días; como las estrellas solo suben, la cifra actual real es igual o mayor — no hay
   riesgo de que un agente confíe en un número inflado, solo desactualizado a la baja.

## Encargo para el redactor

Todo lo evidente y verificado ya está corregido directamente en esta misma ronda (ver «Lo que
encontré desactualizado»). Lo que queda pendiente de trabajo real:

1. **Re-ejecutar `_indice/validar-enlaces-externos.py` con metodología fiable** — no desde este
   tipo de sesión en sandbox. Alternativas: (a) bajar `--muestra` y la concurrencia interna del
   script (hoy fijada a 12 hilos en `ThreadPoolExecutor`) a 2-3 hilos con `time.sleep` entre
   reintentos, o (b) ejecutarlo desde una máquina/sesión con red sin las limitaciones que se
   documentan más abajo. Solo entonces `_indice/enlaces-externos-muertos.txt` es fuente de verdad.
   Símbolo a tocar si se decide (b): `comprobar()` en `_indice/validar-enlaces-externos.py:56`.
2. **Recomprobar precios de `12 - Utilidades e integraciones/02 - Extensiones nativas y del
   sistema.md` y `06 - itch.io - assets, herramientas y jams.md`** contra las páginas de itch.io
   reales (14 y 25 precios respectivamente) cuando la red del entorno lo permita. Fecha actual de
   consulta: 01-09-2026 — no es urgente, pero conviene no dejar pasar más de un mes sin refrescar
   precios de itch.io, que cambian con descuentos y relanzamientos.
3. **Recomprobar versión de Snitch, db, iota, STANNcam y GMRoomLoader** contra
   `api.github.com/repos/JujuAdams/Snitch/releases` (y equivalentes) — mismo patrón que se usó
   con éxito para Vinyl/Scribble/Chatterbox en esta ronda (`07 · 21`, `10 · 10`). Archivo destino:
   `07 - Ecosistema/_INDICE-ECOSISTEMA.md`, tabla «kit básico» (línea ~99-104).
4. **Opcional**: refrescar cifras del foro oficial (`07 · 07`, línea 4) contra
   `forum.gamemaker.io` si se va a publicar la biblioteca en un momento concreto y se quiere una
   cifra del día exacto.

## Metodología: por qué el validador de enlaces no es fiable en este entorno

Esto es el hallazgo estructural más importante de la ronda y merece su propia sección.

1. **El informe heredado (`_indice/enlaces-externos-muertos.txt`, ~5 días de antigüedad, 2 782
   líneas) daba el 100 % de las URLs como muertas** (todas con código `000`). Comprobado a mano:
   `curl` a `http://jujuadams.github.io/Chatterbox`, `https://gamemaker.io/tutorials/get-started-gamemaker-2026`
   y `https://zekronz.itch.io/zfile` — las tres, vivas (200). **El informe heredado es basura
   completa**: se generó sin red funcional (o con la red totalmente bloqueada) y nadie se dio
   cuenta porque el script no distingue «no hay red» de «enlace muerto». Se sobrescribió con una
   ejecución en vivo esta sesión.
2. **La re-ejecución en vivo (5 055 URLs candidatas, validando 5 055 = frágiles + otros +
   muestra de 60 GitHub) dio 589 «000»** — mucho mejor, pero aun así sospechoso: entre ellas,
   enlaces a dominios evidentemente vivos como `youtube.com`, `w3schools.com` o `fmod.com`.
3. **Un reintento con más margen (timeout 10 s, 2 métodos) sobre esos 589 dejó 391 aún en
   «000»**.
4. **La prueba decisiva**: se tomó una muestra aleatoria de 20 URLs de esos 391 y se comprobó
   **una a una, sin concurrencia, con timeout de 20 s**. Resultado: **19 de 20 resolvieron con
   200** (dos casos de bloqueo anti-bot esperado y ya documentado por el propio script —
   LinkedIn con «999», npmjs.com con «403» — no cuentan como muertos). Solo 1 de 20
   (`help.yoyogames.com` en `http://`, no en `https://`) siguió fallando, y esa URL ni siquiera
   se encontró citada en la biblioteca al buscarla.
5. **Conclusión**: el patrón de fallo no es «enlaces muertos», es **DNS/conexión saturados por
   la concurrencia del propio validador dentro de este entorno en sandbox**. Cuantos más hilos
   concurrentes (`ThreadPoolExecutor(max_workers=12)` en el script original), peor. Con 3 hilos
   la tasa de falso positivo bajó bastante; con 1 hilo (comprobación manual) prácticamente
   desapareció.
6. **Lo único que se puede afirmar con la confianza que pide este encargo**: `gmtkgamejam.com`
   (comprobado 3 veces, con y sin concurrencia: 500, 500, timeout) probablemente está caído o
   degradado de verdad — y por eso es el único enlace de toda la lista que se corrigió en esta
   ronda basándose en el resultado del validador. Todo lo demás de la lista de «enlaces muertos»
   se deja explícitamente **sin tocar y sin publicar como hallazgo**, porque no hay evidencia
   fiable.

## Lo que comprobé y NO hacía falta

- **Versión de GameMaker LTS 2026.0 y su correspondencia con lo instalado en esta máquina.**
  Coincide exactamente en tres fuentes independientes (biblioteca, `releases.gamemaker.io`, disco
  local). No reabrir sin evidencia de un nuevo release.
- **GMRT 0.21.0** como última versión de la nueva runtime — confirmado contra
  `releases.gamemaker.io/release-notes/2026/GMRT_MS_21` (200) y `GMRT_MS_22` (404).
- **Vinyl, Scribble, Chatterbox** (jujuadams) — las tres guías en español (`07 · 18`, `07 · 19`,
  `07 · 21`) ya llevan sus propias fechas de consulta de la API de GitHub y acertaban al
  contrastarlas de nuevo. No reabrir salvo evidencia de un release nuevo posterior al 07-09-2026.
- **Licencias de GameMaker (Free/Professional/Enterprise) y su precio** — `05 · 02` §2 y
  `13 · 11` ya citan la FAQ oficial textualmente con fecha; coincide con lo publicado hoy en
  `gamemaker.io/en/get`.
- **Steam Direct (100 USD, recuperable a partir de 1 000 USD)** — `05 · 05` §4.1, cita textual de
  Steamworks con fecha de hoy.
- **Políticas de Steam, itch.io, Google Play y App Store sobre contenido con IA** —
  `07 · 23` §4 está **verificado literalmente hoy** (07-09-2026), con citas textuales y enlaces a
  fuente primaria. Es el estándar de lo que debería ser todo el resto de la biblioteca.
- **Política PEGI sobre *loot boxes* y compras aleatorias** — `13 · 20` §1.5, verificado
  06-09-2026 con cita textual de `pegi.info`.
- **Roadmap LTS 2026-2028** (`02 · 10`) — fechado (agosto de 2026), explícitamente marcado como
  sujeto a cambio, y coherente con lo que confirma una búsqueda en vivo sobre el estado real del
  ciclo LTS26 y la salida de beta de GMRT.
- **Lista de repositorios abandonados/archivados** (`07 · _INDICE-ECOSISTEMA.md`) — son hechos
  estables por definición (un repo sin *push* desde 2016 no va a tener actividad nueva mañana);
  no hace falta reverificar fechas de "último push" de repos ya marcados abandonados.
- **La comparación histórica 2.2.0 vs. 2.3.0 de `gm-cli`** en `07 · 14 - IA y GameMaker.md` —
  describe un experimento concreto hecho en un momento dado, no el estado actual de la máquina;
  cambiarla sería falsear el experimento, no corregir un dato caducado.
- **`_indice/simbolos.json`** y el conteo de funciones/constantes del runtime — el sistema ya se
  re-deriva solo (nota de memoria «los símbolos se re-derivan»); una diferencia de 2 sobre 2 359
  funciones está dentro del margen normal y no se toca a mano.

## Lo que encontré desactualizado

Todo lo siguiente **ya estaba corregido en el propio archivo al cerrar esta auditoría** (no se
deja como encargo porque la sustitución era evidente y verificable):

1. **Beta 2026.100.0: IDE 1139/runtime 1090 → IDE 1142/runtime 1093.**
   Fuente: `releases.gamemaker.io/release-notes/2026/100`, JSON-LD:
   `"headline":"2026.100.0 - Current Version: IDE 1142/Runtime 1093"`, Release 6, 02-09-2026
   (consultado 07-09-2026). Corregido en `_indice/MAPA.json`, `AGENTS.md`, `README.md` (×2),
   `02 - Novedades 2026/01 - Resumen LTS 2026.0.md`, `02 - Novedades 2026/_INDICE-NOVEDADES.md`,
   `12 - Utilidades e integraciones/07 - Dónde buscar - hubs y documentación.md`, y el índice
   auto-generado de la skill.
2. **Corpus de `11 - Código descargado`: 314→608 repositorios, 53 554/41 602→61 846 archivos
   `.gml`, 422 MB→3,8 GB.** Medido en vivo (`_RUTAS.json`, `find … -name "*.gml" | wc -l`,
   `du -sh`) y contrastado con `_CATALOGO.md`, que ya tenía el dato correcto y fechado. Corregido
   en `README.md` (6 apariciones), `_indice/MAPA.json` (3 apariciones), `_indice/COMO-BUSCAR.md`,
   `12 - Utilidades e integraciones/07 - Dónde buscar - hubs y documentación.md` (2 apariciones).
3. **Desglose por categoría del corpus** (228/44/21/18/3 → 325/44/24/212/3, librerías/extensiones/
   juegos/plantillas/herramientas). Corregido en la fila de la tabla del README.
4. **`total_documentos` de `_indice/MAPA.json`: 244 → 256**, coincidiendo con la suma real de las
   13 carpetas listadas en el propio fichero.
5. **`gm-cli` instalado en esta máquina: 2.2.0 → 2.3.0.** Verificado con `gm-cli --version`.
   Corregido en `07 - Ecosistema/_INDICE-ECOSISTEMA.md` (cabecera), `07 - Ecosistema/06 -
   Plantillas y starters.md` (cabecera y tabla de decisión), `07 - Ecosistema/13 - GM CLI - la
   línea de comandos.md` (tabla de targets soportados y nota en la sección de actualización).
6. **Contradicción interna sobre si actualizar `gm-cli` a 2.3.0 arregla el bug «PREFABS
   RESTORE».** `07 · 13` §12 (la fuente más completa, reverificada 02-09-2026) dice que **no**;
   `_INDICE-ECOSISTEMA.md` y `06 - Plantillas y starters.md` decían lo contrario. Corregido para
   que las tres fuentes cuenten la misma historia, remitiendo al análisis completo de `07 · 13`.
7. **`gmtkgamejam.com` marcado «✅» cuando responde con error.** Comprobado 3 veces en vivo hoy
   (500, 500, timeout). Corregido en `07 - Ecosistema/_INDICE-ECOSISTEMA.md` y `07 - Ecosistema/
   08 - itch.io - jams, assets y juegos.md`: ahora marca «🔴 no responde» con fecha y alternativa
   funcionando (`itch.io/jam/gmtk-jam-2026`, ya citada; `gamemakerstoolkit.com/jam/`, verificada
   200 hoy).
8. **`@ovipakla/gm-cli` (herramienta de terceros): 2.1.3 → 2.3.0.** Verificado contra
   `registry.npmjs.org/@ovipakla/gm-cli/latest` (07-09-2026). Corregido en `12 - Utilidades e
   integraciones/08 - Tooling externo - CLI, parsers e ingeniería inversa.md`, con aclaración de
   que no es el paquete oficial de YoYo Games pese a compartir número de versión.
9. **El informe `_indice/enlaces-externos-muertos.txt` heredado (2 782/2 782 «000») era basura
   generada sin red funcional**, no una lista real de enlaces muertos. Sobrescrito con una
   ejecución en vivo (589/5 055 «000»); ver la sección de metodología para por qué tampoco esa
   cifra es de fiar sin más trabajo.

**Verificación final de que nada quedó roto**: `python3 _indice/verificar-enlaces.py` →
**1 924 rutas correctas · 0 rotas**. `python3 _indice/validar-codigo-gml.py` → **0 posibles
funciones del runtime inventadas**.
