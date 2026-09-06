# 19 · DragoniteSpam — Pinceles de baldosas (tile brushes)

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 7 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=NUT5XXnahu0> |
| **Duración** | 7 min 50 s |
| **Publicado** | 17 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | Ninguno |

Capítulo breve que cierra el bloque de baldosas. El autor lo presenta con humildad:

> «No va a ser una función tan interesante como las dos anteriores, pero creo que puede
> resultar útil de vez en cuando.»

## Índice de contenido

1. El problema que resuelven los pinceles
2. El *Brush Builder*
3. Usar los pinceles desde la pestaña *Brushes*
4. Los pinceles son solo plantillas
5. Pinceles a partir de autotiles
6. Cuándo resultan especialmente útiles
7. Un fallo de GameMaker en directo

---

## 1. El problema que resuelven los pinceles

Si hay un **patrón de baldosas que creas con frecuencia**, lo normal es copiar y pegar:
seleccionas la zona en la room, la copias y la pegas en otro sitio.

Eso funciona, pero obliga a **encontrar una versión ya colocada** en alguna room.

Para eso está el **Brush Builder** (constructor de pinceles).

---

## 2. El *Brush Builder*

Se abre desde las propiedades del **tile set**. Es básicamente **un mini editor de rooms**:

- A la izquierda, las baldosas disponibles para elegir.
- En el centro, **una rejilla** donde vas colocándolas.

Colocas una baldosa, luego otra, y construyes el patrón que quieras.

> No es «datos con los que puedas trabajar en tu juego»: es literalmente **un bloc de
> notas** para pegar trozos de baldosas.

---

## 3. Usar los pinceles desde la pestaña *Brushes*

En el editor de rooms, entre las pestañas **Tiles** y **Libraries**, está **Brushes**.

Al hacer clic en un pincel:

> **Se selecciona automáticamente** toda la región de baldosas que definiste, sin que
> tengas que arrastrar para enmarcarla.

Y ya lo puedes pegar donde quieras.

Ventaja: **te ahorras** tener que localizar una copia anterior del patrón en alguna room y
copiarla: está siempre ahí, a mano.

---

## 4. Los pinceles son solo plantillas

> «Como los patrones de los pinceles no son nada real, aparte de una plantilla de copiar y
> pegar…»

Consecuencia tranquilizadora:

> **Si borras un pincel, las baldosas que ya pegaste con él siguen en la room.** No se
> pierde ningún dato asociado, porque el pincel nunca fue más que una plantilla.

---

## 5. Pinceles a partir de autotiles

También puedes construir un pincel **pintando con tu sistema de autotiles** dentro del
Brush Builder, y luego pegarlo como pincel en la room.

> Aquí el autor se encuentra con un **fallo de GameMaker en directo**: intenta seleccionar
> el autotile y no aparece («GameMaker, ¿por qué te comportas de forma rara?»). Tras
> investigar, sospecha que tiene que ver con tenerlo seleccionado en el editor de rooms, y
> acaba funcionando. Lo reporta como bug nada más terminar de grabar.

---

## 6. Cuándo resultan especialmente útiles

Los pinceles brillan en dos situaciones:

### A) Decoraciones que ocupan varias baldosas

Si tu tile set tiene una decoración que se extiende por **varias baldosas individuales**
(por ejemplo, una rejilla de 5 × 5 que forma un muro), puedes crear un pincel con toda la
rejilla en vez de colocarlas una a una.

### B) Patrones formados por baldosas NO adyacentes

Esto es lo más valioso:

> Si quieres construir un patrón con baldosas que **no están juntas en el tile set**, no
> puedes simplemente hacer una selección rectangular en el editor. **Un pincel sí te lo
> permite.**

---

## 7. Un fallo de GameMaker en directo

Vale la pena quedarse con la actitud del autor ante el fallo:

1. Lo detecta («¿por qué no aparece?»).
2. Lo aísla sospechando la causa.
3. **Lo reporta** en cuanto termina de grabar.

Y lo hace delante de la cámara, sin cortar el vídeo.

---

## Puntos clave

1. Un **pincel** es una **plantilla de copiar y pegar** de baldosas, guardada en el tile
   set.
2. Se construye en el **Brush Builder**, que funciona como un mini editor de rooms.
3. Se usa desde la pestaña **Brushes** del editor de rooms: **selecciona la región
   automáticamente**.
4. **Borrar un pincel no afecta** a lo que ya pegaste.
5. Puedes crear pinceles **a partir de autotiles**.
6. Son especialmente útiles para **decoraciones de varias baldosas** y para **patrones con
   baldosas no adyacentes**.
7. **No son datos del juego**: solo una comodidad de edición.

---

## Ejercicio propuesto

> **Objetivo:** crear una pequeña biblioteca de pinceles reutilizables.

1. Abre el tile set que quieras y ve al **Brush Builder**.
2. Crea un primer pincel sencillo: un cuadrado de 2 × 2 con dos baldosas distintas.
3. Vuelve al editor de rooms, abre la pestaña **Brushes** y comprueba que al hacer clic se
   **selecciona la región completa** sin arrastrar.
4. Pégalo en cuatro sitios distintos de la room.

**Parte de patrones complejos**

5. Busca en tu tile set una decoración que ocupe **varias baldosas** (un muro, una
   fuente, un edificio) y crea un pincel con ella entera.
6. Ahora crea un pincel con baldosas **que no estén contiguas en la hoja**: elige tres
   baldosas separadas y compón un patrón. Comprueba que esto **no** se podría hacer con
   una selección rectangular.

**Parte de verificación**

7. **Prueba a borrar un pincel** que ya hayas usado. Comprueba que las baldosas pegadas
   siguen en su sitio y explica por qué.
8. Nombra tus pinceles de forma descriptiva y haz una lista de los cinco patrones que más
   repites en tu nivel: esos son los que merecen un pincel.

**Reto extra:** intenta crear un pincel **pintando con un autotile** dentro del Brush
Builder. Si GameMaker te da problemas con la selección, prueba a cambiar de pestaña o a
deseleccionar en la room, como hace el autor. Documenta el comportamiento: reconocer un
bug y aislarlo es una habilidad tan importante como escribir código.
