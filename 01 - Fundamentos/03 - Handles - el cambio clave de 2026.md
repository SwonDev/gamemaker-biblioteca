# 03 · Handles — el cambio clave de 2026

> **Fuentes principales:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Data_Types.htm> (apartado «Handles»)
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/handle.htm> (`handle_parse`)
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/is_handle.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Instance_Keywords.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/The_Asset_Browser.htm> (shaders/tags, para `asset_get_tags`)

> ⚠️ **Este es el capítulo más importante si vienes de GameMaker 2023 o anterior.**
> El cambio de «IDs numéricos» a **handles** es silencioso: tu código antiguo **compila** y en su mayoría **funciona**… hasta que un día falla de forma rara y difícil de reproducir.

---

## 1. El problema: qué era un «ID» antes

En versiones antiguas, cuando hacías esto:

```gml
var _lista = ds_list_create();
```

`_lista` contenía un **número entero simple**: el índice de la lista. `0`, `1`, `2`… Y cuando hacías:

```gml
var _enemigo = instance_create_layer(x, y, "Instances", obj_slime);
```

`_enemigo` contenía otro **número**: el ID de la instancia. Un `100003`, por ejemplo.

### ¿Qué tenía de malo?

**Nada distinguía un tipo de recurso de otro.** Eran todos números. Eso significa que el compilador no podía ayudarte:

```gml
ds_map_add(mi_lista, "clave", 10);   // ❌ Le pasas una LISTA a una función de MAPA
                                     //    Antes: compilaba. En runtime: comportamiento
                                     //    indefinido o error confuso.
```

Y lo mismo con:

```gml
sprite_get_width(obj_enemigo);        // ❌ Un objeto donde se espera un sprite
audio_play_sound(mi_buffer, 0, false);// ❌ Un buffer donde se espera un sonido
```

Todos estos errores se detectaban **en runtime**, a veces muy lejos de donde estaba el bug real.

---

## 2. La solución de 2026: los handles

Un **handle** es una **referencia a un recurso** que, además del índice, **lleva información del tipo**.

Técnicamente es un **entero de 64 bits**:

```
┌─────────────────────────┬──────────────────────────────┐
│  32 bits de TIPO        │   32 bits de ÍNDICE          │
│  (¿es una ds_list?      │   (¿qué número de recurso?)  │
│   ¿un sprite? ¿una      │                              │
│   instancia?)           │                              │
└─────────────────────────┴──────────────────────────────┘
```

Esa información de tipo se usa para **comprobar que le pasas a cada función el tipo de recurso correcto**. Ahora `ds_map_add(mi_lista, ...)` se puede detectar porque el handle dice «soy una ds_list».

### ¿Qué cosas son handles?

| Categoría | Ejemplos |
|---|---|
| **Estructuras de datos** | DS lists, DS maps, DS grids, DS stacks, DS queues, DS priority queues |
| **Assets** | Objects, Sprites, Rooms, Sounds, Fonts, Paths, Scripts, Shaders, Tile Sets, Sequences, Animation Curves, Timelines, Particles |
| **Instancias de objeto** | Las creadas con `instance_create_layer()` / `instance_create_depth()` |
| **Funciones de script** | Las definidas con `function nombre() {}` en un Script asset |
| **Partículas** | Particle systems, emitters, particle types |
| **Buffers** | Buffers, vertex buffers y vertex formats |
| **Surfaces** | ⚠️ **excepto** `surface_get_target()` y `surface_get_target_depth()` |
| **Referencias creadas con** | `ref_create()` |
| **Time Sources** | Los creados con `time_source_create()` |
| **Capas y tilemaps** | Room layers, tile map element IDs |
| **Flex Panels** | Los nodos de flex panel |

### Cuándo obtienes un handle

1. Cuando **creas** un recurso con una función `*_create()`.
2. Cuando **referencias** un recurso existente en tu código: escribir `obj_player`, `spr_enemigo`, `rm_nivel_1`… devuelve un handle.
3. Cuando obtienes una instancia desde una función: `instance_nearest()`, `instance_place()`, `instance_find()`, etc.

```gml
var _h1 = ds_list_create();                    // handle de DS list
var _h2 = obj_player;                          // handle de object asset
var _h3 = instance_nearest(x, y, obj_enemigo); // handle de instancia
var _h4 = layer_get_id("Suelo");               // handle de capa
var _h5 = mi_funcion;                          // handle de script function
```

---

## 3. Cómo se comparan los handles (y por qué esto rompe código)

### La regla

Un handle es **inválido** cuando su índice es:

| Tipo de handle | Valor inválido |
|---|---|
| **Cualquier handle** (listas, surfaces, buffers, assets…) | `-1` |
| **Handles de instancia** | `-4`, que es la constante **`noone`** |

