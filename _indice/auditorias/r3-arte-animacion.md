# Auditoría r3 · Arte, animación y pipeline visual

> 2026-09-06 · 92 temas evaluados · **69 cubiertos** (75 %) · **14 parciales** (15 %) · **9 faltan** (10 %)
> Método: lectura íntegra de los documentos candidatos + `python3 _indice/buscar.py --texto/--todo`
> + `grep -rn` sobre toda la biblioteca (excluidos `Lumbre/` y `GameMaker_Fuentes/`) + verificación
> símbolo a símbolo con `buscar.py <función>`. Trabajo repartido en 5 sub-auditorías paralelas y
> cruzado por mí con comprobaciones directas adicionales.

## Resumen ejecutivo

El dominio de arte y animación está en un estado **mucho mejor de lo que sugeriría auditarlo desde
cero**, porque la ronda 2 ya cerró los huecos más caros: VFX (`04·39`), iluminación 2D avanzada
(`04·24`), el recetario de 10 shaders de efecto (`08·23`) y la disciplina completa de cámara
(`13·19`, con el marco de Itay Keren) fueron reescritos a partir de la auditoría `vfx.md` y
`colisiones-movimiento-camara.md` y hoy son de los documentos más sólidos de toda la biblioteca.
Pixel art, animación frame-by-frame, esqueletos Spine, Sequences, sprite técnico, atlas/texture
groups y 3D también están en un nivel de implementación real, con código verificado y trampas
documentadas. El hueco que más duele no es de código sino de **criterio de arte y de proceso**:
no hay ni una línea sobre **arte generado por IA** (upscalers, consistencia de estilo,
límites legales) — el único documento con "IA" en el título (`07·14`) habla exclusivamente de IA
como agente de programación, nunca como generadora de assets visuales — y falta la técnica más
elemental de estilo pixel art, el **contorno/outline selectivo**. Se encontró además un defecto
verificado (no solo un hueco): un ejemplo de código en `08·22` con un comentario que contradice
la firma real de la función y produciría animaciones que no loopean creyendo que sí.

## Tabla tema por tema

### Pixel art

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | Paletas indexadas / restricción de color deliberada | ✅ | `13·03` §2.1–2.6 (tamaños típicos, 12 paletas Lospec verificadas, criterio de selección) | El modo "Color Mode → Indexed" del editor se menciona una vez de pasada (§7.1), sin flujo |
| 2 | Dithering (ordenado, Bayer, patrones) | ✅ | `13·03` §3.4 (tabla cuándo sí/no, Bayer 2×2/4×4/8×8, aviso de incompatibilidad con filtrado bilineal) | — |
| 3 | Pixel clustering (evitar "confeti") | ✅ | `13·03` §3.2 (definición, síntomas, prueba de "entornar los ojos", cita de Cure) | — |
| 4 | Anti-aliasing manual selectivo | ✅ | `13·03` §3.3 (5 reglas, color de rampa) + §6.1 (filtrado bilineal, no confundir) | Las dos mitades no se cruzan explícitamente entre sí (mejora de redacción, no de contenido) |
| 5 | Sub-píxel: movimiento y redondeo de posición | ✅ | `13·03` §3.7, §4.6 (`pos_real_x` decimal + `floor()` al dibujar) | — |
| 6 | Legibilidad de silueta de personaje | ✅ | `13·03` §3.6 (prueba de relleno negro, silueta por pose) | — |
| 7 | Rampas de color y luz/sombra (pillow shading) | ✅ | `13·03` §2.2 (hue shifting, cifras de Slynyrd) + §3.5 (pillow shading completo) | — |
| 8 | Proporciones de personaje en píxeles (heads-tall/chibi) | 🟡 | `13·03` §1.3 (tamaño relativo a pantalla, 16–32 px) | No existe la convención de proporción anatómica interna ("cabezas de alto"/chibi vs. realista); 0 resultados de "cabezas de alto" o "chibi" |
| 9 | Outline / contorno selectivo en pixel art | 🔴 | Ninguna en prosa. Solo código sin documentar en `11 - Código descargado/librerias/shaders/gml-outline-shader-drawer` | Falta la técnica de dibujo (contorno negro puro vs. de color extraído de rampa, solo borde externo vs. líneas internas, coste en clusters) — distinta del shader de contorno en tiempo real que sí existe (`08·06 §6.2`) |

