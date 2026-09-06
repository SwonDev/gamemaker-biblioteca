# 07 · Cámaras

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 7 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=VPPZGDzWqqY> |
| **Duración** | 33 min 37 s |
| **Publicado** | 27 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `view_camera[]`, `camera_get_view_width/height`, `camera_set_view_pos`, `random_range`, `lerp`, `abs`, `lengthdir_*`, scripts |

Las cámaras permiten que el personaje **explore un área mucho más grande que la
ventana**, manteniendo la resolución intacta. El capítulo enseña **dos** sistemas: uno
automático de tres clics, y otro programado a mano que permite sacudidas de pantalla y
adelantamiento (*camera lead*).

## Índice de contenido

1. Sistema simple: viewports y cámaras desde el editor
2. Ampliar la room
3. Depuración en directo y la regla de oro
4. Preparar la cámara manual: quitar el seguimiento
5. El objeto `oCamera`
6. El eje de la cámara está en la esquina superior izquierda
7. Seguimiento suave y `clamp()`
8. `camera_set_view_pos()`
9. Sacudida de pantalla (screen shake)
10. `random_range()` frente a `irandom_range()`
11. Scripts: el nuevo tipo de recurso
12. La función `screen_shake()`
13. Práctica avanzada: adelantamiento de cámara (*camera lead*) con `lerp()`

---

## 1. Sistema simple: viewports y cámaras desde el editor

> Si has perdido el panel de propiedades de la room, no te preocupes: **haz clic en el
> nombre de la room** en la pestaña superior y volverá a aparecer el inspector.

En las propiedades de la room:

1. Abre el desplegable **Viewports and Cameras**.
2. Marca **Enable Viewports**.
3. Abre **Viewport 0** y marca **Visible**.

Aparecerán unas líneas blancas que delimitan la cámara. Ahora:

4. Iguala **Width** y **Height** de la cámara y del viewport a tu resolución:
   **480 × 270**.
5. En **Object Following**, elige `oPlayer`.

### Los bordes horizontal y vertical

Por defecto valen **32 y 32**. Eso significa que el objeto puede acercarse hasta 32
píxeles del borde **antes de empujar** la cámara.

Si quieres que el seguimiento sea **perfecto y centrado**, pon cada borde en la
**mitad** de su dimensión:

```
Horizontal Border = 480 / 2 = 240
Vertical Border   = 270 / 2 = 135
```

Con esto la cámara sigue al objeto de forma **exacta, píxel a píxel**.

---

## 2. Ampliar la room

Si ejecutaras ahora no notarías ningún cambio: hace falta que la room sea **más
grande** que la ventana.

El autor la pone a **1020 × 720** (elegido a propósito para que encaje bien con el
tamaño de sus colisiones) y pinta con `Alt` un borde nuevo de `oBlock`, más algunos
bloques sueltos para tener un nivel que explorar.

Al ejecutar: la cámara sigue al jugador por una room enorme **sin cambiar la
resolución del juego**.

---

## 3. Depuración en directo y la regla de oro

Al probar, el autor ve que **las balas ya no rotan**: se le ha olvidado poner
`image_angle = _dir` en la versión nueva del código de disparo.

> «Me gusta que veáis cómo depuro cosas. Mucha gente encuentra un error y dice "ya lo
> arreglaré luego". **No.** Encuentras un error y **no trabajas en nada más hasta que
> esté arreglado**. Y si tienes que volver a una versión anterior de tu juego, vuelves.»

---

## 4. Preparar la cámara manual: quitar el seguimiento

Para programar la cámara a mano:

1. Mantén **todo** lo que has configurado en la room (viewport habilitado, tamaños…).
2. Cambia **Object Following** a **`None`** *(no object)*.

> **Ambos pasos son obligatorios.** Hay que configurar el viewport **y** además
> programar la cámara.

---

## 5. El objeto `oCamera`

Crea el objeto **`oCamera`** y añádelo a la room desde su **Creation Code**:

```gml
instance_create_layer(0, 0, "Instances", oCamera);
```

La posición da igual. El autor recomienda **añadirlo siempre a la room antes de
empezar a programarlo**, para poder probar sobre la marcha.

**Create event:**

