# 08 · Físicas a mano y fluidos

> Cómo simular movimiento, choques, muelles, cuerdas, tela y **agua** escribiendo tú el
> integrador, sin activar Box2D. Es lo que hace la inmensa mayoría de los juegos 2D
> publicados: sale más barato, es más predecible y —lo que de verdad importa— es
> **afinable**. Una física que no puedes ajustar parámetro a parámetro no sirve para
> diseñar sensaciones.
>
> **Qué NO cubre este documento** (y dónde está):
> - **Box2D**: mundo físico, fixtures, joints y las 44 funciones `physics_particle_*` de
>   fluido están en [04 · 22 — Físicas con Box2D](../04%20-%20Recetas%20por%20género/22%20-%20Físicas%20con%20Box2D.md).
>   Aquí solo se decide **cuándo** conviene usarlo.
> - **El plataformas concreto** (coyote time, jump buffer, plataformas móviles y one-way,
>   `move_and_collide`): [04 · 01 — Plataformas 2D](../04%20-%20Recetas%20por%20género/01%20-%20Plataformas%202D.md)
>   y [01 · 08 — Movimiento y colisiones](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md).
> - **La física arcade de un coche** (deriva, agarre lateral, giro dependiente de la
>   velocidad): [04 · 12 — Carreras y vehículos](../04%20-%20Recetas%20por%20género/12%20-%20Carreras%20y%20vehículos.md) §4.
> - **Partículas visuales `part_*`, screen shake y hit stop**:
>   [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md).
> - **La API de primitivas y de shaders**, función por función:
>   [08 · 02](../08%20-%20Referencia%20GML%20completa/02%20-%20Dibujo%20de%20formas%20y%20primitivas.md) y
>   [08 · 06](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md).

---

## 1 · Los principios

### 1.1 A mano o Box2D: la tabla de decisión

La pregunta no es «¿cuál es mejor?» sino **¿la simulación *es* el juego?**

| Si necesitas… | Hazlo | Por qué |
|---|---|---|
| Un personaje que salta con un tacto concreto | **A mano** | Con Box2D no puedes fijar la altura del salto: la negocias con el solver |
| Balas, proyectiles, arcos de tiro | **A mano** | Es una parábola de tres líneas; Box2D es un mundo entero para eso |
| Cientos de proyectiles o partículas chocando entre sí | **A mano** (spatial hash, §4) | Box2D no está pensado para miles de cuerpos diminutos |
| Un coche arcade con deriva | **A mano** ([04 · 12](../04%20-%20Recetas%20por%20género/12%20-%20Carreras%20y%20vehículos.md)) | El agarre lateral es un parámetro de diseño, no una consecuencia |
| Cámara, HUD, capa y pelo que siguen con inercia | **A mano** (muelles, §6) | No hace falta un mundo físico para amortiguar un número |
| Cuerdas, cadenas, tela, tentáculos, ragdolls | **A mano** (Verlet, §7) | Verlet es más estable y más barato que un joint por eslabón |
| Superficie de agua ondulante | **A mano** (§9) | Es una fila de muelles: 40 líneas |
| Arena, lava, agua que llena huecos por celdas | **A mano** (§10) | Un autómata celular, no un solver de cuerpos |
| Cajas que se apilan, ruedan y vuelcan de forma creíble | **Box2D** | Reescribir un solver de contactos con rotación es meses de trabajo |
| Un puzzle donde el jugador construye estructuras | **Box2D** | Los joints y el apilado estable son el juego |
| Fluido de partículas que interactúa con cuerpos rígidos | **Box2D** ([22 §6](../04%20-%20Recetas%20por%20género/22%20-%20Físicas%20con%20Box2D.md)) | Ya está escrito en C++ y corre fuera de la VM |

> 🔺 **La regla de oro:** si el jugador *nota* que la física es la mecánica (*Angry Birds*,
> *World of Goo*, *Besiege*), Box2D. Si la física es solo el *medio* para mover un personaje
> (Celeste, Hollow Knight, Dead Cells), a mano. **Y nunca las dos cosas en el mismo objeto**:
> en cuanto un objeto usa física, `x`/`y` dejan de ser tuyas.

### 1.2 El integrador: por qué Euler explícito explota

Integrar es convertir aceleración en velocidad y velocidad en posición. Hay dos maneras de
escribir esas dos líneas, y **el orden decide si la simulación es estable**:

```gml
// ❌ Euler EXPLÍCITO — usa la velocidad del frame anterior para mover
px  += vel_x * _dt;
vel_x += acel_x * _dt;

// ✅ Euler SEMI-IMPLÍCITO (simpléctico) — actualiza la velocidad ANTES de mover
vel_x += acel_x * _dt;
px  += vel_x * _dt;
```

Con aceleración constante (gravedad pura) los dos dan casi lo mismo. Con aceleración
**variable** —un muelle, una órbita, cualquier fuerza que dependa de la posición— el
explícito **gana energía en cada paso**: el muelle oscila cada vez más fuerte hasta que la
simulación revienta. El semi-implícito conserva la energía media y por eso es el estándar de
facto en videojuegos, incluido Box2D. Glenn Fiedler lo demuestra numéricamente en
*Integration Basics* (fuentes).

**Regla operativa:** en GML, **siempre** actualiza la velocidad antes que la posición. Dos
líneas en el orden correcto valen más que un integrador RK4 en el orden equivocado.

### 1.3 Independencia del framerate: `delta_time` y el paso fijo

`delta_time` son los **microsegundos** transcurridos desde el frame anterior. La API está en
[01 · 06 §7](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md); aquí
importa la consecuencia física.

Multiplicar por `dt` funciona para movimiento uniforme. **Deja de funcionar en cuanto hay
aceleración, muelles o colisiones**, por tres motivos:

1. **La fricción multiplicativa no es lineal.** `vel *= 0.9` cada frame es un 0,9 a 60 fps y
   un 0,81 efectivo a 30 fps: el personaje frena el doble. La corrección correcta es
   exponencial: `vel *= power(0.9, _dt * 60)` — la misma matemática que
   [`lerp_dt()`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml) del script de utilidades.
2. **El túnel.** Con un frame largo (una carga de disco, un `alt-tab`) la bala avanza 400 px
   de golpe y atraviesa la pared sin tocarla nunca.
3. **Los muelles explotan.** Un muelle rígido con `dt` grande sobrecorrige, se pasa, y en dos
   pasos está en el infinito.

Por eso **un plataformas serio corre a paso fijo**: `game_set_speed(60, gamespeed_fps)` y `dt`
implícito de 1 frame. Es determinista, se puede rejugar y depurar, y quita del medio toda la
clase de bugs anterior. Si además necesitas soportar monitores de 144 Hz sin cambiar la
simulación, se usa el **acumulador de Fiedler** (*Fix Your Timestep!*):

```gml
/// obj_fisica · Create — simulación a paso fijo, dibujo a la velocidad del monitor
#macro PASO_FIJO 0.0166666   // 1/60 de segundo
acumulador = 0;
alfa       = 0;              // 0..1, para interpolar el dibujo

/// obj_fisica · Step
// techo de 0,25 s: sin él, un frame largo dispara N pasos y la caída se realimenta
// («espiral de la muerte»)
acumulador += min(delta_time / 1000000, 0.25);

while (acumulador >= PASO_FIJO)
{
    simular_paso(PASO_FIJO);     // TODA la física vive aquí dentro
    acumulador -= PASO_FIJO;
}

alfa = acumulador / PASO_FIJO;   // sobrante: cuánto falta para el siguiente paso
```

```gml
/// obj_fisica · Draw — dibuja entre el estado anterior y el actual: nada de tirones
var _dx = lerp(px_previo, px, alfa);
var _dy = lerp(py_previo, py, alfa);
draw_sprite(spr_caja, 0, _dx, _dy);
```

> 💡 **Cuándo NO montar el acumulador.** Si tu juego corre a 60 fps fijos y no te importa que
> en un monitor de 144 Hz se vea a 60, no lo necesitas: es complejidad a cambio de nada.
> Móntalo cuando quieras **dibujar** a 144 y **simular** a 60, o cuando la simulación deba ser
> reproducible bit a bit (repeticiones, netcode determinista).

---

## 2 · El salto por diseño: derivar la gravedad en vez de adivinarla

Nadie afina un salto tocando `gravedad = 0.4` a ciegas. Se hace al revés: **decides la altura
y el tiempo, y despejas las constantes.**

Con gravedad constante y velocidad inicial `v0` hacia arriba, en el vértice la velocidad es 0.
De `h = v0·t − ½·g·t²` y `v0 = g·t` salen las dos fórmulas que necesitas:

```
g  = 2·h / t²        v0 = 2·h / t
```

donde `h` es la altura máxima del salto **en píxeles** y `t` el tiempo hasta el vértice. Si
trabajas por frames (paso fijo), `t` va en frames y las unidades salen en px/frame y
px/frame². Si trabajas en segundos, en px/s y px/s².

```gml
/// scr_salto — las dos fórmulas, y nada más
/// @func salto_gravedad(_altura, _tiempo_cima)
/// @desc Gravedad necesaria para que un salto alcance `_altura` en `_tiempo_cima`.
/// @param {Real} _altura       Altura máxima del salto, en píxeles.
/// @param {Real} _tiempo_cima  Tiempo hasta el punto más alto (frames o segundos).
/// @returns {Real}             Aceleración por unidad de tiempo al cuadrado.
function salto_gravedad(_altura, _tiempo_cima)
{
    return (2 * _altura) / sqr(_tiempo_cima);
}

/// @func salto_velocidad(_altura, _tiempo_cima)
/// @desc Velocidad inicial (positiva) para ese mismo salto.
/// @returns {Real}
function salto_velocidad(_altura, _tiempo_cima)
{
    return (2 * _altura) / _tiempo_cima;
}
```

```gml
/// obj_jugador · Create — el salto se describe con lo que el diseñador entiende
altura_salto  = 64;    // px: cuatro tiles de 16
tiempo_cima   = 18;    // frames a 60 fps ≈ 0,30 s
tiempo_caida  = 13;    // frames: cae más rápido de lo que sube

grav_subida = salto_gravedad(altura_salto, tiempo_cima);   // ≈ 0.395
grav_caida  = salto_gravedad(altura_salto, tiempo_caida);  // ≈ 0.757
impulso     = salto_velocidad(altura_salto, tiempo_cima);  // ≈ 7.11

vel_x = 0;
vel_y = 0;
```

**Gravedad asimétrica**: bajar más rápido de lo que se sube es lo que se percibe como «salto
con fuerza». Con estas fórmulas no es un número mágico, es *otro tiempo*: `tiempo_caida`
menor que `tiempo_cima`. El detalle de tacto (coyote time, buffer, salto variable soltando el
botón) ya está resuelto en
[04 · 01 §4.2–4.5](../04%20-%20Recetas%20por%20género/01%20-%20Plataformas%202D.md) y no se
repite aquí.

### 2.1 Predecir dónde cae un proyectil

La misma parábola despejada en `t`. Dada la posición, la velocidad y la altura del suelo,
`½·g·t² + vy·t − (y_suelo − y0) = 0`:

```gml
/// @func caida_prevista(_x0, _y0, _vx, _vy, _grav, _y_suelo)
/// @desc X en la que un proyectil balístico cruzará la altura `_y_suelo`.
///       Ojo: en GameMaker la Y crece hacia ABAJO, así que `_vy` negativa es «hacia arriba».
/// @returns {Real} Coordenada X del impacto, o `undefined` si nunca llega.
function caida_prevista(_x0, _y0, _vx, _vy, _grav, _y_suelo)
{
    var _disc = sqr(_vy) + 2 * _grav * (_y_suelo - _y0);
    if (_disc < 0) return undefined;              // se queda por encima del suelo
    var _t = (-_vy + sqrt(_disc)) / _grav;        // raíz positiva: el primer cruce
    return _x0 + _vx * _t;
}
```

```gml
/// obj_enemigo · Step — apuntar al sitio donde el jugador VA a estar
var _impacto = caida_prevista(obj_jugador.x, obj_jugador.y,
                              obj_jugador.vel_x, obj_jugador.vel_y,
                              obj_jugador.grav_caida, altura_suelo);
if (!is_undefined(_impacto)) mirar_hacia = _impacto;
```

### 2.2 Dibujar el arco antes de disparar

El arco punteado de *Worms* o *Angry Birds*: se evalúa la misma parábola en N instantes y se
unen los puntos. **No hace falta simular**: la posición en el instante `t` es analítica.

```gml
/// @func dibujar_arco(_x0, _y0, _vx, _vy, _grav, _pasos, _salto)
/// @desc Traza la trayectoria balística con líneas, parándose al tocar un sólido.
/// @param {Real} _pasos  Número de segmentos a dibujar.
/// @param {Real} _salto  Unidades de tiempo entre segmento y segmento.
function dibujar_arco(_x0, _y0, _vx, _vy, _grav, _pasos = 30, _salto = 3)
{
    var _ax = _x0, _ay = _y0;

    for (var _i = 1; _i <= _pasos; _i++)
    {
        var _t  = _i * _salto;
        var _bx = _x0 + _vx * _t;
        var _by = _y0 + _vy * _t + 0.5 * _grav * sqr(_t);

        // la punta se desvanece: informa sin tapar el escenario
        draw_line_width_colour(_ax, _ay, _bx, _by, 2,
                               c_white, merge_colour(c_white, c_black, _i / _pasos));

        if (position_meeting(_bx, _by, obj_solido)) break;
        _ax = _bx;
        _ay = _by;
    }
}
```

