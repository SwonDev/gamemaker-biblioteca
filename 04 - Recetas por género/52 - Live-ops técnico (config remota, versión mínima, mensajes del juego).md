# 52 · Live-ops técnico (config remota, versión mínima, mensajes del juego)

> **Para quién es esto:** cualquier juego que quiera cambiar un comportamiento **sin publicar
> una actualización en la tienda** — activar un evento un fin de semana, subir el porcentaje de
> jugadores que ven una nueva mecánica, obligar a actualizar tras un parche crítico, avisar de
> una caída de servidor. Todo lo de aquí es **técnico y de una sola persona**: un fichero de
> configuración servido por HTTP y un puñado de comprobaciones en el cliente.
>
> **Lo que esto NO es**: un servicio en vivo completo (temporadas con calendario, pases de
> temporada, eventos con recompensas exclusivas, equipo dedicado a contenido). Esa decisión —y el
> argumento razonado de por qué casi nunca compensa para un estudio pequeño— ya está escrita en
> [`13 · 20 §1.8`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md#18--retención-y-live-ops--y-el-argumento-de-no-hacerlas):
> no se repite aquí. Este documento es la pieza **de ingeniería** que falta aunque decidas no
> montar un live-ops completo — la diferencia entre "puedo apagar un evento roto sin esperar
> a que Apple revise una build" y no poder hacerlo en absoluto.
>
> Tampoco cubre: backend con autoridad de servidor para partidas online (eso es
> [`04 · 14 — Multijugador`](./14%20-%20Multijugador.md)), ni anti-trampas de puntuaciones (eso
> es [`13 · 10 §14`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#14--seguridad-y-anti-trampas)).

---

## 1 · Los principios

### 1.1 Qué es «remote config» y por qué le importa a un estudio de una persona

**Remote config** es, en su forma mínima, un fichero de configuración que el juego **descarga**
en vez de traer incrustado en el build. La diferencia práctica es enorme: cambiar una constante
del build exige recompilar, volver a subir el paquete y esperar la revisión de la tienda (horas
en Steam, **días** en Apple); cambiar un valor en el fichero remoto tarda lo que tarde tu próximo
`http_request` — normalmente segundos, sin ninguna revisión de por medio.

No hace falta un backend de aplicación con base de datos y autenticación para esto. La forma más
barata que existe: **un JSON estático subido a cualquier alojamiento de ficheros con URL pública**
(un bucket S3, GitHub Pages, Netlify, el propio hosting de tu web). El "backend" es literalmente
editar un fichero y subirlo. Solo hace falta un servidor de aplicación de verdad si necesitas
lógica del lado servidor (por ejemplo, feature flags distintos por región geográfica detectada
por IP) — fuera de alcance aquí, y prescindible para el 90 % de los casos de esta receta.

### 1.2 El cliente SIEMPRE tiene un valor por defecto local

**Regla que gobierna todo lo demás**: el juego tiene que funcionar **igual de bien** si el
`http_request` nunca llega a responder — sin red, primer arranque sin conexión, tu servidor
caído, o simplemente porque el jugador nunca abrió el menú que dispara la petición. Cada clave de
configuración remota tiene un **valor por defecto local**, empaquetado en el build, y el juego
arranca con esos valores mientras la respuesta de red (si llega) los sustituye por encima. Un
juego que se queda en pantalla de carga esperando a tu servidor ha convertido tu infraestructura
en un punto único de fallo del juego entero — exactamente lo que la config remota debería evitar,
no causar.

### 1.3 Qué NO cubre este documento

- **La decisión de si hacer live-ops** (calendario de temporadas, equipo dedicado, pase de
  temporada): [`13 · 20 §1.8`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md#18--retención-y-live-ops--y-el-argumento-de-no-hacerlas).
- **Autoridad de servidor para partidas competitivas o multijugador**: nada de lo de aquí impide
  que un jugador con Cheat Engine cambie su reloj local para "activar" un evento antes de tiempo
  (§3.7 lo explica) — para eso hace falta la misma disciplina de
  [`13 · 10 §14.1`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#141-el-hecho-del-que-se-deriva-todo-lo-demás)
  ("el cliente es territorio enemigo"): la config remota es para **contenido y comunicación**,
  no para decidir puntuaciones ni desbloqueos con valor competitivo.
- **Analítica y telemetría** (medir qué hace el jugador): eso es
  [`13 · 01 §9.5-9.7`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json).
  Esta receta es la dirección contraria del cable: el servidor le dice algo al cliente, no al
  revés.

---

## 2 · El método, paso a paso

1. **Diseña el esquema antes de escribir código**: qué claves existen, de qué tipo es cada una, y
   cuál es su valor por defecto si nunca llega respuesta. Escríbelo como un struct: es
   literalmente el JSON que vas a servir.
2. **Elige dónde vive el JSON**: un fichero estático en cualquier hosting con URL pública basta
   para el 90 % de los casos (§1.1). Solo necesitas algo más si vas a personalizar por jugador o
   región en el propio servidor.
3. **El cliente pide, cachea localmente y refresca con una cadencia razonable** (minutos, no cada
   frame ni cada segundo): §3.2.
4. **Cada pieza de la tabla de abajo es una comprobación independiente** sobre la config ya
   cargada (remota si llegó, local si no): no dependen unas de otras.

| Pieza | Qué resuelve | Sección |
|---|---|---|
| **Feature flags porcentuales** | Activar una mecánica nueva para un % de instalaciones, sin tocar el build | §3.3 |
| **Versión mínima del cliente** | Bloquear o avisar a quien juega con una versión con un bug crítico ya parcheado | §3.4 |
| **Mensaje del día (MOTD)** | Comunicar algo puntual sin esperar a la próxima build | §3.5 |
| **Modo mantenimiento** | Avisar con claridad mientras despliegas un cambio de servidor, en vez de dejar el juego roto en silencio | §3.6 |
| **Eventos de temporada por fecha** | Contenido que se activa/desactiva solo entre dos fechas | §3.7 |

---

## 3 · Cómo se traduce a GameMaker

### 3.1 El esquema y los valores por defecto locales

```gml
// ═══ scr_liveops_config ═══
// Todas las claves que puede traer la config remota, con un valor por defecto que
// hace que el juego funcione bien SIN backend (§1.2). Si añades una clave nueva,
// añádela aquí primero: es el contrato entre el JSON remoto y el juego.

function liveops_config_por_defecto()
{
    return {
        version_minima      : GM_version,   // "todo vale" hasta que subas la barrera a mano
        evento_doble_xp     : false,
        evento_doble_xp_pct : 0,             // % de instalaciones con el flag activo (0-100)
        motd_id             : "",            // vacío = no hay MOTD que mostrar
        motd_texto          : "",
        mantenimiento       : false,
        mantenimiento_msg   : "",
        temporada_inicio    : "",            // "AAAA-MM-DD", vacío = sin temporada
        temporada_fin       : ""
    };
}
```

### 3.2 Pedir la config remota: caché local, sin bloquear el arranque

```gml
// ⚠️ LIVEOPS_ENDPOINT es un marcador, no una URL real: tu JSON/backend propio va aquí,
// NUNCA en el código versionado — Included File sin subir o variable de entorno del
// pipeline de build, la misma regla que cualquier secreto (13 · 01 §9.7 aplica lo mismo).
#macro LIVEOPS_ENDPOINT           ""
#macro LIVEOPS_CONFIG_ARCHIVO     "liveops_config.json"
#macro LIVEOPS_REFRESCO_SEGUNDOS  (30 * 60)            // cada 30 min sobra: no es telemetría

global.liveops = liveops_config_por_defecto();
global.liveops_peticion_id     = -1;
global.liveops_ultimo_refresco = -999999999999;        // fuerza el primer intento

/// @description Aplica sobre global.liveops cualquier clave presente en un JSON.
///              Uso interno: lo comparten la carga de caché y la respuesta de red.
function __liveops_aplicar_json(_texto)
{
    try
    {
        var _datos = json_parse(_texto);
        if (!is_struct(_datos)) { return false; }

        var _claves = struct_get_names(_datos);
        var _i;
        for (_i = 0; _i < array_length(_claves); _i++)
        {
            struct_set(global.liveops, _claves[_i], struct_get(_datos, _claves[_i]));
        }
        return true;
    }
    catch (_e)
    {
        show_debug_message("liveops: JSON inválido, se ignora");
        return false;
    }
}

/// @description Llamar UNA vez al arrancar: aplica la última config que se guardó
///              localmente, si la hay, mientras (si hay red) llega una más nueva.
function liveops_cargar_cache()
{
    var _ruta = game_save_id + LIVEOPS_CONFIG_ARCHIVO;
    if (!file_exists(_ruta)) { return; }

    var _f = file_text_open_read(_ruta);
    var _texto = "";
    while (!file_text_eof(_f)) { _texto += file_text_read_string(_f); file_text_readln(_f); }
    file_text_close(_f);

    __liveops_aplicar_json(_texto);
}

/// @description Pide la config al servidor si toca (cadencia de LIVEOPS_REFRESCO_SEGUNDOS,
///              nunca más de una petición en vuelo a la vez). No bloquea nada: la respuesta
///              llega sola al evento Async - HTTP.
function liveops_refrescar()
{
    if (LIVEOPS_ENDPOINT == "") { return; }                          // sin backend: solo defaults
    if (global.liveops_peticion_id != -1) { return; }                // ya hay una en vuelo
    if (get_timer() - global.liveops_ultimo_refresco < LIVEOPS_REFRESCO_SEGUNDOS * 1000000) { return; }

    var _headers = ds_map_create();
    global.liveops_peticion_id = http_request(LIVEOPS_ENDPOINT, "GET", _headers, "");
    ds_map_destroy(_headers);
}
```

```gml
/// obj_control · Async - HTTP
if (async_load[? "id"] == global.liveops_peticion_id)
{
    global.liveops_peticion_id     = -1;
    global.liveops_ultimo_refresco = get_timer();

    if (async_load[? "status"] == 0)
    {
        var _texto = async_load[? "result"];
        if (__liveops_aplicar_json(_texto))
        {
            // Se guarda tal cual para el PRÓXIMO arranque, aunque entonces no haya red.
            var _f = file_text_open_write(game_save_id + LIVEOPS_CONFIG_ARCHIVO);
            file_text_write_string(_f, _texto);
            file_text_close(_f);
        }
    }
    // status < 0 (sin red, servidor caído...): global.liveops se queda como estaba —
    // la caché local o, en el primer arranque sin caché, los valores por defecto.
    // liveops_refrescar() ya reintentará solo en el próximo momento en que se llame.
}
```

> 💡 **Llama a `liveops_cargar_cache()` una vez en el arranque y a `liveops_refrescar()` en
> cada cambio de sala o cada pocos minutos**, nunca en el Step. No es distinto del criterio de
> "un intento por sala" que ya usa el envío de telemetría de
> [`13 · 01 §9.7`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#97--de-volcado-local-a-backend-real-http_request-con-cola-y-reintento):
> reutiliza una cadencia que ya existe, no la inventes de nuevo para cada sistema.

### 3.3 Feature flags: activación gradual sin identificar a nadie

Para un lanzamiento gradual (0 % → 10 % → 50 % → 100 % a lo largo de unos días, mirando que nada
se rompa antes de subir el porcentaje) hace falta que **cada instalación** caiga siempre del
mismo lado de la barrera — si el jugador entra y sale del grupo con el flag en cada sesión, no
estás probando nada, solo generando ruido. La forma más simple que no manda nada a ningún
sitio: un número aleatorio **generado una sola vez y guardado en local**, nunca enviado al
servidor — el servidor solo declara un porcentaje, la decisión de "¿me toca a mí?" la hace el
cliente él solo:

```gml
/// @description Un número 0-99 estable para ESTA instalación del juego. Se genera una
///              sola vez (primer arranque) y se guarda en Configuración (13 · 06 §3.10),
///              nunca en la partida y nunca se envía a ningún backend: no identifica al
///              jugador, solo decide en qué lado de un porcentaje cae este dispositivo.
function liveops_bucket_instalacion()
{
    if (variable_global_exists("__liveops_bucket")) { return global.__liveops_bucket; }

    var _ruta = game_save_id + "liveops_bucket.txt";
    if (file_exists(_ruta))
    {
        var _f = file_text_open_read(_ruta);
        global.__liveops_bucket = real(file_text_read_string(_f));
        file_text_close(_f);
    }
    else
    {
        global.__liveops_bucket = irandom(99);
        var _f = file_text_open_write(_ruta);
        file_text_write_string(_f, string(global.__liveops_bucket));
        file_text_close(_f);
    }

    return global.__liveops_bucket;
}

/// @param {Real} _porcentaje  0-100, el valor que declara el servidor para este flag.
/// @returns {Bool}
function liveops_flag_activo(_porcentaje)
{
    return liveops_bucket_instalacion() < _porcentaje;
}
```

```gml
/// uso: el servidor sube evento_doble_xp_pct de 0 a 25 sin tocar el build
if (liveops_flag_activo(global.liveops.evento_doble_xp_pct))
{
    global.multiplicador_xp = 2;
}
```

> ⚠️ Esto **no** es A/B testing con significancia estadística ni segmentación por
> comportamiento — es un interruptor gradual y estable por instalación, que es todo lo que hace
> falta para un lanzamiento por fases de una sola persona.

### 3.4 Versión mínima del cliente

`GM_version` (documentada en
[`08 · 19`](../08%20-%20Referencia%20GML%20completa/19%20-%20Sistema,%20compilador%20y%20entorno.md))
es el número de versión que **tú mismo** pones en Opciones de Juego → General, como string
(`"1.4.2"`). Compararla contra un mínimo servido por el backend detecta a quien sigue con una
build vieja tras un parche crítico:

```gml
/// @description Compara dos versiones "N.N.N…" COMPONENTE A COMPONENTE, nunca como texto:
///              "1.9" > "1.10" alfabéticamente, pero NO como número de versión.
/// @returns {Real}  -1 si _a es anterior, 1 si es posterior, 0 si son iguales.
function version_comparar(_a, _b)
{
    var _pa = string_split(_a, ".");
    var _pb = string_split(_b, ".");
    var _max = max(array_length(_pa), array_length(_pb));

    var _i;
    for (_i = 0; _i < _max; _i++)
    {
        var _na = (_i < array_length(_pa)) ? real(_pa[_i]) : 0;
        var _nb = (_i < array_length(_pb)) ? real(_pb[_i]) : 0;
        if (_na != _nb) { return sign(_na - _nb); }
    }
    return 0;
}

/// @returns {Bool}  true si esta build es MÁS ANTIGUA que la mínima que acepta el backend.
function liveops_version_bloqueada()
{
    return version_comparar(GM_version, global.liveops.version_minima) < 0;
}
```

```gml
/// obj_menu_principal · Create — tras el primer liveops_cargar_cache()/liveops_refrescar()
if (liveops_version_bloqueada())
{
    room_goto(rm_actualizar_obligatorio);
}
```

```gml
/// rm_actualizar_obligatorio · Draw GUI
draw_text(x, y, $"Hay una actualización obligatoria disponible.\n"
              + $"Tu versión: {GM_version} · Mínima requerida: {global.liveops.version_minima}\n\n"
              + "Actualiza desde la tienda para seguir jugando.");
```

> 🔺 **El juego no puede forzar la actualización él mismo** — eso lo hace la tienda (App Store,
> Steam, Google Play), no tu código. Lo único que puedes hacer desde GML es **bloquear el
> avance** con un mensaje claro y, si tienes un enlace directo a la ficha de la tienda,
> mostrarlo. Para el jugador sin conexión (que nunca recibe el bloqueo): sigue jugando con la
> versión vieja hasta que se conecte — es el mismo principio de §1.2, aplicado también a esto.

### 3.5 Mensaje del día (MOTD), sin repetirlo cada sesión

```gml
/// @description true si hay un MOTD nuevo (por id) que este jugador aún no vio.
function liveops_motd_pendiente()
{
    if (global.liveops.motd_texto == "") { return false; }

    ini_open("config.ini");
    var _visto = ini_read_string("liveops", "motd_visto", "");
    ini_close();

    return (global.liveops.motd_id != _visto);
}

function liveops_motd_marcar_visto()
{
    ini_open("config.ini");
    ini_write_string("liveops", "motd_visto", global.liveops.motd_id);
    ini_close();
}
```

```gml
/// obj_menu_principal · Create
if (liveops_motd_pendiente())
{
    mostrar_dialogo(global.liveops.motd_texto, liveops_motd_marcar_visto);   // el callback
                                                                              // marca "visto"
                                                                              // al cerrarlo
}
```

`motd_id` es lo que distingue "un mensaje nuevo" de "el mismo de siempre": cámbialo (una fecha,
un número que subes a mano) cada vez que publiques un MOTD distinto; si solo cambiaras el texto
sin el id, un jugador que ya vio "hay evento este finde" no volvería a ver "el evento ya acabó"
porque el `ini` seguiría marcando el mensaje como visto.

### 3.6 Modo mantenimiento

```gml
/// obj_menu_principal · Create — antes de dejar avanzar a nada online
if (global.liveops.mantenimiento)
{
    room_goto(rm_mantenimiento);
}
```

```gml
/// rm_mantenimiento · obj_mantenimiento · Draw GUI
var _msg = (global.liveops.mantenimiento_msg != "")
    ? global.liveops.mantenimiento_msg
    : "El juego está en mantenimiento. Vuelve a intentarlo en unos minutos.";
draw_text(x, y, _msg);
```

La única diferencia real con el MOTD es que **bloquea**, no solo informa: úsalo cuando lo que
sea que dependa de tu servidor (un ranking online, un backend de partidas) esté realmente caído,
no como sustituto de un MOTD para avisos que no impiden jugar.

### 3.7 Eventos de temporada con fecha comprobada por el cliente

```gml
/// @description "AAAA-MM-DD" → datetime a medianoche de ese día. -1 si el formato no cuadra.
function __liveops_fecha_a_datetime(_fecha_iso)
{
    var _partes = string_split(_fecha_iso, "-");
    if (array_length(_partes) != 3) { return -1; }

    return date_create_datetime(real(_partes[0]), real(_partes[1]), real(_partes[2]), 0, 0, 0);
}

/// @returns {Bool}  true si la fecha/hora ACTUAL DEL CLIENTE cae dentro de la temporada.
function liveops_temporada_activa()
{
    if (global.liveops.temporada_inicio == "" || global.liveops.temporada_fin == "") { return false; }

    var _inicio = __liveops_fecha_a_datetime(global.liveops.temporada_inicio);
    var _fin    = __liveops_fecha_a_datetime(global.liveops.temporada_fin);
    if (_inicio == -1 || _fin == -1) { return false; }

    var _ahora = date_current_datetime();
    return (date_compare_datetime(_ahora, _inicio) >= 0) && (date_compare_datetime(_ahora, _fin) <= 0);
}
```

```gml
/// uso: mostrar decoración/tienda de temporada solo mientras esté activa
if (liveops_temporada_activa())
{
    instance_create_layer(x, y, "Decoracion", obj_decoracion_temporada);
}
```

> ⚠️ **Esto compara contra el reloj del PROPIO dispositivo del jugador**, que él controla por
> completo (`date_current_datetime()` no puede protegerse de eso — es la misma idea que el
> *speedhack* de
> [`13 · 10 §14.4`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#144-editar-la-memoria-en-caliente-qué-hace-de-verdad-un-cheat-engine),
> aplicada a la fecha en vez de al tiempo transcurrido). Para un evento **cosmético** (decoración
> de temporada, skin de menú) esto es más que suficiente: el peor caso es que alguien vea la
> decoración un día antes adelantando el reloj, sin ninguna consecuencia real. Para un evento
> con **recompensa competitiva o de valor** (un objeto exclusivo con ventaja de juego, una
> entrada a un ranking), la fecha tiene que decidirla el servidor, no compararse en el cliente —
> la misma frontera que traza
> [`13 · 10 §14.1`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#141-el-hecho-del-que-se-deriva-todo-lo-demás).

### 3.8 Por qué todo esto no toca la tienda

Ninguna de las cinco piezas de arriba está en `GM_version`, en un Included File del build ni en
ninguna constante compilada: todas viven en `global.liveops`, rellenado desde un JSON que **tú**
subes cuando quieres, a la URL que quieras. Eso significa: **cambiar cualquiera de estos valores
no dispara ninguna revisión de tienda**, porque el binario que el jugador tiene instalado no
cambia — solo cambia lo que ese binario descarga la próxima vez que pregunta. Es la diferencia
entre esperar la revisión de Apple para apagar un evento roto y apagarlo subiendo un fichero.

---

## 4 · Checklist

```
[ ] ¿Cada clave de config remota tiene un valor por defecto local funcional? (§1.2, §3.1)
[ ] ¿El juego arranca y es jugable SIN esperar respuesta del servidor?
[ ] ¿liveops_refrescar() tiene cadencia (minutos), no se llama en el Step?
[ ] ¿La config que llega se guarda en caché local para el próximo arranque sin red? (§3.2)
[ ] ¿El bucket de feature flags es estable por instalación y NUNCA se envía al servidor? (§3.3)
[ ] ¿La versión mínima compara componente a componente, no como texto? (§3.4)
[ ] ¿El MOTD usa un id para no repetirse ni saltarse un mensaje nuevo? (§3.5)
[ ] ¿El modo mantenimiento tiene pantalla propia, no un cartel encima del menú roto? (§3.6)
[ ] ¿Los eventos de temporada por fecha de cliente son solo cosméticos, nunca competitivos? (§3.7)
[ ] ¿LIVEOPS_ENDPOINT (y cualquier otro secreto) está fuera del código versionado?
```

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo se evita |
|---|---|---|
| El juego se congela en una pantalla de carga esperando la config | Se trató la petición como bloqueante | §1.2: siempre hay defaults locales; el juego arranca con ellos |
| El feature flag cambia de jugador entre sesiones | Se decidió con `irandom()` en cada arranque, sin guardar nada | §3.3: el bucket se genera UNA vez y se persiste en local |
| La versión mínima compara "1.9" > "1.10" | Comparación de strings en vez de componente a componente | §3.4: `version_comparar()` parte por `.` y compara como `Real` |
| El MOTD de la semana pasada vuelve a aparecer | Se cambió el texto pero no el `motd_id` | §3.5: el `ini` guarda el id visto, no el texto |
| Un evento de temporada "competitivo" se activa un día antes con el reloj adelantado | Se confió en `date_current_datetime()` del cliente para algo con valor real | §3.7: cualquier cosa con valor competitivo la decide el servidor |
| `LIVEOPS_ENDPOINT` con la URL real subido al repositorio | Se trató como una constante más, no como un secreto | Fuera del código versionado — la misma regla que cualquier clave o token |
| Se lanza un segundo `http_request` de config mientras el primero sigue en vuelo | No se comprobó `global.liveops_peticion_id` antes de pedir de nuevo | §3.2: el `if` de "ya hay una en vuelo" antes de cada petición |

---

## Ver también

- [13 · 20 §1.8 — Retención y live ops, y el argumento de no hacerlas](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md#18--retención-y-live-ops--y-el-argumento-de-no-hacerlas) — la decisión de negocio que este documento no repite
- [13 · 01 §9.5-9.7 — Telemetría y su envío por HTTP](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json) — la dirección contraria del cable: el cliente le habla al servidor
- [13 · 10 §14 — Seguridad y anti-trampas](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#14--seguridad-y-anti-trampas) — por qué el cliente nunca decide algo con valor competitivo
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — INI para configuración, JSON para datos estructurados, ambos usados aquí
- [04 · 43 — Modding y contenido externo](./43%20-%20Modding%20y%20contenido%20externo.md) — otro caso de "el cliente descarga algo de fuera del build", con el sandbox y `texturegroup_add`
- [04 · 20 — Servicios de plataforma](./20%20-%20Servicios%20de%20plataforma%20%28logros%2C%20anuncios%2C%20compras%29.md) — logros, anuncios, compras y nube: los servicios que SÍ requieren una extensión oficial, a diferencia de esta receta que solo usa `http_request`

---

## Fuentes

- `http_request` — manual oficial:
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asynchronous_Functions/HTTP/http_request.htm>
  (espejo en español consultado el 2026-09-07: `09 - Manual oficial/manual-lts-2026-es/.../http_request.md`)
- `GM_version` — manual oficial:
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/OS_And_Compiler/GM_version.htm>
- `date_compare_datetime` — manual oficial:
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/date_compare_datetime.htm>
- Todos los símbolos de GML de este documento verificados con `python3 "_indice/buscar.py" <símbolo>`
  contra el runtime 2026.0.0.23 el 2026-09-07 (lista completa al final del informe de esta ronda).
