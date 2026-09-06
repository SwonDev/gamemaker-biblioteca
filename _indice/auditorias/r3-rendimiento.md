# Auditoría r3 · Rendimiento, memoria y perfilado

> **Fecha:** 06-09-2026 · **105 temas evaluados** · **79 cubiertos** · **14 parciales** · **11 faltan**
> (y 1 función pedida por el propio brief que se verificó y **no existe**: `draw_get_batch_count`)
> **Biblioteca auditada:** `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje` (excluidos
> `Lumbre/` y `GameMaker_Fuentes/`). Método: `_indice/BRIEF-auditor-r3.md`. Lista canónica
> contrastada con el blog oficial de GameMaker (*How to optimise your games in GameMaker*, *9
> Essential Best-Practise Tips*, vía WebSearch — `gamemaker.io` sigue devolviendo 403 a WebFetch
> directo, confirmando lo ya documentado en `00-auditoria-externa-inicial.md`), Game Programming
> Patterns (Data Locality, Object Pool) y el propio manual oficial espejado en `09 - Manual
> oficial/`. Cada símbolo de GML citado se verificó con `python3 "_indice/buscar.py" <símbolo>`.

## Resumen ejecutivo

El **núcleo duro del dominio está muy bien resuelto y con cifras reales, no folclore**: medir
con `get_timer()` por sistema, YYC vs VM, el presupuesto de 16,67 ms, el Garbage Collector
generacional, el coste de las máscaras de colisión, el particionado espacial, la disposición de
memoria (Data Locality medido con un benchmark real de 200 000 elementos) y el rendimiento móvil
(batería, térmicas, `display_set_sleep_margin`) tienen documentos serios, con código verificado.
El hueco que más duele es de un tipo distinto al resto: **no hay ni una palabra sobre
herramientas externas de perfilado** (RenderDoc, Instruments, Android Profiler) — un agente que
necesite ir más allá del Debug Overlay se queda sin ninguna guía, ni siquiera la honesta de «esto
no lo puedes hacer». Los demás huecos son concretos y pequeños: la comparación medida de
`ds_map`/`ds_list` frente a `struct`/array (solo hay guía cualitativa), `display_set_timing_method`
(vsync) sin una sola línea de prosa propia, el límite real de RAM en HTML5 y móvil más allá de la
VRAM, y el consejo — muy citado en fuentes oficiales — de sustituir instancias por sistemas de
partículas o *asset layers* cuando el elemento es solo visual.

---

## Tabla tema por tema

### A · Medir antes de optimizar

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 1 | Debug Overlay: ventana FPS en modo Stacked para localizar el cuello de botella | ✅ Cubierto | `01 - Fundamentos/15 - Depuración y rendimiento.md` §4 y §6 «Paso 1: mide antes de optimizar» | — |
| 2 | `get_timer()` para medir el coste de un sistema en microsegundos | ✅ Cubierto | `13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md` §14; `13/10 - Testing y QA.md` §6.1 | — |
| 3 | Mini-framework de benchmark reutilizable (`medir()`, calentar antes de medir, repetir, comparar en la misma tanda) | ✅ Cubierto | `13/10` §6.1 | — |
| 4 | GMBenchmark (comparar alternativas con interfaz y gráficas) | ✅ Cubierto | `13/10` §6.2 — script descargado en `11 - Código descargado/librerias/depuracion/GMBenchmark` | — |
| 5 | Contadores propios / vistas de depuración en vivo (`dbg_view`, `dbg_watch`, `dbg_slider_int`…) | ✅ Cubierto | `01/15` §4 «Vistas de depuración personalizadas» | — |
| 6 | `debug_event()` y el resto de funciones de depuración de nivel 2 | ✅ Cubierto | `01/15` §3 | — |
| 7 | `fps` (lógico) vs `fps_real` (real) | ✅ Cubierto | `01 - Fundamentos/06 - Eventos y ciclo del juego.md` §7; `01/15` §4 | — |
| 8 | Presupuesto de frame en ms (16,67 ms a 60 fps, reparto por partida) | ✅ Cubierto | `13/10` §6.3 «El presupuesto por frame» | — |
| 9 | Medir en el hardware objetivo, no en el IDE | ✅ Cubierto | `13/10` §6.4 «Mide en YYC, no en VM»; `04 - Recetas por género/28 - Juegos para móvil (táctil).md` §6.5 «Medir en el dispositivo, no en el PC» | — |
| 10 | Convertir un presupuesto de rendimiento en una prueba automática (CI) | ✅ Cubierto | `13/10` §6.3, ejemplo con `probar()` | — |

