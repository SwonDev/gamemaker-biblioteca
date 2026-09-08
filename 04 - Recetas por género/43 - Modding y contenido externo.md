# 43 · Modding y contenido externo

> Cómo dejar que alguien que no es tú añada contenido a tu juego —números, sprites, atlas
> completos, hechizos con lógica propia— sin que eso signifique darle las llaves del proceso.
> Hoy esto vive partido en cinco sitios que no se hablan: el sandbox de archivos
> ([01 · 14](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#1-el-sandbox-lo-primero-que-debes-entender)),
> la carga de sprites y atlas en tiempo de ejecución
> ([08 · 08](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md)),
> el catálogo de datos dirigidos
> ([13 · 06 §3.8](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#38-datos-dirigidos-definir-el-juego-en-json)),
> el catálogo de lenguajes embebidos
> ([12 · 01 §7](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md#7-ejecutar-código-en-tiempo-de-ejecución-scripting-y-modding))
> y la extensión de publicación
> ([07 · 01 §3](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organización%20YoYoGames.md)). Este
> documento las une en un flujo único: descubrir un mod, validarlo, cargarlo y ejecutarlo sin
> que pueda tumbar el juego.
>
> **No cubre** logros, anuncios ni compras integradas (→
> [04 · 20](./20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md), que
> usa extensiones `GMEXT-*` distintas con el mismo patrón de verificación), el intérprete de
> Bytecode en sí —aquí solo se usa, la construcción está en
> [13 · 23 §3.7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/23%20-%20Catálogo%20de%20patrones%20en%20GML.md#37-bytecode-un-intérprete-mínimo)—,
> el sistema de guardado en sí (→ 01 · 14), ni **ejecutar código nativo de terceros** (DLLs,
> extensiones compiladas): eso está deliberadamente **fuera de alcance** en todo este documento,
> ver §1.1.

---

## 1 · Los principios

### 1.1 Cuatro niveles de confianza, no uno solo

«Modding» no es una sola cosa: es un espectro, y tratarlo como un bloque único es la causa
número uno de que un proyecto o bien no soporte mods de verdad, o bien los soporte de una forma
que compromete la seguridad del jugador.

| Nivel | Qué es | Ejemplo | Si sale mal | Dónde se resuelve |
|---|---|---|---|---|
| **0 · Datos** | JSON puro, sin lógica | Subir el daño de un enemigo, añadir un nivel a una tabla | Un número absurdo, una clave repetida | §3.5 (fusión de catálogo) |
| **1 · Assets** | Sprites, atlas, audio | Reemplazar el sprite de un personaje, un pack de texturas | Memoria agotada, formato corrupto, tamaño fuera de presupuesto | §3.3, §3.4 |
| **2 · Scripts** | Código que decide, no solo datos | «El hechizo cuesta la mitad de maná si el objetivo está quemado» | Bucle infinito, acceso a algo que no debería | §3.6 (catspeak-lang) o el Bytecode de 13 · 23 §3.7 si basta con aritmética |
| **3 · Nativo** | DLLs, extensiones compiladas, binarios arbitrarios | Un `.dll`/`.dylib`/`.so` que el mod trae consigo | Ejecución arbitraria total: el mod ES el proceso | **Fuera de alcance.** No lo soportes salvo que firmes y revises cada mod a mano — es exactamente lo que hace Steam Workshop con su proceso de curación, no algo que un indie pueda replicar de forma segura |

> 🔺 **La regla de oro de este documento**: sube de nivel solo lo que necesites. El 90 % de los
> mods que un jugador quiere hacer —reequilibrar, reskinnear, añadir un nivel— son Nivel 0 o 1.
> Nivel 2 es para el 10 % que de verdad necesita lógica nueva. Nivel 3 casi nunca compensa el
> riesgo para un estudio pequeño.

### 1.2 El sandbox no es opcional: recuerda 01 · 14

Todo lo que sigue se apoya en una regla que **no puedes rodear**: GameMaker solo puede escribir
en el **save area**, y al leer busca primero ahí y luego en el **file bundle** de solo lectura
([01 · 14 §1](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#1-el-sandbox-lo-primero-que-debes-entender)).
Un mod, por definición, **no puede venir empaquetado con el juego** —si viniera, no sería un mod,
sería contenido base— así que **toda la carga de mods pasa por el save area**, con las mismas
restricciones que cualquier guardado: en HTML5 no hay directorios, en Android es invisible sin
root, y cada plataforma tiene su propia ruta.

### 1.3 Las cinco piezas que hoy no se hablan (mapa de este documento)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  mods/<id>/manifest.json          §3.1, §3.2   dónde vive y qué declara │
│  mods/<id>/catalogo.json          §3.5          se fusiona sobre 13·06  │
│  mods/<id>/sprites/*.png          §3.3          sprite_add uno a uno    │
│  mods/<id>/atlas.png + .json      §3.4          texturegroup_add        │
│  mods/<id>/script.cats            §3.6          catspeak-lang, sandbox  │
│  mod.io (descarga/publicación)    §3.7          GMEXT-mod.io            │
└─────────────────────────────────────────────────────────────────────────┘
```

Ningún campo del manifiesto es obligatorio salvo `id`, `nombre` y `version_catalogo`: un mod
de solo-datos no necesita `sprites`, uno de solo-arte no necesita `script`.

---

## 2 · El método, paso a paso

1. **Define el contrato.** Un mod es una carpeta con un `manifest.json` (§3.2). Sin manifiesto
   válido, la carpeta se ignora — nunca se ejecuta nada "por si acaso".
2. **Descubre los mods instalados**, por plataforma (§3.1). En desktop es enumerar directorios;
   en HTML5 no hay directorios que enumerar, así que la lista de mods activos viene de otro
   sitio (mod.io, o una lista que el propio jugador pega).
3. **Valida el manifiesto antes de tocar nada del juego** (§3.2): versión de catálogo compatible,
   tipos de campo correctos, tamaños dentro de presupuesto. Un mod que falla la validación se
   descarta con un aviso, **no** cuelga el arranque.
4. **Carga los assets declarados** — sprites sueltos con `sprite_add` (§3.3) o un atlas completo
   con `texturegroup_add` (§3.4) — y comprueba que cada uno se resolvió antes de seguir.
5. **Fusiona el catálogo del mod sobre el catálogo base** (§3.5) trabajando siempre sobre una
   copia: si la fusión falla a medias, el catálogo original sigue intacto.
6. **Compila y ejecuta el script del mod** dentro de un entorno catspeak con solo las funciones
   que decidiste exponer (§3.6). Nunca en el hilo que dibuja o el que gestiona el guardado.
7. **Publica y descarga con GMEXT-mod.io** (§3.7) cuando quieras alojar mods en un catálogo
   público en vez de depender de que el jugador copie carpetas a mano.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 La carpeta `mods/`: dónde vive y sus límites por plataforma

La carpeta de mods **vive dentro del save area**, nunca en el file bundle. Créala una vez, al
arrancar:

```gml
/// scr_mods.gml — descubrimiento

/// @desc Ruta del directorio de mods, relativa al save area de la plataforma actual.
/// @returns {String}
function mod_carpeta_raiz() {
    return "mods";
}

/// @desc Crea la carpeta de mods si hace falta. Debe llamarse una vez, al arrancar,
///       ANTES de cualquier otra función de este script.
function mod_sistema_iniciar() {
    if (os_browser != browser_not_a_browser) {
        // HTML5: no hay directorios (01 · 14 §11). El sistema de mods de disco
        // queda deshabilitado; solo funciona la vía mod.io de §3.7.
        registro_aviso("Sistema de mods de carpeta deshabilitado en HTML5 (sin directory_*).");
        return false;
    }

    if (!directory_exists(mod_carpeta_raiz())) {
        directory_create(mod_carpeta_raiz());
    }
    return true;
}

/// @desc Lista los nombres de carpeta de todos los mods instalados. Array vacío
///       si el sistema de mods de carpeta no está disponible en esta plataforma.
/// @returns {Array<String>}
function mod_descubrir_todos() {
    var _resultado = [];
    if (os_browser != browser_not_a_browser) return _resultado; // ver mod_sistema_iniciar

    var _nombre = file_find_first(mod_carpeta_raiz() + "/*", fa_directory);
    while (_nombre != "") {
        if (_nombre != "." && _nombre != "..") {
            array_push(_resultado, _nombre);
        }
        _nombre = file_find_next();
    }
    file_find_close();
    return _resultado;
}
```

Tabla de qué funciona de verdad por plataforma — todo lo demás de este documento hereda estos
límites:

| Plataforma | `directory_create`/`_exists` | `file_find_first` con `fa_directory` | `texturegroup_add` | Vía recomendada |
|---|---|---|---|---|
| Windows / macOS / Ubuntu | ✅ | ✅ (los atributos solo se respetan en Windows; en el resto usa `0`/`fa_none`) | ✅ | Carpeta `mods/` completa |
| Android / iOS | ✅ (área propia de la app) | ✅ | ✅ | Carpeta `mods/`, pero el jugador no puede copiar archivos a mano sin herramientas externas → depende de mod.io (§3.7) para llegar ahí |
| **HTML5 / GX.games** | ❌ *(01 · 14 §11: «no puedes crear ni destruir directorios»)* | ❌ | ❌ *(el manual de `texturegroup_add` lo dice explícitamente: «no está disponible en HTML5»)* | Solo catálogo JSON pegado/descargado por HTTP (§3.5) y scripts catspeak (§3.6); los assets nuevos solo pueden llegar como sprite suelto vía URL (§3.3) |

> ⚠️ **Consecuencia práctica**: si tu juego se publica también en HTML5, el modding «de carpeta»
> con atlas propios sencillamente no existe ahí. Diseña el sistema de mods pensando en el mínimo
> común denominador (datos + catspeak) y trata los assets nuevos vía `texturegroup_add` como un
> extra de desktop/móvil, no como la base.

### 3.2 El manifiesto del mod: el contrato antes de confiar en nada

Cada mod declara qué es en un `manifest.json` en la raíz de su carpeta:

```json
// mods/mas_goblins/manifest.json
{
    "id": "mas_goblins",
    "nombre": "Más variedad de goblins",
    "autor": "un_jugador",
    "version_catalogo": 1,
    "catalogo": "catalogo.json",
    "atlas": { "imagen": "atlas.png", "datos": "atlas.json" },
    "sprites": [],
    "script": "script.cats"
}
```

`version_catalogo` es la pieza que evita que un mod viejo rompa un juego actualizado: el juego
declara su propia versión de catálogo y rechaza mods que no coincidan, en vez de fusionar algo
que ya no tiene sentido.

```gml
/// @desc Versión de catálogo que entiende ESTA build del juego. Súbela cada vez
///       que cambies la forma del catálogo base (campos nuevos, tipos distintos).
#macro JUEGO_VERSION_CATALOGO 1

/// @desc Lee y valida el manifiesto de un mod. Nunca confía en los campos sin
///       comprobar tipo y presencia: un mod hecho a mano puede traer cualquier cosa.
/// @param {String} _carpeta_mod   Nombre de la subcarpeta dentro de mods/.
/// @returns {Struct}   El manifiesto validado, o `undefined` si el mod se descarta.
function mod_manifiesto_leer(_carpeta_mod) {
    var _ruta = $"{mod_carpeta_raiz()}/{_carpeta_mod}/manifest.json";
    if (!file_exists(_ruta)) {
        registro_aviso($"Mod «{_carpeta_mod}»: no tiene manifest.json, se ignora.");
        return undefined;
    }

    var _buff = buffer_load(_ruta);
    var _manifiesto;
    try {
        var _texto = buffer_read(_buff, buffer_text);
        _manifiesto = json_parse(_texto);
    } catch (_e) {
        registro_error($"Mod «{_carpeta_mod}»: JSON del manifiesto inválido — {_e.message}");
        buffer_delete(_buff);
        return undefined;
    }
    buffer_delete(_buff);

    if (!is_struct(_manifiesto)) {
        registro_aviso($"Mod «{_carpeta_mod}»: el manifiesto no es un objeto JSON.");
        return undefined;
    }
    if (!variable_struct_exists(_manifiesto, "id") || !is_string(_manifiesto.id)) {
        registro_aviso($"Mod «{_carpeta_mod}»: falta «id» o no es texto.");
        return undefined;
    }
    if (!variable_struct_exists(_manifiesto, "version_catalogo")
    ||  !is_real(_manifiesto.version_catalogo)) {
        registro_aviso($"Mod «{_carpeta_mod}»: falta «version_catalogo» o no es numérico.");
        return undefined;
    }
    if (_manifiesto.version_catalogo != JUEGO_VERSION_CATALOGO) {
        registro_aviso($"Mod «{_manifiesto.id}»: hecho para la versión de catálogo " +
                        $"{_manifiesto.version_catalogo}, esta build usa {JUEGO_VERSION_CATALOGO}. Se descarta.");
        return undefined;
    }

    return _manifiesto;
}
```

> 💡 El patrón es siempre el mismo y ya está en
> [05 · 04 §7](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md): fallar
> **ruidosamente en el registro** y **silenciosamente para el jugador** — un mod roto se ignora y
> se avisa por consola, nunca revienta el arranque del juego.

### 3.3 Cargar sprites de un mod: `sprite_add` y sus límites por plataforma

```gml
python3 _indice/buscar.py sprite_add
# → sprite_add(fname, imgnum, removeback, smooth, xorig, yorig) : Asset.GMSprite
```

Para un puñado de sprites sueltos (un ítem nuevo, un retrato), `sprite_add` uno a uno es
suficiente. Para docenas de sprites de golpe, usa el atlas de §3.4: cada `sprite_add` es una
textura independiente en VRAM, y eso no escala.

```gml
/// @desc Carga un sprite de un mod desde su carpeta. Devuelve -1 si falla,
///       nunca lanza: un PNG corrupto en un mod no debe tumbar el juego.
/// @param {String} _carpeta_mod
/// @param {String} _archivo       Nombre del PNG dentro de la carpeta del mod.
/// @param {Real}   _xorig
/// @param {Real}   _yorig
/// @returns {Asset.GMSprite}
function mod_sprite_cargar(_carpeta_mod, _archivo, _xorig = 0, _yorig = 0) {
    var _ruta = $"{mod_carpeta_raiz()}/{_carpeta_mod}/{_archivo}";
    if (!file_exists(_ruta)) {
        registro_aviso($"Mod «{_carpeta_mod}»: no encuentro «{_archivo}».");
        return -1;
    }

    try {
        return sprite_add(_ruta, 1, false, false, _xorig, _yorig);
    } catch (_e) {
        registro_error($"Mod «{_carpeta_mod}»: sprite_add falló en «{_archivo}» — {_e.message}");
        return -1;
    }
}
```

Tres restricciones de plataforma que el manual documenta explícitamente y que rompen un mod si
las ignoras:

| Plataforma | Restricción | Consecuencia si la ignoras |
|---|---|---|
| **iOS** | Si cargas un Included File de una subcarpeta, **no** incluyas la carpeta en el path — solo el nombre de archivo. En el resto de plataformas sí hace falta la carpeta completa | El mismo código de carga falla en iOS y funciona en el resto; código condicionado por `os_type` |
| **HTML5** | `sprite_add` **sí funciona**, pero de forma **asíncrona** y solo con una **URL**, no con una ruta local (no hay save area de archivos, solo local storage). Además puede necesitar CORS (`http_set_request_crossorigin`) | Tratar la llamada como síncrona: el sprite tarda uno o varios frames en estar listo, y usarlo antes de que llegue el evento produce el sprite por defecto o un crash |
| **Todas** | La memoria de un sprite cargado en runtime es **mayor** de lo esperado — se guarda como página de textura *y* en VRAM. Si no llamas a `sprite_delete()` cuando el mod se desactiva, es una fuga | Memoria creciente en sesiones largas con muchos mods probados |

En HTML5, la carga es async: la URL puede apuntar a un CDN (por ejemplo, el `binary_url` de un
recurso servido por mod.io, o tu propio servidor):

```gml
/// obj_cargador_mods · Create
spr_pendiente = noone;

/// obj_cargador_mods · Un botón "instalar retrato" en HTML5
var _url = "https://cdn.tu-servidor.com/mods/retrato_extra.png";
spr_pendiente = sprite_add(_url, 1, false, false, 0, 0);

/// obj_cargador_mods · Async - Image Loaded (evento del editor de objetos)
if (ds_map_find_value(async_load, "id") == spr_pendiente) {
    if (ds_map_find_value(async_load, "status") >= 0) {
        global.retrato_extra = spr_pendiente;
        registro_info("Retrato del mod cargado desde HTML5.");
    } else {
        registro_aviso("El retrato del mod no se pudo cargar (status < 0).");
    }
}
```

### 3.4 Atlas de golpe: `texturegroup_add` para contenido descargado

```gml
python3 _indice/buscar.py texturegroup_add
# → texturegroup_add(groupname, filename_or_buffer_or_array, struct_or_json) : Undefined
```

**No disponible en HTML5** (nota explícita del manual). Donde sí funciona, es la vía correcta
para un mod que trae **muchos** sprites: una sola textura en vez de una por `sprite_add`, y el
grupo entero se puede descargar de memoria de golpe con `texturegroup_delete` cuando el mod se
desactiva.

El tercer argumento **es un struct, no un array**: una clave por sprite, con el nombre de la
clave como nombre del recurso resultante. Confírmalo tú mismo si dudas —
[08 · 08](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md#texturegroup_addgroupname-filename_or_buffer_or_array-struct_or_json)
tiene la referencia completa de estados y funciones hermanas
(`texturegroup_load`/`_unload`/`_get_status`); aquí solo el flujo de modding:

```gml
/// @desc Carga el atlas declarado en el manifiesto de un mod como grupo de
///       texturas dinámico. El nombre del grupo se deriva del id del mod para
///       que dos mods nunca puedan chocar entre sí.
/// @param {Struct} _manifiesto   El manifiesto ya validado de mod_manifiesto_leer().
/// @returns {Bool}   true si el atlas quedó cargado.
function mod_atlas_cargar(_manifiesto) {
    if (!variable_struct_exists(_manifiesto, "atlas")) return true; // el mod no trae atlas

    if (os_browser != browser_not_a_browser) {
        registro_aviso($"Mod «{_manifiesto.id}»: trae atlas, pero texturegroup_add no existe en HTML5. Se ignora el atlas.");
        return false;
    }

    var _carpeta   = $"{mod_carpeta_raiz()}/{_manifiesto.id}/";
    var _grupo     = $"mod_{_manifiesto.id}";
    var _png       = _carpeta + _manifiesto.atlas.imagen;
    var _json_ruta = _carpeta + _manifiesto.atlas.datos;

    if (!file_exists(_png) || !file_exists(_json_ruta)) {
        registro_aviso($"Mod «{_manifiesto.id}»: faltan los ficheros del atlas.");
        return false;
    }

    if (texturegroup_exists(_grupo)) {
        registro_aviso($"Mod «{_manifiesto.id}»: el grupo «{_grupo}» ya existía, se reemplaza.");
        texturegroup_delete(_grupo);
    }

    var _buff_json = buffer_load(_json_ruta);
    var _datos_json = buffer_read(_buff_json, buffer_text);
    buffer_delete(_buff_json);

    try {
        // struct_or_json ACEPTA una cadena JSON directamente: no hace falta json_parse aquí.
        texturegroup_add(_grupo, _png, _datos_json);
    } catch (_e) {
        registro_error($"Mod «{_manifiesto.id}»: texturegroup_add falló — {_e.message}");
        return false;
    }

    return texturegroup_get_status(_grupo) != texturegroup_status_unloaded;
}

/// @desc Descarga el atlas de un mod cuando se desactiva.
function mod_atlas_descargar(_id_mod) {
    var _grupo = $"mod_{_id_mod}";
    if (texturegroup_exists(_grupo)) texturegroup_delete(_grupo);
}
```

El fichero `atlas.json` de cada mod sigue el formato exacto que exige `texturegroup_add` — un
struct llamado `sprites`, uno por recurso, con `width`/`height`/`frames`:

```json
// mods/mas_goblins/atlas.json
{
    "sprites": {
        "spr_goblin_mod_arquero": {
            "width": 32, "height": 32,
            "frames": [ { "x": 0, "y": 0 }, { "x": 32, "y": 0 } ]
        },
        "spr_goblin_mod_chaman": {
            "width": 32, "height": 32,
            "frames": [ { "x": 0, "y": 32 } ]
        }
    }
}
```

> ⚠️ **`texturegroup_get_sprites` para saber qué se creó de verdad**, en vez de asumir los
> nombres: `var _creados = texturegroup_get_sprites(_grupo);` devuelve el array real de sprites
> del grupo. Úsalo antes de referenciar un sprite del atlas por nombre en el catálogo (§3.5): si
> el JSON del mod tiene una clave mal escrita, el sprite correspondiente simplemente no está.

### 3.5 Fusionar el catálogo de un mod sobre el catálogo base (13 · 06 §3.8)

Este es el punto de unión real: el catálogo de datos dirigidos de
[13 · 06 §3.8](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#38-datos-dirigidos-definir-el-juego-en-json)
ya separa el contenido del código (`catalogo_leer`, `catalogo_cargar_todo`). Un mod de Nivel 0
es, literalmente, **otro JSON con la misma forma** que se fusiona encima.

```gml
/// @desc Fusiona el catálogo de un mod sobre una COPIA del catálogo base.
///       Nunca muta el catálogo base directamente: si algo del mod es inválido,
///       el catálogo original sigue intacto y el mod se descarta entero.
/// @param {Struct} _catalogo_base   El struct devuelto por catalogo_cargar_todo().
/// @param {String} _carpeta_mod
/// @param {String} _id_mod
/// @returns {Struct}   El catálogo fusionado (una copia), o el original si el mod falla.
function catalogo_fusionar_mod(_catalogo_base, _carpeta_mod, _id_mod) {
    var _ruta = $"{mod_carpeta_raiz()}/{_carpeta_mod}/catalogo.json";
    if (!file_exists(_ruta)) return _catalogo_base; // el mod no trae catálogo, nada que fusionar

    var _catalogo_mod = catalogo_leer(_ruta);
    if (!is_struct(_catalogo_mod) || array_length(variable_struct_get_names(_catalogo_mod)) == 0) {
        registro_aviso($"Mod «{_id_mod}»: catalogo.json vacío o inválido, se ignora.");
        return _catalogo_base;
    }

    // Copia profunda: si algo revienta a mitad de fusión, _catalogo_base (el original)
    // nunca se tocó.
    var _resultado = variable_clone(_catalogo_base, 4);
    var _secciones = variable_struct_get_names(_catalogo_mod); // "enemigos", "objetos", "niveles"...

    for (var _i = 0; _i < array_length(_secciones); _i++) {
        var _seccion = _secciones[_i];

        if (!variable_struct_exists(_resultado, _seccion)) {
            registro_aviso($"Mod «{_id_mod}»: sección «{_seccion}» no existe en el catálogo base, se ignora.");
            continue;
        }

        var _entradas_mod  = variable_struct_get(_catalogo_mod, _seccion);
        var _entradas_base = variable_struct_get(_resultado, _seccion);

        // Bucle explícito sobre las claves, no struct_foreach: la función de
        // retorno de struct_foreach no recibe contexto externo, y aquí hace
        // falta escribir en _entradas_base y registrar avisos por clave.
        var _claves_mod = variable_struct_get_names(_entradas_mod);
        for (var _j = 0; _j < array_length(_claves_mod); _j++) {
            var _clave = _claves_mod[_j];

            if (variable_struct_exists(_entradas_base, _clave)) {
                registro_aviso($"Mod «{_id_mod}»: sobrescribe «{_seccion}.{_clave}» " +
                                "(ya existía en el catálogo base u otro mod cargado antes).");
            }
            variable_struct_set(_entradas_base, _clave, variable_struct_get(_entradas_mod, _clave));
        }
    }

    return _resultado;
}

/// @desc Carga el catálogo base y le aplica, en orden, el catálogo de cada mod activo.
/// @param {Array<String>} _mods_activos   Carpetas de mods, en el orden en que se cargan
///                                        (el último gana si dos mods tocan la misma clave).
/// @returns {Struct}
function catalogo_cargar_con_mods(_mods_activos) {
    var _catalogo = catalogo_cargar_todo(); // 13 · 06 §3.8: enemigos / objetos / niveles

    for (var _i = 0; _i < array_length(_mods_activos); _i++) {
        var _carpeta     = _mods_activos[_i];
        var _manifiesto  = mod_manifiesto_leer(_carpeta);
        if (_manifiesto == undefined) continue; // ya se avisó dentro de mod_manifiesto_leer

        _catalogo = catalogo_fusionar_mod(_catalogo, _carpeta, _manifiesto.id);
    }

    return _catalogo;
}
```

> 🔺 **Valida referencias, no solo tipos.** Que `catalogo_fusionar_mod` acepte una entrada no
> significa que sea segura de usar: la función `enemigo_crear` de 13 · 06 §3.8 ya hace lo
> correcto — llama a `asset_get_index(_def.objeto)` y comprueba `-1` antes de crear nada. Un mod
> que referencia un sprite o un objeto que no existe en el proyecto **no debe crashear el juego
> al usarse**; debe fallar esa entrada concreta y seguir con el resto.
>
> 💡 **Orden de carga determinista.** `_mods_activos` es un array, no un `directory_create`
> escaneado al vuelo: guarda el orden explícito (por ejemplo, en las opciones del jugador) para
> que «el mod B sobrescribe al mod A» sea una decisión reproducible, no un accidente del orden en
> que el sistema de archivos devuelve los nombres.

### 3.6 Ejecutar código del jugador sin abrir un agujero: catspeak-lang

Cuando un mod necesita **lógica**, no solo datos, ni el catálogo de §3.5 (datos, sin lógica) ni
escribir GML a mano (lógica, pero solo la tuya) sirven. Hay dos escalones documentados en esta
biblioteca, y elegir el que no toca es el error más caro de esta sección:

| Necesitas | Usa | Por qué |
|---|---|---|
| Aritmética sobre stats, sin variables con nombre ni condicionales | El intérprete **Bytecode** de [13 · 23 §3.7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/23%20-%20Catálogo%20de%20patrones%20en%20GML.md#37-bytecode-un-intérprete-mínimo) | Es tuyo, cabe en un script, y **no tiene bucles**: un contenido mal escrito no puede colgar el juego porque el lenguaje no tiene forma de expresar un bucle infinito |
| Variables, condicionales, funciones definidas por el propio mod | **catspeak-lang** (esta sección) | Escribir y mantener un intérprete con ese alcance cuesta semanas; catspeak-lang ya lo resuelve, mantenido y probado por otros — catalogado en [12 · 01 §7](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md#7-ejecutar-código-en-tiempo-de-ejecución-scripting-y-modding) y en [11 · Código descargado/`_CATALOGO.md`](../11%20-%20Código%20descargado/_CATALOGO.md) |

**catspeak-lang** se presenta a sí mismo, en su propia web, exactamente para este caso: *«Use
Catspeak to implement fast and sandboxed modding support by compiling and executing arbitrary
user code»*. La biblioteca **no tiene el código fuente clonado** —el repo de
`11 - Código descargado/librerias/utilidades/catspeak-lang/` solo trae su generador de
documentación, porque el desarrollo se movió a Codeberg—, así que lo que sigue está verificado
contra la **documentación pública 3.2.0** (`katsaii.com/catspeak-lang`, consultada el 6 de
septiembre de 2026), no contra código local. Trátalo como API de una librería externa, no como
un símbolo del runtime: **no aparece en `buscar.py`** porque no es GML del motor.

**La pieza central es `CatspeakEnvironment`**, un entorno aislado y configurable:

```gml
/// scr_mod_sandbox.gml

/// @desc Crea un entorno catspeak con SOLO lo que un script de mod puede tocar.
///       Se llama una vez por partida, no una vez por mod: todos los mods
///       comparten el mismo entorno restringido.
function mod_entorno_crear() {
    var _entorno = new CatspeakEnvironment();

    // Presets "seguros" documentados por la propia librería: aritmética, arrays,
    // structs, cadenas y aleatoriedad — nada que toque archivos, red o el motor.
    _entorno.applyPreset(CatspeakPreset.TYPE, CatspeakPreset.MATH,
                          CatspeakPreset.STRING, CatspeakPreset.ARRAY,
                          CatspeakPreset.STRUCT, CatspeakPreset.RANDOM);
    // NUNCA CatspeakPreset.UNSAFE: la propia documentación lo etiqueta
    // "Use this preset with extreme caution" — expone reflexión y depuración.

    // Además de los presets, expón SOLO tus propias funciones de dominio,
    // nunca funciones del runtime de GameMaker directamente.
    _entorno.interface.exposeFunction("stat_leer", function(_id_entidad, _nombre_stat) {
        return variable_struct_get(_id_entidad.stats, _nombre_stat);
    });
    _entorno.interface.exposeFunction("danio_aplicar", function(_id_objetivo, _cantidad) {
        _id_objetivo.stats.vida = max(0, _id_objetivo.stats.vida - _cantidad);
    });
    _entorno.interface.exposeConstant("VERSION_API_MODS", 1);

    return _entorno;
}

/// @desc Compila el script de un mod ya validado. NO lo ejecuta todavía.
/// @param {Struct} _entorno    El de mod_entorno_crear().
/// @param {String} _carpeta_mod
/// @param {String} _id_mod
/// @returns {Function}   La función compilada, o undefined si falló.
function mod_script_compilar(_entorno, _carpeta_mod, _id_mod) {
    var _ruta = $"{mod_carpeta_raiz()}/{_carpeta_mod}/script.cats";
    if (!file_exists(_ruta)) return undefined; // el mod no trae script, es normal

    var _buff = buffer_load(_ruta);
    var _codigo_fuente = buffer_read(_buff, buffer_text);
    buffer_delete(_buff);

    try {
        var _ir = _entorno.parseString(_codigo_fuente);
        return _entorno.compile(_ir);
    } catch (_e) {
        registro_error($"Mod «{_id_mod}»: script.cats no compila — {_e.message}");
        return undefined;
    }
}

/// @desc Ejecuta la función ya compilada de un mod. Envuelta en try/catch:
///       un error del script del mod nunca debe propagarse fuera de esta función.
function mod_script_ejecutar(_funcion_compilada, _id_mod) {
    if (_funcion_compilada == undefined) return undefined;

    try {
        return _funcion_compilada();
    } catch (_e) {
        registro_error($"Mod «{_id_mod}»: error al ejecutar el script — {_e.message}");
        return undefined;
    }
}
```

Lo que **nunca** debes exponer a `_entorno.interface`, bajo ningún concepto — la lista exacta que
convierte «sandboxed» en real y no en decorativo:

```
NUNCA expongas al entorno de un mod:
  file_*, buffer_*, directory_*        → acceso a disco fuera del propio mod
  http_*, url_*, buffer_load_async     → red: exfiltración de datos, C2
  ini_*, json_*                        → aunque parezcan inocuos, dan acceso a
                                          leer/escribir estructuras del propio juego
  os_*, display_*, window_*            → huella digital del dispositivo del jugador
  game_end, game_restart, room_goto    → control del ciclo de vida del juego
  instance_create_layer con objeto
    arbitrario del catálogo interno    → un mod podría instanciar CUALQUIER objeto
                                          del proyecto, no solo los pensados para mods
```

Un script de mod solo debería poder hacer lo que **tú** decidiste envolver en una función propia
(`stat_leer`, `danio_aplicar`...). Esa capa intermedia — nunca el acceso directo al runtime — es
la diferencia entre «sandboxed» de verdad y un `execute_string` con maquillaje.

**Contra bucles infinitos**, la propia documentación de catspeak-lang describe el runtime como
uno que *«detects infinite loops and recursion so the sly `while true { }` doesn't freeze your
game»*, y expone un macro de tiempo límite:

> ⚠️ **No verificado con precisión esta sesión**: la documentación pública describe un macro
> `CATSPEAK_TIMEOUT` («el número de microsegundos antes de que un programa catspeak agote su
> tiempo; por defecto, 1 segundo»), pero el valor numérico exacto que aparece en el bloque de
> código de esa misma página (`1000`) es inconsistente con «1 segundo» expresado en microsegundos
> (que serían `1000000`). No se pudo confirmar cuál de los dos es el literal real sin el código
> fuente (no está en el espejo local). **Verifica el valor real en tu versión de catspeak-lang
> antes de depender de él**, y no asumas ninguna de las dos cifras como un hecho.

### 3.7 Publicar y descargar mods: GMEXT-mod.io

**GMEXT-mod.io** es la extensión oficial para alojar mods en **mod.io** (REST, multiplataforma),
catalogada en
[07 · 01 §3](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organización%20YoYoGames.md). Sus
funciones `modio_*` **no están en el runtime**: vienen de la extensión, exactamente como
`steam_*` en
[04 · 20](./20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md#la-regla-que-evita-el-90--de-los-errores).

```sh
python3 _indice/buscar.py modio_mods_add
# → «modio_mods_add» NO existe en el runtime — es de la extensión, no del motor.
```

Verificado directamente contra el código fuente real de la extensión, descargado en
`11 - Código descargado/extensiones_oficiales/GMEXT-mod.io/source/mod.io_gml/scripts/modio_api/modio_api.gml`
(1354 líneas, 75 funciones `modio_*`), el 6 de septiembre de 2026.

**Descargar un mod (el flujo del jugador que se suscribe).** El objeto que devuelve
`modio_mods_get` trae un `modfile.download.binary_url` — la URL real del zip en el CDN de
mod.io — y `modfile.filehash.md5` para comprobar que la descarga no se corrompió:

```gml
/// obj_modio_descargas · Create
descarga_id_actual = -1;
descarga_mod_id_actual = -1;
descarga_hash_esperado = "";
descarga_zip_local = "";
```

> ⚠️ **`mod_modio_descargar()` va en un script, no en este `Create`.** Es «el flujo del jugador
> que se suscribe» — lo dispara previsiblemente un botón de una lista de mods, un objeto
> distinto de `obj_modio_descargas` — y su firma ni siquiera espera un `self` concreto: solo
> recibe `_mod_id` y qualifica cada acceso como `obj_modio_descargas.campo`, nunca como variable
> desnuda. Eso demuestra que no necesita depender de dónde se declaró; dejarla en el `Create`
> solo consigue que cualquier otro objeto que la llame sin cualificar reviente con
> `Variable X.mod_modio_descargar(...) not set before reading it` — mismo mecanismo que
> [`04 · 19` §1](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#1--el-conductor).
> Los dos callbacks de abajo (`mod_modio_descarga_iniciar`/`_fallo`) sí pueden quedarse aquí: se
> pasan por **valor** a `modio_mods_get()` (sin paréntesis), así que el motor conserva su `self`
> original venga de donde venga la llamada — no dependen de cómo se resuelva el identificador.

```gml
/// scr_modio_descargas.gml

/// @desc Pide la info de un mod y arranca la descarga de su fichero activo.
///       Descarga un mod a la vez: para varias descargas en paralelo, encola
///       las llamadas en vez de mandarlas todas de golpe.
/// @param {Real} _mod_id
function mod_modio_descargar(_mod_id) {
    obj_modio_descargas.descarga_mod_id_actual = _mod_id;
    obj_modio_descargas.descarga_zip_local = $"mods_descargas/{_mod_id}.zip";

    if (!directory_exists("mods_descargas")) directory_create("mods_descargas");

    // Funciones con nombre, no anónimas: leen el estado de obj_modio_descargas
    // por nombre de objeto, sin depender de qué variables captura o no un
    // literal function() anidado (no verificado en esta sesión, ver Fuentes).
    modio_mods_get(_mod_id, mod_modio_descarga_iniciar, mod_modio_descarga_fallo);
}

/// @desc Callback de éxito de modio_mods_get(): arranca la descarga del binario.
/// @param {Struct} _respuesta   El struct Mod, con su .modfile anidado.
function mod_modio_descarga_iniciar(_respuesta) {
    obj_modio_descargas.descarga_hash_esperado = _respuesta.modfile.filehash.md5;
    obj_modio_descargas.descarga_id_actual = http_get_file(
        _respuesta.modfile.download.binary_url,
        obj_modio_descargas.descarga_zip_local);
}

/// @desc Callback de fallo de modio_mods_get().
function mod_modio_descarga_fallo(_error) {
    registro_error($"mod.io: no se pudo obtener el mod {obj_modio_descargas.descarga_mod_id_actual} — {_error}");
}

/// obj_modio_descargas · Async - HTTP
if (ds_map_find_value(async_load, "id") == descarga_id_actual) {
    if (ds_map_find_value(async_load, "status") == 0) {
        var _zip_local = ds_map_find_value(async_load, "result");

        // 1) Integridad: compara el hash antes de confiar en el archivo.
        if (md5_file(_zip_local) != descarga_hash_esperado) {
            registro_error("mod.io: el hash del zip descargado no coincide, se descarta.");
            file_delete(_zip_local);
        } else {
            // 2) Extraer al espacio de mods, en su PROPIA carpeta por id.
            var _destino = $"{mod_carpeta_raiz()}/{descarga_mod_id_actual}/";
            var _archivos = zip_unzip(_zip_local, _destino);
            if (_archivos > 0) {
                registro_info($"Mod {descarga_mod_id_actual} instalado ({_archivos} ficheros).");
            } else {
                registro_error($"mod.io: zip_unzip falló para el mod {descarga_mod_id_actual}.");
            }
            file_delete(_zip_local);
        }
    }
}
```

**Publicar un mod (el flujo del creador de contenido).** `modio_mods_add` crea la ficha,
`modio_modfiles_add` sube el zip del contenido (el `manifest.json` + `catalogo.json` + assets de
§3.1-§3.5, comprimidos):

```gml
modio_mods_add("Más variedad de goblins", spr_logo_buffer, "Añade dos variantes de goblin.", {
    description: "Dos enemigos nuevos que usan el catálogo de datos del juego base."
}, function(_mod_creado) {
    var _zip = buffer_load("mi_mod_empaquetado.zip");
    modio_modfiles_add(_mod_creado.id, _zip, {
        version: "1.0.0",
        changelog: "Primera versión.",
        active: true
    }, function(_modfile) {
        registro_info($"Mod publicado, id {_mod_creado.id}, modfile {_modfile.id}.");
    });
});
```

Restricciones reales de la API, verificadas en `docs/modfiles.js` de la propia extensión —no
inventadas, son las que impone mod.io—:

- El fichero debe ir **comprimido en zip** y **no puede superar 500 MB**.
- Los nombres de fichero dentro del zip no pueden contener `\ / ? " < > | : *`.
- Con `active: true` (el valor por defecto), subir un modfile nuevo dispara un evento
  `MODFILE_CHANGED` que los clientes pueden consultar con `modio_events_get_list` para saber que
  hay una actualización disponible — es el mismo mecanismo con el que construirías un «hay una
  versión nueva de este mod» sin sondear manualmente.
- **mod.io escanea cada subida en busca de virus.** El `Modfile` devuelto trae `virus_status`
  (`0` sin escanear, `1` escaneado, `2` en progreso, `3` demasiado grande, `4` no encontrado,
  `5` error) y `virus_positive` (`0`/`1`). **Comprueba ambos antes de instalar automáticamente un
  mod para el jugador** — ver §4, es el primer punto de la sección de riesgo.

---

## 4 · Riesgo: qué puede romper un mod y cómo aislarlo

| Vector | Qué puede pasar | Cómo se aísla |
|---|---|---|
| **Mod con `virus_positive == 1` o sin escanear** | Un binario malicioso llega hasta el jugador disfrazado de contenido | Comprobar `virus_status`/`virus_positive` del `Modfile` (§3.7) **antes** de descargar o instalar; nunca instalar en automático un mod recién subido sin `virus_status == 1` |
| **Catálogo con referencias a assets que no existen** | `asset_get_index` devuelve `-1`, y usarlo sin comprobar crashea la creación de instancias | `enemigo_crear` (13 · 06 §3.8) ya comprueba `-1` — replica el mismo patrón para cualquier función que consuma el catálogo fusionado (§3.5) |
| **Bucle infinito o recursión sin fondo en un script de mod** | El frame no termina nunca, el juego se congela | Usa el Bytecode de 13 · 23 §3.7 (sin bucles, por diseño) si te basta; si necesitas catspeak-lang, apóyate en su detección de bucles infinitos y en `CATSPEAK_TIMEOUT` (§3.6, con la salvedad marcada ahí) |
| **Exponer de más al entorno catspeak** | El script de un mod llama a `file_delete`, `http_request` o similar si están expuestos | La lista negra explícita de §3.6: nunca `file_*`/`buffer_*`/`http_*`/`directory_*`/`os_*` en el `interface`, nunca `CatspeakPreset.UNSAFE` |
| **Atlas o sprite que agota VRAM** | Un mod con texturas gigantes o docenas de atlas activos a la vez | Presupuesto explícito de memoria por mod (número máximo de páginas de textura, revisado con `texturegroup_get_status`); `texturegroup_unload`/`sprite_delete` al desactivar un mod, siempre |
| **Colisión de nombres entre dos mods** | El mod B sobrescribe silenciosamente una clave del mod A sin que nadie se entere | `catalogo_fusionar_mod` (§3.5) registra un aviso en **cada** sobrescritura; el orden de carga es una lista explícita, no el orden del sistema de archivos |
| **Un mod escribe fuera de su propia carpeta** | Un `manifest.json` con rutas manipuladas (`../../partida.sav`) intenta leer o sobrescribir el guardado del jugador | Nunca construyas una ruta de archivo concatenando un campo del manifiesto sin sanear: valida que no contenga `..` antes de usarlo en cualquier función de archivo; cada mod opera solo dentro de `mods/<id>/`, nunca en la raíz del save area |
| **Actualización de un mod rompe una partida guardada que lo usaba** | El jugador carga una partida que referencia una clave de catálogo que el mod ya no tiene en su versión nueva | Versiona (`version_catalogo` del manifiesto, §3.2) y guarda en la propia partida qué mods (id + versión) estaban activos, para poder avisar «falta el mod X v1» en vez de crashear al cargar — el mismo problema de fondo que las migraciones de guardado de [13 · 06 §3.10](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) |
| **Un mod trae código nativo (DLL/extensión)** | Ejecución arbitraria total — el mod deja de ser un mod y pasa a ser el proceso | Fuera de alcance por diseño (§1.1): no cargues extensiones de terceros sin firmarlas y revisarlas tú, uno a uno, como hace la curación de Steam Workshop |

> 🔺 **El principio que resume esta sección**: cada paso de carga de un mod —manifiesto, assets,
> catálogo, script— está envuelto en su propio `try`/`catch` y trabaja sobre una copia o un
> espacio de nombres propio. **Un mod roto pierde ESE mod, nunca la partida ni el proceso.**

---

## 5 · Checklist

```
[ ] ¿El manifiesto se valida ANTES de tocar el catálogo, los assets o ejecutar nada?
[ ] ¿Cada carga (manifiesto, sprite, atlas, script) está en su propio try/catch?
[ ] ¿La fusión de catálogo trabaja sobre una COPIA (variable_clone), nunca sobre el original?
[ ] ¿Cada sobrescritura de clave entre mods queda registrada, no silenciosa?
[ ] ¿El entorno catspeak expone SOLO funciones de dominio propias, nunca *_directorio/*_archivo/http_*?
[ ] ¿Comprobé qué falla en HTML5 (directory_*, texturegroup_add) antes de diseñar el flujo?
[ ] ¿Verifiqué virus_status/virus_positive antes de instalar un mod descargado de mod.io?
[ ] ¿Guardo qué mods (id + versión) usaba una partida, para detectar mods que faltan al cargar?
[ ] ¿sprite_delete()/texturegroup_unload() al desactivar un mod, siempre?
[ ] ¿Los nombres de recurso de un mod usan un espacio de nombres propio (mod_<id>_...) para no chocar con el proyecto base?
```

---

## 6 · Errores clásicos y cómo evitarlos

| Error | Consecuencia | Corrección |
|---|---|---|
| Diseñar el sistema de mods pensando solo en desktop | El día que se publica en HTML5, «modding» deja de significar nada porque `directory_*` y `texturegroup_add` no existen ahí | Diseña primero para el mínimo común (datos + catspeak, §3.1) y trata el resto como mejora de plataforma |
| Confiar en el manifiesto sin comprobar tipos | Un `"version_catalogo": "uno"` (string en vez de número) revienta la comparación o, peor, pasa silenciosamente | `is_real`/`is_string`/`is_struct` explícitos antes de usar cualquier campo, como en `mod_manifiesto_leer` |
| Exponer un preset `UNSAFE` o una función del runtime «solo para probar» y olvidarlo | El sandbox deja de ser un sandbox; un script de mod gana reflexión o acceso a depuración | Lista blanca explícita y revisada de §3.6, nunca lista negra «lo que se me ocurra excluir» |
| Fusionar el catálogo del mod directamente sobre el catálogo base cargado en memoria | Si el mod 3 de 5 falla a mitad de fusión, el catálogo queda en un estado mezclado e irreproducible | `variable_clone` antes de tocar nada (§3.5); si algo falla, se descarta ESE mod y se sigue con el catálogo anterior intacto |
| Tratar `texturegroup_add` como si aceptara un array de sprites con `name` | La llamada falla o crea recursos con nombres inesperados: el formato real es un **struct** clave→definición, no un array | Verifica el struct exacto contra el manual (§3.4) antes de escribir el generador del `atlas.json` |
| Asumir que `sprite_add` es síncrono en HTML5 | El sprite se usa un frame antes de estar listo: aparece el sprite por defecto o un error | Trátalo siempre como asíncrono ahí: `Async - Image Loaded` + comprobar `status` en `async_load` (§3.3) |
| Instalar automáticamente cualquier modfile recién descargado de mod.io | Un archivo con `virus_positive == 1` o sin escanear todavía llega al disco del jugador | Comprobar `virus_status`/`virus_positive` antes de la instalación automática (§3.7, §4) |

---

## Ver también

- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — el sandbox de dos áreas, las rutas del save area por plataforma y por qué HTML5 no tiene directorios; la base de todo §3.1
- [13 · 06 — Arquitectura de un proyecto GameMaker](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) — §3.8 (`catalogo_leer`/`catalogo_cargar_todo`, la base que §3.5 fusiona), §3.3 (`servicio()`), §3.14 (`registro_error`/`registro_aviso`) y §3.10 (migraciones de guardado, el mismo problema que un mod desactivado)
- [13 · 23 — Catálogo de patrones en GML](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/23%20-%20Catálogo%20de%20patrones%20en%20GML.md) — §3.7, el patrón **Bytecode**: la alternativa sin dependencias a catspeak-lang cuando basta con aritmética sobre una pila
- [12 · 01 — Herramientas del flujo de trabajo](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md) — §7, el catálogo completo de lenguajes embebidos (catspeak-lang, JITSpeak, GMLC, GMLVM, RunGML, Apollo) con el resto de opciones si catspeak-lang no encaja
- [11 · Código descargado — `_CATALOGO.md`](../11%20-%20Código%20descargado/_CATALOGO.md) — dónde está el espejo local de `catspeak-lang` y de `GMEXT-mod.io`, y el aviso de licencia de cada repositorio
- [07 · 01 — GitHub, organización YoYoGames](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organización%20YoYoGames.md) — §3, las 44 extensiones `GMEXT-*`, incluida `GMEXT-mod.io`
- [08 · 08 — Texturas y grupos de texturas](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md) — referencia completa de `texturegroup_add`/`_load`/`_unload`/`_get_status` y el resto de gestión de VRAM
- [04 · 20 — Servicios de plataforma](./20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md) — el mismo patrón de «verifica la función de extensión en su propio código fuente», aplicado a Steam/AdMob/Firebase en vez de a mod.io
- [13 · 10 — Testing y QA](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md) — §2.1-2.4 para escribir `catalogo_fusionar_mod` como lógica pura y testeable, y §5 (*golden files*) para una prueba de regresión que detecte cuándo un catálogo fusionado deja de coincidir con lo esperado
- [05 · 04 — Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — §7, el patrón de fallo ruidoso en desarrollo / silencioso para el jugador que usa todo `mod_manifiesto_leer`
- [01 · 03 — Handles](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) — por qué `asset_get_index` se compara con `-1` y nunca con aritmética de enteros
- [01 · 07 — Funciones, métodos y ámbito](../01%20-%20Fundamentos/07%20-%20Funciones%2C%20m%C3%A9todos%20y%20%C3%A1mbito.md#7-closures-clausuras) — §7, las closures que hacen posible que el callback interno de `modio_modfiles_add` en §3.7 siga viendo el `id` del mod creado por el callback externo de `modio_mods_add`

---

## Fuentes

Consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker (LTS)** — espejo local en `09 - Manual oficial/manual-lts-2026-es/`
y `-en/`, páginas abiertas directamente en esta sesión:

- `GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_add.htm` — restricción de iOS (sin subcarpeta en el path), aviso de HTML5/CORS, coste de memoria real
- `The_Asset_Editors/Object_Properties/Async_Events/Image_Loaded.htm` — el flujo async de `sprite_add` con URL, `async_load`, `ds_map_find_value`
- `GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_add.htm` (es y en) — el struct `sprites` exacto, «no disponible en HTML5», sobrescritura y eliminación
- `GameMaker_Language/GML_Reference/File_Handling/File_Directories/directory_create.htm` — «no funcionará en HTML5»
- `GameMaker_Language/GML_Reference/File_Handling/File_Directories/File_Directories.htm` (vía `08 · 17`) — `file_find_first`/`fa_directory` no funciona en HTML5 ni GX.games
- `GameMaker_Language/GML_Reference/Asynchronous_Functions/HTTP/http_get_file.htm` — el ejemplo oficial encadenado con `zip_unzip`, que §3.7 reproduce
- `GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing/zip_unzip.htm` — comportamiento y origen válido del zip (bundle o save area)
- `GameMaker_Language/GML_Overview/Language_Features/try_catch_finally.htm` — estructura exacta del struct de excepción (`message`, `longMessage`, `script`, `stacktrace`)
- `GameMaker_Language/GML_Reference/Variable_Functions/variable_clone.htm` — semántica de copia profunda usada en §3.5; también se consultó `struct_foreach.htm`, descartada para la fusión de catálogo porque su función de retorno no admite contexto externo (se explica en el propio §3.5)
- `GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Information/sprite_get_info.htm` (es y en) — **discrepancia encontrada**: la traducción española de esta página tradujo también los *nombres* de los campos del struct devuelto (`anchura`, `altura`, `tipo`...); los nombres reales, confirmados en la página en inglés y en el propio ejemplo de código de la página española (`_info.type`), son `width`, `height`, `type`, etc. Este documento usa los nombres reales; no se ha corregido la página fuente porque no está en el encargo

**Código fuente real, descargado** en `11 - Código descargado/`:

- `extensiones_oficiales/GMEXT-mod.io/source/mod.io_gml/scripts/modio_api/modio_api.gml` — las 75 funciones `modio_*` citadas en §3.7, incluidas firmas exactas
- `extensiones_oficiales/GMEXT-mod.io/docs/modfiles.js` — límite de 500 MB, caracteres prohibidos en nombres de fichero, evento `MODFILE_CHANGED`
- `extensiones_oficiales/GMEXT-mod.io/docs/response_schemas.js` — structs `Modfile`, `Download`, `Filehash` y los valores de `virus_status`/`virus_positive` usados en §4
- `extensiones_oficiales/GMEXT-mod.io/README.md` y `docs/quick_start_guide.md`
- `librerias/utilidades/catspeak-lang/README.md` — la cita textual sobre *«fast and sandboxed modding support»*

**Documentación pública de catspeak-lang** (no está en el espejo local: el repo descargado solo
trae herramientas de generación de documentación, el código se movió a Codeberg) —
`https://www.katsaii.com/catspeak-lang/3.2.0/`, consultada vía WebFetch el 6 de septiembre de
2026:

- `hom-welcome.html` — *«the sandboxed environment prevents modders from modifying sensitive game state, or freezing your game with infinite loops»*, *«Impossible for modders to execute malicious code by default»*, *«Detects infinite loops and recursion»*
- `lib-struct-catspeakenvironment.html` — métodos `parseString`, `compile`, `applyPreset`; `addFunction`/`addConstant` marcados como obsoletos en favor de `interface.exposeFunction`/`interface.exposeConstant`
- `lib-enum-catspeakpreset.html` — los diez miembros del enum, con `UNSAFE` marcado explícitamente como *«use this preset with extreme caution»*
- `lib-codegen.html` — el macro `CATSPEAK_TIMEOUT` (ver la advertencia ⚠️ en §3.6: la propia documentación es internamente inconsistente sobre su valor numérico)

**Símbolos verificados con `python3 _indice/buscar.py`** contra `simbolos.json` (runtime
`2026.0.0.23`): `directory_create`, `directory_exists`, `directory_destroy`, `file_find_first`,
`file_find_next`, `file_find_close`, `file_exists`, `file_delete`, `fa_directory`, `fa_none`,
`sprite_add`, `sprite_delete`, `sprite_exists`, `texturegroup_add`, `texturegroup_delete`,
`texturegroup_exists`, `texturegroup_get_status`, `texturegroup_get_sprites`,
`texturegroup_load`, `texturegroup_unload`, `texturegroup_status_unloaded`, `buffer_load`,
`buffer_save`, `buffer_delete`, `buffer_read`, `buffer_text`, `json_parse`, `json_stringify`,
`is_struct`, `is_string`, `is_real`, `variable_struct_exists`, `variable_struct_get`,
`variable_struct_set`, `variable_struct_get_names`, `variable_clone`,
`array_length`, `array_push`, `asset_get_index`, `os_browser`, `browser_not_a_browser`,
`http_get_file`, `zip_unzip`, `md5_file`, `ds_map_find_value`, `async_load`, `game_save_id`,
`show_debug_message`, `max`.

**Símbolos que se quiso usar y NO existen** (confirmado con `buscar.py`, se documenta para no
repetir la alucinación): `modio_mods_add` y el resto de `modio_*` (son de la extensión
GMEXT-mod.io, no del runtime — verificados contra su código fuente real en su lugar, ver arriba),
`directory_get_working` (⚠️ aparece **usado en la propia biblioteca**, en
`01 - Fundamentos/14 - Persistencia y archivos.md` §11, como si fuera una función real del
runtime — no lo es; `buscar.py --listar directory_` solo devuelve `directory_create`,
`directory_exists` y `directory_destroy`. No se ha corregido esa página porque no está en el
encargo de este documento, pero queda anotado aquí para quien lo revise).

**Biblioteca interna ya verificada, no repetida aquí**: el catálogo de datos dirigidos completo
(13 · 06 §3.8), el patrón Bytecode completo (13 · 23 §3.7) y el sistema de logging
`registro_error`/`registro_aviso`/`registro_info` (13 · 06 §3.14).

> ⚠️ **Marcado como no verificado esta sesión**: el valor numérico exacto de `CATSPEAK_TIMEOUT`
> (§3.6); si `directory_create("mods/subcarpeta")` crea directorios anidados de golpe o exige que
> el padre ya exista —no está documentado explícitamente y este documento asume, por precaución,
> que hay que crear cada nivel— y el comportamiento exacto de `zip_unzip` en HTML5/GX.games (el
> manual no lo menciona; se asume no soportado por coherencia con el resto de funciones de
> archivo de esa plataforma, no por una fuente que lo confirme directamente).