La forma canónica de comprobar validez:

```gml
// Para cualquier handle que no sea de instancia
if (_handle != -1)
{
    // el handle es válido
}

// Para handles de instancia
if (_instancia != noone)
{
    // la instancia existe
}
```

### ⚠️ La trampa mortal: `self`, `other`, `all`, `noone`

Históricamente estas keywords guardaban valores negativos para que GameMaker supiera cuál era cuál:

| Keyword | Valor legacy |
|---|---|
| `self` | **-1** |
| `other` | -2 |
| `all` | -3 |
| `noone` | -4 |

**Por compatibilidad, esos valores siguen existiendo.** Y aquí está el problema:

```gml
// Imagina que _enemigo es un handle de instancia que resulta ser inválido (-4 = noone)
// o un handle de surface inválido (-1)

with (_enemigo)
{
    // ❌ ERROR CONCEPTUAL: si _enemigo == -1, este bloque NO se salta:
    //    se ejecuta sobre SELF, porque -1 es el valor legacy de self!
}
```

El manual lo dice literalmente:

> *«This can be seen in a `with` block, where if you pass -1 the block is executed on self. This may be unintentional when a Handle is passed with a value of -1, where the expectation would be the with block not executing however it executes on self due to this legacy behaviour.»*

**Consecuencia práctica:** **comprueba siempre** el handle antes de usarlo en `with()`, en vez de confiar en que «si es inválido no hará nada».

```gml
// ✅ CORRECTO
var _enemigo = instance_nearest(x, y, obj_enemigo);
if (_enemigo != noone)
{
    with (_enemigo)
    {
        vida -= 10;
    }
}
```

```gml
// ❌ PELIGROSO (código legacy que parecía funcionar)
with (instance_nearest(x, y, obj_enemigo))
{
    vida -= 10;   // si no hay enemigos, ¡se ejecuta sobre self!
}
```

Otro sitio donde aparece: convertir `self` a string da `"-1"`. Y usar `-1` donde se espera un scope se refiere a `self`.

> **Regla de oro:** nunca uses los valores numéricos `-1`, `-2`, `-3`, `-4` directamente. Usa siempre `self`, `other`, `all`, `noone`.

### `is_handle()`

```gml
var _h = sprite_index;
if (is_handle(_h))
{
    show_debug_message("Esto es un handle");
}
```

Úsalo para validar datos que vienen de fuera (archivos de guardado, JSON, redes), no para código normal donde el tipo ya es obvio.

---

## 4. El reciclado de índices (el bug silencioso)

Esta es la segunda gran fuente de problemas y **funcionaba igual antes**, pero los handles la hacen más visible.

> Los índices se **reciclan**. Si destruyes una DS list con índice `0` y luego creas otra, esa nueva lista **también tendrá el índice `0`**.

```gml
// Create event
mi_lista = ds_list_create();   // supón índice 0

// Clean Up event
ds_list_destroy(mi_lista);
// ⚠️ mi_lista sigue valiendo 0 (el handle no se limpia solo)

// ...más tarde, en otra parte del juego:
otra_lista = ds_list_create();  // ¡puede reutilizar el índice 0!

// Ahora mi_lista apunta a una lista ACTIVA que no es la tuya.
// Cualquier ds_list_add(mi_lista, ...) corrompe la OTRA lista.
```

### La solución: resetea a mano después de destruir

```gml
// Clean Up event

// Para estructuras de datos, buffers, surfaces, time sources...
ds_list_destroy(mi_lista);
mi_lista = -1;

// Para instancias
instance_destroy(_enemigo);
_enemigo = noone;
```

> El propio manual lo recomienda: *«it is good practice to reset a handle variable to -1 after destroying its resource if it continues to be used after destruction. Handles that hold an instance should be reset to noone instead.»*

### Y la inicialización

Inicializa siempre la variable al valor inválido antes de usarla:

```gml
// Create event
mi_superficie = -1;     // no es una instancia → -1
mi_enemigo    = noone;  // es una instancia → noone
mi_lista      = -1;
mi_buffer     = -1;
```

Así, si algo intenta usarla antes de que exista, la comprobación `!= -1` / `!= noone` lo detiene en vez de actuar sobre un recurso ajeno.

---

## 5. Handles y strings: ida y vuelta

### Handle → string

```gml
var _s = string(mi_ds_list);   // "ref ds_list 1"
var _s2 = string(spr_player);  // "ref sprite spr_player"
```

El formato es `"ref <tipo> <id>"` o `"ref <tipo> <nombre>"`, según la representación interna del tipo.

Esto es **muy útil para depurar**:

```gml
show_debug_message($"Colisioné con {_instancia}");
// → Colisioné con ref instance 100234
```

### Handle → número

