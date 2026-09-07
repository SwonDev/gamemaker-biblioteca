# 10 · Rooms, capas, cámaras y viewports

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Rooms.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/General_Layer_Functions/General_Layer_Functions.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/Tile_Map_Layers.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Viewports/Cameras_And_View_Ports.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/The_Asset_Browser.htm> (tipos de asset)

---

## 1. Qué es una room

**Una room es donde ocurre todo.** Todo juego de GameMaker necesita **al menos una room** para poder ejecutarse. Los proyectos nuevos ya traen una creada.

Las rooms se crean en el **Room Editor**, o en runtime con las funciones de *Modifying Rooms*.

### Herencia de rooms

Las rooms pueden **heredar** propiedades de otras: puedes crear una room con un montón de tiles y luego hacer otra room que **herede** esas propiedades sin tener que recrearlas.

En el Asset Browser: clic derecho sobre una room → **Create Child Room**.
Las rooms hijas aparecen vinculadas a la padre en el **Room Manager**.

### Variables y funciones globales

| Elemento | Notas |
|---|---|
| `room` | La room actual |
| `room_first` / `room_last` | Primera y última de la lista |
| `room_next` / `room_previous` | Siguiente / anterior (según el orden del Asset Browser) |
| `room_width` / `room_height` | Tamaño |
| `room_persistent` | ¿Es persistente? |
| `room_speed` | ⚠️ **DEPRECADA** — usa `game_set_speed()` / `game_get_speed()` |

> ⚠️ **Estas variables NO son válidas en la raíz de un script**, porque los scripts se ejecutan antes de cargar la primera room. Sí funcionan dentro de funciones definidas en scripts, porque esas se ejecutan cuando tú quieras.

### Información

```gml
room_exists(room);
room_get_name(room);
room_get_info(room);
```

---

## 2. Navegar entre rooms

```gml
room_goto(room);          // ir a una room concreta
room_goto_next();         // siguiente en la lista
room_goto_previous();     // anterior
room_restart();           // reiniciar la actual
```

### ⚠️ `room_goto()` no es instantáneo... y tiene una trampa

La room **no cambia inmediatamente**. Si creas instancias justo después de llamar a `room_goto()` **en el mismo evento**, se crearán en la room **nueva**, no en la actual.

```gml
// ⚠️ Esto crea la instancia en la NUEVA room
room_goto(rm_nivel_2);
instance_create_layer(100, 100, "Instances", obj_jugador);

// ✅ Orden correcto
instance_create_layer(100, 100, "Instances", obj_jugador);
room_goto(rm_nivel_2);
```

### Persistencia

```gml
room_persistent = true;      // la room recuerda su estado al volver
room_set_persistent(room, true);
```

> ⚠️ Las instancias dentro de rooms no persistentes **se destruyen** al salir. Para que una instancia sobreviva, usa `persistent = true` en la instancia.

