# 11 · Dibujo y renderizado

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Drawing.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/Surfaces.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_create.htm>
> - <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Draw_Events.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/The_Asset_Browser.htm> (lenguajes de shader)
> - `gm-cli manual read "draw_sprite"` / `"gpu_set_blendmode"`

---

## 1. Dónde encaja el dibujo en el frame

El dibujo ocurre **al final del frame**, después de todos los demás eventos.

```
Begin Step → Timelines → Time Sources → Alarms → Step
   → Movimiento → Colisiones → End Step
   → ┌─ DIBUJADO ─────────────────────────┐
     │  Pre-Draw      (display buffer)    │
     │  Draw Begin                        │
     │  Draw                              │
     │  Draw End                          │
     │  Post-Draw     (display buffer)    │
     │  Draw GUI Begin                    │
     │  Draw GUI                          │
     │  Draw GUI End                      │
     └────────────────────────────────────┘
```

> 📖 El orden detallado está en el **tema 06**. Aquí nos centramos en qué se dibuja y cómo.

---

## 2. Los draw targets: a dónde va lo que dibujas

GameMaker **siempre dibuja a un destino** (*draw target*) y lo cambia automáticamente en puntos concretos del ciclo.

### Posibles destinos

**El display buffer:**
1. En los eventos **Pre-Draw** y **Post-Draw**.
2. En los Draw normales, si has **desactivado la application surface** (`application_surface_enable(false)`) y no has fijado una surface propia.

**Una surface:**
1. La **application surface**, si está activada (por defecto).
2. Una **view surface**, si la has fijado con `view_surface_id[]`.
3. Una **surface propia** creada con `surface_create()` y fijada con `surface_set_target()`.

### La secuencia exacta de la application surface

```
Pre-Draw
   └──> se CREA la application surface (si no existía)
        y se fija como render target

Para cada viewport visible (o una vez, si no hay viewports):
   Draw Begin
   Draw
   Draw End
   └──> el render target se RESETEA aquí

Post-Draw
   └──> la application surface se dibuja al display buffer
        (puedes desactivarlo con application_surface_draw_enable)

Draw GUI Begin
Draw GUI
Draw GUI End
```

### La application surface

Es el **destino por defecto** de los eventos Draw normales.

```gml
application_surface_enable(false);       // desactivarla: se dibuja directo al display
application_surface_is_enabled();
application_surface_draw_enable(false);  // no dibujarla automáticamente
application_surface_is_draw_enabled();
application_get_position();              // posición en pantalla
```

> ⚠️ **La application surface se crea la primera vez que se llama a un evento de dibujado en cada room nueva.** Hasta entonces no se dibuja nada.
>
> 💡 Aun así, puedes consultar su posición y redimensionarla en el **Create** sin errores: los valores se aplicarán cuando se cree.

> ⚠️ **Lo único que NO puedes hacer con la application surface es liberarla.** Siempre existe, aunque el handle para acceder a ella pueda cambiar.

### Cuándo desactivar el dibujado automático

```gml
// Post-Draw: quiero dibujar la surface YO, con mi shader
application_surface_draw_enable(false);

// ... y luego, en el mismo Post-Draw:
shader_set(sh_mi_efecto);
draw_surface(application_surface, 0, 0);
shader_reset();
```

---

## 3. Dibujado por defecto vs dibujado personalizado

GameMaker tiene **dos formas** de dibujar en el evento Draw:

### Default draw

- Defines el sprite en las propiedades del objeto y **no pones nada** en el Draw.
- GameMaker dibuja el sprite automáticamente, respetando `image_xscale`, `image_yscale`, `sprite_index`, `image_blend`, etc.
- Si el objeto no tiene sprite asignado, no dibuja nada.

### Custom draw

- Pones código o acciones en el Draw.
- ⚠️ **Anulas por completo el dibujado por defecto.** Si dibujas texto, el sprite **no se dibujará** salvo que lo pidas.

