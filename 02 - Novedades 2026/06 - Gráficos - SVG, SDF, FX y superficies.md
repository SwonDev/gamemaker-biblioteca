# Gráficos: SVG, SDF, FX, superficies y texturas (LTS 2026.0)

---

## 1. Sprites SVG (vectoriales)

### 1.1 Qué se ha añadido

Ahora puedes **importar y previsualizar imágenes SVG en la IDE**, y esa imagen llega al juego en tiempo de compilación.

Cosas verificadas en los release notes:

- Los SVG funcionan con la herramienta **"Import As Strip"**, que convierte el SVG en **fotogramas separados** dentro del sprite.
- Puedes **arrastrar SVGs al panel de previsualización de fotogramas** para añadirlos como fotogramas adicionales.
- ⚠️ No todo el estándar SVG está soportado. Los límites concretos están en estos issues: #5895, #8276, #8275, #8274.

> ⚠️ **GMRT no soporta assets SVG** (aparece en la lista de incompatibilidades conocidas de 0.20.0 y 0.21.0).

### 1.2 Gestión de la caché de sprites vectoriales

Los SVG se rasterizan en runtime, así que GameMaker mantiene una **caché** de esas rasterizaciones. Hay nueve funciones para controlarla:

| Función | Tipo | Qué hace |
|---|---|---|
| `vector_sprite_cache_limit(v)` | setter | Límite de la caché |
| `vector_sprite_cache_get_limit()` | getter | Límite actual |
| `vector_sprite_cache_get_used()` | getter | Uso actual |
| `vector_sprite_cache_get_max_used()` | getter | Pico de uso |
| `vector_sprite_cache_prune_age(v)` | setter | Antigüedad a partir de la cual se podan entradas |
| `vector_sprite_cache_get_prune_age()` | getter | Valor actual de prune age |
| `vector_sprite_cache_prune_fraction(v)` | setter | Fracción de la caché que se poda |
| `vector_sprite_cache_get_prune_fraction()` | getter | Valor actual de prune fraction |
| `vector_sprite_cache_get_oldest_entry_age()` | getter | Antigüedad de la entrada más vieja |

```gml
// Create Event de un objeto de control / arranque

// Limita la caché de sprites vectoriales a 64 MB
vector_sprite_cache_limit(64);

// Poda las entradas con más de 30 segundos sin usarse
vector_sprite_cache_prune_age(30);

// Cuando hay que podar, libera el 25 % de la caché
vector_sprite_cache_prune_fraction(0.25);

// Diagnóstico (útil en el Debug Overlay)
show_debug_message($"Caché vectorial: límite={vector_sprite_cache_get_limit()}");

// En un evento de depuración, para vigilar el consumo:
show_debug_message($"usada={vector_sprite_cache_get_used()} pico={vector_sprite_cache_get_max_used()}");
show_debug_message($"entrada más vieja={vector_sprite_cache_get_oldest_entry_age()}");
```

> He verificado los **nombres** de las nueve funciones contra el índice oficial de *Sprite Manipulation* del manual LTS. Los tipos exactos de argumento y retorno de cada una **no** los he verificado uno a uno en sus páginas individuales: consúltalas antes de usarlas en código de producción.

---

## 2. Fuentes SDF

### 2.1 Qué es SDF

**SDF** = *Signed Distance Field*. En lugar de guardar la fuente como bitmap, guarda la distancia al borde de cada glifo. Resultado: **el texto escala con calidad**, sin pixelarse ni necesitar múltiples tamaños de fuente.

### 2.2 Cómo activarlo

Dos vías:

**A) En la IDE**, desde el **Font Editor**.

**B) En runtime** con `font_enable_sdf()`:

```gml
font_enable_sdf(ind, enable);
// ind:    Font Asset
// enable: Boolean
// devuelve: N/A
```

⚠️ Restricciones:

- La fuente debe haberse añadido con **`font_add()`** cargándola desde un fichero de fuente.
- **No funciona con sprite fonts** ni con fuentes añadidas desde la IDE.
- **No funciona en HTML5** (HTML5 no soporta añadir fuentes freetype). Pero en HTML5 **sí puedes usar SDF activándolo desde la IDE**.

### 2.3 Ejemplo: texto que escala sin perder nitidez

```gml
// Create Event
new_font = font_add("STENCIL.TTF", 32, false, false, 32, 128);
font_enable_sdf(new_font, true);

// Draw Event
draw_set_font(new_font);
draw_set_halign(fa_center);
draw_set_valign(fa_middle);

var _sinval = dsin(current_time / 4);
var _scale  = 4 * (1 + _sinval * 0.3);

draw_text_transformed(500, 400, "Hola Mundo! (versión animada)", _scale, _scale, 0);
```