### Resolución y escalado

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 10 | Resolución interna (baja res + escalado) | ✅ | `13·03` §1 completo + §6.3 (`application_surface`) | — |
| 11 | Píxel perfecto: snapping de posición | ✅ | `13·03` §1.5, §4.6, §6.5 (código `floor()` en personaje y cámara) | — |
| 12 | Cámaras con escalado no entero / shimmering | ✅ | `13·03` §6.5 (código `lerp`+`floor()` solo al entregar) + remite a `03·41-44` (PixelatedPope) | — |
| 13 | Letterbox / pillarbox y aspect ratio | 🟡 | Existe repartido en `04·28 §4.2`, `13·05` (`display_set_gui_maximise`), `13·19:882` — pero **`13·03` no lo menciona ni una vez** | Sección propia en `13·03` que cruce con lo ya escrito en otros documentos |
| 14 | Escalado de UI independiente de la resolución interna | 🟡 | `13·03` §6.4 (GUI a múltiplo entero de la base) | No menciona `display_set_gui_maximise()` (la función que de verdad desacopla GUI de resolución real), que sí usan `01·11` y `13·05` sin cross-link desde aquí |
| 15 | Densidad de pantalla (DPI) | 🟡 | Cubierto en `04·28 §4.3` (`milimetros_a_gui()`, `display_get_dpi_x()`) y `13·05` | **`13·03` no menciona DPI**, y `04·28:324` **promete contenido en `13·03`** ("las tres salidas —escala fraccionaria, altura base que divida bien, resolución doble— están en 13·03") **que no existe ahí** — enlace de contenido roto, verificado con grep |
| 16 | Filtro de textura (nearest vs. lineal) | ✅ | `13·03` §6.1 (tabla de defaults por plataforma, `gpu_set_texfilter`, `gpu_set_texfilter_ext`) | — |
| 17 | `application_surface`, `display_set_gui_size`, `surface_resize` | ✅ | `13·03` §6.3–6.4, §1.6 | Correctamente no usa la familia `view_xview`/`view_yview` (⚠️ OBSOLETA, verificado) |
| 18 | Cámara+snapping combinados (jitter en scroll) | ✅ | `13·03` §6.5 (cámara) + §6.8 (paralaje con `floor()` en End Step) | — |

### Tilesets y autotiling

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 19 | Autotiling blob 47-tile | ✅ | `03 - Cursos/17 - DragoniteSpam - Autotiles.md` §4-5; `13·02` §3.3 (tabla 16 vs. 47) | — |
| 20 | Autotiling Wang tiles (2-corner/edge) | 🟡 | Funcionalmente es el sistema de "16 baldosas" de `03·17` §4 | El término "Wang tiles" nunca aparece; no se traza el paralelismo corner-based vs. edge-based |
| 21 | Reglas de esquina para transiciones de terreno | 🟡 | `03·17` §5 (plantilla de codos); `13·07` §5.3 (sockets WFC) | No hay tabla/algoritmo genérico bitmask→índice reutilizable fuera del editor o de WFC |
| 22 | Animación de tiles en tilemap | ✅ | `03 - Cursos/18 - ...Baldosas Animadas.md` completo + `08·09` §9 (`tilemap_get_frame`) | — |
| 23 | API de tilemap en GameMaker | ✅ | `08·09` completo (44 funciones: `tilemap_set`, `tilemap_get_at_pixel`, `layer_tilemap_create`…) | — |
| 24 | Autotiling: editor vs. runtime GML | 🟡 | `13·02:305,748` dice explícitamente "no se puede pintar autotiles por GML: calcula el bitmask tú" | Se dice "hazlo tú" pero no hay código real de conversión bitmask de vecinos → `tile_set_index()` |
| 25 | Márgenes/spacing de tileset (bleeding) | ✅ | `03 - Cursos/16 - ...Editor de Rooms.md` §4-5 (Output Border=2); `13·03` §6.2 (Edge Filtering, Separate Texture Page) | — |

### Atlas y texture pages

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 26 | Grupos de texturas: qué son y configuración | ✅ | `08·08` completo (API) + manual `Settings/Texture_Groups.md` (editor) | — |
| 27 | Carga bajo demanda / prefetch de texture groups | ✅ | `04·41` §3.3 (pantalla de carga real con `texturegroup_load`/`texturegroup_get_status`) | — |
| 28 | Bleeding entre sprites de atlas y padding | ✅ | `13·03` §6.2 (tabla completa: Edge Filtering, Output Border, Premultiply Alpha) | — |
| 29 | Límites de tamaño de textura (2048/4096) | ✅ | Manual `Texture_Pages.md` (máx. 4096×4096, reducción si excede); `13·03` §6.2 | No hay 8192 porque no existe como límite real — correcto no documentarlo |
| 30 | Empaquetado de atlas y borde del sprite | ✅ | Manual `Texture_Groups.md` ("Tamaño del borde": duplicación de píxeles en bordes) | — |

