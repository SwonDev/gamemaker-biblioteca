# 08 — Texturas y grupos de texturas

> Referencia completa de GML para **GameMaker LTS 2026.0** (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Áreas: `Drawing/Textures/`, `Asset_Management/Sprites/Sprite_Information/` y
> `Asset_Management/Sprites/Sprite_Manipulation/`.
> **33 funciones documentadas.**

---

## Índice

1. [Qué es una textura](#qué-es-una-textura)
2. [Información de páginas de textura](#información-de-páginas-de-textura)
3. [Gestión de VRAM](#gestión-de-vram)
4. [Depuración](#depuración)
5. [Texturas dinámicas y grupos](#texturas-dinámicas-y-grupos)
6. [Caché de sprites](#caché-de-sprites)
7. [Tabla resumen](#tabla-resumen)
8. [Fuentes](#fuentes)

---

## Qué es una textura

En GameMaker, el término **textura** se refiere a las imágenes almacenadas en **VRAM** para
usarlas como sprites u otros elementos gráficos. Concretamente, son texturas:

- Las **páginas de textura** (*texture pages*) creadas por GameMaker, que contienen:
  - Sprites que añades a **grupos de textura** o que pones en una *Separate Texture Page*
  - Glifos de **fuentes**
  - **Tile sets**
- Las **superficies**: texturas personalizadas que proporcionan un lienzo donde puedes dibujar
  cualquier cosa (ver archivo **05**)

Entender esto es clave: cuando pides la textura de un sprite, en realidad estás obteniendo un
puntero a la **página de textura completa** en la que vive ese sprite, no al sprite aislado.

---

## Información de páginas de textura

### `sprite_get_texture(sprite, subimage)`
- **Devuelve:** `Texture`
- **Qué hace:** devuelve la textura de la página de textura en la que está el subimage indicado.
- **Ejemplo:**
```gml
// Pasar un sprite a un shader como sampler
var _tex = sprite_get_texture(spr_ruido, 0);
texture_set_stage(shader_get_sampler_index(sh_agua, "s_ruido"), _tex);

// O dibujarlo como primitiva
draw_primitive_begin_texture(pr_trianglestrip, _tex);
```
- **Notas / trampas:** devuelve la **página completa**, así que para mapear el sprite necesitas
  también sus UV (`sprite_get_uvs`).

### `sprite_get_uvs(sprite, subimage)`
- **Devuelve:** `Array`
- **Qué hace:** devuelve las coordenadas UV del sprite dentro de su página de textura.
- **Ejemplo:**
```gml
var _uv = sprite_get_uvs(spr_jugador, 0);
var _umin = _uv[0], _vmin = _uv[1], _umax = _uv[2], _vmax = _uv[3];
```
- **Notas / trampas:** imprescindible con **vertex buffers**, donde `(0,0)`–`(1,1)` cubre la página
  completa (ver archivo **07**).

### `sprite_get_tpe(sprite, subimage)`
- **Devuelve:** `Array`
- **Qué hace:** devuelve la entrada de la página de textura (*Texture Page Entry*) del subimage
  indicado.
- **Ejemplo:**
```gml
var _tpe = sprite_get_tpe(spr_enemigo, 0);
```
- **Notas / trampas:** función de bajo nivel; úsala para inspección avanzada de cómo GameMaker ha
  empaquetado el sprite.

### `texture_get_width(tex)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve la anchura de la página de textura en píxeles.
- **Ejemplo:**
```gml
var _ancho = texture_get_width(sprite_get_texture(spr_fondo, 0));
```

### `texture_get_height(tex)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve la altura de la página de textura en píxeles.
- **Ejemplo:**
```gml
var _alto = texture_get_height(surface_get_texture(surf));
```

### `texture_get_texel_width(tex)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve la anchura de **un texel** (un píxel de textura) expresada como fracción de
  la textura: `1 / anchura`.
- **Ejemplo:**
```gml
// Esencial para shaders que miran píxeles vecinos (outline, blur, sobel)
var _tex = sprite_get_texture(sprite_index, image_index);
shader_set_uniform_f(u_texel, texture_get_texel_width(_tex),
                              texture_get_texel_height(_tex));
```

### `texture_get_texel_height(tex)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve la altura de un texel como fracción: `1 / altura`.
- **Ejemplo:**
```gml
var _th = texture_get_texel_height(surface_get_texture(application_surface));
```

### `texture_get_uvs(texid)`
- **Devuelve:** `Array` de **4 a 8 elementos**
- **Qué hace:** devuelve las coordenadas UV de la textura en su página.
- **Ejemplo:**
```gml
var _uv = texture_get_uvs(sprite_get_texture(spr_baldosa, 0));
```
- **Notas / trampas:** el número de elementos puede variar (de 4 a 8) según la información
  disponible.

### `texture_set_stage(stage, tex)`
- **Devuelve:** `N/A`
- **Qué hace:** asigna una textura a un «slot» (sampler) de shader.
- **Ejemplo:**
```gml
var _sampler = shader_get_sampler_index(sh_disolver, "s_ruido");
texture_set_stage(_sampler, sprite_get_texture(spr_ruido, 0));
```
- **Notas / trampas:** `stage` puede ser un handle de sampler de shader **o un número real**.

### `texture_global_scale(pow2integer)`
- **Devuelve:** `N/A`
- **Qué hace:** escala **todas** las imágenes del juego por el factor indicado, que debe ser una
  **potencia de 2**: `1` = sin escala, `2` = mitad de tamaño, `4` = cuarta parte, etc.
- **Ejemplo:**
```gml
// Reducir el uso de VRAM a la cuarta parte en dispositivos con poca memoria
if (os_device == os_android) texture_global_scale(2);
```
- **Notas / trampas:**
  - Es una función **global y destructiva en calidad**: afecta a todas las imágenes.
  - Úsala en dispositivos con poca VRAM. Las imágenes escaladas pierden detalle al ampliarse.

---

## Gestión de VRAM

### `texture_prefetch(tex_id)`
- **Devuelve:** `N/A`
- **Qué hace:** carga una textura en VRAM **de forma anticipada**. Acepta un puntero de página de
  textura **o el nombre de un grupo de texturas** (cadena).
- **Ejemplo:**
```gml
// Precargar durante la pantalla de carga
texture_prefetch(sprite_get_texture(spr_boss, 0));
texture_prefetch("tg_Nivel3");
```
- **Notas / trampas:** evita tirones la primera vez que se dibuja una textura grande.

### `texture_flush(tex_id)`
- **Devuelve:** `N/A`
- **Qué hace:** libera de VRAM la textura o el grupo de texturas indicado. Acepta puntero de página
  de textura **o nombre de grupo** (cadena).
- **Ejemplo:**
```gml
// Al salir del nivel 3, liberamos su memoria
texture_flush("tg_Nivel3");
```
- **Notas / trampas:** los datos se recargarán automáticamente desde RAM la próxima vez que se
  necesiten.

### `sprite_prefetch(ind)`
- **Devuelve:** `Real` (`-1` o `0`)
- **Qué hace:** carga en VRAM el sprite indicado de forma anticipada.
- **Ejemplo:**
```gml
// Precargar los sprites del jefe antes del combate
sprite_prefetch(spr_boss);
sprite_prefetch(spr_boss_disparo);
```

### `sprite_prefetch_multi(array)`
- **Devuelve:** `Real` (`-1` o `0`)
- **Qué hace:** carga en VRAM **varios sprites** de golpe, pasando un array de sprites.
- **Ejemplo:**
```gml
var _sprites = [spr_boss, spr_boss_disparo, spr_boss_escudo, spr_explosion];
sprite_prefetch_multi(_sprites);
```
- **Notas / trampas:** más eficiente que muchas llamadas individuales a `sprite_prefetch`.

### `sprite_flush(ind)`
- **Devuelve:** `Real` (`-1` o `0`)
- **Qué hace:** libera de VRAM el sprite indicado.
- **Ejemplo:**
```gml
// Liberar sprites que ya no se usarán en este nivel
sprite_flush(spr_jefe_derrotado);
```

### `sprite_flush_multi(array)`
- **Devuelve:** `Real` (`-1` o `0`)
- **Qué hace:** libera de VRAM varios sprites de golpe.
- **Ejemplo:**
```gml
var _a_liberar = [spr_nivel1_a, spr_nivel1_b, spr_nivel1_c];
sprite_flush_multi(_a_liberar);
```

### `draw_texture_flush()`
- **Devuelve:** `N/A`
- **Qué hace:** vacía la caché de texturas del pipeline de dibujo.
- **Ejemplo:**
```gml
draw_texture_flush();
```
- **Notas / trampas:** función de muy bajo nivel; úsala solo si sabes lo que haces, normalmente
  junto a `draw_flush()` en depuración.

---

## Depuración

### `texture_debug_messages(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva los **mensajes de depuración de texturas**. Con ellos activados,
  GameMaker informa por consola de las operaciones de carga y descarga de páginas de textura.
- **Ejemplo:**
```gml
// Activar al arrancar en modo depuración
if (debug_mode) texture_debug_messages(true);
```
- **Notas / trampas:** el manual indica que estas funciones son **principalmente para depurar el
  proyecto y asegurar un uso eficiente de la memoria de textura**.

### `texture_is_ready(tex_id)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la textura (o el grupo de texturas, si pasas una cadena) está **lista para
  usarse**, es decir, ya cargada y preparada en VRAM.
- **Ejemplo:**
```gml
// Esperar a que un grupo dinámico esté listo antes de empezar el nivel
if (texture_is_ready("tg_Nivel3"))
{
    room_goto(rm_nivel3);
}
else
{
    show_debug_message("Cargando texturas del nivel 3...");
}
```

### `texturegroup_get_textures(tex_id)`
- **Devuelve:** `Array` de `Texture`
- **Qué hace:** devuelve un array con las texturas del grupo indicado (nombre como cadena).
- **Ejemplo:**
```gml
var _texturas = texturegroup_get_textures("tg_UI");
show_debug_message($"El grupo UI tiene {array_length(_texturas)} texturas");
```

### `texturegroup_get_sprites(tex_id)`
- **Devuelve:** `Array` de `Sprite Asset`
- **Qué hace:** devuelve los sprites contenidos en el grupo.
- **Ejemplo:**
```gml
var _sprites = texturegroup_get_sprites("tg_Enemigos");
```

### `texturegroup_get_fonts(tex_id)`
- **Devuelve:** `Array` de `Font Asset`
- **Qué hace:** devuelve las fuentes contenidas en el grupo.
- **Ejemplo:**
```gml
var _fuentes = texturegroup_get_fonts("tg_UI");
```
- **Notas / trampas:** útil porque **las fuentes no admiten mipmapping**: si activas mipmapping en un
  grupo con fuentes, tendrás glifos corruptos.

### `texturegroup_get_tilesets(tex_id)`
- **Devuelve:** `Array` de `Tile Set Asset`
- **Qué hace:** devuelve los tile sets contenidos en el grupo.
- **Ejemplo:**
```gml
var _tilesets = texturegroup_get_tilesets("tg_Mundo");
```

### `texturegroup_get_names()`
- **Devuelve:** `Array`
- **Qué hace:** devuelve los nombres de **todos** los grupos de textura del proyecto.
- **Ejemplo:**
```gml
var _grupos = texturegroup_get_names();
for (var _i = 0; _i < array_length(_grupos); _i++)
{
    show_debug_message($"Grupo: {_grupos[_i]}");
}
```

---

## Texturas dinámicas y grupos

Los grupos de textura pueden cargarse y descargarse en caliente, lo que permite gestionar la memoria
de juegos grandes por zonas.

### Estados de un grupo de textura

| Constante | Valor | Significado |
|---|---|---|
| `texturegroup_status_unloaded` | 0 | El grupo está **en disco**, no en memoria |
| `texturegroup_status_loading` | 1 | El grupo se está **cargando desde disco** |
| `texturegroup_status_loaded` | 2 | El grupo se ha cargado en **RAM** |
| `texturegroup_status_fetched` | 3 | El grupo se ha cargado **y enviado a VRAM**, listo para usarse |

### `texturegroup_load(groupname, [prefetch=true])`
- **Devuelve:** `Real`
- **Qué hace:** carga un grupo de textura en memoria.
- **Argumento `prefetch` (opcional):**
  - `true` (**por defecto**): el grupo se **descomprime y envía a VRAM**.
  - `false`: solo se carga en **RAM**, permaneciendo comprimido.
- **Ejemplo:**
```gml
// Cargar el nivel siguiente en segundo plano solo en RAM (más rápido, menos VRAM)
texturegroup_load("tg_Nivel4", false);

// ...y cuando estemos a punto de entrar, enviarlo a VRAM
texturegroup_load("tg_Nivel4", true);
```
- **Notas / trampas:** usa `prefetch = false` para precargar sin disparar el consumo de VRAM, y
  `true` justo antes de necesitarlo.

### `texturegroup_unload(groupname)`
- **Devuelve:** `N/A`
- **Qué hace:** descarga un grupo de textura de la memoria.
- **Ejemplo:**
```gml
// Al terminar el nivel 1, liberamos su grupo
texturegroup_unload("tg_Nivel1");
```
> ⚠️ **Si nunca llamas a `texturegroup_unload()`, el grupo se queda en VRAM el resto de la
> partida.** No hay una recogida automática equivalente al GC de structs/arrays
> ([`01 · 15 §5`](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#5-el-garbage-collector-recolector-de-basura)):
> un grupo cargado con `texturegroup_load()` sigue en memoria aunque ya no dibujes ningún sprite
> que pertenezca a él, hasta que tú mismo pidas descargarlo.

### `texturegroup_get_status(groupname)`
- **Devuelve:** constante de estado de grupo de textura
- **Qué hace:** devuelve el estado actual del grupo (ver tabla de estados).
- **Ejemplo:**
```gml
// Pantalla de carga: esperar a que el grupo esté listo
var _estado = texturegroup_get_status("tg_Nivel3");

switch (_estado)
{
    case texturegroup_status_unloaded:
        texturegroup_load("tg_Nivel3", true);
        break;

    case texturegroup_status_loading:
        // seguir mostrando la barra de progreso
        break;

    case texturegroup_status_loaded:
        show_debug_message("En RAM, enviando a VRAM...");
        break;

    case texturegroup_status_fetched:
        room_goto(rm_nivel3);   // ¡listo!
        break;
}
```

### `texturegroup_add(groupname, filename_or_buffer_or_array, struct_or_json)`
- **Devuelve:** `N/A`
- **Qué hace:** añade un grupo de textura **en tiempo de ejecución** desde archivos externos.
- **Argumentos:**
  - `groupname`: nombre del grupo de textura.
  - `filename_or_buffer_or_array`: un **nombre de archivo**, un **buffer** o un **array** con una
    combinación de ambos, con los datos a cargar.
  - `struct_or_json`: un **struct** o una **cadena JSON** que describe los datos de los sprites.
- **Ejemplo:**
```gml
// Cargar un pack de texturas descargado como DLC
var _archivos = ["dlc_texturas.png", "dlc_texturas.yy"];
// ⚠️ `sprites` es un STRUCT cuyas claves son los nombres de los sprites, NO un array.
// Cada sprite lleva su array `frames`. Formato verificado contra el manual (texturegroup_add).
var _datos = @'{"sprites": {"spr_dlc_arbol": {"width": 64, "height": 64, "frames": [{"x": 0, "y": 0, "w": 64, "h": 64}]}}}';

texturegroup_add("tg_DLC", _archivos, _datos);

if (texturegroup_get_status("tg_DLC") == texturegroup_status_fetched)
{
    show_debug_message("DLC de texturas cargado");
}
```
- **Notas / trampas:** es la puerta de entrada para contenido descargable y *modding* con assets
  gráficos propios.

### `texturegroup_delete(groupname)`
- **Devuelve:** `N/A`
- **Qué hace:** elimina un grupo de textura.
- **Ejemplo:**
```gml
texturegroup_delete("tg_DLC");
```

### `texturegroup_exists(groupname)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si existe un grupo de textura con ese nombre.
- **Ejemplo:**
```gml
if (texturegroup_exists("tg_DLC")) texturegroup_unload("tg_DLC");
```

### `texturegroup_set_mode(groupname, mode)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el modo de un grupo de textura (relacionado con la carga dinámica: si el grupo
  se carga al arrancar o bajo demanda).
- **Ejemplo:**
```gml
// Configurar un grupo como dinámico para cargarlo solo cuando se pida
texturegroup_set_mode("tg_Nivel5", true);
```

---

## Caché de sprites

### `sprite_set_cache_size(ind, max)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el número **máximo de copias cacheadas** del sprite que pueden almacenarse antes
  de sobrescribir las antiguas.
- **Ejemplo:**
```gml
// Limitar la caché de un sprite que se tiñe de muchos colores
sprite_set_cache_size(spr_enemigo, 8);
```
- **Notas / trampas:**
  - Necesario porque **HTML5 no puede hacer mezcla de color dinámica** como un ejecutable:
    GameMaker guarda una copia mezclada de la imagen y la carga cuando hace falta.
  - Para fuentes existe la equivalente `font_set_cache_size()` (ver archivo **03**).

### `sprite_set_cache_size_ext(ind, index, max)`
- **Devuelve:** `N/A`
- **Qué hace:** igual que `sprite_set_cache_size` pero para un **subimage concreto** del sprite.
- **Ejemplo:**
```gml
// Solo el frame 0 se tiñe mucho: le damos más caché
sprite_set_cache_size_ext(spr_enemigo, 0, 16);
```

---

## Tabla resumen

### Información de páginas de textura (9)

| Función | Devuelve |
|---|---|
| `sprite_get_texture(sprite, subimage)` | `Texture` |
| `sprite_get_uvs(sprite, subimage)` | `Array` |
| `sprite_get_tpe(sprite, subimage)` | `Array` |
| `texture_get_width(tex)` | `Real` |
| `texture_get_height(tex)` | `Real` |
| `texture_get_texel_width(tex)` | `Real` |
| `texture_get_texel_height(tex)` | `Real` |
| `texture_get_uvs(texid)` | `Array` (4–8) |
| `texture_set_stage(stage, tex)` | `N/A` |

### Gestión de VRAM (8)

| Función | Devuelve |
|---|---|
| `texture_prefetch(tex_id)` | `N/A` |
| `texture_flush(tex_id)` | `N/A` |
| `texture_global_scale(pow2integer)` | `N/A` |
| `sprite_prefetch(ind)` | `Real` (−1 o 0) |
| `sprite_prefetch_multi(array)` | `Real` (−1 o 0) |
| `sprite_flush(ind)` | `Real` (−1 o 0) |
| `sprite_flush_multi(array)` | `Real` (−1 o 0) |
| `draw_texture_flush()` | `N/A` |

### Depuración (6)

| Función | Devuelve |
|---|---|
| `texture_debug_messages(enable)` | `N/A` |
| `texture_is_ready(tex_id)` | `Boolean` |
| `texturegroup_get_textures(tex_id)` | `Array` de `Texture` |
| `texturegroup_get_sprites(tex_id)` | `Array` de `Sprite Asset` |
| `texturegroup_get_fonts(tex_id)` | `Array` de `Font Asset` |
| `texturegroup_get_tilesets(tex_id)` | `Array` de `Tile Set Asset` |
| `texturegroup_get_names()` | `Array` |

### Texturas dinámicas y grupos (7)

| Función | Devuelve |
|---|---|
| `texturegroup_load(groupname, [prefetch])` | `Real` |
| `texturegroup_unload(groupname)` | `N/A` |
| `texturegroup_add(groupname, archivo/buffer/array, struct/json)` | `N/A` |
| `texturegroup_delete(groupname)` | `N/A` |
| `texturegroup_exists(groupname)` | `Boolean` |
| `texturegroup_set_mode(groupname, mode)` | `N/A` |
| `texturegroup_get_status(groupname)` | Constante de estado |

### Caché de sprites (2)

| Función | Devuelve |
|---|---|
| `sprite_set_cache_size(ind, max)` | `N/A` |
| `sprite_set_cache_size_ext(ind, index, max)` | `N/A` |

**Total: 33 funciones documentadas.**

> **Nota:** el manual no documenta ninguna función `texture_page_size` ni `texture_page_sizes` como
> función GML. El tamaño de las páginas de textura se configura en las **Game Options → Graphics** y
> en el **Texture Group Editor**, no por código. Para el caso concreto de fuentes sí existe la
> variable integrada `font_texture_page_size` (ver archivo **03**).

---

## Fuentes

- Textures — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/Textures.htm
- `texture_get_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_width.htm
- `texture_get_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_height.htm
- `texture_get_texel_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_texel_width.htm
- `texture_get_texel_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_texel_height.htm
- `texture_get_uvs` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_uvs.htm
- `texture_set_stage` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_set_stage.htm
- `texture_global_scale` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_global_scale.htm
- `texture_prefetch` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_prefetch.htm
- `texture_flush` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_flush.htm
- `texture_is_ready` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_is_ready.htm
- `texture_debug_messages` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_debug_messages.htm
- `draw_texture_flush` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/draw_texture_flush.htm
- `texturegroup_load` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_load.htm
- `texturegroup_unload` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_unload.htm
- `texturegroup_add` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_add.htm
- `texturegroup_delete` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_delete.htm
- `texturegroup_exists` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_exists.htm
- `texturegroup_set_mode` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_set_mode.htm
- `texturegroup_get_status` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_get_status.htm
- `texturegroup_get_textures` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_get_textures.htm
- `texturegroup_get_sprites` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_get_sprites.htm
- `texturegroup_get_fonts` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_get_fonts.htm
- `texturegroup_get_tilesets` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_get_tilesets.htm
- `texturegroup_get_names` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_get_names.htm
- `sprite_get_texture` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Information/sprite_get_texture.htm
- `sprite_get_uvs` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Information/sprite_get_uvs.htm
- `sprite_get_tpe` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Information/sprite_get_tpe.htm
- `sprite_prefetch` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_prefetch.htm
- `sprite_prefetch_multi` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_prefetch_multi.htm
- `sprite_flush` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_flush.htm
- `sprite_flush_multi` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_flush_multi.htm
- `sprite_set_cache_size` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_set_cache_size.htm
- `sprite_set_cache_size_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_set_cache_size_ext.htm
