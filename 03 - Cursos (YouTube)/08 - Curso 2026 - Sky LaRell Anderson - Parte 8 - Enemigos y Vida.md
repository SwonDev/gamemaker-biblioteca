# 08 · Enemigos y puntos de vida

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 8 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=ilBHBKZUeD4> |
| **Duración** | 30 min 27 s |
| **Publicado** | 28 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `draw_healthbar`, `exit`, `distance_to_object`, arrays en `place_meeting`, `game_restart` |

Última mecánica principal antes de pasar al arte y al sonido. Aquí aparecen dos
herramientas potentísimas: **pasar varios objetos a la vez a `place_meeting()`** y la
sentencia **`exit`**.

## Índice de contenido

1. El sprite y el objeto enemigo
2. Calcular el daño por bala
3. Sistema de vida del enemigo
4. Que la bala detecte al enemigo: objetos múltiples
5. La capa de enemigos
6. Barra de vida con `draw_healthbar()`
7. Hacer que los enemigos sean peligrosos
8. Práctica avanzada: vida del jugador con invulnerabilidad
9. Práctica avanzada: indicador de vida con fotogramas
10. Práctica avanzada: estado de agresividad con `exit`

---

## 1. El sprite y el objeto enemigo

Crea **`sEnemy`** de **30 × 30** relleno de rojo, y el objeto **`oEnemy`** con ese
sprite.

> Fíjate en lo rápido que avanzamos ahora que ya conoces los pasos: crear sprite,
> crear objeto, asignar sprite, Create event.

---

## 2. Calcular el daño por bala

La explosión **causa daño cada fotograma mientras está animada y solapando** al
enemigo. Para saber cuánto daño total hace una bala:

```
daño por bala = fotogramas de explosión ÷ (FPS del sprite ÷ FPS del juego)
```

Con los valores del proyecto:

| Dato | Valor |
|---|---|
| Fotogramas de la explosión | **6** |
| FPS del sprite | **30** |
| FPS del juego | **60** |

```
30 / 60 = 0,5
6 / 0,5 = 12
```

**Una bala causa 12 puntos de daño** (1 por fotograma durante 12 fotogramas).

Ahora decides cuántas balas deben matar al enemigo. Con 12 de daño:

- 4 balas → `hp = 48`
- 5 balas → `hp = 60`

El autor se queda con **60**.

---

## 3. Sistema de vida del enemigo

**Create event de `oEnemy`:**

```gml
hp = 60;
```

**Step event de `oEnemy`:**

```gml
// Mientras la explosión nos solape, recibimos daño cada fotograma
if (place_meeting(x, y, oBulletExplode))
{
    hp--;
}

// Sin vida: destruir
if (hp <= 0)
{
    instance_destroy();
}
```

---

## 4. Que la bala detecte al enemigo: objetos múltiples

Para que la bala explote **tanto** contra bloques **como** contra enemigos, hay que
hacer dos cosas:

1. Que la explosión se vea **en el borde** del enemigo.
2. Que la explosión llegue a **producirse**.

La solución es elegante: `place_meeting()` **acepta una lista de objetos** usando
corchetes.

```gml
place_meeting(x + hspeed, y, [oBlock, oEnemy])
```

> Copia el bloque entero **incluidos los corchetes** y sustituye **todas** las
> comprobaciones de colisión de `oBullet`.

**Step event de `oBullet` (versión completa):**

```gml
// Colisión horizontal contra bloques O enemigos
if (place_meeting(x + hspeed, y, [oBlock, oEnemy]))
{
    var _pixel = sign(hspeed);

    while (!place_meeting(x + _pixel, y, [oBlock, oEnemy]))
    {
        x += _pixel;
    }

    instance_create_layer(x, y, "Instances", oBulletExplode);
    instance_destroy();
}

// Colisión vertical contra bloques O enemigos
if (place_meeting(x, y + vspeed, [oBlock, oEnemy]))
{
    var _pixel = sign(vspeed);

    while (!place_meeting(x, y + _pixel, [oBlock, oEnemy]))
    {
        y += _pixel;
    }

    instance_create_layer(x, y, "Instances", oBulletExplode);
    instance_destroy();
}
```

---

## 5. La capa de enemigos

Crea una capa nueva llamada **`Enemies`**, situada **debajo de `Instances` pero
encima de `Collisions`**, y esparce varios `oEnemy` por la room.

Al ejecutar, los enemigos mueren tras varios impactos.