```gml
cam = view_camera[0];            // Nuestro viewport 0
cam_follow_speed = 8;            // Seguimiento: un número MÁS BAJO es MÁS RÁPIDO
follow = oPlayer;                // Objeto al que seguir (se puede cambiar, p. ej. para cutscenes)

width_half  = camera_get_view_width(cam)  * 0.5;
height_half = camera_get_view_height(cam) * 0.5;

x_to = x;   // Donde la cámara QUIERE ir (no necesariamente donde está)
y_to = y;
```

| Variable | Significado |
|---|---|
| `view_camera[0]` | La cámara del viewport 0 |
| `cam_follow_speed` | Divisor del seguimiento; **menor = más rápido** |
| `follow` | Objeto seguido; cambiable en cualquier momento |
| `width_half`, `height_half` | Mitad del tamaño de la cámara |
| `x_to`, `y_to` | Posición **objetivo** |

---

## 6. El eje de la cámara está en la esquina superior izquierda

> Concepto clave: si le dices a la cámara que esté en `(40, 40)`, la **esquina
> superior izquierda** de su rectángulo estará en ese punto. **No** es su centro.

Por eso necesitamos `width_half` y `height_half`: sin esa corrección, el objeto
seguido quedaría siempre **en la esquina superior izquierda** de la pantalla.

---

## 7. Seguimiento suave y `clamp()`

**Step event de `oCamera`:**

```gml
// --- Actualizar destino ---
if (instance_exists(follow))
{
    x_to = follow.x;
    y_to = follow.y;
}

// --- Moverse hacia el destino ---
// Se mueve más despacio cuanto más cerca está del objeto seguido
x += (x_to - x) / cam_follow_speed;
y += (y_to - y) / cam_follow_speed;

// --- No salirse de los límites de la room ---
x = clamp(x, width_half, room_width  - width_half);
y = clamp(y, height_half, room_height - height_half);
```

- `follow.x` / `follow.y`: acceder a una variable de una instancia mediante el punto.
- `x += (x_to - x) / cam_follow_speed` produce un **seguimiento suave y elástico**:
  cuanto más cerca está, menos se mueve por fotograma.
- Los `clamp()` impiden que la cámara muestre el exterior de la room.

---

## 8. `camera_set_view_pos()`

Lo último del Step: aplicar la posición al viewport real.

```gml
// --- Actualizar la vista de la cámara ---
camera_set_view_pos(cam, x - width_half, y - height_half);
```

Se resta la mitad del tamaño para que **`oCamera` quede siempre en el centro** de lo
que se ve, compensando que el eje de la cámara está en la esquina superior izquierda.

El resultado es una cámara **más fluida**: va por detrás del jugador y se detiene
poco después de que él se detenga.

---

## 9. Sacudida de pantalla (screen shake)

**Añade al Create:**

```gml
// --- Cosas de la sacudida ---
shake_length = 0;      // Duración en fotogramas
shake_magnitude = 0;   // Tamaño de la sacudida en píxeles
shake_remain = 0;      // Temporizador de cuenta atrás
buff = 15;             // Distancia en píxeles desde el borde de la room
```

> **¿Para qué sirve `buff`?** Si la cámara va a temblar, deja un margen de 15 píxeles
> para que **al sacudirse nunca salga de la room**. Como los bloques del autor ocupan
> 30 píxeles, 15 es justo la mitad.

Actualiza los `clamp()` para incluir el margen:

```gml
x = clamp(x, width_half  + buff, room_width  - width_half  - buff);
y = clamp(y, height_half + buff, room_height - height_half - buff);
```

**En el Step, justo antes de `camera_set_view_pos()`:**

```gml
// --- Sacudida de pantalla ---
x += random_range(-shake_remain, shake_remain);
y += random_range(-shake_remain, shake_remain);

// La intensidad de la sacudida disminuye con el tiempo
shake_remain -= (1 / shake_length) * shake_magnitude;
```

La última línea hace que la sacudida **se amortigüe** progresivamente hasta quedarse
en cero.

---

## 10. `random_range()` frente a `irandom_range()`

| Función | Devuelve |
|---|---|
| `random_range(a, b)` | Un número **real** con decimales (1,5 / 1,8 / 1,38…) |
| `irandom_range(a, b)` | Un número **entero** (5, 15, 58, 76…) |

