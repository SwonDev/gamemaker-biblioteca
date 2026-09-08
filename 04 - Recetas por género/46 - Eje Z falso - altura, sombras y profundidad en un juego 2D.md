# 46 · Eje Z falso — altura, sombras y profundidad en un juego 2D

> **Dificultad:** media · **Técnica transversal, no un género.**
> Cómo simular que algo está «en el aire» en un juego que solo tiene dos coordenadas. Hace
> falta para saltar en un top-down (`04 · 02`), para el combate de un beat 'em up (`04 · 47`),
> para proyectiles con arco, para plataformas a distinta altura y para el aspecto isométrico.
> **No cubre**: el orden de dibujado básico por Y (`depth = -bbox_bottom`), que ya está resuelto
> en [`04 · 02` §4.4](./02%20-%20Top-Down%20_%20Twin-Stick.md); las máscaras de colisión reales
> (`01 · 08`); ni el 3D de verdad con cámara y `matrix_*`, que es [`04 · 29`](./29%20-%203D%20en%20GameMaker.md)
> y una herramienta totalmente distinta. Este documento es el punto intermedio: sigues en 2D,
> `x`/`y` no cambian de significado, y toda la altura es una **mentira dibujada**.

---

## 1 · Los principios

### 1.1 · El problema que resuelve

GameMaker en 2D tiene dos ejes. El suelo, las paredes, los enemigos y las balas viven en el
plano `(x, y)`. Pero un personaje que salta, una granada que traza un arco, o un guerrero
derribado que vuela hacia atrás **necesitan un tercer número** que suba y baje sin tocar ni la
posición en el suelo ni la colisión contra las paredes. Ese número no existe en el motor: te lo
inventas tú, y por eso es un **eje Z falso**. No es 3D — no hay perspectiva, ni una cámara que
gire, ni un `matrix_*` de por medio (eso es `04 · 29`, y es carísimo comparado con esto). Es
aritmética de instituto aplicada a dónde dibujas el sprite.

La distinción que hay que tener clara desde la primera línea:

| Coordenada | Qué mide | Quién la usa |
|---|---|---|
| `x`, `y` | Dónde está el personaje **en el suelo**. Es su sombra, su punto de apoyo, lo que choca con paredes | `move_and_collide`, `place_meeting`, el `depth`-sort |
| `z` (la que inventas aquí) | Cuánto se ha **despegado** del suelo, en píxeles | Solo el dibujado: dónde se pinta el sprite, y el tamaño/opacidad de la sombra |
| `depth` | Variable **nativa** de GameMaker que decide QUIÉN TAPA A QUIÉN al dibujar | El motor, una vez por instancia y por frame |

**La trampa de nombres que hay que evitar antes de escribir nada**: `depth` no es una
coordenada espacial, es un número de orden de dibujado — dos objetos pueden tener el mismo
`depth` y estar a alturas completamente distintas, o tener alturas iguales y `depth`s opuestos.
Confundir «está más alto» con «se dibuja delante» es el origen de la mitad de los bugs de este
documento (ver §5). Por eso aquí `z` es una variable de instancia normal y corriente, tan
inventada como `vel_x` o `hp`: `python3 "_indice/buscar.py" z` confirma que **no existe** como
variable del runtime, así que no colisiona con nada — al contrario que `depth`, `x` o `y`, que
sí son built-ins y están además en la lista de nombres prohibidos de esta biblioteca.

### 1.2 · Por qué «falso» no es un insulto

*The Legend of Zelda: A Link to the Past*, *Streets of Rage*, la mayoría de los *Pokémon* y
prácticamente todo juego isométrico de 16 bits usan exactamente esta técnica: dos ejes para el
mundo, un tercer número inventado para la altura, dibujado con un simple desplazamiento
vertical del sprite. Es barato (no hay geometría 3D que procesar), es predecible (la colisión
sigue siendo un rectángulo en 2D, no un volumen) y cubre el 90 % de los casos donde un juego
"parece" tener profundidad sin necesitarla de verdad. La sección 8 dice exactamente dónde deja
de compensar.

### 1.3 · El contrato que hay que respetar siempre

1. **`z` nunca participa en la colisión.** `move_and_collide`, `place_meeting`,
   `instance_place`... todos siguen leyendo solo `x`/`y`. Un personaje saltando sigue
   chocando con las paredes exactamente igual que si no hubiera saltado.
2. **`z` solo mueve el DIBUJO**, restando de la posición vertical de pantalla: el sprite se
   pinta en `y - z`, nunca la instancia se mueve a `y - z`.
