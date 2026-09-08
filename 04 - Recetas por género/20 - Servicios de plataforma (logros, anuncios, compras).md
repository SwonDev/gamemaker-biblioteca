# 20 · Servicios de plataforma: logros, anuncios, compras, leaderboards y nube

> Todo lo que un juego necesita **al publicarse** y que no forma parte del juego en sí:
> desbloquear logros, subir puntuaciones a una tabla, mostrar anuncios recompensados, procesar
> compras integradas y guardar en la nube.
>
> **Hueco de receta detectado:** el catálogo de extensiones estaba
> ([12 · 03 — Integraciones con servicios](../12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md)),
> pero sin una línea de GML del flujo real. Este documento lo cierra.

---

## La regla que evita el 90 % de los errores

**Casi ninguna de estas funciones está en el runtime.** Vienen de **extensiones**, y por eso:

```sh
python3 _indice/buscar.py steam_set_achievement
# → «steam_set_achievement» NO existe en el runtime 2026.0.0.23
```

Eso **no** significa que no exista: significa que **no es del runtime, es de la extensión
Steamworks**. `buscar.py` solo conoce `GmlSpec.xml`. Para verificar una función de extensión,
su fuente está descargada:

| Servicio | Extensión (verifícala aquí) |
|---|---|
| Steam (logros, tablas, nube, overlay) | `11 - Código descargado/extensiones_oficiales/GMEXT-Steamworks/` |
| Anuncios | `.../GMEXT-AdMob/` · `.../GMEXT-LevelPlay/` |
| Compras Android | `.../GMEXT-GooglePlayBilling/` |
| Compras iOS | `.../GMEXT-AppleIAP/` |
| Logros/tablas móvil | `.../GMEXT-GooglePlayServices/` · `.../GMEXT-GameCenter/` |
| Backend, analítica, auth | `.../GMEXT-Firebase/` |

> 🔺 **Las 14 extensiones oficiales de servicios están en el proyecto.** Si dudas de una
> función de extensión, `grep -r nombre_funcion "11 - Código descargado/extensiones_oficiales/GMEXT-X"`.
> Las firmas de abajo se verificaron así el 2 de septiembre de 2026, no se inventaron.

---

## 1 · Logros y estadísticas (Steam)

```gml
/// obj_control · Create — arrancar Steam una sola vez
if (steam_initialised()) {
    global.steam = true;
} else {
    global.steam = false;   // el juego debe funcionar IGUAL sin Steam
    show_debug_message("Steam no disponible: modo sin logros");
}
```

```gml
/// desbloquear un logro cuando pasa algo
function logro_desbloquear(_api_name) {
    if (!global.steam) return;
    // no re-enviar si ya está: ahorra tráfico y evita parpadeos del overlay
    if (!steam_get_achievement(_api_name)) {
        steam_set_achievement(_api_name);
    }
}

/// una estadística acumulativa (enemigos derrotados, distancia…)
function stat_sumar(_api_name, _cantidad) {
    if (!global.steam) return;
    var _actual = steam_get_stat_int(_api_name);
    steam_set_stat_int(_api_name, _actual + _cantidad);
    // Steam agrupa el envío; no hace falta llamar a store en cada cambio
}
```

> ⚠️ **Los nombres son los "API Name" del panel de Steamworks, no el título visible.** Si el
> logro se llama «Primera victoria» en la tienda, su API name puede ser `ACH_FIRST_WIN`. Usa
> siempre el API name.
>
> 💡 **`steam_set_achievement` no dibuja nada**: el aviso emergente lo pone el overlay de
> Steam. Si quieres una notificación propia (para tener una en todas las plataformas), emítela
> con [señales](./16%20-%20Señales%20y%20desacoplamiento.md) y dibújala tú.

---

## 2 · Tablas de puntuación (leaderboards)

Son **asíncronas**: pides algo y la respuesta llega después, en el evento **Async - Steam**.