### 2.3 Lanzar hacia un objetivo: resolver el ángulo

Al revés: sabes la velocidad y a dónde quieres llegar, y necesitas el ángulo. La solución
clásica del tiro parabólico da **dos** respuestas: el tiro tenso y el tiro alto (mortero).

```gml
/// @func angulo_de_tiro(_x0, _y0, _tx, _ty, _vel, _grav, _alto)
/// @desc Ángulo (en grados de GameMaker) para alcanzar (_tx,_ty) con velocidad `_vel`.
/// @param {Bool} _alto  `true` = trayectoria en mortero; `false` = tiro tenso.
/// @returns {Real}      Dirección en grados, o `undefined` si está fuera de alcance.
function angulo_de_tiro(_x0, _y0, _tx, _ty, _vel, _grav, _alto = false)
{
    var _dx = _tx - _x0;
    var _dy = _y0 - _ty;                  // positivo = el objetivo está por ENCIMA
    if (_dx == 0) _dx = 0.0001;           // evita la división degenerada

    var _v2   = sqr(_vel);
    var _disc = sqr(_v2) - _grav * (_grav * sqr(_dx) + 2 * _dy * _v2);
    if (_disc < 0) return undefined;      // con esa velocidad no llega: sube `_vel`

    var _raiz = sqrt(_disc);
    var _num  = _alto ? (_v2 + _raiz) : (_v2 - _raiz);

    // arctan2(y, x) resuelve el cuadrante solo: vale con _dx negativo
    return radtodeg(arctan2(_num, _grav * _dx));
}
```

```gml
/// obj_catapulta · disparar al ratón con velocidad fija
var _dir = angulo_de_tiro(x, y, mouse_x, mouse_y, 12, grav_caida, true);
if (!is_undefined(_dir))
{
    var _p = instance_create_layer(x, y, "Instances", obj_proyectil);
    _p.vel_x = lengthdir_x(12, _dir);
    _p.vel_y = lengthdir_y(12, _dir);   // negativo hacia arriba: coincide con GameMaker
}
```

> 💡 **Por qué encaja sin conversiones.** El ángulo que devuelve la fórmula está medido en
> sentido antihorario con el eje Y hacia arriba, exactamente la convención de `direction`,
> `lengthdir_x` y `lengthdir_y` de GameMaker. Y `lengthdir_y` devuelve negativo hacia arriba,
> que es justo lo que espera `vel_y`. El sistema de coordenadas está explicado en
> [08 · 11](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores,%20matrices%20y%20ángulos.md).

---

## 3 · Colisiones propias (y por qué normalmente no hacen falta)

**`move_and_collide()` resuelve el 80 % de los casos** y lo hace mejor de lo que lo vas a
hacer tú: divide el movimiento en sub-pasos, sube pendientes y escalones, acepta arrays de
objetos y tilemaps, y devuelve con qué chocó. Su firma completa y sus trampas están en
[01 · 08 §2](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) — **empieza
siempre por ahí**.

El 20 % restante es cuando necesitas geometría que no es una bounding box: círculos,
detección contra estructuras de datos en vez de instancias, o resolver el solapamiento tú
mismo (empujar partículas Verlet, separar cuerpos blandos).

### 3.1 Las tres pruebas básicas

```gml
/// scr_geometria — pruebas de solapamiento sin instancias de por medio

/// @func solapan_cajas(_ax1,_ay1,_ax2,_ay2,_bx1,_by1,_bx2,_by2)
/// @desc AABB contra AABB. Cuatro comparaciones: es la prueba más barata que existe.
/// @returns {Bool}
function solapan_cajas(_ax1, _ay1, _ax2, _ay2, _bx1, _by1, _bx2, _by2)
{
    return (_ax1 < _bx2) && (_ax2 > _bx1) && (_ay1 < _by2) && (_ay2 > _by1);
}

/// @func solapan_circulos(_ax,_ay,_ar,_bx,_by,_br)
/// @desc Círculo contra círculo. Se compara al cuadrado: nos ahorramos la raíz.
/// @returns {Bool}
function solapan_circulos(_ax, _ay, _ar, _bx, _by, _br)
{
    var _dx = _bx - _ax, _dy = _by - _ay;
    var _r  = _ar + _br;
    return (_dx * _dx + _dy * _dy) < (_r * _r);
}

/// @func solapa_circulo_caja(_cx,_cy,_r,_x1,_y1,_x2,_y2)
/// @desc Círculo contra AABB: se busca el punto de la caja más cercano al centro
///       y se mide la distancia a ese punto. Vale también para las esquinas.
/// @returns {Bool}
function solapa_circulo_caja(_cx, _cy, _r, _x1, _y1, _x2, _y2)
{
    var _px = clamp(_cx, _x1, _x2);
    var _py = clamp(_cy, _y1, _y2);
    var _dx = _cx - _px, _dy = _cy - _py;
    return (_dx * _dx + _dy * _dy) < (_r * _r);
}
```

> 🔺 **`rectangle_in_rectangle()` NO devuelve un booleano.** Devuelve `0` si no se tocan, `1`
> si el origen está **completamente dentro** del destino y `2` si solo se superponen
> (verificado en el manual). Un `if (rectangle_in_rectangle(...))` da `true` en los dos casos
> de contacto, que suele ser lo que quieres, pero si buscas «está totalmente dentro» tienes
> que comparar con `== 1`. `point_in_circle()` y `rectangle_in_circle()`, en cambio, sí son
> booleanas.

### 3.2 Separación mínima: resolver el solapamiento

Detectar no es resolver. Cuando dos cajas ya se solapan, hay que empujarlas por el **eje de
menor penetración**: es el que produce el movimiento más pequeño y por tanto el que menos se
nota.

```gml
/// @func separacion_minima(_ax1,_ay1,_ax2,_ay2,_bx1,_by1,_bx2,_by2)
/// @desc Vector mínimo que hay que sumar a la caja A para dejar de solapar con B.
/// @returns {Array<Real>} [dx, dy]; [0,0] si no se solapan.
function separacion_minima(_ax1, _ay1, _ax2, _ay2, _bx1, _by1, _bx2, _by2)
{
    if (!solapan_cajas(_ax1, _ay1, _ax2, _ay2, _bx1, _by1, _bx2, _by2)) return [0, 0];

    // penetración por cada lado
    var _der = _bx2 - _ax1;      // empujar A a la derecha
    var _izq = _ax2 - _bx1;      // empujar A a la izquierda
    var _aba = _by2 - _ay1;
    var _arr = _ay2 - _by1;

    var _px = (_der < _izq) ?  _der : -_izq;
    var _py = (_aba < _arr) ?  _aba : -_arr;

    // se corrige solo el eje más barato: mover los dos «redondea» las esquinas
    if (abs(_px) < abs(_py)) return [_px, 0];
    return [0, _py];
}
```

```gml
/// obj_caja · Step — empujar suavemente a las cajas que se amontonen
var _lista = ds_list_create();
var _n = instance_place_list(x, y, obj_caja, _lista, false);
for (var _i = 0; _i < _n; _i++)
{
    var _o = _lista[| _i];
    if (_o == id) continue;
    var _s = separacion_minima(bbox_left, bbox_top, bbox_right, bbox_bottom,
                               _o.bbox_left, _o.bbox_top, _o.bbox_right, _o.bbox_bottom);
    x += _s[0] * 0.5;      // la mitad cada una: el reparto simétrico no da tirones
    y += _s[1] * 0.5;
}
ds_list_destroy(_lista);
```

### 3.3 Barrido («swept»): el arreglo del túnel

Un objeto rápido salta la pared entre dos frames. La solución barata y suficiente para el 99 %
de los juegos 2D: **subdividir el movimiento** en pasos menores que el grosor del obstáculo.

```gml
/// @func avanzar_barrido(_dx, _dy, _obj, _grosor_minimo)
/// @desc Mueve la instancia en varios sub-pasos, parando en el primer contacto.
///       `_grosor_minimo` es el lado más fino que puede tener un sólido del nivel.
/// @returns {Bool} `true` si chocó.
function avanzar_barrido(_dx, _dy, _obj, _grosor_minimo = 8)
{
    var _dist  = point_distance(0, 0, _dx, _dy);
    var _pasos = max(1, ceil(_dist / _grosor_minimo));
    var _sx = _dx / _pasos, _sy = _dy / _pasos;

    repeat (_pasos)
    {
        if (place_meeting(x + _sx, y + _sy, _obj)) return true;
        x += _sx;
        y += _sy;
    }
    return false;
}
```

> 💡 **`move_and_collide()` ya hace esto** con su argumento `num_iterations` (4 por defecto).
> Sube ese número antes de escribir el barrido a mano: `move_and_collide(vx, vy, obj, 8)`.
> Escribe el tuyo solo si necesitas parar en el punto exacto del impacto (una bala que deja
> un agujero) o si no estás moviendo una instancia.
>
> 📘 **No reinventes la rueda de las colisiones raras.** El catálogo tiene
> `Loj-Hadron-Collider` (colisiones pixel-perfect), `Bonk` (formas arbitrarias 2D y 3D) y
> `Fracture` (destrucción procedural). Están en
> [`11 - Código descargado/_CATALOGO.md`](../11%20-%20Código%20descargado/_CATALOGO.md),
> sección «Física y colisiones».

Estas tres pruebas resuelven **una pareja**. Cuando hay cientos de entidades y todas deben
chocar entre sí, el problema deja de ser la prueba y pasa a ser *cuántas veces la haces*: eso
lo resuelve el §4.

---

## 4 · Particionado espacial: colisiones cuando hay cientos de cosas

Todo lo anterior asume pocas entidades. En cuanto tienes 300 proyectiles que deben chocar
**entre sí**, o 800 partículas Verlet que no pueden atravesarse, aparece el muro: comparar
todo contra todo son `N·(N−1)/2` parejas.

| Entidades | Parejas por frame | A 60 fps |
|---:|---:|---|
| 50 | 1 225 | trivial |
| 200 | 19 900 | empieza a notarse en la VM |
| 500 | 124 750 | ⚠️ se come el frame |
| 1 000 | 499 500 | inviable en GML |

El arreglo no es optimizar la comparación: es **no hacer la mayoría de ellas**. Dos entidades
que están a media pantalla de distancia no pueden chocar, así que no hay que preguntárselo.
Eso es el particionado espacial.

### 4.1 El spatial hash: una rejilla de cubos

La estructura más simple que funciona. Se divide el mundo en celdas de tamaño fijo; cada
entidad se mete en la celda que le toca; y cada entidad **solo se compara con las de su celda
y las ocho vecinas**. El coste pasa de `O(N²)` a `≈ O(N·k)`, donde `k` es cuántas entidades
caen de media en un bloque de 3 × 3 celdas.

**La regla del tamaño de celda:** un poco más que el **diámetro de la entidad más grande**.
Más pequeña y una entidad ocupa muchas celdas; más grande y cada celda contiene demasiadas y
vuelves al problema original.

```gml
/// scr_rejilla_espacial — spatial hash para colisiones entre muchas entidades

/// @func rejilla_nueva(_ancho, _alto, _celda)
/// @desc Rejilla uniforme de cubos. Cada cubo es un array de referencias.
/// @param {Real} _celda  Lado de la celda; usa ~1,5-2× el diámetro mayor.
/// @returns {Struct}
function rejilla_nueva(_ancho, _alto, _celda)
{
    var _cols  = ceil(_ancho / _celda);
    var _filas = ceil(_alto  / _celda);
    var _cubos = array_create(_cols * _filas);
    for (var _i = 0; _i < _cols * _filas; _i++) _cubos[_i] = [];

    return { celda : _celda, cols : _cols, filas : _filas, cubos : _cubos };
}

/// @func rejilla_vaciar(_r)
/// @desc Deja los cubos a cero SIN reasignar arrays: array_resize(a, 0) reutiliza
///       la memoria, mientras que `= []` crearía un array nuevo por celda y por
///       frame — trabajo gratis para el recolector de basura.
function rejilla_vaciar(_r)
{
    var _n = array_length(_r.cubos);
    for (var _i = 0; _i < _n; _i++) array_resize(_r.cubos[_i], 0);
}

/// @func rejilla_insertar(_r, _e)
/// @desc Mete la entidad (un struct con .px y .py) en su celda.
function rejilla_insertar(_r, _e)
{
    var _cx = clamp(floor(_e.px / _r.celda), 0, _r.cols  - 1);
    var _cy = clamp(floor(_e.py / _r.celda), 0, _r.filas - 1);
    array_push(_r.cubos[_cy * _r.cols + _cx], _e);
}

/// @func rejilla_vecinos(_r, _px, _py, _radio)
/// @desc Todas las entidades de los cubos que toca el círculo (_px,_py,_radio).
///       Es una consulta amplia («broad phase»): devuelve candidatos, no choques.
/// @returns {Array<Struct>}
function rejilla_vecinos(_r, _px, _py, _radio)
{
    var _res = [];
    var _i0 = clamp(floor((_px - _radio) / _r.celda), 0, _r.cols  - 1);
    var _i1 = clamp(floor((_px + _radio) / _r.celda), 0, _r.cols  - 1);
    var _j0 = clamp(floor((_py - _radio) / _r.celda), 0, _r.filas - 1);
    var _j1 = clamp(floor((_py + _radio) / _r.celda), 0, _r.filas - 1);

    for (var _j = _j0; _j <= _j1; _j++)
    {
        for (var _i = _i0; _i <= _i1; _i++)
        {
            var _cubo = _r.cubos[_j * _r.cols + _i];
            var _n = array_length(_cubo);
            for (var _k = 0; _k < _n; _k++) array_push(_res, _cubo[_k]);
        }
    }
    return _res;
}
```

