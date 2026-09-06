# Auditoría de cobertura · Dominio **VFX y gráficos de juego**

> Biblioteca auditada: `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`
> Versión de referencia: GameMaker LTS 2026.0 (IDE `2026.0.0.16`, runtime `2026.0.0.23`)
> Fecha: 2026-09-06 · Ignorados `Lumbre/` y `GameMaker_Fuentes/` según el brief.
> Se cuentan como existentes la carpeta 13 y las recetas 28-31 de la 04.

---

## 0 · Resumen ejecutivo

La biblioteca es **muy fuerte en la API gráfica** (superficies, blending, GPU state, shaders,
partículas) y **muy fuerte en la herramienta** (editor de partículas, FX de capa de 2026,
Sequences). También cubre bien el **game feel** (shake, hit stop, flash de pantalla, texto
flotante, squash).

Donde se queda corta es en las **tres capas intermedias** que separan «sé qué función existe» de
«sé hacer una explosión que se vea bien»:

1. **El oficio del VFX.** No hay ningún documento que enseñe la *anatomía* de un efecto
   (destello → núcleo → escombros → humo → onda), las rampas de color, el timing, la silueta o
   la lectura a distancia. Hay funciones y hay presets con nombre, pero no hay criterio.
2. **El recetario de shaders de efecto.** `08 · 06` trae seis shaders completos y excelentes
   (desaturar, outline, dissolve, luz puntual, onda, viñeta) + palette swap. Faltan los diez
   más pedidos en un juego 2D: hit flash, aberración cromática, CRT/scanlines, glitch,
   pixelado, shockwave, heat haze, blur gaussiano de dos pasadas, bloom (cadena completa) y
   grading por LUT.
3. **Iluminación 2D más allá de la surface oscura.** `04 · 24` monta el sistema básico y él
   mismo remite a «cuando esto se quede corto». Ese «después» no existe: ni normal maps, ni
   sombras proyectadas, ni god rays, ni ciclo día/noche con rampa de color.

Además hay **dos hallazgos concretos y accionables** que no son huecos de tema sino defectos:

- 🔴 **`hit_flash` está declarado y decrementado en tres recetas (`04 · 02`, `04 · 03`,
  `04 · 15`) y no se dibuja en ninguna parte.** `04 · 15 §5.7` lo fija (`_v.hit_flash = 8;`)
  con el comentario «(shader o image_blend)», y `§8.2` lo remite a «posibles mejoras». Un LLM
  que siga la receta produce un juego donde nada parpadea al recibir daño. Es el efecto más
  universal del género y está a medio camino.
- 🔴 **El espejo español del manual traduce los identificadores internos de los FX, y además
  la página está incompleta.** En
  `09 - Manual oficial/manual-lts-2026-es/The_Asset_Editors/Room_Properties/FX/All_Filter_Effect_Types.md`:
  - La versión inglesa tiene **42 filas** (36 filtros + 6 efectos); la española, **28**. Faltan
    14 tipos enteros, entre ellos `_filter_clouds`, `_filter_mask`, `_filter_old_film`,
    `_filter_hue`, `_filter_ripples`, `_effect_glow`, `_effect_gaussian_blur`,
    `_effect_recursive_blur`, `_effect_blend` y `_effect_blend_ext`.
  - De las 28 filas que sí están, **25 llevan el identificador traducido**: `"_cajas_de_filtro"`
    por `"_filter_boxes"`, `"filtro_tintal"` por `"_filter_tintfilter"`, `"_filtro_contorno"`
    por `"_filter_outline"`, `"_filtro_viñeta"` por `"_filter_vignette"`,
    `"Efecto_partículas_de_viento"` por `"_effect_windblown_particles"`… Solo sobreviven
    intactos `_filter_pixelate`, `_filter_whitenoise` y `_filter_zoom_blur`.

  Son **cadenas literales que se pasan a `fx_create()`**: traducidas no crean nada. Esto choca
  frontalmente con la afirmación de `AGENTS.md` §6 («puedes citar el espejo español
  directamente»): para esta página concreta, no. Contrastado fila a fila con
  `manual-lts-2026-en/…/All_Filter_Effect_Types.md`.

- 🟡 **`02 - Novedades 2026/06` §4.1 clasifica mal `_filter_hard_drop_shadow`**: lo lista bajo
  «la sección de **Effects**», y en el manual es un **Filter** (la tabla de Effects tiene
  exactamente seis entradas: `_effect_blend`, `_effect_blend_ext`, `_effect_gaussian_blur`,
  `_effect_glow`, `_effect_recursive_blur`, `_effect_windblown_particles`). La distinción
  importa porque los Effects no se previsualizan en el editor de rooms.

Y un hueco de API medible: de las **34 funciones `part_type_*`** del runtime, solo **13**
aparecen en algún documento de prosa. Faltan justo las que hacen que un efecto deje de parecer
genérico: `part_type_sprite` (usar tu propio sprite), `part_type_blend` (aditivo),
`part_type_step` / `part_type_death` (partículas que engendran partículas — la base de una
explosión en capas o de un fuego artificial) y toda la familia de rampas de color
(`part_type_colour_mix`, `_colour_hsv`, `_colour_rgb`). De las **19 `part_system_*`**, solo
**7**: falta `part_system_automatic_update` / `part_system_update`, que es exactamente lo que
hace falta para que las partículas **respeten el hit stop** que sí documenta `04 · 15 §5.0`.

---

## 1 · Tabla completa