```gml
/// Create — crear/obtener la tabla (idempotente: si existe, la reutiliza)
steam_create_leaderboard("puntuacion_global", lb_sort_descending, lb_disp_numeric);

/// al terminar una partida — subir la puntuación
if (global.steam) {
    // el 4º argumento (force_update): false = solo guarda si mejora la marca previa
    subida = steam_upload_score_ext("puntuacion_global", global.puntos, false);
}
```

```gml
/// pedir las 10 mejores para mostrarlas
descarga = steam_download_scores("puntuacion_global", 1, 10);
```

```gml
/// obj_control · Async - Steam — aquí llegan TODAS las respuestas de Steam
var _id = async_load[? "id"];
var _tipo = async_load[? "event_type"];

if (_tipo == "leaderboard_download") {
    var _entradas = async_load[? "entries"];      // es una cadena JSON
    var _datos = json_parse(_entradas);
    global.ranking = _datos.entries;              // array de {name, score, rank}
}
```

📄 Verificado en `GMEXT-Steamworks/docs/leaderboards.md`. Las constantes `lb_sort_*`,
`lb_disp_*` y `lb_score_method_*` las define la extensión.

> 💡 **El evento Async - Steam es uno solo para toda la extensión.** Distingue siempre por
> `async_load[? "event_type"]`: llegan ahí las respuestas de tablas, de la nube, de la sesión…

---

## 3 · Anuncios (AdMob)

Tres formatos, tres ciclos de vida. El patrón es siempre **cargar → comprobar → mostrar**.

```gml
/// Create — configurar las unidades de anuncio (IDs del panel de AdMob)
admob_rewarded_video_set_ad_unit(global.es_android
    ? "ca-app-pub-XXX/rewarded_android"
    : "ca-app-pub-XXX/rewarded_ios");
admob_rewarded_video_load();     // empieza a cargar; tarda unos segundos
```

```gml
/// el jugador pulsa "ver anuncio por una vida extra"
function ver_anuncio_recompensado() {
    if (admob_rewarded_video_is_valid()) {   // ¿terminó de cargar?
        admob_rewarded_video_show();
    } else {
        // aún no está listo: no bloquees al jugador, dale la recompensa o reintenta
        admob_rewarded_video_load();
        mostrar_aviso("El anuncio no está listo, inténtalo en unos segundos");
    }
}
```

```gml
/// obj_admob · Async - Social — la recompensa SOLO se da aquí
var _tipo = async_load[? "type"];
if (_tipo == "admob_rewarded_video_reward") {
    global.vidas += 1;              // el jugador vio el anuncio entero
}
if (_tipo == "admob_rewarded_video_completed") {
    admob_rewarded_video_load();    // recargar para la próxima
}
```

> ⚠️ **La recompensa se da en el evento async, NUNCA justo después de `_show()`.** Si la das al
> pulsar el botón, el jugador cierra el anuncio antes de tiempo y cobra igual. La regla de oro
> de los anuncios recompensados.
>
> 🔺 **Interstitiales con cabeza:** `admob_interstitial_load()` / `admob_interstitial_show()`.
> Muéstralos en cortes naturales (fin de nivel), nunca a mitad de acción, o Google te penaliza
> y el jugador se va. Banners: `admob_banner_create()` + `admob_banner_show()`.
>
> 💡 En desarrollo, usa **siempre los ad units de prueba de Google**. Mostrar anuncios reales a
> tu propio tráfico de test es motivo de baneo de la cuenta de AdMob.

---

## 4 · Compras integradas (IAP)

Aquí hay una trampa que el manual esconde: **la API `iap_*` nativa está OBSOLETA.**

```sh
python3 _indice/buscar.py iap_purchase
# → iap_acquire(product_id, payload) ⚠️obsoleta
```

**No la uses en un juego nuevo.** La vía moderna son las extensiones por tienda:

| Plataforma | Extensión | Función de compra |
|---|---|---|
| Android | `GMEXT-GooglePlayBilling` | flujo de Billing v5+ con async events |
| iOS/macOS | `GMEXT-AppleIAP` | StoreKit con async events |

El patrón, común a las dos:

```gml
/// 1 · Create — inicializar y consultar los productos disponibles
//    (los IDs los defines en Google Play Console / App Store Connect)

/// 2 · el jugador pulsa "comprar"
//    llamar a la función de compra de la extensión con el product_id

/// 3 · Async - IAP / Async - In-App-Purchase — resolver la compra
var _tipo = async_load[? "type"];
switch (_tipo) {
    case "purchase":        // compra confirmada
        entregar_producto(async_load[? "product_id"]);
        // consumibles (monedas): marcarlos como consumidos
        // no consumibles (quitar anuncios): guardar que ya lo tiene
        break;
    case "restore":         // restaurar compras previas (OBLIGATORIO en iOS)
        entregar_producto(async_load[? "product_id"]);
        break;
}
```

> ⚠️ **Apple RECHAZA tu app si no tienes un botón "Restaurar compras".** Es requisito de
> revisión, no opcional. Google es más flexible pero conviene tenerlo igual.
>
> ⚠️ **Nunca confíes solo en el cliente para desbloquear contenido de pago valioso.** Para IAP
> de mucho valor, verifica el recibo en tu servidor. Para "quitar anuncios" o cosméticos, el
> cliente basta.
>
> 🔺 **Distingue consumible de no consumible:** monedas (consumible, se puede recomprar) vs
> «quitar anuncios» (no consumible, una vez y para siempre, hay que restaurar). Confundirlos es
> el bug de IAP más común.

---

## 5 · Guardado en la nube (Steam Cloud)

```gml
/// guardar la partida también en la nube de Steam
function guardar_nube(_nombre_archivo, _contenido) {
    // primero en local, siempre
    var _f = file_text_open_write(_nombre_archivo);
    file_text_write_string(_f, _contenido);
    file_text_close(_f);

    // y en la nube si está disponible para esta app y este usuario
    if (global.steam && steam_is_cloud_enabled_for_app()) {
        steam_file_write(_nombre_archivo, _contenido, string_byte_length(_contenido));
    }
}

/// al cargar, preferir la nube si trae algo
function cargar_nube(_nombre_archivo) {
    if (global.steam && steam_file_exists(_nombre_archivo)) {
        return steam_file_read(_nombre_archivo);
    }
    if (file_exists(_nombre_archivo)) {
        var _f = file_text_open_read(_nombre_archivo);
        var _s = file_text_read_string(_f);
        file_text_close(_f);
        return _s;
    }
    return "";
}
```

> 💡 **La nube no sustituye al guardado local, lo complementa.** Guarda siempre en local; la
> nube es para que la partida siga al jugador entre equipos. Y `steam_is_cloud_enabled_for_app`
> puede ser `false` aunque haya Steam: el jugador puede desactivar la nube por juego.
>
> 🔺 **`window_set_size` y compañía no aplican aquí**, pero la lógica de "local + fallback" es
> la misma que en [17 · Interoperabilidad con la web](./17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md)
> con `localStorage`.

### 5.1 · Cuota de Steam Cloud

Cada juego tiene un **límite de bytes por usuario** que se configura en el panel de
Steamworks (1 GB por defecto). Comprobarlo evita que un jugador se quede sin poder guardar sin
saber por qué:

```gml
/// antes de escribir en la nube, o al abrir el menú de ajustes de nube
if (global.steam && steam_is_cloud_enabled_for_app()) {
    var _total = steam_get_quota_total();   // bytes totales asignados a este juego
    var _libre = steam_get_quota_free();    // bytes que quedan libres

    if (_libre < 1024 * 100) {   // menos de 100 KB libres: avisa antes de que falle la escritura
        mostrar_aviso("Espacio de Steam Cloud casi lleno. Libera partidas antiguas.");
    }
}
```

📄 Verificado en `GMEXT-Steamworks/docs/cloud.js`. El manual de la propia extensión avisa:
*"once the quota is exhausted file writes will fail"* — si no compruebas la cuota, el jugador
descubre el problema cuando `steam_file_write` ya ha fallado en silencio.

### 5.2 · iCloud (Game Center Saved Games)