### 4.2 Ejemplo completo: 400 partículas que chocan entre sí

```gml
/// obj_particulas · Create
#macro RADIO_PARTICULA 6

rejilla    = rejilla_nueva(room_width, room_height, RADIO_PARTICULA * 4);
particulas = [];
repeat (400)
{
    array_push(particulas, {
        px    : random(room_width),
        py    : random(room_height),
        vx    : random_range(-2, 2),
        vy    : random_range(-2, 2),
        radio : RADIO_PARTICULA
    });
}
```

```gml
/// obj_particulas · Step
var _n = array_length(particulas);

// 1 · integrar y rebotar contra los bordes de la room
for (var _i = 0; _i < _n; _i++)
{
    var _p = particulas[_i];
    _p.vy += 0.25;
    _p.px += _p.vx;
    _p.py += _p.vy;

    if (_p.px < _p.radio)               { _p.px = _p.radio;               _p.vx = -_p.vx * 0.8; }
    if (_p.px > room_width  - _p.radio) { _p.px = room_width  - _p.radio; _p.vx = -_p.vx * 0.8; }
    if (_p.py < _p.radio)               { _p.py = _p.radio;               _p.vy = -_p.vy * 0.8; }
    if (_p.py > room_height - _p.radio) { _p.py = room_height - _p.radio; _p.vy = -_p.vy * 0.8; }
}

// 2 · reconstruir la rejilla. Es O(N) y hay que hacerlo CADA frame: mover una
//     entidad de celda es más caro que rehacer la rejilla entera.
rejilla_vaciar(rejilla);
for (var _i = 0; _i < _n; _i++) rejilla_insertar(rejilla, particulas[_i]);

// 3 · resolver solo contra los vecinos del bloque de celdas
for (var _i = 0; _i < _n; _i++)
{
    var _a   = particulas[_i];
    var _vec = rejilla_vecinos(rejilla, _a.px, _a.py, _a.radio * 2);
    var _m   = array_length(_vec);

    for (var _k = 0; _k < _m; _k++)
    {
        var _b = _vec[_k];
        if (_b == _a) continue;                      // no chocar consigo misma
        if (!solapan_circulos(_a.px, _a.py, _a.radio, _b.px, _b.py, _b.radio)) continue;

        var _dx = _b.px - _a.px;
        var _dy = _b.py - _a.py;
        var _d  = sqrt(_dx * _dx + _dy * _dy);
        if (_d < 0.0001) { _dx = 0.01; _dy = 0; _d = 0.01; }   // centros coincidentes

        // separación: la mitad cada una. Cada pareja se procesa dos veces
        // (A→B y B→A), así que media corrección por vez da la corrección entera.
        var _solape = (_a.radio + _b.radio - _d) * 0.5;
        var _nx = _dx / _d, _ny = _dy / _d;

        _a.px -= _nx * _solape * 0.5;
        _a.py -= _ny * _solape * 0.5;
        _b.px += _nx * _solape * 0.5;
        _b.py += _ny * _solape * 0.5;

        // rebote sobre la normal del contacto (§7.1). Ojo al signo: la normal que
        // "sale" de B hacia A es -n, y la que sale de A hacia B es +n.
        var _ra = rebotar_vector(_a.vx, _a.vy, -_nx, -_ny, 0.5);
        var _rb = rebotar_vector(_b.vx, _b.vy,  _nx,  _ny, 0.5);
        _a.vx = _ra[0]; _a.vy = _ra[1];
        _b.vx = _rb[0]; _b.vy = _rb[1];
    }
}
```

```gml
/// obj_particulas · Draw
var _n = array_length(particulas);
for (var _i = 0; _i < _n; _i++)
{
    var _p = particulas[_i];
    draw_circle_colour(_p.px, _p.py, _p.radio, c_aqua, c_blue, false);
}
```

> 💡 **Un cubo por celda es una simplificación aceptable.** Una entidad que cae justo en el
> borde entre dos celdas solo se registra en una, pero como la consulta barre el bloque de
> celdas que toca su radio, el vecino la encuentra igual. Registrar cada entidad en las cuatro
> celdas que solapa es más exacto y cuesta el cuádruple de inserciones: no compensa mientras
> la celda sea mayor que la entidad.

### 4.3 Cuándo compensa, y cuándo no

| Situación | Qué usar |
|---|---|
| Menos de ~50 entidades | Nada. El bucle doble directo es más rápido que construir la rejilla |
| Instancias de GameMaker, decenas de ellas | `place_meeting()` / `instance_place()` — [01 · 08](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) |
| Instancias, y quieres «todo lo que hay en esta zona» | `collision_rectangle_list()` / `collision_circle_list()` |
| Cientos o miles de entidades que son **structs**, no instancias | **Spatial hash** (§4.1) — no hay alternativa nativa |
| Entidades de tamaños muy dispares, o mundo enorme y casi vacío | Quadtree (§4.4) |
| Geometría **estática** que se consulta mucho y no cambia | Quadtree, construido una sola vez |

**Las funciones nativas son la primera opción cuando tus entidades son instancias.**
`collision_rectangle_list(x1, y1, x2, y2, obj, prec, notme, list, ordered)` devuelve **cuántas**
instancias encontró y rellena una `ds_list` con sus handles: es exactamente una consulta de
región, escrita en C++ y sin coste de GML.

```gml
/// «¿qué enemigos hay a menos de 100 px?» — la versión nativa, para instancias
var _lista = ds_list_create();
var _cuantos = collision_circle_list(x, y, 100, obj_enemigo, false, true, _lista, true);
for (var _i = 0; _i < _cuantos; _i++)
{
    with (_lista[| _i]) { vida -= 5; }
}
ds_list_destroy(_lista);
```

> 🔺 **`prec = true` es caro.** Fuerza comprobación píxel a píxel contra la máscara y exige
> que **todas** las instancias comprobadas tengan máscara precisa. Déjalo en `false` salvo que
> de verdad necesites precisión de píxel; el manual lo dice sin rodeos («`true`, que es más
> lento»).
>
> 🔺 **`ds_list` hay que destruirla.** No la recoge el recolector de basura. Si la creas cada
> frame y no la destruyes, tienes una fuga silenciosa; si la vas a usar todos los frames,
> créala en el Create, límpiala con `ds_list_clear()` y destrúyela en el Clean Up
> ([01 · 15 §8](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)).

**El argumento que decide este documento:** los puntos de Verlet (§6), las columnas de agua
(§9) y las celdas del autómata (§10) **no son instancias**. Ninguna función `collision_*` los
ve. Para que choquen entre sí, la rejilla te la escribes tú.

### 4.4 Y el quadtree, ¿por qué no?

Un **quadtree** subdivide el espacio de forma adaptativa: parte el mundo en cuatro, y cada
cuadrante que acumula demasiadas entidades se vuelve a partir en cuatro. Se adapta a la
densidad: en la zona vacía hay un nodo, en el montón hay veinte.

Y aun así, **en 2D casi siempre gana el spatial hash**, por cuatro razones:

1. **Un mundo 2D típico tiene densidad razonablemente uniforme** y entidades de tamaño
   parecido. La ventaja del quadtree —adaptarse a densidades muy dispares— no se cobra.
2. **Reconstruir es O(N) y sin asignaciones.** El hash se vacía con `array_resize` y se llena
   con `array_push`. Un quadtree exige crear, dividir y fusionar nodos: en GML cada nodo es un
   struct, y crear miles de structs por frame es justo lo que dispara al recolector de basura
   ([01 · 15 §5](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)).
3. **La consulta es aritmética directa**, sin recorrer un árbol: dos divisiones y un índice.
4. **Cabe en 40 líneas.** Un quadtree correcto —con inserción, subdivisión, consulta por
   rango y fusión— son varios cientos, y cada línea es una oportunidad de equivocarse.

**El quadtree gana en tres casos concretos:** geometría **estática** que se construye una vez y
se consulta millones de veces (colisión contra un mapa, *culling* de renderizado), mundos
enormes con clusters muy separados, y entidades de tamaños que difieren en órdenes de magnitud
(donde no existe un tamaño de celda bueno para todos).

> 📘 **Si necesitas uno de verdad, ya está escrito.** En el corpus hay quadtrees funcionando:
> `BBMOD` (`cm_quadtree`) y `DS-3DCollisions` los usan para colisión contra mallas — y no es
> casualidad que ambos sean **3D con geometría estática**, el caso donde el quadtree
> (y su hermano el octree) sí compensa. Rutas en
> [`11 - Código descargado/_CATALOGO.md`](../11%20-%20Código%20descargado/_CATALOGO.md).
>
> ⚠️ **Ningún otro documento propio de esta biblioteca cubre el particionado espacial**: si
> buscas «quadtree» con `buscar.py --todo`, solo salen esas librerías descargadas. Esta
> sección es la única referencia propia sobre el tema.

---

## 5 · Muelles amortiguados: el caballo de batalla

Un muelle amortiguado es **la herramienta más rentable de todo este documento**. Sirve para
cámaras, HUD, capas y pelo, zoom, retroceso de armas, menús que se colocan, barras de vida que
alcanzan su valor... Cualquier número que deba «llegar con inercia» a otro número.

La ecuación es la de Hooke más un término de rozamiento:

```
a = −k·(x − objetivo) − c·v
```

- `k` (**rigidez**) manda en la velocidad: más alto, más rápido llega.
- `c` (**amortiguación**) manda en el rebote. El valor crítico es **`c = 2·√k`**: por debajo
  oscila, por encima llega despacio y sin pasarse.

```gml
/// scr_muelle — un muelle amortiguado de una dimensión

/// @func muelle_nuevo(_valor, _rigidez, _amortiguacion)
/// @desc Crea el estado de un muelle. Por defecto queda críticamente amortiguado
///       (c = 2·√k): llega rápido y NO rebota.
/// @param {Real} _valor          Valor inicial.
/// @param {Real} _rigidez        k. 100 ≈ suave, 400 ≈ nervioso, 900 ≈ seco.
/// @param {Real} _amortiguacion  c. `undefined` = crítica.
/// @returns {Struct}
function muelle_nuevo(_valor, _rigidez = 100, _amortiguacion = undefined)
{
    return {
        valor         : _valor,
        vel           : 0,
        rigidez       : _rigidez,
        amortiguacion : is_undefined(_amortiguacion) ? 2 * sqrt(_rigidez) : _amortiguacion
    };
}

/// @func muelle_actualizar(_m, _objetivo, _dt, _subpasos)
/// @desc Avanza el muelle hacia `_objetivo`. Integración semi-implícita (§1.2).
/// @param {Struct} _m         Estado devuelto por muelle_nuevo().
/// @param {Real}   _objetivo  Valor al que tiende.
/// @param {Real}   _dt        Paso de tiempo en SEGUNDOS.
/// @param {Real}   _subpasos  Sub-divisiones del paso; súbelo si el muelle vibra.
/// @returns {Real}            El nuevo valor.
function muelle_actualizar(_m, _objetivo, _dt, _subpasos = 1)
{
    var _h = _dt / _subpasos;
    repeat (_subpasos)
    {
        var _acel = -_m.rigidez * (_m.valor - _objetivo) - _m.amortiguacion * _m.vel;
        _m.vel   += _acel * _h;      // primero la velocidad
        _m.valor += _m.vel * _h;     // luego la posición
    }
    return _m.valor;
}

/// @func muelle_golpear(_m, _impulso)
/// @desc Mete energía de golpe (retroceso de un arma, impacto en el HUD).
function muelle_golpear(_m, _impulso)
{
    _m.vel += _impulso;
}
```

**Estabilidad, en una regla:** el muelle es estable mientras `√k · dt < 1`. Con `dt = 1/60`
eso permite `k` hasta ≈ 3600. Si necesitas más rigidez —o si tu framerate cae— sube
`_subpasos` en vez de bajar `k`: la sensación se conserva y el muelle deja de vibrar.

