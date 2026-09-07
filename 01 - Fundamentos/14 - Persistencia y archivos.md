# 14 · Persistencia y archivos

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/Additional_Information/The_File_System.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/File_Handling.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Buffers/Buffers.htm>
> - `gm-cli manual read "ini_open"` / `"json_parse"` / `"json_stringify"`
> - <https://github.com/YoYoGames/GM-TestFramework>

---

## 1. El sandbox: lo primero que debes entender

> **Por defecto, GameMaker está *sandboxed*.** No puede guardar ni cargar archivos de ningún sitio que no sea **el propio bundle del juego** o **el almacenamiento local del dispositivo**.

Puedes **desactivar el sandbox** en los targets de escritorio (Windows, macOS, Ubuntu) marcando **«Disable file system sandbox»** en las Game Options de la plataforma. Aun así, seguirás limitado por los permisos del sistema operativo.

### Las dos áreas de archivos

```
┌─────────────────────────────────────────────────────┐
│  FILE BUNDLE  (working_directory)                   │
│  ─────────────────────────────────                  │
│  Los archivos empaquetados con el ejecutable,       │
│  incluidos tus Included Files.                      │
│  SOLO LECTURA.                                      │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│  SAVE AREA  (game_save_id)                          │
│  ────────────────────────                           │
│  Zona de almacenamiento con escritura GARANTIZADA.  │
│  Aquí van tus partidas guardadas.                   │
└─────────────────────────────────────────────────────┘
```

### La regla de resolución (importantísima)

Cuando haces esto:

```gml
var _buff = buffer_load("mi_archivo.dat");
buffer_save(_buff, "mi_archivo.dat");
```

pasa lo siguiente:

**Al LEER:**
1. Se busca primero en el **save area**. Si está, se usa ese.
2. Si no está, se busca en el **file bundle**. Si está (porque es un Included File), se usa ese.

**Al ESCRIBIR:**
- Solo puede escribirse en el **save area** (salvo que el sandbox esté desactivado y especifiques una ruta externa explícita).

### Consecuencias prácticas

| Tipo de operación | Dónde |
|---|---|
| `directory_create()` y demás funciones de directorios | **Solo save area** |
| Funciones de información del sistema de archivos | Devuelven info de **ambas** áreas; escriben solo en el **save area** |
| Escribir texto, binarios o INI | Crea el archivo en el **save area** si no existe, **copiando** la información del original del bundle si lo había |

> 💡 **Esto último es muy útil:** puedes empaquetar un archivo de configuración por defecto como Included File, y la primera vez que lo escribas se copiará automáticamente al save area. El original permanece intacto en la parte de solo lectura.

### Dónde está el save area en cada plataforma

| Plataforma | Ubicación |
|---|---|
| **Windows** | `%localappdata%\<Nombre del juego>` (es decir, `C:\Users\<Usuario>\AppData\Local\<Nombre del juego>`) |
| **HTML5 / GX.games** | Local storage del navegador |
| **macOS** | Depende de si la app está sandboxed; normalmente `~/Library/Application Support/<Nombre del juego>` |
| **Ubuntu (Linux)** | `/home/<usuario>/.config/<nombredeljuego>` |
| **iOS / tvOS** | Ubicación estándar (visible a través de iTunes) |
| **Android** | `/data/<nombre del paquete>` (invisible salvo que el dispositivo esté rooteado) |

> ⚠️ **HTML5 tiene un límite de local storage de entre 1 MB y 5 MB**, según el navegador. No intentes guardar sprites grandes ni capturas de pantalla.

---

## 2. Salirse del sandbox

### En escritorio: diálogos del sistema

```gml
var _ruta = get_open_filename("Texto|*.txt", "");     // abrir
var _ruta = get_save_filename("Texto|*.txt", "");     // guardar
```

La cadena devuelta **puede usarse en el resto de funciones de archivo para saltarse el sandbox**, porque representa una elección explícita del usuario.

### En escritorio: desactivar el sandbox

Game Options → *Disable file system sandbox*. ⚠️ Sigue sujeto a los permisos del SO.

### En HTML5: cargar desde un servidor

> ⚠️ **Usa SIEMPRE `buffer_load_async()`.** La carga síncrona está deprecada en la mayoría de navegadores y acabará eliminándose.