**Existe y está documentada por completo en la extensión oficial**, aunque no aparezca en el
resto de esta receta: es la única vía de nube nativa de Apple, exclusiva de iOS/macOS, y va
**por Game Center**, no por un servicio de nube separado. Verificado línea a línea en
`GMEXT-GameCenter/docs/savedgames.js`.

```gml
/// guardar la partida como un GameCenterSavedGame con nombre "slot1"
function guardar_icloud(_slot, _datos_json) {
    var _buff = buffer_create(string_byte_length(_datos_json) + 1, buffer_fixed, 1);
    buffer_write(_buff, buffer_string, _datos_json);

    gamecenter_saved_games_save(_slot, _buff, function(_resultado) {
        if (_resultado.success) {
            show_debug_message($"iCloud: guardado '{_resultado.name}'");
        }
    });

    buffer_delete(_buff);   // el callback ya copió lo que necesitaba
}
```

```gml
/// cargar: pedir los metadatos primero, luego los bytes con un buffer del tamaño exacto
function cargar_icloud(_slot, _al_terminar) {
    gamecenter_saved_games_data_request(_slot, function(_resultado) {
        if (!_resultado.success) { _al_terminar(undefined); return; }

        var _buff = buffer_create(_resultado.required_size, buffer_fixed, 1);
        if (gamecenter_saved_games_data_fetch(_resultado.handle_id, _buff)) {
            buffer_seek(_buff, buffer_seek_start, 0);
            _al_terminar(buffer_read(_buff, buffer_string));
        } else {
            gamecenter_saved_games_data_release(_resultado.handle_id);
            _al_terminar(undefined);
        }
        buffer_delete(_buff);
    });
}
```

**Conflictos entre dispositivos** (el jugador guardó desde el iPhone y desde el Mac antes de
sincronizar): GameKit los reporta por un **callback suscrito una sola vez**, no por cada
llamada individual —

```gml
/// Create de obj_control — un único suscriptor para toda la partida
gamecenter_saved_games_callback_subscribe(function(_evento) {
    if (_evento.type == "conflict") {
        // El evento solo trae METADATOS de cada lado (nombre, dispositivo, fecha), no los
        // bytes: hay que pedir los datos del elegido antes de poder resolver. Aquí el
        // criterio es "el más reciente"; podría ser cualquier otro.
        var _elegido = _evento.slots[0];
        var _i;
        for (_i = 1; _i < array_length(_evento.slots); _i++) {
            if (_evento.slots[_i].modification_date > _elegido.modification_date) {
                _elegido = _evento.slots[_i];
            }
        }

        var _conflict_id = _evento.conflict_id;   // capturado para el callback anidado
        gamecenter_saved_games_data_request(_elegido.name, function(_datos) {
            if (!_datos.success) return;

            var _buff = buffer_create(_datos.required_size, buffer_fixed, 1);
            if (gamecenter_saved_games_data_fetch(_datos.handle_id, _buff)) {
                gamecenter_saved_games_resolve_conflict(_conflict_id, _buff,
                    function(_resultado) { show_debug_message("Conflicto de iCloud resuelto"); });
            }
            buffer_delete(_buff);
        });
    } else if (_evento.type == "modified") {
        show_debug_message($"iCloud: '{_evento.slot.name}' cambió en otro dispositivo");
    }
});
```

> ⚠️ **Es una feature exclusiva de Apple** (iOS y macOS): en el resto de plataformas no hace
> nada. Guarda siempre en local además (§5 arriba es el patrón), igual que con Steam Cloud.
> 💡 `gamecenter_saved_games_data_release(handle_id)` libera la copia que retiene la extensión
> si pides los datos de un slot y decides no leerlos: sin esto, la extensión los mantiene en
> memoria el resto de la sesión.

### 5.3 · Google Play Saved Games

Nube nativa de Android, **distinta de los logros/leaderboards de Google Play Games** (esos van
por otras funciones de la misma extensión). Verificado en `GMEXT-GooglePlayServices/docs/savedgames.js`.
A diferencia de iCloud, cada slot se **abre** antes de leer o escribir, y solo entonces se
**confirma y cierra**:

```gml
/// abrir (crea el slot si no existe) y, si abrió limpio, leer los datos
play_services_saved_games_open("slot_1", true,
    PlayServicesSavedGamesConflictPolicy.MostRecentlyModified,
    function(_status, _info = undefined) {
        if (!_status.success) return;
        if (_info.is_conflict) return;   // no puede pasar con esta política: se resuelve solo

        var _datos = _info.data != "" ? json_parse(_info.data) : undefined;
    });
```

```gml
/// guardar: el slot debe estar ABIERTO en esta sesión (con play_services_saved_games_open)
var _opciones = new PlayServicesSavedGameCommitOptions();
_opciones.name               = "slot_1";
_opciones.data                = json_stringify(_datos_partida);
_opciones.desc                = "Nivel 3, 00:12:34";
_opciones.played_time_millis  = -1;   // -1 = no tocar el valor que ya había
_opciones.progress_value      = -1;
_opciones.cover_image_path    = "";   // "" = no tocar la miniatura

play_services_saved_games_commit_and_close(_opciones, function(_status, _metadata = undefined) {
    if (_status.success) { show_debug_message("Guardado en Google Play"); }
});
```

**Resolución de conflictos**: `PlayServicesSavedGamesConflictPolicy` trae **cuatro políticas
automáticas**, resueltas en el servidor sin tocar código, y una manual:

| Política | Se queda con… |
|---|---|
| `LongestPlaytime` | el lado con más `played_time_millis` |
| `LastKnownGood` | la última versión que el servidor confirmó consistente |
| `MostRecentlyModified` | el lado modificado más recientemente |
| `HighestProgress` | el lado con mayor `progress_value` |
| `Manual` | ninguna automática: tu código decide con `play_services_saved_games_resolve_conflict(conflict_id, use_local, callback)` |

> 💡 **La UI del sistema ya existe hecha**: `play_services_saved_games_show_saved_games_ui(titulo,
> boton_crear, boton_borrar, max_resultados, callback)` abre el selector nativo de partidas de
> Google, sin construir pantalla propia.
>
> ⚠️ Igual que iCloud: exclusivo de Android con Google Play Services. Guarda siempre en local
> además.

---

## 6 · Xbox Live / UWP (logros, estadísticas, leaderboards, usuarios, nube)

> Nicho: exige una **cuenta de desarrollador de Microsoft** y solo tiene sentido si el
> proyecto exporta a **Windows UWP** (o a Xbox como consola cerrada, ver 6.8). No merece
> documento propio — ~70 páginas del manual para una plataforma que casi nadie de esta
> biblioteca va a tocar —, pero aquí está resumido para que no falte.

### 6.1 · Qué exige y por qué no aparece en `buscar.py`

```sh
python3 _indice/buscar.py xboxlive_get_user
# → «xboxlive_get_user» es un STRUCT o ENUMERACIÓN incorporada, no una función:
#   no figura en GmlSpec.xml, pero sí en el manual.
```