```gml
/// obj_camara · Create — cámara con inercia, sin lerp dependiente del framerate
mx = muelle_nuevo(x, 120);
my = muelle_nuevo(y, 120);

/// obj_camara · Step
var _dt = delta_time / 1000000;
var _cx = muelle_actualizar(mx, obj_jugador.x, _dt);
var _cy = muelle_actualizar(my, obj_jugador.y, _dt);
camera_set_view_pos(view_camera[0], _cx - 320, _cy - 180);
```

```gml
/// obj_hud · Create — la barra de vida "alcanza" al valor real y rebota un poco
barra = muelle_nuevo(100, 220, 14);   // amortiguación por debajo de la crítica (2·√220 ≈ 29,7)

/// obj_hud · Draw GUI
var _v = muelle_actualizar(barra, obj_jugador.vida, delta_time / 1000000);
draw_healthbar(20, 20, 220, 36, _v, c_black, c_red, c_lime, 0, true, true);
```

```gml
/// obj_capa · Create — dos muelles encadenados hacen una capa/cola/coleta
m1x = muelle_nuevo(x, 260, 16);      // el primer nudo, nervioso
m2x = muelle_nuevo(x, 140, 11);      // el segundo, más lento: de ahí el latigazo

/// obj_capa · Step — cada nudo persigue al anterior, no al personaje
var _dt = delta_time / 1000000;
var _ox = obj_jugador.x - lengthdir_x(6, obj_jugador.mirada);
nudo1_x = muelle_actualizar(m1x, _ox,     _dt);
nudo2_x = muelle_actualizar(m2x, nudo1_x, _dt);
```

> 💡 **Muelle o `lerp`.** `lerp(a, b, 0.1)` es un filtro exponencial: llega asintóticamente,
> nunca rebota y **depende del framerate** salvo que uses
> [`lerp_dt()`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml). El muelle tiene *inercia*:
> se pasa, vuelve, y responde a golpes. Para una cámara suave, `lerp_dt` basta; para algo que
> deba sentirse **físico**, muelle.

---

## 6 · Integración de Verlet: cuerdas, tela y cuerpos blandos

Verlet cambia el trato: en vez de guardar la velocidad, guarda la **posición anterior**. La
velocidad está implícita en la diferencia `p − p_anterior`. La fórmula (Jakobsen, *Advanced
Character Physics*):

```
p' = 2·p − p_anterior + a·dt²
```

Su virtud no es la precisión, es que **las restricciones son gratis**: para que dos puntos
estén siempre a la misma distancia, los mueves y ya está — la velocidad se ajusta sola,
porque es una diferencia de posiciones. Eso es lo que hace que una cuerda de 40 eslabones no
tenga que resolver 40 ecuaciones acopladas.

### 6.1 El punto y la varilla

```gml
/// scr_verlet — partículas y restricciones de distancia

/// @func verlet_punto(_px, _py, _fijo)
/// @desc Una partícula de Verlet. `px_ant` es la posición del paso anterior:
///       la velocidad implícita es (px - px_ant).
/// @returns {Struct}
function verlet_punto(_px, _py, _fijo = false)
{
    return { px : _px, py : _py, px_ant : _px, py_ant : _py, fijo : _fijo };
}

/// @func verlet_varilla(_a, _b, _largo)
/// @desc Restricción de distancia entre dos puntos. Si `_largo` es undefined,
///       toma la distancia actual como longitud de reposo.
/// @returns {Struct}
function verlet_varilla(_a, _b, _largo = undefined)
{
    return {
        a     : _a,
        b     : _b,
        largo : is_undefined(_largo) ? point_distance(_a.px, _a.py, _b.px, _b.py) : _largo
    };
}
```

### 6.2 El bucle: integrar → relajar → colisionar

```gml
/// @func verlet_integrar(_puntos, _grav, _roce)
/// @desc Avanza todas las partículas un paso. `_roce` < 1 disipa energía.
function verlet_integrar(_puntos, _grav = 0.5, _roce = 0.99)
{
    var _n = array_length(_puntos);
    for (var _i = 0; _i < _n; _i++)
    {
        var _p = _puntos[_i];
        if (_p.fijo) continue;

        var _vx = (_p.px - _p.px_ant) * _roce;
        var _vy = (_p.py - _p.py_ant) * _roce;

        _p.px_ant = _p.px;
        _p.py_ant = _p.py;

        _p.px += _vx;
        _p.py += _vy + _grav;     // dt = 1 paso, así que a·dt² es la propia gravedad
    }
}

/// @func verlet_relajar(_varillas, _iteraciones)
/// @desc Satisface las restricciones de distancia. Cada iteración las acerca más
///       a la solución exacta: 3-5 basta para una cuerda, 8-15 para tela tensa.
function verlet_relajar(_varillas, _iteraciones = 5)
{
    var _n = array_length(_varillas);
    repeat (_iteraciones)
    {
        for (var _i = 0; _i < _n; _i++)
        {
            var _v = _varillas[_i];
            var _a = _v.a, _b = _v.b;

            var _dx = _b.px - _a.px;
            var _dy = _b.py - _a.py;
            var _d  = sqrt(_dx * _dx + _dy * _dy);
            if (_d < 0.0001) continue;               // puntos coincidentes: nada que hacer

            var _factor = (_d - _v.largo) / _d;      // >0 estirada, <0 comprimida
            var _wa = _a.fijo ? 0 : 1;
            var _wb = _b.fijo ? 0 : 1;
            var _wt = _wa + _wb;
            if (_wt == 0) continue;                  // los dos anclados

            _a.px += _dx * _factor * (_wa / _wt);
            _a.py += _dy * _factor * (_wa / _wt);
            _b.px -= _dx * _factor * (_wb / _wt);
            _b.py -= _dy * _factor * (_wb / _wt);
        }
    }
}

/// @func verlet_suelo(_puntos, _y_suelo, _rebote, _roce)
/// @desc Colisión por proyección contra un suelo horizontal: se devuelve el punto
///       fuera y se retoca la posición anterior para simular rebote y rozamiento.
function verlet_suelo(_puntos, _y_suelo, _rebote = 0.3, _roce = 0.7)
{
    var _n = array_length(_puntos);
    for (var _i = 0; _i < _n; _i++)
    {
        var _p = _puntos[_i];
        if (_p.fijo || _p.py <= _y_suelo) continue;

        var _vx = _p.px - _p.px_ant;
        var _vy = _p.py - _p.py_ant;

        _p.py     = _y_suelo;
        _p.py_ant = _p.py + _vy * _rebote;   // invierte la velocidad vertical
        _p.px_ant = _p.px - _vx * _roce;     // frena la horizontal
    }
}
```

> 🔺 **El orden importa y no es negociable:** integrar → relajar → colisionar. Si colisionas
> antes de relajar, la varilla vuelve a meter el punto dentro del suelo. Si relajas antes de
> integrar, trabajas con datos del frame pasado. Jakobsen lo llama *relajación*, y su gracia es
> que **no converge del todo**: con pocas iteraciones se ve elástico, con muchas se ve rígido.
> Ese es tu mando de tensión.

### 6.3 Cuerda, cadena y tela

```gml
/// @func cuerda_nueva(_x0, _y0, _eslabones, _largo)
/// @desc Cuerda colgante: el primer punto queda anclado.
/// @returns {Struct} { puntos, varillas }
function cuerda_nueva(_x0, _y0, _eslabones = 20, _largo = 8)
{
    var _puntos = [], _varillas = [];
    for (var _i = 0; _i < _eslabones; _i++)
    {
        array_push(_puntos, verlet_punto(_x0, _y0 + _i * _largo, _i == 0));
        if (_i > 0) array_push(_varillas, verlet_varilla(_puntos[_i - 1], _puntos[_i], _largo));
    }
    return { puntos : _puntos, varillas : _varillas };
}

/// @func tela_nueva(_x0, _y0, _cols, _filas, _paso)
/// @desc Malla rectangular con varillas horizontales y verticales. La fila
///       superior queda clavada: una bandera, un telón, una capa.
/// @returns {Struct} { puntos, varillas, cols, filas }
function tela_nueva(_x0, _y0, _cols = 14, _filas = 10, _paso = 10)
{
    var _puntos = [], _varillas = [];

    for (var _j = 0; _j < _filas; _j++)
    {
        for (var _i = 0; _i < _cols; _i++)
        {
            // se clava una de cada cuatro de la fila de arriba: cuelga con pliegues
            var _fijo = (_j == 0) && (_i % 4 == 0);
            array_push(_puntos, verlet_punto(_x0 + _i * _paso, _y0 + _j * _paso, _fijo));
        }
    }
    for (var _j = 0; _j < _filas; _j++)
    {
        for (var _i = 0; _i < _cols; _i++)
        {
            var _k = _j * _cols + _i;
            if (_i > 0) array_push(_varillas, verlet_varilla(_puntos[_k - 1],     _puntos[_k], _paso));
            if (_j > 0) array_push(_varillas, verlet_varilla(_puntos[_k - _cols], _puntos[_k], _paso));
        }
    }
    return { puntos : _puntos, varillas : _varillas, cols : _cols, filas : _filas };
}
```

```gml
/// obj_cuerda · Create
cuerda = cuerda_nueva(x, y, 24, 7);

/// obj_cuerda · Step — el bucle completo, en el orden correcto
verlet_integrar(cuerda.puntos, 0.45, 0.995);
verlet_relajar(cuerda.varillas, 6);
verlet_suelo(cuerda.puntos, room_height - 32, 0.2, 0.6);

// la punta sigue al ratón: se mueve el punto y la cuerda se acomoda sola
var _fin = array_last(cuerda.puntos);
_fin.px = mouse_x;
_fin.py = mouse_y;
```

### 6.4 Cuerpo blando que recupera la forma

Un anillo de puntos con varillas en el borde se aplasta y **no vuelve**: le falta estructura
interna. La forma más simple de dársela son radios a un punto central; la más orgánica, unir
cada punto con el que está dos posiciones más allá.

```gml
/// @func blando_nuevo(_cx, _cy, _radio, _lados, _dureza)
/// @desc Cuerpo blando: anillo + radios al centro + tirantes cruzados.
///       `_dureza` 0..1 escala la longitud de reposo de los radios; por debajo de 1
///       el cuerpo queda «desinflado» y se aplasta más.
/// @returns {Struct} { puntos, varillas, centro }
function blando_nuevo(_cx, _cy, _radio = 24, _lados = 12, _dureza = 1)
{
    var _puntos = [], _varillas = [];
    var _centro = verlet_punto(_cx, _cy);

    for (var _i = 0; _i < _lados; _i++)
    {
        var _a = (_i / _lados) * 360;
        array_push(_puntos, verlet_punto(_cx + lengthdir_x(_radio, _a),
                                         _cy + lengthdir_y(_radio, _a)));
    }
    array_push(_puntos, _centro);

    for (var _i = 0; _i < _lados; _i++)
    {
        var _sig = (_i + 1) % _lados;
        var _dos = (_i + 2) % _lados;
        array_push(_varillas, verlet_varilla(_puntos[_i], _puntos[_sig]));         // borde
        array_push(_varillas, verlet_varilla(_puntos[_i], _puntos[_dos]));         // tirante
        array_push(_varillas, verlet_varilla(_puntos[_i], _centro, _radio * _dureza));
    }
    return { puntos : _puntos, varillas : _varillas, centro : _centro };
}
```

Con `_dureza = 1` y 10 iteraciones de relajación tienes una pelota firme. Con `_dureza = 0.75`
y 3 iteraciones, una gota de gelatina. **El mismo código, dos materiales.**

### 6.5 Dibujarlo

Dos vías, según lo que quieras: líneas (rápido de montar, se ve bien con grosor) o una tira
de triángulos (superficie rellena y texturizable).

```gml
/// @func verlet_dibujar_lineas(_varillas, _grosor, _col)
/// @desc Cada varilla, una línea. Suficiente para cuerdas, cadenas y depuración.
function verlet_dibujar_lineas(_varillas, _grosor = 2, _col = c_white)
{
    draw_set_colour(_col);
    var _n = array_length(_varillas);
    for (var _i = 0; _i < _n; _i++)
    {
        var _v = _varillas[_i];
        draw_line_width(_v.a.px, _v.a.py, _v.b.px, _v.b.py, _grosor);
    }
    draw_set_colour(c_white);
}

/// @func cuerda_dibujar_cinta(_puntos, _ancho, _col)
/// @desc La cuerda como una cinta rellena: en cada nudo se emiten dos vértices
///       perpendiculares al tramo. Con textura sale un látigo o un tentáculo.
function cuerda_dibujar_cinta(_puntos, _ancho = 6, _col = c_white)
{
    var _n = array_length(_puntos);
    if (_n < 2) return;

    draw_primitive_begin(pr_trianglestrip);
    for (var _i = 0; _i < _n; _i++)
    {
        var _p   = _puntos[_i];
        var _sig = _puntos[min(_i + 1, _n - 1)];
        var _ant = _puntos[max(_i - 1, 0)];

        // normal al tramo: la dirección del segmento girada 90°
        var _dir = point_direction(_ant.px, _ant.py, _sig.px, _sig.py) + 90;
        var _w   = _ancho * (1 - _i / _n);        // la cinta se afila hacia la punta

        draw_vertex_colour(_p.px + lengthdir_x(_w, _dir),
                           _p.py + lengthdir_y(_w, _dir), _col, 1);
        draw_vertex_colour(_p.px - lengthdir_x(_w, _dir),
                           _p.py - lengthdir_y(_w, _dir), _col, 1);
    }
    draw_primitive_end();
}
```

