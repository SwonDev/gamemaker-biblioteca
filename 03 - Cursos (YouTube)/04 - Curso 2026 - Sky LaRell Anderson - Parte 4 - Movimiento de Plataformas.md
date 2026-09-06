# 04 · Movimiento de plataformas

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 4 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=MMfaB6VQl7Y> |
| **Duración** | 26 min 57 s |
| **Publicado** | 24 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `keyboard_check_pressed`, `&&`, `clamp`, `max`, `instance_exists` |

Con los fundamentos del capítulo 3 ya asentados, toca el género que más gente quiere
hacer: **plataformas de vista lateral**. Gravedad, salto, y las técnicas de «sensación»
(*game feel*) que separan un plataformas mediocre de uno que apetece jugar.

## Índice de contenido

1. Preparar el proyecto: duplicar la room
2. El sprite del saltador (`sJumper`)
3. Movimiento horizontal (idéntico al capítulo 3)
4. Nombres reservados: `gravity` y `hspeed`
5. Gravedad
6. Colisión vertical
7. El salto: `keyboard_check_pressed()`
8. El buffer de suelo: por qué la perfección es mala
9. Limitar la velocidad de caída con `clamp()`
10. Práctica avanzada: altura de salto variable
11. Práctica avanzada: doble salto

---

## 1. Preparar el proyecto: duplicar la room

En lugar de empezar de cero, **duplica la room del juego**:

1. Selecciona `rGame` y pulsa **`Ctrl + D`** (o clic derecho → **Duplicate**).
2. Renombra la copia (por ejemplo, `rPlatformer`).
3. En el **Creation Code** de `rSplash`, cambia `room_goto(rGame)` por
   `room_goto(rPlatformer)`.

> Aprende los atajos: aceleran muchísimo el flujo de trabajo.

---

## 2. El sprite del saltador (`sJumper`)

En vista lateral conviene una proporción «humana»: **20 × 40** (más alto que ancho).

| Ajuste | Valor | Motivo |
|---|---|---|
| Tamaño | 20 × 40 | Proporción vertical tipo personaje |
| FPS | 0 | Sin animación todavía |
| Origen | **Middle Center** | **Imprescindible** para poder voltear el sprite simétricamente al mirar a izquierda/derecha |

Rellénalo con un color sólido (el autor usa un rosa claro y le dibuja una X).

Crea el objeto **`oJumper`**, asígnale `sJumper` y colócalo **cerca de la parte
superior** de la room, porque lo primero que probaremos es la gravedad.

> Ahora que hay **dos capas de instancias**, asegúrate siempre de que está
> seleccionada la correcta antes de añadir cosas.

---

## 3. Movimiento horizontal

**Create event de `oJumper`:**

```gml
hsp = 0;          // Velocidad horizontal actual
vsp = 0;          // Velocidad vertical actual
move_speed = 2;   // Velocidad máxima de movimiento
```

**Step event — región de entradas y movimiento horizontal:**

```gml
#region ENTRADAS
var _key_left  = keyboard_check(vk_left);
var _key_right = keyboard_check(vk_right);
var _key_jump  = keyboard_check_pressed(vk_up);
#endregion

#region MOVIMIENTO HORIZONTAL
// Obtener la dirección: -1 izquierda, 1 derecha, 0 nada
var _hdir = _key_right - _key_left;
hsp = _hdir * move_speed;

// Colisión horizontal
if (place_meeting(x + hsp, y, oBlock))
{
    var _one_pixel = sign(hsp);
    while (!place_meeting(x + _one_pixel, y, oBlock))
    {
        x += _one_pixel;
    }
    hsp = 0;
}

// Aplicar el movimiento horizontal
x += hsp;
#endregion
```

Exactamente el mismo sistema del capítulo 3. El autor decide **no** aplicar aquí el
truco de los subpíxeles (`x_real`), para mantener el código más legible.

---

## 4. Nombres reservados: `gravity` y `hspeed`

> **Atención:** si escribes `gravity`, el texto **se pondrá verde**. Eso significa que
> ya es una propiedad integrada de GameMaker (en este caso, de la room) y **no puedes
> usarla como variable**.

Lo mismo pasa con `hspeed` o `gravity`: son términos que ya significan algo concreto.
Por eso se usa la abreviatura:

```gml
grav = 0.2;   // Gravedad: cuánto se acelera la caída por fotograma
```

---

## 5. Gravedad

```gml
// Añadir gravedad
vsp += grav;
```

Recuerda la regla de oro del eje Y en GameMaker:

> **`y` aumenta hacia ABAJO.** Por tanto, para que el objeto caiga hay que **sumar** a
> su velocidad vertical.

Con `grav = 0.2`, cada uno de los 60 fotogramas por segundo añade 0,2 a `vsp`: el
objeto acelera hacia abajo de forma continua.

---

## 6. Colisión vertical

La misma lógica de siempre, aplicada al eje Y:

```gml
// Colisión vertical
if (place_meeting(x, y + vsp, oBlock))
{
    var _one_pixel = sign(vsp);
    while (!place_meeting(x, y + _one_pixel, oBlock))
    {
        y += _one_pixel;
    }
    vsp = 0;
}

// Aplicar el movimiento vertical
y += vsp;
```