```gml
var _n = real(mi_ds_list);    // devuelve el ÍNDICE (ej. 1)
var _n2 = int64(mi_ds_list);  // idem en int64
```

### String → handle

```gml
var _h = handle_parse("ref ds_list 1");
```

Devuelve `undefined` si el tipo de handle no es válido o el string está mal formado.

**Ejemplo completo (del manual):**

```gml
sprite = spr_player;
handle_as_string  = string(sprite);
handle_from_string = handle_parse(handle_as_string);

show_debug_message($"{sprite} ({typeof(sprite)})");
show_debug_message($"{handle_as_string} ({typeof(handle_as_string)})");
show_debug_message($"{handle_from_string} ({typeof(handle_from_string)})");
```

Salida:
```
ref sprite spr_player (ref)
ref sprite spr_player (string)
ref sprite spr_player (ref)
```

> Fíjate: el handle original es `"ref"`, se convierte en `"string"`, y al parsearlo vuelve a ser `"ref"`. Los valores se convierten a su representación de string **implícitamente** para mostrarlos.

### ⚠️ ¿Por qué esto importa para guardar partidas?

`json_stringify()` serializa los handles como su **referencia**, y `json_parse()` los reconvierte a referencias de runtime. Pero:

> *«Keep in mind that this will not be useful between game sessions as asset information may have changed, depending on the type of asset. Assets are saved using their names so these references maintain their links as long as the asset name does not change.»*

Traducción: **los handles NO son estables entre sesiones del juego.** Se guardan por **nombre** para los assets, pero el índice se recicla para los recursos dinámicos. Nunca guardes un handle de DS/surface/buffer/instancia en un archivo de guardado esperando que siga siendo válido al recargar.

Puedes **desactivar** esa conversión pasando `true` en el tercer argumento de `json_parse()`:

```gml
var _datos = json_parse(_json, undefined, true);
//                                        ↑ inhibit_string_convert
// Los valores siguen siendo strings; tú decides qué hacer con ellos
```

---

## 6. La compatibilidad hacia atrás (y por qué es un arma de doble filo)

Aquí está la parte delicada. El manual lo explica sin rodeos:

> *«In older versions of GameMaker, resources that are now referenced by handles used simple index numbers and **for legacy support they are still accepted**. This means it is possible for a simple **Real** value to act as a resource ID if such a value is accidentally passed.»*

Es decir: **por compatibilidad, las funciones siguen aceptando números simples.**

```gml
ds_map_add(2, "clave", 10);
// ❌ No hay comprobación de tipo (2 es un Real, no un handle)
//    GameMaker buscará un DS map con ID 2. Si existe, lo modifica.
//    Si no, error en runtime.
```

**Esto significa que el sistema NO te protege al 100 %.** Solo te protege cuando pasas un **handle de verdad** (que lleva el tipo dentro). Si pasas un número pelado, se salta la comprobación.

### La regla del manual

> *«You should ensure that you only pass a **Handle** returned by a `*_create()` function into compatible functions and not pass **Real** values directly.»*

**En la práctica:**

- ✅ Pasa siempre lo que te devolvió `*_create()`.
- ❌ Nunca hardcodees números.
- ❌ Nunca hagas aritmética con handles (`_h + 1`, `_h * 2`).
- ❌ Nunca guardes handles en archivos de guardado.

---

## 7. Guía de migración: antes y después

### Caso 1: estructuras de datos

```gml
// ───────── ANTES (legacy) ─────────
// Create
mi_lista = 0;
mi_lista = ds_list_create();

// Uso
if (mi_lista >= 0) { ds_list_add(mi_lista, 5); }

// Destroy
ds_list_destroy(mi_lista);
```

```gml
// ───────── DESPUÉS (2026) ─────────
// Create
mi_lista = -1;                      // ← inicializa al valor inválido
mi_lista = ds_list_create();

// Uso
if (mi_lista != -1) { ds_list_add(mi_lista, 5); }

// Clean Up
if (mi_lista != -1)
{
    ds_list_destroy(mi_lista);
    mi_lista = -1;                  // ← resetea tras destruir
}
```

### Caso 2: instancias

```gml
// ───────── ANTES ─────────
var _e = instance_nearest(x, y, obj_enemigo);
with (_e) { vida -= 10; }          // si no hay enemigo, actuaba sobre self
```

```gml
// ───────── DESPUÉS ─────────
var _e = instance_nearest(x, y, obj_enemigo);
if (_e != noone)                   // ← comprobación explícita
{
    with (_e) { vida -= 10; }
}
```

### Caso 3: surfaces

