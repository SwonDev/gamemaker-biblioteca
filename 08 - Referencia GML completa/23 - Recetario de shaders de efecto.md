# 23 — Recetario de shaders de efecto

> Diez shaders de efecto completos y listos para copiar, más la pieza que les falta a todos:
> una **cadena de post-procesado multipasada** con ping-pong entre dos superficies. Este
> documento da por sabida la anatomía de un shader de GameMaker, los uniforms integrados y los
> seis shaders base (desaturar, outline, dissolve, luz 2D, onda, viñeta): eso está en
> [08 · 06 — Shaders](./06%20-%20Shaders.md) y no se repite aquí. Tampoco repite el ciclo de
> vida de las superficies (eso es [08 · 05](./05%20-%20Superficies.md)) ni los modos de mezcla
> (eso es [08 · 04](./04%20-%20Color%20y%20blending.md)). Lo que sí trae: **hit flash**,
> aberración cromática, CRT/scanlines, glitch, pixelado/posterizado, shockwave, heat haze
> localizado, blur gaussiano de dos pasadas, bloom (la cadena completa) y grading por LUT.

---

## Índice

1. [Los principios](#1--los-principios)
   - [1.1 Qué falta aquí que no esté en 08 · 06](#11-qué-falta-aquí-que-no-esté-en-08--06)
   - [1.2 Dónde vive cada shader: por instancia o de pantalla completa](#12-dónde-vive-cada-shader-por-instancia-o-de-pantalla-completa)
   - [1.3 LDR frente a HDR: cuándo importa `surface_rgba16float`](#13-ldr-frente-a-hdr-cuándo-importa-surface_rgba16float)
   - [1.4 Por qué encadenar pasadas en vez de un shader gigante](#14-por-qué-encadenar-pasadas-en-vez-de-un-shader-gigante)
2. [El método, paso a paso](#2--el-método-paso-a-paso)
   - [2.1 La cadena de post-procesado multipasada (ping-pong)](#21-la-cadena-de-post-procesado-multipasada-ping-pong)
3. [Las diez recetas](#3--las-diez-recetas)
   - [3.1 Hit flash](#31-hit-flash--el-parpadeo-al-recibir-daño)
   - [3.2 Aberración cromática](#32-aberración-cromática)
   - [3.3 CRT / scanlines](#33-crt--scanlines)
   - [3.4 Glitch / datamosh](#34-glitch--datamosh)
   - [3.5 Pixelado y posterizado](#35-pixelado-y-posterizado)
   - [3.6 Shockwave (distorsión radial expansiva)](#36-shockwave-distorsión-radial-expansiva)
   - [3.7 Heat haze localizado](#37-heat-haze-localizado)
   - [3.8 Blur gaussiano de dos pasadas](#38-blur-gaussiano-de-dos-pasadas)
   - [3.9 Bloom: la cadena completa](#39-bloom-la-cadena-completa)
   - [3.10 Color grading por LUT](#310-color-grading-por-lut)
4. [Checklist antes de dar un shader por terminado](#4--checklist-antes-de-dar-un-shader-por-terminado)
5. [Errores clásicos y cómo evitarlos](#5--errores-clásicos-y-cómo-evitarlos)
6. [Tabla resumen](#6--tabla-resumen)
7. [Ver también](#ver-también)
8. [Fuentes](#fuentes)

---

## 1 · Los principios

### 1.1 Qué falta aquí que no esté en 08 · 06

`08 · 06` ya cubre la anatomía de un shader de GameMaker (vertex + fragment, uniforms `gm_*`,
índices de matriz, GLSL ES 1.0 por plataforma) y seis efectos completos: desaturación, outline,
dissolve, luz 2D puntual, onda de distorsión y viñeta con corner ID, más el intercambio de
paleta. Este documento es su **recetario hermano**: los diez efectos que un juego 2D pide antes
o después y que no estaban escritos en ningún sitio de la biblioteca, más la infraestructura de
post-procesado que varios de ellos necesitan para funcionar en más de una pasada.

Si vienes de cero, lee primero
[08 · 06 §Anatomía de un shader de GameMaker](./06%20-%20Shaders.md#anatomía-de-un-shader-de-gamemaker)
y [§Cómo pasar datos al shader](./06%20-%20Shaders.md#cómo-pasar-datos-al-shader). Aquí se da
por hecho ese flujo de cinco pasos (handles en el Create, `shader_set`, uniforms, dibujar,
`shader_reset`).

### 1.2 Dónde vive cada shader: por instancia o de pantalla completa

Los diez shaders de este documento se dividen en dos familias según **a qué dibujan**:

| Ámbito | Shaders | Se aplica en |
|---|---|---|
| **Por instancia** (un sprite concreto) | Hit flash, pixelado/posterizado (opcional) | Evento Draw de la instancia, alrededor de `draw_self()` |
| **De pantalla completa** (post-procesado) | Aberración cromática, CRT/scanlines, glitch, shockwave, heat haze, blur, bloom, LUT | Evento Draw GUI de un controlador único (`objFxController`), sobre `application_surface` |

Para el segundo grupo, el patrón es siempre el mismo y ya está documentado en
[01 · 11 §13 «Ejemplo completo: HUD + efectos con surface y shader»](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md#13-ejemplo-completo-hud--efectos-con-surface-y-shader):

```gml
// Create de objFxController — UNA sola instancia persistente en el juego
application_surface_draw_enable(false);   // el juego ya no se auto-dibuja a pantalla

// Draw GUI de objFxController — la escena ya está en application_surface
var _pos   = application_get_position();
var _ancho = _pos[2] - _pos[0];
var _alto  = _pos[3] - _pos[1];

shader_set(sh_mi_efecto);
// ... fijar uniforms ...
draw_surface_stretched(application_surface, _pos[0], _pos[1], _ancho, _alto);
shader_reset();
```

Cada receta de la sección 3 asume este envoltorio salvo que diga lo contrario (hit flash y
pixelado, que son por instancia).

### 1.3 LDR frente a HDR: cuándo importa `surface_rgba16float`

Por defecto, `application_surface` es de 8 bits por canal (**LDR**, *low dynamic range*):
cualquier color queda saturado en el rango 0–1. Eso es suficiente para nueve de las diez
recetas de este documento. La única que se beneficia de verdad de una superficie de 16 bits en
coma flotante (**HDR**) es el **bloom** (3.9): sin margen por encima de 1.0, un «bright-pass»
solo puede distinguir «casi blanco» de «el resto», en vez de cuánto brillo real tiene cada
píxel. `surface_rgba16float` y el resto de formatos ya están documentados en
[08 · 05 §Formatos de superficie](./05%20-%20Superficies.md) y
[02 · 06 §5 «Formatos de superficie»](../02%20-%20Novedades%202026/06%20-%20Gráficos%20-%20SVG%2C%20SDF%2C%20FX%20y%20superficies.md);
aquí solo se usa, no se vuelve a explicar.

> 🔺 **No todas las plataformas soportan superficies en coma flotante.** Compruébalo con
> `surface_format_is_supported(surface_rgba16float)` antes de crearlas y ten un formato de
> repuesto (`surface_rgba8unorm`) para cuando no.

### 1.4 Por qué encadenar pasadas en vez de un shader gigante

Es tentador escribir un único fragment shader con quince `uniform` que haga aberración +
viñeta + grano a la vez. Sale más caro y es peor de mantener que **encadenar shaders simples**:
cada pasada solo paga el coste de lo que hace, puedes activar o desactivar efectos sueltos sin
recompilar nada, y puedes reordenar la cadena (la viñeta casi siempre debe ir la última) sin
tocar una sola línea de GLSL. El precio es que necesitas un sitio donde depositar el resultado
de cada pasada antes de pasárselo a la siguiente: eso es exactamente lo que resuelve la
cadena ping-pong de la sección 2.1.

---

## 2 · El método, paso a paso

Para incorporar cualquier receta de este documento a un proyecto:

1. **Crea el shader** en el IDE (recurso *Shader*) y pega el vertex y el fragment de la receta.
2. **Pide los handles de sus uniforms en el Create** de la instancia o del controlador —nunca en
   el Draw— y guárdalos en variables.
3. Si el efecto es **de una sola pasada**, aplícalo directamente: `shader_set` → uniforms →
   dibujar → `shader_reset`.
4. Si el efecto necesita **más de una pasada** (blur, bloom, o varios efectos apilados), monta
   la cadena de la sección 2.1 y dale una pasada por cada shader.
5. **Comprueba la compilación** al arrancar con `shader_is_compiled()` (`08 · 06 §Buenas
   prácticas`) y **reduce resolución** en los efectos caros (blur, bloom) si vas a HTML5 o
   móvil: la sección 3 indica el coste y la plataforma de cada uno.

### 2.1 La cadena de post-procesado multipasada (ping-pong)

La idea es sencilla: **dos superficies del mismo tamaño**, `surf_a` y `surf_b`. En cada pasada,
dibujas la que tiene el resultado actual (la «fuente») sobre la otra (el «destino») con un
shader activo, y luego intercambias los papeles. La siguiente pasada usa como fuente lo que
acabas de escribir. Al terminar, la fuente actual es el resultado final de toda la cadena.

```gml
/// @func fx_cadena_crear(_ancho, _alto, _formato)
/// @desc Crea el par de superficies ping-pong de una cadena de post-procesado.
function fx_cadena_crear(_ancho, _alto, _formato)
{
    var _cadena = {
        surf_a:  surface_create(_ancho, _alto, _formato),
        surf_b:  surface_create(_ancho, _alto, _formato),
        formato: _formato,
        activa:  0,   // 0 = surf_a tiene el resultado actual · 1 = lo tiene surf_b
    };
    return _cadena;
}

/// @func fx_cadena_destruir(_cadena)
function fx_cadena_destruir(_cadena)
{
    if (surface_exists(_cadena.surf_a)) surface_free(_cadena.surf_a);
    if (surface_exists(_cadena.surf_b)) surface_free(_cadena.surf_b);
}

/// @func fx_cadena_redimensionar(_cadena, _ancho, _alto)
/// @desc Llámala cada Draw GUI: no hace nada si el tamaño no ha cambiado.
function fx_cadena_redimensionar(_cadena, _ancho, _alto)
{
    if (surface_get_width(_cadena.surf_a) != _ancho
    ||  surface_get_height(_cadena.surf_a) != _alto)
    {
        surface_resize(_cadena.surf_a, _ancho, _alto);
        surface_resize(_cadena.surf_b, _ancho, _alto);
    }
}

/// @func fx_cadena_fuente(_cadena)
/// @desc La superficie que contiene el resultado actual de la cadena.
function fx_cadena_fuente(_cadena)
{
    return (_cadena.activa == 0) ? _cadena.surf_a : _cadena.surf_b;
}

/// @func fx_cadena_destino(_cadena)
/// @desc La superficie donde se escribirá la PRÓXIMA pasada.
function fx_cadena_destino(_cadena)
{
    return (_cadena.activa == 0) ? _cadena.surf_b : _cadena.surf_a;
}

/// @func fx_pasada(_cadena)
/// @desc Ejecuta UNA pasada: dibuja la fuente sobre el destino con el shader que ya
///       esté activo (fíjalo y pásale los uniforms ANTES de llamar a esta función), y
///       rota el ping-pong. Si no hay ningún shader activo, actúa como una copia simple.
function fx_pasada(_cadena)
{
    var _fuente  = fx_cadena_fuente(_cadena);
    var _destino = fx_cadena_destino(_cadena);

    surface_set_target(_destino);
    draw_clear_alpha(c_black, 0);
    draw_surface(_fuente, 0, 0);
    surface_reset_target();

    _cadena.activa = 1 - _cadena.activa;
}
```

**Uso completo: dos efectos encadenados (aberración cromática + viñeta) sobre la pantalla.**

```gml
// Create de objFxController
application_surface_draw_enable(false);
cadena_post = fx_cadena_crear(display_get_gui_width(), display_get_gui_height(), surface_rgba8unorm);

u_ab_centro     = shader_get_uniform(sh_aberracion, "u_centro");
u_ab_intensidad = shader_get_uniform(sh_aberracion, "u_intensidad");
u_vin_fuerza    = shader_get_uniform(sh_vineta_pp, "u_fuerza");

// Draw GUI de objFxController
var _pos   = application_get_position();
var _ancho = _pos[2] - _pos[0];
var _alto  = _pos[3] - _pos[1];
fx_cadena_redimensionar(cadena_post, _ancho, _alto);

// Pasada 0: copiar la escena a la cadena (sin shader, primera pasada siempre es una copia)
surface_set_target(fx_cadena_destino(cadena_post));
draw_clear_alpha(c_black, 0);
draw_surface(application_surface, 0, 0);
surface_reset_target();
cadena_post.activa = 1 - cadena_post.activa;

// Pasada 1: aberración cromática
shader_set(sh_aberracion);
shader_set_uniform_f(u_ab_centro, 0.5, 0.5);
shader_set_uniform_f(u_ab_intensidad, dano_intensidad);
fx_pasada(cadena_post);
shader_reset();

// Pasada 2: viñeta (reutiliza la misma idea de 08 · 06 §6.6, en versión de pantalla completa)
shader_set(sh_vineta_pp);
shader_set_uniform_f(u_vin_fuerza, 0.5);
fx_pasada(cadena_post);
shader_reset();

// Resultado final a pantalla
draw_surface_stretched(fx_cadena_fuente(cadena_post), _pos[0], _pos[1], _ancho, _alto);
```

- **Coste:** cada pasada es un `draw_surface` a pantalla completa: barato en sí mismo, pero se
  suma. Con 2-3 pasadas a resolución nativa no notarás nada ni en móvil; a partir de 4-5, mide.
- **Orden de efectos:** distorsiones (aberración, shockwave, heat haze) antes que efectos de
  tono (viñeta, LUT, CRT); el blur/bloom normalmente al final, justo antes de la viñeta.
- **Resolución reducida:** para blur y bloom, crea la cadena a **la mitad o un cuarto** del
  tamaño de la GUI (`fx_cadena_crear(_ancho div 2, _alto div 2, ...)`) y solo sube de escala en
  el `draw_surface_stretched` final. El desenfoque no pierde calidad visible —un blur ya de por
  sí difumina el detalle fino— y el coste cae a una cuarta o dieciseisava parte.
- **Errores típicos:** olvidar la pasada 0 (copiar la escena a la cadena) y aplicar la primera
  pasada directamente sobre `application_surface`, que además de no ser parte del ping-pong es
  de solo lectura como destino de dibujo en este contexto; y olvidar
  `fx_cadena_redimensionar()` cuando la ventana cambia de tamaño, lo que dibuja el resultado
  estirado o recortado.

---

## 3 · Las diez recetas

### 3.1 Hit flash — el parpadeo al recibir daño

El efecto más pedido y, según la auditoría de esta biblioteca, el único que estaba **a medio
camino**: `04 · 15 §5.7` declara y decrementa una variable `hit_flash` con el comentario
«(shader o image_blend)» y nunca llega a dibujarse. Aquí están las tres vías completas.

**Cuándo usarlo:** cualquier personaje o enemigo que reciba daño. Es la señal visual más barata
y más universal del género.

#### Vía A (recomendada): shader con uniform `u_flash`

Mezcla el color del sprite con un color plano según una intensidad, **respetando el alfa
original** (la silueta no cambia, solo el color de dentro).

**Vertex shader** (`sh_flash.vsh`):
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

**Fragment shader** (`sh_flash.fsh`):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

// 0 = sin flash, 1 = totalmente sustituido por u_color_flash
uniform float u_flash;
uniform vec3  u_color_flash;

void main()
{
    vec4 base = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;
    vec3 color_final = mix(base.rgb, u_color_flash, u_flash);
    gl_FragColor = vec4(color_final, base.a);
}
```

**Código GML:**
```gml
// Create
u_flash       = shader_get_uniform(sh_flash, "u_flash");
u_color_flash = shader_get_uniform(sh_flash, "u_color_flash");
hit_flash     = 0;
hit_flash_max = 8;

// Recibir daño (llamado desde fuera, p. ej. hit_complete() de 04 · 15 §5.7)
hit_flash = hit_flash_max;

// Step
if (hit_flash > 0) hit_flash--;

// Draw
if (hit_flash > 0)
{
    shader_set(sh_flash);
    shader_set_uniform_f(u_flash, hit_flash / hit_flash_max);
    shader_set_uniform_f(u_color_flash, 1.0, 1.0, 1.0); // blanco; usa 1,0,0 para rojo, etc.
    draw_self();
    shader_reset();
}
else
{
    draw_self();
}
```

#### Vía B (sin shader): blanco aditivo con `draw_sprite_ext`

**No sirve poner `image_blend = c_white`**: `image_blend` multiplica el color del sprite por el
que le des, y multiplicar por blanco (1,1,1) no cambia nada — es un error habitual. Lo que sí
funciona es dibujar una segunda copia del sprite en **modo de mezcla aditivo**
(`bm_add`, familia completa en [08 · 04 §Modos de mezcla](./04%20-%20Color%20y%20blending.md#modos-de-mezcla)):
sumar blanco a cualquier color lo satura hacia blanco.

```gml
// Draw — sin ningún shader
draw_self();

if (hit_flash > 0)
{
    var _fuerza = hit_flash / hit_flash_max;   // 0..1
    gpu_set_blendmode(bm_add);
    draw_sprite_ext(sprite_index, image_index, x, y,
                     image_xscale, image_yscale, image_angle,
                     c_white, _fuerza);
    gpu_set_blendmode(bm_normal);
}
```

- **Ventaja:** cero shaders, funciona en cualquier plataforma que soporte `bm_add`.
- **Límite:** con `_fuerza` baja el resultado es un aclarado, no una silueta plana; para un
  blanco sólido inmediato necesitas `_fuerza` cercana a 1 o dos pasadas superpuestas.

#### Vía C (sin shader, con matices): el truco de la niebla

`gpu_set_fog()` (documentada en [08 · 04](./04%20-%20Color%20y%20blending.md) y en el manual)
mezcla el resultado con un color según la distancia a la cámara. Fijando `start=0` y `end=1`,
cualquier sprite 2D —que está muy por delante de esas distancias— queda cubierto casi al 100 %
por el color de niebla:

```gml
// Draw — activar la niebla justo antes de dibujar el sprite dañado
if (hit_flash > 0)
{
    gpu_set_fog(true, c_white, 0, 1);
    draw_self();
    gpu_set_fog(false, c_black, 0, 1);
}
else
{
    draw_self();
}
```

> ⚠️ **Esta vía es un efecto de borde de la niebla 3D, no una función pensada para esto.** Es un
> truco conocido en la comunidad, pero esta biblioteca no ha podido verificar una fuente
> primaria que lo documente como técnica de flash 2D — solo el comportamiento oficial de
> `gpu_set_fog()`, que sí está confirmado contra el manual. Además es **binario**: no hay forma
> limpia de graduar la intensidad como en la vía A, solo activarlo o no. Úsala solo si de verdad
> no puedes usar shaders; en cualquier otro caso, la vía A o la B son más fiables.

- **Coste:** trivial en las tres vías (un shader simple, o cero shaders).
- **Plataformas:** las tres funcionan en HTML5 y móvil sin cambios.
- **Errores típicos:** aplicar `image_blend = c_white` esperando un flash blanco (no ocurre,
  ver Vía B); olvidar `gpu_set_blendmode(bm_normal)` tras la Vía B (todo el dibujo posterior
  sale aditivo); dejar `hit_flash_max` en 0 y dividir por cero en `hit_flash / hit_flash_max`.

---

### 3.2 Aberración cromática

Separa los canales R, G y B con un desplazamiide radial que crece con la distancia al centro:
el efecto de «lente barata» que se usa para daño fuerte, disparos de cámara o menús retro.

**Vertex shader** (`sh_aberracion.vsh`): el paso-through estándar de
[08 · 06 §Anatomía](./06%20-%20Shaders.md#anatomía-de-un-shader-de-gamemaker) — todas las
recetas de pantalla completa de este documento usan el mismo, así que solo se repite aquí una
vez más y luego se da por sabido.
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

**Fragment shader** (`sh_aberracion.fsh`):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform vec2  u_centro;      // normalmente (0.5, 0.5)
uniform float u_intensidad;  // desplazamiento máximo, en unidades de UV (0.0-0.02 típico)

void main()
{
    vec2 dir  = v_vTexcoord - u_centro;
    float d   = length(dir);
    vec2 desp = dir * d * u_intensidad;

    float r = texture2D(gm_BaseTexture, v_vTexcoord - desp).r;
    float g = texture2D(gm_BaseTexture, v_vTexcoord).g;
    float b = texture2D(gm_BaseTexture, v_vTexcoord + desp).b;
    float a = texture2D(gm_BaseTexture, v_vTexcoord).a;

    gl_FragColor = vec4(r, g, b, a) * v_vColour;
}
```

**Código GML** (post-procesado de pantalla completa, patrón de §1.2):
```gml
// Create
u_ab_centro     = shader_get_uniform(sh_aberracion, "u_centro");
u_ab_intensidad = shader_get_uniform(sh_aberracion, "u_intensidad");
aberracion      = 0;   // 0 = sin efecto, sube al recibir daño fuerte y decae solo

// Step
aberracion = lerp(aberracion, 0, 0.08);   // decae exponencialmente hacia 0

// Draw GUI
var _pos = application_get_position();
shader_set(sh_aberracion);
shader_set_uniform_f(u_ab_centro, 0.5, 0.5);
shader_set_uniform_f(u_ab_intensidad, aberracion);
draw_surface_stretched(application_surface, _pos[0], _pos[1],
                        _pos[2] - _pos[0], _pos[3] - _pos[1]);
shader_reset();
```

- **Coste:** muy bajo — 4 muestras de textura totales frente a 1 del paso normal.
- **Plataformas:** HTML5 y móvil sin problema.
- **Errores típicos:** aplicarlo a un **sprite individual** en vez de a `application_surface`:
  como `gm_BaseTexture` es la página de textura completa (`08 · 06 §Buenas prácticas`, regla 7),
  el desplazamiento puede colarse en sprites vecinos de la misma página si no está en su propia
  Texture Page. Si el desplazamiento es grande, la UV se sale de 0..1 en los bordes de la
  pantalla: el resultado depende del modo de repetición de la textura (por defecto
  desactivado); si se nota, satura la UV con `clamp()` antes de muestrear.

---

### 3.3 CRT / scanlines

Curvatura de pantalla tipo tubo, líneas de escaneado y viñeta suave: la estética de monitor
viejo. `01 · 10 §8` ya menciona `shader_set(sh_crt)` como ejemplo de nombre sin dar el código;
aquí está completo.

**Fragment shader** (`sh_crt.fsh`; vertex = paso-through de 3.2):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform vec2  u_resolucion;          // tamaño de la superficie en píxeles
uniform float u_curvatura;           // 0 = plano, 0.15-0.3 = curvatura de tubo típica
uniform float u_intensidad_scanline; // 0..1
uniform float u_lineas;              // nº de líneas de escaneado visibles (p. ej. resolución.y)

vec2 curvar_uv(vec2 uv)
{
    uv = uv * 2.0 - 1.0;
    vec2 desplaz = uv.yx * uv.yx * u_curvatura;
    uv = uv + uv * desplaz;
    return uv * 0.5 + 0.5;
}

void main()
{
    vec2 uv = curvar_uv(v_vTexcoord);

    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0)
    {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec4 color = texture2D(gm_BaseTexture, uv);

    float linea  = sin(uv.y * u_resolucion.y * (u_lineas / u_resolucion.y) * 3.14159265);
    float sombra = mix(1.0, 0.5 + 0.5 * linea, u_intensidad_scanline);
    color.rgb *= sombra;

    vec2 centro = uv - 0.5;
    float vineta = 1.0 - dot(centro, centro) * 0.6;
    color.rgb *= vineta;

    gl_FragColor = color * v_vColour.a;
}
```

**Código GML:**
```gml
// Create
u_crt_resolucion = shader_get_uniform(sh_crt, "u_resolucion");
u_crt_curvatura  = shader_get_uniform(sh_crt, "u_curvatura");
u_crt_scanline   = shader_get_uniform(sh_crt, "u_intensidad_scanline");
u_crt_lineas     = shader_get_uniform(sh_crt, "u_lineas");

// Draw GUI
var _pos    = application_get_position();
var _ancho  = _pos[2] - _pos[0];
var _alto   = _pos[3] - _pos[1];

shader_set(sh_crt);
shader_set_uniform_f(u_crt_resolucion, _ancho, _alto);
shader_set_uniform_f(u_crt_curvatura, 0.15);
shader_set_uniform_f(u_crt_scanline, 0.35);
shader_set_uniform_f(u_crt_lineas, 240.0);      // ~240 líneas visibles
draw_surface_stretched(application_surface, _pos[0], _pos[1], _ancho, _alto);
shader_reset();
```

- **Coste:** bajo-medio: una rama condicional más varias operaciones aritméticas por píxel.
- **Plataformas:** HTML5 y móvil van bien; en GPUs móviles muy antiguas, la rama `if` puede
  costar más que en escritorio (divergencia de warp). Si notas coste, sustitúyela por un
  multiplicador sin rama: `color.rgb *= step(0.0, uv.x) * step(uv.x, 1.0) * step(0.0, uv.y) *
  step(uv.y, 1.0);` en vez del `if`/`return`.
- **Errores típicos:** curvar la UV y muestrear `gm_BaseTexture` sin comprobar el rango — sin el
  `if` (o el equivalente con `step`), los bordes curvados repiten el borde de la textura en vez
  de mostrar negro. Con `u_curvatura` en 0 el efecto es solo scanlines + viñeta: útil si quieres
  el look sin la curvatura.

---

### 3.4 Glitch / datamosh

Bandas horizontales que se desplazan de golpe y separan ligeramente los canales de color,
activadas por un disparador (bajo de vida, teletransporte, corrupción de datos en la historia).

**Fragment shader** (`sh_glitch.fsh`; vertex = paso-through de 3.2):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform float u_tiempo;
uniform float u_intensidad;   // 0 = sin glitch, 1 = glitch fuerte

// Pseudoaleatorio determinista a partir de una semilla (no hay ruido integrado en GLSL ES 1.0)
float aleatorio(float semilla)
{
    return fract(sin(semilla * 12.9898) * 43758.5453);
}

void main()
{
    vec2 uv = v_vTexcoord;

    // Cada franja de pantalla tiene su propio valor aleatorio, fijo mientras dure el "tick"
    float franja       = floor(uv.y * 40.0);
    float ruido_franja = aleatorio(franja + floor(u_tiempo * 12.0));

    // Solo una fracción de las franjas se activa en cada instante
    float activar = step(0.92 - u_intensidad * 0.4, ruido_franja);
    uv.x += (ruido_franja - 0.5) * 0.1 * u_intensidad * activar;
    uv.x = clamp(uv.x, 0.0, 1.0);

    // Separación de canales en las franjas activas
    float separacion = activar * u_intensidad * 0.01;
    float r = texture2D(gm_BaseTexture, clamp(uv + vec2(separacion, 0.0), 0.0, 1.0)).r;
    float g = texture2D(gm_BaseTexture, uv).g;
    float b = texture2D(gm_BaseTexture, clamp(uv - vec2(separacion, 0.0), 0.0, 1.0)).b;
    float a = texture2D(gm_BaseTexture, uv).a;

    gl_FragColor = vec4(r, g, b, a) * v_vColour;
}
```

**Código GML:**
```gml
// Create
u_glitch_tiempo     = shader_get_uniform(sh_glitch, "u_tiempo");
u_glitch_intensidad = shader_get_uniform(sh_glitch, "u_intensidad");
glitch_activo       = 0;   // frames restantes del glitch actual

// Disparar un glitch de medio segundo (a 60 fps)
function fx_glitch_disparar(_frames)
{
    with (objFxController) glitch_activo = _frames;
}

// Draw GUI
if (glitch_activo > 0)
{
    var _pos = application_get_position();
    shader_set(sh_glitch);
    shader_set_uniform_f(u_glitch_tiempo, current_time / 1000);
    shader_set_uniform_f(u_glitch_intensidad, 1.0);
    draw_surface_stretched(application_surface, _pos[0], _pos[1],
                            _pos[2] - _pos[0], _pos[3] - _pos[1]);
    shader_reset();
    glitch_activo--;
}
else
{
    var _pos = application_get_position();
    draw_surface_stretched(application_surface, _pos[0], _pos[1],
                            _pos[2] - _pos[0], _pos[3] - _pos[1]);
}
```

- **Coste:** bajo — unas pocas operaciones trigonométricas y 4 muestras de textura.
- **Plataformas:** sin problema en HTML5/móvil.
- **Alternativa nativa parcial:** el filtro de capa **`_filter_old_film`** (parpadeo, grano,
  bandas) y **`_filter_rgbnoise`** (ruido de color) del catálogo de FX se acercan a una parte de
  esta estética sin escribir shader propio, aunque no reproducen el desplazamiento de franjas
  por bloques que hace esta receta. Identificadores verificados contra el manual inglés (ver
  Fuentes); el espejo español de esa página concreta **no es fiable para copiarlos** (varios
  identificadores llegan traducidos).
- **Errores típicos:** no saturar `uv.x` con `clamp()` tras desplazarla — sin eso, franjas
  muy desplazadas pueden salirse de la textura y mostrar bordes repetidos o vacíos según la
  plataforma. Dejar `u_intensidad` siempre a 1 en vez de dispararlo puntualmente: el glitch
  pierde impacto si es constante.

---

### 3.5 Pixelado y posterizado

Reduce la resolución efectiva (pixelado) y el número de tonos por canal (posterizado) en un
único shader de dos uniforms. Sirve tanto de estética permanente como de transición (subir el
tamaño de píxel hasta que la imagen es irreconocible, y cortar a la siguiente escena).

**Fragment shader** (`sh_pixelado.fsh`; vertex = paso-through de 3.2):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform vec2  u_tamano_pixel; // tamaño del "pixel" en unidades de UV; (0,0) = desactivado
uniform float u_niveles;      // niveles por canal del posterizado; 0 = desactivado

void main()
{
    vec2 uv = v_vTexcoord;

    if (u_tamano_pixel.x > 0.0 && u_tamano_pixel.y > 0.0)
    {
        uv = floor(uv / u_tamano_pixel) * u_tamano_pixel + u_tamano_pixel * 0.5;
    }

    vec4 color = texture2D(gm_BaseTexture, uv) * v_vColour;

    if (u_niveles > 0.0)
    {
        color.rgb = floor(color.rgb * u_niveles + 0.5) / u_niveles;
    }

    gl_FragColor = color;
}
```

**Código GML** (variante de transición, pixelado creciente sobre la pantalla completa):
```gml
// Create
u_pix_tamano   = shader_get_uniform(sh_pixelado, "u_tamano_pixel");
u_pix_niveles  = shader_get_uniform(sh_pixelado, "u_niveles");
transicion_t   = 0;   // 0 = normal, 1 = totalmente pixelado

// Step (durante una transición de escena)
if (en_transicion) transicion_t = min(transicion_t + 0.04, 1);

// Draw GUI
var _pos    = application_get_position();
var _tex    = surface_get_texture(application_surface);
var _factor = 1 + transicion_t * 40;   // hasta 40 px "de juego" por celda

shader_set(sh_pixelado);
shader_set_uniform_f(u_pix_tamano,
                      texture_get_texel_width(_tex)  * _factor,
                      texture_get_texel_height(_tex) * _factor);
shader_set_uniform_f(u_pix_niveles, 0);   // sin posterizar en esta transición
draw_surface_stretched(application_surface, _pos[0], _pos[1],
                        _pos[2] - _pos[0], _pos[3] - _pos[1]);
shader_reset();
```

- **Coste:** trivial — una división, un `floor` y una muestra de textura.
- **Plataformas:** ninguna limitación.
- **Alternativa nativa sin shader:** los filtros de capa **`_filter_pixelate`** (parámetro
  *Cell Size*) y **`_filter_posterise`** (parámetro *Colour Levels*) hacen exactamente esto sin
  escribir GLSL — la vía correcta si no necesitas combinarlo con nada más ni animarlo por
  código con el detalle de este shader. Identificadores verificados contra el manual inglés
  (ver Fuentes).
- **Errores típicos:** pasar `u_tamano_pixel` en píxeles en vez de en unidades UV (0..1) —
  siempre multiplica por `texture_get_texel_width/height()`, nunca uses el valor en píxeles
  directamente. Aplicarlo sobre un sprite individual sin tener en cuenta que `gm_BaseTexture` es
  la página completa: el pixelado puede alinearse mal con el sprite si su región no empieza en
  un múltiplo del tamaño de celda.

---

### 3.6 Shockwave (distorsión radial expansiva)

Un anillo que se expande desde un punto y distorsiona lo que atraviesa: la onda expansiva de
una explosión. `04 · 30` menciona el concepto de diseño sin implementación; aquí está el shader.

**Fragment shader** (`sh_shockwave.fsh`; vertex = paso-through de 3.2):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform vec2  u_centro;   // centro de la onda, en UV de pantalla (0..1)
uniform float u_radio;    // radio actual del anillo, en unidades de UV
uniform float u_grosor;   // anchura del anillo que distorsiona
uniform float u_fuerza;   // fuerza máxima de la distorsión

void main()
{
    vec2 uv   = v_vTexcoord;
    vec2 dir  = uv - u_centro;
    float d   = length(dir);

    float anillo = 1.0 - smoothstep(0.0, u_grosor, abs(d - u_radio));
    float desp   = anillo * u_fuerza * (1.0 - clamp(d, 0.0, 1.0));

    vec2 dir_norm = dir / max(d, 0.0001);   // evita dividir por cero en el centro exacto
    uv -= dir_norm * desp;

    gl_FragColor = texture2D(gm_BaseTexture, clamp(uv, 0.0, 1.0)) * v_vColour;
}
```

**Código GML:**
```gml
// Create del controlador (o de un objeto de un solo uso, ver 13 · 04 §3.4)
u_sw_centro = shader_get_uniform(sh_shockwave, "u_centro");
u_sw_radio  = shader_get_uniform(sh_shockwave, "u_radio");
u_sw_grosor = shader_get_uniform(sh_shockwave, "u_grosor");
u_sw_fuerza = shader_get_uniform(sh_shockwave, "u_fuerza");
sw_activa   = false;
sw_radio    = 0;
sw_centro_x = 0;
sw_centro_y = 0;

/// @func fx_shockwave_lanzar(_x, _y)
/// @desc Convierte una posición del mundo a UV de pantalla y lanza la onda.
function fx_shockwave_lanzar(_x, _y)
{
    with (objFxController)
    {
        var _sx = (_x - camera_get_view_x(view_camera[0])) / camera_get_view_width(view_camera[0]);
        var _sy = (_y - camera_get_view_y(view_camera[0])) / camera_get_view_height(view_camera[0]);
        sw_centro_x = _sx;
        sw_centro_y = _sy;
        sw_radio    = 0;
        sw_activa   = true;
    }
}

// Step
if (sw_activa)
{
    sw_radio += 0.025;
    if (sw_radio > 1.4) sw_activa = false;   // ya salió de la pantalla
}

// Draw GUI
var _pos = application_get_position();
if (sw_activa)
{
    shader_set(sh_shockwave);
    shader_set_uniform_f(u_sw_centro, sw_centro_x, sw_centro_y);
    shader_set_uniform_f(u_sw_radio, sw_radio);
    shader_set_uniform_f(u_sw_grosor, 0.05);
    shader_set_uniform_f(u_sw_fuerza, 0.03 * (1 - sw_radio / 1.4));   // se atenúa al crecer
    draw_surface_stretched(application_surface, _pos[0], _pos[1],
                            _pos[2] - _pos[0], _pos[3] - _pos[1]);
    shader_reset();
}
else
{
    draw_surface_stretched(application_surface, _pos[0], _pos[1],
                            _pos[2] - _pos[0], _pos[3] - _pos[1]);
}
```

- **Coste:** bajo — un puñado de operaciones vectoriales y una muestra de textura.
- **Plataformas:** sin restricciones.
- **Alternativa nativa parcial:** el filtro **`_filter_twirl_distort`** (ángulo, radio y offset,
  centrado en la cámara) produce un remolino, no un anillo expansivo con radio animado en el
  tiempo — no sustituye a esta receta, pero es la opción sin shader si lo que buscas es un
  remolino fijo. Identificador verificado contra el manual inglés (ver Fuentes).
- **Errores típicos:** no dividir por `max(d, 0.0001)` al normalizar `dir` — en el centro exacto
  (`d = 0`) una división directa produce `NaN` y el resultado puede ser indefinido según la
  GPU. Olvidar convertir la posición del mundo a UV de pantalla (0..1): pasar coordenadas de
  habitación directamente hace que el centro de la onda no coincida con la explosión.

---

### 3.7 Heat haze localizado

La distorsión de calor **restringida a una región de la pantalla** (la lava, no toda la
imagen), que es justo lo que le faltaba a la técnica ya documentada en
[13 · 08 §11.3 «Agua por shader: distorsión con una textura de ruido»](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md#113-agua-por-shader-distorsión-con-una-textura-de-ruido).
No repitas esa base (el desplazamiento por dos capas de ruido): aquí solo se añade la máscara
de región y el detalle propio del calor (sin distorsión vertical, más rápida y sutil).

**Fragment shader** (`sh_heathaze.fsh`; vertex = paso-through de 3.2):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform sampler2D s_ruido;   // textura de ruido en escala de grises, repetible
uniform float     u_tiempo;
uniform float     u_fuerza;
uniform vec4      u_region;  // xmin, ymin, xmax, ymax en UV de pantalla (0..1)

void main()
{
    vec2 uv = v_vTexcoord;

    // Máscara suave: 1 dentro de la región, 0 fuera, con un margen de difuminado
    vec2 margen = vec2(0.02, 0.02);
    float dentro = smoothstep(u_region.x - margen.x, u_region.x + margen.x, uv.x)
                 * smoothstep(u_region.z + margen.x, u_region.z - margen.x, uv.x)
                 * smoothstep(u_region.y - margen.y, u_region.y + margen.y, uv.y)
                 * smoothstep(u_region.w + margen.y, u_region.w - margen.y, uv.y);

    vec2 uv_ruido = uv * 4.0 + vec2(0.0, -u_tiempo * 0.2);
    float n = texture2D(s_ruido, uv_ruido).r - 0.5;

    uv += vec2(n, n * 0.4) * u_fuerza * dentro;

    gl_FragColor = texture2D(gm_BaseTexture, uv) * v_vColour;
}
```

**Código GML:**
```gml
// Create — región de la lava convertida de coordenadas de mundo a UV de pantalla
s_hh_ruido  = shader_get_sampler_index(sh_heathaze, "s_ruido");
u_hh_tiempo = shader_get_uniform(sh_heathaze, "u_tiempo");
u_hh_fuerza = shader_get_uniform(sh_heathaze, "u_fuerza");
u_hh_region = shader_get_uniform(sh_heathaze, "u_region");

// Draw GUI
var _pos    = application_get_position();
var _cam    = view_camera[0];
var _cx     = camera_get_view_x(_cam);
var _cy     = camera_get_view_y(_cam);
var _cw     = camera_get_view_width(_cam);
var _ch     = camera_get_view_height(_cam);

// Rectángulo de la lava en el mundo -> UV de pantalla
var _u0 = (lava_x1 - _cx) / _cw;
var _v0 = (lava_y1 - _cy) / _ch;
var _u1 = (lava_x2 - _cx) / _cw;
var _v1 = (lava_y2 - _cy) / _ch;

shader_set(sh_heathaze);
texture_set_stage(s_hh_ruido, sprite_get_texture(spr_ruido_calor, 0));
gpu_set_texrepeat_ext(s_hh_ruido, true);   // spr_ruido_calor debe ir en Separate Texture Page
shader_set_uniform_f(u_hh_tiempo, current_time / 1000);
shader_set_uniform_f(u_hh_fuerza, 0.006);
shader_set_uniform_f(u_hh_region, _u0, _v0, _u1, _v1);
draw_surface_stretched(application_surface, _pos[0], _pos[1],
                        _pos[2] - _pos[0], _pos[3] - _pos[1]);
shader_reset();
```

- **Coste:** bajo — 2 muestras de textura (escena + ruido).
- **Plataformas:** sin restricciones.
- **Alternativa nativa:** el filtro de capa **`_filter_heathaze`** (con parámetros de velocidad,
  escala y cantidad de dos capas de distorsión, más aberración cromática integrada —
  `g_ChromaSpreadAmount`) hace un heat haze de **pantalla completa** sin shader. No tiene
  máscara de región propia, así que para limitarlo a un área tendrías que aplicarlo a una capa
  separada que solo contenga esa zona. Identificador y parámetros verificados contra el manual
  inglés (ver Fuentes); es la opción a preferir si no necesitas la máscara con margen difuminado
  de esta receta.
- **Errores típicos:** el mismo que en 13 · 08 §11.3 — `spr_ruido_calor` debe marcarse como
  **Separate Texture Page**, o `gpu_set_texrepeat_ext(..., true)` repetirá la página entera y
  colará trozos de otros sprites. Si `u_region` no coincide con la cámara actual (por ejemplo,
  tras hacer scroll), el efecto se queda "pegado" a una zona de la pantalla que ya no es la
  lava: recalcula la región cada frame, no solo una vez.

---

### 3.8 Blur gaussiano de dos pasadas

Un desenfoque gaussiano de calidad se separa en dos pasadas 1D (horizontal y vertical) en vez
de un único kernel 2D: para un radio equivalente, pasar de **N × N** muestras a **N + N** es la
diferencia entre inviable y barato. Es la base técnica que reutiliza el bloom (3.9).

**Fragment shader** (`sh_blur_gaussiano.fsh`; vertex = paso-through de 3.2). El kernel de 9
muestras con estos pesos ya se insinuaba en
[08 · 06 §`shader_set_uniform_f_array`](./06%20-%20Shaders.md#shader_set_uniform_f_arrayhandle-array)
como ejemplo de "pesos para un kernel de desenfoque"; aquí se usa de verdad, desenrollado para
evitar bucles dinámicos (más compatibles con GPUs móviles antiguas):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform vec2  u_direccion; // (texel_width, 0) para horizontal · (0, texel_height) para vertical
uniform float u_radio;     // multiplicador del radio del desenfoque (1.0 = radio base)

void main()
{
    vec2 uv = v_vTexcoord;
    vec2 d  = u_direccion * u_radio;

    vec4 suma  = texture2D(gm_BaseTexture, uv) * 0.227027;
    suma += texture2D(gm_BaseTexture, uv + d * 1.0) * 0.1945946;
    suma += texture2D(gm_BaseTexture, uv - d * 1.0) * 0.1945946;
    suma += texture2D(gm_BaseTexture, uv + d * 2.0) * 0.1216216;
    suma += texture2D(gm_BaseTexture, uv - d * 2.0) * 0.1216216;
    suma += texture2D(gm_BaseTexture, uv + d * 3.0) * 0.0540541;
    suma += texture2D(gm_BaseTexture, uv - d * 3.0) * 0.0540541;
    suma += texture2D(gm_BaseTexture, uv + d * 4.0) * 0.0162162;
    suma += texture2D(gm_BaseTexture, uv - d * 4.0) * 0.0162162;

    gl_FragColor = suma;
}
```

**Código GML** (usando la cadena ping-pong de 2.1, a resolución reducida):
```gml
// Create
cadena_blur = fx_cadena_crear(display_get_gui_width() div 2, display_get_gui_height() div 2,
                               surface_rgba8unorm);
u_blur_direccion = shader_get_uniform(sh_blur_gaussiano, "u_direccion");
u_blur_radio     = shader_get_uniform(sh_blur_gaussiano, "u_radio");

// Draw GUI
var _pos = application_get_position();
fx_cadena_redimensionar(cadena_blur, display_get_gui_width() div 2, display_get_gui_height() div 2);

// Pasada 0: copiar la escena, ya reducida a la mitad de resolución
surface_set_target(fx_cadena_destino(cadena_blur));
draw_clear_alpha(c_black, 0);
draw_surface_stretched(application_surface, 0, 0,
                        surface_get_width(cadena_blur.surf_a),
                        surface_get_height(cadena_blur.surf_a));
surface_reset_target();
cadena_blur.activa = 1 - cadena_blur.activa;

// Pasada 1: horizontal
var _tex = surface_get_texture(fx_cadena_fuente(cadena_blur));
shader_set(sh_blur_gaussiano);
shader_set_uniform_f(u_blur_direccion, texture_get_texel_width(_tex), 0);
shader_set_uniform_f(u_blur_radio, 1.5);
fx_pasada(cadena_blur);
shader_reset();

// Pasada 2: vertical
_tex = surface_get_texture(fx_cadena_fuente(cadena_blur));
shader_set(sh_blur_gaussiano);
shader_set_uniform_f(u_blur_direccion, 0, texture_get_texel_height(_tex));
shader_set_uniform_f(u_blur_radio, 1.5);
fx_pasada(cadena_blur);
shader_reset();

// Resultado a pantalla, escalado de vuelta a resolución completa
draw_surface_stretched(fx_cadena_fuente(cadena_blur), _pos[0], _pos[1],
                        _pos[2] - _pos[0], _pos[3] - _pos[1]);
```

- **Coste:** 9 muestras × 2 pasadas = 18, frente a las 9×9 = 81 de un kernel 2D directo del
  mismo radio — la razón de ser de la separación. A resolución reducida (mitad), el coste real
  cae otra vez a una cuarta parte.
- **Plataformas:** HTML5 y móvil van bien a resolución reducida; a resolución nativa y con
  `u_radio` alto, vigila el framerate en gama baja.
- **Alternativa nativa:** el efecto de capa **`_effect_gaussian_blur`** (con *Downsample Count*,
  *Passes* e *Intensity*) hace exactamente esto sin escribir shader ni gestionar superficies —
  el propio manual dice que es más rápido que el filtro *Large Blur*. Úsalo si te basta con
  desenfocar una capa entera y no necesitas encadenarlo con otros shaders propios. Identificador
  y parámetros verificados contra el manual inglés (ver Fuentes).
- **Errores típicos:** aplicar las dos pasadas sobre la MISMA superficie sin pasar por el
  ping-pong (lees y escribes el mismo buffer a la vez: resultado indefinido). Calcular
  `texture_get_texel_width/height()` sobre `application_surface` en vez de sobre la superficie
  reducida de la cadena: el radio del desenfoque saldría mal escalado.

---

### 3.9 Bloom: la cadena completa

El resplandor alrededor de lo muy brillante. La cadena real, en cuatro pasos: **bright-pass con
umbral → downsample → blur de dos pasadas → composición aditiva** sobre la escena original.
Reutiliza `sh_blur_gaussiano` de 3.8: no lo repitas si ya lo tienes.

**Fragment shader del bright-pass** (`sh_brillo.fsh`; vertex = paso-through de 3.2):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform float u_umbral;   // 0.7-0.9 típico en LDR; más bajo en HDR real

void main()
{
    vec4 color = texture2D(gm_BaseTexture, v_vTexcoord);
    float brillo = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    float factor = max(brillo - u_umbral, 0.0);
    gl_FragColor = vec4(color.rgb * factor, color.a);
}
```

**Código GML — la cadena completa:**
```gml
// Create
application_surface_draw_enable(false);

var _formato_bloom = surface_format_is_supported(surface_rgba16float)
                      ? surface_rgba16float : surface_rgba8unorm;

surf_brillo = -1;
surf_blur_a = -1;
surf_blur_b = -1;

u_brillo_umbral  = shader_get_uniform(sh_brillo, "u_umbral");
u_blur_direccion = shader_get_uniform(sh_blur_gaussiano, "u_direccion");
u_blur_radio     = shader_get_uniform(sh_blur_gaussiano, "u_radio");

// Draw GUI
var _pos          = application_get_position();
var _ancho        = _pos[2] - _pos[0];
var _alto         = _pos[3] - _pos[1];
var _ancho_bloom  = _ancho div 2;   // resolución reducida a la mitad para el resplandor
var _alto_bloom   = _alto div 2;

if (!surface_exists(surf_brillo))
{
    surf_brillo = surface_create(_ancho_bloom, _alto_bloom, _formato_bloom);
    surf_blur_a = surface_create(_ancho_bloom, _alto_bloom, _formato_bloom);
    surf_blur_b = surface_create(_ancho_bloom, _alto_bloom, _formato_bloom);
}

// 1. Bright-pass + downsample en el mismo dibujado
surface_set_target(surf_brillo);
draw_clear_alpha(c_black, 0);
shader_set(sh_brillo);
shader_set_uniform_f(u_brillo_umbral, 0.75);
draw_surface_stretched(application_surface, 0, 0, _ancho_bloom, _alto_bloom);
shader_reset();
surface_reset_target();

// 2. Blur gaussiano de dos pasadas sobre el bright-pass
surface_set_target(surf_blur_a);
draw_clear_alpha(c_black, 0);
shader_set(sh_blur_gaussiano);
shader_set_uniform_f(u_blur_direccion, texture_get_texel_width(surface_get_texture(surf_brillo)), 0);
shader_set_uniform_f(u_blur_radio, 1.0);
draw_surface(surf_brillo, 0, 0);
shader_reset();
surface_reset_target();

surface_set_target(surf_blur_b);
draw_clear_alpha(c_black, 0);
shader_set(sh_blur_gaussiano);
shader_set_uniform_f(u_blur_direccion, 0, texture_get_texel_height(surface_get_texture(surf_blur_a)));
shader_set_uniform_f(u_blur_radio, 1.0);
draw_surface(surf_blur_a, 0, 0);
shader_reset();
surface_reset_target();

// 3. Composición: escena normal + resplandor aditivo encima, escalado a resolución completa
draw_surface_stretched(application_surface, _pos[0], _pos[1], _ancho, _alto);

gpu_set_blendmode(bm_add);
draw_surface_stretched(surf_blur_b, _pos[0], _pos[1], _ancho, _alto);
gpu_set_blendmode(bm_normal);
```

- **Coste:** alto comparado con el resto de esta lista — un bright-pass + 2 pasadas de blur +
  composición, aunque todo a resolución reducida. Es el shader más caro del documento junto con
  CRT en gama baja.
- **Plataformas:** en HTML5/móvil, reduce aún más la resolución del bloom (a un cuarto) si hace
  falta, y comprueba `surface_format_is_supported(surface_rgba16float)` — el código de arriba ya
  cae a `surface_rgba8unorm` si no está soportado.
- **LDR frente a HDR real:** con `application_surface` normal (LDR, 8 bits), el bright-pass solo
  distingue "casi blanco" del resto — un bloom "barato" pero visualmente correcto para la
  mayoría de juegos 2D. Un bloom con verdadero rango dinámico requiere que la propia escena se
  dibuje a una superficie `surface_rgba16float` (no `application_surface`) con colores que
  superen 1.0 en los elementos emisivos, para que el umbral capture intensidad real y no solo
  cercanía al blanco. Eso es un cambio de pipeline mayor, fuera del alcance de esta receta —
  ver los formatos de superficie en [08 · 05](./05%20-%20Superficies.md).
- **Cuándo NO usarlo en pixel art:** el bloom difumina bordes, y un borde nítido es la mitad del
  atractivo del pixel art. Si tu juego es de estilo retro estricto, o bien evita el bloom por
  completo, o **restríngelo a una capa emisiva aparte** (dibuja SOLO partículas, luces y magia
  en una segunda superficie, aplícales el bloom, y compón esa capa sobre la escena nítida sin
  tocarla) en vez de aplicarlo a la pantalla completa.
- **Alternativa nativa:** el efecto de capa **`_effect_glow`** (radio, calidad, intensidad,
  gamma y alfa) hace un resplandor equivalente sin shader ni gestión de superficies propia — el
  manual avisa de que puede costar en dispositivos débiles, igual que esta receta. Es la opción
  a preferir si no necesitas el control fino del umbral de brillo. Identificador y parámetros
  verificados contra el manual inglés (ver Fuentes).
- **Errores típicos:** olvidar `surface_format_is_supported()` y crear directamente una
  superficie `surface_rgba16float` que falle en silencio en una plataforma sin soporte; aplicar
  el bloom a resolución completa (coste innecesario: el resplandor es borroso por definición,
  no necesita nitidez); olvidar `gpu_set_blendmode(bm_normal)` después de la composición
  aditiva.

---

### 3.10 Color grading por LUT

Recolorea toda la imagen según una tabla de referencia (**LUT**, *look-up table*): el mismo
mecanismo que usan los grados de color de cine y de la mayoría de motores AAA. GameMaker trae
un filtro nativo con esta idea (`_filter_lut_colour`, ver más abajo); esta receta es la versión
por shader propio, útil si quieres controlar la mezcla entre dos LUTs o combinarlo con otras
pasadas de esta cadena.

**Cómo se representa una LUT como textura 2D:** una tabla de color de N niveles por canal
(N=16 es un buen equilibrio) se "desenrolla" como una tira de N tiles de N×N píxeles: el eje X
recorre **rojo** dentro de cada tile y **azul** entre tiles; el eje Y recorre **verde**. Una
imagen de 256×16 píxeles (16 tiles de 16 px) codifica una LUT de 16³ = 4096 colores.

**Fragment shader** (`sh_lut.fsh`; vertex = paso-through de 3.2):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform sampler2D s_lut;
uniform float     u_tamano;  // niveles por canal, p. ej. 16.0 (debe coincidir con la textura)
uniform float     u_mezcla;  // 0 = sin gradar, 1 = LUT completo

vec3 aplicar_lut(vec3 color, float tamano)
{
    color = clamp(color, 0.0, 1.0);

    float azul_indice = color.b * (tamano - 1.0);
    float azul_tile    = floor(azul_indice);
    float azul_mezcla  = fract(azul_indice);

    float ancho_tile = 1.0 / (tamano * tamano);

    vec2 uv1;
    uv1.x = (azul_tile * tamano + color.r * (tamano - 1.0) + 0.5) / (tamano * tamano);
    uv1.y = (color.g * (tamano - 1.0) + 0.5) / tamano;

    vec2 uv2 = vec2(uv1.x + ancho_tile, uv1.y);

    vec3 m1 = texture2D(s_lut, uv1).rgb;
    vec3 m2 = texture2D(s_lut, uv2).rgb;

    return mix(m1, m2, azul_mezcla);
}

void main()
{
    vec4 original = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;
    vec3 gradado  = aplicar_lut(original.rgb, u_tamano);
    vec3 resultado = mix(original.rgb, gradado, u_mezcla);
    gl_FragColor = vec4(resultado, original.a);
}
```

**Generar la LUT neutra (identidad) por código** — el punto de partida para editarla en
cualquier programa de imagen, o para tener al menos una LUT "sin efecto" verificable:
```gml
/// @func generar_lut_identidad(_tamano)
/// @desc Crea un sprite con una LUT identidad (sin recolorear) de _tamano niveles por canal.
function generar_lut_identidad(_tamano)
{
    var _ancho = _tamano * _tamano;
    var _alto  = _tamano;
    var _surf  = surface_create(_ancho, _alto);

    surface_set_target(_surf);
    draw_clear(c_black);
    for (var _b = 0; _b < _tamano; _b++)
    {
        for (var _g = 0; _g < _tamano; _g++)
        {
            for (var _r = 0; _r < _tamano; _r++)
            {
                var _col = make_colour_rgb(
                    round((_r / (_tamano - 1)) * 255),
                    round((_g / (_tamano - 1)) * 255),
                    round((_b / (_tamano - 1)) * 255));
                draw_point_colour(_b * _tamano + _r, _g, _col);
            }
        }
    }
    surface_reset_target();

    var _spr = sprite_create_from_surface(_surf, 0, 0, _ancho, _alto, false, false, 0, 0);
    surface_free(_surf);
    return _spr;
}
```

**Código GML de uso:**
```gml
// Create
spr_lut_identidad = generar_lut_identidad(16);
// surface_save(_surf, "identidad.png") ANTES de surface_free, si quieres editarla fuera:
// ábrela en cualquier editor de imagen o herramienta de grading, aplícale el grado de color
// que quieras directamente sobre la tira, guárdala, e impórtala como spr_lut_grado_atardecer.

s_lut       = shader_get_sampler_index(sh_lut, "s_lut");
u_lut_tamano = shader_get_uniform(sh_lut, "u_tamano");
u_lut_mezcla = shader_get_uniform(sh_lut, "u_mezcla");

// Draw GUI
var _pos = application_get_position();
shader_set(sh_lut);
texture_set_stage(s_lut, sprite_get_texture(spr_lut_grado_atardecer, 0));
gpu_set_texfilter_ext(s_lut, false);    // SIN interpolación: point filtering obligatorio
gpu_set_texrepeat_ext(s_lut, false);    // sin repetición: evita sangrado entre tiles
shader_set_uniform_f(u_lut_tamano, 16);
shader_set_uniform_f(u_lut_mezcla, 0.8);
draw_surface_stretched(application_surface, _pos[0], _pos[1],
                        _pos[2] - _pos[0], _pos[3] - _pos[1]);
shader_reset();
```

- **Coste:** bajo — 2 muestras extra de la LUT por píxel.
- **Plataformas:** sin restricciones; asegúrate de que `spr_lut_grado_atardecer` esté marcado
  como **Separate Texture Page**, igual que cualquier textura de datos (ruido, LUT, paleta).
- **Alternativa nativa:** el filtro de capa **`_filter_lut_colour`** hace exactamente esto —
  *Intensity* + una textura de LUT — sin escribir shader. Es la opción a preferir salvo que
  necesites mezclar dos LUTs distintas o combinarlo con otras pasadas propias de esta cadena.
  Identificador y parámetros verificados contra el manual inglés (ver Fuentes).
- **Errores típicos:** dejar el filtrado lineal activado en el sampler de la LUT
  (`gpu_set_texfilter_ext(s_lut, true)`) — interpolar entre celdas de la tabla mezcla colores de
  entradas vecinas que no tienen nada que ver, y el grading sale con bandas o manchas. Usar un
  `u_tamano` que no coincide con el tamaño real de la textura (una LUT de 16 niveles mide
  256×16 px; si generas o importas una de otro tamaño, actualiza el uniform a juego).

---

## 4 · Checklist antes de dar un shader por terminado

- [ ] ¿El efecto necesita **toda la pantalla** o solo **un sprite**? Decide el ámbito (§1.2)
      antes de escribir una línea de GLSL.
- [ ] ¿Necesita más de una pasada? Monta la cadena ping-pong (§2.1) **antes** de escribir el
      shader, no después.
- [ ] Los handles de uniforms (`shader_get_uniform`, `shader_get_sampler_index`) se piden **una
      vez en el Create**, nunca en el Draw.
- [ ] Cada `shader_set()` tiene su `shader_reset()`; cada `gpu_set_blendmode(bm_add)` tiene su
      `gpu_set_blendmode(bm_normal)`; cada `surface_set_target()` tiene su
      `surface_reset_target()`.
- [ ] Si usas una textura de datos (ruido, LUT, paleta): ¿está marcada como **Separate Texture
      Page**? Si no, `gpu_set_texrepeat_ext(..., true)` colará píxeles de sprites vecinos.
- [ ] Si vas a HTML5 o móvil: comprobaste `shaders_are_supported()` y `shader_is_compiled()` al
      arrancar (`08 · 06 §Buenas prácticas`), y reduciste resolución en blur/bloom.
- [ ] Si usas `surface_rgba16float`: comprobaste `surface_format_is_supported()` con una
      alternativa LDR de repuesto.
- [ ] Si el juego es pixel art: ¿el efecto (bloom, blur, CRT) rompe la nitidez? Pruébalo con
      filtrado de punto y a resolución nativa antes de generalizarlo, o restríngelo a una capa
      concreta.
- [ ] ¿Existe ya un filtro o efecto **nativo** que resuelva esto sin shader (`_filter_*`,
      `_effect_*`)? Cada receta de la sección 3 dice cuál es, si lo hay, y cuándo preferirlo.

---

## 5 · Errores clásicos y cómo evitarlos

1. **`image_blend = c_white` no produce un flash blanco.** Es una multiplicación: multiplicar
   por blanco no cambia nada. Usa la Vía A (shader) o la Vía B (aditivo) de 3.1.
2. **Aplicar un shader de pantalla completa sobre un sprite individual** sin tener en cuenta que
   `gm_BaseTexture` es la página de textura entera (`08 · 06` regla 7): el efecto puede leer o
   escribir píxeles de sprites vecinos si esa página no está separada.
3. **Correr las dos pasadas de un blur sobre la misma superficie** en vez de por el ping-pong:
   lees y escribes el mismo buffer en la misma pasada, resultado indefinido.
4. **Crear `surface_rgba16float` sin comprobar soporte.** En plataformas sin soporte, la llamada
   puede fallar o degradar en silencio; usa `surface_format_is_supported()` siempre.
5. **Olvidar restaurar el estado de la GPU**: `shader_reset()`, `gpu_set_blendmode(bm_normal)`,
   `gpu_set_texrepeat_ext(..., false)`. El efecto se "queda pegado" al resto del dibujado del
   frame si no se restaura.
6. **Interpolación lineal en una textura de LUT o de paleta.** Corrompe la tabla; siempre
   `gpu_set_texfilter_ext(sampler, false)` para datos que no son una imagen "de verdad".
7. **Bloom o blur a resolución nativa cuando la mitad basta.** El desenfoque no necesita
   nitidez: es el ahorro de coste más grande de todo este documento y el más fácil de olvidar.
8. **Dividir por una distancia que puede ser cero** (shockwave, cualquier `normalize()` desde un
   punto que puede coincidir con el píxel actual): usa `max(d, 0.0001)` en el denominador.
9. **No convertir coordenadas de mundo a UV de pantalla** antes de pasarlas a un shader de
   pantalla completa (shockwave, heat haze localizado): el efecto aparece descentrado o fijo en
   un punto de la pantalla en vez de seguir al mundo.
10. **Aplicar bloom/blur/CRT sin criterio a un juego de pixel art estricto.** Empasta los bordes
    que son la mitad del atractivo del estilo. Restringe el efecto a una capa concreta o
    plantéate si hace falta.

---

## 6 · Tabla resumen

| Receta | Sección | Ámbito | Pasadas | Coste | Alternativa nativa sin shader |
|---|---|---|---|---|---|
| Hit flash | 3.1 | Por instancia | 1 | Muy bajo | — (`image_blend` solo no basta) |
| Aberración cromática | 3.2 | Pantalla completa | 1 | Muy bajo | — |
| CRT / scanlines | 3.3 | Pantalla completa | 1 | Bajo-medio | — |
| Glitch / datamosh | 3.4 | Pantalla completa | 1 | Bajo | `_filter_old_film`, `_filter_rgbnoise` (parcial) |
| Pixelado y posterizado | 3.5 | Ambos | 1 | Muy bajo | `_filter_pixelate`, `_filter_posterise` |
| Shockwave | 3.6 | Pantalla completa | 1 | Bajo | `_filter_twirl_distort` (parcial, sin anillo animado) |
| Heat haze localizado | 3.7 | Pantalla completa | 1 | Bajo | `_filter_heathaze` (sin máscara de región) |
| Blur gaussiano 2 pasadas | 3.8 | Pantalla completa | 2 | Medio | `_effect_gaussian_blur` |
| Bloom | 3.9 | Pantalla completa | 4 | Alto | `_effect_glow` |
| Color grading por LUT | 3.10 | Pantalla completa | 1 | Bajo | `_filter_lut_colour` |

---

## Ver también

- [08 · 06 — Shaders](./06%20-%20Shaders.md) — anatomía, uniforms `gm_*`, API completa de
  `shader_*`/`texture_*` y los seis shaders base que este documento no repite.
- [08 · 05 — Superficies](./05%20-%20Superficies.md) — ciclo de vida, volatilidad y formatos de
  superficie (LDR/HDR) usados por la cadena ping-pong y el bloom.
- [08 · 04 — Color y blending](./04%20-%20Color%20y%20blending.md) — modos de mezcla (`bm_add`
  para el hit flash aditivo) y el búfer de stencil, con dos recetas de máscara de efecto en su
  nueva sección «Máscaras de efecto con stencil».
- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) —
  declara y decrementa `hit_flash` (§5.6-§5.7) sin dibujarlo: la receta 3.1 de este documento es
  el dibujado que le faltaba.
- [04 · 24 — Iluminación 2D](../04%20-%20Recetas%20por%20género/24%20-%20Iluminación%202D.md) —
  el sistema de luces con una superficie sobre el que tiene sentido aplicar viñeta, LUT o bloom
  como pasadas finales.
- [13 · 08 — Físicas a mano y fluidos §11.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md#113-agua-por-shader-distorsión-con-una-textura-de-ruido) —
  la técnica base de distorsión por ruido que reutiliza el heat haze localizado (3.7).
- [02 · 06 — Gráficos: SVG, SDF, FX y superficies](../02%20-%20Novedades%202026/06%20-%20Gráficos%20-%20SVG%2C%20SDF%2C%20FX%20y%20superficies.md) —
  los filtros y efectos nativos de 2026 (`fx_create`, `layer_set_fx`) que varias recetas de este
  documento citan como alternativa sin shader.
- [11 - Código descargado/_CATALOGO.md](../11%20-%20Código%20descargado/_CATALOGO.md) — librerías
  de terceros con shaders ya escritos: `bktGlitchFilter` (glitch), `1PassBlur` y `Bokeh`
  (desenfoque), `RenderStack` (gestión de capas de render), `Xpanda`/`Shady.gml` (`#include` en
  shaders, útil si acabas con muchos de los de este documento).

---

## Fuentes

- Shaders (anatomía y API) — ya citada en [08 · 06 §Fuentes](./06%20-%20Shaders.md#fuentes); no
  se repite aquí.
- `gpu_set_fog` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_fog.htm (consultado 2026-09-06, base de la Vía C de 3.1)
- `surface_format_is_supported` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_format_is_supported.htm (consultado 2026-09-06)
- `surface_resize` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_resize.htm (consultado 2026-09-06)
- `surface_save` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_save.htm (consultado 2026-09-06)
- `sprite_create_from_surface` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_create_from_surface.htm (consultado 2026-09-06)
- `draw_point_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_point_colour.htm (consultado 2026-09-06)
- `draw_clear_alpha` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_clear_alpha.htm (consultado 2026-09-06)
- All Filter/Effect Types (catálogo completo de FX, identificadores y parámetros de
  `_filter_pixelate`, `_filter_posterise`, `_filter_lut_colour`, `_filter_heathaze`,
  `_filter_twirl_distort`, `_filter_old_film`, `_filter_rgbnoise`, `_effect_glow`,
  `_effect_gaussian_blur`) — https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/FX/All_Filter_Effect_Types.htm
  (consultado 2026-09-06, **espejo inglés**; el espejo español de esta página concreta traduce
  varios identificadores literales y le faltan filas — ver
  `_indice/auditorias/vfx.md` §0 — así que no se cita ni se copia de ahí).
- gpu_set_texrepeat (comportamiento por defecto, base de las notas de repetición de textura en
  3.2/3.4) — https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_texrepeat.htm (consultado 2026-09-06)

> ⚠️ **No verificado en esta sesión (WebSearch agotado, según el brief de este encargo):** la
> Vía C de 3.1 (truco de `gpu_set_fog` para un flash 2D) es una técnica conocida en la
> comunidad de GameMaker, pero esta biblioteca no ha podido localizar ni abrir una fuente
> primaria que la documente como tal — solo el comportamiento oficial de `gpu_set_fog()`, que sí
> está verificado arriba. El hilo del foro oficial *GM Shaders* de Xor, ya catalogado en
> [07 · 07](../07%20-%20Ecosistema/07%20-%20Foro%20oficial%20-%20hilos%20clave.md), es una fuente
> plausible para varias de estas técnicas (aberración, CRT, glitch) pero no se ha vuelto a abrir
> en esta sesión: no se cita como fuente de ningún código concreto de este documento, todo el
> cual se ha derivado y razonado desde la especificación GLSL ES 1.0 y la API de GameMaker ya
> verificada.
