# 17 · Interoperabilidad con la web (HTML5)

> Cómo hacer que tu juego de GameMaker **hable con la página** que lo contiene, en los dos
> sentidos. Es lo que necesitas para guardar en un servidor, leer parámetros de la URL,
> integrarte con un portal o abrir un diálogo nativo del navegador.
>
> **Hueco detectado** al cruzar el [catálogo de tutoriales del foro](../07%20-%20Ecosistema/16%20-%20Cat%C3%A1logo%20de%20la%20secci%C3%B3n%20Tutorials%20del%20foro.md)
> con esta biblioteca. Mecanismo verificado contra el manual LTS 2026 el 2 de septiembre de 2026.

---

## El mecanismo, en una frase

**No hay una función `js_eval` en GML.** La comunicación se hace con una **extensión de
JavaScript**: un archivo `.js` dentro de una extensión del proyecto, que solo se compila para
el target HTML5.

| Dirección | Cómo |
|---|---|
| **GML → JavaScript** | Declaras la función en la extensión; la llamas desde GML como cualquier otra |
| **JavaScript → GML** | Prefijas tu función GML con **`gmcallback_`** y la llamas desde JS |

📘 [Crear una extensión](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/Creating_An_Extension.md) ·
📘 [Funciones de script](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Overview/Script_Functions.md)

---

## 1 · GML → JavaScript

### Crear la extensión

1. **Clic derecho en el navegador de recursos → Create → Extension.**
2. En el Inspector de la extensión, **Add Placeholder** → dale nombre (p. ej. `web`).
3. Sobre ese placeholder, **Add File** y elige tu `.js`.
4. Dentro del archivo, **Add Function** por cada función que quieras exponer a GML.

> ⚠️ **El `.js` solo se compila para HTML5.** En Windows, macOS o Android esas funciones **no
> existen**. Protege siempre las llamadas:
>
> ```gml
> if (os_browser != browser_not_a_browser) {
>     web_guardar("partida", json_stringify(datos));
> }
> ```

### El archivo JavaScript

```javascript
// web.js — guardar y leer del almacenamiento del navegador
function web_guardar(clave, valor) {
    try {
        window.localStorage.setItem(clave, valor);
        return 1;
    } catch (e) {
        return 0;          // modo privado, cuota llena, cookies bloqueadas…
    }
}

function web_leer(clave) {
    try {
        var v = window.localStorage.getItem(clave);
        return (v === null) ? "" : v;
    } catch (e) {
        return "";
    }
}

// leer un parámetro de la URL: mijuego.html?nivel=3
function web_param(nombre) {
    var p = new URLSearchParams(window.location.search);
    return p.get(nombre) || "";
}
```

### Declararlas en el IDE

Por cada función, en **Add Function** hay que rellenar:

| Campo | Valor para `web_guardar` |
|---|---|
| **Name** | `web_guardar` (el nombre con el que la llamas en GML) |
| **External Name** | `web_guardar` (el nombre real en el `.js`) |
| **Return Type** | `double` |
| **Arguments** | `string`, `string` |

> 🔺 **Solo hay dos tipos: `double` y `string`.** No puedes pasar structs ni arrays
> directamente. Para datos complejos, serializa:
> [`json_stringify`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing/json_stringify.md)
> al salir y
> [`json_parse`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing/json_parse.md)
> al volver.

### Usarlas desde GML

```gml
/// guardar la partida en el navegador
function guardar_web() {
    if (os_browser == browser_not_a_browser) return false;

    var _datos = { nivel: global.nivel, hp: global.hp, monedas: global.monedas };
    return web_guardar("partida", json_stringify(_datos)) == 1;
}

/// recuperarla
function cargar_web() {
    if (os_browser == browser_not_a_browser) return undefined;

    var _txt = web_leer("partida");
    if (_txt == "") return undefined;

    try {
        return json_parse(_txt);
    } catch (_e) {
        return undefined;      // datos corruptos de una versión anterior
    }
}
```

> 💡 **El `try`/`catch` alrededor de `json_parse` no es opcional.** Un jugador con datos
> guardados de una versión anterior de tu juego hará que el `parse` falle, y sin el `catch`
> el juego se cierra al arrancar.

---

## 2 · JavaScript → GML

Aquí entra el prefijo **`gmcallback_`**. Una función GML con ese prefijo **no se ofusca** al
compilar, así que conserva su nombre y JavaScript puede llamarla.

