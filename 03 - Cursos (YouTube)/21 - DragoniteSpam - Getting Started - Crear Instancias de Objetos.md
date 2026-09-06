# 21 · DragoniteSpam — Crear instancias de objetos por código

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 9 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=bPDMWCzzGd0> |
| **Duración** | 12 min 5 s |
| **Publicado** | 18 de febrero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `depth = -y`, `instance_create_depth()`, `instance_create_layer()`, `hspeed`/`vspeed`, variables locales con `var` |

Construir niveles arrastrando objetos al editor está muy bien, pero **a veces necesitas
crear cosas mientras el juego corre**. Este capítulo enseña cómo, y de paso presenta la
que probablemente es **la línea de código más famosa de todo GameMaker**.

## Índice de contenido

1. `depth = -y`: la línea más famosa de GameMaker
2. Crear instancias desde el editor
3. `instance_create_depth()`
4. Argumentos opcionales entre corchetes
5. `instance_create_layer()`
6. Capas: el editor restrige, el runtime no
7. El valor devuelto: una referencia a la instancia
8. Variables locales frente a variables de instancia
9. El operador punto
10. `hspeed` y `vspeed`

---

## 1. `depth = -y`: la línea más famosa de GameMaker

Antes de empezar, el autor añade un objeto **`obj_scarecrow`** (espantapájaros) con el
sprite anclado en **bottom center**, igual que el jugador. En su **Step** solo hay una
línea:

```gml
depth = -y;
```

> «En mi opinión, probablemente sea **la línea de código más famosa de todo GameMaker**.
> Es extremadamente común verla por ahí.»

**Qué hace:** garantiza que los objetos **más cerca de la parte inferior de la pantalla se
dibujen delante** de los que están más arriba. Eso da el efecto de **profundidad
correcto** en juegos con cámara cenital.

El autor tiene un vídeo largo explicando el cómo y el porqué, pero avisa de que entra en
cosas más avanzadas de las vistas hasta ahora en la serie.

Añade la misma línea al final del Step del jugador.

---

## 2. Crear instancias desde el editor

Arrastrar `obj_scarecrow` a la room es fácil y da mucho juego. Y gracias a
`depth = -y`:

- Si te pones **delante** del espantapájaros, te dibujan **encima**.
- Si te pones **detrás**, te dibujan **debajo**.

Eso es, en esencia, **ordenación por profundidad** (*depth sorting*).

Pero es muy habitual querer **crear estas cosas por código**.

---

## 3. `instance_create_depth()`

En el Step del jugador:

```gml
if (keyboard_check_pressed(vk_space))
{
    instance_create_depth(200, 150, 0, obj_scarecrow);
}
```

### ¿Por qué `_pressed`?

> Se usa **`keyboard_check_pressed`** en lugar de `keyboard_check` porque queremos que
> responda **exactamente una vez** al pulsar, y **no continuamente** mientras se mantiene
> la tecla.

### Los argumentos

| Argumento | Significado |
|---|---|
| `x` | Posición X donde se crea (200 en el ejemplo) |
| `y` | Posición Y donde se crea (150) |
| `depth` | La profundidad; se deja en 0 porque luego `depth = -y` la ajusta |
| `obj` | Referencia al objeto a crear (`obj_scarecrow`) |
| `var_struct` | Opcional: *variable definitions* (no se usa aquí) |

Al ejecutar y pulsar espacio, **se crea un espantapájaros en las coordenadas 200, 150**.

> Si sigues pulsando, **visualmente no cambia nada**, pero **se siguen creando**: están
> todos apilados en el mismo sitio.

### Lección de método

> «Cuando pruebas algo nuevo, empieza por el **caso de uso más simple** y ve
> complicándolo a partir de ahí.»

Después, el autor cambia las coordenadas fijas por la posición del jugador, y ya puedes
**ir soltando espantapájaros a tus pies** mientras corres.

---

## 4. Argumentos opcionales entre corchetes

Si pasas el ratón por encima de la función verás la firma, y en la documentación del
fondo verás el último argumento.

> **Regla general de documentación:** si ves **corchetes `[]` alrededor del argumento** de
> una función, significa que es **opcional** y puedes ignorarlo.

(El autor señala que las dos ayudas usan notaciones distintas —corchetes y asterisco— lo
cual resulta algo confuso, pero el significado es el mismo.)

---

## 5. `instance_create_layer()`

Es **casi la misma función**, con una diferencia: en lugar de una **profundidad**, recibe
una **referencia a una capa**.

```gml
if (keyboard_check_pressed(vk_space))
{
    instance_create_layer(x, y, "Instances", obj_scarecrow);
}
```

La capa se puede indicar:

- Por su **nombre** (una cadena, como `"Instances"`).
- Por una **referencia** obtenida al crear capas por código (algo que también se puede
  hacer).

> Ojo: como estamos haciendo `depth = -y`, eso **acaba sobrescribiendo** la profundidad o
> capa con la que se creó la instancia.

---

## 6. Capas: el editor restrige, el runtime no

En el editor de rooms, GameMaker **diferencia** tipos de capa:

- Background layers.
- Tile layers.
- Instance layers.
- (Y las **UI layers**, que el autor describe como «algo nuevo, todavía muy beta y algo
  roto».)

Pero:

> **En tiempo de ejecución, GameMaker no diferencia entre tipos de capa.**