### Animación de personajes

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 31 | Frames por acción (idle/walk/run/attack) | ✅ | `13·04` §... y `13·03` §4.3 (tabla 2/4/6/8 frames por coste/uso) | — |
| 32 | Timing y spacing | ✅ | `13·04` §1.2 (Williams: timing≠spacing) + `13·03` §4.2 (duración relativa por momento) | — |
| 33 | Anticipación | ✅ | `13·04` §1.1, §1.3 (salto de 6 subimágenes con 2 de anticipación), checklist §9 | — |
| 34 | Follow-through / overlap | ✅ | `13·04` §4.4 (código de cadena de eslabones con retardo) | — |
| 35 | Smear frames | ✅ | `13·04` §1.4 (ataque de 4 subimágenes con smear) + `13·03` §4.5 (reglas) | — |
| 36 | Animación "en 1s/2s/3s" | ✅ | `13·04` §8 (tabla 24/12/8/4-6 subimágenes·s⁻¹, cita de Richard Williams) | — |
| 37 | Animación procedural / IK básico | 🟡 | `13·04` §4 (lerp+delta_time, cadena de eslabones simple — precursor de IK) | **No hay IK real** (2-bone/CCD). 0 resultados de "IK", "cinemática inversa", "inverse kinematics" en toda la biblioteca |
| 38 | Animación secundaria (pelo, ropa, cola) | ✅ | `13·04` §4.4 (mismo código, explícito para pelo/capa/cola/maza) | — |
| 39 | Blend/crossfade entre animaciones de SPRITE (no Spine) | 🔴 | `13·04` §3.5 solo resuelve el **corte seco** (`cambiar_sprite()`) | No existe ninguna receta de fundido visual entre dos animaciones de fotogramas (alpha cruzado 2-4 frames); 0 resultados de "cross-fade entre sprite" |

### Esqueletos

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 40 | Spine: import, skins, slots, eventos | 🟡 | `08·22` §2-4 (skins, slots/color, eventos vía `skeleton_animation_get_event_frames`) | El enlace de "import" apunta a `04·00`, que no menciona Spine (enlace roto). **Defecto verificado**: línea 33, `skeleton_animation_set("correr", 0);` comentado como "en bucle" — la firma real es `skeleton_animation_set(animname, [loop])`, `0` = **sin bucle**, justo lo contrario |
| 41 | DragonBones en GameMaker | 🔴 | — | **Ausencia total.** 0 resultados de "DragonBones" en toda la biblioteca (ni siquiera documentado como no soportado) |
| 42 | Mezcla de animaciones esqueletales | ✅ | `08·22` §1 (`skeleton_animation_mix("idle","correr",0.2)`, explicación del porqué) | No explica multi-track simultáneo (piernas track 0 + brazos track 1) aunque `skeleton_animation_set_ext` se usa una vez sin explotarlo |
| 43 | Attachments (cambio de equipamiento) | ✅ | `08·22` §3bis (`skeleton_attachment_exists/replace/create/destroy` con ejemplo espada→hacha) | — |
| 44 | Rendimiento de esqueletos en escena / LOD | 🔴 | `08·22` solo dice "más CPU" sin cifras | Sin guía de cuántos personajes Spine soporta una escena ni técnica de LOD (bajar fps de animación / desactivar mezcla fuera de cámara) |

### Sequences y Animation Curves

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 45 | Sequences: qué son, tracks, keyframes | ✅ | `13·04` §6.1-6.2 (vocabulario, todas las `seqtracktype_*` verificadas) | El struct de pista/keyframe solo existe en el manual espejado, sin resumen propio |
| 46 | Animation Curves: interpolación y easing | ✅ | `13·04` §5.2-5.3 (Linear/Catmull-Rom/Bezier, código de evaluación cacheada) | — |
| 47 | Cuándo usar Sequences vs. código puro | ✅ | `13·04` §2, §6.7 (tabla + regla "si el jugador puede interrumpirlo, no es una Sequence") | — |
| 48 | Generar/editar Sequences por código | 🔴 | `13·04` §6.1 solo **nombra** `sequence_get()`/`sequence_create()` en una tabla | `sequence_track_new`, `sequence_keyframe_new`, `sequence_keyframedata_new` existen (verificados) pero no aparecen ni una vez en el documento — 0 coincidencias |

