# 10 · Crear tus propios recursos de arte

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 10 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=JRLgsnoVdp4> |
| **Duración** | 24 min 47 s |
| **Publicado** | 30 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Herramienta** | GIMP 3 (gratuito y de código abierto) |

Este capítulo es una **sesión improvisada**: el autor crea el arte desde cero, sin
planificación previa, mostrando su proceso real. Es la respuesta a la pregunta que le
hacen sus alumnos: *«¿cómo hago arte si no soy artista?»*.

> «No soy artista, pero nunca había tenido un recurso que mostrar. Ahora puedo
> enseñároslo.»

## Índice de contenido

1. La herramienta: GIMP
2. Qué arte necesita el jugador (y por qué un barco)
3. Configurar el lienzo para pixel art
4. Dibujar el barco: simetría y líneas rectas
5. Buscar referencias sin copiar
6. Recortar y exportar en PNG
7. Separar el arte de la máscara de colisión
8. El cañón
9. El truco del arte en blanco y el *color blend*
10. Los bloques: cajas de madera
11. Renombrar recursos con seguridad
12. El enemigo: darle sentido al juego

---

## 1. La herramienta: GIMP

El autor usa **GIMP**, que define como:

- **Completamente gratis y de código abierto.**
- Como Photoshop, pero **más sencillo y reducido**.
- Tan ligero que «podrías ejecutarlo en una nevera inteligente».
- Funciona en **cualquier sistema**.

La versión actual que usa es la **3**.

---

## 2. Qué arte necesita el jugador (y por qué un barco)

El arte del jugador **define el tipo de juego**. Las mismas mecánicas sirven para
juegos muy distintos.

Claves para decidir:

- Es un juego **vista cenital (top-down)**, así que el arte debería ser **más o menos
  simétrico** en todos los lados.
- **No vale una persona**: el cañón rota en todas direcciones y el objeto siempre mira
  hacia donde te mueves. Una persona sujetando un arma no encajaría.
- Podrías cambiar el código de animación… pero no merece la pena.

La solución: **un barco**.

> Es la lección de diseño más valiosa del capítulo: **elige un arte que encaje con cómo
> está programado tu juego**, en vez de reprogramar el juego para que encaje con el
> arte que tenías en la cabeza.

---

## 3. Configurar el lienzo para pixel art

```
Archivo → Nuevo → 40 × 40
Opciones avanzadas → Rellenar con: Transparencia
```

> **Rellenar con transparencia** es imprescindible, porque exportaremos en **PNG**, que
> **sí admite transparencia**. Así el sprite no tendrá un fondo cuadrado opaco.

Ajustes de dibujo:

1. Herramienta **Lápiz**.
2. Tamaño de pincel: **1 píxel**.
3. **Ver → Mostrar cuadrícula** e **Imagen → Configurar cuadrícula → 1 × 1**.

> La cuadrícula de 1 píxel te permite **ver y contar exactamente dónde está cada
> píxel**. Es la diferencia entre pixel art limpio y pixel art sucio.

Elige un color de primer plano muy visible (el autor prueba rojo, lo encuentra
demasiado chillón y vuelve al blanco).

---

## 4. Dibujar el barco: simetría y líneas rectas

> **Recuerda la convención:** la orientación 0 en GameMaker mira hacia la **derecha**.
> Así que el barco debe **apuntar a la derecha**.

### Líneas rectas

> **Clic en un píxel + mantener `Shift` + clic en otro** dibuja una **línea recta**
> entre ambos.

### Simetría por espejado

El método del autor:

1. Dibuja **media** forma con líneas rectas.
2. Herramienta **Seleccionar** → selecciona la zona.
3. `Ctrl + C` y `Ctrl + V`.
4. Herramienta **Mover** para colocar la copia.
5. Herramienta **Voltear** (`Shift + F`) → **volteado vertical**.
6. Herramienta **Mover** de nuevo para encajarla.

> «No queda perfecto, y no pasa nada. **Trabajar a baja resolución cubre multitud de
> pecados.**»

### No te compliques

> «Cuando estás empezando y no eres artista, **no lo compliques**. Solo necesitas una
> forma de barco. Eso es una forma de barco.»

El autor llega a dibujar y **borrar todo** con `Ctrl + A` y `Supr` porque el primer
intento no le convence. Lo vuelve a intentar más simple. Es parte del proceso.

---