```gml
// Create
buff = buffer_create(1, buffer_grow, 1);
id_carga = buffer_load_async(buff, "https://miservidor.com/datos.json", 0, -1);

// Async - Save/Load
if (async_load[? "id"] == id_carga)
{
    if (async_load[? "status"] == true)
    {
        var _json = buffer_read(buff, buffer_string);
        global.datos = json_parse(_json);
    }
    buffer_delete(buff);
    buff = -1;
}
```

> 💡 Si cargas imágenes con `sprite_add()`, el manejo asíncrono ya lo hace GameMaker por ti.

---

## 3. Diferencias entre plataformas que te morderán

| Plataforma | Particularidad |
|---|---|
| **iOS** | Si cargas un Included File de una carpeta (`"Fondos/fondo1.png"`), **no necesitas** incluir la carpeta: basta el nombre de archivo. Puedes incluir la ruta si tienes archivos con el mismo nombre en carpetas distintas. **En todas las demás plataformas sí debes** incluir la carpeta. |
| **macOS / Ubuntu** | Los nombres y rutas **distingen mayúsculas**. Para evitar problemas, GameMaker **poner todo en minúsculas por defecto**. |
| **HTML5** | No puedes crear ni destruir directorios en el local storage. Guardar/cargar funciona como se describe, pero cargar del servidor requiere `buffer_load_async()`. |

> ⚠️ **Regla de oro para nombres de archivo:** usa siempre minúsculas y evita espacios y acentos.

---

## 4. Archivos INI

Formato clásico de secciones y claves. Ideal para **configuración sencilla**.

```gml
ini_open(nombre);
// ... leer / escribir ...
ini_close();
```

> ⚠️ **Solo puedes tener un INI abierto a la vez.** `ini_open()` cierra automáticamente el que estuviera abierto.
> ⚠️ **La información no se guarda en disco hasta `ini_close()`**: hasta entonces vive en memoria.
> 💡 Si solo **lees** y el archivo no existe, se devuelven los valores por defecto y **el archivo no se crea**. Solo se crea si escribes.

### Funciones

```
ini_open(nombre)
ini_close()
ini_read_string(seccion, clave, defecto)
ini_read_real(seccion, clave, defecto)
ini_write_string(seccion, clave, valor)
ini_write_real(seccion, clave, valor)
ini_key_exists(seccion, clave)
ini_section_exists(seccion)
ini_key_delete(seccion, clave)
ini_section_delete(seccion)
```

### Ejemplo

```gml
// ─── Guardar opciones ───
ini_open("opciones.ini");
ini_write_real("audio", "musica",  global.volumen_musica);
ini_write_real("audio", "efectos", global.volumen_efectos);
ini_write_real("video", "pantalla_completa", window_get_fullscreen() ? 1 : 0);
ini_write_string("jugador", "nombre", global.nombre_jugador);
ini_close();

// ─── Cargar opciones ───
ini_open("opciones.ini");
global.volumen_musica  = ini_read_real("audio", "musica", 0.7);
global.volumen_efectos = ini_read_real("audio", "efectos", 1.0);
var _fs = ini_read_real("video", "pantalla_completa", 0);
global.nombre_jugador  = ini_read_string("jugador", "nombre", "Jugador");
ini_close();

window_set_fullscreen(_fs == 1);
```

### Truco: INI como string (para HTML5)

`ini_close()` puede devolver el contenido como string, lo que te permite meterlo en un buffer y guardarlo con las funciones async:

```gml
ini_open("datos.ini");
ini_write_real("progreso", "nivel", 5);
var _contenido = ini_close();

var _buff = buffer_create(string_byte_length(_contenido) + 1, buffer_grow, 1);
buffer_write(_buff, buffer_string, _contenido);
buffer_save_async(_buff, "datos.ini", 0, buffer_get_size(_buff));
// ⚠️ No borres el buffer aquí: debe sobrevivir hasta el evento Async
```

---

## 5. Archivos de texto

```
file_text_open_read(nombre)      file_text_open_write(nombre)
file_text_open_append(nombre)    file_text_close(fileid)
file_text_read_string(fileid)    file_text_read_real(fileid)
file_text_readln(fileid)         file_text_eof(fileid)
file_text_eoln(fileid)           file_text_write_string(fileid, cadena)
file_text_write_real(fileid, valor)  file_text_writeln(fileid)
```

```gml
// Guardar un log
var _f = file_text_open_append("log.txt");
file_text_write_string(_f, $"[{date_datetime_string(date_current_datetime())}] Evento ocurrido");
file_text_writeln(_f);
file_text_close(_f);
```

---

