# 17 · DragoniteSpam — Autotiles

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 5 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=EVXimiZPo28> |
| **Duración** | 10 min 0 s |
| **Publicado** | 14 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | Ninguno (los autotiles no son accesibles por código) |

Capítulo corto y muy satisfactorio: cómo dejar de colocar a mano cada esquina y cada
borde, y que GameMaker los conecte por ti.

## Índice de contenido

1. El problema: colocar esquinas a mano es tedioso
2. Qué es un sistema de autotiles
3. Dónde se configura: la pestaña *Autotiling*
4. 16 o 47 baldosas
5. Rellenar la plantilla
6. Qué hacer con las piezas que te faltan
7. La última casilla: la baldosa vacía
8. Usar el autotile en el editor de rooms
9. Limitación: no se puede acceder por código
10. Nombres de autotiles: sin restricciones

---

## 1. El problema: colocar esquinas a mano es tedioso

Cuando diseñas un nivel baldosa a baldosa, los **interiores** puedes rellenarlos con el
cubo de pintura y ahorrar tiempo. Pero las **esquinas, los bordes y las uniones** hay que
colocarlos a mano.

> Enseguida se convierte en una tarea tediosa en la que desearías poder seleccionar un
> bloque de baldosas y **pintarlas de golpe con las esquinas y los bordes encajando
> limpiamente**.

Para eso existen los **autotiles**.

---

## 2. Qué es un sistema de autotiles

Un sistema de autotiles permite **especificar una disposición concreta de baldosas**
formada por esquinas, bordes, codos e intersecciones, y crear con ella una **plantilla**.

El resultado: puedes tomar una colección de baldosas y **pintarlas como si fueran una
sola unidad**, y el motor decide automáticamente qué pieza va en cada sitio.

> Los autotiles son **bastante comunes hoy en día**: prácticamente cualquier motor 2D que
> no sea malo trae algo así incorporado.

---

## 3. Dónde se configura: la pestaña *Autotiling*

> **Ojo:** hay que abrir el **tile set**, **no el sprite** del que se construyó.

Dentro del editor del tile set, abre la pestaña **Autotiling**.

---

## 4. 16 o 47 baldosas

GameMaker ofrece dos sistemas:

| Sistema | Cuándo usarlo |
|---|---|
| **16 baldosas** | El **más común**. Cubre esquinas, bordes y codos básicos |
| **47 baldosas** | Si tu tile set tiene un sistema más complicado de **uniones, intersecciones y esquinas** que pueden combinarse de muchas formas |

El autor ha visto usar ambos en juegos reales. Funcionan igual: solo cambia cuántas
piezas tienes que asignar.

---

## 5. Rellenar la plantilla

La plantilla muestra una rejilla con zonas en **dos tonos de gris**:

| Tono | Significado |
|---|---|
| **Gris claro** | La zona **rellena** (por ejemplo, la arena) |
| **Gris oscuro** | La zona **vacía** |

Ejemplos de lo que te pide:

- Una baldosa vertical **rellena a la izquierda y vacía a la derecha**.
- Un **codo** relleno en el suroeste.
- Un **codo** relleno en el sureste.
- Una pieza **recta horizontal** rellena por abajo.
- Un codo relleno en el noroeste…
- Y así con todas.

Para asignarlas, **haz clic en la baldosa correspondiente de tu tile set**. El autor va
rellenando la plantilla pieza a pieza.

---

## 6. Qué hacer con las piezas que te faltan

El pack que usa el autor **no incluye** las dos baldosas diagonales con dos esquinas.

Opciones que plantea:

1. **Dibujarlas tú**, si eres el artista.
2. **Pedírselas** a tu artista.
3. **Editarlas** combinando piezas existentes en Photoshop, Aseprite…
4. Usar la baldosa vacía y **aceptar que quede un hueco** (lo que hace él en el vídeo).

Consecuencia de la opción 4:

> Si intentas disponer baldosas en esa configuración, **aparecerá un hueco**. Y si lo
> rellenas con una baldosa de interior, te pasa lo contrario: **tendrás una zona rellena
> donde no debería haberla**.

Para un juego real, su consejo es claro:

> Contacta con quien hizo el tile set, **págame unos dólares** para que lo complete, o
> ábrelo en un editor y únelo tú mismo. Este pack en concreto parece bastante amigable
> para hacerlo.