```gml
// Draw event
draw_self();                             // dibuja el sprite como lo haría por defecto
draw_text(x, y - 40, $"Vida: {vida}");   // y además texto
```

### ⚠️ Dos reglas de oro del Draw

1. **No hagas cálculos pesados en el Draw.** Es el evento que más tiempo y recursos consume. La lógica va en Step, alarmas u otros eventos.
2. **Si `visible = false`, se saltan TODOS los eventos de dibujado** (excepto *Resize*). No pongas lógica esencial ahí.

---

## 4. Dibujar sprites y texto

### `draw_sprite()`

```gml
draw_sprite(sprite, subimg, x, y);
```

| Argumento | Descripción |
|---|---|
| `sprite` | El sprite asset. Puedes usar `sprite_index` |
| `subimg` | El frame. `image_index` o `-1` = frame actual de la animación |
| `x`, `y` | Posición, **centrada en el x offset / y offset del sprite** |

```gml
draw_sprite(sprite_index, image_index, x, y);   // ≡ draw_self()
draw_sprite(spr_icono, 0, 32, 32);
```

> 💡 Si `subimg` es mayor que el número de frames, **GameMaker hace bucle**: con 5 frames (0-4), un índice 7 dibuja el frame 2.

> ⚠️ **Con sprites de animación esquelética (Spine), `draw_sprite()` puede no funcionar bien**: podría dibujar solo el primer frame de la pose por defecto. Usa las funciones `draw_skeleton_*()`.

### Variantes `_ext`

```gml
draw_sprite_ext(sprite, subimg, x, y, xscale, yscale, rot, color, alpha);
draw_sprite_part(sprite, subimg, left, top, width, height, x, y);
draw_sprite_part_ext(...);
draw_sprite_stretched(sprite, subimg, x, y, w, h);
draw_sprite_stretched_ext(...);
draw_sprite_pos(sprite, subimg, x1,y1, x2,y2, x3,y3, x4,y4, alpha);
draw_sprite_tiled(sprite, subimg, x, y);
draw_sprite_tiled_ext(...);
draw_sprite_general(...);
```

```gml
// Un destello rojo al recibir daño
draw_sprite_ext(sprite_index, image_index, x, y,
                image_xscale, image_yscale, image_angle,
                c_red,        // color de mezcla
                0.7);         // alpha
```

### Texto

```gml
draw_text(x, y, "Hola");
draw_text_ext(x, y, cadena, separacion_linea, ancho_max);
draw_text_colour(x, y, cadena, c1, c2, c3, c4, alpha);
draw_text_transformed(x, y, cadena, xscale, yscale, angle);
```

```gml
// Example
draw_set_font(fnt_ui);
draw_set_colour(c_white);
draw_set_halign(fa_center);
draw_set_valign(fa_middle);
draw_text(x, y - 48, $"Nivel {nivel}");
draw_set_halign(fa_left);      // ← ¡resetea siempre!
draw_set_valign(fa_top);
```

> ⚠️ `draw_set_*` afecta al estado **global** de dibujo. Si cambias la fuente, el color o la alineación, **resétalos** o afectarás a todo lo que se dibuje después.

---

## 5. Color y alpha

```gml
draw_set_colour(c_red);
draw_set_alpha(0.5);
draw_set_colour(c_white);
draw_set_alpha(1);

// Colores hexadecimales
var _color = $2c8edd;         // formato $ / 0x
var _css   = #dd8e2c;         // formato CSS #RRGGBB (¡intercambiado!)
```

> ⚠️ Recuerda del tema 02: `$2c8edd` **no** equivale a `#2c8edd`. Para que coincidan hay que intercambiar los dos primeros y los dos últimos caracteres.

### Funciones útiles

```
make_colour_rgb(r, g, b)
make_colour_hsv(hue, sat, val)
colour_get_red / green / blue / hue / saturation / value
merge_colour(c1, c2, cantidad)
```

---

## 6. Blend modes (modos de mezcla)

Cuando GameMaker va a dibujar un píxel hay un color **origen** (el que vas a dibujar) y un color **destino** (el que ya hay). El blend mode decide cómo se combinan.

