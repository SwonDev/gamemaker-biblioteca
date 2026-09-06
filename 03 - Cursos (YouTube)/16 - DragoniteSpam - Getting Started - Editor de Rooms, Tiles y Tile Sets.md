# 16 · DragoniteSpam — El editor de rooms: tiles, tile sets y capas de sprites

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 4 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=kyFICZcm6Vo> |
| **Duración** | 19 min 12 s |
| **Publicado** | 20 de diciembre de 2025 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | Ninguno (trabajo en el editor) |

Capítulo dedicado a **decorar niveles**: cómo convertir un sprite en un conjunto de
baldosas, pintar con él en el editor de rooms y decidir **cuándo usar una instancia y
cuándo basta con un sprite**.

## Índice de contenido

1. Importar la hoja de baldosas
2. Por qué no vale arrastrar el sprite a la room
3. Crear un tile set
4. Propiedades del tile set
5. *Output border*: por qué no ponerlo a cero
6. *Disable source sprite export* y las colisiones
7. Crear una capa de baldosas
8. Herramientas de pintado
9. La baldosa vacía está siempre arriba a la izquierda
10. El orden de las capas importa
11. Varias capas de baldosas
12. Capas de assets para props
13. Propiedades de un sprite en una capa de assets
14. Instancias frente a sprites: cuándo usar cada uno

---

## 1. Importar la hoja de baldosas

El autor usa el mismo pack de **itch.io** del capítulo anterior: una colección gratuita
que, por lo que se ve, **fue hecha por un artista de verdad** y no «escupida por
generación automática» (algo que a mucha gente del sector creativo le importa).

Dentro del pack hay una carpeta `environment` con carpetas de tile sets. Elige
**floor tiles** y la arrastra a GameMaker.

> Al importar, GameMaker avisa de que **importar archivos como sprite no es una acción
> que se pueda deshacer**. Si el mensaje te molesta, puedes suprimirlo
> permanentemente marcando la casilla.

**No** le pone el sufijo `_strip15`: esta vez quiere la imagen tal cual. La llama
`spr_tiles_floor`.

---

## 2. Por qué no vale arrastrar el sprite a la room

Si intentas arrastrar el sprite al editor de rooms estando en una **capa de instancias**,
**GameMaker no te deja**: el editor de rooms **no permite mezclar tipos de assets en una
misma capa**.

Te ofrecerá crear una **capa de assets** nueva, donde puedes soltar sprites en vez de
instancias de objetos. Pero:

> Suelta **el sprite entero como una única entidad**. Puedes moverlo, pero **no puedes
> pintar con las baldosas** que contiene.

(Nota curiosa: **mediante código** sí puedes asignar distintos tipos de asset a una capa;
es el editor de rooms el que no lo permite, por organización.)

---

## 3. Crear un tile set

```
Clic derecho en el navegador de recursos → Create → Tile Set  (casi al final de la lista)
```

Un **tile set** se puede entender como **un tipo especial de sprite**, o una extensión de
los sprites, **que permite usar ese sprite como baldosas** en el editor de rooms.

Para asignarle el sprite:

- Haz clic en el selector y elige el sprite, o
- **arrastra el sprite** desde el navegador de recursos hasta el editor del tile set.

Al hacerlo, aparecen **líneas de cuadrícula** sobre el sprite: acabas de trocearlo en una
**colección de baldosas**.

---

## 4. Propiedades del tile set

| Propiedad | Qué hace |
|---|---|
| **Tile size** | El tamaño de cada baldosa |
| **Offset** | Desplazamiento horizontal o vertical |
| **Spacing** | Espacio o relleno entre baldosas, si tu hoja lo tiene |

El autor lo deja todo a cero para este ejemplo.

---

## 5. *Output border*: por qué no ponerlo a cero

Abajo verás **Output Border X e Y**.

> Por defecto valen **2**. **Déjalos así.**

Si los pones a cero, **bajo ciertas condiciones aparecen costuras visibles** (*seams*)
entre las baldosas, que casi seguro que no quieres.

---

## 6. *Disable source sprite export* y las colisiones

Esta opción viene **desmarcada** por defecto.

- **Si vas a usar el tile set con colisiones**, debe seguir **desmarcada**. Desactivar la
  exportación del sprite original **hace que las colisiones no funcionen**.