### B · Dibujado

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 11 | `draw_get_batch_count()` (verificado por el brief) | ⚠️ No existe | `python3 _indice/buscar.py draw_get_batch_count` → «NO existe en el runtime 2026.0.0.23» | No hay función GML para leer vertex batches por código; solo la ventana FPS del overlay lo muestra. No proponer nada que la use |
| 12 | Qué rompe un lote de dibujo (batch): textura, blend mode, shader, surface de destino | ✅ Cubierto | `01 - Fundamentos/11 - Dibujo y renderizado.md` §11 «Rendimiento: batching, texture pages, draw calls» | — |
| 13 | Texture swaps y vertex batches: por qué nunca son cero y cómo bajarlos | ✅ Cubierto | `01/15` §4 y §6; `01/11` §11 | — |
| 14 | **Overdraw** (coste de superponer sprites/capas semitransparentes) | 🔴 Falta | `grep -rli "overdraw\|sobredibuj"` en la biblioteca propia → 0 resultados (solo aparece en el manual espejado, para partículas 3D con `gpu_set_ztestenable`, y en `04/39` sin explicar el concepto 2D) | Como concepto de rendimiento 2D (sprites grandes semitransparentes apilados, capas de iluminación/VFX a pantalla completa) no está explicado en ningún documento propio |
| 15 | Orden de dibujado: `depth` (variable heredada) vs capas (`layer_depth`), coste de reordenar | 🟡 Parcial | `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md` (funcional: `layer_get_depth`, `layer_force_draw_depth`) | Documenta el mecanismo, no el coste de que GameMaker reordene el árbol de dibujo cuando cambias `depth` cada frame en muchas instancias |
| 16 | `draw_sprite()` vs vertex buffers manuales | ✅ Cubierto | `01/11` §4, §7 y §8; `08 - Referencia GML completa/07 - Vertex buffers y formatos.md` | — |
| 17 | Primitivas de dibujo (`draw_primitive_begin/end`): rápidas de escribir, lentas de ejecutar | ✅ Cubierto | `01/11` §7 | — |
| 18 | Vertex buffers: `vertex_submit`, `vertex_freeze` (congelar para más velocidad) | ✅ Cubierto | `01/11` §7; `08/07` §«Envío a la GPU» y §«vertex_freeze» | — |
| 19 | `draw_flush()`: cuándo y por qué rompe el batching a propósito | ✅ Cubierto | `01/11` §11 | — |
| 20 | `draw_enable_drawevent()` para saltarse el Draw en cálculos por lotes/headless | ✅ Cubierto | `01/11` §11 | — |
| 21 | Culling y descarte temprano de píxeles (`gpu_set_sprite_cull`, `gpu_set_alphatestenable`, `gpu_set_alphatestref`, `gpu_set_blendenable`) | ✅ Cubierto | `01/11` §11; `08 - Referencia GML completa/04 - Color y blending.md` | — |
| 22 | Código de lógica dentro del evento Draw (el Draw debe solo dibujar) | ✅ Cubierto | `01/15` §6 «Código en el Draw» | — |
| 23 | Cadenas de texto reconstruidas cada frame en el Draw (`"Vida: " + string(vida)`) | ✅ Cubierto | `01/15` §6 | — |
| 24 | `application_surface`: qué es, redimensionar solo al cambiar de resolución, desactivar su dibujado automático | ✅ Cubierto | `01/11` §2; `13 - Diseño y producción de videojuegos/03 - Pixel art y resolución.md` §6.3 | — |
| 25 | Coste de compilación de shaders / posible *stutter* en el primer uso | 🟡 Parcial | `08 - Referencia GML completa/06 - Shaders.md` §«`shader_is_compiled`» (comprobar que compiló, no cuándo compila) | No dice en qué momento del ciclo de vida GameMaker compila los shaders ni si hay coste de «primer uso» como en motores con variantes de shader; verificar contra el manual antes de afirmar nada |

### C · Texturas

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 26 | Texture pages: qué son y cómo se generan | ✅ Cubierto | `08 - Referencia GML completa/08 - Texturas y grupos de texturas.md` §«Qué es una textura» | — |
| 27 | Grupos de textura y carga/descarga dinámica (`texturegroup_load`, `texturegroup_unload`, `texturegroup_get_status`) | ✅ Cubierto | `08/08` §«Texturas dinámicas y grupos»; `04 - Recetas por género/41 - Transiciones, carga y pausa.md` §3.3 | — |
| 28 | Prefetch de texturas y sprites (`texture_prefetch`, `sprite_prefetch`, `sprite_prefetch_multi`) | ✅ Cubierto | `08/08` §«Gestión de VRAM» | — |
| 29 | Swaps de textura por frame: impacto y cómo agrupar sprites para evitarlos | ✅ Cubierto | `01/11` §11; `01/15` §6 «Paso 3» | — |
| 30 | Tamaño de página de textura por plataforma (2048 por defecto, 4096 revienta en gama baja) | ✅ Cubierto | `13/03` §6.2; `04/28` §6.2 | — |
| 31 | Sprites enormes / *Separate Texture Page* (cada subimagen se come su propia página) | ✅ Cubierto | `13/03` §6.2 | — |
| 32 | Filtrado de textura: `gpu_set_texfilter()` (no `texture_set_interpolation`, que no existe) | ✅ Cubierto | `13/03` §6.1, con la lista explícita de nombres inventados que no existen | — |
| 33 | Sangrado de textura (*bleeding*) y sus tres remedios (Tile H/V, Edge Filtering, Output Border) | ✅ Cubierto | `13/03` §6.2 «Páginas de textura: el sangrado y sus tres remedios» | — |
| 34 | Caché de sprites (`sprite_set_cache_size`) | ✅ Cubierto | `08/08` §«Caché de sprites» | — |
| 35 | `texture_global_scale()` para bajar VRAM en dispositivos limitados | ✅ Cubierto | `08/08`; `05 - Referencia/02 - Publicar y exportar.md` §4.5.3 | — |
| 36 | Formato del grupo de texturas (BZ2+QOI vs QOI a secas) y su coste de descompresión en Android | ✅ Cubierto | `13/03` §6.2 (vía referencia cruzada) | — |