### 2.4 `font_sdf_spread()`

Controla el **spread** del SDF. Relacionado con los efectos (ver abajo): el spread **limita hasta dónde puede extenderse un efecto** desde el borde del glifo.

### 2.5 `font_get_sdf_enabled()`

Comprueba si una fuente tiene SDF activado.

---

## 3. Efectos de fuente: `font_enable_effects()`

Una vez que una fuente tiene SDF activado, puedes aplicarle **outline**, **glow** y **drop shadow**.

```gml
font_enable_effects(ind, enable, [params]);
// ind:     Font Asset (debe tener SDF activado)
// enable:  Boolean
// params:  Struct OPCIONAL con las propiedades de los efectos
// devuelve: N/A
```

Los efectos aparecen al usar la fuente con `draw_set_font()` o en una **text track de una Sequence**.

### 3.1 Propiedades generales

| Propiedad | Rango | Qué hace |
|---|---|---|
| `thickness` | −32 … 32 | Añade o quita grosor a la fuente |
| `coreColour` | color | Color del núcleo (sin contorno, glow, etc.) |
| `coreAlpha` | 0…1 | Alfa del núcleo |

### 3.2 Outline

| Propiedad | Rango | Defecto |
|---|---|---|
| `outlineEnable` | bool | **desactivado** |
| `outlineDistance` | 0 … 64 | — |
| `outlineColour` | color | — |
| `outlineAlpha` | 0…1 | — |

### 3.3 Glow

| Propiedad | Rango | Defecto |
|---|---|---|
| `glowEnable` | bool | **desactivado** |
| `glowStart` | 0 … 64 | distancia desde el borde donde empieza a desvanecerse |
| `glowEnd` | 0 … 64 | distancia donde se ha desvanecido por completo |
| `glowColour` | color | — |
| `glowAlpha` | 0…1 | — |

### 3.4 Drop Shadow

| Propiedad | Rango | Defecto |
|---|---|---|
| `dropShadowEnable` | bool | **desactivado** |
| `dropShadowSoftness` | 0 … 64 | nivel de desenfoque |
| `dropShadowOffsetX` | px | desplazamiento X |
| `dropShadowOffsetY` | px | desplazamiento Y |
| `dropShadowColour` | color | — |
| `dropShadowAlpha` | 0…1 | — |

> ⚠️ **El offset de la sombra se ve afectado por la escala**: un offset de 10 px se convierte en 100 px si dibujas con escala 10.
> El color de un efecto se **multiplica** por el color de blend que esté puesto al dibujar.

### 3.5 Ejemplos

```gml
// Create Event — un efecto por fuente
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

// Draw Event
draw_set_font(fnt_contorno);
draw_text(x, y, "Esta fuente tiene contorno.");

draw_set_font(fnt_brillo);
draw_text(x, y + 60, "Esta fuente tiene brillo.");
```

Varios efectos a la vez en la misma fuente:

```gml
// Create Event
font_enable_effects(fnt_titulo, true, {
    dropShadowEnable:    true,
    dropShadowSoftness:  20,
    dropShadowOffsetX:   4,
    dropShadowOffsetY:   4,
    dropShadowAlpha:     1,
    outlineEnable:       true,
    outlineDistance:     2,
    outlineColour:       c_black,
    glowEnable:          true,
    glowEnd:             6,
    glowColour:          c_red,
    glowAlpha:           4
});
```

---

## 4. Filters & Effects (FX)

### 4.1 FX nuevos en 2026.0

Según los release notes, se han añadido estos tipos de capa:

- **Old Film** (`_filter_old_film`)
- **Hue** (`_filter_hue`)
- **Ripples** (`_filter_ripples`)
- **Blocks Background** (`_filter_blocks`)
- **Panorama Background** (`_filter_panorama`)
- **Parallax Background** (`_filter_parallax`)

Y se ha corregido el filtro **Boxes**, que antes no funcionaba en HTML5.

⚠️ **Corrección:** `_filter_hard_drop_shadow` es un **Filter**, no un Effect — su propio identificador lleva el prefijo `_filter_` y así lo confirma la tabla oficial (§4.5). Es nuevo en 2026.0, pero se añade a la lista de Filters de arriba, no a la de Effects.

En la sección de **Effects** (que solo funcionan en juego, no como filtro de capa) están los nuevos:

- **Glow** (`_effect_glow`)
- **Recursive Blur** (`_effect_recursive_blur`)
- **Gaussian Blur** (`_effect_gaussian_blur`)
- **Windblown Particles** (`_effect_windblown_particles`)

### 4.2 Parámetros de los FX más relevantes

