# 09 · Plataformas para principiantes — apuntes de la serie de Alas de reptil (2025)

> **Fuente:** canal [Alas de reptil](https://www.youtube.com/@alasdereptil) · 2025.
> **Es el material en español más reciente que se ha encontrado** (el último vídeo es de
> **octubre de 2025**), y el único que enseña desde cero para GameMaker actual.
>
> | # | Vídeo | Fecha | Duración | Qué enseña |
> |---|---|---|---:|---|
> | 1 | [Mover el personaje](https://youtu.be/9Uka6j38UfY) | 15-02-2025 | 10:27 | Sprites, objeto, evento Step, movimiento en X |
> | 2 | [Movimiento (versión corta)](https://youtu.be/SQ2FpeqyVbs) | 27-02-2025 | 10:05 | El mismo tema con código más compacto |
> | 3 | [Hacer que salte](https://youtu.be/-qns_bZZN3s) | 26-03-2025 | 10:55 | Suelo, `gravity`, `vspeed`, salto |
> | 4 | [Colisiones con muros y techos](https://youtu.be/YuzPNHNP1N8) | 02-10-2025 | 7:17 | `place_free`, `collision_line`, máscara propia |
>
> **Esto no es una transcripción**: son apuntes propios con el código reescrito y verificado
> para LTS 2026. Para seguir las clases en vídeo, ve a los enlaces.

---

## Para quién es

Para **empezar de cero**. La serie no da nada por sabido: enseña a crear un sprite, colocar el
origen, crear el objeto y meterlo en una room antes de escribir una línea de código. Si vienes
de otro motor y solo quieres el patrón bueno, salta a
[08 · Megaman X](./08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md).

> ⚠️ **Aviso importante que la serie no da:** este enfoque usa las **variables de movimiento
> integradas** de GameMaker (`gravity`, `vspeed`, `hspeed`) y `place_free`. Es lo más fácil de
> entender y funciona para un primer juego, pero **se rompe a velocidades altas** y con
> geometría compleja. Está explicado en [Los límites de este enfoque](#los-límites-de-este-enfoque).

---

## 1 · Antes del código: sprites, origen y room

Tres cosas que la serie insiste en dejar bien y que causan la mitad de los problemas de los
principiantes:

**Dibuja el personaje mirando a la derecha.** Todo el código de giro asume esa orientación:
`image_xscale = 1` es «como lo dibujaste» y `-1` es «espejado».

**Baja los FPS del sprite.** Los sprites nuevos vienen a 30 fps y una animación de 4 fotogramas
se ve frenética. Alrededor de **10 fps** es un punto de partida razonable para pixel art.

**Pon el origen abajo y en el centro.** Es el detalle más importante del primer vídeo:

- **Centrado en horizontal** → al voltear el sprite con `image_xscale = -1`, gira sobre sí
  mismo en vez de dar un salto lateral.
- **Abajo (`y` = alto del sprite)** → `y` pasa a ser «los pies del personaje». Con eso, apoyar
  al personaje sobre un bloque es una resta directa, sin compensaciones.

> 🔺 **2026:** el origen se ajusta en el editor de sprites, y hay preajustes en el desplegable
> **Origin** (`Bottom Centre` es justo el que quieres aquí). **Todos los sprites del personaje
> deben compartir el mismo origen** o el personaje pegará saltos al cambiar de animación.

**Todos los sprites del personaje, el mismo origen.** Si `spr_quieto` tiene el origen arriba y
`spr_andando` abajo, el personaje da un brinco cada vez que empieza a andar.

---

## 2 · Movimiento horizontal

### La versión larga (vídeo 1)

Un `if` por tecla. Se entiende de un vistazo:

```gml
/// obj_player · Step
var _vel = 5;
dir_h = 0;                                   // se reinicia cada paso

if (keyboard_check(vk_right)) {
    x += _vel;
    dir_h = 1;
    image_xscale = 1;
}
if (keyboard_check(vk_left)) {
    x -= _vel;
    dir_h = -1;
    image_xscale = -1;
}

// cambio de sprite según si nos movemos o no
if (dir_h == 0) sprite_index = spr_quieto;
else            sprite_index = spr_andando;
```

> 💡 **Por qué `dir_h = 0` va arriba del todo:** se pone a cero al principio de **cada paso**;
> si estás pulsando una tecla vuelve a 1 o -1, y si la sueltas se queda en 0. Es lo que permite
> saber «ahora mismo no me estoy moviendo» sin comprobar las teclas otra vez.

### La versión corta (vídeo 2)

En el segundo vídeo el autor vuelve sobre el tema con un código más compacto — y es el que
merece la pena aprender:

```gml
/// obj_player · Step
var _vel = 5;
dir_h = keyboard_check(vk_right) - keyboard_check(vk_left);   // -1, 0 o 1

if (dir_h != 0) {
    x += dir_h * _vel;
    image_xscale = dir_h;        // el signo ya da la orientación
    sprite_index = spr_andando;
} else {
    sprite_index = spr_quieto;
}
```

> 💡 **`derecha - izquierda`** es el modismo estándar de GameMaker. `keyboard_check` devuelve
> 1 o 0, así que la resta da -1, 0 o 1 de golpe, y pulsar las dos teclas a la vez se cancela
> solo. Sirve para el eje vertical igual, y es la base del movimiento en 8 direcciones.
>
> 🔺 **Ojo con `sprite_index` en el Step:** asignarlo cada frame **reinicia la animación** si
> el sprite ya era ese. Aquí funciona porque solo hay dos sprites, pero en cuanto añadas un
> tercer estado necesitas la guarda `if (sprite_index != nuevo)`. Está explicado en
> [08 · Megaman X, sección 3](./08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md#3--máquina-de-estados-de-animación).

---

## 3 · Suelo, gravedad y salto

### Detectar el suelo con `collision_line`

En vez de comprobar solapamiento, se traza una **línea imaginaria justo debajo de los pies** y
se mira si toca el suelo:

```gml
/// obj_player · End Step
if (collision_line(x - 5, y + 1, x + 5, y + 1, obj_suelo, false, false)) {
    // hay suelo debajo
    gravity = 0;
    vspeed  = 0;
} else {
    gravity = 0.3;
}
```

Los seis argumentos son: `x1, y1, x2, y2, objeto, precise, notme`. La línea va de 5 px a la
izquierda a 5 px a la derecha de los pies, un píxel por debajo.

> 💡 **Por qué en End Step y no en Step:** el End Step se ejecuta **después** de que GameMaker
> haya aplicado `gravity` y `vspeed` y movido al objeto. Ahí es donde tiene sentido corregir la
> posición final.

### Limitar la velocidad de caída

Sin límite, la gravedad acelera indefinidamente y en dos segundos el personaje atraviesa el
suelo sin que ninguna comprobación llegue a tiempo:

```gml
if (vspeed > 7) vspeed = 7;
```

> 💡 **Esto no es cosmético, es de corrección.** Un objeto que cae a 40 px/frame puede saltarse
> un bloque de 32 px entero entre dos frames. Ponle siempre techo a la velocidad de caída.

### Encajar exactamente sobre el bloque

Aun con la línea, el personaje se hunde unos píxeles antes de detectarse. La solución es
preguntar **con qué bloque** se ha chocado y alinearse con él:

```gml
var _suelo = instance_place(x, y + 1, obj_suelo);
if (_suelo != noone) {
    y = _suelo.bbox_top;      // los pies justo sobre la cara superior del bloque
}
```

> 💡 Esto funciona **porque el origen está abajo**: `y` son los pies. Si el origen estuviera en
> el centro habría que restar medio sprite. Aquí se ve por qué el origen importaba tanto.
>
> 🔺 **2026:** mejor `bbox_top` del bloque que su `y`. La `y` del bloque depende de dónde esté
> su origen; `bbox_top` es siempre el borde real de la máscara.

### Saltar (solo desde el suelo)

```gml
/// dentro del if que confirma que hay suelo
if (keyboard_check_pressed(ord("Z"))) {
    vspeed = -10;
}
```

> 💡 **Poner el salto dentro del `if` del suelo** es lo que impide saltar en el aire. Es más
> limpio que una variable `puede_saltar` y no se puede desincronizar.
>
> 💡 **`ord("Z")`** convierte una letra en su código de tecla. Para las flechas y teclas
> especiales usa las constantes `vk_*` (`vk_space`, `vk_up`…).
>
> 🔺 **`keyboard_check_pressed`, no `keyboard_check`.** `_pressed` se dispara **una vez** al
> pulsar; sin el `_pressed`, mantener la tecla reaplica el impulso cada frame y el personaje
> sale volando.

### Sprite de salto

En el `else` (es decir, en el aire):

```gml
} else {
    gravity = 0.3;
    sprite_index = spr_saltando;
}
```

---

## 4 · Colisión con paredes y techos

### Paredes: preguntar antes de moverse

En vez de mover y corregir, se comprueba **si el destino está libre**:

```gml
if (dir_h != 0) {
    if (place_free(x + dir_h * _vel, y)) {
        x += dir_h * _vel;
    }
    image_xscale = dir_h;
}
```

> 💡 **`place_free` solo mira objetos marcados como `Solid`** en el editor. Si tu suelo no está
> marcado como sólido, esto no hará nada. Es la causa número uno de «no me funciona».
>
> 🔺 **2026 — el defecto de este método:** si `_vel` es 5 y te quedan 3 px hasta la pared,
> `place_free` da `false` y **no te mueves nada**: te frenas a 3 px de la pared en vez de
> pegarte a ella. Con velocidades bajas casi no se nota; con velocidades altas queda un hueco
> feo. La solución es el bucle de aproximación:
>
> ```gml
> var _dx = dir_h * _vel;
> if (!place_free(x + _dx, y)) {
>     while (place_free(x + sign(_dx), y)) x += sign(_dx);   // acercarse píxel a píxel
>     _dx = 0;
> }
> x += _dx;
> ```

### Techos: la misma línea, arriba

```gml
/// End Step
if (collision_line(x - 5, y - 15, x + 5, y - 15, obj_suelo, false, false)) {
    y = yprevious;
    vspeed = 0;
}
```

> 💡 **`yprevious`** es la `y` que tenía el objeto al principio del paso. Devolverlo ahí es la
> forma más rápida de anular un movimiento que no debía ocurrir.

### Una máscara de colisión propia

El problema que aparece al final del cuarto vídeo, y que merece la pena entender: si la
máscara del personaje es **su propio sprite**, la línea del techo (a `y - 15`) puede quedar
**dentro** de la máscara, y entonces el personaje se frena solo al andar pegado a una pared.

La solución es **darle al objeto una máscara propia**, más pequeña que el sprite:

1. Crea un sprite pequeño de color sólido (por ejemplo 10×10).
2. Ponle el mismo origen que al personaje (abajo y centrado).
3. En el objeto, campo **Collision Mask** → ese sprite.

> 🔺 **2026:** es exactamente la misma recomendación que en
> [08 · Megaman X](./08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md#create):
> **una sola máscara para todos los estados del personaje**. Si cada animación aporta su
> máscara, las colisiones cambian de tamaño al animar y el personaje se atasca o vibra. Es de
> las cosas que más quebraderos de cabeza ahorra.

---

## Los límites de este enfoque

La serie usa las variables de movimiento integradas (`gravity`, `vspeed`) y `place_free`. Es lo
correcto para aprender, pero conviene saber dónde se rompe:

| Límite | Qué pasa | Solución |
|---|---|---|
| `place_free` todo o nada | te frenas a varios píxeles de la pared | bucle de aproximación píxel a píxel |
| `gravity` + `vspeed` | GameMaker mueve el objeto **antes** de que puedas comprobar nada | llevar `vsp` propia y mover tú |
| Solo objetos `Solid` | `place_free` ignora todo lo demás | `place_meeting` con el objeto concreto |
| Sin rampas ni plataformas atravesables | no hay forma de añadirlas | resolución por ejes |
| `collision_line` a distancia fija | falla si la velocidad supera esa distancia | comprobar en el destino, no a distancia fija |

**Cuándo dar el salto:** en cuanto quieras rampas, plataformas de un solo sentido, movimiento
rápido o wall jump. El patrón está en
[08 · Megaman X, sección 1](./08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md#1--el-núcleo-colisión-por-ejes).

---

## Ruta sugerida

1. Esta serie completa, escribiendo el código tú (no copiándolo).
2. [06 · Curso de GML](./06%20-%20Curso%20de%20GML%20en%20v%C3%ADdeo%20-%20transcripci%C3%B3n%20estructurada.md) — el lenguaje en serio.
3. [07 · Eventos](./07%20-%20Curso%20de%20eventos%20en%20v%C3%ADdeo%20-%20transcripci%C3%B3n%20estructurada.md) — qué evento usar y por qué.
4. [08 · Megaman X](./08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md) — rehacer el movimiento bien.

---

Fuente original: canal [Alas de reptil](https://www.youtube.com/@alasdereptil).
