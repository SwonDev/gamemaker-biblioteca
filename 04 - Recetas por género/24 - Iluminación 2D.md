# 24 · Iluminación 2D

> Mazmorras oscuras, linternas, antorchas, día/noche con luces de colores. El truco es viejo y
> sencillo: **una superficie oscura con agujeros de luz**, dibujada encima de la escena.
>
> **Cobertura parcial detectada:** había primitivas sueltas (shader de luz puntual, blend
> modes, ciclo día/noche), pero no un sistema de varias luces de color. Este documento lo monta.

---

## La idea en una frase

Dibujas el mundo normal. Luego, encima, una **superficie negra semitransparente** que lo
oscurece. En esa superficie, **borras** o **sumas** luz allí donde hay una fuente. El resultado:
todo oscuro menos donde iluminas.

```
mundo (normal)  →  + capa oscura  →  - agujeros de luz  =  escena iluminada
```

---

## 1 · El sistema de luces con una superficie

```gml
/// obj_iluminacion · Create — una capa de luz del tamaño de la pantalla
surf_luz = -1;
color_ambiente = c_black;      // c_black = noche cerrada; make_color_rgb(20,20,40) = azulado

/// lista de luces activas: cada una es un struct
global.luces = [];
```

```gml
/// obj_iluminacion · Draw End (después de todo lo demás, antes del HUD)
if (!surface_exists(surf_luz)) {
    surf_luz = surface_create(camera_get_view_width(view_camera[0]),
                              camera_get_view_height(view_camera[0]));
}

surface_set_target(surf_luz);
draw_clear_alpha(color_ambiente, 1);           // llenar de oscuridad

// cada luz "borra" oscuridad con un sprite de luz (un degradado radial blanco→transparente)
gpu_set_blendmode(bm_subtract);                // restar = abrir un hueco de luz
for (var _i = 0; _i < array_length(global.luces); _i++) {
    var _l = global.luces[_i];
    draw_sprite_ext(spr_luz, 0, _l.x, _l.y, _l.tam, _l.tam, 0, c_white, _l.intensidad);
}
gpu_set_blendmode(bm_normal);
surface_reset_target();

// dibujar la capa de luz sobre la escena, en coordenadas de cámara
draw_surface(surf_luz, camera_get_view_x(view_camera[0]), camera_get_view_y(view_camera[0]));
```

> 🔺 **`bm_subtract` abre luz blanca; para luces de COLOR usa `bm_add` sobre negro.** Con
> subtract, la luz es siempre blanca (revela el color real del mundo). Para una antorcha
> naranja o una alarma roja, cambia el enfoque: capa negra + `bm_add` con el sprite de luz
> teñido del color (`c_orange`, `c_red`). Suma el color a la oscuridad.
>
> 💡 **`spr_luz` es un degradado radial**: blanco en el centro, transparente en el borde. Un
> PNG de 256×256 con un círculo difuminado. La escala (`_l.tam`) controla el radio.

---

## 2 · Colocar y mover luces

```gml
/// añadir una luz (una antorcha fija, la linterna del jugador…)
function luz_crear(_x, _y, _tam, _intensidad) {
    var _l = { x: _x, y: _y, tam: _tam, intensidad: _intensidad };
    array_push(global.luces, _l);
    return _l;      // guarda la referencia para moverla o quitarla
}

/// la linterna sigue al jugador
mi_luz.x = obj_jugador.x;
mi_luz.y = obj_jugador.y;

/// parpadeo de antorcha: intensidad que oscila
antorcha.intensidad = 0.8 + 0.2 * sin(current_time / 100) + random_range(-0.05, 0.05);
```

> 💡 **El parpadeo con `sin()` + un poco de `random` es lo que hace viva a una antorcha.** Un
> valor fijo se ve muerto. Ver [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md).

---

## 3 · Normal maps 2D: relieve con una sola luz

El sistema de §1 abre y cierra brillo, pero no tiene **dirección**: una pared lisa y una pared
de ladrillos reciben exactamente la misma luz. Un *normal map* añade esa dirección: cada píxel
del sprite lleva, codificado en su color, hacia dónde "mira" esa porción de superficie, y el
shader calcula cuánta luz le llega según el ángulo con el que la luz incide — el mismo `N·L`
(producto escalar normal·dirección de luz) de toda la iluminación 3D, aplicado a un sprite 2D.

### 3.1 Qué es un normal map y cómo se codifica

Un normal map es una textura normal (RGB) donde **cada canal de color es una coordenada de un
vector 3D normalizado**: R = X, G = Y, B = Z, remapeados de su rango real (-1..1) al rango de
color (0..255 / 0..1). Un píxel "plano" (que mira directo hacia la cámara, sin relieve) tiene
normal `(0, 0, 1)`, que codificado da el azul lavanda característico `RGB(128, 128, 255)` — el
color de fondo de cualquier normal map. Cuanto más se inclina la superficie, más se aleja el
píxel de ese lavanda hacia rojo/verde/cian.

> ⚠️ **Convención de ejes.** La mayoría de generadores de normal maps asumen Y creciendo hacia
> **arriba** (convención OpenGL); GameMaker dibuja con Y creciendo hacia **abajo**. Si el
> relieve sale "al revés" (la cara que debería mirar hacia la luz queda en sombra y viceversa),
> el primer sitio donde mirar es invertir el canal G tras decodificar
> (`normal.y = -normal.y;`). Depende de qué herramienta generó el mapa — no lo des por hecho
> sin comprobarlo con una luz que sepas de qué lado tiene que pegar.

