# 06 · Disparar proyectiles

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 6 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=c_pgGGkc2oc> |
| **Duración** | 40 min 6 s |
| **Publicado** | 26 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `speed`/`direction`, `point_direction`, `lengthdir_x/y`, `draw_sprite_ext`, `angle_difference`, `string()`, variables globales |

Capítulo lleno de primicias: el sistema `speed`/`direction`, las **variables globales**,
los **scripts**, la trigonometría útil de `lengthdir_*` y el dibujado avanzado con
`draw_sprite_ext()`. Incluye además dos sesiones de **depuración en directo**.

## Índice de contenido

1. El sprite de la bala y la convención de ángulos
2. `speed` y `direction`: movimiento automático
3. Cadencia de disparo con un temporizador
4. Crear la bala y apuntarla con `point_direction()`
5. La explosión: animación y evento Animation End
6. Fuera de la room: limpiar memoria
7. Colisiones de la bala con `hspeed` / `vspeed`
8. Variables globales y puntuación
9. Dibujar texto con `string()`
10. Destruir bloques y sumar puntos
11. Práctica avanzada: pistola giratoria y `draw_sprite_ext()`
12. Práctica avanzada: disparar desde la boca del cañón
13. Práctica avanzada: rotar al jugador con `angle_difference()`

---

## 1. El sprite de la bala y la convención de ángulos

Crea **`sBullet`** de **5 × 5**, FPS 0, origen **Middle Center**.

Como la bala va a **rotar** para mirar hacia donde vuela, necesita **direccionalidad**
en su diseño: el autor le dibuja una especie de «cola».

> **Convención de ángulos en GameMaker:** `0` es **derecha**, `90` es **arriba**,
> `180` es **izquierda** y `270` es **abajo**.

Por eso, **todo lo que deba rotar se diseña mirando a la derecha**, y luego se rota
por código.

Revisa la **máscara de colisión** y asegúrate de que sea la imagen completa: donde
choque la bala importa para la mecánica.

Crea el objeto **`oBullet`** y asígnale el sprite.

---

## 2. `speed` y `direction`: movimiento automático

**Create event de `oBullet`:**

```gml
speed = 9;   // Píxeles por fotograma
```

Es la primera vez que aparece `speed`. Es una **propiedad integrada**:

- Todos los objetos tienen `speed = 0` y `direction = 0` por defecto.
- `direction = 0` significa «hacia la derecha», pero **con `speed` 0 no se mueve**.
- Al fijar `speed`, GameMaker **calcula automáticamente** cuántos píxeles son
  horizontales y cuántos verticales, y los guarda en **`hspeed`** y **`vspeed`**.

Es un sistema precioso: fijas `speed` y `direction`, y puedes leer `hspeed` y
`vspeed` para tus colisiones.

---

## 3. Cadencia de disparo con un temporizador

Queremos que **al mantener pulsado el ratón el jugador dispare sin parar**, con un
intervalo entre balas.

**Create event de `oPlayer`:**

```gml
attack_cooldown_max = 6;   // Fotogramas entre cada bala
attack_cooldown = 0;       // Temporizador de cuenta atrás
```

Se inicializa a **0** para que **el primer clic dispare de inmediato**.

**En la región ENTRADAS del Step:**

```gml
var _key_attack = mouse_check_button(mb_any);
```

> **⚠️ Error real del tutorial:** el autor escribe primero `keyboard_check(mb_any)` y
> el juego no dispara. Lo detecta al ejecutar y lo corrige en directo: `mb_any`
> **solo** funciona con las funciones de ratón.
>
> «Estamos depurando en directo dentro del tutorial, y eso te pasará en tus propios
> proyectos. Por eso ejecutamos el juego tan a menudo.»

---

## 4. Crear la bala y apuntarla con `point_direction()`

**Nueva región SHOOTING en el Step de `oPlayer`:**