> El autor observa que, **como la cadencia de disparo es mayor que los 6 fotogramas
> de la explosión**, el enemigo absorbe varias balas mientras su vida baja. El
> resultado le parece bien: «a veces, si algo **se siente** bien, importa más que sea
> preciso».

---

## 6. Barra de vida con `draw_healthbar()`

**Añade al Create:**

```gml
max_hp = hp;
```

**Draw event de `oEnemy`:**

```gml
draw_self();   // Dibuja al enemigo

// Solo mostramos la barra si ha recibido daño
if (hp < max_hp)
{
    var _bar_h = 5;                 // Alto de la barra en píxeles
    var _w = sprite_width  / 2;     // Mitad del ancho: la barra se adapta al sprite
    var _h = sprite_height / 2;     // Mitad del alto

    draw_healthbar(
        x - _w,                     // x1 (esquina superior izquierda)
        y - _h - 1 - _bar_h,        // y1: encima del sprite, con 1 píxel de colchón
        x + _w,                     // x2 (esquina inferior derecha)
        y - _h - 1,                 // y2
        (hp / max_hp) * 100,        // Cantidad: de 0 a 100
        c_black,                    // Color de fondo
        c_red,                      // Color con vida mínima
        c_lime,                     // Color con vida máxima
        0,                          // Dirección (0 = barra horizontal clásica)
        false,                      // ¿Mostrar fondo?
        false                       // ¿Mostrar borde?
    );
}
```

Detalles:

- `hp / max_hp` da una fracción (0 a 1); multiplicada por 100 da el **0-100** que
  exige la función (**no** es un porcentaje: es literalmente un valor de 0 a 100).
- Usar `sprite_width / 2` hace que **si cambias el tamaño del sprite, la barra se
  adapte sola**.
- El `- 1` garantiza al menos **un píxel de separación** con el sprite.
- **Dirección:** 0, 1, 2 o 3, según de dónde «tire» la barra. Consulta la
  documentación si quieres barras verticales o inversas.
- Aunque pongas `false` en «mostrar fondo», **hay que rellenar el argumento de
  color igualmente**.

> `draw_healthbar()` sirve para **cualquier cantidad entre 0 y 100 %**, no solo para
> vida: progreso, carga, energía…

---

## 7. Hacer que los enemigos sean peligrosos

**Nueva región en el Step de `oPlayer`:**

```gml
#region VIDA / FIN DE PARTIDA
if (place_meeting(x, y, oEnemy))
{
    room_restart();
}
#endregion
```

Con eso, tocar un enemigo reinicia la room.

---

## 8. Práctica avanzada: vida del jugador con invulnerabilidad

> El autor avisa de que esta sección avanzada es **más larga** que la parte normal del
> capítulo.

**Añade al Create de `oPlayer`:**

```gml
hp = 4;                    // Vida del jugador
max_hp = hp;

invul_timer_max = 120;     // Fotogramas de invulnerabilidad tras recibir daño
invul_timer = 0;

blink_timer_max = 8;       // Fotogramas entre parpadeos
blink_timer = 0;

a = 1;                     // Alfa: 1 = opaco, 0.5 = semitransparente
```

**Sustituye la región VIDA / FIN DE PARTIDA por:**

```gml
#region VIDA / FIN DE PARTIDA
// Recibir daño (solo si no somos invulnerables)
if (place_meeting(x, y, oEnemy) && (invul_timer <= 0))
{
    hp--;
    invul_timer = invul_timer_max;
}

// Mientras dure la invulnerabilidad…
if (invul_timer > 0)
{
    // …parpadear
    if (blink_timer > 0)
    {
        blink_timer--;
    }
    else
    {
        blink_timer = blink_timer_max;

        // Alternar entre semitransparente y opaco
        if (a == 1)
        {
            a = 0.5;
        }
        else
        {
            a = 1;
        }
    }

    // Reducir el temporizador de invulnerabilidad
    invul_timer--;
}
else
{
    // Fin de la invulnerabilidad: dejar el alfa sólido y resetear
    a = 1;
    blink_timer = 0;
}

// Sin vida: reiniciar el juego
if (hp <= 0)
{
    game_restart();
}
#endregion
```

### Por qué usar comparaciones inclusivas

> El autor siempre usa `<=` o `>=` en vez de `==` **a propósito**. Es más seguro: si
> más adelante el daño pasa a ser de 3 en 3, la vida podría saltar de 1 a −2 y
> **nunca ser exactamente 0**. Con `<= 0` lo capturas igual.
>
> «Cuando trabajas con números, es bueno tener comprobaciones **inclusivas** en lugar
> de precisas.»

