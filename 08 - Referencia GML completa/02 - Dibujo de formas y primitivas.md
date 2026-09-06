# 02 — Dibujo de formas y primitivas

> Referencia completa de GML para **GameMaker LTS 2026.0** (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Áreas: `Drawing/Basic_Forms/`, `Drawing/Primitives/`, `Drawing/Lighting/` y parte de
> `Drawing/Colour_And_Alpha/`.

---

## Índice

1. [Advertencia de rendimiento común](#advertencia-de-rendimiento-común)
2. [Líneas y puntos](#líneas-y-puntos)
3. [Rectángulos](#rectángulos)
4. [Rectángulos redondeados](#rectángulos-redondeados)
5. [Círculos y elipses](#círculos-y-elipses)
6. [Triángulos](#triángulos)
7. [Formas compuestas y utilidades](#formas-compuestas-y-utilidades)
8. [Lectura de píxeles](#lectura-de-píxeles)
9. [Primitivas inmediatas (`draw_primitive_*`)](#primitivas-inmediatas-draw_primitive_)
10. [Iluminación 3D](#iluminación-3d)
11. [Funciones que NO existen](#funciones-que-no-existen)
12. [Tabla resumen](#tabla-resumen)
13. [Fuentes](#fuentes)

---

## Advertencia de rendimiento común

El manual es tajante sobre las funciones de esta sección:

> **IMPORTANTE** Estas funciones son lentas al llamarlas y solo se suministran como herramientas
> básicas de dibujo.
>
> **IMPORTANTE** Estas funciones **rompen el *vertex batching*** y aumentan el número de cambios de
> textura en tu juego, así que tener múltiples llamadas a cualquiera de ellas en un mismo frame de
> dibujo puede provocar problemas de rendimiento.

Además:

- **Las líneas, puntos y formas se dibujan siempre a escala 1:1 con la resolución de pantalla**,
  independientemente del evento en el que se dibujen.
- Solo surten efecto en **eventos de dibujo**.
- **No generan eventos de colisión**: son puramente gráficas.
- Todas respetan el color, alfa y modo de mezcla actuales.
- **Aviso importante con shaders:** la mayoría de shaders esperan las entradas *vértice, textura y
  color*. Estas funciones solo envían **vértice y color**, por lo que un shader puede no dibujar
  nada al aplicarse sobre ellas. Si necesitas dibujar formas con shader, personalízalo sabiendo que
  no llega coordenada de textura.

---

## Líneas y puntos

### `draw_line(x1, y1, x2, y2)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja una línea de **1 píxel** de grosor entre dos puntos.
- **Ejemplo:**
```gml
// Línea de visión desde el enemigo hasta el jugador
draw_set_colour(c_red);
draw_line(x, y, obj_player.x, obj_player.y);
```
- **Notas / trampas:** según la plataforma puede necesitar ±1 en las coordenadas para que el grosor
  sea el deseado.

### `draw_line_colour(x1, y1, x2, y2, col1, col2)`
- **Devuelve:** `N/A`
- **Qué hace:** línea de 1 píxel con degradado de `col1` (inicio) a `col2` (fin). Sustituye al color
  fijado con `draw_set_colour()`.
- **Ejemplo:**
```gml
// Rayo láser que se desvanece hacia el final
draw_line_colour(x, y, x + 300, y, c_yellow, make_colour_rgb(255, 80, 0));
```

### `draw_line_width(x1, y1, x2, y2, w)`
- **Devuelve:** `N/A`
- **Qué hace:** línea del grosor indicado en píxeles.
- **Ejemplo:**
```gml
// Cable de grosor 4
draw_line_width(x, y, obj_ancla.x, obj_ancla.y, 4);
```
- **Notas / trampas:** consume más que `draw_line`; úsala solo cuando necesites grosor.

### `draw_line_width_colour(x1, y1, x2, y2, w, col1, col2)`
- **Devuelve:** `N/A`
- **Qué hace:** línea con grosor y degradado de color combinados.
- **Ejemplo:**
```gml
// Barra de energía dibujada como línea gruesa degradada
draw_line_width_colour(x, y, x + 120, y, 8, c_lime, c_red);
```

### `draw_point(x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja un único píxel con el color y alfa actuales.
- **Ejemplo:**
```gml
// Sistema de partículas minimalista
for (var _i = 0; _i < 100; _i++)
{
    draw_point(irandom(room_width), irandom(room_height));
}
```
- **Notas / trampas:** es la función de forma más barata. Ideal para efectos de ruido o estrellas.

### `draw_point_colour(x, y, col1)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja un único píxel del color indicado, ignorando el color base.
- **Ejemplo:**
```gml
draw_point_colour(x, y, c_aqua);
```

---

## Rectángulos

### `draw_rectangle(x1, y1, x2, y2, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja un rectángulo relleno (`outline = false`) o un contorno de 1 píxel
  (`outline = true`). `(x1, y1)` es la esquina superior izquierda y `(x2, y2)` la inferior derecha.
- **Ejemplo:**
```gml
// Caja de colisión visible en modo depuración
draw_set_alpha(0.3);
draw_rectangle(bbox_left, bbox_top, bbox_right, bbox_bottom, false);
draw_set_alpha(1);
draw_rectangle(bbox_left, bbox_top, bbox_right, bbox_bottom, true);
```
- **Notas / trampas:** puede necesitar ±1 en x/y según plataforma para las dimensiones exactas.

### `draw_rectangle_colour(x1, y1, x2, y2, col1, col2, col3, col4, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** rectángulo con un color por esquina; si difieren se genera un degradado.
- **Orden:** `col1` = superior izquierda, `col2` = superior derecha, `col3` = inferior derecha,
  `col4` = inferior izquierda.
- **Ejemplo:**
```gml
// Degradado vertical de cielo
draw_rectangle_colour(0, 0, room_width, room_height,
                      c_navy, c_navy, c_aqua, c_aqua, false);
```
- **Notas / trampas:** el degradado se interpola por triángulos (el rectángulo son dos), igual que
  en `draw_sprite_general`.

---

## Rectángulos redondeados

### `draw_roundrect(x1, y1, x2, y2, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** rectángulo redondeado con **radio fijo**. La precisión de las esquinas depende de
  `draw_set_circle_precision()`.
- **Ejemplo:**
```gml
draw_roundrect(20, 20, 220, 90, false);
```
- **Notas / trampas:** si necesitas controlar el radio, usa `draw_roundrect_ext`.

### `draw_roundrect_colour(x1, y1, x2, y2, col1, col2, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** rectángulo redondeado con radio fijo y degradado del **centro** (`col1`) al
  **borde** (`col2`).
- **Ejemplo:**
```gml
// Botón con brillo central
draw_roundrect_colour(20, 20, 220, 90, c_white, c_gray, false);
```

### `draw_roundrect_ext(x1, y1, x2, y2, xrad, yrad, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** rectángulo redondeado con radios de curva independientes en X e Y, en píxeles.
- **Ejemplo:**
```gml
// Panel de diálogo con esquinas muy redondeadas
draw_roundrect_ext(40, 300, 600, 420, 24, 24, false);
```

### `draw_roundrect_colour_ext(x1, y1, x2, y2, xrad, yrad, col1, col2, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** combina radios personalizados con degradado centro → borde.
- **Ejemplo:**
```gml
// Notificación con degradado y esquinas suaves
draw_roundrect_colour_ext(40, 40, 400, 120, 16, 16, c_white, c_black, false);
```

---

## Círculos y elipses

### `draw_circle(x, y, r, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** círculo relleno o contorno de 1 píxel, con centro en `(x, y)` y radio `r`.
- **Ejemplo:**
```gml
// Radio de ataque
draw_set_alpha(0.2);
draw_circle(x, y, rango_ataque, false);
draw_set_alpha(1);
```

### `draw_circle_colour(x, y, r, col1, col2, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** círculo con degradado radial desde el **centro** (`col1`) hasta el **borde**
  (`col2`).
- **Ejemplo:**
```gml
// Explosión luminosa: blanco en el centro, naranja en el borde
draw_circle_colour(x, y, 64, c_white, c_orange, false);
```
- **Notas / trampas:** si `outline = true`, `col1` es irrelevante.

### `draw_ellipse(x1, y1, x2, y2, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** elipse inscrita en el rectángulo definido por las dos esquinas.
- **Ejemplo:**
```gml
// Sombra elíptica bajo el personaje
draw_set_colour(c_black);
draw_set_alpha(0.35);
draw_ellipse(x - 30, y - 8, x + 30, y + 8, false);
draw_set_alpha(1);
```

### `draw_ellipse_colour(x1, y1, x2, y2, col1, col2, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** elipse con degradado del centro al borde.
- **Ejemplo:**
```gml
draw_ellipse_colour(x - 60, y - 20, x + 60, y + 20, c_yellow, c_red, false);
```

### `draw_set_circle_precision(precision)`
- **Devuelve:** `N/A`
- **Qué hace:** fija con cuántos lados se aproximan los círculos y elipses. GameMaker no dibuja
  círculos reales: dibuja **polígonos** con suficientes lados para parecerlo.
- **Ejemplo:**
```gml
// Círculos pequeños: menos precisión, más rendimiento
draw_set_circle_precision(8);
draw_circle(x, y, 4, false);

// Círculo grande de interfaz: máxima suavidad
draw_set_circle_precision(64);
draw_circle(x, y, 200, false);
```
- **Notas / trampas:**
  - Rango válido: **4 a 64**.
  - **El valor debe ser divisible por 4** (4, 8, 12, …, 64).
  - Valor por defecto: **24**.
  - Afecta también a las esquinas de `draw_roundrect*`.

---

## Triángulos

### `draw_triangle(x1, y1, x2, y2, x3, y3, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** triángulo relleno o en contorno definido por tres vértices.
- **Ejemplo:**
```gml
// Indicador de dirección sobre la cabeza del personaje
var _dir = point_direction(x, y, mouse_x, mouse_y);
var _d = point_distance(x, y, mouse_x, mouse_y);
draw_triangle(x + lengthdir_x(20, _dir), y + lengthdir_y(20, _dir),
              x + lengthdir_x(12, _dir - 140), y + lengthdir_y(12, _dir - 140),
              x + lengthdir_x(12, _dir + 140), y + lengthdir_y(12, _dir + 140),
              false);
```

### `draw_triangle_colour(x1, y1, x2, y2, x3, y3, col1, col2, col3, outline)`
- **Devuelve:** `N/A`
- **Qué hace:** triángulo con un color por vértice e interpolación entre ellos.
- **Ejemplo:**
```gml
draw_triangle_colour(100, 100, 300, 100, 200, 300,
                     c_red, c_lime, c_blue, false);
```

---

## Formas compuestas y utilidades

### `draw_arrow(x1, y1, x2, y2, size)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja una flecha desde `(x1, y1)` hasta `(x2, y2)`. El mástil se traza entre ambos
  puntos y la punta se dibuja **al final**, ocupando `size` píxeles **descontados del mástil**, de
  modo que el extremo de la punta coincide exactamente con `(x2, y2)`. El ancho de la punta se
  calcula automáticamente en proporción a la longitud.
- **Ejemplo:**
```gml
// Flecha de fuerza de disparo: crece al arrastrar el ratón
draw_arrow(x, y, mouse_x, mouse_y, 16);
```

### `draw_button(x1, y1, x2, y2, up)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja un botón rectangular muy simple con borde biselado, usando el color y alfa
  actuales. `up = true` lo dibuja en relieve (sin pulsar); `up = false`, hundido.
- **Ejemplo:**
```gml
// Botón que responde al ratón
var _pulsado = point_in_rectangle(mouse_x, mouse_y, 100, 100, 260, 140) && mouse_check_button(mb_left);
draw_button(100, 100, 260, 140, !_pulsado);
```
- **Notas / trampas:** es una función heredada y muy limitada visualmente; para interfaces reales
  usa sprites con Nine Slice.

### `draw_healthbar(x1, y1, x2, y2, amount, backcol, mincol, maxcol, direction, showback, showborder)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja una barra de progreso. Pese al nombre sirve para vida, maná, energía, tiempo…
  cualquier valor expresable como **porcentaje entre 0 y 100**.
- **Argumento `direction`** (anclaje de la barra):

  | Valor | Anclaje |
  |---|---|
  | `0` | izquierda |
  | `1` | derecha |
  | `2` | arriba |
  | `3` | abajo |

- **Ejemplo:**
```gml
// Barra de vida del jugador, de izquierda a derecha, con fondo y borde
var _porcentaje = (vida / vida_maxima) * 100;
draw_healthbar(20, 20, 220, 44, _porcentaje,
               c_black, c_red, c_lime, 0, true, true);
```
- **Notas / trampas:**
  - `mincol` es el color cuando el valor es **0**; `maxcol` cuando es **100**. Entre ambos se
    interpola.
  - Si `showback = false`, el argumento `backcol` se ignora.
  - `showborder` añade un borde negro de 1 píxel a los elementos.

### `draw_path(path, x, y, absolute)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja un **path asset** como línea simple, en la posición absoluta en la que se
  creó (`absolute = true`) o relativa a la instancia (`absolute = false`).
- **Ejemplo:**
```gml
// Depurar rutas generadas con mp_grid_path()
draw_set_colour(c_lime);
draw_path(ruta, x, y, true);
```
- **Notas / trampas:** es una herramienta de **depuración**; resulta muy útil con paths dinámicos
  creados por `mp_grid_path()`.

---

## Lectura de píxeles

### `draw_getpixel(x, y)`
- **Devuelve:** `Colour`
- **Qué hace:** devuelve el color del píxel que se está dibujando en el **destino de dibujo actual**
  en las coordenadas indicadas.
- **Ejemplo:**
```gml
// Detectar si el suelo bajo el jugador es de un color concreto
var _color_suelo = draw_getpixel(x, y + 1);
if (_color_suelo == c_black) show_debug_message("Suelo negro");
```
- **Notas / trampas:**
  - **IMPORTANTE (textual del manual): provoca un impacto de rendimiento enorme** y solo debe usarse
    cuando sea absolutamente necesario.
  - El resultado depende del evento y del destino de dibujo activo.
  - **No devuelve el alfa**. Para eso usa `draw_getpixel_ext`.

### `draw_getpixel_ext(x, y)`
- **Devuelve:** `Real` — valor completo **AGBR de 32 bits**
- **Qué hace:** igual que `draw_getpixel` pero devolviendo también el canal alfa.
- **Ejemplo:**
```gml
// Extraer componentes de un valor AGBR de 32 bits
var _agbr = draw_getpixel_ext(x, y);
var _alfa  = (_agbr >> 24) & 255;
var _azul  = (_agbr >> 16) & 255;
var _verde = (_agbr >>  8) & 255;
var _rojo  =  _agbr        & 255;
```
- **Notas / trampas:** misma advertencia de rendimiento enorme.

---

## Primitivas inmediatas (`draw_primitive_*`)

Las primitivas inmediatas permiten definir geometría vértice a vértice **directamente en el frame**,
sin crear un vertex buffer. Son la vía rápida para efectos puntuales.

### Tipos de primitiva

| Constante | Descripción |
|---|---|
| `pr_pointlist` | Lista de puntos: se dibuja un punto por cada vértice |
| `pr_linelist` | Lista de líneas: 1-2, 3-4, 5-6… |
| `pr_linestrip` | Tira de líneas: 1-2, 2-3, 3-4… |
| `pr_trianglelist` | Lista de triángulos: 1-2-3, 4-5-6… |
| `pr_trianglestrip` | Tira de triángulos: 1-2-3, 2-3-4, 3-4-5… |
| `pr_trianglefan` | Abanico: cada dos vértices se unen al primero para formar un triángulo |

- **Aviso sobre `pr_trianglefan`:** no tiene soporte nativo en todas las plataformas (Windows,
  Xbox). GameMaker lo **convierte en tiempo de compilación**, por lo que en esas plataformas es
  **mucho más lento** que los demás tipos. Evítalo si buscas rendimiento.
- En HTML5 requiere WebGL activado.

### `draw_primitive_begin(kind)`
- **Devuelve:** `N/A`
- **Qué hace:** inicia la definición de una primitiva **sin textura**. Debe llamarse antes de
  definir cualquier vértice.
- **Ejemplo:**
```gml
// Triángulo de color liso
draw_primitive_begin(pr_trianglelist);
draw_vertex_colour(100, 100, c_red,   1);
draw_vertex_colour(200, 100, c_lime,  1);
draw_vertex_colour(150, 200, c_blue,  1);
draw_primitive_end();
```

### `draw_primitive_begin_texture(kind, tex)`
- **Devuelve:** `N/A`
- **Qué hace:** inicia una primitiva **con textura**. El `tex` se obtiene normalmente con
  `sprite_get_texture()` o `surface_get_texture()`. Usa `-1` para ninguna textura.
- **Ejemplo:**
```gml
// Bandera ondulante hecha con una tira de triángulos
var _tex = sprite_get_texture(spr_bandera, 0);
draw_primitive_begin_texture(pr_trianglestrip, _tex);
for (var _i = 0; _i <= 10; _i++)
{
    var _px = x + _i * 12;
    var _onda = sin(current_time * 0.005 + _i * 0.6) * 8;
    draw_vertex_texture(_px, y + _onda,        _i / 10, 0);
    draw_vertex_texture(_px, y + 60 + _onda,   _i / 10, 1);
}
draw_primitive_end();
```

### `draw_primitive_end()`
- **Devuelve:** `N/A`
- **Qué hace:** finaliza la definición de la primitiva y **la dibuja**.
- **Ejemplo:**
```gml
draw_primitive_end();
```
- **Notas / trampas:** si no la llamas, **no se dibuja nada**.

### `draw_vertex(x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** define la posición de un vértice, usando el color y alfa actuales.
- **Ejemplo:**
```gml
draw_primitive_begin(pr_linelist);
draw_vertex(0, 0);
draw_vertex(100, 100);
draw_primitive_end();
```

### `draw_vertex_colour(x, y, col, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** define un vértice **con su propio color y alfa**. Los vértices con colores distintos
  se interpolan suavemente entre sí.
- **Ejemplo:**
```gml
// Abanico de triángulos degradado
draw_primitive_begin(pr_trianglefan);
draw_vertex_colour(x, y, c_white, 1);
for (var _a = 0; _a <= 360; _a += 30)
{
    draw_vertex_colour(x + lengthdir_x(60, _a), y + lengthdir_y(60, _a),
                       make_colour_hsv(_a, 200, 255), 0.6);
}
draw_primitive_end();
```

### `draw_vertex_texture(x, y, xtex, ytex)`
- **Devuelve:** `N/A`
- **Qué hace:** define un vértice con coordenadas de textura (UV).
- **Ejemplo:**
```gml
// Quad texturizado completo
var _tex = sprite_get_texture(spr_fondo, 0);
draw_primitive_begin_texture(pr_trianglestrip, _tex);
draw_vertex_texture(  0,   0, 0, 0);
draw_vertex_texture(320,   0, 1, 0);
draw_vertex_texture(  0, 240, 0, 1);
draw_vertex_texture(320, 240, 1, 1);
draw_primitive_end();
```
- **Notas / trampas:**
  - **Mapeo UV de `draw_vertex_texture`:** `(0, 0)` es la esquina superior izquierda **de la región
    del sprite dentro de la página de textura** y `(1, 1)` la inferior derecha de esa región.
  - Esto es **distinto** de `vertex_texcoord()` en vertex buffers, donde `(0, 0)`–`(1, 1)` cubre la
    **página de textura completa**. Con buffers usa `sprite_get_uvs()` para obtener el rango.

### `draw_vertex_texture_colour(x, y, xtex, ytex, col, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** vértice con textura, color de mezcla y alfa.
- **Ejemplo:**
```gml
// Textura teñida de rojo y semitransparente
var _tex = sprite_get_texture(spr_fantasma, 0);
draw_primitive_begin_texture(pr_trianglestrip, _tex);
draw_vertex_texture_colour(0, 0, 0, 0, c_red, 0.5);
draw_vertex_texture_colour(64, 0, 1, 0, c_red, 0.5);
draw_vertex_texture_colour(0, 64, 0, 1, c_red, 0.5);
draw_vertex_texture_colour(64, 64, 1, 1, c_red, 0.5);
draw_primitive_end();
```
- **Notas / trampas:** para conservar el aspecto de la textura y cambiar solo el alfa, pasa `-1` o
  `c_white` como color.

---

## Iluminación 3D

El sistema de iluminación integrado da realismo a escenas 3D, donde las caras de las primitivas
tienen un color plano independiente de su orientación.

> **Requisito indispensable:** las funciones de iluminación necesitan una **propiedad normal** en el
> formato de vértice de lo que se dibuje. Por tanto **no funcionan con funciones de dibujo
> normales** como `draw_sprite`; los vertex buffers que quieran usar iluminación deben incluir
> normales en su formato (ver `vertex_format_add_normal()` en el archivo **07**).

### `draw_set_lighting(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva **todos** los efectos de iluminación. Por defecto está
  **desactivado** (`false`).
- **Ejemplo:**
```gml
draw_set_lighting(true);
```

### `draw_get_lighting()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la iluminación está activa para toda la escena.
- **Ejemplo:**
```gml
if (!draw_get_lighting()) draw_set_lighting(true);
```

### `draw_light_define_ambient(col)`
- **Devuelve:** `N/A`
- **Qué hace:** define la **luz ambiental**: la que existe en la escena sin haber definido ninguna
  fuente puntual ni direccional. Es, en la práctica, el color y brillo generales.
- **Ejemplo:**
```gml
// Luz ambiental tenue azulada para una escena nocturna
draw_light_define_ambient(make_colour_rgb(20, 24, 40));
```
- **Notas / trampas:** el color por defecto es `c_black` (oscuridad total).

### `draw_light_define_point(ind, x, y, z, range, col)`
- **Devuelve:** `N/A`
- **Qué hace:** define una **luz puntual** (posicional) con posición en el espacio 3D, radio de
  alcance en píxeles y color.
- **Ejemplo:**
```gml
// Antorcha que sigue al jugador
draw_light_define_point(0, obj_player.x, obj_player.y, 40, 220, c_orange);
draw_light_enable(0, true);
```
- **Notas / trampas:**
  - **Solo hay 8 luces hardware disponibles**: como máximo 8 definidas pueden estar activas a la vez
    (aunque puedes definir más).
  - El color afecta a la intensidad percibida: algunos colores «oscurecen» más que otros.
  - `ind` es un índice arbitrario que luego usan `draw_light_enable` y `draw_light_get`.

### `draw_light_define_direction(ind, x, y, z, col)`
- **Devuelve:** `N/A`
- **Qué hace:** define una **luz direccional** (como el sol). El vector de dirección se guarda
  **normalizado** y se **niega** antes de enviarse al shader.
- **Ejemplo:**
```gml
// Sol: luz direccional cálida
draw_light_define_direction(1, -1, -1, -0.5, c_yellow);
draw_light_enable(1, true);
```
- **Notas / trampas:** mismo límite de 8 luces hardware.

### `draw_light_enable(ind, enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva una luz previamente definida. Por defecto las luces están
  **desactivadas**.
- **Ejemplo:**
```gml
// Interrumpe la luz al pulsar un interruptor
draw_light_enable(0, !interruptor_apagado);
```

### `draw_light_get_ambient()`
- **Devuelve:** `Colour`
- **Qué hace:** devuelve el color actual de la luz ambiental.
- **Ejemplo:**
```gml
var _amb = draw_light_get_ambient();
show_debug_message($"Ambiente: {_amb}");
```
- **Notas / trampas:** el valor por defecto es `c_black` con alfa 1 (opaco).

### `draw_light_get(ind)`
- **Devuelve:** `Array` de 7 elementos
- **Qué hace:** devuelve los parámetros de la luz indicada.

  | Índice | Contenido |
  |---|---|
  | `[0]` | activada / desactivada (`true` / `false`) |
  | `[1]` | constante de tipo de luz |
  | `[2]` | valor x |
  | `[3]` | valor y |
  | `[4]` | valor z |
  | `[5]` | radio de la luz (siempre `1` en luces direccionales) |
  | `[6]` | color de la luz (un real) |

  Constantes de tipo:

  | Constante | Significado |
  |---|---|
  | `lighttype_dir` | luz direccional |
  | `lighttype_point` | luz puntual |

- **Ejemplo:**
```gml
// Hace crecer el radio de la luz 1 hasta 200
var _luz = draw_light_get(1);
if (_luz[5] < 200)
{
    _luz[5] += 5;
    draw_light_define_point(1, 200, 123, 50, _luz[5], c_white);
}
```
- **Notas / trampas:** los valores `[2]`, `[3]` y `[4]` guardan la **posición** en luces puntuales y
  el **vector de dirección normalizado** en luces direccionales.

---

## Funciones que NO existen

Durante la verificación se comprobó que las siguientes funciones solicitadas **no existen** en el
manual de GameMaker LTS 2026 (ni en el canal *monthly*, *lts* ni *beta*). No las uses:

| Función que no existe | Alternativa real |
|---|---|
| `draw_polygon()` | `draw_primitive_begin(pr_trianglefan)` + `draw_vertex*`, o un vertex buffer |
| `draw_mesh()` | Vertex buffers: `vertex_create_buffer()` + `vertex_submit()` (archivo **07**) |
| `draw_line_width_colour()` con más argumentos | la firma es exactamente `(x1, y1, x2, y2, w, col1, col2)` |

---

## Tabla resumen

| Función | Devuelve |
|---|---|
| `draw_line(x1, y1, x2, y2)` | `N/A` |
| `draw_line_colour(x1, y1, x2, y2, col1, col2)` | `N/A` |
| `draw_line_width(x1, y1, x2, y2, w)` | `N/A` |
| `draw_line_width_colour(x1, y1, x2, y2, w, col1, col2)` | `N/A` |
| `draw_point(x, y)` | `N/A` |
| `draw_point_colour(x, y, col1)` | `N/A` |
| `draw_rectangle(x1, y1, x2, y2, outline)` | `N/A` |
| `draw_rectangle_colour(x1, y1, x2, y2, c1, c2, c3, c4, outline)` | `N/A` |
| `draw_roundrect(x1, y1, x2, y2, outline)` | `N/A` |
| `draw_roundrect_colour(x1, y1, x2, y2, col1, col2, outline)` | `N/A` |
| `draw_roundrect_ext(x1, y1, x2, y2, xrad, yrad, outline)` | `N/A` |
| `draw_roundrect_colour_ext(x1, y1, x2, y2, xrad, yrad, col1, col2, outline)` | `N/A` |
| `draw_circle(x, y, r, outline)` | `N/A` |
| `draw_circle_colour(x, y, r, col1, col2, outline)` | `N/A` |
| `draw_ellipse(x1, y1, x2, y2, outline)` | `N/A` |
| `draw_ellipse_colour(x1, y1, x2, y2, col1, col2, outline)` | `N/A` |
| `draw_triangle(x1, y1, x2, y2, x3, y3, outline)` | `N/A` |
| `draw_triangle_colour(x1, y1, x2, y2, x3, y3, c1, c2, c3, outline)` | `N/A` |
| `draw_arrow(x1, y1, x2, y2, size)` | `N/A` |
| `draw_button(x1, y1, x2, y2, up)` | `N/A` |
| `draw_healthbar(... 11 args)` | `N/A` |
| `draw_path(path, x, y, absolute)` | `N/A` |
| `draw_set_circle_precision(precision)` | `N/A` |
| `draw_getpixel(x, y)` | `Colour` |
| `draw_getpixel_ext(x, y)` | `Real` (AGBR 32 bits) |
| `draw_primitive_begin(kind)` | `N/A` |
| `draw_primitive_begin_texture(kind, tex)` | `N/A` |
| `draw_primitive_end()` | `N/A` |
| `draw_vertex(x, y)` | `N/A` |
| `draw_vertex_colour(x, y, col, alpha)` | `N/A` |
| `draw_vertex_texture(x, y, xtex, ytex)` | `N/A` |
| `draw_vertex_texture_colour(x, y, xtex, ytex, col, alpha)` | `N/A` |
| `draw_set_lighting(enable)` | `N/A` |
| `draw_get_lighting()` | `Boolean` |
| `draw_light_define_ambient(col)` | `N/A` |
| `draw_light_define_point(ind, x, y, z, range, col)` | `N/A` |
| `draw_light_define_direction(ind, x, y, z, col)` | `N/A` |
| `draw_light_enable(ind, enable)` | `N/A` |
| `draw_light_get_ambient()` | `Colour` |
| `draw_light_get(ind)` | `Array` |

**Total: 40 funciones documentadas** (+ 6 constantes de tipo de primitiva, 2 de tipo de luz).

---

## Fuentes

- Basic Forms — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/Basic_Forms.htm
- `draw_arrow` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_arrow.htm
- `draw_button` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_button.htm
- `draw_circle` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_circle.htm
- `draw_circle_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_circle_colour.htm
- `draw_ellipse` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_ellipse.htm
- `draw_ellipse_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_ellipse_colour.htm
- `draw_line` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_line.htm
- `draw_line_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_line_colour.htm
- `draw_line_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_line_width.htm
- `draw_line_width_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_line_width_colour.htm
- `draw_point` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_point.htm
- `draw_point_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_point_colour.htm
- `draw_rectangle` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_rectangle.htm
- `draw_rectangle_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_rectangle_colour.htm
- `draw_roundrect` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_roundrect.htm
- `draw_roundrect_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_roundrect_colour.htm
- `draw_roundrect_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_roundrect_ext.htm
- `draw_roundrect_colour_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_roundrect_colour_ext.htm
- `draw_triangle` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_triangle.htm
- `draw_triangle_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_triangle_colour.htm
- `draw_set_circle_precision` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_set_circle_precision.htm
- `draw_healthbar` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_healthbar.htm
- `draw_path` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_path.htm
- `draw_getpixel` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_getpixel.htm
- `draw_getpixel_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_getpixel_ext.htm
- Primitives And Vertex Formats — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/Primitives_And_Vertex_Formats.htm
- `draw_primitive_begin` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_primitive_begin.htm
- `draw_primitive_begin_texture` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_primitive_begin_texture.htm
- `draw_primitive_end` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_primitive_end.htm
- `draw_vertex` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_vertex.htm
- `draw_vertex_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_vertex_colour.htm
- `draw_vertex_texture` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_vertex_texture.htm
- `draw_vertex_texture_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_vertex_texture_colour.htm
- Lighting — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/Lighting.htm
- `draw_set_lighting` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/draw_set_lighting.htm
- `draw_get_lighting` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/draw_get_lighting.htm
- `draw_light_define_ambient` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/draw_light_define_ambient.htm
- `draw_light_define_point` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/draw_light_define_point.htm
- `draw_light_define_direction` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/draw_light_define_direction.htm
- `draw_light_enable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/draw_light_enable.htm
- `draw_light_get_ambient` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/draw_light_get_ambient.htm
- `draw_light_get` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Lighting/draw_light_get.htm