Con esto el personaje cae y se detiene al tocar los bloques.

---

## 7. El salto: `keyboard_check_pressed()`

### Dos funciones distintas

| Función | Qué comprueba |
|---|---|
| `keyboard_check(tecla)` | Si la tecla **está siendo mantenida** pulsada este frame |
| `keyboard_check_pressed(tecla)` | Si la tecla **acaba de pulsarse** este frame |

`keyboard_check_pressed` solo devuelve verdadero **en el primer fotograma** del
pulso; después, aunque sigas apretando, ya no registra. Es ideal para botones como
**saltar**.

**En el Create:**

```gml
jump_speed = -6;   // Debe ser NEGATIVO para moverse hacia arriba
```

**En el Step (después de la gravedad y antes de la colisión):**

```gml
// Salto
if (_key_jump && (vsp > 0))
{
    vsp = jump_speed;
}
```

### El operador `&&`

`&&` significa **Y**: el código solo se ejecuta si **ambas** condiciones son
verdaderas.

- `_key_jump` → se acaba de pulsar la tecla de salto.
- `vsp > 0` → la velocidad vertical es positiva, es decir, **estamos cayendo o
  quietos** (no ya subiendo).

---

## 8. El buffer de suelo: por qué la perfección es mala

Con el código anterior puedes pulsar salto repetidamente en el aire y «volar» al
estilo Flappy Bird. Puede ser una mecánica divertida, pero lo normal es exigir
**estar en el suelo**.

El problema de exigir contacto exacto:

> **La perfección es lo opuesto al buen diseño de juego.** Si el jugador pulsa salto
> un fotograma antes de tocar el suelo, el juego «se come» la orden y da la sensación
> de que no responde.

La solución es un **margen de tolerancia**:

```gml
ground_buffer = 3;   // ¿A cuántos píxeles del suelo cuenta como estar en el suelo?
```

Y en el Step, justo después de la gravedad:

```gml
// Comprobar si estamos lo bastante cerca del suelo
var _on_ground = place_meeting(x, y + ground_buffer, oBlock);
```

Ahora la condición de salto tiene tres partes:

```gml
if (_key_jump && (vsp > 0) && _on_ground)
{
    vsp = jump_speed;
}
```

Puedes escribir `_on_ground` directamente (GameMaker lo lee como verdadero), o
explícitamente `_on_ground == true`. Para comprobar lo contrario, antepón un `!`:
`!_on_ground`.

Resultado: solo saltas desde el suelo, pero con **3 píxeles de margen**, lo que hace
el control mucho más natural.

---

## 9. Limitar la velocidad de caída con `clamp()`

Sin límite, la gravedad acelera indefinidamente y las caídas largas se vuelven
incontrolables.

```gml
grav_max = 6;   // Máximo de píxeles por fotograma al caer
```

Y en el Step, **justo antes del código de colisión vertical**:

```gml
// Limitar la velocidad de caída
vsp = clamp(vsp, jump_speed, grav_max);
```

`clamp(valor, mínimo, máximo)` comprueba el valor y lo **recorta** al rango: si se
pasa del máximo lo deja en el máximo, si se queda por debajo del mínimo lo deja en el
mínimo. Al asignar el resultado a `vsp`, la velocidad de caída nunca superará 6
píxeles por fotograma.

---

## 10. Práctica avanzada: altura de salto variable

> El autor avisa de nuevo: si lo anterior ya te abruma, limítate a verlo. Podrás
> continuar con el siguiente capítulo sin problemas.

Ahora mismo, un toque breve produce el salto completo. Lo ideal: **salto corto si
tocas, salto largo si mantienes**.

**En el Create:**

```gml
jump_speed_min = -2;   // Altura mínima de salto al pulsar brevemente
```

**En las entradas, añade una variable más** (esta vez con `keyboard_check`, para
saber si se está **manteniendo**):

```gml
var _key_jump_held = keyboard_check(vk_up);
```

**En el Step, justo antes del `clamp`:**

```gml
// Altura de salto variable
if (vsp < 0 && !_key_jump_held)
{
    // Si estamos subiendo y NO se mantiene el botón de salto
    vsp = max(vsp, jump_speed_min);
}
```

Cómo funciona:

- `vsp < 0` → estamos **subiendo** (recordamos: hacia arriba es negativo).
- `!_key_jump_held` → hemos **soltado** el botón.
- `max(vsp, jump_speed_min)` → se queda con el **mayor** de los dos. Al soltar,
  recorta la velocidad ascendente a `-2`, así que el salto se corta en seco.

Si mantienes el botón, `vsp` nunca se recorta y el salto llega a su altura completa.

---

## 11. Práctica avanzada: doble salto

**En el Create:**

```gml
jump_air_ready = true;     // Booleano: ¿está listo el salto aéreo?
jump_air_threshold = -1;   // Hay que ir más rápido que esto hacia abajo para saltar en el aire
jump_speed_air = -5;       // El salto aéreo es algo más bajo que el normal
```