> 📘 **Ya existe una implementación de Verlet en GML** para leer y comparar:
> `GMVerlet-Integration` de tabularelf, en
> [`11 - Código descargado/_CATALOGO.md`](../11%20-%20Código%20descargado/_CATALOGO.md).
> ⚠️ Es experimental, de 2021 y **sin licencia declarada**: léela como referencia, no la
> copies a un proyecto que vayas a publicar.

---

## 7 · Cuerpos rígidos sencillos

### 7.1 Rebote con restitución

Todo rebote es la misma fórmula: reflejar la velocidad respecto a la normal de la superficie,
escalando la componente perpendicular por el coeficiente de restitución `e`.

```
v' = v − (1 + e)·(v · n)·n          con n normalizada
```

```gml
/// @func rebotar_vector(_vx, _vy, _nx, _ny, _restitucion)
/// @desc Refleja la velocidad contra una superficie de normal (_nx,_ny) NORMALIZADA.
/// @param {Real} _restitucion  0 = se pega; 1 = rebote perfecto; >1 explota.
/// @returns {Array<Real>} [vx, vy]
function rebotar_vector(_vx, _vy, _nx, _ny, _restitucion = 0.6)
{
    var _d = dot_product(_vx, _vy, _nx, _ny);
    if (_d > 0) return [_vx, _vy];                 // ya se aleja: no rebotes dos veces
    var _k = (1 + _restitucion) * _d;
    return [_vx - _k * _nx, _vy - _k * _ny];
}
```

```gml
/// obj_pelota · Step — rebotar contra el suelo y las paredes de la room
vel_y += 0.5;
x += vel_x;
y += vel_y;

if (y > room_height - 8)
{
    y = room_height - 8;
    var _r = rebotar_vector(vel_x, vel_y, 0, -1, 0.65);   // normal del suelo: hacia arriba
    vel_x = _r[0] * 0.98;                                  // rozamiento tangencial
    vel_y = _r[1];
    if (abs(vel_y) < 0.6) vel_y = 0;                       // umbral: si no, tiembla eternamente
}
```

> 🔺 **El `if (_d > 0) return` no es un adorno.** Sin él, un objeto que ya se aleja de la
> superficie recibe un segundo rebote y sale disparado. Es el bug número uno de los rebotes
> escritos a mano.

### 7.2 Rotación al chocar (aproximación)

Un cuerpo rígido de verdad necesita tensor de inercia y resolución de contactos. Para una caja
que cae y hay que verla girar, esta aproximación convence: **el giro es proporcional al momento
del impulso respecto al centro**, es decir al producto vectorial 2D entre el brazo y el
impulso.

```gml
/// @func giro_por_impacto(_brazo_x, _brazo_y, _imp_x, _imp_y, _inercia)
/// @desc Velocidad angular (grados por paso) que añade un impulso aplicado en un punto.
/// @param {Real} _brazo_x  Vector del centro de masa al punto de contacto.
/// @param {Real} _inercia  Resistencia al giro. Para una caja de lado L: ≈ L*L/6.
/// @returns {Real}
function giro_por_impacto(_brazo_x, _brazo_y, _imp_x, _imp_y, _inercia)
{
    var _cruz = _brazo_x * _imp_y - _brazo_y * _imp_x;   // producto vectorial en 2D
    return radtodeg(_cruz / max(_inercia, 0.0001));
}
```

```gml
/// obj_caja · al aterrizar sobre una esquina
var _brazo_x = punto_contacto_x - x;         // dónde tocó respecto al centro
var _brazo_y = punto_contacto_y - y;
vel_giro += giro_por_impacto(_brazo_x, _brazo_y, 0, -vel_y * 1.6, sqr(32) / 6);
vel_giro *= 0.97;                            // rozamiento angular: si no, gira para siempre
image_angle += vel_giro;
```

> ⚠️ **Esto es una aproximación deliberada**, no física correcta: no conserva el momento
> angular del sistema y no reparte el impulso entre los dos cuerpos. Se ve bien para escombros,
> cajas y monedas que caen. **Para apilar cajas rotadas de forma estable, usa Box2D**
> ([04 · 22](../04%20-%20Recetas%20por%20género/22%20-%20Físicas%20con%20Box2D.md)): ahí el
> problema es el solver de contactos, no la fórmula.

### 7.3 Ragdoll con Verlet

Un ragdoll no es más que el §6 con la topología de un esqueleto: puntos en las
articulaciones, varillas en los huesos y **varillas largas de más como límite de ángulo**.

```gml
/// @func ragdoll_nuevo(_x, _y)
/// @desc Muñeco de 6 puntos: cabeza, pecho, cadera, dos manos y dos pies.
///       Las varillas cruzadas (pecho-cadera larga) hacen de tope articular.
/// @returns {Struct} { puntos, varillas }
function ragdoll_nuevo(_x, _y)
{
    var _cabeza = verlet_punto(_x,      _y - 24);
    var _pecho  = verlet_punto(_x,      _y - 12);
    var _cadera = verlet_punto(_x,      _y);
    var _mano_i = verlet_punto(_x - 14, _y - 6);
    var _mano_d = verlet_punto(_x + 14, _y - 6);
    var _pie_i  = verlet_punto(_x - 7,  _y + 20);
    var _pie_d  = verlet_punto(_x + 7,  _y + 20);

    var _puntos = [_cabeza, _pecho, _cadera, _mano_i, _mano_d, _pie_i, _pie_d];
    var _varillas = [
        verlet_varilla(_cabeza, _pecho),
        verlet_varilla(_pecho,  _cadera),
        verlet_varilla(_pecho,  _mano_i),
        verlet_varilla(_pecho,  _mano_d),
        verlet_varilla(_cadera, _pie_i),
        verlet_varilla(_cadera, _pie_d),
        // topes: impiden que el muñeco se doble sobre sí mismo
        verlet_varilla(_cabeza, _cadera),
        verlet_varilla(_mano_i, _mano_d),
        verlet_varilla(_pie_i,  _pie_d)
    ];
    return { puntos : _puntos, varillas : _varillas };
}
```

El bucle es idéntico al de la cuerda. Para «lanzar» el ragdoll al morir, basta con separar
`px_ant` de `px`: la velocidad implícita hace el resto.

```gml
/// al morir: empujar el ragdoll en la dirección del golpe
var _p = ragdoll.puntos;
for (var _i = 0; _i < array_length(_p); _i++)
{
    _p[_i].px_ant = _p[_i].px - lengthdir_x(6, dir_golpe);
    _p[_i].py_ant = _p[_i].py - lengthdir_y(6, dir_golpe) - 3;
}
```

---

## 8 · Flotabilidad: objetos que flotan, se hunden y salpican

El principio de Arquímedes dice que el empuje vale el peso del fluido desplazado. En 2D y con
densidad constante eso se reduce a **la fracción sumergida del objeto**:

```gml
/// @func fraccion_sumergida(_y_centro, _alto, _nivel_agua)
/// @desc Qué parte del objeto (0..1) está por debajo de la línea de agua.
/// @returns {Real}
function fraccion_sumergida(_y_centro, _alto, _nivel_agua)
{
    var _abajo = _y_centro + _alto * 0.5;
    return clamp((_abajo - _nivel_agua) / _alto, 0, 1);
}

/// @func flotacion_aplicar(_y_centro, _alto, _vel_x, _vel_y, _nivel_agua, _empuje, _arrastre)
/// @desc Empuje de Arquímedes más arrastre. Devuelve la velocidad ya corregida,
///       para poder llamarla igual desde una instancia que desde un struct.
/// @param {Real} _empuje    Aceleración de empuje con el objeto TOTALMENTE sumergido.
/// @returns {Array<Real>}   [vel_x, vel_y]
function flotacion_aplicar(_y_centro, _alto, _vel_x, _vel_y, _nivel_agua, _empuje, _arrastre = 0.12)
{
    var _f = fraccion_sumergida(_y_centro, _alto, _nivel_agua);
    if (_f <= 0) return [_vel_x, _vel_y];

    _vel_y -= _empuje * _f;                 // hacia arriba (la Y crece hacia abajo)
    _vel_x *= 1 - _arrastre * _f;           // el agua frena en los dos ejes
    _vel_y *= 1 - _arrastre * _f;
    return [_vel_x, _vel_y];
}
```

- **La densidad relativa es `grav / empuje`.** Un corcho: `empuje = 3 · grav`. Una piedra:
  `empuje = 0.2 · grav`. Un cofre que se hunde despacio: `0.9 · grav`.
- **El arrastre es lo que evita la oscilación eterna.** Sin él, un barril entra en el agua,
  sale disparado, vuelve a caer y así indefinidamente. Con `0.10–0.15` se estabiliza en tres o
  cuatro rebotes, que es exactamente lo que se ve en la realidad.

```gml
/// obj_barril · Step
vel_y += grav;

var _v = flotacion_aplicar(y, alto, vel_x, vel_y, obj_agua.nivel, grav * 2.4, 0.12);
vel_x = _v[0];
vel_y = _v[1];

x += vel_x;
y += vel_y;

// entrada y salida: una sola vez, no cada frame
var _dentro = (y + alto * 0.5) > obj_agua.nivel;
if (_dentro != estaba_dentro)
{
    agua_salpicar(obj_agua.datos, x, vel_y * (_dentro ? 1.4 : -0.8));
    audio_play_sound(_dentro ? snd_chapoteo : snd_salir, 6, false);
    // las gotas son partículas normales: ver 04 · 15 §5.5
    part_particles_create(obj_fx.ps, x, obj_agua.nivel, obj_fx.pt_gota,
                          6 + floor(abs(vel_y) * 3));
    estaba_dentro = _dentro;
}
```

---

## 9 · Fluido, nivel 1: superficie de agua con muelles

La técnica canónica de agua 2D (Michael Hoffman, *Make a Splash With Dynamic 2D Water
Effects*): **la superficie es una fila de muelles verticales**, uno por columna, y cada muelle
tira de sus vecinos. Es barata, es estable y se ve bien en cuanto la afinas.

Tres constantes mandan:

| Constante | Qué hace | Rango útil |
|---|---|---|
| `tension` (k) | Rapidez con la que la columna vuelve al nivel | 0,010 – 0,050 |
| `amortiguacion` | Cuánto se calma la ola | 0,010 – 0,050 |
| `difusion` (spread) | Cuánto se contagia a las columnas vecinas | 0 – 0,5 |

Hoffman usa `k = 0.025`, amortiguación `0.025`, difusión ≈ `0.25` y **8 pasadas** de
propagación por frame. Son un buen punto de partida.

```gml
/// scr_agua — superficie de agua por muelles acoplados

/// @func agua_nueva(_x0, _ancho, _nivel, _profundidad, _columnas)
/// @desc Crea una masa de agua con la superficie discretizada en columnas.
/// @returns {Struct}
function agua_nueva(_x0, _ancho, _nivel, _profundidad = 120, _columnas = 80)
{
    var _cols = [];
    repeat (_columnas) array_push(_cols, { altura : _nivel, vel : 0 });

    return {
        x0            : _x0,
        paso          : _ancho / (_columnas - 1),
        nivel         : _nivel,
        profundidad   : _profundidad,
        columnas      : _cols,
        tension       : 0.025,
        amortiguacion : 0.025,
        difusion      : 0.25,
        pasadas       : 8
    };
}

/// @func agua_actualizar(_agua)
/// @desc Un paso: primero cada muelle por su cuenta, luego la propagación lateral.
function agua_actualizar(_agua)
{
    var _cols = _agua.columnas;
    var _n    = array_length(_cols);

    // 1 · cada columna es un muelle amortiguado hacia el nivel de reposo
    for (var _i = 0; _i < _n; _i++)
    {
        var _c = _cols[_i];
        var _x = _c.altura - _agua.nivel;
        _c.vel    += -_agua.tension * _x - _agua.amortiguacion * _c.vel;
        _c.altura += _c.vel;
    }

    // 2 · propagación: cada columna arrastra a sus vecinas.
    //     Los deltas se ACUMULAN aparte y se aplican después, para que la ola no
    //     viaje más rápido hacia un lado que hacia el otro.
    var _izq = array_create(_n, 0);
    var _der = array_create(_n, 0);

    repeat (_agua.pasadas)
    {
        for (var _i = 0; _i < _n; _i++)
        {
            if (_i > 0)
            {
                _izq[_i] = _agua.difusion * (_cols[_i].altura - _cols[_i - 1].altura);
                _cols[_i - 1].vel += _izq[_i];
            }
            if (_i < _n - 1)
            {
                _der[_i] = _agua.difusion * (_cols[_i].altura - _cols[_i + 1].altura);
                _cols[_i + 1].vel += _der[_i];
            }
        }
        for (var _i = 0; _i < _n; _i++)
        {
            if (_i > 0)      _cols[_i - 1].altura += _izq[_i];
            if (_i < _n - 1) _cols[_i + 1].altura += _der[_i];
        }
    }
}

/// @func agua_salpicar(_agua, _px, _fuerza)
/// @desc Mete velocidad en la columna más cercana a `_px`. Es TODO el splash:
///       la propagación se encarga de convertirlo en ondas.
function agua_salpicar(_agua, _px, _fuerza)
{
    var _n = array_length(_agua.columnas);
    var _i = clamp(round((_px - _agua.x0) / _agua.paso), 0, _n - 1);
    _agua.columnas[_i].vel += _fuerza;
}

/// @func agua_altura_en(_agua, _px)
/// @desc Altura interpolada de la superficie en una X cualquiera. Sirve para que
///       un barco se apoye en la ola y no en el nivel de reposo.
/// @returns {Real}
function agua_altura_en(_agua, _px)
{
    var _n = array_length(_agua.columnas);
    var _t = clamp((_px - _agua.x0) / _agua.paso, 0, _n - 1);
    var _i = floor(_t);
    var _j = min(_i + 1, _n - 1);
    return lerp(_agua.columnas[_i].altura, _agua.columnas[_j].altura, frac(_t));
}
```

