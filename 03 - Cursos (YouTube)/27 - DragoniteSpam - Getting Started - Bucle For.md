# 27 · DragoniteSpam — El bucle `for`

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 15 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=CQhjPYyraWU> |
| **Duración** | 10 min 23 s |
| **Publicado** | 4 de abril de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `for` |

El bucle `for` está **a medio camino** entre `repeat` y `while`: es la forma más popular de
escribir un bucle.

## Índice de contenido

1. De `while` a `for`
2. Las tres partes del `for`
3. El `for` es puro azúcar sintáctico
4. La tradición de llamar `i` al contador
5. Usar el contador para crear patrones
6. Ecuaciones paramétricas
7. Las tres partes admiten lo que quieras
8. El mito: «los `for` son lentos en GameMaker»

---

## 1. De `while` a `for`

Un bucle finito escrito con `while` necesita **tres cosas separadas**:

```gml
var _max_scarecrows = 10;
var _current_scarecrows = 0;

while (_current_scarecrows < _max_scarecrows)
{
    // …generar espantapájaros…

    _current_scarecrows++;
}
```

Es decir:

1. Definir el **número máximo de iteraciones**.
2. Definir e inicializar el **contador del bucle**.
3. **Incrementar** el contador al final de cada vuelta.

Cuando el contador alcanza el máximo, la condición deja de cumplirse y el bucle termina.

---

## 2. Las tres partes del `for`

El `for` **contrae** esas tres cosas en una sola línea:

```gml
for (var i = 0; i < _max_scarecrows; i++)
{
    // …generar espantapájaros…
}
```

| Parte | Código | Cuándo se ejecuta |
|---|---|---|
| **Condición de inicialización** | `var i = 0` | **Antes** de que el bucle empiece |
| **Condición de actualización** | `i < _max_scarecrows` | Se comprueba **en cada vuelta**; si es falsa, el bucle termina |
| **Sentencia final** | `i++` | **Al final** de cada vuelta |

Es básicamente lo mismo que el `while`, pero **todo en la misma línea**.

---

## 3. El `for` es puro azúcar sintáctico

> **El bucle `for` no ofrece nada nuevo respecto a `while`.** Solo es algo más cómodo de
> montar, porque la mayoría de los bucles de un programa tienen precisamente esta forma.

---

## 4. La tradición de llamar `i` al contador

Verás esto constantemente:

```gml
for (var i = 0; i < 10; i++)
```

Usar la letra **`i`** es una **abreviatura que todo el mundo acepta**:

- `i` puede significar **index** (índice).
- Puede significar **integer** (entero).
- Puede significar lo que quieras.

> Lo importante es que **cuando veas un bucle con una variable `i`, sabrás automáticamente
> que es el contador del bucle**.

Es especialmente común al recorrer **listas o arrays** (algo que la serie aún no ha visto).

---

## 5. Usar el contador para crear patrones

Hasta ahora no hacíamos nada con el contador. Pero puedes usarlo, y eso abre un mundo de
posibilidades muy «de videojuego».

### Una línea horizontal

```gml
for (var i = 0; i < 10; i++)
{
    instance_create_layer(x + 15 * i, y, "Instances", obj_scarecrow);
}
```

Razonamiento línea a línea:

- `i = 0` → el primero se genera en `x + 15 × 0` = **encima del jugador**.
- `i = 1` → el segundo en `x + 15 × 1` = 15 píxeles a la derecha.
- `i = 2` → el tercero en `x + 15 × 2` = 30 píxeles…
- Y así sucesivamente: **una fila perfectamente espaciada**.

### Una diagonal

```gml
for (var i = 0; i < 10; i++)
{
    instance_create_layer(x + 15 * i, y - 15 * i, "Instances", obj_scarecrow);
}
```

> **Ejercicio mental del autor:** antes de ejecutarlo, intenta predecir el resultado.
> Produce **una línea diagonal apuntando arriba y a la derecha**.

---

## 6. Ecuaciones paramétricas