## 5. Buscar referencias sin copiar

Cuando se atasca, hace lo que haría cualquiera:

> **Busca «topdown pixel art boat»** para ver cómo lo resuelven otros.

Observa el patrón: proa puntiaguda, luego recto hacia atrás, y un pequeño entrante. Ese
esquema le sirve de guía, pero **dibuja su propia versión**.

Después añade detalles:

- Un **borde** alrededor.
- Engrosar una línea un píxel más.
- Herramienta **Seleccionar por color** para aislar un color y manipularlo.
- «Florituras» de redondez y textura **contando píxeles**: uno-dos-tres, uno-dos-tres.

---

## 6. Recortar y exportar en PNG

El barco mide 40 píxeles de ancho pero **no tanto de alto**, y eso está bien.

1. Herramienta **Recortar** y recorta al contenido.
2. **Archivo → Exportar** → guárdalo en el escritorio como **`S_boat.png`**.
3. **Córtalo y llévalo a tu carpeta de Google Drive**, en una subcarpeta
   `art assets`.

> Igual que con la música y los YYZ: **respalda el arte en la nube**.

---

## 7. Separar el arte de la máscara de colisión

El jugador necesita **una máscara de colisión predecible** y, además, un dibujo
bonito. La solución del autor:

1. **Duplica** el sprite `sPlayer` y llámalo **`sPlayerCollision`**, manteniéndolo en
   **40 × 40**. Este será la máscara.
2. En `sPlayer`, pulsa **Import** y carga el barco. GameMaker ajusta el tamaño a
   **40 × 24** con origen **Middle Center**.

Así el arte es libre y **la colisión sigue siendo un rectángulo limpio**.

---

## 8. El cañón

El sprite `sGun` es de **20 × 7**. El autor lo hace algo más fino y lo exporta como
`s_gun`.

El cañón **no necesita colisión**, así que no hay que preocuparse por su máscara.

---

## 9. El truco del arte en blanco y el *color blend*

> **¿Por qué todo el arte es blanco?** Porque así el autor puede **colorearlo desde
> GameMaker** con el ajuste de **Color Blend** del objeto.

Aplicación en `oPlayer`:

| Elemento | Color Blend |
|---|---|
| El jugador (barco) | **Blanco** (sin teñir) |
| El cañón | **Negro**, para que destaque sobre el barco |

Es una técnica potentísima: **un mismo arte sirve para muchos personajes o
variantes**, cambiando solo un valor. Y de paso, permite que el jugador elija color.

---

## 10. Los bloques: cajas de madera

Como el juego va de barcos, los bloques pasan a ser **cajas de madera flotando en el
agua**. El sprite es de **30 × 30**.

Método:

1. Rellena el fondo.
2. Dibuja **diagonales de uno-dos-tres** píxeles: es el truco para simular tablas de
   madera.
3. Cuenta píxeles: **uno, dos, tres** arriba; **uno, dos, tres** abajo.
4. Haz que las tablas **se solapen** ligeramente para que parezcan listones.
5. Añade pequeños **clavos**.
6. **Selecciona todo el color guía y bórralo** con `Supr`: así se elimina la capa de
   referencia de golpe.

> «Lo bueno de trabajar a resolución tan pequeña es que **literalmente puedes contar
> píxeles**».

Exporta como `s_box` / `s_crate`.

---

## 11. Renombrar recursos con seguridad

El código del juego llama al sprite `sBlock`, pero ahora es una caja.

> **GameMaker actualiza el nombre automáticamente en todo el código** cuando renombras
> un recurso, **siempre que el código estuviera funcionando**.

Así que puedes renombrarlo a `sBox` con tranquilidad.

---

## 12. El enemigo: darle sentido al juego

Los enemigos también son de **30 × 30**.

El autor se plantea el enemigo desde la **narrativa** del juego: un pirata en mar
abierto, y lo que lo hunde no son enemigos como tales, sino **los pensamientos
intrusivos y las preocupaciones**.

¿Cómo se siente un pensamiento intrusivo?

> «Sabe a veneno. Te está enfermando. Duele.»

Opciones que baraja: estrellas, cuchillos, una pastilla… y se decide por una **cara
triste estilizada**, dibujada contando píxeles de tres en tres:

- Contorno redondeado.
- Ojos.
- Cejas: «lo más triste no son las cejas enfadadas, sino las de una **víctima que no
  quiere estar ahí**».

