# 07 — Vertex buffers y formatos

> Referencia completa de GML para **GameMaker LTS 2026.0** (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Área: `Drawing/Primitives/`.
> **45 funciones documentadas.**

---

## Índice

1. [Conceptos: primitiva, vértice y formato](#conceptos-primitiva-vértice-y-formato)
2. [Tipos de primitiva](#tipos-de-primitiva)
3. [Regla de oro del orden de atributos](#regla-de-oro-del-orden-de-atributos)
4. [Definición de formatos de vértice](#definición-de-formatos-de-vértice)
5. [Creación y gestión de vertex buffers](#creación-y-gestión-de-vertex-buffers)
6. [Escritura de vértices](#escritura-de-vértices)
7. [Envío a la GPU (submit)](#envío-a-la-gpu-submit)
8. [Actualización y copia entre buffers](#actualización-y-copia-entre-buffers)
9. [Diferencia de UV: draw_vertex vs vertex_texcoord](#diferencia-de-uv-draw_vertex-vs-vertex_texcoord)
10. [Ejemplos prácticos completos](#ejemplos-prácticos-completos)
11. [Tabla resumen](#tabla-resumen)
12. [Fuentes](#fuentes)

---

## Conceptos: primitiva, vértice y formato

Una **primitiva** es un tipo de dibujo hecho a partir de puntos que definen lo que se ve en pantalla.
Pueden ser puntos sueltos, líneas o triángulos, y pueden colorearse, tener alfa e incluso textura.

Los puntos de una primitiva se llaman **vértices** (*vertices*, singular *vertex*) y almacenan datos
sobre su posición, color, textura y posiblemente otra información. La GPU dibuja esos vértices según
el **tipo de primitiva** que indiques.

GameMaker ofrece **dos formas** de crear primitivas:

| Enfoque | Cuándo usarlo |
|---|---|
| **Funciones de primitiva** (`draw_primitive_*` / `draw_vertex_*`) | Efectos puntuales que cambian cada frame. Se definen y dibujan al vuelo. Ver archivo **02** |
| **Vertex buffers** | Geometría **reutilizable**: se define una vez y se envía muchas veces. Mucho más rápido |

Un vertex buffer es un **buffer** que almacena datos de vértices. Con ellos separas la *definición*
de la primitiva de su *dibujado*. Los datos se almacenan según un **formato de vértice** que debes
definir primero.

---

## Tipos de primitiva

| Constante | Descripción |
|---|---|
| `pr_pointlist` | **Lista de puntos**: se dibuja un punto por cada vértice |
| `pr_linelist` | **Lista de líneas**: se dibuja una línea entre el 1.º y el 2.º vértice, entre el 3.º y el 4.º, etc. |
| `pr_linestrip` | **Tira de líneas**: 1-2, 2-3, 3-4, etc. |
| `pr_trianglelist` | **Lista de triángulos**: triángulo con los vértices 1-2-3, luego 4-5-6, etc. |
| `pr_trianglestrip` | **Tira de triángulos**: triángulo con 1-2-3, luego 2-3-4, luego 3-4-5, etc. |
| `pr_trianglefan` | **Abanico de triángulos**: cada dos vértices se unen al primero para formar un triángulo |

- **Advertencia sobre `pr_trianglefan`:** no tiene soporte nativo en todas las plataformas
  (Windows, Xbox). GameMaker **convierte el tipo en tiempo de compilación** para que funcione, lo que
  hace que en esas plataformas sea **mucho más lento** que los demás. Evítalo si buscas rendimiento.
- En HTML5 requiere WebGL activado.

---

## Regla de oro del orden de atributos

> **El orden en que añades propiedades al construir la primitiva está definido por el orden en que
> añadiste esas propiedades al crear el formato de vértice.** Si definiste el formato con el orden
> *posición, color, coordenada de textura*, debes añadir esas propiedades en ese mismo orden o
> **obtendrás errores**.

Además: si has definido un formato que solo tiene datos de posición, **no tiene sentido** construir
la primitiva con datos de color.

---

## Definición de formatos de vértice

Un formato de vértice lista los atributos que se almacenan para un vértice, **en orden**. Se empieza
con `vertex_format_begin()`, se añaden atributos con `vertex_format_add_*` y se cierra con
`vertex_format_end()`.

### `vertex_format_begin()`
- **Devuelve:** `N/A`
- **Qué hace:** inicia la definición de un nuevo formato de vértice. Debe llamarse antes de añadir
  ningún atributo.
- **Ejemplo:**
```gml
// Script asset: definir el formato por defecto del proyecto
vertex_format_begin();
vertex_format_add_position_3d();
vertex_format_add_colour();
vertex_format_add_texcoord();
global.formato_default = vertex_format_end();
```

### `vertex_format_add_position()`
- **Devuelve:** `N/A`
- **Qué hace:** añade una **posición 2D** (x, y) al formato.

### `vertex_format_add_position_3d()`
- **Devuelve:** `N/A`
- **Qué hace:** añade una **posición 3D** (x, y, z) al formato.
- **Ejemplo:**
```gml
vertex_format_begin();
vertex_format_add_position_3d();
vertex_format_add_colour();
vertex_format_add_texcoord();
formato_3d = vertex_format_end();
```

### `vertex_format_add_colour()`
- **Devuelve:** `N/A`
- **Qué hace:** añade un atributo de **color RGBA** al formato.
- **Notas / trampas:** el manual marca una observación **IMPORTANTE** sobre esta función; consulta la
  página oficial si vas a usar colores en formatos multi-atributo con shaders personalizados.

### `vertex_format_add_texcoord()`
- **Devuelve:** `N/A`
- **Qué hace:** añade datos de **posición de textura** (u, v) al formato.

### `vertex_format_add_normal()`
- **Devuelve:** `N/A`
- **Qué hace:** añade datos de **normal** (nx, ny, nz) al formato.
- **Notas / trampas:** **imprescindible para usar el sistema de iluminación** (`draw_light_*`, ver
  archivo **02**), que requiere una propiedad normal en el formato del vértice.

### `vertex_format_add_custom(type, usage)`
- **Devuelve:** `N/A`
- **Qué hace:** añade un tipo de datos **personalizado** para atributos específicos del formato.

**Constantes de tipo de dato:**

| Constante | Descripción |
|---|---|
| `vertex_type_float1` | Un único valor en coma flotante |
| `vertex_type_float2` | Dos valores en coma flotante |
| `vertex_type_float3` | Tres valores en coma flotante |
| `vertex_type_float4` | Cuatro valores en coma flotante |
| `vertex_type_colour` | Cuatro componentes (r, g, b, a) |
| `vertex_type_ubyte4` | Cuatro bytes sin signo (de 0 a 255) |

> **IMPORTANTE:** en **Windows, Xbox, PS4 y PS5** el tipo `ubyte4` **solo funciona si usas el tipo de
> shader nativo** (HLSL/PSSL) e indicas en el shader que la entrada es `uint4`.

**Constantes de uso** (*usage*): hay que definirlas para que los valores se «enlacen»
correctamente dentro del shader, porque DirectX y OpenGL tienen requisitos distintos.

| Constante | Uso |
|---|---|
| `vertex_usage_position` | valores de posición (x, y, z) |
| `vertex_usage_colour` | valores de color (r, g, b, a) |
| `vertex_usage_normal` | normal del vértice (nx, ny, nz) |
| `vertex_usage_texcoord` | coordenadas UV (u, v) |
| `vertex_usage_blendweight` | peso de mezcla de la matriz de entrada (animación esquelética) |
| `vertex_usage_blendindices` | índices de las matrices a usar (animación esquelética) |
| `vertex_usage_depth` | valor de búfer de profundidad del vértice |
| `vertex_usage_tangent` | valores de tangente |
| `vertex_usage_binormal` | valores de binormal |
| `vertex_usage_fog` | valores de niebla |
| `vertex_usage_sample` | índice de sampler |

> **Restricción importante:** `vertex_format_add_custom()` **solo admite `vertex_usage_position`,
> `vertex_usage_colour`, `vertex_usage_normal` y `vertex_usage_texcoord` cuando usas shaders GLSL.**
> Estos se mapean a los atributos del shader `in_Position`, `in_Colour[0 - ...]` e `in_Normal`
> respectivamente. Cualquier otro atributo (por ejemplo, coordenadas de textura) puede mapearse a
> cualquier atributo que definas.

- **Ejemplo:**
```gml
// Formato personalizado con dos coordenadas de textura (multitextura)
vertex_format_begin();
vertex_format_add_position_3d();
vertex_format_add_custom(vertex_type_float2, vertex_usage_texcoord);
vertex_format_add_custom(vertex_type_float2, vertex_usage_texcoord);
vertex_format_add_colour();
formato_multitextura = vertex_format_end();
```

### `vertex_format_end()`
- **Devuelve:** `Vertex Format`
- **Qué hace:** cierra el formato iniciado con `vertex_format_begin()` y lo devuelve.
- **Ejemplo:**
```gml
global.formato_default = vertex_format_end();
```

### `vertex_format_delete(format_id)`
- **Devuelve:** `N/A`
- **Qué hace:** elimina el formato de vértice indicado. **Debe llamarse siempre que termines de usar
  los formatos creados.**
- **Ejemplo:**
```gml
// Evento Cleanup / Game End
vertex_format_delete(global.formato_default);
```

### `vertex_format_exists(format_id)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el formato de vértice existe en memoria.
- **Ejemplo:**
```gml
if (!vertex_format_exists(global.formato_default))
{
    global.formato_default = crear_formato_default();
}
```

### `vertex_format_get_info(format)`
- **Devuelve:** `Struct` con la información del formato de vértice
- **Qué hace:** devuelve un struct que describe el formato: sus atributos, tipos y usos.
- **Ejemplo:**
```gml
var _info = vertex_format_get_info(global.formato_default);
show_debug_message(_info);
```

---

## Creación y gestión de vertex buffers

### `vertex_create_buffer()`
- **Devuelve:** `Vertex Buffer`
- **Qué hace:** crea un vertex buffer **vacío**.
- **Ejemplo:**
```gml
vb = vertex_create_buffer();
```

### `vertex_create_buffer_ext(size)`
- **Devuelve:** `Vertex Buffer`
- **Qué hace:** crea un vertex buffer vacío reservando un **tamaño inicial en bytes**. Úsalo cuando
  sepas de antemano cuántos vértices vas a escribir: evita realocaciones.
- **Ejemplo:**
```gml
// 4 vértices x 36 bytes por vértice (pos3d + color + uv = 12 + 4 + 8 + ... )
vb = vertex_create_buffer_ext(4 * 36);
```

### `vertex_create_buffer_from_buffer(buffer, format)`
- **Devuelve:** `Vertex Buffer`
- **Qué hace:** crea un vertex buffer y lo rellena con los datos de un **buffer** normal.
- **Ejemplo:**
```gml
// Cargar un modelo desde disco
var _buff = buffer_load("modelo.mod");
vb_modelo = vertex_create_buffer_from_buffer(_buff, global.formato_default);
buffer_delete(_buff);
```
- **Notas / trampas:** consulta la guía *Transferring Data Between Buffers* del manual para saber
  cómo pasar datos entre los dos tipos de buffer.

### `vertex_create_buffer_from_buffer_ext(buffer, format, src_offset, vert_num)`
- **Devuelve:** `Vertex Buffer`
- **Qué hace:** igual que la anterior pero indicando el **desplazamiento** dentro del buffer origen y
  el **número de vértices** que tendrá el vertex buffer.
- **Ejemplo:**
```gml
// Tomar 100 vértices empezando en el byte 512 del buffer
vb = vertex_create_buffer_from_buffer_ext(_buff, global.formato_default, 512, 100);
```

### `vertex_get_buffer_size(buffer)`
- **Devuelve:** `Real` (bytes)
- **Qué hace:** devuelve el tamaño del vertex buffer en bytes.
- **Ejemplo:**
```gml
show_debug_message($"VB: {vertex_get_buffer_size(vb)} bytes");
```

### `vertex_get_number(buffer)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el **número de vértices** del buffer.
- **Ejemplo:**
```gml
var _n = vertex_get_number(vb);
```

### `vertex_buffer_exists(buffer)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el vertex buffer existe en memoria.
- **Ejemplo:**
```gml
if (!vertex_buffer_exists(vb)) vb = vertex_create_buffer();
```

### `vertex_delete_buffer(buffer)`
- **Devuelve:** `N/A`
- **Qué hace:** elimina el vertex buffer y libera su memoria.
- **Ejemplo:**
```gml
// Evento Cleanup
vertex_delete_buffer(vb);
```

---

## Escritura de vértices

Para escribir en un vertex buffer: `vertex_begin()` → `vertex_position*()`, `vertex_colour()`, etc.
→ `vertex_end()`.

### `vertex_begin(buffer, format)`
- **Devuelve:** `N/A`
- **Qué hace:** inicia la escritura de vértices en el buffer, indicando el formato que se usará.
- **Ejemplo:**
```gml
vertex_begin(vb, global.formato_default);
```

### `vertex_end(buffer)`
- **Devuelve:** `N/A`
- **Qué hace:** finaliza la escritura de vértices.
- **Ejemplo:**
```gml
vertex_end(vb);
```

### `vertex_position(buffer, x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe la **posición 2D** del vértice.
- **Ejemplo:**
```gml
vertex_position(vb, 0, 0);
```

### `vertex_position_3d(buffer, x, y, z)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe la **posición 3D** del vértice.
- **Ejemplo:**
```gml
vertex_position_3d(vb, 0, 0, 0);
```

### `vertex_colour(buffer, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe el **color** y el **alfa** del vértice. El color puede ser una constante o un
  valor hexadecimal; el alfa va de 0 a 1.
- **Ejemplo:**
```gml
vertex_colour(vb, c_white, 1);
vertex_colour(vb, c_red, 0.5);
```

### `vertex_argb(buffer, argb)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe el color del vértice como un **valor ARGB** único.
- **Ejemplo:**
```gml
// Blanco opaco en formato ARGB de 32 bits
vertex_argb(vb, $FFFFFFFF);
```
- **Notas / trampas:** es más rápida que `vertex_colour` si ya tienes el valor empaquetado.

### `vertex_texcoord(buffer, u, v)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe las **coordenadas de textura** (UV) del vértice.
- **Ejemplo:**
```gml
var _uv = sprite_get_uvs(spr_imagen, 0);
vertex_texcoord(vb, _uv[0], _uv[1]);
```
- **Notas / trampas:** **`(0, 0)` es la esquina superior izquierda de la PÁGINA DE TEXTURA COMPLETA y
  `(1, 1)` la inferior derecha**, es decir, el rango `[0, 1]` cubre toda la página. Por eso debes usar
  `sprite_get_uvs()`, `font_get_uvs()` o `tileset_get_uvs()` para obtener el rango de un asset
  concreto. Ver la sección [Diferencia de UV](#diferencia-de-uv-draw_vertex-vs-vertex_texcoord).

### `vertex_normal(buffer, nx, ny, nz)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe la **normal** del vértice. Necesario si el formato la incluye (imprescindible
  para iluminación).
- **Ejemplo:**
```gml
// Normal apuntando hacia el observador (plano 2D)
vertex_normal(vb, 0, 0, 1);
```

### `vertex_float1(buffer, float)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe **un** valor en coma flotante para el atributo personalizado actual.

### `vertex_float2(buffer, float, float)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe **dos** valores en coma flotante.

### `vertex_float3(buffer, float, float, float)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe **tres** valores en coma flotante.

### `vertex_float4(buffer, float, float, float, float)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe **cuatro** valores en coma flotante.

### `vertex_ubyte4(buffer, byte1, byte2, byte3, byte4)`
- **Devuelve:** `N/A`
- **Qué hace:** escribe **cuatro bytes sin signo** (0–255).
- **Notas / trampas:** en Windows, Xbox, PS4 y PS5 solo funciona con shaders nativos (HLSL/PSSL) y
  declarando la entrada como `uint4`.

**Ejemplo de escritura con atributos personalizados:**
```gml
// Formato: posición 3D + dos UV + color
vertex_begin(vb, formato_multitextura);
vertex_position_3d(vb, 0,   0, 0);
vertex_float2(vb, 0, 0);          // UV set 1
vertex_float2(vb, 0, 0);          // UV set 2
vertex_colour(vb, c_white, 1);
vertex_end(vb);
```

---

## Envío a la GPU (submit)

### `vertex_submit(buffer, primtype, texture)`
- **Devuelve:** `N/A`
- **Qué hace:** envía el vertex buffer completo a la canalización gráfica para dibujarlo.
- **Argumentos:** `buffer` (vertex buffer), `primtype` (constante de tipo de primitiva),
  `texture` (textura a usar, o `-1` para ninguna).
- **Ejemplo:**
```gml
var _tex = sprite_get_texture(spr_imagen, 0);
vertex_submit(vb, pr_trianglestrip, _tex);
```
- **Notas / trampas:** solo puede usarse en eventos de dibujo.

### `vertex_submit_ext(buffer, primtype, texture, offset, number)`
- **Devuelve:** `N/A`
- **Qué hace:** envía **un rango** de vértices del buffer.
- **Argumentos:** `offset` es el índice del primer vértice a enviar (debe ser **> 0**; usa `-1` para
  enviar todos los vértices a partir del offset) y `number` es el número de vértices a enviar.
- **Ejemplo:**
```gml
// Enviar 6 vértices empezando en el vértice 5 (múltiplo de 3 para pr_trianglelist)
vertex_submit_ext(vb, pr_trianglelist, -1, 5, 6);
```
- **Notas / trampas:**
  - Solo usable en eventos de dibujo.
  - Funciona tanto con buffers normales como **congelados**.
  - **El número de vértices debe ser acorde al tipo de primitiva** que estés dibujando (por ejemplo,
    múltiplo de 3 para `pr_trianglelist`).
  - Los `pr_trianglefan` se convierten internamente a `pr_trianglelist` en las plataformas que no
    los soportan.

### `vertex_freeze(buffer)`
- **Devuelve:** `N/A`
- **Qué hace:** **congela** el vertex buffer, convirtiéndolo en inmutable pero mucho más rápido de
  enviar a la GPU. Es la optimización clave para geometría estática.
- **Ejemplo:**
```gml
// Geometría del nivel: se construye una vez y se congela
vertex_begin(vb_nivel, global.formato_default);
// ... escribir todos los vértices del nivel ...
vertex_end(vb_nivel);
vertex_freeze(vb_nivel);   // a partir de aquí no se puede modificar
```
- **Notas / trampas:** tras congelarlo **no puedes modificarlo**. Si necesitas cambiarlo, destrúyelo
  y créalo de nuevo. Úsalo solo para geometría que no cambia.

---

## Actualización y copia entre buffers

### `vertex_update_buffer_from_buffer(dest_vbuff, dest_offset, src_buffer[, src_offset, src_size])`
- **Devuelve:** `N/A`
- **Qué hace:** copia datos desde un **buffer** normal a un vertex buffer existente.
- **Argumentos:** `dest_vbuff` (vertex buffer destino), `dest_offset` (desplazamiento en bytes donde
  empezar a escribir), `src_buffer` (buffer origen), `src_offset` (**opcional**, desplazamiento en
  bytes en el origen, por defecto `0`), `src_size` (**opcional**, tamaño en bytes a copiar, por
  defecto `-1` = copiar el buffer completo).
- **Ejemplo:**
```gml
// Actualizar solo la parte de vértices que se mueve
vertex_update_buffer_from_buffer(vb, 0, buff_dinamico, 0, 512);
```

### `vertex_update_buffer_from_vertex(dest_vbuff, dest_vert, src_vbuff[, src_vert, src_vert_num])`
- **Devuelve:** `N/A`
- **Qué hace:** copia vértices **de un vertex buffer a otro**.
- **Argumentos:** `dest_vbuff` (vertex buffer destino), `dest_vert` (índice del primer vértice
  destino), `src_vbuff` (vertex buffer origen), `src_vert` (**opcional**, índice del primer vértice
  origen), `src_vert_num` (**opcional**, número de vértices a copiar).
- **Ejemplo:**
```gml
// Copiar 12 vértices del buffer 3 al buffer destino, a partir del vértice 0
vertex_update_buffer_from_vertex(vb_destino, 0, vb_origen, 3, 12);
```
- **Notas / trampas:** no funciona con buffers congelados como destino.

---

## Diferencia de UV: draw_vertex vs vertex_texcoord

Esta es una de las trampas más habituales. Las dos familias de funciones **interpretan las UV de
forma distinta**:

| Función | Qué significan (0,0) y (1,1) |
|---|---|
| `draw_vertex_texture()` y `draw_vertex_texture_colour()` | La esquina superior izquierda es la de la **región del sprite dentro de la página de textura**, y la inferior derecha la de esa misma región |
| `vertex_texcoord()` | `(0, 0)` es la esquina superior izquierda de la **página de textura completa** y `(1, 1)` la inferior derecha: el rango `[0, 1]` cubre **toda la página** |

**Solución para vertex buffers:** usa `sprite_get_uvs()`, `font_get_uvs()` o `tileset_get_uvs()`
para obtener el rango UV de un asset concreto dentro de la página.

```gml
var _uv = sprite_get_uvs(spr_imagen, 0);
var _umin = _uv[0], _vmin = _uv[1], _umax = _uv[2], _vmax = _uv[3];
// ...y usar _umin/_vmin/_umax/_vmax en vertex_texcoord()
```

---

## Ejemplos prácticos completos

### Ejemplo 1 — Quad texturizado con un sprite

El caso más habitual: dibujar un sprite sobre geometría propia para poder deformarlo.

```gml
// Script asset — definir el formato una sola vez (llamar al iniciar el juego)
function scr_definir_formato()
{
    vertex_format_begin();
    vertex_format_add_position_3d();
    vertex_format_add_colour();
    vertex_format_add_texcoord();
    global.formato_default = vertex_format_end();
}
```

```gml
// Evento Create
var _uv = sprite_get_uvs(spr_imagen, 0);
var _umin = _uv[0], _vmin = _uv[1], _umax = _uv[2], _vmax = _uv[3];

vb = vertex_create_buffer();

vertex_begin(vb, global.formato_default);

// Esquina superior izquierda
vertex_position_3d(vb,   0,   0, 0); vertex_colour(vb, c_white, 1); vertex_texcoord(vb, _umin, _vmin);
// Esquina superior derecha
vertex_position_3d(vb, 100,   0, 0); vertex_colour(vb, c_white, 1); vertex_texcoord(vb, _umax, _vmin);
// Esquina inferior izquierda
vertex_position_3d(vb,   0, 100, 0); vertex_colour(vb, c_white, 1); vertex_texcoord(vb, _umin, _vmax);
// Esquina inferior derecha
vertex_position_3d(vb, 100, 100, 0); vertex_colour(vb, c_white, 1); vertex_texcoord(vb, _umax, _vmax);

vertex_end(vb);
```

```gml
// Evento Draw
var _tex = sprite_get_texture(spr_imagen, 0);
vertex_submit(vb, pr_trianglestrip, _tex);
```

```gml
// Evento Cleanup
vertex_delete_buffer(vb);
```

> Observa el orden: `pr_trianglestrip` con 4 vértices dibuja dos triángulos (1-2-3 y 2-3-4). El orden
> de las esquinas (sup. izq., sup. der., inf. izq., inf. der.) es el correcto para una tira.

---

### Ejemplo 2 — Terreno 3D generado proceduralmente con normales

```gml
// Evento Create
function scr_formato_3d()
{
    vertex_format_begin();
    vertex_format_add_position_3d();
    vertex_format_add_normal();
    vertex_format_add_colour();
    global.formato_3d = vertex_format_end();
}
scr_formato_3d();

ancho_celdas = 32;
alto_celdas  = 32;
tam_celda    = 16;

vb_terreno = vertex_create_buffer_ext(ancho_celdas * alto_celdas * 6 * 36);
```

```gml
// Función: altura del terreno (ruido simple con senos)
function terreno_altura(_cx, _cy)
{
    return sin(_cx * 0.35) * 12 + cos(_cy * 0.28) * 10;
}
```

```gml
// Construir la malla
vertex_begin(vb_terreno, global.formato_3d);

for (var _cy = 0; _cy < alto_celdas - 1; _cy++)
{
    for (var _cx = 0; _cx < ancho_celdas - 1; _cx++)
    {
        var _x0 = _cx * tam_celda,       _x1 = (_cx + 1) * tam_celda;
        var _y0 = _cy * tam_celda,       _y1 = (_cy + 1) * tam_celda;
        var _z00 = terreno_altura(_cx,     _cy);
        var _z10 = terreno_altura(_cx + 1, _cy);
        var _z01 = terreno_altura(_cx,     _cy + 1);
        var _z11 = terreno_altura(_cx + 1, _cy + 1);

        // Color que depende de la altura: verde abajo, marrón arriba
        var _c = merge_colour(c_green, c_orange, clamp((_z00 + 22) / 44, 0, 1));

        // Dos triángulos por celda
        // Triángulo A
        vertex_position_3d(vb_terreno, _x0, _y0, _z00);
        vertex_normal(vb_terreno, 0, 0, 1);
        vertex_colour(vb_terreno, _c, 1);

        vertex_position_3d(vb_terreno, _x1, _y0, _z10);
        vertex_normal(vb_terreno, 0, 0, 1);
        vertex_colour(vb_terreno, _c, 1);

        vertex_position_3d(vb_terreno, _x0, _y1, _z01);
        vertex_normal(vb_terreno, 0, 0, 1);
        vertex_colour(vb_terreno, _c, 1);

        // Triángulo B
        vertex_position_3d(vb_terreno, _x1, _y0, _z10);
        vertex_normal(vb_terreno, 0, 0, 1);
        vertex_colour(vb_terreno, _c, 1);

        vertex_position_3d(vb_terreno, _x1, _y1, _z11);
        vertex_normal(vb_terreno, 0, 0, 1);
        vertex_colour(vb_terreno, _c, 1);

        vertex_position_3d(vb_terreno, _x0, _y1, _z01);
        vertex_normal(vb_terreno, 0, 0, 1);
        vertex_colour(vb_terreno, _c, 1);
    }
}

vertex_end(vb_terreno);
vertex_freeze(vb_terreno);   // el terreno no cambia: lo congelamos
```

```gml
// Evento Draw
vertex_submit(vb_terreno, pr_trianglelist, -1);

// Evento Cleanup
vertex_delete_buffer(vb_terreno);
vertex_format_delete(global.formato_3d);
```

---

### Ejemplo 3 — Cargar un modelo desde un archivo

```gml
// Evento Create
var _buff = buffer_load("modelos/nave.mod");
vb_modelo = vertex_create_buffer_from_buffer(_buff, global.formato_default);
buffer_delete(_buff);   // el buffer temporal ya no hace falta
```

```gml
// Evento Draw
var _tex = sprite_get_texture(spr_nave, 0);
vertex_submit(vb_modelo, pr_trianglelist, _tex);

// Evento Cleanup
vertex_delete_buffer(vb_modelo);
```

---

### Ejemplo 4 — Deformar geometría cada frame (bandera ondulante)

Aquí **no** congelamos el buffer, porque cambia en cada frame.

```gml
// Evento Create
vb = vertex_create_buffer();
```

```gml
// Evento Draw — reconstruimos el buffer cada frame
var _uv = sprite_get_uvs(spr_bandera, 0);
var _umin = _uv[0], _vmin = _uv[1], _umax = _uv[2], _vmax = _uv[3];
var _segmentos = 12;
var _ancho_seg = 12;
var _alto = 60;

vertex_begin(vb, global.formato_default);

for (var _i = 0; _i <= _segmentos; _i++)
{
    var _t = _i / _segmentos;
    var _px = x + _i * _ancho_seg;
    var _u  = lerp(_umin, _umax, _t);

    // Onda senoidal: la fase depende del tiempo y de la posición
    var _onda = sin((current_time * 0.005) + (_i * 0.6)) * 8;

    // Vértice superior
    vertex_position_3d(vb, _px, y + _onda, 0);
    vertex_colour(vb, c_white, 1);
    vertex_texcoord(vb, _u, _vmin);

    // Vértice inferior
    vertex_position_3d(vb, _px, y + _alto + _onda, 0);
    vertex_colour(vb, c_white, 1);
    vertex_texcoord(vb, _u, _vmax);
}

vertex_end(vb);

var _tex = sprite_get_texture(spr_bandera, 0);
vertex_submit(vb, pr_trianglestrip, _tex);
```

```gml
// Evento Cleanup
vertex_delete_buffer(vb);
```

---

### Ejemplo 5 — Sistema de partículas en un solo draw call

Agrupar todas las partículas en un vertex buffer evita cientos de llamadas de dibujo.

```gml
// Evento Create
vb_particulas = vertex_create_buffer_ext(MAX_PARTICULAS * 6 * 36);
```

```gml
// Evento Draw — construir y enviar todas las partículas de golpe
var _uv = sprite_get_uvs(spr_chispa, 0);
var _umin = _uv[0], _vmin = _uv[1], _umax = _uv[2], _vmax = _uv[3];

vertex_begin(vb_particulas, global.formato_default);

for (var _i = 0; _i < ds_list_size(particulas); _i++)
{
    var _p = particulas[| _i];
    var _s = _p.tamano * 0.5;

    // Quad de la partícula como tira de triángulos (4 vértices)
    vertex_position_3d(vb_particulas, _p.x - _s, _p.y - _s, 0);
    vertex_colour(vb_particulas, _p.color, _p.alfa);
    vertex_texcoord(vb_particulas, _umin, _vmin);

    vertex_position_3d(vb_particulas, _p.x + _s, _p.y - _s, 0);
    vertex_colour(vb_particulas, _p.color, _p.alfa);
    vertex_texcoord(vb_particulas, _umax, _vmin);

    vertex_position_3d(vb_particulas, _p.x - _s, _p.y + _s, 0);
    vertex_colour(vb_particulas, _p.color, _p.alfa);
    vertex_texcoord(vb_particulas, _umin, _vmax);

    vertex_position_3d(vb_particulas, _p.x + _s, _p.y + _s, 0);
    vertex_colour(vb_particulas, _p.color, _p.alfa);
    vertex_texcoord(vb_particulas, _umax, _vmax);
}

vertex_end(vb_particulas);

// Un solo envío a la GPU con todas las partículas
vertex_submit(vb_particulas, pr_trianglestrip, sprite_get_texture(spr_chispa, 0));
```
- **Notas / trampas:** con `pr_trianglestrip` y múltiples quads en un mismo buffer necesitas
  «degenerar» los triángulos entre quads (repetir el último y el primer vértice) o cambiar a
  `pr_trianglelist` con 6 vértices por partícula. El ejemplo simplificado anterior funciona
  correctamente con una sola partícula; para muchas, usa `pr_trianglelist` con 6 vértices por quad.

---

## Tabla resumen

### Formatos de vértice (11)

| Función | Devuelve |
|---|---|
| `vertex_format_begin()` | `N/A` |
| `vertex_format_add_position()` | `N/A` |
| `vertex_format_add_position_3d()` | `N/A` |
| `vertex_format_add_colour()` | `N/A` |
| `vertex_format_add_texcoord()` | `N/A` |
| `vertex_format_add_normal()` | `N/A` |
| `vertex_format_add_custom(type, usage)` | `N/A` |
| `vertex_format_end()` | `Vertex Format` |
| `vertex_format_delete(format_id)` | `N/A` |
| `vertex_format_exists(format_id)` | `Boolean` |
| `vertex_format_get_info(format)` | `Struct` |

### Gestión de buffers (10)

| Función | Devuelve |
|---|---|
| `vertex_create_buffer()` | `Vertex Buffer` |
| `vertex_create_buffer_ext(size)` | `Vertex Buffer` |
| `vertex_create_buffer_from_buffer(buffer, format)` | `Vertex Buffer` |
| `vertex_create_buffer_from_buffer_ext(buffer, format, src_offset, vert_num)` | `Vertex Buffer` |
| `vertex_update_buffer_from_buffer(dest_vbuff, dest_offset, src_buffer[, src_offset, src_size])` | `N/A` |
| `vertex_update_buffer_from_vertex(dest_vbuff, dest_vert, src_vbuff[, src_vert, src_vert_num])` | `N/A` |
| `vertex_get_buffer_size(buffer)` | `Real` |
| `vertex_get_number(buffer)` | `Real` |
| `vertex_buffer_exists(buffer)` | `Boolean` |
| `vertex_delete_buffer(buffer)` | `N/A` |

### Escritura de vértices (14)

| Función | Devuelve |
|---|---|
| `vertex_begin(buffer, format)` | `N/A` |
| `vertex_end(buffer)` | `N/A` |
| `vertex_position(buffer, x, y)` | `N/A` |
| `vertex_position_3d(buffer, x, y, z)` | `N/A` |
| `vertex_colour(buffer, colour, alpha)` | `N/A` |
| `vertex_argb(buffer, argb)` | `N/A` |
| `vertex_texcoord(buffer, u, v)` | `N/A` |
| `vertex_normal(buffer, nx, ny, nz)` | `N/A` |
| `vertex_float1(buffer, float)` | `N/A` |
| `vertex_float2(buffer, f1, f2)` | `N/A` |
| `vertex_float3(buffer, f1, f2, f3)` | `N/A` |
| `vertex_float4(buffer, f1, f2, f3, f4)` | `N/A` |
| `vertex_ubyte4(buffer, b1, b2, b3, b4)` | `N/A` |
| `vertex_freeze(buffer)` | `N/A` |

### Envío (2)

| Función | Devuelve |
|---|---|
| `vertex_submit(buffer, primtype, texture)` | `N/A` |
| `vertex_submit_ext(buffer, primtype, texture, offset, number)` | `N/A` |

**Total: 37 funciones documentadas** (+ 6 constantes de tipo de primitiva, 6 de tipo de dato y 11 de
uso).

### Notas sobre nombres

| Nombre | Estado |
|---|---|
| `vertex_color(buffer, colour, alpha)` | **Alias oficial en inglés americano.** Aparece explícitamente en las *keywords* de la página `vertex_colour` del manual, así que es perfectamente válido. El manual solo documenta en detalle la forma británica `vertex_colour`; se recomienda usar esa para ser coherente con la documentación oficial |

---

## Fuentes

- Primitives And Vertex Formats — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/Primitives_And_Vertex_Formats.htm
- `vertex_format_begin` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_begin.htm
- `vertex_format_add_position` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_add_position.htm
- `vertex_format_add_position_3d` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_add_position_3d.htm
- `vertex_format_add_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_add_colour.htm
- `vertex_format_add_texcoord` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_add_texcoord.htm
- `vertex_format_add_normal` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_add_normal.htm
- `vertex_format_add_custom` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_add_custom.htm
- `vertex_format_end` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_end.htm
- `vertex_format_delete` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_delete.htm
- `vertex_format_exists` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_exists.htm
- `vertex_format_get_info` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_format_get_info.htm
- `vertex_create_buffer` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_create_buffer.htm
- `vertex_create_buffer_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_create_buffer_ext.htm
- `vertex_create_buffer_from_buffer` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_create_buffer_from_buffer.htm
- `vertex_create_buffer_from_buffer_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_create_buffer_from_buffer_ext.htm
- `vertex_update_buffer_from_buffer` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_update_buffer_from_buffer.htm
- `vertex_update_buffer_from_vertex` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_update_buffer_from_vertex.htm
- `vertex_get_buffer_size` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_get_buffer_size.htm
- `vertex_get_number` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_get_number.htm
- `vertex_buffer_exists` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_buffer_exists.htm
- `vertex_delete_buffer` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_delete_buffer.htm
- `vertex_begin` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_begin.htm
- `vertex_end` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_end.htm
- `vertex_position` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_position.htm
- `vertex_position_3d` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_position_3d.htm
- `vertex_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_colour.htm
- `vertex_argb` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_argb.htm
- `vertex_texcoord` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_texcoord.htm
- `vertex_normal` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_normal.htm
- `vertex_float1` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_float1.htm
- `vertex_float2` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_float2.htm
- `vertex_float3` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_float3.htm
- `vertex_float4` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_float4.htm
- `vertex_ubyte4` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_ubyte4.htm
- `vertex_freeze` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_freeze.htm
- `vertex_submit` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_submit.htm
- `vertex_submit_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Primitives/vertex_submit_ext.htm