```gml
/// scr_web_callbacks — funciones que la página puede llamar
function gmcallback_pausar_juego() {
    global.pausado = true;
}

function gmcallback_cambiar_idioma(_codigo) {
    global.idioma = _codigo;
    senal_emitir("idioma_cambiado", { idioma: _codigo });
}
```

Y desde la página que contiene el juego:

```html
<button onclick="gmcallback_pausar_juego()">Pausa</button>
<button onclick="gmcallback_cambiar_idioma('es')">Español</button>
```

> 🔺 **Sin el prefijo `gmcallback_` esto no funciona.** El compilador renombra las funciones
> GML, y desde JavaScript no hay forma de saber el nombre nuevo. Es el detalle que hace que
> «no me funciona» sea la experiencia habitual la primera vez.
>
> 💡 Las funciones [`clickable_*`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Web_And_HTML5/Web_And_HTML5.md)
> usan este mismo mecanismo para superponer elementos HTML sobre el lienzo.

---

## 3 · Lo que NO puedes hacer en web

| Quiero… | Realidad |
|---|---|
| Redimensionar el lienzo con `window_set_size` | ❌ **No funciona en HTML5 ni GX.games.** El tamaño se define en las opciones del juego. Ver [16 · Exportar y publicar](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) |
| Guardar en el disco del jugador | ❌ Solo `localStorage`, y se borra al limpiar datos del navegador |
| Reproducir audio nada más cargar | ❌ Los navegadores lo bloquean hasta la primera interacción |
| Usar extensiones nativas (DLL, C++) | ❌ Solo `.js` |
| Grupos de texturas dinámicos | ❌ `texturegroup_*` no está en HTML5 |

📘 [Web y HTML5](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Web_And_HTML5/Web_And_HTML5.md)

---

## 3 bis · Desbloquear el audio: la pantalla «pulsa para empezar»

La fila de arriba dice que el navegador bloquea el audio hasta el primer gesto del jugador; esto
es la receta para resolverlo, no solo para enunciarlo. El mecanismo (`audio_system_is_available()`,
el evento async que avisa cuando el contexto cambia) ya está documentado en
[01 · 13 §11](../01%20-%20Fundamentos/13%20-%20Audio.md); lo que falta es **la pantalla que engancha
ese mecanismo con el flujo del juego**.

### El flujo: carga → «pulsa para empezar» → juego

```gml
/// obj_pulsa_para_empezar · Create — se entra aquí DESPUÉS de la carga, nunca durante
mostrar_prompt = true;

/// obj_pulsa_para_empezar · Draw GUI
if (mostrar_prompt)
{
    var _cx = display_get_gui_width()  / 2;
    var _cy = display_get_gui_height() / 2;
    draw_text_transformed(_cx, _cy, "Pulsa para empezar", 1.5, 1.5, 0);
}

/// obj_pulsa_para_empezar · Global Left Pressed — CUALQUIER clic o toque cuenta como el gesto
if (mostrar_prompt)
{
    mostrar_prompt = false;
    musica_arrancar();      // ver más abajo: aquí es la ÚNICA vez que hace falta comprobar nada
    room_goto(rm_menu);
}

/// scr_audio — musica_arrancar(), llamada UNA sola vez, desde dentro del gesto del jugador
function musica_arrancar()
{
    if (!audio_system_is_available())
    {
        // En navegadores raros el contexto sigue sin arrancar incluso tras el clic.
        // No revientes el juego por esto: sencillamente no metas música todavía y confía en
        // el evento async de 01 · 13 §11 para reintentarlo cuando el navegador lo permita.
        show_debug_message("audio no disponible tras el gesto; se reintentará solo");
        return;
    }
    audio_play_sound(mus_menu, 100, true);
}
```

> 💡 **El gesto vale para TODO el juego, no solo para el sonido que arranques ahí.** Una vez el
> navegador ve un clic o un toque dentro del juego, el contexto de audio queda desbloqueado para
> cualquier `audio_play_sound()` posterior, no solo para el de ese evento. Por eso basta con una
> pantalla, no con comprobar el gesto en cada sonido.
>
> ⚠️ **La comprobación no es exclusiva de HTML5.** `audio_system_is_available()` siempre devuelve
> `true` en escritorio y en móvil, así que puedes dejar el `if` puesto sin ramificar por
> `os_browser`: el mismo código sirve para todos los targets.