### Sprite técnico (origen, máscara, nine-slice, runtime)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 49 | Origen del sprite e impacto en animación/colisión | ✅ | `03 - Cursos/31...md` §11; `04·39` §3.11 (`draw_sprite_general` ignora el origen); `13·04:399-409` | Cambio de origen por código (`sprite_set_offset`) sin ejemplo propio en la biblioteca |
| 50 | Máscara de colisión: tipos y elección | ✅ | `01·08` L284-380 (tabla Rectangle/Ellipse/Diamond/Precise/Precise-per-frame, `sprite_collision_mask()`) | — |
| 51 | Nine-slice para UI escalable | ✅ | `13·05` §3.4 completo (`sprite_nineslice_create`, `sprite_set_nineslice`, struct, constantes `nineslice_*`, 4 trampas) | — |
| 52 | Sprite dinámico en runtime (crear/editar por código) | 🟡 | `04·43` §3.3 (`mod_sprite_cargar`); `04·10` §5.8 (`sprite_create_from_surface`); `08·23` §3.10 | Sin receta unificada; son ejemplos dispersos en 3 documentos de género distinto |
| 53 | `sprite_add` desde archivo vs. generación procedural | ✅ | `13·03` L800-825; `08·23` §3.10 (generación pixel a pixel); `08·05` (transferencia buffer→superficie) | — |
| 54 | Surfaces como sprites (`sprite_create_from_surface`) | ✅ | `08·23` §3.10 (`generar_lut_identidad()`: crea, dibuja, convierte, libera superficie) | — |
| 55 | Gestión de memoria de sprites dinámicos | 🟡 | Avisos correctos y repetidos en `04·43`, `04·10`, `13·03` sobre `sprite_delete()` | Dispersos; sin sección de referencia dedicada (paralela a la de superficies en `08·05`) |

### Iluminación 2D

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 56 | Normal maps 2D | ✅ | `04·24` §3 completo (codificación RGB→vector, shader completo, requisito Separate Texture Page) | Generación del normal map en sí queda fuera del motor (recomienda `Laigter` externo, dicho honestamente) |
| 57 | Luces por superficie (aditiva/multiplicativa) | ✅ | `04·24` §1 (superficie + `bm_subtract`/`bm_add`, código completo) | — |
| 58 | Sombras dinámicas 2D (shadow casting) | ✅ | `04·24` §4 (extrusión de aristas, integración con superficie, penumbra por blur, presupuesto) | Penumbra geométrica exacta fuera de alcance, dicho explícitamente |
| 59 | Ciclo día/noche con rampa de color | ✅ | `04·24` §6 (paradas horarias, interpolación, teñido de luces) | — |
| 60 | Occluders / máscaras de oclusión de luz | ✅ | `04·24` §4.1, §5.1 (god rays) | Solo formas rectangulares para oclusores; cóncavos requieren descomposición (dicho) |

### Color grading y post-proceso

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 61 | Color grading vía shader (LUT) | 🟡 | `08·23` §3.10 completo (LUT como textura, `aplicar_lut()`) + `_filter_lut_colour` nativo | Solo LUT; no hay receta de color grading por **matriz** (equivalente a ColorMatrixFilter 4×4) |
| 62 | Post-proceso: bloom, viñeta, aberración cromática, CRT | ✅ | `08·23` completo (10 recetas: hit flash, aberración cromática, CRT, glitch, pixelado, shockwave, heat haze, blur 2 pasadas, bloom completo, LUT) | — |
| 63 | Blend modes y usos creativos | ✅ | `08·04` (1256 líneas: `gpu_set_blendmode`/`_ext`/`_ext_sepalpha`, ecuaciones, stencil) | — |

### 3D en GameMaker

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 64 | Modelos 3D: formatos y carga | ✅ | `04·29` §4 (parser `.obj` en GML puro); confirma `d3d_*` y `GM3D_*` NO existen (0 símbolos) | Ausencia de cargador nativo — es límite real del motor, correctamente documentado, no un hueco |
| 65 | Vertex buffers y formatos personalizados | ✅ | `08·07` completo (37 funciones, 5 ejemplos: quad, terreno con normales, bandera, partículas) | — |
| 66 | Materiales 3D básicos | ✅ | `04·29` §5 (Lambert por shader + textura combinada; legacy `draw_set_lighting`) | Sin PBR (metalness/roughness) — fuera de alcance del motor, dicho explícitamente (BBMOD como vía) |
| 67 | Billboards en 3D | ✅ | `04·29` §6 (`cartel_matriz()`, giro desde cámara, caso 2.5D) | — |
| 68 | Low-poly: viabilidad y límites | ✅ | `04·29` L15-56 (árbol de decisión + tabla "qué es razonable") | — |