Cada componente se guarda como float entre 0 y 1. El nuevo color se calcula multiplicando origen y destino por sendos factores y sumando.

```gml
gpu_set_blendmode(bm_add);
// ... dibujar ...
gpu_set_blendmode(bm_normal);   // ← SIEMPRE resetea
```

| Constante | Uso típico |
|---|---|
| `bm_normal` | Por defecto |
| `bm_add` | Efectos de luz, fuego, partículas brillantes |
| `bm_subtract` | Oscurecer |
| `bm_max` | Mezcla por máximo |
| `bm_reverse_subtract` | Invertir |

Para modos avanzados: `gpu_set_blendmode_ext(src, dest)` y `gpu_set_blendequation(ecuacion)`.

```gml
// Ejemplo: resplandor de una antorcha
gpu_set_blendmode(bm_add);
draw_sprite_ext(spr_resplandor, 0, x, y, 2, 2, 0, c_orange, 0.6);
gpu_set_blendmode(bm_normal);
```

> 📖 Guía completa recomendada por el manual: **Guide To Using Blendmodes** (incluye el apartado *Surfaces And Alpha*).

---

## 7. Primitivas y vertex buffers

### Primitivas (rápidas de escribir, lentas de ejecutar)

```gml
draw_primitive_begin(pr_trianglelist);
draw_vertex(x1, y1);
draw_vertex(x2, y2);
draw_vertex(x3, y3);
draw_primitive_end();
```

Tipos: `pr_pointlist`, `pr_linelist`, `pr_linestrip`, `pr_trianglelist`, `pr_trianglestrip`, `pr_trianglefan`.

Con textura y color: `draw_vertex_texture()`, `draw_vertex_colour()`, `draw_vertex_texture_colour()`.

```gml
// Un triángulo degradado
draw_primitive_begin(pr_trianglefan);
draw_vertex_colour(x,      y,      c_red,   1);
draw_vertex_colour(x+100,  y,      c_lime,  1);
draw_vertex_colour(x+50,   y+100,  c_blue,  1);
draw_primitive_end();
```

### Vertex buffers (la forma rápida y correcta)

Para geometría compleja o que se dibuja muchas veces:

```gml
// ─── Create ───
vertex_format_begin();
vertex_format_add_position();
vertex_format_add_colour();
vertex_format_add_texcoord();
formato = vertex_format_end();

vb = vertex_create_buffer();

vertex_begin(vb, formato);
// ... vertex_position(), vertex_colour(), vertex_texcoord() ...
vertex_end(vb);

vertex_freeze(vb);   // congela: ya no se modificará → más rápido

// ─── Draw ───
vertex_submit(vb, pr_trianglelist, sprite_get_texture(spr_mi_textura, 0));

// ─── Clean Up ───
vertex_delete_buffer(vb);
vb = -1;
```

> ⚠️ Los **vertex buffers son un recurso dinámico**: deben destruirse con `vertex_delete_buffer()` o tendrás memory leak.

---

## 8. Surfaces

### Qué son

Una surface es un «lienzo» en el que puedes dibujar, manipular y luego volcar a pantalla.

Usos típicos:
- Efectos de **decals** (sangre, escombros): atrapas instancias en la surface y luego las destruyes.
- Texturas manipuladas en shaders.
- Sprites creados sobre la marcha.
- Overlays complejos.
- **Post-procesado** a pantalla completa.

### ⚠️ Las seis reglas de las surfaces (léelas dos veces)

1. **Las surfaces son VOLÁTILES.** Si la ventana o el dispositivo pierde el foco (Alt+Tab en Windows, una llamada en Android), la surface **puede destruirse**. Viven solo en VRAM.
   → **Comprueba siempre con `surface_exists()` y ten código de recreación.**
   > 💡 Esto no parece pasar con los sprites porque también están en RAM: al recuperar el foco se restauran desde ahí automáticamente.