### D · Surfaces

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 37 | Coste real de crear una surface (VRAM, no gratis) | ✅ Cubierto | `01/11` §8 «Las seis reglas de las surfaces», regla 2 | — |
| 38 | Recrear una surface tras pérdida de foco (`surface_exists()` siempre) | ✅ Cubierto | `01/11` §8 regla 1 y «El patrón correcto» | — |
| 39 | Resolución de la surface (no más grande que la vista/ventana) | ✅ Cubierto | `01/11` §8 regla 2 | — |
| 40 | No crear/redimensionar surfaces por frame | ✅ Cubierto | `13/03` §6.3 «Dos reglas que evitan la mitad de los problemas» | — |
| 41 | `application_surface_enable`/`_draw_enable` para desactivarla y dibujar a mano | ✅ Cubierto | `08 - Referencia GML completa/05 - Superficies.md` §«La Application Surface»; `13/03` §6.3 | — |

### E · Instancias

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 42 | Coste de miles de instancias activas (Step/Draw de cada una) | 🟡 Parcial | `01/15` §6 «Paso 6» (enmarcado solo para colisiones, con cifras de `13/08` §4.3 para entidades en spatial hash) | No hay una cifra o benchmark de «cuántas instancias vacías (sin colisión) empiezan a doler» solo por overhead de Step/Draw |
| 43 | `instance_deactivate_region()`/`instance_activate_region()` y la trampa de llamarlas cada step | ✅ Cubierto | `01/15` §6 «Paso 2»; `01/11` §11 | — |
| 44 | Pooling de instancias vs `instance_create`/`instance_destroy` continuo | ✅ Cubierto | `06 - Assets y Scripts/scr_pool.gml` (con la justificación de rendimiento en la cabecera) | — |
| 45 | **Sustituir instancias por sistemas de partículas / asset layers / tiles cuando el elemento es solo visual o estático** | 🔴 Falta | Blog oficial de GameMaker (WebSearch, *How to optimise your games*): «people frequently fall into using objects when they should use particle systems, data structures, or asset layers instead» — `grep` en la biblioteca propia de «partículas... en vez de instancia» y «asset layer... rendimiento» → 0 resultados | No hay ninguna sección que compare el coste de una instancia completa (eventos, colisión, `id`) frente a una partícula del sistema nativo o un elemento de asset layer para efectos y decoración puramente visuales |
| 46 | `with()` sobre un objeto con muchas instancias vs mantener tu propia lista | ✅ Cubierto | `01/15` §6 «Paso 2» | — |
| 47 | `instance_number()` como medida de cuántas instancias hay | ✅ Cubierto (funcional) | `01 - Fundamentos/09 - Instancias, objetos y herencia.md` §6 | — |
| 48 | Eventos definidos pero vacíos (Step/Draw sin código): ¿tienen coste real? | 🔴 Falta | `grep` de «evento vacío», «step vacío» → 0 resultados de fondo sobre coste; solo aparece como curiosidad de otro tema (`03/31`, `13/05`) | Ningún documento dice si un evento Step/Draw creado pero vacío añade una llamada medible por instancia, ni cómo comprobarlo |
| 49 | Herencia y `event_inherited()`: coste de la cadena de llamadas al padre | 🟡 Parcial (menor) | `01/09` §7 (funcional, sin coste) | Nicho: las jerarquías de GameMaker rara vez pasan de 2-3 niveles: bajo impacto real |

### F · Colisiones

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 50 | Rejilla espacial / *spatial hash* propia | ✅ Cubierto | `13/08 - Físicas a mano y fluidos.md` §4 «Particionado espacial» | — |
| 51 | Quadtree y por qué esta biblioteca no lo recomienda para 2D | ✅ Cubierto | `13/08` §4.4 «Y el quadtree, ¿por qué no?» | — |
| 52 | `collision_*` nativas (`collision_rectangle`, `collision_circle`, `collision_line`, `_list`) vs comprobación manual | ✅ Cubierto | `01 - Fundamentos/08 - Movimiento y colisiones.md` §3.5 | — |
| 53 | Coste relativo de cada forma de máscara (`bboxkind_*`), de Rectangle a Precise per frame | ✅ Cubierto | `01/08` §4 «Elegir la forma de la máscara», tabla con columna «Coste relativo» | — |
| 54 | `place_meeting()`/`move_and_collide()` en bucles anidados: coste O(n²) con `all` | ✅ Cubierto | `01/15` §6 «Paso 6» | — |
| 55 | Particionado espacial aplicado a `place_meeting`/`move_and_collide` (no solo a física a mano) | ✅ Cubierto | `01/15` §6 «Paso 6», enlaza a `13/08` §4 | — |

