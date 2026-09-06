# 19 · Sistema, compilador y entorno en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## Novedades de 2026 en esta área

### `GM_runtime_type` — detectar el runtime

GameMaker LTS 2026 distingue entre dos runtimes:

| Valor | Runtime |
| --- | --- |
| `"gms2"` | El runtime clásico de GameMaker. |
| `"gmrt"` | El nuevo runtime GMRT (GameMaker Runtime). |

```gml
show_debug_message($"Runtime en uso: {string_upper(GM_runtime_type)}");

if (GM_runtime_type == "gmrt")
{
    // comportamiento específico del nuevo runtime
}
```

### `os_get_info` — información detallada del sistema

Devuelve un **DS map** con datos del sistema operativo y del hardware. Es la forma
moderna de obtener información que antes no estaba disponible.

```gml
var _info = os_get_info();
show_debug_message(_info);
ds_map_destroy(_info);     // ⚠ obligatorio: es un DS map
```

Claves que aparecen en **todas** las plataformas salvo HTML5:

- `is64bit`: `true` o `false`, según si el runner va en 64 bits.

Claves adicionales en **Windows** (muy útiles para extensiones):

- `udid`: identificador único de la máquina.
- `video_d3d11_device`, `video_d3d11_context`, `video_d3d11_swapchain`: punteros a los objetos de DX11.
- `video_adapter_vendorid`, `video_adapter_deviceid`, `video_adapter_subsysid`, `video_adapter_revision`.
- `video_adapter_description`, `video_adapter_dedicatedvideomemory`, `video_adapter_dedicatedsystemmemory`, `video_adapter_sharedsystemmemory`.

Claves adicionales en **macOS** (información de OpenGL):

- `udid`, `gl_vendor_string`, `gl_version_string`, `gl_renderer_string`.

> El contenido exacto depende del sistema y del dispositivo, así que **pruébalo en todas
> las plataformas que vayas a publicar**.

---

## Constantes de `os_type`

| Constante | Sistema |
| --- | --- |
| `os_windows` | Windows |
| `os_macosx` | macOS X |
| `os_linux` | Linux |
| `os_android` | Android |
| `os_ios` | iOS (iPhone, iPad, iPod Touch) |
| `os_tvos` | Apple tvOS |
| `os_gxgames` | GX.games |
| `os_operagx` | Opera GX |
| `os_ps4`, `os_ps5` | PlayStation 4 y 5 |
| `os_switch` | Nintendo Switch |
| `os_xboxone`, `os_xboxseriesxs` | Xbox One y Xbox Series X|S |

---

## Opciones de `gml_pragma`

`gml_pragma` afecta a **cómo se compila** el proyecto. Las directivas se preprocesan
antes de compilar, así que pueden colocarse en cualquier parte del código.

| Directiva | Qué hace |
| --- | --- |
| `"forceinline"` | Pide al compilador de C++ que **inline** la función. Solo con YYC. Aumenta el tamaño del ejecutable y el tiempo de compilación. |
| `"global", "<código>"` | Ejecuta **código GML en ámbito global** en tiempo de compilación, antes de la primera room. Ejemplo: `gml_pragma("global", "Init()");` |
| `"optimise", "<opt>", "<control>"` | Sugerencia de optimización al compilador. Ejemplo: `gml_pragma("optimise", "js_array_check", "push, off");` |
| `"PNGCrush"` | Aplica **PNGCrush** a cada textura generada. Ahorra tamaño, pero aumenta mucho el tiempo de compilación. |
| `"Texgroup.Scale", "<grupo>", "<divisor>"` | Escala las texturas del grupo indicado. Ejemplo: `gml_pragma("Texgroup.Scale", "level1", "2");` |
| `"UnityBuild", "<true/false>"` | Colapsa todos los `.cpp` en uno solo. Compila más rápido, pero sin caché. Solo YYC. |
| `"AllowReentrantStatic"` | Recupera el comportamiento **antiguo** de inicialización de `static` (versiones hasta 2024.8). Solo para proyectos existentes: GMRT no lo permitirá. |
| `"MarkTagAsUsed", "<tag>"` | Con la opción «eliminar assets sin usar» activada, **impide** que se eliminen los assets que lleven ese **tag**. Imprescindible si cargas assets dinámicamente en tiempo de ejecución. |

```gml
// Evita que se eliminen los assets marcados con el tag "used"
gml_pragma("MarkTagAsUsed", "used");

// Inicialización global antes de la primera room
gml_pragma("global", "Init()");

// Texturas del grupo "level1" a la mitad de tamaño
gml_pragma("Texgroup.Scale", "level1", "2");
```