```gml
#region DISPARO
if (_key_attack)
{
    if (attack_cooldown <= 0)
    {
        // --- Disparar una bala ---
        var _bullet = instance_create_layer(x, y, "Instances", oBullet);

        with (_bullet)
        {
            // Ángulo desde la bala hasta el ratón
            direction = point_direction(x, y, mouse_x, mouse_y);

            // Girar el sprite para que mire en esa dirección
            image_angle = direction;
        }

        attack_cooldown = attack_cooldown_max;   // Reiniciar el temporizador
    }
    else
    {
        attack_cooldown--;   // Aún no toca: descontar un fotograma
    }
}
else
{
    // Si no se pulsa, resetear para que el próximo clic dispare al instante
    attack_cooldown = 0;
}
#endregion
```

### `point_direction()`

```gml
point_direction(x1, y1, x2, y2)
```

Traza una línea imaginaria entre dos puntos y **devuelve su ángulo** (de 0 a 360).

### `image_angle`

Es la **rotación del sprite** en grados. Igualándola a `direction`, la bala mira
siempre hacia donde vuela.

> El autor usa `<= 0` en lugar de `== 0` porque es **más inclusivo** y evita saltarse
> el valor por un descentraje.

---

## 5. La explosión: animación y evento Animation End

Crea **`sBulletExplode`** de **7 × 7** (más grande que la bala de 5 × 5).

> **¿Por qué más grande?** Porque la explosión **sustituye** a la bala justo donde
> impacta, y queremos que **se solape ligeramente** con lo que ha golpeado. Ese
> solapamiento es lo que nos permitirá luego usar `place_meeting()` para **hacer
> daño**.

- **FPS:** 30.
- **Origen:** Middle Center.
- **Máscara de colisión:** imagen completa (mejor *full image* que *automática*).

Dibuja los fotogramas a mano: círculo pequeño → más grande → más redondeado →
cuadrado → un solo píxel. Puedes copiar y pegar fotogramas con `Ctrl + C` / `Ctrl + V`.

Crea el objeto **`oBulletExplode`**.

---

## 6. Fuera de la room: limpiar memoria

Añade a `oBulletExplode` dos eventos del grupo **Other**:

```gml
// Other → Outside Room
instance_destroy();
```

```gml
// Other → Animation End
instance_destroy();
```

- **Outside Room** → por si la explosión acaba fuera de los límites.
- **Animation End** → cuando la animación termina, se reproduce una vez y se destruye.

> Si no destruyes lo que sale de la room, **el juego sigue reteniéndolo en memoria**
> sin motivo.

Añade también **Outside Room → `instance_destroy()`** a `oBullet`, por si una bala
escapa por un hueco del muro.

---

## 7. Colisiones de la bala con `hspeed` / `vspeed`

**Step event de `oBullet`:** la misma lógica de siempre, pero usando `hspeed` y
`vspeed` en lugar de `hsp` y `vsp`:

```gml
// Colisión horizontal
if (place_meeting(x + hspeed, y, oBlock))
{
    var _pixel = sign(hspeed);

    while (!place_meeting(x + _pixel, y, oBlock))
    {
        x += _pixel;
    }

    // Crear la explosión justo donde hemos chocado…
    instance_create_layer(x, y, "Instances", oBulletExplode);

    // …y destruir la bala
    instance_destroy();
}

// Colisión vertical
if (place_meeting(x, y + vspeed, oBlock))
{
    var _pixel = sign(vspeed);

    while (!place_meeting(x, y + _pixel, oBlock))
    {
        y += _pixel;
    }

    instance_create_layer(x, y, "Instances", oBulletExplode);
    instance_destroy();
}
```

Al igual que `hsp`/`vsp`, **`hspeed` positivo es derecha** y **`vspeed` positivo es
abajo**, así que `sign()` sigue funcionando igual.

> **Segundo error real del tutorial:** tras crear `oBulletExplode`, el autor olvida
> **asignarle el sprite**. Al ejecutar no aparece nada. Lo detecta y lo arregla.