Estados: **CUBIERTO** (documento y sección exactos, con código verificado) ·
**PARCIAL** (existe pero incompleto) · **FALTA**.

### A · Partículas: sistema, API y diseño de efectos

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| A1 | Particle System asset y editor del IDE (emitters, regiones, presets, *Copy GML to Clipboard*) | CUBIERTO | `02 - Novedades 2026/05 - Sistema de partículas nuevo.md` §2 «El Particle System Editor», §2.1–2.4 | — | Manual, *The Particle System Editor* |
| A2 | `particle_add()` / `particle_get_info()` / variantes en runtime | CUBIERTO | `02 - Novedades 2026/05` §4 y §5 (4 ejemplos completos) | — | Manual, `particle_add` |
| A3 | Sistema clásico `part_system_* / part_emitter_* / part_type_*` | PARCIAL | `04 - Recetas por género/15 - Game feel y juice.md` §5.5 «Partículas nativas» · `02 - Novedades 2026/05` §6 | 13 de 34 `part_type_*` y 7 de 19 `part_system_*` en prosa. Ausentes: `part_type_sprite`, `part_type_blend`, `part_type_subimage`, `part_type_step`, `part_type_death`, `part_type_colour_mix/_hsv/_rgb`, `part_system_automatic_update`, `part_system_update`, `part_system_global_space`, `part_particles_count`, `part_particles_clear` | Manual, *Particles* (índice) |
| A4 | Partículas colocadas en el editor de rooms (`layer_particle_*`) | CUBIERTO | `02 - Novedades 2026/05` §«7 bis. Partículas colocadas en el editor de rooms» | — | Manual, *Particle System Layers* |
| A5 | *Built-in effects* (`effect_create_layer`, `ef_smoke`…) | CUBIERTO | `02 - Novedades 2026/05` §7 «Cuándo usar cada uno» (tabla + ejemplo) | — | Manual, *Effects* |
| A6 | **Explosión**: anatomía en capas (destello → núcleo → escombros → humo → onda) | PARCIAL | `04 - Recetas por género/15` §5.5 (`fx_explosion` = chispas + humo + shake + hit stop) | Solo dos emisiones simultáneas. Sin destello aditivo, sin escombros con gravedad, sin onda expansiva, sin escalonado temporal, sin rampa de color fuego→humo | GDC *Juice it or lose it* (Petri Purho / Martin Jonasson); realtimevfx.com, «anatomy of an explosion» |
| A7 | Humo | CUBIERTO | `04 - Recetas por género/15` §5.5 (`pt_smoke`) + preset `Smoke` en `02 · 05 §2.2` | — | Manual, presets del editor |
| A8 | Fuego / llamas | PARCIAL | `02 - Novedades 2026/05` §2.2 nombra los presets `Fire`, `Embers`, `Embers 2`, `Flame Intensity` | Solo el nombre del preset. Ni parámetros, ni versión por código, ni `part_type_blend` aditivo (que es lo que hace que el fuego parezca fuego) | Xor / *GM Shaders*, `XorDev/Fire-Fun` (catalogado en `11/_CATALOGO.md §Shaders`) |
| A9 | Chispas de impacto | CUBIERTO | `04 - Recetas por género/15` §5.5 (`pt_spark`) + `fx_impact()` con abanico direccional | — | — |
| A10 | Polvo (pasos, aterrizaje) | CUBIERTO | `04 - Recetas por género/15` §5.5 (`pt_dust`, `fx_dust_land()`) | — | — |
| A11 | Sangre / gore | CUBIERTO | `04 - Recetas por género/15` §5.5 (`pt_blood`) | — | — |
| A12 | Magia, aura, carga de ataque | FALTA | — | Efecto orbital/convergente, rampa HSV, pulso, aditivo | realtimevfx.com («magic circle», «charge-up»); Slynyrd, *Pixelblog* de efectos |
| A13 | Lluvia (sistema de clima) | PARCIAL | `02 - Novedades 2026/05` §2.2 nombra el preset `Rain` | Sin sistema: sin salpicaduras al tocar suelo, sin viento, sin capa de intensidad, sin desactivar bajo techo | Manual, `_effect_windblown_particles`; realtimevfx.com «weather systems» |
| A14 | Nieve | FALTA | — | No hay preset `Snow` ni receta. La vía viable es `_effect_windblown_particles` (documentado en `02 · 06 §4.1` solo como nombre) | Manual, *All Filter/Effect Types* |
| A15 | Niebla ambiental 2D | PARCIAL | `02 - Novedades 2026/05` §7 bis la cita como caso de uso de `layer_particle_*` · `08 · 04` documenta `gpu_set_fog()` (que es 3D) | Sin receta: capas de niebla con parallax, `bm_add` suave, ruido animado | Manual, `_filter_clouds` / `_filter_fractal_noise` |
| A16 | Presupuesto de rendimiento de partículas | PARCIAL | `02 - Novedades 2026/05` §8 «Limitaciones y avisos» (cualitativo: «no tengas 40.000», over-draw en móvil) · `01 - Fundamentos/15 - Depuración y rendimiento.md` §Draw (texture swaps, vertex batches) | Sin `part_particles_count()` para medir, sin culling de emisores fuera de cámara, sin pooling de sistemas, sin cifras objetivo por plataforma | Manual, `part_particles_count`; realtimevfx.com «VFX budgets» |