### 3.2 Generar el normal map

GameMaker no trae ningún conversor de altura→normal integrado, y hacerlo píxel a píxel en GML
en tiempo real no es razonable sin un compute shader (no disponible aquí). Las dos vías reales:

1. **Pintarlo a mano** sobre la paleta de normal map (empezar en `RGB(128,128,255)` y aclarar/
   oscurecer cada canal según hacia dónde quieras que "sobresalga" cada zona) — control total,
   pero exige entender la codificación mientras pintas.
2. **Generarlo desde un sprite o un mapa de alturas en escala de grises** con una herramienta
   dedicada. `Laigter` (azagaya, GPL-3.0, **1 305 ★**) es un generador automático de normal/
   specular/occlusion maps para sprites, gratuito y open source — consultado 2026-09-06, ver
   Fuentes. No forma parte de esta biblioteca ni de GameMaker: es una herramienta externa que
   procesas el sprite y exportas el PNG resultante como un sprite más del proyecto.

### 3.3 El shader

Se aplica **por instancia**, en el Draw del propio sprite con relieve (una pared, una armadura,
el suelo) — no de pantalla completa como el sistema de superficie de §1. Necesita la posición
en **espacio de mundo** del fragmento (para medir la distancia y dirección reales hasta la luz,
no solo su UV), así que el vertex shader ya no es el paso-through por defecto:
usa `MATRIX_WORLD` (ver [08 · 06 §Índices de matriz](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md#índices-de-matriz)), "útil para iluminación si tienes información de
luz en espacio de mundo" — literalmente este caso.

**Vertex shader** (`sh_normal2d.vsh`):
```glsl
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

varying vec2 v_vTexcoord;
varying vec4 v_vColour;
varying vec2 v_vMundo;      // posición del vértice en espacio de mundo, para medir luz real

void main()
{
    vec4 posicion_mundo = gm_Matrices[MATRIX_WORLD] * vec4(in_Position, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * vec4(in_Position, 1.0);

    v_vMundo    = posicion_mundo.xy;
    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

**Fragment shader** (`sh_normal2d.fsh`), calcado del punto de luz de
[08 · 06 §6.4](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md#64-luz-2d-puntual-con-atenuación)
pero muestreando el relieve en vez de aplicar la misma luz a todo el sprite:
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;
varying vec2 v_vMundo;

precision highp float;   // igual que en 08 · 06 §6.4: importante en Android

uniform sampler2D u_s_normal;      // el normal map — misma UV que el difuso, ver 3.4
uniform vec3      u_luz_pos;       // x, y de la luz en espacio de mundo; z = su "altura"
uniform float     u_radio;
uniform vec3      u_luz_color;
uniform float     u_luz_intensidad;
uniform vec3      u_ambiente;

void main()
{
    vec4 difusa = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;

    vec3 normal = texture2D(u_s_normal, v_vTexcoord).rgb * 2.0 - 1.0;   // 0..1 -> -1..1
    normal = normalize(normal);

    vec3 hacia_luz  = vec3(u_luz_pos.xy - v_vMundo, u_luz_pos.z);
    float distancia = length(hacia_luz);
    hacia_luz       = hacia_luz / max(distancia, 0.0001);

    float difuso     = max(dot(normal, hacia_luz), 0.0);       // el N·L de toda la vida
    float atenuacion = 1.0 - clamp(distancia / u_radio, 0.0, 1.0);
    atenuacion = atenuacion * atenuacion;

    vec3 luz = u_ambiente + u_luz_color * (difuso * atenuacion * u_luz_intensidad);

    gl_FragColor = vec4(difusa.rgb * luz, difusa.a);
}
```

**Código GML** (en el objeto que tiene relieve, no en el controlador de luces):
```gml
/// obj_pared_ladrillo · Create
u_nm_normal     = shader_get_sampler_index(sh_normal2d, "u_s_normal");
u_nm_luz_pos    = shader_get_uniform(sh_normal2d, "u_luz_pos");
u_nm_radio      = shader_get_uniform(sh_normal2d, "u_radio");
u_nm_luz_color  = shader_get_uniform(sh_normal2d, "u_luz_color");
u_nm_luz_intens = shader_get_uniform(sh_normal2d, "u_luz_intensidad");
u_nm_ambiente   = shader_get_uniform(sh_normal2d, "u_ambiente");

altura_relieve = 80;   // "altura" en Z de la luz sobre este sprite: más alta, sombreado más suave
```

```gml
/// obj_pared_ladrillo · Draw
var _luz = global.luces[0];   // la luz principal que ilumina este sprite (linterna, antorcha...)

shader_set(sh_normal2d);
texture_set_stage(u_nm_normal, sprite_get_texture(spr_pared_ladrillo_normal, image_index));
shader_set_uniform_f(u_nm_luz_pos, _luz.x, _luz.y, altura_relieve);
shader_set_uniform_f(u_nm_radio, _luz.tam);
shader_set_uniform_f(u_nm_luz_color, 1, 0.9, 0.75);
shader_set_uniform_f(u_nm_luz_intens, _luz.intensidad);
shader_set_uniform_f(u_nm_ambiente, 0.10, 0.10, 0.16);
draw_self();
shader_reset();
```

### 3.4 El requisito que lo hace o lo rompe: Separate Texture Page

`v_vTexcoord` es la UV **dentro de la página de texturas compartida** donde GameMaker empaquetó
el sprite — normalmente un sub-rectángulo pequeño, no 0..1. Para que esa misma UV sirva también
para muestrear `u_s_normal`, **el sprite difuso Y su normal map deben marcarse los dos como
"Separate Texture Page"** en su grupo de texturas (la misma propiedad que ya usa el ruido de
[08 · 23 §3.7](../08%20-%20Referencia%20GML%20completa/23%20-%20Recetario%20de%20shaders%20de%20efecto.md#37-heat-haze-localizado)):
así cada uno ocupa su página entera y su UV es un limpio 0..1, igual en los dos. Si te lo
saltas, el shader mostrea un trozo cualquiera del normal map — el relieve sale con parches sin
sentido, no con un error de compilación que avise del fallo.

### 3.5 Varias luces sobre el mismo sprite

La receta de arriba usa una sola luz (`global.luces[0]`). Para sumar varias, sube `u_luz_pos` y
`u_luz_color` a *arrays* de tamaño fijo (`shader_set_uniform_f_array`, un límite razonable como
4) y acumula su contribución dentro de un `for` en el fragment shader — el coste crece de forma
lineal con ese límite, así que no lo subas más de lo que realmente vayas a necesitar ver.

- **Coste:** una muestra de textura extra + un puñado de operaciones vectoriales, barato por
  píxel. Lo caro es tener que hacer `shader_set`/`shader_reset` por cada sprite con relieve en
  vez de dejar que el batching por defecto los agrupe — resérvalo para sprites protagonistas
  (paredes en primer plano, el propio jugador), no para todo el tileset.
- **Alternativa lista:** `Bulb` (JujuAdams, MIT, 107 ★, ya descargado en
  `11 - Código descargado/librerias/iluminacion/Bulb/` y catalogado en
  [11 · `_CATALOGO.md` §Iluminación y sombras](../11%20-%20Código%20descargado/_CATALOGO.md#iluminación-y-sombras))
  trae normal maps con specular ya resueltos (`__shdBulbLightWithNormalMap`,
  `BulbNormalMapDrawSpriteExt`) con una variante en espacio-objeto que evita el requisito de
  Separate Texture Page de arriba a cambio de un vertex shader más complejo — la opción cuando
  esta receta se te quede corta.

---

## 4 · Sombras proyectadas (*shadow casting*)

Las luces de §1-§3 atraviesan paredes: una antorcha ilumina igual el lado de acá y el de allá de
una columna. Una sombra proyectada tapa la luz allí donde un **oclusor** (una pared, una caja,
una columna) se interpone entre la luz y el punto iluminado. La técnica clásica en 2D, sin
raytracing ni un motor de físicas: **extruir cada arista del oclusor lejos de la luz** y pintar
el cuadrilátero resultante como sombra sólida.

### 4.1 La geometría: extrusión de aristas

Para una arista del oclusor con extremos `A` y `B`, y una luz en `L`:

1. Calcula la dirección desde la luz hasta cada extremo: `point_direction(L, A)` y
   `point_direction(L, B)`.
2. Proyecta cada extremo **lejos** de la luz, a lo largo de esa misma dirección, una distancia
   mayor que el radio de cualquier luz (`A' = A + lengthdir(lejos, dirA)`, igual para `B'`).
3. `A`, `A'`, `B`, `B'` forman un cuadrilátero: la sombra que esa arista proyecta. Dibújalo con
   `draw_primitive_begin(pr_trianglestrip)` + 4 `draw_vertex_colour` + `draw_primitive_end()` —
   una franja triangular de 4 vértices son 2 triángulos, exactamente ese cuadrilátero.

> 💡 **Para un oclusor convexo (una caja, una columna) puedes extruir las 4 aristas sin
> distinguir cuáles "miran" hacia la luz.** Solo dos de las cuatro son la silueta real vista
> desde la luz, pero las sombras de las otras dos quedan **contenidas** dentro de la unión de
> esas dos — pintar sombra sólida de más ahí no se nota, y te ahorras clasificar aristas
> frontales/traseras. Para oclusores cóncavos esto deja de ser cierto: descompón en convexos.

**Funciones:**
```gml
/// Crea un oclusor rectangular (una pared, una caja, una columna) que bloqueará la luz.
function sombra_ocluidor_crear(_x, _y, _ancho, _alto)
{
    var _o = {
        x1: _x,          y1: _y,
        x2: _x + _ancho, y2: _y,
        x3: _x + _ancho, y3: _y + _alto,
        x4: _x,          y4: _y + _alto
    };
    array_push(global.ocluidores, _o);
    return _o;
}

/// Extruye UNA arista (ax,ay)-(bx,by) lejos de (_lx,_ly) y dibuja el cuadrilátero de sombra.
function sombra_dibujar_arista(_ax, _ay, _bx, _by, _lx, _ly, _lejos, _col)
{
    var _dir_a = point_direction(_lx, _ly, _ax, _ay);
    var _dir_b = point_direction(_lx, _ly, _bx, _by);

    var _ax2 = _ax + lengthdir_x(_lejos, _dir_a);
    var _ay2 = _ay + lengthdir_y(_lejos, _dir_a);
    var _bx2 = _bx + lengthdir_x(_lejos, _dir_b);
    var _by2 = _by + lengthdir_y(_lejos, _dir_b);

    draw_primitive_begin(pr_trianglestrip);
    draw_vertex_colour(_ax,  _ay,  _col, 1);
    draw_vertex_colour(_ax2, _ay2, _col, 1);
    draw_vertex_colour(_bx,  _by,  _col, 1);
    draw_vertex_colour(_bx2, _by2, _col, 1);
    draw_primitive_end();
}

/// Dibuja las 4 sombras de un oclusor rectangular (coordenadas de mundo), vistas desde (_lx,_ly).
function sombra_ocluidor_dibujar(_o, _lx, _ly, _lejos, _col)
{
    sombra_dibujar_arista(_o.x1, _o.y1, _o.x2, _o.y2, _lx, _ly, _lejos, _col);
    sombra_dibujar_arista(_o.x2, _o.y2, _o.x3, _o.y3, _lx, _ly, _lejos, _col);
    sombra_dibujar_arista(_o.x3, _o.y3, _o.x4, _o.y4, _lx, _ly, _lejos, _col);
    sombra_dibujar_arista(_o.x4, _o.y4, _o.x1, _o.y1, _lx, _ly, _lejos, _col);
}

/// Igual que sombra_ocluidor_dibujar(), pero trasladado al espacio LOCAL de una superficie
/// pequeña de lado (_radio*2) centrada en la luz — la que usa el bucle de 4.2.
function sombra_ocluidor_dibujar_local(_o, _lx, _ly, _radio, _col)
{
    var _ox    = _lx - _radio;
    var _oy    = _ly - _radio;
    var _lejos = _radio * 3;   // de sobra para salir de esta superficie pequeña

    sombra_ocluidor_dibujar(
        { x1: _o.x1 - _ox, y1: _o.y1 - _oy, x2: _o.x2 - _ox, y2: _o.y2 - _oy,
          x3: _o.x3 - _ox, y3: _o.y3 - _oy, x4: _o.x4 - _ox, y4: _o.y4 - _oy },
        _radio, _radio, _lejos, _col
    );
}
```

### 4.2 Integrarlo con el sistema de §1: una superficie por luz-con-sombra

Pintar la sombra directamente sobre `surf_luz` compartida tiene una trampa: si repintas de
oscuridad ambiente la zona que un oclusor le tapa a la Luz A, y esa misma zona SÍ la alcanza la
Luz B (sin nada en medio desde su ángulo), borras también la contribución de B. La solución
correcta — y la única con la que varias luces con sombra dan un resultado correcto al
solaparse — es resolver el disco + sus sombras de **cada** luz en una superficie propia, pequeña
(del tamaño de su radio, no de toda la pantalla), y sumarla después:

```gml
/// obj_iluminacion · Create — amplía lo de §1, sin tocarlo
global.ocluidores  = [];    // paredes, columnas: lo que bloquea el paso de la luz
surf_sombra_tmp    = -1;    // superficie reutilizable: una por luz-con-sombra, no una por luz total

/// Como luz_crear() de §2, pero con color propio y si proyecta sombra. No sustituye a
/// luz_crear(): úsala para las luces que necesiten estos dos campos extra.
function luz_crear_avanzada(_x, _y, _tam, _intensidad, _color, _arroja_sombra)
{
    var _l = {
        x: _x, y: _y, tam: _tam, intensidad: _intensidad,
        color: _color, arroja_sombra: _arroja_sombra
    };
    array_push(global.luces, _l);
    return _l;
}
```

```gml
/// obj_iluminacion · Draw End — versión con sombras (para luces creadas con luz_crear_avanzada())
var _cam   = view_camera[0];
var _vx    = camera_get_view_x(_cam);
var _vy    = camera_get_view_y(_cam);
var _ancho = camera_get_view_width(_cam);
var _alto  = camera_get_view_height(_cam);

if (!surface_exists(surf_luz)) surf_luz = surface_create(_ancho, _alto);

surface_set_target(surf_luz);
draw_clear_alpha(color_ambiente, 1);
gpu_set_blendmode(bm_add);                      // luces de color, ver §1

for (var _i = 0; _i < array_length(global.luces); _i++)
{
    var _l = global.luces[_i];

    if (!_l.arroja_sombra)
    {
        draw_sprite_ext(spr_luz, 0, _l.x, _l.y, _l.tam, _l.tam, 0, _l.color, _l.intensidad);
        continue;
    }

    // Luz con sombra: se resuelve en SU PROPIA superficie, del tamaño de su radio — así su
    // sombra no puede borrar la luz de una fuente distinta (ver "Las trampas").
    var _lado = _l.tam * 2;
    if (!surface_exists(surf_sombra_tmp)) {
        surf_sombra_tmp = surface_create(_lado, _lado);
    } else {
        surface_resize(surf_sombra_tmp, _lado, _lado);
    }

    surface_set_target(surf_sombra_tmp);        // las superficies se apilan (ver Fuentes):
    draw_clear_alpha(c_black, 0);               // esta sí empieza transparente
    gpu_set_blendmode(bm_add);
    draw_sprite_ext(spr_luz, 0, _l.tam, _l.tam, _l.tam, _l.tam, 0, _l.color, _l.intensidad);

    gpu_set_blendmode(bm_normal);
    for (var _j = 0; _j < array_length(global.ocluidores); _j++)
    {
        var _o = global.ocluidores[_j];
        if (point_distance(_l.x, _l.y, _o.x1, _o.y1) < _lado)   // culling barato por distancia
        {
            sombra_ocluidor_dibujar_local(_o, _l.x, _l.y, _l.tam, c_black);
        }
    }
    surface_reset_target();                     // vuelve a surf_luz sin más: es la que se abrió antes

    gpu_set_blendmode(bm_add);
    draw_surface(surf_sombra_tmp, _l.x - _l.tam - _vx, _l.y - _l.tam - _vy);
}

gpu_set_blendmode(bm_normal);
surface_reset_target();

draw_surface(surf_luz, _vx, _vy);
```

### 4.3 Penumbra

La receta de arriba da una sombra **dura**: un borde nítido, sin degradado — correcta, pero
digital. La manera barata y robusta de ablandarla sin más geometría es difuminar
`surf_sombra_tmp` antes de componerla, con el blur gaussiano de dos pasadas de
[08 · 23 §3.8](../08%20-%20Referencia%20GML%20completa/23%20-%20Recetario%20de%20shaders%20de%20efecto.md#38-blur-gaussiano-de-dos-pasadas):
al ser ya una superficie pequeña (del tamaño del radio de la luz), dos pasadas a resolución
reducida son baratas, y el resultado es indistinguible de una penumbra real en la mayoría de
juegos 2D.

La penumbra geométricamente correcta sale de tratar la luz como un **disco**, no un punto: el
oclusor tapa del todo (umbra) donde ni un solo punto del disco ve la luz — lo que ya dibuja la
receta de arriba —, y tapa solo en parte (penumbra) la franja entre las dos líneas tangentes
desde los bordes del disco hasta cada vértice del oclusor, con el alfa interpolando de 1 a 0 a
lo ancho de esa franja vía `draw_vertex_colour`. Programarlo bien exige clasificar qué aristas
son "de silueta" desde cada borde del disco — más geometría de la que entra en esta receta sin
arriesgar un caso mal cubierto (oclusores cóncavos, aristas mal orientadas). ⚠️ Queda fuera de
este documento con esa honestidad: el atajo del blur de arriba cubre casi todos los casos reales
sin ese riesgo.

### 4.4 Presupuesto por luz

Cada luz con sombra cuesta: un `surface_resize` (barato, vive en GPU) + hasta 4 cuadriláteros
por oclusor cercano (el culling por distancia de arriba ya lo limita) + un `draw_surface` extra
para componerla. Con eso, **1-2 luces con sombra activas a la vez** es lo razonable en un juego
2D corriente — la linterna del jugador, o el sol si la vista es cenital. El resto de las luces
del nivel (antorchas de pared, brillos ambientales) van sin `arroja_sombra` y siguen costando
exactamente lo mismo que en §1. Si el nivel tiene decenas de oclusores, no los recorras todos
por luz cada frame: guarda en cada luz una lista ya filtrada de oclusores cercanos, recalculada
solo cuando la luz se mueve, en vez del filtro por distancia de arriba.

### 4.5 Cuando esto se quede corto

`Bulb` (JujuAdams, MIT, 107 ★, ya descargado en
`11 - Código descargado/librerias/iluminacion/Bulb/` y catalogado en
[11 · `_CATALOGO.md` §Iluminación y sombras](../11%20-%20Código%20descargado/_CATALOGO.md#iluminación-y-sombras))
resuelve lo mismo con vertex buffers y una proyección en Z por vértice
(`__BulbAddOcclusionHard`, `BulbStaticOccluder`) en vez de `pr_trianglestrip` por arista — más
caro de montar, pero soporta oclusores de forma arbitraria (no solo rectángulos) y penumbra real
sin el atajo de blur de 4.3. Es la alternativa lista de la que hablaba este documento desde que
solo tenía el sistema de superficie única de §1.

---

## 5 · God rays (rayos volumétricos)

La luz que entra por una ventana o entre las copas de los árboles se vuelve visible como haces
cuando hay algo en el aire (polvo, niebla) que la dispersa hacia la cámara. Sin partículas ni
volumen real, la técnica de post-proceso estándar —de Kenny Mitchell (Electronic Arts) en
*GPU Gems 3*, cap. 13, "Volumetric Light Scattering as a Post-Process" (ver Fuentes)— es un
**radial blur que acumula muestras hacia la posición en pantalla de la fuente de luz**, cada una
más débil que la anterior.

### 5.1 La máscara de oclusión

El shader no lee la escena entera: lee una **máscara** pequeña, en blanco y negro, donde blanco
= "aquí se ve la fuente de luz" y negro = "aquí no". Para una ventana: blanco donde está el
hueco de la ventana, negro en todo lo demás — incluido cualquier marco, personaje o mueble que
la tape desde el punto de vista actual.

El código de abajo asume **una sola fuente** en la room (`obj_fuente_rayos`, la ventana o el
hueco por el que entra la luz) y accede a su posición como `obj_fuente_rayos.x`/`.y` — válido en
GML cuando solo hay una instancia; con varias fuentes, repite el bloque de máscara + blur por
cada una y compón todas en `surf_rayos` antes del paso 3.

```gml
/// Create del controlador (obj_iluminacion sirve, o uno propio)
u_ry_uv          = shader_get_uniform(sh_godrays, "u_luz_uv");
u_ry_densidad    = shader_get_uniform(sh_godrays, "u_densidad");
u_ry_decaimiento = shader_get_uniform(sh_godrays, "u_decaimiento");
u_ry_peso        = shader_get_uniform(sh_godrays, "u_peso");
u_ry_exposicion  = shader_get_uniform(sh_godrays, "u_exposicion");

surf_mascara = -1;
surf_rayos   = -1;
rayos_escala = 0.5;      // resolución reducida: a 0.5, una cuarta parte de los píxeles reales
```

```gml
/// obj_iluminacion · Draw End — construir la máscara y el radial blur
var _cam   = view_camera[0];
var _vx    = camera_get_view_x(_cam);
var _vy    = camera_get_view_y(_cam);
var _ancho = camera_get_view_width(_cam);
var _alto  = camera_get_view_height(_cam);
var _mw    = _ancho * rayos_escala;
var _mh    = _alto  * rayos_escala;

if (!surface_exists(surf_mascara)) surf_mascara = surface_create(_mw, _mh);
if (!surface_exists(surf_rayos))   surf_rayos   = surface_create(_mw, _mh);

// 1) la máscara: negro en todo salvo la fuente de luz (el hueco de la ventana), en blanco
surface_set_target(surf_mascara);
draw_clear(c_black);
draw_sprite_ext(spr_fuente_luz, 0,
                (obj_fuente_rayos.x - _vx) * rayos_escala, (obj_fuente_rayos.y - _vy) * rayos_escala,
                rayos_escala, rayos_escala, 0, c_white, 1);

// lo que tapa la fuente desde este punto de vista (marcos, personajes...), en negro encima
with (obj_bloquea_rayos)
{
    draw_sprite_ext(sprite_index, image_index,
                    (x - _vx) * other.rayos_escala, (y - _vy) * other.rayos_escala,
                    other.rayos_escala, other.rayos_escala, image_angle, c_black, 1);
}
surface_reset_target();

// 2) el radial blur hacia la fuente, en UV de pantalla — misma conversión mundo->UV que en
//    08 · 23 §3.6 (shockwave)
var _luz_u = (obj_fuente_rayos.x - _vx) / _ancho;
var _luz_v = (obj_fuente_rayos.y - _vy) / _alto;

surface_set_target(surf_rayos);
shader_set(sh_godrays);
shader_set_uniform_f(u_ry_uv, _luz_u, _luz_v);
shader_set_uniform_f(u_ry_densidad, 0.9);
shader_set_uniform_f(u_ry_decaimiento, 0.96);
shader_set_uniform_f(u_ry_peso, 0.4);
shader_set_uniform_f(u_ry_exposicion, 0.35);
draw_surface_stretched(surf_mascara, 0, 0, _mw, _mh);
shader_reset();
surface_reset_target();
```

```gml
/// obj_iluminacion · Draw GUI — componer los rayos sobre la escena ya compuesta
gpu_set_blendmode(bm_add);
draw_surface_stretched(surf_rayos, 0, 0, _ancho, _alto);
gpu_set_blendmode(bm_normal);
```

### 5.2 El shader

**Vertex** — paso-through estándar, igual que en
[08 · 06 §Anatomía de un shader de GameMaker](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md#anatomía-de-un-shader-de-gamemaker):
```glsl
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * vec4(in_Position, 1.0);
    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

**Fragment** (`sh_godrays.fsh`) — la implementación del algoritmo de radial blur con
decaimiento de Mitchell, adaptada a GameMaker:
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform vec2  u_luz_uv;       // posición de la fuente en UV de pantalla (0..1)
uniform float u_densidad;     // separación entre muestras: controla lo largos que salen los rayos
uniform float u_decaimiento;  // 0..1: cuánto se apaga cada muestra sucesiva
uniform float u_peso;         // peso de cada muestra antes del decaimiento acumulado
uniform float u_exposicion;   // multiplicador final

#define NUM_MUESTRAS 48

void main()
{
    vec2 uv   = v_vTexcoord;
    vec2 paso = (uv - u_luz_uv) * (u_densidad / float(NUM_MUESTRAS));

    float decaimiento = 1.0;
    vec3  acumulado   = vec3(0.0);

    for (int i = 0; i < NUM_MUESTRAS; i++)
    {
        uv -= paso;
        vec3 muestra = texture2D(gm_BaseTexture, uv).rgb;
        muestra *= decaimiento * u_peso;
        acumulado += muestra;
        decaimiento *= u_decaimiento;
    }

    gl_FragColor = vec4(acumulado * u_exposicion * v_vColour.a, 1.0);
}
```

- **Coste:** `NUM_MUESTRAS` lecturas de textura **por píxel de la máscara**, no de toda la
  pantalla — con `rayos_escala = 0.5` eso ya es una cuarta parte de los píxeles reales. Baja a
  24-32 muestras y a escala 0.25 en HTML5 o móvil; el *banding* que aparece con pocas muestras
  se puede disimular añadiendo ruido al `paso` (dither), pero no hace falta para una primera
  versión.
- **Alternativa nativa parcial:** el filtro **`_filter_zoom_blur`** (`g_ZoomBlurCenter`,
  `g_ZoomBlurIntensity`, `g_ZoomBlurFocusRadius`) aplicado sobre toda la escena y centrado en la
  posición en pantalla de la fuente produce un tirón radial que en una estética retro puede
  pasar por rayos volumétricos baratos — pero difumina literalmente todo lo que hay en pantalla,
  no una máscara limpia: un personaje cerca del punto también sale emborronado. Identificador
  verificado contra el manual inglés (ver Fuentes). Es la opción de un solo filtro de capa
  cuando el presupuesto no permita ni la máscara ni el shader de arriba.

---

## 6 · Ciclo día/noche con rampa de color

`04 · 09 §5.5` monta un ciclo día/noche con una capa plana de `c_navy` y alfa variable: oscurece
la escena, pero no la tiñe — a mediodía y a medianoche todo tiene el mismo tono, solo cambia
cuánto se ve. Una rampa de color real hace que el amanecer se vea **cálido**, el mediodía
**neutro**, el atardecer **cálido** otra vez y la noche **azulada** — y, con el sistema de §1,
puede teñir también las luces del nivel, no solo el ambiente.

### 6.1 Paradas horarias

```gml
/// obj_iluminacion · Create — amplía lo de §1
global.paradas_dia = [
    { hora: 0.00, ambiente: make_colour_rgb(20,  20,  45),  tinte: make_colour_rgb(150, 160, 255) }, // medianoche: azul frío
    { hora: 0.20, ambiente: make_colour_rgb(35,  32,  60),  tinte: make_colour_rgb(170, 165, 255) }, // antes del amanecer
    { hora: 0.27, ambiente: make_colour_rgb(255, 170, 110), tinte: make_colour_rgb(255, 205, 160) }, // amanecer cálido
    { hora: 0.50, ambiente: make_colour_rgb(255, 255, 255), tinte: make_colour_rgb(255, 255, 255) }, // mediodía neutro
    { hora: 0.73, ambiente: make_colour_rgb(255, 150, 90),  tinte: make_colour_rgb(255, 190, 130) }, // atardecer
    { hora: 0.80, ambiente: make_colour_rgb(55,  48,  90),  tinte: make_colour_rgb(190, 175, 255) }, // anochecer
    { hora: 1.00, ambiente: make_colour_rgb(20,  20,  45),  tinte: make_colour_rgb(150, 160, 255) }, // vuelta a medianoche
];

tinte_dia = c_white;
```

Cada parada guarda dos colores: `ambiente` (lo que ya consume el `color_ambiente` de §1) y
`tinte` (con el que se tiñe cada luz, ver 6.3). El amanecer y el atardecer son cálidos por la
misma razón por la que lo son en una fotografía real: a rasante, la luz atraviesa más atmósfera
y pierde las frecuencias frías por dispersión — referencia visual en Slynyrd, *Pixelblog 6 —
Light and Shadow* (ver Fuentes).

### 6.2 Interpolar entre paradas

```gml
/// Busca las dos paradas que rodean _tiempo (0..1, igual que objTimeOfDay.tiempo de 04 · 09
/// §5.5) e interpola con merge_colour(). Devuelve un struct { ambiente, tinte }.
function dianoche_color_en(_tiempo)
{
    var _paradas = global.paradas_dia;
    var _n       = array_length(_paradas);

    for (var _i = 0; _i < _n - 1; _i++)
    {
        var _a = _paradas[_i];
        var _b = _paradas[_i + 1];

        if (_tiempo >= _a.hora && _tiempo <= _b.hora)
        {
            var _f = (_b.hora > _a.hora) ? (_tiempo - _a.hora) / (_b.hora - _a.hora) : 0;
            return {
                ambiente: merge_colour(_a.ambiente, _b.ambiente, _f),
                tinte:    merge_colour(_a.tinte,    _b.tinte,    _f)
            };
        }
    }

    var _ultima = _paradas[_n - 1];             // por si _tiempo se sale de 0..1 por redondeo
    return { ambiente: _ultima.ambiente, tinte: _ultima.tinte };
}
```

```gml
/// obj_iluminacion · Step — sincronizado con objTimeOfDay (04 · 09 §5.5)
var _color     = dianoche_color_en(objTimeOfDay.tiempo);
color_ambiente = _color.ambiente;    // el mismo campo que ya lee el Draw End de §1/§4, sin tocarlo
tinte_dia      = _color.tinte;
```

### 6.3 Teñir también las luces

Sobre la versión de `Draw End` de §4, un único cambio: mezclar el color propio de cada luz con
`tinte_dia` antes de dibujarla, en vez de usar `_l.color` directo.

```gml
/// obj_iluminacion · Draw End — la línea que cambia dentro del bucle de luces de §4
var _color_luz = merge_colour(_l.color, tinte_dia, 0.35);   // 35 %: sutil, no lava el color propio
draw_sprite_ext(spr_luz, 0, _l.x, _l.y, _l.tam, _l.tam, 0, _color_luz, _l.intensidad);
```

Con esto, una antorcha naranja se ve casi igual a mediodía (el tinte es blanco neutro) pero se
tiñe ligeramente de azul en plena noche — como si la luz ambiente de verdad se colara sobre ella
— sin dejar de ser reconociblemente naranja.

> 💡 **Si tu reloj de juego mide horas de 0 a 24 en vez de 0 a 1**, normaliza antes de llamar a
> `dianoche_color_en()`: `_tiempo = _hora_del_dia / 24;`. Las `hora` de las paradas están en la
> misma escala 0..1 que `objTimeOfDay.tiempo`.
>
> 💡 **Con 6-7 paradas y recalculando cada frame** (no solo al cruzar de tramo) el ojo no
> detecta ningún salto de color; con 2-3 paradas muy separadas, sí.

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| Dibujar la luz en Draw normal | Se mezcla con el mundo en mal orden; usa Draw End |
| No recrear la surface tras perderla | Las surfaces se borran al cambiar de resolución/ventana; comprueba `surface_exists` siempre |
| Coordenadas de mundo vs de cámara | La luz se desalinea al mover la cámara; dibuja la surface en la esquina de la cámara |
| Olvidar `gpu_set_blendmode(bm_normal)` al acabar | Todo lo que dibujes después sale mal |
| Una surface por luz | Mata el rendimiento; una sola surface para todas |
| Mezclar luces de `luz_crear()` (§2) y `luz_crear_avanzada()` (§4) en el mismo `global.luces` | El Draw End con sombras de §4 espera `.color` y `.arroja_sombra` en cada luz; a una luz "vieja" sin esos campos, el bucle revienta |
| Normal map y sprite difuso en páginas de textura distintas | El shader de §3 muestrea un trozo cualquiera del normal map; marca los DOS sprites como Separate Texture Page |
| Extruir sombras (§4) con `_lejos` insuficiente | La sombra se corta antes de salir de la superficie; usa un valor mayor que la diagonal de donde se dibuja |
| Anidar `surface_set_target` sin cerrar cada una con su propio `surface_reset_target` | Las superficies se apilan como paréntesis (§4.2); saltarse un cierre manda el dibujado posterior a la superficie equivocada, o a ninguna |

> ⚠️ **Las surfaces son volátiles.** Se pierden al minimizar, cambiar de resolución o de
> ventana. **Nunca** asumas que existe: `if (!surface_exists(...)) surf = surface_create(...)`
> antes de usarla, cada vez. Es la causa nº 1 de bugs con iluminación.

---

## Ver también

- [08 · 05 — Superficies](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md) — cómo funcionan las surfaces
- [08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md) — anatomía de un shader y la luz 2D puntual (§6.4) sobre la que se construye §3
- [08 · 23 — Recetario de shaders de efecto](../08%20-%20Referencia%20GML%20completa/23%20-%20Recetario%20de%20shaders%20de%20efecto.md) — la cadena de post-procesado multipasada, el blur gaussiano (§4.3) y la conversión mundo→UV (§5) que usan estas secciones
- [08 · 04 — Color y blending](../08%20-%20Referencia%20GML%20completa/04%20-%20Color%20y%20blending.md) — los blend modes en detalle
- [04 · 09 — Survival y crafting §5.5](./09%20-%20Survival%20y%20crafting.md#55-ciclo-díanoche) — el reloj `objTimeOfDay.tiempo` que alimenta §6
- [11 · `_CATALOGO.md` §Iluminación y sombras](../11%20-%20Código%20descargado/_CATALOGO.md#iluminación-y-sombras) — `Bulb`, la librería descargada con la que se contrastaron §3 y §4

---

## Fuentes

- Kenny Mitchell (Electronic Arts), *GPU Gems 3*, capítulo 13 — "Volumetric Light Scattering as
  a Post-Process" (NVIDIA): el algoritmo de radial blur con decaimiento de §5. Consultado
  2026-09-06,
  <https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process>.
- Amit Patel (Red Blob Games), *2D Visibility*: la geometría de líneas de visión en la que se
  apoya la extrusión de aristas de §4. Consultado 2026-09-06,
  <https://www.redblobgames.com/articles/visibility/>.
- `Bulb` (JujuAdams, MIT, 107 ★) — código fuente descargado en
  `11 - Código descargado/librerias/iluminacion/Bulb/`: sus shaders
  `__shdBulbLightWithNormalMap` y sus scripts `__BulbAddOcclusionHard`/`BulbStaticOccluder` son
  la implementación real con la que se contrastaron §3 y §4 (vertex buffers con proyección en Z
  por vértice, en vez de `pr_trianglestrip` por arista: más cara de montar y más completa).
  <https://github.com/JujuAdams/Bulb>.
- `Laigter` (azagaya, GPL-3.0, 1 305 ★) — "automatic normal map generator for sprites": la vía
  recomendada en §3.2 para generar normal maps sin pintarlos a mano. Consultado 2026-09-06,
  <https://github.com/azagaya/laigter>.
- Raymond Schlitter (Slynyrd), *Pixelblog 6 — Light and Shadow*: referencia visual de
  convenciones de luz y sombra en pixel art, citada en §6.1. Consultado 2026-09-06,
  <https://www.slynyrd.com/blog/2018/6/15/pixelblog-6-light-and-shadow>.
- Manual oficial de GameMaker, `surface_set_target()`: confirma que las superficies se apilan
  (abrir y cerrar cada una como un paréntesis), la base de la superficie temporal por luz de
  §4.2. Espejo local:
  `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_set_target.md`.
- *All Filter and Effect Types* (manual inglés): confirma que no existe ningún filtro nativo de
  "god rays" ni de sombras 2D en 2026.0, y que `_filter_zoom_blur` (§5.2) sí existe con los
  parámetros citados. `09 - Manual oficial/manual-lts-2026-en/The_Asset_Editors/Room_Properties/FX/All_Filter_Effect_Types.md`.