**Glow** (`_effect_glow`)

| Parámetro IDE | Parámetro runtime | Tipo |
|---|---|---|
| Radius | `g_GlowRadius` | Real |
| Quality | `g_GlowQuality` | Real |
| Intensity | `g_GlowIntensity` | Real |
| Gamma | `g_GlowGamma` | Real |
| Alpha | `g_GlowAlpha` | Real |

> ⚠️ Puede reducir el rendimiento en dispositivos poco potentes.

**Recursive Blur** (`_effect_recursive_blur`)

| Parámetro IDE | Parámetro runtime | Tipo |
|---|---|---|
| Radius | `g_RecursiveBlurRadius` | Real |
| Quality | `g_RecursiveBlurQuality` | Real |
| Gamma | `g_RecursiveBlurGamma` | Real |

"Recursive" se refiere al método: **es más rápido que un filtro de blur normal**. Aun así, puede penalizar en dispositivos flojos.

**Hard Drop Shadow** (`_filter_hard_drop_shadow`)

| Parámetro IDE | Parámetro runtime | Tipo |
|---|---|---|
| X Displacement | `g_DisplacementX` | Real |
| Y Displacement | `g_DisplacementY` | Real |
| Opacity | `g_Opacity` | Real |
| Colour | `g_Colour` | Array |

**Gaussian Blur** (`_effect_gaussian_blur`) — más rápido que Large Blur

| Parámetro IDE | Parámetro runtime | Tipo |
|---|---|---|
| Downsample Count | `g_numDownsamples` | Real |
| Passes | `g_numPasses` | Real |
| Intensity | `g_intensity` | Real |

- *Downsample Count*: veces que se reduce la imagen antes de desenfocar → más intensidad, pero puede dejar bloques.
- *Passes*: veces que se aplica el blur en cada nivel → más intensidad, más coste.

### 4.3 Ejemplo: crear y modificar un FX en runtime

```gml
// Create Event
fx_glow = fx_create("_effect_glow");

// Draw / Step — modificar parámetros
fx_set_parameter(fx_glow, "g_GlowRadius",    8);
fx_set_parameter(fx_glow, "g_GlowIntensity", 1.4);
fx_set_parameter(fx_glow, "g_GlowAlpha",     0.9);

// Aplicar a una capa
layer_set_fx("Effects", fx_glow);
```

> Los nombres internos (`"_effect_glow"`, etc.) son los que se pasan a `fx_create()`. Los parámetros de runtime son los que se usan con las funciones de Filter/Effect.

### 4.4 Limitaciones generales de los FX

- **No funcionan si el application surface está desactivado** (`application_surface_enable(false)`). Los FX necesitan esa textura para trabajar.
- Los FX que usan una imagen de textura requieren que esa imagen esté en una **texture page separada** (se configura en el Sprite Editor).

### 4.5 Catálogo completo de FX (42 tipos)

Los apartados anteriores solo cubren los 11 FX nuevos de 2026.0. La tabla oficial de *Filters &
Effects* tiene **42 tipos: 36 Filters + 6 Effects** — verificado fila a fila contra
`manual-lts-2026-en/The_Asset_Editors/Room_Properties/FX/All_Filter_Effect_Types.md`
(el espejo español de esa página tenía identificadores traducidos y filas incompletas; ya está
corregido, ver [`09 - Manual oficial/README.md`](../09%20-%20Manual%20oficial/README.md)).

La diferencia entre ambas categorías: un **Filter** se puede previsualizar en el Room Editor y
usarse como filtro de capa o de capa única; un **Effect** solo existe en tiempo de juego, nunca
se previsualiza en el editor. `_filter_hard_drop_shadow` es Filter pese a añadirse junto a los
Effects nuevos de 2026.0 (§4.1 lo tenía mal listado; ya corregido).