Para la sacudida se usa **`random_range()`**: los decimales dan **sutileza** al
temblor, algo especialmente importante en un juego de pixel art tan pequeño.

---

## 11. Scripts: el nuevo tipo de recurso

Un **script** es una colección de código a la que puedes **pasar información** para
alterar su comportamiento.

Crea el grupo **`Scripts`**. Hay dos sabores:

### Funciones a nivel de objeto

```gml
function my_cool_script(_thing1, _thing2)
{
    // …código…
}
```

Es **una variable que guarda código**. Se puede llamar desde el Step u otros eventos:

```gml
my_cool_script(50, 75);
```

Y dentro, `_thing1` y `_thing2` funcionan como variables locales.

### Funciones a nivel de recurso (asset)

Son las que puede llamar **cualquier objeto del juego**.

> **Regla importante:** en un script de recurso, **el nombre del script debe coincidir
> con el nombre de la función**.

---

## 12. La función `screen_shake()`

**Script `screen_shake`:**

```gml
function screen_shake(_magnitude, _frames)
{
    if (_magnitude > 0)
    {
        shake_remain = _magnitude;
        shake_length = _frames;
    }
}
```

Ahora puedes llamarla desde **cualquier sitio**. Por ejemplo, al disparar en `oPlayer`:

```gml
screen_shake(2, 10);   // 2 píxeles de magnitud durante 10 fotogramas
```

El editor te mostrará los argumentos mientras escribes. El autor usa una magnitud tan
pequeña porque **se dispara muy a menudo**; para comprobar el efecto, prueba
`screen_shake(10, 120)`.

> Es un detalle de *juice* que da mucha vida al juego.

---

## 13. Práctica avanzada: adelantamiento de cámara con `lerp()`

> Ahora la cámara va **por detrás** del movimiento. Pero si vas hacia arriba, quieres
> **ver más arriba que abajo**: lo que queda atrás no importa. Eso es el **camera
> lead**.

**Añade al Create de `oPlayer`:**

```gml
cam_lead = 100;        // Píxeles de adelantamiento en la dirección del movimiento
cam_lead_rate = 0.1;   // Velocidad de cambio hacia el nuevo objetivo

cam_x = x;             // Donde queremos que esté la cámara (adelantada)
cam_y = y;
```

**Nueva región CAMERA LEAD en el Step de `oPlayer`:**

```gml
#region ADELANTAMIENTO DE CÁMARA
// Dirección en la que nos movemos
var _cam_dir = point_direction(x, y, x + hsp, y + vsp);

// Objetivo: adelantado según la velocidad relativa
var _cam_x_target = x + lengthdir_x(cam_lead * abs(hsp / move_speed), _cam_dir);
var _cam_y_target = y + lengthdir_y(cam_lead * abs(vsp / move_speed), _cam_dir);

// Acercarse al objetivo un 10 % cada fotograma
cam_x = lerp(cam_x, _cam_x_target, cam_lead_rate);
cam_y = lerp(cam_y, _cam_y_target, cam_lead_rate);
#endregion
```

### `abs()`

**Valor absoluto**: convierte un negativo en positivo.

Se necesita porque `hsp` puede ser negativo, y `lengthdir_x` **ya recibe la dirección**
en `_cam_dir`. Si la longitud fuera también negativa, el resultado apuntaría **al lado
contrario**. `abs()` garantiza que solo medimos *cuánto*, no *hacia dónde*.

### La relación con la velocidad

`abs(hsp / move_speed)` es la **velocidad actual como porcentaje de la máxima**:

| Velocidad | Fracción | Adelantamiento (con `cam_lead = 100`) |
|---|---|---|
| Máxima | 1,0 | **100 píxeles** |
| Mitad | 0,5 | **50 píxeles** |
| Parado | 0 | **0 píxeles** |

### `lerp()`

```gml
lerp(a, b, amount)
```

Devuelve el valor que está **a un porcentaje dado entre `a` y `b`**.

Con `cam_lead_rate = 0.1`, cada fotograma nos acercamos **un 10 %** de la distancia
restante: un movimiento suave que se va frenando al aproximarse.

### Conectar con la cámara

En el Step de `oCamera`, cambia el destino para que lea las nuevas variables:

```gml
x_to = follow.cam_x;
y_to = follow.cam_y;
```