### Ajuste del origen

Después de probar, el autor cambia el origen de `sBullet` a **Middle Right**:

> Así la posición de la bala queda **en la punta**, en la dirección hacia la que mira.
> Solapa más con lo que golpea, y **queremos que solape** porque usaremos
> `place_meeting()` para causar daño.

---

## 8. Variables globales y puntuación

Una **variable global** puede ser leída y modificada **por cualquier parte del
juego**. Se declara con el prefijo `global.`:

```gml
global.points = 0;
```

Se escribe en rojo y después en fucsia en el editor.

### ¿Dónde declararlas?

En el **Creation Code de `rSplash`**, antes de saltar a la room real:

```gml
global.points = 0;   // Puntuación del jugador

room_goto(rTitle);
```

> **Nunca intentes leer una variable global que no se ha declarado antes.** La solución
> del autor es declarar **todas** las globales en `rSplash`, antes de ir al juego. En
> sus proyectos reales guarda un **script** con todas las variables globales al que
> llama desde el Creation Code de `rSplash`.

---

## 9. Dibujar texto con `string()`

Añade un evento **Draw** a `oPlayer`:

```gml
draw_self();   // ¡Necesario! Si no, deja de verse el sprite

draw_set_font(fDefault);
draw_set_valign(fa_top);      // Alineación vertical ARRIBA…
draw_set_halign(fa_center);   // …así el texto cuelga por DEBAJO
draw_set_color(c_white);

// La puntuación 25 píxeles por debajo del jugador
draw_text(x, y + 25, string(global.points));
```

Dos claves:

- **`draw_set_valign(fa_top)`** garantiza que el texto se dibuje **debajo** de la
  posición indicada, que es justo lo que queremos.
- **`draw_text()` necesita una cadena, no un número.** `global.points` es un número,
  así que hay que convertirlo con **`string()`**: `string(15)` devuelve `"15"`.

---

## 10. Destruir bloques y sumar puntos

**Step event de `oBlock`:**

```gml
if (place_meeting(x, y, oBulletExplode))
{
    global.points++;      // Sumar un punto
    instance_destroy();   // Destruir el bloque
}
```

Gracias a que la explosión es **más grande que la bala y se solapa con el bloque**,
esta simple comprobación funciona.

---

## 11. Práctica avanzada: pistola giratoria y `draw_sprite_ext()`

Crea **`sGun`** de **20 × 7**, FPS 0, origen **Middle Left**.

> El origen **Middle Left** es el **anclaje**: la pistola se sujeta al jugador por su
> extremo izquierdo y **rota alrededor de ese punto**.

**No hace falta crear un objeto**: el arma se dibujará desde el Draw de `oPlayer`.

**En el Draw de `oPlayer`:**

```gml
// --- Cañón de la pistola ---
var _dir = point_direction(x, y, mouse_x, mouse_y);

draw_sprite_ext(sGun, 0, x, y, 1, 1, _dir, c_white, 1);
```

### `draw_sprite_ext()`

```gml
draw_sprite_ext(sprite, subimg, x, y, xscale, yscale, rot, colour, alpha);
```

| Argumento | Valor usado | Significado |
|---|---|---|
| `sprite` | `sGun` | Sprite a dibujar |
| `subimg` | `0` | Fotograma (**se cuenta desde 0**) |
| `x`, `y` | `x`, `y` | Posición (el anclaje es Middle Left) |
| `xscale`, `yscale` | `1`, `1` | Sin estirar |
| `rot` | `_dir` | Rotación en grados |
| `colour` | `c_white` | **No cambia el color** (blanco es el neutro) |
| `alpha` | `1` | Completamente visible |

---

## 12. Práctica avanzada: disparar desde la boca del cañón

Ahora la bala nace en el centro del jugador. Para que salga **del final del cañón**,
sea cual sea la rotación:

