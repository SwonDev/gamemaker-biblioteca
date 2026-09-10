# 01 — Dibujo básico y sprites

> Referencia completa de GML para **GameMaker LTS 2026.0** (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Área: `GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/`.
> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## Índice

1. [Conceptos previos: el ciclo de dibujo](#conceptos-previos-el-ciclo-de-dibujo)
2. [Dibujo del sprite propio](#dibujo-del-sprite-propio)
3. [Familia `draw_sprite*`](#familia-draw_sprite)
4. [Sprites vectoriales: SWF y SVG](#sprites-vectoriales-swf-y-svg)
5. [Animación esquelética (Spine)](#animación-esquelética-spine)
6. [Control global del dibujo](#control-global-del-dibujo)
7. [Limpiar el destino de dibujo](#limpiar-el-destino-de-dibujo)
8. [Variables de instancia de sprite (`image_*`)](#variables-de-instancia-de-sprite-image_)
9. [Tabla resumen](#tabla-resumen)
10. [Fuentes](#fuentes)

---

## Conceptos previos: el ciclo de dibujo

Antes de usar cualquier función de dibujo conviene tener claro **dónde** se está dibujando.

GameMaker **no dibuja directamente en pantalla** en los eventos de dibujo normales. Dibuja en un
destino de dibujo (*draw target*) que cambia automáticamente durante el frame:

| Momento del frame | Destino de dibujo |
|---|---|
| **Pre-Draw** | Búfer de pantalla (*display buffer*) |
| **Draw Begin / Draw / Draw End** | Application Surface (o una superficie de vista si `view_surface_id` está fijada, o tu propia superficie si llamas a `surface_set_target`) |
| **Post-Draw** | Búfer de pantalla — aquí se vuelca la Application Surface |
| **Draw GUI Begin / Draw GUI / Draw GUI End** | Búfer de pantalla |

Consecuencias prácticas:

- **Todo lo que dibujes debe ir en un evento de dibujo.** Fuera de ahí no verás nada.
- **En el momento en que añades código al evento Draw, tomas el control**: GameMaker deja de
  dibujar el sprite asignado automáticamente. Si quieres que se siga viendo, llama a `draw_self()`
  o dibuja explícitamente con `draw_sprite*`.
- Las funciones de esta sección funcionan tanto en la Application Surface como en superficies
  propias y en el búfer de pantalla, según el evento.

---

## Dibujo del sprite propio

### `draw_self()`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja el sprite asignado a la instancia exactamente igual a como lo dibujaría
  GameMaker si el evento Draw estuviera vacío. Es el *default draw*: respeta todas las
  transformaciones que hayas aplicado en eventos anteriores mediante las variables
  `image_*` (`image_xscale`, `image_yscale`, `image_angle`, `image_blend`, `image_alpha`) y el
  origen del sprite.
- **Ejemplo:**
```gml
// Evento Draw: dibujo la nave con sus transformaciones y encima un halo
draw_self();
draw_sprite(spr_halo, 0, x, y - 32);
```
- **Notas / trampas:**
  - Equivale a
    `draw_sprite_ext(sprite_index, image_index, x, y, image_xscale, image_yscale, image_angle, image_blend, image_alpha);`
  - Es la forma más barata de conservar el dibujo por defecto cuando añades código al Draw.
  - Si el objeto no tiene sprite asignado, no dibuja nada.

---

## `image_index` como ESTADO: la trampa que no está en el código ni en el sprite

El manual describe dos usos de `image_index` y los presenta como intercambiables: seguir una
animación, o **elegir un «estado» en un sprite estático** —encendido/apagado, abierto/cerrado,
como los botones de una ventana—. Lo que no dice es que **mezclarlos no funciona**.

Si el sprite tiene `playbackSpeed` distinto de 0 y más de un fotograma, **la animación
reescribe `image_index` en cada paso**. El estado que asignas dura un fotograma y desaparece.

**Medido sobre un proyecto real**: un punto de control con dos sub-imágenes y
`playbackSpeed = 60` perdía su estado «encendido» **30 veces por segundo**. No era «a veces»:
ese estado no existía visualmente.

> 🔍 **Y es de los peores de diagnosticar, por una razón concreta: no está en ningún archivo.**
> Lees el objeto y la asignación es correcta. Lees el sprite y la velocidad es plausible. El
> fallo **solo existe en la combinación de los dos**, así que revisar cualquiera de ellos por
> separado —que es como se revisa— lo da por bueno.

**Las dos salidas**, y basta con una:

```gml
image_speed = 0;          // en el objeto, antes de asignar el estado
image_index = encendido;
```

o poner el `playbackSpeed` del sprite a 0, que es lo correcto cuando sus fotogramas **no son
un ciclo** sino variantes que elige el código. Distinguir las dos clases al importar ahorra
este fallo entero:

| El sprite es… | `playbackSpeed` |
|---|---|
| Un **ciclo** (caminar, trepar, una baliza que parpadea) | el de la animación (10, 4…) |
| **Variantes de estado** que elige el código (palanca, punto de control, puerta) | **0** |

> ⚠️ **Ojo al importar en lote**: el valor por defecto de la tubería de importación puede ser
> `playbackSpeed = 60`, y entonces le toca a **todos** los sprites a la vez. En el caso medido
> estaban los nueve mal, no los cuatro que se habían detectado leyendo el código.

**Se comprueba solo:**

```sh
python3 "$BIB/_indice/auditar-juego-completo.py" <proyecto>
```

Lista los objetos que asignan `image_index` sin poner `image_speed = 0` cuyo sprite además se
anima, y **hace fallar el informe**. No se queja de un objeto que ya para la animación, ni de
un sprite de un solo fotograma, ni de una asignación comentada.

## Familia `draw_sprite`

### `draw_sprite(sprite, subimg, x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja un subimage (frame) concreto de un sprite en una posición de la room. La
  posición se centra en el **origen** del sprite (`x offset` / `y offset` definidos en el Sprite
  Editor).
- **Ejemplo:**
```gml
// Dibuja el sprite asignado en su frame actual y, encima, un icono de estado
draw_sprite(sprite_index, image_index, x, y);
draw_sprite(spr_estado_stun, 0, x, y - 48);
```
- **Notas / trampas:**
  - Si `subimg` supera el número de frames, **GameMaker hace bucle automáticamente**: con 5
    subimages (0..4) y `subimg = 7`, se dibuja el frame 2.
  - `image_index` o `-1` equivalen al frame de animación actual del objeto.
  - **No funciona bien con sprites de animación esquelética**: solo dibuja el primer frame de la
    pose por defecto. Usa `draw_skeleton*` en su lugar.

### `draw_sprite_ext(sprite, subimg, x, y, xscale, yscale, rot, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** como `draw_sprite` pero con control de escala, rotación, color de mezcla y alfa.
  Cambiar estos valores **no modifica el recurso**, solo cómo se dibuja.
- **Ejemplo:**
```gml
// Latido: escala y alfa oscilantes con la misma pose del objeto
var _pulso = 1 + 0.08 * sin(current_time * 0.01);
draw_sprite_ext(sprite_index, image_index, x, y, _pulso, _pulso, 0, c_white, 0.75);
```
- **Notas / trampas:**
  - `colour` se **mezcla** (multiplica) con el sprite; `c_white` lo deja intacto.
  - La rotación `rot` se mide en grados: 0 = normal, 90 = 90° **en sentido antihorario**.
  - En HTML5 sin WebGL, cada combinación de color distinta crea una copia cacheada del sprite →
    pérdida de rendimiento. Limítalo con `sprite_set_cache_size()`.
  - Respeta **Nine Slice** si el sprite lo tiene activado.

### `draw_sprite_general(sprite, subimg, left, top, width, height, x, y, xscale, yscale, rot, c1, c2, c3, c4, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** combina `draw_sprite_ext` con `draw_sprite_part` y añade un color **independiente
  por esquina** para crear degradados.
- **Orden de las esquinas:** `c1` = superior izquierda, `c2` = superior derecha,
  `c3` = inferior derecha, `c4` = inferior izquierda.
- **Ejemplo:**
```gml
// Barra de vida: recorta 8 px de margen, la estira y la tiñe de rojo a negro
draw_sprite_general(spr_barra, 0, 8, 8, sprite_width - 16, sprite_height - 16,
                    x, y, 2, 0.5, 0,
                    c_red, c_red, c_black, c_black, 1);
```
- **Notas / trampas:**
  - El degradado **no** es uniforme en todo el rectángulo: un rectángulo son dos triángulos y el
    color se interpola por separado en cada uno. Es un efecto conocido, no un bug.
  - Aplica la misma advertencia de rendimiento en HTML5 sin WebGL que `draw_sprite_ext`.

### `draw_sprite_part(sprite, subimg, left, top, width, height, x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja **solo una porción** del sprite. `left` y `top` son coordenadas **relativas
  a la esquina superior izquierda del sprite**, no al origen ni a la room.
- **Ejemplo:**
```gml
// Recorta 4 px a cada lado del sprite de 24x24 asignado
draw_sprite_part(sprite_index, image_index, 4, 0, sprite_width - 8, sprite_height - 4, x, y);
```
- **Notas / trampas:**
  - Si `left`/`top` son negativos o el rectángulo se sale del sprite, el resultado puede incluir
    píxeles de frames vecinos en la página de textura.
  - Ideal para barras de progreso y revelado progresivo de imágenes.

### `draw_sprite_part_ext(sprite, subimg, left, top, width, height, x, y, xscale, yscale, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** igual que `draw_sprite_part` pero con escala, color y alfa.
- **Ejemplo:**
```gml
// Silueta negra del sprite estirada al doble de ancho y mitad de alto
draw_sprite_part_ext(sprite_index, image_index, 8, 8,
                     sprite_width - 16, sprite_height - 16,
                     x, y, 2, 0.5, c_black, 1);
```
- **Notas / trampas:**
  - **Trampa importante:** si la página de textura tiene **Automatic Crop** activado, el espacio
    vacío alrededor del sprite se ha eliminado y esta función no dará el resultado esperado.
    Desactiva *Automatic Crop* en el Texture Group Editor.

### `draw_sprite_stretched(sprite, subimg, x, y, w, h)`
- **Devuelve:** `N/A`
- **Qué hace:** estira el sprite para que ocupe exactamente el área `w × h`.
- **Ejemplo:**
```gml
// Fondo que ocupa media pantalla en alto
draw_sprite_stretched(spr_fondo, 0, 0, 0, room_width, room_height / 2);
```
- **Notas / trampas:**
  - **Ignora el origen del sprite**: la esquina superior izquierda queda en `(x, y)`.
  - Respeta Nine Slice.

### `draw_sprite_stretched_ext(sprite, subimg, x, y, w, h, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** como `draw_sprite_stretched` más color de mezcla y alfa.
- **Ejemplo:**
```gml
// Marca de agua semitransparente a pantalla completa
draw_sprite_stretched_ext(spr_logo, 0, 0, 0, room_width, room_height, c_white, 0.15);
```
- **Notas / trampas:** también ignora el origen del sprite.

### `draw_sprite_pos(sprite, subimg, x1, y1, x2, y2, x3, y3, x4, y4, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja el sprite deformado sobre el cuadrilátero definido por cuatro esquinas. Es
  la función clásica para perspectiva falsa, sombras proyectadas y banderas ondulantes.
- **Orden de las esquinas (obligatorio, en sentido horario):**
  `(x1,y1)` superior izquierda → `(x2,y2)` superior derecha → `(x3,y3)` inferior derecha →
  `(x4,y4)` inferior izquierda.
- **Ejemplo:**
```gml
// Sombra proyectada y sesgada hacia la derecha
draw_sprite_pos(spr_sombra, 0,
                x - 100, y - 50,
                x -  50, y + 150,
                x + 100, y + 200,
                x + 100, y,
                0.5);
```
- **Notas / trampas:**
  - El manual avisa explícitamente de **texture shearing**: al deformar un cuadrilátero se
    distorsiona el mapeo de textura. Para deformaciones fuertes es mejor un vertex buffer con
    coordenadas de textura propias.
  - No admite color de mezcla, solo `alpha`.

### `draw_sprite_tiled(sprite, subimg, x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** repite el sprite en mosaico cubriendo **toda la vista** (o la room si no hay vista
  activa), empezando en `(x, y)`.
- **Ejemplo:**
```gml
// Suelo de baldosas que se desplaza con la cámara
draw_sprite_tiled(spr_baldosa, 0, 0, 0);
```
- **Notas / trampas:**
  - Solo para proyecciones 2D (ortográficas); **no funciona bien con cámara 3D**.
  - El tamaño de cada baldosa es el del sprite, no el de la instancia.
  - **No admite sprites con Nine Slice.**

### `draw_sprite_tiled_ext(sprite, subimg, x, y, xscale, yscale, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** mosaico con escala, color y alfa configurables.
- **Ejemplo:**
```gml
// Rejilla de depuración roja al doble de tamaño y semitransparente
draw_sprite_tiled_ext(spr_rejilla, 0, 0, 0, 2, 2, c_red, 0.5);
```
- **Notas / trampas:** mismas limitaciones que `draw_sprite_tiled` (solo 2D, sin Nine Slice).

---

## Sprites vectoriales: SWF y SVG

GameMaker permite importar sprites vectoriales en formato SWF (Flash) y SVG. Estas funciones
controlan el antialiasing de esos sprites y son de **ámbito global**: afectan a todos los sprites
vectoriales dibujados después de la llamada.

### `draw_enable_swf_aa(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa (`true`) o desactiva (`false`) el antialiasing para sprites vectoriales
  **SWF**. Por defecto está **desactivado**.
- **Ejemplo:**
```gml
if (draw_get_swf_aa_level() == 0)
{
    draw_enable_swf_aa(true);
    draw_set_swf_aa_level(0.5);
}
```
- **Notas / trampas:** el nivel de AA lo determina `draw_set_swf_aa_level`.

### `draw_set_swf_aa_level(AA)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el nivel de antialiasing para sprites SWF, entre `0` (nada) y `1` (máximo).
- **Ejemplo:**
```gml
draw_enable_swf_aa(true);
draw_set_swf_aa_level(0.75);
```
- **Notas / trampas:** no tiene efecto si antes no has llamado a `draw_enable_swf_aa(true)`.

### `draw_get_swf_aa_level()`
- **Devuelve:** `Real` (0..1)
- **Qué hace:** devuelve el nivel de antialiasing actual para sprites SWF.
- **Ejemplo:**
```gml
var _aa = draw_get_swf_aa_level();
show_debug_message($"AA de SWF: {_aa}");
```

### `draw_enable_svg_aa(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa (`true`) o desactiva (`false`) el antialiasing para sprites vectoriales
  **SVG**. Por defecto está **desactivado**.
- **Ejemplo:**
```gml
draw_enable_svg_aa(true);
draw_set_svg_aa_level(0.6);
```

### `draw_set_svg_aa_level(AA)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el nivel de antialiasing para sprites SVG, entre `0` y `1`.
- **Ejemplo:**
```gml
draw_set_svg_aa_level(1); // suavizado máximo
```

### `draw_get_svg_aa_level()`
- **Devuelve:** `Real` (0..1)
- **Qué hace:** devuelve el nivel de antialiasing actual para sprites SVG.
- **Ejemplo:**
```gml
if (draw_get_svg_aa_level() == 0) draw_enable_svg_aa(true);
```

---

## Animación esquelética (Spine)

> Estas funciones son **exclusivas** de sprites creados con un programa de animación esquelética
> como Spine. Para todo lo demás usa `draw_sprite*` o `draw_self`.

### `draw_skeleton(sprite, animname, skinname, frame, x, y, xscale, yscale, rot, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja un frame concreto de una animación esquelética indicando animación, skin y
  frame, sin modificar las propiedades reales del sprite.
- **Ejemplo:**
```gml
// Primer frame del salto, con la skin 1, a escala y ángulo de la instancia
draw_skeleton(spr_jump, "jump", "skin1", 0,
              x, y, image_xscale, image_yscale, image_angle, c_white, 0.5);
```
- **Notas / trampas:** `frame` va de `0` a `image_number - 1`. `animname` y `skinname` son cadenas
  tal y como se definieron en Spine.

### `draw_skeleton_instance(instance, animname, skinname, frame, x, y, xscale, yscale, rot, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** igual que `draw_skeleton` pero tomando el sprite del **ID de instancia** indicado,
  en lugar de un recurso de sprite directo.
- **Ejemplo:**
```gml
draw_skeleton_instance(obj_player, "jump", "skin1", 0, x, y, 1, 1, 0, c_white, 1);
```

### `draw_skeleton_collision(sprite, animname, frame, x, y, xscale, yscale, rot, colour)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja las **máscaras de colisión** asociadas a la animación esquelética. Es una
  herramienta de depuración visual.
- **Ejemplo:**
```gml
// Ver las cajas de colisión del frame actual en rojo
draw_skeleton_collision(sprite_index, "walk", image_index, x, y, 1, 1, 0, c_red);
```
- **Notas / trampas:** la bounding box de un sprite de Spine se configura **en Spine**, no en
  GameMaker.

### `draw_skeleton_time(sprite, animname, skinname, time, x, y, xscale, yscale, rot, colour, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja la animación en un instante temporal concreto, medido en **segundos** desde
  el inicio. Es la forma correcta de animar con *delta time*.
- **Ejemplo:**
```gml
// Evento Draw: avanza el tiempo con delta_time (microsegundos -> segundos)
tiempo_anim += delta_time / 1000000;
var _duracion = skeleton_animation_get_duration("walk");
if (tiempo_anim > _duracion) tiempo_anim -= _duracion;

draw_skeleton_time(sprite_index, "walk", "skin1", tiempo_anim,
                   x, y, image_xscale, image_yscale, image_angle, c_white, image_alpha);
```
- **Notas / trampas:**
  - Puedes pasar valores superiores a la duración y la animación vuelve al inicio, pero **pierdes
    precisión de coma flotante** conforme el tiempo acumulado crece. Haz el bucle manualmente como
    en el ejemplo.
  - No tiene parámetro `alpha` (sí `colour`).

---

## Control global del dibujo

### `draw_enable_drawevent(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** habilita (`true`) o deshabilita (`false`) los **eventos Draw de todas las
  instancias del juego**. Útil para técnicas de salto de frames.
- **Ejemplo:**
```gml
// Frame skipping: dibujar solo 1 de cada 5 frames
frame_skip++;
draw_enable_drawevent((frame_skip mod 5) == 0);
```
- **Notas / trampas:**
  - **No solo oculta el dibujo: suprime por completo los eventos Draw**, así que cualquier lógica
    que viviera ahí dejará de ejecutarse.
  - Si la llamas al inicio absoluto del juego (Create del primer objeto de la primera room), la
    ventana puede quedarse en negro permanentemente.

### `draw_flush()`
- **Devuelve:** `N/A`
- **Qué hace:** vacía por completo la canalización de dibujo (*draw pipeline*).
- **Ejemplo:**
```gml
draw_flush();
```
- **Notas / trampas:**
  - Es una función **exclusiva de depuración**. El manual prohíbe su uso general: «no debería
    usarse salvo indicación del soporte de GameMaker», porque **degrada seriamente el
    rendimiento**.
  - No funciona en HTML5 si WebGL está desactivado o no es compatible.

---

## Limpiar el destino de dibujo

### `draw_clear(col)`
- **Devuelve:** `N/A`
- **Qué hace:** limpia **todo el destino de dibujo actual** con un color sólido, **sin mezcla de
  alfa**. Solo tiene efecto en eventos de dibujo.
- **Ejemplo:**
```gml
draw_clear(c_blue);
```
- **Notas / trampas:** es la forma habitual de limpiar una superficie recién creada.

### `draw_clear_alpha(col, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** limpia el destino de dibujo con un color **y** fija el canal alfa del destino al
  valor indicado. No mezcla, pero deja el alfa preparado para operaciones posteriores.
- **Ejemplo:**
```gml
// Limpieza estándar de una superficie: negra y totalmente transparente
surface_set_target(mi_superficie);
draw_clear_alpha(c_black, 0);
surface_reset_target();
```
- **Notas / trampas:**
  - En HTML5 permite que el canvas sea **transparente** y se vea el HTML que hay debajo. Para
    ello elimina antes las Background Layers de la room en el editor.
  - Es la función recomendada para inicializar superficies.

### `draw_clear_depth(depth)`
- **Devuelve:** `N/A`
- **Qué hace:** limpia el **búfer de profundidad** del destino de dibujo actual al valor indicado.
- Rango: `0` = *znear*, `1` = *zfar*.
- **Ejemplo:**
```gml
draw_clear_depth(1); // reinicia la profundidad al plano lejano
```
- **Notas / trampas:** requiere que el destino tenga búfer de profundidad
  (ver `surface_depth_disable` y `surface_has_depth` en el archivo **05 - Superficies**).

### `draw_clear_stencil(stencil)`
- **Devuelve:** `N/A`
- **Qué hace:** limpia el **búfer de stencil** del destino de dibujo actual a un valor entero de
  `0` a `255`.
- **Ejemplo:**
```gml
draw_clear_stencil(0);
```
- **Notas / trampas:** es el primer paso típico de cualquier técnica con stencil
  (máscaras de recorte, siluetas, outline selectivo). Ver `gpu_set_stencil_*` en el archivo
  **04 - Color y blending**.

### `draw_clear_ext([colour], [alpha], [depth], [stencil])`
- **Devuelve:** `N/A`
- **Qué hace:** limpia en una sola llamada el destino de dibujo y sus búferes de profundidad y
  stencil. Cada argumento es **opcional**: ponlo a `undefined` para omitir esa parte.
- **Ejemplo:**
```gml
// Limpia color a blanco, alfa a 1, profundidad a 0 y stencil a 20
draw_clear_ext(c_white, 1, 0, 20);

// Solo limpia el stencil
draw_clear_ext(undefined, undefined, undefined, 0);
```
- **Notas / trampas:**
  - Si **todos** los argumentos son `undefined`, la función no hace nada.
  - `colour` y `alpha` van emparejados: si especificas uno debes especificar el otro.

---

## Variables de instancia de sprite (`image_*`)

No son funciones, pero controlan directamente qué dibujan `draw_self` y `draw_sprite_ext`. Documentadas
en `Asset_Management/Sprites/Sprite_Instance_Variables/`.

| Variable | Tipo | Acceso | Qué controla |
|---|---|---|---|
| `sprite_index` | Sprite Asset | L/E | Sprite asignado a la instancia (`-1` si no tiene) |
| `image_alpha` | Real | L/E | Transparencia: `0` = invisible, `1` = opaco |
| `image_angle` | Real | L/E | Rotación en grados (0 = derecha, 90 = arriba, 180 = izquierda, 270 = abajo) |
| `image_blend` | Colour | L/E | Tinte. `-1` o `c_white` = sin tinte |
| `image_index` | Real | L/E | Frame actual de animación (coma flotante simple) |
| `image_number` | Real | **Solo lectura** | Número de subimages del sprite asignado |
| `image_speed` | Real | L/E | Multiplicador de velocidad de animación (`1` = normal) |
| `image_xscale` | Real | L/E | Escala horizontal (`-1` voltea sin escalar) |
| `image_yscale` | Real | L/E | Escala vertical (`-1` voltea sin escalar) |
| `sprite_width` | Real | **Solo lectura** | Ancho del sprite **ya escalado** |
| `sprite_height` | Real | **Solo lectura** | Alto del sprite **ya escalado** |
| `sprite_xoffset` | Real | L/E | Origen X del sprite |
| `sprite_yoffset` | Real | L/E | Origen Y del sprite |

**Ejemplo combinado:**
```gml
// Evento Create de una explosión
image_speed = 0.5;              // mitad de velocidad
image_angle = irandom(360);     // rotación aleatoria
image_xscale = 0.5;
image_yscale = 0.5;
image_blend = c_orange;         // tinte naranja

// Evento Draw
draw_self();

// Evento Step: se desvanece y se destruye al terminar
image_alpha -= 0.02;
if (image_alpha <= 0) instance_destroy();
```

- **Notas / trampas:**
  - Para que los cambios en `image_*` se vean, la instancia debe **no tener** evento Draw (dibujo
    por defecto) o dibujarse con `draw_self` / `draw_sprite_ext`.
  - Cambiar `image_xscale` / `image_yscale` **escala también la máscara de colisión** y la bounding
    box.
  - `image_number` cuenta frames, pero los índices empiezan en `0`: con 1 subimage,
    `image_number` vale `1` y `image_index` vale `0`.
  - `sprite_width` / `sprite_height` devuelven el tamaño **escalado**. Para el tamaño original del
    recurso usa `sprite_get_width()` / `sprite_get_height()`.
  - Cambiar `sprite_index` **conserva el frame visible** si el nuevo sprite tiene ese subimage.

---

## Tabla resumen

| Función | Devuelve | Ámbito |
|---|---|---|
| `draw_self()` | `N/A` | Instancia |
| `draw_sprite(sprite, subimg, x, y)` | `N/A` | Destino actual |
| `draw_sprite_ext(... 9 args)` | `N/A` | Destino actual |
| `draw_sprite_general(... 15 args)` | `N/A` | Destino actual |
| `draw_sprite_part(sprite, subimg, left, top, w, h, x, y)` | `N/A` | Destino actual |
| `draw_sprite_part_ext(... 12 args)` | `N/A` | Destino actual |
| `draw_sprite_stretched(sprite, subimg, x, y, w, h)` | `N/A` | Destino actual |
| `draw_sprite_stretched_ext(... 10 args)` | `N/A` | Destino actual |
| `draw_sprite_pos(... 11 args)` | `N/A` | Destino actual |
| `draw_sprite_tiled(sprite, subimg, x, y)` | `N/A` | Vista completa |
| `draw_sprite_tiled_ext(... 8 args)` | `N/A` | Vista completa |
| `draw_enable_swf_aa(enable)` | `N/A` | Global |
| `draw_set_swf_aa_level(AA)` | `N/A` | Global |
| `draw_get_swf_aa_level()` | `Real` | Global |
| `draw_enable_svg_aa(enable)` | `N/A` | Global |
| `draw_set_svg_aa_level(AA)` | `N/A` | Global |
| `draw_get_svg_aa_level()` | `Real` | Global |
| `draw_skeleton(... 11 args)` | `N/A` | Destino actual |
| `draw_skeleton_instance(... 11 args)` | `N/A` | Destino actual |
| `draw_skeleton_collision(... 9 args)` | `N/A` | Depuración |
| `draw_skeleton_time(... 11 args)` | `N/A` | Destino actual |
| `draw_enable_drawevent(enable)` | `N/A` | Global |
| `draw_flush()` | `N/A` | Depuración |
| `draw_clear(col)` | `N/A` | Destino actual |
| `draw_clear_alpha(col, alpha)` | `N/A` | Destino actual |
| `draw_clear_depth(depth)` | `N/A` | Búfer profundidad |
| `draw_clear_stencil(stencil)` | `N/A` | Búfer stencil |
| `draw_clear_ext([colour], [alpha], [depth], [stencil])` | `N/A` | Destino + búferes |

**Total: 28 funciones documentadas** (+ 13 variables de instancia de sprite).

---

## Fuentes

Todas las firmas se han verificado contra el manual oficial de GameMaker LTS 2026.

- Índice general de dibujo — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Drawing.htm
- Sprites y tiles — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/Sprites_And_Tiles.htm
- `draw_self` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_self.htm
- `draw_sprite` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite.htm
- `draw_sprite_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_ext.htm
- `draw_sprite_general` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_general.htm
- `draw_sprite_part` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_part.htm
- `draw_sprite_part_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_part_ext.htm
- `draw_sprite_stretched` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_stretched.htm
- `draw_sprite_stretched_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_stretched_ext.htm
- `draw_sprite_pos` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_pos.htm
- `draw_sprite_tiled` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_tiled.htm
- `draw_sprite_tiled_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_tiled_ext.htm
- `draw_enable_swf_aa` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_enable_swf_aa.htm
- `draw_set_swf_aa_level` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_set_swf_aa_level.htm
- `draw_get_swf_aa_level` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_get_swf_aa_level.htm
- `draw_enable_svg_aa` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_enable_svg_aa.htm
- `draw_set_svg_aa_level` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_set_svg_aa_level.htm
- `draw_get_svg_aa_level` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_get_svg_aa_level.htm
- `draw_skeleton` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Skeletal_Animation/Drawing_And_Miscellaneous/draw_skeleton.htm
- `draw_skeleton_instance` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Skeletal_Animation/Drawing_And_Miscellaneous/draw_skeleton_instance.htm
- `draw_skeleton_collision` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Skeletal_Animation/Drawing_And_Miscellaneous/draw_skeleton_collision.htm
- `draw_skeleton_time` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Skeletal_Animation/Drawing_And_Miscellaneous/draw_skeleton_time.htm
- `draw_enable_drawevent` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/draw_enable_drawevent.htm
- `draw_flush` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/draw_flush.htm
- `draw_clear` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_clear.htm
- `draw_clear_alpha` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Colour_And_Alpha/draw_clear_alpha.htm
- `draw_clear_depth` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/draw_clear_depth.htm
- `draw_clear_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/draw_clear_ext.htm
- `draw_clear_stencil` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/draw_clear_stencil.htm
- Sprite Instance Variables — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Instance_Variables/Sprite_Instance_Variables.htm
