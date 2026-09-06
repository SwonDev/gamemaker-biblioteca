# 03 · Movimiento básico y colisiones

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 3 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=LjZ3QPIqkOE> |
| **Duración** | 56 min 20 s |
| **Publicado** | 23 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `keyboard_check`, `place_meeting`, `sign`, `while`, `clamp`, `min`, `max`, `round` |

Este es el capítulo más largo y denso de la serie. Aquí escribes tu primer código de
verdad y construyes **un sistema de colisiones completo y reutilizable** que sirve
para casi cualquier juego 2D.

## Índice de contenido

1. Eventos: Create y Step
2. El game frame y los FPS
3. Comentarios en GML
4. Propiedades integradas: `x` e `y`
5. Operadores de asignación
6. Variables: de instancia frente a locales
7. Leer el teclado: `keyboard_check()`
8. Calcular la dirección con resta
9. Movimiento horizontal completo
10. Movimiento vertical: el eje Y está invertido
11. Capas de la room y bloques de colisión
12. Colisiones: `place_meeting()` y el bucle `while`
13. Condicionales: `if`, `else`, `!` y `while`
14. Regiones de código
15. Práctica avanzada: movimiento con momento
16. Subpíxeles: `x_real`, `y_real` y `round()`

---

## 1. Eventos: Create y Step

Las instancias tienen **propiedades integradas** que aparecen en verde oscuro al
escribirlas. El código se ejecuta dentro de **eventos**: cosas que ocurren.

Para añadir un evento a un objeto: **Add Event**.

| Evento | Cuándo se ejecuta |
|---|---|
| **Create** | **Una sola vez**, en el instante en que la instancia se crea |
| **Step** | **Cada game frame** del juego |
| Begin Step / End Step | Antes / después del Step normal |

El autor arrastra la pestaña del **Create** hasta el extremo izquierdo, para recordar
visualmente que es código que corre una vez y luego el Step toma el relevo.

---

## 2. El game frame y los FPS

Un **game frame** (fotograma de juego) es cada vez que el juego comprueba
instrucciones. En otros programas se llaman *ticks*.

Puedes ver y cambiar la velocidad en:

```
Game Options → General → Game Frames Per Second  (por defecto 60)
```

Deja el valor en **60**, que es el estándar.

> ¿Por qué ejecutar código 60 veces por segundo? Porque queremos que el juego
> compruebe 60 veces por segundo si el jugador está pulsando una tecla, de modo que
> el control se sienta **inmediato y sensible**.

---

## 3. Comentarios en GML

```gml
// Esto es un comentario: GameMaker lo ignora por completo
```

Todo lo que escribas tras dos barras **no se ejecuta**. Los comentarios aparecen en
verde oscuro. Sin ellos, el texto se interpreta como código y **el juego fallaría al
ejecutarlo**.

---

## 4. Propiedades integradas: `x` e `y`

- **`x`** → posición horizontal de la instancia en la room.
- **`y`** → posición vertical.

```gml
x = 100;   // La instancia se teletransporta a x = 100
```

Pero lo interesante es **sumar** sobre la posición actual:

```gml
x = x + 1;   // Cada frame: mira dónde estoy, súmale 1, y ese es mi nuevo sitio
```

Con esto, el objeto se mueve **un píxel a la derecha 60 veces por segundo**.

---

## 5. Operadores de asignación

Escribir `x = x + 1` es correcto pero tedioso. Las formas abreviadas:

| Forma | Equivale a | Efecto |
|---|---|---|
| `x += 1` | `x = x + 1` | Suma 1 |
| `x -= 1` | `x = x - 1` | Resta 1 |
| `x++` | `x = x + 1` | Suma 1 (aún más corto) |
| `x--` | `x = x - 1` | Resta 1 |
| `x *= 1.5` | `x = x * 1.5` | Multiplica (¡cuidado: crece exponencialmente!) |

> `x *= 1.5` dentro de un Step es un experimento divertido: como se multiplica 60
> veces por segundo, la velocidad se dispara de forma exponencial.

---

## 6. Variables: de instancia frente a locales

### Variables de instancia (en Create)

```gml
hsp = 2;   // Esta variable pertenece al objeto y GameMaker la recuerda
```

Declaradas en el **Create**, viven en memoria **mientras la instancia exista** y
puedes manipularlas de frame a frame. **Solo ese objeto** puede usarlas.

### Variables locales (`var`)

