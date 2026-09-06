# 03 — Texto y fuentes

> Referencia completa de GML para **GameMaker LTS 2026.0** (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Áreas: `Drawing/Text/`, `Strings/` y `Asset_Management/Fonts/`.
> Incluye el sistema **SDF** (*Signed Distance Field*), la gran novedad de tipografía en 2026.

---

## Índice

1. [Ajustes globales de texto](#ajustes-globales-de-texto)
2. [Dibujo de texto simple](#dibujo-de-texto-simple)
3. [Dibujo de texto con color](#dibujo-de-texto-con-color)
4. [Dibujo de texto transformado](#dibujo-de-texto-transformado)
5. [Combinaciones `ext`](#combinaciones-ext)
6. [Medición de texto](#medición-de-texto)
7. [Gestión de fuentes](#gestión-de-fuentes)
8. [Fuentes de sprite](#fuentes-de-sprite)
9. [Fuentes SDF (Signed Distance Field)](#fuentes-sdf-signed-distance-field)
10. [Caché de fuentes](#caché-de-fuentes)
11. [Tabla resumen](#tabla-resumen)
12. [Fuentes](#fuentes)

---

## Ajustes globales de texto

Todas las funciones `draw_text*` usan cuatro ajustes globales. Configúralos antes de dibujar:

| Ajuste | Función |
|---|---|
| Fuente | `draw_set_font()` |
| Color y alfa | `draw_set_colour()` y `draw_set_alpha()` |
| Alineación horizontal | `draw_set_halign()` |
| Alineación vertical | `draw_set_valign()` |

### `draw_set_font(font)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la fuente con la que se dibujará el texto.
- **Ejemplo:**
```gml
draw_set_font(fnt_titulo);
draw_text(32, 32, "Game Over");
draw_set_font(-1); // vuelve a la fuente por defecto
```
- **Notas / trampas:** la fuente debe existir como asset del proyecto o haber sido creada con
  `font_add`, `font_add_sprite` o `font_add_sprite_ext`. Pasa `-1` para la fuente por defecto.

### `draw_set_halign(halign)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la alineación horizontal de todo el texto posterior. Por defecto `fa_left`.

  | Constante | Alineación |
  |---|---|
  | `fa_left` | izquierda (por defecto) |
  | `fa_center` | centro |
  | `fa_right` | derecha |

- **Ejemplo:**
```gml
draw_set_halign(fa_center);
draw_text(room_width / 2, 100, "Centrado");
```
- **Notas / trampas:** la alineación cambia la posición **y la dirección** en la que se dibuja el
  texto. Recuerda restaurar `fa_left` si el resto de la interfaz lo espera.

### `draw_set_valign(valign)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la alineación vertical. Por defecto `fa_top`.

  | Constante | Alineación |
  |---|---|
  | `fa_top` | arriba (por defecto) |
  | `fa_middle` | centro vertical |
  | `fa_bottom` | abajo |

- **Ejemplo:**
```gml
draw_set_halign(fa_center);
draw_set_valign(fa_middle);
draw_text(room_width / 2, room_height / 2, "Centro exacto");
```

### `draw_get_font()`
- **Devuelve:** `Font Asset`
- **Qué hace:** devuelve la fuente actualmente asignada, o un handle inválido (`-1`) si no hay
  ninguna.
- **Ejemplo:**
```gml
var _fuente_previa = draw_get_font();
draw_set_font(fnt_titulo);
draw_text(x, y, "Título");
draw_set_font(_fuente_previa); // restaura
```

### `draw_get_halign()`
- **Devuelve:** constante de alineación horizontal (`fa_left`, `fa_center`, `fa_right`)
- **Qué hace:** devuelve la alineación horizontal actual.
- **Ejemplo:**
```gml
if (draw_get_halign() != fa_left) draw_set_halign(fa_left);
```

### `draw_get_valign()`
- **Devuelve:** constante de alineación vertical (`fa_top`, `fa_middle`, `fa_bottom`)
- **Qué hace:** devuelve la alineación vertical actual.
- **Ejemplo:**
```gml
show_debug_message($"Alineación vertical: {draw_get_valign()}");
```

---

## Dibujo de texto simple

### `draw_text(x, y, string)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja una cadena en la posición indicada usando los ajustes globales de texto.
- **Ejemplo:**
```gml
// Usa \n para saltos de línea y + para concatenar
draw_text(x, y, "Hola, " + global.nombre + "!\nEspero que estés bien.");
```
- **Notas / trampas:**
  - Usa la función `string()` para convertir números a texto antes de concatenarlos.
  - `"\n"` dentro de la cadena produce un salto de línea.

### `draw_highscore(x1, y1, x2, y2)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja la lista de puntuaciones altas almacenada por el sistema interno de
  *highscores* de GameMaker dentro del rectángulo indicado, con la fuente, color y alfa actuales.
  El espaciado y la posición se calculan automáticamente.
- **Ejemplo:**
```gml
draw_set_font(fnt_marcador);
draw_set_colour(c_white);
draw_highscore(100, 100, 700, 500);
```
- **Notas / trampas:** es específico del sistema de highscores integrado; para tus propias
  puntuaciones usa `draw_text` con tus estructuras.

---

## Dibujo de texto con color

### `draw_text_colour(x, y, string, c1, c2, c3, c4, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja texto con un **degradado de cuatro colores**, uno por esquina, y un alfa
  propio. Sustituye al color y alfa base.
- **Orden de las esquinas:** `c1` = superior izquierda, `c2` = superior derecha,
  `c3` = inferior derecha, `c4` = inferior izquierda.
- **Ejemplo:**
```gml
// Título dorado con degradado vertical
draw_text_colour(32, 32, "¡VICTORIA!",
                 c_yellow, c_yellow, c_orange, c_orange, 1);
```
- **Notas / trampas:**
  - **En HTML5 el degradado no está disponible salvo con WebGL activado.** Sin WebGL se usa el
    primer color (`c1`) para toda la fuente.
  - Cada combinación de colores crea una **copia cacheada de la fuente**. Limítalo con
    `font_set_cache_size()`.
  - Para colorear bloques grandes de texto es más eficiente usar `draw_set_colour()` +
    `draw_set_alpha()` + `draw_text()`.

---

## Dibujo de texto transformado

### `draw_text_transformed(x, y, string, xscale, yscale, angle)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja texto escalado en X/Y y rotado.
- **Ejemplo:**
```gml
// Título que late
var _escala = 1 + 0.05 * sin(current_time * 0.005);
draw_set_halign(fa_center);
draw_text_transformed(room_width / 2, 80, "NIVEL 1", _escala, _escala, 0);
```
- **Notas / trampas:**
  - El ángulo se mide en grados: `0` = normal, y cada grado por encima de 0 rota el texto **en
    sentido antihorario**.
  - Escala `1` = tamaño normal.
  - Escalar texto puede verse mal en HTML5 y móviles; el manual recomienda tener recursos de fuente
    a distintos tamaños, o fuentes grandes escaladas **hacia abajo** en lugar de hacia arriba.

### `draw_text_transformed_colour(x, y, string, xscale, yscale, angle, c1, c2, c3, c4, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** combina escala, rotación, degradado de cuatro colores y alfa.
- **Ejemplo:**
```gml
// Texto dañado: rojo, rotado y pulsando
draw_text_transformed_colour(x, y, "-10", 1.5, 1.5, -15,
                             c_red, c_red, c_maroon, c_maroon, 0.9);
```

---

## Combinaciones `ext`

Las variantes `_ext` añaden **salto de línea automático** con separación y ancho máximo
configurables.

### `draw_text_ext(x, y, string, sep, w)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja texto limitando el ancho de línea a `w` píxeles. Si una línea supera ese
  valor, GameMaker la parte **en el espacio en blanco más cercano**. Si el texto no tiene espacios,
  **sobrepasará** el ancho máximo.
- **Ejemplo:**
```gml
// Diálogo con caja de texto de 300 px y separación de 20 px entre líneas
draw_text_ext(64, 400, texto_dialogo, 20, 300);
```
- **Notas / trampas:**
  - `sep = -1` usa la separación por defecto, basada en la altura del carácter «M» de la fuente.
  - Los espacios en blanco **al principio** de la cadena o de una línea nueva no cuentan para el
    ancho máximo: funcionan como sangría.

### `draw_text_ext_colour(x, y, string, sep, w, c1, c2, c3, c4, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** combina salto de línea (`_ext`) con degradado de color.
- **Ejemplo:**
```gml
draw_text_ext_colour(64, 400, texto_dialogo, 20, 300,
                     c_white, c_white, c_gray, c_gray, 1);
```

### `draw_text_ext_transformed(x, y, string, sep, w, xscale, yscale, angle)`
- **Devuelve:** `N/A`
- **Qué hace:** combina salto de línea con escala y rotación.
- **Ejemplo:**
```gml
draw_text_ext_transformed(64, 400, texto_dialogo, 20, 300, 1.2, 1.2, 0);
```
- **Notas / trampas:** **el argumento `w` se basa en escala 1**. Si escalas el texto, ajusta `w` en
  consecuencia (con `xscale = 2`, un `w` de 300 se ve como 600 píxeles).

### `draw_text_ext_transformed_colour(x, y, string, sep, w, xscale, yscale, angle, c1, c2, c3, c4, alpha)`
- **Devuelve:** `N/A`
- **Qué hace:** la función más completa: salto de línea, escala, rotación, degradado y alfa.
- **Ejemplo:**
```gml
// Bloque de créditos: rotado, degradado y con límite de ancho
draw_text_ext_transformed_colour(100, 200, creditos, 18, 400,
                                 0.9, 0.9, -3,
                                 c_white, c_white, c_navy, c_navy, 0.95);
```

**Árbol de variantes:**

```
draw_text                                    texto simple
 ├─ draw_text_colour                         + degradado 4 esquinas + alfa
 ├─ draw_text_transformed                    + escala + rotación
 │   └─ draw_text_transformed_colour         + degradado + alfa
 └─ draw_text_ext                            + separación + ancho máximo
     ├─ draw_text_ext_colour                 + degradado + alfa
     └─ draw_text_ext_transformed            + escala + rotación
         └─ draw_text_ext_transformed_colour + degradado + alfa
```

---

## Medición de texto

Imprescindibles para centrar, ajustar cajas y detectar desbordamientos. Usan la **fuente
actualmente definida**.

### `string_width(string)`
- **Devuelve:** `Real` (píxeles)
- **Qué hace:** devuelve el ancho que ocuparía la cadena al dibujarla con `draw_text()`, teniendo en
  cuenta los saltos de línea.
- **Ejemplo:**
```gml
// Caja de tooltip ajustada al texto
var _txt = "Curar 50 PV";
var _ancho = string_width(_txt);
draw_rectangle(x, y, x + _ancho + 16, y + 28, false);
draw_text(x + 8, y + 6, _txt);
```

### `string_height(string)`
- **Devuelve:** `Real` (píxeles)
- **Qué hace:** devuelve el alto de la cadena, teniendo en cuenta la separación entre líneas y los
  saltos de línea.
- **Ejemplo:**
```gml
var _alto = string_height("Línea 1\nLínea 2");
```

### `string_width_ext(string, sep, w)`
- **Devuelve:** `Real` (píxeles)
- **Qué hace:** devuelve el **ancho máximo** que ocuparía la cadena dibujada con `draw_text_ext()`,
  es decir, tras aplicar el salto de línea automático.
- **Ejemplo:**
```gml
var _ancho = string_width_ext(texto_largo, 20, 300);
```
- **Notas / trampas:** `sep` y `w` pueden ser `-1` para usar el espaciado por defecto.

### `string_height_ext(string, sep, w)`
- **Devuelve:** `Real` (píxeles)
- **Qué hace:** devuelve el alto que ocuparía la cadena dibujada con `draw_text_ext()`, contando
  todas las líneas resultantes.
- **Ejemplo:**
```gml
// Centrar verticalmente un párrafo
var _alto = string_height_ext(texto, 20, 300);
draw_text_ext(64, (room_height - _alto) / 2, texto, 20, 300);
```

---

## Gestión de fuentes

### `font_add(name, size, bold, italic, first, last)`
- **Devuelve:** `Font Asset` (o `-1` si falla)
- **Qué hace:** añade una fuente al juego desde un archivo incluido en los **Included Files** del
  proyecto. Devuelve un handle que debes guardar.
- **Ejemplo:**
```gml
// Evento Create de un objeto persistente
global.fnt_pixel = font_add("fuentes/PressStart2P.ttf", 16, false, false, 32, 255);
if (global.fnt_pixel == -1) show_debug_message("No se pudo cargar la fuente");
```
- **Notas / trampas:**
  - El archivo debe ser **`.ttf` u `.otf`** y estar en Included Files.
  - `size`: **puntos** para Web Fonts, **píxeles** para fuentes de archivo.
  - Si no sabes qué rango usar: `first = 32`, `last = 128` (ASCII básico). Para español conviene
    llegar al menos a 255 (á, é, í, ó, ú, ñ, Ñ, ¿, ¡).
  - Devuelve `-1` si algo falla: comprueba siempre el resultado.

### `font_add_enable_aa(enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva el antialiasing para las fuentes añadidas con `font_add()`. Por
  defecto el AA está **activado**.
- **Ejemplo:**
```gml
// Píxel art: sin antialiasing
font_add_enable_aa(false);
global.fnt_pixel = font_add("PressStart2P.ttf", 16, false, false, 32, 255);
font_add_enable_aa(true);
```
- **Notas / trampas:** **debe llamarse antes** de añadir las fuentes; no afecta a las ya añadidas.
  Basta una llamada, no hace falta repetirla cada frame.

### `font_add_get_enable_aa()`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el antialiasing está activo para las fuentes añadidas con `font_add()`.
- **Ejemplo:**
```gml
if (!font_add_get_enable_aa()) show_debug_message("AA desactivado");
```

### `font_delete(ind)`
- **Devuelve:** `N/A`
- **Qué hace:** elimina una fuente del juego.
- **Ejemplo:**
```gml
// Al cerrar el nivel, liberamos la fuente cargada en caliente
font_delete(global.fnt_temporal);
global.fnt_temporal = -1;
```
- **Notas / trampas:**
  - **Es una eliminación permanente**: cambiar de room o reiniciar el juego **no** la recupera. El
    jugador tendría que salir y volver a entrar.
  - Solo tiene sentido para liberar memoria de fuentes añadidas con `font_add` o `font_add_sprite`.

### `font_exists(ind)`
- **Devuelve:** `Boolean`
- **Qué hace:** comprueba si existe una fuente con ese índice, tanto del Asset Browser como añadida
  por código.
- **Ejemplo:**
```gml
if (font_exists(global.fnt_pixel)) draw_set_font(global.fnt_pixel);
```

### `font_get_first(ind)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el primer carácter (valor ASCII) incluido al añadir la fuente.
- **Notas / trampas:**
  - **DEPRECADA.** El manual avisa de que, por cómo se gestionan ahora las fuentes, **esta función
    devuelve siempre 32**. No la uses para lógica real.

### `font_get_last(ind)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el último carácter (valor UTF-8) incluido al añadir la fuente.
- **Ejemplo:**
```gml
var _ultimo = font_get_last(fnt_dialogo);
```

### `font_get_bold(ind)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la fuente tiene la marca de **negrita**.
- **Ejemplo:**
```gml
if (font_get_bold(fnt_titulo)) show_debug_message("Es negrita");
```

### `font_get_italic(ind)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si la fuente tiene la marca de **cursiva**.
- **Ejemplo:**
```gml
if (font_get_italic(fnt_cita)) draw_set_alpha(0.8);
```

### `font_get_name(ind)`
- **Devuelve:** `String`
- **Qué hace:** devuelve el nombre que se le dio a la fuente como asset en el Asset Browser.
- **Ejemplo:**
```gml
show_debug_message(font_get_name(fnt_titulo)); // "fnt_titulo"
```
- **Notas / trampas:** es **solo una cadena**, no sirve para referenciar la fuente; para eso
  necesitas el índice.

### `font_get_size(ind)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el tamaño del recurso de fuente, el valor en puntos que muestra el
  diálogo del recurso.
- **Ejemplo:**
```gml
var _tam = font_get_size(fnt_titulo);
```

### `font_get_fontname(ind)`
- **Devuelve:** `String`
- **Qué hace:** devuelve el **nombre real del sistema** de la fuente. Por ejemplo, un asset llamado
  `fnt_main` puede devolver `"Arial"`.
- **Ejemplo:**
```gml
show_debug_message(font_get_fontname(fnt_main)); // "Arial"
```

### `font_get_texture(font)`
- **Devuelve:** `Texture`
- **Qué hace:** devuelve un puntero a la página de textura de la fuente, para usarla en primitivas o
  en shaders.
- **Ejemplo:**
```gml
var _tex_fuente = font_get_texture(fnt_titulo);
texture_set_stage(u_sampler, _tex_fuente);
```
- **Notas / trampas:** combínalo con `texture_get_width()`, `texture_get_height()`,
  `texture_get_uvs()` o `texture_get_texel_width/height()`.

### `font_get_uvs(font)`
- **Devuelve:** `Array` de 4 elementos
- **Qué hace:** devuelve las coordenadas UV de la textura de la fuente en su página de textura:

  | Índice | Valor |
  |---|---|
  | `[0]` | izquierda (*left*) |
  | `[1]` | arriba (*top*) |
  | `[2]` | derecha (*right*) |
  | `[3]` | abajo (*bottom*) |

- **Ejemplo:**
```gml
var _uv = font_get_uvs(fnt_titulo);
var _u0 = _uv[0], _v0 = _uv[1], _u1 = _uv[2], _v1 = _uv[3];
```
- **Notas / trampas:** esencial para mapear correctamente una fuente sobre un vertex buffer.

### `font_get_info(ind)`
- **Devuelve:** `Struct`
- **Qué hace:** devuelve información del recurso de fuente en forma de struct.
- **Ejemplo:**
```gml
var _info = font_get_info(fnt_titulo);
show_debug_message(_info);
```

### `font_get_sdf_enabled(ind)`
- **Devuelve:** `Boolean`
- **Qué hace:** indica si el renderizado **SDF** está activado para esa fuente.
- **Ejemplo:**
```gml
if (!font_get_sdf_enabled(fnt_titulo)) font_enable_sdf(fnt_titulo, true);
```

### `font_get_sdf_spread(ind)`
- **Devuelve:** `Real`
- **Qué hace:** devuelve el valor *spread* de una fuente con SDF activado.
- **Ejemplo:**
```gml
var _spread = font_get_sdf_spread(fnt_titulo);
```
- **Notas / trampas:** si la fuente no existe, devuelve `-1`.

---

## Fuentes de sprite

Permiten crear una fuente a partir de una tira de sprites (*sprite strip*) donde cada subimage es
un glifo. Muy útiles para tipografías de píxel art o iconos.

### `font_add_sprite(spr, first, prop, sep)`
- **Devuelve:** `Font Asset`
- **Qué hace:** crea una fuente a partir de una tira de sprites. `first` es el número de mapa UTF-8
  del primer carácter (usa `ord()` para obtenerlo). El glifo «primero» tendrá `image_index` 0.
- **Ejemplo:**
```gml
// Tira de sprites que empieza en "!" y va en orden ASCII
global.fnt_pixel = font_add_sprite(spr_glifos, ord("!"), true, 2);
```
- **Notas / trampas:**
  - Usa `ord()` para obtener el valor UTF-8 correcto de la letra inicial.
  - El espacio puedes definirlo con cualquier carácter; su anchura será la del espacio, pero **esa
    imagen nunca se dibuja**.
  - Si no proporcionas sprite para el espacio, se usa la anchura del carácter más ancho.
  - `prop = true` → fuente proporcional; `false` → monoespaciada.

### `font_add_sprite_ext(spr, string_map, prop, sep)`
- **Devuelve:** `Font Asset`
- **Qué hace:** igual que `font_add_sprite` pero el orden de los glifos se toma de una **cadena**
  (`string_map`) en lugar de un rango ASCII consecutivo. El sprite **debe** ser un asset del Asset
  Browser o añadido con `sprite_add()`.
- **Ejemplo:**
```gml
// Solo los caracteres que necesito, en el orden de la cadena
global.fnt_digitos = font_add_sprite_ext(spr_numeros, "0123456789:+-%", false, 1);
```
- **Notas / trampas:** es la opción recomendada para fuentes de iconos o juegos de caracteres
  limitados (marcadores, HUD).

### `font_replace_sprite(ind, spr, first, prop, sep)`
- **Devuelve:** `N/A` — sustituye los glifos **en el propio recurso `ind`**, no crea uno nuevo.
- **Qué hace:** sustituye los glifos de una fuente existente por los de una tira de sprites, con la
  misma semántica que `font_add_sprite`.
- **Ejemplo:**
```gml
// Reemplaza los glifos del font creado arriba (global.fnt_pixel) por otra tira de sprites
font_replace_sprite(global.fnt_pixel, spr_glifos_alt, ord("!"), true, 2);
```

### `font_replace_sprite_ext(ind, spr, string_map, prop, sep)`
- **Devuelve:** `N/A` — sustituye los glifos **en el propio recurso `ind`**, no crea uno nuevo.
- **Qué hace:** igual que `font_replace_sprite` pero tomando el orden de una cadena.
- **Ejemplo:**
```gml
// Reemplaza los glifos del font creado arriba (global.fnt_digitos) por otra tira de sprites
font_replace_sprite_ext(global.fnt_digitos, spr_numeros_hd, "0123456789", false, 1);
```

---

## Fuentes SDF (Signed Distance Field)

**Novedad destacada de 2026.** El renderizado SDF almacena, en lugar del glifo dibujado, el **campo
de distancia con signo** hasta su borde. Esto permite escalar el texto sin perder nitidez y aplicar
efectos de contorno, brillo y sombra **directamente en la fuente**, sin shaders propios ni copias
del texto.

### `font_enable_sdf(ind, enable)`
- **Devuelve:** `N/A`
- **Qué hace:** activa o desactiva el renderizado SDF de una fuente.
- **Ejemplo:**
```gml
// Cargar fuente y activarle SDF en tiempo de ejecución
global.fnt_ui = font_add("Inter.ttf", 24, false, false, 32, 255);
font_enable_sdf(global.fnt_ui, true);
```
- **Notas / trampas:**
  - La fuente **debe** haber sido añadida con `font_add()` y cargada desde archivo. **No funciona
    con fuentes de sprite** ni con fuentes añadidas desde el IDE.
  - **No funciona en HTML5**, porque HTML5 no admite añadir fuentes freetype. En HTML5 puedes usar
    SDF activándolo en el Font Editor del IDE.

### `font_sdf_spread(ind, spread)`
- **Devuelve:** `N/A`
- **Qué hace:** cambia el valor *spread* de una fuente con SDF. El spread es la distancia en píxeles
  que se extiende el campo de distancia desde el borde de cada glifo.
- **Rango:** de **2** a **32** píxeles inclusive. **Por defecto: 8.**
- **Ejemplo:**
```gml
// Spread grande para un glow amplio
font_sdf_spread(fnt_titulo, 24);
```
- **Notas / trampas:**
  - **El spread limita cuánto puede extenderse un efecto** desde el borde del glifo.
  - Un spread mayor permite efectos de radio mayor (glows grandes) pero **ocupa más espacio en la
    página de textura**.
  - Un spread menor ahorra textura y **mejora la precisión** de renderizado.

### `font_enable_effects(ind, enable, [params])`
- **Devuelve:** `N/A`
- **Qué hace:** activa efectos sobre una fuente **con SDF habilitado**. Las propiedades se pasan en
  el struct opcional `params`. Los efectos aparecen al usar la fuente con `draw_set_font()` o en una
  pista de texto de una secuencia.
- **Efectos disponibles:** contorno (*Outline*), brillo (*Glow*) y sombra proyectada
  (*Drop Shadow*). Se pueden combinar todos a la vez.

#### Propiedades generales

| Propiedad | Descripción | Rango |
|---|---|---|
| `thickness` | Añade o quita grosor a la fuente | −32 a 32 |
| `coreColour` | Color del núcleo de la fuente (sin contornos ni brillos) | Colour |
| `coreAlpha` | Alfa del núcleo | 0 a 1 |

#### Contorno (*Outline*)

| Propiedad | Descripción | Rango |
|---|---|---|
| `outlineEnable` | Activa el contorno (**desactivado** por defecto) | Boolean |
| `outlineDistance` | Grosor del contorno desde el borde del glifo | 0 a 64 |
| `outlineColour` | Color del contorno | Colour |
| `outlineAlpha` | Alfa del contorno | 0 a 1 |

#### Brillo (*Glow*)

| Propiedad | Descripción | Rango |
|---|---|---|
| `glowEnable` | Activa el brillo (**desactivado** por defecto) | Boolean |
| `glowStart` | Distancia desde el borde donde el brillo empieza a desvanecerse | 0 a 64 |
| `glowEnd` | Distancia desde el borde donde el brillo se ha desvanecido por completo | 0 a 64 |
| `glowColour` | Color del brillo | Colour |
| `glowAlpha` | Alfa del brillo | 0 a 1 |

#### Sombra proyectada (*Drop Shadow*)

| Propiedad | Descripción | Rango |
|---|---|---|
| `dropShadowEnable` | Activa la sombra (**desactivada** por defecto) | Boolean |
| `dropShadowSoftness` | Suavidad o nivel de desenfoque de la sombra | 0 a 64 |
| `dropShadowOffsetX` | Desplazamiento en X (4 = 4 px a la derecha) | Real |
| `dropShadowOffsetY` | Desplazamiento en Y (4 = 4 px hacia abajo) | Real |
| `dropShadowColour` | Color de la sombra | Colour |
| `dropShadowAlpha` | Alfa de la sombra | 0 a 1 |

- **Ejemplo 1 — contorno y brillo en dos fuentes distintas:**
```gml
// Evento Create
font_enable_effects(fnt_contorno, true, {
    outlineEnable:   true,
    outlineDistance: 2,
    outlineColour:   c_black
});

font_enable_effects(fnt_brillo, true, {
    glowEnable: true,
    glowEnd:    16,
    glowColour: c_red
});

// Evento Draw
draw_set_font(fnt_contorno);
draw_text(x, y, "Esta fuente tiene contorno.");

draw_set_font(fnt_brillo);
draw_text(x, y + 60, "Esta fuente tiene brillo.");
```
- **Ejemplo 2 — sombra proyectada suave:**
```gml
font_enable_effects(fnt_titular, true, {
    dropShadowEnable:    true,
    dropShadowSoftness:  20,
    dropShadowOffsetX:   4,
    dropShadowOffsetY:   4,
    dropShadowColour:    c_black,
    dropShadowAlpha:     0.75
});
```
- **Notas / trampas:**
  - **El valor de spread SDF limita cuánto puede extenderse el efecto** desde el borde del glifo.
    Si tu glow se corta, sube `font_sdf_spread()`.
  - **El desplazamiento de la sombra se ve afectado por la escala** de dibujo del texto: un
    desplazamiento de 10 px se convierte en 100 px si dibujas con escala 10.
  - **El color del efecto se multiplica** por el color de mezcla que esté puesto al dibujar el
    texto.

---

## Caché de fuentes

### `font_set_cache_size(ind, max)`
- **Devuelve:** `N/A`
- **Qué hace:** fija cuántas copias mezcladas de la fuente pueden cachearse antes de sobrescribir
  las antiguas.
- **Ejemplo:**
```gml
// Evita que el degradado de texto llene la caché en HTML5
font_set_cache_size(fnt_dialogo, 8);
```
- **Notas / trampas:**
  - Existe porque **HTML5 no puede hacer mezcla de color dinámica** como un ejecutable: GameMaker
    guarda una copia mezclada de las imágenes y la carga cuando hace falta.
  - **Valor por defecto: 4.**
  - Para fuentes de sprite usa `sprite_set_cache_size()`.

### `font_texture_page_size`
- **Devuelve:** `Real` (anchura/altura máxima en píxeles)
- **Qué hace:** **variable integrada** (*built-in variable*) que permite leer o fijar el tamaño de
  la página de textura que se crea al usar `font_add()`. GameMaker genera una caché de los glifos
  necesarios hasta el tamaño definido por esta variable.
- **Ejemplo:**
```gml
// Páginas de textura más grandes para fuentes con muchos glifos (CJK, por ejemplo)
font_texture_page_size = 2048;
global.fnt_cjk = font_add("NotoSansSC.ttf", 24, false, false, 32, 65535);
```
- **Notas / trampas:**
  - El proceso es incremental: cada carácter que usas se cachea en la página de textura.
  - Cuando la página se llena (por usar caracteres grandes o muchos distintos), GameMaker crea
    otra página.

### `font_cache_glyph(font, glyph_index)`
- **Devuelve:** `Struct` con la posición del glifo en la página de textura, p. ej. `{ x: 208, y: 62 }`
- **Qué hace:** pre-cachea un glifo concreto de una fuente, evitando el coste de cachearlo en el
  momento de dibujarlo por primera vez.
- **Ejemplo:**
```gml
// Pre-cachear en la carga para evitar tirones al mostrar el HUD
for (var _c = ord("0"); _c <= ord("9"); _c++)
{
    font_cache_glyph(fnt_hud, _c);
}

// Obtener el handle de la página de textura donde está el glifo
var _tex = font_get_texture(fnt_hud);
```
- **Notas / trampas:**
  - Si no pre-cacheas un carácter, **se cachea automáticamente** justo antes de dibujarse por
    primera vez.
  - `glyph_index` es el código del carácter: usa `ord()` o `string_ord_at()`.

---

## Tabla resumen

| Función | Devuelve |
|---|---|
| `draw_set_font(font)` | `N/A` |
| `draw_set_halign(halign)` | `N/A` |
| `draw_set_valign(valign)` | `N/A` |
| `draw_get_font()` | `Font Asset` |
| `draw_get_halign()` | Constante |
| `draw_get_valign()` | Constante |
| `draw_text(x, y, string)` | `N/A` |
| `draw_text_colour(x, y, str, c1, c2, c3, c4, alpha)` | `N/A` |
| `draw_text_transformed(x, y, str, xscale, yscale, angle)` | `N/A` |
| `draw_text_transformed_colour(x, y, str, xs, ys, ang, c1..c4, alpha)` | `N/A` |
| `draw_text_ext(x, y, string, sep, w)` | `N/A` |
| `draw_text_ext_colour(x, y, str, sep, w, c1..c4, alpha)` | `N/A` |
| `draw_text_ext_transformed(x, y, str, sep, w, xs, ys, angle)` | `N/A` |
| `draw_text_ext_transformed_colour(x, y, str, sep, w, xs, ys, ang, c1..c4, alpha)` | `N/A` |
| `draw_highscore(x1, y1, x2, y2)` | `N/A` |
| `string_width(string)` | `Real` |
| `string_height(string)` | `Real` |
| `string_width_ext(string, sep, w)` | `Real` |
| `string_height_ext(string, sep, w)` | `Real` |
| `font_add(name, size, bold, italic, first, last)` | `Font Asset` |
| `font_add_enable_aa(enable)` | `N/A` |
| `font_add_get_enable_aa()` | `Boolean` |
| `font_add_sprite(spr, first, prop, sep)` | `Font Asset` |
| `font_add_sprite_ext(spr, string_map, prop, sep)` | `Font Asset` |
| `font_replace_sprite(spr, first, prop, sep)` | `Font Asset` |
| `font_replace_sprite_ext(spr, string_map, prop, sep)` | `Font Asset` |
| `font_delete(ind)` | `N/A` |
| `font_exists(ind)` | `Boolean` |
| `font_get_first(ind)` | `Real` — **DEPRECADA, devuelve siempre 32** |
| `font_get_last(ind)` | `Real` |
| `font_get_bold(ind)` | `Boolean` |
| `font_get_italic(ind)` | `Boolean` |
| `font_get_name(ind)` | `String` |
| `font_get_size(ind)` | `Real` |
| `font_get_fontname(ind)` | `String` |
| `font_get_info(ind)` | `Struct` |
| `font_get_texture(font)` | `Texture` |
| `font_get_uvs(font)` | `Array` |
| `font_enable_sdf(ind, enable)` | `N/A` |
| `font_get_sdf_enabled(ind)` | `Boolean` |
| `font_sdf_spread(ind, spread)` | `N/A` |
| `font_get_sdf_spread(ind)` | `Real` |
| `font_enable_effects(ind, enable, [params])` | `N/A` |
| `font_set_cache_size(ind, max)` | `N/A` |
| `font_cache_glyph(font, glyph_index)` | `Struct` |
| `font_texture_page_size` | `Real` (variable integrada) |

**Total: 46 funciones/variables documentadas.**

### Funciones que NO existen

| Solicitada | Estado |
|---|---|
| `font_replace()` | **No existe.** Existen `font_replace_sprite()` y `font_replace_sprite_ext()` |
| `font_get_cache_size()` | **No existe.** Solo existe el *setter* `font_set_cache_size()` |

---

## Fuentes

- Text — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/Text.htm
- `draw_set_font` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_set_font.htm
- `draw_set_halign` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_set_halign.htm
- `draw_set_valign` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_set_valign.htm
- `draw_get_font` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_get_font.htm
- `draw_get_halign` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_get_halign.htm
- `draw_get_valign` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_get_valign.htm
- `draw_text` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_text.htm
- `draw_text_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_text_ext.htm
- `draw_text_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_text_colour.htm
- `draw_text_transformed` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_text_transformed.htm
- `draw_text_transformed_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_text_transformed_colour.htm
- `draw_text_ext_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_text_ext_colour.htm
- `draw_text_ext_transformed` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_text_ext_transformed.htm
- `draw_text_ext_transformed_colour` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_text_ext_transformed_colour.htm
- `draw_highscore` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text/draw_highscore.htm
- `string_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/string_width.htm
- `string_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/string_height.htm
- `string_width_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/string_width_ext.htm
- `string_height_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/string_height_ext.htm
- Fonts — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/Fonts.htm
- `font_add` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_add.htm
- `font_add_enable_aa` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_add_enable_aa.htm
- `font_add_get_enable_aa` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_add_get_enable_aa.htm
- `font_add_sprite` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_add_sprite.htm
- `font_add_sprite_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_add_sprite_ext.htm
- `font_replace_sprite` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_replace_sprite.htm
- `font_replace_sprite_ext` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_replace_sprite_ext.htm
- `font_delete` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_delete.htm
- `font_exists` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_exists.htm
- `font_get_first` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_first.htm
- `font_get_last` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_last.htm
- `font_get_bold` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_bold.htm
- `font_get_italic` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_italic.htm
- `font_get_name` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_name.htm
- `font_get_size` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_size.htm
- `font_get_fontname` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_fontname.htm
- `font_get_info` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_info.htm
- `font_get_texture` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_texture.htm
- `font_get_uvs` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_uvs.htm
- `font_enable_sdf` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_enable_sdf.htm
- `font_get_sdf_enabled` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_sdf_enabled.htm
- `font_sdf_spread` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_sdf_spread.htm
- `font_get_sdf_spread` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_get_sdf_spread.htm
- `font_enable_effects` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_enable_effects.htm
- `font_set_cache_size` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_set_cache_size.htm
- `font_texture_page_size` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_texture_page_size.htm
- `font_cache_glyph` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_cache_glyph.htm