- Un **booleano** es una variable que solo vale `true` o `false`. Aunque GameMaker no
  distingue realmente entre `true/false` y `1/0`, declararlo así **nos recuerda** cómo
  se va a usar.
- `jump_air_threshold = -1` permite saltar en el aire si **subes muy despacio**, si
  estás **parado en el apex** o si estás **cayendo**.

**En el Step, se reestructura el bloque de salto:**

```gml
// Salto
if (_key_jump && (vsp > jump_air_threshold))
{
    if (_on_ground)
    {
        // Salto normal desde el suelo
        vsp = jump_speed;
        jump_air_ready = true;   // Al tocar el suelo se recupera el doble salto
    }
    else if (jump_air_ready)
    {
        // Doble salto en el aire
        vsp = jump_speed_air;
        jump_air_ready = false;  // Se consume: ya no hay más saltos
    }
}
```

Puntos importantes:

- Se sustituye `(vsp > 0)` por `(vsp > jump_air_threshold)` para **permitir también el
  salto durante la caída**.
- `else if (jump_air_ready)` garantiza **un solo** salto aéreo: al usarlo se pone a
  `false` y no vuelve a estar disponible.
- `jump_air_ready = true` dentro de la rama de suelo es lo que **restaura** el doble
  salto al aterrizar. El autor lo confirma explícitamente: «se reiniciará cuando
  estemos en el suelo».

> El autor señala que, con este sistema, **si caes de una plataforma todavía puedes
> hacer el salto aéreo**. Es una mecánica que le encanta y que da mucha seguridad al
> jugador.

---

## Puntos clave

1. **Duplica recursos con `Ctrl + D`** en vez de recrearlos.
2. **Origen `Middle Center`** en sprites de personaje: es lo que permite voltearlos
   simétricamente al mirar a un lado u otro.
3. **`gravity` y `hspeed` están reservados.** Usa `grav` y `hsp`.
4. **La gravedad se suma** (`vsp += grav`) porque `y` crece hacia abajo.
5. **`jump_speed` debe ser negativo** para subir.
6. **`keyboard_check_pressed()`** detecta solo el primer fotograma del pulso: es la
   función correcta para saltar.
7. **`&&`** exige que se cumplan **todas** las condiciones.
8. **Un buffer de suelo de 3 píxeles** evita que el juego «se coma» la orden de
   salto. La perfección es mala diseño.
9. **`clamp(vsp, jump_speed, grav_max)`** evita la aceleración infinita al caer.
10. **Altura de salto variable:** si subes y sueltas el botón, recorta con
    `max(vsp, jump_speed_min)`.
11. **Doble salto:** un booleano `jump_air_ready` que se consume al usarse y se
    restaura al tocar el suelo.

---

## Ejercicio propuesto

> **Objetivo:** montar un plataformas jugable y después tunear su *game feel*.

**Parte A — El plataformas básico**

1. Duplica `rGame` como `rPlatformer` y apunta `rSplash` a la nueva room.
2. Crea `sJumper` (20 × 40, FPS 0, origen **Middle Center**) y `oJumper`.
3. Coloca a `oJumper` arriba de la room, sobre la capa `Instances` correcta.
4. Implementa el Create con `hsp`, `vsp` y `move_speed = 2`.
5. Implementa el movimiento horizontal con colisión (idéntico al capítulo 3).
6. Añade `grav = 0.2` y `vsp += grav`, y la colisión vertical. Comprueba que cae y
   aterriza.
7. Añade `jump_speed = -6`, `_key_jump` con `keyboard_check_pressed(vk_up)` y la
   condición `if (_key_jump && (vsp > 0))`.
8. Añade `ground_buffer = 3` y `_on_ground`, y amplía la condición a
   `if (_key_jump && (vsp > 0) && _on_ground)`.
9. Añade `grav_max = 6` y `vsp = clamp(vsp, jump_speed, grav_max);`.

**Parte B — Afinar la sensación**

10. Prueba el juego y ajusta `move_speed`, `grav`, `jump_speed` y `grav_max` hasta que
    el salto se sienta bien. Anota los valores: ¿qué pasa si `grav` es grande y
    `jump_speed` muy negativo? (salto seco y pesado) ¿Y si es al revés? (salto
    flotante tipo *Moon*).
11. Comenta temporalmente la línea del `ground_buffer` (usa `place_meeting(x, y + 1,
    oBlock)`) y comprueba lo frustrante que resulta. Vuelve a ponerlo a 3.

**Parte C — Avanzado**

12. Implementa la **altura de salto variable** con `jump_speed_min` y `max()`.
13. Implementa el **doble salto** con `jump_air_ready`, `jump_air_threshold` y
    `jump_speed_air`.
14. Coloca una plataforma flotante en la capa `Colisiones` con `Alt` y comprueba que
    **puedes saltar en el aire si te caes de ella**.
15. Exporta tu YYZ.

**Reto extra:** ¿qué ocurre si pones `jump_speed_air` **más negativo** que
`jump_speed`? Inténtalo y explica por qué el diseño estándar prefiere que el doble
salto sea algo más débil.