### B · Trails y estelas

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| B1 | *Afterimage* / sprites fantasma de dash | CUBIERTO | `04 - Recetas por género/06 - Metroidvania.md` §5.4 «Habilidades en el jugador» (`objAfterimage`, Create/Step completos) | — | — |
| B2 | Trail de espada con `draw_primitive(pr_trianglestrip)` | FALTA | La primitiva se documenta en `08 - Referencia GML completa/02 - Dibujo de formas y primitivas.md` y `01 · 11`, pero nadie la usa para una estela | Historial de posiciones, ancho decreciente, UV a lo largo del arco, textura con degradado | GDC *Juice it or lose it*; realtimevfx.com «ribbon trails» |
| B3 | Trail de proyectil / dash con cola de partículas o vertex buffer | FALTA | — | Emisor que sigue a la instancia, `part_system_global_space` para que la cola se quede atrás | Manual, `part_system_global_space` |
| B4 | *Motion blur* | PARCIAL | `13 - Diseño y producción de videojuegos/04 - Animación de sprites, Sequences y Animation Curves.md` §1.4 lo trata como *smear* dibujado a mano | Sin la vía técnica: FX `_filter_linear_blur` / `_filter_zoom_blur`, o acumulación en surface | Manual, *All Filter/Effect Types* |

### C · Shaders de efecto

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| C1 | Anatomía de un shader de GameMaker (vsh/fsh, uniforms integrados, matrices, plataformas, trampas) | CUBIERTO | `08 - Referencia GML completa/06 - Shaders.md` §«Anatomía», §«Constantes integradas», §«Buenas prácticas y trampas» (10 reglas) | — | Manual, *Shaders* |
| C2 | Contorno (outline) | CUBIERTO | `08 · 06` §6.2 «Contorno (outline)» (vsh + fsh completos) · también FX `_filter_outline` en `02 · 06 §4` · librería `gml-outline-shader-drawer` en `11/_CATALOGO.md §Shaders` | — | — |
| C3 | Desaturación / escala de grises | CUBIERTO | `08 · 06` §6.1 «Desaturación progresiva» | — | — |
| C4 | *Dissolve* / disolución | CUBIERTO | `08 · 06` §6.3 «Disolución (dissolve)» | — | — |
| C5 | *Palette swap* | CUBIERTO | `08 · 06` §«Palette swap (intercambio de paleta)» (método simple + nota de textura de paleta + librería Chameleon) | — | — |
| C6 | Viñeta | CUBIERTO | `08 · 06` §6.6 «Extra: viñeta con corner ID» · `01 - Fundamentos/11` §13 «Ejemplo completo: HUD + efectos con surface y shader» | — | — |
| C7 | Distorsión de onda / agua | CUBIERTO | `08 · 06` §6.5 «Onda (wave) de distorsión» · `13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md` §11.3 «Agua por shader: distorsión con una textura de ruido» (incluye la trampa de la página de textura compartida) | — | — |
| C8 | Luz 2D puntual por shader | CUBIERTO | `08 · 06` §6.4 «Luz 2D puntual con atenuación» | — | — |
| C9 | **Hit flash** (flash blanco al recibir daño) | PARCIAL 🔴 | Variable declarada y decrementada en `04 · 02 §5.1/§5.2`, `04 · 03 §5.7`, `04 · 15 §5.7`; citado como mejora en `04 · 15 §8.2` | **No se dibuja en ningún sitio.** Faltan las tres vías: `image_blend` + `gpu_set_fog` (el truco clásico), shader de uniform `u_flash`, o `draw_sprite_ext` blanco encima | GDC *Juice it or lose it*; Xor / *GM Shaders* |
| C10 | Distorsión de calor (*heat haze*) | PARCIAL | La técnica equivalente (UV + ruido) está en `13 · 08 §11.3`; el FX `_filter_heathaze` está en el manual (`All_Filter_Effect_Types.md`) pero no en `02 · 06 §4` | Sin receta con ese nombre; sin la variante localizada (solo sobre la lava, no toda la pantalla) | Manual, `_filter_heathaze` |
| C11 | CRT / scanlines | PARCIAL | `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md` §8 «Viewports a surfaces» usa `shader_set(sh_crt)` **como nombre**, sin código | Todo el GLSL: curvatura, scanlines, máscara de subpíxel, sangrado, viñeta | *The Book of Shaders*; Xor / *GM Shaders* |
| C12 | Bloom / glow | PARCIAL | FX `_effect_glow` con sus 5 parámetros en `02 - Novedades 2026/06` §4.2 · `01 · 11` §8 menciona `surface_rgba16float` «para un pipeline de bloom» | La cadena real: *bright-pass* con umbral → downsample → blur → composite aditivo sobre HDR. Y cuándo NO usar bloom en pixel art | *The Book of Shaders*; `XorDev/1PassBlur` y `blur-shaders` (catalogados) |
| C13 | Aberración cromática | FALTA | Solo citada como característica del asset de pago *Post-Processing FX* (`04 · 15 §9`, `12 · 05`, `12 · 06`) | El shader: desplazamiento RGB radial escalado por la distancia al centro, ligado a la intensidad del daño | Xor / *GM Shaders*, hilo `GM Shaders` del foro (`07 · 07`) |
| C14 | Pixelado / posterizado por shader | PARCIAL | `08 · 05` cita `shader_set(sh_pixelado)` como ejemplo de `application_surface_draw_enable(false)`, sin GLSL · FX `_filter_pixelate` y `_filter_posterise` en el manual | El GLSL (2 líneas) y su uso como transición | Manual; *The Book of Shaders* |
| C15 | Glitch / datamosh | FALTA | Librería `bktGlitchFilter` catalogada en `11/_CATALOGO.md §Shaders y postprocesado`; FX `_filter_old_film` y `_filter_rgbnoise` en el manual | Receta propia: desplazamiento de bandas, separación RGB, ruido temporal, disparo por evento | `nkrapivin/bktGlitchFilter`; Manual `_filter_old_film` |
| C16 | Hologram / *rim light* / fresnel 2D | FALTA | — | Barrido de scanlines + tinte + parpadeo + borde brillante | realtimevfx.com; Xor / *GM Shaders* |
| C17 | *Shockwave* / distorsión radial | FALTA | «Onda expansiva» aparece una vez en `04 · 30` como concepto de diseño, sin implementación | Anillo de distorsión UV que se expande con el tiempo; el FX `_filter_twist_distort` es lo más cercano | GDC *Juice it or lose it*; Manual `_filter_twist_distort` |
| C18 | Blur gaussiano / desenfoque | PARCIAL | FX `_effect_gaussian_blur` y `_filter_large_blur` con parámetros en `02 · 06 §4.2` · librerías `1PassBlur`, `blur-shaders`, `Bokeh` en `11/_CATALOGO.md` | Sin shader propio de dos pasadas (H+V) ni criterio de coste | `XorDev/1PassBlur` |
| C19 | *Color grading* por LUT | FALTA | FX `_filter_lut_colour` en el manual; no aparece en ningún documento de la biblioteca | Cómo se construye una LUT, cómo se pasa como sampler, cómo se interpola entre dos | Manual, `_filter_lut_colour` |
| C20 | `#include` en shaders (Xpanda / Shady) | CUBIERTO (como catálogo) | `11 - Código descargado/_CATALOGO.md` §«Shaders y postprocesado» (`Xpanda`, `Shady.gml`, `Shadertoy2GM`) | Sin guía en español de ninguno, pero el brief no pide guías de librerías aquí | — |