### 9.1 Dibujarla: una tira de triángulos

```gml
/// @func agua_dibujar(_agua, _col_arriba, _col_abajo)
/// @desc El cuerpo del agua como tira de triángulos, con degradado vertical,
///       más una línea de espuma en la superficie.
function agua_dibujar(_agua, _col_arriba = c_aqua, _col_abajo = c_navy)
{
    var _n = array_length(_agua.columnas);

    draw_primitive_begin(pr_trianglestrip);
    for (var _i = 0; _i < _n; _i++)
    {
        var _px = _agua.x0 + _i * _agua.paso;
        var _py = _agua.columnas[_i].altura;
        draw_vertex_colour(_px, _py,                     _col_arriba, 0.65);
        draw_vertex_colour(_px, _py + _agua.profundidad, _col_abajo,  0.90);
    }
    draw_primitive_end();

    // cresta: la línea que hace que se lea como «superficie» y no como «mancha»
    for (var _i = 1; _i < _n; _i++)
    {
        var _ax = _agua.x0 + (_i - 1) * _agua.paso;
        var _bx = _agua.x0 + _i * _agua.paso;
        draw_line_width_colour(_ax, _agua.columnas[_i - 1].altura,
                               _bx, _agua.columnas[_i].altura, 2, c_white, c_white);
    }
}
```

### 9.2 El reflejo

El reflejo se dibuja con la **misma** tira de triángulos, pero texturizada con una superficie
que contiene la escena y con las UV **espejadas respecto a la línea de agua**. Al ondular la
superficie, el reflejo ondula con ella: es lo que lo hace creíble.

```gml
/// @func agua_dibujar_reflejo(_agua, _surf_escena, _alfa)
/// @desc Reflejo del mundo sobre el agua. `_surf_escena` debe contener la escena
///       dibujada en coordenadas de PANTALLA (una copia de la application surface,
///       o una surface propia del tamaño de la vista).
function agua_dibujar_reflejo(_agua, _surf_escena, _alfa = 0.35)
{
    if (!surface_exists(_surf_escena)) return;

    var _tex = surface_get_texture(_surf_escena);
    var _sw  = surface_get_width(_surf_escena);
    var _sh  = surface_get_height(_surf_escena);
    var _n   = array_length(_agua.columnas);

    draw_primitive_begin_texture(pr_trianglestrip, _tex);
    for (var _i = 0; _i < _n; _i++)
    {
        var _px = _agua.x0 + _i * _agua.paso;
        var _py = _agua.columnas[_i].altura;
        var _u  = _px / _sw;

        // el punto simétrico de (py + d) respecto a py es (py - d)
        var _v_sup = _py / _sh;
        var _v_fon = (_py - _agua.profundidad) / _sh;

        draw_vertex_texture_colour(_px, _py,                     _u, _v_sup, c_white, _alfa);
        draw_vertex_texture_colour(_px, _py + _agua.profundidad, _u, _v_fon, c_white, 0);
    }
    draw_primitive_end();
}
```

> 🔺 **Dos condiciones que hay que cumplir**, o el reflejo sale desplazado:
> 1. La surface debe estar en **coordenadas de pantalla**. Si la cámara se mueve, resta la
>    posición de la vista a `_px` antes de calcular `_u`, o dibuja el agua en Draw GUI.
> 2. Si `_py - profundidad` sale del rango 0..1, la textura se sale de la surface. Recorta la
>    profundidad del reflejo o activa la repetición del sampler. Las UV de
>    `draw_vertex_texture` cubren **la región del sprite dentro de la página de textura**; con
>    una *surface* eso es la surface entera, así que 0..1 es correcto. El matiz está en
>    [08 · 02](../08%20-%20Referencia%20GML%20completa/02%20-%20Dibujo%20de%20formas%20y%20primitivas.md).

---

## 10 · Fluido, nivel 2: autómata celular de líquido por celdas

Es el modelo de *Noita*, de *Powder Game* y de todos los *falling sand*: el mundo es una
rejilla y cada celda guarda **cuánta masa de líquido tiene**, no un simple sí/no. Con masa
continua salen gratis la presión, el nivel que se iguala y los vasos comunicantes.

Las reglas, por celda y en este orden (formulación de W-Shadow, popularizada por jgallant):

1. **Abajo**: cede a la celda inferior hasta dejarla en su *estado estable*.
2. **Izquierda** y **derecha**: reparte el sobrante para igualar con los lados.
3. **Arriba**: solo si la celda está **comprimida** (masa > 1), empuja hacia arriba.

```gml
/// scr_liquido — autómata celular de líquido con masa y compresión

#macro MASA_MAX       1.0      // masa "normal" de una celda llena, sin presión
#macro MASA_COMPRESION 0.02    // masa extra que admite por cada celda que tiene encima
#macro MASA_MINIMA    0.0001   // por debajo de esto la celda se considera seca
#macro FLUJO_MAX      1.0      // caudal máximo por celda y paso: frena las cascadas

/// @func estado_estable(_masa_total)
/// @desc Cuánta masa debe quedarse la celda de ABAJO cuando dos celdas verticales
///       suman `_masa_total`. Es lo que produce la presión: la de abajo se queda
///       con más de 1 y el exceso empuja hacia arriba.
/// @returns {Real}
function estado_estable(_masa_total)
{
    if (_masa_total <= 1) return 1;
    if (_masa_total < 2 * MASA_MAX + MASA_COMPRESION)
        return (sqr(MASA_MAX) + _masa_total * MASA_COMPRESION) / (MASA_MAX + MASA_COMPRESION);
    return (_masa_total + MASA_COMPRESION) / 2;
}

/// @func liquido_nuevo(_ancho, _alto)
/// @desc Rejilla de masa + rejilla de sólidos. Se usa doble buffer: se lee de
///       `masa` y se escribe en `nueva`, y al final se intercambian.
/// @returns {Struct}
function liquido_nuevo(_ancho, _alto)
{
    var _masa = [], _nueva = [], _solido = [];
    for (var _j = 0; _j < _alto; _j++)
    {
        array_push(_masa,   array_create(_ancho, 0));
        array_push(_nueva,  array_create(_ancho, 0));
        array_push(_solido, array_create(_ancho, false));
    }
    return { ancho : _ancho, alto : _alto, masa : _masa, nueva : _nueva, solido : _solido };
}

/// @func liquido_actualizar(_g)
/// @desc Un paso de simulación completo sobre toda la rejilla.
function liquido_actualizar(_g)
{
    var _w = _g.ancho, _h = _g.alto;
    var _m = _g.masa,  _n = _g.nueva, _s = _g.solido;

    // partimos de una copia: los flujos se suman y restan sobre ella
    for (var _j = 0; _j < _h; _j++)
        for (var _i = 0; _i < _w; _i++)
            _n[_j][_i] = _m[_j][_i];

    for (var _j = 0; _j < _h; _j++)
    {
        for (var _i = 0; _i < _w; _i++)
        {
            if (_s[_j][_i]) { _n[_j][_i] = 0; continue; }

            var _restante = _m[_j][_i];
            if (_restante < MASA_MINIMA) { _n[_j][_i] = 0; continue; }

            var _flujo = 0;

            // 1 · ABAJO
            if (_j < _h - 1 && !_s[_j + 1][_i])
            {
                _flujo = estado_estable(_restante + _m[_j + 1][_i]) - _m[_j + 1][_i];
                if (_flujo > MASA_MINIMA) _flujo *= 0.5;   // amortigua: evita el parpadeo
                _flujo = clamp(_flujo, 0, min(FLUJO_MAX, _restante));
                _n[_j][_i]     -= _flujo;
                _n[_j + 1][_i] += _flujo;
                _restante      -= _flujo;
            }
            if (_restante < MASA_MINIMA) { _n[_j][_i] -= _restante; continue; }

            // 2 · IZQUIERDA
            if (_i > 0 && !_s[_j][_i - 1])
            {
                _flujo = (_m[_j][_i] - _m[_j][_i - 1]) / 4;
                if (_flujo > MASA_MINIMA) _flujo *= 0.5;
                _flujo = clamp(_flujo, 0, _restante);
                _n[_j][_i]     -= _flujo;
                _n[_j][_i - 1] += _flujo;
                _restante      -= _flujo;
            }
            if (_restante < MASA_MINIMA) { _n[_j][_i] -= _restante; continue; }

            // 3 · DERECHA
            if (_i < _w - 1 && !_s[_j][_i + 1])
            {
                _flujo = (_m[_j][_i] - _m[_j][_i + 1]) / 4;
                if (_flujo > MASA_MINIMA) _flujo *= 0.5;
                _flujo = clamp(_flujo, 0, _restante);
                _n[_j][_i]     -= _flujo;
                _n[_j][_i + 1] += _flujo;
                _restante      -= _flujo;
            }
            if (_restante < MASA_MINIMA) { _n[_j][_i] -= _restante; continue; }

            // 4 · ARRIBA (solo el exceso comprimido)
            if (_j > 0 && !_s[_j - 1][_i])
            {
                _flujo = _restante - estado_estable(_restante + _m[_j - 1][_i]);
                if (_flujo > MASA_MINIMA) _flujo *= 0.5;
                _flujo = clamp(_flujo, 0, min(FLUJO_MAX, _restante));
                _n[_j][_i]     -= _flujo;
                _n[_j - 1][_i] += _flujo;
            }
        }
    }

    // intercambio de buffers: sin copiar arrays, solo dos referencias
    _g.masa  = _n;
    _g.nueva = _m;
}
```

### 10.1 Dibujarlo sin morir en el intento

**Nunca** dibujes una celda por `draw_rectangle` cada frame: una rejilla de 200 × 120 son
24 000 llamadas de dibujo por frame y el juego se cae solo. Las dos vías buenas:

**a) Buffer → superficie de 1 píxel por celda, escalada.** Es la más rápida y la que escala a
rejillas grandes.

```gml
/// @func liquido_dibujar(_g, _surf, _buf, _px, _py, _escala)
/// @desc Escribe la rejilla en un buffer RGBA, la vuelca a una superficie del
///       tamaño exacto de la rejilla y la dibuja escalada.
function liquido_dibujar(_g, _surf, _buf, _px, _py, _escala = 4)
{
    buffer_seek(_buf, buffer_seek_start, 0);

    for (var _j = 0; _j < _g.alto; _j++)
    {
        for (var _i = 0; _i < _g.ancho; _i++)
        {
            var _m = _g.masa[_j][_i];
            if (_m > 0.01)
            {
                // más masa = más opaco y más oscuro: se lee la profundidad
                var _a = floor(clamp(_m, 0.35, 1) * 255);
                buffer_write(_buf, buffer_u8,  40);                       // R
                buffer_write(_buf, buffer_u8, floor(170 - _m * 60));      // G
                buffer_write(_buf, buffer_u8, 235);                       // B
                buffer_write(_buf, buffer_u8, _a);                        // A
            }
            else
            {
                repeat (4) buffer_write(_buf, buffer_u8, 0);
            }
        }
    }

    buffer_set_surface(_buf, _surf, 0);

    gpu_set_texfilter(false);            // sin interpolación: celdas nítidas
    draw_surface_ext(_surf, _px, _py, _escala, _escala, 0, c_white, 1);
}
```

```gml
/// obj_liquido · Create
rejilla = liquido_nuevo(160, 90);
surf    = surface_create(160, 90);
buf     = buffer_create(160 * 90 * 4, buffer_fixed, 1);

/// obj_liquido · Clean Up — obligatorio: ni surfaces ni buffers se liberan solos
if (surface_exists(surf)) surface_free(surf);
buffer_delete(buf);
```

