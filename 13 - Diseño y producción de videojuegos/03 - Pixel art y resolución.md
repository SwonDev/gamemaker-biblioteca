# 03 · Pixel art y resolución

> El pixel art no es «gráficos de baja resolución»: es una disciplina con reglas propias, y
> la mitad de esas reglas se deciden **antes de dibujar el primer píxel**, al elegir la
> resolución base del juego. Este documento cubre las dos mitades: la artística (paletas,
> clusters, sombreado, tiles, animación) y la técnica (qué ajustes de GameMaker convierten
> un sprite nítido en un pegote borroso, y cómo evitarlos).
>
> **Qué NO cubre este documento:**
> - **El sistema de cámara completo** (viewport, `application_surface`, pantalla completa,
>   sacudida, zoom, filtrado bilineal por shader): lo desarrolla, paso a paso y con código,
>   la serie de PixelatedPope en [03 · 41](../03%20-%20Cursos%20%28YouTube%29/41%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%201%20-%20Principiante.md)–[44](../03%20-%20Cursos%20%28YouTube%29/44%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%204%20-%20Experto.md).
>   Aquí solo se resume **la decisión** que hay que tomar y sus consecuencias sobre el arte.
> - **La API de animación** (`image_speed`, Sequences, Animation Curves): la cubre
>   [13 · 04 — Animación de sprites, Sequences y Animation Curves](./04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md).
>   Aquí se trata la animación **como dibujo**: cuántos frames, qué frames y por qué.
> - **Dónde conseguir arte libre y qué herramienta de pixel art usar**: está en
>   [07 · 09 — Asset packs y recursos gráficos](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md)
>   (§3 herramientas, §10 paletas). No se repite.
> - **Automatizar Aseprite → GameMaker** (AseSync, conveyorbelt, GM Link):
>   [12 · 05 — Pipeline de arte, audio y niveles](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md) §1.

---

## 1 · La resolución base: la decisión que condiciona todo el arte

### 1.1 Por qué se parte de 1920 × 1080 y se divide

La resolución base (o *resolución nativa*, o *resolución interna*) es **el tamaño en píxeles
del lienzo que dibuja tu juego antes de escalarlo a la ventana**. No es el tamaño de la
ventana ni el tamaño de la room: es cuánta información visual existe realmente.

La regla de oro es sencilla y no tiene alternativa razonable en 2026: **elige una resolución
base que divida exactamente 1920 × 1080**, porque 1080p sigue siendo la resolución de
escritorio dominante y porque 1440p y 4K son múltiplos limpios de partes de ella.

Dividir «por el mismo número» arriba y abajo mantiene la relación de aspecto 16:9
(1920/1080 = 1,777…). Dividir por números distintos la rompe y el juego sale estirado o con
franjas negras raras.

### 1.2 Qué resoluciones base escalan de verdad

La tabla siguiente es **aritmética pura, comprobable**: para cada base, qué factor de escala
haría falta para llenar cada monitor sin deformar. Solo cuentan los factores **enteros
e iguales en X e Y**; cualquier otra cosa deforma píxeles.

| Base | 1280×720 | 1920×1080 | 2560×1440 | 3840×2160 |
|---|---|---|---|---|
| **256 × 144** | ×5 | 7,5 ✗ | ×10 | ×15 |
| **320 × 180** | ×4 | ×6 | ×8 | ×12 |
| **384 × 216** | 3,33 ✗ | ×5 | 6,67 ✗ | ×10 |
| **426 × 240** | 3,005 ✗ | 4,51 ✗ | 6,01 ✗ | 9,01 ✗ |
| **480 × 270** | 2,67 ✗ | ×4 | 5,33 ✗ | ×8 |
| **512 × 288** | 2,5 ✗ | 3,75 ✗ | ×5 | 7,5 ✗ |
| **640 × 360** | ×2 | ×3 | ×4 | ×6 |
| **640 × 480** (4:3) | ✗ | ✗ | ×3 | ✗ |

De ahí sale el resultado que conviene memorizar:

> **Solo `640 × 360` y sus divisores exactos (`320 × 180`, `160 × 90`, `128 × 72`, `80 × 45`,
> `64 × 36`) escalan con número entero en 720p, 1080p, 1440p y 4K a la vez.**
>
> El motivo: el máximo común divisor de 1280, 1920, 2560 y 3840 es **640**, y el de 720, 1080,
> 1440 y 2160 es **360**. Cualquier base 16:9 que no divida 640 × 360 fallará en al menos uno
> de los cuatro monitores.

Por qué importa tanto el 16:9 y no otra proporción: según la encuesta de hardware de Steam
que cita Notkey Studio (diciembre de 2025), **1920×1080 es el 52,6 % de los escritorios**,
**2560×1440 el 20,6 %** y **3840×2160 el 4,9 %**. Las tres son 16:9. La documentación de Godot
llega a la misma conclusión por otro camino: recomienda un *viewport* de pixel art **entre
256×224 y 640×480**, y señala que *«640×360 is a good baseline, as it scales to 1280×720,
1920×1080, 2560×1440, and 3840×2160 without any black bars when using integer scaling»*.

`384 × 216` y `480 × 270` son excelentes opciones **si aceptas que 720p y 1440p necesitarán
barras o un escalado no entero**; en la práctica muchos juegos comerciales lo aceptan.
`426 × 240` (o el `424 × 240` de Sonic Mania) no encaja en ningún múltiplo entero: es una
elección estética, no matemática.

### 1.3 Qué se siente distinto en cada resolución

La resolución base decide **cuánto mundo ves de golpe** y **cuánto detalle cabe en un
personaje**:

| Base | Tiles de 16 px visibles | Un sprite de 32 px ocupa | Encaja con | Protagonista |
|---|---|---|---|---|
| 256 × 144 | 16 × 9 | 22 % del alto | Plataformas íntimo, cámara pegada | 16–24 px |
| 320 × 180 | 20 × 11,25 | 17,8 % | Plataformas y acción cenital estándar | 24–32 px |
| 384 × 216 | 24 × 13,5 | 14,8 % | Metroidvania, RPG de salas grandes | 32–48 px |
| 480 × 270 | 30 × 16,9 | 11,9 % | Estrategia, gestión, mucha interfaz | 24–32 px |
| 640 × 360 | 40 × 22,5 | 8,9 % | Pixel art detallado con HUD fino | 48–64 px |

**El error más caro es empezar a dibujar antes de fijar esto.** Cambiar de 320×180 a
480×270 a mitad del proyecto obliga a **redibujar** todos los sprites: escalar pixel art no
es redimensionar una foto, es rehacerlo.

> ⚠️ Regla práctica que se repite en la comunidad y que conviene tomar como orientación, no
> como ley: **el sprite del protagonista debería ocupar entre un 8 % y un 20 % del alto de
> la pantalla**. Por debajo, el jugador no lee la animación; por encima, no ve el nivel.

### 1.4 El tamaño de tile manda sobre el tamaño de la pantalla

Elige **primero** el tamaño de tile (8, 16 o 32 px) y **después** ajusta la base para que
sea múltiplo suyo, o al menos para que el número de tiles visibles no salga con decimales
molestos en el alto.

- **8 px**: muy retro, tipo NES. Poco espacio para detalle; obliga a paletas cortas.
- **16 px**: el estándar de facto. Encaja bien con 320×180 (20 columnas) y perfecto con
  384×216 (24 × 13,5) o 640×360 (40 × 22,5).
- **32 px**: pixel art detallado. Con 320×180 solo verías 10 × 5,6 tiles: demasiado poco.
  Pide 480×270 o 640×360.

Truco: si quieres un número redondo de filas, **480 × 272** da 30 × 17 tiles de 16 px
exactos… pero rompe el 16:9 (480/272 = 1,7647). Es un ejemplo de la tensión permanente entre
«que la rejilla cuadre» y «que la pantalla cuadre». Gana la pantalla.

### 1.5 Pixel-perfect frente a subpíxel: la decisión, en dos párrafos

Hay dos formas de renderizar un juego de pixel art, y **no hay una correcta**:

| | Rejilla estricta (*pixel-perfect*) | Subpíxel |
|---|---|---|
| Cómo | La `application_surface` mide exactamente la base y luego se escala entera | La `application_surface` mide base × escala; el juego se renderiza a la resolución real |
| Ventaja | Cada píxel del arte es un bloque idéntico. Estética retro impecable | Movimiento, zoom y rotación mucho más suaves |
| Coste | El movimiento «salta» de píxel en píxel; la cámara tiembla si no redondeas | El arte deja de estar en una rejilla; aparecen líneas entre tiles y bordes irregulares |
| Lo eligen | Juegos que imitan hardware antiguo | Juegos con pixel art detallado y cámara suave |

PixelatedPope, tras cuatro capítulos de sistema de cámara, **no cierra la decisión**: escribe
las dos líneas de `surface_resize()` y recomienda probar las dos, porque es «puramente
preferencia personal». Su conclusión práctica al final de la serie sí es tajante: **diseña
para 1920 × 1080 y no persigas el escalado entero universal**, porque hay monitores (su
ejemplo: un teléfono que reporta 2297 px de ancho, un número primo) donde el escalado entero
perfecto es literalmente imposible.

El código completo de ese sistema —resolución base en macros, cálculo de la escala de
ventana, GUI, pantalla completa, dibujar el juego «en una caja» y el shader de filtrado
bilineal estilo Sonic Mania— está en
[03 · 42](../03%20-%20Cursos%20%28YouTube%29/42%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%202%20-%20Intermedio.md),
[03 · 43](../03%20-%20Cursos%20%28YouTube%29/43%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%203%20-%20Avanzado.md) y
[03 · 44](../03%20-%20Cursos%20%28YouTube%29/44%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%204%20-%20Experto.md).
**No lo repitas aquí: úsalo.**

### 1.6 Lo mínimo que necesitas para que la escala sea entera

Si aún no vas a montar el sistema completo, esta función basta para arrancar: calcula el
mayor múltiplo entero de tu base que cabe en el monitor y deja un hueco para la barra de
título.

```gml
/// @function escala_entera_maxima(_ancho_base, _alto_base, _pantalla_completa)
/// @desc    Mayor factor ENTERO de escala que cabe en el monitor. Mínimo 1.
///          Con _pantalla_completa a false reserva sitio para la barra de título.
/// @return  {Real} Factor entero >= 1.
function escala_entera_maxima(_ancho_base, _alto_base, _pantalla_completa)
{
    var _escala_x = display_get_width()  / _ancho_base;
    var _escala_y = display_get_height() / _alto_base;
    var _escala   = floor(min(_escala_x, _escala_y));

    // En ventana, la barra de título y los bordes roban alto. Si el ajuste
    // era JUSTO (sin parte decimal), la ventana no cabría: baja un escalón.
    if (!_pantalla_completa && frac(_escala_y) == 0)
    {
        _escala -= 1;
    }

    return max(1, _escala);
}

/// @function aplicar_resolucion(_ancho_base, _alto_base, _escala)
/// @desc    Fija ventana, superficie de aplicación y GUI de forma coherente.
///          Llámala al arrancar y cada vez que cambies de escala o de modo.
function aplicar_resolucion(_ancho_base, _alto_base, _escala)
{
    window_set_size(_ancho_base * _escala, _alto_base * _escala);
    window_center();

    // Rejilla estricta: la superficie mide exactamente la base.
    // Para subpíxeles, multiplica ambos por _escala.
    surface_resize(application_surface, _ancho_base, _alto_base);

    // La GUI a la resolución base: el HUD comparte rejilla con el arte.
    display_set_gui_size(_ancho_base, _alto_base);
}
```

