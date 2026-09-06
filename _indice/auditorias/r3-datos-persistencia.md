# Auditoría r3 · Datos, guardado, persistencia, live-ops y telemetría

> 2026-09-06 · 93 temas evaluados · **54 cubiertos** (58 %) · **17 parciales** (18 %) · **22 faltan** (24 %)
> Método: lectura íntegra de `01/14`, `06/scr_save_load.gml`, `04/20`, `13/06 §3.8-3.10`, `13/01
> §9`, `13/20`, `04/25`, `04/28 §7`, `08/16-17` + `python3 _indice/buscar.py`/`--todo`/`--texto` +
> `grep -rn` sobre toda la biblioteca (excluidos `Lumbre/` y `GameMaker_Fuentes/`) + verificación
> símbolo a símbolo. Trabajo repartido en 3 sub-auditorías paralelas (nube/ajustes/datos de
> contenido · seguridad/GDPR · testing/versionado/live-ops) y cruzado por mí con lectura directa
> de las citas más decisivas y con las auditorías `r3-multijugador-online.md` y
> `r3-procedural-niveles.md` para no duplicar sus hallazgos.

## Resumen ejecutivo

El núcleo de guardado está en un nivel notablemente más maduro de lo que sugeriría auditarlo desde
cero: `13·06 §3.10` tiene migración encadenada real (escalones acumulativos v0→v1→v2→v3, campos
nuevos con `??=`, campos eliminados con `variable_struct_remove`) y un autoguardado con criterio
explícito de cuándo disparar y un indicador visual — mejor que la media del oficio. La seguridad
de rankings también resultó sorprendentemente sólida (`13·10 §14`: plausibilidad de puntuación +
replay firmado con re-simulación server-side). Pero hay un **defecto activo y verificado, no un
hueco**, que es el hallazgo más grave de esta ronda: **10 documentos de `04 - Recetas por
género`** (los que un agente consulta primero para implementar un género) enseñan a guardar
partidas escribiendo en `working_directory` — la zona de **solo lectura** según el propio `01·14
§1` y según la advertencia explícita del script canónico `scr_save_load.gml` ("NO uses
working_directory") — código que funciona en el IDE y se rompe en cualquier build exportada. El
segundo hallazgo importante es de **visibilidad, no de contenido**: iCloud y Google Play Saved
Games con resolución de conflictos real (eventos, políticas automáticas) sí existen, mirando la
documentación de las extensiones oficiales, pero son invisibles desde `04·20`/`01·14`, así que un
lector normal concluiría erróneamente que no existen. Los huecos de contenido genuino más caros
son: **live-ops técnico** (remote config, feature flags, versión mínima, MOTD, mantenimiento — cero
líneas, solo un argumento de diseño de por qué NO hacerlo), **telemetría enviada de verdad por
HTTP** (existe `http_request` pero nunca se conecta con `telemetria_volcar`), **depuración de saves
en producción** (sin backup rotativo, sin inspector, sin logging persistente) y **protección de
datos de menores/GDPR** más allá de una frase que nombra correctamente el RGPD.

## Tabla tema por tema

### Guardado — qué y cómo

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | Qué guardar y qué no (estado derivable vs. fuente de verdad) | 🔴 | Ninguna. `13·06 §3.10` clasifica *dónde* va cada clase de dato, pero ningún documento dice explícitamente "no guardes lo que puedes recalcular" (FPS, frame de animación en curso, cámara temporal) | Un principio explícito con 2-3 ejemplos de qué NO guardar porque se recalcula al cargar |
| 2 | Serializar datos puros, nunca handles | ✅ | `01·14 §8` ("El impacto de los handles en los guardados", con cita literal del manual y ejemplo MAL/BIEN) | — |
| 3 | `json_stringify`/`json_parse` de structs anidados | ✅ | `01·14 §8` completo (7 advertencias numeradas, `inhibit_string_convert`, profundidad máx. 128) | — |
| 4 | Structs anidados como forma del save | ✅ | `01·14 §9` (`guardar_partida()`/`cargar_partida()` con jugador/globales anidados); `06/scr_save_load.gml` (sobre con `version`+`fecha`+`datos`) | — |
| 5 | IDs estables entre entidades (nunca el `id` de instancia) | ✅ | `13·06` checklist línea 1114 ("nunca un handle de asset ni un ID de instancia"); `04·06:972` (`room_identifier` propio); `04·14:119` (`net_id`); `04·09` (`unique_id` de cadena) | Es un principio repetido en 4 sitios sin una sección canónica única que los enlace entre sí |
| 6 | Referencias circulares al serializar a JSON | 🟡 | Sin advertencia propia; solo rastro indirecto en la ficha de la librería de terceros catalogada `Elephant` (`07·02:273`), que se anuncia como solución a esto | Una línea en `01·14 §8` avisando de qué pasa (no probado si `json_stringify` cuelga, trunca o lanza excepción) |
| 7 | Guardar un mundo grande / streaming por chunks / solo zonas modificadas | ✅ | `04·09 §4.6, §5.4` (`ChunkData`, patrón *diff* con `tiles_modificados`/`nodos_talados`, semilla+coordenadas); ya confirmado independientemente por `r3-procedural-niveles.md` filas #41-42, #51 | El propio código de este ejemplo (`survival_save()`) tiene el defecto de `working_directory` (ver fila 39) |
| 8 | Guardado sin congelar el juego (asíncrono / repartido en frames) | 🔴 | `01·15` no menciona "guardado" ni una vez; `01·14` solo usa `buffer_save_async` como truco de INI-como-string en HTML5, nunca como técnica de rendimiento | Con un sistema de chunking ya construido (`04·09`) para mundos grandes, no hay ninguna guía de repartir la serialización en varios fotogramas |
| 9 | Autoguardado: cuándo disparar, escritura segura, indicador | ✅ | `13·06 §3.10` "Autoguardado" (tabla de 4 momentos con sí/no razonado, ranura `"auto"` dedicada, bandera `autoguardado_bloqueado`, icono en Draw GUI) | — |
| 10 | Ranuras múltiples con metadata rica (thumbnail, tiempo jugado, %) | 🟡 | `scr_save_load.gml::save_list()` da solo slot/existe/versión/fecha. Miniatura sí existe en `04·10 §5.8` (captura de `application_surface`); tiempo jugado en `04·06`/`04·04` | Nada integra las 4 piezas en una sola función; falta enlazar las tres implementaciones reales |
| 11 | Guardado rápido / carga rápida (quicksave-quickload) | 🔴 | Cero resultados en toda la biblioteca | Una tecla dedicada (F5/F9 o similar) que reutilice `save_game("quicksave", …)` |
| 12 | Guardar arrays y `ds_map`/`ds_list` dentro del save | ✅ | Arrays: directos con `json_stringify` (`01·14 §8`); `ds_map`/`ds_list`: `json_encode()` (`01·14 §8` punto 7, `08·13:798-868` con 4 ejemplos) | — |
| 13 | Structs con constructor/método: qué se pierde al serializar | ✅ | `08·15` "Serializar structs con constructores": *"`json_stringify` guarda los datos, pero no el constructor"* + técnica de reconstrucción por nombre | — |
| 14 | Separar el guardado por clase: Configuración / Progreso persistente / Estado de partida | ✅ | `13·06 §3.10` tabla completa (qué es, dónde, cuándo se escribe, ejemplos) | — |

### Robustez

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 15 | Corrupción por apagón / cierre a mitad de escritura (motivación) | ✅ | `scr_save_load.gml` cabecera: *"si el juego se cierra a medias, la partida sigue intacta"* | — |
| 16 | Escritura atómica: temporal + validar + reemplazar | ✅ | `scr_save_load.gml::save_game()` completo (3 pasos: escribir en `.tmp`, releer y validar, `file_delete`+`file_rename`) | — |
| 17 | Copia de seguridad / backup rotativo de guardados anteriores | 🔴 | Confirmado ausente: ni en `scr_save_load.gml` (solo `.tmp`+reemplazo), ni en `13·06 §3.10`, ni en el resto de la biblioteca | Guardar N copias rotando nombres para recuperar una partida de hace 2 guardados |
| 18 | Checksum/hash de integridad usado como mecanismo de RECHAZO | 🔴 | `01·14 §12` lo menciona suelto (`md5_string_utf8`, sin comparación). **Defecto verificado**: `13·10 §14.3` calcula `sha1_string_utf8(...)` en `replay_cerrar()` con el comentario "sella el paquete", pero `replay_verificar()` (mismo documento, líneas siguientes) **nunca lee ni compara ese hash** — solo re-simula y compara la puntuación final. Ya apuntado desde el ángulo de red por `r3-multijugador-online.md` fila A12 | El flujo completo (calcular → guardar aparte → recalcular al leer → comparar → rechazar) no existe para ningún caso, ni siquiera para el replay que dice usarlo |
| 19 | Detectar un save manipulado a mano | 🟡 | `scr_save_load.gml::load_game_safe(_slot, _validador)` acepta un validador externo; ejemplo mínimo real en `06/README.md:194-197` (`_d.vida > 0`) | Falta un validador con varias reglas a la vez, no solo una condición suelta |
| 20 | Recuperar de un save roto (fallback a backup) | 🔴 | No hay backup (fila 17), así que no hay de dónde recuperar; `load_game_raw` solo devuelve `undefined` si el JSON es inválido | Sin backup rotativo, este tema no se puede resolver — depende de cerrar la fila 17 primero |
| 21 | Qué hacer si falla el guardado | ✅ | `scr_save_load.gml::save_game()` devuelve `false` y registra un mensaje en cada uno de sus 3 pasos de fallo posible | — |
| 22 | Validación de esquema al cargar (tipos, campos obligatorios) | ✅ | `scr_save_load.gml::load_game_raw()` (`struct_exists` de `version`/`datos`); `13·01::balance_cargar()` (existe, parsea, es struct, tiene `version`) | — |

### Versionado y migración

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 23 | Número de versión en el save | ✅ | `scr_save_load.gml` (`SAVE_VERSION`), `01·14 §9` (`VERSION_GUARDADO`), `13·06` (`VERSION_GUARDADO`) | — |
| 24 | Migrar de v1 a v5 **en cadena** (escalones acumulativos) | ✅ | `13·06 §3.10` (líneas 638-667): `if (_v < 1) {...} if (_v < 2) {...} if (_v < 3) {...}`, con la regla explícita "nunca un `switch`: un guardado de la v0 tiene que poder llegar a la v5 pasando por todas" | `01·14 §13` y `scr_save_load.gml` (que solo tienen un hook único) no enlazan a este patrón — es una desconexión de enlace, no de contenido |
| 25 | Campos nuevos con valor por defecto al migrar | ✅ | `13·06 §3.10:661-663` (`_d.dificultad ??= Dificultad.NORMAL`) | — |
| 26 | Campos eliminados o renombrados entre versiones | 🟡 | Eliminación: ✅ `13·06 §3.10:657-660` (`variable_struct_remove`). Renombrado: 0 resultados en toda la biblioteca | Un escalón de ejemplo que renombre una clave (leer la vieja, escribir la nueva, borrar la vieja) — trivial mostrarlo, no está |
| 27 | Saves de una build de demo cargados en el juego final | 🔴 | Cero resultados en toda la biblioteca | Cualquier mención de compatibilidad de saves entre build de demo y build completa del mismo juego |
| 28 | Checklist de ingeniería: no romper partidas tras un parche | 🟡 | `13·11 §7:887` (una frase: "un parche que toca el formato de guardado sube el MAYOR y avisa antes de aplicarse"); `13·06 §4.3` checklist de arquitectura ("el guardado tiene `version` y existe `partida_migrar`") | Un checklist dedicado de release (distinto del argumento de negocio de `13·20 §1.8`): probar saves de la build anterior, verificar que la cadena cubre todos los saltos, no borrar migraciones aún en uso |

### Seguridad de datos

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 29 | Cifrar el save de verdad (AES/simétrico real) | 🟡 | Nativo: 0 resultados (`--listar aes`/`crypt`/`encrypt`). Sí hay 2 extensiones de terceros **ya catalogadas**: `Lock-And-Key` (`11/_CATALOGO.md:127`) y `GameMaker-Save` (XChaCha20-Poly1305, `11/_CATALOGO.md:677`) | Ninguna está enlazada desde `01·14 §12` (donde hoy solo aparece base64) — es enlazar, no reescribir |
| 30 | Ofuscar sin cifrar, y por qué es solo fricción | ✅ | `01·14 §12` ("base64 NO es seguridad. Solo evita la edición casual") + `13·10 §14.5` (por qué, con más detalle técnico) | — |
| 31 | Anti-trampas local: por qué es una carrera perdida | ✅ | `13·10 §14.1` ("El cliente es territorio enemigo"), `04·14 §2.2` ("Nunca confíes en el cliente"), `12·04:86` | — |
| 32 | Hash/firma con `buffer_` para detectar edición | 🔴 | Mismo defecto que la fila 18: se calcula (`buffer_md5`/`sha1`/`crc32` documentados en `08·16`) pero nunca se usa para comparar y rechazar en ningún flujo real | — (depende de cerrar la fila 18) |
| 33 | Firmar y validar un ranking/leaderboard online (autoridad de servidor) | ✅ | `13·10 §14.2` (`puntuacion_es_plausible`, rechaza valores físicamente imposibles) + `§14.3` (replay firmado + re-simulación server-side — autoridad real, no teatro). Ya evaluado por `r3-multijugador-online.md` fila I5 (✅) | Falta un ejemplo de **backend HTTP propio** no-Steam (ya señalado por esa misma auditoría, fila I2 — no lo dupliques, enlaza) |
| 34 | `buffer_md5`/`buffer_sha1`/`buffer_crc32`: dónde se calculan | ✅ | `08·16` "Hashes y sumas de comprobación" (referencia completa de las 3 funciones) | Sin workflow real de uso (ver filas 18/32) |
| 35 | Validador de save que detecta valores imposibles (vida negativa, nivel fuera de rango, dinero absurdo) | 🟡 | Patrón de rango sí existe pero aplicado a otra cosa: `13·10 §14.2` (`puntuacion_es_plausible`, techo por diseño + máximo teórico); ejemplo de una sola condición para saves en `06/README.md:194-197` | Un validador unificado con varias reglas de rango a la vez, aplicado a un save general (no solo a una puntuación) |
| 36 | Sanear rutas de archivo controladas por datos externos (path traversal) | ✅ | `04·43` checklist: *"Nunca construyas una ruta de archivo concatenando un campo del manifiesto sin sanear: valida que no contenga `..`"* | — |

### Rutas y sistema de archivos

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 37 | `game_save_id` | ✅ | `01·14 §1` (tabla de las dos áreas), `scr_save_load.gml` (regla nº 3 de la cabecera), `04·28 §7.1` | — |
| 38 | `working_directory` vs. save area: la regla de resolución | ✅ (doc.) 🔴 (uso real) | Documentado con precisión en `01·14 §1` y `05·03:508,676` (glosario). **Defecto sistémico verificado**: 10 documentos de `04 - Recetas por género` (03, 04, 05, 06, 07, 09, 10, 11, 12, 15 — 15 ocurrencias) escriben partidas con `file_text_open_write(working_directory + "archivo.json")`, contradiciendo la regla de la propia biblioteca y la advertencia explícita de `scr_save_load.gml` ("NO uses `working_directory`"). Solo `04·28 §7.1` lo hace bien | Corregir las 15 ocurrencias a `game_save_id + "archivo.json"` o a un nombre de archivo suelto (que resuelve solo al save area) |
| 39 | Sandbox por plataforma (dónde está el save area en cada SO) | ✅ | `01·14 §1` tabla completa (Windows/HTML5/macOS/Ubuntu/iOS/Android) | — |
| 40 | Permisos de escritura en móvil (Android runtime permissions) | ✅ | `04·28 §7.2` completo: `os_check_permission`/`os_request_permission`, las 3 constantes, evento Async System, lista de permisos "peligrosos" | — |
| 41 | Permisos en consolas | 🔴 | Solo Xbox Live/UWP tangencial (`04·20 §6`, centrado en servicios, no en permisos de archivo); consolas nativas fuera de alcance documentado por NDA (`04·20 §6.7`) | Correcto no inventar nada aquí — es un límite de cobertura honesto, no un hueco explotable |
| 42 | `file_exists` antes de leer/escribir | ✅ | Uso extendido en `scr_save_load.gml`, `01·14 §9` | — |
| 43 | Included Files: acceso de solo lectura y regla de resolución | ✅ | `01·14 §1` (tabla + "consecuencias prácticas": escribir copia el original del bundle al save area) | — |
| 44 | Diferencias entre plataformas (HTML5 sin sistema de archivos real) | ✅ | `01·14 §1` (límite de localStorage 1-5 MB), `§3` (tabla de particularidades iOS/macOS/HTML5) | — |

### Formatos

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 45 | JSON (`json_stringify`/`json_parse`) | ✅ | `01·14 §8` completo | — |
| 46 | INI | ✅ | `01·14 §4` completo (10 funciones, truco de INI-como-string para HTML5) | — |
| 47 | CSV (`load_csv`, pipeline de hoja de cálculo) | ✅ | `08·17:1343-1370` (`load_csv` → DS grid); `13·01 §4.4-4.5` (pipeline completo con 5 reglas de formato) | — |
| 48 | Buffers binarios a medida | ✅ | `01·14 §7` (tipos, alineación, patrón de lectura/escritura); `08·16` referencia completa | — |
| 49 | `buffer_save`/`buffer_load` | ✅ | `01·14 §7`, `08·16` | — |
| 50 | `buffer_compress`/`buffer_decompress` | 🟡 | Mencionado en `01·14 §7`, `08·16`, `13·07` — solo como entrada de lista de funciones, sin ejemplo integrado en un flujo de guardado real | Un ejemplo: comprimir el JSON de un save grande antes de `buffer_save`, con la cifra de cuánto ahorra |
| 51 | Tamaño y velocidad: JSON vs. binario, cuándo cada uno | 🔴 | Cero comparación explícita en toda la biblioteca (verificado por grep dedicado) | Una tabla de decisión: JSON (legible, más grande, más lento de parsear) vs. buffer binario (compacto, rápido, ilegible) — cuándo compensa cada uno |
| 52 | Buffer con estructura mixta (tipos fijos + strings variables) | ✅ | `01·14 §7` "Leer y escribir: el patrón" (mezcla `buffer_string`+`buffer_u16`+`buffer_f32` en el mismo buffer) | Sin el nombre técnico "estructura mixta" explícito, pero el patrón está |

### Datos de contenido (data-driven)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 53 | Definir el contenido en archivos externos vs. hardcodear | ✅ | `13·01 §9.1-9.3` (tabla de dónde vive cada dato + `balance_cargar`/`balance_guardar`/`balance_restaurar`); `13·06 §3.8` (`catalogo_leer`, `enemigo_crear` con `instance_create_layer` + struct) | — |
| 54 | Hoja de cálculo (Excel/Sheets) → CSV/JSON como pipeline | ✅ | `13·01 §4.4-4.5` (diagrama + 5 reglas: `id` en snake_case, una fila = una entidad, sin celdas combinadas…) | — |
| 55 | Validación de datos de contenido al cargar (rangos, tipos) | 🟡 | `balance_cargar()` valida existencia/parseo/versión (aviso, no bloqueo); `enemigo_crear()` valida clave y `asset_get_index() != -1` con `registro_error()` | No hay validación de **rangos** (`hp > 0`) ni un validador que recorra todo el catálogo de una vez al arrancar y liste todas las entradas mal formadas juntas |
| 56 | Recarga en caliente (hot reload) de código/assets en desarrollo | 🟡 | De **números** de balance: ✅ nativo y gratis (`13·01 §9.4`, Debug Overlay `dbg_slider` + `ref_create`). De **código/assets**: solo GMLive.gml de YellowAfterlife (`12·01 §8`), de pago (29,95 $) y **no descargada** en la biblioteca | — |
| 57 | Herramientas de autor para diseñadores no programadores | 🟡 | Para niveles: Tiled/LDtk (`12·05`); para localización: `Localize`/`small_pp_localization_tool` (sincroniza con Google Sheets) | Para balance/contenido general no hay herramienta de autor dedicada: el "editor" es la propia hoja de cálculo |
| 58 | Tablas de balance como datos vs. como código | ✅ | `13·01 §9.1` tabla completa | — |
| 59 | Validar referencias cruzadas entre catálogos | ✅ | `13·06 §3.8::enemigo_crear()` (comprueba que el objeto/sprite del catálogo existe de verdad en el proyecto antes de instanciar) | — |

### Nube

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 60 | Steam Cloud | ✅ | `04·20 §5` (guardar/cargar con fallback local+nube) | Gestión de cuota (`steam_get_quota_total`/`steam_get_quota_free`, documentadas en `GMEXT-Steamworks/docs/cloud.js:42-70`) no está enlazada ni mencionada |
| 61 | iCloud (Apple) | ✅ | `GMEXT-GameCenter/docs/Quick_Start_Guide.md:118-136`: *"Saved games are stored in the player's iCloud account"*, API completa (`gamecenter_saved_games_save/fetch/callback_subscribe/resolve_conflict`) verificada línea a línea | **Invisible desde el camino narrativo**: no aparece en `04·20` ni `01·14`, solo en la documentación de la extensión — un lector normal concluiría que no existe |
| 62 | Google Play Saved Games (nube, distinto de logros) | ✅ | `GMEXT-GooglePlayServices/docs/savedgames.js` (291 líneas): API completa con metadata (`progress_value`, `played_time_millis`, `cover_image_path`) | Mismo problema de visibilidad que la fila 61 |
| 63 | Conflictos de guardado entre dispositivos | ✅ | GameCenter: evento `"conflict"` con `conflict_id`; Google Play: `PlayServicesSnapshotOpenInfo.is_conflict` | Steam Cloud lo resuelve el propio cliente fuera del juego (correcto no documentar código que no existe); ningún documento narrativo menciona el problema en prosa general |
| 64 | Resolución de conflictos (criterio) | ✅ | `gamecenter_saved_games_resolve_conflict` (elección manual); `PlayServicesSavedGamesConflictPolicy` con 4 políticas automáticas ya definidas (`LongestPlaytime`, `LastKnownGood`, `MostRecentlyModified`, `HighestProgress`) | Mismo problema de visibilidad |

### Ajustes del jugador

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 65 | Separar ajustes de partida (progreso) de ajustes de sistema | ✅ | `04·25 §5.6` (cita explícita a `13·06 §3.10`); `13·06 §3.10` tabla de 3 clases | — |
| 66 | Ajustes por perfil de usuario (varios jugadores, mismo dispositivo) | 🔴 | `04·25 §5.4` dice explícitamente "esto NO es multijugador local independiente" — son solo ranuras de mando físico, no perfiles de guardado. 0 resultados de "perfil de usuario" ligado a saves | No existe en ningún documento; sería una feature nueva a diseñar |
| 67 | Persistencia de ajustes independiente del save de progreso | ✅ | `04·25` tabla "Las trampas": *"Guardar el rebinding en el guardado de partida → se pierde al borrar el slot; es Configuración, no progreso"* | — |

### Telemetría y analítica

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 68 | Qué medir en un juego (eventos clave) | ✅ | `13·01 §9.5` (`telemetria_registrar`, ejemplo con muertes por sala, extensible a cualquier tipo de evento) | — |
| 69 | Embudos (funnels) | ✅ | `13·20 §3.4` (embudo de tienda: abierta→vista→comprada→reembolsada, leído con `jq`); `13·01 §9.6` (muertes por sala) | — |
| 70 | Retención D1/D7/D30 | 🟡 | `13·20 §1.9` da las **definiciones** de KPI (fórmulas, para qué sirven) | Sin implementación GML de cómo calcular cohortes reales (agrupar por fecha de instalación y medir quién vuelve) |
| 71 | Diseño de eventos (taxonomía, nombres, propiedades) | ✅ | `13·01 §9.5::telemetria_registrar(_tipo, _extra)` (tipo + struct de campos propios) | — |
| 72 | Envío de eventos por HTTP a un backend (batching, cola offline, reintentos) | 🔴 | `http_request(url, method, header_map, body)` existe y está documentado (`05·02`, `07·14`, `04·43`), pero **nunca** en contexto de telemetría: `telemetria_volcar()` solo escribe a JSON local | Una receta que envíe el JSON de telemetría por HTTP, con cola si falla la conexión y reintento — o al menos decir explícitamente que hoy solo hay volcado local |
| 73 | Consentimiento explícito antes de trackear/enviar telemetría | ✅ | `13·11 §7` "Telemetría con consentimiento": marco de 5 puntos (preguntar antes con "no" tan fácil como "sí", recoger lo mínimo, sin consentimiento sin envío, política de privacidad obligatoria, lo local basta la mayoría de las veces) | — |
| 74 | GDPR/RGPD como cumplimiento de protección de datos | 🟡 | `13·11 §9.3`: una frase que nombra correctamente el RGPD ("aplica por la residencia del jugador, no por la tuya") y advierte de que "el trato de datos de menores tiene reglas propias" | Sin desarrollo del cumplimiento real (base legal, derecho de acceso/borrado, plazos de retención, notificación de brecha) — sigue siendo mención, no guía |
| 75 | Datos de menores / COPPA (distinto de PEGI, que sí está cubierto) | 🔴 | 0 resultados en contenido propio; COPPA solo aparece en documentación **importada** de extensiones de anuncios (`GMEXT-PlayAgeSignals`, `GMEXT-AdMob`) | Hueco real y total en contenido propio de la biblioteca |
| 76 | Anonimizar / seudonimizar identificadores de jugador | 🟡 | 0 resultados de "anonimizar"/"seudónimo". El patrón ya existe de facto sin nombrarlo: `13·01 §9.5` genera `sesion: $"{fecha}#{irandom(9999)}"` (pseudónimo por sesión, no ligado a identidad) | Nombrar el principio y enlazarlo con el patrón de sesión ya existente; el patrón explicado explícitamente solo vive en código de terceros descargado (`Snitch`) sin enlazar |
| 77 | No enviar datos personales identificables (PII) | ✅ | `13·11 §7` punto 2: *"Identificadores de la máquina, ubicación, nombre de usuario: no. Lo que no recoges no lo puedes perder ni filtrar"* | — |
| 78 | Herramientas de terceros para analítica (GameAnalytics, backend propio) | 🟡 | Solo `GMEXT-Firebase` (Analytics) catalogado de pleno derecho; `GameAnalytics` solo aparece como backend opcional de `Snitch` (crash-reporting, no eventos de juego) | Confirma que Firebase es la única opción real hoy — no hay nada que crear, solo dejarlo dicho con claridad |

### Live-ops

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 79 | Configuración remota (remote config) sin publicar parche | 🔴 | Solo Firebase Remote Config, documentación **de la extensión** (`GMEXT-Firebase/docs/Guides_Remote_Config.md`), no de esta biblioteca | Una receta con `http_request` nativo contra un backend propio para leer valores sin publicar parche |
| 80 | Banderas de característica (feature flags) con activación gradual | 🔴 | Cero resultados relevantes | Cualquier patrón de activación porcentual/gradual |
| 81 | Eventos de temporada con fechas comprobadas por el cliente | 🔴 | `date_compare_datetime`/`date_current_datetime` extensamente documentados (manual, `08·18`, `03·38`) pero nunca aplicados a activar/desactivar contenido por fecha | Receta técnica: guardar fecha de inicio/fin y comprobarla en el arranque |
| 82 | Contenido descargable (DLC) vía Included Files remotos o tienda | 🟡 | `texturegroup_add()` (`08·08`) se presenta explícitamente como "la puerta de entrada para contenido descargable y modding" (según `_indice/auditorias/ingenieria.md` fila G4), pero solo carga desde archivos **locales**; el mecanismo nativo de DLC de Steam/tienda no está cubierto | El documento que una `texturegroup_add` + descarga HTTP + Included Files remotos, o documente el DLC nativo de Steamworks |
| 83 | Control de versión mínima del cliente / parches por tienda | 🔴 | `GM_version` documentado (`08·19`) pero nunca en un patrón de "forzar actualización" contra un mínimo remoto | Receta: comparar `GM_version` contra un valor servido por HTTP y bloquear/avisar |
| 84 | Mensajes del juego / anuncios in-game (MOTD) | 🔴 | Cero resultados en toda la biblioteca | Patrón de mensaje configurable por servidor mostrado al arrancar |
| 85 | Modo mantenimiento | 🔴 | Cero resultados en toda la biblioteca | Patrón de bloqueo del juego con aviso mientras se despliega un cambio de servidor |
| 86 | Argumento de diseño: por qué (NO) hacer live-ops en un estudio pequeño | ✅ | `13·20 §1.8` completo: árbol de decisión, 4 razones para no hacerlo, cuándo sí tiene sentido, coste calculado en las mismas unidades que el resto de la estimación de producción | Es diseño/producción, no ingeniería — por eso las filas 79-85 siguen siendo huecos técnicos reales aunque este argumento exista |

### Depuración de datos y testing

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 87 | Tests automatizados de guardado/carga (round-trip) | ✅ | `13·10 §5.2` (líneas 864-905): 3 pruebas reales — ciclo completo, partida de versión vieja, fichero corrupto — con criterio propio, no solo remisión al framework externo | — |
| 88 | Fuzz testing / corrupción aleatoria de saves | 🟡 | `13·10 §5.2` solo prueba una cadena fija inválida (`"{esto no es json"`); QA manual G5 en `§9.1` también es manual, no aleatorio | Truncar el archivo en un punto aleatorio / corromper bytes al azar y comprobar recuperación con gracia |
| 89 | Inspector de save dentro del propio juego (modo debug) | 🔴 | `01·15` usa `dbg_view`/`dbg_watch` para vida, FPS, memoria — nunca para datos de guardado. Cero resultados de "inspector"/"visor de guardado" | Un `dbg_view` (o pantalla propia) que muestre/edite el struct del save cargado en JSON legible |
| 90 | Editar un save a mano para forzar un escenario de prueba | 🔴 | Cero resultados; el JSON legible en texto plano lo permite implícitamente, pero no hay ninguna receta práctica escrita | Una nota práctica: "abre `save_1.json`, cambia `vida` a 1, guarda, carga" |
| 91 | Logging persistente de guardado/carga para depurar en producción | 🔴 | `scr_save_load.gml` usa solo `show_debug_message()` en todas sus rutas de error; `13·10 §7.2` define `registrar()` (logger con niveles que sobrevive al cierre) pero **nunca se conecta** a `save_game`/`load_game` en ningún documento | Que `save_game`/`load_game` llamen a `registrar(NIVEL.ERROR, …)` para que un fallo de guardado de un jugador quede en `partida.log` |
| 92 | *Golden files* y determinismo (bonus, relacionado) | ✅ | `13·10 §5.1` (ficheros dorados versionados en Git, guardados en `game_save_id`) | — |
| 93 | Framework de test: oficial (GM-TestFramework) vs. propio (`scr_pruebas`) | ✅ | `13·10 §3-4` (mini-framework propio completo + comparación con GM-TestFramework y `crispy`, con criterio de cuál elegir) | — |

## Huecos por prioridad

### 🔴 Graves

1. **Defecto activo**: 10 documentos de `04 - Recetas por género` (03, 04, 05, 06, 07, 09, 10, 11,
   12, 15 — 15 ocurrencias) enseñan a guardar partidas con `working_directory` (solo lectura),
   contradiciendo `01·14 §1` y la advertencia explícita de `scr_save_load.gml`. Código que funciona
   en el IDE y falla en cualquier build exportada, en móvil y en macOS sandboxed.
2. **Defecto activo**: el hash de integridad de un replay/save se **calcula pero nunca se
   compara**, en el único sitio de toda la biblioteca que dice usarlo para eso (`13·10 §14.3`).
3. **Live-ops técnico inexistente**: remote config, feature flags, versión mínima del cliente,
   MOTD, modo mantenimiento — 5 piezas con cero implementación, pese a que las funciones base
   (`http_request`, `date_compare_datetime`, `GM_version`) ya están documentadas para otros usos.
4. **Telemetría que nunca sale del disco local**: `http_request` existe y se documenta para
   modding/IA, pero jamás se conecta con `telemetria_volcar()` para enviar datos a un backend.
5. **Sin red de seguridad de saves**: no hay backup rotativo (17) ni forma de recuperar un save
   roto (20) — la escritura atómica evita la corrupción a mitad de escritura, pero no protege de
   un bug del propio juego que sobrescribe una partida válida con datos malos.
6. **Depuración de saves en producción, débil**: sin inspector en runtime (89), sin receta de
   editar a mano (90), sin logging persistente conectado (91) — un bug de guardado reportado por
   un jugador es difícil de diagnosticar con lo que hay hoy.
7. **Guardado sin congelar, ausente** (8): con un sistema de chunking para mundos grandes ya
   construido (`04·09`), no hay ninguna guía de repartir el guardado en varios frames.
8. **Quicksave/quickload** (11) y **perfiles de usuario para guardado** (66): ausentes, con demanda
   real en varios géneros (RPG, roguelike).
9. **Datos de menores / COPPA** (75): hueco legal real y total en contenido propio.
10. **Tamaño y velocidad JSON vs. binario** (51): sin criterio de decisión, pese a que ambos
    formatos están completamente documentados por separado.
11. **Saves de demo→juego final** (27): ausente.

### 🟠 Medios

- Cifrado real del save (29): resoluble **enlazando** dos extensiones ya catalogadas, no
  escribiendo nada nuevo.
- GDPR/RGPD sin desarrollo (74): una frase correcta, sin guía práctica de cumplimiento.
- Validador de save con reglas múltiples de rango (35) y validación de contenido con
  rangos/tipos (55).
- Herramientas de autor para balance/contenido general (57).
- Anonimizar identificadores (76): el patrón ya existe sin nombrarlo.
- Retención D1/D7/D30 con cohortes reales (70).
- Campos renombrados en migración (26): técnica trivial, falta el ejemplo.
- Checklist de ingeniería "no romper tras un parche" (28).
- Fuzz testing de saves (88).
- DLC vía descarga (82).
- Ranuras con metadata rica unificada (10).

### 🟡 Menores

- Referencias circulares en JSON (6): una advertencia de una línea basta.
- `buffer_compress` sin ejemplo integrado (50).
- Permisos en consola (41): límite honesto por NDA, no un hueco explotable.
- **Nube (61, 62, 63, 64)**: no falta contenido, falta enlazar `04·20`/`01·14` a la documentación
  ya existente de las extensiones oficiales — el arreglo más barato de todo este informe.
- Herramientas de analítica de terceros (78): Firebase ya resuelve el caso principal.
- Cuota de Steam Cloud (60): dos funciones sin enlazar.

## Encargo para el redactor

1. **Corregir el defecto de `working_directory`** en los 10 documentos de `04 - Recetas por
   género` (03, 04, 05, 06, 07, 09, 10, 11, 12, 15): sustituir
   `file_text_open_write(working_directory + "archivo.json")` por
   `file_text_open_write(game_save_id + "archivo.json")` (o un nombre de archivo suelto, que
   resuelve solo al save area). Es una corrección de código, no contenido nuevo. Símbolos
   verificados: `game_save_id`, `working_directory`, `file_text_open_write`.

2. **Corregir el defecto del hash sin comparar** en `13·10 §14.3`: o bien `replay_verificar()`
   compara `_replay.hash` contra un `sha1_string_utf8` recalculado del paquete recibido antes de
   re-simular, o bien el comentario de `replay_cerrar()` dice honestamente que el hash hoy no se
   verifica en ningún sitio. Símbolo verificado: `sha1_string_utf8`.

3. **Nueva sección en `01·14`** (tras §12, "Codificación y hashes"): *"Checksum como verificación
   real: calcular, guardar aparte, comparar y rechazar"* — el flujo completo que hoy falta en toda
   la biblioteca, con `md5_string_utf8`/`buffer_sha1` (ya verificados) sobre el propio
   `scr_save_load.gml`.

4. **Ampliar `scr_save_load.gml`** con `save_backup(_slot, _n)` (rotar N copias anteriores antes de
   sobrescribir) y una función de recuperación que intente el backup si el save principal falla la
   validación. Símbolos: `file_exists`, `file_rename`, `file_delete` (ya verificados, usados en el
   propio script).

5. **Nuevo documento o sección de live-ops técnico** — candidato: `04 - Recetas por
   género/46 - Live-ops técnico (config remota, versión mínima, mensajes del juego).md`, enlazado
   desde `13·20 §1.8`. Contenido: remote config con `http_request` puro contra un backend propio,
   feature flags porcentuales, comprobación de `GM_version` contra un mínimo remoto, MOTD, modo
   mantenimiento. Símbolos verificados: `http_request`, `GM_version`, `date_compare_datetime`,
   `date_current_datetime`.

6. **Ampliar `13·01 §9.5-9.6`** con el envío real de `telemetria_volcar()` por HTTP: usar
   `http_request` con cola local de reintento si falla la conexión (reutilizando el propio archivo
   JSON como cola). Enlazar el marco de consentimiento ya escrito en `13·11 §7` en vez de
   repetirlo.

7. **Ampliar `13·11 §9.3`** (Política de privacidad) con un párrafo de GDPR/RGPD práctico: base
   legal mínima para telemetría de juego (interés legítimo vs. consentimiento), derecho de acceso
   y borrado, plazo de retención razonable, y una frase específica sobre datos de menores (COPPA
   en EE. UU., el umbral de edad del RGPD para consentimiento sin tutor). No inventar cifras sin
   verificar la fuente — dejar `⚠️` donde no se ha verificado, igual que ya hace `13·20 §1.5`.

8. **Enlazar la nube "invisible"**: añadir a `04·20 §5` (Steam Cloud) un enlace a las funciones de
   cuota (`steam_get_quota_total`/`steam_get_quota_free`, ya verificadas en `GMEXT-Steamworks/
   docs/cloud.js`), y añadir dos subsecciones nuevas —§5 bis (iCloud vía Game Center Saved Games)
   y §5 ter (Google Play Saved Games)— que resuman la API ya verificada de
   `GMEXT-GameCenter/docs/Quick_Start_Guide.md` y `GMEXT-GooglePlayServices/docs/savedgames.js`,
   incluidas las políticas de resolución de conflictos (`LongestPlaytime`, `LastKnownGood`,
   `MostRecentlyModified`, `HighestProgress`). Es reorganizar/enlazar contenido ya verificado, no
   inventar nada.

9. **Añadir un inspector de save en `01·15`** (Depuración): un `dbg_view` que muestre el struct del
   save cargado como JSON legible en el propio Debug Overlay, más una nota práctica de "editar
   `save_1.json` a mano para forzar un escenario". Símbolos: `dbg_view`, `dbg_text_separator`
   (verificar firma exacta con `buscar.py` antes de escribir el ejemplo).

10. **Conectar `registrar()` (`13·10 §7.2`) con `scr_save_load.gml`**: sustituir o complementar
    `show_debug_message()` por `registrar(NIVEL.ERROR, …)` en las 3 rutas de fallo de `save_game`
    y en `__save_read_raw`, para que un fallo de guardado quede en `partida.log` y no solo en la
    consola de desarrollo.

11. **Añadir quicksave/quickload**: una sección corta en `01·14` o `04·00` (Anatomía de un juego
    completo) que reutilice `save_game("quicksave", …)`/`load_game("quicksave")` con una tecla
    dedicada (verificar con `buscar.py` el input que se use, p. ej. `keyboard_check_pressed`).

12. **Migración encadenada: enlazar, no repetir**. Añadir en `01·14 §13` y en la cabecera de
    `scr_save_load.gml` un enlace a `13·06 §3.10` como "el patrón de migración recomendado", en
    vez de dejar el hook único como si fuera la única opción.

13. **Añadir una tabla de decisión JSON vs. binario** en `01·14` (tras §8 o §9): tamaño, velocidad
    de parseo, legibilidad, cuándo compensa cada uno — usando las cifras que ya existen dispersas
    (`buffer_compress` para el caso de ahorro de tamaño).

14. **Añadir sección de saves de demo→completo** en `04·00` (Anatomía de un juego completo) o
    `13·11` (Producción): qué comprobar si el juego se distribuye primero como demo y luego como
    versión completa con el mismo formato de save.

15. *(Menor, opcional)* Nombrar explícitamente el patrón de pseudónimo de sesión ya existente en
    `13·01 §9.5` ("sesión con `irandom` sin ligar a identidad") como técnica de anonimización, y
    enlazarlo desde donde se hable de telemetría/consentimiento.

## Lo que comprobé y NO hacía falta

- **Migración de esquema por versión, campos nuevos y eliminados** — parecía que solo existía un
  hook único genérico en `scr_save_load.gml`, pero `13·06 §3.10` ya tiene el patrón completo de
  escalones acumulativos con ejemplos reales de campo añadido y campo eliminado. Solo falta
  enlazarlo desde el documento canónico de persistencia (`01·14`), no escribirlo de nuevo.
- **Autoguardado** — parecía disperso y sin criterio; `13·06 §3.10` tiene una tabla completa de
  cuándo sí/no disparar, con razón para cada caso, más un indicador visual — no hace falta nada
  nuevo.
- **Anti-trampas y validación de leaderboards** — se sospechaba un hueco típico del oficio;
  `13·10 §14.1-14.3` lo cubre con plausibilidad de puntuación y replay firmado con re-simulación
  server-side, ya evaluado también por `r3-multijugador-online.md` (fila I5, ✅). Solo el detalle
  puntual del hash sin comparar (encargo #2) es un defecto real dentro de un bloque por lo demás
  sólido.
- **Guardado de mundo grande por chunks** — ya evaluado independientemente y marcado ✅ por
  `r3-procedural-niveles.md` (filas #41, #42, #51); confirmado de nuevo aquí desde el ángulo de
  persistencia, con el matiz de que el propio código de ese ejemplo tiene el defecto de
  `working_directory`.
- **Modding de terceros y contenido externo** — `_indice/auditorias/ingenieria.md` (ronda previa)
  lo marcaba PARCIAL con piezas sueltas; `04·43 - Modding y contenido externo.md` (862 líneas,
  escrito después) ya lo cierra por completo, incluida la validación de rutas de manifiesto
  (path traversal). Solo la pieza de DLC-vía-descarga sigue suelta (fila 82).
- **Separar ajustes de sistema y de partida** — parecía que solo estaba en `04·25`; en realidad la
  clasificación canónica de 3 clases vive en `13·06 §3.10` y `04·25` solo la cita, lo cual es
  correcto (no hay duplicación).
- **Integridad de paquetes de red vía checksum** — ya evaluada por `r3-multijugador-online.md`
  (fila A12, 🟡); no se ha vuelto a evaluar desde el ángulo de red aquí, solo desde el ángulo de
  guardado/replay (que resultó ser el mismo defecto de fondo: se calcula pero no se compara).
- **Rate limiting de un backend propio** y **leaderboard no-Steam con backend HTTP real** — ya
  identificados como huecos por `r3-multijugador-online.md` (filas I6 🔴 e I2 🟡
  respectivamente); no se duplican aquí, solo se referencian donde se solapan con seguridad de
  datos (fila 33).