---

## Alarmas: legacy frente a time sources

Las **alarmas** siguen existiendo y funcionando, pero en código nuevo se recomiendan
los **time sources**, que son más flexibles y no ocupan un evento por temporizador.

```gml
// ❌ Legacy: alarmas (una por evento, número limitado)
alarm[0] = room_speed * 3;

// ✅ Moderno: time sources
var _ts = time_source_create(time_source_game, 3, time_source_units_seconds);
time_source_start(_ts);
```

---

## Sistema operativo y dispositivo


### `os_type`

- **Devuelve:** OS Type Constant
- **Qué hace:** Constante de solo lectura que indica **para qué sistema operativo se ha compilado** el juego. Ojo: no es necesariamente el SO del dispositivo que lo ejecuta (por ejemplo, un juego compilado para Android y corriendo en Fire OS devuelve `os_android`).
- **Ejemplo:**

```gml
switch (os_type)
{
    case os_windows: global.config = 0; break;
    case os_linux: global.config = 1; break;
    case os_macosx: global.config = 2; break;
}
```

- **Notas:** No es el SO del dispositivo, sino el SO **para el que se compiló**. Constantes: `os_windows`, `os_macosx`, `os_linux`, `os_android`, `os_ios`, `os_tvos`, `os_gxgames`, `os_ps4`, `os_ps5`, `os_switch`, `os_xboxone`, `os_xboxseriesxs`, `os_operagx`.

### `os_version`

- **Devuelve:** Real
- **Qué hace:** La **versión** del sistema operativo como número real (por ejemplo `10.0` en Windows 10). Es un valor aproximado y depende de la plataforma.
- **Ejemplo:**

```gml
if (os_type == os_android && os_version > 10)
{
    global.GFX = 1;
}
```

### `os_browser`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Indica el **navegador** en el que se está ejecutando el juego cuando el target es HTML5 (`browser_not_a_browser`, `browser_chrome`, `browser_firefox`, `browser_safari`, …).
- **Ejemplo:**

```gml
if (os_browser == browser_not_a_browser)
{
    global.Config = 0;
}
else
{
    global.Config = 1;
}
```

### `os_device`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Indica el **tipo de dispositivo**. **Obsoleta** en LTS 2026: usa `os_get_info` o la información de la plataforma.
- **Ejemplo:**

```gml
if (os_browser = browser_not_a_browser)
{
    switch (os_device)
    {
        case device_ios_ipad: global.Config = 2; break;
        case device_ios_iphone: global.Config = 3; break;
        case device_ios_iphone_retina: global.Config = 4; break;
        case device_ios_unknown: global.Config = 5; break;
    }
}
else
{
    global.Config = 1;
}
```

- **Notas:** **Obsoleta.**

### `os_get_config()`

- **Devuelve:** String
- **Qué hace:** Devuelve la **configuración** del sistema como string con información sobre la CPU, la memoria y las capacidades gráficas.
- **Ejemplo:**

```gml
if (os_get_config() = "Free_Version")
{
    global.Ads = true;
}
else global.Ads = false;
```

### `os_get_info()`

- **Devuelve:** DS Map
- **Qué hace:** Devuelve un **DS map** con información detallada del sistema operativo y del hardware. Novedad relevante de 2026. El mapa **no** se recolecta: destrúyelo con `ds_map_destroy`.
- **Ejemplo:**

```gml
if (os_type == os_android)
{
    var _info = os_get_info();

    if (_info[? "android_tv"])
    {
        global.android_tv = true;
    }
}
```

- **Notas:** ⚠ Devuelve un **DS map**: destrúyelo con `ds_map_destroy`. En todas las plataformas salvo HTML5 incluye la clave `"is64bit"`. En Windows añade datos de DX11 muy útiles para extensiones (`video_d3d11_device`, `video_adapter_description`, `udid`…).

### `os_get_language()`

- **Devuelve:** String
- **Qué hace:** Devuelve el **idioma** del sistema como código ISO (por ejemplo `"es"`, `"en"`, `"fr"`). Es la base para seleccionar el idioma por defecto del juego.
- **Ejemplo:**

```gml
switch (os_get_language())
{
    case "es": ini_open("spanish.ini"); break;
    case "fr": ini_open("french.ini"); break;
    case "it": ini_open("italian.ini"); break;
    default: ini_open("english.ini"); break;
}
```

### `os_get_region()`

- **Devuelve:** String
- **Qué hace:** Devuelve la **región** geográfica del sistema como código ISO (por ejemplo `"ES"`, `"US"`).
- **Ejemplo:**