| Tipo (nombre EN) | Identificador exacto | Categoría | Parámetros `g_*`/`param_*` principales | Para qué sirve |
|---|---|---|---|---|
| Fondo de bloques (Blocks Background) | `"_filter_blocks"` | Filter | `g_BlocksPosition`, `g_BlocksPerspective`, `g_BlocksShading` | fondo generativo de bloques 3D en perspectiva, útil para menús o transiciones |
| Cajas (Boxes) | `"_filter_boxes"` | Filter | `g_BoxesScale`, `g_BoxesSize`, `g_BoxesDisplacement` | fondo de cajas en mosaico animadas, decorativo o de menú |
| Nubes (Clouds) | `"_filter_clouds"` | Filter | `g_CloudScale`, `g_CloudVelocity`, `g_CloudTurbulence` | capa de nubes animadas para climas o fondos de cielo |
| Balance de color (Colour Balance) | `"_filter_colour_balance"` | Filter | `g_ColourBalanceShadows`, `g_ColourBalanceMidtones`, `g_ColourBalanceHighlights` | corrección de color por rangos tonales (sombras/medios/luces), para grading |
| Tinte de color (Colour Tint) | `"_filter_tintfilter"` | Filter | `g_TintCol` | tintar toda la pantalla de un color (ej. daño, veneno, filtro nocturno) |
| Colorear (Colourise) | `"_filter_colourise"` | Filter | `g_Intensity`, `g_TintCol` | recolorear todo el contenido a un tono y saturación fijos |
| Contraste (Constrast) | `"_filter_contrast"` | Filter | `g_ContrastIntensity`, `g_ContrastBrightness` | ajuste rápido de contraste y brillo global |
| Desaturar (Desaturate) | `"_filter_greyscale"` | Filter | `g_Intensity` | reduce saturación (pantalla de pausa, muerte, flashback en blanco y negro) |
| Distorsionar (Distort) | `"_filter_distort"` | Filter | `g_DistortScale`, `g_DistortAmount`, `g_DistortOffset` | distorsión con textura propia (ondas de calor con forma personalizada) |
| Fondo de puntos (Dots Background) | `"_filter_dots"` | Filter | `g_DotsScale`, `g_DotsSize`, `g_DotsOffset` | fondo o efecto de puntos en mosaico; con escala baja funciona como ruido |
| Detección de bordes (Edge Detect) | `"_filter_edgedetect"` | Filter | `g_Threshold` | modo "solo contornos", útil para efectos tipo boceto o rayos X |
| Ruido fractal (Fractal Noise) | `"_filter_fractal_noise"` | Filter | `g_FractalNoiseScale`, `g_FractalNoisePersistence`, `g_FractalNoiseOffset` | ruido fractal animado; base para nubes, humo o texturas orgánicas |
| Gradiente (Gradient) | `"_filter_gradient"` | Filter | `g_GradientColour1`, `g_GradientColour2`, `g_GradientPosition1` | degradado de dos colores con posición y modo configurables, para HUD o cielo |
| Sombra proyectada nítida (Hard Drop Shadow) | `"_filter_hard_drop_shadow"` | Filter | `g_DisplacementX`, `g_DisplacementY`, `g_Opacity` | sombra proyectada nítida con offset fijo (X, Y), para texto o HUD |
| Neblina de calor (Heat Haze) | `"_filter_heathaze"` | Filter | `g_Distort1Speed`, `g_Distort2Speed`, `g_Distort1Scale` | neblina de calor animada de doble distorsión, para desiertos o lava |
| Tono (Hue) | `"_filter_hue"` | Filter | `g_HueShift`, `g_HueSaturation` | rotación de matiz y saturación de toda la pantalla |
| Desenfoque grande (Large Blur) | `"_filter_large_blur"` | Filter | `g_Radius`, `g_NoiseTexture` | desenfoque general; más lento que `_effect_gaussian_blur`, evitarlo si hay alternativa |
| Desenfoque lineal (Linear Blur) | `"_filter_linear_blur"` | Filter | `g_LinearBlurVector`, `g_NoiseTexture` | desenfoque direccional (motion blur en un eje) |
| Gradación de color por LUT (LUT Colour Grading) | `"_filter_lut_colour"` | Filter | `g_LUTColourIntensity`, `g_LUTColourTexture` | color grading por textura LUT (look cinematográfico) |
| Máscara (Mask) | `"_filter_mask"` | Filter | `g_MaskStart`, `g_MaskEnd`, `g_MaskTexture` | recorta el contenido según la luminosidad de un sprite (máscaras de forma) |
| Película antigua (Old Film) | `"_filter_old_film"` | Filter | `g_OldFilmFlickerIntensity`, `g_OldFilmFlickerSpeed`, `g_OldFilmJitterIntensity` | look de película antigua: parpadeo, grano, motas, barras y viñeteado en anillo |
| Contorno (Outline) | `"_filter_outline"` | Filter | `g_OutlineColour`, `g_OutlineRadius`, `g_OutlinePixelScale` | contorno alrededor del contenido opaco; usar como FX de capa única (`fx_set_single_layer`) |
| Fondo panorámico (Panorama Background) | `"_filter_panorama"` | Filter | `g_PanoramaDirection`, `g_PanoramaPerspective`, `g_PanoramaCylinder` | fondo panorámico con perspectiva, para escenas 3D falsas o cielos envolventes |
| Fondo parallax (Parallax Background) | `"_filter_parallax"` | Filter | `g_ParallaxDirection`, `g_ParallaxPerspective`, `g_ParallaxPosition` | fondo con perspectiva 3D plana y niebla de profundidad; puede costar en gama baja |
| Pixelar (Pixelate) | `"_filter_pixelate"` | Filter | `g_CellSize` | pixelado ajustable (transición, estilo retro, censura) |
| Posterizar (Posterise) | `"_filter_posterise"` | Filter | `g_ColourLevels` | reduce los niveles de color por canal (look de cómic o PS1) |
| Ruido RGB (RGB Noise) | `"_filter_rgbnoise"` | Filter | `g_RGBNoiseIntensity`, `g_RGBNoiseAnimation`, `g_RGBNoiseColour` | ruido de color animado (estática de TV, glitch) |
| Ondulaciones (Ripples) | `"_filter_ripples"` | Filter | `g_RipplesPosition`, `g_RipplesSpeed`, `g_RipplesWidth` | ondas concéntricas animadas desde un punto (impacto en agua) |
| Sacudida de pantalla (Screen Shake) | `"_filter_screenshake"` | Filter | `g_Magnitude`, `g_ShakeSpeed`, `g_NoiseTexture` | sacudida de pantalla por shader; alternativa a mover la cámara a mano |
| Fondo de rayas (Stripes Background) | `"_filter_stripes"` | Filter | `g_StripesWidth`, `g_StripesDirection`, `g_StripesOffset` | fondo de rayas animadas, decorativo |
| Distorsión de remolino (Twirl Distort) | `"_filter_twirl_distort"` | Filter | `g_DistortAngle`, `g_DistortRadius`, `g_DistortOffset` | remolino de distorsión centrado en cámara + offset (portal, succión) |
| Desenfoque de torsión (Twist Blur) | `"_filter_twist_blur"` | Filter | `g_TwistBlurCenter`, `g_TwistBlurIntensity`, `g_TwistBlurTexture` | desenfoque de torsión alrededor de un punto |
| Bajo el agua (Underwater) | `"_filter_underwater"` | Filter | `g_Distort1Speed`, `g_Distort2Speed`, `g_Distort1Scale` | look bajo el agua: doble distorsión + tinte + destello |
| Viñeta (Vignette) | `"_filter_vignette"` | Filter | `g_VignetteEdges`, `g_VignetteSharpness`, `g_VignetteTexture` | viñeteado de bordes, con textura propia opcional |
| Ruido blanco (White Noise) | `"_filter_whitenoise"` | Filter | `g_WhiteNoiseIntensity`, `g_WhiteNoiseAnimation`, `g_WhiteNoiseTexture` | ruido blanco animado (estática, glitch, daño de pantalla) |
| Desenfoque de zoom (Zoom Blur) | `"_filter_zoom_blur"` | Filter | `g_ZoomBlurCenter`, `g_ZoomBlurIntensity`, `g_ZoomBlurFocusRadius` | desenfoque de zoom radial desde un punto (impacto, velocidad) |
| Mezcla (Blend) | `"_effect_blend"` | Effect | `g_Blend` | aplica un blend mode a una capa entera sin tocar cada sprite; vía barata de "aditivo de capa" |
| Mezcla extendida (Blend Ext) | `"_effect_blend_ext"` | Effect | `g_BlendExt_Src`, `g_BlendExt_Dest`, `g_BlendExt_AlphaSrc` | blend mode extendido (factores de origen/destino por separado) a una capa entera |
| Desenfoque gaussiano (Gaussian Blur) | `"_effect_gaussian_blur"` | Effect | `g_numDownsamples`, `g_numPasses`, `g_intensity` | desenfoque gaussiano barato (downsample + pasadas); preferible a `_filter_large_blur` |
| Resplandor (Glow) | `"_effect_glow"` | Effect | `g_GlowRadius`, `g_GlowQuality`, `g_GlowIntensity` | resplandor/bloom sencillo de un paso sobre el contenido de la capa |
| Desenfoque recursivo (Recursive Blur) | `"_effect_recursive_blur"` | Effect | `g_RecursiveBlurRadius`, `g_RecursiveBlurQuality`, `g_RecursiveBlurGamma` | desenfoque recursivo, más barato que un blur normal |
| Partículas arrastradas por el viento (Windblown Particles) | `"_effect_windblown_particles"` | Effect | `param_sprite`, `param_num_particles`, `param_particle_spawn_time` | sistema de partículas de hojas/viento listo para usar, con estelas y "sopladores" |