Si seleccionas una capa de baldosas e intentas arrastrar un objeto encima, **GameMaker te
regaña**. Pero **mediante código sí puedes** crear una instancia en una capa de baldosas.

> El autor lo considera **bueno en general**: la restricción del editor dificulta poner
> algo en la capa equivocada y luego no encontrarlo. Pero conviene saber que, por código,
> **todas las capas son básicamente iguales**.

---

## 7. El valor devuelto: una referencia a la instancia

Las dos funciones **devuelven un valor**, y ese valor **no es un número ni una cadena**:
es una **referencia a la instancia creada**.

```gml
var _new_instance = instance_create_layer(x, y, "Instances", obj_scarecrow);
```

---

## 8. Variables locales frente a variables de instancia

La palabra clave **`var`** marca una variable como **local al código que se está
ejecutando**.

| Tipo | Duración |
|---|---|
| **Variable de instancia** | Ligada a una instancia concreta; **sigue existiendo** después de que termine el código que la creó |
| **Variable local (`var`)** | **Deja de existir** en cuanto termina el código que la creó |

> El autor quiere hacer un vídeo específico sobre esta distinción más adelante.

---

## 9. El operador punto

Con la referencia guardada puedes acceder a **las variables de esa instancia** usando el
**operador punto**:

```gml
_new_instance.x              // La X de la instancia creada, no la nuestra
_new_instance.y
_new_instance.sprite_index
```

---

## 10. `hspeed` y `vspeed`

Son variables integradas que **actualizan la posición de la instancia automáticamente**.

```gml
var _new_instance = instance_create_layer(x, y, "Instances", obj_scarecrow);
_new_instance.hspeed = 5;   // Se va disparado hacia la derecha
```

Y por supuesto:

```gml
_new_instance.vspeed = -3;  // Hacia arriba (recordamos: Y negativo es arriba)
```

> **Aviso del autor:** `hspeed` y `vspeed` «no se usan mucho en juegos grandes porque son
> un incordio». En general, **los comportamientos automáticos de GameMaker pueden ser un
> incordio**. Pero para cosas simples funcionan de maravilla.

---

## Puntos clave

1. **`depth = -y`** da ordenación por profundidad correcta en cámaras cenitales. Es la
   línea más famosa de GameMaker.
2. Usa **`keyboard_check_pressed`** para que algo ocurra **una sola vez** por pulsación.
3. **`instance_create_depth(x, y, depth, obj)`** crea en una profundidad concreta.
4. **`instance_create_layer(x, y, "capa", obj)`** crea en una capa concreta.
5. **Los argumentos entre corchetes `[]` son opcionales.**
6. **El editor de rooms restringe los tipos de capa; el runtime no.** Por código puedes
   crear instancias en cualquier capa.
7. Ambas funciones **devuelven una referencia a la instancia** creada.
8. **`var`** crea una variable **local** que muere al terminar el código.
9. El **operador punto** accede a las variables de una instancia concreta.
10. **`hspeed` / `vspeed`** mueven automáticamente; útiles para cosas simples, incómodas
    en proyectos grandes.

---

## Ejercicio propuesto

> **Objetivo:** dominar la creación de instancias y la manipulación del valor devuelto.

**Parte A — Ordenación por profundidad**

1. Crea `obj_scarecrow` con un sprite anclado en **bottom center**.
2. Añade `depth = -y;` en su **Step**.
3. Añade la misma línea al final del **Step** del jugador.
4. Coloca cinco espantapájaros en la room y comprueba que al ponerte delante te dibujan
   encima, y al ponerte detrás, debajo.

**Parte B — Crear por código**

5. En el Step del jugador, añade:
   ```gml
   if (keyboard_check_pressed(vk_space))
   {
       instance_create_depth(200, 150, 0, obj_scarecrow);
   }
   ```
6. Ejecuta y pulsa espacio varias veces **sin moverte**. Explica por qué no ves cambios
   aunque sí se están creando instancias.
7. **Comprueba el error a propósito:** cambia a `keyboard_check` y observa cómo se crean
   decenas por segundo al mantener pulsado. Vuelve a `_pressed`.
8. Cambia las coordenadas fijas por `x, y` y comprueba que sueltas espantapájaros a tus
   pies al correr.

**Parte C — La capa**

9. Sustituye por `instance_create_layer(x, y, "Instances", obj_scarecrow)` y comprueba que
   funciona igual.
10. **Comprueba la restricción del editor:** selecciona una capa de baldosas e intenta
    arrastrar un objeto encima. Lee el aviso. Después hazlo **por código** y comprueba que
    el runtime te lo permite.

**Parte D — El valor devuelto**

11. Guarda la instancia en una variable local:
    ```gml
    var _nuevo = instance_create_layer(x, y, "Instances", obj_scarecrow);
    _nuevo.hspeed = 5;
    ```
12. Comprueba que los espantapájaros salen disparados hacia la derecha.
13. Añade también `_nuevo.vspeed = -3;` y observa la diagonal.
14. Prueba a asignar `_nuevo.sprite_index` a otro sprite y comprueba el cambio.

**Reto extra:** intenta usar la variable local `_nuevo` **en otro evento** (por ejemplo en
el Draw). Comprueba que no existe y lee el error. Explica la diferencia entre variable
local y variable de instancia, y di en qué casos necesitarías guardar la referencia como
variable de instancia en lugar de local.