```gml
switch (os_get_language())
{
    case "zh":
        var _region = os_get_region();
        if (_region == "HK" || _region == "MO" || _region == "TW")
        {
            ini_open("chinese_traditional.ini");
        }
        else
        {
            ini_open("chinese_simplified.ini");
        }
    break;

    case "fr":
        ini_open("french.ini");
    break;

    case "it":
        ini_open("italian.ini");
    break;

    default:
        ini_open("english.ini");
    break;
}
```

### `os_is_paused()`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el juego está **en pausa**, es decir, si ha perdido el foco (por ejemplo, al cambiar de aplicación en un móvil).
- **Ejemplo:**

```gml
if (os_is_paused())
{
    if (!instance_exists(obj_pause_menu))
    {
        instance_create_layer(0, 0, "Controllers", obj_pause_menu);
    }
}
```

### `os_is_network_connected([attempt_connection])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Indica si el dispositivo tiene **conexión a internet**. Opcionalmente puede intentar establecer la conexión antes de responder, mediante el argumento `attempt_connection`.
- **Ejemplo:**

```gml
if os_is_network_connected()
{
    global.connected = true;
}
```

- **Notas:** Puede devolver `true` con conexiones que no dan acceso a internet (Bluetooth, Wi-Fi sin salida), así que no es infalible. Con `network_connect_active` o `network_connect_passive`, si devuelve `false`, el resultado real llega más tarde al evento **Async Networking**.

---

## Energía y orientación


### `os_powersave_enable(flag)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Activa o desactiva el **modo de ahorro de energía**. Al activarlo, GameMaker reduce el trabajo en segundo plano para consumir menos batería.
- **Ejemplo:**

```gml
if (os_type == os_android) || (os_type == os_ios)
{
    os_powersave_enable(false);
}
```

- **Notas:** Útil en móvil para prolongar la batería cuando el juego está en segundo plano.

### `os_lock_orientation(flag)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Bloquea o desbloquea la **orientación** de la pantalla en dispositivos móviles.
- **Ejemplo:**

```gml
if (os_type == os_android) || (os_type == os_ios)
{
    os_lock_orientation(true);
}
```

### `os_set_orientation_lock(landscape_enable, portrait_enable)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Permite indicar de forma independiente si se permite la orientación **horizontal** (*landscape*) y **vertical** (*portrait*).
- **Ejemplo:**

```gml
os_set_orientation_lock(true, true);
```

---

## Permisos


### `os_check_permission(permission)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Indica si el juego tiene **concedido** el permiso indicado (por ejemplo el de la cámara o el del micrófono).
- **Ejemplo:**

```gml
if (os_type == os_android)
{
    if (os_check_permission("android.permission.INTERNET") == os_permission_denied)
    {
        os_request_permission("android.permission.INTERNET");
    }
}
```

- **Notas:** Los permisos dependen de la plataforma y hay que declararlos en las opciones del juego.

### `os_request_permission(permissions...)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Solicita al sistema uno o varios **permisos**. La respuesta llega de forma asíncrona.
- **Ejemplo:**

*Ejemplo 1*


```gml
if (os_type == os_android)
{
    if (os_check_permission("android.permission.INTERNET") == os_permission_denied)
    {
        os_request_permission("android.permission.INTERNET");
    }
}
```

*Ejemplo 2*


```gml
var _read = "android.permission.READ_EXTERNAL_STORAGE";
var _write = "android.permission.WRITE_EXTERNAL_STORAGE";

if (os_check_permission(_write) && os_check_permission(_read))
{
    MobileUtils_Share_Open("Title!", "image/gif", file);
}
else
{
    os_request_permission(_write, _read);
}
```

- **Notas:** La respuesta llega de forma asíncrona: comprueba después con `os_check_permission`.

---

## Constantes del compilador de GameMaker


### `GM_version`

- **Devuelve:** String
- **Qué hace:** Constante de solo lectura con la **versión de GameMaker** con la que se ha compilado el juego, como string.
- **Ejemplo:**

```gml
draw_text(32, 32, date_time_string(GM_build_date));
draw_text(32, 64, "v" + GM_version);
```

### `GM_build_type`

- **Devuelve:** String
- **Qué hace:** Constante de solo lectura con el **tipo de build** (`"Debug"`, `"Release"`, …).
- **Ejemplo:**

```gml
draw_text(32, 32, GM_build_type);
```

### `GM_build_date`