> Los identificadores son cadenas literales que se pasan a `fx_create()` tal cual: no se
> traducen, no llevan mayúscula inicial y no admiten espacios. Los parámetros de runtime se
> leen/escriben con [`fx_get_parameter`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Filter_Effect_Layers/fx_get_parameter.md)
> y `fx_set_parameter` sobre el struct que devuelve `fx_create()`.

#### `fx_set_single_layer()` y `layer_enable_fx()`: cuándo usar cada uno

Son dos funciones distintas para dos preguntas distintas:

- **`fx_set_single_layer(filter_or_effect, enable)`** decide **a cuántas capas afecta** un FX
  struct. Por defecto (`enable = false`) un FX aplicado a una capa con `layer_set_fx()` se
  aplica también a **todas las capas por debajo**. Con `enable = true` se aplica **solo** a la
  capa a la que está asignado.
  - Úsalo cuando el efecto solo tiene sentido sobre una capa concreta: el propio manual pone
    `_filter_outline` como ejemplo (un contorno alrededor de todo lo que hay por debajo casi
    nunca es lo que quieres) y lo mismo aplica a `_filter_screenshake` sobre una capa aislada de
    "cosas que tiemblan".
  - ⚠️ No actives el modo de capa única en un FX aplicado a una **capa FX vacía**: una capa FX
    no dibuja nada por sí misma, así que en modo de capa única no habría contenido al que
    aplicar el filtro y no se vería nada.

  ```gml
  // Create Event
  var _fx_contorno = fx_create("_filter_outline");
  fx_set_parameter(_fx_contorno, "g_OutlineColour", [0, 0, 0, 1]);
  fx_set_single_layer(_fx_contorno, true);      // solo esta capa, no las de abajo
  layer_set_fx("Personajes", _fx_contorno);
  ```