## 6. Archivos binarios

```
file_bin_open(nombre, modo)      file_bin_close(fileid)
file_bin_read_byte(fileid)       file_bin_write_byte(fileid, valor)
file_bin_position(fileid)         file_bin_seek(fileid, posicion)
file_bin_size(fileid)
```

> Para la mayoría de los casos, **los buffers son más cómodos y potentes**.

---

## 7. Buffers

Un **buffer** es una región de memoria física para contener datos temporalmente mientras se mueven o manipulan (por ejemplo, paquetes de red).

### ⚠️ Notas de uso (importantes)

- Al crear un buffer se **limpia automáticamente** y se rellena de `0`.
- El argumento **«size»** siempre es **en bytes**.
- El argumento **«alignment»** es cómo se almacenan los datos dentro. Con alineación 4, si escribes 1 byte haces `buffer_tell()` → `1`. Escribes otro byte → `buffer_tell()` devuelve **5**, porque la alineación ha «rellenado». La alineación solo afecta a **dónde** se escribe.
- **«offset»** también es en bytes. Con alineación de 2 bytes, saltar 4 posiciones alineadas = offset de `2 * 4 = 8` bytes.
- Algunas funciones de buffer **crean un buffer nuevo** (por ejemplo `buffer_load()`). Esos también hay que borrarlos con `buffer_delete()`.
- La memoria de los buffers es **memoria del sistema**: los datos sobreviven a la pérdida de foco, pero se pierden al cerrar la app.
- El **«used size»** empieza en 0 con `buffer_create()` y se actualiza al escribir. En un buffer cargado externamente, es el tamaño real de los datos. Se puede cambiar con `buffer_set_used_size()`.
- Un buffer de tipo **`buffer_grow`** se redimensiona solo. Su tamaño en memoria será mayor que el necesario; el real se obtiene con `buffer_get_used_size()`.
- Si necesitas un buffer de tamaño exacto: escribe en uno `grow` hasta el tamaño deseado, copia los bytes con `buffer_copy()` a uno nuevo del tamaño exacto y borra el `grow`.

> ⚠️ **Tras destruir un buffer, pon la variable a `-1`.** El manual lo recomienda explícitamente.

### Tipos de buffer

```
buffer_fixed   tamaño fijo
buffer_grow    crece automáticamente
buffer_wrap    circular: al llegar al final vuelve al principio
buffer_fast    acceso rápido, solo 1 byte de alineación
buffer_vbuffer para datos de vertex buffer
buffer_network optimizado para red (big-endian)
```

### Tipos de datos

```
buffer_u8 / buffer_s8 / buffer_u16 / buffer_s16
buffer_u32 / buffer_s32 / buffer_u64 / buffer_f16
buffer_f32 / buffer_f64 / buffer_bool
buffer_string   (string terminado en nulo)
buffer_text     (string sin terminador)
```

### Funciones

```
// Generales
buffer_exists / buffer_create / buffer_delete
buffer_read / buffer_write / buffer_fill
buffer_seek / buffer_tell / buffer_peek / buffer_poke
buffer_get_type / buffer_get_alignment / buffer_get_address
buffer_get_size / buffer_resize / buffer_sizeof
buffer_set_used_size / buffer_get_used_size
buffer_copy / buffer_copy_stride

// Cargar y guardar
buffer_save / buffer_save_ext / buffer_save_async
buffer_load / buffer_load_ext / buffer_load_async / buffer_load_partial

// Compresión
buffer_compress / buffer_decompress

// Grupos async
buffer_async_group_begin / buffer_async_group_option / buffer_async_group_end

// Surfaces
buffer_get_surface / buffer_set_surface
buffer_get_surface_depth / buffer_set_surface_depth

// Hashes
buffer_md5 / buffer_sha1 / buffer_crc32

// Codificación
buffer_base64_encode / buffer_base64_decode / buffer_base64_decode_ext
```

### Leer y escribir: el patrón

```gml
// ESCRIBIR
var _buff = buffer_create(1024, buffer_grow, 1);
buffer_write(_buff, buffer_string, "MiJuego v1.0");
buffer_write(_buff, buffer_u16, 5);
buffer_write(_buff, buffer_f32, 123.456);
buffer_save(_buff, "partida.save");
buffer_delete(_buff);

// LEER (siempre en el MISMO orden)
var _buff = buffer_load("partida.save");
var _version = buffer_read(_buff, buffer_string);
var _nivel   = buffer_read(_buff, buffer_u16);
var _puntos  = buffer_read(_buff, buffer_f32);
buffer_delete(_buff);
```

