# 37 · DragoniteSpam — El temido «Variable Not Set Before Reading It»

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 25 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=RT1RjEy4BT4> |
| **Duración** | 21 min 6 s |
| **Publicado** | 9 de agosto de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | lectura de errores, pila de llamadas (*call stack*), ámbito de variables |

> A diferencia del problema de los sprites borrosos —que se arregla marcando una casilla—,
> **este error exige trabajo por tu parte**: hay que averiguar **dónde** ocurrió, **por qué** y
> **cómo arreglarlo**.

## Índice de contenido

1. Cómo leer un error de GameMaker
2. La pila de llamadas (*stack trace*)
3. Causa 1: la definición está comentada o no existe
4. Causa 2: el nombre está mal escrito
5. Causa 3: la variable no está definida en el otro objeto
6. Causa 4: confundir el ámbito (objeto equivocado)
7. Causa 5: variables definidas solo en ramas condicionales
8. Los avisos amarillos de Feather
9. Redefinir variables: funciona, pero no lo hagas
10. Leer una pila de llamadas con funciones

---

## 1. Cómo leer un error de GameMaker

Prácticamente todos los mensajes de error tienen la misma forma:

```
ERROR in
action number 1
of Draw Event
for object obj_player:

Variable obj_player.has_hat(100034, -2147483648) not set before reading it.
 at gml_Object_obj_player_Draw_0 (line 8) - if (has_hat == true)
```

Las primeras líneas te dicen:

| Dato | Ejemplo |
|---|---|
| **Dónde** ocurrió | En el **evento Draw** de `obj_player` |
| **Qué línea** exacta | **Línea 8** |
| **Qué error** | `Variable obj_player.has_hat has not been set before reading it` |

> El autor lo define como **el mensaje de error más común** que se encuentra la gente,
> porque es **muy fácil de provocar**.

---

## 2. La pila de llamadas (*stack trace*)

Debajo del error aparece una línea: es la **pila de llamadas**.

> Te dice **exactamente en qué punto de tu código** ocurrió. En el ejemplo solo tiene una
> línea y no es muy interesante; en un juego con muchos objetos y scripts, **puede ser
> bastante larga**.

---

## 3. Causa 1: la definición está comentada o no existe

El autor va al Draw de `obj_player`, línea 8, y ve `if (has_hat == true)`. Lógicamente la
variable debería estar definida en el **Create**… pero al mirar:

> **La línea está comentada.** Y cuando comentas la línea que define una variable,
> **lógicamente el juego no podrá usarla después».**

Solución: descomentar la línea.

Otras variantes de lo mismo:

- **Olvidaste definir la variable.**
- **Borraste líneas** que creías que no hacían falta, y una de ellas definía algo que se
  seguía usando en otra parte.

---

## 4. Causa 2: el nombre está mal escrito

> «Si esto no te ha pasado, no te rías, **te pasará** tarde o temprano.»

Si defines `has_hat` en el Create y luego escribes `has_hats` (o transpones letras, o
olvidas un guion bajo, o te equivocas con las mayúsculas), obtienes **el mismo error**.

Errores típicos:

- Letras **transpuestas** (`hast_hat`).
- Olvidar una letra al final.
- Olvidar un **guion bajo**.
- **Los nombres de variable en GameMaker distinguen mayúsculas de minúsculas**: `Has_Hat` y
  `has_hat` son distintos.

> **Consejo:** si tienes dudas, **copia y pega el nombre** de la variable. Así te aseguras
> de que se escribe igual en todas partes.

---

## 5. Causa 3: la variable no está definida en el otro objeto

Ejemplo: el jugador toca un botón y quieres subir un marcador.

```gml
var _button = instance_place(x, y, obj_button);

if (_button != noone)
{
    _button.high_score++;   // ⚠️ obj_button no define high_score
}
```

> `instance_place()` devuelve una **referencia a la instancia** si hay colisión, o el valor
> especial **`noone`** si no.

El error aquí será:

```
Variable obj_button.high_score not set before reading it
```

Porque **nunca has definido `high_score` en el Create de `obj_button`**.

Solución: inicialízala.

```gml
// Create event de obj_button
high_score = 0;
```

El autor usa un truco antiguo para ver el valor:

```gml
window_set_caption(_button.high_score);
```

> Es una función que fija el texto de la barra de título de la ventana. El autor reconoce
> que no pensaba en ella «desde hace unos quince años».

Al estar encima del botón, el valor sube **60 veces por segundo**.

---

## 6. Causa 4: confundir el ámbito (objeto equivocado)

Si en lugar de `_button.high_score` escribes `high_score` a secas **dentro del Step del
jugador**…

> …el juego se cierra con:
> ```
> Variable obj_player.high_score not set before reading it
> ```

La razón: `high_score` pertenece a `obj_button`, pero estás intentando tratarla como si
fuera una variable de instancia de `obj_player`, y **ese objeto no la tiene definida**.

> Si eres espabilado, al leer `obj_player.high_score` pensarás «eso no cuadra; esa variable
> debería pertenecer a otro objeto». Y eso te pondrá sobre la pista.

---

## 7. Causa 5: variables definidas solo en ramas condicionales

Este es el más interesante. Imagina que refactorizas el movimiento:

```gml
var _move_speed;

if (keyboard_check(vk_shift))
{
    _move_speed = 4;   // Correr
}
else
{
    _move_speed = 2;   // Andar
}

x += _move_speed;
```

> **Esto funciona**, y el autor lo garantiza al 100 %: por lectura del código se ve que la
> variable **siempre** queda definida en una de las dos ramas.

Pero aparecen **subrayados amarillos** bajo `_move_speed`.

### El aviso de Feather