- Si **no** vas a usar colisiones en esas baldosas, puedes marcarla: GameMaker
  descartará la información del sprite que no necesita en tiempo de ejecución.

También está el **texture group**, análogo a los ajustes de textura de los sprites.

### Funciones avanzadas (con vídeo propio)

El editor de tile sets tiene tres apartados avanzados que el autor **no toca aquí**:
**brush builder**, **tile animation** y **autotiling**.

---

## 7. Crear una capa de baldosas

En el editor de rooms, pulsa el icono **`+`** para añadir capas.

> Si has visto material antiguo de GameMaker, verás los iconos alineados en el inspector
> de la room. Hoy están **escondidos dentro de ese menú** porque se han añadido más tipos
> de capa y ya no cabe todo.

Elige **Tile Layer**, llámala `tiles_floor` y asígnale el tile set (haciendo clic o
arrastrando desde el navegador de recursos).

---

## 8. Herramientas de pintado

| Herramienta | Uso |
|---|---|
| **Pincel** | Pintar baldosa a baldosa con el ratón |
| **Rectángulo** | Pintar un rectángulo entero de golpe |
| **Cubo de pintura** (*flood fill*) | Rellenar **toda** la rejilla de baldosas de la room |
| **Voltear / rotar** | Girar o reflejar baldosas |
| **Borrador** | Borrar una región rectangular |

> Para un suelo entero, pintar a mano se hace pesado enseguida: usa el **rectángulo** o el
> **cubo de pintura**.

También puedes seleccionar baldosas y usar `Ctrl + X` / `Ctrl + V` para copiarlas y
pegarlas como pinceles.

---

## 9. La baldosa vacía está siempre arriba a la izquierda

> **En todos los tile sets, la baldosa de la esquina superior izquierda es
> automáticamente la baldosa vacía (*null tile*)**, aunque en tu sprite haya dibujada
> otra cosa.

A mucha gente esto le resulta contraintuitivo. Consecuencia práctica:

> Si en tu hoja de baldosas **tienes algo importante en esa primera casilla**, muévelo a
> otra posición de la imagen.

---

## 10. El orden de las capas importa

Al pintar el suelo, el personaje **desaparece debajo de las baldosas**.

La causa: la capa `tiles_floor` está **por encima** de la capa de instancias, y las capas
**se apilan de arriba abajo**: lo que está arriba se dibuja encima.

- Un **suelo** debe estar **debajo** del jugador.
- Una capa de **primer plano** de baldosas sí puede ir encima.

---

## 11. Varias capas de baldosas

Si pintas hierba directamente sobre la arena, **la estás sobrescribiendo**. La solución es
crear **otra capa de baldosas**:

1. Crea `tiles_grass`.
2. Asígnale el tile set de suelo.
3. Pinta un cuadrado de hierba sobre la arena.

Al ser capas separadas no se pisan: tienes un **sustrato** de arena y una **capa
superficial** de hierba.

> Puedes crear **tantas capas como quieras** y apilarlas en el orden que necesites.

### Un detalle sobre la escala

El personaje está escalado ×4, pero **las capas de baldosas no tienen propiedad de
escala**. El resultado se ve raro.

> El autor lo repite: este es justo el momento en el que deberías usar una solución de
> **cámara y viewport** en lugar de escalar cada objeto.

---

## 12. Capas de assets para props

Los props (rocas, herramientas, árboles, arbustos) vienen como **sprites separados dentro
de una hoja**. El autor la importa y la trocea con el editor:

```
Edit Image → Convert to Frames
  Number of frames:      6
  Frames per row:        3
  Frame width:          64
  Frame height:        144
```

Después crea una **capa de assets** y arrastra los árboles por la room.

> «Esto sí es un uso mucho más útil de las capas de assets que arrastrar el sprite del
> suelo entero, que era una tontería.»

---

## 13. Propiedades de un sprite en una capa de assets

Al seleccionar un sprite de una capa de assets, en la **parte inferior izquierda** del
editor de rooms puedes ajustar:

| Propiedad | Notas |
|---|---|
| **Position** | Posición |
| **Scale** | Escala (también arrastrando los tiradores) |
| **Rotate** | Rotación |
| **Flip / mirror** | Reflejar; invierte el `image_xscale` o `image_yscale` |
| **Animation speed** | ⚠️ **Se animan por defecto**: ponlo a 0 si no quieres |
| **Image frame** | El fotograma concreto a mostrar |