```gml
var _key_left = keyboard_check(vk_left);
```

- Se crean **este frame** y GameMaker las olvida al terminar.
- Son perfectas para cosas que **deben comprobarse cada frame desde cero**, como si
  una tecla está pulsada.

El autor prefija las locales con **guion bajo** (`_key_left`) para distinguirlas de
un vistazo. Es una convención, no una obligación.

> En GameMaker no hay distinción real entre `1`/`0` y `true`/`false`. Una función
> como `keyboard_check()` devuelve `1` si la tecla está pulsada y `0` si no.

---

## 7. Leer el teclado: `keyboard_check()`

```gml
var _key_left = keyboard_check(vk_left);
```

`keyboard_check()` **comprueba si una tecla está siendo mantenida pulsada** en este
frame. Las constantes de flechas son `vk_left`, `vk_right`, `vk_up`, `vk_down`.

Si quieres usar **letras**, no existen constantes: usa `ord()` con la letra entre
comillas:

```gml
var _key_left = keyboard_check(ord("A"));
```

Para descubrir todas las constantes disponibles, haz **clic central sobre `vk_left`**
y se abrirá la página *Keyboard Input* del manual con la lista completa.

---

## 8. Calcular la dirección con resta

Truco elegante y muy usado:

```gml
var _hdir = _key_right - _key_left;
```

| Teclas pulsadas | Cuenta | `_hdir` | Significado |
|---|---|---|---|
| Derecha | 1 − 0 | **1** | Derecha |
| Izquierda | 0 − 1 | **−1** | Izquierda |
| Ninguna | 0 − 0 | **0** | Nada |
| Ambas | 1 − 1 | **0** | Se anulan |

Un solo número resume la dirección: **−1 izquierda, 1 derecha, 0 quieto**.

---

## 9. Movimiento horizontal completo

**Create event de `oPlayer`:**

```gml
hsp = 0;          // Velocidad horizontal actual
vsp = 0;          // Velocidad vertical actual
move_speed = 3;   // Velocidad máxima de movimiento
```

**Step event de `oPlayer`:**

```gml
// --- Obtener entradas ---
var _key_left  = keyboard_check(vk_left);
var _key_right = keyboard_check(vk_right);

// --- Calcular movimiento horizontal ---
// Obtener la dirección: -1 izquierda, 1 derecha, 0 nada
var _hdir = _key_right - _key_left;

// Fijar la velocidad según la dirección
hsp = _hdir * move_speed;

// Aplicar el movimiento horizontal
x += hsp;
```

Si `hsp` es 0, sumar cero deja `x` exactamente donde estaba. El objeto se detiene.

---

## 10. Movimiento vertical: el eje Y está invertido

> **En GameMaker, `y = 0` es la parte SUPERIOR de la room, e `y` AUMENTA hacia
> abajo.**

Y en horizontal, `x = 0` es la izquierda y aumenta hacia la derecha.

Esto tiene una consecuencia directa al calcular la dirección vertical: como **abajo
es positivo**, la resta se hace al revés:

```gml
var _vdir = _key_down - _key_up;   // ABAJO primero, no arriba
```

- Pulsar **abajo** → 1 − 0 = **1** → `y` aumenta → baja.
- Pulsar **arriba** → 0 − 1 = **−1** → `y` disminuye → sube.

**Step completo con ambos ejes:**

```gml
// --- Obtener entradas ---
var _key_left  = keyboard_check(vk_left);
var _key_right = keyboard_check(vk_right);
var _key_up    = keyboard_check(vk_up);
var _key_down  = keyboard_check(vk_down);

// --- Movimiento horizontal ---
var _hdir = _key_right - _key_left;
hsp = _hdir * move_speed;
x += hsp;

// --- Movimiento vertical ---
var _vdir = _key_down - _key_up;   // Abajo es positivo
vsp = _vdir * move_speed;
y += vsp;
```

> Si prefieres usar **WASD**, sustituye las constantes por `ord("A")`, `ord("D")`,
> `ord("W")` y `ord("S")`.

---

## 11. Capas de la room y bloques de colisión

GameMaker funciona **por capas**, como Photoshop. En la room verás (en el panel de
Layers):

- **Instances** — donde viven las instancias de objetos.
- **Background** — el color o imagen de fondo.

Para organizar las colisiones, añade **otra capa de instancias**:

1. En el panel de capas, pulsa el **`+`**. Hay **siete tipos** de capa disponibles.
2. Elige **Instance Layer** y llámala `Colisiones`.
3. Arrástrala **debajo** de la capa `Instances` (lo que está arriba está más cerca
   del jugador).

Ahora crea el sprite y el objeto bloque:

- **`sBlock`:** 30 × 30, FPS 0, origen **Top Left**, relleno gris.
- **`oBlock`:** objeto al que se le asigna `sBlock`.

Con la capa `Colisiones` seleccionada, ajusta la rejilla a **30 × 30** (el tamaño del
sprite) y pinta con `Alt` un **borde completo** alrededor de la room.

> Ventaja de las capas separadas: si haces `Shift` + arrastrar para seleccionar todo
> en la capa `Colisiones` y pulsas `Supr`, **no borras a `oPlayer`**, porque está en
> otra capa.

---

## 12. Colisiones: `place_meeting()` y el bucle `while`

### La idea

`place_meeting(x, y, obj)` responde a una pregunta hipotética:

> *«Si yo estuviera en la posición (x, y), ¿solaparía con una instancia de `obj`?»*

No te mueve: **solo pregunta**. Por eso podemos usarla para **mirar antes de saltar**.

### El problema

Si simplemente haces `x += hsp` y después compruebas la colisión, el objeto ya se ha
metido dentro de la pared.

### La solución: comprobar dónde *estarás*

```gml
if (place_meeting(x + hsp, y, oBlock))
```

Es decir: *«si me moviera `hsp` píxeles, ¿chocaría?»*. Si la respuesta es sí, en vez
de moverte de golpe, **avanza de píxel en píxel hasta tocar la pared**.

### `sign()` y el bucle `while`

```gml
var _one_pixel = sign(hsp);   // 1 si vamos a la derecha, -1 si a la izquierda
```

`sign()` devuelve **1** si el valor es positivo y **−1** si es negativo.

```gml
while (!place_meeting(x + _one_pixel, y, oBlock))
{
    x += _one_pixel;
}
```

El `!` (que en programación se lee *bang*) **invierte** la condición: «mientras
**no** vaya a chocar…».

Y `while` significa:

> **Repite este código dentro del mismo frame, una y otra vez, hasta que la condición
> deje de cumplirse.**

### Animación del algoritmo

Imagina que estás a 2 píxeles de la pared y `hsp = 3`:

1. «¿Si muevo 1 píxel, choco?» → No → mueve 1 píxel.
2. «¿Si muevo 1 píxel más, choco?» → No → mueve 1 píxel.
3. «¿Si muevo 1 píxel más, choco?» → **Sí** → para.

Resultado: te quedas **pegado a la pared, sin atravesarla**.

### Código completo de colisión horizontal

```gml
// --- Colisión horizontal ---
if (place_meeting(x + hsp, y, oBlock))
{
    // ¿El siguiente fotograma solapará con oBlock?

    // Obtener 1 o -1 según la dirección del movimiento
    var _one_pixel = sign(hsp);

    // Avanzar de píxel en píxel hasta estar pegados al bloque
    while (!place_meeting(x + _one_pixel, y, oBlock))
    {
        x += _one_pixel;
    }

    hsp = 0;   // Detener el movimiento
}

// Aplicar el movimiento horizontal
x += hsp;
```

### Colisión vertical (la misma lógica en el eje Y)

```gml
// --- Colisión vertical ---
if (place_meeting(x, y + vsp, oBlock))
{
    // Obtener 1 o -1 según la dirección del movimiento
    var _one_pixel = sign(vsp);

    while (!place_meeting(x, y + _one_pixel, oBlock))
    {
        y += _one_pixel;
    }

    vsp = 0;   // Detener el movimiento
}

// Aplicar el movimiento vertical
y += vsp;
```

> **Orden correcto:** primero la colisión horizontal y su movimiento, y **después**
> calcular el movimiento vertical con su colisión. Así el movimiento diagonal
> funciona: puedes deslizarte por una pared.

---

## 13. Condicionales: `if`, `else`, `!` y `while`

```gml
if (condición)
{
    // código que se ejecuta si la condición es verdadera
}
```

- El código condicional **siempre se indenta un nivel** con `Tab`. GameMaker te
  ayuda: al resaltar una llave de cierre, resalta también su pareja.
- Para **comparar** se usan **dos** iguales (`==`); para **asignar**, uno solo (`=`).