### D · Post-procesado, FX de capa y superficies

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| D1 | Superficies: ciclo de vida, formatos, volatilidad, blending, `surface_*` completa | CUBIERTO | `08 - Referencia GML completa/05 - Superficies.md` (794 líneas, familia completa) · `01 · 11` §8 «Las seis reglas de las surfaces» | — | Manual, *Surfaces* |
| D2 | Post-procesado a pantalla completa con `application_surface` | CUBIERTO | `01 - Fundamentos/11` §13 «Ejemplo completo: HUD + efectos con surface y shader» (`application_surface_draw_enable(false)` + Post-Draw + HUD sin afectar) · `08 · 05` §«La Application Surface» (orden de eventos, `application_get_position`) | — | Manual, `application_surface` |
| D3 | Cadena de post-procesado **multipasada** (ping-pong entre surfaces) | FALTA | — | Dos surfaces alternándose, orden de efectos, coste por pasada, resolución reducida para el blur | *The Book of Shaders*; `FoxyOfJungle/RenderStack` (catalogado) |
| D4 | Filters & Effects de capa: API (`fx_create`, `fx_set_parameter`, `layer_set_fx`) | CUBIERTO | `02 - Novedades 2026/06 - Gráficos - SVG, SDF, FX y superficies.md` §4.3 «Ejemplo: crear y modificar un FX en runtime» | — | Manual, *Filter and Effect Layers* |
| D5 | **Catálogo completo de FX** (42 filtros y efectos con identificadores y parámetros) | PARCIAL 🔴 | `02 · 06` §4.1–4.2 cubre **solo los 11 nuevos de 2026**. El catálogo completo, y correcto, está en `manual-lts-2026-en/The_Asset_Editors/Room_Properties/FX/All_Filter_Effect_Types.md` (42 filas); el espejo español de esa página tiene 28 filas y 25 identificadores traducidos | Tabla propia con los 42 identificadores correctos + aviso del error del espejo. Sin documentar en la biblioteca: `_filter_clouds`, `_filter_lut_colour`, `_filter_mask`, `_filter_heathaze`, `_filter_underwater`, `_filter_screenshake`, `_filter_vignette`, `_filter_gradient`, `_filter_colour_balance`, `_filter_colourise`, `_filter_edgedetect`, `_filter_twirl_distort`, `_filter_twist_blur`, `_filter_zoom_blur`, `_filter_linear_blur`, `_filter_posterise`, `_filter_whitenoise`, `_filter_dots`, `_filter_stripes`, `_effect_blend`, `_effect_blend_ext`… | Manual (rama `-en`), *All Filter/Effect Types* |
| D5b | FX de mezcla de capa (`_effect_blend`, `_effect_blend_ext`) — aplicar un blend mode a una capa entera | FALTA | — | Es la vía «sin shader» para una capa aditiva de efectos (glow barato). No aparece en ningún documento | Manual (rama `-en`), tabla de *Effects* |
| D6 | FX de capa única vs global (`fx_set_single_layer`, `layer_enable_fx`) | FALTA en prosa | Las funciones existen en `08 - Referencia GML completa/_API del runtime/API-funciones.md` | Cuándo un FX debe aplicarse a una capa sola (el outline lo exige, según el propio manual) y cuándo a toda la escena | Manual, *Filters and Effects* |
| D7 | Redirigir un viewport a una surface propia (`view_surface_id`) | CUBIERTO | `01 - Fundamentos/10` §8 «Viewports a surfaces» | — | Manual, *Views And Viewports* |
| D8 | Formatos de surface HDR (`rgba16float`, `r8unorm`…) y cuándo usarlos | CUBIERTO | `02 · 06` §5 «Formatos de superficie» (tabla + criterio) · `08 · 05` §«Formatos de superficie» · `01 · 11` §8 | — | Manual, `surface_create` |
| D9 | Efectos de fuente (outline, glow, drop shadow) con `font_enable_effects()` | CUBIERTO | `02 · 06` §3 «Efectos de fuente» + §3.2–3.5 con ejemplos | — | Manual, `font_enable_effects` |
| D10 | Búfer de stencil para máscaras de efecto | PARCIAL | `08 - Referencia GML completa/04 - Color y blending.md` §«Búfer de stencil» (16 funciones documentadas una a una) | Referencia de API sin ninguna receta: recortar un efecto a la silueta de un sprite, máscara de agujero | Manual, *GPU Control* |