### Cámara y composición visual

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 69 | Look-ahead por velocidad/dirección | ✅ | `06/scr_camera.gml` (`cam_set_lookahead`); usado en `04·01 §5.7`, `04·02 §5.7`, `04·12 §5.6` | — |
| 70 | Camera shake / screen shake | ✅ | Triple: `scr_camera.gml` (`cam_shake`), `04·15 §5.1` (trauma², Eiserloh), FX nativo `_filter_screenshake` | — |
| 71 | Composición visual: tercios, espacio negativo | 🟡 | Heurísticas reales con otro vocabulario: `13·02 §1.3` (landmark, *weenie*, líneas de guía — Kevin Lynch/Disney) | "Regla de los tercios" y "espacio negativo" no aparecen por su nombre; es un problema de vocabulario/indexación, no de contenido |
| 72 | Camera bounds/clamps al room | ✅ | `scr_camera.gml` (`cam_set_bounds`); extendido a zonas en `13·19 §3.5` | — |
| 73 | Multi-cámara / split-screen | ✅ | `01·10 §7` (código completo, 2 viewports) | `13·19` líneas 747 y 1040 citan `04·14 §8` para split-screen; ese §8 es "Cómo escalarlo" (delta compression) — cita a corregir, la función en sí está bien resuelta |

### Parallax y capas

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 74 | Parallax scrolling con `layer_x`/`layer_get_x` | ✅ | `01·10 §3, §12`; pixel-perfect en `13·03 §6.8` | — |
| 75 | Parallax infinito / tiling continuo | ✅ | `01·10 §10` (`layer_background_htiled`, `layer_background_speed`); `04·03 §4.1` (shmup) | Sin receta explícita de wrap-around por reposicionamiento de segmentos (patrón de *endless runner* con fondos generados por partes) — el mecanismo nativo cubre el caso general |
| 76 | Profundidad visual: capas + niebla/atmósfera | ✅ | `04·39 §3.7` (niebla con `draw_sprite_tiled_ext`+aditivo); FX nativo `_filter_parallax`; `layer_background_blend` | — |

### Arte de UI

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 77 | Iconos SVG vs. bitmap (2026) | ✅ | `02·06 §1` (import SVG, "Import As Strip", 9 funciones de caché, aviso GMRT sin soporte) | — |
| 78 | Fuentes bitmap vs. TTF | ✅ | `13·05 §3.6` (tabla comparativa: escalado, rotación, coste, estética, idiomas) | — |
| 79 | Escalado de fuentes sin pérdida (SDF) | ✅ | `02·06 §2-3` completo (`font_enable_sdf`, `font_sdf_spread`, `font_enable_effects` con outline/glow/drop shadow) | — |

### Pipeline de arte

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 80 | Aseprite → GameMaker: exportadores automatizados | ✅ | `12·05 §1` (AseSync, conveyorbelt★7, GM Link, GM-Sprite-Importer); `13·03 §5` (CLI de Aseprite + `sprite_add`) | — |
| 81 | Nomenclatura de assets de arte | ✅ | `05·04 §1` (tabla completa de prefijos `spr_/snd_/fnt_/bg_/ts_/tl_/an_/ps_/pt_`) | No cubre nomenclatura de archivos exportados sueltos fuera del motor |
| 82 | Control de versiones de arte (Git LFS) | ✅ | `13·11 §4.1` (muy completo: comandos reales, exclusión de `.yy`/`.yyp`, cuotas GitHub verificadas 06-09-2026, alternativas GitLab/Perforce) | — |
| 83 | Hoja de sprites vs. frames sueltos | 🟡 | `13·03 §5.4` (convención `_stripN`, coste de memoria) | Sin comparación explícita de pros/contras frente a frames sueltos (solo una línea en `07·09`) |
| 84 | Exportación automatizada arte→motor | ✅ | `12·05 §1` + `12·08 §1` (`@bscotch/stitch`, `@bscotch/yy` para leer/escribir `.yy`/`.yyp` sin corromper) | — |

### Rendimiento visual

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 85 | Batching: qué lo rompe | ✅ | `01·11 §11` (código MAL/BIEN ordenando por textura/blend/shader) | — |
| 86 | Overdraw: qué es, cómo medirlo, evitarlo | 🔴 | Solo una mención de pasada en `04·39:922` ("causa principal de tirones en móvil") | Sin definición, sin método de medición (GameMaker no tiene overlay nativo), sin técnicas de mitigación |
| 87 | Nº de texturas simultáneas / draw calls | ✅ | `01·15` (ventana Texture del Debug Overlay); `12·05 §6bis` | — |
| 88 | Herramientas de perfilado visual (Debug Overlay) | ✅ | `01·15` completo (FPS/Log/Audio/Memory/Texture Groups/Texture/FlexPanel) | — |
| 89 | Vertex buffers estáticos / instancing | ✅ | `08·07` (`vertex_freeze`); `04·29 §9` ("un buffer por malla, no por objeto") | Sin ejemplo 2D explícito (el único ejemplo es 3D); GameMaker no tiene instancing real, correctamente no reclamado |