2. **Consumen mucha VRAM.** Mantenlas lo más pequeñas posible; normalmente no más grandes que la vista o la ventana.

3. **Crea las surfaces SOLO en el evento Draw.** Si las creas en el Create, podrías obtener el **mismo índice que la application surface**, con resultados desastrosos. Y limita también el *dibujado* a la surface al Draw.

4. **Una surface siempre está en (0,0).** Debes convertir coordenadas absolutas a relativas restando la posición de la cámara.

5. **No puedes dibujar una surface sobre sí misma.**

6. **El blending puede comportarse distinto de lo esperado.** Lee *Surfaces And Alpha* antes de trabajar con surfaces.

### El patrón correcto

```gml
// ─── Create event ───
surf = -1;                       // ← inicializa al valor inválido

// ─── Draw event ───
if (!surface_exists(surf))       // ← comprueba SIEMPRE
{
    surf = surface_create(960, 540);
    surface_set_target(surf);
    draw_clear_alpha(c_black, 0);   // límpiala: puede contener "ruido"
    surface_reset_target();
}

// Dibujar EN la surface (coordenadas relativas a la cámara)
surface_set_target(surf);
var _vx = camera_get_view_x(view_camera[0]);
var _vy = camera_get_view_y(view_camera[0]);

with (obj_sangre)
{
    draw_sprite(sprite_index, image_index, x - _vx, y - _vy);
}

surface_reset_target();

// Dibujar LA surface en pantalla
draw_surface(surf, 0, 0);

// ─── Clean Up event ───
if (surface_exists(surf))
{
    surface_free(surf);
    surf = -1;                   // ← resetea el handle
}
```

### Convertir coordenadas (regla 4 en la práctica)

```gml
if (view_current == 0)
{
    surface_set_target(surf);
    with (obj_efecto)
    {
        var _vx = camera_get_view_x(view_camera[1]);
        var _vy = camera_get_view_y(view_camera[1]);
        draw_sprite(sprite_index, image_index, x - _vx, y - _vy);
    }
    surface_reset_target();
}
else
{
    draw_surface(surf, 0, 0);
}
```

### Formatos de surface (2026)

```gml
surface_create(w, h, [formato]);
```

| Constante | Descripción |
|---|---|
| `surface_rgba8unorm` | **(Por defecto)** 4 canales RGBA de 8 bits (0-255). «unorm» = normalizado a 0-1 al leerse en shaders |
| `surface_r8unorm` | Un solo canal (rojo) de 8 bits. **Ocupa la cuarta parte**. En shader, los demás canales valen 0 |
| `surface_rg8unorm` | Dos canales (rojo, verde) de 8 bits |
| `surface_rgba4unorm` | 4 canales de 4 bits (rango 0-15) |
| `surface_rgba16float` | 4 canales de 16 bits float. **Mayor precisión**: ideal para **HDR** (valores fuera de 0-255) |
| `surface_r16float` | Un canal de 16 bits float |
| `surface_rgba32float` | 4 canales de 32 bits float. Máxima precisión; más lento y menos soportado |
| `surface_r32float` | Un canal de 32 bits float |

```gml
// Surface HDR para un pipeline de bloom
surf_hdr = surface_create(960, 540, surface_rgba16float);

// Máscara de un solo canal (ahorro de memoria al 75%)
surf_mascara = surface_create(256, 256, surface_r8unorm);
```

> 💡 Saber los bytes por píxel es **imprescindible** si transfieres datos de la surface a un buffer (`buffer_get_surface()` / `buffer_set_surface()`).

### Otras funciones

```
surface_exists / surface_create / surface_create_ext / surface_resize
surface_set_target / surface_set_target_ext / surface_reset_target
surface_get_target / surface_get_target_depth / surface_get_target_ext
surface_copy / surface_copy_part
surface_depth_disable / surface_get_depth_disable / surface_has_depth
surface_get_height / surface_get_width
surface_get_texture / surface_get_texture_depth
surface_getpixel / surface_getpixel_ext
surface_get_format / surface_format_is_supported
surface_free / surface_save / surface_save_part

// Dibujo
draw_surface / draw_surface_ext / draw_surface_part / draw_surface_part_ext
draw_surface_stretched / draw_surface_stretched_ext
draw_surface_tiled / draw_surface_tiled_ext / draw_surface_general

// Transferencia a/desde buffers
buffer_get_surface / buffer_set_surface
```

