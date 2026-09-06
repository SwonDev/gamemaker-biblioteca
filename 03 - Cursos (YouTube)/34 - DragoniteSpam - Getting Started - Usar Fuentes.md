# 34 · DragoniteSpam — Usar fuentes

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 22 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=5W7457-y4aY> |
| **Duración** | 16 min 7 s |
| **Publicado** | 4 de julio de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `draw_set_font()` |

> «La fuente por defecto que obtienes al dibujar texto en GameMaker, siendo honestos,
> **no se ve muy bien**. En el mundo de la tipografía está solo medio paso por encima de
> algo como Arial o Helvetica.»

## Índice de contenido

1. Crear un recurso de fuente
2. Elegir la tipografía
3. Tamaño y vista previa
4. Aplicar la fuente
5. Por qué el texto se sigue viendo mal al escalar
6. Anti-aliasing: no es para lo que crees
7. **SDF**: la solución real
8. Límites de SDF
9. Efectos con SDF
10. Estilos: negrita, cursiva…
11. Rangos de caracteres (¡importante para español!)
12. Otras opciones avanzadas

---

## 1. Crear un recurso de fuente

Las fuentes son **un tipo de recurso propio** en GameMaker: se añaden igual que un sprite,
un sonido o un objeto.

```
Clic derecho en el navegador de recursos → Create → Font
```

Por tradición, el autor las nombra `fmt_` + nombre (`fmt_the_game_font`).

---

## 2. Elegir la tipografía

En el inspector de la fuente verás un desplegable con **todas las fuentes instaladas en tu
sistema**.

> Si descargas e instalas una fuente, **aparecerá en esa lista**. Si tenías GameMaker
> abierto, puede que necesites **reiniciarlo**. (También existe la opción **Help → Refresh
> system fonts**.)

El autor, «para ser rebelde», elige **Comic Sans** en el vídeo, porque le parece
«demasiado odiada».

---

## 3. Tamaño y vista previa

- Elige el **tamaño** (él usa 20 para que se lea bien en el vídeo).
- Hay una **ventana de vista previa** donde puedes escribir y ver cómo quedan los caracteres
  con esa configuración.

---

## 4. Aplicar la fuente

Igual que el color o la alineación:

```gml
draw_set_font(fmt_the_game_font);
draw_set_color(c_aqua);
draw_text(x, y - 100, "Hace calor hoy, ¿verdad?");
```

> Sobre el color, el autor hace una observación práctica: la forma más legible de destacar
> un texto suele ser **contorno o sombra paralela**, no solo el color. Pero eso requiere
> funciones más avanzadas de fuentes.

---

## 5. Por qué el texto se sigue viendo mal al escalar

> **Por defecto no puedes escalar una fuente de forma limpia en tiempo de ejecución.**

Recordamos el mecanismo:

> **Al compilar el juego, GameMaker guarda cada carácter (cada glifo) de tu fuente como un
> pequeño sprite y los va encadenando.**

Hacer renderizado de fuentes de verdad en tiempo de ejecución es **caro**, así que
GameMaker no lo hace. Si escalas o transformas, GameMaker **estira y aplasta esos
sprites**, y aparecen los artefactos.

---

## 6. Anti-aliasing: no es para lo que crees

Es tentador pensar que la casilla **Anti-aliasing** lo arregla. Pero:

1. **Está activada por defecto.**
2. **No sirve para eso.**

> El anti-aliasing es para cuando la fuente se **rasteriza al compilar el juego**.

---

## 7. SDF: la solución real

Para escalar texto limpiamente hay que marcar:

```
☑ Enable SDF
```

**SDF** = *Signed Distance Field* (campo de distancia con signo).

Qué hace:

> Es una forma de renderizar fuentes que **no necesita un renderizador completo**, pero
> **incluye información adicional de anti-aliasing** en los sprites de mapa de bits que
> genera el compilador.

Gracias a eso:

> **Puedes escalar la fuente arriba y abajo, dentro de límites razonables, conservando
> información de suavizado.**

Técnicamente, GameMaker pasa a renderizar el texto **con un shader especial** que usa esa
información SDF para **suavizar las curvas sobre la marcha** y eliminar los artefactos.

El autor lo demuestra: con escala 1,5 y rotación 10°, el texto sin SDF se ve «con píxeles
bloque»; con SDF, **mucho más suave**.

---

## 8. Límites de SDF

> «Como **seguimos sin hacer renderizado de fuentes de verdad** —solo anti-aliasing—, **hay
> límites**.»

Si en lugar de 1,5× escalas a **3×**:

> Empiezan a aparecer problemas: **ya no se parece a la fuente original**, aunque sobre el
> papel dibujar a tamaño 20 y triplicarlo debería equivaler a dibujarlo a tamaño 60.

La razón:

> GameMaker sigue convirtiendo cada glifo en un sprite. Incluso con la información extra,
> **si lo agrandas demasiado se pierde información**: no hay suficiente en la versión
> rasterizada.

### La solución práctica

> Crea la fuente con un **tamaño algo mayor** (por ejemplo **40**) y evita escalados
    absurdos.

Con un tamaño mayor hay **más espacio en cada sprite** para codificar la información de
anti-aliasing, así que aguanta mucho mejor el escalado.

> También puedes crear una fuente enorme y **escalarla hacia abajo**, que dentro de lo
> razonable funciona bien.

---

## 9. Efectos con SDF

Además del escalado, las fuentes SDF permiten aplicar **efectos**:

- Contornos (*outlines*).
- Resplandores (*glows*).
- Sombras paralelas (*drop shadows*).

Pero para eso necesitas **características más avanzadas del lenguaje** (structs y gestión
de datos) que la serie todavía no ha visto.

---

## 10. Estilos: negrita, cursiva…

Si la tipografía tiene versiones de estilo (**bold**, *italic*, **bold italic**, semibold,
condensed…), se eligen en el desplegable **Style**.

> **No puedes cambiar el estilo en tiempo de ejecución**, porque la fuente se rasteriza al
> compilar. Se configura desde las propiedades del recurso.

---

## 11. Rangos de caracteres (¡importante para español!)

> **Por defecto, las fuentes de GameMaker NO contienen todos los caracteres de la
> tipografía.**

El rango por defecto incluye solo:

- Letras mayúsculas.
- Letras minúsculas.
- Números.
- Ciertos signos de puntuación.

Eso suele bastar para inglés, pero **hay muchísimos idiomas con caracteres fuera de ese
rango**.

### El ejemplo del vídeo

Al intentar escribir **Pokémon** con la `é` acentuada:

> La `é` **no se renderiza**: aparece un carácter sustituto que indica que falta en el
> rango de la fuente.

Y el autor lo generaliza explícitamente:

> «La **eñe** en muchas palabras y nombres en español» es otro ejemplo de carácter que
> necesitarás.

También nombres de personajes o de jugadores con acentos u otros caracteres no latinos.

### Cómo añadirlos

En la interfaz de **rangos de la fuente** puedes añadir:

| Opción | Contenido |
|---|---|
| El rango por defecto | Letras, números y puntuación básica |
| Solo dígitos | Números |
| Solo letras | Letras |
| **Todo el rango ASCII** | Incluye **la mayoría de los caracteres acentuados** |
| Un rango Unicode personalizado | El que necesites |
| Caracteres sueltos | Se escriben directamente en el cuadro |

Herramientas:

- **Add range**: añadir un rango.
- **Delete range**: eliminar un rango que hayas añadido por error.
- Puedes escribir directamente los caracteres que quieras mostrar.

> **Ojo:** si añades solo un carácter concreto, **todos los demás quedarán en blanco**.
> Lo suyo es combinar el rango ASCII (o el que necesites) con caracteres sueltos.

Para idiomas con escrituras distintas:

- **Caracteres cirílicos** (ruso).
- **Caracteres asiáticos** (chino, japonés, coreano).
- **Devanagari** (hindi).
- **Hebreo**.

> En todos esos casos tendrás que **asegurarte de añadir los rangos correspondientes** para
> que GameMaker los reconozca.

---

## 12. Otras opciones avanzadas

Hay algunos ajustes más:

- El **renderizador de fuentes** concreto usado al rasterizar.
- Si se aplica **kerning** (el autor no se imagina por qué querrías desactivarlo).
- Otros ajustes de tipografía avanzada.

> «Prácticamente nunca uso ninguno de estos, pero ahí están si te interesan cosas más
> avanzadas de tipografía.»

---

## Puntos clave

1. **Las fuentes son un tipo de recurso propio** en GameMaker.
2. El desplegable lista **todas las fuentes instaladas en tu sistema** (a veces hay que
   reiniciar GameMaker o usar *Refresh system fonts*).
3. **`draw_set_font(fnt)`** aplica la fuente.
4. **No hay renderizado de fuentes en tiempo de ejecución**: cada glifo es un sprite
   generado al compilar.
5. **El anti-aliasing NO arregla el escalado**: es para la rasterización en compilación.
6. **Habilita SDF** para poder escalar el texto manteniendo el suavizado.
7. **SDF tiene límites**: crea la fuente con un tamaño mayor (40) en vez de escalarla al
   triple.
8. **Los estilos (negrita, cursiva) se fijan en el recurso**, no en tiempo de ejecución.
9. **⚠️ Por defecto la fuente NO incluye acentos ni eñes.** Añade el rango ASCII completo
   (o el que necesites) para textos en español.
10. Para cirílico, asiático, hindi o hebreo hay que añadir sus rangos Unicode.

---

## Ejercicio propuesto

> **Objetivo:** montar una fuente propia que funcione correctamente **en español** y que
> aguante el escalado.

**Parte A — Crear la fuente**

1. Crea el recurso de fuente `fmt_principal`.
2. Elige una tipografía instalada en tu Mac. Si quieres una pixel, descárgala e instálala
   (y reinicia GameMaker si no aparece).
3. Pon el tamaño a **20** y usa la vista previa para comprobar cómo se ven los caracteres.

**Parte B — Aplicarla**

4. Aplícala con `draw_set_font(fmt_principal);` y dibuja un texto.
5. Cambia el color y la alineación y comprueba que todo sigue funcionando.

**Parte C — El problema de los acentos (clave para español)**

6. **Antes de tocar nada**, escribe un texto con acentos y eñes:
   ```gml
   draw_text(x, y - 100, "¡Hola! ¿Cómo estás? Niño, canción, corazón");
   ```
7. Ejecuta y **comprueba qué caracteres salen mal**. Este es el fallo más común en proyectos
   hispanohablantes.
8. Ve a los **rangos de la fuente** y añade el **rango ASCII completo**.
9. Guarda, vuelve a compilar y comprueba que ahora **acentos, eñes y signos de apertura
   (¿ ¡) se renderizan correctamente**.
10. **Prueba el error inverso:** borra el rango por defecto y deja solo la `é`. Comprueba
    que todo lo demás desaparece. Vuelve a dejarlo bien.

**Parte D — SDF**

11. Reactiva la cámara con zoom y escala el texto a 1,5 con una pequeña rotación. Observa
    los artefactos.
12. Marca **Enable SDF** y comprueba la mejora.
13. Sube la escala a **3×** y comprueba que **vuelven los problemas**.
14. Soluciónalo como indica el autor: sube el **tamaño de la fuente a 40** en vez de escalar
    tanto. Comprueba el resultado.

**Reto extra:** configura una fuente para un idioma con alfabeto no latino (por ejemplo
ruso con caracteres cirílicos). Localiza su rango Unicode, añádelo y verifica que se
renderiza. Anota el rango que has usado.
