# 13 · Matemáticas aplicadas al juego

> Las matemáticas que un desarrollador usa **a diario**, ordenadas por el problema que
> resuelven —«¿está detrás de mí?», «¿por qué mi suavizado va distinto a 144 fps?», «¿cuánta
> XP pido en el nivel 10?»— y no por el nombre de la función.
>
> **Esto no es una referencia de funciones.** Las fichas (firma, argumentos, retorno) están en
> [08 · 10 — Matemáticas y números](../08%20-%20Referencia%20GML%20completa/10%20-%20Matem%C3%A1ticas.md)
> y [08 · 11 — Vectores, matrices y ángulos](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores%2C%20matrices%20y%20%C3%A1ngulos.md).
> Las utilidades ya escritas y probadas están en
> [`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml). Aquí se explica
> **cuándo** usarlas, **por qué** funcionan y **qué pasa cuando se usan mal**.

**Versión de referencia:** GameMaker LTS 2026.0 · IDE `2026.0.0.16` · runtime `2026.0.0.23`.
Todos los símbolos de GML de este documento están verificados con `_indice/buscar.py`.

---

## 0 · Mapa: del problema a la sección

| Lo que tienes delante | Vas a §|
|---|---|
| «¿El enemigo está delante o detrás de mí?» · «¿lo tengo en el cono de visión?» | [2](#2--vectores-en-la-práctica) |
| «¿La pared queda a mi izquierda o a mi derecha?» | [2.5](#25--producto-cruzado-2d-a-qué-lado-está) |
| «La bala tiene que rebotar en la pared» | [2.7](#27--reflexión-rebotar-contra-una-pared) |
| «La torreta gira dando la vuelta larga al pasar por 0°» | [3.1](#31--angle_difference-la-diferencia-mínima-entre-dos-ángulos) |
| «Mi cámara suave va distinto a 30 y a 144 fps» | [4.2](#42--el-lerp-exponencial-y-por-qué-el-tuyo-está-roto) |
| «Quiero una trayectoria curva para un objeto que vuela al HUD» | [4.6](#46--bézier-cuadrática-y-cúbica) |
| «Quiero una ruta suave que **pase por** unos puntos que he puesto a mano» | [4.7](#47--catmull-rom-pasar-por-los-puntos) |
| «Salen cinco espadas seguidas y el jugador cree que está roto» | [5.5](#55--bolsa-aleatoria-shuffle-bag) · [5.6](#56--aleatorio-con-memoria-evitar-rachas-sin-quitar-el-azar) |
| «El crítico del 15 % no ha salido en 20 golpes» | [5.7](#57--crítico-con-piedad-pity) |
| «Necesito saber si un punto está dentro de este polígono raro» | [6.3](#63--punto-en-polígono-ray-casting-par-impar) |
| «¿Se cruzan estos dos segmentos?» · «¿el láser toca el círculo?» | [6.5](#65--intersección-segmento-segmento) · [6.6](#66--segmento-contra-círculo) |
| «¿A qué distancia estoy del `path`?» · «¿este disparo cruza una curva?» | [6.9](#69--colisión-contra-paths-y-curvas) |
| «Mundo ↔ celda» · «isométrico» · «hexágonos» | [7](#7--rejillas-y-coordenadas) |
| «¿Cuánta XP pido en el nivel 10? ¿Cuánto cuesta la mejora 5?» | [8](#8--curvas-de-crecimiento-para-diseño) |
| «Órbitas, espirales, misiles teledirigidos» | [9](#9--trigonometría-útil) |
| «Rotar un grupo de sprites como si fuera uno solo» | [10](#10--matrices-y-transformaciones-en-2d) |
| «`if (a == b)` no entra nunca y no entiendo por qué» | [11](#11--precisión-numérica) |
| «Frames, segundos, `delta_time` y temporizadores» | [12](#12--tiempo) |

---

## 1 · El sistema de coordenadas, y las tres trampas que esconde

### 1.1 · Y hacia abajo, ángulos antihorario

GameMaker mezcla dos convenciones que en matemáticas no van juntas:

- **X** crece a la **derecha** y **Y** crece hacia **abajo** (convención de pantalla).
- Los **ángulos** crecen en sentido **antihorario en pantalla**: `0` = derecha, `90` = **arriba**,
  `180` = izquierda, `270` = abajo. Están en **grados**, no en radianes.

Eso significa que el motor ya te ha hecho la conversión: `lengthdir_y(1, 90)` devuelve `-1`,
porque «arriba» en pantalla es Y negativa. Toda la familia `point_direction`, `lengthdir_*`,
`dsin`, `dcos`, `image_angle` y `direction` comparte esa convención y es **coherente entre sí**.

Las tres trampas que salen de ahí:

| Trampa | Qué pasa | Antídoto |
|---|---|---|
| Mezclar `sin`/`cos` con `dsin`/`dcos` | Un ángulo en grados metido en `sin()` da basura | Grados en todo el proyecto; `dsin`/`dcos` siempre |
| Escribir tú la trigonometría con Y hacia abajo | El signo del seno queda invertido respecto a `lengthdir_y` | Usa `lengthdir_x/y`; si escribes la fórmula, es `y -= sin(...)` |
| Restar ángulos con `-` | `10 - 350 = -340` cuando la respuesta correcta es `+20` | `angle_difference` (§3.1) |

```gml
/// Comprobación mental de una línea: los cuatro puntos cardinales
show_debug_message($"0°   -> ({lengthdir_x(1, 0)},   {lengthdir_y(1, 0)})");    // (1, 0)  derecha
show_debug_message($"90°  -> ({lengthdir_x(1, 90)},  {lengthdir_y(1, 90)})");   // (0, -1) ARRIBA
show_debug_message($"180° -> ({lengthdir_x(1, 180)}, {lengthdir_y(1, 180)})");  // (-1, 0) izquierda
show_debug_message($"270° -> ({lengthdir_x(1, 270)}, {lengthdir_y(1, 270)})");  // (0, 1)  abajo
```

### 1.2 · Las dos formas de decir «dirección», y cuándo usar cada una

Un movimiento en 2D se puede representar de dos maneras equivalentes. No son intercambiables
en la práctica: cada una hace fácil una cosa y difícil la otra.

| | **Ángulo + longitud** (`point_direction` / `lengthdir_x,y`) | **Vector explícito** (`vx`, `vy`) |
|---|---|---|
| Girar hacia algo | Trivial: sumar grados | Requiere rotar el vector |
| Sumar dos movimientos | **Imposible directamente**: hay que pasar a vector | Trivial: `vx1+vx2`, `vy1+vy2` |
| Limitar la velocidad | Trivial: `clamp` de la longitud | Normalizar y multiplicar |
| Rebotar | Requiere reflejar el ángulo a mano | Fórmula cerrada (§2.7) |
| Coste | 2 llamadas trigonométricas por uso | Sumas y multiplicaciones |
| Lo usa | Torretas, orbitas, disparos, IA sencilla | Físicas, *steering* acumulativo, colisión |

**Regla práctica:** si el movimiento es **una sola causa**, usa ángulo. Si es la **suma de
varias fuerzas** (gravedad + impulso + empuje + viento), usa vector y solo conviértelo a ángulo
al final para dibujar (`image_angle = point_direction(0, 0, vx, vy);`).

```gml
/// Ida y vuelta entre las dos representaciones (exacta en ambos sentidos)
// Ángulo+longitud  ->  vector
var _vx = lengthdir_x(_longitud, _angulo);
var _vy = lengthdir_y(_longitud, _angulo);

// Vector  ->  ángulo+longitud
var _angulo    = point_direction(0, 0, _vx, _vy);   // 0..360
var _longitud  = point_distance(0, 0, _vx, _vy);
```

> 💡 `point_direction(0, 0, vx, vy)` es la manera **verificada y segura** de hacer `atan2` en
> GameMaker: ya devuelve grados en `0..360` y ya tiene en cuenta que Y va hacia abajo. La
> alternativa cruda es `darctan2(-_vy, _vx)`, que devuelve `-180..180` y exige el signo a mano.
> Salvo que necesites el rango con signo, usa `point_direction`.

### 1.3 · Coste: cuándo importa y cuándo no

`point_distance` calcula una raíz cuadrada. En un bucle de 2 000 comprobaciones por frame eso
se nota; en 20 no. La optimización clásica es **comparar cuadrados** y no sacar nunca la raíz:

```gml
/// ¿Hay algún enemigo dentro del radio? Sin una sola raíz cuadrada.
var _radio_al_cuadrado = sqr(rango_ataque);
var _encontrado = noone;

with (obj_enemigo)
{
    var _dx = x - other.x;
    var _dy = y - other.y;
    if (_dx * _dx + _dy * _dy <= _radio_al_cuadrado)   // sqr() también vale
    {
        _encontrado = id;
        break;
    }
}
```

Esto **solo** funciona para comparar («¿está más cerca que?»), nunca para usar la distancia como
número (una barra de vida, un volumen de sonido, un factor de fuerza): ahí sí hace falta la raíz.

---

## 2 · Vectores en la práctica

GameMaker **no tiene un tipo vector**: se trabaja con componentes sueltas o con un `struct`
`{ x, y }`. El inventario de lo que sí trae está en
[08 · 11 §Vectores](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores%2C%20matrices%20y%20%C3%A1ngulos.md).
Lo que sigue es lo que hay que escribirse, con la pregunta de juego que responde cada operación.

| Operación | Pregunta que responde | En GML |
|---|---|---|
| Magnitud | «¿Cuánto me estoy moviendo?» | `point_distance(0, 0, vx, vy)` |
| Normalizar | «Dame solo la dirección, sin la velocidad» | Dividir por la magnitud (§2.2) |
| Producto escalar | «¿Está delante o detrás?» «¿mira hacia mí?» | `dot_product`, `dot_product_normalised` |
| Producto cruzado 2D | «¿A la izquierda o a la derecha?» «¿gira en sentido horario?» | A mano (§2.5) |
| Proyección | «¿Cuánto de este movimiento va en esa dirección?» | A mano (§2.6) |
| Reflexión | «¿Cómo rebota?» | A mano (§2.7) |

### 2.1 · Magnitud, y el vector nulo

```gml
/// @func magnitud(_vx, _vy)
/// @desc Longitud del vector. Es `point_distance` desde el origen: usa esa,
///       que está optimizada, en lugar de escribir la raíz a mano.
/// @param {Real} _vx  Componente X.
/// @param {Real} _vy  Componente Y.
/// @return {Real}     Longitud, siempre >= 0.
function magnitud(_vx, _vy)
{
    return point_distance(0, 0, _vx, _vy);
}
```

### 2.2 · Normalizar (y la división por cero que se come la partida)

Normalizar es reducir el vector a longitud 1 conservando la dirección. **El vector nulo `(0,0)`
no tiene dirección**, así que dividir por su magnitud produce `NaN` y a partir de ahí todo lo
que toque esa variable se convierte en `NaN` sin avisar: la instancia desaparece de pantalla y
no salta ningún error. Es el bug más difícil de encontrar de esta lista.

```gml
/// @func normalizar(_vx, _vy, [_por_defecto_x], [_por_defecto_y])
/// @desc Devuelve el vector con longitud 1. Si el vector es nulo devuelve el
///       valor por defecto (por omisión, (0,0)) EN LUGAR de dividir por cero.
/// @param {Real} _vx  Componente X.
/// @param {Real} _vy  Componente Y.
/// @param {Real} [_por_defecto_x]  Qué devolver si el vector es nulo.
/// @param {Real} [_por_defecto_y]  Qué devolver si el vector es nulo.
/// @return {Array<Real>}  [x, y] con longitud 1 (o el valor por defecto).
function normalizar(_vx, _vy, _por_defecto_x = 0, _por_defecto_y = 0)
{
    var _long = point_distance(0, 0, _vx, _vy);
    if (_long <= math_get_epsilon()) { return [_por_defecto_x, _por_defecto_y]; }
    return [_vx / _long, _vy / _long];
}
```

> 🔺 La comprobación es `<= math_get_epsilon()`, no `== 0`. Un vector de longitud `1e-14` no es
> cero pero al dividir produce componentes de orden `1e14`, que es igual de catastrófico. Ver §11.

### 2.3 · Producto escalar: ¿está delante o detrás?

El producto escalar de dos vectores es `x1·x2 + y1·y2`. Lo único que hay que recordar de él es
**el signo**, que responde a una pregunta binaria de juego:

| Resultado | Significado |
|---|---|
| `> 0` | Los dos vectores apuntan **hacia el mismo lado** (ángulo < 90°) |
| `= 0` | Son **perpendiculares** |
| `< 0` | Apuntan a **lados opuestos** (ángulo > 90°) |

```gml
/// @func esta_delante(_x, _y, _mirando, _obj_x, _obj_y)
/// @desc ¿El punto (_obj_x,_obj_y) queda en el hemisferio hacia el que mira
///       quien está en (_x,_y) con orientación _mirando (grados)?
/// @param {Real} _x         X del observador.
/// @param {Real} _y         Y del observador.
/// @param {Real} _mirando   Orientación del observador, en grados.
/// @param {Real} _obj_x     X del objetivo.
/// @param {Real} _obj_y     Y del objetivo.
/// @return {Bool}           True si está por delante (menos de 90° de desvío).
function esta_delante(_x, _y, _mirando, _obj_x, _obj_y)
{
    var _fx = lengthdir_x(1, _mirando);   // vector unitario de la mirada
    var _fy = lengthdir_y(1, _mirando);
    return (dot_product(_fx, _fy, _obj_x - _x, _obj_y - _y) > 0);
}
```

Casos reales donde esto es exactamente lo que hace falta: apuñalar por la espalda (comparar la
orientación del atacante con la de la víctima), decidir si un sonido suena a izquierda o
derecha, saber si el jugador se aleja o se acerca a un enemigo.

### 2.4 · Cono de visión, con el ángulo de verdad

El signo del producto escalar solo distingue «delante / detrás» (un cono de 180°). Para un cono
de apertura arbitraria hace falta el **producto escalar normalizado**, que devuelve directamente
el coseno del ángulo entre los dos vectores, en `-1..1`.

```gml
/// @func en_cono_vision(_x, _y, _mirando, _apertura, _alcance, _obj_x, _obj_y)
/// @desc ¿El objetivo cae dentro del cono de visión? Compara cosenos: es una
///       multiplicación y una comparación, sin arcocosenos.
/// @param {Real} _x         X del observador.
/// @param {Real} _y         Y del observador.
/// @param {Real} _mirando   Orientación del observador, en grados.
/// @param {Real} _apertura  Apertura TOTAL del cono, en grados (90 = 45 a cada lado).
/// @param {Real} _alcance   Distancia máxima, en píxeles.
/// @param {Real} _obj_x     X del objetivo.
/// @param {Real} _obj_y     Y del objetivo.
/// @return {Bool}
function en_cono_vision(_x, _y, _mirando, _apertura, _alcance, _obj_x, _obj_y)
{
    var _dx = _obj_x - _x;
    var _dy = _obj_y - _y;

    // 1) Alcance, comparando cuadrados: nos ahorra la raíz.
    if (_dx * _dx + _dy * _dy > sqr(_alcance)) { return false; }

    // 2) Apertura. dcos(apertura/2) es el coseno del semiángulo: el umbral.
    var _fx  = lengthdir_x(1, _mirando);
    var _fy  = lengthdir_y(1, _mirando);
    var _cos = dot_product_normalised(_fx, _fy, _dx, _dy);

    return (_cos >= dcos(_apertura * 0.5));
}
```

> 💡 Un cono de visión **completo** necesita además comprobar que no hay una pared en medio.
> Eso es `collision_line` (§6.8) o el raycasting de
> [04 · 05 §5.6](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md).
> El cono decide *dónde puede mirar*; el rayo decide *qué llega a ver*.

### 2.5 · Producto cruzado 2D: ¿a qué lado está?

En 2D el producto cruzado no da un vector: da un **escalar** cuyo signo dice de qué lado cae un
punto respecto de una recta orientada. GameMaker **no tiene** una función para esto (`cross_product`
no existe); son dos multiplicaciones.

```gml
/// @func lado_de_la_linea(_ax, _ay, _bx, _by, _px, _py)
/// @desc Producto cruzado 2D de AB × AP. Dice a qué lado de la recta A->B cae P.
///       > 0  ->  a la IZQUIERDA de A->B en pantalla (Y hacia abajo)
///       = 0  ->  los tres puntos son colineales
///       < 0  ->  a la DERECHA
///       El valor absoluto es el doble del área del triángulo ABP.
/// @param {Real} _ax  X del origen del segmento.
/// @param {Real} _ay  Y del origen del segmento.
/// @param {Real} _bx  X del final del segmento.
/// @param {Real} _by  Y del final del segmento.
/// @param {Real} _px  X del punto a clasificar.
/// @param {Real} _py  Y del punto a clasificar.
/// @return {Real}     Escalar con signo.
function lado_de_la_linea(_ax, _ay, _bx, _by, _px, _py)
{
    return (_bx - _ax) * (_py - _ay) - (_by - _ay) * (_px - _ax);
}
```

Usos directos: decidir si un coche va por dentro o por fuera de la curva, ordenar los vértices
de un polígono, saber si el jugador ha cruzado una línea de meta y **en qué sentido**, o
comprobar si un triángulo está definido en sentido horario.

> ⚠️ El signo depende de la orientación del eje Y. Con Y hacia abajo, un resultado **positivo**
> corresponde a la **izquierda** de A→B tal como se ve en pantalla. Si copias una fórmula de un
> texto de matemáticas escrito con Y hacia arriba, el criterio sale al revés: compruébalo con
> tres puntos conocidos antes de fiarte.

### 2.6 · Proyección: descomponer un movimiento

Proyectar el vector **v** sobre una dirección **d** (unitaria) da cuánto de **v** va en esa
dirección. Con eso se construyen dos cosas muy usadas: **deslizar por una pared** (quitarle a la
velocidad la componente que entra en la pared) y **velocidad de aproximación** (para saber si
dos objetos se acercan de verdad o solo se cruzan).

```gml
/// @func deslizar_por_pared(_vx, _vy, _normal_x, _normal_y)
/// @desc Quita del movimiento la parte que entra en la pared, dejando solo la
///       que la recorre. Es lo que hace que un personaje resbale por un muro
///       en diagonal en lugar de clavarse.
/// @param {Real} _vx        Velocidad X.
/// @param {Real} _vy        Velocidad Y.
/// @param {Real} _normal_x  X de la normal UNITARIA de la pared.
/// @param {Real} _normal_y  Y de la normal UNITARIA de la pared.
/// @return {Array<Real>}    [vx, vy] ya proyectados.
function deslizar_por_pared(_vx, _vy, _normal_x, _normal_y)
{
    var _entrante = dot_product(_vx, _vy, _normal_x, _normal_y);
    return [_vx - _normal_x * _entrante,
            _vy - _normal_y * _entrante];
}
```

### 2.7 · Reflexión: rebotar contra una pared

Un rebote perfectamente elástico es `v' = v − 2·(v·n)·n`, con **n** la normal **unitaria** de la
pared. Añadiendo un coeficiente de restitución se controla cuánta energía conserva el rebote.

```gml
/// @func reflejar_vector(_vx, _vy, _normal_x, _normal_y, [_restitucion])
/// @desc Rebota el vector contra una superficie de normal unitaria.
/// @param {Real} _vx           Velocidad X entrante.
/// @param {Real} _vy           Velocidad Y entrante.
/// @param {Real} _normal_x     X de la normal UNITARIA de la superficie.
/// @param {Real} _normal_y     Y de la normal UNITARIA de la superficie.
/// @param {Real} [_restitucion] 1 = rebote perfecto, 0.5 = pierde la mitad, 0 = se pega.
/// @return {Array<Real>}       [vx, vy] tras el rebote.
function reflejar_vector(_vx, _vy, _normal_x, _normal_y, _restitucion = 1)
{
    var _d = dot_product(_vx, _vy, _normal_x, _normal_y);
    var _rx = _vx - 2 * _d * _normal_x;
    var _ry = _vy - 2 * _d * _normal_y;
    return [_rx * _restitucion, _ry * _restitucion];
}
```

Para paredes alineadas con los ejes no hace falta nada de esto: la normal es `(±1, 0)` o
`(0, ±1)` y la reflexión se reduce a invertir una componente (`vx = -vx`). La fórmula general
vale la pena en cuanto aparece una **rampa**, un **parachoques inclinado** o un **tilemap con
esquinas en diagonal**.

```gml
/// obj_bala · Evento Step — rebote contra una plataforma inclinada 30°
if (place_meeting(x + vx, y + vy, obj_rampa))
{
    // La normal de una rampa de ángulo A es perpendicular a ella: A + 90.
    var _n = normalizar(lengthdir_x(1, angulo_rampa + 90),
                        lengthdir_y(1, angulo_rampa + 90));
    var _v = reflejar_vector(vx, vy, _n[0], _n[1], 0.8);
    vx = _v[0];
    vy = _v[1];
    rebotes += 1;
    if (rebotes >= 3) { instance_destroy(); }
}
```

> 🔺 **La normal tiene que ser unitaria.** Si la sacas de la diferencia entre dos puntos sin
> normalizar, el rebote sale con una energía multiplicada por el cuadrado de la longitud y la
> bala sale disparada. Pasa siempre por `normalizar()` (§2.2).

---

## 3 · Ángulos

### 3.1 · `angle_difference`: la diferencia mínima entre dos ángulos

Restar ángulos con `-` es incorrecto en cuanto se cruza el 0: `10 - 350 = -340`, cuando la
respuesta que quiere el juego es `+20`. `angle_difference(dest, src)` devuelve la diferencia
**más corta**, siempre en `-180..180`, con signo positivo = antihorario.

La propiedad que hay que recordar, y que dice el manual: **`src + angle_difference(dest, src)`
te lleva a `dest`**. Eso es exactamente lo que hace falta para girar.

```gml
/// Cuánto y hacia dónde hay que girar para mirar al ratón
var _objetivo = point_direction(x, y, mouse_x, mouse_y);
var _falta    = angle_difference(_objetivo, image_angle);   // -180..180

// Signo: > 0 hay que girar en sentido antihorario, < 0 horario.
// Magnitud: cuántos grados quedan. abs(_falta) < 5 -> «ya está apuntando».
```

### 3.2 · Girar hacia un objetivo con velocidad máxima

El error clásico es `image_angle = _objetivo;`, que teletransporta la torreta. El segundo error
clásico es `image_angle += _falta * 0.1;`, que gira rápido al principio y **nunca llega** al
final (además de depender de los fps, §4.2). La versión correcta limita los grados por paso:

```gml
/// @func girar_hacia(_actual, _objetivo, _grados_max)
/// @desc Gira `_actual` hacia `_objetivo` como mucho `_grados_max` grados,
///       tomando siempre el camino corto y sin pasarse.
/// @param {Real} _actual      Ángulo actual, en grados.
/// @param {Real} _objetivo    Ángulo al que se quiere llegar, en grados.
/// @param {Real} _grados_max  Giro máximo permitido en esta llamada.
/// @return {Real}             Nuevo ángulo.
function girar_hacia(_actual, _objetivo, _grados_max)
{
    var _falta = angle_difference(_objetivo, _actual);
    return _actual + clamp(_falta, -_grados_max, _grados_max);
}
```

```gml
/// obj_torreta · Evento Step — 180°/s, independiente de los fps
var _dt = delta_time / 1000000;
image_angle = girar_hacia(image_angle,
                          point_direction(x, y, obj_jugador.x, obj_jugador.y),
                          180 * _dt);
```

**La velocidad de giro es una decisión de diseño, no un detalle técnico.** Una torreta que gira
a 90 °/s se puede esquivar rodeándola; a 720 °/s, no. Esa cifra es una de las palancas de
dificultad más limpias que existen — ver
[13 · 01 §3](./01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md).

### 3.3 · Envolver un valor a un rango (`wrap` no existe en GML)

`wrap` **no existe** en el runtime (verificado; lo más parecido es `move_wrap`, que actúa sobre
la posición de la instancia, no sobre un número). Hace falta escribirla, y la versión correcta
usa el módulo **dos veces** para que funcione también con valores negativos.

```gml
/// @func envolver(_valor, _minimo, _maximo)
/// @desc Envuelve `_valor` dentro de [_minimo, _maximo). Funciona con negativos:
///       envolver(-10, 0, 360) devuelve 350, no -10.
/// @param {Real} _valor   Valor a envolver.
/// @param {Real} _minimo  Límite inferior, incluido.
/// @param {Real} _maximo  Límite superior, EXCLUIDO.
/// @return {Real}         Valor dentro del rango.
function envolver(_valor, _minimo, _maximo)
{
    var _rango = _maximo - _minimo;
    if (_rango <= 0) { return _minimo; }
    // El doble módulo corrige el signo: en GML, -10 % 360 vale -10.
    return _minimo + (((_valor - _minimo) % _rango) + _rango) % _rango;
}
```

```gml
angulo_camara = envolver(angulo_camara + giro, 0, 360);    // ángulos
hora_del_dia  = envolver(hora_del_dia + _dt, 0, 24);       // ciclo día/noche
indice_menu   = envolver(indice_menu + 1, 0, array_length(opciones));   // menú circular
```

> 💡 `point_direction` ya devuelve `0..360`, y `image_angle` se normaliza solo al asignarle un
> valor. `envolver` hace falta para **tus propias** variables acumuladas: fases de onda, horas de
> reloj, índices de menú, contadores cíclicos.

### 3.4 · `dcos`/`dsin` frente a `cos`/`sin`

Son la misma función; solo cambia la unidad del argumento. **La regla es elegir una y no
mezclarlas jamás en el mismo proyecto.**

| | Grados (`dsin`, `dcos`, `dtan`, `darctan2`) | Radianes (`sin`, `cos`, `tan`, `arctan2`) |
|---|---|---|
| Encaja con | `image_angle`, `direction`, `point_direction`, `lengthdir_*` | Fórmulas de libro, shaders (GLSL usa radianes) |
| Ciclo completo | `360` | `2 * pi` |
| Legible al depurar | Sí: «45» se lee | No: «0.7853981…» |
| Recomendación | **Por defecto en GameMaker** | Solo dentro de un shader o al portar una fórmula |

```gml
// Conversión, cuando toca cruzar la frontera (por ejemplo, pasar un ángulo a un shader)
var _rad = degtorad(image_angle);
var _deg = radtodeg(_rad);

// Estas dos líneas son idénticas:
var _a = dsin(30);
var _b = sin(degtorad(30));   // más caro y más fácil de equivocar
```

> 🔺 El error más común de esta sección: `x += cos(image_angle) * velocidad;`. `image_angle`
> está en **grados**, así que `cos(90)` no vale 0 sino −0,448. El movimiento sale caótico pero
> «casi plausible», que es lo que hace que cueste tanto detectarlo. Usa `lengthdir_x/y`.

### 3.5 · Apuntar con retardo: la torreta que se siente pesada

Un giro con velocidad constante (§3.2) es preciso pero mecánico. Un giro con **retardo
exponencial** acelera y frena solo, y es lo que da sensación de masa. El truco es aplicar el
suavizado a la **diferencia** de ángulos, nunca a los ángulos en bruto (o cruzará el 0 dando la
vuelta larga).

```gml
/// obj_torreta_pesada · Evento Create
angulo_deseado = image_angle;
velocidad_giro = 0;      // grados por segundo, con inercia

/// obj_torreta_pesada · Evento Step
var _dt = delta_time / 1000000;

angulo_deseado = point_direction(x, y, mouse_x, mouse_y);
var _falta = angle_difference(angulo_deseado, image_angle);

// Muelle amortiguado sobre la diferencia: acelera hacia el objetivo y se frena solo.
var _rigidez     = 40;    // cuánto tira hacia el objetivo
var _amortiguado = 9;     // cuánto frena; sin esto, oscila eternamente
velocidad_giro += (_falta * _rigidez - velocidad_giro * _amortiguado) * _dt;
velocidad_giro  = clamp(velocidad_giro, -540, 540);   // tope físico del motor de la torreta

image_angle += velocidad_giro * _dt;
```

La teoría del muelle amortiguado y del **muelle crítico** (el que llega sin rebotar) está en
[13 · 08 — Físicas a mano y fluidos](./08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md).
Aquí basta con la intuición: `_rigidez` es cuánto tira, `_amortiguado` es cuánto frena, y la
frontera entre «rebota» y «llega y para» está aproximadamente en `_amortiguado = 2*sqrt(_rigidez)`.

### 3.6 · Promediar ángulos: por qué la media aritmética miente

`(350 + 10) / 2 = 180`, que es exactamente el ángulo **opuesto** al correcto (0°). Promediar
ángulos exige pasar a vectores, sumar y volver:

```gml
/// @func angulo_medio(_angulos)
/// @desc Media circular de un array de ángulos en grados. La media aritmética
///       da resultados absurdos al cruzar el 0; esta no.
/// @param {Array<Real>} _angulos  Ángulos en grados.
/// @return {Real}                 Ángulo medio en 0..360, o 0 si se cancelan.
function angulo_medio(_angulos)
{
    var _sx = 0, _sy = 0;
    var _n = array_length(_angulos);
    for (var _i = 0; _i < _n; _i++)
    {
        _sx += lengthdir_x(1, _angulos[_i]);
        _sy += lengthdir_y(1, _angulos[_i]);
    }
    if (point_distance(0, 0, _sx, _sy) <= math_get_epsilon()) { return 0; }
    return point_direction(0, 0, _sx, _sy);
}
```

Es justo lo que necesita el **alineamiento** de una bandada (que todos apunten hacia la
dirección media del grupo) — ver
[04 · 23 §6](../04%20-%20Recetas%20por%20g%C3%A9nero/23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md).

---

## 4 · Interpolación, suavizado y easing

### 4.1 · `lerp`: lo que hace y lo que no

`lerp(a, b, amt)` devuelve `a + (b - a) * amt`. Es una **mezcla lineal**, nada más. Tres cosas
que conviene tener claras antes de usarla en cualquier sitio:

1. **No está limitada a `0..1`.** `lerp(0, 10, 1.5)` devuelve `15`: extrapola. A veces es útil
   (adelantar una predicción), casi siempre es un bug. Si no lo quieres: `clamp(_t, 0, 1)`.
2. **Es lineal**: el resultado nunca tiene aceleración. Todo lo que «se sienta bien» sale de
   deformar `_t` **antes** de meterlo en `lerp` (eso es exactamente lo que hace el *easing*).
3. **No sabe nada del tiempo.** Llamarla una vez por frame con un factor fijo es el error de la
   sección siguiente.

```gml
// Interpolar dos posiciones: es lerp dos veces, una por eje. `lerp_2d` no existe.
var _px = lerp(x0, x1, _t);
var _py = lerp(y0, y1, _t);

// Interpolar un color: NO se hace con lerp sobre el entero del color.
var _col = merge_colour(c_red, c_yellow, _t);   // esta sí interpola canal a canal
```

### 4.2 · El «lerp exponencial», y por qué el tuyo está roto

Esta línea está en el 90 % de los proyectos y **está mal**:

```gml
x = lerp(x, objetivo_x, 0.1);   // ❌ depende de la tasa de fotogramas
```

El razonamiento: tras un frame queda el `90 %` de la distancia; tras `n` frames queda `0.9^n`.
A 60 fps, en un segundo queda `0.9^60 ≈ 0,0018`. A 144 fps queda `0.9^144 ≈ 3·10⁻⁷`. **La cámara
va casi cuatro órdenes de magnitud más pegada en un monitor rápido.** No es un matiz estético:
cambia la jugabilidad, y en un juego con *input* preciso cambia si un salto es posible o no.

La corrección es dejar de pensar en «cuánto avanzo por frame» y pensar en **«qué fracción de la
distancia queda tras un segundo»**. Esa fracción es una constante del diseño, y elevarla al
tiempo transcurrido da el factor correcto para cualquier `dt`:

```
factor_del_paso = 1 − restante_por_segundo ^ dt
```

En GML eso es `1 - power(_restante, _dt)`. La biblioteca ya lo trae escrito de dos formas
equivalentes —`lerp_dt()` en
[`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml) y `suavizar()` en
[13 · 04 §4.2](./04%20-%20Animaci%C3%B3n%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md)—
así que **no lo reescribas**. Lo que sí falta, y es lo que hace que el parámetro sea razonable
para un diseñador, es la formulación por **media vida**.

### 4.3 · Media vida: el único parámetro de suavizado que se puede razonar

«Restante tras un segundo = 0,002» no significa nada para nadie. «Tarda 0,12 s en recorrer la
mitad de la distancia» sí: es medible con un cronómetro y comparable entre sistemas.

```gml
/// @func suavizar_media_vida(_actual, _objetivo, _media_vida, _dt)
/// @desc Suavizado exponencial parametrizado por MEDIA VIDA: los segundos que
///       tarda en cubrir la mitad de la distancia que le queda. Independiente
///       de la tasa de fotogramas.
///       Equivale a lerp_dt() de scr_math_util, con un parámetro legible.
/// @param {Real} _actual      Valor actual.
/// @param {Real} _objetivo    Valor destino.
/// @param {Real} _media_vida  Segundos para cubrir la mitad de la distancia.
/// @param {Real} _dt          Tiempo transcurrido, en SEGUNDOS.
/// @return {Real}             Nuevo valor.
function suavizar_media_vida(_actual, _objetivo, _media_vida, _dt)
{
    if (_media_vida <= 0) { return _objetivo; }          // 0 = sin suavizado
    var _k = 1 - power(0.5, _dt / _media_vida);
    return lerp(_actual, _objetivo, _k);
}
```

```gml
/// obj_camara · Evento Step
var _dt = delta_time / 1000000;
x = suavizar_media_vida(x, obj_jugador.x, 0.12, _dt);   // 0,12 s a media distancia
y = suavizar_media_vida(y, obj_jugador.y, 0.12, _dt);
```

Las tres formulaciones son la misma curva con distinto parámetro. Elige una y documéntala:

| Formulación | Fórmula del factor | El parámetro significa |
|---|---|---|
| Restante por segundo | `1 - power(_r, _dt)` | Fracción que queda tras 1 s (0,002 = rápido) |
| Media vida | `1 - power(0.5, _dt / _h)` | Segundos para cubrir media distancia |
| Constante de decaimiento | `1 - exp(-_lambda * _dt)` | `λ` grande = rápido; la de los libros de física |

Equivalencias exactas: `_lambda = ln(2) / _h` y `_r = exp(-_lambda)`. Y el aviso que importa:

> 🔺 Un suavizado exponencial **nunca llega** matemáticamente al objetivo, solo se acerca. Si el
> valor alimenta una comparación (`if (x == objetivo)`) o un contador de estado, añade un corte:
> `if (abs(_objetivo - _actual) < 0.5) { _actual = _objetivo; }`. Con posiciones en píxeles el
> umbral natural es medio píxel; por debajo de eso, nadie lo ve.

### 4.4 · `smoothstep`: no es nativa, y hay dos versiones

`smoothstep` **no existe en el runtime** (verificado). Está escrita en
[`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml) y, con la curva
quíntica de Perlin, en
[13 · 07 §2.1](./07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md). La diferencia entre las
dos versiones es real y decide cuál usar:

| Curva | Fórmula | Derivada 1.ª en los extremos | Derivada 2.ª | Para qué |
|---|---|---|---|---|
| Cúbica (*smoothstep*) | `t*t*(3 - 2*t)` | 0 | ≠ 0 | Fundidos, transiciones de UI, mezclas de valores |
| Quíntica (*smootherstep*) | `t*t*t*(t*(t*6 - 15) + 10)` | 0 | 0 | Ruido, desplazamiento de geometría, cualquier cosa que luego se **derive** o se ilumine |

La regla: si el resultado se va a **derivar** (normales de un terreno, iluminación de una
superficie desplazada), la quíntica evita bandas visibles. Para todo lo demás, la cúbica es más
barata y se ve igual.

### 4.5 · El catálogo de easings, y qué pide cada situación

Las funciones ya están escritas —`ease_linear`, `ease_in_sine`, `ease_out_quad`,
`ease_in_out_cubic`, `ease_out_back`, `ease_out_elastic`, `ease_out_bounce`, `ease_out_expo` y
compañía— en [`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml), y el
motor que las aplica a lo largo del tiempo es
[`scr_tween.gml`](../06%20-%20Assets%20y%20Scripts/scr_tween.gml). **No las reimplementes.**
Lo que falta ahí es el criterio de cuál elegir:

| Situación | Easing | Por qué |
|---|---|---|
| Algo **entra** en pantalla (menú, notificación, cartel) | `ease_out_back` / `ease_out_cubic` | Llega deprisa y se asienta; el rebote leve lo hace «aterrizar» |
| Algo **sale** de pantalla | `ease_in_cubic` | Acelera al irse: nadie mira lo que se va |
| Movimiento **de A a B** que el jugador sigue con la vista | `ease_in_out_cubic` | Arranque y frenada simétricos, lectura natural |
| Barra de vida bajando | `ease_out_quad` | El golpe se lee inmediato y la cola comunica cuánto queda |
| Objeto que **cae** y toca el suelo | `ease_out_bounce` | Es lo que espera el ojo |
| Recompensa, cofre, subida de nivel | `ease_out_elastic` | Exagerado a propósito: marca que es importante |
| Cualquier valor **continuo** que persigue a otro (cámara, mira, HUD) | **Ninguno**: usa §4.2 | El easing necesita principio y fin; un seguimiento no los tiene |

> 🔺 La última fila es la confusión más cara. Un *easing* interpola entre **dos valores fijos**
> durante **una duración conocida**. Un seguimiento persigue un objetivo **que se mueve**. Si
> aplicas un tween a la cámara, cada vez que el jugador cambie de dirección reinicias el tween y
> la cámara da tirones.

Las fórmulas canónicas y su representación gráfica están en **easings.net**; los nombres de
`scr_math_util` son los mismos (`easeOutBack` → `ease_out_back`).

### 4.5 bis · Componer curvas en vez de memorizarlas

Squirrel Eiserloh planteó en la GDC de 2015 que casi todas las curvas útiles se **construyen**
a partir de cuatro operaciones sobre curvas más simples, en lugar de copiarse de una tabla. Es
la parte de la charla que más rentabilidad da en el día a día, porque convierte «necesito una
curva que arranque suave y termine con un tirón» en tres líneas de código.

```gml
/// @func invertir_curva(_t)
/// @desc `flip` de Eiserloh: espeja la curva en los dos ejes.
///       Aplicado dos veces alrededor de otra función convierte un
///       «arranque suave» en una «frenada suave» y viceversa.
/// @param {Real} _t  0..1
/// @return {Real}    1 - t
function invertir_curva(_t)
{
    return 1 - _t;
}

/// @func arranque_suave(_t, [_grado])
/// @desc `smoothStart` de Eiserloh: sale despacio y acelera. Es t elevado a n.
///       Grado 2 = suave, 5 = muy marcado. Equivale a ease_in_quad/cubic/...
/// @param {Real} _t       0..1
/// @param {Real} [_grado] Exponente, 2..5.
/// @return {Real}         0..1
function arranque_suave(_t, _grado = 2)
{
    return power(_t, _grado);
}

/// @func frenada_suave(_t, [_grado])
/// @desc `smoothStop` de Eiserloh: sale rápido y frena. Es el arranque suave
///       espejado dos veces. Equivale a ease_out_quad/cubic/...
/// @param {Real} _t       0..1
/// @param {Real} [_grado] Exponente, 2..5.
/// @return {Real}         0..1
function frenada_suave(_t, _grado = 2)
{
    return invertir_curva(power(invertir_curva(_t), _grado));
}

/// @func escalar_curva(_t, _curva)
/// @desc `scale` de Eiserloh: multiplica la curva por t. Suaviza el arranque
///       de cualquier curva sin tocar su final.
/// @param {Real} _t          0..1
/// @param {Function} _curva  Función que recibe y devuelve 0..1.
/// @return {Real}
function escalar_curva(_t, _curva)
{
    return _t * _curva(_t);
}

/// @func mezclar_curvas(_t, _curva_a, _curva_b)
/// @desc `crossfade` de Eiserloh: empieza siendo la curva A y acaba siendo la B.
///       Es la operación que produce curvas nuevas sin inventar fórmulas.
/// @param {Real} _t            0..1
/// @param {Function} _curva_a  Curva dominante al principio.
/// @param {Function} _curva_b  Curva dominante al final.
/// @return {Real}
function mezclar_curvas(_t, _curva_a, _curva_b)
{
    return lerp(_curva_a(_t), _curva_b(_t), _t);
}
```

```gml
// Un «smoothstep» construido, no copiado: arranque suave mezclado con frenada suave.
var _s = mezclar_curvas(_t, arranque_suave, frenada_suave);   // ≈ 3t² - 2t³

// Un golpe que sale disparado y frena en seco al final, sin buscar en ninguna tabla.
var _golpe = frenada_suave(_t, 5);
```

⚠️ Los nombres originales (`smoothStart`, `smoothStop`, `flip`, `scale`, `crossfade`) están
verificados contra una implementación pública que cita la charla; **no** contra la transcripción
del vídeo, que es de pago en GDC Vault. Las fórmulas sí son comprobables por álgebra elemental.

### 4.6 · Bézier cuadrática y cúbica

Una Bézier **no pasa por sus puntos de control intermedios**: los usa para tirar de la curva.
Eso la hace ideal para trayectorias que quieres *dirigir* (un objeto que vuela del enemigo al
contador de oro del HUD, un ataque en arco, una curva de UI) e inadecuada para pasar por puntos
marcados a mano (para eso, §4.7).

```gml
/// @func bezier_cuadratica(_p0, _p1, _p2, _t)
/// @desc Bézier de 3 puntos sobre un solo eje. B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
///       Llámala una vez por eje. P1 es el «imán» que curva la trayectoria.
/// @param {Real} _p0  Valor inicial.
/// @param {Real} _p1  Punto de control (la curva NO pasa por él).
/// @param {Real} _p2  Valor final.
/// @param {Real} _t   Progreso, 0..1.
/// @return {Real}
function bezier_cuadratica(_p0, _p1, _p2, _t)
{
    var _u = 1 - _t;
    return _u * _u * _p0 + 2 * _u * _t * _p1 + _t * _t * _p2;
}

/// @func bezier_cubica(_p0, _p1, _p2, _p3, _t)
/// @desc Bézier de 4 puntos. B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
///       Dos controles: permite una curva en S, que la cuadrática no puede hacer.
/// @param {Real} _p0  Valor inicial.
/// @param {Real} _p1  Primer punto de control.
/// @param {Real} _p2  Segundo punto de control.
/// @param {Real} _p3  Valor final.
/// @param {Real} _t   Progreso, 0..1.
/// @return {Real}
function bezier_cubica(_p0, _p1, _p2, _p3, _t)
{
    var _u  = 1 - _t;
    var _u2 = _u * _u;
    var _t2 = _t * _t;
    return _u2 * _u * _p0
         + 3 * _u2 * _t * _p1
         + 3 * _u * _t2 * _p2
         + _t2 * _t * _p3;
}
```

```gml
/// obj_moneda_al_hud · Evento Create — arco desde el enemigo hasta el contador
origen_x = x;             origen_y = y;
destino_x = 40;           destino_y = 28;          // posición del icono en el GUI
// El control se pone POR ENCIMA de la recta: con Y hacia abajo, restar sube.
control_x = (origen_x + destino_x) * 0.5;
control_y = min(origen_y, destino_y) - 80;
progreso = 0;

/// obj_moneda_al_hud · Evento Step
progreso = min(progreso + delta_time / 1000000 / 0.6, 1);   // 0,6 s de vuelo
var _t = ease_out_quad(progreso);   // el easing va sobre t, no sobre la curva
x = bezier_cuadratica(origen_x, control_x, destino_x, _t);
y = bezier_cuadratica(origen_y, control_y, destino_y, _t);
if (progreso >= 1) { global.oro += 1; instance_destroy(); }
```

> 💡 **La velocidad a lo largo de una Bézier no es uniforme.** `_t = 0.5` no está en la mitad
> del recorrido, sino en la mitad del **parámetro**. En tramos muy curvados el objeto acelera.
> Para un movimiento a velocidad constante hay que reparametrizar por longitud de arco, que es
> mucho más código; en un juego, casi nunca compensa. Si lo que quieres es control de velocidad,
> usa un `path` del IDE o Animation Curves (§4.8).

### 4.7 · Catmull-Rom: pasar por los puntos

Catmull-Rom es la *spline* que **sí pasa por todos sus puntos de control**. Es lo que quieres
cuando alguien coloca cuatro marcadores en la room y espera que el objeto los recorra suavemente:
patrullas curvas, cámaras cinemáticas, movimiento de un jefe. Necesita **cuatro** puntos para
interpolar entre los dos centrales: uno antes y uno después, que dan la pendiente.

```gml
/// @func catmull_rom(_p0, _p1, _p2, _p3, _t)
/// @desc Interpola entre _p1 y _p2 usando _p0 y _p3 solo para calcular la
///       pendiente en los extremos. La curva PASA por _p1 y por _p2.
///       Forma uniforme (alpha = 0), la clásica.
/// @param {Real} _p0  Punto anterior (fuera del tramo).
/// @param {Real} _p1  Inicio del tramo. La curva pasa por aquí en t = 0.
/// @param {Real} _p2  Final del tramo. La curva pasa por aquí en t = 1.
/// @param {Real} _p3  Punto siguiente (fuera del tramo).
/// @param {Real} _t   Progreso dentro del tramo, 0..1.
/// @return {Real}
function catmull_rom(_p0, _p1, _p2, _p3, _t)
{
    var _t2 = _t * _t;
    var _t3 = _t2 * _t;
    return 0.5 * ((2 * _p1)
                + (-_p0 + _p2) * _t
                + (2 * _p0 - 5 * _p1 + 4 * _p2 - _p3) * _t2
                + (-_p0 + 3 * _p1 - 3 * _p2 + _p3) * _t3);
}
```

```gml
/// @func ruta_evaluar(_puntos, _t_global, _cerrada)
/// @desc Recorre un array de puntos {x, y} con Catmull-Rom, tratando el array
///       entero como una ruta continua parametrizada de 0 a 1.
/// @param {Array<Struct>} _puntos   Array de structs con .x y .y (mínimo 2).
/// @param {Real} _t_global          Progreso total, 0..1.
/// @param {Bool} [_cerrada]         True para un circuito que vuelve al inicio.
/// @return {Struct}                 { x, y }
function ruta_evaluar(_puntos, _t_global, _cerrada = false)
{
    var _n = array_length(_puntos);
    if (_n < 2) { return { x: _puntos[0].x, y: _puntos[0].y }; }

    var _tramos = _cerrada ? _n : (_n - 1);
    var _pos    = clamp(_t_global, 0, 1) * _tramos;
    var _i      = min(floor(_pos), _tramos - 1);
    var _t      = _pos - _i;

    // Índices vecinos: se envuelven si la ruta es cerrada, se repiten si es abierta.
    var _i0 = _cerrada ? ((_i - 1 + _n) % _n) : max(_i - 1, 0);
    var _i1 = _cerrada ? (_i % _n)            : _i;
    var _i2 = _cerrada ? ((_i + 1) % _n)      : min(_i + 1, _n - 1);
    var _i3 = _cerrada ? ((_i + 2) % _n)      : min(_i + 2, _n - 1);

    return {
        x: catmull_rom(_puntos[_i0].x, _puntos[_i1].x, _puntos[_i2].x, _puntos[_i3].x, _t),
        y: catmull_rom(_puntos[_i0].y, _puntos[_i1].y, _puntos[_i2].y, _puntos[_i3].y, _t)
    };
}
```

> 🔺 Con puntos muy juntos seguidos de otros muy separados, la Catmull-Rom **uniforme** (la de
> arriba) puede formar bucles y salirse del recorrido. La variante *centrípeta* lo evita
> reparametrizando por la raíz de la distancia entre puntos. ⚠️ La implementación centrípeta no
> está escrita en esta biblioteca: si te topas con bucles, la salida práctica es **repartir los
> puntos de forma más regular**, que además es mejor diseño de ruta.

### 4.8 · `animcurve_*`: la alternativa que se edita con el ratón

GameMaker trae curvas como **asset**: se dibujan en el IDE y se leen desde código con
`animcurve_get`, `animcurve_get_channel` y `animcurve_channel_evaluate`. Los tipos de
interpolación disponibles son `animcurvetype_linear`, `animcurvetype_bezier` y
`animcurvetype_catmullrom` (constantes verificadas).

| | Funciones `ease_*` (código) | Animation Curves (asset) |
|---|---|---|
| Se ajusta | Cambiando la fórmula | Arrastrando puntos, viendo el resultado |
| Quién la toca | Programador | Diseñador o artista, sin abrir código |
| Iterar | Recompilar | Editar y recargar |
| Portable a otro proyecto | Copiar un `.gml` | Copiar el asset |
| Varias magnitudes a la vez | Una llamada por magnitud | Un canal por magnitud, en la **misma** curva |

La regla: si la curva la va a tocar quien no programa, o si necesitas **varias magnitudes
sincronizadas** (escala, rotación y opacidad de un mismo efecto), usa el asset. El detalle
completo —crear canales por código, evaluarlos, y cuándo **no** usarlas— está en
[13 · 04 §5](./04%20-%20Animaci%C3%B3n%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md).

### 4.9 · `approach`, `clamp` y compañía: llegar sin pasarse

Para mover un valor hacia otro a **velocidad constante** (y no exponencial), la operación es
`approach`, que ya está escrita en
[`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml). No existe como
función nativa. Su valor está en que **nunca sobrepasa**, que es lo que rompe el intento ingenuo:

```gml
// ❌ Oscila para siempre alrededor del objetivo si el paso no lo divide exacto
if (velocidad < objetivo) { velocidad += 0.5; } else { velocidad -= 0.5; }

// ✅ approach() se queda clavado en el objetivo
velocidad = approach(velocidad, objetivo, 0.5);
```

Las cuatro herramientas de «mover un número» y cuál toca en cada caso:

| Quiero… | Uso | Comportamiento |
|---|---|---|
| Ir a velocidad constante y parar | `approach` (scr_math_util) | Lineal; llega exacto |
| Acercarme cada vez más despacio | §4.2 / §4.3 | Exponencial; nunca llega del todo |
| No salirme de un rango | `clamp(v, min, max)` | Se pega al borde |
| Salir por el otro lado | `envolver` (§3.3) | Cíclico |

---

## 5 · Probabilidad y aleatoriedad

### 5.1 · El catálogo mínimo, y la trampa de la semilla

| Necesito | Función | Rango |
|---|---|---|
| Un real | `random(n)` | `[0, n)` |
| Un real entre dos valores | `random_range(n1, n2)` | `[n1, n2)` |
| Un entero | `irandom(n)` | `[0, n]` — **el extremo entra** |
| Un entero entre dos | `irandom_range(n1, n2)` | `[n1, n2]` — ambos entran |
| Elegir entre opciones | `choose(a, b, c, ...)` | Uniforme entre los argumentos |
| Barajar un array (copia) | `array_shuffle(arr)` | Devuelve un array **nuevo** |
| Barajar un array (en el sitio) | `array_shuffle_ext(arr)` | Modifica el original |

> 🔺 **`irandom` incluye el extremo superior; `random` no.** Para elegir un índice de array:
> `irandom(array_length(_a) - 1)`, nunca `irandom(array_length(_a))`. El fallo aparece una vez de
> cada `n` y se manifiesta como un `undefined` en un sitio que «funcionaba».

**La semilla.** GameMaker arranca siempre con la misma semilla para que depurar sea reproducible.
El manual de `random` y de `randomise` es explícito: si quieres azar de verdad, llama a
`randomise()` **una vez** al arrancar el juego. La página de `array_shuffle` matiza que en la
build final el comportamiento ya es aleatorio; ⚠️ como las dos páginas del manual oficial no
dicen exactamente lo mismo, la regla segura —y la que no cuesta nada— es **llamar siempre a
`randomise()` una vez en el arranque** y no depender de qué haga el build.

```gml
/// obj_arranque · Evento Create  (el primer objeto del primer room)
randomise();                       // UNA vez, en todo el juego
global.semilla_partida = random_get_seed();   // guárdala: reproduce la partida entera
```

### 5.2 · Semillas y determinismo

`random_set_seed(val)` fija la secuencia. Las tres reglas que evitan los problemas conocidos:

1. **Guarda la semilla, no el resultado.** Un save de un roguelike es la semilla más las
   acciones del jugador.
2. **Un generador por sistema.** Si el combate consume números del mismo flujo que el generador
   de mazmorras, el piso siguiente cambia según cuántos golpes hayas dado. La solución y el
   código de un generador propio están en
   [04 · 05 §4.1 y §5.0](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md);
   el marco conceptual, en
   [13 · 07 §1.1](./07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md).
3. ⚠️ **La misma semilla no garantiza el mismo resultado entre plataformas.** Lo dice el manual
   de `random_set_seed`: los resultados son consistentes dentro de una plataforma, pero pueden
   variar entre ellas. Si tu juego comparte semillas entre jugadores (*daily runs*, códigos de
   nivel), no confíes en el RNG del motor: escribe el tuyo, con aritmética entera controlada.

### 5.3 · Distribuciones: uniforme no es lo que la gente espera

`random` es **uniforme**: todos los valores son igual de probables. Casi nunca es lo que quiere
el diseño. El daño de un arma, la altura de un árbol o el retardo de una animación se sienten
mejor con una distribución **concentrada en el centro**, con extremos raros.

**La forma barata: sumar tiradas.** La suma de varias uniformes tiende a la campana (teorema
central del límite). Es lo que hace 3d6 en los juegos de rol y es más que suficiente en un juego.

```gml
/// @func campana(_minimo, _maximo, [_tiradas])
/// @desc Valor aleatorio concentrado en el centro del rango. Con 2 tiradas es
///       un triángulo; con 3 o más ya se parece a una campana. Nunca se sale
///       del rango, a diferencia de una normal de verdad.
/// @param {Real} _minimo    Valor mínimo posible.
/// @param {Real} _maximo    Valor máximo posible.
/// @param {Real} [_tiradas] Cuántas uniformes sumar. 3 es el punto dulce.
/// @return {Real}
function campana(_minimo, _maximo, _tiradas = 3)
{
    var _suma = 0;
    for (var _i = 0; _i < _tiradas; _i++) { _suma += random(1); }
    return _minimo + (_suma / _tiradas) * (_maximo - _minimo);
}
```

**La forma exacta: Box-Muller.** Cuando necesitas una normal de verdad —dispersión de disparos
de una escopeta, ruido gaussiano, variación estadística de una simulación— la transformación de
Box-Muller convierte dos uniformes en dos normales independientes.

```gml
/// @func gauss(_media, _desviacion)
/// @desc Valor de una distribución normal, por la transformación de Box-Muller
///       (forma polar). El resultado NO tiene límites: el 99,7 % cae dentro de
///       ±3 desviaciones, pero el 0,3 % restante puede irse lejos.
///       Recórtalo con clamp() si el valor alimenta algo sensible.
/// @param {Real} _media       Centro de la distribución.
/// @param {Real} _desviacion  Desviación típica (sigma).
/// @return {Real}
function gauss(_media, _desviacion)
{
    var _u1 = random_range(0.0000001, 1);   // evitamos ln(0), que es -infinito
    var _u2 = random(1);
    var _z  = sqrt(-2 * ln(_u1)) * dcos(360 * _u2);
    return _media + _z * _desviacion;
}
```

```gml
/// Dispersión de una escopeta: la mayoría de perdigones cerca del centro
repeat (8)
{
    var _desvio = clamp(gauss(0, 4), -12, 12);     // ±12° como tope duro
    var _b = instance_create_layer(x, y, "Balas", obj_perdigon);
    _b.direction = image_angle + _desvio;
    _b.speed     = random_range(9, 11);
}
```

**Ponderada por tabla acumulada** (loot, encuentros, eventos): ya está resuelta con código
completo en
[04 · 05 §4.6 y §5.7](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md).
No la repitas.

### 5.4 · Qué distribución para qué

| Sistema | Distribución | Por qué |
|---|---|---|
| Daño de un arma | Campana estrecha (§5.3) | El jugador aprende el daño «típico»; los extremos son sabor |
| Botín de un cofre | Ponderada por tabla | Hace falta control exacto por objeto |
| Dispersión de disparos | Normal (`gauss`) recortada | El centro debe ser claramente más probable |
| Qué enemigo aparece | **Bolsa** (§5.5) | Evita rachas que parecen un bug |
| Crítico | Con memoria (§5.6) o piedad (§5.7) | La uniforme pura genera rachas que enfadan |
| Retardo de una animación de adorno | Uniforme | Desincronizar es todo lo que se pide |

### 5.5 · Bolsa aleatoria (*shuffle bag*)

El azar uniforme produce rachas: cinco espadas seguidas es perfectamente normal y el jugador lo
lee como un fallo. La **bolsa** elimina ese problema: metes todas las opciones dentro, sacas sin
reponer y solo rellenas cuando se vacía. Garantiza que en cada vuelta salga todo exactamente el
número de veces previsto. Es el mecanismo que usan las piezas del Tetris moderno (la «bolsa de
7»), y funciona igual para enemigos, cartas, frases de diálogo o pistas de música.

```gml
/// @func bolsa_crear(_contenido)
/// @desc Crea una bolsa aleatoria. `_contenido` es un array con TODOS los
///       elementos de una vuelta completa; repite un elemento para darle más
///       peso: ["espada","espada","espada","gema"] = 3 de cada 4 vueltas espada.
/// @param {Array} _contenido  Los elementos de una vuelta.
/// @return {Struct}           La bolsa, para pasársela a bolsa_sacar().
function bolsa_crear(_contenido)
{
    return {
        origen:    _contenido,
        pendiente: array_shuffle(_contenido),   // devuelve una copia barajada
        ultimo:    undefined
    };
}

/// @func bolsa_sacar(_bolsa, [_evitar_repetir])
/// @desc Saca un elemento. Cuando se vacía, se rellena y se baraja sola.
/// @param {Struct} _bolsa            La bolsa creada con bolsa_crear().
/// @param {Bool}   [_evitar_repetir] Si true, evita que el primero de una vuelta
///                                   sea igual al último de la anterior.
/// @return {Any}                     El elemento extraído.
function bolsa_sacar(_bolsa, _evitar_repetir = true)
{
    if (array_length(_bolsa.pendiente) == 0)
    {
        _bolsa.pendiente = array_shuffle(_bolsa.origen);

        // `array_pop` saca por el FINAL: el próximo en salir es el último del
        // array. La única costura visible de una bolsa es el final de una vuelta
        // pegado al principio de la siguiente; se corrige intercambiándolo con
        // el primero, que saldrá al final de esta vuelta.
        var _n = array_length(_bolsa.pendiente);
        if (_evitar_repetir && _n > 1 && _bolsa.pendiente[_n - 1] == _bolsa.ultimo)
        {
            var _tmp = _bolsa.pendiente[_n - 1];
            _bolsa.pendiente[_n - 1] = _bolsa.pendiente[0];
            _bolsa.pendiente[0] = _tmp;
        }
    }

    _bolsa.ultimo = array_pop(_bolsa.pendiente);
    return _bolsa.ultimo;
}
```

```gml
/// obj_generador_oleadas · Evento Create
bolsa_enemigos = bolsa_crear(["baba", "baba", "baba", "arquero", "arquero", "bruto"]);

/// Cada aparición
var _tipo = bolsa_sacar(bolsa_enemigos);   // en cada 6 salen 3 babas, 2 arqueros, 1 bruto
```

### 5.6 · Aleatorio «con memoria»: evitar rachas sin quitar el azar

La bolsa es determinista por vueltas. Cuando quieres conservar la incertidumbre pero suavizar
las rachas, la técnica es **penalizar lo que acaba de salir**: cada opción tiene un peso que baja
al usarse y se recupera con el tiempo.

```gml
/// @func sorteo_con_memoria(_pesos, _recientes, [_penalizacion])
/// @desc Sorteo ponderado que castiga las opciones usadas hace poco.
/// @param {Array<Real>} _pesos          Peso base de cada opción.
/// @param {Array<Real>} _recientes      Un contador por opción: cuántas veces salió
///                                      recientemente. Se decrementa fuera, con el tiempo.
/// @param {Real} [_penalizacion]        Cuánto multiplica el peso por cada uso reciente
///                                      (0.35 = cada aparición reciente lo deja al 35 %).
/// @return {Real}                       Índice elegido.
function sorteo_con_memoria(_pesos, _recientes, _penalizacion = 0.35)
{
    var _n = array_length(_pesos);
    var _total = 0;
    var _ajustados = array_create(_n, 0);

    for (var _i = 0; _i < _n; _i++)
    {
        _ajustados[_i] = _pesos[_i] * power(_penalizacion, _recientes[_i]);
        _total += _ajustados[_i];
    }
    if (_total <= 0) { return irandom(_n - 1); }   // todo penalizado: uniforme

    var _tirada = random(_total);
    var _acum = 0;
    for (var _i = 0; _i < _n; _i++)
    {
        _acum += _ajustados[_i];
        if (_tirada < _acum) { _recientes[_i] += 1; return _i; }
    }
    return _n - 1;   // sólo se llega aquí por error de redondeo en el último tramo
}
```

Los contadores de `_recientes` se bajan desde fuera —una unidad cada X segundos, o al cambiar de
sala— y eso controla cuánta memoria tiene el sistema. Con memoria 0 vuelve a ser un sorteo
ponderado normal.

### 5.7 · Crítico con piedad (*pity*)

Un crítico del 15 % significa que **una de cada 20 veces** el jugador encadena 12 golpes sin
crítico. Estadísticamente correcto, emocionalmente insoportable. La solución estándar de la
industria es la **distribución pseudoaleatoria**: la probabilidad empieza baja y sube en cada
fallo, de forma que la media a largo plazo sigue siendo la prometida pero desaparecen tanto las
rachas largas de fallo como los dobles críticos seguidos.

```gml
/// @func critico_tirar(_estado)
/// @desc Tirada de crítico con probabilidad creciente. Empieza por debajo de la
///       nominal y sube en cada fallo; al acertar se reinicia. La probabilidad
///       MEDIA a largo plazo tiende a `_estado.nominal`.
/// @param {Struct} _estado  { nominal, incremento, fallos }
/// @return {Bool}           True si es crítico.
function critico_tirar(_estado)
{
    _estado.fallos += 1;
    var _p = _estado.incremento * _estado.fallos;
    if (random(1) < _p) { _estado.fallos = 0; return true; }
    return false;
}
```

```gml
/// obj_jugador · Evento Create
/// OJO: `incremento` NO es la probabilidad nominal. Es bastante menor, porque
/// la probabilidad crece en cada fallo y hay que compensar esa acumulación.
critico = { nominal: 0.25, incremento: 0.0847, fallos: 0 };

/// Al golpear
var _dano = arma_dano;
if (critico_tirar(critico))
{
    _dano *= 2;
    global.pantalla_temblor = max(global.pantalla_temblor, 6);   // el aviso visual
}
```

Con `incremento = 0.0847` el primer golpe tiene un 8,5 % de probabilidad, el segundo un 17 %, el
tercero un 25,5 %… y a partir del duodécimo el crítico está garantizado. La media a largo plazo
es el 25 % prometido, pero **la racha larga desaparece**.

Las dos constantes verificadas contra la documentación de *Dota 2*, que es el sistema mejor
documentado de este mecanismo:

| Probabilidad nominal | Constante `incremento` (C) |
|---|---|
| 25 % | 0,0847 |
| 50 % | 0,3021 |

⚠️ Para cualquier otra probabilidad, la constante se obtiene **resolviendo numéricamente**: no
hay fórmula cerrada publicada. El camino práctico es lanzar el histograma de §5.8 sobre
`critico_tirar` y ajustar `incremento` hasta que la tasa observada coincida con la nominal.

### 5.8 · Probar que tu RNG es justo: histograma en el Debug Overlay

Ningún sistema de probabilidad se da por bueno sin medirlo. Diez mil tiradas tardan un
parpadeo, y el Debug Overlay las muestra sin salir del juego.

```gml
/// obj_probar_rng · Evento Create
caras      = 6;
resultados = array_create(caras, 0);
tiradas    = 0;
histograma = "(sin datos)";

// El método se define ANTES del botón que lo llama: así el orden de lectura
// coincide con el de ejecución. `ref_create` no admite variables locales, por
// eso `histograma` es una variable de instancia, no un `var`.
refrescar_histograma = function()
{
    if (tiradas == 0) { histograma = "(sin datos)"; return; }

    var _esperado = tiradas / caras;
    var _texto = $"Tiradas: {tiradas}   ideal por cara: {string_format(100 / caras, 2, 2)} %\n";

    for (var _i = 0; _i < caras; _i++)
    {
        var _porcentaje = resultados[_i] / tiradas * 100;
        var _desvio     = (resultados[_i] - _esperado) / _esperado * 100;
        _texto += $"{_i}: {string_repeat("#", round(_porcentaje))} "        // 1 carácter = 1 %
                + $"{string_format(_porcentaje, 2, 2)} %"
                + $"  (desvío {string_format(_desvio, 3, 1)} %)\n";
    }
    histograma = _texto;
};

tirar_muchas = function()
{
    repeat (10000)
    {
        var _cara = irandom(caras - 1);   // 0..5: OJO, irandom incluye el extremo
        resultados[_cara] += 1;
        tiradas += 1;
    }
    refrescar_histograma();
};

vista = dbg_view("Prueba de RNG", true, -1, -1, 460, 320);
dbg_section("Reparto observado");
dbg_text(ref_create(self, "histograma"));
dbg_button("10 000 tiradas más", tirar_muchas);
```

**Cómo se lee.** Con 10 000 tiradas de un dado de 6 caras, cada cara debería salir el 16,67 %.
Una desviación de ±1,5 puntos es ruido normal; una cara sistemáticamente por debajo del 15 % en
varias ejecuciones seguidas señala un error en tu código —casi siempre un `irandom(n)` donde
debía ir `irandom(n - 1)`, o un `<` donde debía ir un `<=` al recorrer la tabla acumulada—.
Este mismo esquema sirve para verificar una tabla de loot, un generador de mazmorras (contando
tipos de sala) o el sistema de piedad de §5.7.

---

## 6 · Geometría de colisión

### 6.1 · Qué trae GameMaker y hasta dónde llega

Antes de escribir geometría a mano, comprueba si el motor ya lo resuelve. Estas funciones son
nativas, están verificadas y son más rápidas que cualquier cosa que escribas en GML:

| Función nativa | Qué hace | Devuelve |
|---|---|---|
| `point_in_rectangle(px, py, x1, y1, x2, y2)` | Punto dentro de un rectángulo alineado | `Bool` |
| `point_in_circle(px, py, cx, cy, r)` | Punto dentro de un círculo | `Bool` |
| `point_in_triangle(px, py, x1, y1, x2, y2, x3, y3)` | Punto dentro de un triángulo | `Bool` |
| `rectangle_in_rectangle(sx1, sy1, sx2, sy2, dx1, dy1, dx2, dy2)` | Dos rectángulos | **`0`** = nada · **`1`** = origen totalmente dentro · **`2`** = solapan |
| `collision_line(x1, y1, x2, y2, obj, prec, notme)` | ¿Hay una instancia en esta línea? | `Id.Instance` o `noone` |
| `place_meeting(x, y, obj)` | ¿Chocaría la instancia si estuviera ahí? | `Bool` |

> 🔺 `rectangle_in_rectangle` **no devuelve un booleano**: devuelve 0, 1 o 2. Escribir
> `if (rectangle_in_rectangle(...))` funciona por accidente (1 y 2 son *truthy*), pero
> `if (... == 1)` significa «totalmente contenido», no «se tocan». Es una fuente clásica de
> bugs de cámara y de culling.

Lo que **no** trae el motor y hay que escribirse: punto en polígono arbitrario, intersección
segmento-segmento, distancia punto-segmento, segmento contra círculo y cajas rotadas. Están
abajo. El sistema general de colisiones (máscaras, `move_and_collide`, tilemaps, *collision
space*) está en
[01 · 08 — Movimiento y colisiones](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md);
aquí solo va la geometría pura, la que sirve cuando **no hay instancia** que consultar.

### 6.2 · Cuándo basta con las nativas

- **Rectángulo alineado**: siempre. `point_in_rectangle` con `bbox_left/top/right/bottom`.
- **Radio de efecto de una explosión**: `point_in_circle`, o mejor la comparación de cuadrados
  de §1.3 si es dentro de un bucle grande.
- **Área triangular** (un cono de disparo aproximado, una zona de un minimapa):
  `point_in_triangle`. Y cualquier polígono convexo se descompone en triángulos.

```gml
/// ¿El ratón está sobre esta instancia? (bounding box, sin precisión de sprite)
if (point_in_rectangle(mouse_x, mouse_y, bbox_left, bbox_top, bbox_right, bbox_bottom))
{
    resaltado = true;
}
```

### 6.3 · Punto en polígono (*ray casting* par-impar)

Para un polígono arbitrario —una zona dibujada a mano, una región de un mapa, un área de
trigger no rectangular— el algoritmo estándar es el de **paridad de cruces**: se lanza un rayo
desde el punto hacia el infinito y se cuentan las aristas que cruza. Impar = dentro, par = fuera.
Funciona con polígonos cóncavos y con agujeros, y no necesita que los vértices estén en ningún
orden concreto.

```gml
/// @func dentro_de_poligono(_px, _py, _vertices)
/// @desc Ray casting con regla par-impar (algoritmo PNPOLY de W. R. Franklin).
///       Vale para polígonos cóncavos. Los vértices se cierran solos: no repitas
///       el primero al final.
/// @param {Real} _px  X del punto a comprobar.
/// @param {Real} _py  Y del punto a comprobar.
/// @param {Array<Struct>} _vertices  Array de structs con .x y .y, en orden.
/// @return {Bool}     True si el punto está dentro.
function dentro_de_poligono(_px, _py, _vertices)
{
    var _n = array_length(_vertices);
    var _dentro = false;

    // j sigue a i con un vértice de retraso: recorre las aristas (j -> i).
    var _j = _n - 1;
    for (var _i = 0; _i < _n; _i++)
    {
        var _vi = _vertices[_i];
        var _vj = _vertices[_j];

        // ¿La arista cruza la horizontal que pasa por el punto?
        if ((_vi.y > _py) != (_vj.y > _py))
        {
            // X del corte de la arista con esa horizontal.
            var _corte = (_vj.x - _vi.x) * (_py - _vi.y) / (_vj.y - _vi.y) + _vi.x;
            if (_px < _corte) { _dentro = !_dentro; }
        }
        _j = _i;
    }
    return _dentro;
}
```

La comparación `(_vi.y > _py) != (_vj.y > _py)` es la clave y no es cosmética: garantiza que un
vértice exactamente a la altura del punto se cuente **una sola vez**, que es el caso límite que
rompe las implementaciones ingenuas.

### 6.4 · Distancia de un punto a un segmento

No es lo mismo que la distancia a la recta infinita. Un enemigo a 400 px de la prolongación de
un láser de 50 px de largo no está en peligro. La operación es: proyectar el punto sobre el
segmento, **recortar el parámetro a `[0,1]`** y medir hasta ahí.

```gml
/// @func distancia_punto_segmento(_px, _py, _ax, _ay, _bx, _by)
/// @desc Distancia mínima del punto P al SEGMENTO AB (no a la recta infinita).
/// @param {Real} _px  X del punto.
/// @param {Real} _py  Y del punto.
/// @param {Real} _ax  X del extremo A.
/// @param {Real} _ay  Y del extremo A.
/// @param {Real} _bx  X del extremo B.
/// @param {Real} _by  Y del extremo B.
/// @return {Real}     Distancia en píxeles.
function distancia_punto_segmento(_px, _py, _ax, _ay, _bx, _by)
{
    var _dx = _bx - _ax;
    var _dy = _by - _ay;
    var _largo2 = _dx * _dx + _dy * _dy;

    // Segmento degenerado (A y B coinciden): es una distancia punto a punto.
    if (_largo2 <= math_get_epsilon()) { return point_distance(_px, _py, _ax, _ay); }

    // u = proyección de AP sobre AB, normalizada. El clamp lo confina al segmento.
    var _u = clamp(((_px - _ax) * _dx + (_py - _ay) * _dy) / _largo2, 0, 1);

    return point_distance(_px, _py, _ax + _u * _dx, _ay + _u * _dy);
}
```

Usos: grosor real de un láser o de una estela, «¿el jugador está pegado a esta pared?», detección
de proximidad a un camino, y el corazón de la colisión cápsula (§6.6).

### 6.5 · Intersección segmento-segmento

La pregunta «¿se cruzan estos dos segmentos, y dónde?» aparece en cuanto hay una bala rápida
(que en un frame salta por encima de una pared fina), un ataque en barrido, o una comprobación
de línea de visión contra geometría que no son instancias.

```gml
/// @func cortan_segmentos(_ax, _ay, _bx, _by, _cx, _cy, _dx, _dy)
/// @desc ¿Se cortan los segmentos AB y CD? Devuelve el punto de corte o undefined.
///       Resuelve el sistema A + u·AB = C + v·CD y comprueba que u y v estén en [0,1].
/// @param {Real} _ax  X del inicio del primer segmento.
/// @param {Real} _ay  Y del inicio del primer segmento.
/// @param {Real} _bx  X del final del primer segmento.
/// @param {Real} _by  Y del final del primer segmento.
/// @param {Real} _cx  X del inicio del segundo segmento.
/// @param {Real} _cy  Y del inicio del segundo segmento.
/// @param {Real} _dx  X del final del segundo segmento.
/// @param {Real} _dy  Y del final del segundo segmento.
/// @return {Struct|Undefined}  { x, y, u } donde u es 0..1 sobre AB, o undefined.
function cortan_segmentos(_ax, _ay, _bx, _by, _cx, _cy, _dx, _dy)
{
    var _r_x = _bx - _ax,  _r_y = _by - _ay;    // vector del primer segmento
    var _s_x = _dx - _cx,  _s_y = _dy - _cy;    // vector del segundo

    var _den = _r_x * _s_y - _r_y * _s_x;       // producto cruzado 2D (§2.5)
    if (abs(_den) <= math_get_epsilon()) { return undefined; }   // paralelos o colineales

    var _qp_x = _cx - _ax,  _qp_y = _cy - _ay;
    var _u = (_qp_x * _s_y - _qp_y * _s_x) / _den;   // parámetro sobre AB
    var _v = (_qp_x * _r_y - _qp_y * _r_x) / _den;   // parámetro sobre CD

    if (_u < 0 || _u > 1 || _v < 0 || _v > 1) { return undefined; }   // se cruzan fuera

    return { x: _ax + _u * _r_x, y: _ay + _u * _r_y, u: _u };
}
```

> 💡 El campo `u` es lo que hace útil esta función frente a un simple `true/false`: al comprobar
> una bala contra varias paredes, el **impacto real es el de menor `u`**, el más cercano al
> origen. Sin eso, la bala atraviesa la pared cercana y golpea la lejana.

```gml
/// La bala se ha movido de (x_prev, y_prev) a (x, y). ¿Qué pared toca primero?
var _mejor_u = 2;      // fuera de rango: cualquier corte real será menor
var _impacto = undefined;

for (var _i = 0; _i < array_length(global.paredes); _i++)
{
    var _p = global.paredes[_i];
    var _c = cortan_segmentos(x_prev, y_prev, x, y, _p.ax, _p.ay, _p.bx, _p.by);
    if (_c != undefined && _c.u < _mejor_u) { _mejor_u = _c.u; _impacto = _c; }
}
if (_impacto != undefined) { x = _impacto.x; y = _impacto.y; instance_destroy(); }
```

### 6.6 · Segmento contra círculo

Un enemigo circular contra un disparo instantáneo, o una bala con radio: el problema se reduce
a la distancia punto-segmento de §6.4, que ya está resuelta.

```gml
/// @func segmento_corta_circulo(_ax, _ay, _bx, _by, _cx, _cy, _radio)
/// @desc ¿El segmento AB toca el círculo de centro C y radio dado?
///       También vale para una bala GRUESA contra un punto: suma los dos radios.
/// @param {Real} _ax     X del inicio del segmento.
/// @param {Real} _ay     Y del inicio del segmento.
/// @param {Real} _bx     X del final del segmento.
/// @param {Real} _by     Y del final del segmento.
/// @param {Real} _cx     X del centro del círculo.
/// @param {Real} _cy     Y del centro del círculo.
/// @param {Real} _radio  Radio del círculo.
/// @return {Bool}
function segmento_corta_circulo(_ax, _ay, _bx, _by, _cx, _cy, _radio)
{
    return (distancia_punto_segmento(_cx, _cy, _ax, _ay, _bx, _by) <= _radio);
}
```

Esto resuelve de una vez el **túnel** (*tunneling*): una bala que a 40 px por frame se salta un
enemigo de 16 px de ancho no lo detecta con `place_meeting`, pero sí comprobando el **segmento
recorrido** en ese frame contra el círculo del enemigo.

### 6.7 · AABB frente a OBB

| | **AABB** (caja alineada con los ejes) | **OBB** (caja orientada) |
|---|---|---|
| Coste | 4 comparaciones | Proyección sobre 4 ejes |
| Rota con el objeto | No: la caja crece al girar | Sí |
| En GameMaker | `bbox_*` + `rectangle_in_rectangle` | A mano |
| Cuándo | Casi siempre | Naves, coches, plataformas inclinadas |

```gml
/// @func cajas_se_solapan(_ax1, _ay1, _ax2, _ay2, _bx1, _by1, _bx2, _by2)
/// @desc Solapamiento de dos cajas ALINEADAS con los ejes. Cuatro comparaciones.
///       Se lee mejor por la negativa: no se tocan si una está entera a un lado.
/// @param {Real} _ax1  Izquierda de la caja A.
/// @param {Real} _ay1  Arriba de la caja A.
/// @param {Real} _ax2  Derecha de la caja A.
/// @param {Real} _ay2  Abajo de la caja A.
/// @param {Real} _bx1  Izquierda de la caja B.
/// @param {Real} _by1  Arriba de la caja B.
/// @param {Real} _bx2  Derecha de la caja B.
/// @param {Real} _by2  Abajo de la caja B.
/// @return {Bool}
function cajas_se_solapan(_ax1, _ay1, _ax2, _ay2, _bx1, _by1, _bx2, _by2)
{
    return !(_ax2 < _bx1 || _bx2 < _ax1 || _ay2 < _by1 || _by2 < _ay1);
}
```

Para cajas **rotadas** se usa el teorema de los ejes separadores: dos convexos no se tocan si
existe **alguna** dirección en la que sus proyecciones no se solapan. Con dos rectángulos basta
probar cuatro direcciones (los dos ejes de cada caja).

```gml
/// @func caja_rotada_solapa(_a, _b)
/// @desc Teorema de los ejes separadores para dos rectángulos orientados.
///       Cada caja es { x, y, ancho, alto, angulo } con el origen en su CENTRO.
/// @param {Struct} _a  Primera caja.
/// @param {Struct} _b  Segunda caja.
/// @return {Bool}      True si se solapan.
function caja_rotada_solapa(_a, _b)
{
    var _cajas = [_a, _b];

    // Sólo hacen falta 4 ejes: los dos de cada caja.
    for (var _c = 0; _c < 2; _c++)
    {
        var _base = _cajas[_c].angulo;
        for (var _e = 0; _e < 2; _e++)
        {
            var _ang = _base + _e * 90;
            var _ex  = lengthdir_x(1, _ang);
            var _ey  = lengthdir_y(1, _ang);

            // Proyección del centro y "radio" de cada caja sobre este eje.
            var _pa = dot_product(_a.x, _a.y, _ex, _ey);
            var _ra = abs(dot_product(lengthdir_x(_a.ancho * 0.5, _a.angulo),
                                      lengthdir_y(_a.ancho * 0.5, _a.angulo), _ex, _ey))
                    + abs(dot_product(lengthdir_x(_a.alto  * 0.5, _a.angulo + 90),
                                      lengthdir_y(_a.alto  * 0.5, _a.angulo + 90), _ex, _ey));

            var _pb = dot_product(_b.x, _b.y, _ex, _ey);
            var _rb = abs(dot_product(lengthdir_x(_b.ancho * 0.5, _b.angulo),
                                      lengthdir_y(_b.ancho * 0.5, _b.angulo), _ex, _ey))
                    + abs(dot_product(lengthdir_x(_b.alto  * 0.5, _b.angulo + 90),
                                      lengthdir_y(_b.alto  * 0.5, _b.angulo + 90), _ex, _ey));

            // Si en ESTE eje no se solapan, ya está: no colisionan.
            if (abs(_pa - _pb) > _ra + _rb) { return false; }
        }
    }
    return true;   // ningún eje los separa
}
```

> 💡 GameMaker ya rota la máscara de colisión de un sprite con `image_angle`, con la regla de los
> dos sprites que explica
> [01 · 08 §4](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md). El OBB a mano
> solo hace falta cuando la caja **no** es un sprite: zonas lógicas, hitboxes de datos, geometría
> generada.

### 6.8 · `collision_line`: cuándo basta y cuándo no

`collision_line` es la forma barata y verificada de preguntar «¿hay algo entre estos dos puntos?».
Es lo correcto para línea de visión, para raycasting sencillo y para detectar suelo por delante.

```gml
/// ¿Ve el enemigo al jugador? Cono (§2.4) + comprobación de muros.
if (en_cono_vision(x, y, image_angle, 90, 320, obj_jugador.x, obj_jugador.y))
&& (collision_line(x, y, obj_jugador.x, obj_jugador.y, obj_muro, false, true) == noone)
{
    estado = "persiguiendo";
}
```

Sus tres límites, y qué usar en su lugar:

| Límite | Alternativa |
|---|---|
| Devuelve **una instancia cualquiera** de las que cruza, no la más cercana | `collision_line_list(..., ordered = true)` — ver abajo. Solo si necesitas el **punto exacto** de impacto (no solo qué instancia), recorre sus aristas con `cortan_segmentos` (§6.5) |
| Solo detecta **instancias**, no tilemaps ni geometría de datos | `tilemap_get_at_pixel` a lo largo de la línea, o §6.5 contra tus propias aristas |
| Con `prec = true` exige que **el sprite** tenga colisiones precisas activadas | Comprobarlo en el editor del sprite; si no, se comporta como bounding box sin avisar |

**«La más cercana» ya lo resuelve el motor, no hace falta ordenar a mano.**
`collision_line_list(x1, y1, x2, y2, obj, prec, notme, list, ordered)` acepta un último
argumento, `ordered`, que **ordena el resultado por distancia desde el inicio de la línea**. Con
`ordered = true`, el primer elemento de la lista es ya la instancia más cercana:

```gml
var _lista = ds_list_create();
var _n = collision_line_list(x, y, obj_jugador.x, obj_jugador.y, obj_muro, false, true,
                              _lista, true);              // ← ordered = true

if (_n > 0)
{
    var _mas_cercano = _lista[| 0];   // ya es el más cercano al INICIO de la línea
}
ds_list_destroy(_lista);
```

Ejemplo real, con penetración y todo, en
[04 · 34 §5.4 «Arma hitscan: penetración ordenada y caída de daño»](../04%20-%20Recetas%20por%20g%C3%A9nero/34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munici%C3%B3n%20y%20bal%C3%ADstica.md).

### 6.9 · Colisión contra paths y curvas

Ni un `path` del IDE ni una Bézier (§4.6) ni una Catmull-Rom (§4.7) son formas de colisión: los
`collision_*` nativos no saben qué es un `path`, y una curva calculada por fórmula no es un
objeto contra el que preguntar. El truco es siempre el mismo: **muestrear la curva en una
polilínea** (un array de puntos `{x, y}`) y reutilizar lo que ya existe en este documento para
segmentos — §6.4 para «¿a qué distancia estoy?» y §6.5 para «¿me cruza?».

**Muestrear un `path` con `path_get_x`/`path_get_y`:**

```gml
/// @func path_muestrear(_path, _muestras)
/// @desc Convierte un path del IDE en una polilínea: un array de puntos {x, y}
///       tomados a intervalos regulares de PROGRESO (path_get_x/y usan 0..1,
///       no píxeles — ver path_get_length si necesitas la longitud real).
/// @param {Asset.GMPath} _path   El path a muestrear.
/// @param {Real} _muestras       Cuántos puntos generar (mínimo 2).
/// @return {Array<Struct>}       [{x, y}, ...]
function path_muestrear(_path, _muestras)
{
    var _puntos = array_create(_muestras);
    for (var _i = 0; _i < _muestras; _i++)
    {
        var _t = _i / (_muestras - 1);
        _puntos[_i] = { x: path_get_x(_path, _t), y: path_get_y(_path, _t) };
    }
    return _puntos;
}
```

**¿A qué distancia del path estoy?** — reutilizando `distancia_punto_segmento` (§6.4) tramo a
tramo: la distancia mínima a la polilínea es la menor de las distancias a cada uno de sus
segmentos.

```gml
/// @func distancia_a_polilinea(_px, _py, _puntos)
/// @desc Distancia mínima de un punto a una polilínea (path o curva muestreada).
/// @param {Real} _px  @param {Real} _py  El punto a medir.
/// @param {Array<Struct>} _puntos        Polilínea: array de {x, y}.
/// @return {Real}
function distancia_a_polilinea(_px, _py, _puntos)
{
    var _minima = infinity;
    for (var _i = 0; _i < array_length(_puntos) - 1; _i++)
    {
        var _d = distancia_punto_segmento(_px, _py,
            _puntos[_i].x, _puntos[_i].y, _puntos[_i + 1].x, _puntos[_i + 1].y);
        if (_d < _minima) { _minima = _d; }
    }
    return _minima;
}
```

```gml
/// obj_escolta · Step — vuelve a la ruta si se aleja demasiado del camino de patrulla
if (distancia_a_polilinea(x, y, ruta_muestreada) > 48)
{
    estado = "regresando_a_la_ruta";
}
```

**¿Me cruza?** — la versión de §6.5 (`cortan_segmentos`) tramo a tramo, quedándose con la `u`
menor exactamente igual que hace `04 · 34 §5.4` con paredes: el primer tramo que corta el
proyectil es el que importa.

```gml
/// @func polilinea_corta_segmento(_puntos, _ax, _ay, _bx, _by)
/// @desc ¿El segmento AB corta la polilínea? Recorre sus tramos con
///       cortan_segmentos (§6.5) y se queda con el impacto de menor u: el
///       primero que tocaría un proyectil que viaja de A a B.
/// @return {Struct|Undefined}  { x, y, u } o undefined si no hay corte.
function polilinea_corta_segmento(_puntos, _ax, _ay, _bx, _by)
{
    var _mejor_u = 2;      // fuera de rango: cualquier corte real será menor
    var _impacto = undefined;

    for (var _i = 0; _i < array_length(_puntos) - 1; _i++)
    {
        var _c = cortan_segmentos(_ax, _ay, _bx, _by,
            _puntos[_i].x, _puntos[_i].y, _puntos[_i + 1].x, _puntos[_i + 1].y);
        if (_c != undefined && _c.u < _mejor_u) { _mejor_u = _c.u; _impacto = _c; }
    }
    return _impacto;
}
```

Uso típico: un láser o una barrera que sigue la forma de un `path` en vez de ser recta — la bala
prueba contra la polilínea muestreada igual que probaría contra una pared.

**Lo mismo contra una Bézier o una Catmull-Rom.** No hace falta código nuevo: se muestrea la
curva con las funciones de §4.6/§4.7 en vez de `path_get_x/y`, y `distancia_a_polilinea()` /
`polilinea_corta_segmento()` funcionan igual sobre el resultado, porque solo esperan un array de
`{x, y}`:

```gml
/// @func curva_muestrear(_p0, _p1, _p2, _muestras)
/// @desc Muestrea una Bézier cuadrática (§4.6) en una polilínea de puntos {x, y}.
///       Para la cúbica, sustituye bezier_cuadratica por bezier_cubica (con _p3).
///       Para una ruta Catmull-Rom de varios tramos (§4.7), sustituye por
///       ruta_evaluar(_puntos, _t) — ya devuelve un struct {x, y} por muestra.
/// @return {Array<Struct>}
function curva_muestrear(_p0, _p1, _p2, _muestras)
{
    var _puntos = array_create(_muestras);
    for (var _i = 0; _i < _muestras; _i++)
    {
        var _t = _i / (_muestras - 1);
        _puntos[_i] = {
            x: bezier_cuadratica(_p0.x, _p1.x, _p2.x, _t),
            y: bezier_cuadratica(_p0.y, _p1.y, _p2.y, _t)
        };
    }
    return _puntos;
}
```

> ⚠️ **Cuántas muestras hacen falta no tiene una respuesta cerrada**: depende de lo cerrada que
> sea la curva y de la distancia mínima de colisión que necesites. Una guía práctica y barata:
> para un `path`, `path_get_length(_path) / 8` da aproximadamente una muestra cada 8 píxeles: en
> la mayoría de curvas de patrulla o cámara eso ya es indistinguible de la curva real.
>
> 💡 **Muestrea una vez, no cada Step.** La polilínea de un `path` o de una curva con control
> points fijos no cambia frame a frame: genérala en el `Create` (o al cargar el nivel) y guarda
> el array, igual que ya se cachea `tilemap_suelo` en
> [01 · 08](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md). Volver a muestrear
> en cada `Step` es trabajo repetido para un resultado que no ha cambiado.

---

## 7 · Rejillas y coordenadas

### 7.1 · Mundo ↔ celda ↔ mundo

La conversión más usada de todo el desarrollo 2D, y la que más veces se escribe mal. **Siempre
`floor`, nunca `round` ni `div`**: `round(-0.4)` da `0`, así que las coordenadas negativas
colapsan dos celdas en una y el mapa se rompe a la izquierda del origen.

```gml
#macro TILE 16

/// @func celda_desde_mundo(_valor, [_tam])
/// @desc Píxel del mundo -> índice de celda. Con `floor`, para que funcione
///       también con coordenadas negativas.
/// @param {Real} _valor  Coordenada en píxeles.
/// @param {Real} [_tam]  Tamaño de la celda.
/// @return {Real}        Índice de celda (entero, puede ser negativo).
function celda_desde_mundo(_valor, _tam = TILE)
{
    return floor(_valor / _tam);
}

/// @func mundo_desde_celda(_celda, [_tam], [_centrado])
/// @desc Índice de celda -> píxel del mundo.
/// @param {Real} _celda      Índice de celda.
/// @param {Real} [_tam]      Tamaño de la celda.
/// @param {Bool} [_centrado] True devuelve el CENTRO; false, la esquina superior izquierda.
/// @return {Real}            Coordenada en píxeles.
function mundo_desde_celda(_celda, _tam = TILE, _centrado = true)
{
    return _celda * _tam + (_centrado ? _tam * 0.5 : 0);
}
```

> 🔺 El error de la **esquina frente al centro** se manifiesta como «todo está medio tile
> desplazado». Colocar una instancia en `mundo_desde_celda(c)` sin centrar la pone en la esquina;
> si además el origen del sprite está en el centro, el desfase es de medio tile en las dos
> direcciones. Decide una convención por proyecto y escríbela en `scr_config`.

### 7.2 · Ajustar a la rejilla (*snapping*)

`snap(valor, incremento)` ya está escrita en
[`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml): es
`round(_valor / _incremento) * _incremento`. Es lo que quieres para un editor de niveles o para
colocar una torreta. Ojo con la diferencia:

| Operación | Resultado con `TILE = 16` y `x = 40` | Para qué |
|---|---|---|
| `snap(x, TILE)` | `48` (el múltiplo **más cercano**) | Editor, colocar objetos, alinear UI |
| `celda_desde_mundo(x) * TILE` | `32` (la esquina de **su** celda) | Lógica de rejilla, pathfinding |
| `mundo_desde_celda(celda_desde_mundo(x))` | `40` (el **centro** de su celda) | Colocar sobre el tile pisado |

### 7.3 · Isométrico (rombo 2:1)

En una vista isométrica, la rejilla lógica sigue siendo cuadrada: lo único que cambia es cómo se
proyecta a pantalla. Con rombos de `ancho × alto` (el clásico 2:1 son `64 × 32`):

```gml
#macro ISO_ANCHO 64
#macro ISO_ALTO  32

/// @func iso_desde_celda(_col, _fila)
/// @desc Celda de la rejilla lógica -> píxel en pantalla, proyección isométrica.
///       El resultado es el CENTRO del rombo.
/// @param {Real} _col   Columna de la rejilla.
/// @param {Real} _fila  Fila de la rejilla.
/// @return {Struct}     { x, y } en píxeles.
function iso_desde_celda(_col, _fila)
{
    return {
        x: (_col - _fila) * (ISO_ANCHO * 0.5),
        y: (_col + _fila) * (ISO_ALTO  * 0.5)
    };
}

/// @func celda_desde_iso(_px, _py)
/// @desc Píxel en pantalla -> celda de la rejilla lógica. La inversa de la anterior.
///       Devuelve valores fraccionarios: aplica floor() para obtener la celda.
/// @param {Real} _px  X en píxeles (relativa al origen de la rejilla).
/// @param {Real} _py  Y en píxeles.
/// @return {Struct}   { col, fila }, sin redondear.
function celda_desde_iso(_px, _py)
{
    var _a = _px / (ISO_ANCHO * 0.5);
    var _b = _py / (ISO_ALTO  * 0.5);
    return { col: (_a + _b) * 0.5, fila: (_b - _a) * 0.5 };
}
```

```gml
/// ¿Sobre qué casilla está el ratón?
var _c = celda_desde_iso(mouse_x - origen_x, mouse_y - origen_y);
var _col  = floor(_c.col);
var _fila = floor(_c.fila);
```

> 💡 **El orden de dibujado es el otro problema del isométrico**, y no es matemático sino de
> `depth`: se pinta de arriba abajo, con `depth = -(col + fila)`. Si dos objetos comparten
> celda, hace falta un desempate. La organización de capas y profundidad está en
> [01 · 10 — Rooms, capas, cámaras y viewports](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md).

#### 7.3.1 · Colisionar en la rejilla lógica, no en pantalla

El error clásico es llamar a `place_meeting`/`instance_position` con las coordenadas de
**pantalla**: el rombo distorsiona las distancias (una casilla "más lejos" en `y` de pantalla
puede estar más cerca en la rejilla que una vecina en `x`), así que las máscaras de colisión
rectangulares/circulares miden mal quién está al lado de quién. La solución es la misma que en
7.1: **la lógica de juego vive en `(col, fila)`, no en píxeles.**

```gml
#macro ISO_SIN_OCUPAR -1

/// obj_control · Create
grid_ocupacion = ds_grid_create(ancho_mapa, alto_mapa);
ds_grid_clear(grid_ocupacion, ISO_SIN_OCUPAR);

/// @func iso_celda_ocupada(_col, _fila)
/// @desc Consulta la rejilla lógica, no la pantalla: es lo que hay que
///       llamar en vez de place_meeting/instance_position en isométrico.
function iso_celda_ocupada(_col, _fila)
{
    if (_col < 0 || _fila < 0 || _col >= ds_grid_width(grid_ocupacion)
        || _fila >= ds_grid_height(grid_ocupacion)) return true; // fuera de mapa, "ocupado"
    return ds_grid_get(grid_ocupacion, _col, _fila) != ISO_SIN_OCUPAR;
}

/// obj_unidad · intentar mover a una celda vecina
var _col_destino  = mi_col + _dcol;
var _fila_destino = mi_fila + _dfila;
if (!iso_celda_ocupada(_col_destino, _fila_destino))
{
    ds_grid_set(grid_ocupacion, mi_col, mi_fila, ISO_SIN_OCUPAR);
    mi_col  = _col_destino;
    mi_fila = _fila_destino;
    ds_grid_set(grid_ocupacion, mi_col, mi_fila, id);

    var _p = iso_desde_celda(mi_col, mi_fila);
    x = _p.x;
    y = _p.y;
}
```

`place_meeting` sigue siendo válido para colisiones **finas** dentro de una misma escena (un
proyectil contra un personaje, ambos ya convertidos a píxeles de pantalla): lo que hay que
evitar es usarlo para decidir **adyacencia de rejilla**, que es un problema de `(col, fila)`,
no de bounding boxes en pantalla. Para pathfinding sobre esta misma rejilla, ver
[38 · Pathfinding avanzado](../04%20-%20Recetas%20por%20g%C3%A9nero/38%20-%20Pathfinding%20avanzado%20-%20flow%20fields%2C%20JPS%20y%20plataformas.md).

#### 7.3.2 · La máscara `Diamond` para las siluetas del tile

Cuando sí hace falta una máscara de colisión en píxeles de pantalla (por ejemplo, para que el
cursor solo "entre" en el rombo visible del tile y no en su bounding box cuadrado), GameMaker
trae un modo de máscara pensado exactamente para esto: **`bboxkind_diamond`**, seleccionable en
las propiedades de colisión del sprite (o por código con `sprite_collision_mask`). Recorta la
máscara a la silueta del rombo en vez del rectángulo que lo envuelve:

```gml
/// forzar la máscara Diamond en un sprite de tile isométrico ya cargado
sprite_collision_mask(
    spr_tile_iso,
    true,               // sepmasks: una máscara por subimagen
    bboxmode_automatic,  // recorta al contenido no transparente
    0, 0, 0, 0,           // bbleft/top/right/bottom: ignorados en modo automático
    bboxkind_diamond,
    0                     // tolerance: alfa mínimo para contar como "sólido"
);
```

Está documentada con su coste real (más cara que `Ellipse`, más barata que `Precise`) en
[01 · 08 — Movimiento y colisiones §5](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md):
úsala solo donde la silueta importa (el tile que el cursor puede seleccionar), no en toda la
capa de suelo — con miles de tiles el coste de `Diamond` frente a `Rectangle` se nota.

#### 7.3.3 · Desempate de `depth` cuando dos objetos comparten celda

`depth = -(col + fila)` ordena las **celdas**, pero dentro de la misma celda pueden convivir
varios objetos (un personaje de pie sobre una alfombra, dos unidades que se cruzan un instante).
El desempate necesita una segunda componente que no cambie el orden entre celdas distintas, solo
dentro de la misma:

```gml
/// obj_entidad_iso · Step (o al reposicionarse)
// prioridad de capa: 0 = suelo/decoración, 1 = props sobre el suelo, 2 = unidades, 3 = VFX
#macro ISO_CAPA_UNIDAD 2

depth = -(mi_col + mi_fila) * 100 - ISO_CAPA_UNIDAD * 10 - (y / room_height);
```

El término `(y / room_height)` es un desempate fino: un valor entre 0 y 1 que rompe empates
exactos entre instancias de la **misma** capa en la **misma** celda usando su posición vertical
real en pantalla (más abajo en pantalla = más cerca de la cámara = se dibuja después). Con el
multiplicador `× 100` para la celda y `× 10` para la capa, ese término fino nunca puede invertir
el orden entre celdas o capas distintas — solo decide el caso raro de un empate real.

> ⚠️ Si dos unidades ocupan exactamente la misma celda y capa con la misma `y`, el desempate
> anterior no distingue entre ellas: añade `id` como último criterio
> (`... - (y / room_height) - (id / 100000000)`) si el orden debe ser además determinista entre
> ejecuciones.

#### 7.3.4 · Offset por altura (elevación)

Cuando el mapa tiene desniveles (una plataforma elevada, un personaje saltando), la posición
**lógica** sigue siendo `(col, fila)` — la elevación no mueve de celda — pero la posición **en
pantalla** sí debe desplazarse hacia arriba, y el orden de dibujado debe tenerlo en cuenta o los
objetos elevados se dibujan "detrás" de lo que en realidad tienen delante:

```gml
/// @func iso_desde_celda_con_altura(_col, _fila, _altura)
/// @desc Como iso_desde_celda, pero desplaza la Y de pantalla hacia arriba
///       según la altura lógica (en "niveles", no en píxeles).
/// @param {Real} _altura  Nivel de elevación (0 = suelo).
function iso_desde_celda_con_altura(_col, _fila, _altura)
{
    var _base = iso_desde_celda(_col, _fila);
    return {
        x: _base.x,
        y: _base.y - (_altura * ISO_ALTO_ESCALON)
    };
}
```

Con `ISO_ALTO_ESCALON` como constante propia (por ejemplo, la mitad de `ISO_ALTO`: cuánto sube
la silueta en pantalla por cada nivel de elevación). Dos consecuencias que hay que resolver a
la vez:

- **La colisión de rejilla (7.3.1) no cambia**: `iso_celda_ocupada` sigue mirando `(col, fila)`,
  no la altura. Si el juego necesita que la altura también bloquee el paso (no se puede subir
  una pared de 3 niveles de un paso), esa comprobación es aparte: compara la diferencia de
  altura entre celda origen y destino contra un máximo permitido, no la mezcles con la
  ocupación.
- **El `depth` de 7.3.3 necesita el término de altura**, o un objeto elevado que debería tapar
  a uno del suelo se dibuja mal:

```gml
depth = -(mi_col + mi_fila) * 100 - ISO_CAPA_UNIDAD * 10 - mi_altura - (y / room_height);
```

Réstale la altura (no la sumes): un objeto más alto debe dibujarse **después** —encima— de lo
que tiene en el suelo en su misma celda, y `depth` más negativo se dibuja después.

### 7.4 · Hexágonos

Los hexágonos tienen dos orientaciones —**punta arriba** (*pointy top*) y **lado plano arriba**
(*flat top*)— y varios sistemas de coordenadas. El que hace la matemática simple es el sistema
**axial** `(q, r)`: dos ejes, como una rejilla cuadrada deformada. `size` es la distancia del
centro a un vértice (el radio del círculo circunscrito).

```gml
#macro HEX_SIZE 32
#macro RAIZ3    1.7320508075688772   // sqrt(3), precalculada

/// @func hex_a_pixel(_q, _r, [_punta_arriba])
/// @desc Coordenada axial de hexágono -> centro del hexágono en píxeles.
///       Fórmulas de la guía «Hexagonal Grids» de Red Blob Games.
/// @param {Real} _q  Coordenada axial q.
/// @param {Real} _r  Coordenada axial r.
/// @param {Bool} [_punta_arriba]  True = punta arriba; false = lado plano arriba.
/// @return {Struct}  { x, y } del centro, en píxeles.
function hex_a_pixel(_q, _r, _punta_arriba = true)
{
    if (_punta_arriba)
    {
        return { x: HEX_SIZE * (RAIZ3 * _q + RAIZ3 * 0.5 * _r),
                 y: HEX_SIZE * (1.5 * _r) };
    }
    return { x: HEX_SIZE * (1.5 * _q),
             y: HEX_SIZE * (RAIZ3 * 0.5 * _q + RAIZ3 * _r) };
}

/// @func pixel_a_hex(_px, _py, [_punta_arriba])
/// @desc Píxel -> coordenada axial FRACCIONARIA. Hay que redondearla con
///       redondear_hex(): el redondeo normal se equivoca cerca de los bordes.
/// @param {Real} _px  X en píxeles, relativa al centro del hexágono (0,0).
/// @param {Real} _py  Y en píxeles.
/// @param {Bool} [_punta_arriba]  Misma orientación que en hex_a_pixel.
/// @return {Struct}   { q, r } sin redondear.
function pixel_a_hex(_px, _py, _punta_arriba = true)
{
    var _x = _px / HEX_SIZE;
    var _y = _py / HEX_SIZE;
    if (_punta_arriba)
    {
        return { q: (RAIZ3 / 3) * _x - (1 / 3) * _y,  r: (2 / 3) * _y };
    }
    return { q: (2 / 3) * _x,  r: -(1 / 3) * _x + (RAIZ3 / 3) * _y };
}

/// @func redondear_hex(_q, _r)
/// @desc Redondea una coordenada axial fraccionaria al hexágono correcto.
///       Pasa a coordenadas cúbicas (q, r, s) con q + r + s = 0, redondea las
///       tres y corrige la que más se haya movido. Redondear q y r por separado
///       da el hexágono equivocado cerca de los vértices.
/// @param {Real} _q  Coordenada axial q fraccionaria.
/// @param {Real} _r  Coordenada axial r fraccionaria.
/// @return {Struct}  { q, r } enteras.
function redondear_hex(_q, _r)
{
    var _s = -_q - _r;
    var _rq = round(_q), _rr = round(_r), _rs = round(_s);
    var _dq = abs(_rq - _q), _dr = abs(_rr - _r), _ds = abs(_rs - _s);

    if (_dq > _dr && _dq > _ds)      { _rq = -_rr - _rs; }
    else if (_dr > _ds)              { _rr = -_rq - _rs; }
    // Si la que más se movió es s, no hace falta corregir nada de (q, r).

    return { q: _rq, r: _rr };
}
```

Las medidas que hacen falta para colocar los sprites, derivadas de esas mismas fórmulas:

| | Punta arriba | Lado plano arriba |
|---|---|---|
| Ancho del hexágono | `sqrt(3) * size` | `2 * size` |
| Alto del hexágono | `2 * size` | `sqrt(3) * size` |
| Separación horizontal entre centros | `sqrt(3) * size` | `1.5 * size` |
| Separación vertical entre centros | `1.5 * size` | `sqrt(3) * size` |

```gml
/// ¿Sobre qué hexágono está el ratón?
var _f = pixel_a_hex(mouse_x - origen_x, mouse_y - origen_y, true);
var _h = redondear_hex(_f.q, _f.r);
var _c = hex_a_pixel(_h.q, _h.r, true);
draw_circle(origen_x + _c.x, origen_y + _c.y, HEX_SIZE * 0.9, true);   // resaltado
```

---

## 8 · Curvas de crecimiento para diseño

### 8.1 · Las cinco formas, y qué comunica cada una

Toda progresión numérica de un juego —XP por nivel, coste de mejoras, daño de un arma, precio de
un edificio— es una de estas cinco curvas. Elegir la forma **antes** de escribir números es la
diferencia entre balancear y parchear.

| Forma | Fórmula (`n` = nivel, desde 1) | Qué comunica | Riesgo |
|---|---|---|---|
| **Lineal** | `base + paso * (n - 1)` | «Cada nivel cuesta un poco más» | Se vuelve trivial: el poder crece más rápido que el coste |
| **Cuadrática** | `base * n * n` | «El esfuerzo crece de forma notable» | Ninguno grave; es la más segura por defecto |
| **Exponencial** | `base * power(razon, n - 1)` | «Cada nivel es un salto» | Se dispara: en el nivel 20 los números son ilegibles |
| **Logarítmica** | `base * ln(n + 1)` | «Rendimientos decrecientes» | Se aplana tanto que deja de motivar |
| **Sigmoide** | `techo / (1 + exp(-k * (n - centro)))` | «Arranque lento, tirón medio, techo» | Tres parámetros que hay que ajustar juntos |

```gml
/// scr_progresion — las cinco curvas, listas para usar en una tabla de balance.

/// @func progresion_lineal(_nivel, _base, _paso)
/// @param {Real} _nivel  Nivel, empezando en 1.
/// @param {Real} _base   Valor del nivel 1.
/// @param {Real} _paso   Cuánto sube por nivel.
/// @return {Real}
function progresion_lineal(_nivel, _base, _paso)
{
    return _base + _paso * (_nivel - 1);
}

/// @func progresion_cuadratica(_nivel, _base)
/// @param {Real} _nivel  Nivel, empezando en 1.
/// @param {Real} _base   Coeficiente; el nivel 1 vale exactamente _base.
/// @return {Real}
function progresion_cuadratica(_nivel, _base)
{
    return _base * _nivel * _nivel;
}

/// @func progresion_exponencial(_nivel, _base, _razon)
/// @param {Real} _nivel  Nivel, empezando en 1.
/// @param {Real} _base   Valor del nivel 1.
/// @param {Real} _razon  Multiplicador por nivel. 1.15 = +15 % cada uno.
/// @return {Real}
function progresion_exponencial(_nivel, _base, _razon)
{
    return _base * power(_razon, _nivel - 1);
}

/// @func progresion_logaritmica(_nivel, _base)
/// @param {Real} _nivel  Nivel, empezando en 1.
/// @param {Real} _base   Escala vertical.
/// @return {Real}
function progresion_logaritmica(_nivel, _base)
{
    return _base * ln(_nivel + 1);
}

/// @func progresion_sigmoide(_nivel, _techo, _pendiente, _centro)
/// @param {Real} _nivel      Nivel, empezando en 1.
/// @param {Real} _techo      Valor máximo al que tiende la curva.
/// @param {Real} _pendiente  Cuánto de brusco es el tramo central (0.5..1.5).
/// @param {Real} _centro     Nivel en el que la curva va por la mitad del techo.
/// @return {Real}
function progresion_sigmoide(_nivel, _techo, _pendiente, _centro)
{
    return _techo / (1 + exp(-_pendiente * (_nivel - _centro)));
}
```

### 8.2 · Las cinco curvas, a diez niveles

XP necesaria **para pasar** cada nivel, con `base = 100` para las tres primeras,
`base = 400` para la logarítmica y `techo = 2000, pendiente = 0.9, centro = 5.5` para la
sigmoide. Los valores están calculados con las fórmulas de arriba:

| Nivel | Lineal (paso 100) | Cuadrática | Exponencial (×1,5) | Logarítmica | Sigmoide |
|---:|---:|---:|---:|---:|---:|
| 1 | 100 | 100 | 100 | 277 | 34 |
| 2 | 200 | 400 | 150 | 439 | 82 |
| 3 | 300 | 900 | 225 | 555 | 191 |
| 4 | 400 | 1 600 | 338 | 644 | 412 |
| 5 | 500 | 2 500 | 506 | 717 | 779 |
| 6 | 600 | 3 600 | 759 | 778 | 1 221 |
| 7 | 700 | 4 900 | 1 139 | 832 | 1 588 |
| 8 | 800 | 6 400 | 1 709 | 879 | 1 809 |
| 9 | 900 | 8 100 | 2 563 | 921 | 1 918 |
| 10 | 1 000 | 10 000 | 3 844 | 959 | 1 966 |
| **Total 1→10** | **5 500** | **38 500** | **11 333** | — | — |
| **Nivel 10 ÷ nivel 1** | **10×** | **100×** | **38×** | **3,5×** | **58×** |

Lo que se lee en la tabla, y que es el motivo de mirarla antes de programar:

- La **cuadrática** multiplica el coste por 100 en diez niveles, pero el **acumulado** crece de
  forma manejable. Es la opción por defecto para XP.
- La **exponencial** parece suave al principio (150, 225, 338…) y se dispara después. Con razón
  1,5 y 30 niveles el último cuesta 12 millones. **La razón es el parámetro más peligroso de un
  juego**: 1,15 y 1,5 producen mundos completamente distintos.
- La **logarítmica** solo sirve para lo que debe **frenarse**: bonus por estadística,
  probabilidad de crítico, reducción de daño por armadura. Como coste de progresión mata la
  sensación de logro.
- La **sigmoide** es la única que tiene **techo**, y por eso es la correcta para dificultad,
  velocidad de enemigos o densidad de oleadas: nunca se descontrola.

### 8.3 · Cuál para qué

| Sistema | Curva | Por qué |
|---|---|---|
| XP para subir de nivel | Cuadrática | Crece de forma perceptible sin explotar |
| Coste de mejora repetible | Exponencial con razón baja (1,07 – 1,15) | Es la que crea la decisión «¿ahorro o compro ya?» |
| Daño de un arma por nivel | Lineal o cuadrática suave | Debe ser **predecible**: el jugador calcula golpes, no logaritmos |
| Reducción de daño por armadura | Logarítmica, o `armadura / (armadura + k)` | Nunca puede llegar al 100 %: el techo es obligatorio |
| Velocidad / dificultad por oleada | Sigmoide | Tiene un máximo jugable que no se puede superar |
| Precio de venta de recursos | Lineal | Un mercado que no sea legible frustra |

> 💡 La curva de coste geométrica con números reales, el cálculo del TTK y la disciplina de
> «balancear en múltiplos, no en absolutos» están desarrollados en
> [13 · 01 §4.4](./01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md).
> Esta sección da las **formas**; aquella, el **método** para poner los números.

### 8.4 · Invertir la curva: nivel a partir de la XP acumulada

Al cargar una partida solo tienes la XP total. Para la lineal y la cuadrática existe fórmula
cerrada, pero **la solución robusta es un bucle**: funciona con cualquier curva, incluidas las
que no se pueden invertir, y con 100 niveles cuesta 100 sumas.

```gml
/// @func nivel_desde_xp(_xp_total, _curva, _nivel_maximo)
/// @desc Devuelve el nivel alcanzado y la XP sobrante hacia el siguiente.
///       Vale para CUALQUIER curva: solo necesita poder evaluarla nivel a nivel.
/// @param {Real} _xp_total      XP acumulada del jugador.
/// @param {Function} _curva     Función que recibe un nivel y devuelve su coste.
/// @param {Real} _nivel_maximo  Tope duro, para que el bucle siempre termine.
/// @return {Struct}             { nivel, sobrante, coste_siguiente }
function nivel_desde_xp(_xp_total, _curva, _nivel_maximo)
{
    var _nivel = 1;
    var _resto = _xp_total;

    while (_nivel < _nivel_maximo)
    {
        var _coste = _curva(_nivel);
        if (_resto < _coste) { break; }
        _resto -= _coste;
        _nivel += 1;
    }

    return {
        nivel: _nivel,
        sobrante: _resto,
        coste_siguiente: (_nivel < _nivel_maximo) ? _curva(_nivel) : 0
    };
}
```

```gml
/// Barra de XP del HUD, con la curva cuadrática de la tabla
var _curva = function(_n) { return progresion_cuadratica(_n, 100); };
var _p = nivel_desde_xp(global.xp_total, _curva, 50);

draw_text(8, 8, $"Nivel {_p.nivel}");
if (_p.coste_siguiente > 0)
{
    draw_healthbar(8, 24, 208, 32, _p.sobrante / _p.coste_siguiente * 100,
                   c_black, c_aqua, c_aqua, 0, true, true);
}
```

---

## 9 · Trigonometría útil

### 9.1 · Órbitas

Un satélite alrededor de un punto es una fase que avanza y `lengthdir_x/y` que la convierte en
posición. Guardar la **fase** y no la posición es lo que permite pausar, invertir o acelerar la
órbita sin acumular error.

```gml
/// obj_satelite · Evento Create
fase          = 0;      // grados recorridos
radio         = 48;
grados_por_s  = 90;     // una vuelta cada 4 segundos
excentricidad = 0.6;    // 1 = círculo; < 1 aplasta la órbita en vertical

/// obj_satelite · Evento Step
var _dt = delta_time / 1000000;
fase = envolver(fase + grados_por_s * _dt, 0, 360);

x = obj_planeta.x + lengthdir_x(radio, fase);
y = obj_planeta.y + lengthdir_y(radio, fase) * excentricidad;
depth = (lengthdir_y(1, fase) > 0) ? obj_planeta.depth - 1 : obj_planeta.depth + 1;
```

La última línea es el detalle que vende la órbita: cuando el satélite pasa por delante del
planeta se dibuja encima, y cuando pasa por detrás, debajo.

### 9.2 · Movimiento sinusoidal, y por qué no se usa `current_time`

`wave(desde, hasta, duracion, offset)` ya está en
[`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml) y resuelve el caso
normal. Lo que hay que saber es **por qué no basta con leer el reloj del sistema**: `current_time`
no se pausa, no respeta la escala de tiempo y no se puede rebobinar. Acumula tu propia fase.

```gml
/// obj_pez · Evento Create — nado con dos ondas de distinta frecuencia
fase_a = random(360);           // desfase inicial: evita que todos naden a la vez
fase_b = random(360);
y_base = y;

/// obj_pez · Evento Step
var _dt = delta_time / 1000000;
fase_a = envolver(fase_a + 140 * _dt, 0, 360);
fase_b = envolver(fase_b +  73 * _dt, 0, 360);   // frecuencia NO múltiplo de la otra

// Sumar dos senos de periodos inconmensurables da un movimiento que nunca se
// repite igual: parece orgánico en lugar de mecánico.
y = y_base + dsin(fase_a) * 6 + dsin(fase_b) * 3;
image_angle = dcos(fase_a) * 8;
```

### 9.3 · Espirales

Una espiral es una órbita cuyo radio cambia con la fase. Dos variantes cubren casi todo:

```gml
/// Espiral de Arquímedes: el radio crece proporcionalmente al ángulo.
/// Las vueltas quedan igual de separadas. Para balas en abanico y remolinos.
var _radio = radio_inicial + fase * 0.35;

/// Espiral logarítmica: el radio se multiplica. Las vueltas se separan cada vez más.
/// Es la de las conchas y las galaxias; para agujeros negros y absorciones.
var _radio = radio_inicial * exp(fase * 0.012);

x = centro_x + lengthdir_x(_radio, fase);
y = centro_y + lengthdir_y(_radio, fase);
```

```gml
/// obj_jefe · patrón de disparo en espiral doble
disparo_fase = envolver(disparo_fase + 7, 0, 360);   // 7 grados por disparo
repeat (2)
{
    var _b = instance_create_layer(x, y, "Balas", obj_bala_enemiga);
    _b.direction = disparo_fase;
    _b.speed     = 3;
    disparo_fase = envolver(disparo_fase + 180, 0, 360);   // el segundo brazo, opuesto
}
```

### 9.4 · Misil teledirigido: girar limitado + avanzar

Un misil que apunta perfectamente al objetivo es imposible de esquivar y aburrido. La gracia
está en **limitar el giro**: el misil se pasa, tiene que corregir y describe la curva
característica. Es `girar_hacia` (§3.2) más un avance constante.

```gml
/// obj_misil · Evento Create
objetivo       = noone;
velocidad      = 260;    // px/s
giro_max       = 200;    // grados/s: la palanca de dificultad de esta arma
vida_restante  = 6;      // segundos antes de autodestruirse

/// obj_misil · Evento Step
var _dt = delta_time / 1000000;

vida_restante -= _dt;
if (vida_restante <= 0) { instance_destroy(); exit; }

if (instance_exists(objetivo))
{
    // Predicción sencilla: apuntar a donde ESTARÁ, no a donde está.
    // `objetivo.speed` está en píxeles por STEP: hay que pasarlo a px/s.
    var _fps = game_get_speed(gamespeed_fps);
    var _vel_objetivo = objetivo.speed * _fps;
    var _tiempo_vuelo = point_distance(x, y, objetivo.x, objetivo.y) / velocidad;
    var _px = objetivo.x + lengthdir_x(_vel_objetivo * _tiempo_vuelo, objetivo.direction);
    var _py = objetivo.y + lengthdir_y(_vel_objetivo * _tiempo_vuelo, objetivo.direction);

    image_angle = girar_hacia(image_angle, point_direction(x, y, _px, _py), giro_max * _dt);
}

x += lengthdir_x(velocidad * _dt, image_angle);
y += lengthdir_y(velocidad * _dt, image_angle);
```

> 🔺 `room_speed` está **obsoleta** en 2026 (`buscar.py` lo marca). La conversión de «píxeles por
> step» a «píxeles por segundo» se hace con `game_get_speed(gamespeed_fps)`. El detalle, en
> [01 · 06 §7](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md).

**Las tres palancas de diseño de un misil**, y cómo se sienten:

| Palanca | Bajo | Alto |
|---|---|---|
| `giro_max` | Se esquiva rodeándolo; el misil orbita | Imposible de esquivar; deja de ser divertido |
| `velocidad` | Da tiempo a reaccionar, se ve venir | Es prácticamente un hitscan |
| `vida_restante` | El misil perdona: da una vía de escape | Persecución hasta el final |

La combinación clásica que funciona: velocidad alta, **giro bajo** y vida media. El jugador
esquiva con un movimiento lateral en el último momento, y eso se siente como una habilidad.

### 9.5 · Cono de visión y campo de visión con rayos

El cono geométrico (§2.4) dice **hacia dónde** puede mirar un enemigo. Para saber **qué llega a
ver** hay dos niveles:

1. **Un rayo por objetivo** (barato): `collision_line` desde el enemigo a cada candidato dentro
   del cono. Es lo correcto para IA de sigilo con pocos actores.
2. **Muchos rayos, para dibujar el área visible** (caro): el campo de visión completo de un
   roguelike o la niebla de guerra. El código está resuelto en
   [04 · 05 §5.6](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md);
   no lo reescribas.

```gml
/// Un cono de visión dibujado como abanico de rayos, para depurar la IA
draw_set_alpha(0.25);
draw_primitive_begin(pr_trianglefan);
draw_vertex(x, y);
var _mitad = apertura * 0.5;
for (var _a = -_mitad; _a <= _mitad; _a += 3)     // un rayo cada 3 grados
{
    var _ang = image_angle + _a;
    var _fx = x + lengthdir_x(alcance, _ang);
    var _fy = y + lengthdir_y(alcance, _ang);

    // Recortar el rayo donde tope con un muro.
    var _muro = collision_line(x, y, _fx, _fy, obj_muro, false, true);
    if (_muro != noone)
    {
        var _d = point_distance(x, y, _muro.x, _muro.y);
        _fx = x + lengthdir_x(_d, _ang);
        _fy = y + lengthdir_y(_d, _ang);
    }
    draw_vertex(_fx, _fy);
}
draw_primitive_end();
draw_set_alpha(1);
```

---

## 10 · Matrices y transformaciones en 2D

En un juego 2D casi nunca hacen falta matrices. Hacen falta **tres operaciones** que se pueden
escribir sin ellas, y **un caso** en el que la matriz sí gana. La referencia completa de la
familia `matrix_*` —incluidos el orden *column-major* y la pila de matrices— está en
[08 · 11 §Matrices](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores%2C%20matrices%20y%20%C3%A1ngulos.md),
y su uso en 3D, en
[04 · 29 — 3D en GameMaker](../04%20-%20Recetas%20por%20g%C3%A9nero/29%20-%203D%20en%20GameMaker.md).

### 10.1 · Rotar un punto alrededor de otro

La operación más pedida: la punta de un cañón, el punto de anclaje de un arma, la posición de un
orbe alrededor del personaje. La versión legible usa las funciones del motor y **no puede
equivocarse de signo**:

```gml
/// @func rotar_punto(_px, _py, _cx, _cy, _grados)
/// @desc Rota el punto P alrededor del centro C. Usa las funciones nativas, así
///       que respeta automáticamente la convención de ángulos de GameMaker.
/// @param {Real} _px      X del punto a rotar.
/// @param {Real} _py      Y del punto a rotar.
/// @param {Real} _cx      X del centro de rotación.
/// @param {Real} _cy      Y del centro de rotación.
/// @param {Real} _grados  Grados a rotar (positivo = antihorario en pantalla).
/// @return {Struct}       { x, y } del punto rotado.
function rotar_punto(_px, _py, _cx, _cy, _grados)
{
    var _dist = point_distance(_cx, _cy, _px, _py);
    var _ang  = point_direction(_cx, _cy, _px, _py) + _grados;
    return { x: _cx + lengthdir_x(_dist, _ang),
             y: _cy + lengthdir_y(_dist, _ang) };
}
```

Para un bucle caliente (cientos de puntos por frame) la forma directa evita la raíz cuadrada.
**Fíjate en el signo del segundo `dsin`: es el que corrige el eje Y invertido.**

```gml
/// Misma rotación, sin raíz cuadrada. Verificada contra rotar_punto().
var _dx = _px - _cx;
var _dy = _py - _cy;
var _c  = dcos(_grados);
var _s  = dsin(_grados);
var _rx = _cx + _dx * _c + _dy * _s;
var _ry = _cy - _dx * _s + _dy * _c;
```

### 10.2 · Escalar desde un pivote

Escalar un sprite con `image_xscale` lo hace desde su **origen**. Para escalar desde cualquier
otro punto —un menú que se despliega desde su esquina, una explosión que crece desde su base—
hay que mover, escalar y devolver:

```gml
/// @func escalar_desde_pivote(_px, _py, _cx, _cy, _escala_x, _escala_y)
/// @desc Escala el punto P respecto del pivote C. Con escala 1 devuelve P intacto.
/// @param {Real} _px        X del punto.
/// @param {Real} _py        Y del punto.
/// @param {Real} _cx        X del pivote.
/// @param {Real} _cy        Y del pivote.
/// @param {Real} _escala_x  Factor horizontal.
/// @param {Real} _escala_y  Factor vertical.
/// @return {Struct}         { x, y }
function escalar_desde_pivote(_px, _py, _cx, _cy, _escala_x, _escala_y)
{
    return { x: _cx + (_px - _cx) * _escala_x,
             y: _cy + (_py - _cy) * _escala_y };
}
```

```gml
/// Un panel que crece desde su esquina inferior izquierda al abrirse
var _e = ease_out_back(progreso_apertura);
var _p = escalar_desde_pivote(x, y, x, y + alto, _e, _e);
draw_sprite_ext(spr_panel, 0, _p.x, _p.y, _e, _e, 0, c_white, 1);
```

### 10.3 · `matrix_build` + `matrix_set`: transformar un grupo entero

Éste es el caso en el que la matriz gana de calle: **dibujar muchos elementos y que todos giren,
escalen y se muevan como un solo objeto**. Un HUD que rota, un mecha con seis piezas, un mapa
que se inclina. Sin matriz habría que rotar cada elemento por separado; con ella, se dibuja todo
en coordenadas locales (con el `(0,0)` en el centro del grupo) y la matriz hace el resto.

```gml
/// obj_grupo · Evento Draw — todo el grupo gira y escala como una pieza
var _mundo_previa = matrix_get(matrix_world);      // guardar SIEMPRE lo que había

// x, y = posición del grupo; angulo y escala = su transformación.
// El orden de argumentos es (x, y, z, rotX, rotY, rotZ, escX, escY, escZ).
matrix_set(matrix_world, matrix_build(x, y, 0,  0, 0, angulo,  escala, escala, 1));

// A partir de aquí, TODO se dibuja en coordenadas locales, con (0,0) en el centro.
draw_sprite(spr_chasis, 0,   0,   0);
draw_sprite(spr_brazo,  0, -18,  -6);
draw_sprite(spr_brazo,  0,  18,  -6);
draw_sprite(spr_cabina, 0,   0, -22);

matrix_set(matrix_world, _mundo_previa);           // restaurar, o el resto sale torcido
```

> 🔺 **Restaurar la matriz no es opcional.** `matrix_world` es estado global del renderizador: si
> sales del evento Draw sin devolverla a lo que había, todo lo que se dibuje después —el HUD, las
> partículas, otras instancias— sale transformado. El síntoma es «se ha vuelto loco el juego» y
> la causa está a veinte líneas de distancia. Guarda con `matrix_get` y restaura siempre.

> 💡 Las **colisiones no se enteran** de la matriz. `matrix_world` afecta solo al dibujado: las
> máscaras siguen donde estaban. Si el grupo transformado tiene que colisionar, la posición real
> hay que calcularla con `rotar_punto` (§10.1).

---

## 11 · Precisión numérica

### 11.1 · Los reales son dobles, y comparar con `==` es una trampa

En GameMaker todos los números son **reales de doble precisión**: no hay tipo entero. Eso
significa que `0.1 + 0.2` no vale exactamente `0.3`, que un contador que suma `0.1` sesenta veces
no vale exactamente `6`, y que `if (x == 100)` puede no entrar nunca aunque en el depurador ponga
`100`.

```gml
// ❌ Puede no entrar nunca
if (image_index == 1) { disparar(); }

// ✅ Tres formas correctas, según el caso
if (floor(image_index) == 1) { disparar(); }          // el fotograma 1, entero
if (abs(_valor - _objetivo) < 0.001) { /* ... */ }    // comparación con tolerancia
if (_valor >= _umbral) { /* ... */ }                  // desigualdad, no igualdad
```

```gml
/// @func casi_igual(_a, _b, [_tolerancia])
/// @desc Comparación de reales con margen. Úsala en lugar de == siempre que los
///       valores procedan de un cálculo y no de una constante escrita a mano.
/// @param {Real} _a             Primer valor.
/// @param {Real} _b             Segundo valor.
/// @param {Real} [_tolerancia]  Margen aceptable. 0.001 para píxeles; menos para normalizados.
/// @return {Bool}
function casi_igual(_a, _b, _tolerancia = 0.001)
{
    return (abs(_a - _b) <= _tolerancia);
}
```

### 11.2 · `math_set_epsilon`: la solución global, y por qué usarla con cuidado

`math_set_epsilon(v)` cambia el comportamiento de **todos** los operadores de comparación
(`<`, `>`, `==`, `<=`, `>=`, `!=`) para el resto de la ejecución: dos números que difieran menos
de `v` se consideran iguales. El manual avisa de dos cosas: **`0` desactiva el redondeo** y
**`1` produce un error**; el rango válido es `0` a `0.999999999`.

```gml
/// obj_arranque · Evento Create
math_set_epsilon(0.000001);   // una millonésima: suficiente para animación y píxeles
```

Cuándo usarla y cuándo no:

| | |
|---|---|
| ✅ Sirve para | Quitar de golpe la clase entera de bugs de `image_index == n` y contadores acumulados |
| ❌ No sirve para | Comparar magnitudes grandes: un épsilon absoluto de `1e-6` no arregla nada al comparar dos valores de orden `1e9` |
| ⚠️ Cuidado con | Es **global y silencioso**. Alguien que lea `if (a == b)` no sabrá que hay una tolerancia detrás. Documéntalo en `scr_config` |

Para los casos importantes, la comparación explícita de §11.1 es más honesta: se lee en el propio
código.

### 11.3 · Acumular error en bucles largos

La regla, y es una sola: **no acumules lo que puedes calcular**. Sumar `_dt` diez mil veces
acumula diez mil redondeos; multiplicar un contador de pasos por una constante, ninguno.

```gml
// ❌ Deriva: tras media hora, `posicion` no coincide con el resultado exacto
posicion += velocidad * _dt;

// ✅ Sin deriva: el tiempo se acumula (barato) y la posición se calcula
tiempo_vivo += _dt;
posicion = posicion_inicial + velocidad * tiempo_vivo;
```

Dónde importa de verdad, y dónde no:

| Situación | ¿Importa? |
|---|---|
| Posición de un personaje que el jugador controla | **No**: el jugador corrige constantemente |
| Fase de una onda decorativa | **No**: `envolver()` la mantiene acotada y nadie mide |
| Plataforma móvil que debe volver **exactamente** a su sitio | **Sí**: usa una fase 0..1 y `lerp` |
| Reloj de partida, cronómetro de récord | **Sí**: `get_timer()`, que es un entero de microsegundos |
| Simulación determinista (repeticiones, red) | **Sí, crítico**: aritmética entera o de punto fijo |

### 11.4 · Enteros grandes e `int64`

Los reales de doble precisión representan enteros exactos hasta `2^53` (unos 9 000 billones).
Por encima de eso, sumar 1 puede no cambiar nada. Para juegos *idle*, contadores de daño
acumulado o identificadores de plataforma se usa `int64`, que da 64 bits con signo.

```gml
var _oro = int64("9007199254740993");   // desde string: no pierde el dígito por el camino
show_debug_message(string(_oro));
```

Tres avisos:

1. `int64` acepta **real, string, `int64`, `int32` o `ptr`**; cualquier otra cosa **detiene el
   juego** con un error. Valídalo antes con `is_numeric` o `is_string`.
2. Si el número viene de un servidor o de un archivo, léelo como **string** y conviértelo: pasar
   por real ya habría perdido precisión.
3. Para números de juego *idle* que superan `int64` (más allá de `9,2·10¹⁸`), la solución no es
   un entero más grande sino **guardar mantisa y exponente por separado** y mostrar «1,4 aa».

---

## 12 · Tiempo

### 12.1 · Frames ↔ segundos

```gml
/// @func segundos_a_frames(_segundos)
/// @desc Convierte segundos a pasos del juego, usando la velocidad REAL
///       configurada. Nunca escribas 60 a mano: no todos los proyectos van a 60.
/// @param {Real} _segundos  Tiempo en segundos.
/// @return {Real}           Número de pasos (redondeado).
function segundos_a_frames(_segundos)
{
    return round(_segundos * game_get_speed(gamespeed_fps));
}

/// @func frames_a_segundos(_frames)
/// @desc La conversión inversa.
/// @param {Real} _frames  Número de pasos.
/// @return {Real}         Tiempo en segundos.
function frames_a_segundos(_frames)
{
    return _frames / game_get_speed(gamespeed_fps);
}
```

```gml
alarm[0] = segundos_a_frames(2.5);   // legible y correcto a cualquier velocidad
```

### 12.2 · `delta_time` está en microsegundos

`delta_time` es el tiempo transcurrido desde el paso anterior **en microsegundos** (millonésimas
de segundo). La primera línea de cualquier Step que use tiempo real es siempre la misma:

```gml
var _dt = delta_time / 1000000;   // ahora está en segundos
```

Las tres cosas que hay que saber sobre él:

| | |
|---|---|
| **Mide tiempo real** | No se pausa con un *hit stop* ni respeta la escala de tiempo. Si tienes un sistema de cámara lenta, multiplica `_dt` por tu propia escala |
| **Puede dar un pico enorme** | Al minimizar la ventana, al cargar un recurso o al arrastrar la barra de título, `_dt` puede valer medio segundo y el personaje atraviesa el mapa. **Recórtalo**: `_dt = min(_dt, 1/30);` |
| **`fps` y `fps_real` no son lo mismo** | `fps` son los fotogramas dibujados; `fps_real` es cuántos podría dibujar si no estuviera limitado. Para diagnosticar rendimiento sirve `fps_real` |

```gml
/// obj_control · Evento Begin Step — el delta time saneado, una sola vez por frame
global.dt = min(delta_time / 1000000, 1 / 30);   // nunca más de 1/30 s por paso
```

### 12.3 · Temporizadores independientes del framerate

Tres formas, de menos a más maquinaria:

```gml
/// A) Contador en segundos: la más simple, y suficiente el 90 % de las veces.
///    Sobrevive a los cambios de velocidad del juego y se puede pausar solo.
cadencia_restante -= global.dt;
if (cadencia_restante <= 0 && teclado_disparo)
{
    disparar();
    cadencia_restante = 0.18;      // segundos entre disparos, legible
}
```

```gml
/// B) Alarm: cuenta en PASOS, no en segundos. Se pausa sola con el juego
///    (una instancia desactivada no descuenta) y es la más barata.
alarm[0] = segundos_a_frames(0.18);
```

```gml
/// C) Time source: cuenta en unidades reales y sobrevive al cambio de room.
///    Para lógica global: oleadas, autoguardado, ciclos día/noche.
temporizador = time_source_create(time_source_game, 30, time_source_units_seconds,
                                  function() { generar_oleada(); }, [], -1);
time_source_start(temporizador);
```

| | Contador (`global.dt`) | `alarm` | `time_source` |
|---|---|---|---|
| Unidad | Segundos | Pasos | Segundos o pasos, a elegir |
| Se pausa con la instancia | Sí, si dejas de restar | Sí | Depende del padre (`time_source_game` sí) |
| Sobrevive al cambio de room | No | No | Sí, con `time_source_global` |
| Cuántos por instancia | Los que quieras | 12 | Los que quieras |
| Cuándo | Cadencias, invulnerabilidad, retardos cortos | Lo mismo, con menos código | Lógica global y repetitiva |

El catálogo completo de *time sources*, con `call_later` y el orden exacto de ejecución, está en
[01 · 06 §8](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md).

> 💡 Para **medir** cuánto tarda un trozo de código, la herramienta es `get_timer()`, que
> devuelve microsegundos desde el arranque como entero (sin la deriva de los reales):
> `var _t0 = get_timer(); ... ; show_debug_message($"{(get_timer() - _t0) / 1000} ms");`

---

## 13 · Checklist

**Antes de escribir una función matemática**

- [ ] ¿Existe ya en el runtime? `python3 "_indice/buscar.py" <nombre>`.
- [ ] ¿Existe ya en la biblioteca? `scr_math_util.gml` trae `approach`, `wave`, `remap`,
      `remap_clamped`, `lerp_dt`, `smoothstep`, `snap` y toda la familia `ease_*`.
- [ ] Si es geometría de colisión, ¿lo resuelve `place_meeting`, `collision_line` o una de las
      `point_in_*`? Casi siempre sí.

**Ángulos**

- [ ] Todo el proyecto en **grados**, con `dsin`/`dcos`; radianes solo dentro de un shader.
- [ ] Ninguna resta de ángulos con `-`: siempre `angle_difference`.
- [ ] Todo giro hacia un objetivo pasa por `girar_hacia` o por un `clamp` explícito.
- [ ] Toda fase acumulada pasa por `envolver(fase, 0, 360)`.

**Vectores**

- [ ] Ninguna normalización sin comprobar antes que el vector no es nulo.
- [ ] Toda normal que entre en `reflejar_vector` es unitaria.
- [ ] Comparaciones de distancia dentro de bucles grandes, con cuadrados y sin `sqrt`.

**Tiempo e interpolación**

- [ ] Ningún `lerp(a, b, k)` con `k` constante llamado una vez por frame.
- [ ] Todo suavizado usa `lerp_dt`, `suavizar` o `suavizar_media_vida`, con `delta_time`.
- [ ] `delta_time` recortado (`min(_dt, 1/30)`) en un único sitio, al principio del frame.
- [ ] Ningún `60` escrito a mano: `game_get_speed(gamespeed_fps)`.
- [ ] `room_speed` no aparece por ninguna parte (está obsoleta).

**Aleatoriedad**

- [ ] `randomise()` exactamente una vez, en el arranque.
- [ ] Índices de array con `irandom(array_length(_a) - 1)`.
- [ ] Un generador o una semilla derivada por sistema, si hay contenido procedural.
- [ ] Cada tabla de probabilidad, verificada con el histograma de §5.8 antes de publicar.
- [ ] Los sistemas donde una racha se percibiría como un bug usan bolsa o piedad, no uniforme.

**Precisión**

- [ ] Ninguna comparación `==` entre reales calculados: `casi_igual` o una desigualdad.
- [ ] Lo que debe volver exactamente a un valor no se acumula: se recalcula desde una fase 0..1.
- [ ] Los enteros por encima de `2^53` van por `int64`, y se leen desde string.

**Dibujado transformado**

- [ ] Cada `matrix_set(matrix_world, ...)` tiene su restauración con el valor de `matrix_get`.
- [ ] Las colisiones de un grupo transformado se calculan aparte: la matriz no las mueve.

---

## 14 · Errores clásicos y cómo evitarlos

| # | Error | Qué se ve | La corrección |
|---|---|---|---|
| 1 | `cos(image_angle)` | Movimiento «casi correcto» pero caótico | `image_angle` está en grados: `dcos`, o mejor `lengthdir_x/y` |
| 2 | `lerp(x, obj, 0.1)` por frame | La cámara va distinto en cada monitor | §4.2 / §4.3, con `delta_time` |
| 3 | Normalizar sin comprobar el vector nulo | La instancia desaparece; ningún error en consola | §2.2: devolver un valor por defecto |
| 4 | `angulo_a - angulo_b` | La torreta da la vuelta larga al cruzar 0° | `angle_difference(dest, src)` |
| 5 | `random(...)` sin `randomise()` | Cada partida es idéntica a la anterior | `randomise()` una vez en el arranque |
| 6 | `irandom(array_length(a))` | `undefined` una vez de cada n | `irandom(array_length(a) - 1)` |
| 7 | `if (real_calculado == valor)` | La condición no entra nunca | `casi_igual()` o `floor()` (§11.1) |
| 8 | `round()` para pasar de mundo a celda | El mapa se rompe en coordenadas negativas | `floor()`, siempre (§7.1) |
| 9 | `if (rectangle_in_rectangle(...))` esperando un booleano | Confundir «contenido» con «se tocan» | Devuelve 0, 1 o 2: compara explícitamente |
| 10 | `matrix_set` sin restaurar | Todo lo dibujado después sale torcido | `matrix_get` antes, restaurar después (§10.3) |
| 11 | Reflejar con una normal no unitaria | La bala sale disparada tras rebotar | `normalizar()` la normal (§2.7) |
| 12 | Bala rápida contra enemigo pequeño | Atraviesa sin tocarlo (*tunneling*) | Comprobar el **segmento recorrido**, no la posición (§6.6) |
| 13 | `image_angle += falta * 0.1` | Gira rápido y nunca termina de apuntar | `girar_hacia` con tope por segundo (§3.2) |
| 14 | Media aritmética de ángulos | El resultado apunta al lado contrario | `angulo_medio` (§3.6) |
| 15 | `current_time` para una oscilación | No se pausa, no respeta la cámara lenta | Acumular fase propia con `delta_time` (§9.2) |
| 16 | Progresión exponencial con razón alta | En el nivel 25 los números son ilegibles | Razón 1,07 – 1,15, o cuadrática (§8) |
| 17 | Un solo RNG para todo | La mazmorra cambia según cuántos golpes diste | Un generador por sistema (§5.2) |
| 18 | Suavizado exponencial sin corte | El valor nunca llega y una condición no se cumple | Añadir el corte de medio píxel (§4.3) |

---

## Ver también

**Referencia de funciones (las fichas, no el criterio)**

- [08 · 10 — Matemáticas y números en GML](../08%20-%20Referencia%20GML%20completa/10%20-%20Matem%C3%A1ticas.md)
- [08 · 11 — Vectores, matrices y ángulos en GML](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores%2C%20matrices%20y%20%C3%A1ngulos.md)

**Código ya escrito y probado**

- [`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml) — `approach`, `wave`, `remap`, `lerp_dt`, `smoothstep`, `snap` y la familia `ease_*`
- [`scr_tween.gml`](../06%20-%20Assets%20y%20Scripts/scr_tween.gml) — el motor que aplica esas curvas a lo largo del tiempo

**Dónde se aplica cada bloque**

- [01 · 06 — Eventos y ciclo del juego](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) — `delta_time`, *time sources*, orden de eventos
- [01 · 08 — Movimiento y colisiones](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) — máscaras, `move_and_collide`, tilemaps
- [01 · 10 — Rooms, capas, cámaras y viewports](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) — profundidad y orden de dibujado
- [04 · 05 — Roguelike y generación procedural](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md) — RNG con semilla (§4.1), tablas de loot ponderadas (§4.6 y §5.7), campo de visión por raycasting (§5.6)
- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md) — escala de tiempo, temblor de pantalla
- [04 · 22 — Físicas con Box2D](../04%20-%20Recetas%20por%20g%C3%A9nero/22%20-%20F%C3%ADsicas%20con%20Box2D.md) — cuándo delegar la geometría en el motor de físicas
- [04 · 23 — IA de enemigos y steering behaviors](../04%20-%20Recetas%20por%20g%C3%A9nero/23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) — seek, arrive, wander, flocking
- [04 · 29 — 3D en GameMaker](../04%20-%20Recetas%20por%20g%C3%A9nero/29%20-%203D%20en%20GameMaker.md) — matrices de verdad, proyección y cámara
- [04 · 34 — Combate a distancia: armas, munición y balística](../04%20-%20Recetas%20por%20g%C3%A9nero/34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munici%C3%B3n%20y%20bal%C3%ADstica.md) — hitscan con `collision_line_list` ordenada (§6.8), penetración y caída de daño
- [13 · 01 — Diseño de juego: core loop, mecánicas, balance y dificultad](./01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md) — el método para poner los números en las curvas de §8
- [13 · 04 — Animación de sprites, Sequences y Animation Curves](./04%20-%20Animaci%C3%B3n%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md) — `lerp` con `delta_time`, oscilaciones, Animation Curves
- [13 · 07 — Generación procedural avanzada](./07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md) — determinismo, ruido, `smoothstep` quíntico
- [13 · 08 — Físicas a mano y fluidos](./08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md) — muelles, amortiguación crítica, integradores

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/manual-lts-2026-es/`;
`gamemaker.io` devuelve 403 a las herramientas automáticas, de ahí el espejo):

- [Maths And Numbers — GML Reference](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Maths_And_Numbers.htm)
- `angle_difference` — la propiedad `src + angle_difference(dest, src) → dest`, y el criterio de signos
- `math_set_epsilon` — rango válido `0`–`0.999999999`, y que afecta a los seis operadores de comparación
- `random`, `randomise`, `random_set_seed` — semilla inicial fija, y el aviso de que **la misma semilla puede dar resultados distintos entre plataformas**
- `delta_time` — microsegundos
- `rectangle_in_rectangle` — devuelve `0`, `1` o `2`, no un booleano
- `int64`, `array_shuffle`, `array_shuffle_ext`, `dot_product_normalised`, `matrix_build`, `dbg_view`, `dbg_text`, `ref_create`

**Interpolación independiente de la tasa de fotogramas**

- Rory Driscoll, *Frame Rate Independent Damping using Lerp* (7 de marzo de 2016) — <https://www.rorydriscoll.com/2016/03/07/frame-rate-independent-damping-using-lerp/>. Publica las dos formas equivalentes: `Lerp(source, target, 1 - Pow(smoothing, dt))` y `Lerp(a, b, 1 - Exp(-lambda * dt))`, y define *smoothing* como «la proporción del origen que queda tras un segundo». Es la fórmula de §4.2.
- Scott Lembcke, *Improved Lerp Smoothing* (Game Developer, 4 de abril de 2018) — <https://www.gamedeveloper.com/programming/improved-lerp-smoothing->. Publica `value = lerp(target, value, exp2(-rate * deltaTime))` con la aclaración «con `rate = 1.0` el valor recorre la mitad de la distancia cada segundo». Es exactamente la formulación por media vida de §4.3 (`exp2(-rate*dt)` equivale a `power(0.5, dt/h)` con `h = 1/rate`).
- Freya Holmér, *Lerp smoothing is broken* (Guadalindie 2024, 30 de mayo de 2024) — <https://www.youtube.com/watch?v=LSNQuFEDOyQ>. ⚠️ La transcripción no se pudo extraer; se cita como referencia del problema, no como fuente de una fórmula concreta.

**Curvas, splines y easing**

- Squirrel Eiserloh, *Math for Game Programmers: Fast and Funky 1D Nonlinear Transformations* (GDC 2015) — <https://www.youtube.com/watch?v=mr5xkf6zSzk>. La versión de GDC Vault (<https://www.gdcvault.com/play/1022142/Math-for-Game-Programmers-Fast>) devuelve HTTP 402: es de pago. ⚠️ Los nombres de sus operaciones (`flip`, `smoothStart`, `smoothStop`, `scale`, `reverseScale`, `crossfade`) de §4.5 bis están verificados contra una implementación pública que cita la charla, **no** contra la transcripción original; las fórmulas sí son comprobables por álgebra elemental.
- Freya Holmér, *The Continuity of Splines* (diciembre de 2022) — <https://www.youtube.com/watch?v=jvPPXbo87ds>. ⚠️ Tampoco se pudo transcribir. Se cita como referencia de fondo para Bézier, Hermite, Catmull-Rom y la continuidad C⁰/C¹/C² y G¹/G²; la advertencia sobre la variante centrípeta de Catmull-Rom en §4.7 queda marcada como no verificada contra fuente primaria.
- *Easing Functions Cheat Sheet* — <https://easings.net/>. Las fórmulas están en su código fuente, `src/easings.yml` del repositorio <https://github.com/ai/easings.net>. De ahí salen las constantes que usa `scr_math_util` (`c1 = 1.70158` en `easeOutBack`, `n1 = 7.5625` y `d1 = 2.75` en `easeOutBounce`). La ruta `easings.net/es` devuelve 404: el sitio detecta el idioma del navegador y no usa subrutas.

**Rejillas, hexágonos y geometría**

- Amit J. Patel, *Hexagonal Grids* (Red Blob Games; creada en 2013, última modificación 24 de julio de 2026) — <https://www.redblobgames.com/grids/hexagons/> y su complemento de código <https://www.redblobgames.com/grids/hexagons/implementation.html>. De ahí salen literalmente las fórmulas axial→píxel y píxel→axial de §7.4, y la necesidad del redondeo en coordenadas cúbicas.
- Amit J. Patel, *Grid parts and relationships* — <https://www.redblobgames.com/grids/parts/>. Establece que el isométrico es solo una proyección de pantalla: la matemática de la rejilla es idéntica a la de una rejilla cuadrada, que es la base de §7.3.
- Amit J. Patel, *Line drawing on a grid* — <https://www.redblobgames.com/grids/line-drawing.html>. La formulación de `lerp` que cita esta biblioteca en §4.1: `start * (1.0 - t) + end * t`.
- W. Randolph Franklin, *PNPOLY — Point Inclusion in Polygon Test* — <https://wrfranklin.org/Research/Short_Notes/pnpoly.html>. El algoritmo de §6.3 es la traducción directa de su código C, incluida la comparación `(verty[i] > testy) != (verty[j] > testy)` que resuelve el caso de un vértice a la altura exacta del punto.
- Paul Bourke, *Intersection point of two line segments in 2 dimensions* — <http://paulbourke.net/geometry/pointlineplane/>. Publica las ecuaciones de partida y la condición del denominador nulo para el caso paralelo; ⚠️ la forma expandida de `ua`/`ub` de §6.5 y la extensión de la distancia punto-recta a punto-**segmento** (recortando el parámetro a `[0,1]`) son álgebra estándar derivada de esas ecuaciones, no citas literales de la página.

**Probabilidad**

- Amit J. Patel, *Probability and Games: Damage Rolls* (Red Blob Games; modificado el 22 de junio de 2026) — <https://www.redblobgames.com/articles/probability/damage-rolls.html>. Establece que, manteniendo el rango fijo, **más dados producen una distribución más estrecha**: es el fundamento de la función `campana` de §5.3.
- *Random Distribution* — Liquipedia Dota 2, <https://liquipedia.net/dota2/Random_Distribution>. Documenta `P(N) = C · N` y da las constantes verificadas de §5.7 (25 % → `C ≈ 0,0847`; 50 % → `C ≈ 0,3021`), junto con la progresión 8,5 % → 17 % → 25,5 % del ejemplo.
- *Box–Muller transform* — <https://en.wikipedia.org/wiki/Box%E2%80%93Muller_transform>. La forma básica `Z₀ = √(−2·ln U₁) · cos(2π·U₂)` que implementa `gauss()` en §5.3.
- *Tetris* — <https://en.wikipedia.org/wiki/Tetris>. Cita literal sobre el mecanismo de §5.5: «la distribución de tetrominós estaba completamente aleatorizada en las primeras versiones, mientras que las versiones modernas usan un “sistema de bolsa”, en el que se garantiza que cada tetrominó aparezca una vez por cada conjunto de siete». ⚠️ Las fuentes primarias de la guía oficial de Tetris (`tetris.wiki`, `harddrop.com`) devuelven HTTP 403 y no se pudieron verificar.