### Depth y stencil buffer

Por defecto las surfaces tienen **depth buffer y stencil buffer**. Se puede desactivar con `surface_depth_disable()`.

> 📖 Más detalles en *The Depth And Stencil Buffer*.

### `surface_create_ext()` (solo HTML5)

Permite vincular una surface a un elemento `<canvas>` ya existente en tu página web, para «partir» el juego en varias zonas del HTML. **Solo HTML5**, y siempre crea formato `surface_rgba8unorm`.

```gml
s1 = surface_create_ext("surface1", 192, 550);
s2 = surface_create_ext("surface2", 608, 186);
view_surface_id[1] = s1;
view_surface_id[2] = s2;
```

---

## 9. Shaders

Un shader es un programa que corre **directamente en la tarjeta gráfica**. Se compone de un **vertex shader** y un **fragment (pixel) shader**, que trabajan juntos para manipular lo que se renderiza.

### Lenguajes según plataforma

| Lenguaje | Plataforma |
|---|---|
| **GLSL ES** | **Todas** |
| **GLSL** | Mac y Ubuntu (Linux) |
| **HLSL11** | Windows, XboxOne |
| **PSSL** | PlayStation 4 |

Se cambia con clic derecho sobre el shader → **Shader Type**.

```gml
// Aplicar un shader
shader_set(sh_mi_shader);

// Pasarle uniforms
shader_set_uniform_f(shader_get_uniform(sh_mi_shader, "u_tiempo"), current_time / 1000);
shader_set_uniform_f(shader_get_uniform(sh_mi_shader, "u_intensidad"), 0.8);

// ... dibujar ...

shader_reset();   // ← SIEMPRE resetea
```

> ⚠️ **GLSL ES para todo** es la opción más portable. Si solo apuntas a Windows/Mac/Linux puedes usar GLSL o HLSL11.

---

## 10. Draw GUI vs Draw normal

| | Draw normal | Draw GUI |
|---|---|---|
| Afectado por la cámara | ✅ Sí (posición, escala, rotación) | ❌ No |
| `(0,0)` | Esquina de la vista | Esquina de la application surface / display |
| Cuándo se dibuja | Antes | **Siempre encima** |
| Ideal para | El mundo del juego | HUD, menús, interfaces |

```gml
// Draw GUI event del HUD
draw_set_font(fnt_ui);
draw_set_halign(fa_left);
draw_text(16, 16, $"Vida: {obj_jugador.vida}");
draw_text(16, 40, $"Puntos: {global.puntuacion}");

// Barra de vida
draw_healthbar(16, 64, 216, 88,
               obj_jugador.vida / obj_jugador.vida_max,
               c_black, c_red, c_lime, 0, true, true);
```

Funciones de control:
```gml
display_set_gui_size(640, 360);     // tamaño lógico fijo; se escala solo
display_set_gui_maximise(true);     // ocupar toda la pantalla (incluidas barras negras)
```

> ⚠️ Con **Aspect Ratio Correction** activado, la GUI **no** se dibuja sobre las barras negras. `display_set_gui_maximise()` cambia eso.

---

## 11. Rendimiento: batching, texture pages, draw calls

### Los tres números que vigilar

La ventana **FPS** del Debug Overlay muestra en su barra de título:
- **Texture swaps** (cambios de textura)
- **Vertex batches** (lotes de vértices)
- **FPS real**

> ⚠️ Los dos primeros **nunca serán cero**: incluso con una room vacía, GameMaker dibuja y agrupa cosas, así que verás 2 o 3.

### Cómo funciona el batching

GameMaker agrupa operaciones de dibujo en **lotes** para minimizar llamadas a la GPU. Un lote se rompe cuando cambias algo que obliga a cambiar de estado:

- Cambiar de **textura** (sprite de otra texture page).
- Cambiar de **blend mode**.
- Cambiar de **shader**.
- Cambiar el **draw target** (surface).

**Consecuencia práctica: ordena tus draws.**

```gml
// ❌ MAL: alternas sprites de texture pages distintas → rompe el lote cada vez
for (var i = 0; i < 100; i++)
{
    draw_sprite(spr_enemigo, 0, x[i], y[i]);
    draw_sprite(spr_ui_icono, 0, x[i], y[i] + 20);
}

// ✅ BIEN: agrupas por textura → dos lotes
for (var i = 0; i < 100; i++) { draw_sprite(spr_enemigo, 0, x[i], y[i]); }
for (var i = 0; i < 100; i++) { draw_sprite(spr_ui_icono, 0, x[i], y[i] + 20); }
```

### Texture pages (Texture Groups)

- Los sprites se empaquetan en **texture pages**. Si tus sprites caben en menos páginas, habrá menos cambios de textura.
- Usa **Texture Groups** para controlar qué va junto (clic derecho en sprites → *Assign Texture Group*).
- Los sprites marcados como **Separate Texture Page** van a su propia página: úsalos con moderación.
- Las **Dynamic Textures** se cargan y descargan bajo demanda.

> 💡 **Regla de oro:** agrupa en el mismo texture group los sprites que se dibujan juntos en pantalla (por ejemplo, todos los enemigos de un nivel).

### `draw_flush()`

Fuerza el vaciado de todo el pipeline de dibujo.

```gml
draw_flush();
```

Úsalo con cuidado: rompe el batching a propósito. Solo tiene sentido en casos muy concretos (por ejemplo, sincronizar con operaciones externas).

### `draw_enable_drawevent()`

```gml
draw_enable_drawevent(false);   // desactiva TODOS los eventos de dibujo
```

Útil para ahorrar el paso de dibujado en juegos headless o en cálculos por lotes, pero casi nunca lo necesitarás.

### Otras técnicas de optimización

```gml
gpu_set_sprite_cull(true);      // descartar sprites fuera de cámara
gpu_set_alphatestenable(true);  // descartar píxeles transparentes pronto
gpu_set_ztestenable(true);      // profundidad (3D)
gpu_set_texrepeat(true);        // permitir texturas repetidas
```

```gml
// Desactivar instancias fuera de cámara (lo más efectivo con muchas instancias)
instance_deactivate_all(colspace.room);
instance_activate_region(_vx - 128, _vy - 128, _vw + 256, _vh + 256, true);
```

---

## 12. Categorías de funciones de dibujo (mapa de la sección)

| Categoría | Para qué |
|---|---|
| **Colour And Alpha** | Color, alpha, limpieza |
| **GPU Control** | Blend modes, culling, z-test, alphatest, estado de la GPU |
| **Mipmapping** | Niveles de detalle de texturas |
| **Basic Forms** | Rectángulos, círculos, líneas, elipses, polígonos |
| **Sprites And Tiles** | `draw_sprite*`, `draw_tilemap`, `draw_self` |
| **Text** | `draw_text*` y configuración de fuentes |
| **Primitives And Vertex Formats** | `draw_primitive*`, vertex buffers |
| **Surfaces** | Todo lo de surfaces |
| **Lighting** | Sistema de luces legacy |
| **Particles** | Sistema de partículas |
| **Textures** | Control de texturas |
| **Shaders** | Shaders y uniforms |
| **Video Playback** | Reproducción de vídeo |
| **Depth And Stencil Buffer** | Buffers de profundidad y stencil |

### Formas básicas (muy útiles para debug y UI)