> ⚠️ **El orden de lectura debe coincidir exactamente con el de escritura.** Un solo `buffer_u8` donde iba un `buffer_u16` corrompe todo lo que venga después.

---

## 8. JSON: la opción recomendada en 2026

### `json_stringify()`

```gml
json_stringify(valor, [pretty_print], [funcion_filtro]);
```

Convierte un **struct** o un **array** (y todo lo anidado) en un string JSON válido.

```gml
var _datos =
{
    version : "1.0.0",
    datos   :
    {
        monedas    : 4,
        mana       : 15,
        nombre     : "Gurpreet",
        items      : [ITEM.ESPADA, ITEM.ARCO, ITEM.GUITARRA]
    }
};

var _json        = json_stringify(_datos);          // compacto
var _json_bonito = json_stringify(_datos, true);    // con indentación
```

### `json_parse()`

```gml
json_parse(json, [funcion_filtro], [inhibit_string_convert]);
```

Convierte un string JSON en structs y arrays anidados.

```gml
var _json = "{\"miObj\": { \"manzanas\":10, \"naranjas\":12 }}";
var _datos = json_parse(_json);

if (struct_exists(_datos, "miObj") && is_struct(_datos.miObj))
{
    show_debug_message(_datos.miObj.manzanas);   // 10
}
```

### ⚠️ Lo que debes saber (y que te va a morder)

1. **El orden de las variables del struct no está garantizado.**
2. **Los assets y estructuras de datos NO se serializan con su contenido**: se guarda la **referencia** (handle). Al parsear se reconvierten a referencias de runtime.
3. ⚠️ **Esto NO sirve entre sesiones del juego:** los índices se reciclan. Los assets se guardan **por nombre**, así que el enlace sobrevive **mientras no cambies el nombre del asset**.
4. `null` en JSON → `undefined` al parsear.
5. **Profundidad máxima de anidamiento al parsear: 128.**
6. Parsear algo inválido lanza una **excepción** (no devuelve `undefined`).
7. Para serializar **DS lists y DS maps**, usa `json_encode()`, no `json_stringify()`.
8. La función filtro tiene firma `function(clave, valor) -> nuevo_valor`.

### 🆕 `inhibit_string_convert`

El tercer argumento de `json_parse()` desactiva la reconversión de strings a referencias de runtime:

```gml
var _datos = json_parse(_json, undefined, true);
// Los handles, int64, NaN e infinity siguen como strings
```

Úsalo cuando vayas a **validar** el JSON antes de usarlo, o cuando los handles no te interesen.

### ⚠️ El impacto de los handles en los guardados (el tema clave)

Esto es lo que el manual dice literalmente sobre `json_stringify()`:

> *«the function will **not** serialise the data contained inside assets, data structures and other runtime assets into JSON, and will simply store the internal handle reference for the asset (which is of little use as the index will change between runs of the game).»*

**Traducción práctica:**

```gml
// ═══ LO QUE NO DEBES HACER ═══
var _guardado =
{
    nivel          : 5,
    mi_ds_lista    : mi_ds_lista,     // ❌ se guarda un handle inútil
    mi_superficie  : mi_superficie,   // ❌ idem
    instancia_ref  : obj_enemigo      // ❌ idem
};
```

```gml
// ═══ LO QUE SÍ DEBES HACER ═══
var _guardado =
{
    nivel       : 5,
    inventario  : ["espada", "pocion", "pocion"],   // ✅ datos puros
    posicion    : { x: x, y: y },                   // ✅
    nombre_item : "Espada oxidada"                  // ✅ por NOMBRE, no por handle
};

// Y al cargar, reconstruyes desde los datos:
var _datos = json_parse(_json);
nombre_item = _datos.nombre_item;
// ...y recreas las estructuras dinámicas desde cero
```

---

## 9. Sistema de guardado completo (recomendado)