- **Devuelve:** Datetime
- **Qué hace:** Constante de solo lectura con la **fecha y hora** en que se compiló el juego, como valor *datetime*.
- **Ejemplo:**

```gml
draw_text(32, 32, date_time_string(GM_build_date));
draw_text(32, 64, "v" + GM_version);
```

- **Notas:** Devuelve un *datetime*: usa `date_datetime_string(GM_build_date)` para mostrarlo.

### `GM_runtime_type`

- **Devuelve:** String
- **Qué hace:** Constante de solo lectura con el **tipo de runtime**: `"gms2"` para el runtime clásico o `"gmrt"` para el nuevo runtime (GMRT). **Novedad de 2026.**
- **Ejemplo:**

```gml
show_debug_message($"Using runtime: {string_upper(GM_runtime_type)}");
```

- **Notas:** Es la forma de detectar en tiempo de ejecución si estás en el runtime clásico o en GMRT: `if (GM_runtime_type == "gmrt") { /* ... */ }`.

### `GM_runtime_version`

- **Devuelve:** String
- **Qué hace:** Constante de solo lectura con la **versión del runtime** con la que se está ejecutando el juego, como string.
- **Ejemplo:**

```gml
draw_text(32, 32, date_time_string(GM_build_date));
draw_text(32, 64, "v" + GM_version);
draw_text(32, 96, "Runtime " + GM_runtime_version);
```

### `GM_project_filename`

- **Devuelve:** String
- **Qué hace:** Constante de solo lectura con el **nombre del fichero del proyecto** (el `.yyp`).
- **Ejemplo:**

```gml
draw_text(32, 32, GM_project_filename);
```

### `GM_is_sandboxed`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el juego se está ejecutando **dentro del sandbox**, es decir, con el sistema de ficheros restringido.
- **Ejemplo:**

```gml
draw_text(5, 5, $"Running sandboxed: {(GM_is_sandboxed ? "yes" : "no")}");
```

---

## Control de la compilación


### `gml_pragma(command, [optional...])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Afecta a **cómo se compila** el proyecto en el target indicado. Las directivas se procesan antes de compilar, así que pueden colocarse en cualquier sitio del código.
- **Ejemplo:**

```gml
gml_pragma("forceinline");
```

- **Notas:** Directivas disponibles: `"forceinline"`, `"global"`, `"optimise"/"optimize"`, `"PNGCrush"`, `"Texgroup.Scale"`, `"UnityBuild"`, `"AllowReentrantStatic"` y **`"MarkTagAsUsed"`**.

### `gml_release_mode(flag)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Activa el **modo release**, que relaja ciertas comprobaciones de error a cambio de mayor rendimiento. Úsalo solo cuando el juego esté depurado.
- **Ejemplo:**

```gml
gml_release_mode(true);
```

- **Notas:** Úsalo solo en la build final: se pierden comprobaciones de error valiosas durante el desarrollo.

### `code_is_compiled()`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el código está **compilado** con el YoYo Compiler (YYC) en lugar de interpretado.
- **Ejemplo:**

```gml
if (code_is_compiled())
{
    show_debug_message("Compiler okay!");
}
```

- **Notas:** Permite activar rutas de código distintas según se esté interpretando o compilando con YYC.

---

## Línea de comandos y entorno


### `parameter_count()`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **parámetros de línea de comandos** se han pasado al juego.
- **Ejemplo:**

```gml
p_num = parameter_count();
```

### `parameter_string(n)`

- **Devuelve:** String
- **Qué hace:** Devuelve el parámetro de línea de comandos número `n` como string.
- **Ejemplo:**

```gml
var _p_num = parameter_count();
if (_p_num > 0)
{
    for (var i = 0; i < _p_num; i++)
    {
        p_string[i] = parameter_string(i + 1);
    }
}
```

- **Notas:** El índice `n` va de 1 a `parameter_count()`; el 0 suele ser la ruta del ejecutable.

### `environment_get_variable(name)`

- **Devuelve:** String
- **Qué hace:** Devuelve el valor de una **variable de entorno** del sistema, o un string vacío si no existe.
- **Ejemplo:**

```gml
e_str = environment_get_variable("APPDATA");
```

- **Notas:** Devuelve `""` si la variable no existe. No la uses para guardar secretos.

---

## Planificador de Windows


### `scheduler_resolution_get()`

- **Devuelve:** Real (or -1 for default)
- **Qué hace:** Devuelve la **resolución del planificador de hilos** de Windows en milisegundos, o `-1` si se usa el valor por defecto.
- **Ejemplo:**

```gml
scheduler_resolution = scheduler_resolution_get();
```