```gml
/// obj_arranque · Create — uso típico en una room de inicialización
ancho_base = 320;
alto_base  = 180;
escala     = escala_entera_maxima(ancho_base, alto_base, false);

aplicar_resolucion(ancho_base, alto_base, escala);
gpu_set_texfilter(false);       // sin interpolación: pixel art nítido

room_goto(rm_menu);
```

> 🔺 Si tu HUD necesita más resolución que el juego (texto pequeño legible sobre arte de
> 320×180), llama a `display_set_gui_size()` con un múltiplo de la base —por ejemplo
> `320*2 × 180*2`— y dibuja el HUD ahí. La GUI **no** comparte la limitación de subpíxel del
> mundo: puede escalar y rotar sin perder nitidez, y eso rompe la ilusión retro si abusas.
> El detalle está en [03 · 44](../03%20-%20Cursos%20%28YouTube%29/44%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%204%20-%20Experto.md) §3–§6.

---

## 2 · Paletas: menos colores, mejores decisiones

### 2.1 Por qué limitar la paleta

Limitar colores no es nostalgia de hardware: es **una restricción que produce coherencia**.

1. **Coherencia automática.** Si todo sale de los mismos 32 colores, el personaje nuevo
   encaja con el fondo viejo sin retocar nada.
2. **Mejores decisiones.** Elegir entre 16,7 millones de colores paraliza; elegir entre 24
   obliga a pensar en **valor** (claro/oscuro) antes que en tono.
3. **Legibilidad.** Con pocos colores, cada color significa algo.
4. **Práctico en GameMaker.** Una paleta corta hace viable el intercambio de paleta en runtime
   sin redibujar sprites.

Tamaños típicos y para qué sirven:

| Tamaño | Sensación | Cuándo |
|---|---|---|
| **2–4 colores** | Game Boy / 1-bit | Jams, estilo muy marcado, juegos de puzles |
| **8–16 colores** | NES / arcade temprano | Estilo limpio, muy legible, muy rápido de producir |
| **24–32 colores** | SNES / Mega Drive | El punto dulce para un juego indie completo |
| **48–64 colores** | Pixel art moderno | Cuando hay varios biomas o mucha iluminación |
| **>64** | Ilustración pixelada | Solo si sabes por qué; deja de ser una restricción útil |

> 💡 Una paleta de 32 colores **no** son 32 colores independientes: son unas 6–8 **rampas**
> de 4–5 tonos cada una. Contar rampas es más útil que contar colores.

### 2.2 Rampas y desplazamiento de tono (*hue shifting*)

Una **rampa** es la serie de colores que usas para pintar un mismo material de la sombra a la
luz. La forma ingenua de construirla —coger un color y bajar/subir el brillo— produce un
resultado plano y sucio: es el error número uno del pixel art principiante.

La técnica correcta se llama **hue shifting** (desplazamiento de tono):

> **Al oscurecer, gira el tono hacia el azul/violeta y sube la saturación.
> Al aclarar, gira el tono hacia el amarillo/naranja y baja la saturación.**

Es decir, en una rampa de 5 pasos las tres propiedades HSV se mueven **a la vez**:

| Paso | Tono (H) | Saturación (S) | Brillo (B) |
|---|---|---|---|
| Sombra profunda | girado hacia azul/violeta | media | muy bajo, rara vez 0 |
| Sombra | girado hacia el frío | alta | bajo |
| Base | referencia | **máxima de la rampa** | medio |
| Luz | girado hacia el cálido | alta | alto |
| Brillo | girado más hacia amarillo | media-baja | muy alto, rara vez 100 |

**Cuánto girar**, con cifras de Raymond Schlitter (Slynyrd), que documenta su paleta *Mondo*
—128 colores en **8 rampas de 9 muestras**— en el primer artículo de su *Pixelblog*:

- **+20° de tono entre muestra y muestra** de una misma rampa. Escribe literalmente que
  *«20 is about as high as I go»*: más que eso y la rampa deja de leerse como un solo material.
- **45° entre rampa y rampa**, para que las 8 rampas recorran el círculo cromático completo.
- La **saturación hace pico en el centro** de la rampa y **nunca llega a 100 ni a 0**.
- El **brillo sube de forma constante** de un extremo al otro y normalmente **no arranca en 0**,
  salvo que quieras negro puro.
- Añade al final **unos cuantos neutros desaturados** para equilibrar los tonos vibrantes.

Por qué funciona: la luz real tiene color (el sol es cálido, la sombra la rellena el cielo,
que es frío). Una rampa que solo cambia el brillo describe un objeto iluminado por una bombilla
gris en un cuarto gris. Una rampa con hue shifting describe un objeto en el mundo.

**Compartir rampas es lo que hace que una paleta parezca una paleta.** Que la sombra de la
piel y la luz de la madera sean el mismo color no es un descuido: es lo que ata la imagen.

### 2.3 Contraste y legibilidad: el valor manda

Prueba infalible: **pasa tu sprite a escala de grises**. Si en gris se sigue leyendo qué es
cada cosa, la imagen funciona. Si se convierte en una mancha uniforme, tienes un problema de
**valor**, no de color, y ningún ajuste de tono lo va a arreglar.

Reglas prácticas:

- **El personaje debe contrastar en valor con el fondo**, no solo en tono. Un daltónico y un
  jugador con el brillo del monitor mal calibrado deben distinguirlo igual.
- **Baja el contraste del fondo.** El truco más eficaz de un pixel artist no es hacer el
  personaje más llamativo: es **apagar el escenario** (menos saturación, rango de valores más
  estrecho, tonos más fríos).
- **Reserva los extremos.** El color más claro y el más oscuro de la paleta son munición:
  úsalos para lo importante (el filo del arma, la pupila, el objeto interactuable), no para
  rellenar una pared.
- **Peligro y recompensa tienen color propio.** Si el rojo saturado solo aparece en lo que
  hace daño, el jugador lo aprende sin que se lo digas.

### 2.4 Paletas conocidas de Lospec

Lospec no escribe los tutoriales: es un **catálogo** (4 457 paletas y 586 tutoriales
comprobados el 6 de septiembre de 2026) que exporta a HEX, PNG, GPL, PAL y ASE, listos para
Aseprite, GIMP o Paint.NET. Estas doce están verificadas una a una:

| Paleta | Colores | Autor / origen | URL |
|---|---:|---|---|
| **1bit Monitor Glow** | 2 | Polyducks | <https://lospec.com/palette-list/1bit-monitor-glow> |
| **SLSO8** | 8 | Luis Miguel Maldonado | <https://lospec.com/palette-list/slso8> |
| **PICO-8** | 16 | consola virtual de Lexaloffle | <https://lospec.com/palette-list/pico-8> |
| **Sweetie 16** | 16 | GrafxKid · paleta por defecto de TIC-80 | <https://lospec.com/palette-list/sweetie-16> |
| **NA16** | 16 | Nauris (`namatnieks`) | <https://lospec.com/palette-list/na16> |
| **Steam Lords** | 16 | Slynyrd | <https://lospec.com/palette-list/steam-lords> |
| **Vinik24** | 24 | Vinik | <https://lospec.com/palette-list/vinik24> |
| **Endesga 32 (EN32)** | 32 | ENDESGA, creada para *NYKRA* | <https://lospec.com/palette-list/endesga-32> |
| **Apollo** | 46 | AdamCYounis | <https://lospec.com/palette-list/apollo> |
| **AAP-64** | 64 | Adigun A. Polack | <https://lospec.com/palette-list/aap-64> |
| **Journey** | 64 | PineappleOnPizza | <https://lospec.com/palette-list/journey> |
| **Resurrect 64** | 64 | Kerrie Lake | <https://lospec.com/palette-list/resurrect-64> |

> 🔺 **Apollo tiene 46 colores, no 48.** Es un error que se repite en artículos de segunda mano.

Dos que merecen atención por lo que enseñan, no solo por lo que dan:

- **Sweetie 16** se describe a sí misma como *«4 ramps with hue shifting»*: 16 colores = 4 rampas
  de 4. Es la demostración más corta de que **una paleta son rampas, no colores sueltos**.
- **Vinik24** son *«connected ramps of four shades, all sharing the same shadow and the same
  highlight»*: seis rampas de cuatro tonos que **comparten el color más oscuro y el más claro**.
  Ese es el truco de economía que hace que 24 colores rindan como 40.

Y una paleta que no está en Lospec y sigue siendo el mejor ejercicio de iniciación: **los 4
verdes de la Game Boy original**. Con cuatro tonos solo puedes pensar en **valor**, que es
exactamente lo que hay que aprender primero.


### 2.5 Cómo elegir una para tu proyecto

1. **Decide el número de colores por el alcance del juego, no por gusto.** Un jam de 48 horas
   con 16 colores termina; con 64 no.
2. **Comprueba que la paleta tiene las rampas que necesitas.** Si tu juego es una cueva y la
   paleta solo tiene una rampa fría de 3 pasos, te vas a quedar corto. Cuenta rampas.
3. **Comprueba el rango de valores.** Convierte la paleta a gris: si no hay un negro casi puro
   y un blanco casi puro, no vas a poder hacer contraste fuerte.
4. **Reserva 2–4 colores para la interfaz** y no los uses en el mundo. Así el HUD nunca se
   confunde con el escenario.
5. **Empieza con una prestada, termina con la tuya.** Coge una paleta de Lospec, pinta tres
   sprites y un tile, y **ajústala**: quita lo que no usas, añade lo que te falta. Una paleta
   ajena sin retocar suele delatar que no se ha pensado el juego.
6. **Guárdala como archivo.** Aseprite exporta e importa `.gpl`, `.pal`, `.aco` y `.hex`;
   GameMaker guarda paletas dentro del propio sprite en su editor de imagen.

### 2.6 Paletas dentro de GameMaker

- **Editor de imagen del IDE.** Cada sprite lleva su propia paleta de muestras. Con
  `Ctrl`/`Cmd` + clic sobre una muestra la editas; desde **Opciones de la paleta de colores**
  puedes **copiar los colores de un sprite y aplicarlos a otro**. Es suficiente para retoques,
  no para producción seria.
- **Intercambio de paleta en runtime.** Recolorear sin duplicar sprites (equipos de un
  multijugador, variantes de enemigo, daltonismo) se resuelve con un shader de sustitución.
  La librería libre **Chameleon** ya lo trae hecho; está catalogada en
  [12 · 05 §1](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md).
- **Tintado barato.** Para un flash de daño no hace falta shader:

```gml
/// obj_enemigo · Step — cuenta atrás del parpadeo
if (parpadeo > 0) parpadeo -= 1;

/// obj_enemigo · Draw — flash de color plano sin shader
if (parpadeo > 0)
{
    // La niebla cubriendo todo el rango de profundidad de la cámara 2D
    // pinta el sprite entero del color indicado, conservando el alfa.
    gpu_set_fog(true, c_white, -16000, 16000);
    draw_self();
    gpu_set_fog(false, c_black, 0, 1);
}
else
{
    draw_self();
}
```

> ⚠️ `image_blend` **multiplica**: solo puede oscurecer o teñir, nunca aclarar. Para el
> clásico «todo el sprite en blanco un frame» hay que usar `gpu_set_fog()` como arriba, o un
> shader. Es el motivo por el que tanto tutorial antiguo dice que «`image_blend = c_white` no
> hace nada»: efectivamente, no hace nada.

---

## 3 · Las técnicas: qué separa un sprite limpio de uno sucio

### 3.1 Líneas limpias: *jaggies* y *banding*

Una línea en pixel art es una **secuencia de tramos rectos**. La calidad de la línea depende
de que esos tramos sigan un patrón regular.

- **Jaggies** («dientes»): un tramo que rompe el patrón. En una diagonal de tramos de 2 px,
  un tramo de 1 o de 3 salta a la vista como un diente.

  ```
  MAL (jaggies)          BIEN (patrón 2-2-2)
  ██                     ██
    █                      ██
    ███                      ██
       █                       ██
  ```

- **Patrones que funcionan**: constantes (`1-1-1-1`, `2-2-2-2`, `3-3-3-3`) o crecientes de
  forma monótona (`1-2-3-4`, `4-3-2-1`). Nunca `2-1-2-3-2`.

- **Banding** («bandeo»). La definición precisa es de cure: *«banding, most simply, is when
  pixels line up. When neighbor pixels end at the same x or y coordinate on the underlying
  grid, the grid immediately becomes more evident»*. Es decir: dos tramos paralelos que
  terminan en la misma columna o fila **hacen visible la rejilla** y aplanan la forma.
  Subtipos con nombre propio: **hugging** (el contorno abraza la forma que envuelve),
  **staircase banding** (bandas gruesas en escalera), **skip-one banding** (queda un hueco de
  1 px y la mente lo rellena igual) y **45 degree banding**. Se arregla dejando que la segunda
  línea **se despegue** cada pocos píxeles, o eliminando la interior.

- **Doble píxel**: en una diagonal, evitar que dos píxeles del mismo tramo se toquen solo por
  la esquina cuando el resto se toca por el lado. Ese píxel «suelto» es el error clásico del
  dibujo hecho con el ratón a mano alzada.

**Consecuencia práctica:** dibuja con **lápiz de 1 px**, sin suavizado, y con la cuadrícula
de 1 px encendida. En el editor de imagen de GameMaker eso es *Toggle Canvas Grid*; en
Aseprite, `View → Grid`. Cualquier herramienta que difumine (aerógrafo, pincel suave,
selección con *feather*) sobra.

### 3.2 Clusters: la unidad real del pixel art

Un **cluster** es un grupo de píxeles del mismo color que forma una mancha. El pixel art
bueno se compone de **pocos clusters grandes y bien formados**; el malo, de muchos clusters
pequeños y píxeles sueltos.

Síntomas: **píxeles huérfanos** (uno rodeado de otro color: a tamaño real parece suciedad),
**ruido** (manchas de 1–2 px repartidas, que se leen como textura sucia y no como material) y
**clusters con forma imposible** (una sombra en sierra no describe ninguna geometría real).
Como dice cure en el tutorial de Pixel Joint: *«in the wild, pixels travel in packs»*.

Prueba rápida: **entorna los ojos** o mira la imagen al 100 %. Lo que se vuelve ruido gris sobra.

### 3.3 Anti-aliasing manual

El anti-aliasing (AA) en pixel art es **manual y selectivo**: colocas a mano píxeles de un
color intermedio en el punto donde una curva cambia de tramo, para suavizar el escalón.

Reglas:

1. **Solo en los cambios de pendiente**, nunca a lo largo de un tramo recto.
2. **Un solo píxel intermedio** por escalón en resoluciones bajas; dos como mucho en arte
   grande.
3. **El color intermedio sale de la rampa**, no de mezclar en RGB. Si no tienes un color
   intermedio en la paleta, probablemente no necesitas AA ahí.
4. **Nunca hagas AA contra el fondo transparente en un sprite móvil.** El píxel intermedio
   asume un color de fondo concreto; si el sprite pasa por delante de otra cosa, aparece un
   halo. AA contra transparencia solo en elementos que siempre se ven sobre el mismo fondo
   (una interfaz, un logotipo).
5. **En resoluciones muy bajas (sprites de 16 px), casi siempre sobra.** El AA come contraste
   y el contraste es lo único que tienes.

### 3.4 Dithering: cuándo sí y cuándo no

El **dithering** entrelaza dos colores en un patrón (tablero de ajedrez, líneas, Bayer) para
sugerir un tercero que no existe en la paleta.

| Cuándo **sí** | Cuándo **no** |
|---|---|
| Degradados amplios de fondo: cielo, agua profunda, niebla | En sprites pequeños que se mueven: el patrón vibra |
| Texturas de material: piedra rugosa, óxido, tela vieja | En bordes y siluetas: destroza la lectura |
| Cuando la paleta es corta a propósito y el dithering **es** el estilo | Como sustituto de una rampa: añade el tono a la paleta, será más limpio |
| Transiciones demasiado duras entre dos colores de la misma rampa | Si vas a escalar de forma no entera: se convierte en muaré |

Tipos, de menos a más agresivo: **50 %** (damero), **25 % / 75 %**, **Bayer 2×2 / 4×4 / 8×8**.
Los degradados largos encadenan densidades: 75 % → 50 % → 25 % → 0 %. Apunte histórico de
cure que sigue vigente: en un **CRT** la pantalla difuminaba la trama y el dithering era casi
gratis; en un **LCD** el patrón ya no se esconde, así que es mucho menos versátil que antes.

> ⚠️ El dithering y el filtrado de texturas son enemigos declarados. Si dejas
> «Interpolate colours between pixels» activado (§6.1), tu dithering se convertirá en un
> gris plano borroso.

### 3.5 Sombreado: la luz tiene dirección

**Define una fuente de luz para todo el juego y no la muevas.** La convención más común es
arriba a la izquierda, pero cualquiera vale mientras sea consistente: el problema no es la
dirección, es que cada sprite tenga la suya.

El error canónico es el ***pillow shading*** («sombreado de almohada»): oscurecer los bordes
y aclarar el centro de la forma de manera uniforme, sin dirección. El resultado parece un
cojín inflado y no describe ningún volumen.

```
PILLOW SHADING (mal)        LUZ DIRECCIONAL (bien)
    ▒▒▒▒▒▒                      ░░░░▒▒
  ▒▒░░░░░░▒▒                  ░░░░▒▒▒▒▓▓
  ▒▒░░██░░▒▒                  ░░▒▒▒▒▓▓▓▓
  ▒▒░░░░░░▒▒                  ▒▒▒▒▓▓▓▓██
    ▒▒▒▒▒▒                      ▓▓▓▓██
```

Los elementos que sí describen volumen:

| Elemento | Qué es | Error habitual |
|---|---|---|
| **Luz directa** | La cara que mira a la fuente | Olvidarla y dejar todo en tono base |
| **Medio tono / base** | La transición | Hacerla demasiado ancha; se aplana |
| **Sombra propia** | La cara opuesta a la luz | Que sea solo «el base más oscuro» sin hue shifting |
| **Luz de rebote** | Un tono más claro en el borde inferior de la sombra | No usarla; el objeto queda recortado y muerto |
| **Sombra proyectada** | La que el objeto arroja sobre el suelo | Olvidarla: el personaje flota |
| **Especular** | El punto de máximo brillo en materiales pulidos | Ponerlo en materiales mates |

Y la regla de coste/beneficio: **la sombra proyectada bajo el personaje es el píxel mejor
invertido de todo el sprite**. Sin ella, nada está apoyado en el suelo.

### 3.6 Silueta y lectura a distancia

La prueba definitiva de un sprite: **rellénalo de negro sólido**. Si sigues sabiendo qué es
y en qué estado está, la silueta funciona. Si dos enemigos distintos dan la misma mancha
negra, uno de los dos está mal diseñado.

- **Cada personaje, una silueta única**: distintos en altura, anchura y contorno, no solo
  en color.
- **Las poses de acción también tienen silueta.** Si el ataque no cambia la silueta, el jugador
  no lo verá con la pantalla llena.
- **Nada importante debe leerse solo por color** — ver
  [04 · 27 — Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md).
- **Comprueba a tamaño real, en movimiento y sobre el fondo real.** Un sprite bonito al 800 %
  sobre fondo blanco no dice nada.

### 3.7 Subpíxel en el dibujo (no en el motor)

«Subpíxel» tiene dos significados y conviene no mezclarlos:

- **Subpíxel en el motor** (§1.5): renderizar a más resolución que la base.
- **Subpíxel en el dibujo**: usar el color para sugerir que algo se ha movido menos de un
  píxel. Si una antena debe moverse «medio píxel», dibujas el píxel con un tono intermedio
  entre la antena y el fondo. El ojo interpreta el desplazamiento aunque la rejilla no lo
  permita.

Es la técnica que hace que una animación de 16 px parezca fluida sin añadir frames. Se usa
sobre todo en el **idle** y en los movimientos pequeños de la cara.

### 3.8 Tiles que casan y cómo romper la repetición

Un tile es **casable** (*tileable*) cuando su borde derecho continúa en su borde izquierdo y
su borde inferior en el superior, sin costura visible.

Método fiable en cualquier editor: dibuja el tile, **desplázalo la mitad de su tamaño en X e
Y** (en Aseprite, `Edit → Shift`, o el filtro de *offset*), y arregla la costura que ahora
queda en el centro. Repite hasta que no se vea nada.

Lo que delata a un tileset amateur:

| Problema | Síntoma | Solución |
|---|---|---|
| **Costura** | Línea visible entre tiles | Desplazar y retocar; comprobar los cuatro bordes |
| **Repetición evidente** | Un detalle llamativo se ve en rejilla | Quitar el detalle del tile base; llevarlo a variantes |
| **Rejilla visible** | Se «ve» la cuadrícula aunque no haya costura | Que los clusters crucen el borde del tile |
| **Ruido uniforme** | Todo textura, nada de descanso | Dejar zonas planas: el ojo necesita descansar |

Cómo romper la repetición **sin dibujar cien tiles**:

1. **Un tile base plano y aburrido** + **3–6 variantes con un detalle cada una**, colocadas
   con poca probabilidad. El 80 % de la pared es el tile aburrido.
2. **Decoración en una capa aparte** (grietas, hierba, manchas), no dentro del tile. En
   GameMaker eso es una *asset layer* encima de la *tile layer*.
3. **Variación de valor, no de forma**: dos o tres versiones del mismo tile con un punto de
   luz distinto ya rompen la sensación de rejilla.