```gml
if (1 == 1) { /* verdadero: se ejecuta */ }
if (1 == 2) { /* falso: se ignora por completo */ }
```

### `else`

```gml
if (condición)
{
    // si se cumple
}
else
{
    // en CUALQUIER otro caso
}
```

`else` captura todo lo demás: es la forma de decir «si esto sí, haz A; si no, haz B».

---

## 14. Regiones de código

Cuando el Step empieza a crecer, usa **regiones** para plegar secciones:

```gml
#region ENTRADAS
    // ...código de lectura de teclado...
#endregion

#region MOVIMIENTO HORIZONTAL
    // ...código horizontal...
#endregion

#region MOVIMIENTO VERTICAL
    // ...código vertical...
#endregion
```

GameMaker muestra un pequeño botón de **minimizar** junto a cada región, así puedes
plegar lo que no necesitas y trabajar con el código limpio.

---

## 15. Práctica avanzada: movimiento con momento

> El autor avisa: esto es **práctica avanzada**. Si lo anterior ya te ha resultado
> abrumador, **limítate a leerlo** y salta al siguiente capítulo. Podrás volver e
> implementarlo más adelante.

El movimiento de «mantener tecla = velocidad instantánea» se siente rígido. Los
juegos de plataformas suelen usar **momento**: aceleras poco a poco hasta la
velocidad máxima y frenas gradualmente al soltar.

**Añade al Create:**

```gml
accel = 0.1;    // Aceleración: cuánto se suma al momento
decel = 0.05;   // Desaceleración: cuánto se resta del momento
```

**En el Step, sustituye `hsp = _hdir * move_speed` por:**

```gml
// Añadir aceleración: negativo da momento a la izquierda, positivo a la derecha
hsp += _hdir * accel;

// Frenar a oPlayer si no se pulsa ninguna dirección
if (_hdir == 0)   // Sin dirección pulsada, o ambas
{
    if (hsp < 0)  // Yendo a la izquierda
    {
        hsp = min(hsp + decel, 0);
    }
    else          // Yendo a la derecha (o quieto)
    {
        hsp = max(hsp - decel, 0);
    }
}

// Limitar la velocidad horizontal máxima
hsp = clamp(hsp, -move_speed, move_speed);
```

### `min()` y `max()`

- **`min(a, b, …)`** devuelve el **más pequeño** de los valores que le pases.
- **`max(a, b, …)`** devuelve el **más grande**.

`min(hsp + decel, 0)` es la clave para **acercarse a cero sin pasarse**: si vas a
−3, cada frame se acerca a 0 (−2,95; −2,90; …) y en cuanto la suma rebasaría cero,
`min()` devuelve **0** y se detiene. `max()` hace lo mismo hacia abajo.

### `clamp()`

```gml
clamp(valor, mínimo, máximo)
```

Garantiza que un valor **nunca salga** del rango indicado. Así `hsp` jamás superará
`move_speed` ni bajará de `-move_speed`.

Copia exactamente el mismo bloque para el eje vertical, cambiando `hsp`→`vsp`,
`_hdir`→`_vdir`.

---

## 16. Subpíxeles: `x_real`, `y_real` y `round()`

GameMaker **admite posiciones con decimales** (por ejemplo `x = 1.7`), y eso hace
que el arte se estire, se recorte o se aproxime.

En juegos grandes (720p o más) no importa. Pero en **pixel art pequeño y crujiente**
sí: quieres que cada píxel sea un píxel.

### La técnica

Separa la **posición real** (con decimales) de la **posición dibujada** (siempre
entera).

**En el Create:**

```gml
x_real = x;   // Posición real de oPlayer (admite subpíxeles)
y_real = y;   // Posición real de oPlayer
```

**En el Step:**

```gml
x_real += hsp;
x = round(x_real);   // En pantalla siempre un número entero

// ...

y_real += vsp;
y = round(y_real);
```

`round()` redondea al entero más cercano. También existen `floor()` (siempre redondea
hacia abajo) y `ceil()` (siempre hacia arriba).

> **Cuidado:** al hacer esto tendrás que **cambiar también el código de colisiones**
> para que use `x_real` e `y_real` en lugar de `x` e `y`. Si no, el objeto se quedará
> atascado, porque estarás comprobando una coordenada y moviendo otra.

Recorre todo el Step y **sustituye cada `x` e `y` por `x_real` e `y_real`**, salvo en
las dos líneas donde se redondea y se asigna a `x` / `y`.