> 💡 **Por qué `room_goto()` puede doler con muchas instancias.** Esa destrucción de arriba no es
> gratis: al salir de una room no persistente, GameMaker recorre y destruye **cada instancia no
> persistente** que hubiera en ella (Destroy → Clean Up de cada una, como en
> [`01 · 09` §4](./09%20-%20Instancias%2C%20objetos%20y%20herencia.md#4-destruir-instancias)), y al entrar en la nueva room **crea**
> todas las instancias colocadas en el editor y ejecuta su Room Creation Code. Con unas pocas
> decenas de instancias no se nota; con varios miles (una room de mundo abierto muy poblada, un
> editor de niveles con generación procedural pesada) ese barrido de destrucción + creación es un
> pico de trabajo real en el frame en que ocurre — es la misma familia de coste que
> [`01 · 15 §6 Paso 2`](./15%20-%20Depuración%20y%20rendimiento.md#paso-2-los-sospechosos-habituales)
> describe para crear/destruir objetos sueltos, multiplicado por «toda la room a la vez». Si el
> tirón se nota, la pantalla de carga real de
> [`04 · 41 §3.3`](../04%20-%20Recetas%20por%20género/41%20-%20Transiciones%2C%20carga%20y%20pausa.md#33-la-pantalla-de-carga-real)
> es donde ese coste se absorbe sin que se vea como un frame congelado.

### Modificar rooms (con cuidado)

```
room_add()                 room_duplicate()          room_assign()
room_instance_add()        room_instance_clear()
room_set_width()           room_set_height()
room_set_persistent()      room_set_view_enabled()
room_set_viewport()        room_get_viewport()
room_set_camera()          room_get_camera()
```

> ⚠️ **Nunca ejecutes estas funciones desde la room que quieres cambiar.** Hazlo desde una instancia de otra room.
> ⚠️ Los cambios son **permanentes** durante toda la ejecución, incluso si llamas a `room_restart()`. Solo cerrar y reabrir el juego los resetea.

---

## 3. Capas (Layers)

Todo lo que añades a una room va sobre una **capa**.

### Para qué sirven las capas

1. **Agrupan lógicamente** los assets.
2. **Afectan al dibujado:**
   - con un desplazamiento (x, y) y una velocidad,
   - a una profundidad (`layer_depth`),
   - con código personalizado (`layer_script_begin` / `layer_script_end`) y shader (`layer_shader`).

### Tipos de elemento por capa

| Tipo de capa | Contenido |
|---|---|
| **Instances** | Instancias de objetos |
| **Tiles** | Tile maps (a partir de tile sets) |
| **Background** | Imágenes de fondo |
| **Assets** | Sprites y secuencias |
| **Paths** | ⚠️ No añaden ningún elemento |
| **Effects** | Filtros y efectos |
| **UI** | Capas de interfaz (Flex Panels) |
| **Text** | Elementos de texto |
| **Particle System** | Sistemas de partículas |

> ⚠️ **En el Room Editor estás limitado a un tile map por capa** (se crea al añadir una Tile Layer). **En código puedes tener varios tile maps en la misma capa.**

### ⚠️ Novedad: en código puedes mezclar tipos en una capa

> *«you can have multiple different element types on one layer.»*

En el Room Editor no se permite, pero al crear cosas dinámicamente sí:

```gml
var _capa = layer_create(-100, "MiCapaMixta");
// Un fondo, un tile map y una instancia... ¡todo en la misma capa!
```

Por eso existe `layer_get_all_elements()`.

### Obtener capas

```gml
var _todas = layer_get_all();              // array con los handles de todas
var _capa  = layer_get_id("Suelo");        // por nombre del Room Editor
```

### Funciones principales

```
layer_exists / layer_get_id / layer_get_depth / layer_get_type
layer_get_id_at_depth / layer_get_name / layer_get_all
layer_get_all_elements / layer_get_element_layer / layer_get_element_type
layer_create(depth, [nombre]) / layer_destroy(capa)
layer_x / layer_y / layer_hspeed / layer_vspeed
layer_get_x / layer_get_y / layer_get_hspeed / layer_get_vspeed
layer_add_instance / layer_has_instance / layer_instance_get_instance
layer_destroy_instances / layer_element_move
layer_set_visible / layer_get_visible
layer_depth / layer_force_draw_depth
layer_script_begin / layer_script_end / layer_shader
```

### Capas en OTRA room

```gml
layer_set_target_room(rm_otra);
// ...todas las funciones de capa aplican a rm_otra...
layer_reset_target_room();
```

> ⚠️ **Mientras apuntas a otra room NO puedes** usar `instance_create_layer()`, `instance_create_depth()` ni `layer_add_instance()`.

### Activar / desactivar instancias por capa

```gml
instance_deactivate_layer(capa);
instance_activate_layer(capa);
```

> Solo afecta a las **instancias** de la capa, aunque la capa tenga otros elementos.

### Ejemplo: parallax con capas

```gml
// Create del controlador
capa_fondo_lejano = layer_get_id("Fondo_Lejano");
capa_fondo_cercano = layer_get_id("Fondo_Cercano");

// Step
var _cam_x = camera_get_view_x(view_camera[0]);

layer_x(capa_fondo_lejano,  _cam_x * 0.2);   // se mueve poco → lejos
layer_x(capa_fondo_cercano, _cam_x * 0.6);   // se mueve más  → cerca
```

---

## 4. Tile maps y tile sets

### La cadena de conceptos

| Concepto | Qué es |
|---|---|
| **Tile set** | El asset: una imagen partida en celdas |
| **Tile layer** | Lo que creas en el Room Editor para añadir tile sets |
| **Tile map** | La colección de tiles añadida a una capa, como **un único elemento** |

### El «blob» de datos de tile

Cada celda guarda un valor de **32 bits**:

```
bits 0-18   → índice del tile en el tile set (19 bits)
bits 19-27  → sin usar (puedes usarlos tú)
bit 28      → mirror
bit 29      → flip
bit 30      → rotate
bit 31      → sin usar
```

Constantes de máscara:

```gml
tile_rotate        tile_mirror       tile_flip
tile_index_mask    // para extraer los 19 bits del índice
```

```gml
// Leer y manipular un tile
var _datos = tilemap_get(mi_tilemap, celda_x, celda_y);
var _indice = _datos & tile_index_mask;
var _es_espejo = (_datos & tile_mirror) != 0;

// Rotarlo
_datos = tile_set_rotate(_datos, true);
tilemap_set(mi_tilemap, _datos, celda_x, celda_y);
```

### Máscara de bits personalizada

Puedes usar los bits libres para **tus propios datos** (por ejemplo, marcar celdas como «venenosa» o «ruidosa»).

- Se aplica con `&` al **dibujar** el tile map: los bits fuera de la máscara se ignoran visualmente, pero puedes leerlos y escribirlos.
- Hay una máscara **por tilemap** (`tilemap_set_mask`) y una **global** (`tilemap_set_global_mask`). Se combinan con `&` internamente.

**Cómo calcularla:** tomas el número de tiles del tile set y le restas 1.
- Un tile set de 16×16 = 256 tiles → máscara `255` (`$ff`).
- Si el número no es potencia de 2, redondea hacia arriba: 20×20 = 400 → redondea a 512 → máscara `511` (`$1ff`).

Combínala con las constantes para preservar flip/rotate/mirror:

```gml
var _mascara = 255 | tile_rotate | tile_mirror | tile_flip;
tilemap_set_mask(mi_tilemap, _mascara);
```

### Obtener el tile map

```gml
// Create event
mi_tilemap = layer_tilemap_get_id("Tiles_1");
```

### Funciones principales

```
layer_tilemap_get_id / layer_tilemap_exists / layer_tilemap_create
layer_tilemap_destroy / layer_tilemap_set_colmask / layer_tilemap_get_colmask

tilemap_tileset / tilemap_clear / tilemap_x / tilemap_y
tilemap_set / tilemap_set_at_pixel
tilemap_set_mask / tilemap_set_global_mask
tilemap_set_width / tilemap_set_height
tilemap_get_mask / tilemap_get_global_mask / tilemap_get_tileset
tilemap_get_frame / tilemap_get_tile_width / tilemap_get_tile_height
tilemap_get_width / tilemap_get_height / tilemap_get_x / tilemap_get_y
tilemap_get / tilemap_get_at_pixel
tilemap_get_cell_x_at_pixel / tilemap_get_cell_y_at_pixel

// Edición de tiles individuales
tile_get_empty / tile_get_index / tile_get_flip / tile_get_mirror / tile_get_rotate
tile_set_empty / tile_set_index / tile_set_flip / tile_set_mirror / tile_set_rotate

// Dibujo
draw_tilemap / draw_tile
```

### Colisiones con tile maps

```gml
// Create
tilemap = layer_tilemap_get_id("TileLayer");

// Step
if (!place_meeting(x + 4, y, tilemap)) { x += 4; }
```

**Requisitos (repetido porque es el error más común):**
1. El tile set debe tener **sprite asignado** con máscara de colisión válida.
2. La opción **«Disable Source Sprite Export»** del tile set debe estar **desactivada**.

> ⚠️ Un tile map con ID `0` existe y es válido. `instance_place()` sobre él devuelve `0`, que evaluaría como `false` si lo usas como booleano. **Compara siempre contra `noone`.**

---

## 5. Cámaras y viewports: aclarar los tres conceptos

> *«It's easy to get confused when talking about cameras, views and viewports.»*

| Concepto | Qué es |
|---|---|
| **Camera** | Se coloca en un punto de la room y define cómo se muestra: posición, tamaño, orientación (y en 3D, campo de visión y aspecto) |
| **View** | Lo que la cámara **ve**, según su posición, proyección y rotación. La vista se pasa al viewport para renderizarse en la application surface |
| **Viewport** | El área **de la pantalla** donde se muestra la vista de la cámara |

### Límites

- **8 viewports** independientes (numerados 0-7).
- **Cámaras ilimitadas**, pero solo **8 activas** a la vez (una por viewport).
- Normalmente solo necesitas **un** viewport.

> 💡 El viewport puede tener un tamaño **distinto** al de la vista de la cámara. Si no es 1:1, **escalas o distorsionas** la vista.

### El canvas size (importante)

> El área total de la bounding box de **todos los viewports activos en la PRIMERA room del juego** define el **canvas size** (o el tamaño de la ventana en Windows, macOS y Ubuntu).

Las zonas no cubiertas por un viewport se dibujan con el color de la ventana.

> ⚠️ Para que se vea ese color, debes activar **Clear Display Buffer** en el Room Editor. Y solo puedes fijar el color con `window_set_colour()`; si no lo haces, será negro.

### ⚠️ Rendimiento con múltiples cámaras

> Los eventos de dibujado normales (**Draw Begin**, **Draw**, **Draw End**) se llaman **una vez por cada vista visible**. Con tres cámaras activas, **el trabajo de dibujado se triplica**.

Solución: usa `view_current` para limitar qué dibujas en cada vista.

```gml
// Draw event
if (view_current == 0)
{
    // Solo dibuja en el viewport 0
    draw_self();
}
```

> ⚠️ **Si creas una cámara y no la destruyes con `camera_destroy()`, tendrás un memory leak.**

---

## 6. Variables globales de vistas

| Variable | Qué es |
|---|---|
| `view_camera[0..7]` | El **handle** de la cámara asignada a cada viewport |
| `view_enabled` | ¿Están activadas las vistas? |
| `view_visible[0..7]` | ¿Es visible ese viewport? |
| `view_xport[0..7]` / `view_yport[0..7]` | Posición del viewport en la pantalla |
| `view_wport[0..7]` / `view_hport[0..7]` | Tamaño del viewport |
| `view_surface_id[0..7]` | Surface a la que se dibuja ese viewport |
| `view_current` | Qué viewport se está dibujando ahora mismo |

### Funciones equivalentes

```
view_get_camera / view_set_camera
view_get_visible / view_set_visible
view_get_xport / view_set_xport      (y yport, wport, hport)
view_get_surface_id / view_set_surface_id
```

---

## 7. Crear y manipular cámaras

### Crear

```gml
camera_create();   // cámara vacía
camera_create_view(x, y, ancho, alto, [angulo], [objetivo],
                   [vel_x], [vel_y], [borde_x], [borde_y]);
```

```gml
// Create del controlador
mi_camara = camera_create_view(0, 0, 960, 540, 0, obj_jugador, 8, 8, 200, 150);
view_camera[0] = mi_camara;
```

### Destruir (¡obligatorio!)

```gml
// Clean Up / Room End
camera_destroy(mi_camara);
```

### Funciones de configuración

```
camera_set_view_pos(cam, x, y)          camera_set_view_size(cam, w, h)
camera_set_view_speed(cam, vx, vy)      camera_set_view_border(cam, bx, by)
camera_set_view_angle(cam, angulo)      camera_set_view_target(cam, instancia)
camera_set_update_script(cam, script)   camera_set_begin_script / end_script
camera_set_view_mat(cam, matriz)        camera_set_proj_mat(cam, matriz)
camera_set_default(cam)
camera_apply(cam)                       camera_copy_transforms(dest, origen)
```

Y sus `camera_get_*` equivalentes.

### Seguir al jugador manualmente (el patrón más común)

```gml
// ═══════════ obj_camara (End Step) ═══════════
// End Step: el jugador YA se ha movido
var _cam = view_camera[0];
var _vw  = camera_get_view_width(_cam);
var _vh  = camera_get_view_height(_cam);

// Posición deseada: centrada en el jugador
var _destino_x = obj_jugador.x - _vw / 2;
var _destino_y = obj_jugador.y - _vh / 2;

// Suavizado (interpolación lineal)
var _actual_x = camera_get_view_x(_cam);
var _actual_y = camera_get_view_y(_cam);

var _suavizado = 0.12;
var _nuevo_x = lerp(_actual_x, _destino_x, _suavizado);
var _nuevo_y = lerp(_actual_y, _destino_y, _suavizado);

// Limitar a los bordes de la room
_nuevo_x = clamp(_nuevo_x, 0, max(0, room_width  - _vw));
_nuevo_y = clamp(_nuevo_y, 0, max(0, room_height - _vh));

camera_set_view_pos(_cam, round(_nuevo_x), round(_nuevo_y));
```

> 💡 **`round()` al final** evita el «temblor» de píxeles en juegos pixel art.

> 💡 Ponlo en **End Step**, no en Step: así la cámara reacciona a la posición **ya actualizada** del jugador.

### Pantalla partida (split screen)

```gml
// Create del controlador
view_enabled = true;

// Viewport 0: mitad izquierda
view_set_visible(0, true);
view_set_xport(0, 0);
view_set_yport(0, 0);
view_set_wport(0, 480);
view_set_hport(0, 540);

// Viewport 1: mitad derecha
view_set_visible(1, true);
view_set_xport(1, 480);
view_set_yport(1, 0);
view_set_wport(1, 480);
view_set_hport(1, 540);

cam_j1 = camera_create_view(0, 0, 480, 540, 0, obj_jugador_1);
cam_j2 = camera_create_view(0, 0, 480, 540, 0, obj_jugador_2);

view_camera[0] = cam_j1;
view_camera[1] = cam_j2;
```

### Frustum culling

```gml
sphere_is_visible(x, y, z, radio);   // ¿está visible esa esfera?
gpu_set_sprite_cull(true);           // descartar sprites fuera de cámara
```

---

## 8. Viewports a surfaces

Puedes redirigir un viewport a una surface propia:

```gml
// Create
if (!surface_exists(surf_vista))
{
    surf_vista = surface_create(480, 270);
}
view_surface_id[0] = surf_vista;

// Ahora TODO lo que se vea en el viewport 0 se dibuja en surf_vista
// Puedes aplicarle un shader, escalarla, etc.

// Post-Draw
if (surface_exists(surf_vista))
{
    shader_set(sh_crt);
    draw_surface_stretched(surf_vista, 0, 0, 960, 540);
    shader_reset();
}

// Clean Up
if (surface_exists(surf_vista))
{
    surface_free(surf_vista);
    surf_vista = -1;
}
```

> 💡 Es la técnica estándar para juegos de **baja resolución escalados**: tu juego corre a 480×270 y lo estiras a pantalla completa con pixel-perfect.

---

## 9. Transiciones entre rooms

GameMaker no tiene un sistema de transiciones integrado, pero el patrón es sencillo con un objeto persistente:

```gml
// ═══════════ obj_transicion (persistente) ═══════════

// ─── Create ───
if (instance_number(obj_transicion) > 1)
{
    instance_destroy();
    exit;
}
persistent = true;

estado       = "idle";      // "idle" | "saliendo" | "entrando"
room_destino = noone;
alfa         = 0;
velocidad    = 0.05;

// ─── función pública ───
function ir_a(_room)
{
    if (estado != "idle") { return; }   // ya hay transición en curso

    estado       = "saliendo";
    room_destino = _room;
}

// ─── Step ───
switch (estado)
{
    case "saliendo":
        alfa += velocidad;
        if (alfa >= 1)
        {
            alfa = 1;
            room_goto(room_destino);    // ← el cambio real
            estado = "entrando";
        }
        break;

    case "entrando":
        alfa -= velocidad;
        if (alfa <= 0)
        {
            alfa   = 0;
            estado = "idle";
        }
        break;
}

// ─── Draw GUI (va encima de todo) ───
if (alfa > 0)
{
    draw_set_alpha(alfa);
    draw_set_colour(c_black);
    draw_rectangle(0, 0, display_get_gui_width(), display_get_gui_height(), false);
    draw_set_alpha(1);
}
```

**Uso desde cualquier parte:**

```gml
with (obj_transicion) { ir_a(rm_nivel_2); }
```

> 💡 **Draw GUI** garantiza que el fundido a negro tape **todo**, incluido el HUD.

> 🔺 Este fundido es la base mínima. Un repertorio completo de transiciones (wipe, cortinas,
> iris, disolución con shader y ruido) sobre esta misma máquina de tres estados, más la
> pantalla de carga real con `texturegroup_load`/`texturegroup_get_status` y el menú de pausa
> completo que debe congelar el mundo **antes** de que empiece cualquiera de estos efectos,
> están en
> [04 · 41 — Transiciones, carga y pausa](../04%20-%20Recetas%20por%20género/41%20-%20Transiciones,%20carga%20y%20pausa.md).

---

## 10. Fondos (Backgrounds)

Las capas de fondo son ideales para parallax y para imágenes grandes.

```gml
var _capa = layer_get_id("Fondo");
var _elem = layer_background_get_id(_capa);

layer_background_sprite(_elem, spr_fondo_montanas);
layer_background_xscale(_elem, 2);
layer_background_yscale(_elem, 2);
layer_background_htiled(_elem, true);    // repetir horizontalmente
layer_background_blend(_elem, c_gray);
layer_background_alpha(_elem, 0.8);
layer_background_speed(_elem, 2);        // scroll automático
```

### ⚠️ Rooms con scroll

Si activas el scroll de una room, recuerda: el tiempo que GameMaker dedica a procesar los fondos con scroll aparece en la sección **Scroll** del gráfico del Debug Overlay.

---

## 11. Filtros y efectos de capa

```gml
// Crear una capa de efectos y aplicarle un filtro
var _capa = layer_create(-1000, "Efectos");
layer_shader(_capa, sh_desenfoque);

// O scripts de inicio/fin de capa
layer_script_begin(_capa, function()
{
    gpu_set_blendmode(bm_add);
});

layer_script_end(_capa, function()
{
    gpu_set_blendmode(bm_normal);
});
```

> 💡 Los scripts de capa te permiten «inyectar» código antes y después de dibujar la capa. Es una forma limpia de aplicar configuraciones de dibujo por grupos.

---

## 12. Ejemplo completo: room de juego con capas, tiles y cámara

```gml
// ═══════════ obj_controlador_nivel (Create) ═══════════

// 1. Referencias a capas existentes en el Room Editor
capa_suelo  = layer_get_id("Suelo");
capa_fondo  = layer_get_id("Fondo");
capa_jug    = layer_get_id("Jugador");

// 2. Tile map de colisión (se cachea una vez)
tilemap_colision = layer_tilemap_get_id("Tiles_Colision");

// 3. Cámara propia
camara = camera_create_view(0, 0, 640, 360, 0, noone, -1, -1, -1, -1);
view_enabled = true;
view_camera[0] = camara;
view_set_visible(0, true);

// 4. Parallax del fondo
layer_hspeed(capa_fondo, 0);

// ═══════════ obj_controlador_nivel (End Step) ═══════════
// 5. Cámara sigue al jugador con límites
if (instance_exists(obj_jugador))
{
    var _vw = camera_get_view_width(camara);
    var _vh = camera_get_view_height(camara);

    var _dx = obj_jugador.x - _vw / 2;
    var _dy = obj_jugador.y - _vh / 2;

    _dx = clamp(_dx, 0, max(0, room_width  - _vw));
    _dy = clamp(_dy, 0, max(0, room_height - _vh));

    camera_set_view_pos(camara,
        lerp(camera_get_view_x(camara), _dx, 0.15),
        lerp(camera_get_view_y(camara), _dy, 0.15));

    // 6. Parallax: el fondo se mueve a distinta velocidad
    layer_x(capa_fondo, camera_get_view_x(camara) * 0.5);
}

// ═══════════ obj_controlador_nivel (Clean Up) ═══════════
// 7. ¡Limpia la cámara! Si no, memory leak
if (camara != -1)   // no existe camera_exists; una cámara válida no es -1
{
    camera_destroy(camara);
    camara = -1;
}
```

```gml
// ═══════════ obj_jugador (Step) ═══════════
var _dx = (keyboard_check(vk_right) - keyboard_check(vk_left)) * 3;
var _dy = (keyboard_check(vk_down)  - keyboard_check(vk_up))   * 3;

// El tile map y los objetos sólidos, en un solo array
move_and_collide(_dx, _dy, [obj_pared, obj_controlador_nivel.tilemap_colision]);
```

---

## Resumen

1. **Toda room necesita al menos una capa** y todo asset va en una capa.
2. Las capas agrupan, controlan el **depth** del dibujado y permiten scripts y shaders propios.
3. **En código puedes mezclar tipos de elemento en una capa**; en el Room Editor no.
4. **Tile set → tile layer → tile map.** Cada celda es un blob de 32 bits con índice + flip/mirror/rotate.
5. **Cámara = qué ves; vista = lo que ve; viewport = dónde en pantalla.** 8 viewports, 8 cámaras activas.
6. **Destruye las cámaras** con `camera_destroy()` o tendrás memory leak.
7. **Cada cámara activa multiplica el trabajo de dibujado.** Usa `view_current` para limitarlo.
8. `view_surface_id[]` te permite renderizar un viewport a una surface: la base del escalado pixel-perfect y del post-procesado.
9. Las transiciones de room se hacen con un **objeto persistente** + fundido en **Draw GUI**.
10. ⚠️ Las funciones de **modificar rooms** no se ejecutan desde la room afectada, y sus cambios son permanentes durante la sesión.