```gml
// ───────── DESPUÉS (el patrón recomendado) ─────────
// Create event
surf = -1;

// Draw event
if (!surface_exists(surf))
{
    surf = surface_create(960, 540);
}

surface_set_target(surf);
draw_clear_alpha(c_black, 0);
// ... dibujar ...
surface_reset_target();

draw_surface(surf, 0, 0);

// Clean Up event
if (surface_exists(surf))
{
    surface_free(surf);
    surf = -1;
}
```

> 💡 Las surfaces son **volátiles**: pueden destruirse si la ventana pierde el foco (Alt+Tab en Windows, una llamada en Android). Por eso el patrón es «comprobar y recrear» en el Draw, no «crear una vez en el Create».

### Caso 4: buffers

```gml
// Create
buff = -1;
buff = buffer_create(1024, buffer_grow, 1);

// Clean Up
if (buffer_exists(buff))
{
    buffer_delete(buff);
    buff = -1;                      // ← el manual lo recomienda explícitamente
}
```

> El manual de Buffers lo dice: *«After the buffer is destroyed, we recommend that you set the variable that holds a buffer reference to -1.»*

### Caso 5: pasar assets como argumentos

```gml
// ───────── ANTES: pasabas el número ─────────
crear_enemigo(3);   // ¿el objeto 3? ¿qué objeto es?

// ───────── DESPUÉS: pasas el handle ─────────
crear_enemigo(obj_slime);   // inequívoco, legible, con tipo
```

### Caso 6: Time Sources (nuevos en 2022+, alternativa moderna a alarms)

```gml
// Create
ts_disparo = -1;

// Al disparar
ts_disparo = time_source_create(
    time_source_game,
    0.25,
    time_source_units_seconds,
    function() { puedo_disparar = true; }
);
time_source_start(ts_disparo);

// Clean Up
if (time_source_exists(ts_disparo))
{
    time_source_destroy(ts_disparo);
    ts_disparo = -1;
}
```

---

## 8. Errores de audio: un caso donde los handles se notan

La documentación de audio es explícita sobre cómo se comportan los handles inválidos:

- Cualquier función que recibe un **Sound Asset** o un **Audio Sync Group ID** lanza un **error fatal** (crashea el juego) si le pasas un handle inválido.
- Las funciones que reciben un **Sound Instance ID** solo **imprimen un mensaje** en el Output Log; no crashean.
- Las operaciones inválidas (por ejemplo, grabar con un dispositivo ya activo) lanzan error fatal.

Puedes cambiar el comportamiento:

```gml
audio_throw_on_error(true);
// Ahora los errores fatales solo se registran en el log y el juego continúa
// ⚠️ El efecto del error puede seguir causando bugs, pero no crashea
```

---

## 9. Checklist de migración para un proyecto antiguo

Recorre tu código buscando estos patrones:

```
[ ] ds_*_create()  → variable sin inicializar a -1
[ ] surface_create() → sin surface_exists() antes de usar
[ ] buffer_create() → variable no reseteada a -1 tras buffer_delete()
[ ] with() sin comprobar noone antes
[ ] Comparaciones tipo: if (mi_lista) / if (mi_lista >= 0) / if (mi_lista > 0)
[ ] Comparaciones de instancia tipo: if (enemigo) / if (enemigo > 0)
[ ] Aritmética con IDs: id + 1, id * 2
[ ] IDs hardcodeados: ds_map_add(2, ...), sprite_get_width(3)
[ ] Handles serializados en JSON de guardado
[ ] Variables declaradas como 0 que deberían ser -1 o noone
```

### La sustitución de comparaciones, en tabla

| ❌ Legacy | ✅ 2026 |
|---|---|
| `if (lista)` | `if (lista != -1)` |
| `if (lista >= 0)` | `if (lista != -1)` |
| `if (instancia)` | `if (instancia != noone)` |
| `if (instancia > 0)` | `if (instancia != noone)` |
| `if (id != 0)` | `if (id != noone)` |
| `lista = 0;` (init) | `lista = -1;` |
| `enemigo = 0;` (init) | `enemigo = noone;` |

---

## 10. Resumen en cinco frases

1. Un **handle** es un int64: **32 bits de tipo + 32 bits de índice**.
2. Permite a GameMaker **detectar que le pasas el recurso equivocado** a una función.
3. Un handle inválido vale **`-1`**, o **`noone` (-4)** si es de instancia. Compruébalo siempre.
4. **Los índices se reciclan**: resetea la variable a `-1` / `noone` después de destruir el recurso.
5. Por compatibilidad, las funciones **siguen aceptando números pelados**… así que la disciplina es tuya: **solo pases handles**.

### Y la trampa que más duele

```gml
with (-1) { ... }   // NO se salta: se ejecuta sobre self
```
Porque `-1` es el valor legacy de `self`. De ahí que la comprobación explícita `!= noone` / `!= -1` sea **obligatoria**, no opcional.