---

## 7. La última casilla: la baldosa vacía

La última casilla de la plantilla es **la baldosa vacía por antonomasia**.

> Lo normal es asignarle la **baldosa vacía real** del tile set (la de la esquina superior
> izquierda). Pero puedes rellenarla con otra cosa si quieres.

---

## 8. Usar el autotile en el editor de rooms

1. Vuelve al editor de rooms y selecciona la **capa de baldosas** con la que quieras
   trabajar.
2. Abre la pestaña **Libraries**.
3. Selecciona tu biblioteca de autotiles.

A partir de ahí, **pinta normalmente**: verás que los bordes se rellenan solos.

Puedes darle un nombre pulsando el **icono de lápiz** (o con `F2` / clic derecho →
rename).

Al ejecutar el juego, el resultado es **prácticamente idéntico** al del editor.

---

## 9. Limitación: no se puede acceder por código

> **En GameMaker no puedes acceder a los autotiles mediante código** (al menos en la
> versión actual).

Eso significa que no puedes manipular baldosas sobre la marcha usando el sistema de
autotiles.

Alternativas si lo necesitas:

- **Escribir tu propio sistema** de autotiles en GML, modificando cada baldosa a mano.
  «Eso va a ser mucha matemática, aunque supongo que también podrías usar un gran árbol
  de `if / else`. Hay gente que lo ha hecho.»

El autor confiesa que **le gustaría** que se pudiera acceder por código.

---

## 10. Nombres de autotiles: sin restricciones

Como los autotiles **no son accesibles por código**, su nombre **solo se usa dentro del
IDE**.

> Por eso **no estás limitado** por las reglas de nombrado de assets, variables o
> funciones: puedes poner **espacios** e incluso **dos puntos** en el nombre.

---

## Puntos clave

1. **Los autotiles conectan esquinas y bordes automáticamente**: te ahorran un trabajo
   enorme en el diseño de niveles.
2. Se configuran en la pestaña **Autotiling** del **tile set**, no del sprite.
3. **16 baldosas** para lo normal; **47** para sistemas de uniones más complejos.
4. En la plantilla, **gris claro = relleno** y **gris oscuro = vacío**.
5. Si te faltan piezas, **dibújalas, cómpralas al artista o únelas en un editor**.
6. La última casilla es **la baldosa vacía**.
7. Se usan desde la pestaña **Libraries** de la capa de baldosas.
8. **No se puede acceder a los autotiles por código**; tendrías que escribir tu propio
   sistema.
9. **El nombre del autotile es libre**: admite espacios y dos puntos.

---

## Ejercicio propuesto

> **Objetivo:** configurar un autotile de 16 baldosas y comprobar sus límites.

1. Abre el tile set que creaste en el capítulo anterior y ve a la pestaña
   **Autotiling**.
2. Crea un sistema de **16 baldosas**.
3. Antes de rellenar nada, **identifica en la plantilla** estas cuatro piezas y anótalas:
   vertical rellena a la izquierda, vertical rellena a la derecha, codo noroeste y codo
   sureste.
4. Rellena la plantilla completa asignando cada baldosa de tu tile set.
5. Asigna la última casilla a la **baldosa vacía** real de tu tile set.
6. Dale un nombre con espacios (por ejemplo `Suelo: arena`), para comprobar que el IDE
   lo permite.
7. Vuelve a la room, selecciona la capa de baldosas, abre **Libraries**, elige tu
   autotile y pinta una forma irregular. Comprueba que bordes y esquinas encajan solos.

**Parte de diagnóstico**

8. Dibuja a propósito una configuración que **requiera una pieza que no tengas** y
   observa el hueco. Anota qué pieza te falta.
9. Rellena ese hueco con una baldosa de interior y comprueba el problema inverso: zona
   rellena donde no debería haberla.
10. Soluciónalo de verdad: edita tu hoja de baldosas en un editor externo para crear la
    pieza que falta, y asígnala en la plantilla.

**Reto extra:** crea **un segundo tile set** con autotile de **47 baldosas** usando otra
hoja de tu pack. Compara cuánto más tardas en configurarlo y qué configuraciones
adicionales te permite resolver. ¿Merece la pena para tu juego?
