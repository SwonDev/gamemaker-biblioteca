# 04 — Color y blending

> Referencia completa de GML para **GameMaker LTS 2026.0** (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Áreas: `Drawing/Colour_And_Alpha/`, `Drawing/GPU_Control/`, `Drawing/Mipmapping/` y
> `Drawing/Depth_And_Stencil_Buffer/`.
> **102 funciones documentadas.**

---

## Índice

1. [Cómo funciona el color en GML](#cómo-funciona-el-color-en-gml)
2. [Constantes de color](#constantes-de-color)
3. [Componentes de color](#componentes-de-color)
4. [Creación y mezcla de colores](#creación-y-mezcla-de-colores)
5. [Color y alfa de dibujo](#color-y-alfa-de-dibujo)
6. [Cómo funciona el blending](#cómo-funciona-el-blending)
7. [Modos de mezcla](#modos-de-mezcla)
8. [Factores de mezcla](#factores-de-mezcla)
9. [Ecuaciones de mezcla](#ecuaciones-de-mezcla)
10. [Escritura de canales y alpha test](#escritura-de-canales-y-alpha-test)
11. [Pila de estado de la GPU](#pila-de-estado-de-la-gpu)
12. [Culling](#culling)
13. [Búfer de profundidad (Z-buffer)](#búfer-de-profundidad-z-buffer)
14. [Niebla (fog)](#niebla-fog)
15. [Filtrado y repetición de texturas](#filtrado-y-repetición-de-texturas)
16. [Región de recorte (scissor)](#región-de-recorte-scissor)
17. [Búfer de stencil](#búfer-de-stencil)
18. [Mipmapping](#mipmapping)
19. [Frustum culling de sprites](#frustum-culling-de-sprites)
20. [Funciones legacy sin página en el manual](#funciones-legacy-sin-página-en-el-manual)
21. [Tabla resumen](#tabla-resumen)
22. [Fuentes](#fuentes)

---

## Cómo funciona el color en GML

Un color en GameMaker es un **entero de 32 bits** con los componentes empaquetados en el orden
**BGR** (azul, verde, rojo) para los literales con `$`, o **RGB** para los literales con `#`.

```gml
// Formato $BBGGRR (azul, verde, rojo)
var _azul_claro = $FFCC11;

// Formato #RRGGBB (rojo, verde, azul) — mismo color que el anterior
var _mismo_color = #11CCFF;

// GML también acepta $AABBGGRR, pero la mayoría de funciones de color
// ignoran la parte del alfa y solo usan el color.
```

- **Evita usar códigos hexadecimales justo después de un corchete de apertura `[`**: GameMaker puede
  interpretarlos como un *accessor*.

---

## Constantes de color

| Constante | Valor decimal |
|---|---|
| `c_aqua` | 16776960 |
| `c_black` | 0 |
| `c_blue` | 16711680 |
| `c_dkgray` | 4210752 |
| `c_fuchsia` | 16711935 |
| `c_gray` | 8421504 |
| `c_green` | 32768 |
| `c_lime` | 65280 |
| `c_ltgray` | 12632256 |
| `c_maroon` | 128 |
| `c_navy` | 8388608 |
| `c_olive` | 32896 |
| `c_orange` | 4235519 |
| `c_purple` | 8388736 |
| `c_red` | 255 |
| `c_silver` | 12632256 |
| `c_teal` | 8421376 |
| `c_white` | 16777215 |
| `c_yellow` | 65535 |

---

## Componentes de color

### `colour_get_red(col)`
- **Devuelve:** `Real` (0–255)
- **Qué hace:** devuelve la cantidad de rojo del color.
- **Ejemplo:**
```gml
var _r = colour_get_red(image_blend);
```

### `colour_get_green(col)`
- **Devuelve:** `Real` (0–255)
- **Qué hace:** devuelve la cantidad de verde del color.
- **Ejemplo:**
```gml
var _g = colour_get_green(image_blend);
```

### `colour_get_blue(col)`
- **Devuelve:** `Real` (0–255)
- **Qué hace:** devuelve la cantidad de azul del color.
- **Ejemplo:**
```gml
var _b = colour_get_blue(image_blend);
```

**Ejemplo combinado — descomponer un color:**
```gml
// Oscurecer un color un 50 %
var _r = colour_get_red(_color)   * 0.5;
var _g = colour_get_green(_color) * 0.5;
var _b = colour_get_blue(_color)  * 0.5;
var _oscuro = make_colour_rgb(_r, _g, _b);
```

### `colour_get_hue(col)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el **tono** (*hue*) del color, dentro del modelo HSV.
- **Ejemplo:**
```gml
var _tono = colour_get_hue(c_orange);
```

### `colour_get_saturation(col)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve la **saturación** del color dentro del modelo HSV: cuánto del tono puro está
  mezclado en el color final.
- **Ejemplo:**
```gml
var _sat = colour_get_saturation(c_orange);
```

### `colour_get_value(col)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el **valor** o luminosidad del color dentro del modelo HSV: cuánta «luz»
  está mezclada en el color final.
- **Ejemplo:**
```gml
var _lum = colour_get_value(c_orange);
```

---

## Creación y mezcla de colores

### `make_colour_rgb(red, green, blue)`
- **Devuelve:** `Colour`
- **Qué hace:** crea un color a partir de los componentes rojo, verde y azul (cada uno 0–255).
- **Ejemplo:**
```gml
// Naranja personalizado
var _naranja = make_colour_rgb(255, 128, 0);
draw_set_colour(_naranja);
```

### `make_colour_hsv(hue, sat, val)`
- **Devuelve:** `Colour`
- **Qué hace:** crea un color a partir de tono, saturación y valor.
- **Ejemplo:**
```gml
// Arcoíris animado
var _color = make_colour_hsv(current_time mod 255, 200, 255);
draw_set_colour(_color);
```
- **Notas / trampas:** ideal para ciclos de color y efectos de «brillo» sin cálculos manuales.

### `merge_colour(col1, col2, amount)`
- **Devuelve:** `Colour`
- **Qué hace:** mezcla dos colores. `amount = 0` devuelve `col1`, `amount = 1` devuelve `col2`,
  y un valor intermedio devuelve la mezcla proporcional (`0.5` = mitad y mitad).
- **Ejemplo:**
```gml
// Barra de vida que va de rojo a verde según la vida restante
var _t = vida / vida_maxima;                 // 0..1
var _color = merge_colour(c_red, c_lime, _t);
draw_healthbar(20, 20, 220, 44, _t * 100, c_black, c_red, c_lime, 0, true, true);
```

---

## Color y alfa de dibujo

### `draw_set_colour(col)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el color base de dibujo para el juego.
- **Ejemplo:**
```gml
draw_set_colour(c_red);
draw_text(x, y, "Peligro");
draw_set_colour(c_white);
```
- **Notas / trampas:**
  - **Afecta a fuentes, formas, primitivas y 3D. NO afecta a los sprites**: para teñir un sprite usa
    `image_blend` o `draw_sprite_ext`.
  - El color base se multiplica por el color propio de cada vértice o sprite.

### `draw_get_colour()`
- **Devuelve:** `Colour`
- **Qué hace:** devuelve el color de dibujo actual.
- **Ejemplo:**
```gml
var _color_previo = draw_get_colour();
draw_set_colour(c_yellow);
draw_text(x, y, "Aviso");
draw_set_colour(_color_previo);
```

### `draw_set_alpha(alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el alfa de dibujo, entre `0` (transparente) y `1` (opaco).
- **Ejemplo:**
```gml
// Fundido a negro de la escena
draw_set_alpha(alfa_fundido);
draw_set_colour(c_black);
draw_rectangle(0, 0, room_width, room_height, false);
draw_set_alpha(1);
```

### `draw_get_alpha()`
- **Devuelve:** `Real` (0–1)
- **Qué hace:** devuelve el alfa de dibujo actual. Afecta a la transparencia de **todas** las
  funciones de dibujo.
- **Ejemplo:**
```gml
if (draw_get_alpha() < 1) draw_set_alpha(1);
```

---

## Cómo funciona el blending

Cuando GameMaker va a dibujar un píxel hay dos colores en juego:

- **Fuente** (*source*): el color del píxel que vamos a dibujar.
- **Destino** (*destination*): el color que ya hay en el píxel sobre el que dibujamos.

Cada componente se almacena como un valor en coma flotante entre 0 y 1. El color final se calcula
multiplicando cada componente del color fuente por un **factor**, cada componente del destino por
otro **factor**, y combinando los resultados según la **ecuación** elegida:

```
resultado = (fuente × factor_fuente)  ECUACIÓN  (destino × factor_destino)
```

Por defecto la ecuación es la suma, así que:

```
resultado = (fuente × factor_fuente) + (destino × factor_destino)
```

---

## Modos de mezcla

### `gpu_set_blendmode(mode)`
- **Devuelve:** `N/A`
- **Qué hace:** fija uno de los modos de mezcla básicos. Cada modo es en realidad una composición de
  factores y una ecuación:

  | Constante | Descripción | Modo extendido equivalente | Ecuación |
  |---|---|---|---|
  | `bm_normal` | Mezcla normal (**por defecto**) | (`bm_src_alpha`, `bm_inv_src_alpha`) | `bm_eq_add` |
  | `bm_add` | Mezcla aditiva: se suman las luminosidades | (`bm_src_alpha`, `bm_one`) | `bm_eq_add` |
  | `bm_subtract` | Mezcla sustractiva: la fuente se resta del destino | (`bm_zero`, `bm_inv_src_colour`) | `bm_eq_add` |
  | `bm_reverse_subtract` | Mezcla sustractiva inversa: el destino se resta de la fuente | (`bm_src_alpha`, `bm_one`) | `bm_eq_reverse_subtract` |
  | `bm_min` | Se selecciona el valor menor de fuente y destino | (`bm_one`, `bm_one`) | `bm_eq_min` |
  | `bm_max` | Mezcla máxima: similar a la aditiva | (`bm_src_alpha`, `bm_inv_src_colour`) | `bm_eq_add` |

- **Ejemplo:**
```gml
// Explosión con mezcla aditiva: los brillos se acumulan
gpu_set_blendmode(bm_add);
draw_sprite_ext(spr_explosion, 0, x, y, 2, 2, 0, c_white, 0.8);
gpu_set_blendmode(bm_normal); // SIEMPRE restaura
```
- **Notas / trampas:** **restaura siempre a `bm_normal`** después de usar un modo especial; es de
  ámbito global y afecta a todo el dibujo posterior.

### `gpu_get_blendmode()`
- **Devuelve:** constante de modo de mezcla
- **Qué hace:** devuelve el modo de mezcla actual.
- **Ejemplo:**
```gml
if (gpu_get_blendmode() != bm_normal) gpu_set_blendmode(bm_normal);
```

### `gpu_set_blendenable(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la **mezcla de alfa** por completo.
- **Ejemplo:**
```gml
// Dibujar sin blending: los píxeles sobrescriben directamente
gpu_set_blendenable(false);
draw_sprite(spr_mascara, 0, x, y);
gpu_set_blendenable(true);
```
- **Notas / trampas:** con la mezcla desactivada, el canal alfa del destino queda intacto, lo que
  produce resultados sorprendentes al trabajar con superficies.

### `gpu_get_blendenable()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la mezcla de alfa está activa.

### `gpu_set_blendmode_ext(src, dest)`
- **Devuelve:** `N/A`
- **Qué hace:** crea un modo de mezcla **personalizado** indicando el factor de la fuente y el del
  destino.
- **Ejemplo:**
```gml
// Mezcla aditiva pura: suma total de colores, sin atenuar por alfa
gpu_set_blendmode_ext(bm_one, bm_one);
draw_sprite(spr_luz, 0, x, y);
gpu_set_blendmode(bm_normal);
```
- **Notas / trampas:**
  - Puedes pasar dos argumentos individuales **o un array** de dos elementos (por ejemplo, el que
    devuelve `gpu_get_blendmode_ext()`):
    - `[0]` = modo de la fuente (por defecto `bm_src_alpha`)
    - `[1]` = modo del destino (por defecto `bm_inv_src_alpha`)
  - **En HTML5 sin WebGL no se muestran correctamente** los modos `bm_src_colour`,
    `bm_inv_src_colour`, `bm_dest_colour`, `bm_inv_dest_colour` y `bm_src_alpha_sat`.

### `gpu_get_blendmode_ext()`
- **Devuelve:** `Array` de 2 elementos `[src, dest]`
- **Qué hace:** devuelve los factores de mezcla extendidos actuales.
- **Ejemplo:**
```gml
var _modo = gpu_get_blendmode_ext();
// ... dibujar con otro modo ...
gpu_set_blendmode_ext(_modo[0], _modo[1]);
```

### `gpu_set_blendmode_ext_sepalpha(src, dest, alphasrc, alphadest)`
- **Devuelve:** `N/A`
- **Qué hace:** como `gpu_set_blendmode_ext` pero con factores **independientes** para los
  componentes RGB y para el componente alfa.
- **Ejemplo:**
```gml
// Multiplicar el color pero dejar el alfa intacto en el destino
gpu_set_blendmode_ext_sepalpha(bm_dest_colour, bm_zero, bm_zero, bm_one);
draw_rectangle(0, 0, room_width, room_height, false);
gpu_set_blendmode(bm_normal);
```
- **Notas / trampas:** es la vía para construir superficies solo de alfa y efectos de multiplicación
  selectiva.

### `gpu_get_blendmode_ext_sepalpha()`
- **Devuelve:** `Array` de 4 elementos `[src, dest, alphasrc, alphadest]`
- **Qué hace:** devuelve los cuatro factores actuales.

### `gpu_get_blendmode_src()`
- **Devuelve:** constante de factor
- **Qué hace:** devuelve el factor de la fuente.

### `gpu_get_blendmode_dest()`
- **Devuelve:** constante de factor
- **Qué hace:** devuelve el factor del destino.

### `gpu_get_blendmode_srcalpha()`
- **Devuelve:** constante de factor
- **Qué hace:** devuelve el factor de la fuente **para el canal alfa**.

### `gpu_get_blendmode_destalpha()`
- **Devuelve:** constante de factor
- **Qué hace:** devuelve el factor del destino **para el canal alfa**.

---

## Factores de mezcla

Once constantes utilizables como fuente, destino o ambos. Si la fuente tiene componentes
(Rs, Gs, Bs, As) y el destino (Rd, Gd, Bd, Ad):

| Constante | Factor (R, G, B, A) |
|---|---|
| `bm_zero` | (0, 0, 0, 0) |
| `bm_one` | (1, 1, 1, 1) |
| `bm_src_colour` | (Rs, Gs, Bs, As) |
| `bm_inv_src_colour` | (1−Rs, 1−Gs, 1−Bs, 1−As) |
| `bm_src_alpha` | (As, As, As, As) |
| `bm_inv_src_alpha` | (1−As, 1−As, 1−As, 1−As) |
| `bm_dest_alpha` | (Ad, Ad, Ad, Ad) |
| `bm_inv_dest_alpha` | (1−Ad, 1−Ad, 1−Ad, 1−Ad) |
| `bm_dest_colour` | (Rd, Gd, Bd, Ad) |
| `bm_inv_dest_colour` | (1−Rd, 1−Gd, 1−Bd, 1−Ad) |
| `bm_src_alpha_sat` | (f, f, f, 1) donde f = min(As, 1−Ad) |

> **IMPORTANTE:** HTML5 sin WebGL **no** mostrará correctamente `bm_src_colour`,
> `bm_inv_src_colour`, `bm_dest_colour`, `bm_inv_dest_colour` ni `bm_src_alpha_sat`.

---

## Ecuaciones de mezcla

### `gpu_set_blendequation(equation)`
- **Devuelve:** `N/A`
- **Qué hace:** cambia cómo se calcula el píxel final a partir de la fuente y el destino.

  | Constante | Ecuación | Resultado |
  |---|---|---|
  | `bm_eq_add` | `source + destination` | Suma ambos (**por defecto**) |
  | `bm_eq_subtract` | `destination − source` | Resta la fuente del destino |
  | `bm_eq_reverse_subtract` | `source − destination` | Resta el destino de la fuente |
  | `bm_eq_min` | `min(source, destination)` | El valor menor |
  | `bm_eq_max` | `max(source, destination)` | El valor mayor |

- **Ejemplo:**
```gml
// Agujero oscuro: resta el círculo del fondo
gpu_set_blendmode_ext(bm_src_alpha, bm_one);
gpu_set_blendequation(bm_subtract);
draw_circle(100, 100, 50, false);
gpu_set_blendmode(bm_normal); // restaura factores Y ecuación
```
- **Notas / trampas:**
  - **Los factores de mezcla no se aplican con `bm_eq_min` ni `bm_eq_max`**, lo que equivale a usar
    `bm_one` como factores.
  - Volver a `bm_normal` restaura tanto los factores como la ecuación.

### `gpu_get_blendequation()`
- **Devuelve:** constante de ecuación
- **Qué hace:** devuelve la ecuación de mezcla actual.

### `gpu_set_blendequation_sepalpha(equation, equation_alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** fija ecuaciones distintas para los componentes RGB y para el alfa.
- **Ejemplo:**
```gml
gpu_set_blendequation_sepalpha(bm_eq_add, bm_eq_max);
```

- **Notas / trampas:**
  - **No existe `gpu_get_blendequation_sepalpha()`.** El manual documenta únicamente el *setter*
    `gpu_set_blendequation_sepalpha()`; para leer el estado de la ecuación existe solo
    `gpu_get_blendequation()`. Si necesitas conservar las ecuaciones separadas para restaurarlas,
    guárdalas tú en variables cuando las fijes.

---

## Escritura de canales y alpha test

### `gpu_set_colourwriteenable(red_or_array, [green, blue, alpha])`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la escritura de cada canal (rojo, verde, azul y alfa) para todo el
  dibujo posterior. Permite crear, por ejemplo, **superficies que solo contengan alfa**.
- **Ejemplo:**
```gml
// Superficie de solo alfa: desactivamos la escritura de RGB
gpu_set_colourwriteenable(false, false, false, true);
surface_set_target(surf_mascara);
draw_clear_alpha(c_black, 0);
draw_sprite(spr_forma, 0, 0, 0);
surface_reset_target();
gpu_set_colourwriteenable(true, true, true, true);

// Forma alternativa con array
gpu_set_colourwriteenable([false, false, false, true]);
```
- **Notas / trampas:** el valor por defecto de todos los componentes es activado. Recuerda
  restaurarlo.

### `gpu_get_colourwriteenable()`
- **Devuelve:** `Array` de 4 booleanos `[red, green, blue, alpha]`
- **Qué hace:** devuelve el estado de escritura de cada canal.

### `gpu_set_alphatestenable(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva el **test de alfa** (por defecto **desactivado**). Con el test
  activado, los píxeles cuyo alfa no supere la referencia se descartan.
- **Ejemplo:**
```gml
gpu_set_alphatestenable(true);
gpu_set_alphatestref(128); // descarta alfa < 50 %
draw_sprite(spr_hojas, 0, x, y);
gpu_set_alphatestenable(false);
```
- **Notas / trampas:** es una alternativa barata al *alpha-to-coverage* y muy útil para follaje y
  sprites con bordes duros.

### `gpu_get_alphatestenable()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el test de alfa está activo.

### `gpu_set_alphatestref(val)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el valor de referencia del test de alfa, de **0 a 255** (por defecto `0`).
- **Ejemplo:**
```gml
gpu_set_alphatestref(200);
```

### `gpu_get_alphatestref()`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el valor de referencia actual.

---

## Pila de estado de la GPU

### `gpu_push_state()`
- **Devuelve:** `N/A`
- **Qué hace:** guarda el estado actual de la GPU en una pila (modo de mezcla, escritura de alfa,
  culling, etc.).
- **Ejemplo:**
```gml
gpu_push_state();            // guarda todo el estado
gpu_set_blendmode(bm_add);
draw_set_alpha(0.5);   // la transparencia de dibujo es draw_set_alpha, no gpu_set_alpha
draw_sprite(spr_resplandor, 0, x, y);
gpu_pop_state();             // restaura exactamente lo que había
```
- **Notas / trampas:** es la forma recomendada de aislar cambios de estado, mucho más segura que
  restaurar a mano cada ajuste.

### `gpu_pop_state()`
- **Devuelve:** `N/A`
- **Qué hace:** recupera el estado anterior de la pila y lo aplica.
- **Notas / trampas:** cada `gpu_pop_state()` consume un `gpu_push_state()`. No los desequilibres.

### `gpu_get_state()`
- **Devuelve:** `DS Map` con el estado de la GPU
- **Qué hace:** devuelve el estado actual completo como un DS map.
- **Ejemplo:**
```gml
var _estado = gpu_get_state();
// guardarlo para restaurarlo más tarde en otro punto del código
estado_guardado = _estado;
```

### `gpu_set_state(ds_map)`
- **Devuelve:** `N/A`
- **Qué hace:** aplica un estado de GPU previamente obtenido con `gpu_get_state()`.
- **Ejemplo:**
```gml
gpu_set_state(estado_guardado);
```

---

## Culling

Un polígono tiene una cara **frontal** y una **trasera**. La frontal es aquella cuyos vértices están
definidos en orden **antihorario**. Normalmente se dibujan ambas, pero en una forma cerrada (una
pirámide, por ejemplo) la trasera nunca se ve: activar el culling ahorra aproximadamente **la mitad
del tiempo de dibujo**.

### `gpu_set_cullmode(cullmode)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el modo de culling.

  | Constante | Descripción |
  |---|---|
  | `cull_noculling` | No se descarta nada (**por defecto**) |
  | `cull_clockwise` | Se descartan todos los triángulos en sentido horario |
  | `cull_counterclockwise` | Se descartan todos los triángulos en sentido antihorario |

- **Ejemplo:**
```gml
gpu_set_cullmode(cull_clockwise);
vertex_submit(vb_modelo, pr_trianglelist, tex_modelo);
gpu_set_cullmode(cull_noculling);
```
- **Notas / trampas:** exige definir los polígonos **en el orden correcto**; si inviertes el orden
  de los vértices, las caras desaparecen.

### `gpu_get_cullmode()`
- **Devuelve:** constante de culling
- **Qué hace:** devuelve el modo de culling actual.

---

## Búfer de profundidad (Z-buffer)

### `gpu_set_ztestenable(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva el test del búfer Z. Con el test activado, solo se dibuja un
  píxel si pasa la comparación de profundidad.
- **Ejemplo:**
```gml
gpu_set_ztestenable(true);
// dibujo 3D...
gpu_set_ztestenable(false);
```
- **Notas / trampas:** solo tiene utilidad real en proyectos 3D.

### `gpu_get_ztestenable()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el test Z está activo.

### `gpu_set_zfunc(cmp_func)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la función de comparación del test Z. Por defecto `cmpfunc_lessequal`.

  | Constante | Comparación |
  |---|---|
  | `cmpfunc_never` | nunca |
  | `cmpfunc_less` | menor que |
  | `cmpfunc_equal` | igual |
  | `cmpfunc_lessequal` | menor o igual |
  | `cmpfunc_greater` | mayor que |
  | `cmpfunc_notequal` | distinto |
  | `cmpfunc_greaterequal` | mayor o igual |
  | `cmpfunc_always` | siempre |

- **Ejemplo:**
```gml
// Fondo que se dibuja siempre, ignorando la profundidad
gpu_set_ztestenable(true);
gpu_set_zfunc(cmpfunc_always);
draw_sprite(spr_fondo, 0, 0, 0);
gpu_set_ztestenable(false);
```

### `gpu_get_zfunc()`
- **Devuelve:** constante de comparación
- **Qué hace:** devuelve la función de comparación Z actual.

### `gpu_set_zwriteenable(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la **escritura** en el búfer de profundidad.
- **Ejemplo:**
```gml
// Dibujar partículas translúcidas sin que escriban profundidad
gpu_set_zwriteenable(false);
draw_sprite(spr_humo, 0, x, y);
gpu_set_zwriteenable(true);
```
- **Notas / trampas:** desactivar la escritura Z es la técnica estándar para elementos translúcidos,
  evitando que se ocluyan entre sí.

### `gpu_get_zwriteenable()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la escritura en el búfer Z está activa.

### `gpu_set_depth(depth)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la profundidad (coordenada Z) que se usará para dibujar.
- **Ejemplo:**
```gml
gpu_set_depth(100);
draw_sprite(spr_capa_lejana, 0, x, y);
gpu_set_depth(0);
```

### `gpu_get_depth()`
- **Devuelve:** `Real`
- **Qué hace:** devuelve la profundidad de dibujo actual.

---

## Niebla (fog)

### `gpu_set_fog(enable, colour, start, end)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la niebla y configura su color y distancias. La niebla hace que
  los objetos lejanos se vean desvaídos o invisibles, lo que ayuda a crear atmósfera y a **enmascarar
  que no se están dibujando los objetos lejanos**.
- **Ejemplo:**
```gml
// Niebla gris desde 300 hasta 1200 unidades de la cámara
gpu_set_fog(true, c_gray, 300, 1200);
draw_sprite(spr_arbol, 0, x, y);
gpu_set_fog(false, c_black, 0, 0);
```
- **Notas / trampas:** `start` y `end` son distancias **relativas a la cámara**.

### `gpu_get_fog()`
- **Devuelve:** `Array` con la configuración de niebla `[enable, colour, start, end]`
- **Qué hace:** devuelve el estado actual de la niebla.
- **Ejemplo:**
```gml
var _niebla = gpu_get_fog();
show_debug_message($"Niebla activa: {_niebla[0]}");
```

---

## Filtrado y repetición de texturas

### `gpu_set_texfilter(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva el filtrado de texturas (**interpolación lineal**) de todas las
  imágenes dibujadas.
- **Ejemplo:**
```gml
// Píxel art: sin interpolación, bordes duros
gpu_set_texfilter(false);
draw_sprite(spr_pixel, 0, x, y);
gpu_set_texfilter(true);
```
- **Notas / trampas:** desactivarlo es esencial para que el píxel art se vea nítido al escalar.

### `gpu_get_texfilter()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el filtrado global está activo.

### `gpu_set_texfilter_ext(sampler_id, enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la interpolación lineal **de un único sampler** cuando se usan
  shaders.
- **Ejemplo:**
```gml
var _sampler = shader_get_sampler_index(sh_mi_shader, "s_textura");
gpu_set_texfilter_ext(_sampler, false);
```

### `gpu_get_texfilter_ext(sampler_id)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el filtrado está activo para ese sampler.

### `gpu_set_texrepeat(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** indica a GameMaker si debe **repetir** la textura cuando las coordenadas UV superan
  el rango 0–1.
- **Ejemplo:**
```gml
// Fondo en scroll infinito: la textura se repite
gpu_set_texrepeat(true);
draw_sprite_tiled(spr_fondo, 0, 0, 0);
gpu_set_texrepeat(false);
```

### `gpu_get_texrepeat()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la repetición global está activa.

### `gpu_set_texrepeat_ext(sampler_id, enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la repetición **de un único sampler** al usar shaders.
- **Ejemplo:**
```gml
var _sampler = shader_get_sampler_index(sh_agua, "s_ruido");
gpu_set_texrepeat_ext(_sampler, true);
```

### `gpu_get_texrepeat_ext(sampler_id)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la repetición está activa para ese sampler.

---

## Región de recorte (scissor)

### `gpu_set_scissor(x_or_struct, [y, w, h])`
- **Devuelve:** `N/A`
- **Qué hace:** define una región rectangular de recorte dentro del destino de dibujo. Solo se
  dibujará dentro de esa región.
- **Ejemplo:**
```gml
// Recortar el dibujo a un panel de 200x150
gpu_set_scissor(100, 100, 200, 150);
draw_sprite(spr_fondo_largo, 0, 0, 0);
gpu_set_scissor(0, 0, 0, 0); // desactivar

// Forma alternativa con struct
gpu_set_scissor({ x: 100, y: 100, w: 200, h: 150 });
```
- **Notas / trampas:** `y`, `w` y `h` son opcionales **solo si** el primer argumento es un struct.

### `gpu_get_scissor()`
- **Devuelve:** `Struct` con `x`, `y`, `w`, `h`
- **Qué hace:** devuelve la región de recorte actual.
- **Ejemplo:**
```gml
var _recorte = gpu_get_scissor();
show_debug_message($"Recorte: {_recorte.x}, {_recorte.y}");
```

---

## Búfer de stencil

El stencil es un búfer de 8 bits por píxel que permite pruebas y operaciones por píxel. Es más
flexible que el búfer de profundidad porque permite definir **qué hacer** cuando la prueba pasa y
cuando falla.

La comparación es: `(ref & read_mask) cmp_func (stencil & read_mask)`.

### `gpu_set_stencil_enable(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva el test de stencil.
- **Ejemplo:**
```gml
gpu_set_stencil_enable(true);
```

### `gpu_get_stencil_enable()`
- **Devuelve:** `Boolean`

### `gpu_set_stencil_func(cmp_func)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la función de comparación del test (por defecto `cmpfunc_always`). Usa las
  constantes `cmpfunc_*` de la tabla de la sección de profundidad.
- **Ejemplo:**
```gml
gpu_set_stencil_func(cmpfunc_always);
```

### `gpu_get_stencil_func()`
- **Devuelve:** constante de comparación

### `gpu_set_stencil_ref(ref)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el valor de referencia del test, **acotado al rango 0–255**.
- **Ejemplo:**
```gml
// Dibujar un rectángulo de 50x50 con valor de referencia 10
gpu_set_stencil_ref(10);
draw_rectangle(0, 0, 49, 49, false);
```

### `gpu_get_stencil_ref()`
- **Devuelve:** `Real`

### `gpu_set_stencil_pass(stencil_op)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la operación a realizar cuando el test de stencil **pasa**.

### `gpu_set_stencil_fail(stencil_op)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la operación a realizar cuando el test de stencil **falla**.

### `gpu_set_stencil_depth_fail(stencil_op)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la operación cuando el test de stencil **pasa pero el de profundidad falla**.

**Constantes de operación de stencil** (por defecto todas son `stencilop_keep`):

| Constante | Descripción |
|---|---|
| `stencilop_keep` | Mantiene el valor actual del búfer |
| `stencilop_zero` | Pone el valor a 0 |
| `stencilop_replace` | Sustituye el valor por el de referencia |
| `stencilop_incr` | Incrementa, saturando en el máximo |
| `stencilop_incr_wrap` | Incrementa, volviendo a 0 al superar el máximo |
| `stencilop_decr` | Decrementa, saturando en 0 |
| `stencilop_decr_wrap` | Decrementa, volviendo al máximo al bajar de 0 |
| `stencilop_invert` | Invierte bit a bit el valor |

- **Ejemplo completo — máscara con stencil:**
```gml
// Evento Draw: dibujar solo dentro de una estrella
gpu_set_stencil_enable(true);
gpu_set_stencil_func(cmpfunc_always);
gpu_set_stencil_pass(stencilop_replace);
gpu_set_stencil_ref(1);

draw_clear_stencil(0);            // limpia el stencil
draw_sprite(spr_estrella, 0, 0, 0); // «pinta» la máscara con valor 1

gpu_set_stencil_func(cmpfunc_equal); // solo dibuja donde stencil == ref
gpu_set_stencil_pass(stencilop_keep);
gpu_set_stencil_ref(1);
draw_sprite(spr_foto, 0, 0, 0);      // se recorta a la estrella

gpu_set_stencil_enable(false);
```

### `gpu_get_stencil_pass()`
- **Devuelve:** constante de operación

### `gpu_get_stencil_fail()`
- **Devuelve:** constante de operación

### `gpu_get_stencil_depth_fail()`
- **Devuelve:** constante de operación

### `gpu_set_stencil_read_mask(mask)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la máscara de lectura: 8 bits que se combinan con AND bit a bit en la
  comparación. Rango `[0, 255]` o `[0x00, 0xFF]`.
- **Ejemplo:**
```gml
gpu_set_stencil_read_mask(0x0F);
```

### `gpu_get_stencil_read_mask()`
- **Devuelve:** `Real`

### `gpu_set_stencil_write_mask(write_mask)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la máscara de escritura: define, para cada bit, si se puede escribir o no.
- **Ejemplo:**
```gml
gpu_set_stencil_write_mask(0xFF);
```

### `gpu_get_stencil_write_mask()`
- **Devuelve:** `Real`

## Máscaras de efecto con stencil: dos recetas

Las 16 funciones de arriba están documentadas una a una, pero sin un solo caso de uso completo.
Dos bastan para cubrir lo que de verdad se pide: **recortar un dibujado a la silueta de un
sprite** y **una máscara de agujero** (linterna, mirilla, transición circular). El recetario de
shaders de efecto de pantalla completa —aberración, CRT, glitch, blur, bloom, LUT— vive en
[08 · 23](./23%20-%20Recetario%20de%20shaders%20de%20efecto.md); estas dos recetas son su
complemento con stencil, sin necesitar ni un shader.

### Receta 1 — Recortar un dibujado a la silueta de un sprite

La idea: «pintar» la máscara en el búfer de stencil con el alfa del sprite recortador, y luego
dibujar lo que quieras **solo donde esa máscara vale 1**. Sirve para que un retrato, un mapa o
un efecto de partículas nunca se salga de la silueta de un marco o un personaje.

```gml
// Evento Draw — recortar spr_foto a la silueta de spr_marco_estrella
gpu_set_stencil_enable(true);
draw_clear_stencil(0);                    // el stencil empieza limpio (todo a 0)

// 1. Pintar la máscara: cualquier píxel dibujado aquí deja el valor 1 en el stencil
gpu_set_stencil_func(cmpfunc_always);     // esta pasada siempre "pasa"
gpu_set_stencil_pass(stencilop_replace);  // y al pasar, escribe el valor de referencia
gpu_set_stencil_ref(1);
draw_sprite(spr_marco_estrella, 0, x, y); // solo importa su ALFA, no su color

// 2. Dibujar el contenido: solo donde el stencil vale 1 (donde se pintó la máscara)
gpu_set_stencil_func(cmpfunc_equal);
gpu_set_stencil_pass(stencilop_keep);     // esta pasada no vuelve a escribir el stencil
gpu_set_stencil_ref(1);
draw_sprite(spr_foto, 0, x, y);           // se recorta a la silueta de la estrella

gpu_set_stencil_enable(false);
```

- **Coste:** muy bajo — dos dibujados y ningún shader.
- **Errores típicos:** olvidar `draw_clear_stencil(0)` antes de pintar la máscara (arrastra
  valores del frame anterior); no restaurar `gpu_set_stencil_enable(false)` al terminar, con lo
  que el resto del dibujado del frame queda recortado sin querer; usar `stencilop_replace` en
  la segunda pasada por error, lo que reescribe la máscara en vez de solo leerla.

### Receta 2 — Máscara de agujero (linterna con forma)

La inversa de la receta 1: en vez de mostrar el contenido SOLO dentro de una forma, lo muestras
**en todas partes MENOS dentro de ella** — el hueco de una linterna, una mirilla, o el «agujero»
que deja un power-up de visión. La diferencia está en qué función de comparación usa la segunda
pasada: `cmpfunc_notequal` en vez de `cmpfunc_equal`.

```gml
// Evento Draw — oscuridad con un agujero con la forma de spr_haz_linterna
gpu_set_stencil_enable(true);
draw_clear_stencil(0);

// 1. Pintar el hueco de la linterna en el stencil
gpu_set_stencil_func(cmpfunc_always);
gpu_set_stencil_pass(stencilop_replace);
gpu_set_stencil_ref(1);
draw_sprite(spr_haz_linterna, 0, mouse_x, mouse_y);

// 2. Dibujar la oscuridad en todo lo que NO es el hueco
gpu_set_stencil_func(cmpfunc_notequal);
gpu_set_stencil_pass(stencilop_keep);
gpu_set_stencil_ref(1);
draw_set_colour(c_black);
draw_set_alpha(0.9);
draw_rectangle(0, 0, display_get_gui_width(), display_get_gui_height(), false);
draw_set_alpha(1);

gpu_set_stencil_enable(false);
```

- **Coste:** muy bajo, igual que la receta 1.
- **Cuándo preferir esto a la surface oscura de**
  [04 · 24 §1](../04%20-%20Recetas%20por%20género/24%20-%20Iluminación%202D.md) — el sistema de
  luces con surface soporta múltiples luces con color y atenuación; el stencil es más barato
  pero binario (dentro/fuera, sin degradado) y solo tiene sentido con una forma fija por capa.
- **Errores típicos:** invertir `cmpfunc_equal`/`cmpfunc_notequal` entre las dos recetas (es la
  única línea que cambia entre "mostrar dentro" y "mostrar fuera"); dibujar la máscara del paso
  1 con alfa parcial esperando un borde suave — el stencil no interpola: un píxel con cualquier
  alfa mayor que 0 en `draw_sprite` cuenta como escrito por completo. Para un borde difuminado
  de verdad, hace falta un shader (por ejemplo, adaptando la viñeta de
  [08 · 06 §6.6](./06%20-%20Shaders.md#66-extra-viñeta-con-corner-id)), no stencil.

---

## Mipmapping

El mipmapping precalcula versiones reducidas de cada textura para usarlas a distancia, evitando el
parpadeo (*aliasing*) y mejorando el rendimiento.

### Constantes de activación

| Constante | Descripción |
|---|---|
| `mip_off` | Mipmapping desactivado |
| `mip_on` | Mipmapping activado para todas las texturas |
| `mip_markedonly` | Activado solo para los grupos de textura que lo tengan marcado (**por defecto**) |

> **NOTA: las fuentes no admiten mipmapping.** Activar mipmapping al dibujar texto, o en grupos de
> textura que contengan fuentes, puede provocar **fallos gráficos en el renderizado del texto**.

### Constantes de filtrado de mip

| Constante | Descripción |
|---|---|
| `tf_point` | Sin filtrado entre niveles de mip: transiciones visibles, **mejor rendimiento** (por defecto) |
| `tf_linear` | Filtrado lineal entre niveles (*trilinear*): suaviza las transiciones, **pequeño coste** |
| `tf_anisotropic` | Filtrado anisotrópico: gran mejora de calidad y menos desenfoque, **el mayor coste** |

### `gpu_set_tex_mip_enable(setting)` / `gpu_get_tex_mip_enable()`
- **Devuelven:** `N/A` / constante
- **Qué hace:** activa o desactiva el mipmapping globalmente.
- **Ejemplo:**
```gml
if (gpu_get_tex_mip_enable() != mip_on) gpu_set_tex_mip_enable(mip_on);
```

### `gpu_set_tex_mip_enable_ext(sampler_index, setting)` / `gpu_get_tex_mip_enable_ext(sampler_index)`
- **Devuelven:** `N/A` / constante
- **Qué hace:** igual, pero para un sampler de shader concreto.

### `gpu_set_tex_mip_filter(filter)` / `gpu_get_tex_mip_filter()`
- **Devuelven:** `N/A` / constante
- **Qué hace:** fija el modo de filtrado entre niveles de mip. Por defecto `tf_point`.
- **Ejemplo:**
```gml
gpu_set_tex_mip_filter(tf_anisotropic);
gpu_set_tex_max_aniso(8);
```

### `gpu_set_tex_mip_filter_ext(sampler_index, filter)` / `gpu_get_tex_mip_filter_ext(sampler_index)`
- **Devuelven:** `N/A` / constante
- **Qué hace:** filtrado de mip para un sampler concreto.

### `gpu_set_tex_mip_bias(bias)` / `gpu_get_tex_mip_bias()`
- **Devuelven:** `N/A` / `Real`
- **Qué hace:** fija el sesgo de mipmap. `0` = sin sesgo, `1` = primer mipmap, `2` = segundo…
  Valores altos hacen las texturas más borrosas a distancia; **valores negativos** las mantienen
  nítidas a mayor distancia. Por defecto `0`.
- **Ejemplo:**
```gml
gpu_set_tex_mip_bias(-0.5); // texturas más nítidas a distancia
```

### `gpu_set_tex_mip_bias_ext(sampler_index, bias)` / `gpu_get_tex_mip_bias_ext(sampler_index)`
- **Devuelven:** `N/A` / `Real`

### `gpu_set_tex_min_mip(minmip)` / `gpu_get_tex_min_mip()`
- **Devuelven:** `N/A` / `Real`
- **Qué hace:** fija el nivel **mínimo** de mipmap: `0` es la resolución más alta, `1` el primer mip,
  etc.

### `gpu_set_tex_min_mip_ext(sampler_index, minmip)` / `gpu_get_tex_min_mip_ext(sampler_index)`
- **Devuelven:** `N/A` / `Real`

### `gpu_set_tex_max_mip(maxmip)` / `gpu_get_tex_max_mip()`
- **Devuelven:** `N/A` / `Real`
- **Qué hace:** fija el nivel **máximo** de mipmap. Por defecto `16`.
- **Ejemplo:**
```gml
// Evitar bleeding: borde de página de 8 px + mip máximo de 3
gpu_set_tex_max_mip(3);
```
- **Notas / trampas:** limitar el mip máximo es la solución recomendada para evitar artefactos de
  *bleeding* entre sprites vecinos en la página de textura a gran distancia.

### `gpu_set_tex_max_mip_ext(sampler_index, maxmip)` / `gpu_get_tex_max_mip_ext(sampler_index)`
- **Devuelven:** `N/A` / `Real`

### `gpu_set_tex_max_aniso(maxaniso)` / `gpu_get_tex_max_aniso()`
- **Devuelven:** `N/A` / `Real`
- **Qué hace:** fija el nivel máximo de anisotropía al usar `tf_anisotropic`. Por defecto `16`.
- **Ejemplo:**
```gml
gpu_set_tex_mip_filter(tf_anisotropic);
gpu_set_tex_max_aniso(4);
```

### `gpu_set_tex_max_aniso_ext(sampler_index, maxaniso)` / `gpu_get_tex_max_aniso_ext(sampler_index)`
- **Devuelven:** `N/A` / `Real`

---

## Frustum culling de sprites

### `gpu_set_sprite_cull(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva globalmente el **culling de frustum** de sprites y tilemaps. Está
  **activado por defecto**.
- **Ejemplo:**
```gml
// Desactivar el culling si haces trucos raros con la cámara
gpu_set_sprite_cull(false);
```
- **Notas / trampas:** con el culling activado, los sprites se comprueban contra el frustum de la
  vista **en la CPU**.

### `gpu_get_sprite_cull()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el culling de sprites está activo.

---

## Funciones legacy sin página en el manual

Se comprobó exhaustivamente que las siguientes funciones **clásicas de GML no tienen página propia
en el manual de GameMaker LTS 2026** (ni en los canales *monthly*, *lts* ni *beta*). Aparecen en
innumerable código heredado y siguen presentes en el runtime, pero **no están documentadas** y el
manual dirige explícitamente a `gpu_set_blendmode` / `gpu_set_blendmode_ext` como reemplazo:

| Función legacy | Reemplazo documentado |
|---|---|
| `draw_set_blend_mode(mode)` | `gpu_set_blendmode(mode)` |
| `draw_set_blend_mode_ext(src, dest)` | `gpu_set_blendmode_ext(src, dest)` |
| `draw_get_blend_mode()` | `gpu_get_blendmode()` |
| `draw_get_blend_mode_ext()` | `gpu_get_blendmode_ext()` |

**Recomendación:** en código nuevo usa siempre la familia `gpu_*`, que es la documentada y la que
recibe mantenimiento.

---

## Tabla resumen

### Color y alfa (13)

| Función | Devuelve |
|---|---|
| `colour_get_red(col)` | `Real` |
| `colour_get_green(col)` | `Real` |
| `colour_get_blue(col)` | `Real` |
| `colour_get_hue(col)` | `Real` |
| `colour_get_saturation(col)` | `Real` |
| `colour_get_value(col)` | `Real` |
| `make_colour_rgb(red, green, blue)` | `Colour` |
| `make_colour_hsv(hue, sat, val)` | `Colour` |
| `merge_colour(col1, col2, amount)` | `Colour` |
| `draw_set_colour(col)` | `N/A` |
| `draw_get_colour()` | `Colour` |
| `draw_set_alpha(alpha)` | `N/A` |
| `draw_get_alpha()` | `Real` |

### GPU Control (65)

| Función | Devuelve |
|---|---|
| `gpu_set_blendmode(mode)` / `gpu_get_blendmode()` | `N/A` / constante |
| `gpu_set_blendmode_ext(src, dest)` / `gpu_get_blendmode_ext()` | `N/A` / `Array[2]` |
| `gpu_set_blendmode_ext_sepalpha(s, d, as, ad)` / `gpu_get_blendmode_ext_sepalpha()` | `N/A` / `Array[4]` |
| `gpu_set_blendequation(equation)` / `gpu_get_blendequation()` | `N/A` / constante |
| `gpu_set_blendequation_sepalpha(eq, eq_a)` | `N/A` — **sin getter** |
| `gpu_set_blendenable(enable)` / `gpu_get_blendenable()` | `N/A` / `Boolean` |
| `gpu_get_blendmode_src()` | constante |
| `gpu_get_blendmode_dest()` | constante |
| `gpu_get_blendmode_srcalpha()` | constante |
| `gpu_get_blendmode_destalpha()` | constante |
| `gpu_set_colourwriteenable(r, [g, b, a])` / `gpu_get_colourwriteenable()` | `N/A` / `Array[4]` |
| `gpu_set_alphatestenable(enable)` / `gpu_get_alphatestenable()` | `N/A` / `Boolean` |
| `gpu_set_alphatestref(val)` / `gpu_get_alphatestref()` | `N/A` / `Real` |
| `gpu_push_state()` | `N/A` |
| `gpu_pop_state()` | `N/A` |
| `gpu_set_state(ds_map)` / `gpu_get_state()` | `N/A` / DS Map |
| `gpu_set_cullmode(cullmode)` / `gpu_get_cullmode()` | `N/A` / constante |
| `gpu_set_ztestenable(enable)` / `gpu_get_ztestenable()` | `N/A` / `Boolean` |
| `gpu_set_zfunc(cmp_func)` / `gpu_get_zfunc()` | `N/A` / constante |
| `gpu_set_zwriteenable(enable)` / `gpu_get_zwriteenable()` | `N/A` / `Boolean` |
| `gpu_set_depth(depth)` / `gpu_get_depth()` | `N/A` / `Real` |
| `gpu_set_fog(enable, col, start, end)` / `gpu_get_fog()` | `N/A` / `Array` |
| `gpu_set_texfilter(enable)` / `gpu_get_texfilter()` | `N/A` / `Boolean` |
| `gpu_set_texfilter_ext(sampler_id, enable)` / `gpu_get_texfilter_ext(sampler_id)` | `N/A` / `Boolean` |
| `gpu_set_texrepeat(enable)` / `gpu_get_texrepeat()` | `N/A` / `Boolean` |
| `gpu_set_texrepeat_ext(sampler_id, enable)` / `gpu_get_texrepeat_ext(sampler_id)` | `N/A` / `Boolean` |
| `gpu_set_scissor(x, [y, w, h])` / `gpu_get_scissor()` | `N/A` / `Struct` |
| `gpu_set_stencil_enable(enable)` / `gpu_get_stencil_enable()` | `N/A` / `Boolean` |
| `gpu_set_stencil_func(cmp_func)` / `gpu_get_stencil_func()` | `N/A` / constante |
| `gpu_set_stencil_ref(ref)` / `gpu_get_stencil_ref()` | `N/A` / `Real` |
| `gpu_set_stencil_pass(op)` / `gpu_get_stencil_pass()` | `N/A` / constante |
| `gpu_set_stencil_fail(op)` / `gpu_get_stencil_fail()` | `N/A` / constante |
| `gpu_set_stencil_depth_fail(op)` / `gpu_get_stencil_depth_fail()` | `N/A` / constante |
| `gpu_set_stencil_read_mask(mask)` / `gpu_get_stencil_read_mask()` | `N/A` / `Real` |
| `gpu_set_stencil_write_mask(mask)` / `gpu_get_stencil_write_mask()` | `N/A` / `Real` |
| `gpu_set_sprite_cull(enable)` / `gpu_get_sprite_cull()` | `N/A` / `Boolean` |

### Mipmapping (24)

| Función | Devuelve |
|---|---|
| `gpu_set_tex_mip_enable(setting)` / `gpu_get_tex_mip_enable()` | `N/A` / constante |
| `gpu_set_tex_mip_enable_ext(sampler, setting)` / `gpu_get_tex_mip_enable_ext(sampler)` | `N/A` / constante |
| `gpu_set_tex_mip_filter(filter)` / `gpu_get_tex_mip_filter()` | `N/A` / constante |
| `gpu_set_tex_mip_filter_ext(sampler, filter)` / `gpu_get_tex_mip_filter_ext(sampler)` | `N/A` / constante |
| `gpu_set_tex_mip_bias(bias)` / `gpu_get_tex_mip_bias()` | `N/A` / `Real` |
| `gpu_set_tex_mip_bias_ext(sampler, bias)` / `gpu_get_tex_mip_bias_ext(sampler)` | `N/A` / `Real` |
| `gpu_set_tex_min_mip(minmip)` / `gpu_get_tex_min_mip()` | `N/A` / `Real` |
| `gpu_set_tex_min_mip_ext(sampler, minmip)` / `gpu_get_tex_min_mip_ext(sampler)` | `N/A` / `Real` |
| `gpu_set_tex_max_mip(maxmip)` / `gpu_get_tex_max_mip()` | `N/A` / `Real` |
| `gpu_set_tex_max_mip_ext(sampler, maxmip)` / `gpu_get_tex_max_mip_ext(sampler)` | `N/A` / `Real` |
| `gpu_set_tex_max_aniso(maxaniso)` / `gpu_get_tex_max_aniso()` | `N/A` / `Real` |
| `gpu_set_tex_max_aniso_ext(sampler, maxaniso)` / `gpu_get_tex_max_aniso_ext(sampler)` | `N/A` / `Real` |

**Total: 102 funciones documentadas** (13 + 65 + 24).

---

## Fuentes

- Colour And Alpha — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/Colour_And_Alpha.htm
- `colour_get_red` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/colour_get_red.htm
- `colour_get_green` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/colour_get_green.htm
- `colour_get_blue` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/colour_get_blue.htm
- `colour_get_hue` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/colour_get_hue.htm
- `colour_get_saturation` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/colour_get_saturation.htm
- `colour_get_value` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/colour_get_value.htm
- `make_colour_rgb` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/make_colour_rgb.htm
- `make_colour_hsv` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/make_colour_hsv.htm
- `merge_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/merge_colour.htm
- `draw_set_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_set_colour.htm
- `draw_get_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_get_colour.htm
- `draw_set_alpha` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_set_alpha.htm
- `draw_get_alpha` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_get_alpha.htm
- GPU Control — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/GPU_Control.htm
- `gpu_set_blendmode` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_blendmode.htm
- `gpu_set_blendmode_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_blendmode_ext.htm
- `gpu_set_blendmode_ext_sepalpha` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_blendmode_ext_sepalpha.htm
- `gpu_set_blendequation` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_blendequation.htm
- `gpu_set_blendequation_sepalpha` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_blendequation_sepalpha.htm
- `gpu_set_blendenable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_blendenable.htm
- `gpu_set_colourwriteenable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_colourwriteenable.htm
- `gpu_set_alphatestenable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_alphatestenable.htm
- `gpu_set_alphatestref` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_alphatestref.htm
- `gpu_push_state` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_push_state.htm
- `gpu_pop_state` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_pop_state.htm
- `gpu_get_state` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_get_state.htm
- `gpu_set_state` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_state.htm
- `gpu_set_cullmode` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_cullmode.htm
- `gpu_set_ztestenable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_ztestenable.htm
- `gpu_set_zfunc` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_zfunc.htm
- `gpu_set_zwriteenable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_zwriteenable.htm
- `gpu_set_depth` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_depth.htm
- `gpu_set_fog` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_fog.htm
- `gpu_set_texfilter` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_texfilter.htm
- `gpu_set_texfilter_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_texfilter_ext.htm
- `gpu_set_texrepeat` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_texrepeat.htm
- `gpu_set_texrepeat_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_texrepeat_ext.htm
- `gpu_set_scissor` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_scissor.htm
- `gpu_set_stencil_enable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_stencil_enable.htm
- `gpu_set_stencil_func` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_stencil_func.htm
- `gpu_set_stencil_ref` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_stencil_ref.htm
- `gpu_set_stencil_pass` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_stencil_pass.htm
- `gpu_set_stencil_fail` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_stencil_fail.htm
- `gpu_set_stencil_depth_fail` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_stencil_depth_fail.htm
- `gpu_set_stencil_read_mask` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_stencil_read_mask.htm
- `gpu_set_stencil_write_mask` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_stencil_write_mask.htm
- `gpu_set_sprite_cull` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_sprite_cull.htm
- Mipmapping — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Mipmapping/Mipmapping.htm
- `gpu_set_tex_mip_enable` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Mipmapping/gpu_set_tex_mip_enable.htm
- `gpu_set_tex_mip_filter` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Mipmapping/gpu_set_tex_mip_filter.htm
- `gpu_set_tex_mip_bias` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Mipmapping/gpu_set_tex_mip_bias.htm
- `gpu_set_tex_min_mip` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Mipmapping/gpu_set_tex_min_mip.htm
- `gpu_set_tex_max_mip` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Mipmapping/gpu_set_tex_max_mip.htm
- `gpu_set_tex_max_aniso` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Mipmapping/gpu_set_tex_max_aniso.htm
- The Depth And Stencil Buffer — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Depth_And_Stencil_Buffer/The_Depth_And_Stencil_Buffer.htm