### `scheduler_resolution_set(milliseconds)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Fija la resolución del planificador de hilos de Windows en milisegundos. Afecta a la precisión de los temporizadores.
- **Ejemplo:**

```gml
scheduler_resolution_set(2);
```

- **Notas:** Solo afecta a **Windows**.

---

## Funciones externas (heredadas)


### `external_define(dll, name, calltype, restype, argnumb, argtype[0], argtype[1], ...argtype[10])`

- **Devuelve:** External Function
- **Qué hace:** Define una función externa de una librería dinámica (DLL / dylib). **Heredada**: hoy las funciones de extensión se declaran en el editor de extensiones.
- **Ejemplo:**

```gml
my_funcion = external_define("MyDLL.dll", "MyMin", dll_cdecl, ty_real, 2, ty_real, ty_real);
```

- **Notas:** Estas funciones son **heredadas** y solo funcionan en Windows y macOS. Declara las funciones de extensión en el editor de extensiones.

### `external_call(id, args[0...15])`

- **Devuelve:** Cualquiera (the type of value returned will depend on the defined function)
- **Qué hace:** Llama a una función externa definida con `external_define`. **Heredada**.
- **Ejemplo:**

```gml
my_function = external_define("MyDLL.dll", "MyMin", dll_cdecl, ty_real, 2, ty_real, ty_real);
var _a = external_call(my_function, x, y);
```

- **Notas:** Heredada.

### `external_free(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Libera una librería externa cargada con `external_define`. **Heredada**.
- **Ejemplo:**

```gml
external_free("MyDLL.dll");
```

- **Notas:** Heredada.

---

## Velocidad del juego y URLs


### `game_set_speed(speed, type)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Fija la **velocidad del juego**: los fotogramas por segundo (`gamespeed_fps`) o los microsegundos por fotograma (`gamespeed_microseconds`).
- **Ejemplo:**

```gml
if (os_browser == browser_not_a_browser)
{
    game_set_speed(60, gamespeed_fps);
}
else
{
    game_set_speed(30, gamespeed_fps);
}
```

### `game_get_speed(type)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la velocidad actual del juego, en la unidad que indiques.
- **Ejemplo:**

```gml
if (game_get_speed(gamespeed_fps) != 60)
{
    game_set_speed(60, gamespeed_fps);
}
```

### `url_open(url)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Abre la URL indicada en el **navegador** del sistema.
- **Ejemplo:**

```gml
url_open("http://gamemaker.io");
```

- **Notas:** Abre el navegador, así que el juego pierde el foco.

### `url_open_ext(url, target)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Igual que `url_open`, pero permite indicar el **destino** (`_blank`, `_self`, …).
- **Ejemplo:**

```gml
url_open_ext("http://gamemaker.io", "_blank");
```

### `url_get_domain()`

- **Devuelve:** String
- **Qué hace:** Devuelve el **dominio** desde el que se está sirviendo el juego (pensado para HTML5).
- **Ejemplo:**

```gml
dom_name=url_get_domain();
```

---

## Receta: detectar la plataforma y adaptar el juego

```gml
function es_movil()
{
    return (os_type == os_android || os_type == os_ios);
}

function configurar_segun_plataforma()
{
    switch (os_type)
    {
        case os_windows:
        case os_macosx:
        case os_linux:
            global.mostrar_botones_tactiles = false;
            break;

        case os_android:
        case os_ios:
            global.mostrar_botones_tactiles = true;
            os_powersave_enable(true);
            break;
    }
}
```

## Receta: idioma por defecto según el sistema

```gml
var _idioma = os_get_language();   // "es", "en", "fr"...

switch (_idioma)
{
    case "es": global.idioma = "español"; break;
    case "en": global.idioma = "ingles";  break;
    default:   global.idioma = "ingles";
}
```

## Receta: comprobar si hay internet antes de sincronizar

```gml
if (os_is_network_connected())
{
    sincronizar_puntuaciones();
}
else
{
    show_debug_message("Sin conexión: se sincronizará más tarde");
}
```

---

## Funciones que NO existen en GML

| Nombre | Alternativa real |
| --- | --- |
| `sleep()` | No existe. Usa *time sources* o un temporizador manual con `current_time`. |
| `game_get_id()` | Usa `game_save_id` (es del área de ficheros, no un id de juego). |
| `os_is_timezone()` | No existe. |

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [OS And Compiler (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/OS_And_Compiler/OS_And_Compiler.htm)
- [General Game Control (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/General_Game_Control/General_Game_Control.htm)
- [Time Sources (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Time_Sources/Time_Sources.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