> Si recuerdas las **ecuaciones paramétricas** del instituto, esto es exactamente eso: hemos
> creado una ecuación paramétrica que dicta la posición X e Y de cada espantapájaros.

Y con un contador de bucle es facilísimo.

Un paso más: si quisieras generar los espantapájaros **en un anillo**, usarías
**ángulos y trigonometría** para calcular X e Y, en vez de avanzar linealmente.

---

## 7. Las tres partes admiten lo que quieras

Que lo normal sea `i = 0`, `i < n`, `i++` **no significa que sea obligatorio**.

Puedes poner lo que quieras en las tres partes:

```gml
for (var i = 100; i < 200; i += 10)   // Empieza en 100, de 10 en 10
```

Eso sí:

> Es **debatible lo útil** que suele ser. Y existe código muy «maldito» por ahí que hace
> cosas rarísimas con la condición de actualización.
>
> «Si ves algo súper raro así, ten por seguro que **no significa que tú debas escribir tu
> código de esa forma**.»

---

## 8. El mito: «los `for` son lentos en GameMaker»

El autor se ve obligado a desmentirlo:

> En internet verás gente acusando a los bucles `for` de GameMaker de ser **lentos**.
> **En su mayor parte, eso no es verdad.**

Los motivos que dan son complicados, y casi siempre fruto de **malinterpretar o
tergiversar** lo que ocurre en el resto de su código.

> Si estás empezando, **no deberías preocuparte por esto**. Preocúpate por aprender qué hace
> cada pieza.
>
> «Si ves a alguien diciendo que los bucles de GameMaker son lentos, dile que se quede
> después de clase.»

---

## Puntos clave

1. **`for (inicialización; condición; incremento)`** contrae el patrón del `while` en una
   línea.
2. Las tres partes: **antes del bucle**, **comprobación en cada vuelta**, **final de cada
   vuelta**.
3. **El `for` no aporta nada nuevo**: es pura comodidad.
4. **Usar `i` como contador es la tradición** aceptada por todos.
5. **El contador sirve para crear patrones**: filas, diagonales, anillos.
6. Eso es, en el fondo, una **ecuación paramétrica**.
7. Las tres partes admiten cualquier código, pero lo normal es la forma clásica.
8. **Los `for` de GameMaker NO son lentos**: es un mito de internet.

---

## Ejercicio propuesto

> **Objetivo:** usar el contador del bucle para generar patrones, y practicar la predicción
> de código.

1. Escribe primero el bucle finito con `while` (máximo, contador, incremento) y verifica que
   genera 10 espantapájaros.
2. Reescríbelo como `for` en una sola línea. Comprueba que el resultado es idéntico.
3. Cambia el nombre del contador a `i` y comprueba que sigue funcionando.

**Parte de patrones**

4. Genera una **fila horizontal** con `x + 15 * i`.
5. Genera una **diagonal** con `x + 15 * i` e `y - 15 * i`.
6. Antes de ejecutar cada uno, **escribe qué patrón esperas**. Después compruébalo y anota
   si acertaste.

**Parte de creatividad**

7. Genera una **columna vertical** (mismo X, Y variable).
8. Genera un **cuadrado**: cuatro bucles, uno por lado (o piensa cómo hacerlo con las
   matemáticas del contador).
9. **Reto:** genera un **anillo** usando trigonometría. Para 12 espantapájaros en círculo:
   ```gml
   var _radio = 60;
   for (var i = 0; i < 12; i++)
   {
       var _angulo = (360 / 12) * i;
       var _xx = x + lengthdir_x(_radio, _angulo);
       var _yy = y + lengthdir_y(_radio, _angulo);
       instance_create_layer(_xx, _yy, "Instances", obj_scarecrow);
   }
   ```
   Comprueba el resultado y explica por qué aquí sí hace falta trigonometría.

**Reto extra:** escribe a propósito un `for` «maldito» que funcione pero sea ilegible (por
ejemplo, modificando la variable de la condición dentro del cuerpo del bucle). Después
reescríbelo de forma clara. Compara ambos y explica por qué el autor insiste en que el
código raro **no** es mejor código.