4. **Autotiles** para los bordes: GameMaker trae *auto tiling* de 16 y 47 piezas en el editor
   de tilesets. Lo cubre [03 · 17 — Autotiles](../03%20-%20Cursos%20%28YouTube%29/17%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Autotiles.md).

### 3.9 Contorno (*outline*) selectivo

El contorno es la técnica de estilo más elemental del pixel art y, a la vez, la más mal
entendida: no es una única decisión («¿lleva línea o no?»), son **dos decisiones
independientes** — qué color lleva la línea, y dónde se dibuja.

**Decisión 1 — de qué color es la línea:**

| Estilo | Cómo se hace | Efecto |
|---|---|---|
| **Contorno negro puro** | Un píxel de `#000000` (o casi) rodeando toda la silueta | Máximo contraste con cualquier fondo; look «Game Boy» / cómic clásico. Riesgo: aísla el sprite del entorno como una pegatina recortada — cuanto más colorido el fondo, más artificial se ve |
| **Contorno selectivo (de color extraído de la rampa)** | El tono **más oscuro de la rampa de ese color** (la sombra final de §2.2 *Hue shifting*), no negro puro | El sprite se integra mejor con el escenario; es el estilo dominante en pixel art moderno de gama alta (*Celeste*, *Owlboy*, *Eastward*). Exige tener ya la rampa de cada color resuelta |
| **Contorno perdido (*lost edges*)** | El contorno selectivo, pero **se interrumpe** donde el valor ya separa dos zonas por sí solo — por ejemplo donde el lado iluminado de un brazo casi toca un fondo claro | La técnica más avanzada: la línea «entra y sale» de la silueta según haga falta, en vez de rodearla entera. Cuesta más disciplina de valor (§2.3) pero da el resultado menos plano |

**Decisión 2 — dónde se dibuja la línea:**

- **Borde externo únicamente**: separa la silueta completa del fondo. Es lo mínimo necesario
  para que el sprite se lea sobre cualquier escenario, y lo único imprescindible en
  resoluciones muy bajas.
- **Líneas internas**: separan zonas *dentro* del propio sprite que el sombreado por sí solo
  no distingue (el borde entre una manga y el torso, del mismo material y casi el mismo
  valor). Solo compensan a partir de sprites medianos-grandes (24-32 px de alto en adelante);
  por debajo, cada línea interna es un cluster entero gastado en separar en vez de en dar
  volumen — exactamente el coste que se explica a continuación.

**El coste real: contorno frente a presupuesto de píxeles.** Un contorno externo de 1 px
alrededor de un sprite de 16×16 no añade 1 px de silueta: **la resta**, porque ese anillo de
contorno ocupa espacio que antes podía ser rampa de luz/sombra (§2.2, §3.5). En un sprite de
16 px de alto, un contorno de 1 px arriba y 1 px abajo ya es un 12 % del alto total dedicado
a separación, no a volumen. Es la razón real —no solo estética— de que juegos de resolución
muy baja (8-16 px) prescindan del contorno por completo y confíen únicamente en el contraste
de valor con el fondo (§2.3): a esa escala, cada píxel de contorno es un píxel que no puede
ser sombra, luz ni detalle.

**Regla práctica**: si tu paleta de escenario ya separa bien el personaje por valor (prueba
de escala de grises de §2.3), el contorno es redundante y cuesta píxeles que no necesitas. Si
el fondo es denso, oscuro o cambia mucho de color (un shmup con fondos variados, por
ejemplo), el contorno externo compensa su coste porque es la única garantía de legibilidad
constante.

**Implementación en GameMaker — tres vías, no confundirlas:**

1. **Dibujado a mano en el sprite** (la vía por defecto). El contorno es parte de los
   píxeles del sprite: coste de ejecución cero, pero fijo — para cambiarlo hay que reeditar
   el sprite en Aseprite. Es la vía correcta para el 95 % de los casos de este documento.
