# 02 · Objetos, sprites y rooms

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 2 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=0LlKlja0d3E> |
| **Duración** | 20 min 6 s |
| **Publicado** | 22 de enero de 2026 |
| **Nivel** | Principiante absoluto |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `room_goto()` |

## Índice de contenido

1. El editor de rooms: navegación y rejilla
2. Convención de nombres para los recursos
3. Elegir la resolución: 480 × 270
4. Los grupos Objects y Sprites
5. Crear el sprite del jugador (`sPlayer`)
6. El origen del sprite
7. Crear el objeto del jugador (`oPlayer`)
8. Colocar instancias: `Alt` y `Shift`
9. Objeto frente a instancia
10. El tamaño de la ventana y la room de arranque (`rSplash`)
11. Creation code y tu primera línea de GML
12. Funciones, argumentos y la ayuda contextual

---

## 1. El editor de rooms: navegación y rejilla

Al hacer doble clic en una room se abre el **editor de rooms** en una pestaña nueva.
Puedes volver al espacio de trabajo pulsando la pestaña correspondiente.

El autor cierra el panel auxiliar (dock) que aparece a un lado para tener la vista
despejada.

### Atajos de navegación

| Acción | Cómo se hace |
|---|---|
| Desplazar la vista | **Clic central** (rueda) y arrastrar |
| Zoom rápido | **`Ctrl` + rueda del ratón** |
| Volver a encuadrar | Botón **Center Fit** |

> El zoom con `Ctrl` + rueda es uno de esos atajos que acabarás usando sin pensar,
> en lugar de los botones de la interfaz.

### La rejilla (grid)

Junto a los botones de zoom hay un icono para **activar y desactivar la rejilla**.
Su menú desplegable permite ajustar:

- El **color** de la rejilla.
- El **tamaño** de celda.
- Si los objetos se **imantan a las intersecciones** de la rejilla.
- El **brillo** de la rejilla.

---

## 2. Convención de nombres para los recursos

El autor usa un sistema que tomó prestado de **Sara Spalding** (canal de YouTube):

```
<minúscula><Mayúscula><resto>
```

Es decir, **una letra minúscula inicial que indica el tipo de recurso**, seguida del
nombre en PascalCase:

| Prefijo | Tipo de recurso | Ejemplo |
|---|---|---|
| `r` | Room | `rGame` |
| `s` | Sprite | `sPlayer` |
| `o` | Object | `oPlayer` |
| *(y así con sonidos, fuentes…)* | | |

La ventaja: **con solo mirar el nombre sabes si el recurso está en el grupo
correcto**. Si arrastras algo por error a otra carpeta, el prefijo te lo delata al
instante.

Para renombrar: **clic derecho → Rename** o selecciona y pulsa **`F2`**. A partir de
ahora, cuando el autor diga «renombra», usa `F2`.

---

## 3. Elegir la resolución: 480 × 270

Por defecto la room mide **1366 × 768** píxeles. El autor la cambia a:

```
Ancho:  480
Alto:   270
```

### ¿Por qué una resolución tan pequeña?

- Si estás empezando, **no tiene sentido trabajar en una resolución enorme**: crear
  arte para ella exige órdenes de magnitud más esfuerzo.
- **480 × 270 escala perfectamente a 1080p y a 4K** (exactamente ×4 y ×2 en cada
  eje, respectivamente).

El autor lo demuestra con su propio juego publicado en Steam, *Snapshot Spirit
Live!*, que es **literalmente un juego de 480 × 270 píxeles** y se ve perfecto tanto
en monitores 4K como en 1080p.

Si quieres un aspecto aún más «crujiente», puedes ir a la mitad:

```
240 × 135
```

> Empieza tu andadura con resoluciones pequeñas. 480 × 270 es, en palabras del
> autor, una resolución «mágica».

### Si GameMaker se vuelve lento

Si el programa empieza a ir pesado (por ejemplo, abrir una room tarda una eternidad)
es porque se está quedando sin memoria. Solución:

> **Cierra GameMaker y vuelve a abrirlo.** Eso libera toda la memoria que el programa
> estaba usando.

---

## 4. Los grupos Objects y Sprites

Creamos dos grupos nuevos en la biblioteca de recursos:

- **`Objects`** — cosas del juego que **pueden ejecutar código**.
- **`Sprites`** — elementos **visuales** que precargas en el juego.

Para crear un recurso directamente dentro de un grupo (y que no acabe suelto):

```
Clic derecho en el grupo → Create → Sprite / Object / …
```

---

## 5. Crear el sprite del jugador (`sPlayer`)

```
Clic derecho en Sprites → Create → Sprite → renombrar a sPlayer
```