### La música de la pantalla de carga: no lo intentes

La room de carga (la barra de progreso, el logo del estudio) se ejecuta **antes** de que exista
ningún gesto: cualquier `audio_play_sound()` ahí falla en silencio o, según el navegador, ni
siquiera llega a sonar cuando el contexto se desbloquee después. No hay forma honesta de tener
música durante la carga en HTML5.

Lo que sí puedes hacer con esa espera es **precargar**, no reproducir: si la música del menú vive
en un *audio group* aparte, lánzalo con `audio_group_load()` durante la carga y compruébalo con
`audio_group_is_loaded()` antes de dar la pantalla de carga por terminada. Así, cuando el jugador
por fin pulsa, `audio_play_sound()` en `musica_arrancar()` no tiene que esperar a que el grupo
termine de bajar: suena al instante, sin el tartamudeo de un `audio_group_load()` disparado tarde.

---

## 3 ter · Memoria en HTML5: el techo real

[`01 · 15 §5`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md#5-el-garbage-collector-recolector-de-basura)
ya avisa de que en HTML5 la recogida de basura la hace el motor de JavaScript, no `gc_*()`. Lo
que falta decir es **cuánta memoria hay disponible antes de que algo falle**, porque en web no
es solo «menos que en escritorio»: es un techo que varía por navegador, por dispositivo, y que
**no da ninguna excepción que puedas capturar desde GML**.

**De dónde sale el techo.** El runtime HTML5 de GameMaker se compila a WebAssembly, y WASM usa
punteros de 32 bits — eso pone un **máximo absoluto de 4 GB** de memoria lineal por instancia,
según confirma el propio equipo de V8: *"up to 4GB of memory in WebAssembly applications"*
(v8.dev/blog/4gb-wasm-memory, consultado 2026-09-07). No todos los navegadores llegan ahí:
Chrome y Safari en desktop soportan ese máximo de 4 GB; Firefox históricamente limita el
**crecimiento** de una `WebAssembly.Memory` a 2 GB (issue oficial de Mozilla/WebAssembly,
consultado 2026-09-07). Esto ya deja claro que **el mismo build de GameMaker tiene techos
distintos según el navegador del jugador**, algo que no pasa en ningún export nativo.

⚠️ **Y esos 2-4 GB son el límite del motor JS, no el que de verdad vas a tener disponible.** En
**móvil el techo real es mucho más bajo y mucho más inconsistente** — un desarrollador que
midió el límite de memoria de Safari en iOS de forma sistemática reporta *"a web page in mobile
Safari on my 3rd generation iPhone SE at around 100 MB"* y *"on my 8th generation iPad at around
200 MB"* antes de que la pestaña muera (lapcatsoftware.com/articles/2026/1/7.html, artículo
fechado el 7 de enero de 2026), mientras que un hilo del propio foro de Apple Developer sobre un
iPhone 12 Pro mide **~1,5 GB** en un dispositivo «usado» normalmente, subiendo a ~3 GB tras un
reinicio completo (developer.apple.com/forums/thread/761666, consultado 2026-09-07). La
diferencia entre 100 MB y 3 GB en el mismo fabricante y familia de dispositivos no es un error
de medición: **es la prueba de que no hay UN número fiable** — depende del modelo exacto, la
versión de iOS/navegador, cuánta memoria tiene ya ocupada el sistema y el patrón concreto de
asignación de tu juego.

⚠️ **Lo que sí es constante: no hay excepción capturable.** El mismo artículo lo prueba
explícitamente: *"Using `try {} catch {}` blocks in JavaScript doesn't help at all; there's no
JavaScript exception to catch"* — cuando el navegador decide que ya es suficiente, recarga la
pestaña o la mata directamente, sin pasar por ningún camino de error que el código (ni el tuyo
en GML, ni el JavaScript generado por GameMaker) pueda interceptar. No existe un
`exception_unhandled_handler()` (§3 de
[`01 · 15`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md)) para esto:
un HTML5 sin memoria se ve, desde dentro del juego, exactamente igual que si alguien hubiera
cerrado la pestaña de golpe.

**Qué hacer con esto, en la práctica:**

- **Presupuesta memoria como si el objetivo fuera el peor dispositivo de la lista**, no el
  navegador de escritorio donde pruebas normalmente. Los cientos de MB de un móvil de gama baja,
  no los GB de un PC, son el número que importa para HTML5/itch.io/GX.games.
