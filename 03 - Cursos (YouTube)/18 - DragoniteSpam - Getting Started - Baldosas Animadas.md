# 18 · DragoniteSpam — Baldosas animadas

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 6 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=npNY6u65BdI> |
| **Duración** | 17 min 28 s |
| **Publicado** | 17 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | Ninguno (se configura en el editor) |

> «Sinceramente, creo que las baldosas animadas de GameMaker no reciben el cariño que se
> merecen, porque son bastante chulas… y podrían serlo más si no fuera porque GameMaker
> no las ha actualizado en como nueve años.»

## Índice de contenido

1. Preparar el tile set de agua
2. La bendición y la maldición de la baldosa superior izquierda
3. Configurar la animación
4. Velocidad de la animación
5. Truco: animación esporádica rellenando con fotogramas vacíos
6. Truco: desincronizar las animaciones
7. Limitaciones reales
8. Las animaciones también aparecen en la pestaña Libraries
9. Combinar animación con autotiles
10. El botón de *play* del editor de rooms

---

## 1. Preparar el tile set de agua

El pack gratuito de itch.io incluye una colección de **baldosas de agua con cuatro
fotogramas de animación** cada una, en varios patrones: unas solo con burbujas, otras con
un remolino.

1. Arrastra la imagen a GameMaker como sprite: `spr_tiles_water`.
2. Clic derecho → **Create → Tile Set** → `ts_water`.
3. Asígnale el sprite.

---

## 2. La bendición y la maldición de la baldosa superior izquierda

> **Este** tile set **sí** tiene un dibujo en la esquina superior izquierda.

Como vimos en el capítulo 16, GameMaker **siempre** designa esa casilla como **baldosa
nula (vacía)**. Por tanto, ese dibujo **queda inaccesible**.

Es un buen recordatorio: si vas a crear tus propias hojas, **deja esa casilla vacía**.

Opcionalmente puedes configurar un **autotile** para estas baldosas de agua, igual que en
el capítulo anterior.

---

## 3. Configurar la animación

Crea una room nueva (`rm_level2`) y ponla **primera en el orden de rooms** para que sea
la que arranca (se hace desde el desplegable de **Room Manager**, arriba a la derecha del
navegador de recursos: un sitio bastante escondido).

Después, para animar:

1. Abre las propiedades del **tile set** (no del sprite).
2. Ve al apartado **Tile Animation** (en el lateral).
3. Pulsa **Add animation**.
4. Indica el **número de fotogramas**: en este caso **4**.
5. Haz clic, en orden, en los **4 fotogramas** de tu tile set que forman la secuencia.

Ya tienes definida una secuencia de baldosas animadas. El botón de **play** te la
reproduce.

> Lo mejor: **todas las baldosas de esa secuencia que hayas pintado en la room se animan
> automáticamente**, sin tener que hacer nada más.

---

## 4. Velocidad de la animación

Por defecto va a **15 FPS**, que es rápido para animaciones sencillas. El autor prueba 4 y
se queda en **3 FPS**, mucho más adecuado para el agua.

---

## 5. Truco: animación esporádica rellenando con fotogramas vacíos

**Problema:** quieres que el agua esté quieta y que **de vez en cuando** aparezca una
gota, no que gotee sin parar.

**Solución del autor:** amplía la secuencia a **16 fotogramas** y rellena los huecos con
la baldosa «en reposo»:

```
Fotograma:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
Contenido:  ·  ·  ·  ·  G1 G2 G3 G4 ·  ·  ·  ·  ·  ·  ·
             └─ reposo ─┘ └─ gota ─┘ └──── reposo ────┘
```

Donde `·` es la baldosa de agua azul lisa y `G1..G4` son los cuatro fotogramas de la
gota.

> Resultado: la gota aparece, desaparece, y **unos fotogramas después vuelve a aparecer**.
> «Eso es definitivamente más interesante que lo que teníamos antes.»

---

## 6. Truco: desincronizar las animaciones

Con el truco anterior, **todas las baldosas están sincronizadas al mismo fotograma**, lo
que se ve artificial.

No hay una forma integrada de hacerlo, pero sí un atajo:

> **La animación de cada baldosa empieza en el fotograma inicial que colocaste en el
> editor de rooms.**

Así que, si en lugar de colocar siempre el fotograma 1, colocas unas veces el 1, otras el
5, otras el 9… **las animaciones quedan escalonadas** y el efecto es mucho más natural.

---

## 7. Limitaciones reales

El autor es muy honesto con lo que **no** se puede hacer:

| Limitación | Consecuencia |
|---|---|
| No hay **probabilidad** de reproducción | No puedes decir «que se anime el 20 % de las veces» |
| No hay **retardo entre fotogramas** | No puedes espaciar los fotogramas |
| No hay forma integrada de **desincronizar** | Hay que usar el truco del fotograma inicial |
| **No puedes tener velocidades distintas** para distintas animaciones del mismo tile set | Todas van a la misma velocidad |