```gml
// ═══════════ Script: scr_save ═══════════

#macro ARCHIVO_GUARDADO "save01.json"
#macro VERSION_GUARDADO "1.0.0"

/// @function         guardar_partida()
/// @description      Serializa el estado del juego a JSON y lo guarda.
/// @return {Bool}    true si se guardó correctamente
function guardar_partida()
{
    // 1. Construir un struct con DATOS PUROS (sin handles)
    var _datos =
    {
        version    : VERSION_GUARDADO,
        fecha      : date_datetime_string(date_current_datetime()),

        jugador    :
        {
            x        : obj_jugador.x,
            y        : obj_jugador.y,
            vida     : obj_jugador.vida,
            vida_max : obj_jugador.vida_max,
            nivel    : obj_jugador.nivel
        },

        globales   :
        {
            puntuacion : global.puntuacion,
            habitacion : room_get_name(room)
        },

        inventario : obj_jugador.inventario   // array de strings/structs puros
    };

    // 2. Convertir a JSON
    var _json = json_stringify(_datos, true);

    // 3. Escribir en un buffer y guardar
    var _buff = buffer_create(string_byte_length(_json) + 1, buffer_grow, 1);
    buffer_write(_buff, buffer_string, _json);
    buffer_save(_buff, ARCHIVO_GUARDADO);
    buffer_delete(_buff);

    show_debug_message($"Partida guardada ({string_byte_length(_json)} bytes)");
    return true;
}

/// @function         cargar_partida()
/// @description      Carga y valida la partida guardada.
/// @return {Struct}  Los datos cargados, o undefined si no hay / es inválida
function cargar_partida()
{
    // 1. ¿Existe el archivo?
    if (!file_exists(ARCHIVO_GUARDADO))
    {
        show_debug_message("No hay partida guardada");
        return undefined;
    }

    // 2. Leer el buffer
    var _buff = buffer_load(ARCHIVO_GUARDADO);
    var _json = buffer_read(_buff, buffer_string);
    buffer_delete(_buff);

    // 3. Parsear (puede lanzar excepción si el JSON está corrupto)
    var _datos;
    try
    {
        _datos = json_parse(_json);
    }
    catch (_error)
    {
        show_debug_message("El archivo de guardado está corrupto");
        return undefined;
    }

    // 4. Validar la estructura
    if (!is_struct(_datos))                    { return undefined; }
    if (!struct_exists(_datos, "version"))     { return undefined; }
    if (!struct_exists(_datos, "jugador"))     { return undefined; }
    if (_datos.version != VERSION_GUARDADO)
    {
        show_debug_message($"Versión de guardado incompatible: {_datos.version}");
        return migrar_guardado(_datos);   // hook para migraciones
    }

    show_debug_message("Partida cargada correctamente");
    return _datos;
}

/// @function         borrar_partida()
function borrar_partida()
{
    if (file_exists(ARCHIVO_GUARDADO))
    {
        file_delete(ARCHIVO_GUARDADO);
    }
}

/// @function         hay_partida_guardada()
function hay_partida_guardada()
{
    return file_exists(ARCHIVO_GUARDADO);
}
```

```gml
// ═══════════ Uso ═══════════

// Al guardar
guardar_partida();

// Al cargar
var _datos = cargar_partida();
if (!is_undefined(_datos))
{
    global.puntuacion  = _datos.globales.puntuacion;
    obj_jugador.vida   = _datos.jugador.vida;
    obj_jugador.nivel  = _datos.jugador.nivel;
    obj_jugador.inventario = _datos.inventario;

    // Ir a la room guardada
    var _room = asset_get_index(_datos.globales.habitacion);
    if (_room != -1) { room_goto(_room); }
}
```

**Por qué está bien:**
- Guarda **datos puros**, nunca handles.
- **Valida** la estructura antes de usarla.
- **Versiona** el guardado (imprescindible: tarde o temprano cambiarás la estructura).
- Tiene un **hook de migración**.
- Usa `try/catch` para JSON corrupto.

---

## 10. Guardado y carga del estado completo (`game_save*`)

GameMaker incluye funciones de guardado «de juguete» para empezar rápido:

```
game_save(nombre_archivo)         game_load(nombre_archivo)
game_save_buffer(buffer)          game_load_buffer(buffer)
```

> ⚠️ El manual avisa: *«these functions are designed for beginners to get a basic save system up and running as quickly as possible, but for more complex projects, you should create your own save system»*.

**Úsalas en prototipos. Para un juego real, escribe tu propio sistema** (sección 9).

---

## 11. Directorios

```
directory_create(nombre)          directory_exists(nombre)
directory_destroy(nombre)
```

> ⚠️ **Solo hay tres.** `directory_get_working()` **no existe** en el runtime 2026.0.0.23
> (`python3 "_indice/buscar.py" --listar directory_` devuelve tres símbolos). La carpeta de
> trabajo se lee con la variable `working_directory`, no con una función.