### G · GML: estructuras de datos, GC, strings, funciones

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 56 | Arrays vs structs — coste medido de verdad (*Data Locality*, array de structs vs *struct-of-arrays*) | ✅ Cubierto | `13 - Diseño y producción de videojuegos/23 - Catálogo de patrones en GML.md` §3.4 «Data Locality — medido, no folclore» (benchmark real, factor 2,7× medido en YYC/M5 Pro) | — |
| 57 | `ds_map`/`ds_list` vs `struct`/array — coste de acceso medido | 🟡 Parcial | `05 - Referencia/03 - Glosario GML.md` entrada «Data structure (`ds_*`)» (guía cualitativa: «en 2026 usa arrays y structs salvo necesidad concreta»); `13/10` §6.2 muestra el patrón de `GMBenchmark` con el ejemplo literal `dot operator` vs `struct accessor` pero sin ejecutarlo ni dar cifras | Falta el benchmark ejecutado (mismo patrón que la Data Locality de `13/23` §3.4) que compare `ds_map_find_value` con acceso a struct y con `ds_list` vs array, con cifras reales |
| 58 | Copia por referencia vs por valor (arrays y structs son *handles* desde 2026) | ✅ Cubierto | `01 - Fundamentos/05 - Arrays y estructuras de datos.md` §7 «Copiar: superficial vs profundo»; `01/03` (handles) | — |
| 59 | Recolector de basura: generacional + incremental, `gc_target_frame_time`, `gc_get_stats` | ✅ Cubierto | `01/15` §5 «El Garbage Collector» | — |
| 60 | `delete` y `weak_ref_create`/`weak_ref_alive` — limpieza determinista frente a esperar al GC | ✅ Cubierto | `01/15` §5 «Referencias débiles» | — |
| 61 | Forzar `gc_collect()` en un momento seguro (cambio de room) para que el GC no dispare en mitad de una escena de acción | 🟡 Parcial | `01/15` §5, una línea de comentario en el ejemplo (`// Forzar una recogida en un momento seguro`) | Es una idea correcta pero no desarrollada: no hay ejemplo enganchado a la pantalla de carga real de `04/41` §3.3, que sería el sitio natural |
| 62 | Strings inmutables y coste de concatenación repetida | ✅ Cubierto | `01/15` §6 «Cadenas de texto construidas cada frame» | — |
| 63 | Funciones `string_*` recalculadas en el Draw | ✅ Cubierto | `01/15` §6 | — |
| 64 | Coste de crear un `function()` (método/closure) dentro de un bucle o del Step | 🔴 Falta | `grep` de «función.*cada step», «closure.*rendimiento» → 0 resultados propios | El principio general de `01/15` §6 («no crear structs/arrays en el Step») no se extiende explícitamente a *method variables*/closures creadas en caliente, que también son una asignación que el GC debe recoger |
| 65 | `static` como técnica para cachear un valor costoso y no recalcularlo | 🟡 Parcial | `01 - Fundamentos/07 - Funciones, métodos y ámbito.md` §6 «`static` en funciones» (documentado como mecanismo de lenguaje, no como técnica de rendimiento) | Falta un ejemplo explícito «static para memoizar un cálculo caro» |
| 66 | Funciones globales (scripts) vs métodos de struct — coste de llamada | 🔴 Falta | `grep` de «coste de llamar», «script.*vs.*method.*rendimiento» → 0 resultados | Tema nicho pero citable: no hay comparación de rendimiento entre llamar a un script global y llamar a un método ligado a un struct |
| 67 | `struct_get_ext()` (acceso por hash) más rápido que `struct_get()` repetido | ✅ Cubierto | `08 - Referencia GML completa/15 - Structs - funciones.md` §«`struct_get_ext`» | — |
| 68 | Object Pool como patrón general (no solo instancias) | ✅ Cubierto | `13/23` §Checklist; `06/scr_pool.gml` | — |
| 69 | Advertencia explícita contra la microoptimización de aritmética dentro de bucles | ✅ Cubierto | `13/08` §14 «Lo que no funciona: microoptimizar la aritmética dentro del bucle» | — |

### H · Audio

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 70 | Límite de voces simultáneas (`audio_channel_num()`, 128 por defecto) | ✅ Cubierto | `01 - Fundamentos/13 - Audio.md` §3 «El límite de voces» | — |
| 71 | Streaming (`audio_create_stream`) vs decodificado en memoria, para música larga | ✅ Cubierto | `01/13` §9 «Audio en streaming» | — |
| 72 | `audio_group_*`: carga/descarga de grupos de audio por nivel | ✅ Cubierto | `01/13` §8 «Audio groups» | — |
| 73 | Coste de CPU de los buses/efectos de audio (reverb, EQ, cuántos bus/efectos son razonables) | 🟡 Parcial (menor) | `02 - Novedades 2026/07 - Audio - buses y efectos.md` §5 (funcional, sin coste de CPU) | Nicho: solo relevante si se abusa de efectos DSP; no bloquea a la mayoría de proyectos |