### Arte generado por IA

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 90 | Upscalers de pixel art con IA | 🔴 | — | 0 apariciones de "upscal[er/ing]" en toda la biblioteca |
| 91 | Consistencia de estilo en IA (seeds, ControlNet, LoRA) | 🔴 | `13·03 §7.2` solo dice que la IA sirve para "hojas de referencia", nunca para el sprite final | 0 menciones de ControlNet, LoRA o seeds en toda la biblioteca |
| 92 | Limitaciones legales del arte IA (copyright, políticas de plataforma) | 🔴 | Una frase suelta en `13·03 §7.2` ("declara lo que uses"), sin fuente. `13·11 §12.5` trata cesión de derechos humana, no autoría de IA | Sin doctrina de autoría (US Copyright Office), sin política real de divulgación de Steam, sin fuentes citadas |

## Huecos por prioridad

### 🔴 Graves

1. **Arte generado por IA: ausencia total como criterio de producción** (temas 90, 91, 92). El
   único documento con "IA" en el título (`07 - Ecosistema/14 - IA y GameMaker.md`) trata
   exclusivamente IA como agente de programación (MCP, Claude Code); nunca como generadora de
   assets visuales. Es contradictorio con el propio flujo de trabajo del proyecto (que usa
   `gpt-image-2` vía `codex exec` para iconos/logos/hojas de modelado 3D): la biblioteca no
   documenta ese mismo criterio para arte 2D de juego.
2. **Outline/contorno selectivo en pixel art** (tema 9). Técnica de estilo elemental sin ninguna
   receta en prosa; solo existe como código de terceros sin documentar.
3. **Defecto verificado en `08 - Referencia GML completa/22 - Animación esqueletal (Spine).md`
   línea 33**: `skeleton_animation_set("correr", 0);` comentado como "en bucle" cuando `0` en el
   segundo argumento (`loop`, booleano) **desactiva** el bucle — justo lo contrario. Un LLM que
   copie el ejemplo produce animaciones que se detienen creyendo que loopean.
4. **Blend/crossfade entre animaciones de sprite frame-by-frame** (tema 39, distinto de la mezcla
   esqueletal de Spine, que sí existe). Técnica común (fundido de 2-4 frames al cambiar de
   animación) totalmente ausente; solo hay corte seco documentado.

### 🟠 Medios

5. **DragonBones: ausencia total** (tema 41), ni siquiera documentada como no soportada.
6. **Autotiling por código sin receta de bitmask→índice de tile** (temas 20, 21, 24). Se dice
   "hazlo tú" tres veces en la biblioteca pero nunca se muestra el código de conversión.
7. **Overdraw: solo una mención de pasada** (tema 86), sin definición ni técnica de mitigación.
8. **Rendimiento y LOD de esqueletos Spine en escena** (tema 44), sin cifras ni técnica.
9. **IK / cinemática inversa básica ausente** (tema 37); solo hay cadenas de eslabones con
   retardo, que no son IK real.
10. **`13·03 - Pixel art y resolución.md` no cruza con letterbox/pillarbox, DPI ni
    `display_set_gui_maximise()`** (temas 13, 14, 15), y **`04·28` promete contenido en `13·03`
    sobre escalado fraccionario en móvil que no existe ahí** — enlace de contenido roto,
    verificado con grep.