- **`layer_enable_fx(layer_name_or_id, enable)`** solo **muestra u oculta** el FX ya asignado a
  una capa; no lo añade ni lo quita (eso es `layer_set_fx()` / `layer_clear_fx()`). Es la forma
  barata de encender/apagar un efecto por código sin recrear el FX struct cada vez.
  - Úsalo para condicionar un FX a un estado de juego: la propia página del manual pone el
    ejemplo de desaturar la pantalla cuando la vida es baja.

  ```gml
  // Step Event
  layer_enable_fx("CapaDesaturar", hp <= 3);
  ```

  Comprueba el estado actual con [`layer_fx_is_enabled(layer_name_or_id)`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Filter_Effect_Layers/layer_fx_is_enabled.md)
  y el del modo de capa única con [`fx_get_single_layer(filter_or_effect)`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Filter_Effect_Layers/fx_get_single_layer.md).

---

## 5. Formatos de superficie

### 5.1 Novedad

`surface_create()` acepta un **tercer argumento opcional** con el formato de datos de la superficie.

```gml
surface_create(w, h, [format]);
// w, h:    Real
// format:  Surface Format Constant (opcional, por defecto surface_rgba8unorm)
// devuelve: Surface (o handle inválido -1 si algo falla)
```

### 5.2 Tabla de formatos

| Constante | Canales | Bits por canal | Notas |
|---|---|---|---|
| `surface_rgba8unorm` | RGBA | 8 | **Por defecto.** Rango 0-255 por canal. "unorm" = normalizado a 0-1 al leerlo en un shader |
| `surface_r8unorm` | R | 8 | **Un cuarto del espacio** de RGBA. En shader, los demás canales valen 0 |
| `surface_rg8unorm` | RG | 8 | Dos canales |
| `surface_rgba4unorm` | RGBA | 4 | Rango 0-15 por canal |
| `surface_rgba16float` | RGBA | 16 (float) | Mayor precisión. **Caso de uso: HDR**, permite valores fuera de 0-255 |
| `surface_r16float` | R | 16 (float) | Un cuarto del espacio respecto al anterior |
| `surface_rgba32float` | RGBA | 32 (float) | La máxima precisión; **más lento de renderizar y menos soportado** |
| `surface_r32float` | R | 32 (float) | Un solo canal |

### 5.3 Cuándo usar cada uno

| Necesitas | Usa |
|---|---|
| Surface normal | `surface_rgba8unorm` (por defecto) |
| **HDR** o rangos de color amplios | `surface_rgba16float` |
| Una **máscara** de un solo canal | `surface_r8unorm` (ahorras un 75 % de memoria) |
| Datos genéricos de 2 canales (p. ej. normales 2D) | `surface_rg8unorm` |
| Máxima precisión y te sobra GPU | `surface_rgba32float` |

```gml
// Create Event

// Superficie normal
surf_normal = surface_create(1024, 1024);

// Superficie HDR: permite valores de color más allá de 0-255
surf_hdr = surface_create(1024, 1024, surface_rgba16float);

// Máscara de un solo canal: un cuarto de memoria
surf_mascara = surface_create(512, 512, surface_r8unorm);

// Limpiar siempre: una superficie recién creada puede contener "ruido"
surface_set_target(surf_normal);
draw_clear_alpha(c_black, 0);
surface_reset_target();
```