3. **El `depth`-sort usa la posición de suelo, no la de dibujo.** Si ordenas por `y - z`, un
   salto alto te dibuja mal delante o detrás de las paredes según lo alto que estés en vez de
   según dónde estás parado. Es la trampa más citada de este documento (§5.1).
4. **La sombra vive en el suelo**, en `(x, y)`, no en `(x, y - z)`. Es lo que ancla visualmente
   la altura: sin sombra, el ojo no puede distinguir "está lejos" de "está en el aire".

---

## 2 · El método, paso a paso

```
1. Añade z y zvel a la entidad — variables de instancia normales, no built-ins.
2. En el Step: aplica gravedad a zvel, luego zvel a z. Si z <= 0 → aterrizó (z = 0, zvel = 0).
3. El movimiento en el suelo (vel_x/vel_y con move_and_collide) es COMPLETAMENTE independiente:
   se sigue calculando y aplicando igual, esté z en 0 o en 80.
4. En el Draw: dibuja el sprite en (x, y - z). Nunca cambies x/y de verdad.
5. Dibuja la sombra en (x, y), con escala y alfa en función de z (más alto = más pequeña
   y más clara).
6. El depth-sort (04 · 02 §4.4) sigue leyendo bbox_bottom / y de SUELO. z no entra ahí.
```

Ese es el esqueleto entero. Todo lo que sigue son variaciones sobre este mismo patrón: saltar,
lanzar algo con arco, tener suelos a distinta altura, y qué hacer con la cámara y el orden de
dibujado cuando el eje Z falso empieza a mezclarse con paredes, agua o una vista isométrica.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 · Las variables base

```gml
/// obj_entidad_saltable — Create
/// (padre de cualquier cosa que se despegue del suelo: jugador, enemigo, proyectil)

// --- Posición en el suelo: la de siempre, no toques nada aquí ---
// x, y ya existen como variables nativas y siguen siendo la verdad del lugar
// donde está parado. move_and_collide() sigue leyendo/escribiendo estas dos.

// --- Eje Z falso: inventado, solo para el dibujado ---
z             = 0;      // altura sobre el suelo, en píxeles. 0 = pisando el suelo.
zvel          = 0;      // velocidad vertical en el eje falso (positivo = subiendo)
en_el_suelo   = true;

#macro GRAV_Z 0.6        // gravedad del salto, en píxeles/frame². Ajusta al gusto.
```

> ⚠️ `z` y `zvel` **no existen** como símbolos del runtime — confirmado con
> `python3 "_indice/buscar.py" z` y `python3 "_indice/buscar.py" zvel` (ninguno aparece: no hay
> nada parecido que sugerir). Son nombres libres. No lo son, en cambio, `x`, `y`, `depth`,
> `speed`, `direction`: si les asignas algo, estás moviendo la instancia o pisando el
> orden de dibujado del motor sin darte cuenta — la advertencia del apartado 4 de `AGENTS.md`.

### 3.2 · Gravedad y aterrizaje: el Step

```gml
/// obj_entidad_saltable — Step (después de mover x/y con move_and_collide)

if (!en_el_suelo || zvel != 0)
{
    zvel -= GRAV_Z;
    z    += zvel;

    if (z <= 0)
    {
        z           = 0;
        zvel        = 0;
        en_el_suelo = true;
        // Aquí engancha el "aterrizaje": polvo, sonido de impacto, squash (04 · 15).
    }
}
```

**Por qué esto no es lo mismo que la gravedad de `04 · 01`**: en un plataformas, la gravedad
tira de `vel_y`, que se suma a `y`, y `y` sí choca contra el suelo real (`move_and_collide`
detiene la caída). Aquí `z` no choca con nada — el "suelo" contra el que aterriza es
simplemente `z == 0` por convención matemática, no una colisión. Esa es la simplificación
completa que hace que el eje Z falso sea barato: no hace falta un segundo `move_and_collide`
en un eje vertical imaginario.

### 3.3 · Saltar: el disparador

```gml
/// obj_jugador_top_down — Step (antes o después del movimiento en el suelo, da igual)

if (en_el_suelo && keyboard_check_pressed(vk_space))
{
    zvel        = 9;         // impulso inicial hacia "arriba"
    en_el_suelo = false;
}
```

Nótese que el salto **no** cancela ni pausa el movimiento en el suelo: `vel_x`/`vel_y` se
siguen calculando y aplicando con `move_and_collide` exactamente igual saltando que sin
saltar. Es la diferencia clave frente a un plataformas: aquí saltar es "despegarse
visualmente", no "el único eje contra el que hay gravedad".