> ⚠️ **El orden de los bytes es RGBA en Windows, pero el manual advierte de que «en otros
> objetivos puede ser diferente dependiendo del SO o incluso del dispositivo»** (página de
> `buffer_get_surface`). Si el agua sale naranja en macOS o en Android, es esto: escribe una
> celda de prueba de color conocido y comprueba el orden en cada plataforma antes de dar el
> pipeline por bueno.
>
> 🔺 **Las surfaces se pierden.** Al minimizar la ventana, cambiar de resolución o volver de
> suspensión, el sistema puede liberarlas. Comprueba `surface_exists()` en el Draw y recréala
> si hace falta. Detalle en
> [08 · 05 — Superficies](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md).

**b) Superficie sucia.** Si el líquido casi no cambia (un depósito quieto), dibuja con
`draw_rectangle` **dentro de una surface** y solo la redibuja cuando algo se mueva. Cambias
24 000 llamadas por frame por 24 000 cada vez que alguien rompe una pared.

### 10.2 Cuánto aguanta

El coste es **`ancho × alto` iteraciones por paso**, con aritmética de coma flotante y accesos
a arrays anidados. Órdenes de magnitud, medidos con `get_timer()` (§14):

| Rejilla | Celdas | Uso típico |
|---|---:|---|
| 80 × 45 | 3 600 | Un charco, un depósito, un puzzle de una pantalla |
| 160 × 90 | 14 400 | Una sala entera a 4 px por celda: el punto dulce |
| 320 × 180 | 57 600 | ⚠️ Solo con YYC y simulando 1 de cada 2 frames |
| 640 × 360 | 230 400 | ⚠️ No en GML puro. Es territorio de compute shader |

Dos trucos que multiplican el techo:

- **Simular por regiones.** Solo las celdas cerca del jugador o marcadas como «activas».
  *Noita* divide el mundo en **fragmentos de 64 × 64** y solo simula los que tienen algo que
  hacer (charla de GDC 2019, fuentes). Es la optimización que convierte «una pantalla» en «un
  mundo».
- **Simular a mitad de ritmo.** Un paso cada dos frames es imperceptible en agua y libera la
  mitad del presupuesto.

---

## 11 · Fluido, nivel 3: partículas, Box2D y shaders

### 11.1 SPH en cinco líneas

**Smoothed Particle Hydrodynamics** (Müller, Charypar y Gross, SCA 2003) es el método de
partículas estándar:

1. El fluido son N partículas con masa, posición y velocidad; no hay rejilla.
2. La **densidad** en cada partícula se estima sumando la masa de las vecinas, ponderada por
   un núcleo `W(r, h)` que decae con la distancia.
3. De la densidad sale la **presión** con una ecuación de estado (`p = k·(ρ − ρ₀)`).
4. Cada partícula recibe tres fuerzas: presión (gradiente del núcleo), viscosidad (laplaciano
   del núcleo) y gravedad.
5. Se integra y se repite. **El coste está en encontrar las vecinas**, y por eso hace falta
   una rejilla espacial de aceleración.

### 11.2 Por qué no en GML puro

Cada partícula recorre sus vecinas dos veces por paso (una para la densidad, otra para las
fuerzas) y evalúa polinomios con raíces cuadradas. Aun con rejilla espacial, son decenas de
operaciones de coma flotante por pareja de partículas, **dentro del Step**. En la VM eso
significa unos **cientos** de partículas antes de que el Step se coma el frame; con YYC, un
factor de 2-3 más ([01 · 15 §6](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)).
⚠️ Cifra orientativa: mídela con `get_timer()` en tu máquina antes de diseñar alrededor de
ella.

**Las tres salidas reales, de menor a mayor esfuerzo:**

| Si quieres… | Usa |
|---|---|
| Fluido que interactúa con cuerpos rígidos, sin escribir el solver | `physics_particle_*` de Box2D: [04 · 22 §6](../04%20-%20Recetas%20por%20género/22%20-%20Físicas%20con%20Box2D.md) |
| Un charco o un río que se comporta como líquido | El autómata celular del §10 |
| Que *parezca* agua sin simular nada | Un shader de distorsión sobre la escena (§11.3) |

### 11.3 Agua por shader: distorsión con una textura de ruido

La ilusión más barata y la que mejor resultado da por línea escrita. El fragment shader
desplaza la coordenada de muestreo según dos capas de ruido que se mueven en direcciones
distintas: como no se repiten en fase, el patrón nunca se ve.

```glsl
// sh_agua.fsh — GLSL ES 1.0 (funciona en todas las plataformas)
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform float     u_tiempo;   // segundos
uniform vec2      u_fuerza;   // amplitud de la distorsión, en unidades de UV
uniform sampler2D u_ruido;    // textura de ruido en escala de grises, repetible

void main()
{
    // dos muestras del mismo ruido a escalas y velocidades distintas
    vec2 uv1 = v_vTexcoord * 3.0 + vec2( u_tiempo * 0.05, u_tiempo * 0.03);
    vec2 uv2 = v_vTexcoord * 5.0 + vec2(-u_tiempo * 0.04, u_tiempo * 0.07);

    float n1 = texture2D(u_ruido, uv1).r - 0.5;
    float n2 = texture2D(u_ruido, uv2).r - 0.5;

    vec2 desplaz = vec2(n1 + n2, n1 - n2) * u_fuerza;

    gl_FragColor = v_vColour * texture2D(gm_BaseTexture, v_vTexcoord + desplaz);
}
```

```gml
/// obj_agua · Create — los handles se piden UNA vez, nunca en el Draw
u_tiempo = shader_get_uniform(sh_agua, "u_tiempo");
u_fuerza = shader_get_uniform(sh_agua, "u_fuerza");
s_ruido  = shader_get_sampler_index(sh_agua, "u_ruido");

/// obj_agua · Draw — aplicar la distorsión a la escena ya dibujada
if (shaders_are_supported() && shader_is_compiled(sh_agua))
{
    shader_set(sh_agua);
    shader_set_uniform_f(u_tiempo, current_time / 1000);
    shader_set_uniform_f(u_fuerza, 0.008, 0.004);   // más en X que en Y: se lee como agua
    texture_set_stage(s_ruido, sprite_get_texture(spr_ruido, 0));
    gpu_set_texrepeat_ext(s_ruido, true);           // el ruido tiene que repetirse
    draw_surface(surf_escena, 0, 0);
    shader_reset();
}
```

> 🔺 **La trampa del ruido en una página de textura compartida.** `sprite_get_texture()`
> devuelve la página entera, y el sprite es solo una región de ella: al pedir UV fuera de
> 0..1 con `gpu_set_texrepeat_ext(..., true)` **repites la página, no el sprite**, y aparecen
> trozos de otros sprites. Marca `spr_ruido` como **Separate Texture Page** en su Inspector.
> Toda la anatomía de un shader de GameMaker (uniforms integrados, matrices, plataformas) está
> en [08 · 06](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md).

---

## 12 · Metaballs: agua y limo estilizados

Los *metaballs* («blobs») son la técnica para que varias gotas se fundan en una sola masa al
acercarse. La idea: **dibujar círculos de alfa degradado que se suman, y luego cortar por un
umbral**. Donde la suma pasa del umbral hay masa; donde no, no hay nada.

```gml
/// @func blobs_dibujar(_surf, _gotas, _umbral, _col)
/// @desc Dibuja una lista de gotas fundidas entre sí.
/// @param {Id.Surface} _surf    Superficie de trabajo del tamaño de la vista.
/// @param {Array} _gotas        Structs { px, py, radio }.
/// @param {Real}  _umbral       0..255. Más alto = las gotas se funden más tarde.
function blobs_dibujar(_surf, _gotas, _umbral = 140, _col = c_lime)
{
    var _n = array_length(_gotas);

    // 1 · acumular el alfa de todas las gotas en la superficie
    surface_set_target(_surf);
    draw_clear_alpha(c_black, 0);
    gpu_set_blendmode_ext(bm_one, bm_one);        // suma pura: también suma el alfa

    for (var _i = 0; _i < _n; _i++)
    {
        var _g = _gotas[_i];
        // spr_blob: un círculo blanco con el alfa cayendo del centro al borde
        var _e = (_g.radio * 2) / sprite_get_width(spr_blob);
        draw_sprite_ext(spr_blob, 0, _g.px, _g.py, _e, _e, 0, _col, 1);
    }

    gpu_set_blendmode(bm_normal);
    surface_reset_target();

    // 2 · dibujarla con corte de alfa: solo sobrevive lo que superó el umbral
    gpu_set_alphatestenable(true);
    gpu_set_alphatestref(_umbral);
    draw_surface(_surf, 0, 0);
    gpu_set_alphatestref(0);
    gpu_set_alphatestenable(false);
}
```

- **`spr_blob`** es el único asset que hace falta: un círculo blanco de 64 × 64 con el alfa
  degradado del centro (255) al borde (0). Se dibuja en cualquier editor en dos minutos.
- **El umbral es el mando de viscosidad.** Bajo (≈ 60): las gotas se funden de lejos, aspecto
  de limo. Alto (≈ 200): apenas se tocan, aspecto de agua.
- **El borde sale duro y con escalones.** Eso es lo que da el aspecto de dibujo animado. Si lo
  quieres suave, sustituye el corte de alfa por un fragment shader que haga `smoothstep` sobre
  el alfa acumulado.