> Sobre la última: «No estoy del todo seguro de por qué es así. No parece haber un motivo
> técnico, pero es una limitación.»

El autor ha enviado sugerencias de mejora a GameMaker sobre varias de estas cosas, aunque
no espera que lleguen pronto.

---

## 8. Las animaciones también aparecen en la pestaña Libraries

Puedes **dar nombre** a tus animaciones (`ripples`, `animation drop`…) y aparecerán en la
pestaña **Libraries** del editor de rooms, junto a los autotiles.

> El autor reconoce en directo que siempre había seleccionado los fotogramas a mano en el
> tile set, y que tenerlos listados y con nombre en Libraries «probablemente lo hace más
> fácil y debería estar haciéndolo así».

---

## 9. Combinar animación con autotiles

Aquí viene lo interesante: defines un **autotile** con las piezas de costa de tu tile set y
lo pintas… pero **las ondas del borde no se animan**.

> **Solución:** si defines una **animación de baldosas**, esta **se propaga y se aplica
> también cuando usas esas baldosas como parte de un autotile**.

El problema es el coste:

> Hay que repetir el proceso para **cada una de las 16 piezas** de la plantilla del
> autotile. El autor lo hace en el vídeo y confiesa que **le lleva muchísimo tiempo**.

Su sueño: poder seleccionar una región rectangular y decir «crea una animación con este
bloque, el siguiente, el siguiente y el último». GameMaker no lo permite.

---

## 10. El botón de *play* del editor de rooms

> «Hay gente que cree que el botón de *play* del editor de rooms ejecuta el juego y se
> confunde cuando no lo hace.»

- El botón para **ejecutar el juego** está **arriba** (o usa **F5**).
- El botón de *play* del editor de rooms es **Play Animation**: previsualiza las
  animaciones de sprites y de baldosas **sin ejecutar el juego**.

Es fácil pasarlo por alto, pero es muy útil para ver el resultado antes de compilar.

---

## Puntos clave

1. Las **baldosas animadas** se configuran en **Tile Animation**, en el **tile set**.
2. Se define el **número de fotogramas** y se hace clic en ellos **en orden**.
3. **Todas las baldosas pintadas de esa secuencia se animan solas.**
4. **3-4 FPS** suele quedar mejor que los 15 por defecto.
5. **Rellena con fotogramas de reposo** para conseguir animaciones esporádicas.
6. **Coloca distintos fotogramas iniciales** para desincronizar las animaciones.
7. **No hay probabilidades, retardos ni velocidades individuales.**
8. Las animaciones **se pueden nombrar** y aparecen en la pestaña **Libraries**.
9. **La animación se propaga a los autotiles**, pero hay que configurarla pieza a pieza.
10. El botón de *play* del editor de rooms **previsualiza animaciones**, no ejecuta el
    juego.

---

## Ejercicio propuesto

> **Objetivo:** dar vida a un nivel con agua animada, incluyendo efectos esporádicos y
> desincronizados.

1. Importa la hoja de agua de tu pack como `spr_tiles_water`.
2. **Comprueba la trampa:** mírala en el editor. ¿Tiene algo dibujado en la esquina
   superior izquierda? Si es así, ten en cuenta que esa baldosa será inaccesible.
3. Crea el tile set `ts_water` y asígnale el sprite.
4. Crea `rm_level2`, ponla **primera en el Room Manager** y añade una capa de baldosas
   **debajo** de la capa de instancias.
5. Rellena la room entera con el cubo de pintura. Ejecuta y confirma que está **estática**.
6. Ve a **Tile Animation → Add animation**, pon **4 fotogramas** y selecciona los cuatro
   de una secuencia.
7. Baja la velocidad a **3 FPS** y comprueba el resultado con el botón **Play Animation**
   del editor de rooms.

**Parte de trampeo creativo**

8. Crea una **segunda animación de 16 fotogramas**: 4 de reposo, 4 de gota y 8 de reposo.
   Píntala y comprueba que la gota aparece **de vez en cuando**.
9. **Desincrónala:** borra parte de las baldosas y vuelve a pintarlas seleccionando
   distintos fotogramas iniciales de la secuencia. Comprueba que ya no van todas a la vez.
10. Nombra las dos animaciones (`ripples` y `gota`) y búscalas en la pestaña
    **Libraries**.

**Reto extra:** define un **autotile** de costa sobre el mismo tile set y comprueba que
las baldosas de los bordes **heredan la animación**. Cronometra cuánto tardas en animar
las 16 piezas y reflexiona sobre si merece la pena en tu proyecto o si es mejor pintar los
bordes a mano.
