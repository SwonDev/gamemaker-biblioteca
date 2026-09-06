# 05 — Superficies

> Referencia completa de GML para **GameMaker LTS 2026.0** (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Áreas: `Drawing/Surfaces/` y `Buffers/`.
> **43 funciones documentadas** + la variable global `application_surface`.

---

## Índice

1. [Qué es una superficie y reglas de uso](#qué-es-una-superficie-y-reglas-de-uso)
2. [Ciclo de vida](#ciclo-de-vida)
3. [Formatos de superficie](#formatos-de-superficie)
4. [Creación y destrucción](#creación-y-destrucción)
5. [Consulta de superficies](#consulta-de-superficies)
6. [Destino de dibujo](#destino-de-dibujo)
7. [Búfer de profundidad](#búfer-de-profundidad)
8. [Copia entre superficies](#copia-entre-superficies)
9. [Lectura de píxeles](#lectura-de-píxeles)
10. [Guardado en disco](#guardado-en-disco)
11. [Dibujo de superficies](#dibujo-de-superficies)
12. [Transferencia a y desde buffers](#transferencia-a-y-desde-buffers)
13. [La Application Surface](#la-application-surface)
14. [Tabla resumen](#tabla-resumen)
15. [Fuentes](#fuentes)

---

## Qué es una superficie y reglas de uso

Una superficie es un lienzo en memoria de vídeo (VRAM) sobre el que puedes dibujar y que después
puedes usar como textura. GameMaker **no dibuja directamente a pantalla** en los eventos de dibujo
normales, sino a la **Application Surface**.

El manual establece una serie de reglas que conviene respetar:

1. **Las superficies son volátiles.** Viven solo en memoria de textura y pueden destruirse en
   cualquier momento (por ejemplo, al minimizar la ventana en Windows con Alt+Tab, o cuando la app
   de Android pierde el foco por una llamada). **Comprueba siempre con `surface_exists()`** antes de
   usarlas y ten código de recreación.
   - Esto no parece ocurrir con los sprites, pero en realidad **sí ocurre**: la diferencia es que
     los sprites también están en RAM, y al recuperar el foco se restauran automáticamente desde ahí.
2. **Consumen mucha VRAM.** Mantenlas lo más pequeñas posible; lo normal es que no superen el tamaño
   de la vista o de la ventana.
3. **Crea las superficies en el evento Draw.** Si las creas en el Create, puedes obtener el mismo
   índice que `application_surface` y acabar usando sin saberlo el destino de render actual. Lo
   mismo aplica a dibujar en ellas: hazlo en Draw.
4. **Al dibujar en una superficie, su origen siempre es (0, 0).** Debes convertir coordenadas
   absolutas en relativas restando la posición de la cámara:
   ```gml
   var _vx = camera_get_view_x(view_camera[0]);
   var _vy = camera_get_view_y(view_camera[0]);
   draw_sprite(sprite_index, image_index, x - _vx, y - _vy);
   ```
5. **No puedes dibujar una superficie sobre sí misma.** El manual indica que este código no puede
   usarse y escribe un mensaje en la consola:
   ```gml
   surface_set_target(surf);
   draw_surface(surf, 0, 0);   // ERROR
   surface_reset_target();
   ```
6. **El comportamiento de blending en superficies propias puede ser distinto del esperado.** Lee la
   guía *Surfaces And Alpha* del manual antes de trabajar con alfa en superficies.

> **Nota de rendimiento:** se recomienda encarecidamente crear las superficies con tamaños que sean
> **potencia de 2** (16, 128, 512, 1024…). No es estrictamente necesario en Windows y macOS, pero
> mejora la compatibilidad, y **en HTML5 y dispositivos es esencial**.

---

## Ciclo de vida

```gml
// Evento Create
surf = -1;

// Evento Draw
if (!surface_exists(surf))
{
    surf = surface_create(960, 540);     // 1. crear
    surface_set_target(surf);            // 2. fijar como destino
    draw_clear_alpha(c_black, 0);        // 3. limpiar (¡recomendado!)
    surface_reset_target();              // 4. devolver el destino
}

surface_set_target(surf);
draw_sprite(spr_icono, 0, 48, 48);       // dibujar lo que quieras
surface_reset_target();

draw_surface(surf, 0, 0);                // 5. usar la superficie

// Evento Cleanup / Room End
surface_free(surf);                      // 6. liberar
```

Al crear una superficie, **su contenido es indefinido** («ruido» de memoria), así que límpiala antes
de usarla con `draw_clear_alpha()`.

---

## Formatos de superficie

`surface_create()` acepta un argumento de formato opcional. El formato determina cuántos bytes
ocupa cada píxel, dato imprescindible si vas a transferir la superficie a o desde un **buffer**.

| Constante | Canales | Bits por canal | Uso recomendado |
|---|---|---|---|
| `surface_rgba8unorm` **(por defecto)** | RGBA | 8 (rango 0–255) | Uso general. «unorm» significa que al leerlo en un shader los valores se normalizan a 0–1 |
| `surface_r8unorm` | R | 8 | Máscaras de un solo canal. Ocupa **la cuarta parte** que RGBA. En shader, todos los canales salvo rojo valen 0 |
| `surface_rg8unorm` | RG | 8 + 8 | Dos canales, por ejemplo para datos de dirección o velocidad |
| `surface_rgba4unorm` | RGBA | 4 (rango 0–15) | Máxima compresión con 4 canales; calidad baja |
| `surface_rgba16float` | RGBA | 16 en coma flotante | **HDR**: permite valores fuera del rango 0–255 |
| `surface_r16float` | R | 16 en coma flotante | Campo de alturas, profundidad, mapas de datos de alta precisión |
| `surface_rgba32float` | RGBA | 32 en coma flotante | Máxima precisión. **Más lento de renderizar** y menos compatible |
| `surface_r32float` | R | 32 en coma flotante | Datos numéricos de precisión máxima en un canal |

```gml
// Superficie HDR para un pipeline de bloom
if (surface_format_is_supported(surface_rgba16float))
{
    surf_hdr = surface_create(1024, 1024, surface_rgba16float);
}
```

---

## Creación y destrucción

### `surface_create(w, h, [format])`
- **Devuelve:** `Surface` (o un handle inválido `-1` si algo falla)
- **Qué hace:** crea una superficie nueva y la devuelve.
- **Ejemplo:**
```gml
// Superficie estándar
surf = surface_create(1024, 1024);

// Superficie HDR explícita
surf_hdr = surface_create(1024, 1024, surface_rgba16float);

// Superficie de un solo canal para una máscara
surf_mascara = surface_create(512, 512, surface_r8unorm);
```
- **Notas / trampas:**
  - Contenido indefinido al crear: límpiala.
  - Si la generación automática de búfer de profundidad está activada (lo está por defecto), también
    se crean búfer de profundidad **y de stencil**.
  - Usa tamaños potencia de 2.

### `surface_create_ext(name, w, h)`
- **Devuelve:** `Surface` (o `-1` si falla)
- **Qué hace:** vincula una superficie a un **elemento `<canvas>` ya existente en tu página web**,
  permitiendo dividir el juego y dibujar partes en distintos lugares de la página.
- **Ejemplo:**
```gml
// HTML5: dibujar un minimapa en un canvas propio de la página
surf_minimapa = surface_create_ext("canvasMinimapa", 256, 256);
```
- **Notas / trampas:** es una función específica de HTML5.

### `surface_resize(surface_id, w, h)`
- **Devuelve:** `N/A`
- **Qué hace:** redimensiona una superficie existente a las nuevas dimensiones en píxeles.
- **Ejemplo:**
```gml
// Adaptar la superficie al tamaño de la ventana
if (surface_get_width(surf) != window_get_width())
{
    surface_resize(surf, window_get_width(), window_get_height());
}
```
- **Notas / trampas:** **el contenido se pierde** al redimensionar; vuelve a limpiar y redibujar.

### `surface_free(surface)`
- **Devuelve:** `N/A`
- **Qué hace:** libera una superficie de memoria.
- **Ejemplo:**
```gml
// Evento Cleanup
if (surface_exists(surf)) surface_free(surf);
```
- **Notas / trampas:** el manual es tajante: usa esta función **siempre** que termines con una
  superficie, normalmente al final de la room. No hacerlo provoca **fugas de memoria que acabarán
  ralentizando y haciendo crashear el juego**.

### `surface_exists(surface)`
- **Devuelve:** `Boolean`
- **Qué hace:** comprueba si la superficie existe.
- **Ejemplo:**
```gml
// Patrón obligatorio en el Draw
if (!surface_exists(surf))
{
    surf = surface_create(960, 540);
    surface_set_target(surf);
    draw_clear_alpha(c_black, 0);
    surface_reset_target();
}
```
- **Notas / trampas:** el manual la califica de **esencial** por la naturaleza volátil de las
  superficies. Compruébala **incluso antes de dibujar la superficie en pantalla**.

---

## Consulta de superficies

### `surface_get_width(surface_id)`
- **Devuelve:** `Real` (píxeles)
- **Qué hace:** devuelve la anchura de la superficie.
- **Ejemplo:**
```gml
var _w = surface_get_width(surf);
```

### `surface_get_height(surface_id)`
- **Devuelve:** `Real` (píxeles)
- **Qué hace:** devuelve la altura de la superficie.
- **Ejemplo:**
```gml
var _h = surface_get_height(surf);
```

### `surface_get_texture(surface_id)`
- **Devuelve:** `Texture` (o `-1` si la superficie no existe)
- **Qué hace:** devuelve la textura de la página de textura de la superficie, para usarla en
  primitivas, 3D o shaders.
- **Ejemplo:**
```gml
// Pasar la superficie a un shader como sampler
var _tex = surface_get_texture(surf_ruido);
texture_set_stage(shader_get_sampler_index(sh_agua, "s_ruido"), _tex);
```
- **Notas / trampas:** devuelve el **ID** de la textura, no un puntero (al contrario que
  `sprite_get_texture`).

### `surface_get_texture_depth(surface)`
- **Devuelve:** `Texture` (o `-1` si no existe textura de profundidad)
- **Qué hace:** devuelve la **textura de profundidad** de la superficie, para pasarla a un shader
  (imprescindible para efectos como *depth of field*, niebla por profundidad o SSAO).
- **Ejemplo:**
```gml
var _tex_prof = surface_get_texture_depth(surf_escena);
texture_set_stage(u_sampler_profundidad, _tex_prof);
```

### `surface_get_format(surface_id)`
- **Devuelve:** constante de formato de superficie
- **Qué hace:** devuelve el formato con el que se creó la superficie.
- **Ejemplo:**
```gml
if (surface_get_format(surf) == surface_rgba16float)
{
    show_debug_message("Superficie HDR");
}
```

### `surface_format_is_supported(format)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el formato indicado está soportado **en la plataforma actual**.
- **Ejemplo:**
```gml
// Elegir HDR solo si la plataforma lo soporta
var _formato = surface_format_is_supported(surface_rgba16float)
             ? surface_rgba16float
             : surface_rgba8unorm;
surf = surface_create(1024, 1024, _formato);
```
- **Notas / trampas:** úsalo siempre antes de pedir formatos exóticos, sobre todo en móviles y
  HTML5.

---

## Destino de dibujo

### `surface_set_target(surface, [depth])`
- **Devuelve:** `Boolean` — si el destino de render se fijó correctamente
- **Qué hace:** fija la superficie como destino de dibujo actual. El argumento opcional `depth`
  permite usar el búfer de profundidad de **otra** superficie.
- **Ejemplo:**
```gml
if (surface_set_target(surf))
{
    draw_clear_alpha(c_black, 0);
    with (obj_efecto) draw_self();
    surface_reset_target();
}
```
- **Notas / trampas:** el manual advierte de que hacerlo mal **lanza un error fatal**.

### `surface_set_target_ext(index, surface_id)`
- **Devuelve:** `Boolean`
- **Qué hace:** asigna una superficie a uno de los **4 destinos de render** disponibles (índices
  `0` a `3`). Diseñada para trabajar con shaders que escriben en múltiples destinos (MRT).
- **Ejemplo:**
```gml
// Renderizado a múltiples destinos
surface_set_target(0, surf_color);
surface_set_target_ext(1, surf_normales);
surface_set_target_ext(2, surf_profundidad);
draw_surface(surf_escena, 0, 0);
surface_reset_target();
```

### `surface_get_target()`
- **Devuelve:** `Real` (el ID de la superficie destino, o `-1` si no hay ninguna fijada)
- **Qué hace:** devuelve la superficie fijada actualmente como destino de dibujo.
- **Ejemplo:**
```gml
var _destino = surface_get_target();
```

### `surface_get_target_depth()`
- **Devuelve:** `Real` (`-1` si no se usa búfer de profundidad)
- **Qué hace:** devuelve la superficie cuyo búfer de profundidad se está usando actualmente. Puede
  ser distinta del destino de dibujo si se pasó el argumento `depth` a `surface_set_target`.
- **Ejemplo:**
```gml
if (surface_get_target_depth() == -1) show_debug_message("Sin profundidad");
```

### `surface_get_target_ext(index)`
- **Devuelve:** `Real` (`-1` si no hay superficie asignada a ese índice)
- **Qué hace:** devuelve la superficie asignada a uno de los 4 destinos de render.
- **Ejemplo:**
```gml
var _destino1 = surface_get_target_ext(1);
```

### `surface_reset_target()`
- **Devuelve:** `Boolean` — si se restauró correctamente
- **Qué hace:** devuelve el dibujo al destino anterior. Si habías anidado superficies, vuelve a la
  superficie anterior; si no, vuelve a la Application Surface o al búfer de pantalla.
- **Ejemplo:**
```gml
surface_set_target(surf_a);
draw_clear_alpha(c_black, 0);

    surface_set_target(surf_b);  // anidado
    draw_sprite(spr_x, 0, 0, 0);
    surface_reset_target();      // vuelve a surf_a

draw_surface(surf_b, 10, 10);
surface_reset_target();          // vuelve al destino original
```

---

## Búfer de profundidad

### `surface_depth_disable(disable)`
- **Devuelve:** `N/A`
- **Qué hace:** con `true`, **desactiva** la creación automática de búfer de profundidad para las
  superficies que se creen a partir de ese momento.
- **Ejemplo:**
```gml
// Juego 2D: ahorramos memoria desactivando la profundidad
surface_depth_disable(true);
surf = surface_create(512, 512);
surface_depth_disable(false);
```
- **Notas / trampas:** asignar búferes de profundidad **básicamente duplica el tamaño** de las
  superficies, un coste innecesario en juegos 2D.

### `surface_get_depth_disable()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la generación automática de búfer de profundidad está activa.
- **Ejemplo:**
```gml
if (!surface_get_depth_disable()) surface_depth_disable(true);
```

### `surface_has_depth(surface)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la superficie tiene búfer de profundidad (y, por relación, de stencil, ya
  que para que exista stencil debe estar activada la creación de profundidad).
- **Ejemplo:**
```gml
if (surface_has_depth(surf))
{
    var _tex = surface_get_texture_depth(surf);
    texture_set_stage(u_profundidad, _tex);
}
```

---

## Copia entre superficies

### `surface_copy(destination, x, y, source)`
- **Devuelve:** `N/A`
- **Qué hace:** copia la imagen completa de una superficie sobre otra, en la posición local
  indicada, donde `(0, 0)` es la esquina superior izquierda de la superficie destino. **Sobrescribe**
  el contenido previo y **no** realiza ninguna mezcla.
- **Ejemplo:**
```gml
// Copiar el estado anterior de la pantalla a una superficie de respaldo
surface_copy(surf_respaldo, 0, 0, surf_actual);
```

### `surface_copy_part(destination, x, y, source, xs, ys, ws, hs)`
- **Devuelve:** `N/A`
- **Qué hace:** copia **una porción** de la superficie origen. Las coordenadas de origen (`xs`, `ys`)
  y el tamaño (`ws`, `hs`) están basados en el **tamaño de la superficie**.
- **Ejemplo:**
```gml
// Copiar un tile de 64x64 del atlas a la superficie de destino
surface_copy_part(surf_destino, 128, 128, surf_atlas, 0, 0, 64, 64);
```

---

## Lectura de píxeles

### `surface_getpixel(surface_id, x, y)`
- **Devuelve:** `Colour` o `Array` (según el formato de la superficie)
- **Qué hace:** devuelve el color de un píxel concreto usando coordenadas locales de la superficie,
  donde `(0, 0)` es la esquina superior izquierda.
- **Comportamiento según formato:**

  | Formatos | Devuelve |
  |---|---|
  | `surface_rgba8unorm`, `surface_rgba4unorm`, `surface_r8unorm`, `surface_rg8unorm` | Un **color** normal. Los canales no usados valen 0 |
  | `surface_rgba16float`, `surface_r16float`, `surface_rgba32float`, `surface_r32float` | Un **array** con los valores de los canales |

- **Ejemplo:**
```gml
// Detectar colisión por color en una superficie de terreno
var _color = surface_getpixel(surf_terreno, x, y);
if (_color != c_black) show_debug_message("Suelo sólido");
```
- **Notas / trampas:** el manual advierte de que **es extremadamente lenta y puede provocar una
  pausa en el juego**. No la uses en bucles por frame.

### `surface_getpixel_ext(surface_id, x, y)`
- **Devuelve:** `Real` (valor **abgr de 32 bits**) o `Array` (según formato)
- **Qué hace:** igual que `surface_getpixel` pero devolviendo el valor completo de 32 bits con el
  alfa incluido.
- **Ejemplo:**
```gml
var _abgr = surface_getpixel_ext(surf, x, y);
var _alfa = (_abgr >> 24) & 255;
```
- **Notas / trampas:** misma advertencia de lentitud extrema.

---

## Guardado en disco

### `surface_save(surface_id, fname)`
- **Devuelve:** `N/A`
- **Qué hace:** guarda la superficie completa en disco con el nombre de archivo indicado.
- **Ejemplo:**
```gml
// Captura de pantalla para el modo foto
surface_save(application_surface, "captura_" + string(current_time) + ".png");
```

### `surface_save_part(surface_id, fname, x, y, width, height)`
- **Devuelve:** `N/A`
- **Qué hace:** guarda **una parte** de la superficie en disco.
- **Ejemplo:**
```gml
// Guardar solo el avatar: recorte de 128x128 desde (16, 16)
surface_save_part(surf_perfil, "avatar.png", 16, 16, 128, 128);
```

---

## Dibujo de superficies

### `draw_surface(id, x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja la superficie en la posición indicada.
- **Ejemplo:**
```gml
draw_surface(surf, 0, 0);
```

### `draw_surface_ext(id, x, y, xscale, yscale, rot, col, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja la superficie con escala, rotación, color de mezcla y alfa.
- **Ejemplo:**
```gml
// Transición de escena: la superficie se desvanece girando
draw_surface_ext(surf, room_width / 2, room_height / 2,
                 1.2, 1.2, angulo, c_white, alfa);
```

### `draw_surface_part(surface, left, top, w, h, x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja **una porción** de la superficie.
- **Ejemplo:**
```gml
// Mostrar solo un trozo de 200x150 de la superficie
draw_surface_part(surf, 100, 100, 200, 150, x, y);
```

### `draw_surface_part_ext(surface, left, top, w, h, x, y, xscale, yscale, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** porción de superficie con escala, color y alfa.
- **Ejemplo:**
```gml
// Sprite sheet contenido en una superficie, escalado x2 y teñido
draw_surface_part_ext(surf_hoja, 0, 0, 32, 32, x, y, 2, 2, c_white, 1);
```

### `draw_surface_stretched(surface, x, y, w, h)`
- **Devuelve:** `N/A`
- **Qué hace:** estira la superficie para que ocupe el área indicada.
- **Ejemplo:**
```gml
// Post-procesado a pantalla completa
draw_surface_stretched(surf_post, 0, 0, room_width, room_height);
```

### `draw_surface_stretched_ext(surface, x, y, w, h, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** estirada con color de mezcla y alfa.
- **Ejemplo:**
```gml
draw_surface_stretched_ext(surf_post, 0, 0, room_width, room_height, c_white, 0.8);
```

### `draw_surface_tiled(surface, x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja la superficie en mosaico cubriendo la vista.
- **Ejemplo:**
```gml
draw_surface_tiled(surf_patron, 0, 0);
```

### `draw_surface_tiled_ext(surface, x, y, xscale, yscale, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** mosaico con escala, color y alfa.
- **Ejemplo:**
```gml
draw_surface_tiled_ext(surf_patron, 0, 0, 2, 2, c_white, 0.5);
```

### `draw_surface_general(surface, left, top, width, height, x, y, xscale, yscale, rot, c1, c2, c3, c4, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** la más completa: porción de superficie con escala, rotación y un color por esquina.
- **Orden de esquinas:** `c1` superior izquierda, `c2` superior derecha, `c3` inferior derecha,
  `c4` inferior izquierda.
- **Ejemplo:**
```gml
// Superficie deformada con degradado de esquinas
draw_surface_general(surf, 0, 0, 256, 256, x, y, 1, 1, 15,
                     c_white, c_white, c_black, c_black, 1);
```

---

## Transferencia a y desde buffers

### `buffer_get_surface(buffer, surface, offset)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe el contenido de una superficie en un buffer.
- **Ejemplo:**
```gml
// Leer los píxeles de una superficie para analizarlos o enviarlos por red
var _tam = 4 * surface_get_width(surf) * surface_get_height(surf);
var _buff = buffer_create(_tam, buffer_fixed, 1);
buffer_get_surface(_buff, surf, 0);
// ... procesar _buff ...
buffer_delete(_buff);
```
- **Notas / trampas:**
  - El buffer debe haberse creado antes, con **alineación de 1 byte** y tamaño suficiente; si no
    estás seguro, usa un buffer `buffer_grow`.
  - El tamaño necesario depende del **formato** de la superficie (ver tabla de formatos).

### `buffer_set_surface(buffer, surface, offset)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe el contenido de un buffer en una superficie.
- **Ejemplo:**
```gml
// Generar una textura proceduralmente desde código
var _buff = buffer_create(4 * 256 * 256, buffer_fixed, 1);
for (var _i = 0; _i < 256 * 256; _i++)
{
    buffer_write(_buff, buffer_u8, irandom(255)); // R
    buffer_write(_buff, buffer_u8, irandom(255)); // G
    buffer_write(_buff, buffer_u8, irandom(255)); // B
    buffer_write(_buff, buffer_u8, 255);          // A
}
buffer_set_surface(_buff, surf_ruido, 0);
buffer_delete(_buff);
```
- **Notas / trampas:**
  - El tamaño del buffer debe ser **igual o mayor** que el de la superficie.
  - **Si el buffer es más pequeño, la función falla silenciosamente** (sin error).

---

## La Application Surface

### `application_surface`
- **Devuelve:** `Surface`
- **Qué hace:** variable global e integrada que da acceso a la Application Surface, utilizable con
  **cualquiera** de las funciones de superficie.
- **Ejemplo:**
```gml
// Aplicar un shader a toda la escena
shader_set(sh_vineta);
draw_surface(application_surface, 0, 0);
shader_reset();
```
- **Notas / trampas:**
  - **Lo único que no puedes hacer con ella es liberarla** (`surface_free`). Siempre existe, aunque
    el handle para acceder a ella pueda cambiar.
  - Se crea la primera vez que se llama a un evento de dibujo en cada room nueva, por lo que no se
    dibuja nada hasta ese momento. Puedes consultar su posición y redimensionarla en el Create sin
    error.

**Orden de eventos de la Application Surface:**

| Evento | Qué ocurre |
|---|---|
| Pre-Draw | Se crea la Application Surface (si no existía) y se fija como destino de render |
| Draw Begin / Draw / Draw End | Para cada viewport visible (o una vez si no hay viewports). **Aquí se restablece el destino** |
| Post-Draw | La Application Surface se dibuja al búfer de pantalla (desactivable con `application_surface_draw_enable`) |
| Draw GUI Begin / Draw GUI / Draw GUI End | Dibujo de interfaz |

### `application_surface_enable(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la Application Surface. Por defecto está **activada**; al
  desactivarla, todo se dibuja directamente al búfer de pantalla.
- **Ejemplo:**
```gml
// Renderizado directo para máximo rendimiento en un juego 2D simple
application_surface_enable(false);
```

### `application_surface_is_enabled()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la Application Surface está habilitada.
- **Ejemplo:**
```gml
if (application_surface_is_enabled()) draw_surface(application_surface, 0, 0);
```

### `application_surface_draw_enable(flag)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva el **dibujado automático** de la Application Surface. Por defecto
  está activado. Desactivarlo es el paso previo para dibujarla tú mismo, normalmente con un shader.
- **Ejemplo:**
```gml
// Evento Create
application_surface_draw_enable(false);

// Evento Draw GUI (o Post-Draw)
shader_set(sh_pixelado);
draw_surface(application_surface, 0, 0);
shader_reset();
```

### `application_surface_is_draw_enabled()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el dibujado automático de la Application Surface está activo.
- **Ejemplo:**
```gml
if (!application_surface_is_draw_enabled())
{
    draw_surface(application_surface, 0, 0);
}
```

### `application_get_position()`
- **Devuelve:** `Array` de 4 elementos
- **Qué hace:** devuelve la posición de la Application Surface:

  | Índice | Contenido |
  |---|---|
  | `[0]` | x de la esquina superior izquierda |
  | `[1]` | y de la esquina superior izquierda |
  | `[2]` | x de la esquina inferior derecha |
  | `[3]` | y de la esquina inferior derecha |

  Todo relativo al tamaño de la pantalla o ventana.
- **Ejemplo:**
```gml
// Si dibujas tú la Application Surface, respeta su posición y escala
var _pos = application_get_position();
var _xx = _pos[0];
var _yy = _pos[1];
var _ww = _pos[2] - _pos[0];
var _hh = _pos[3] - _pos[1];

draw_surface_stretched(application_surface, _xx, _yy, _ww, _hh);
```
- **Notas / trampas:** con la opción *maintain aspect ratio* activada en las Game Options,
  GameMaker centra y escala la superficie automáticamente. Si tomas el control del dibujado, esta
  función te dice **exactamente dónde** se estaba dibujando para que puedas alinear tu interfaz.

---

## Tabla resumen

| Función | Devuelve |
|---|---|
| `surface_create(w, h, [format])` | `Surface` |
| `surface_create_ext(name, w, h)` | `Surface` |
| `surface_resize(surface_id, w, h)` | `N/A` |
| `surface_free(surface)` | `N/A` |
| `surface_exists(surface)` | `Boolean` |
| `surface_get_width(surface_id)` | `Real` |
| `surface_get_height(surface_id)` | `Real` |
| `surface_get_texture(surface_id)` | `Texture` |
| `surface_get_texture_depth(surface)` | `Texture` |
| `surface_get_format(surface_id)` | Constante de formato |
| `surface_format_is_supported(format)` | `Boolean` |
| `surface_set_target(surface, [depth])` | `Boolean` |
| `surface_set_target_ext(index, surface_id)` | `Boolean` |
| `surface_get_target()` | `Real` |
| `surface_get_target_depth()` | `Real` |
| `surface_get_target_ext(index)` | `Real` |
| `surface_reset_target()` | `Boolean` |
| `surface_depth_disable(disable)` | `N/A` |
| `surface_get_depth_disable()` | `Boolean` |
| `surface_has_depth(surface)` | `Boolean` |
| `surface_copy(destination, x, y, source)` | `N/A` |
| `surface_copy_part(dest, x, y, src, xs, ys, ws, hs)` | `N/A` |
| `surface_getpixel(surface_id, x, y)` | `Colour` o `Array` |
| `surface_getpixel_ext(surface_id, x, y)` | `Real` o `Array` |
| `surface_save(surface_id, fname)` | `N/A` |
| `surface_save_part(surface_id, fname, x, y, w, h)` | `N/A` |
| `draw_surface(id, x, y)` | `N/A` |
| `draw_surface_ext(id, x, y, xs, ys, rot, col, alpha)` | `N/A` |
| `draw_surface_part(surface, left, top, w, h, x, y)` | `N/A` |
| `draw_surface_part_ext(surf, left, top, w, h, x, y, xs, ys, col, alpha)` | `N/A` |
| `draw_surface_stretched(surface, x, y, w, h)` | `N/A` |
| `draw_surface_stretched_ext(surface, x, y, w, h, colour, alpha)` | `N/A` |
| `draw_surface_tiled(surface, x, y)` | `N/A` |
| `draw_surface_tiled_ext(surface, x, y, xs, ys, colour, alpha)` | `N/A` |
| `draw_surface_general(surf, left, top, w, h, x, y, xs, ys, rot, c1..c4, alpha)` | `N/A` |
| `buffer_get_surface(buffer, surface, offset)` | `N/A` |
| `buffer_set_surface(buffer, surface, offset)` | `N/A` |
| `application_surface` (variable global) | `Surface` |
| `application_surface_enable(enable)` | `N/A` |
| `application_surface_is_enabled()` | `Boolean` |
| `application_surface_draw_enable(flag)` | `N/A` |
| `application_surface_is_draw_enabled()` | `Boolean` |
| `application_get_position()` | `Array` |

**Total: 42 funciones + 1 variable global (`application_surface`) = 43 entradas documentadas.**

---

## Fuentes

- Surfaces — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/Surfaces.htm
- `surface_create` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_create.htm
- `surface_create_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_create_ext.htm
- `surface_resize` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_resize.htm
- `surface_free` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_free.htm
- `surface_exists` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_exists.htm
- `surface_get_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_width.htm
- `surface_get_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_height.htm
- `surface_get_texture` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_texture.htm
- `surface_get_texture_depth` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_texture_depth.htm
- `surface_get_format` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_format.htm
- `surface_format_is_supported` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_format_is_supported.htm
- `surface_set_target` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_set_target.htm
- `surface_set_target_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_set_target_ext.htm
- `surface_get_target` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_target.htm
- `surface_get_target_depth` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_target_depth.htm
- `surface_get_target_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_target_ext.htm
- `surface_reset_target` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_reset_target.htm
- `surface_depth_disable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_depth_disable.htm
- `surface_get_depth_disable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_get_depth_disable.htm
- `surface_has_depth` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_has_depth.htm
- `surface_copy` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_copy.htm
- `surface_copy_part` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_copy_part.htm
- `surface_getpixel` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_getpixel.htm
- `surface_getpixel_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_getpixel_ext.htm
- `surface_save` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_save.htm
- `surface_save_part` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_save_part.htm
- `draw_surface` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface.htm
- `draw_surface_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface_ext.htm
- `draw_surface_part` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface_part.htm
- `draw_surface_part_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface_part_ext.htm
- `draw_surface_stretched` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface_stretched.htm
- `draw_surface_stretched_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface_stretched_ext.htm
- `draw_surface_tiled` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface_tiled.htm
- `draw_surface_tiled_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface_tiled_ext.htm
- `draw_surface_general` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/draw_surface_general.htm
- `buffer_get_surface` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Buffers/buffer_get_surface.htm
- `buffer_set_surface` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Buffers/buffer_set_surface.htm
- `application_surface` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/application_surface.htm
- `application_surface_enable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/application_surface_enable.htm
- `application_surface_is_enabled` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/application_surface_is_enabled.htm
- `application_surface_draw_enable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/application_surface_draw_enable.htm
- `application_surface_is_draw_enabled` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/application_surface_is_draw_enabled.htm
- `application_get_position` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/application_get_position.htm