**Ninguna función `xboxlive_*` está en `GmlSpec.xml`.** No es una alucinación descartada:
es una familia completa que el índice de esta biblioteca no puede verificar por firma, porque
`GmlSpec.xml` solo lista la API del runtime base y estas funciones solo existen cuando el
proyecto se compila con el **exportador UWP** (con la casilla **Habilitar XBox Live** marcada
en Opciones de Juego → Windows UWP). Las firmas de este documento están tomadas directamente
del manual oficial, página por página — no de `simbolos.json` — así que trátalas con la misma
cautela que a cualquier función de extensión (§ arriba, "La regla que evita el 90 % de los
errores"): no se pueden probar sin un proyecto UWP real y una cuenta de Xbox.

La familia hermana `uwp_*` (control general de la app UWP: `uwp_suspend`,
`uwp_is_constrained`, `uwp_show_help`, `uwp_check_privilege`…) sí está en `GmlSpec.xml` —
**pero sus 21 funciones están marcadas `⚠️obsoleta`** en el runtime 2026.0.0.23:

```sh
python3 _indice/buscar.py --listar uwp
# → 21 símbolos, todos con ⚠️obsoleta
```

Lo que exige, en conjunto:

| Requisito | Detalle |
|---|---|
| Exportador | **Windows UWP** (no HTML5, no Windows de escritorio normal) |
| Casilla | **Habilitar XBox Live** en Opciones de Juego → Windows UWP |
| Cuenta mínima | **Programa de Creadores** de Xbox — solo funciones básicas de usuario/cuenta |
| Cuenta completa | **ID@Xbox** (cuenta de desarrollador de pago) para logros, estadísticas, leaderboards y matchmaking reales, configurados antes en el panel **XDP** (Xbox Developer Portal) |
| Certificación | Clave de desarrollador (`.pfx`) generada desde un proyecto vacío de Visual Studio, enlazada en Opciones de Juego → Empaquetado |
| Login | UWP en PC solo permite **un usuario a la vez**; la consola Xbox nativa permite varios |

⚠️ Nada de esto se ha podido probar en esta biblioteca: no hay cuenta ID@Xbox ni proyecto UWP
real disponibles. Todo lo que sigue es lo que documenta el manual oficial.

### 6.2 · Usuarios y cuentas

| Función | Firma (manual) | Qué hace |
|---|---|---|
| `xboxlive_show_account_picker` | `xboxlive_show_account_picker()` | Abre el selector de cuentas de Xbox si nadie ha iniciado sesión |
| `xboxlive_user_is_signed_in` | `xboxlive_user_is_signed_in()` | Devuelve si hay un usuario con sesión iniciada |
| `xboxlive_user_is_signing_in` | `xboxlive_user_is_signing_in()` | Devuelve si el login "silencioso" está en curso |
| `xboxlive_get_user_count` | `xboxlive_get_user_count()` | Número de usuarios de Xbox con sesión iniciada |
| `xboxlive_get_user` | `xboxlive_get_user(index)` | El puntero de ID del usuario en el índice dado (`pointer_null` si no existe) |
| `xboxlive_user_for_pad` | `xboxlive_user_for_pad(pad)` | El puntero de ID de usuario asignado a un mando concreto |
| `xboxlive_gamertag_for_user` | `xboxlive_gamertag_for_user()` | El gamertag del usuario con sesión iniciada (cadena vacía si no hay ninguno) |
| `xboxlive_gamerscore_for_user` | `xboxlive_gamerscore_for_user(user_id)` | El *gamerscore* del usuario dado |
| `xboxlive_gamedisplayname_for_user` | `xboxlive_gamedisplayname_for_user(user_id)` | El nombre de visualización del usuario |
| `xboxlive_set_rich_presence` | `xboxlive_set_rich_presence(user_id, is_user_active, rich_presence_string, [service_config_id])` | Fija el texto de "presencia enriquecida" que ven los amigos |

```gml
/// obj_control · Create — flujo de login típico
if !xboxlive_user_is_signed_in()
{
    if (!xboxlive_user_is_signing_in())
    {
        xboxlive_show_account_picker();
    }
}
else
{
    // xboxlive_get_user(0): UWP en PC solo permite un usuario a la vez (§6.1). Este
    // puntero es el "user_id" que piden xboxlive_stats_setup(), xboxlive_achievements_
    // set_progress() y el resto de funciones de estadísticas/logros de §6.3 — sin
    // guardarlo, cualquier logro o estadística revienta con una global sin definir.
    global.gamertag = xboxlive_gamertag_for_user();
    global.user_id  = xboxlive_get_user(0);
}
```

### 6.3 · Estadísticas y logros

Requiere haber llamado antes a `xboxlive_stats_setup(user_id, service_config_id, title_id)`
— el `service_config_id` y el `title_id` son el ID único del juego en el panel XDP.

| Función | Firma (manual) | Qué hace |
|---|---|---|
| `xboxlive_stats_setup` | `xboxlive_stats_setup(user_id, service_config_id, title_id)` | Inicializa el sistema de estadísticas para un usuario |
| `xboxlive_stats_set_stat_int` | `xboxlive_stats_set_stat_int(user_id, stat, value)` | Fija una estadística entera (la crea si no existe) |
| `xboxlive_stats_set_stat_real` | `xboxlive_stats_set_stat_real(user_id, stat, value)` ⚠️ firma no confirmada por WebFetch, solo por el nombre del archivo del manual | Fija una estadística real |
| `xboxlive_stats_set_stat_string` | `xboxlive_stats_set_stat_string(user_id, stat, value)` ⚠️ igual | Fija una estadística de texto |
| `xboxlive_stats_get_stat` | `xboxlive_stats_get_stat(user_id, stat)` ⚠️ igual | Lee el valor local de una estadística |
| `xboxlive_stats_flush_user` | `xboxlive_stats_flush_user(user_id, priority)` | Envía las estadísticas pendientes al servidor (no llamar con mucha frecuencia: Xbox limita la tasa) |
| `xboxlive_get_stats_for_user` | `xboxlive_get_stats_for_user(user_id, serviceconfig_id, statname1, …)` | Pide hasta 14 estadísticas al servidor; responde por evento asíncrono de sistema |
| `xboxlive_achievements_set_progress` | `xboxlive_achievements_set_progress(user_id, achievement, progress)` | Actualiza el progreso de un logro (0-100; nunca acepta un valor menor al actual) |
| `xboxlive_achievement_show_achievements` | `xboxlive_achievement_show_achievements()` | Abre la pantalla de logros del sistema (pausa recomendada mientras se muestra) |
| `xboxlive_achievement_load_friends` | `xboxlive_achievement_load_friends(...)` ⚠️ firma no confirmada | Carga la lista de amigos para filtrar leaderboards |

```gml
/// obj_logros · desbloquear un logro
xboxlive_achievements_set_progress(global.user_id, "LOGRO_PRIMER_JEFE", 100);
```

### 6.4 · Tablas de clasificación (leaderboards)

Dos vías, ambas asíncronas (responden en el evento **Social Asíncrono**, no en el de Sistema):

| Función | Firma (manual) | Qué hace |
|---|---|---|
| `xboxlive_achievement_load_leaderboard` | `xboxlive_achievement_load_leaderboard(ident, minindex, maxindex, filter)` | Pide un tramo de una tabla ya creada en XDP, con filtro de amigos/todos |
| `xboxlive_read_player_leaderboard` | `xboxlive_read_player_leaderboard(leaderboard_name, user_name, num_items, friend_filter)` | Pide la posición de un jugador concreto |
| `xboxlive_stats_get_leaderboard` | `xboxlive_stats_get_leaderboard(...)` ⚠️ firma no confirmada | Variante orientada a estadísticas (sistema 2013) |
| `xboxlive_stats_get_social_leaderboard` | `xboxlive_stats_get_social_leaderboard(user_id, stat_name, max_items, start_rank, skip_result_to_me, real_data)` ⚠️ orden de argumentos deducido del ejemplo del manual, no de una tabla de firma | Leaderboard social filtrado por estadística |

Constantes de filtro (del manual, no de `simbolos.json`): `xboxlive_achievement_filter_all_players`,
`xboxlive_achievement_filter_friends_only`, `xboxlive_achievement_filter_favorites_only`,
`xboxlive_achievement_filter_friends_alt`, `xboxlive_achievement_filter_favorites_alt`.

El evento social asíncrono llega con un `async_load` que trae `id` igual a la constante
`xboxlive_achievement_leaderboard_info`, y claves `leaderboardidᵢ`, `numentries`, `PlayerN`,
`PlayeridN`, `RankN`, `ScoreN` para cada posición — el mismo patrón de "parsear el `ds_map` de
`async_load`" que ya usan Steam y AdMob en las secciones 1-3 de arriba.

### 6.5 · Guardado de partida y nube

| Función | Firma (manual) | Qué hace |
|---|---|---|
| `xboxlive_get_savedata_user` | `xboxlive_get_savedata_user()` | El usuario actualmente asociado al área de guardado (`pointer_null` si ninguno) |
| `xboxlive_set_savedata_user` | `xboxlive_set_savedata_user(user_id)` | Redirige las escrituras/lecturas de archivo (`file_text_*`, `buffer_save_async`…) a ese usuario |
| `xboxlive_get_file_error` | `xboxlive_get_file_error()` | Devuelve la constante de error tras un fallo de archivo: `xboxlive_fileerror_outoflocalstorage`, `xboxlive_fileerror_quotaexceeded`, `xboxlive_fileerror_noerror` |

Con `xboxlive_set_savedata_user` fijado, las funciones normales de archivo de
[14 · Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md)
pasan a operar en el área de guardado ligada a Xbox Live — no hay una API `xboxlive_file_*`
paralela.

### 6.6 · Creación de partidas (matchmaking)

| Función | Firma (manual) | Qué hace |
|---|---|---|
| `xboxlive_matchmaking_create` | `xboxlive_matchmaking_create(user_id, visibility, template, hopper, sdatemplate, [matchattributes])` | Crea una sesión multijugador con plantillas ya definidas en XDP |
| `xboxlive_matchmaking_find` | `xboxlive_matchmaking_find(user_id, template, hopper, sdatemplate, [matchattributes])` | Busca sesiones existentes que encajen |
| `xboxlive_matchmaking_join_session` | `xboxlive_matchmaking_join_session(...)` ⚠️ firma no confirmada | Se une a una sesión encontrada |
| `xboxlive_matchmaking_send_invites` | `xboxlive_matchmaking_send_invites(...)` ⚠️ firma no confirmada | Invita a otros jugadores a la sesión |
| `xboxlive_matchmaking_session_leave` | `xboxlive_matchmaking_session_leave(...)` ⚠️ firma no confirmada | Abandona la sesión actual |

`visibility` usa las constantes `xboxlive_match_visibility_open`,
`xboxlive_match_visibility_private` y `xboxlive_match_visibility_usetemplate`. Todo el flujo
responde por evento social asíncrono con `requestid`, `status`, `sessionid` y `error` en
`async_load` — compara con el patrón de sesiones de
[14 · Multijugador](./14%20-%20Multijugador.md), que resuelve lo mismo sin depender de Xbox.

### 6.7 · Diferencia entre UWP y consola Xbox nativa

Todo lo anterior es la API que **el manual público documenta**, y solo se activa exportando a
**Windows UWP** con la casilla de Xbox Live marcada — es decir, un juego para PC que además
habla con los servicios de Xbox Live (logros, gamertag, leaderboards), no un juego nativo de
consola. ⚠️ La exportación **nativa a Xbox One/Series** (la que produce un paquete que corre
directamente en la consola, vía el GDK de Microsoft) es un programa cerrado de YoYo Games bajo
NDA: requiere ser **ID@Xbox** aprobado, firmar acuerdos de confidencialidad y pasar la
certificación de Microsoft, y su documentación **no está en el manual público** ni, por tanto,
en el espejo de esta biblioteca. No se puede confirmar aquí ninguna API adicional específica de
ese exportador: si el encargo es un juego para consola Xbox real, hay que gestionar el acceso
directamente con YoYo Games / Microsoft.

---

## Las trampas, juntas

| Trampa | Consecuencia |
|---|---|
| Dar la recompensa tras `_show()` en vez de en el async | El jugador cobra sin ver el anuncio |
| Usar la API `iap_*` nativa | Está obsoleta; usa las extensiones por tienda |
| No implementar "Restaurar compras" en iOS | Apple rechaza la app |
| Confundir consumible y no consumible | Compras que se pierden o se duplican |
| Asumir que Steam/anuncios/IAP están siempre | El juego debe funcionar igual sin ellos |
| Usar el título del logro en vez del API name | El logro no se desbloquea |
| Mostrar anuncios reales en desarrollo | Baneo de la cuenta de AdMob |
| Verificar solo en el cliente una IAP cara | Se piratea trivialmente |

---

## Ver también

- [12 · 03 — Integraciones con servicios](../12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md) — el catálogo: qué extensión existe para qué
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — para tus propias notificaciones de logro
- [14 · Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — el guardado local que la nube complementa
- [14 · Multijugador](./14%20-%20Multijugador.md) — donde también se usa el evento async