### E · Iluminación y sombras 2D

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| E1 | Sistema de luces con una surface (oscuridad + agujeros) | CUBIERTO | `04 - Recetas por género/24 - Iluminación 2D.md` §1 «El sistema de luces con una superficie» + §2 «Colocar y mover luces» + §«Las trampas» | — | — |
| E2 | Luces de color (`bm_add` sobre negro) frente a `bm_subtract` | CUBIERTO | `04 · 24` §1, nota destacada | — | — |
| E3 | Parpadeo de antorcha (`sin()` + ruido) | CUBIERTO | `04 · 24` §2 | — | — |
| E4 | *Normal maps* 2D | FALTA | Citado dos veces como destino («para cuando esto se quede corto», `04 · 24 §Ver también`) y en `07 · 04` / `07 · 16` como tema de tutoriales ajenos | Cómo se genera el mapa de normales, cómo se pasa como segundo sampler, la fórmula de N·L, el coste | `07 - Ecosistema/16 - Catálogo de la sección Tutorials del foro.md`; Xor / *GM Shaders* |
| E5 | Sombras proyectadas (*shadow casting* por oclusores) | FALTA en prosa | Librería `Bulb` (107 ★, MIT) catalogada en `11 - Código descargado/_CATALOGO.md` §«Iluminación y sombras» | La técnica: extruir los bordes del oclusor desde la luz con `draw_primitive(pr_trianglestrip)`, penumbra, coste por luz | `JujuAdams/Bulb` |
| E6 | *God rays* / rayos volumétricos | FALTA | — | Radial blur desde el punto de luz sobre una máscara de oclusión | *The Book of Shaders*; realtimevfx.com |
| E7 | Ciclo día/noche | PARCIAL | `04 - Recetas por género/09 - Survival y crafting.md` §4.7 y §5.5 «Ciclo día/noche» (rectángulo `c_navy` con alfa variable en Draw GUI) | Sin rampa de color (amanecer cálido → mediodía neutro → atardecer → noche azul), sin `merge_colour` entre paradas, sin integración con el sistema de luces de `04 · 24`, sin afectar al color de las luces | Slynyrd / *Pixelblog* (luz y hora del día) |
| E8 | Sprite de luz radial (el degradado que necesitan luces y partículas) | PARCIAL | `04 · 24` §1 lo describe en una nota: «un PNG de 256×256 con un círculo difuminado» | Cómo hacerlo bien en Aseprite (rampa de alfa, no de valor), o generarlo por código con `draw_circle_colour` en una surface | Slynyrd / Dan Fessler (pixel-art VFX) |

### F · Sprites de efecto, arte y herramientas

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| F1 | Objeto de efecto de una sola pasada (Animation End → `instance_destroy`) | CUBIERTO | `13 - Diseño y producción de videojuegos/04 - Animación de sprites, Sequences y Animation Curves.md` §3.3 «Detectar el final de la animación» (con el ejemplo literal `obj_explosion`) y §3.4 «Reproducir una vez y congelar» | — | Manual, *Animation End* |
| F2 | Sequences para VFX | CUBIERTO | `13 · 04` §6 «Sequences (asset)» (§6.1–6.7) · `02 · 05` §3.2 (pista `seqtracktype_particlesystem` y su limitación) | — | Manual, *Sequences* |
| F3 | Animation Curves para curvas de efecto | CUBIERTO | `13 · 04` §5 «Animation Curves (asset)» (§5.1–5.6, incluida la creación por código) | — | Manual, *Animation Curves* |
| F4 | Aseprite: flujo general (capas, tags, exportar hoja + JSON, importar en GameMaker) | CUBIERTO | `13 - Diseño y producción de videojuegos/03 - Pixel art y resolución.md` §5 «Flujo de trabajo con Aseprite» (§5.1–5.4, con la CLI real) | — | Documentación oficial de Aseprite |
| F5 | Aseprite **para VFX**: hojas de explosión, *smears*, rampas de alfa, arte para aditivo | FALTA | `13 · 03` §4.5 cubre *smears* de personaje, no de efecto | Número de fotogramas de una explosión, *ease out* del timing, sombra de color en vez de negro, por qué el arte para `bm_add` se pinta distinto | Slynyrd *Pixelblog*; Dan Fessler (pixel-art VFX) |
| F6 | Editor de partículas del IDE como herramienta de trabajo | CUBIERTO | `02 · 05` §2.4 «Canvas y Toolbox» (rejilla, zoom, *Copy GML*, docking) | — | Manual |