### I · Memoria

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 74 | Medir memoria real (ventana Memory del overlay, `gc_get_stats()`) | ✅ Cubierto | `01/15` §4 «La ventana Memory» | — |
| 75 | Fugas por estructuras de datos (`ds_*`) creadas y nunca destruidas | ✅ Cubierto | `01/15` §8 «Checklist de limpieza de recursos dinámicos» | — |
| 76 | Buffers no liberados (`buffer_create` sin `buffer_delete`) | ✅ Cubierto | `01/15` §8 | — |
| 77 | Texturas/grupos de texturas retenidos en VRAM sin descargar | ✅ Cubierto (vía API) | `08/08` §«Texturas dinámicas y grupos» (`texturegroup_unload`) | Existe la función; falta un aviso explícito tipo «si nunca llamas a `texturegroup_unload`, el grupo se queda en VRAM para siempre» — hoy se infiere, no se dice |
| 78 | Presupuesto de memoria RAM real por plataforma (más allá de VRAM y tamaño en disco) | 🔴 Falta | `05 - Referencia/02 - Publicar y exportar.md` §4.5 cubre **tamaño en disco** y VRAM, no techos de RAM en tiempo de ejecución; `grep` de «presupuesto de memoria», «memory budget» → 0 resultados | No hay ninguna cifra ni referencia sobre cuánta RAM tolera de verdad un juego GameMaker en iOS/Android antes de que el sistema operativo lo mate por presión de memoria (dato público, no NDA) |
| 79 | Límites de memoria en HTML5 (heap del navegador/WASM) | 🔴 Falta | `04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md` §3 no lo menciona; `01/15` §5 solo dice que en HTML5 el GC lo gestiona el motor de JavaScript | Ningún documento avisa del techo práctico de memoria en un build HTML5 ni de cómo se manifiesta (el navegador mata la pestaña, no hay excepción capturable) |
| 80 | Límites de memoria en móvil (más allá de batería/térmicas) | 🟡 Parcial | `04/28` §6 cubre batería, térmicas y fps, no un techo de RAM | Falta la cifra pública (avisos de memoria de iOS/Android) que ya existe para el resto de límites de plataforma |

### J · Carga y arranque

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 81 | De qué está hecho el tiempo de carga y cómo medirlo | ✅ Cubierto | `05 - Referencia/02 - Publicar y exportar.md` §4.5 «Presupuesto de build: tamaño y arranque» | — |
| 82 | Carga asíncrona real con `texturegroup_get_status`/`texturegroup_status_fetched` | ✅ Cubierto | `04 - Recetas por género/41 - Transiciones, carga y pausa.md` §3.3 «La pantalla de carga real» | — |
| 83 | `sprite_add()` en runtime: coste y restricciones (iOS, HTML5/CORS) | 🟡 Parcial | `04 - Recetas por género/43 - Modding y contenido externo.md` (mencionado en el contexto de mods, «coste de memoria real») | Falta enmarcarlo como tema de rendimiento (coste de decodificar una imagen en runtime vs empaquetada) fuera del contexto de modding |
| 84 | Pantalla de carga real (progreso que mide de verdad, no decorativo) | ✅ Cubierto | `04/41` §3.3, con el antipatrón explícito de «no uses un temporizador como fuente de verdad» | — |
| 85 | Coste de `room_goto()`: destruir instancias no persistentes, posible recarga de recursos | 🟡 Parcial | `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md` §«`room_goto()` no es instantáneo… y tiene una trampa» (cubre el retraso hasta fin de evento, no el coste de la transición en sí) | Falta decir qué se destruye/recrea realmente al cambiar de room y por qué eso puede doler con muchas instancias |
| 86 | Precalcular en Create/carga en vez de en el primer Step o en el Draw | ✅ Cubierto | `13 - Diseño y producción de videojuegos/07 - Generación procedural avanzada.md` §2.9 «Rendimiento: precalcula, no calcules en Draw» (citado también desde `13/23` §3.4) | — |