> El autor echa de menos una **tira visual de fotogramas** donde hacer clic en el que
> quieres, en vez de escribir el número. Lo apunta como posible sugerencia de mejora.

Muchas de estas propiedades **también se pueden fijar en instancias** dentro de una room,
algo que no se había comentado en los vídeos anteriores.

---

## 14. Instancias frente a sprites: cuándo usar cada uno

Esta es la regla de oro del capítulo:

> **Por convención, lo que necesite interacción, colisión o comportamientos debe ser una
> instancia. Lo que esté ahí solo por motivos visuales puede ser un sprite en una capa de
> assets.**

Razones para preferir sprites en capas de assets:

- Son **más fáciles de trabajar** al diseñar niveles: tienen «menos piezas móviles».
- GameMaker **las dibuja algo más eficientemente** que las instancias.

Ejemplos concretos:

| Situación | Elige |
|---|---|
| Mil árboles, arbustos o hierbas **puramente decorativos** | **Sprite** en capa de assets |
| Un árbol que **puedes talar** | **Instancia** |
| Un arbusto del que **puedes recolectar** | **Instancia** |

---

## Puntos clave

1. **Un tile set es un sprite especial** que se puede usar como baldosas en el editor.
2. **El editor de rooms no permite mezclar tipos de asset en una capa.**
3. **Deja *Output Border* en 2**: a cero aparecen costuras entre baldosas.
4. **Si vas a usar colisiones con el tile set, deja *Disable source sprite export*
   desmarcado.**
5. **La baldosa superior izquierda es siempre la vacía**: no pongas nada importante ahí.
6. Usa el **rectángulo** o el **cubo de pintura** para superficies grandes.
7. **Las capas se apilan de arriba abajo**: el suelo va debajo del jugador.
8. **Usa varias capas de baldosas** para superponer hierba sobre arena sin sobrescribir.
9. **Los sprites de las capas de assets se animan por defecto**: pon la velocidad a 0.
10. **Interacción, colisión o comportamiento → instancia. Solo visual → sprite.**

---

## Ejercicio propuesto

> **Objetivo:** montar un nivel con dos capas de baldosas y decorarlo con props,
> decidiendo correctamente qué va como instancia y qué como sprite.

1. Descarga el pack de itch.io (o cualquier pack con tile sets) e importa la hoja de
   suelo **sin** usar `_strip`. Llámala `spr_tiles_floor`.
2. **Comprueba el error:** arrástrala al editor de rooms estando en la capa de
   instancias. Lee el aviso y acepta crear una capa de assets. Observa que suelta el
   sprite entero de una pieza. Después bórrala.
3. Crea el tile set `ts_floor` y asígnale el sprite arrastrándolo.
4. Ajusta el tamaño de baldosa al de tu hoja. Comprueba las líneas de cuadrícula.
5. **Experimenta con *Output Border*:** ponlo a 0, pinta una zona grande y busca
   costuras. Vuelve a dejarlo en 2.
6. Crea la capa de baldosas `tiles_floor` **debajo** de la capa de instancias y rellena
   toda la room con el cubo de pintura.
7. Comprueba que el personaje se ve **por encima** del suelo. Si no, revisa el orden de
   las capas.
8. **Comprueba la baldosa vacía:** intenta pintar con la baldosa superior izquierda y
   verifica que en realidad estás borrando.
9. Crea una segunda capa `tiles_grass` **encima** de la de suelo y pinta un parche de
   hierba. Comprueba que no borra la arena.
10. Importa la hoja de props y trocéala con **Convert to Frames**.
11. Crea una capa de assets y coloca al menos diez árboles y rocas.
12. **Pon la velocidad de animación a 0** en todos y comprueba que dejan de parpadear.

**Reto extra:** aplica la regla de oro. Haz una lista de diez elementos de tu juego
(jugador, árbol decorativo, cofre, roca de fondo, enemigo, suelo, antorcha, arbusto de
bayas, puerta, nube) y clasifícalos en **instancia** o **sprite**, justificando cada uno
según si necesita interacción, colisión o comportamiento.
