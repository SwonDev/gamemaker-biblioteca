# 06 — Shaders

> Referencia completa y profunda de GML para **GameMaker LTS 2026.0**
> (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Áreas: `Asset_Management/Shaders/`, `Drawing/Textures/` y `Drawing/GPU_Control/`.
> **16 funciones de shader + 11 funciones de apoyo documentadas.**

---

## Índice

1. [Qué es un shader](#qué-es-un-shader)
2. [Lenguajes de shader por plataforma](#lenguajes-de-shader-por-plataforma)
3. [Anatomía de un shader de GameMaker](#anatomía-de-un-shader-de-gamemaker)
4. [Constantes integradas (uniforms)](#constantes-integradas-uniforms)
5. [Índices de matriz](#índices-de-matriz)
6. [Cómo pasar datos al shader](#cómo-pasar-datos-al-shader)
7. [Referencia de funciones](#referencia-de-funciones)
8. [Funciones de apoyo: texturas y samplers](#funciones-de-apoyo-texturas-y-samplers)
9. [Ejemplos completos de shaders](#ejemplos-completos-de-shaders)
   - [6.1 Desaturación progresiva](#61-desaturación-progresiva)
   - [6.2 Contorno (outline)](#62-contorno-outline)
   - [6.3 Disolución (dissolve)](#63-disolución-dissolve)
   - [6.4 Luz 2D puntual con atenuación](#64-luz-2d-puntual-con-atenuación)
   - [6.5 Onda (wave) de distorsión](#65-onda-wave-de-distorsión)
   - [6.6 Extra: viñeta con corner ID](#66-extra-viñeta-con-corner-id)
10. [Buenas prácticas y trampas](#buenas-prácticas-y-trampas)
11. [Tabla resumen](#tabla-resumen)
12. [Fuentes](#fuentes)

---

## Qué es un shader

Un shader es un **programa de dos partes que se ejecuta directamente en la tarjeta gráfica**. Por
eso es rapidísimo: la GPU hace todo el trabajo y libera ciclos de CPU para la lógica del juego.

El shader completo se compone de:

1. **Vertex shader** — procesa los **vértices** individuales (los puntos de los triángulos con los
   que se renderiza cualquier imagen). GameMaker crea un flujo de vértices —un *vertex buffer*— que
   define la geometría de esos triángulos. Un sprite, por ejemplo, es un «quad» formado por dos
   triángulos. La salida del vertex shader la usa la GPU para ensamblar triángulos, recortarlos y
   enviarlos al rasterizador, que genera los **fragmentos** (estructuras relativas a cada píxel).
2. **Fragment shader** (o *pixel shader*) — recibe esos fragmentos y produce el **color y alfa
   finales** de cada píxel del triángulo renderizado.

Al crear un shader en GameMaker se generan **ambos programas a la vez**, porque no puedes crear un
shader sin las dos partes. Aunque solo quieras usar el fragment shader, necesitas un vertex shader
de «paso through»; por eso el shader nuevo ya viene con ambos escritos.

---

## Lenguajes de shader por plataforma

| Lenguaje de shader | Plataformas de destino |
|---|---|
| **GLSL ES 1.0** | **Todas las plataformas** |
| GLSL | Mac y Ubuntu (Linux) |
| HLSL 11 | Windows y Xbox |
| PSSL | PlayStation 4 y 5 |

**Recomendación del manual:** escribe siempre en **GLSL ES 1.0**, ya que funciona en todas partes, y
sigue la especificación oficial lo más fielmente posible, porque **algunas plataformas son más
estrictas que otras**.

- HTML5 y GX.games usan **WebGL**, que sigue la especificación GLSL ES 1.0 pero **no soporta
  ninguna de sus funcionalidades no obligatorias**.
- Para que los shaders funcionen en HTML5 debes tener **WebGL activado** en las HTML5 Game Options.

Si necesitas **más precisión** matemática (algunos dispositivos Android ejecutan shaders en modo de
baja precisión), añade al principio del fragment shader:

```glsl
precision highp float;
```

---

## Anatomía de un shader de GameMaker

### Vertex shader por defecto (paso through)

```glsl
// ATRIBUTOS: datos que entran por vértice
attribute vec3 in_Position;         // (x, y, z)
//attribute vec3 in_Normal;         // (x, y, z)  solo si el formato de vértice lo incluye
attribute vec4 in_Colour;           // (r, g, b, a)
attribute vec2 in_TextureCoord;     // (u, v)

// VARYINGS: datos que se interpolan hacia el fragment shader
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    // Posición del vértice en espacio de objeto
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);

    // Transformación obligatoria: objeto -> mundo -> vista -> proyección
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;

    // Pasamos color y UV al fragment shader
    v_vColour    = in_Colour;
    v_vTexcoord  = in_TextureCoord;
}
```

### Fragment shader por defecto (paso through)

```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    // Color final = color del vértice x textura muestreada en la UV
    gl_FragColor = v_vColour * texture2D(gm_BaseTexture, v_vTexcoord);
}
```

### Reglas del pipeline

| Concepto | Regla |
|---|---|
| `attribute` | Entrada por vértice, **solo en el vertex shader** |
| `varying` | Se escribe en el vertex shader y se lee en el fragment shader, **interpolado** |
| `uniform` | Valor constante para toda la llamada de dibujo; se fija desde GML |
| `gl_Position` | Salida obligatoria del vertex shader |
| `gl_FragColor` | Salida obligatoria del fragment shader (en GLSL ES 1.0) |
| `texture2D()` | Muestreo de textura en GLSL ES 1.0 |

> **No puedes cambiar el valor de un uniform dentro del shader.** Debes fijarlo desde GML antes de
> dibujar, obteniendo antes su «handle» con `shader_get_uniform()`.

---

## Constantes integradas (uniforms)

Además de las funciones de GLSL ES, GameMaker expone una serie de uniforms propios. Los nombres
empiezan por `gm_`.

### Comunes

| Uniform | Shader | Descripción |
|---|---|---|
| `gm_Matrices[matrix]` | Vertex | Array de `mat4` con las matrices de transformación. Se indexa con las constantes de índice de matriz |
| `gm_BaseTexture` | Fragment | Sampler 2D con la textura que GameMaker está dibujando: la página de textura completa donde está el sprite, la textura de la superficie, o la que pases a `vertex_submit()` |

### Iluminación (solo vertex shader)

| Uniform | Descripción |
|---|---|
| `gm_LightingEnabled` | Booleano: si la iluminación está activa (valor de `draw_light_enable` / `draw_get_lighting`) |
| `gm_Lights_Direction[]` | Array de `vec4`: vector de dirección normalizado **y negado** (X, Y, Z) + W = 1 si la luz está activa, 0 si no. Se configura con `draw_light_define_direction` |
| `gm_Lights_PosRange[]` | Array de `vec4`: posición (X, Y, Z) + W = el rango de la luz (0 si está desactivada). Se configura con `draw_light_define_point` |
| `gm_Lights_Colour[]` | Array de `vec4`: color de la luz (R, G, B), con alfa siempre a 1 |
| `gm_AmbientColour` | `vec4` con el color de la luz ambiental (`draw_light_define_ambient`) |

### Niebla

| Uniform | Shader | Descripción |
|---|---|---|
| `gm_FogStart` | Vertex | Distancia a la que los polígonos empiezan a mezclarse con el color de niebla |
| `gm_RcpFogRange` | Vertex | Distancia a la que la niebla es máxima y ya no se ve nada |
| `gm_PS_FogEnabled` | Fragment | `true` / `false` según si la niebla de píxel está activa en la GPU |
| `gm_VS_FogEnabled` | Vertex | `true` / `false` según si la niebla de vértice está activa |
| `gm_FogColour` | Fragment | El color de niebla usado por GameMaker |

### Alpha testing

| Uniform | Shader | Descripción |
|---|---|---|
| `gm_AlphaTestEnabled` | Fragment | Booleano: si el alpha test está activo (`gpu_set_alphatestenable`) |
| `gm_AlphaRefValue` | Fragment | `float` con el valor de referencia del alpha test (`gpu_set_alphatestref`) |

---

## Índices de matriz

Estas constantes (en realidad `#define`, en MAYÚSCULAS) se usan como **índices del array uniform
`gm_Matrices`**:

| Constante | Descripción |
|---|---|
| `MATRIX_VIEW` | Matriz de vista actual |
| `MATRIX_PROJECTION` | Matriz de proyección actual |
| `MATRIX_WORLD` | Matriz de mundo. Útil para iluminación si tienes información de luz en espacio de mundo |
| `MATRIX_WORLD_VIEW` | Resultado de multiplicar mundo × vista. Se usa a menudo para la niebla |
| `MATRIX_WORLD_VIEW_PROJECTION` | Resultado de mundo × vista × proyección. **Es la matriz normal para transformar posiciones de vértice** |

Otras constantes disponibles:

| Constante | Descripción |
|---|---|
| `MATRICES_MAX` | Tamaño del array de matrices (`gm_Matrices`) en el vertex shader |
| `MAX_VS_LIGHTS` | Número máximo de luces puntuales y direccionales disponibles en el vertex shader |

**Ejemplo:**
```glsl
gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;
```

---

## Cómo pasar datos al shader

El flujo completo desde GML es siempre el mismo:

```gml
// 1. CREATE: obtener los handles UNA vez y guardarlos
u_intensidad = shader_get_uniform(sh_mi_shader, "u_intensidad");
u_color      = shader_get_uniform(sh_mi_shader, "u_color");
u_textura    = shader_get_sampler_index(sh_mi_shader, "s_textura");

// 2. DRAW: activar el shader
shader_set(sh_mi_shader);

// 3. Fijar los uniforms
shader_set_uniform_f(u_intensidad, 0.75);
shader_set_uniform_f(u_color, 1.0, 0.5, 0.0);      // vec3
texture_set_stage(u_textura, sprite_get_texture(spr_ruido, 0));

// 4. Dibujar
draw_self();

// 5. SIEMPRE restaurar
shader_reset();
```

> **Obtén los handles en el Create y guárdalos en variables de instancia o globales.** Llamar a
> `shader_get_uniform()` en cada frame es un coste innecesario.

---

## Referencia de funciones

### `shader_set(shader)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el shader de dibujo. **Todo el dibujo posterior** se hará con él.
- **Ejemplo:**
```gml
shader_set(sh_desaturar);
draw_self();
shader_reset();
```
- **Notas / trampas:** siempre acompáñalo de `shader_reset()` cuando termines.

### `shader_reset()`
- **Devuelve:** `N/A`
- **Qué hace:** restaura el shader por defecto. Debe llamarse cuando ya no quieras usar el shader
  actual.
- **Ejemplo:**
```gml
shader_reset();
```

### `shader_current()`
- **Devuelve:** `Shader Asset` (o handle inválido `-1` si no hay shader activo)
- **Qué hace:** devuelve el shader que se está usando para renderizar.
- **Ejemplo:**
```gml
if (shader_current() != -1) show_debug_message(shader_get_name(shader_current()));
```

### `shader_get_name(shader)`
- **Devuelve:** `String`
- **Qué hace:** devuelve el nombre del recurso de shader.
- **Ejemplo:**
```gml
show_debug_message(shader_get_name(sh_actual)); // "sh_desaturar"
```

### `shader_is_compiled(shader)`
- **Devuelve:** `Boolean`
- **Qué hace:** comprueba en tiempo de ejecución que el shader se ha compilado correctamente.
- **Ejemplo:**
```gml
// Comprobación al arrancar el juego
if (!shader_is_compiled(sh_principal))
{
    show_debug_message("¡El shader no compiló! Usando ruta alternativa");
    usar_shader = false;
}
```
- **Notas / trampas:**
  - El manual recomienda usarla **al inicio del juego** para verificar que la plataforma ha podido
    compilar los shaders. Es especialmente relevante en Windows, donde algunos equipos pueden usar
    DX9 con Shader Level 2.0 en lugar de una versión posterior con nivel 3.0.
  - **Si tu shader no se ha compilado y llamas a `shader_set`, el resultado es indefinido.**

### `shaders_are_supported()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la plataforma de destino soporta shaders.
- **Ejemplo:**
```gml
if (shaders_are_supported())
{
    application_surface_draw_enable(false);
}
```
- **Notas / trampas:**
  - Devuelve `false` en **HTML5 sin WebGL** y en dispositivos Android antiguos.
  - **En Android**, si el proyecto no tiene ningún shader definido, la función devolverá `false`
    (no hay nada que compilar).

### `shader_get_uniform(shader, uniform)`
- **Devuelve:** `Shader Uniform Handle`
- **Qué hace:** obtiene el handle de una constante (uniform) del shader por su nombre.
- **Ejemplo:**
```gml
// Evento Create
u_tiempo = shader_get_uniform(sh_agua, "u_tiempo");
u_color  = shader_get_uniform(sh_agua, "u_color");
```
- **Notas / trampas:** aunque un shader son dos programas distintos (vertex y fragment), esta
  función **no los diferencia**: devuelve el handle del uniform de cualquiera de los dos.

### `shader_get_sampler_index(shader, uniform)`
- **Devuelve:** `Shader Sampler Handle`
- **Qué hace:** obtiene el handle de un sampler del shader por su nombre, para después asignarle una
  textura con `texture_set_stage()`.
- **Ejemplo:**
```gml
// Evento Create
s_ruido = shader_get_sampler_index(sh_disolver, "s_ruido");

// Evento Draw
texture_set_stage(s_ruido, sprite_get_texture(spr_ruido, 0));
```
- **Notas / trampas:** igual que `shader_get_uniform`, no distingue entre vertex y fragment.

### `shader_set_uniform_f(handle, value1 [, value2, value3, value4])`
- **Devuelve:** `N/A`
- **Qué hace:** fija el valor (o valores) de una constante de tipo **coma flotante**.
- **Ejemplo:**
```gml
// float
shader_set_uniform_f(u_intensidad, 0.75);

// vec2
shader_set_uniform_f(u_resolucion, 1920.0, 1080.0);

// vec3
shader_set_uniform_f(u_color, 1.0, 0.5, 0.0);
```
- **Notas / trampas:**
  - Debes saber **qué tipo** es la constante para pasar el número correcto de valores: un `vec2`
    necesita dos valores, un `vec3` tres, etc.
  - **Excepción con colores de 32 bits:** puedes pasar hasta **ocho valores de color de 32 bits** y
    GameMaker los convierte automáticamente en `vec4` con componentes de 0 a 1. Para eso
    **obligatoriamente** debes pasarlos como colores.

### `shader_set_uniform_f_array(handle, array)`
- **Devuelve:** `N/A`
- **Qué hace:** fija una constante a un **array de valores en coma flotante**.
- **Ejemplo:**
```gml
// Array de pesos para un kernel de desenfoque
var _pesos = [0.227, 0.194, 0.121, 0.054, 0.016];
shader_set_uniform_f_array(u_pesos, _pesos);
```

### `shader_set_uniform_f_buffer(uniform, buffer, offset, count)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el valor de un uniform a una lista de valores en coma flotante almacenados en
  un **buffer**.
- **Argumentos:** `uniform` (handle), `buffer` (el buffer a leer), `offset` (desplazamiento en
  **bytes**), `count` (número de valores de tipo `buffer_f32` a usar).
- **Ejemplo:**
```gml
// Enviar 64 posiciones de luz desde un buffer
shader_set_uniform_f_buffer(u_luces, buff_luces, 0, 64);
```

### `shader_set_uniform_i(handle, value1 [, value2, value3, value4])`
- **Devuelve:** `N/A`
- **Qué hace:** fija el valor (o valores) de una constante de tipo **entero**.
- **Ejemplo:**
```gml
shader_set_uniform_i(u_num_luces, 4);
shader_set_uniform_i(u_flags, 1, 0, 1);
```
- **Notas / trampas:** también funciona con booleanos declarados como `bool` en el shader.

### `shader_set_uniform_i_array(handle, array)`
- **Devuelve:** `N/A`
- **Qué hace:** fija una constante a un array de valores **enteros**.
- **Ejemplo:**
```gml
var _tipos = [0, 1, 1, 0];
shader_set_uniform_i_array(u_tipos_luz, _tipos);
```

### `shader_set_uniform_matrix(handle)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el valor de una constante de shader a la **matriz de transformación actual**
  (la que hayas configurado con las funciones de matrices de GML).
- **Ejemplo:**
```gml
// Pasar una matriz de rotación propia al shader
var _mat = matrix_build(x, y, 0, 0, 0, angulo, 1, 1, 1);
matrix_set(matrix_world, _mat);
shader_set_uniform_matrix(u_matriz_rotacion);
draw_self();
matrix_set(matrix_world, matrix_build_identity());
```

### `shader_set_uniform_matrix_array(handle, array)`
- **Devuelve:** `N/A`
- **Qué hace:** fija una constante a un **array de matrices**.
- **Ejemplo:**
```gml
// Enviar 4 matrices de 4x4 = 16 floats cada una = 64 valores
var _mats = array_create(4 * 16);
// ... rellenar _mats con los 64 floats ...
shader_set_uniform_matrix_array(u_matrices, _mats);
```
- **Notas / trampas:** la longitud del array **debe ser múltiplo de 16**, es decir
  `numero_de_matrices * 16`.

### `shader_enable_corner_id(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa el uso de **IDs de esquina** en los shaders. Fija un estado global para todos
  los shaders: al activarlo, el shader «roba» 2 bits de los valores de color de entrada —uno del bit
  más bajo del rojo y otro del bit más bajo del azul—. El shader puede recuperarlos para saber
  **con qué vértice (qué esquina) está trabajando**.
- **Cómo calcularlo en el vertex shader:**
```glsl
vec2 rem = mod(in_Colour.rb * 255., 2.);
int corner_id = int(dot(vec2(1., 2.), rem));
```
- **Tabla de IDs de esquina:**

  | Bit bajo de rojo | Bit bajo de azul | Corner ID | Posición |
  |---|---|---|---|
  | 0 | 0 | 0 | superior izquierda |
  | 1 | 0 | 1 | superior derecha |
  | 0 | 1 | 2 | inferior derecha |
  | 1 | 1 | 3 | inferior izquierda |

- **Notas / trampas:**
  - El **bit más bajo del azul** almacena el **bit más significativo**; el del **rojo**, el menos
    significativo.
  - **NO funciona con vertex buffers ni primitivas**, porque en ese caso el color de cada vértice lo
    gestiona el usuario.

---

## Funciones de apoyo: texturas y samplers

### `texture_set_stage(stage, tex)`
- **Devuelve:** `N/A`
- **Qué hace:** asigna una textura a un «slot» (sampler) del shader.
- **Ejemplo:**
```gml
var _sampler = shader_get_sampler_index(sh_disolver, "s_ruido");
var _tex     = sprite_get_texture(spr_ruido, 0);
texture_set_stage(_sampler, _tex);
```
- **Notas / trampas:** el primer argumento puede ser un handle de sampler **o un número real**
  (índice de slot).

### `texture_get_width(tex)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve la anchura de la página de textura.
- **Ejemplo:**
```gml
var _ancho = texture_get_width(sprite_get_texture(spr_fondo, 0));
```

### `texture_get_height(tex)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve la altura de la página de textura.
- **Ejemplo:**
```gml
var _alto = texture_get_height(surface_get_texture(surf));
```

### `texture_get_texel_width(tex)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el ancho de **un texel** (un píxel de textura) expresado como fracción de
  la textura: `1 / anchura`. Esencial para efectos que miran píxeles vecinos.
- **Ejemplo:**
```gml
// Enviar el tamaño de texel al shader para un efecto de contorno
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
var _uv = texture_get_uvs(sprite_get_texture(spr_jugador, 0));
var _u0 = _uv[0], _v0 = _uv[1], _u1 = _uv[2], _v1 = _uv[3];
```

### `sprite_get_texture(sprite, subimage)`
- **Devuelve:** `Texture`
- **Qué hace:** devuelve la textura de la página donde está el subimage indicado del sprite.
- **Ejemplo:**
```gml
var _tex = sprite_get_texture(spr_ruido, 0);
texture_set_stage(s_ruido, _tex);
```

### `sprite_get_uvs(sprite, subimage)`
- **Devuelve:** `Array`
- **Qué hace:** devuelve las UV del sprite **dentro de la página de textura**. Imprescindible para
  vertex buffers, donde `(0,0)`–`(1,1)` cubre la página completa.
- **Ejemplo:**
```gml
var _uv = sprite_get_uvs(spr_bandera, 0);
var _umin = _uv[0], _vmin = _uv[1], _umax = _uv[2], _vmax = _uv[3];
```

### `font_get_texture(font)` / `font_get_uvs(font)`
- **Devuelven:** `Texture` / `Array`
- **Qué hacen:** equivalente para fuentes. Documentadas en **03 - Texto y fuentes**.

### `gpu_set_texfilter_ext(sampler_id, enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la interpolación lineal **de un sampler concreto**.
- **Ejemplo:**
```gml
var _s = shader_get_sampler_index(sh_agua, "s_ruido");
gpu_set_texfilter_ext(_s, true);
```

### `gpu_set_texrepeat_ext(sampler_id, enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva la repetición de textura **de un sampler concreto**.
- **Ejemplo:**
```gml
// El ruido debe repetirse para que el scroll sea infinito
var _s = shader_get_sampler_index(sh_agua, "s_ruido");
gpu_set_texrepeat_ext(_s, true);
```

---

## Ejemplos completos de shaders

Los cinco shaders siguientes son **completos y funcionales** en GLSL ES 1.0 (válidos en todas las
plataformas, incluido HTML5 con WebGL).

---

### 6.1 Desaturación progresiva

Convierte el sprite a escala de grises con una intensidad regulable. Ideal para efectos de
«muerte», pausa o flashback.

**Vertex shader** (`sh_desaturar.vsh`):
```glsl
// Atributos de entrada por vértice
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

// Datos que se interpolan hacia el fragment shader
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    // Transformación estándar: objeto -> mundo -> vista -> proyección
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;

    // Pasamos el color del vértice y las coordenadas de textura
    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

**Fragment shader** (`sh_desaturar.fsh`):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

// Intensidad de la desaturación: 0 = color original, 1 = gris completo
uniform float u_intensidad;

void main()
{
    // Muestreamos el color original de la textura
    vec4 color_base = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;

    // Luminancia perceptual (pesos estándar de Rec. 601)
    // El ojo es más sensible al verde que al rojo, y al rojo que al azul
    float luminancia = dot(color_base.rgb, vec3(0.299, 0.587, 0.114));

    // Mezclamos entre el color original y el gris según la intensidad
    vec3 resultado = mix(color_base.rgb, vec3(luminancia), u_intensidad);

    // El alfa se conserva intacto
    gl_FragColor = vec4(resultado, color_base.a);
}
```

**Código GML:**
```gml
// Evento Create
u_intensidad = shader_get_uniform(sh_desaturar, "u_intensidad");
desaturacion = 0;

// Evento Step: sube la desaturación al morir
if (muriendo) desaturacion = min(desaturacion + 0.02, 1);

// Evento Draw
shader_set(sh_desaturar);
shader_set_uniform_f(u_intensidad, desaturacion);
draw_self();
shader_reset();
```

---

### 6.2 Contorno (outline)

Añade un contorno de color alrededor de la silueta del sprite, muestreando los píxeles vecinos y
detectando los bordes por alfa.

**Vertex shader** (`sh_outline.vsh`):
```glsl
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;

    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

**Fragment shader** (`sh_outline.fsh`):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

// Tamaño de un texel: 1.0 / ancho y 1.0 / alto de la página de textura
uniform vec2 u_texel;

// Color y grosor del contorno
uniform vec3 u_color_borde;
uniform float u_grosor;

void main()
{
    // Color del píxel actual
    vec4 centro = texture2D(gm_BaseTexture, v_vTexcoord);

    // Acumulamos el alfa de los 4 vecinos (arriba, abajo, izquierda, derecha)
    // escalados por el grosor pedido
    vec2 d = u_texel * u_grosor;
    float alfa_vecinos = 0.0;
    alfa_vecinos += texture2D(gm_BaseTexture, v_vTexcoord + vec2( d.x, 0.0)).a;
    alfa_vecinos += texture2D(gm_BaseTexture, v_vTexcoord + vec2(-d.x, 0.0)).a;
    alfa_vecinos += texture2D(gm_BaseTexture, v_vTexcoord + vec2(0.0,  d.y)).a;
    alfa_vecinos += texture2D(gm_BaseTexture, v_vTexcoord + vec2(0.0, -d.y)).a;

    // Si algún vecino tiene alfa, estamos en el borde exterior
    float borde = clamp(alfa_vecinos, 0.0, 1.0);

    // Componemos: el borde primero, el sprite original encima
    vec3 color_borde = u_color_borde * borde;
    vec3 color_final = mix(color_borde, centro.rgb, centro.a);

    float alfa_final = max(borde, centro.a) * v_vColour.a;

    gl_FragColor = vec4(color_final * v_vColour.rgb, alfa_final);
}
```

**Código GML:**
```gml
// Evento Create
u_texel       = shader_get_uniform(sh_outline, "u_texel");
u_color_borde = shader_get_uniform(sh_outline, "u_color_borde");
u_grosor      = shader_get_uniform(sh_outline, "u_grosor");

// Evento Draw
var _tex = sprite_get_texture(sprite_index, image_index);

shader_set(sh_outline);
shader_set_uniform_f(u_texel,
                     texture_get_texel_width(_tex),
                     texture_get_texel_height(_tex));
shader_set_uniform_f(u_color_borde, 0.0, 0.0, 0.0); // contorno negro
shader_set_uniform_f(u_grosor, 2.0);                // 2 píxeles de grosor
draw_self();
shader_reset();
```

---

### 6.3 Disolución (dissolve)

Desintegra el sprite usando una textura de ruido como umbral. Efecto clásico de muerte o
aparición.

**Vertex shader** (`sh_disolver.vsh`):
```glsl
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;

    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

**Fragment shader** (`sh_disolver.fsh`):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

// Textura de ruido en escala de grises
uniform sampler2D s_ruido;

// Progreso de la disolución: 0 = intacto, 1 = totalmente disuelto
uniform float u_progreso;

// Color y anchura del «borde ardiente» en el frente de disolución
uniform vec3 u_color_borde;
uniform float u_ancho_borde;

void main()
{
    vec4 color_base = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;

    // Muestreamos el ruido en la misma UV del sprite
    float ruido = texture2D(s_ruido, v_vTexcoord).r;

    // Descartamos el fragmento si el ruido es menor que el progreso:
    // así el sprite se «agujerea» siguiendo el patrón del ruido
    if (ruido < u_progreso)
    {
        discard;
    }

    //Calculamos la distancia al frente de disolución para el borde ardiente
    float distancia = ruido - u_progreso;
    float borde = 1.0 - smoothstep(0.0, u_ancho_borde, distancia);

    // Mezclamos el color original con el del borde
    vec3 color_final = mix(color_base.rgb, u_color_borde, borde);

    gl_FragColor = vec4(color_final, color_base.a);
}
```

**Código GML:**
```gml
// Evento Create
s_ruido        = shader_get_sampler_index(sh_disolver, "s_ruido");
u_progreso     = shader_get_uniform(sh_disolver, "u_progreso");
u_color_borde  = shader_get_uniform(sh_disolver, "u_color_borde");
u_ancho_borde  = shader_get_uniform(sh_disolver, "u_ancho_borde");
progreso       = 0;

// Evento Step
if (disolviendo) progreso = min(progreso + 0.01, 1);

// Evento Draw
shader_set(sh_disolver);
texture_set_stage(s_ruido, sprite_get_texture(spr_ruido_disolver, 0));
shader_set_uniform_f(u_progreso, progreso);
shader_set_uniform_f(u_color_borde, 1.0, 0.4, 0.0); // naranja ardiente
shader_set_uniform_f(u_ancho_borde, 0.08);
draw_self();
shader_reset();
```
- **Notas / trampas:** `discard` es costoso en algunas GPUs móviles. Si necesitas máximo rendimiento,
  usa `gl_FragColor = vec4(0.0);` en lugar de `discard` (aunque eso dibuja negro en vez de
  transparente, así que solo sirve si el fondo es negro).

---

### 6.4 Luz 2D puntual con atenuación

Ilumina una escena con una luz puntual en coordenadas de pantalla, con radio, color e intensidad
configurables. Se aplica a la **Application Surface completa** y multiplica la luz por la escena.

**Vertex shader** (`sh_luz2d.vsh`):
```glsl
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;

    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

**Fragment shader** (`sh_luz2d.fsh`):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

precision highp float;   // mayor precisión: importante en Android

// Resolución de la superficie (en píxeles) para convertir UV a píxeles
uniform vec2 u_resolucion;

// Posición de la luz en PÍXELES (coordenadas de la superficie)
uniform vec2 u_posicion_luz;

// Radio de la luz en píxeles
uniform float u_radio;

// Color e intensidad de la luz
uniform vec3 u_color_luz;
uniform float u_intensidad;

// Color ambiental: lo que se ve donde NO llega la luz
uniform vec3 u_ambiente;

void main()
{
    // Color original de la escena
    vec4 escena = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;

    // Convertimos la UV actual a píxeles dentro de la superficie
    vec2 pixel = v_vTexcoord * u_resolucion;

    // Distancia en píxeles desde el píxel actual hasta la luz
    float distancia = distance(pixel, u_posicion_luz);

    // Atenuación suave y cuadrática: 1 en el centro, 0 en el borde del radio
    float atenuacion = 1.0 - clamp(distancia / u_radio, 0.0, 1.0);
    atenuacion = atenuacion * atenuacion;   // caída cuadrática, más natural

    // Luz total = ambiente + aporte de la luz atenuada
    vec3 luz = u_ambiente + u_color_luz * (atenuacion * u_intensidad);

    // Multiplicamos la escena por la luz
    gl_FragColor = vec4(escena.rgb * luz, escena.a);
}
```

**Código GML:**
```gml
// Evento Create del controlador de luces
application_surface_draw_enable(false);

u_resolucion     = shader_get_uniform(sh_luz2d, "u_resolucion");
u_posicion_luz   = shader_get_uniform(sh_luz2d, "u_posicion_luz");
u_radio          = shader_get_uniform(sh_luz2d, "u_radio");
u_color_luz      = shader_get_uniform(sh_luz2d, "u_color_luz");
u_intensidad     = shader_get_uniform(sh_luz2d, "u_intensidad");
u_ambiente       = shader_get_uniform(sh_luz2d, "u_ambiente");

// Evento Draw GUI (la escena ya está dibujada en la Application Surface)
var _pos = application_get_position();
var _ancho = _pos[2] - _pos[0];
var _alto  = _pos[3] - _pos[1];

shader_set(sh_luz2d);

// La superficie puede tener otra resolución: la pasamos para el cálculo
shader_set_uniform_f(u_resolucion,
                     surface_get_width(application_surface),
                     surface_get_height(application_surface));

// Posición de la luz del jugador en coordenadas de la superficie
var _lx = (obj_player.x / room_width)  * surface_get_width(application_surface);
var _ly = (obj_player.y / room_height) * surface_get_height(application_surface);
shader_set_uniform_f(u_posicion_luz, _lx, _ly);

shader_set_uniform_f(u_radio, 320.0);
shader_set_uniform_f(u_color_luz, 1.0, 0.85, 0.6); // luz cálida
shader_set_uniform_f(u_intensidad, 1.6);
shader_set_uniform_f(u_ambiente, 0.12, 0.12, 0.20); // azul noche tenue

draw_surface_stretched(application_surface, _pos[0], _pos[1], _ancho, _alto);
shader_reset();
```

---

### 6.5 Onda (wave) de distorsión

Deforma horizontalmente el sprite o la pantalla con una onda sinusoidal. Funciona tanto como efecto
de «bandera» como de distorsión de calor o agua.

**Vertex shader** (`sh_onda.vsh`):
```glsl
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

varying vec2 v_vTexcoord;
varying vec4 v_vColour;

// Tiempo en segundos, amplitud en píxeles y frecuencia de la onda
uniform float u_tiempo;
uniform float u_amplitud;
uniform float u_frecuencia;

void main()
{
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);

    // Desplazamiento vertical sinusoidal en función de X y del tiempo
    // in_Position.x está en espacio de objeto (píxeles del sprite)
    float desplazamiento = sin((in_Position.x * u_frecuencia) + u_tiempo) * u_amplitud;
    object_space_pos.y += desplazamiento;

    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;

    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

**Fragment shader** (`sh_onda.fsh`):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    // El fragmento no hace nada especial: la deformación ocurrió en el vértice
    gl_FragColor = v_vColour * texture2D(gm_BaseTexture, v_vTexcoord);
}
```

**Código GML:**
```gml
// Evento Create
u_tiempo     = shader_get_uniform(sh_onda, "u_tiempo");
u_amplitud   = shader_get_uniform(sh_onda, "u_amplitud");
u_frecuencia = shader_get_uniform(sh_onda, "u_frecuencia");

// Evento Draw
shader_set(sh_onda);
shader_set_uniform_f(u_tiempo, current_time / 1000); // segundos
shader_set_uniform_f(u_amplitud, 6.0);               // 6 px de recorrido
shader_set_uniform_f(u_frecuencia, 0.05);            // onda suave
draw_sprite(spr_bandera, 0, x, y);
shader_reset();
```

**Variante: distorsión de pantalla.** Si aplicas el mismo shader a la Application Surface, el
desplazamiento debe hacerse en el **fragment shader** (porque la superficie es un quad y no tiene
suficientes vértices):

```glsl
// Fragment shader para distorsión de la Application Surface
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform float u_tiempo;
uniform float u_amplitud;

void main()
{
    // Desplazamos la coordenada de MUERSTREO, no la geometría
    vec2 uv = v_vTexcoord;
    uv.x += sin((uv.y * 20.0) + u_tiempo * 3.0) * u_amplitud;

    gl_FragColor = v_vColour * texture2D(gm_BaseTexture, uv);
}
```

---

### 6.6 Extra: viñeta con corner ID

Ejemplo que usa `shader_enable_corner_id()` para saber en qué esquina estamos y construir una UV
normalizada sin necesidad de uniforms extra.

**Vertex shader:**
```glsl
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

varying vec2 v_vTexcoord;
varying vec4 v_vColour;
varying vec2 v_vPosicion;      // posición normalizada 0..1 dentro del quad

// Devuelve 0..1 según la posición del vértice en el quad
// usando los bits de esquina que inyecta GameMaker
float indice_esquina(vec4 color)
{
    vec2 rem = mod(color.rb * 255., 2.);
    return dot(vec2(1., 2.), rem);
}

void main()
{
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;

    // corner_id: 0 = sup. izq., 1 = sup. der., 2 = inf. der., 3 = inf. izq.
    float corner_id = indice_esquina(in_Colour);

    // Reconstruimos la posición normalizada dentro del quad
    v_vPosicion.x = (corner_id == 1.0 || corner_id == 2.0) ? 1.0 : 0.0;
    v_vPosicion.y = (corner_id >= 2.0) ? 1.0 : 0.0;

    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

**Fragment shader:**
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;
varying vec2 v_vPosicion;

uniform float u_fuerza;   // 0 = sin viñeta, 1 = bordes muy oscuros

void main()
{
    vec4 color_base = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;

    // Distancia desde el centro del quad (0,5 ; 0,5)
    float d = distance(v_vPosicion, vec2(0.5, 0.5));

    // Viñeta: se oscurece hacia los bordes
    float vineta = smoothstep(0.8, 0.25, d);
    float oscurecido = mix(1.0, vineta, u_fuerza);

    gl_FragColor = vec4(color_base.rgb * oscurecido, color_base.a);
}
```

**Código GML:**
```gml
// Evento Create — activar los IDs de esquina UNA vez
shader_enable_corner_id(true);
u_fuerza = shader_get_uniform(sh_vineta, "u_fuerza");

// Evento Draw GUI
shader_set(sh_vineta);
shader_set_uniform_f(u_fuerza, 0.8);
draw_surface_stretched(application_surface, 0, 0, display_get_gui_width(), display_get_gui_height());
shader_reset();
```
- **Notas / trampas:** recuerda que los corner IDs **no funcionan con vertex buffers ni
  primitivas**, porque el color de cada vértice lo define el usuario.

---

## Palette swap (intercambio de paleta)

Cambiar los colores de un sprite sin repintarlo: equipos de color, personalización de
personaje, o **modos daltónicos** ([27 · Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md)).
La idea: el sprite usa unos pocos colores "índice"; el shader los sustituye por los de una
paleta de destino.

**Método simple (pocos colores):** un `uniform` con los colores de origen y de destino, y el
shader reemplaza cada píxel que coincida.

```glsl
// shd_palette.fsh — reemplaza hasta 4 colores
varying vec2 v_vTexcoord;
varying vec4 v_vColour;
uniform vec3 u_origen[4];
uniform vec3 u_destino[4];

void main() {
    vec4 col = texture2D(gm_BaseTexture, v_vTexcoord);
    for (int i = 0; i < 4; i++) {
        if (distance(col.rgb, u_origen[i]) < 0.02) {
            col.rgb = u_destino[i];
        }
    }
    gl_FragColor = v_vColour * col;
}
```

```gml
/// pasar las paletas al shader antes de dibujar
shader_set(shd_palette);
shader_set_uniform_f_array(shader_get_uniform(shd_palette, "u_origen"),  paleta_origen);
shader_set_uniform_f_array(shader_get_uniform(shd_palette, "u_destino"), paleta_equipo_rojo);
draw_self();
shader_reset();
```

> 💡 **Para muchos colores, usa una textura de paleta** (una fila de píxeles) y busca por índice
> en vez de comparar color a color: mucho más rápido y escalable. La librería
> [Chameleon](../07%20-%20Ecosistema/02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md) ya
> lo resuelve si no quieres escribir el shader.
>
> 🔺 **`shader_set_uniform_f_array` sí existe; `shader_set_uniform_f_buffer` es la variante con
> búfer.** Verifica ambas con `buscar.py` antes de elegir.

---

## Buenas prácticas y trampas

1. **Obtén los handles una sola vez.** `shader_get_uniform()` y `shader_get_sampler_index()` en el
   Create, guardados en variables. Nunca por frame.
2. **Siempre `shader_reset()`.** Olvidarlo hace que todo el dibujo posterior del juego use tu shader
   sin querer.
3. **Comprueba la compilación al arrancar** con `shader_is_compiled()` y
   `shaders_are_supported()`, sobre todo si apuntas a HTML5 o Android antiguos.
4. **`precision highp float;`** al principio del fragment shader si haces matemáticas exigentes;
   algunos dispositivos Android ejecutan shaders en baja precisión por defecto.
5. **Cuidado con `discard`**: puede ser muy costoso en GPUs móviles, porque deshabilita
   optimizaciones de profundidad temprana.
6. **Las funciones de formas (`draw_rectangle`, `draw_circle`, …) solo envían vértice y color**,
   sin coordenada de textura. Un shader que espere `v_vTexcoord` puede no dibujar nada sobre ellas.
7. **`gm_BaseTexture` es la página de textura COMPLETA**, no el sprite. Por eso las UV de los
   sprites llegan ya ajustadas a su región: para sprites dibujados con `draw_sprite*` las UV van de
   0 a 1 dentro de la región del sprite, pero al trabajar con **vertex buffers** debes usar
   `sprite_get_uvs()`.
8. **Los shaders no se aplican antes del dibujo**: se aplican a lo que dibujes entre `shader_set()`
   y `shader_reset()`. Si quieres post-procesar toda la escena, desactiva el dibujado automático con
   `application_surface_draw_enable(false)` y dibuja tú la Application Surface con el shader.
9. **Evita WebGL en HTML5 sin soporte**: sin WebGL, HTML5 no ejecuta shaders.
10. **Depuración:** si un shader no hace nada, comprueba primero que los nombres de los uniforms en
    GML coinciden **exactamente** (distingue mayúsculas) con los del código GLSL.

---

## Tabla resumen

### Funciones de shader (16)

| Función | Devuelve |
|---|---|
| `shader_set(shader)` | `N/A` |
| `shader_reset()` | `N/A` |
| `shader_current()` | `Shader Asset` |
| `shader_get_name(shader)` | `String` |
| `shader_is_compiled(shader)` | `Boolean` |
| `shaders_are_supported()` | `Boolean` |
| `shader_get_uniform(shader, uniform)` | `Shader Uniform Handle` |
| `shader_get_sampler_index(shader, uniform)` | `Shader Sampler Handle` |
| `shader_set_uniform_f(handle, v1[, v2, v3, v4])` | `N/A` |
| `shader_set_uniform_f_array(handle, array)` | `N/A` |
| `shader_set_uniform_f_buffer(uniform, buffer, offset, count)` | `N/A` |
| `shader_set_uniform_i(handle, v1[, v2, v3, v4])` | `N/A` |
| `shader_set_uniform_i_array(handle, array)` | `N/A` |
| `shader_set_uniform_matrix(handle)` | `N/A` |
| `shader_set_uniform_matrix_array(handle, array)` | `N/A` |
| `shader_enable_corner_id(enable)` | `N/A` |

### Funciones de apoyo (11)

| Función | Devuelve |
|---|---|
| `texture_set_stage(stage, tex)` | `N/A` |
| `texture_get_width(tex)` | `Real` |
| `texture_get_height(tex)` | `Real` |
| `texture_get_texel_width(tex)` | `Real` |
| `texture_get_texel_height(tex)` | `Real` |
| `texture_get_uvs(texid)` | `Array` (4–8) |
| `sprite_get_texture(sprite, subimage)` | `Texture` |
| `sprite_get_uvs(sprite, subimage)` | `Array` |
| `font_get_texture(font)` | `Texture` |
| `font_get_uvs(font)` | `Array` |
| `gpu_set_texfilter_ext(sampler_id, enable)` / `gpu_set_texrepeat_ext(sampler_id, enable)` | `N/A` |

**Total: 27 funciones documentadas** + 5 shaders completos + 1 extra.

### Función que NO existe

| Solicitada | Estado |
|---|---|
| `shader_set_uniform_i_buffer()` | **No existe.** Solo hay `shader_set_uniform_f_buffer()` (versión float) |

---

## Fuentes

- Shaders — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/Shaders.htm
- The Shader Editor — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/The_Shader_Editor.htm
- Built-In Shader Constants — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/Shader_Constants.htm
- `shader_set` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set.htm
- `shader_reset` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_reset.htm
- `shader_current` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_current.htm
- `shader_get_name` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_get_name.htm
- `shader_is_compiled` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_is_compiled.htm
- `shaders_are_supported` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shaders_are_supported.htm
- `shader_get_uniform` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_get_uniform.htm
- `shader_get_sampler_index` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_get_sampler_index.htm
- `shader_set_uniform_f` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set_uniform_f.htm
- `shader_set_uniform_f_array` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set_uniform_f_array.htm
- `shader_set_uniform_f_buffer` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set_uniform_f_buffer.htm
- `shader_set_uniform_i` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set_uniform_i.htm
- `shader_set_uniform_i_array` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set_uniform_i_array.htm
- `shader_set_uniform_matrix` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set_uniform_matrix.htm
- `shader_set_uniform_matrix_array` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set_uniform_matrix_array.htm
- `shader_enable_corner_id` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_enable_corner_id.htm
- `texture_set_stage` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_set_stage.htm
- `texture_get_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_width.htm
- `texture_get_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_height.htm
- `texture_get_texel_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_texel_width.htm
- `texture_get_texel_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_texel_height.htm
- `texture_get_uvs` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texture_get_uvs.htm
- `sprite_get_texture` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Information/sprite_get_texture.htm
- `sprite_get_uvs` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Information/sprite_get_uvs.htm
- `font_get_texture` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_texture.htm
- `font_get_uvs` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_uvs.htm
- `gpu_set_texfilter_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_texfilter_ext.htm
- `gpu_set_texrepeat_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_texrepeat_ext.htm