> Recordatorio: se recomienda que las superficies tengan **tamaños potencia de 2** (16, 128, 512, 1024). No es obligatorio en Windows/macOS pero mejora la compatibilidad; en HTML5 y móvil **es esencial**.

### 5.4 `surface_create_ext()` y profundidad

Existe también `surface_create_ext()`. Y recuerda: si el buffer de profundidad automático está activado (lo está por defecto), se crean también depth buffer y stencil buffer; se desactiva con `surface_depth_disable()`.

---

## 6. Grupos de texturas dinámicos: `texturegroup_add()`

### 6.1 Qué hace

Crea un **Dynamic Texture Group** nuevo en el juego a partir de **ficheros de imagen y/o buffers**, usando información de sprites que le pasas como struct. Es la forma de cargar texturas (y por tanto sprites) **en runtime**.

```gml
texturegroup_add(groupname, filename_or_buffer_or_array, struct_or_json);
// groupname:                    String  (nombre del Texture Group)
// filename_or_buffer_or_array:  String | Buffer | Array con mezcla de ambos
// struct_or_json:               Struct | String con JSON
// devuelve:                     N/A
```

### 6.2 Reglas

- Si ya existe un Texture Group con ese nombre → **error fatal**.
- Formatos de imagen aceptados: cualquier formato bitmap, y en buffer además **PNG, JPEG, GIF, QOIF, DDS, ASTC**, etc.
- Cualquier textura comprimida por hardware debe estar soportada en el target.
- ⚠️ **No está soportado en HTML5.**
- ⚠️ La textura se **descarga** justo después de crearse: cárgala con `texturegroup_load()` o se cargará sola al dibujar por primera vez un sprite del grupo.
- ⚠️ **Los buffers usados por un texture group no pueden borrarse mientras el grupo exista.** Borra primero el grupo, luego el buffer.

### 6.3 Struct de datos de sprites

Debe tener esta forma:

```
sprites:
  <nombre_sprite>:
    width, height                    (obligatorios)
    frames: [ { x, y (obligatorios),
                w, h,
                x_offset, y_offset,
                crop_width, crop_height,
                original_width, original_height,
                tp } ]
    xoffset, yoffset                 (opcionales)
    bbox_left/right/top/bottom       (opcionales)
    bbox_kind                        (opcional)
    frame_speed, frame_type          (opcionales)
    rotated_bounds                   (opcional)
    mask / masks                     (opcional)
    nineslice                        (opcional)
    messages                         (opcional)
    frame_info                       (opcional)
```

`tp` es el **índice del fichero de imagen** dentro del array que pasaste a la función, para cuando usas varias texturas.

### 6.4 Ejemplo básico

```gml
// Create Event
var _sprite_data = {
    sprites :
    {
        chico_azul :
        {
            width  : 116,
            height : 128,
            frames :
            [
                { x : 116*0, y : 128*0 },
                { x : 116*1, y : 128*0 },
                { x : 116*2, y : 128*0 },
                { x : 116*3, y : 128*0 },
                { x : 116*4, y : 128*0 },
                { x : 116*5, y : 128*0 },
            ],
        },
        chico_rojo :
        {
            width  : 116,
            height : 128,
            frame_speed : 8,
            frames :
            [
                { x : 116*0, y : 128*1 },
                { x : 116*1, y : 128*1 },
                { x : 116*2, y : 128*1 },
                { x : 116*3, y : 128*1 },
                { x : 116*4, y : 128*1 },
                { x : 116*5, y : 128*1 },
            ],
        }
    }
};

texturegroup_add("MiGrupoTexturas", "image.png", _sprite_data);

var _sprites = texturegroup_get_sprites("MiGrupoTexturas");
// _sprites es un array con los sprites del grupo, listos para usar
```

### 6.5 Varias texturas desde distintas fuentes

```gml
// Create Event
buffer = buffer_load("image2.png");

var _sprite_data = {
    sprites :
    {
        chico_azul :
        {
            width : 116, height : 128,
            frames : [ { x : 116*0, y : 128*0 } ],
        },
        chico_rojo :
        {
            width : 116, height : 128,
            frames : [ { x : 116*0, y : 128*0, tp : 1 } ],   // segunda textura
        }
    }
};

texturegroup_add("MiOtroGrupo", ["image.png", buffer], _sprite_data);

// Clean Up Event
texturegroup_delete("MiOtroGrupo");   // PRIMERO el grupo...
buffer_delete(buffer);                // ...luego el buffer
```