### G · Screen-space, feedback y game feel

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| G1 | *Screen shake* por trauma | CUBIERTO | `04 - Recetas por género/15` §4.1 «Screen shake» + §5.1 «Cámara con shake por trauma» (código completo, trauma², decaimiento) | — | GDC *Juice it or lose it*; *Math for Game Programmers: Juicing Your Cameras With Math* (Squirrel Eiserloh) |
| G2 | *Hit stop* / freeze frames / *time scale* | CUBIERTO | `04 · 15` §4.2 y §5.0 «Sistema de tiempo: hit stop y time scale» (Begin Step, orden explicado) | Detalle: las partículas no se congelan con el hit stop (haría falta `part_system_automatic_update(ps,false)` + `part_system_update(ps)`) | Manual, `part_system_automatic_update` |
| G3 | Flash de pantalla | CUBIERTO | `04 · 15` §5.6 «Flash de impacto y texto flotante» (`fx_flash`, Draw GUI, aviso de alfa baja) | — | — |
| G4 | Números de daño y texto flotante | CUBIERTO | `04 · 15` §5.6 (`fx_floating_text` + `objFloatingText` completo, con *pop* por tween y sombra) · usado en `04 · 07`, `04 · 09`, `04 · 11`, `04 · 30` | — | — |
| G5 | *Squash & stretch* y anticipación | CUBIERTO | `04 · 15` §4.3, §5.3 «Squash & stretch reusable», §5.8 «Anticipación en un ataque enemigo» | — | Los 12 principios de animación |
| G6 | *Zoom punch* / *camera kick* | FALTA | `04 · 15` §5.1 hace shake pero no zoom; `04 · 06` menciona «zoom de cámara» para otra cosa | Empuje de FOV con `camera_set_view_size` + retorno con easing, ligado al mismo trauma | GDC *Juicing Your Cameras With Math* |
| G7 | Transición de pantalla: fundido a negro | CUBIERTO | `01 - Fundamentos/10` §9 «Transiciones entre rooms» (`obj_transicion` persistente, máquina de estados) · `04 - Recetas por género/00 - Anatomía de un juego completo.md` §2 | — | — |
| G8 | Transiciones de iris, cortinilla, disolución por píxel | FALTA | `04 · 10` menciona «cortinillas» como idea de ampliación; asset de pago *Transitions Pro* citado en `12 · 06` | Máscara circular creciente, wipe direccional, dissolve con textura de ruido (reutiliza el shader de `08 · 06 §6.3`) | `foxyofjungle/foxey-transitions-pro` |
| G9 | Accesibilidad: reducir flashes, fotosensibilidad, shake desactivable | CUBIERTO | `04 · 15` §6 «Gestión del estado del jugador» (`flash_enabled`, guardado en ajustes) · `04 - Recetas por género/27 - Accesibilidad.md` | — | WCAG 2.3 / *Game Accessibility Guidelines* |
| G10 | Feedback en capas (visual + audio + háptico) al mismo golpe | CUBIERTO | `04 · 15` §4.7 «Feedback audiovisual en capas» + §5.7 «El "golpe completo"» (10 capas numeradas en una función) | — | GDC *Juice it or lose it* |