### Aplicar el parpadeo

En el **Draw**, donde dibujas el sprite del jugador y el arma, cambia el argumento de
alfa por la variable `a`:

```gml
draw_sprite_ext(sPlayer, 0, x, y, 1, 1, angle, c_white, a);
draw_sprite_ext(sGun,    0, x, y, 1, 1, _dir,  c_white, a);
```

> **Tercer error real del tutorial:** el autor tiene una errata en el nombre de una
> variable y el juego da error. Lo localiza por la línea que indica el compilador y lo
> corrige.

---

## 9. Práctica avanzada: indicador de vida con fotogramas

Crea el sprite **`sHP`** de **19 × 4**, FPS 0, origen **Bottom Center**.

> El origen **abajo-centro** facilita calcular la posición: el indicador quedará
> **encima** del jugador.

Dibuja **cinco fotogramas**, cada uno con el número correspondiente de cajas
rellenas:

| Fotograma | Vida representada |
|---|---|
| 0 | 0 HP |
| 1 | 1 HP |
| 2 | 2 HP |
| 3 | 3 HP |
| 4 | 4 HP |

**En el Draw de `oPlayer`:**

```gml
// --- Indicador de vida ---
if (hp < max_hp)
{
    draw_sprite(sHP, hp, x, y - sprite_height / 2 - 10);
}
```

El truco está en pasar **`hp` como subimagen**: como los fotogramas están ordenados,
el número de vida **es** el índice del fotograma. Elegante y sin condicionales.

Se dibuja 10 píxeles por encima del jugador. El fotograma 0 existe por si en el futuro
añades un fundido y quieres ver el «cero».

> Podrías dibujar corazones si el sprite fuera algo más alto y ancho.

---

## 10. Práctica avanzada: estado de agresividad con `exit`

Los enemigos estarán quietos hasta que te acerques; entonces te perseguirán.

**Añade al Create de `oEnemy`:**

```gml
move_speed = 1;         // Velocidad de persecución
aggro_distance = 100;   // Distancia a la que detectan al jugador
```

**En el Step, antes de todo lo demás:**

```gml
// --- Cosas de agresividad ---
if (distance_to_object(oPlayer) > aggro_distance)
{
    exit;   // ¡Salir del evento! Nada de lo de abajo se ejecuta
}

// Todo lo que sigue SOLO ocurre si oPlayer está más cerca que aggro_distance
```

### `exit`

> `exit` le dice a GameMaker: **deja de leer el resto de este evento**.

Es utilísimo. Ejemplo del autor: si tienes un menú de pausa, pones al principio del
Step `if (global.pause) exit;` y **todo el evento se detiene** sin tener que
envolverlo en un `if` gigante.

### `distance_to_object()`

Mide la distancia desde el **borde de la caja de colisión** de la instancia que llama
hasta el **borde de la instancia más cercana** del objeto indicado.

(Recuerda: `distance_to_point()` hace lo mismo pero hacia unas coordenadas concretas.)

### Calcular el movimiento

Truco ingenioso: se usa el sistema `speed`/`direction` **solo para que GameMaker
calcule `hspeed` y `vspeed`**, y luego se anula:

```gml
// Calcular movimiento horizontal y vertical
speed = 1;
direction = point_direction(x, y, oPlayer.x, oPlayer.y);

var _hsp = hspeed;   // GameMaker ya ha calculado los componentes
var _vsp = vspeed;

speed = 0;           // No queremos que se mueva solo: lo haremos con colisiones
```

> **El orden importa:** hay que leer `hspeed`/`vspeed` **antes** de poner `speed = 0`.

Y después, las colisiones de siempre, contra bloques **y** contra otros enemigos:

```gml
// Colisión horizontal
if (place_meeting(x + _hsp, y, [oBlock, oEnemy]))
{
    var _pixel = sign(_hsp);

    while (!place_meeting(x + _pixel, y, [oBlock, oEnemy]))
    {
        x += _pixel;
    }

    _hsp = 0;
}
x += _hsp;

// Colisión vertical
if (place_meeting(x, y + _vsp, [oBlock, oEnemy]))
{
    var _pixel = sign(_vsp);

    while (!place_meeting(x, y + _pixel, [oBlock, oEnemy]))
    {
        y += _pixel;
    }

    _vsp = 0;
}
y += _vsp;
```

Al incluir `oEnemy` en la lista, **los enemigos chocan entre sí** y se van apartando
unos a otros en vez de amontonarse.