```gml
var _dir = point_direction(x, y, mouse_x, mouse_y);

// Punto situado a lo largo del cañón, en la dirección _dir
var _x = x + lengthdir_x(sprite_get_width(sGun), _dir);
var _y = y + lengthdir_y(sprite_get_width(sGun), _dir);

var _bullet = instance_create_layer(_x, _y, "Instances", oBullet);

with (_bullet)
{
    direction = _dir;
    image_angle = _dir;
}
```

### `lengthdir_x()` y `lengthdir_y()`

> Dados una **longitud** y un **ángulo**, devuelven el **componente X** y el
> **componente Y** de ese desplazamiento.

Es trigonometría sin dolor. Y se usa **`sprite_get_width(sGun)`** en lugar de un
número fijo: **si cambias el tamaño del arma, las cuentas siguen saliendo**.

> «Cualquiera que aprenda GameMaker debería conocer `lengthdir_x` e `lengthdir_y`.
> Acabas usándolos mucho más de lo que imaginas.»

---

## 13. Práctica avanzada: rotar al jugador con `angle_difference()`

**En el Create de `oPlayer`:**

```gml
angle = 0;              // Rotación actual
angle_change_rate = 0.1;// Velocidad de giro
```

### El truco de la máscara

En el **Draw**, sustituye `draw_self()` por dibujar el sprite a mano:

```gml
draw_sprite_ext(sPlayer, 0, x, y, 1, 1, angle, c_white, 1);
```

> **Por qué:** así el sprite asignado al objeto **solo actúa como máscara de
> colisión**, y esa máscara **nunca rota**. Si rotaras la máscara, una esquina podría
> engancharse con un bloque. Dibujando a mano en el Draw, **parece** que rota pero las
> colisiones siguen siendo un cuadrado simple y predecible.

**Nueva región ANGLE en el Step:**

```gml
#region ÁNGULO
// -10 = izquierda, 10 = derecha, 0 = ambas o ninguna
var _intent_h = (_key_right * 10) - (_key_left  * 10);
var _intent_v = (_key_down  * 10) - (_key_up    * 10);

if (_intent_h != 0 || _intent_v != 0)
{
    // Dirección hacia la que el jugador QUIERE ir
    var _dir = point_direction(x, y, x + _intent_h, y + _intent_v);

    // Diferencia entre esa dirección y nuestro ángulo actual
    var _diff = angle_difference(_dir, angle);

    // Girar gradualmente: siempre un porcentaje de la diferencia
    angle += _diff * angle_change_rate;
}
#endregion
```

Conceptos nuevos:

| Operador / Función | Significado |
|---|---|
| `!=` | **Distinto de** |
| `\|\|` | **O** (basta con que una de las dos se cumpla) |
| `angle_difference(origen, destino)` | Devuelve la diferencia **con signo**: positivo si hay que girar a un lado, negativo al otro |

> El número 10 es arbitrario: sirve 1, 100 o 200. Solo crea un punto alejado desde el
> que trazar la línea y obtener el ángulo.

### Por qué multiplicar por `angle_change_rate`

- `angle += _diff` → **salta** de golpe a la dirección deseada.
- `angle += _diff * angle_change_rate` → se acerca **un 10 % cada fotograma**: giro
  suave y gradual.

Para verlo, añade una **flecha** al sprite `sPlayer` que indique hacia dónde mira.

---

## Puntos clave

1. **Los ángulos en GameMaker:** 0 = derecha, 90 = arriba, 180 = izquierda, 270 =
   abajo. **Diseña mirando a la derecha** todo lo que rote.
2. **`speed` + `direction`** hacen que GameMaker calcule `hspeed` y `vspeed` por ti.
3. **`mouse_check_button(mb_any)`** para el ratón; `mb_any` **no** funciona con
   `keyboard_check()`.
4. **`point_direction(x1,y1,x2,y2)`** da el ángulo entre dos puntos.
5. **`image_angle = direction`** hace que el sprite mire hacia donde va.
6. **Un temporizador `attack_cooldown`** controla la cadencia; resetea a 0 al soltar
   para que el siguiente clic sea inmediato.