11. **Composición visual como disciplina de arte** (tema 71): existen heurísticas reales
    (landmark, *weenie*) pero con vocabulario distinto al que un agente buscaría ("regla de los
    tercios", "espacio negativo").

### 🟡 Menores

12. Proporción "cabezas de alto"/chibi ausente (tema 8) — solo se cubre tamaño relativo a pantalla.
13. `sequence_track_new`/`sequence_keyframe_new`/`sequence_keyframedata_new` verificados pero sin
    ejemplo de uso — generación de Sequences por código no demostrada (tema 48).
14. Color grading solo por LUT, sin receta de matriz de color 4×4 (tema 61).
15. Sprite dinámico en runtime y su gestión de memoria: contenido correcto pero disperso en 3
    documentos de género distinto, sin sección de referencia unificada (temas 52, 55).
16. Hoja de sprites vs. frames sueltos sin comparación explícita de pros/contras (tema 83).
17. `sprite_set_offset` (cambio de origen por código) sin ejemplo propio en la biblioteca (tema 49).
18. Cita cruzada rota: `13·19` líneas 747 y 1040 apuntan a `04·14 §8` para split-screen; la
    sección real es `01·10 §7` (tema 73).
19. Import de Spine (`08·22`, tema 40) enlaza a `04·00`, que no menciona Spine — enlace roto.

## Encargo para el redactor

1. **Nueva sección en `13 - Diseño y producción de videojuegos/03 - Pixel art y resolución.md`**,
   junto a §3 (Estilo): *"Outline/contorno selectivo"*. Contenido: contorno negro puro vs. de
   color extraído de la rampa, borde externo vs. líneas internas, coste en clusters. Enlazar
   (no duplicar) el shader de contorno en tiempo real que ya existe en `08·06 §6.2`.
   Sin símbolos GML nuevos — es criterio de dibujo, no de código.

2. **Ampliar `07 - Ecosistema/14 - IA y GameMaker.md`** con una sección nueva y bien delimitada
   *"§X · IA como generadora de arte (distinto del resto del documento)"*, o crear
   `07 - Ecosistema/14 bis - Arte generado por IA.md` si el redactor considera que mezclar ambos
   sentidos de "IA" en un documento confunde más de lo que aclara. Contenido: (a) upscalers de
   pixel art — riesgos de artefactos y pérdida de rejilla, cuándo aceptar el resultado; (b)
   consistencia de estilo — seeds, ControlNet, LoRA, img2img con referencia de estilo fija; (c)
   límites legales — postura de la U.S. Copyright Office sobre autoría humana mínima, política de
   divulgación de contenido generado por IA en Steam (requiere investigación con fuentes
   primarias verificadas, no inventar). Sin símbolos GML — es un tema de proceso.

3. **Corrección puntual en `08 - Referencia GML completa/22 - Animación esqueletal (Spine).md`
   línea 33**: cambiar `skeleton_animation_set("correr", 0);  // en bucle` por
   `skeleton_animation_set("correr", true);  // en bucle` (o mostrar explícitamente el contraste
   `true`/`false`). Símbolo verificado: `skeleton_animation_set(animname, [loop])`.

4. **Nueva sección en `13 - Diseño y producción de videojuegos/04 - Animación de sprites,
   Sequences y Animation Curves.md`**, junto a §3.5: *"Blend/crossfade entre animaciones de
   sprite"*. Contenido: fundido de 2-4 frames con `draw_sprite_ext` a alpha cruzado (dibujar la
   animación saliente con `image_alpha` decreciente y la entrante con alpha creciente durante la
   transición), en vez del corte seco de `cambiar_sprite()`. Símbolos verificados:
   `draw_sprite_ext`, `image_alpha`, `image_index`.

5. **Nota breve en `08·22`** (o en `13·04`): dejar constancia explícita de que **DragonBones no
   tiene soporte nativo en GameMaker** (solo Spine vía la familia `skeleton_*`, 48 funciones
   verificadas) y remitir a Spine como alternativa recomendada.

6. **Nueva sub-sección en `13 - Diseño y producción de videojuegos/02 - Diseño de niveles.md`**
   (o en `04 - Recetas por género/05 - Roguelike y generación procedural.md`, que ya tiene
   `vecinos_opacos()`): *"Autotiling por código: bitmask de vecinos → índice de tile"*. Tabla de
   conversión para 4 vecinos (16-tile) y 8 vecinos (47-tile blob) con código GML usando
   `tile_set_index()`/`tilemap_set()` (ambos verificados).

7. **Nueva sección en `04 - Recetas por género/39 - VFX - diseño y catálogo de efectos.md`**
   (o en `01 - Fundamentos/15 - Depuración y rendimiento.md`): *"Overdraw: qué es, cómo medirlo
   y cómo evitarlo"*. Contenido: definición (píxeles transparentes redibujados varias veces),
   cómo inferirlo del Debug Overlay a falta de un contador nativo, mitigación (menos capas
   aditivas solapadas, `gpu_set_alphatestenable`/`gpu_set_alphatestref`, límite de partículas ya
   descrito en `04·39 §3.12`). Símbolos verificados: `gpu_set_alphatestenable`,
   `gpu_set_alphatestref`, `show_debug_overlay`.

8. **Ampliar `08·22`** con *"Rendimiento y LOD de esqueletos"*: cifras cualitativas de referencia
   (como hace `04·39 §3.12` con partículas) y técnica de reducir la tasa de actualización de
   animación para esqueletos lejanos o fuera de cámara. Símbolos a verificar antes de usarlos:
   `skeleton_animation_get_position`/`skeleton_animation_set_position` (confirmar firma exacta
   con `buscar.py` antes de escribir el ejemplo).

9. **Ampliar `13·04` §4** (junto a la cadena de eslabones existente) con el límite explícito de
   que esa cadena **no es IK real**, y opcionalmente un solver CCD (Cyclic Coordinate Descent) de
   2-3 huesos en GML puro. Sin símbolos nuevos: usa `point_direction`/`lengthdir_x`/`lengthdir_y`,
   ya verificados y en uso en el resto de la biblioteca.

10. **Cerrar el enlace roto de `13·03`**: añadir una sección (p. ej. §6.9) *"Letterbox, DPI y GUI
    desacoplada de la resolución interna"* que cruce con `display_get_dpi_x()` (ya usado en
    `04·28`), `display_set_gui_maximise()` (ya usado en `01·11`/`13·05`) y las tres salidas para
    pixel art fraccionario en móvil que `04·28:324` promete. Símbolos verificados:
    `display_get_dpi_x`, `display_set_gui_maximise`, `display_set_gui_size`.