### 6.6 Truco útil del manual

El botón **"Preview"** de Graphics Game Options abre una carpeta con una vista previa de las Texture Pages, y ahí hay un fichero **`asset_layout_info.json`**. Puedes:

1. montar las Texture Pages en la IDE,
2. sacar ese JSON,
3. pasárselo como **string** a `texturegroup_add()`.

Así te ahorras calcular a mano las coordenadas, anchos, etc.

### 6.7 Funciones relacionadas

- `texturegroup_delete()` — borra el grupo; si había sobrescrito sprites, los restaura
- `texturegroup_load()` — carga la textura
- `texturegroup_get_sprites()` — array de sprites del grupo

> **Fix reciente:** `texturegroup_add()` no funcionaba como estaba documentado. Corregido en Beta **2026.100 Release 4**: ya afecta tanto a referencias de asset como dinámicas y hace fallback correcto cuando la textura se descarga.

---

## 7. Compresión de texturas GPU

Se ha añadido soporte de **compresión de texturas GPU**, pero **no va en el core**: se distribuye como **extensión aparte**.

- Repositorio: https://github.com/YoYoGames/GM-GPUTextureCompression
- Manual: `Settings > Texture Information > Texture Compression`

Esto permite usar formatos comprimidos por hardware (ASTC, DDS…) que reducen muchísimo el consumo de VRAM, a costa de tamaño de fichero distinto y soporte por plataforma.

---

## 8. `sphere_is_visible()` — frustum culling

Función nueva para saber si una esfera está dentro del **frustum** de la cámara actual. Fundamental para optimizar escenas 3D.

```gml
sphere_is_visible(x, y, z, radius);
// x, y, z:  Real  (posición de la esfera)
// radius:   Real
// devuelve: Boolean
```

### Cómo se define el frustum

Lo determinan las **matrices de vista y proyección activas** —normalmente las de la cámara activa—. Si llamas a la función **después de `camera_apply()`**, usa las matrices de esa cámara.

- Con proyección **ortográfica**: el frustum es una caja.
- Con proyección **en perspectiva**: es una pirámide truncada.

### Ejemplo: no dibujar modelos 3D que no se ven

```gml
// Draw Event
var _visible = sphere_is_visible(x, y, z, radius);

if (!_visible)
{
    exit;   // fuera de cámara: no lo mandes a la GPU
}

vertex_submit(mi_modelo_complejo, pr_trianglelist, textura);
```

La esfera debe ser la **esfera envolvente** (*bounding sphere*) de tu modelo.

> Nota: he verificado la existencia, firma y comportamiento de `sphere_is_visible()` en el manual LTS, pero **no** he podido confirmar en qué versión concreta se introdujo (el issue de petición es de marzo de 2025). Está presente en LTS 2026.0.

---

## 9. Otros cambios gráficos de 2026.0

- **"Interpolate colours between pixels"** activado por defecto en Windows (antes no, y no coincidía con el manual ni con otros targets).
- **Vsync** activado por defecto en todos los targets.
- Corrección automática de valores inválidos en capas de filtro/efecto al abrir una room: el Room Editor **detecta y repara** los valores mal puestos que provocaban el error `Unknown Function argument 1 invalid reference to (sprite) - requested -1 max is`.
  - ⚠️ Tienes que **abrir la room y hacer clic en la capa de filtro/efecto** activa para que GameMaker diagnostique y repare el problema.
- Game Options ahora **exporta los valores de texture page como .json** al pulsar "Preview", para que los edites a mano y los uses en el juego.
- Se elimina la opción redundante **"Generate Mipmaps For Separate Texture Pages"** (se gestiona desde el editor de Texture Groups).

---

## Fuentes

- Manual: Sprite Manipulation (caché de sprites vectoriales) — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/Sprite_Manipulation.htm
- Manual: `font_enable_sdf()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_enable_sdf.htm
- Manual: `font_enable_effects()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_enable_effects.htm
- Manual: `surface_create()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_create.htm
- Manual: `texturegroup_add()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_add.htm
- Manual: `sphere_is_visible()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Viewports/sphere_is_visible.htm
- Manual: FX Types & Parameters — https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/FX/All_Filter_Effect_Types.htm
- Extensión de compresión GPU — https://github.com/YoYoGames/GM-GPUTextureCompression
- Blog LTS 2026.0 — https://gamemaker.io/en/blog/lts-2026-release
- Release notes 2026.0.0 — https://releases.gamemaker.io/release-notes/2026/0
- Release notes Beta 2026.100 — https://releases.gamemaker.io/release-notes/2026/100