> **⚠️ Cuidado con las referencias directas:** escribir `oPlayer.x` **provoca un
> fallo** si en algún momento no existe ninguna instancia de `oPlayer` en la room.
> Puedes protegerte con `if (instance_exists(oPlayer))`. En este juego en concreto el
> autor sabe que `oPlayer` siempre existe (al morir reinicia, no se destruye).

> **Cuarto error real:** al escribir este bloque aparecen errores de compilación por
> un punto y coma y una letra de más. El autor los localiza gracias a los
> **subrayados ondulados** del editor.

---

## Puntos clave

1. **El daño por bala se calcula** con `fotogramas ÷ (FPS sprite ÷ FPS juego)`.
2. **`place_meeting()` acepta una lista de objetos**: `[oBlock, oEnemy]`.
3. **`draw_healthbar()`** necesita un valor de **0 a 100**, no un porcentaje:
   `(hp / max_hp) * 100`.
4. Usa **`sprite_width / 2`** para que la barra se adapte si cambias el arte.
5. **Las comparaciones inclusivas (`<=`, `>=`) son más seguras** que las exactas.
6. Podemos usar el **índice de fotograma como valor** (`draw_sprite(sHP, hp, …)`) si
   ordenamos los fotogramas con sentido.
7. **`exit` detiene el evento en seco**: ideal para pausas y estados de agresividad.
8. **`distance_to_object()`** mide de borde a borde de la caja de colisión.
9. **Truco:** fija `speed`/`direction`, lee `hspeed`/`vspeed`, y vuelve a poner
   `speed = 0`. El orden importa.
10. **Incluir `oEnemy` en las colisiones** hace que los enemigos no se amontonen.
11. **Cuidado con `oPlayer.x`**: si el objeto puede no existir, protege con
    `instance_exists()`.
12. `room_restart()` reinicia la room; **`game_restart()`** reinicia el juego entero.

---

## Ejercicio propuesto

> **Objetivo:** dotar a los enemigos de vida, barra de vida, letalidad e inteligencia
> básica, y dar vida al jugador.

**Parte A — Enemigos con vida**

1. Crea `sEnemy` (30 × 30, rojo) y `oEnemy`.
2. Calcula el daño de tu explosión con la fórmula y fija `hp` en consecuencia. Si
   quieres 3 balas, ¿cuánto vale `hp`?
3. Implementa en el Step el daño por solapamiento con `oBulletExplode` y la destrucción
   al llegar a cero.
4. Cambia **todas** las colisiones de `oBullet` para usar `[oBlock, oEnemy]`.
5. Crea la capa `Enemies` (entre `Collisions` e `Instances`) y coloca 5 enemigos.

**Parte B — Barra de vida**

6. Añade `max_hp = hp` al Create.
7. Añade el Draw con `draw_self()` y `draw_healthbar()` con los 11 argumentos.
8. Comprueba que la barra **solo aparece** al recibir el primer impacto.
9. Prueba los valores de dirección 0, 1, 2 y 3 y describe qué hace cada uno.

**Parte C — Letalidad y vida del jugador**

10. Haz que tocar un enemigo provoque `room_restart()`.
11. Implementa la vida del jugador: `hp`, `max_hp`, `invul_timer_max`, `blink_timer_max`
    y `a`.
12. Implementa la recepción de daño, el parpadeo alternando `a` entre 1 y 0,5, y el
    reinicio con `game_restart()`.
13. Pasa la variable `a` como alfa en los dos `draw_sprite_ext()` del Draw.
14. Crea `sHP` con origen **Bottom Center** y sus 5 fotogramas, y dibújalo con
    `draw_sprite(sHP, hp, …)`.

**Parte D — Agresividad (avanzado)**

15. Añade `move_speed` y `aggro_distance` al Create de `oEnemy`.
16. Añade el `if (distance_to_object(oPlayer) > aggro_distance) { exit; }` al principio
    del Step.
17. Implementa el cálculo de movimiento con `speed`/`direction` → `hspeed`/`vspeed`
    → `speed = 0`, y las dos colisiones contra `[oBlock, oEnemy]`.
18. Comprueba que los enemigos te persiguen al acercarte, chocan con los bloques y
    **se empujan entre ellos**.

**Reto extra:** el autor advierte del peligro de `oPlayer.x`. Crea una habitación de
pruebas **sin** `oPlayer` y mete un `oEnemy`. Observa el fallo, y después resuélvelo
envolviendo el bloque de agresividad en `if (instance_exists(oPlayer))`. Explica por
qué GameMaker no detecta este problema al editar.