11. **Vincular vocabulario en `13·02 §1.3`**: añadir los términos "regla de los tercios" y
    "espacio negativo" junto al contenido ya existente (landmark, *weenie*, líneas de guía) para
    que sea localizable por ese nombre. Es indexación, no contenido nuevo.

12. **Corregir citas rotas** (coste mínimo, alto valor): `13·19` líneas 747 y 1040 — cambiar
    `04·14 §8` por `01·10 §7` para split-screen. `08·22` línea 22 — cambiar el enlace de import
    de Spine, que apunta a `04·00` (no menciona Spine), por una explicación propia breve del
    flujo del IDE (arrastrar `.json`+`.atlas`+`.png` al Sprite Editor).

13. *(Menor, opcional)* Añadir en `13·03 §1.3` una línea sobre la convención "cabezas de alto"
    (heads-tall) junto a la tabla de tamaño de protagonista ya existente.

14. *(Menor, opcional)* En `08·06` o `08·23`, receta de color grading por matriz 4×4 (equivalente
    a saturación/contraste/brillo combinados), complementando la vía LUT ya existente.

15. *(Menor, opcional)* Consolidar en `08·05 - Superficies.md` una sub-sección "Ciclo de vida de
    sprites dinámicos" que reúna (sin repetir) los avisos ya correctos pero dispersos en `04·43`,
    `04·10` y `13·03` sobre `sprite_delete()`.

## Lo que comprobé y NO hacía falta

Temas que, por conocimiento general del oficio, parecían huecos evidentes y resultaron ya
cubiertos — no hace falta que otro agente los reabra:

- **VFX: anatomía en capas, timing, rampa de color, trails, decals, destrucción, presupuesto** —
  `04·39` (1028 líneas) cierra exactamente los huecos que había detectado la auditoría de ronda 2
  (`vfx.md`); incluye el cierre de API de 13 funciones `part_type_*`/`part_system_*`.
- **Iluminación 2D avanzada: normal maps, sombras proyectadas, god rays, ciclo día/noche** —
  `04·24` (778 líneas) también cierra los huecos de `vfx.md`; nada de esto falta ya.
- **Shaders de efecto: hit flash, aberración cromática, CRT/scanlines, glitch, pixelado,
  shockwave, heat haze, blur de dos pasadas, bloom completo, LUT** — `08·23` (10 recetas
  completas) cierra el hueco que `vfx.md` marcaba como "los diez más pedidos".
- **Cámara como disciplina completa: marco de Itay Keren, camera window asimétrico,
  edge-snapping, platform-snapping, zonas de cámara, transición pantalla-a-pantalla, cámara
  multijugador con zoom dinámico, cinemáticas** — `13·19` (1047 líneas) cierra todos los huecos
  que marcaba `colisiones-movimiento-camara.md` (ronda 2).
- **Nine-slice** — parecía indocumentado en una búsqueda superficial (solo aparecía como campo de
  struct en `02·06`), pero `13·05 §3.4` lo cubre por completo con receta y trampas.
- **Sistema de partículas nuevo, `layer_particle_*`, editor visual** — `02·05` completo.
- **Sprites SVG, fuentes SDF, efectos de fuente, catálogo de 42 FX de capa, texture groups
  dinámicos, frustum culling 3D** — `02·06` completo y verificado función a función.
- **Máscara de colisión: los 5 tipos y su coste** — `01·08` completo.
- **Batching: qué lo rompe** — `01·11 §11`, con código MAL/BIEN.
- **Debug Overlay / perfilado visual** — `01·15` completo (FPS, memoria, texturas).
- **Blend modes** — `08·04` (1256 líneas), la referencia más exhaustiva del corpus.
- **Git LFS para arte** — `13·11 §4.1`, con comandos reales y cuotas verificadas en vivo.
- **Aseprite → GameMaker automatizado** — `12·05 §1` y `13·03 §5`.
- **Nomenclatura de assets** — `05·04 §1`.
- **Fuentes bitmap vs. TTF** — tabla comparativa completa en `13·05 §3.6`.
- **Parallax scrolling y parallax infinito** — `01·10 §3, §10, §12` (incluye
  `layer_background_htiled` nativo, no solo capas manuales).
- **3D en GameMaker: honestidad sobre límites reales** — `04·29` confirma y documenta
  correctamente que `d3d_*` y `GM3D_*` **no existen** en el runtime 2026.0.0.23; no es un hueco,
  es la respuesta correcta.
- **Vertex buffers y formatos personalizados** — `08·07`, referencia completa de 37 funciones.