El resultado tiene un movimiento ligeramente «escalonado»: es el aspecto correcto de
un pixel art auténtico, donde **ningún píxel se deforma nunca**.

### Orden de ejecución

> El código del Step se ejecuta **de arriba abajo**, todo él, en cada frame. Por eso
> puedes modificar `hsp`, `vsp`, `x_real` e `y` por el camino y los cambios se
> acumulan en el mismo fotograma.

---

## Puntos clave

1. **Create** corre una vez; **Step** corre 60 veces por segundo.
2. **`x` e `y`** son propiedades integradas de las instancias.
3. **`+=`, `-=`, `++`, `--`** son atajos de asignación.
4. **Variables de instancia** (en Create) persisten; **locales (`var`)** viven un
   solo frame. El autor las prefija con `_`.
5. **`keyboard_check(vk_left)`** para flechas; **`keyboard_check(ord("A"))`** para
   letras.
6. **`_key_right - _key_left`** da −1, 0 o 1 en una sola línea.
7. **En GameMaker, `y` crece hacia ABAJO.** Por eso la dirección vertical es
   `_key_down - _key_up`.
8. **`place_meeting(x, y, obj)`** es una pregunta hipotética: no mueve nada.
9. El patrón de colisión es: **comprobar `x + hsp` → avanzar de píxel en píxel con
   `while` y `sign()` → poner `hsp = 0` → aplicar `x += hsp`**.
10. **Haz la colisión horizontal completa antes de empezar la vertical** para poder
    deslizarte por las paredes.
11. **Dos iguales para comparar, uno para asignar.**
12. **`#region` / `#endregion`** te permiten plegar secciones de código.
13. **`clamp()`, `min()` y `max()`** dan movimiento con aceleración y frenada
    suaves.
14. **Separa `x_real` de `x`** con `round()` para pixel art perfecto. Y no olvides
    actualizar las colisiones.

---

## Ejercicio propuesto

> **Objetivo:** construir desde cero un sistema de movimiento en 8 direcciones con
> colisiones sólidas, y después añadirle momento.

**Parte A — Movimiento y colisiones**

1. Parte del proyecto del capítulo 2. Crea `sBlock` (30 × 30, origen **Top Left**)
   y `oBlock`.
2. Añade la capa `Colisiones` debajo de `Instances` y pinta un borde cerrado
   alrededor de `rGame` con `Alt`.
3. En el **Create** de `oPlayer`, declara:

   ```gml
   hsp = 0;          // Velocidad horizontal actual
   vsp = 0;          // Velocidad vertical actual
   move_speed = 3;   // Velocidad máxima
   ```

4. En el **Step**, implementa las tres regiones (`ENTRADAS`, `MOVIMIENTO
   HORIZONTAL`, `MOVIMIENTO VERTICAL`) con flechas.
5. Añade la colisión horizontal y la vertical exactamente como se ha explicado.
6. Comprueba que **no puedes salirte** de la room, que te **deslizas** por las
   paredes al ir en diagonal, y que las esquinas no te atrapan.
7. Cambia las flechas por **WASD** usando `ord()`.

**Parte B — Momento (avanzado)**

8. Añade `accel = 0.1` y `decel = 0.05` al Create.
9. Sustituye la asignación directa de velocidad por el bloque de aceleración,
   frenada con `min()`/`max()` y límite con `clamp()`.
10. Aplica lo mismo al eje vertical.
11. Experimenta: prueba `accel = 0.3` con `decel = 0.4` (movimiento seco y
    arcade) frente a `accel = 0.05` con `decel = 0.02` (movimiento flotante, tipo
    hielo). Anota cuál encaja mejor con el juego que imaginas.

**Parte C — Pixel perfect (avanzado)**

12. Añade `x_real` e `y_real` al Create.
13. Cambia los movimientos a `x_real += hsp;` / `x = round(x_real);` y el equivalente
    vertical.
14. **Repasa todo el Step y sustituye `x` e `y` por `x_real` e `y_real` en las
    colisiones.** Comprueba que ya no te quedas atascado.
15. Exporta tu YYZ.

**Reto extra:** coloca un bloque suelto en medio de la room y comprueba que puedes
rodearlo. Después, método infalible de depuración: comenta temporalmente la línea
`hsp = 0;` y observa qué ocurre. Vuelve a dejarla como estaba y explica con tus
palabras por qué es necesaria.