- **Vigila el crecimiento, no solo el pico.** Grupos de texturas que no se descargan
  (`texturegroup_unload()`,
  [`08 · 08`](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md#texturegroup_unloadgroupname)),
  estructuras de datos sin destruir (checklist de
  [`01 · 15 §8`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md#8-checklist-de-limpieza-de-recursos-din%C3%A1micos))
  y arrays que solo crecen entre rooms son, en HTML5, la diferencia entre «funciona toda la
  partida» y «se recarga solo a los diez minutos» — y el jugador nunca sabrá por qué.
- **Prueba en un móvil de verdad, en el navegador de verdad, antes de publicar** — el mismo
  principio de [`04 · 28 §6.5`](28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#65-medir-en-el-dispositivo-no-en-el-pc),
  aplicado aquí a Safari/Chrome móvil en vez de al export nativo. Un juego que va sobrado de
  memoria en tu portátil puede recargarse solo en un iPhone SE sin que el Debug Overlay (que
  [`01 · 15 §4`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md#4-nivel-3-el-debug-overlay)
  ya avisa que **no existe en HTML5**) te dé ninguna pista.

---

## 4 · Detectar dónde te estás ejecutando

```gml
/// ¿estamos en un navegador, y en cuál?
if (os_browser != browser_not_a_browser) {
    switch (os_browser) {
        case browser_chrome:   break;
        case browser_firefox:  break;
        case browser_safari:   break;
        case browser_edge:     break;
    }
    // tamaño real de la ventana del navegador
    var _w = browser_width;
    var _h = browser_height;
}
```

> 💡 **`os_browser` frente a `os_type`:** `os_type` te dice el sistema operativo
> (`os_windows`, `os_macosx`…) incluso dentro de un navegador. Para saber si estás en web,
> comprueba **`os_browser != browser_not_a_browser`**.
>
> 🔺 **Ojo:** existe `os_operagx` para GX.games, pero **no está documentada en el manual** —
> se encontró leyendo el runtime. Ver
> [20 · Lo que el manual no documenta](../08%20-%20Referencia%20GML%20completa/20%20-%20Lo%20que%20el%20manual%20no%20documenta.md).

---

## 5 · Comunicarte con tu propio servidor

Para guardar puntuaciones o partidas en un servidor **no necesitas JavaScript**: GML trae
peticiones HTTP asíncronas, y funcionan en todos los targets.

```gml
/// Create
peticion = http_post_string("https://tu-servidor.com/puntuacion",
                            json_stringify({ jugador: global.nombre, puntos: global.puntos }));

/// Async - HTTP
if (async_load[? "id"] == peticion) {
    if (async_load[? "status"] == 0) {
        var _r = json_parse(async_load[? "result"]);
        show_debug_message($"guardado: {_r.ok}");
    }
}
```

> ⚠️ **En web te va a frenar el CORS.** El navegador bloquea peticiones a otro dominio salvo
> que el servidor responda con las cabeceras `Access-Control-Allow-Origin`. No es un fallo de
> GameMaker: hay que configurarlo **en el servidor**.
>
> 💡 **Nunca metas una clave de API en el juego.** Todo lo que compilas a HTML5 es
> **público**: cualquiera puede leer el JavaScript resultante. Las claves van en tu servidor.

---

## 6 · Autenticación con tokens sobre HTTP

El ejemplo del §5 sube una puntuación **sin identificarse**: cualquiera que conozca la URL
puede mandar el mismo POST haciéndose pasar por otro jugador. En cuanto tu backend distingue
cuentas de usuario —o simplemente quieres saber quién manda cada petición—, hace falta
**autenticación**, y el patrón estándar sobre HTTP es un **token portador** (*bearer token*) en
la cabecera `Authorization`.

`http_post_string()` (usado en el §5) no acepta cabeceras. Para eso está
[`http_request()`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asynchronous_Functions/HTTP/http_request.md),
que recibe un cuarto argumento: un `ds_map` de cabeceras. El propio manual lo dice sin rodeos:
*"una solicitud HTTP puede usarse para muchas cosas, como la autenticación mediante cabeceras
HTTP si usas APIs RESTful"*, y su ejemplo oficial construye exactamente ese `ds_map` con una
clave `"Authorization"`.

```gml
/// @func servidor_peticion_autenticada(_url, _metodo, _token, _cuerpo)
/// @desc Envía una petición HTTP con un token de sesión en la cabecera Authorization.
///       El token NUNCA se escribe a mano en el código: lo devuelve tu propio endpoint de
///       login (más abajo) y vive solo en memoria mientras dura la sesión — nunca en el .sav.
/// @param {String} _url
/// @param {String} _metodo   "GET", "POST"...
/// @param {String} _token    El token de sesión ya obtenido (ver login más abajo).
/// @param {String} _cuerpo   "" si no hace falta cuerpo (por ejemplo, en un GET).
/// @returns {Real} El Async Request ID, para comparar en el evento Async - HTTP.
function servidor_peticion_autenticada(_url, _metodo, _token, _cuerpo)
{
    var _headers = ds_map_create();
    ds_map_add(_headers, "Authorization", "Bearer " + _token);
    ds_map_add(_headers, "Content-Type", "application/json");

    var _id = http_request(_url, _metodo, _headers, _cuerpo);

    // http_request() ya copió lo que necesitaba de _headers al enviar: destrúyelo siempre
    // después de la llamada, igual que cualquier otro ds_map que no vayas a reutilizar.
    ds_map_destroy(_headers);
    return _id;
}
```

**De dónde sale el token: un login normal que devuelve una cadena, no una contraseña
permanente incrustada en el juego.**

```gml
/// @desc Botón "Entrar" del formulario de login. NUNCA escribas un usuario/contraseña real
///       aquí: estas dos variables vienen de campos de texto que rellena el jugador.
peticion_login = http_post_string(
    "https://TU-SERVIDOR-AQUI.example/login",                          // ⚠️ marcador: tu endpoint real
    json_stringify({ usuario: campo_usuario_texto, contrasena: campo_contrasena_texto }));

/// Async - HTTP
if (async_load[? "id"] == peticion_login)
{
    if (async_load[? "status"] == 0 && async_load[? "http_status"] == 200)
    {
        var _r = json_parse(async_load[? "result"]);
        global.token_sesion = _r.token;      // solo en memoria; se pierde al cerrar el juego
    }
    else
    {
        // Credenciales inválidas, servidor caído, rate limit (ver 13/10 §14.7)...
        mostrar_error_login();
    }
}
```

Tres reglas que ya son las de esta biblioteca aplicadas a este caso concreto:

- **La contraseña viaja en el cuerpo del POST, nunca en la URL** (una URL queda en logs de
  servidor y en el historial del navegador) **y el endpoint tiene que estar detrás de HTTPS**
  —`https://`, o `network_socket_wss` si hablas por WebSocket en vez de HTTP— porque sin
  cifrado de transporte tanto la contraseña como el token viajan **en claro**. Verifícalo antes
  de escribir nada: `curl -I https://tu-endpoint` debe responder, no solo `http://`.
- **El servidor decide si el token es válido, nunca el cliente.** Un token caducado o revocado
  debe hacer que el servidor rechace la petición (normalmente con `401 Unauthorized`) aunque el
  cliente insista en mandarlo — la misma regla de
  [`04 · 14`](14%20-%20Multijugador.md) §2.2, aplicada a HTTP en vez de a sockets.
- **El endpoint de login es el primero que necesita *rate limiting*.** Sin límite de intentos
  por cuenta/IP, alguien puede probar contraseñas por fuerza bruta. Patrón completo, sin
  símbolos de GML nuevos porque es lógica de servidor:
  [`13 · 10 — Testing y QA`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md) §14.7.

Símbolos verificados: `http_request`, `http_post_string`, `ds_map_create`, `ds_map_add`,
`ds_map_destroy`, `json_stringify`, `json_parse`.

---

## Ver también

- [16 · Exportar y publicar](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) — la casilla que centra el juego, y las limitaciones de HTML5
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — para que los callbacks no acoplen media base de código
- [Catálogo del foro](../07%20-%20Ecosistema/16%20-%20Cat%C3%A1logo%20de%20la%20secci%C3%B3n%20Tutorials%20del%20foro.md) — el hilo original que destapó este hueco
- [14 · Multijugador](14%20-%20Multijugador.md) §2.2 — «nunca confíes en el cliente», la regla que el §6 de este documento aplica a HTTP
- [13 · 10 — Testing y QA](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md) §14 — validación en servidor, replay firmado y §14.7 *rate limiting*
- [01 · 15 §5 y §11](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) — el Garbage Collector en HTML5 (§3 ter de este documento parte de ahí) y las herramientas externas de perfilado