Configuración:

1. **Tamaño:** botón **Resize Sprite** → pestaña **Resize Canvas** → **40 × 40**
   píxeles → **Apply**.
2. **FPS:** ponerlo a **0**. Es la velocidad de animación si el sprite tuviera
   varios fotogramas; con un solo fotograma no importa.
3. **Origen (origin):** cambiarlo a **Middle Center**.
4. **Relleno:** botón **Edit Image** → herramienta **cubo de pintura (bucket fill)**
   → elegir un color sólido.

El autor añade además un **borde** y una **crucecita** con el pincel o la herramienta
de línea para distinguir mejor la posición del sprite. Es opcional.

> **No hace falta que parezca arte de verdad.** Cuando prototipas, trabaja con
> **formas básicas** para entender cómo funcionan las mecánicas y el movimiento, y
> sustitúyelas por arte real más adelante. Ahora mismo solo necesitamos un cuadrado.

---

## 6. El origen del sprite

El **origen** es la pequeña cruz que marca el punto de anclaje del sprite.

Cuando asignas un sprite a un objeto y colocas ese objeto en la room, **las
coordenadas `x` e `y` de la instancia corresponden al origen**, y el resto del sprite
se dibuja en relación con él.

- Origen **Top Left** → `x`/`y` señalan la esquina superior izquierda.
- Origen **Middle Center** → `x`/`y` señalan el centro.

Se nota muchísimo al colocar objetos con la rejilla activada: con origen *Middle
Center*, el **centro** del objeto se imanta a las intersecciones; con *Top Left*, se
imanta la **esquina**.

Para el jugador usamos **Middle Center** (más adelante se verá por qué).

---

## 7. Crear el objeto del jugador (`oPlayer`)

```
Clic derecho en Objects → Create → Object → renombrar a oPlayer
```

En el objeto, haz clic donde pone **No Sprite** y selecciona `sPlayer`.

Ahora arrastra `oPlayer` desde la biblioteca hasta la room. Ya tienes algo en
pantalla.

---

## 8. Colocar instancias: `Alt` y `Shift`

Con un objeto seleccionado en la room:

- **`Alt` + arrastrar:** «pintas» con el objeto. El sprite sigue al ratón y cada clic
  coloca una instancia nueva.
- **`Shift` + arrastrar:** selección múltiple enmarcando un área.
- **`Supr`:** borra lo seleccionado.
- **`Ctrl + Z`:** deshace.

Si ajustas la rejilla a **20 × 20** (la mitad del sprite de 40 × 40), al pintar con
`Alt` los bloques se alinean de forma perfecta y continua.

> Recuerda: si estás en un portátil con **Laptop Mode** activado, muchos de estos
> atajos no funcionarán. Desactívalo.

---

## 9. Objeto frente a instancia

Distinción fundamental:

- El **objeto** es la plantilla. Vive en la biblioteca de recursos.
- Las **instancias** son las copias que colocas en las rooms.

Analogía del autor:

> Imagina que el objeto es una **palabra del diccionario** y la room es tu **libro**.
> Puedes usar esa palabra tantas veces como quieras en la historia.

Hay **un** objeto `oPlayer`, pero puedes poner **tantas instancias** como quieras. Es
como los Goombas de Mario: existe un objeto Goomba, y puedes llenar el nivel de
Goombas.

### El hábito de ejecutar constantemente

> Cada vez que añadas o cambies algo, **ejecuta el juego** para comprobar que no has
> introducido un error. El 99,9 % de los fallos son tuyos, no de GameMaker.

---

## 10. El tamaño de la ventana y la room de arranque (`rSplash`)

Regla importante de GameMaker:

> **La primera room que se carga determina el tamaño de la ventana del juego.**

Como queremos que el juego se vea más grande (el doble), creamos una room de
arranque:

```
Clic derecho en Rooms → Create → Room → renombrar a rSplash
```

Para que sea la primera:

1. Observa el icono de **casita** junto a una room: marca cuál se carga primero.
2. Haz clic en la casita (o junto a `rSplash`) para abrir el **Room Manager**.
3. En **Room Order**, arrastra `rSplash` hasta la **parte superior**.

Ahora configura `rSplash` a **960 × 540**, exactamente el doble de 480 × 270.

Al ejecutar, verás que `rSplash` fija el tamaño de la ventana y después el resto del
juego se estira hasta esa medida.

---

## 11. Creation code y tu primera línea de GML

El **Creation Code** de una room es código que se ejecuta **una única vez**, justo
cuando la room entra en existencia.

Al abrirlo por primera vez, GameMaker pregunta si quieres usar:

- **GML Visual** (arrastrar y soltar), o
- **GML Code**.

> **No uses el sistema visual.** Limita el tipo de juegos que puedes hacer. GML es lo
> bastante sencillo para que cualquiera lo aprenda. Marca «Don't ask again for this
> project» y elige **GML Code**.

Y esta es tu primera línea:

```gml
room_goto(rGame);
```

Qué hace, pieza a pieza:

| Parte | Significado |
|---|---|
| `room_goto` | Una **función** (una herramienta que hace algo) |
| `(rGame)` | El **argumento**: la información que le pasas a la herramienta |
| `;` | El punto y coma que **termina el comando** |

El punto y coma es opcional en la práctica (GameMaker lo tolera), pero **siempre
deberías ponerlo**: marca claramente el final de una instrucción.

Resultado: en el instante en que `rSplash` existe, salta inmediatamente a `rGame`.
No llegas a ver la pantalla de arranque, pero la ventana ya tiene el tamaño correcto.

> El autor recomienda **tener siempre una room `rSplash`** en todos tus proyectos:
> es el lugar garantizado donde ejecutar código antes de que cargue el resto del
> juego.

---

## 12. Funciones, argumentos y la ayuda contextual

Repasemos los conceptos:

- **Función:** una herramienta que hace algo (`room_goto`).
- **Argumento:** la información que le das entre paréntesis (`rGame`).

Y el atajo más valioso de todo GameMaker:

> **Cualquier cosa que aparezca en color dentro del código se puede pulsar con el
> botón central del ratón** para abrir su página en la documentación.

Al hacerlo verás qué hace la función, sus limitaciones, qué argumentos necesita,
enlaces relacionados y un **ejemplo de uso**.

---

## Puntos clave

1. **`Ctrl` + rueda** para zoom rápido; **clic central + arrastrar** para desplazarte.
2. **Nombra con prefijo minúsculo:** `rGame`, `sPlayer`, `oPlayer`. El prefijo te
   dice el tipo de un vistazo.
3. **Trabaja a 480 × 270.** Escala limpia a 1080p y 4K y te ahorra una cantidad
   brutal de trabajo artístico.
4. **Origen del sprite = punto de anclaje.** `Middle Center` para el jugador.
5. **Prototipa con formas simples**; el arte viene después.
6. **`Alt` + arrastrar** pinta instancias; **`Shift` + arrastrar** selecciona en
   bloque.
7. **Un objeto, muchas instancias.**
8. **Ejecuta el juego a cada cambio.** El 99,9 % de los bugs son tuyos.
9. **La primera room que carga fija el tamaño de la ventana.** Usa una `rSplash` a
   960 × 540.
10. **Usa GML Code, no GML Visual.**
11. **Clic central sobre el código de color** abre la ayuda de esa función.

---

## Ejercicio propuesto

> **Objetivo:** montar un proyecto de 480 × 270 con dos habitaciones y un salto
> automático entre ellas.

1. Crea un proyecto nuevo siguiendo la convención `Practica Rooms <AAMMDD> V1`.
2. Renombra `Room1` a `rGame` y ponla a **480 × 270**.
3. Crea los grupos `Sprites`, `Objects` y `Rooms` (y mueve `rGame` dentro de
   `Rooms`).
4. Crea el sprite `sPlayer` de **32 × 32**, FPS 0, origen **Middle Center**,
   relleno de color sólido. Añádele un borde de otro color para distinguirlo.
5. Crea el objeto `oPlayer`, asígnale `sPlayer` y coloca **una** instancia en el
   centro de `rGame`.
6. Crea `rSplash` a **960 × 540** y ponla primera en el **Room Order**.
7. Abre el **Creation Code** de `rSplash`, elige GML Code y escribe:

   ```gml
   // La primera habitación fija el tamaño de la ventana;
   // en cuanto existe, saltamos al juego real.
   room_goto(rGame);
   ```

8. Ejecuta. Comprueba que la ventana es grande y que ves al jugador en el centro.
9. Practica la documentación: haz **clic central sobre `room_goto`** y lee la
   entrada completa en el manual. Fíjate en el ejemplo que incluye.
10. Vuelve a `rGame`, activa la rejilla de **16 × 16** y practica pintar con `Alt`,
    seleccionar con `Shift` y borrar con `Supr`. Después deja una sola instancia.
11. Exporta tu YYZ de respaldo.

**Reto extra:** crea una tercera room `rFinal` de 480 × 270 y haz que `rGame` lleve a
ella en su Creation Code con `room_goto(rFinal)`. Comprueba qué tamaño de ventana
resulta y explica por qué.