```gml
draw_rectangle(x1, y1, x2, y2, outline);
draw_rectangle_colour(x1, y1, x2, y2, c1, c2, c3, c4, outline);
draw_roundrect(x1, y1, x2, y2, outline);
draw_circle(x, y, radio, outline);
draw_ellipse(x1, y1, x2, y2, outline);
draw_line(x1, y1, x2, y2);
draw_line_width(x1, y1, x2, y2, ancho);
draw_point(x, y);
draw_arrow(x1, y1, x2, y2, tamano);
draw_polygon(...);
draw_triangle(x1,y1, x2,y2, x3,y3, outline);
```

```gml
// Ejemplo: dibujar la bounding box de colisión para depurar
draw_set_colour(c_red);
draw_rectangle(bbox_left, bbox_top, bbox_right, bbox_bottom, true);
draw_set_colour(c_white);
```

---

## 13. Ejemplo completo: HUD + efectos con surface y shader

```gml
// ═══════════ obj_render (Create) ═══════════
persistent = true;

surf_mundo = -1;

// ═══════════ obj_render (Post-Draw) ═══════════
// Post-Draw va ANTES de los Draw GUI: perfecto para post-procesado
// que NO debe afectar al HUD.

// 1. No queremos que GameMaker dibuje la surface automáticamente
application_surface_draw_enable(false);

// 2. Dibujamos la application surface con nuestro shader
shader_set(sh_vinheta);

var _u_tiempo = shader_get_uniform(sh_vinheta, "u_tiempo");
shader_set_uniform_f(_u_tiempo, current_time / 1000);

draw_surface_stretched(application_surface, 0, 0,
                       window_get_width(), window_get_height());

shader_reset();

// ═══════════ obj_render (Draw GUI) ═══════════
// El HUD NO se ve afectado por la vinheta (va después)
draw_set_font(fnt_ui);
draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_set_colour(c_white);

draw_text(16, 16, $"Vida: {obj_jugador.vida}/{obj_jugador.vida_max}");
draw_text(16, 40, $"Puntos: {global.puntuacion}");

draw_healthbar(16, 64, 216, 88,
               obj_jugador.vida / obj_jugador.vida_max,
               c_black, c_red, c_lime, 0, true, true);

// Resetea el estado global
draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_set_colour(c_white);
draw_set_alpha(1);
```

```gml
// ═══════════ obj_sangre_decal (Create) ═══════════
// Nos "pegamos" a la surface y luego desaparecemos: coste cero
with (obj_render)
{
    if (!surface_exists(surf_mundo))
    {
        surf_mundo = surface_create(room_width, room_height);
        surface_set_target(surf_mundo);
        draw_clear_alpha(c_black, 0);
        surface_reset_target();
    }

    surface_set_target(surf_mundo);
    draw_sprite_ext(sprite_index, image_index, x, y,
                    image_xscale, image_yscale, image_angle,
                    c_white, 0.8);
    surface_reset_target();
}

instance_destroy();   // ya no existo: solo queda la mancha en la surface
```

---

## Resumen

1. El dibujo ocurre **al final del frame**, y siempre va a un **draw target** (application surface por defecto).
2. **Default draw** vs **custom draw**: si pones código en el Draw, **anulas** el dibujado del sprite (añade `draw_self()`).
3. ⚠️ **`visible = false` salta todos los eventos de dibujo.** No pongas lógica ahí.
4. **Draw GUI siempre encima** y sin transformación de cámara: es para interfaces.
5. **Pre-Draw y Post-Draw** dibujan al display buffer: el sitio del post-procesado a pantalla completa.
6. ⚠️ **Las surfaces son volátiles**: comprueba `surface_exists()` y recréalas. Créalas **solo en el Draw**.
7. Las surfaces tienen **formatos** (`rgba8unorm`, `r8unorm`, `rgba16float`…): elígelos según precisión y memoria.
8. **Shaders**: GLSL ES para todo; GLSL para Mac/Linux; HLSL11 para Windows/Xbox.
9. **El batching se rompe** al cambiar de textura, blend mode, shader o draw target. **Agrupa tus draws por textura.**
10. Vigila **texture swaps** y **vertex batches** en el Debug Overlay. Nunca serán 0, pero cuanto más bajos, mejor.