> ⚠️ **`gpu_set_alphatestenable()` «puede afectar negativamente al rendimiento de los
> dispositivos iOS y Android»**, según el manual. En móvil, mide antes de comprometerte con
> esta técnica; la alternativa por shader suele salir más barata porque no rompe el batch.
>
> 🔺 **Devuelve siempre el estado.** `gpu_set_alphatestref(0)` y
> `gpu_set_alphatestenable(false)` al terminar: si te los dejas puestos, el resto del juego se
> dibuja con recorte de alfa y los sprites con bordes suaves salen dentados.
>
> 🔗 **Alternativa vectorial: marching squares.** Si el escalón del corte de alfa no te vale
> (necesitas el contorno como polilínea, no solo un dibujo recortado — por ejemplo para chocar
> contra él, o para dibujarlo con un grosor de línea propio), la técnica está en
> [13 · 07 §3 ter](./07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md#3-ter--marching-squares-contornos-suaves):
> recorre el mismo campo de alfa acumulado con `marching_squares_lista()` en vez de recortarlo.
> Más caro de calcular, sin dentado y con un contorno que puedes usar para algo más que dibujar.
> No dupliques el acumulado: sigue siendo `blobs_dibujar()` quien lo genera.

---

## 13 · Viento, hierba y ambiente

No todo movimiento necesita simulación. Una función de desplazamiento basta para hierba,
antorchas, ramas, telas de fondo y cualquier cosa que solo tenga que **estar viva**.

```gml
/// @func ruido_valor(_n)
/// @desc Ruido pseudoaleatorio determinista y continuo por interpolación.
///       No es Perlin, pero para viento y ambiente sobra — y no depende del
///       estado del generador de números aleatorios del juego.
/// @returns {Real} 0..1
function ruido_valor(_n)
{
    var _i = floor(_n);
    var _f = frac(_n);
    var _a = frac(sin(_i       * 12.9898) * 43758.5453);
    var _b = frac(sin((_i + 1) * 12.9898) * 43758.5453);
    var _s = _f * _f * (3 - 2 * _f);          // suavizado tipo smoothstep
    return lerp(_a, _b, _s);
}

/// @func viento_offset(_px, _tiempo, _amplitud, _rafaga)
/// @desc Desplazamiento horizontal del viento en la posición `_px`.
///       Suma una brisa base (seno) y ráfagas irregulares (ruido).
/// @returns {Real}
function viento_offset(_px, _tiempo, _amplitud = 3, _rafaga = 2)
{
    var _brisa   = dsin(_tiempo * 60 + _px * 1.5) * _amplitud;
    var _rafagas = (ruido_valor(_tiempo * 0.4 + _px * 0.01) - 0.5) * 2 * _rafaga;
    return _brisa + _rafagas;
}
```

```gml
/// obj_hierba · Draw — una brizna que se dobla desde la base
var _t = current_time / 1000;
var _d = viento_offset(x * 0.05, _t, 3, 2.5);

// la punta se desplaza; la base no se mueve: eso es lo que se lee como «doblarse»
draw_primitive_begin(pr_trianglestrip);
draw_vertex_colour(x - 2,      y,      c_green, 1);
draw_vertex_colour(x + 2,      y,      c_green, 1);
draw_vertex_colour(x - 1 + _d, y - 14, c_lime,  1);
draw_vertex_colour(x + 1 + _d, y - 14, c_lime,  1);
draw_primitive_end();
```

> 💡 **Desincroniza siempre.** Si todas las briznas usan el mismo `_t`, la pradera se mueve
> como un solo bloque y el efecto se rompe. Pasar `x` a la función (como arriba) las desfasa
> por posición gratis. Es la misma idea que el argumento `_offset` de
> [`wave()`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml).
>
> 📘 Para ruido de verdad —Perlin, simplex, octavas, mapas de altura— el sitio es el documento
> [**07 — Generación procedural avanzada**](./07%20-%20Generación%20procedural%20avanzada.md), dedicado a la generación procedural.

---

## 14 · Rendimiento: medir antes de decidir

Todo lo de este documento corre en el **Step**, dentro de la VM. Antes de subir el número de
partículas o el tamaño de la rejilla, mide.

```gml
/// obj_fisica · Step — cuánto cuesta de verdad cada sistema, en microsegundos
var _t0 = get_timer();
verlet_integrar(cuerda.puntos, 0.45, 0.995);
verlet_relajar(cuerda.varillas, 6);
coste_verlet = get_timer() - _t0;

var _t1 = get_timer();
liquido_actualizar(rejilla);
coste_liquido = get_timer() - _t1;

/// obj_fisica · Draw GUI
draw_text(8, 8, $"Verlet: {coste_verlet} µs · Líquido: {coste_liquido} µs");
```

**La referencia que importa:** a 60 fps hay **16 666 µs** por frame para *todo* —lógica,
dibujo, audio y sistema—. Un sistema de física que se lleve más de 3 000 µs (un 18 %) ya es el
protagonista del presupuesto.

Para saber si el cuello está en el `Step` o en el `Draw`, el **Debug Overlay** con la ventana
FPS en modo *Stacked* lo separa por categorías: eso y el resto del método está en
[01 · 15 §6](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md).

⚠️ **Órdenes de magnitud, no promesas.** Las cifras siguientes son estimaciones basadas en el
coste relativo de cada bucle, **no mediciones**: mídelas en tu máquina con el fragmento de
arriba antes de diseñar alrededor de ellas.

| Sistema | VM (orientativo) | YYC (orientativo) | Qué lo limita |
|---|---|---|---|
| Puntos Verlet + varillas | ~1 000 puntos con 5 iteraciones | ~3 000 | El bucle de relajación: coste = puntos × iteraciones |
| Columnas de agua (§9) | ~200 columnas × 8 pasadas | ~600 | Las pasadas de propagación |
| Celdas de líquido (§10) | ~15 000 celdas | ~50 000 | Accesos a arrays anidados |
| Partículas SPH (§11.1) | unos cientos | ~1 000 | La búsqueda de vecinas |
| Entidades en spatial hash (§4) | ~2 000 chocando entre sí | ~6 000 | Reconstruir la rejilla y recorrer vecinos |

**Las tres optimizaciones que de verdad mueven la aguja**, por orden de rentabilidad:

1. **Simular menos.** Regiones activas, un paso cada dos frames, congelar lo que está fuera de
   la cámara. Ganancia: ×2 a ×10.
2. **YYC.** El código de física es aritmética pura en bucles cerrados, justo donde el YYC
   rinde ×2-×3. Sobre el dibujado no hace nada.
3. **Bajar iteraciones antes que bajar entidades.** Una cuerda de 40 puntos con 3 iteraciones
   se ve mejor que una de 15 con 10.

Lo que **no** funciona: microoptimizar la aritmética dentro del bucle. Si el bucle se ejecuta
50 000 veces, el problema es el 50 000, no la multiplicación.

---

## 15 · Checklist

```
INTEGRACIÓN
[ ] ¿Actualizo la velocidad ANTES de la posición? (semi-implícito, §1.2)
[ ] ¿La fricción multiplicativa está corregida por dt (power) o el juego va a paso fijo?
[ ] Si uso el acumulador: ¿tiene techo (0,25 s) contra la espiral de la muerte?

SALTO Y PROYECTILES
[ ] ¿La gravedad sale de la altura y el tiempo deseados, o la he adivinado?
[ ] ¿La gravedad de caída es mayor que la de subida?
[ ] ¿El arco dibujado usa la MISMA gravedad que el proyectil real?

COLISIONES
[ ] ¿He probado antes move_and_collide() con más iteraciones?
[ ] Con más de ~50 entidades chocando entre sí: ¿hay spatial hash, o sigo en O(N²)?
[ ] ¿La celda de la rejilla mide ~1,5-2× el diámetro mayor?
[ ] ¿Reconstruyo la rejilla cada frame con array_resize(a, 0), no con `= []`?
[ ] ¿Destruyo las ds_list que creo para collision_*_list()?
[ ] ¿Separo el solapamiento por el eje de menor penetración, no por los dos?
[ ] ¿El rebote comprueba que el objeto se acerca (dot < 0) antes de reflejar?
[ ] ¿Hay umbral de reposo para que no tiemble eternamente?

MUELLES Y VERLET
[ ] ¿√rigidez · dt < 1, o hay sub-pasos?
[ ] ¿El orden es integrar → relajar → colisionar?
[ ] ¿El roce de Verlet es < 1? (con 1 exacto, la energía nunca se disipa)

FLUIDOS
[ ] ¿El agua de muelles acumula los deltas aparte y los aplica después?
[ ] ¿La rejilla de líquido usa doble buffer?
[ ] ¿Dibujo la rejilla con buffer→surface, y no con miles de draw_rectangle?
[ ] ¿Compruebo surface_exists() antes de usar cualquier surface?
[ ] ¿Libero surfaces y buffers en el Clean Up?

RENDIMIENTO
[ ] ¿He medido con get_timer() antes de subir números?
[ ] ¿El coste total de física se queda por debajo del 20 % del frame?
[ ] ¿He probado YYC si el cuello está en el Step?
```

---

## 16 · Errores clásicos y cómo evitarlos

| Error | Qué se ve | Arreglo |
|---|---|---|
| Integrar con Euler explícito | El muelle oscila cada vez más hasta reventar | Velocidad antes que posición (§1.2) |
| `vel *= 0.9` sin corregir por `dt` | El personaje frena distinto según los FPS | `power(0.9, _dt * 60)` o paso fijo |
| Colisionar después de mover, sin separar | El personaje se queda clavado dentro de la pared | `separacion_minima()` tras detectar (§3.2) |
| Comparar todas las entidades contra todas | A partir de 200 el Step se come el frame | Spatial hash (§4) |
| Vaciar la rejilla con `cubo = []` cada frame | El recolector de basura sube y el juego da tirones | `array_resize(cubo, 0)` (§4.1) |
| `collision_*_list()` con `prec = true` por defecto | Mucho más lento sin necesitarlo | `false` salvo que exijas precisión de píxel |
| Muelle rígido con `dt` grande | Vibra, se dispara o se va al infinito | Sub-pasos, o baja la rigidez |
| Rebotar sin comprobar el signo del producto escalar | El objeto sale disparado al tocar el suelo | `if (dot > 0) return` (§7.1) |
| Verlet con roce exactamente 1 | La cuerda no se para nunca, «respira» | Roce 0,98–0,995 |
| Relajar antes de integrar | La cuerda va un frame por detrás y se estira | Integrar → relajar → colisionar |
| Aplicar los deltas del agua dentro del mismo bucle | La ola viaja más rápido hacia un lado | Acumular en `_izq`/`_der` y aplicar después (§9) |
| Simular el líquido sobre la misma rejilla que se lee | Cascadas imposibles: el agua «cae» varias celdas por paso | Doble buffer (§10) |
| `draw_rectangle` por celda | 5 fps con una rejilla mediana | Buffer → surface (§10.1) |
| Dejar el test de alfa activado | Todo el juego sale con bordes dentados | Reponer el estado tras `blobs_dibujar()` |
| No liberar surfaces ni buffers | La memoria sube hasta que el juego cae | `surface_free()` y `buffer_delete()` en Clean Up |
| Mezclar `physics_*` con `x`/`y` propias | Tembleques y saltos imposibles de depurar | Un objeto es de física **o** es tuyo ([04 · 22](../04%20-%20Recetas%20por%20género/22%20-%20Físicas%20con%20Box2D.md)) |
| Usar `if (rectangle_in_rectangle(...))` esperando «dentro» | Da `true` también cuando solo se rozan | Comparar `== 1` (devuelve 0/1/2) |

---

## Ver también

- [04 · 22 — Físicas con Box2D](../04%20-%20Recetas%20por%20género/22%20-%20Físicas%20con%20Box2D.md) — la otra mitad: cuándo sí conviene el motor, joints y `physics_particle_*`
- [04 · 01 — Plataformas 2D](../04%20-%20Recetas%20por%20género/01%20-%20Plataformas%202D.md) — el tacto del salto ya resuelto: coyote time, buffer, salto variable
- [04 · 12 — Carreras y vehículos](../04%20-%20Recetas%20por%20género/12%20-%20Carreras%20y%20vehículos.md) — física arcade de coche: agarre lateral y deriva
- [01 · 08 — Movimiento y colisiones](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) — `move_and_collide()`, máscaras, bounding boxes
- [01 · 06 — Eventos y ciclo del juego](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) §7 — `delta_time`, `game_set_speed`, Time Sources
- [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md) §6 — Debug Overlay, VM frente a YYC
- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) — partículas, screen shake, hit stop
- [08 · 02 — Dibujo de formas y primitivas](../08%20-%20Referencia%20GML%20completa/02%20-%20Dibujo%20de%20formas%20y%20primitivas.md) — `draw_primitive_*`, `draw_vertex_*`, tipos de primitiva
- [08 · 05 — Superficies](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md) — surfaces, formatos y por qué se pierden
- [08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md) — GLSL ES 1.0, uniforms, samplers
- [08 · 11 — Vectores, matrices y ángulos](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores,%20matrices%20y%20ángulos.md) — el sistema de coordenadas, `lengthdir_*`, `dot_product`
- [06 · scr_math_util.gml](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml) — `approach`, `wave`, `remap`, `lerp_dt`, `smoothstep`, easings
- [11 · Catálogo del código descargado](../11%20-%20Código%20descargado/_CATALOGO.md) — sección «Física y colisiones»: Bonk, Loj-Hadron-Collider, Fracture, GMVerlet-Integration; y quadtrees reales en BBMOD y DS-3DCollisions
- [13 · 07 — Generación procedural avanzada](./07%20-%20Generación%20procedural%20avanzada.md) — generación procedural y ruido (Perlin, octavas, mapas)

---

## Fuentes

Consultadas el **6 de septiembre de 2026**:

- **Glenn Fiedler — «Integration Basics»**, gafferongames.com.
  <https://gafferongames.com/post/integration_basics/>
  Demostración numérica de por qué Euler explícito gana energía en sistemas oscilantes y por
  qué el semi-implícito («simpléctico») es el estándar en juegos pese a ser de primer orden.
- **Glenn Fiedler — «Fix Your Timestep!»**, gafferongames.com.
  <https://gafferongames.com/post/fix_your_timestep/>
  El acumulador de tiempo, el techo contra la «espiral de la muerte» y la interpolación del
  estado para dibujar. Origen del §1.3.
- **Thomas Jakobsen — «Advanced Character Physics»**, GDC 2001 (IO Interactive).
  <https://www.cs.cmu.edu/afs/cs/academic/class/15462-s13/www/lec_slides/Jakobsen.pdf>
  Integración de Verlet (`x' = 2x − x_ant + a·dt²`), restricciones de distancia por relajación
  iterativa, colisión por proyección y ragdolls a partir de varillas. Base de todo el §6.
- **Michael Hoffman — «Make a Splash With Dynamic 2D Water Effects»**, Envato Tuts+.
  <https://code.tutsplus.com/make-a-splash-with-dynamic-2d-water-effects--gamedev-236t>
  La superficie como fila de muelles, la propagación con deltas izquierda/derecha y las
  constantes de referencia (k = 0,025, amortiguación 0,025, difusión 0–0,5, 8 pasadas).
  Base del §9.
- **W-Shadow — «Simple Fluid Simulation With Cellular Automata»** (2009).
  <https://w-shadow.com/blog/2009/09/01/simple-fluid-simulation/>
  El modelo de masa con compresión: `MaxMass`, `MaxCompress`, `MinMass` y la función
  `get_stable_state_b()`. Base del §10.
- **Jon Gallant — «2D Liquid Simulator With Cellular Automaton in Unity»** (2017).
  <https://www.jgallant.com/2d-liquid-simulator-with-cellular-automaton-in-unity/>
  La versión práctica del mismo modelo, con el orden de reglas abajo → lados → arriba.
- **Petri Purho — «Exploring the Tech and Design of *Noita*»**, GDC 2019.
  <https://www.gdcvault.com/play/1025695/Exploring-the-Tech-and-Design>
  (vídeo libre: <https://www.youtube.com/watch?v=prXuyMCgbTc>)
  Cómo escalar un *falling sand* a un mundo continuo: fragmentos de 64 × 64 y simulación solo
  de los activos.
- **M. Müller, D. Charypar, M. Gross — «Particle-Based Fluid Simulation for Interactive
  Applications»**, Symposium on Computer Animation (SCA) 2003.
  <https://matthias-research.github.io/pages/publications/sca03.pdf>
  El artículo fundacional de SPH en tiempo real. Referencia del §11.1.
- **Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/`):
  páginas de `buffer_get_surface` (orden de bytes RGBA y su advertencia por plataforma),
  `buffer_set_surface`, `gpu_set_alphatestref` y `gpu_set_alphatestenable` (umbral 0–255 y
  aviso de rendimiento en iOS/Android), `rectangle_in_rectangle` (devuelve 0/1/2),
  `point_in_circle`, `get_timer` (microsegundos) y `draw_primitive_begin`.