### 3.4 · Dibujar en `y - z`, colisionar en `(x, y)`

```gml
/// obj_entidad_saltable — Draw
draw_sprite_ext(sprite_index, image_index, x, y - z, image_xscale, image_yscale,
                 image_angle, image_blend, image_alpha);
```

`draw_self()` a secas dibuja en `(x, y)`: no sirve en cuanto `z != 0`. Hay que sustituirlo por
`draw_sprite_ext` (o `draw_sprite`, si no necesitas escala/ángulo/color) apuntando explícitamente
a `y - z`. Esto es LO ÚNICO que cambia visualmente: la máscara de colisión, que GameMaker calcula
sobre la posición real `(x, y)`, sigue intacta y sigue siendo donde el personaje puede o no
recibir un golpe por contacto de cuerpo — el salto no lo hace invulnerable a proyectiles que
vayan por el suelo, a menos que tú decidas explícitamente que sí (ver §3.9).

### 3.5 · La sombra: encoge y se aclara con la altura

> ⚠️ **Esta función va en un script, no en el `Draw` de `obj_entidad_saltable`.** Este mismo
> documento la reutiliza desde `obj_jugador_top_down` (§3.7), `obj_proyectil_arco` (§3.9) y
> `obj_entidad_iso` (§4) — objetos distintos, sin relación de herencia entre ellos. Un
> `function nombre() {...}` declarado dentro de un evento queda ligado a esa instancia como una
> variable más de `self`, no como un identificador global: solo lo llamaría sin reventar el
> propio `obj_entidad_saltable`. Como aquí la va a llamar cualquiera, vive en un script
> (`scr_eje_z_falso.gml`) desde el principio — el mismo razonamiento que
> [`04 · 19` §1](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#1--el-conductor).
> No necesita ningún `with`: no lee ni escribe variables de instancia, solo los parámetros que
> recibe.

```gml
/// scr_eje_z_falso.gml

/// @func sombra_dibujar(_x, _y, _z, _radio_base, _z_max_visible)
/// @desc Sombra elíptica en el suelo. Encoge y se aclara cuanto más alto está
///       el objeto; desaparece del todo por encima de `_z_max_visible`.
/// @param {Real} _x             Posición de suelo X.
/// @param {Real} _y             Posición de suelo Y.
/// @param {Real} _z             Altura actual.
/// @param {Real} _radio_base    Radio de la sombra a ras de suelo.
/// @param {Real} _z_max_visible Altura a la que la sombra ya no se ve.
function sombra_dibujar(_x, _y, _z, _radio_base, _z_max_visible)
{
    var _t = clamp(_z / _z_max_visible, 0, 1);       // 0 = suelo, 1 = altura máxima
    var _radio = lerp(_radio_base, _radio_base * 0.35, _t);
    var _alfa  = lerp(0.45, 0.08, _t);

    draw_set_alpha(_alfa);
    draw_ellipse_color(_x - _radio, _y - _radio * 0.4,
                        _x + _radio, _y + _radio * 0.4,
                        c_black, c_black, false);
    draw_set_alpha(1);
}
```

```gml
/// obj_entidad_saltable — Draw
sombra_dibujar(x, y, z, sprite_width * 0.3, 120);
draw_sprite_ext(sprite_index, image_index, x, y - z, image_xscale, image_yscale,
                 image_angle, image_blend, image_alpha);
```

**Por qué una elipse y no un sprite**: es la opción de coste cero — no hay que dibujar ni
exportar un asset extra, y `draw_ellipse_color` ya acepta dos colores para dar un ligero
degradado. Si tu juego tiene un estilo de pixel art marcado, cambia la elipse por un sprite de
sombra fijo (`spr_sombra_oval`) escalado con `image_xscale`/`image_yscale` en función de `_t`:
el mismo cálculo de `_radio`/`_alfa`, solo cambia la llamada de dibujo.

> 💡 `13 · 03` §6 (Pixel art y resolución) ya señala que **la sombra proyectada bajo el
> personaje es "el píxel mejor invertido de todo el sprite"**: es la señal más barata de que
> algo tiene volumen. Este documento es la mecánica que hay detrás de esa frase.

### 3.6 · El orden de dibujado, con `z` de por medio

Esta sección **no repite** la técnica base de `04 · 02` §4.4 (`depth = -bbox_bottom`, o el
`objDepthSorter` de su §5.6): esa sigue siendo la forma de decidir quién tapa a quién. Lo que
añade el eje Z falso es una regla que hay que respetar para no romperla:

```gml
/// obj_entidad_saltable — End Step
// El depth-sort usa SIEMPRE la posición de pie en el suelo, nunca la de dibujo.
// z puede valer 80 y esto no debe cambiar ni una unidad.
depth = -bbox_bottom;
```

**La trampa exacta**: si en algún punto escribes `depth = -(bbox_bottom - z)` (razonamiento
intuitivo: "está más arriba, se dibuja más atrás"), un salto alto hace que el personaje se
dibuje delante de columnas y paredes por las que en realidad está pasando por detrás en el
plano del suelo — o al revés. `depth` decide **quién tapa a quién en la pantalla**, y esa
pregunta la responde la posición donde estás parado, no lo despegado que estés de ella. La
única vez que la altura debería influir en el orden de dibujado es cuando el objeto ya no está
sobre el "carril" del suelo en absoluto (una plataforma elevada que de verdad está en otra
capa — ver §3.8), y en ese caso ya no es una cuestión de `z`, es una cuestión de a qué **zona de
suelo** perteneces.

Tres formas de resolver el orden de dibujado en total, y cuándo usar cada una:

| Técnica | Cuándo usarla | Coste |
|---|---|---|
| `depth` fijo por tipo de objeto (asignado una vez, en el Create) | Capas que nunca se cruzan entre sí: fondo, suelo, HUD | Ninguno — ni siquiera hace falta recalcular |
| `depth = -bbox_bottom` dinámico, cada Step/End Step | Entidades que se mueven por el mismo plano y pueden pasar unas por delante de otras (jugador, enemigos, árboles) | Una escritura por instancia y frame — barato |
| Ordenar a mano con un controlador (`objDepthSorter`, `04 · 02` §5.6) | Cientos de instancias donde escribir `depth` disperso genera *overhead* de reordenación interna | Un `array_sort()` por frame, pero una sola pasada en vez de N |

### 3.7 · Saltar en un top-down: uniendo todo

```gml
/// obj_jugador_top_down — Create
vel_x = 0;
vel_y = 0;
z     = 0;
zvel  = 0;
en_el_suelo = true;

/// obj_jugador_top_down — Step
// 1. Movimiento en el suelo: igual que en 04 · 02 §4.1-§4.2, sin cambios.
var _ix = (keyboard_check(vk_right) - keyboard_check(vk_left));
var _iy = (keyboard_check(vk_down)  - keyboard_check(vk_up));
if (_ix != 0 || _iy != 0)
{
    var _dir = point_direction(0, 0, _ix, _iy);
    vel_x = lengthdir_x(3, _dir);
    vel_y = lengthdir_y(3, _dir);
}
else
{
    vel_x = 0;
    vel_y = 0;
}
move_and_collide(vel_x, vel_y, obj_solido, 4, 0, 0, 8, 8);

// 2. Salto: solo afecta a z.
if (en_el_suelo && keyboard_check_pressed(vk_space))
{
    zvel        = 9;
    en_el_suelo = false;
}

// 3. Física del eje falso.
if (!en_el_suelo)
{
    zvel -= GRAV_Z;
    z    += zvel;
    if (z <= 0) { z = 0; zvel = 0; en_el_suelo = true; }
}

// 4. Depth-sort: siempre con la posición real, nunca con y - z.
depth = -bbox_bottom;

/// obj_jugador_top_down — Draw
sombra_dibujar(x, y, z, sprite_width * 0.3, 100);
draw_sprite_ext(sprite_index, image_index, x, y - z, image_xscale, image_yscale,
                 image_angle, image_blend, image_alpha);
```

Este es el `objPlayer` de `04 · 02` con exactamente ocho líneas nuevas repartidas en tres
sitios. Todo lo demás — cámara, disparo, animación — sigue funcionando sin tocarlo.

### 3.8 · Suelos a distinta altura: plataformas, escalones y pozos

Un top-down con plataformas elevadas necesita responder a una pregunta que `move_and_collide`
por sí solo no resuelve: *¿puedo caminar por aquí, o tengo que haber saltado primero?* La
solución es una zona de suelo — el mismo patrón que `obj_camara_zona` en
[`13 · 19` §3.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/19%20-%20Cámaras%20de%20juego%20-%20encuadre,%20seguimiento%20y%20control.md#35-region-based-anchors-zonas-de-cámara),
aplicado a la altura del suelo en vez de al encuadre de cámara:

```gml
/// obj_zona_altura — objeto invisible, estirado en el Room Editor sobre el área
/// de una plataforma, un escalón o un pozo.
/// Variables de instancia (una por zona, puestas en el editor):
///   altura_suelo : 0     — altura de ESTE trozo de suelo, en píxeles.
///                          Positivo = plataforma elevada. Negativo = pozo/hueco.
///   solido_desde : 8     — si el jugador está a z >= a esta distancia POR ENCIMA
///                          de altura_suelo, puede aterrizar aquí (viene saltando).

/// obj_zona_altura — Create
altura_suelo = 0;
solido_desde = 8;
```

> ⚠️ **`suelo_altura_en()` va en `scr_eje_z_falso.gml` (§3.5), no en este `Create`.** La llama
> `obj_jugador_top_down` (abajo) — un objeto distinto de `obj_zona_altura` — y por dentro ya usa
> `with (obj_zona_altura) {...}`, así que no depende en absoluto de quién la invoque. El único
> motivo para que reviente es dejarla ligada al evento equivocado: mismo mecanismo que el resto
> de este documento y de [`04 · 19` §1](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#1--el-conductor).

```gml
/// scr_eje_z_falso.gml (continuación de §3.5)

/// @func suelo_altura_en(_x, _y)
/// @desc Altura del suelo bajo un punto. 0 si no hay ninguna zona (suelo raso).
///       Si dos zonas se solapan (un escalón dentro de una plataforma), gana
///       la de mayor altura_suelo: coloca las zonas más altas DESPUÉS en el
///       Room Editor si quieres forzar el desempate a mano.
function suelo_altura_en(_x, _y)
{
    var _mejor = 0;
    with (obj_zona_altura)
    {
        if (point_in_rectangle(_x, _y, bbox_left, bbox_top, bbox_right, bbox_bottom))
        {
            _mejor = max(_mejor, altura_suelo);
        }
    }
    return _mejor;
}
```

```gml
/// obj_jugador_top_down — Step (añadido tras la física del eje falso)
var _suelo_aqui = suelo_altura_en(x, y);

if (en_el_suelo)
{
    // Reengancha al nuevo nivel de suelo al caminar de una zona a otra sin saltar
    // (subir una rampa suave, o bajar un escalón pequeño sin caer).
    z = _suelo_aqui;
}
else if (zvel <= 0 && (z - _suelo_aqui) <= 4)
{
    // Aterrizaje: solo "engancha" al suelo si venías cayendo Y estás a su altura.
    // Sin la comprobación de z, un salto normal en suelo raso "aterrizaría" de
    // golpe sobre cualquier plataforma que pises por debajo mientras subes.
    z           = _suelo_aqui;
    zvel        = 0;
    en_el_suelo = true;
}
```

**Colisión «solo si estoy a esta altura»**: la pared invisible que bloquea el paso a una
plataforma elevada (para que no se pueda subir caminando, solo saltando) es un `obj_solido`
normal — pero solo debe bloquear si el jugador **no** está ya a esa altura:

```gml
/// obj_borde_plataforma — objeto sólido en el borde de una plataforma elevada.
/// Bloquea el paso salvo que el jugador esté a la altura de la plataforma
/// (ya saltó y está aterrizando encima) o por debajo de ella del todo (pasa
/// caminando por debajo, como un puente).

/// obj_jugador_top_down — Step (antes de move_and_collide)
with (obj_borde_plataforma)
{
    var _bloquea = (other.z < altura_bloqueo - 4) && (other.z > altura_paso_libre + 4);
    solid = _bloquea;   // variable nativa: activa/desactiva la colisión sólida
}
```

Un **pozo** es el mismo sistema con `altura_suelo` negativo: si `z <= altura_suelo` (el
jugador ha caído por debajo del nivel de suelo normal), se dispara la caída — quitar vida,
teletransportar al último punto seguro, o lo que pida el diseño. No hace falta ningún sistema
nuevo, es la misma comparación de `z` contra `suelo_altura_en()` mirando hacia abajo en vez de
hacia arriba.

### 3.9 · Proyectiles con arco, y su sombra

Una granada, una flecha lobbeada, un balón que bota: todos son la misma física del §3.2 pero
sin depender del jugador — el proyectil entero es una entidad con `x`, `y`, `z`, `zvel` propios,
y con velocidad horizontal constante mientras el eje falso hace su parábola.

```gml
/// obj_proyectil_arco — Create
/// @param {Real} _dir      Dirección horizontal de lanzamiento (grados).
/// @param {Real} _dist     Distancia horizontal total que debe recorrer.
/// @param {Real} _altura   Altura máxima del arco, en píxeles.
function proyectil_arco_lanzar(_dir, _dist, _altura)
{
    // Tiempo de vuelo en frames, despejado de la parábola: sube y baja
    // con la misma gravedad, así que el tiempo total es el doble del tiempo
    // de subida. v0 = sqrt(2 * GRAV_Z * _altura); tiempo_subida = v0 / GRAV_Z.
    var _v0             = sqrt(2 * GRAV_Z * _altura);
    var _frames_totales = max(1, round((_v0 / GRAV_Z) * 2));

    vel_x = lengthdir_x(_dist / _frames_totales, _dir);
    vel_y = lengthdir_y(_dist / _frames_totales, _dir);
    z     = 0;
    zvel  = _v0;
}

/// obj_proyectil_arco — Step
x    += vel_x;
y    += vel_y;
zvel -= GRAV_Z;
z    += zvel;

if (z <= 0)
{
    z = 0;
    // Impacto: crear la explosión/salpicadura AQUÍ, en (x, y) — no en (x, y - z).
    instance_create_layer(x, y, layer, obj_explosion);
    instance_destroy();
}

/// obj_proyectil_arco — Draw
sombra_dibujar(x, y, z, 6, 96);
draw_sprite_ext(sprite_index, image_index, x, y - z, image_xscale, image_yscale,
                 image_angle, image_blend, image_alpha);
```

`sqrt` (`python3 "_indice/buscar.py" sqrt`) y el resto de funciones de esta sección ya estaban
verificadas para el resto del documento. La sombra del proyectil es la pista visual que le dice
al jugador **dónde va a caer** antes de que caiga — en un shmup o un shooter top-down es,
literalmente, la telegrafía del golpe (`13 · 18` la llama así para los ataques de jefe).

### 3.10 · Agua y profundidad

El mismo eje, con el signo invertido y una lectura distinta: en vez de "cuánto me he
despegado del suelo", `z` pasa a significar "cuánto me he hundido". Es útil para una piscina,
un río poco profundo o un pantano donde el personaje se mueve más lento cuanto más hondo entra:

```gml
/// obj_jugador_top_down — Step (variante para zonas de agua)
var _en_agua = place_meeting(x, y, obj_zona_agua);

if (_en_agua)
{
    z = approach(z, -12, 0.5);     // "approach": scr_math_util, 06 · scr_math_util.gml
    var _factor_lentitud = 1 - (abs(z) / 24);   // más hondo, más lento
    vel_x *= _factor_lentitud;
    vel_y *= _factor_lentitud;
}
else
{
    z = approach(z, 0, 1.5);       // sale del agua: vuelve a la superficie
}

image_blend = merge_color(c_white, c_blue, clamp(abs(z) / 24, 0, 0.5));
```

La sombra en agua se sustituye por un **círculo de ondas** en la superficie (`z = 0` lógico,
aunque el sprite se dibuje más abajo por estar hundido) en vez de una elipse oscura — la misma
función `sombra_dibujar()` sirve de base, solo cambia qué dibuja en el hueco.

---

## 4 · El caso isométrico

En isométrico, la proyección de pantalla ya no es una identidad (`pantalla = mundo`): el
mundo se proyecta a un rombo. Las fórmulas de conversión están completas en
[`13 · 13` §7.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md#73--isométrico-rombo-21)
(`iso_desde_celda`, `celda_desde_iso`, `ISO_ANCHO`/`ISO_ALTO`) y **no se repiten aquí**. Lo
único que aporta este documento es cómo se compone el eje Z falso con esa proyección, porque la
pregunta "¿dónde dibujo algo que ha saltado, en un mundo isométrico?" tiene una respuesta
sorprendentemente simple:

```gml
/// obj_entidad_iso — Draw
var _pantalla = iso_desde_celda(col, fila);   // 13 · 13 §7.3
sombra_dibujar(_pantalla.x, _pantalla.y, z, ISO_ANCHO * 0.25, 80);
draw_sprite_ext(sprite_index, image_index, _pantalla.x, _pantalla.y - z,
                 image_xscale, image_yscale, image_angle, image_blend, image_alpha);
```

**`z` sigue restando de la coordenada de pantalla vertical, exactamente igual que en top-down**
— la proyección isométrica solo cambia cómo se calcula esa coordenada a partir de la celda, no
lo que la altura le hace después. Y el orden de dibujado tampoco cambia de criterio: `13 · 13`
§7.3 ya deja dicho que se pinta con `depth = -(col + fila)`, usando la celda lógica — nunca la
`z` del salto, por la misma razón exacta del §3.6: la altura es dibujo, la celda es dónde estás
parado. El único matiz nuevo es el desempate cuando **dos objetos comparten la misma celda**
(uno saltando sobre el otro): ahí sí hace falta un segundo criterio, y el más simple es sumar
una fracción de `z` solo para ese caso — `depth = -(col + fila) - (z * 0.001)` — lo bastante
pequeña para que nunca invierta el orden entre celdas distintas, solo desempate dentro de la
misma.

---

## 5 · Interacción con `04 · 29` — cuándo esto deja de compensar

`04 · 29` §"La decisión que va antes del código" ya traza la frontera para el 3D en general;
aquí se aplica al caso concreto de la altura:

| Si tu juego necesita… | El eje Z falso… |
|---|---|
| Saltar en un top-down, un beat 'em up, o lanzar algo con arco | Compensa siempre. Es la herramienta correcta, no un parche. |
| Varias entidades a distinta altura que deben **colisionar entre sí en 3D** (un salto que esquiva un barrido bajo pero no uno alto) | Empieza a doler: hace falta comparar rangos de `z` a mano en cada choque (ver `04 · 47` §4 para el caso concreto del beat 'em up) |
| Una cámara que **rota** alrededor de la escena, o mira en perspectiva desde un ángulo variable | Se rompe: la sombra y el offset de dibujo asumen una cámara cenital o isométrica fija. Eso es una cámara 3D real (`04 · 29` §7) |
| Geometría que se **oculta detrás de otra geometría** según el ángulo de vista (un pilar que tapa según por dónde mires) | No lo resuelve nunca: eso es oclusión 3D real, con un `z-buffer` (`04 · 29`) |
| Terreno con pendientes de verdad, no plataformas planas a distinta altura | Ninguno de los dos: es `04 · 37` (traversal en plataformas, heightmap por tile) si sigues en 2D lateral, o 3D real si el terreno es libre |

La pregunta de decisión, en una frase: si la altura solo necesita **subir y bajar en pantalla**
sin que la cámara se mueva alrededor de la escena, el eje Z falso es más barato y más fácil de
depurar que el 3D real. En cuanto la cámara necesita girar o algo necesita ocultarse detrás de
otra cosa según el ángulo, has salido de este documento.

---

## 6 · Checklist

- [ ] `z` y `zvel` son variables de instancia propias, **no** built-ins (verificado: no existen
      en el runtime) y nunca se leen dentro de `move_and_collide`/`place_meeting`.
- [ ] El sprite se dibuja en `(x, y - z)`; la instancia real sigue en `(x, y)`.
- [ ] El `depth`-sort usa `bbox_bottom` o `y` de suelo — **nunca** `y - z`.
- [ ] Hay una sombra en `(x, y)` que encoge y se aclara con `z` creciente.
- [ ] El aterrizaje comprueba `z <= suelo_altura_en(x, y)` con la zona correcta, no solo `z <= 0`
      a secas, si el nivel tiene plataformas a distinta altura.
- [ ] Los proyectiles con arco usan su propio `z`/`zvel` independientes del jugador.
- [ ] En isométrico, `z` sigue restando de la coordenada de pantalla; el `depth`-sort sigue
      usando `col + fila`, no `z`.
- [ ] Se ha decidido explícitamente si un ataque/proyectil que va "por el suelo" puede fallar
      contra alguien con `z` suficiente (salto que esquiva un barrido) — por defecto, no lo hace
      solo.

---

## 7 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Arreglo |
|---|---|---|
| Ordenar el `depth` con `y - z` en vez de con `y`/`bbox_bottom` | Un salto alto se dibuja mal delante o detrás de paredes según lo alto que se está, en vez de según dónde se está parado | `depth = -bbox_bottom`, calculado con la posición REAL, sin restar `z` (§3.6) |
| Escribir `y -= z` en vez de dibujar en `y - z` | El personaje "salta" de verdad en el plano de colisión: atraviesa paredes que debería chocar, o dispara el aterrizaje contra suelos que no tocaba | `z` no toca nunca `x`/`y`. Solo se lee en el evento Draw |
| Sombra fija de tamaño y alfa, sin depender de `z` | El salto "se siente" plano — no hay pista visual de la altura | `sombra_dibujar()` con `_t = z / z_max` interpolando radio y alfa (§3.5) |
| Aterrizar comparando solo `z <= 0` en un nivel con plataformas | El jugador atraviesa plataformas elevadas al caer, o "aterriza" en el aire sobre una plataforma que no debería alcanzar todavía | Comparar contra `suelo_altura_en(x, y)`, no contra 0 a secas (§3.8) |
| Sombra dibujada DESPUÉS del sprite en el mismo evento Draw | La sombra tapa los pies del personaje en vez de quedar debajo | Dibujar primero la sombra, luego el sprite, en ese orden dentro del mismo Draw |
| Reutilizar el `z` del salto para el `elevacion`/juggle de `04 · 30` sin decidirlo a propósito | El golpe que lanza por los aires mueve la `y` real (como hace `04 · 30` §5.7, pensado para un hack-and-slash sin carril de profundidad) y el personaje "flota" fuera de su carril de colisión en un juego que sí tiene eje Z falso | Decide explícitamente cuál de los dos sistemas manda: si tu juego usa este documento, redirige `elevacion` a sumar a `zvel` en vez de a `vel_y` — ver `04 · 47` §3 |
| Cámara isométrica que gira o hace zoom variable con este sistema tal cual | La sombra y el offset de altura empiezan a verse en el ángulo equivocado en cuanto la cámara deja de ser cenital/isométrica fija | Eso ya no es este documento: `04 · 29` §7 (cámaras 3D) |
| Suelos a distinta altura sin `solido_desde`/margen de tolerancia | El jugador "engancha" al suelo de una plataforma nada más rozarla con un salto muy bajo, o rebota al aterrizar por 1 píxel de diferencia | Usa un margen (`4` px en los ejemplos de §3.8), no una igualdad exacta |

---

## Ver también

- [04 · 02 — Top-Down / Twin-Stick](./02%20-%20Top-Down%20_%20Twin-Stick.md) §4.4 — el
  `depth = -bbox_bottom` base que este documento extiende, no repite.
- [04 · 01 — Plataformas 2D](./01%20-%20Plataformas%202D.md) — la gravedad, el salto y la
  máquina de estados de las que este documento toma prestado el patrón, aplicado a un eje que
  ya no colisiona con nada.
- [04 · 47 — Beat 'em up y brawler](./47%20-%20Beat%20em%20up%20y%20brawler.md) — el uso más
  exigente de este sistema: alinear a varias entidades en el mismo carril de Z para que un
  golpe conecte.
- [04 · 12 — Carreras y vehículos](./12%20-%20Carreras%20y%20vehículos.md) — rampas y saltos de
  vehículo son el mismo patrón de `z`/`zvel` aplicado a un objeto con inercia propia.
- [04 · 37 — Traversal en plataformas](./37%20-%20Traversal%20en%20plataformas%20-%20pendientes%2C%20paredes%2C%20escaleras%20y%20bordes.md) —
  cuando la altura del suelo es una pendiente continua, no una plataforma plana: es terreno de
  heightmap por tile, no de zonas de altura.
- [04 · 29 — 3D en GameMaker](./29%20-%203D%20en%20GameMaker.md) — dónde este documento deja de
  compensar y hace falta una cámara y un `z-buffer` de verdad (§5 de este documento).
- [04 · 30 — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) §5.7 —
  su campo `elevacion` mueve la `y` real para un juggle simple; este documento es la alternativa
  cuando el juego sí necesita un carril de suelo independiente de la altura del golpe.
- [13 · 19 — Cámaras de juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/19%20-%20Cámaras%20de%20juego%20-%20encuadre%2C%20seguimiento%20y%20control.md) §3.5 —
  el patrón de «zona» del que `obj_zona_altura` (§3.8) es una variación aplicada al suelo en vez
  de a la cámara.
- [13 · 13 — Matemáticas aplicadas al juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) §7.3 —
  la proyección isométrica completa (mundo↔pantalla, orden de dibujado por celda) que el §4 de
  este documento usa sin repetir.
- [13 · 03 — Pixel art y resolución](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md) §6 —
  por qué la sombra proyectada es "el píxel mejor invertido" de un sprite.
- [06 · `scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml) — `approach()`,
  usado en §3.10 para el amortiguado al entrar y salir del agua.

---

## Fuentes

- Manual oficial de GameMaker — `draw_sprite_ext`, `draw_ellipse_color`, `move_and_collide`,
  `point_in_rectangle` — `09 - Manual oficial/manual-lts-2026-es/` (espejo local, consultado
  2026-09-06).
- Amit J. Patel, *Grid parts and relationships*, Red Blob Games —
  <https://www.redblobgames.com/grids/parts/> — citado también por `13 · 13`: el isométrico es
  una proyección de pantalla, no una rejilla distinta.
- El propio código verificado de esta biblioteca en `04 · 02` (depth-sort), `04 · 01`
  (patrón de gravedad y salto) y `13 · 13` §7.3 (isométrico), usados aquí como base sin
  duplicar su contenido.
