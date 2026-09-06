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

## Ver también

- [16 · Exportar y publicar](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) — la casilla que centra el juego, y las limitaciones de HTML5
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — para que los callbacks no acoplen media base de código
- [Catálogo del foro](../07%20-%20Ecosistema/16%20-%20Cat%C3%A1logo%20de%20la%20secci%C3%B3n%20Tutorials%20del%20foro.md) — el hilo original que destapó este hueco