```gml
if (!directory_exists("perfiles"))
{
    directory_create("perfiles");
}
```

> ⚠️ Solo funcionan en el **save area**.
> ⚠️ En **HTML5** no puedes crear ni destruir directorios.

---

## 12. Codificación y hashes

```
base64_encode(cadena)             base64_decode(cadena)
md5_string_unicode(cadena)        md5_string_utf8(cadena)
md5_file(nombre)                  sha1_string_unicode / sha1_string_utf8
buffer_md5(buff, offset, tam)     buffer_sha1(...)     buffer_crc32(...)
```

```gml
// Ofuscar un guardado para que no se edite a mano (NO es seguridad real)
var _json = json_stringify(_datos);
var _ofuscado = base64_encode(_json);
// ...al cargar: base64_decode(_ofuscado)

// Checksum de integridad
var _checksum = md5_string_utf8(_json);
```

> ⚠️ **base64 NO es seguridad.** Solo evita la edición casual. Si necesitas proteger el guardado de verdad, tendrás que añadir verificación en servidor.

---

## 12 bis. Checksum como verificación real: calcular, guardar aparte, comparar y rechazar

El punto anterior calcula un checksum (`md5_string_utf8`) pero no dice qué hacer con él. Un
checksum que se calcula y no se compara en ningún sitio no protege nada: es exactamente el
defecto que tenía el replay firmado de
[13 · 10 §14.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#143-replay-firmado-la-única-verificación-real-para-un-ranking-de-un-jugador)
antes de corregirlo. El flujo completo tiene **cuatro pasos**, no uno:

1. **Calcular** el hash de los datos, antes de escribir nada.
2. **Guardarlo aparte** del propio dato que protege (si viviera dentro del mismo bloque que
   hashea, hashear el bloque completo incluiría al propio hash: problema circular).
3. **Recalcularlo al leer**, sobre los mismos bytes que se hashearon al escribir.
4. **Comparar y, si no coincide, rechazar** — no seguir cargando una partida que puede tener
   cualquier campo corrompido o retocado a mano.

### ⚠️ La trampa: reserializar un struct para comparar el hash

El error natural es calcular el checksum sobre los **datos ya parseados**: `sha1_string_utf8
(json_stringify(_datos_leidos))`. **No lo hagas.** El motivo está en §8 de este mismo
documento: *"el orden de las variables del struct no está garantizado"*. Si escribiste el
checksum sobre `json_stringify(_datos)` la primera vez y luego lo comparas contra
`json_stringify(json_parse(json_stringify(_datos)))`, nada garantiza que las claves salgan en
el mismo orden las dos veces — y un simple cambio de orden cambia el hash de un guardado
perfectamente válido. **Un checksum sobre un array no tiene este problema** (los arrays sí
mantienen orden), pero la mayoría de guardados son structs.

**La solución que usa `scr_save_load.gml`**: el checksum se calcula sobre el **texto JSON
exacto** que se va a escribir, y ese mismo texto —no el struct que representa— se guarda tal
cual, como un string anidado dentro del sobre. Al leer, se compara el hash contra ese texto
**antes** de parsearlo. Como un string sobrevive el parseo byte a byte (a diferencia de un
struct, cuyas claves sí pueden reordenarse), la comparación nunca da un falso rechazo:

```gml
// ═══ Al guardar (extracto real de save_game() en scr_save_load.gml) ═══
var _datos_json = json_stringify(_datos);        // el texto se hashea UNA vez
var _sobre = {
    version  : SAVE_VERSION,
    fecha    : date_datetime_string(date_current_datetime()),
    checksum : sha1_string_utf8(_datos_json),     // hash del TEXTO, no del struct
    datos    : _datos_json                        // se guarda el TEXTO, no el struct
};
// _sobre se escribe entero con json_stringify(_sobre) — datos queda como
// un string JSON anidado dentro del JSON exterior.
```

```gml
// ═══ Al cargar (extracto real de __save_load_envelope() en scr_save_load.gml) ═══
// _sobre.datos sigue siendo el MISMO texto que se hasheó al escribir: comparar
// no depende de que json_stringify reproduzca el mismo orden de claves.
if (sha1_string_utf8(_sobre.datos) != _sobre.checksum) {
    return undefined;   // corrupto o manipulado: SE RECHAZA, no se intenta usar a medias
}
_sobre.datos = json_parse(_sobre.datos);   // ahora sí, a struct/array usable
```

La implementación completa —con compatibilidad hacia guardados de antes de que existiera el
checksum, y conectada con las copias de seguridad de más abajo— está en
[`scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml): `save_game()`,
`__save_envelope_checksum_ok()` y `__save_load_envelope()`. No la repitas: enlázala.

> 💡 **`md5_string_utf8` en vez de `sha1_string_utf8`** funciona igual de bien para esto — es
> un poco más rápido y un poco más corto — si no te hace falta la resistencia extra a
> colisiones de SHA-1. Para detectar corrupción accidental (no un atacante decidido a
> falsificar el hash también), cualquiera de los dos vale; `scr_save_load.gml` usa
> `sha1_string_utf8` porque es la misma función que ya usa el replay firmado de 13 · 10 §14.3,
> y usar la misma en todo el proyecto evita tener dos convenciones de hash a la vez.

## 12 ter. Copia de seguridad rotativa y qué pasa si se apaga a mitad

El checksum **rechaza** un guardado roto; por sí solo no da ningún sitio al que volver. Para
eso hace falta una **copia de seguridad rotativa**: antes de sobrescribir el save de un slot,
el save anterior pasa a ser una copia (`bak1`), la copia que había pasa a ser la siguiente
(`bak2`), y así hasta el límite que decidas conservar.

```gml
// ═══ save_backup(_slot, _n) — de scr_save_load.gml, llamada sola en cada save_game() ═══
function save_backup(_slot, _n) {
    if (_n <= 0) { return true; }              // 0 = backups desactivados

    var _i = _n;
    repeat (_n - 1) {                          // de la más vieja a la más nueva
        var _origen  = save_backup_path(_slot, _i - 1);
        var _destino = save_backup_path(_slot, _i);
        if (file_exists(_origen)) {
            if (file_exists(_destino)) { file_delete(_destino); }
            file_rename(_origen, _destino);
        }
        _i--;
    }

    var _actual = save_get_path(_slot);
    if (file_exists(_actual)) {
        var _bak1 = save_backup_path(_slot, 1);
        if (file_exists(_bak1)) { file_delete(_bak1); }
        file_rename(_actual, _bak1);           // el save actual pasa a ser bak1
    }
    return true;
}
```

**Qué pasa si el juego (o la consola, o el sistema operativo) se apaga a mitad de un
guardado**, paso por paso, con la escritura atómica de §9 y la copia de seguridad juntas:

| Momento exacto del corte | Qué queda en disco | Qué recupera el jugador |
|---|---|---|
| Durante el paso 1 (escribiendo el `.tmp`) | Un `.tmp` a medio escribir; el save bueno intacto | El save de siempre. `save_game()` nunca llegó a tocarlo |
| Entre el paso 1 y el 2 (`.tmp` completo, sin validar) | `.tmp` completo pero aún no verificado; el save bueno intacto | El save de siempre. La próxima llamada a `save_game()` sobrescribe el `.tmp` sin problema |
| Durante la rotación de backups (§ arriba) | El save "principal" puede haber desaparecido un instante (ya renombrado a `bak1`), pero el `.tmp` validado está listo al lado | `load_game()` normal fallaría un instante; `load_game_recover()` encuentra los datos en `bak1` igualmente |
| Justo antes del `file_rename` final | `.tmp` validado y `bak1` con el save anterior, ninguno todavía es el save "oficial" | Igual que arriba: `load_game_recover()` no pierde nada, solo tiene que mirar en `bak1` |
| Después del `file_rename` final | Save nuevo en su sitio, `.tmp` ya no existe | El save nuevo, como si nada hubiera pasado |

**En ningún punto de esa secuencia un guardado a medio escribir sustituye a uno bueno.** Es la
misma garantía que ya daba la escritura atómica de §9, extendida para cubrir también el
instante de la rotación de backups.

**Recuperar cuando el save principal falla la validación** (corrupto, checksum que no
coincide, o simplemente no existe) usa la misma cadena de copias:

```gml
// load_game_recover() prueba el save principal y, si falla, bak1, bak2… en orden
var _datos = load_game_recover("slot1");
if (is_undefined(_datos)) {
    mostrar_aviso("No se pudo recuperar ninguna copia de esta partida.");
}
```

> ⚠️ `load_game_recover()` **no** restaura automáticamente la copia como save principal: solo
> te devuelve los datos utilizables. Si el jugador sigue jugando desde ahí, el siguiente
> `save_game()` normal ya deja las cosas donde deben estar.
>
> 💡 `SAVE_BACKUP_COUNT` (por defecto 3) se cambia con un `#macro` al principio de
> `scr_save_load.gml`. Cada copia adicional es un fichero más en disco del mismo tamaño que el
> save: para partidas grandes, sopesa cuántas merece la pena conservar.

---

## 13. GameMaker Test Framework (tests automáticos)

Además de guardar datos, GameMaker tiene un **framework de tests oficial**:

- **Repositorio:** <https://github.com/YoYoGames/GM-TestFramework>
- Permite escribir **tests unitarios** para tu lógica GML y ejecutarlos de forma automática.
- Es especialmente útil para verificar **sistemas de guardado/carga**: escribes tests que guardan, cargan y comparan.

### Por qué importa para persistencia

El guardado es **el subsistema más fácil de romper sin darte cuenta**: cambias una variable, añades un campo, y todos los guardados antiguos dejan de funcionar. Un test que:

1. Crea un estado conocido.
2. Lo guarda.
3. Lo carga.
4. Compara que todo coincide.

…te avisa en el momento en que lo rompes, en vez de tres semanas después con un bug report de un jugador.

```gml
// Ejemplo conceptual de test (la API exacta está en el repo)
// test_guardado_carga()
// {
//     var _estado = { vida: 50, nivel: 3 };
//     guardar(_estado);
//     var _cargado = cargar();
//     assert_equal(_cargado.vida, 50, "La vida no se conservó");
//     assert_equal(_cargado.nivel, 3, "El nivel no se conservó");
// }
```

> 📖 **Consulta el repositorio para la API exacta.** Las firmas de las macros/funciones de aserción son las que define el framework, y no conviene inventárselas.

---

## 14. Checklist de persistencia

```
[ ] ¿Uso minúsculas y sin espacios en los nombres de archivo?
[ ] ¿Guardo solo DATOS PUROS, nunca handles?
[ ] ¿Versiono el formato de guardado?
[ ] ¿Valido la estructura antes de usar los datos cargados?
[ ] ¿Tengo un plan de migración para guardados antiguos?
[ ] ¿Borro los buffers después de usarlos y pongo la variable a -1?
[ ] ¿Uso buffer_load_async() si cargo desde servidor en HTML5?
[ ] ¿Sé dónde está el save area en mi plataforma objetivo?
[ ] ¿He probado a guardar y cargar en TODAS las plataformas objetivo?
[ ] ¿Tengo un test que verifica ida y vuelta (guardar → cargar → comparar)?
[ ] ¿El checksum se COMPARA al cargar, no solo se calcula al guardar? (§12 bis)
[ ] ¿Tengo copias de seguridad rotativas y una función de recuperación si el save principal falla? (§12 ter)
```

---

## Resumen

1. **El sandbox limita** el acceso a dos áreas: **file bundle** (lectura) y **save area** (lectura/escritura).
2. Al **leer**: primero se busca en el save area, luego en el bundle. Al **escribir**: solo save area.
3. **El save area está en un sitio distinto por plataforma** (AppData en Windows, `~/Library/Application Support` en macOS…).
4. **HTML5**: local storage de 1-5 MB, y carga desde servidor **solo** con `buffer_load_async()`.
5. **INI** para configuración simple; **texto/binario** para logs y formatos propios; **buffers** para todo lo demás.
6. ⭐ **JSON (`json_stringify` / `json_parse`) es la opción recomendada en 2026** para guardar structs y arrays.
7. ⚠️ **Nunca guardes handles**: no son estables entre sesiones. Guarda **datos puros** y reconstruye.
8. **Versiona y valida** siempre tu formato de guardado.
9. Los **buffers** requieren que leas en el mismo orden en que escribiste, o corrompes los datos.
10. Usa el **GameMaker Test Framework** para verificar ida y vuelta en tu sistema de guardado.
11. ⚠️ **Un checksum que se calcula pero no se compara no protege nada.** Calcula → guarda aparte → recalcula al leer → compara → rechaza si no coincide (§12 bis).
12. **Hashea el TEXTO JSON, nunca un struct reserializado**: el orden de sus claves no está garantizado, y reserializar puede dar un falso rechazo.
13. **Las copias de seguridad rotativas son la única forma real de recuperar un save roto**: la escritura atómica evita la corrupción a mitad, pero no protege de un bug que sobrescribe una partida buena con datos malos (§12 ter).