> **⚠️ Cuidado:** cualquier objeto al que la cámara pueda seguir **debe tener
> `cam_x` y `cam_y` declarados**, o el juego se cerrará al intentar leerlos.

---

## Puntos clave

1. **Habilita Viewports + Viewport 0 Visible** y pon el tamaño a tu resolución.
2. **Bordes = la mitad de la resolución** (240 y 135) para un seguimiento centrado
   exacto.
3. **Amplía la room** para que la cámara tenga sentido.
4. **Depura al instante.** No acumules bugs; vuelve atrás si hace falta.
5. **La posición de la cámara es su esquina superior izquierda**, no su centro: de ahí
   `width_half` y `height_half`.
6. **`x += (x_to - x) / cam_follow_speed`** da un seguimiento elástico; **menor
   divisor = más rápido**.
7. **`clamp()`** evita salirse de la room. Con sacudida, añade un **`buff`** de 15
   píxeles.
8. **`camera_set_view_pos(cam, x - width_half, y - height_half)`** centra la vista.
9. **`random_range()`** da decimales (ideal para sacudidas sutiles);
   **`irandom_range()`** da enteros.
10. **Un script de recurso debe llamarse igual que su función** y puede invocarse
    desde cualquier parte del juego.
11. **`abs()`** evita que una longitud negativa invierta la dirección.
12. **`lerp(a, b, 0.1)`** es la forma idiomática de acercarse suavemente a un objetivo.

---

## Ejercicio propuesto

> **Objetivo:** pasar del seguimiento automático a una cámara programada con sacudida y
> adelantamiento.

**Parte A — Cámara automática**

1. En `rGame`, habilita **Viewports** y marca **Viewport 0 → Visible**.
2. Pon cámara y viewport a **480 × 270**.
3. Asigna **Object Following → `oPlayer`** y los bordes a **240** y **135**.
4. Amplía la room a **1020 × 720** y pinta un borde nuevo de bloques. Comprueba el
    seguimiento.
5. Deja los bordes en 32 y observa la diferencia: el jugador «empuja» la cámara al
    llegar al borde. Vuelve a ponerlos a la mitad.

**Parte B — Cámara manual**

6. Pon **Object Following → None**.
7. Crea `oCamera` y añádelo con `instance_create_layer(0, 0, "Instances", oCamera);` en
    el Creation Code de `rGame`.
8. Implementa el Create con `cam`, `cam_follow_speed`, `follow`, `width_half`,
    `height_half`, `x_to` e `y_to`.
9. Implementa el Step con `instance_exists(follow)`, el movimiento dividido, los
    `clamp()` y `camera_set_view_pos()`.
10. Comprueba que la cámara es ahora más fluida y «flota» tras el jugador.

**Parte C — Sacudida**

11. Añade `shake_length`, `shake_magnitude`, `shake_remain` y `buff = 15`.
12. Actualiza los `clamp()` con `+ buff` y `- buff`.
13. Añade el bloque de sacudida con `random_range()` y la amortiguación.
14. Crea el grupo `Scripts` y la función `screen_shake(_magnitude, _frames)`.
    **Asegúrate de que el nombre del script y el de la función coinciden.**
15. Llama a `screen_shake(2, 10)` al disparar. Después prueba `screen_shake(10, 120)`
    para ver el efecto exagerado, y vuelve a dejar 2 y 10.

**Parte D — Adelantamiento (avanzado)**

16. Añade a `oPlayer`: `cam_lead = 100`, `cam_lead_rate = 0.1`, `cam_x`, `cam_y`.
17. Implementa la región `ADELANTAMIENTO DE CÁMARA` con `point_direction()`,
    `lengthdir_x/y`, `abs()` y `lerp()`.
18. Cambia en `oCamera` `follow.x` / `follow.y` por `follow.cam_x` / `follow.cam_y`.
19. Comprueba que al moverte la cámara se adelanta en la dirección del movimiento.

**Reto extra:** el autor advierte de que todo objeto seguido debe tener `cam_x` y
`cam_y`. Crea un objeto temporal `oCaja`, asígnalo a `follow` mediante código y
comprueba el error. Después declara `cam_x` y `cam_y` en su Create y verifica que
funciona. Explica por qué GameMaker no avisa de este fallo en tiempo de edición.