### H · Técnico transversal

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| H1 | *Blend modes*: `bm_add`, `bm_subtract`, `bm_multiply`, `_ext`, `_sepalpha`, ecuaciones | CUBIERTO | `08 - Referencia GML completa/04 - Color y blending.md` §«Cómo funciona el blending», §«Modos de mezcla», §«Factores de mezcla», §«Ecuaciones de mezcla» (familia completa, 65 funciones de GPU control) | — | Manual, *GPU Control* |
| H2 | Aditivo en partículas (`part_type_blend`) | FALTA en prosa | Solo en `08 - .../＿API del runtime/API-funciones.md` | Es el interruptor que separa «humo» de «fuego/magia»; debería estar en la receta de VFX | Manual, `part_type_blend` |
| H3 | Ordenación por profundidad y capas de efectos | CUBIERTO | `01 - Fundamentos/10` §capas (`layer_create`, orden) · `01 - Fundamentos/11` §resumen (batching por textura) · `02 · 05` §2.4 (*Draw Order* de partículas) · `04 · 02 §5.2` (`depth = -bbox_bottom`) | — | Manual, *Layers* |
| H4 | *Decals* y marcas persistentes (sangre en el suelo) | PARCIAL | `01 - Fundamentos/11` §8 «Surfaces» los cita como uso típico y §13 trae `obj_sangre_decal` completo (se pinta en `surf_mundo` y se autodestruye) | La surface es del tamaño de la room (`surface_create(room_width, room_height)`) sin aviso de VRAM; **sin estrategia de volatilidad** (al perder el foco desaparece toda la sangre); sin límite, sin desvanecimiento, sin agujeros de bala con rotación | Manual, *Surfaces And Alpha* |
| H5 | Destrucción y escombros (romper un sprite en trozos) | FALTA | «Escombros» aparece en `01 · 11` y `13 · 09` como palabra, no como técnica | Rejilla de `draw_sprite_part` con velocidad propia, o `sprite_create_from_surface` por trozos; combinado con partículas de polvo | realtimevfx.com; `13 · 08` (físicas a mano) da la base cinemática |
| H6 | Culling y coste de dibujo (`gpu_set_sprite_cull`, `sphere_is_visible`) | CUBIERTO | `02 · 06` §8 «`sphere_is_visible()` — frustum culling» · `08 · 04` §«Frustum culling de sprites» · `01 · 10` §7 | — | Manual |
| H7 | Librerías de terceros de VFX, partículas, shaders e iluminación | CUBIERTO | `11 - Código descargado/_CATALOGO.md` §«Partículas y efectos» (`Dynamo`, `Pulse`, `Burrn`), §«Shaders y postprocesado` (`Xpanda`, `Shady.gml`, `1PassBlur`, `Bokeh`, `bktGlitchFilter`, `Shadertoy2GM`, `gml-outline-shader-drawer`), §«Iluminación y sombras» (`Bulb`) · `12 · 05` y `12 · 06` (*Post-Processing FX*, *RenderStack*, *Transitions Pro*) · `07 · 07` (hilo *GM Shaders* de Xor) | — | — |

**Recuento:** 82 temas · **CUBIERTO 44** (43 + 1 «como catálogo») · **PARCIAL 18** ·
**FALTA 20** (17 + 3 «FALTA en prosa», que existen como entrada de API autogenerada pero sin
ningún documento que los explique).

Cobertura efectiva: **54 %** cubierto, **22 %** parcial, **24 %** ausente. El grueso de lo
cubierto está en la API (bloques C1-C8, D1-D2, D7-D10, H1, H3, H6) y en el game feel (G1-G5,
G7, G9-G10); el grueso de lo ausente está en el **oficio** (A6, A8, A12-A16, B2-B3, F5) y en los
**shaders de efecto** (C9, C11-C19).

---

## 2 · Propuestas priorizadas

### 🔴 ALTA

**1 · `04 - Recetas por género/32 - VFX - diseño y catálogo de efectos.md`** *(documento nuevo)*

El documento que falta: el oficio, no la API. Anatomía de un efecto en capas (destello aditivo
de 2 fotogramas → núcleo → escombros con gravedad → humo que sube y se dilata → onda expansiva),
timing escalonado, rampas de color y por qué el humo nace del color del fuego. Recetas completas
y verificadas para explosión, fuego, magia/carga, lluvia con salpicadura, nieve y niebla, cada
una en las dos vías (asset del editor y `part_type_*` por código). Cierra el hueco de API:
`part_type_sprite`, `part_type_blend`, `part_type_step`/`part_type_death`, las rampas
`part_type_colour_*`, `part_system_global_space` y el presupuesto medido con
`part_particles_count()` + culling de emisores. Incluye congelar partículas durante el hit stop
con `part_system_automatic_update` / `part_system_update`. Enlaza a `04 · 15` (juice),
`02 · 05` (editor) y `08 · 04` (blending).

**2 · `08 - Referencia GML completa/23 - Recetario de shaders de efecto.md`** *(documento nuevo, hermano de `08 · 06`)*

Los diez shaders que faltan, cada uno con vsh + fsh completos y el GML que los alimenta:
**hit flash** (y las tres alternativas sin shader), aberración cromática, CRT/scanlines,
glitch, pixelado/posterizado, shockwave radial, heat haze localizado, blur gaussiano de dos
pasadas, **bloom** (bright-pass → downsample → blur → composite aditivo sobre
`surface_rgba16float`) y grading por LUT. Y la pieza estructural que hoy no existe en ningún
sitio: la **cadena de post-procesado multipasada con ping-pong entre dos surfaces**, con orden
de efectos, coste por pasada y resolución reducida para los blurs. `08 · 06` se queda como la
referencia de la API y este documento como el recetario.

**3 · Sección nueva en `02 - Novedades 2026/06 - Gráficos…` §4.5 «Catálogo completo de FX»**

`02 · 06 §4` solo cubre los 11 FX nuevos de 2026; hay **42** (36 filtros + 6 efectos). Tabla
propia con los 42 tipos, sus **identificadores internos en inglés** (`_filter_boxes`,
`_filter_outline`, `_filter_lut_colour`, `_filter_heathaze`, `_filter_underwater`,
`_filter_screenshake`, `_filter_mask`, `_effect_blend`…), sus parámetros de runtime y una
columna de «para qué sirve de verdad». Con **el aviso en rojo** de que el espejo español de esa
página está incompleto (28 filas de 42) y traduce 25 de los identificadores, por lo que **no se
puede copiar de ahí**: hay que citar `manual-lts-2026-en/…/All_Filter_Effect_Types.md`. Corrige
de paso la clasificación de `_filter_hard_drop_shadow` (es filtro, no efecto) y añade
`fx_set_single_layer` / `layer_enable_fx` con el criterio de FX de capa única vs global.

> Nota de mantenimiento, fuera del alcance de esta auditoría: convendría comprobar si el mismo
> patrón de traducción de identificadores literales afecta a otras páginas del espejo español, y
> si procede matizar la afirmación de `AGENTS.md` §6 sobre citarlo sin comprobar.

**4 · Ampliar `04 - Recetas por género/24 - Iluminación 2D.md` con §3-§6 (o documento hermano `33 - Iluminación 2D avanzada.md`)**

El propio `04 · 24` remite a «cuando esto se quede corto» y ese destino no existe. Cuatro
secciones: **normal maps 2D** (generación, segundo sampler, N·L, coste), **sombras proyectadas**
(extrusión de aristas del oclusor con `pr_trianglestrip`, penumbra, presupuesto por luz, y
`Bulb` como alternativa lista), **god rays** (radial blur sobre máscara de oclusión) y **ciclo
día/noche con rampa de color** (`merge_colour` entre paradas horarias, tiñendo tanto el ambiente
como las luces), que además arregla el `04 · 09 §5.5` actual —un rectángulo `c_navy` plano— y
lo conecta con el sistema de luces.

### 🟡 MEDIA

**5 · Sección «Trails y estelas» dentro de la propuesta 1** *(o §5.9 de `04 · 15`)*

Trail de espada con `draw_primitive(pr_trianglestrip)`: historial de posiciones, ancho
decreciente, UV a lo largo del arco, textura con degradado. Trail de proyectil con emisor que
sigue a la instancia y `part_system_global_space` para que la cola se quede atrás. Motion blur
por FX (`_filter_linear_blur`, `_filter_zoom_blur`). Enlaza al `objAfterimage` que ya existe en
`04 · 06 §5.4` en vez de duplicarlo.

**6 · Cerrar el `hit_flash` huérfano** *(edición cruzada, no documento nuevo)*

Añadir el dibujado en `04 · 15 §5.6` (con las tres vías: `image_blend`+`gpu_set_fog`, shader de
uniform, sprite blanco encima) y una nota de una línea en `04 · 02 §5.1` y `04 · 03 §5.7`
apuntando ahí. Es el arreglo de mayor relación valor/esfuerzo de todo el informe: hoy tres
recetas declaran una variable que nadie usa.

**7 · Sección «Decals, destrucción y escombros» dentro de la propuesta 1**

Arregla y amplía el `obj_sangre_decal` de `01 · 11 §13`: aviso de VRAM por usar una surface del
tamaño de la room, **estrategia de volatilidad** (redibujar desde una lista de marcas al
recrear la surface, o aceptar la pérdida y decirlo), límite y desvanecimiento por antigüedad,
agujeros de bala con rotación. Y la destrucción: romper un sprite en una rejilla de
`draw_sprite_part` con velocidad e inercia propias, más polvo.

**8 · Ampliar `04 · 15` §5.9 y `01 · 10` §9 con screen-space y transiciones que faltan**

*Zoom punch* / *camera kick* (empuje de `camera_set_view_size` con retorno por easing, ligado al
mismo trauma del shake) en `04 · 15`. Transiciones de iris, cortinilla direccional y disolución
por píxel en `01 · 10 §9`, reutilizando el shader de dissolve que ya está en `08 · 06 §6.3`.

### 🟢 BAJA

**9 · Sección «Arte de efectos» en `13 - Diseño y producción de videojuegos/03 - Pixel art y resolución.md` §5.5**

Cuántos fotogramas lleva una explosión y por qué el timing va con *ease out*; *smears* de efecto
(distinto de los de personaje que ya cubre §4.5); rampas de alfa frente a rampas de valor; por
qué el arte destinado a `bm_add` se pinta con otras reglas; cómo hacer el sprite de luz radial
que piden `04 · 24` y las partículas. Enlaza a Slynyrd y Dan Fessler.

**10 · Máscaras de efecto con stencil: §nuevo en `08 - Referencia GML completa/04 - Color y blending.md`**

Las 16 funciones de stencil están documentadas una a una sin una sola receta. Dos ejemplos
bastan: recortar un efecto a la silueta de un sprite, y una máscara de agujero (linterna con
forma). Es el más prescindible de la lista, pero es el único bloque de API de `08 · 04` sin
ningún caso de uso.

---

## 3 · Limitaciones de esta auditoría

- **Sin acceso a la web.** El presupuesto de `WebSearch` de la sesión estaba agotado (200/200) y
  no pude verificar en vivo ninguna fuente externa. Todas las URLs que cito salen **de la propia
  biblioteca** (`07 · 07` para el hilo *GM Shaders* de Xor, `11/_CATALOGO.md` para los repos,
  `12 · 05`/`12 · 06` para los assets de FoxyOfJungle). Las fuentes que nombro sin URL —GDC
  *Juice it or lose it*, *Math for Game Programmers: Juicing Your Cameras With Math*, *The Book
  of Shaders*, realtimevfx.com, Slynyrd, Dan Fessler— **no las he podido comprobar en esta
  sesión**: las doy por su nombre canónico, no por un enlace verificado.
- **No compilé nada.** El brief pide auditar cobertura, no producir código, y no toqué ningún
  proyecto de GameMaker. Los juicios de «código completo y verificado» se basan en leer el
  código de los documentos, no en pasarlo por `gm-cli compile`. Los símbolos sí los verifiqué
  todos con `python3 _indice/buscar.py --listar` (familias `part_type_`, `part_emitter_`,
  `part_system_`, `part_particles`) y con fichas individuales (`part_particles_count`).
- **`11 - Código descargado/` solo se auditó por el catálogo**, no leyendo el GML de los 148
  repositorios. Es posible que alguna técnica que marco como FALTA aparezca implementada dentro
  de algún repo descargado; eso no cambia el veredicto, porque el brief pregunta por la
  documentación en español de la biblioteca, no por la existencia del código ajeno.
- **`03 - Cursos (YouTube)` y `10 - Cursos en español`** los incluí en los `grep` pero no abrí
  sus transcripciones: por el propio orden de autoridad de `AGENTS.md` §1 son la fuente más
  débil y no cambiarían un CUBIERTO.
- **El error de traducción de los identificadores de FX sí está comprobado a fondo** para esa
  página: extraje todos los identificadores entrecomillados de las dos versiones y los comparé
  (42 en inglés, 28 en español, 25 de ellos traducidos). **No revisé el resto de las ~3 000
  páginas del espejo español**: es plausible que el mismo patrón afecte a otras páginas con
  cadenas literales dentro de tablas, y merecería una comprobación sistemática que queda fuera
  de esta auditoría.