Exporta como `s_enemy` y lo importa.

> **Ojo con la máscara:** los enemigos **sí** tienen colisiones, pero como el sprite no
> rota y usa la imagen completa, la colisión sigue funcionando sin cambios.

Por último, como el arte ya tiene color, la barra de vida del enemigo **deja de
combinar**: el autor cambia su color a **`c_white`**.

---

## Puntos clave

1. **GIMP** es gratuito, de código abierto y suficiente para pixel art.
2. **Elige arte que encaje con tu código**, no al revés. Un barco funciona en vista
   cenital porque es simétrico y rotable.
3. **Orientación 0 = derecha** en GameMaker: dibuja mirando a la derecha.
4. **Rellenar con transparencia** y exportar en **PNG**.
5. **Cuadrícula de 1 píxel** para ver y contar cada píxel.
6. **`Shift` + clic** dibuja líneas rectas.
7. **Simetría:** dibuja la mitad, copia, pega y **voltea verticalmente** (`Shift + F`).
8. **La baja resolución cubre multitud de pecados.** No te compliques.
9. **Busca referencias** cuando te atasques, pero dibuja tu propia versión.
10. **Separa arte y colisión**: un sprite `sPlayerCollision` para la máscara y otro con
    el dibujo.
11. **Arte en blanco + Color Blend** = múltiples variantes del mismo recurso.
12. **Contar píxeles de tres en tres** da texturas de madera y volúmenes convincentes.
13. **Renombrar un recurso actualiza el código automáticamente.**
14. **Respaldar el arte en la nube**, como todo lo demás.

---

## Ejercicio propuesto

> **Objetivo:** sustituir todos los cuadrados de colores del prototipo por arte de
> verdad, siguiendo el proceso del autor.

**Parte A — Prepara el entorno**

1. Instala **GIMP** (o el editor de pixel art que prefieras).
2. Crea en tu nube la carpeta `art assets` dentro de la carpeta del proyecto.

**Parte B — El barco (jugador)**

3. Crea un lienzo de **40 × 40** con **relleno transparente**.
4. Activa la **cuadrícula de 1 × 1** y pon el pincel a **1 píxel**.
5. Dibuja **media** silueta de barco **mirando a la derecha** usando `Shift` + clic
   para las líneas rectas.
6. Cópiala, pégala y **voltea verticalmente** para conseguir simetría. Encájala con la
   herramienta Mover.
7. Busca «topdown pixel art boat» y mejora tu versión: proa, entrante, borde.
8. Añade textura **contando píxeles de tres en tres**.
9. **Recorta** al contenido y **exporta como PNG**.
10. Súbelo a tu carpeta `art assets` en la nube.

**Parte C — Integración en GameMaker**

11. **Duplica `sPlayer` como `sPlayerCollision`** y déjalo en 40 × 40.
12. Importa el barco en `sPlayer` y comprueba el nuevo tamaño y el origen **Middle
    Center**.
13. Haz el cañón `sGun` más fino y expórtalo.
14. Comprueba que el juego sigue funcionando igual.

**Parte D — Experimenta con el color**

15. Deja el arte **en blanco**.
16. En `oPlayer`, ajusta el **Color Blend** del barco a blanco y el del cañón a negro.
17. Ahora cambia el Color Blend del barco a otros colores y observa cómo **el mismo
    arte** se convierte en variantes distintas. Anota tres combinaciones que te gusten.

**Parte E — Bloques y enemigo**

18. Dibuja una **caja de madera de 30 × 30** con el truco de las diagonales de tres
    píxeles y los clavos. Selecciona el color guía y bórralo antes de exportar.
19. Renombra `sBlock` a `sBox` y comprueba que **el código sigue compilando**:
    GameMaker ha actualizado todas las referencias.
20. Dibuja un **enemigo de 30 × 30** con sentido narrativo para tu juego. No hace falta
    que sea una cara: prueba una medusa, una roca con ojos o una mancha de petróleo.
21. Ajusta el color de la barra de vida del enemigo para que contraste con el arte
    nuevo (por ejemplo `c_white`).

**Reto extra:** el autor insiste en que **un arte sencillo solo es de aficionado si no
encaja con la visión del juego**. Escribe un párrafo describiendo la «visión» de tu
juego en tres frases, y revisa tus cuatro sprites: ¿cuentan todos la misma historia? Si
alguno no encaja, cámbialo.