### K · Delta time y estabilidad

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 87 | `delta_time` y movimiento independiente del framerate | ✅ Cubierto | `01 - Fundamentos/06 - Eventos y ciclo del juego.md` §7 | — |
| 88 | Paso fijo vs paso variable: tabla de decisión | ✅ Cubierto | `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md` §3.9 | — |
| 89 | Acumulador de tiempo (patrón *Fix Your Timestep* de Glenn Fiedler), con techo contra la espiral de la muerte | ✅ Cubierto | `13/06` §3.9; `13/08` §1.3, con el techo `min(delta_time/1000000, 0.25)` | — |
| 90 | `game_set_speed()`/`game_get_speed()` frente a `room_speed` (deprecado) | ✅ Cubierto | `01/06` §7 | — |
| 91 | Vsync y control del método de temporización (`display_set_timing_method`) | 🔴 Falta | `python3 _indice/buscar.py display_set_timing_method` → existe, pero «explicada en la biblioteca» sale **vacío**: 0 documentos propios la usan o explican, solo el manual espejado y las notas de versión de terceros | Ninguna prosa propia explica vsync ni sus modos, pese a ser la función exacta para diagnosticar *frame pacing* |
| 92 | *Hitching*/tirones: causas generales (GC, carga de assets, vsync) más allá del caso móvil | 🟡 Parcial | `04/28` §6.3 cubre `display_set_sleep_margin` en móvil | Falta una sección que una las tres causas (GC, streaming de assets, vsync) como checklist único; hoy están dispersas y solo una (móvil) tiene nombre propio |
| 93 | Forzar el GC fuera del gameplay activo (ver también #61) | 🟡 Parcial | `01/15` §5 | Ver fila 61 |

### L · Plataformas

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 94 | Móvil: 30 vs 60 fps, batería y temperatura | ✅ Cubierto | `04/28` §6.1 | — |
| 95 | HTML5: límites de ejecución (sin Debug Overlay, GC del motor JS, sin `texturegroup_*` dinámicos) | ✅ Cubierto | `01/15` §4 y §5; `04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md` §3 | — |
| 96 | Consolas: honestidad sobre lo que no se puede documentar por NDA | ✅ Cubierto | `05/02` §3.8/§3.8bis | — |
| 97 | Steam Deck: recomendaciones de rendimiento específicas | 🟡 Parcial (menor) | `05/02` §3.6 (solo build target: Linux nativo vs Windows+Proton, sin resolución/fps recomendados) | Se resuelve trasladando el criterio 30/60 fps de `04/28` §6.1; no merece documento propio |
| 98 | YYC (VM vs nativo) en cada plataforma de exportación | ✅ Cubierto | `04/28` §6.4; `13/10` §6.4; `01/15` §6 «Paso 4» | — |

### M · Tamaño del build

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 99 | De qué está hecho el tamaño de un build (texturas, audio) | ✅ Cubierto | `05/02` §4.5.1 | — |
| 100 | Qué reduce el tamaño de verdad y qué no (mitos incluidos) | ✅ Cubierto | `05/02` §4.5.3, tabla explícita | — |
| 101 | Compresión de texturas GPU (ASTC/DDS vía `GM-GPUTextureCompression`) | ✅ Cubierto | `05/02` §4.5.3; `02 - Novedades 2026/06 - Gráficos - SVG, SDF, FX y superficies.md` §7 | — |
| 102 | Límites de tamaño por plataforma (iOS 4 GB, Android 500 MB / aviso a 200 MB) | ✅ Cubierto | `05/02` §4.5.4, con fuentes oficiales de Apple/Google citadas y fechadas | — |

### N · Herramientas externas

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 103 | RenderDoc (captura de frame GPU) | 🔴 Falta | `grep -rli renderdoc` en la biblioteca propia → 0 resultados (solo aparece citado en el README de una librería de terceros descargada); WebSearch confirma que no hay integración oficial documentada de GameMaker con RenderDoc, a diferencia de Unity/Unreal | Ni una palabra sobre si RenderDoc puede engancharse a un build exportado de GameMaker (Windows OpenGL/DirectX) ni cómo, ni el aviso honesto de que no hay integración oficial |
| 104 | Instruments (macOS/iOS) para perfilar el binario exportado | 🔴 Falta | `grep` de «Instruments», «Time Profiler» → 0 resultados propios | El build de macOS/iOS es una app Xcode estándar: en teoría se puede abrir con Instruments como cualquier app nativa, pero no hay ni una línea que lo diga ni que avise de sus límites (símbolos, GML no mapea a un stack legible) |
| 105 | Android Profiler / `adb` para perfilar el build exportado | 🔴 Falta | `grep` de «Android Profiler», «adb.*profil» → 0 resultados propios | Mismo caso que Instruments, para Android Studio/`adb shell dumpsys` |

---

## Huecos por prioridad

### 🔴 Graves

1. **Herramientas externas de perfilado (RenderDoc, Instruments, Android Profiler)** — temas 103-105. Es el hueco que el propio brief pedía explícitamente cerrar con honestidad, y hoy no existe ni la versión «esto no se puede» ni la versión «esto sí, así». Un agente que necesite ir más allá del Debug Overlay no tiene ninguna guía y puede inventarse una integración que no existe.
2. **Sustituir instancias por partículas/asset layers/tiles cuando el elemento es solo visual o estático** — tema 45. Está citado por el propio blog oficial de GameMaker como el error de rendimiento más común, y esta biblioteca no lo menciona en ningún sitio.
3. **`display_set_timing_method` (vsync) sin una sola línea de prosa propia** — tema 91. La función existe, está verificada, y es la herramienta exacta para diagnosticar *frame pacing*; hoy solo vive en el manual espejado.
4. **Coste de crear `function()`/closures dentro de un bucle caliente** — tema 64. El principio ya existe para structs/arrays (`01/15` §6) pero no se extiende explícitamente a métodos, y es el mismo mecanismo de GC.
5. **Límites de memoria en HTML5** — tema 79. Ningún aviso del techo práctico de memoria en un build web, con el agravante de que ahí no hay excepción capturable: el navegador mata la pestaña.

### 🟠 Medios

6. **`ds_map`/`ds_list` vs `struct`/array — falta el benchmark ejecutado con cifras** — tema 57. Hay guía cualitativa y hasta el ejemplo de código para medirlo (`13/10` §6.2), pero nadie lo ha corrido y puesto en un documento, a diferencia del Data Locality de `13/23` §3.4.
7. **Presupuesto de memoria RAM real por plataforma (móvil, más allá de VRAM/disco)** — temas 78, 80. Dato público (avisos de memoria de iOS/Android), no bloqueado por NDA, y hoy falta.
8. **Overdraw como concepto de rendimiento 2D** — tema 14.
9. **Coste de `room_goto()` más allá de la trampa de timing** — tema 85.
10. **Funciones globales vs métodos de struct — coste de llamada** — tema 66.
11. **Eventos vacíos: ¿tienen coste?** — tema 48.

### 🟡 Menores

12. `static` como técnica explícita de memoización (tema 65).
13. Coste de CPU de buses/efectos de audio (tema 73).
14. Steam Deck: recomendaciones de rendimiento propias más allá del build target (tema 97).
15. Orden de dibujado `depth` vs capas: coste de reordenar (tema 15).
16. Forzar `gc_collect()` enganchado a la pantalla de carga real (temas 61, 93).
17. Aviso explícito de que un grupo de texturas cargado y nunca descargado se queda en VRAM (tema 77).
18. Herencia y coste de `event_inherited()` (tema 49) — bajo impacto real en GameMaker.
19. Coste de `sprite_add()` en runtime como tema de rendimiento, no solo de modding (tema 83).
20. Coste de compilación de shaders / posible *stutter* de primer uso (tema 25) — verificar primero si aplica de verdad al modelo de shaders de GameMaker antes de escribir nada.

---

## Encargo para el redactor

1. **Documento nuevo — `01 - Fundamentos/15 - Depuración y rendimiento.md` §10 (nueva) «Herramientas externas de perfilado»** *(o sección homóloga en `05 - Referencia/02 - Publicar y exportar.md`, para no duplicar con el checklist de release)*.
   Cierra los temas 103-105. Contenido: (a) **RenderDoc** — verificar primero por qué API gráfica exporta GameMaker en Windows por defecto (OpenGL o Direct3D, según runtime) antes de escribir nada sobre si RenderDoc puede engancharse; si no se puede confirmar con una fuente primaria, decirlo explícitamente en vez de inventar pasos. (b) **Instruments** — el build de macOS/iOS es una app Xcode estándar: se puede abrir con `Product → Profile`, pero el código GML no aparece en el stack (solo funciones del runtime C++); avisar de esa limitación. (c) **Android Profiler/`adb`** — mismo patrón: sirve para CPU/memoria/batería del proceso, no para inspeccionar GML. Ningún símbolo de GML nuevo que verificar aquí: es contexto de herramientas externas, no funciones del runtime.

2. **Sección nueva en `01 - Fundamentos/09 - Instancias, objetos y herencia.md` (tras §7 «Herencia de objetos») — «§8 · Cuándo NO usar una instancia»**
   Cierra el tema 45. Compara el coste de una instancia completa (eventos, colisión, `id`, memoria de sus variables) frente a: sistemas de partículas nativos (`part_system_create`, ya cubiertos en `04 - Recetas por género/39 - VFX - diseño y catálogo de efectos.md` — enlazar, no repetir) para efectos puramente visuales; *asset layers*/`layer_sprite_create` para decoración estática; tiles/tilemap para elementos repetitivos de nivel. Enlaza a `06/scr_pool.gml` para el caso en que sí hace falta instancia pero se puede reutilizar. Símbolos a verificar antes de citarlos: `part_system_create`, `layer_sprite_create`, `layer_background_create` (`buscar.py` sobre cada uno).

3. **Sección nueva en `01 - Fundamentos/06 - Eventos y ciclo del juego.md` §7 (ampliar) o subsección «§7 bis · Vsync y frame pacing»**
   Cierra el tema 91 y aporta al 92. Explica `display_set_timing_method(method)` y `display_get_timing_method()` (firmas ya verificadas), sus modos documentados en el manual (`09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Cameras_And_Display/display_set_timing_method.md` — traducir/resumir de ahí, no inventar), y cómo se relaciona con `display_set_sleep_margin()` (ya cubierta en `04/28` §6.3) para formar el cuadro completo de *frame pacing*. Cierra con un mini-checklist de causas de *hitching*: GC (`01/15` §5), carga de texturas (`04/41` §3.3) y vsync (esta sección).

4. **Ampliar `01 - Fundamentos/15 - Depuración y rendimiento.md` §6 «Paso 2: los sospechosos habituales»** con un nuevo sospechoso: **«Crear `function()` dentro del Step»**, con el mismo formato ❌/✅ que ya usa el documento para structs/arrays (líneas ya existentes en ese mismo paso). Un ejemplo de método creado cada frame para un callback vs uno creado una vez en el Create y reutilizado.

5. **Ejecutar y documentar el benchmark que falta: `ds_map` vs `struct`, `ds_list` vs `array`** — en `13 - Diseño y producción de videojuegos/23 - Catálogo de patrones en GML.md`, como continuación natural de §3.4 (Data Locality), o como nueva §3.4 bis. Usar el mismo método ya validado (`get_timer()`, calentamiento, YYC vía `gm-cli run --runtime native`, varias pasadas) sobre `ds_map_add`/`ds_map_find_value` frente a `struct[$ "clave"]`/acceso con punto, y `ds_list_add`/`ds_list_find_value` frente a `array_push`/acceso por índice. Publicar el factor medido, no una intuición. Símbolos a verificar: `ds_map_create`, `ds_map_add`, `ds_map_find_value`, `ds_list_create`, `ds_list_add`, `ds_list_find_value` (ya se sabe que existen, pero re-verificar firmas exactas antes de escribir el código).

6. **Sección nueva o ampliación en `04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md` §3** — «Memoria en HTML5: el techo real». Cierra el tema 79. Investigar (WebSearch/manual oficial) el límite práctico de heap de un build GameMaker HTML5 en los navegadores principales y qué pasa al superarlo (la pestaña se cierra, no hay excepción de GML capturable — confirmar esto último contra el manual antes de afirmarlo).

7. **Ampliación menor en `04 - Recetas por género/28 - Juegos para móvil (táctil).md` §6.3** — una fila más en la tabla «Lo demás que se paga caro»: el techo de RAM real antes de que iOS/Android maten el proceso por presión de memoria (dato público de Apple/Google, buscar la cifra o el criterio oficial vigente, no inventar un número).

8. **Tres retoques de una frase, sin documento nuevo** (agrúpense donde el redactor tenga hueco, no merecen sección propia):
   - `08 - Referencia GML completa/08 - Texturas y grupos de texturas.md` §«Texturas dinámicas y grupos»: una nota de aviso — «si nunca llamas a `texturegroup_unload()`, el grupo se queda en VRAM el resto de la partida» (tema 77).
   - `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md`, junto a la sección de `room_goto()`: qué se destruye realmente al cambiar de room (instancias no persistentes) y por qué eso puede doler con miles de instancias (tema 85).
   - `01 - Fundamentos/15 - Depuración y rendimiento.md` §5, en el ejemplo de `gc_collect()`: enlazar explícitamente a la pantalla de carga real de `04/41` §3.3 como el sitio natural para forzar la recogida (temas 61, 93).

---

## Lo que comprobé y NO hacía falta

- **Micro-optimización de aritmética dentro de bucles (sqrt vs distancia al cuadrado, tablas de
  lookup para trigonometría).** Parecía un hueco clásico de rendimiento, pero `13/08` §14 ya
  cierra la puerta explícitamente: «lo que no funciona: microoptimizar la aritmética dentro del
  bucle. Si el bucle se ejecuta 50 000 veces, el problema es el 50 000, no la multiplicación». Es
  una postura editorial deliberada, no un olvido — no reabrir.
- **Object Pool y Data Locality como patrones generales.** Están completos y medidos
  (`06/scr_pool.gml`, `13/23` §3.4); no confundir con el hueco real (tema 45), que es específico
  de *cuándo NO hace falta ni siquiera un objeto pooleado*.
- **Coste de las máscaras de colisión y particionado espacial.** Cubierto con tabla de coste
  relativo y benchmarks orientativos (`01/08` §4, `13/08` §4); no proponer nada nuevo aquí.
- **Medir en VM vs YYC / en el dispositivo real.** Repetido y consistente en tres documentos
  (`13/10` §6.4, `01/15` §6 Paso 4, `04/28` §6.4-6.5): ya no hace falta insistir más.
- **Pantalla de carga con progreso real vs decorativo.** `04/41` §3.3 ya evita explícitamente el
  antipatrón del temporizador como fuente de verdad; no es un hueco.
- **`gpu_set_blendenable`/`gpu_set_alphatestref`/`gpu_set_sprite_cull`.** Aparecían en la lista
  canónica del blog oficial como técnicas de rendimiento y estaban ya cubiertas en
  `08 - Referencia GML completa/04 - Color y blending.md` y `01/11` §11 — no duplicar.
- **Streaming de audio y límite de voces.** `01/13` §3 y §9 lo resuelven con cifras del manual
  (128 voces por defecto) y ejemplo de `audio_create_stream`; no es un hueco de rendimiento.