2. **Contorno en tiempo real por shader**, para resaltar dinámicamente un objeto (selección,
   objeto interactivo, *outline* de un enemigo marcado). Ya está resuelto con vertex+fragment
   shader completos en [08 · 06 §6.2 — Contorno (outline)](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md#62-contorno-outline);
   no se repite aquí.
3. **Sprite dilatado sin shader** (el truco «del pobre», útil si el proyecto no quiere montar
   un pipeline de shaders para un solo efecto puntual): dibujar el sprite desplazado 1 px en
   8 direcciones con un color plano forzado, y el sprite real encima.

   ```gml
   /// obj_objeto_interactivo · Draw — contorno por sprite dilatado (sin shader)
   if (resaltado)
   {
       // gpu_set_fog fuerza un color plano sobre cualquier dibujado 2D (08 · 23 §3.1, vía C:
       // truco verificado en su comportamiento oficial, no como técnica de contorno documentada)
       gpu_set_fog(true, color_contorno, 0, 1);
       for (var _i = 0; _i < 8; _i++)
       {
           var _dir = _i * 45;
           draw_sprite_ext(sprite_index, image_index,
                            x + lengthdir_x(1, _dir), y + lengthdir_y(1, _dir),
                            image_xscale, image_yscale, image_angle, c_white, image_alpha);
       }
       gpu_set_fog(false, c_black, 0, 1);
   }

   draw_self();   // el sprite real, siempre encima de las 8 copias del contorno
   ```

   > ⚠️ Nueve dibujados por instancia (8 copias + el sprite real) es barato para unos pocos
   > objetos resaltados, pero **no lo apliques a docenas de instancias a la vez**: multiplica
   > directamente el *overdraw* de esa zona de pantalla — ver
   > [01 · 15 — Overdraw](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#overdraw).

---

## 4 · Animación en pixel art

> Aquí se trata **qué dibujar y cuántos frames**. La reproducción en GameMaker
> (`image_speed`, tipos de velocidad, Sequences, Animation Curves, máquinas de estado de
> animación) está en
> [13 · 04 — Animación de sprites, Sequences y Animation Curves](./04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md).

### 4.1 Frames clave primero, intermedios después

Nunca animes «frame 1, frame 2, frame 3…». Dibuja primero **las poses extremas** y después
rellena. En un puñetazo: anticipación (retrocede), extremo (brazo estirado), recuperación.
Tres dibujos que ya cuentan la acción. En pixel art **un frame clave bien dibujado vale más
que cuatro intermedios mediocres**, y cuesta cuatro veces menos.

### 4.2 Timing: los frames no duran lo mismo

El error de principiante es dar a todos los frames la misma duración. El *timing* es lo que
da peso:

| Momento | Duración relativa | Por qué |
|---|---|---|
| Anticipación | Larga (2–4 frames de juego) | Avisa al jugador de lo que viene |
| Extremo / impacto | **Muy corta** (1 frame) o congelada | El golpe se siente por lo súbito |
| Recuperación | Media | Devuelve el control |
| Reposo | Larga | Descanso visual |

GameMaker anima un sprite a velocidad constante (`image_speed` es un multiplicador global del
sprite), así que para conseguir tiempos distintos por frame tienes dos vías: **duplicar
frames** en la hoja (el frame que dura el doble aparece dos veces) o **controlar
`image_index` a mano**. La primera es la que usa todo el mundo en pixel art y la que exportan
por defecto las hojas de Aseprite.

### 4.3 Ciclos de andar: 4, 6 u 8 frames

| Frames | Coste | Sensación | Cuándo |
|---|---|---|---|
| **2** | Trivial | Caricaturesco, tipo Game Boy | Enemigos de fondo, sprites de 8–16 px |
| **4** | Bajo | Legible y funcional; el estándar indie | Sprites de 16–32 px, muchos personajes |
| **6** | Medio | Fluido sin ser caro | Protagonista de un juego de 32 px |
| **8** | Alto | Muy fluido, cine | Protagonista de 48 px o más, o juegos con pocos personajes |

Estructura de un ciclo de 8 frames (los cuatro primeros se **espejan** para los cuatro
últimos si el personaje es simétrico, lo que reduce el trabajo a la mitad):

1. **Contacto** — pie delantero toca el suelo, piernas más abiertas.
2. **Descenso** — el peso baja; el cuerpo está en su punto **más bajo**.
3. **Paso** — piernas juntas bajo el cuerpo.
4. **Elevación** — el cuerpo está en su punto **más alto**.
5–8. Lo mismo con la pierna contraria.

En un ciclo de 4 frames se conservan **contacto** y **paso** de cada lado. La clave, aunque
solo tengas 4 frames: **el cuerpo tiene que subir y bajar 1 píxel**. Un ciclo sin ese
rebote parece que el personaje patina.

### 4.4 El *idle* no es un frame quieto

Un personaje inmóvil se lee como un error del juego. El *idle* mínimo son **2 frames** con el
cuerpo desplazado 1 píxel en vertical, a velocidad baja (2–4 frames de juego por imagen). Con
4 frames puedes añadir respiración: pecho, hombros y pelo se mueven en momentos distintos
(**desfase**: no todo empieza y acaba a la vez).

Un truco barato y muy eficaz: **un idle secundario** que se dispara tras N segundos sin
input (el personaje bosteza, mira alrededor, ajusta el arma). Cuesta poco y da personalidad.

### 4.5 *Smears*: cómo animar movimientos rápidos

Un ***smear*** (o *multiple*) es un frame deliberadamente deformado que representa el
movimiento entre dos poses: un brazo estirado en un arco, una espada convertida en un
abanico, un puño alargado. Se ve un solo frame y el ojo no lo procesa como dibujo, sino como
velocidad.

Reglas:

**Un smear dura 1 frame** (dos y parece un error), **va entre dos poses claras** —nunca al
principio ni al final— y **puede romper la anatomía por completo**: es su trabajo. Variantes:
**estirar** la forma en la dirección del movimiento, **multiplicar** la parte (tres brazos
translúcidos) o dibujar el **arco** que recorre el objeto.

Es la técnica que hace que un ataque de 3 frames se sienta rápido en vez de pobre. Combínala
con el *hit stop* de [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) §4.2:
el smear vende la velocidad, la congelación vende el impacto.

### 4.6 Subpíxel en el movimiento del personaje

Si tu juego usa rejilla estricta (§1.5), un personaje que se mueve a 0,7 px por frame
avanzará 0, 1, 0, 1, 1, 0… píxeles: el movimiento se ve a tirones aunque la velocidad sea
constante. La solución **no** es redondear la posición, sino **guardar la posición real y
redondear solo al dibujar**:

```gml
/// obj_jugador · Create
pos_real_x = x;
pos_real_y = y;

/// obj_jugador · Step — la física trabaja con decimales
pos_real_x += velocidad_x;
pos_real_y += velocidad_y;

// La posición "oficial" (colisiones, cámara) se queda en enteros
x = floor(pos_real_x);
y = floor(pos_real_y);
```

> 🔺 **`floor()` y no `round()` para la posición del personaje**, porque `round()` cambia de
> valor en `.5` y produce un desplazamiento asimétrico al ir a la izquierda y a la derecha.
> Para la **cámara**, en cambio, se usa `floor()` o `round()` de forma consistente: lo
> importante es que nunca llegue un decimal a `camera_set_view_pos()` (§6.5).

---

## 5 · Flujo de trabajo con Aseprite

> Qué herramienta elegir (Aseprite, LibreSprite, Piskel, Pixelorama, GraphicsGale) está en
> [07 · 09 §3](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md).
> **Automatizar** el ciclo Aseprite → GameMaker (AseSync, conveyorbelt, GM Link, GM-Sprite-Importer)
> está en [12 · 05 §1](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md).
> Aquí va **el flujo manual**, que es el que hay que entender antes de automatizarlo.

### 5.1 Capas

Aseprite distingue cuatro tipos: **Background Layer** (opaca, única, siempre abajo, no se
mueve), **Transparent Layer** (con alfa, apilable), **Layer Group** (*«handle a set of layers
as one unit»*) y **Tilemap Layer** (desde la v1.3).

Organización que funciona para un personaje de juego:

```
[Grupo] EFECTOS      → destellos, polvo, smears (se exportan aparte o se funden)
[Grupo] EQUIPO       → arma, casco, capa   (capas separadas = intercambiables)
[Grupo] CUERPO       → líneas · color · sombra
[Capa]  REFERENCIA   → boceto o rotoscopia, oculta al exportar
[Fondo] gris medio   → nunca blanco: cansa la vista y falsea el juicio del color
```

> 💡 Slynyrd trabaja **sobre fondo gris**, no blanco, por esas dos razones. Cuesta cero y se
> nota desde el primer sprite.

Cada capa tiene *visibility*, *lock*, *name* y **continuous** (cómo se crean las celdas nuevas).

### 5.2 Tags: una animación por etiqueta

Un **tag** marca un rango de frames como una animación. Es la pieza que conecta el arte con el
código: `idle`, `walk`, `jump`, `attack`, `hurt`, `death`.

- Se crea seleccionando el rango en la línea de tiempo → *Frame → Tags → New Tag*, o pulsando
  **F2 dos veces** (la primera crea una etiqueta «Loop», la segunda abre sus propiedades).
- La propiedad importante es **Animation Direction**, con tres modos documentados oficialmente:
  **Forward**, **Reverse** y **Ping-pong**. La v1.3 añadió además un campo **Repeat**.
- **Onion skinning** (papel cebolla) con **F3**: ver los frames anterior y siguiente
  semitransparentes mientras dibujas, con tinte rojo/azul configurable.

**Convención que ahorra disgustos:** un `.aseprite` por personaje, con **todas** sus
animaciones en tags dentro del mismo archivo. Así la paleta, el tamaño de lienzo y el pivote
son los mismos para todo, que es justo lo que se rompe cuando se trabaja con un archivo por
animación.

### 5.3 Exportar: hoja de sprites y JSON

El diálogo *File → Export Sprite Sheet* sirve para un caso puntual. Para producción se usa la
**línea de órdenes**, que además es lo único bien documentado (la sección de CLI del manual del
diálogo está marcada como *work in progress* desde hace años).

```sh
# Una animación completa: hoja horizontal + metadatos
aseprite -b jugador.aseprite \
         --sheet-type horizontal \
         --sheet spr_jugador.png \
         --data  spr_jugador.json \
         --format json-array \
         --list-tags --list-layers

# Un atlas empaquetado de varios archivos, con margen entre formas
aseprite -b arte/*.aseprite \
         --sheet-pack --sheet-width 1024 --sheet-height 1024 \
         --shape-padding 2 --border-padding 2 --extrude \
         --sheet atlas.png --data atlas.json --format json-array
```

Opciones que de verdad usarás: `-b` (sin interfaz), `--sheet-type`
(`horizontal`/`vertical`/`rows`/`columns`/`packed`), `--sheet-pack`, `--data`, `--format`
(`json-hash` por defecto, **`json-array` si vas a leerlo con código**), `--split-tags`,
`--split-layers`, `--trim`, `--extrude`, `--shape-padding`, `--scale`, `--list-tags`,
`--list-layers`, `--list-slices`, `--filename-format` (tokens `{title}`, `{layer}`, `{tag}`,
`{frame}`, `{extension}`).

Forma del JSON con `--format json-array`:

```jsonc
{
  "frames": [
    { "filename": "jugador 0.aseprite",
      "frame":            { "x": 0, "y": 0, "w": 32, "h": 32 },
      "rotated":          false,
      "trimmed":          false,
      "spriteSourceSize": { "x": 0, "y": 0, "w": 32, "h": 32 },
      "sourceSize":       { "w": 32, "h": 32 },
      "duration":         100 }        // milisegundos
  ],
  "meta": {
    "app": "http://www.aseprite.org/", "version": "…",
    "image": "spr_jugador.png", "format": "RGBA8888",
    "size": { "w": 256, "h": 32 }, "scale": "1",
    "frameTags": [ { "name": "walk", "from": 0, "to": 3 } ],   // solo con --list-tags
    "layers":    [ { "name": "cuerpo" } ]                      // solo con --list-layers
  }
}
```

Tres trampas reales al escribir un importador:

1. **`frameTags` NO aparece si no pasas `--list-tags`.** Los ejemplos oficiales de JSON que
   enlaza Aseprite son de la v1.1 y no lo incluyen; media internet copia ese ejemplo y luego
   se pregunta por qué su importador no ve las etiquetas.
2. **`frame.x` / `frame.y` son píxeles dentro del PNG**, no índices de celda. Con
   `--sheet-pack` caen donde el empaquetador decida.
3. **`duration` está en milisegundos**, no en frames de juego. Convertir requiere conocer la
   velocidad de la room.

### 5.4 Importar en GameMaker

**La vía sencilla y la que deberías usar el 90 % de las veces: las tiras `_stripN`.**

GameMaker reconoce una convención de nombre: si un PNG contiene los frames dispuestos **en
horizontal de izquierda a derecha** y el archivo se llama `nombre_stripN.png`, donde `N` es el
número de frames, al arrastrarlo al IDE (o al importarlo con el botón *Import* del editor de
sprites) **se convierte automáticamente en un sprite animado**. El sufijo `_stripN` se elimina
del nombre del asset.

> El ancho de cada frame será **el ancho total de la tira dividido entre N**. Una tira de
> 250 px con 5 frames da frames de 50 px. Si el ancho total no es múltiplo de N, los frames
> saldrán descuadrados: comprueba siempre esa división.

Por eso `--sheet-type horizontal` es la opción correcta al exportar desde Aseprite: produce
exactamente la tira que GameMaker espera.

Y la vía en tiempo de ejecución, para mods, contenido descargable o un editor dentro del juego:

```gml
/// Cargar una tira desde disco en tiempo de ejecución
// sprite_add(fichero, num_frames, quitar_fondo, suavizar, x_origen, y_origen)
// - quitar_fondo y suavizar deben ir a FALSE en pixel art
// - el origen se da en píxeles dentro del frame
var _spr = sprite_add("arte/jugador_strip6.png", 6, false, false, 16, 32);

if (!sprite_exists(_spr))
{
    show_debug_message("No se pudo cargar la tira del jugador");
}
else
{
    sprite_set_speed(_spr, 10, spritespeed_framespersecond);  // 10 fps reales
    sprite_index = _spr;
}
```

> 🔺 `sprite_add()` **no** lee el JSON de Aseprite: solo la imagen. Si quieres las etiquetas,
> tienes que leer el `.json` tú con `json_parse()` y guardarte los rangos `from`/`to` en un
> struct. Y recuerda `sprite_delete()` cuando ya no lo necesites: los sprites cargados en
> runtime no los libera nadie por ti.

> 🔺 Tres avisos del manual sobre `sprite_add()` que afectan al pixel art:
> **(1)** `removeback` decide qué color quitar mirando **el píxel de abajo a la izquierda**, y
> `smooth` crea un borde semitransparente: los dos arruinan un sprite de bordes duros, por eso
> van a `false`. **(2)** En **HTML5** y al cargar desde una URL, la carga es **asíncrona** y
> dispara el evento **Image Loaded**; desde un servidor seguro puede hacer falta
> `http_set_request_crossorigin()`. **(3)** Un sprite cargado así ocupa **más memoria de la
> esperada**: se guarda como página de textura *y* en memoria de GPU.

---

## 6 · Los ajustes de GameMaker que arruinan el pixel art

### 6.1 «Interpolate colours between pixels»: el ajuste número uno

Es, con diferencia, **el problema más frecuente de los usuarios nuevos de GameMaker**: el
sprite se ve nítido en el editor y borroso al ejecutar. La causa es el filtrado bilineal de
texturas, y se apaga en un sitio:

```
Game Options → [tu plataforma] → Graphics → ☐ Interpolate colours between pixels
```

El equivalente en código, que puedes cambiar en cualquier momento, es
`gpu_set_texfilter(false)`. El diagnóstico completo, con las tres soluciones y el caso de la
interfaz en alta definición, está en
[03 · 36 — ¿Por qué todo se ve borroso?](../03%20-%20Cursos%20%28YouTube%29/36%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Por%20Qué%20Todo%20se%20ve%20Borroso.md).
Lo que ese documento no dice y aquí importa: **el valor por defecto depende de la plataforma**,
así que un juego que se ve bien en macOS puede salir borroso en Windows sin que toques nada.

| Plataforma | «Interpolate colours between pixels» por defecto |
|---|---|
| Windows | **Activado** |
| HTML5 · Opera GX · GX Games · Reddit | **Activado** |
| Android · Amazon Fire | **Activado** |
| macOS | Desactivado |
| iOS · tvOS | Desactivado |
| Ubuntu (Linux) | Desactivado |
| Windows UWP | Desactivado |

> 🔺 **Hay que desmarcarlo en cada plataforma de exportación, una por una.** No es un ajuste
> global. Y la función `gpu_set_texfilter()` documenta su propio valor por defecto como
> `false`, que es lo que hace tan confuso el asunto: el ajuste del proyecto lo sobreescribe al
> arrancar.

Nombres que **no existen** y que la gente inventa constantemente:
`texture_set_interpolation`, `sprite_set_texfilter`, `texture_set_filter`, `image_smooth`,
`gpu_set_pixel_filter`. Ninguno está en el runtime 2026.0.0.23. Los que sí existen son
`gpu_set_texfilter(enable)`, `gpu_get_texfilter()` y sus variantes por *sampler* para shaders,
`gpu_set_texfilter_ext(sampler_id, enable)` y `gpu_get_texfilter_ext()`.

> ⚠️ En el runtime 2026.0.0.23 existe **además** `gpu_set_tex_filter(linear)` —con guion bajo,
> de la familia «tex»— y varios juegos reales la usan, pero **no tiene página en el manual**.
> Usa `gpu_set_texfilter()`, que sí está documentada.

### 6.2 Páginas de textura: el sangrado y sus tres remedios

Aunque apagues la interpolación, hay un segundo origen de artefactos: GameMaker empaqueta
todos los sprites en **páginas de textura** y, al escalar o al mover a posiciones no enteras,
el hardware puede leer un texel del sprite vecino. Aparecen **líneas de colores extraños en
los bordes** y **costuras entre tiles**.

| Ajuste | Dónde | Cuándo tocarlo |
|---|---|---|
| **Tile Horizontal / Tile Vertical** | Editor de sprites → Ajustes de textura | Sprites que se repiten (fondos de scroll). El borde se rellena con el lado opuesto en vez de repetir el píxel del borde |
| **Edge Filtering** (filtrado de bordes) | Editor de sprites → Ajustes de textura | Si ves *halos* de color alrededor de un sprite con interpolación activa: los píxeles del borde adoptan el color del píxel opaco más cercano |
| **Separate Texture Page** | Editor de sprites → Ajustes de textura | Cuando un sprite grande debe estar aislado. ⚠️ **Cada subimagen recibe su propia página**: un sprite de 10 frames genera 10 páginas. Se come la VRAM |
| **Output Border** | Propiedades del tileset | **El ajuste que arregla las costuras entre tiles.** Añade píxeles de relleno alrededor de cada tile. Por defecto vale **2**; si vas a escalar o hacer zoom, súbelo |
| **Premultiply Alpha** | Editor de sprites → Ajustes de textura | Solo si dibujas el sprite sobre una *surface* o haces efectos concretos |

Dos avisos del manual que muerden en proyectos reales:

- **Si una imagen es mayor que el tamaño máximo de página de textura de la plataforma, GameMaker
  la reduce a la mitad** (y otra vez si hace falta) hasta que quepa. No la parte: la encoge.
  Un fondo que se ve perfecto en Windows con páginas de 4096 puede salir borroso en iOS con
  páginas de 2048. **Comprueba el tamaño de página de la exportación más pequeña.**
- Las imágenes se **recortan** por defecto para quitar el transparente sobrante. Se desactiva
  desde el gestor de grupos de texturas.

La API completa (`texturegroup_load`, `sprite_prefetch`, `sprite_flush`, `texture_get_texel_width`…)
está en [08 · 08 — Texturas y grupos de texturas](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md).

### 6.3 `application_surface` y `surface_resize`

`application_surface` es la superficie donde GameMaker dibuja todo antes de mandarlo a la
ventana. Su tamaño es **la resolución real de tu juego**, y decide la disyuntiva de §1.5:

```gml
// Rejilla estricta: el juego se dibuja a la base y se amplía entero.
surface_resize(application_surface, ancho_base, alto_base);

// Subpíxel: el juego se dibuja a la resolución de la ventana.
surface_resize(application_surface, ancho_base * escala, alto_base * escala);
```

Dos reglas que evitan la mitad de los problemas:

1. **Redimensiónala cada vez que cambie el modo de pantalla o el tamaño de ventana**, no solo
   al arrancar. Si no, la imagen sale estirada al entrar en pantalla completa.
2. **No la redimensiones cada frame.** Reasignar una superficie es caro y, en algunos drivers,
   la superficie se pierde y se recrea vacía.

Si necesitas dibujar el juego a mano (para meterlo en una «caja» centrada, aplicar un shader de
filtrado o poner marcos de televisor CRT), se desactiva su dibujado automático con
`application_surface_draw_enable(false)` y se dibuja en el evento **Post Draw** con
`draw_surface_ext()` o `draw_surface_stretched()`. Ese camino, con sus efectos secundarios
—el ratón deja de estar donde crees, las sombras semitransparentes se oscurecen si no llamas a
`gpu_set_blendenable(false)`, y las UI layers se descolocan— está desarrollado en
[03 · 44](../03%20-%20Cursos%20%28YouTube%29/44%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%204%20-%20Experto.md) §8–§10.

### 6.4 Ventana y GUI: que todo sea el mismo múltiplo

Los tres tamaños tienen que ser coherentes o el resultado es una mezcla de escalas:

| Elemento | Función | Regla en pixel art |
|---|---|---|
| Ventana | `window_set_size(w, h)` | `base × escala entera` |
| Superficie de aplicación | `surface_resize(application_surface, …)` | `base` (rejilla estricta) o `base × escala` (subpíxel) |
| Capa GUI | `display_set_gui_size(w, h)` | `base`, o `base × 2` si el HUD necesita más detalle |

Si no llamas a `display_set_gui_size()`, la GUI toma el tamaño de la ventana y tu HUD de pixel
art se dibujará **a la escala del monitor**, mezclando píxeles de dos tamaños distintos en la
misma pantalla. Es el segundo error más común después de la interpolación.

> 📱 **En móvil el problema se agrava**: no hay dos o tres relaciones de aspecto como en
> escritorio, sino una decena, y además entra en juego la **densidad de píxeles (DPI)** — los
> mismos píxeles de pantalla pueden ser una pantalla de 5" o de 7". La estrategia de altura fija
> con anchura variable, el *letterbox* como alternativa sin código, y la conversión de DPI a
> píxeles de GUI están en
> [04 · 28 §4 «Resolución y escalado en móvil»](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md).

### 6.5 Posiciones fraccionarias y el redondeo de la cámara

Un decimal en la posición de la cámara desplaza **la escena entera** medio píxel, y con la
interpolación apagada eso se ve como un temblor de bordes que se llama *pixel shimmering*.

```gml
/// obj_camara · End Step — cámara suave que no tiembla
var _cam = view_camera[0];
var _vw  = camera_get_view_width(_cam);
var _vh  = camera_get_view_height(_cam);

// El seguimiento se calcula SIEMPRE con decimales…
destino_x = lerp(destino_x, obj_jugador.x - _vw * 0.5, 0.12);
destino_y = lerp(destino_y, obj_jugador.y - _vh * 0.5, 0.12);

destino_x = clamp(destino_x, 0, max(0, room_width  - _vw));
destino_y = clamp(destino_y, 0, max(0, room_height - _vh));

// …y se redondea SOLO al entregarlo a la cámara.
camera_set_view_pos(_cam, floor(destino_x), floor(destino_y));
```

El patrón es siempre el mismo, y es el mismo de §4.6: **estado con decimales, presentación con
enteros**. Si guardas ya redondeado, el `lerp()` se atasca y la cámara nunca llega al destino.

La misma disciplina vale para todo lo que se dibuja: `draw_sprite(spr, 0, floor(x), floor(y))`
si `x` puede traer decimales. Un sistema de cámara completo, con zona muerta, adelanto y
sacudida, ya está resuelto en
[`scr_camera.gml`](../06%20-%20Assets%20y%20Scripts/scr_camera.gml) (`cam_update()` ya redondea).

### 6.6 Rotar sprites en pixel art

**Rotar destruye pixel art.** No es un fallo de GameMaker: rotar una rejilla de píxeles obliga
a decidir de qué píxel de origen sale cada píxel de destino, y salvo en múltiplos de 90° esa
correspondencia no existe. El resultado es una silueta dentada, líneas que se parten y detalles
de 1 px que desaparecen y reaparecen a cada frame.

| Ángulos | Qué pasa | Qué hacer |
|---|---|---|
| 0°, 90°, 180°, 270° | Correspondencia exacta; sin pérdida | `draw_sprite_ext()` con total tranquilidad |
| Cualquier otro | Silueta dentada, detalles que parpadean | Ver más abajo |

Las cuatro alternativas, de mejor a peor:

1. **Pre-rotar los frames a mano.** Dibujas 8, 16 o 32 orientaciones y eliges la más cercana.
   Es lo que hacían los juegos de la época y sigue siendo lo que mejor se ve. Caro en arte,
   gratis en runtime.

   ```gml
   /// Elegir el frame pre-rotado más cercano
   /// Convención: el sprite tiene _pasos frames, el 0 mira a la derecha,
   /// y avanzan en sentido antihorario como los ángulos de GameMaker.
   /// @function frame_por_angulo(_angulo, _pasos)
   /// @param  {Real} _angulo Ángulo en grados (0 = derecha).
   /// @param  {Real} _pasos  Número de orientaciones dibujadas.
   /// @return {Real} Índice de subimagen.
   function frame_por_angulo(_angulo, _pasos)
   {
       var _paso = 360 / _pasos;
       return (round(((_angulo mod 360) + 360) mod 360 / _paso)) mod _pasos;
   }

   /// obj_nave · Draw
   var _idx = frame_por_angulo(direccion_apuntado, sprite_get_number(sprite_index));
   draw_sprite_ext(sprite_index, _idx, floor(x), floor(y), 1, 1, 0, c_white, 1);
   ```

2. **Cuantizar el ángulo** al múltiplo más cercano de 22,5° o 45° y rotar con
   `draw_sprite_ext()`. La rotación sigue estropeando píxeles, pero al menos **no cambia cada
   frame**, así que no parpadea. Aceptable para objetos que giran despacio.

3. **Rotar solo lo que puede permitírselo**: partículas, destellos, humo, cosas sin líneas
   finas. Un brillo rotado no se nota; una espada con contorno de 1 px, sí.

4. **Rotar con subpíxel activado** (§1.5): se ve mucho mejor porque hay más resolución real, a
   cambio de que el juego deje de estar en rejilla estricta. Es el compromiso de muchos juegos
   modernos con pixel art detallado.

> 🔺 Lo mismo vale para el **escalado no entero de sprites sueltos**: `image_xscale = 1.3` es
> tan destructivo como una rotación de 30°. Para un efecto de *squash & stretch* legible, usa
> escalas cercanas a 1 y duración corta —ver
> [04 · 15 §4.3](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md)— o anímalo
> a mano en los frames.

### 6.7 Fuentes pixel

Una fuente de píxeles está diseñada para verse a **un tamaño exacto** (y a sus múltiplos
enteros). Fuera de él es un borrón. Tres cosas hay que hacer bien:

**1. Apagar el antialias.** En el editor de fuentes del IDE hay una casilla de *antialiasing*
en la sección de tamaño. En código, para fuentes cargadas de un fichero:

```gml
/// obj_arranque · Create — cargar una fuente pixel sin suavizado
font_add_enable_aa(false);          // OBLIGATORIO antes de font_add()
global.fnt_hud = font_add("fuentes/PressStart2P.ttf", 16, false, false, 32, 255);
font_add_enable_aa(true);           // devolver el ajuste a su estado normal

if (!font_exists(global.fnt_hud))
{
    show_debug_message("La fuente no se cargó: uso la de reserva");
    global.fnt_hud = fnt_reserva;   // recurso del IDE
}

draw_set_font(global.fnt_hud);
```

`font_add_enable_aa()` **solo afecta a las fuentes añadidas después**; no cambia las ya
cargadas. El error clásico es llamarla al final.

**2. Usar el tamaño nativo.** Si la fuente está dibujada a 8 px, úsala a 8, 16, 24 o 32. Nunca
a 10 ni a 14.

**3. Regenerar la textura tras cualquier cambio.** GameMaker genera la textura de una fuente
**una sola vez**. Si cambias el tamaño, el rango de caracteres o el antialias y no pulsas
**Regenerate**, el juego seguirá usando la textura vieja y parecerá que tu cambio no hace nada.

Ajustes finos del editor que importan en resoluciones bajas: **Hinting** (por defecto «normal»;
en fuentes pixel suele convenir *Disable Hinting*, porque deforma glifos para encajarlos en una
rejilla que la fuente ya respeta), **Rounding** (por defecto `floor`) y **Apply kerning**. Y los
botones **From code** / **From file**, que generan solo los rangos de caracteres que usas de
verdad: en un juego localizado al ruso o al chino, eso es la diferencia entre una página de
textura y ocho.

**La alternativa que no falla: fuentes de sprite.** Dibujas los glifos como un sprite y los
registras. Control total sobre cada píxel, sin depender del renderizador de fuentes:

```gml
// Cada frame del sprite es un carácter, empezando por "!" (ASCII 33)
// prop = true → anchura proporcional; sep = separación extra en píxeles
global.fnt_bitmap = font_add_sprite(spr_glifos, ord("!"), true, 1);

// O con un mapa explícito, si tu sprite no sigue el orden ASCII
global.fnt_numeros = font_add_sprite_ext(spr_digitos, "0123456789", false, 0);
```

**Cuándo sí conviene SDF.** Las fuentes SDF (*signed distance field*) guardan la distancia al
borde del glifo en vez del mapa de bits, así que **escalan a cualquier tamaño sin pixelarse**.
Es exactamente lo contrario de lo que quiere el pixel art… y por eso son perfectas para lo que
*no* es pixel art dentro de tu juego: **el texto de menús, opciones, créditos y subtítulos**,
que se beneficia de ser nítido a cualquier resolución.

```gml
var _fnt = font_add("fuentes/Inter.ttf", 32, false, false, 32, 255);
font_enable_sdf(_fnt, true);
```

Restricciones: la fuente debe haberse añadido con `font_add()` desde un fichero, **no funciona
con fuentes de sprite** ni con fuentes creadas en el IDE, y en HTML5 solo se puede activar
desde el IDE. Detalle, efectos de borde y sombra en
[02 · 06 §2–§3](../02%20-%20Novedades%202026/06%20-%20Gráficos%20-%20SVG,%20SDF,%20FX%20y%20superficies.md).

### 6.8 Orden de dibujo y paralaje de píxel entero

El paralaje delata inmediatamente un juego mal montado: si la capa de fondo se coloca en
`camera_x * 0,3`, en cuanto la cámara esté en 101 el fondo estará en 30,3 y sus píxeles no
coincidirán con la rejilla del resto.

```gml
/// obj_paralaje · Create
capa_lejos  = layer_get_id("Fondo_Lejano");
capa_cerca  = layer_get_id("Fondo_Cercano");

/// obj_paralaje · End Step — después de mover la cámara
var _cam_x = camera_get_view_x(view_camera[0]);
var _cam_y = camera_get_view_y(view_camera[0]);

// floor() en cada capa: cada plano cae en la rejilla de píxel
layer_x(capa_lejos,  floor(_cam_x * 0.25));
layer_y(capa_lejos,  floor(_cam_y * 0.25));
layer_x(capa_cerca,  floor(_cam_x * 0.60));
layer_y(capa_cerca,  floor(_cam_y * 0.60));
```

> 🔺 Va en **End Step**, después de que la cámara se haya movido. En Step normal el fondo
> llegaría un frame tarde y «nadaría» respecto al escenario.

Sobre el orden de dibujo: en pixel art conviene **una capa por plano** (cielo, fondo lejano,
fondo cercano, tiles, instancias, decoración delante, efectos) y ordenar por capa, **no** por
`depth` calculado a partir de `y` salvo en un cenital con solapamiento. Cambiar `depth` en
tiempo real fuerza a GameMaker a reordenar y rompe el agrupamiento de páginas de textura. Las
capas están cubiertas en
[01 · 10 §3](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md).

---

## 7 · Cuando no hay artista

### 7.1 Assets libres

Es la respuesta correcta para un prototipo, una jam o un programador en solitario. Kenney
(CC0), los *asset bundles* oficiales de GameMaker, OpenGameArt e itch.io están catalogados,
con su licencia comprobada, en
[07 · 09](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md). **Revisa esa
lista antes de dibujar nada**: probablemente el tileset que necesitas ya existe.

Lo único que hay que añadir aquí es el criterio de **coherencia**: mezclar packs de artistas
distintos se nota al instante, porque cada uno trae su paleta, su tamaño de tile y su dirección
de luz. Dos remedios baratos: **(1)** reducir todo a una paleta común —en Aseprite, cargar la
paleta objetivo y remapear, o pasar a *Sprite → Color Mode → Indexed*—, y **(2)** unificar el
tamaño de tile eligiendo uno y descartando el otro, nunca escalándolo.

### 7.2 IA: referencia sí, resultado no

Un modelo de imagen puede darte una **hoja de referencia** utilísima: paleta, composición,
silueta, variantes de un mismo objeto, ideas de diseño. Lo que **no** te da es pixel art.

El motivo es estructural, no de calidad del modelo: el pixel art se define por el control
sobre **cada píxel individual**, y un generador produce una imagen que *parece* pixel art a
tamaño grande pero que, ampliada, tiene píxeles de tamaños distintos, cientos de colores fuera
de paleta, bordes con antialias y ninguna rejilla coherente. A 320×180 se convierte en una
mancha, y «bajarlo de resolución» solo reproduce el mismo problema más pequeño.

Uso honesto y productivo:

| Sí | No |
|---|---|
| Generar referencias de estilo, color y composición | Generar el sprite final |
| Explorar variantes de diseño de un personaje antes de dibujarlo | «Convertir a pixel art» una ilustración |
| Fondos muy lejanos y desenfocados que nunca se ven a tamaño real | Tiles, personajes, iconos, cualquier cosa con silueta |
| Mockups para enseñar una idea al equipo | Assets que vas a publicar |

Y una nota de mercado que no es opinión: buena parte de la comunidad de pixel art rechaza
abiertamente el arte generado, hasta el punto de que los tutoriales de Pedro Medeiros llevan
la etiqueta «No generative AI was used». Si publicas en itch.io o Steam, **declara lo que uses**.

> Para el resto del criterio —qué sirve de IA generativa fuera del pixel art (upscalers,
> texturas, retratos), el problema de la consistencia de estilo (seeds, ControlNet, LoRA) y
> el estado legal verificado con fecha (derechos de autor, Content Survey de Steam, AI
> Disclosure de itch.io)— ver
> [07 · 23 — Arte generado por IA](../07%20-%20Ecosistema/23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md).

### 7.3 Placeholders: cajas grises con disciplina

Lo más rápido y lo más profesional es **no dibujar nada todavía**. Un rectángulo de color plano
con el tamaño exacto del sprite futuro te deja programar todo el juego.

```gml
/// obj_placeholder · Draw — caja con origen y caja de colisión visibles
var _w = 16, _h = 24;          // tamaño DEFINITIVO del sprite futuro

draw_set_color(c_gray);
draw_rectangle(x - _w * 0.5, y - _h, x + _w * 0.5 - 1, y - 1, false);

draw_set_color(c_red);         // el origen: pies del personaje
draw_rectangle(x - 1, y - 1, x + 1, y + 1, false);

draw_set_color(c_lime);        // dirección a la que mira
draw_line(x, y - _h * 0.5, x + sign(image_xscale) * _w, y - _h * 0.5);
draw_set_color(c_white);
```

Tres reglas para que el placeholder no se convierta en deuda:

1. **El tamaño es definitivo desde el principio.** Cambiar de 16×24 a 24×32 al final del
   proyecto reajusta colisiones, cámara, plataformas y niveles enteros.
2. **Un color distinto por categoría** (jugador, enemigo, plataforma, objeto, peligro). Ver el
   juego en cajas de colores es una herramienta de depuración, no un castigo.
3. **Marca el origen y la dirección.** Casi todos los bugs de «el sprite está desplazado» son
   en realidad un origen mal puesto que nadie miró hasta que llegó el arte final.

---

## 8 · Checklists

### 8.1 Un sprite está terminado cuando…

- [ ] Está dibujado a la **resolución base del juego**, no a otra escala.
- [ ] Usa **solo colores de la paleta del proyecto**.
- [ ] En **escala de grises** se sigue leyendo qué es (prueba de valor).
- [ ] Rellenado de **negro sólido**, su silueta es única y reconocible.
- [ ] Se lee **a tamaño real**, no solo ampliado al 800 %.
- [ ] **Sin píxeles huérfanos** ni ruido de 1 px que no sea intencionado.
- [ ] **Sin jaggies**: los tramos de cada línea siguen un patrón regular.
- [ ] **Sin banding**: no hay dos líneas paralelas alineadas píxel a píxel.
- [ ] La **luz viene de la dirección acordada** para todo el juego.
- [ ] **No hay pillow shading**: la sombra describe volumen, no el contorno.
- [ ] Tiene **sombra proyectada** o algún anclaje al suelo, si procede.
- [ ] El **origen** está donde debe (pies para un personaje, centro para un proyectil).
- [ ] La **caja de colisión** está definida y no es la silueta entera.
- [ ] Si tiene AA manual, **no toca el borde exterior** contra transparencia.
- [ ] Se ve correcto **sobre los fondos reales del juego**, no sobre blanco.
- [ ] Nombre con prefijo `spr_` y **sin `_stripN`** ya importado.

### 8.2 Un tileset está terminado cuando…

- [ ] El **tamaño de tile es potencia de 2** (8, 16, 32) y coherente con el resto del juego.
- [ ] Todos los tiles **casan por los cuatro bordes**, comprobado con el truco del desplazamiento.
- [ ] A pantalla llena **no se ve la rejilla**: hay clusters que cruzan el borde del tile.
- [ ] Hay **variantes** del tile base y su probabilidad de aparición es baja.
- [ ] Hay **zonas planas de descanso**: no todo es textura.
- [ ] Los **bordes y esquinas** están completos (16 piezas mínimo, 47 para el juego completo).
- [ ] El **Output Border** del tileset está a 2 o más si vas a escalar o hacer zoom.
- [ ] El tileset **no se solapa con la capa de decoración**: lo suelto va en su propia capa.
- [ ] El **contraste es menor** que el de los personajes: el fondo no compite.
- [ ] Las **zonas transitables se distinguen de las sólidas** sin depender del color.

### 8.3 El proyecto está bien configurado cuando…

- [ ] **«Interpolate colours between pixels» desmarcado en cada plataforma** de exportación.
- [ ] La **resolución base está en macros**, no repartida en números sueltos.
- [ ] **Ventana, `application_surface` y GUI** son múltiplos coherentes de la base.
- [ ] La cámara recibe **enteros**: `floor()` o `round()` en `camera_set_view_pos()`.
- [ ] Las capas de **paralaje** se colocan con `floor()`.
- [ ] Las **fuentes pixel** están sin antialias, a su tamaño nativo y **regeneradas**.
- [ ] **Nada rota** salvo múltiplos de 90°, partículas o efectos sin líneas finas.
- [ ] El juego se ha **probado en pantalla completa y en ventana**, en 1080p y en 1440p.
- [ ] El tamaño de **página de textura de la exportación más pequeña** admite tu imagen mayor.

---

## 9 · Errores clásicos

| Error | Síntoma | Arreglo |
|---|---|---|
| Interpolación activa | Todo borroso al ejecutar, nítido en el editor | §6.1 · plataforma **por plataforma** |
| Base elegida a ojo | No escala entero en ningún monitor | §1.2 · divide 640×360 |
| Cambiar la base a media producción | Hay que redibujar todo el arte | Decidirla antes del primer sprite |
| GUI sin `display_set_gui_size()` | HUD con píxeles de otro tamaño que el juego | §6.4 |
| Cámara con decimales | Bordes que tiemblan al moverse | §6.5 · redondear **solo al entregar** |
| Redondear el estado, no la presentación | El `lerp()` se atasca, la cámara no llega | Guardar decimales, dibujar enteros |
| Rotación libre de sprites | Silueta dentada que parpadea | §6.6 · pre-rotar o cuantizar |
| Paleta sin hue shifting | Arte plano y gris pese a tener colores | §2.2 |
| *Pillow shading* | Todo parece un cojín; no hay volumen | §3.5 · una dirección de luz para el juego |
| Dithering en sprites móviles | Ruido que vibra al moverse | §3.4 · solo en fondos y texturas |
| Contraste del fondo igual que el del personaje | El jugador se pierde de vista | §2.3 · apagar el escenario |
| Tiles sin *Output Border* | Costuras y líneas entre tiles al escalar | §6.2 · subirlo a 2 o más |
| Fuente pixel con antialias | Texto sucio e ilegible a tamaño pequeño | §6.7 · `font_add_enable_aa(false)` antes |
| Fuente cambiada y no regenerada | «Mi cambio no hace nada» | §6.7 · botón **Regenerate** |
| `image_blend = c_white` para el flash | No pasa nada | §2.6 · el blend multiplica; usa `gpu_set_fog()` |
| Sprite mayor que la página de textura | Nítido en Windows, borroso en iOS | §6.2 · GameMaker lo **encoge** a la mitad |
| Mezclar packs de assets | Cada zona parece de otro juego | §7.1 · una paleta y un tamaño de tile |

---

## Ver también

- [03 · 36 — ¿Por qué todo se ve borroso?](../03%20-%20Cursos%20%28YouTube%29/36%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Por%20Qué%20Todo%20se%20ve%20Borroso.md) — el ajuste de interpolación, explicado desde cero
- [03 · 41](../03%20-%20Cursos%20%28YouTube%29/41%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%201%20-%20Principiante.md) · [42](../03%20-%20Cursos%20%28YouTube%29/42%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%202%20-%20Intermedio.md) · [43](../03%20-%20Cursos%20%28YouTube%29/43%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%203%20-%20Avanzado.md) · [44](../03%20-%20Cursos%20%28YouTube%29/44%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%204%20-%20Experto.md) — **el sistema de cámara y resolución completo**
- [03 · 10 — Crear tus propios recursos de arte](../03%20-%20Cursos%20%28YouTube%29/10%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2010%20-%20Recursos%20de%20Arte.md) — dibujar el arte del juego con GIMP, sin ser artista
- [03 · 11 — Animaciones y Tile Sets](../03%20-%20Cursos%20%28YouTube%29/11%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2011%20-%20Animaciones%20y%20Tile%20Sets.md) · [03 · 17 — Autotiles](../03%20-%20Cursos%20%28YouTube%29/17%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Autotiles.md)
- [07 · 09 — Asset packs y recursos gráficos](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md) — herramientas de pixel art, assets libres y licencias
- [12 · 05 — Pipeline de arte, audio y niveles](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md) — automatizar Aseprite → GameMaker
- [08 · 08 — Texturas y grupos de texturas](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md) · [08 · 05 — Superficies](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md) · [08 · 03 — Texto y fuentes](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md)
- [02 · 06 — Gráficos: SVG, SDF, FX y superficies](../02%20-%20Novedades%202026/06%20-%20Gráficos%20-%20SVG,%20SDF,%20FX%20y%20superficies.md) — fuentes SDF y efectos
- [01 · 10 — Rooms, capas, cámaras y viewports](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) · [01 · 11 — Dibujo y renderizado](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md)
- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) — *squash & stretch*, *hit stop*, flash de impacto
- [04 · 27 — Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) — daltonismo y legibilidad
- [04 · 28 §4 — Resolución y escalado en móvil](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md) — relación de aspecto variable, *letterbox* y DPI en Android/iOS
- [`06 · scr_camera.gml`](../06%20-%20Assets%20y%20Scripts/scr_camera.gml) — cámara con zona muerta, suavizado y redondeo

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/manual-lts-2026-es/`):

| Qué se sacó de ahí | Página |
|---|---|
| «Interpolate colours between pixels» y su valor por defecto en cada plataforma | `Settings/Game_Options/Windows.htm` y sus páginas hermanas (macOS, Ubuntu, iOS, tvOS, Android, Amazon Fire, HTML5, Opera GX, GX Games, Reddit, Windows UWP) |
| Filtrado de texturas por código | `…/GML_Reference/Drawing/GPU_Control/gpu_set_texfilter.htm` |
| Páginas de textura, bordes, reducción a la mitad | `Settings/Texture_Information/Texture_Pages.htm` |
| Ajustes de textura del sprite: *tile*, *edge filtering*, página separada | `The_Asset_Editors/Sprites.htm` |
| Imágenes en tira `_stripN` | `The_Asset_Editors/Sprite_Properties/Sprite_Strips.htm` |
| *Output Border* del tileset | `The_Asset_Editors/Tile_Sets.htm` |
| Editor de fuentes: antialias, hinting, rangos, **Regenerate** | `The_Asset_Editors/Fonts.htm` |
| Editor de imagen: papel cebolla, rejilla, paletas de sprite | `The_Asset_Editors/Image_Editor.htm` |

Prefijo común: <https://manual.gamemaker.io/lts/en/>. Las firmas de `sprite_add()`,
`font_add_enable_aa()`, `font_enable_sdf()` y `gpu_set_fog()` se verificaron con
`python3 _indice/buscar.py`.

**Blog y tutoriales oficiales de GameMaker:**

- Samuel Wain, «How To Make Pixel Art For 2D Games», 2 de agosto de 2023 —
  <https://gamemaker.io/en/blog/make-pixel-art-2d-games> (resoluciones de hardware clásico,
  la regla «duplicar el tile cuadruplica el trabajo», el consejo del `_stripN`)
- Mark Alexander, «The Image Editor – IDE Basics», 1 de enero de 2021 —
  <https://gamemaker.io/en/tutorials/image-editor>

**Pixel art como disciplina:**

- cure, «The Pixel Art Tutorial», Pixel Joint, 2010 —
  <http://pixeljoint.com/forum/forum_posts.asp?TID=11299> — la fuente más rigurosa sobre
  clusters, jaggies, banding, dithering, sel-out, rampas y hue shifting
- Derek Yu, «Pixel Art Tutorial» —
  <https://www.derekyu.com/makegames/pixelart.html> — y «Pixel Art: Common Mistakes» —
  <https://www.derekyu.com/makegames/pixelart2.html> (pillow shading, *naive coloring*,
  *cardboard designs*, la regla de los píxeles gruesos)
- Raymond Schlitter (Slynyrd), «Pixelblog» — catálogo de 63 entradas:
  <https://www.slynyrd.com/pixelblog-catalogue> · nº 1 «Color Palettes»
  <https://www.slynyrd.com/blog/2018/1/10/pixelblog-1-color-palettes> (los +20° de hue shift,
  las 8 rampas × 9 muestras de la paleta Mondo) · nº 5 «Back to the Basics»
  <https://www.slynyrd.com/blog/2018/5/16/pixelblog-5-back-to-basics> · nº 28 «Side View Tiles»
  <https://www.slynyrd.com/blog/2020/5/21/pixelblog-28-side-view-tiles>
- Pedro Medeiros (Saint11), artista de *Celeste* y *TowerFall* — más de 80 tutoriales gratuitos,
  uno por lámina: <https://saint11.art/blog/pixel-art-tutorials/> · paquete descargable en
  <https://studiominiboss.itch.io/pixel-art-tutorials> (*pay what you want* desde 5 USD)
- Michael Azzi («Michafrar»), «Pixel Logic — A Guide to Pixel Art» —
  <https://michafrar.gumroad.com/l/pixel-logic> (10 USD). Manual visual de referencia sobre
  *line art*, antialiasing, color, legibilidad, dithering, perspectivas, subpixeling y animación
- Lospec — directorio de 586 tutoriales <https://lospec.com/pixel-art-tutorials> y lista de
  4 457 paletas <https://lospec.com/palette-list>; las doce paletas citadas en §2.4 se
  verificaron una a una

**Resolución y escalado entero:**

- «Integer Scaling» — <https://tanalin.com/en/articles/integer-scaling/> — definición, la
  distinción entre *nearest neighbour* y escalado entero, y la fórmula
  `R = min(⌊SW/W⌋, ⌊SH/H⌋)`
- Godot Engine, «Multiple resolutions» —
  <https://docs.godotengine.org/en/stable/tutorials/rendering/multiple_resolutions.html> —
  rango recomendado 256×224 a 640×480 y la recomendación explícita de 640×360
- Notkey Studio, «Choosing the right render resolution for a pixel art game» —
  <https://notkey.studio/en/tutorials/choosing-the-right-render-resolution-for-a-pixel-art-game/>
  — tabla de escalados y reparto de resoluciones de la encuesta de hardware de Steam
- Bugnet, «Choosing a pixel art resolution for your game» —
  <https://bugnet.io/blog/choosing-a-pixel-art-resolution-for-your-game>

**Aseprite:**

- Documentación: <https://www.aseprite.org/docs/> · capas <https://www.aseprite.org/docs/layers/>
  · etiquetas <https://www.aseprite.org/docs/tags/> · papel cebolla
  <https://www.aseprite.org/docs/onion-skinning/> · hoja de sprites
  <https://www.aseprite.org/docs/sprite-sheet/>
- Línea de órdenes: <https://www.aseprite.org/docs/cli/>
- Formato del JSON exportado (ejemplos oficiales enlazados desde la documentación de la CLI):
  `json-hash` <https://gist.github.com/dacap/db18e5747a4b6e208d3c> ·
  `json-array` <https://gist.github.com/dacap/a32adb9248320326733a>

### Qué queda marcado como no verificado

- El **índice de capítulos de *Pixel Logic*** no lo publican ni Gumroad ni ninguna fuente
  oficial: por eso arriba se describe su contenido en prosa y no como lista de capítulos.
- La cifra del **8–20 % del alto de pantalla** para el sprite del protagonista (§1.3) es una
  regla práctica extendida en la comunidad, coherente con las recomendaciones de altura de
  personaje de 16/24/32/48 px, pero **no procede de una fuente normativa**.
- Aseprite documenta oficialmente **tres** direcciones de animación (*Forward*, *Reverse*,
  *Ping-pong*) más el campo *Repeat* de la v1.3. Cualquier cuarto modo que veas mencionado
  por ahí **no está en la documentación oficial**.
- La documentación de Aseprite **no cubre** la opacidad ni los modos de fusión de capas, ni el
  diálogo completo de exportación (su sección de línea de órdenes sigue marcada como
  *work in progress*). Todo lo de §5.3 sale de la CLI, que sí está documentada.