7. **La explosión debe ser más grande que la bala** para solaparse con el objetivo y
   poder causar daño.
8. **`instance_destroy()` en Outside Room y Animation End** evita fugas de memoria.
9. **`global.points`** es accesible desde todo el juego; **declárala en `rSplash`**
   antes de cualquier uso.
10. **`draw_text()` necesita cadenas**: convierte números con `string()`.
11. **`draw_sprite_ext(sprite, subimg, x, y, xscale, yscale, rot, colour, alpha)`** es
    la función de dibujado más potente; `c_white` no altera el color y `alpha = 1` es
    opaco.
12. **`lengthdir_x(longitud, ángulo)`** da el desplazamiento horizontal;
    **`sprite_get_width()`** mantiene las cuentas correctas si cambias el arte.
13. **Dibujar el sprite a mano permite que la máscara de colisión no rote.**
14. **`angle_difference()` + multiplicar por una tasa** da giros suaves.
15. **Depura al momento**: el autor insiste en que un bug se arregla **antes** de
    seguir con otra cosa, aunque haya que volver a una versión anterior.

---

## Ejercicio propuesto

> **Objetivo:** montar un sistema de disparo completo con cadencia, explosiones y
> puntuación global.

**Parte A — Disparo básico**

1. Crea `sBullet` (5 × 5, origen **Middle Right**, máscara *full image*) y `oBullet`
   con `speed = 9` en su Create.
2. Añade a `oPlayer`: `attack_cooldown_max = 6` y `attack_cooldown = 0`.
3. Añade `_key_attack = mouse_check_button(mb_any)` a las entradas.
4. Crea la región `DISPARO` con el temporizador, `instance_create_layer()`,
   `point_direction()` e `image_angle`.
5. **Comprueba el error a propósito:** cambia `mouse_check_button` por
   `keyboard_check` y observa que no dispara. Vuelve a dejarlo correcto.

**Parte B — Explosiones**

6. Crea `sBulletExplode` (7 × 7, FPS 30, origen Middle Center) con al menos 5
   fotogramas. **Asígnaselo a `oBulletExplode`**.
7. Añade a `oBulletExplode` los eventos **Outside Room** y **Animation End**, ambos
   con `instance_destroy()`.
8. Añade **Outside Room** a `oBullet` también.
9. Implementa las colisiones de la bala con `hspeed` / `vspeed`, creando la explosión
   antes de destruirse.

**Parte C — Puntuación**

10. Declara `global.points = 0;` en el Creation Code de `rSplash`, **antes** del
    `room_goto()`.
11. Añade el Draw a `oPlayer` con `draw_self()`, fuente, `valign(fa_top)`,
    `halign(fa_center)` y `draw_text(x, y + 25, string(global.points))`.
12. Haz que `oBlock` sume un punto y se destruya al solaparse con `oBulletExplode`.
13. Comprueba que al destruir bloques la puntuación sube.

**Parte D — Avanzado**

14. Crea `sGun` (20 × 7, origen **Middle Left**) y dibújala con `draw_sprite_ext()`
    siguiendo el ratón.
15. Cambia el punto de aparición de la bala con `lengthdir_x()` /
    `lengthdir_y()` y `sprite_get_width(sGun)`.
16. Añade `angle` y `angle_change_rate`, **quita `draw_self()`** y dibuja `sPlayer` con
    `draw_sprite_ext()`.
17. Implementa la región `ÁNGULO` con las intenciones, `||`, `angle_difference()` y el
    giro gradual.
18. Dibuja una flecha en `sPlayer` para ver hacia dónde mira.

**Reto extra:** el autor aumenta el tamaño de `sGun` a 30 × 7. Comprueba que la bala
sigue saliendo por la boca del cañón **sin tocar una sola línea de código**, gracias a
`sprite_get_width()`. Explica por qué.