> **Feather** es el sistema de IntelliSense de GameMaker. Te avisa de que intentas acceder a
> la variable local `_move_speed` **fuera del ámbito en que se definió**.

La razón de fondo:

> Técnicamente GameMaker **te deja** hacerlo. Pero **no deberías**, no porque rompa el código
> ahora mismo, sino porque **hace que sea más fácil romperlo después**.

### La demostración del desastre

Una semana más tarde decides añadir «modo sigilo» y cambias el `else` por un `else if`:

```gml
if (keyboard_check(vk_shift))
{
    _move_speed = 4;
}
else if (keyboard_check(vk_control))
{
    _move_speed = 1;
}
```

> Si el jugador **no** pulsa ni Shift ni Control, **ninguna de las dos ramas se ejecuta** y
> `_move_speed` **nunca se define**.

Resultado: `local variable _move_speed not set before reading it`.

### La solución correcta

Define la variable **con su valor por defecto antes** de las condicionales:

```gml
var _move_speed = 3;   // Valor por defecto: andar

if (keyboard_check(vk_shift))
{
    _move_speed = 4;   // Correr
}
else if (keyboard_check(vk_control))
{
    _move_speed = 1;   // Sigilo
}

x += _move_speed;
```

Ahora funciona siempre, y los subrayados amarillos desaparecen.

---

## 8. Los avisos amarillos de Feather

> **Debes hacer caso a los avisos amarillos y escribir el código de forma que no aparezcan.**

Aunque GameMaker permita algo, el aviso existe porque **puede ser señal de que has cometido
un error** que por pura casualidad no está rompiendo nada… **todavía**.

> «La actitud general en la comunidad de GameMaker es que puedes ignorar los subrayados
> amarillos. **No deberías**, porque están ahí por algo.»

---

## 9. Redefinir variables: funciona, pero no lo hagas

Tras la solución anterior aparecen **dos avisos amarillos nuevos**: estás **redefiniendo**
una variable que ya estaba definida.

> Otra vez: **funciona** y no rompe el juego por sí mismo. Pero es señal de un posible error
> que, si no tienes suerte, **sí** puede romper cosas en otras situaciones.

---

## 10. Leer una pila de llamadas con funciones

El último ejemplo incluye una **función** definida en un script, que accede a una variable
inexistente. Al pulsar Tab se llama a la función y el juego falla.

Ahora la pila tiene **dos líneas**:

```
at gml_Script_some_function_or_other (line 2)
at gml_Object_obj_player_Step_0 (line 10)
```

Cómo leerla:

> **Se lee de abajo arriba.**

1. `obj_player` Step, línea 10 → aquí se **llama** a la función.
2. `some_function_or_other`, línea 2 → aquí es donde **ocurrió realmente** el error.

> En un juego grande puede haber **muchas llamadas intermedias** por las que tendrás que ir
> subiendo para localizar el fallo exacto.

---

## Puntos clave

1. **Es el error más común** al empezar con GameMaker.
2. El mensaje te da **el objeto, el evento y la línea exacta**.
3. La **pila de llamadas** indica el recorrido; **se lee de abajo arriba**.
4. **Causas simples:** definición comentada, borrada, olvidada o **mal escrita**.
5. **Los nombres distinguen mayúsculas de minúsculas.**
6. Si usas el **operador punto**, la variable debe estar definida **en ese objeto**.
7. Cuidado con el **ámbito**: no trates una variable de otro objeto como propia.
8. **Define las variables con su valor por defecto ANTES** de las condicionales.
9. **Haz caso a los avisos amarillos de Feather**: existen por algo.
10. Saltarse un `else` y dejar solo `else if` puede dejar la variable **sin definir nunca**.

---

## Ejercicio propuesto

> **Objetivo:** provocar **a propósito** cada uno de los cinco casos y aprender a leer el
> mensaje de error. Provocar fallos es la forma más rápida de aprender a depurar.

1. **Comentada:** comenta en el Create la línea que define una variable y ejecuta. Lee el
   error: ¿ qué objeto, qué evento, qué línea te indica? Descoméntala.
2. **Mal escrita:** cambia una letra del nombre de la variable en un solo sitio. Ejecuta y
   lee el error. Después prueba a cambiar una **mayúscula** y comprueba que también falla.
3. **Otro objeto:** crea `obj_button` con colisión, usa `instance_place()` e intenta
   `_boton.high_score++` **sin** definirla. Lee el error y arréglalo definiendo la variable
   en el Create de `obj_button`.
4. **Ámbito equivocado:** escribe `high_score++` a secas desde el Step del jugador. Lee el
   error (`obj_player.high_score`) y explica por qué te da la pista.
5. **Visualización:** usa `window_set_caption()` para mostrar el valor en la barra de título.

**Parte de condicionales (la importante)**

6. Escribe el patrón `if / else` que define `_move_speed` en ambas ramas. Comprueba que
   funciona y **observa los subrayados amarillos**.
7. Cambia el `else` por `else if (keyboard_check(vk_control))`. Ejecuta **sin pulsar ninguna
   de las dos teclas** y comprueba el error.
8. Arréglalo definiendo `_move_speed` con su valor por defecto **antes** del `if`. Comprueba
   que los subrayados desaparecen y que las tres velocidades funcionan.
9. Fíjate en los **nuevos avisos amarillos** por redefinir la variable y reflexiona sobre por
   qué Feather te lo señala.

**Reto extra:** crea un script con una función que acceda a una variable inexistente,
llámala desde el Step al pulsar Tab, y lee la **pila de llamadas de dos líneas**. Identifica
cuál es la línea que llama y cuál la que falla. Explica por qué se lee **de abajo arriba**.
