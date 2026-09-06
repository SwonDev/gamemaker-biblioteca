# Auditoría r3 · Generación procedural y diseño de niveles

> 2026-09-06 · 83 temas evaluados · 66 cubiertos · 9 parciales · 8 faltan

## Resumen ejecutivo

Este dominio es, con diferencia, uno de los mejor tratados de toda la biblioteca. El documento
[`13 · 07 — Generación procedural avanzada`](<../../13 - Diseño y producción de videojuegos/07 - Generación procedural avanzada.md>)
(2431 líneas) y su hermano
[`04 · 05 — Roguelike y generación procedural`](<../../04 - Recetas por género/05 - Roguelike y generación procedural.md>)
(1400 líneas) cubren ruido, autómatas celulares, BSP, random walk, Poisson-disc, Wave Function
Collapse, gramáticas/L-systems, ensamblaje por piezas, niveles de plataformas por ritmo y
validación con código GML verificado y fuentes primarias citadas (Perlin SIGGRAPH 2002, Bridson
SIGGRAPH 2007, RogueBasin, Boris the Brave, Gillian Smith FDG 2009, Shaker/Togelius/Nelson). El
diseño de niveles a mano (`13 · 02`) y de mundo/exploración (`13 · 22`) están igual de completos,
con un sistema de grafo de bloqueos con validación BFS por habilidades que es, de hecho, mejor
que lo que documentan muchos libros de texto. El hueco que más duele es doble: **faltan por
completo dos algoritmos clásicos del canon de PCG citados explícitamente en el encargo — Voronoi
y marching squares** (ni una mención fuera de un efecto visual sin relación) —, y **no existe
ningún patrón para generar sin congelar el frame** (time-sliced generation con `time_source`):
todo el código asume que la generación entera cabe en un solo `Step`. El resto de huecos son
nichos reales pero menores: generación de ciudades/carreteras, poda de callejones sin salida, el
algoritmo clásico de laberinto por backtracking recursivo y el editor Ogmo.

## Tabla tema por tema

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | BSP (Binary Space Partitioning) | ✅ | `04·05` §4.2, §5.2 (`dungeon_generate_bsp` completo) | — |
| 2 | Autómatas celulares (cuevas) | ✅ | `13·07` §3 (regla RogueBasin R1≥5‖R2≤2, `cueva_celular`) | — |
| 3 | Drunkard walk / random walk | ✅ | `04·05` §4.2, §5.3 (`dungeon_generate_walk`) | — |
| 4 | Ruido value | ✅ | `13·07` §2.2 | — |
| 5 | Ruido Perlin | ✅ | `13·07` §2.3 (curva quíntica, cita Perlin SIGGRAPH 2002) | — |
| 6 | Ruido Simplex | ✅ | `13·07` §2.4 — decisión razonada de **no** implementarlo en 2D (coste vs beneficio, aviso de patentes), remite a `12·05` para implementaciones de terceros | — |
| 7 | fBm (octavas) y domain warping | ✅ | `13·07` §2.5, §2.6 | — |
| 8 | Diagramas de Voronoi | 🔴 | — | Ningún documento de diseño lo trata. Solo aparece `GMS-Voronoi-Pixels` (efecto visual) y `Fracture.ConvexVoronoi` (fractura física) en `11 - Código descargado`, sin relación con generación de niveles/biomas |
| 9 | Difusión / DLA (diffusion-limited aggregation) | 🔴 | — | No hay mención. Nicho pero real (cuevas ramificadas, vetas de mineral) |
| 10 | Generación basada en múltiples agentes | 🔴 | — | Solo existe el agente único del *drunkard walk* (`04·05` §5.3). Ningún ejemplo con varios excavadores cooperando |
| 11 | Grafos de mazmorra / lock-and-key | ✅ | `13·22` §3.1-3.2 (grafo con aristas `requiere`, BFS por habilidades, `mundo_grafo_validar_progresion` detecta soft-locks) | Está resuelto a escala de **mundo/zonas**, no de una mazmorra interna con llaves anidadas (pequeña/grande al estilo Zelda); el patrón es el mismo pero no hay un ejemplo a esa escala |
| 12 | Wave Function Collapse | ✅ | `13·07` §5 (modelo *simple tiled* completo, cita Gumin/Boris the Brave) | — |
| 13 | Gramáticas de forma / L-systems | ✅ | `13·07` §6.1 (cita Prusinkiewicz & Lindenmayer) | — |
| 14 | Gramáticas de misión | ✅ | `13·07` §6.2 | — |
| 15 | Cadenas de Markov (nombres) | ✅ | `13·07` §6.3 | — |
| 16 | Poisson disk sampling | ✅ | `13·07` §4 (Bridson SIGGRAPH 2007, fórmula correcta del anillo `r·√(1+3u)`) | — |
| 17 | Marching squares | 🔴 | — | Cero menciones (`buscar.py --todo` sin resultados). Los *metaballs* de `13·08` §12 usan recorte de alfa por sprite, no extracción de isolíneas |
| 18 | Salas prefabricadas vs generadas | ✅ | `13·07` §7 (Spelunky/Isaac, piezas con puertas etiquetadas) | — |
| 19 | Pasillos y conectividad | ✅ | `04·05` §5.2 (corredores en L), `13·07` §3.1 (`conservar_region_mayor`) | — |
| 20 | Cerraduras y llaves (mecánica) | ✅ | `13·02` §1.4 (duro/blando/de conocimiento), `04·06` §5.5-5.6 | — |
| 21 | Lock-and-key con grafos (validación) | ✅ | `13·22` §3.1-3.2 | Ver ítem 11 |
| 22 | Backtracking (algoritmo de laberinto perfecto) | 🟡 | `13·07` §5.1 solo menciona el backtracking de WFC (que se evita a propósito) | Falta el algoritmo clásico *recursive backtracker* para laberintos sin bucles (DFS que excava y retrocede). BSP+corredores cubre un caso distinto (salas, no laberinto puro) |
| 23 | Salas especiales (jefe, tesoro, tienda) | 🟡 | `13·07` §7.2 (pieza `sala_tesoro` de ejemplo), `04·05` §5.9 (escaleras en la celda más lejana) | No hay un algoritmo dedicado que asigne roles de sala por distancia/rol (p. ej. "la sala más lejana del grafo es la del jefe") |
| 24 | Dificultad progresiva por profundidad | ✅ | `04·05` §5.9 (`poblar_piso`: enemigos y cofres escalan con `piso`) | — |
| 25 | Poda de callejones sin salida | 🔴 | — | No hay técnica de detección/eliminación (o conversión a secreto) de callejones sin salida tras generar |
| 26 | Validación: ¿es jugable? | ✅ | `13·07` §10 (`nivel_aceptable` con umbrales explícitos) | — |
| 27 | Alcanzabilidad (BFS) | ✅ | `13·07` §10 (`distancias_bfs`), `13·22` §3.2 (`mundo_zonas_distancias`) | — |
| 28 | Flood fill | ✅ | `04·05` §5.4 (`dungeon_flood_fill`, `dungeon_es_valida`) | — |
| 29 | Garantía de solución (generar-validar-reintentar) | ✅ | `13·07` §1.2, `04·05` §5.4 (`dungeon_generate_valid`), `13·07` §10 (`generar_hasta_valido`) | — |
| 30 | Reintentos con tope | ✅ | `04·05` §5.4 (tope 30), `13·07` §1.2 y checklist §12 | — |
| 31 | Presupuesto de TIEMPO (no solo de intentos) | 🟡 | — | Todos los topes son de número de intentos; ninguno usa `get_timer()` para cortar la generación tras N milisegundos reales |
| 32 | Biomas por umbral (altura+humedad) | ✅ | `13·07` §2.7 (diagrama de Whittaker vía Red Blob Games, `bioma_por_umbral`) | — |
| 33 | Mapas de altura (heightmap) | ✅ | `13·07` §2.7 (`generar_mapa_biomas`, campo `alturas`) | — |
| 34 | Ríos | 🟡 | `13·07` §6.1, fila de tabla: *"Árbol binario… Ramas, raíces, **ríos**"* | Solo una mención de una fila de tabla reutilizando el L-system genérico de ramas; no hay un método dedicado (p. ej. acumulación de flujo sobre el heightmap ya generado en §2.7) |
| 35 | Cuevas | ✅ | `13·07` §3 | — |
| 36 | Islas | ✅ | `13·07` §2.7 (`forma_isla`, *"square bump"* de Red Blob Games) | — |
| 37 | Continentes múltiples | 🟡 | `13·07` §2.7 (`isla = 0` → "continente infinito", como opuesto binario a isla única) | No hay técnica para varios continentes separados por agua en el mismo mapa (necesitaría Voronoi o una segunda capa de umbral a mayor escala — ligado al hueco 8) |
| 38 | Ciudades y carreteras | 🔴 | `13·07` §6.1, fila de tabla: *"L-systems… calles"* | Ninguna implementación: ni trazado de manzanas, ni red de calles, ni el ejemplo L-system genérico se aplica a una cuadrícula urbana |
| 39 | Vegetación (distribución + forma) | ✅ | `13·07` §4 (Poisson-disc por bioma) + §6.1 (L-system arbusto/árbol) | — |
| 40 | Distribución de recursos | ✅ | `13·07` §4 (ejemplo completo pintando por bioma) | — |
| 41 | Chunking de mundos grandes | ✅ | `04·09` §4.6, §5.4 (`CHUNK_TILES`, `RADIO_CARGA`, semilla+diff) | — |
| 42 | Streaming (carga/descarga por proximidad) | ✅ | `04·09` §5.4 (radio de carga, `instance_deactivate_region`/`instance_activate_region` vía chunk_get) | — |
| 43 | Niveles de plataformas por ritmo | ✅ | `13·07` §8 (cita Gillian Smith FDG 2009, dos capas ritmo→geometría, `mejor_nivel` sobre 1000 candidatos) | — |
| 44 | Segmentos/piezas de plataforma | ✅ | `13·07` §8 (`ritmo_a_geometria`) | — |
| 45 | Generación por chunks / scroll infinito (runner) | 🟡 | `04·09` §4.6/§5.4 (chunking genérico) + `13·07` §8 (ritmo) existen por separado | Ningún ejemplo combina ambos para un *endless runner* (streaming de tramos de plataforma solo hacia delante, descarte hacia atrás) |
| 46 | Dificultad adaptativa en plataformas (tiempo real) | 🟡 | `13·07` §8 (`mejor_nivel` filtra contra una dificultad OBJETIVO fija) | No ajusta la dificultad EN VIVO según el rendimiento del jugador; la DDA está tratada en abstracto en `13·01` §3.3 pero no conectada al generador |
| 47 | Semillas (`randomize`, `random_get_seed`) | ✅ | `13·07` §1.1, `04·05` §4.1 | — |
| 48 | `random_set_seed` y `fix_range_bug` | ✅ | `13·07` §1.1 (cita textual del manual LTS 2026 sobre el bug de rango heredado) | — |
| 49 | Generadores propios (RNG independiente del global) | ✅ | `04·05` §5.0 (LCG con justificación de precisión de `double`) | — |
| 50 | Reproducibilidad entre plataformas | ✅ | `13·07` §1.1 (cita: *"results may vary between platforms"*) | — |
| 51 | Guardar la semilla, no el mapa | ✅ | `04·05` §6 (`save_run`/`load_run`), `13·07` checklist §12 | — |
| 52 | `random` vs `irandom` vs `choose` | ✅ | Símbolos verificados (`buscar.py`); usados en contexto en `04·05` §5.0 y `13·07` | No hay un documento de Fundamentos dedicado solo a explicarlos de forma aislada (están dispersos en `01 - Fundamentos`, sin sección propia) — no bloquea, el uso correcto ya está mostrado |
| 53 | Secuencias independientes (RNG por sistema) | ✅ | `04·05` §4.1 regla 2, `13·07` §1.1 | — |
| 54 | Ritmo y *pacing* | ✅ | `13·02` §1.2 (gráfico de intensidad, *Level Design Book*) | — |
| 55 | Introducción de mecánicas (kishōtenketsu) | ✅ | `13·02` §1.1 (los cuatro momentos) | — |
| 56 | Curva de dificultad | ✅ | `13·01` §3, `13·02` §1.1 | — |
| 57 | Secuencia de aprendizaje | ✅ | `13·02` §1.1 | — |
| 58 | Señalización y *affordances* | ✅ | `13·02` §1.3 (landmark, weenie, líneas de guía, contraste, silueta; cita Kevin Lynch) | — |
| 59 | Líneas de visión / composición para enseñar el espacio | ✅ | `13·22` §2.3, §3.5 (cámara con atractores/detractores) — terminología distinta ("señalizar a distancia") pero mismo concepto | — |
| 60 | Composición del espacio | ✅ | `13·02` §2.6 (tipos de estructura) | — |
| 61 | Puntos de referencia (*landmarks*) | ✅ | `13·02` §1.3, `13·22` §2.3 | — |
| 62 | Rutas alternativas | ✅ | `13·02` §1.5 | — |
| 63 | Secretos | ✅ | `13·02` §1.5 (tres capas de secretos) | — |
| 64 | Checkpoints | ✅ | `13·02` §1.6, §3.8 (código completo con `orden` creciente) | — |
| 65 | Backtracking (mundo, atajos) | ✅ | `13·02` §1.5, `13·22` (grafo con ciclos deliberados) | — |
| 66 | Metroidvania y control de progreso | ✅ | `04·06` completo, `13·22` §1.5, §3.1-3.2 | — |
| 67 | *Gating* (llaves, cerraduras, puertas blandas) | ✅ | `13·02` §1.4 | — |
| 68 | Rooms de GameMaker | ✅ | `13·02` §3.1 (Room Editor: rejilla, guías, orden de creación) | — |
| 69 | Capas / instance layers | ✅ | `13·02` §3.1 (capas mínimas de un nivel), `01·10` §3 | — |
| 70 | Tilemaps (tile set, autotiles, colisión) | ✅ | `13·02` §3.3-3.4 | — |
| 71 | Editor externo: Tiled | ✅ | `07·09` §4 (plugin nativo de exportación a `.yy`, flujo paso a paso) + `12·05` §2 (GMTiled, ⚠️ sin repo mantenido en 2026) | — |
| 72 | Editor externo: LDtk | ✅ | `12·05` §2 (`LDtkParser` ★63 MIT, `LDtk to GMS`) | — |
| 73 | Editor externo: Ogmo | 🔴 | — | Cero menciones en todo el repositorio |
| 74 | Editor de niveles in-game | ✅ | `13·02` §3.10 (30 líneas, F2/F5/F9) | — |
| 75 | `room_instance_add` y sus trampas | ✅ | `13·07` §7.1 (cita textual: corrompe el asset permanentemente) | — |
| 76 | Room como nivel vs nivel como datos | ✅ | `13·02` §3.9 (tabla comparativa, cargador JSON completo, `room_get_info()`) | — |
| 77 | Generación en tiempo de carga vs precalculada | 🟡 | `13·02` §3.9 (comparación editor-time vs datos) | No se discute explícitamente "generar en el Room Start" vs "generar offline una vez y distribuir el resultado como asset" (relevante para juegos con niveles fijos pero generados una sola vez en desarrollo) |
| 78 | Generar sin congelar el juego (time-slicing) | 🔴 | `13·07` §13 solo indica el síntoma ("WFC sobre rejilla grande → congelación") y remite a "trocear la rejilla" sin código | No hay ningún patrón con `time_source_create`/`call_later`/alarm que reparta N pasos de un autómata celular o WFC entre varios `Step` para no bloquear el frame |
| 79 | Streaming/culling conectado a generación procedural | 🟡 | Culling general en `01·10`/`01·11`; chunking en `04·09` | Ninguno conecta explícitamente "no dibujes/actualices lo que el streaming aún no cargó" como una única técnica |
| 80 | Precalcular en Create, no en Draw | ✅ | `13·07` §2.9 (tabla de costes: Draw vs Create vs tilemap) | — |
| 81 | Plantillas y salas curadas (híbrido) | ✅ | `13·07` §1.5, §7 (Spelunky/Isaac) | — |
| 82 | Generación con restricciones de diseño | ✅ | `13·07` §1.4 (*possibility space*, tabla de 4 técnicas de acotación) | — |
| 83 | GMRoomLoader (rooms como prefabs en runtime) | ✅ | `12·05` §2, `13·07` §7.1 | — |

## Huecos por prioridad

### 🔴 Graves

1. **Diagramas de Voronoi** (#8) — algoritmo canónico de PCG citado explícitamente en el encargo, cero cobertura como técnica de generación (biomas por territorio, formas de sala orgánicas, partición de regiones). Solo aparece como efecto visual sin relación (`GMS-Voronoi-Pixels`) o como patrón de fractura física (`Fracture.ConvexVoronoi`).
2. **Marching squares** (#17) — mismo caso: cero cobertura. Es la técnica estándar para extraer contornos suaves de un campo escalar (paredes de cueva redondeadas, siluetas de metaballs, isolíneas de un heightmap), y el documento de físicas ya trata *metaballs* con una técnica alternativa (recorte de alfa) sin mencionar esta.
3. **Generación sin congelar el frame** (#78) — el propio documento `13·07` reconoce el síntoma ("segundos de congelación") en su tabla de errores clásicos pero no da ninguna solución en código. Todo el corpus de generación (autómatas, WFC, BSP) asume que cabe entero en un `Step`. Es el hueco con más impacto práctico: cualquier generador que crezca (mapas grandes, WFC con más tiles) golpea este límite y hoy no hay ninguna plantilla `time_source`/`call_later` que resolverlo.
4. **Ciudades y carreteras** (#38) — pedido explícitamente en el encargo; solo existe como una palabra suelta en una fila de tabla del documento de L-systems, sin ejemplo de trazado de calles ni de manzanas.
5. **Poda de callejones sin salida** (#25) — pedido explícitamente; ninguna técnica de detección/eliminación tras generar.
6. **Editor Ogmo** (#73) — pedido explícitamente en el encargo; cero menciones en el repositorio.
7. **Difusión / DLA** y **generación multi-agente** (#9, #10) — nicho, pero pedidos explícitamente y con cero cobertura (aunque el `drunkard walk` de un solo agente ya cubre el caso más simple).

### 🟠 Medios

- **Backtracking recursivo para laberintos** (#22) — el algoritmo clásico de laberinto perfecto (DFS que excava y retrocede) no está, aunque BSP+corredores resuelve un problema adyacente.
- **Salas especiales por rol** (#23) — falta un algoritmo explícito (más allá del ejemplo suelto de "sala_tesoro" y "escaleras en la celda más lejana") para asignar sistemáticamente jefe/tesoro/tienda por posición en el grafo.
- **Continentes múltiples** (#37) — solo se cubre el caso de una isla única o un continente infinito; ligado al hueco de Voronoi.
- **Ríos** (#34) — mencionados una vez en una tabla, sin método propio (podría resolverse con acumulación de flujo sobre el heightmap que `13·07` §2.7 ya genera).
- **Generación por chunks para runners/scroll infinito** (#45) — el chunking genérico y el generador de ritmo existen por separado pero nunca se combinan en un ejemplo.

### 🟡 Menores

- **Presupuesto de tiempo real en reintentos** (#31) — todos los topes son de número de intentos, ninguno usa `get_timer()`.
- **Dificultad adaptativa en tiempo real para plataformas** (#46) — existe selección contra un objetivo fijo, no ajuste dinámico por rendimiento del jugador.
- **Generación en carga vs precalculada como decisión explícita** (#77) — se puede inferir de la comparación existente, pero no está nombrada como tal.
- **Streaming conectado a culling** (#79) — ambos existen por separado, sin un puente explícito.
- **Lock-and-key a escala de mazmorra interna** (#11/#21) — el patrón de grafo+BFS ya existe a escala de mundo; falta solo el ejemplo a escala de una mazmorra con llave pequeña/grande.

## Encargo para el redactor

1. **Nueva subsección "3 bis · Voronoi: regiones y formas orgánicas"** en
   [`13 · 07 — Generación procedural avanzada`](<../../13 - Diseño y producción de videojuegos/07 - Generación procedural avanzada.md>),
   justo después de §3 (autómatas celulares). Contenido: diagrama de Voronoi por
   fuerza bruta (para rejillas pequeñas/medianas, sin necesitar el algoritmo de Fortune) —
   sembrar N puntos con `muestreo_poisson()` (ya existente en §4, para que las celdas no
   degeneren) y, por cada celda de la rejilla, encontrar el punto semilla más cercano con
   `point_distance()` (verificado) recorriendo el array de semillas; el índice de la semilla
   más cercana es el id de región. Aplicaciones a enlazar: biomas por territorio (en vez de por
   umbral de ruido), formas de sala orgánicas para mazmorras, y continentes múltiples (huecos
   #8 y #37 se resuelven con la misma técnica). Símbolos verificados:
   `point_distance`, `array_create`, `array_length`, ya usados en el resto del documento.
   Advertir del coste `O(celdas · semillas)` y cuándo trocear (mismo patrón que WFC en §13).

2. **Nueva subsección "3 ter · Marching squares: contornos suaves"** en el mismo documento,
   después de la anterior. Contenido: extracción de isolíneas de un campo binario o escalar
   (útil sobre el resultado de `cueva_celular()` de §3, o sobre un campo de metaballs) usando
   la tabla de 16 configuraciones estándar y dibujando con `draw_primitive_begin(pr_linelist)` /
   `draw_vertex()` / `draw_primitive_end()` (verificados con `buscar.py`). Enlazar desde
   [`13 · 08 §12 — Metaballs`](<../../13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md>)
   como alternativa de mayor calidad visual al recorte de alfa ya documentado allí, sin
   duplicar ese contenido.

3. **Nueva subsección "14 · Generar sin congelar el frame"** en `13·07`, después del checklist
   (§12) y antes de "Ver también". Contenido: patrón de generación **por pasos** usando
   `time_source_create(time_source_global, 1, tu_units_frames, callback, [], -1)` (firma
   verificada) o `call_later()` (verificado) para ejecutar, por ejemplo, UNA pasada de
   `cueva_celular()` o UNA celda de colapso de `ColapsoOndas` por frame en vez de la rejilla
   entera de golpe; combinar con un presupuesto de tiempo real por frame usando `get_timer()`
   (ya usado en el documento) para procesar "tantos pasos como quepan en 2 ms" y ceder el resto
   al siguiente frame. Esto resuelve a la vez el hueco #78 (grave) y el #31 (presupuesto de
   tiempo, menor). Actualizar la fila correspondiente de la tabla de errores clásicos (§13,
   "WFC sobre una rejilla grande") para enlazar aquí en vez de decir solo "trocear la rejilla".

4. **Nueva subsección en `13 · 22 — Diseño de mundo y exploración`**, tras §3.3 (distribuir
   POIs): **"3 bis · Ciudades y redes de calles"**. Contenido mínimo: generación de una
   cuadrícula de manzanas con calles principales (L-system aplicado a una retícula, reutilizando
   `expandir_lsistema()`/`dibujar_lsistema()` de `13·07` §6.1 con reglas de ramificación
   ortogonal) o, más simple y más fiable en GML, un algoritmo de subdivisión recursiva de
   manzanas al estilo BSP (reutilizando `BSPNode` de `04·05` §5.2) con calles en los cortes.
   Enlazar, no repetir, el código de `dungeon_generate_bsp()` y `expandir_lsistema()`.

5. **Nueva subsección "6 bis · Ríos por acumulación de flujo"** en `13·07`, tras §6.1
   (L-systems). Contenido: sobre el heightmap ya generado por `generar_mapa_biomas()` (§2.7),
   calcular la dirección de descenso más pronunciada por celda y trazar el río siguiendo ese
   descenso desde puntos de partida en zonas altas hasta el nivel del mar (`Bioma.Agua`);
   alternativa mucho más simple que un L-system genérico y reutiliza datos que el documento ya
   produce. No inventar funciones nuevas: todo el cálculo es aritmética sobre el array
   `alturas` ya existente.

6. **Nueva subsección "3 quater · Poda de callejones sin salida"** en `13·07`, tras la sección
   de autómatas (§3) o de validación (§10). Contenido: tras generar y conectar regiones,
   recorrer la rejilla contando vecinos de suelo por celda (reutilizar el patrón de
   `vecinos_opacos`/`contar_muros` ya escrito); una celda de suelo con exactamente 1 vecino de
   suelo es un callejón sin salida. Dos usos: **rellenarlo** (convertirlo en muro, iterando
   hasta que no queden, como una erosión) para mazmorras más directas, o **marcarlo** como
   candidato a sala secreta (enlazar con `13·02` §1.5, "secretos en tres capas") en vez de
   rellenarlo. Símbolos: los mismos arrays planos ya usados en el documento.

7. **Algoritmo de laberinto por backtracking recursivo**, como variante adicional en la tabla
   de "Algoritmos, de menor a mayor complejidad" de `04·05` §4.2, con su propia subsección de
   código en §5 (posición sugerida: nueva §5.3 bis, entre random walk y flood fill). Contenido:
   el DFS clásico sobre una rejilla de celdas impares (excavar, marcar visitado, retroceder
   cuando no hay vecino sin visitar) — genera un **laberinto perfecto** (árbol sin ciclos, una
   única ruta entre dos puntos cualesquiera), a diferencia de BSP (salas) y random walk
   (orgánico). Reutilizar el struct `RNG` de §5.0 (`shuffle`) para barajar el orden de vecinos.

8. **Ampliar `12 · 05 §2`** con una fila para **Ogmo Editor**: investigar primero (WebSearch,
   no inventar) si existe algún importador mantenido en 2026 de mapas `.ogmo`/`.json` de Ogmo
   Editor a GameMaker; si no lo hay, decirlo explícitamente igual que ya se hace con GMTiled
   ("⚠️ no se ha encontrado un repositorio mantenido"), en vez de omitir el editor por completo.
   Esto cierra el hueco #73 sin inventar nada.

9. **Nueva subsección breve "8 bis · Chunks de plataforma para scroll infinito"** en `13·07`,
   tras §8 (ritmo). Contenido: combinar `generar_ritmo()`/`ritmo_a_geometria()` (ya escritas)
   con el patrón de chunking de `04·09` §5.4 (adaptado a 1D: solo genera hacia delante, descarta
   instancias que salen por detrás de la cámara con `instance_destroy()`), en vez de dejar que
   el lector deduzca la combinación por su cuenta. Enlazar ambas fuentes, no reescribirlas.

10. **Nota breve (2-3 frases, no una sección nueva)** en `13·07` §7 (ensamblaje por piezas) o en
    `04·06` (Metroidvania) sobre **asignación de roles de sala por distancia en el grafo**
    (hueco #23): la sala más lejana del inicio en el BFS de `distancias_bfs()` (§10) es una
    candidata natural a sala de jefe; las salas con solo una puerta (calculable con el mismo
    conteo de vecinos del hueco #25) son candidatas a tesoro/secreto. Es una observación sobre
    código ya existente, no requiere símbolos nuevos.

## Lo que comprobé y NO hacía falta

- **Simplex noise sin implementación** — no es un hueco: `13·07` §2.4 explica por qué
  deliberadamente no se reimplementa en 2D (coste no justificado, aviso de patentes en
  dimensiones ≥3) y remite a implementaciones de terceros catalogadas en `12·05`. Es una
  decisión editorial razonada, no una omisión.
- **`random` vs `irandom` vs `choose` como documento propio en Fundamentos** — parecía un hueco
  porque `01 - Fundamentos/` no tiene una sección dedicada solo al RNG básico (son menciones
  incidentales en otros documentos), pero el uso correcto, con semilla y determinismo, SÍ está
  completamente explicado donde importa: `04·05` §4.1 y §5.0. No hace falta un documento nuevo
  solo para explicar tres funciones ya usadas correctamente en cinco sitios distintos.
  Comprobado: `random_set_seed`, `random_get_seed`, `randomize`, `irandom`, `irandom_range`,
  `choose` — los seis existen y están citados con firma exacta.
- **Tiled y LDtk** — parecía un hueco potencial (el encargo los pedía explícitamente) pero están
  cubiertos con detalle real: Tiled tiene un flujo completo con plugin nativo de exportación en
  `07·09` §4, y LDtk con dos importadores catalogados en `12·05` §2 (`LDtkParser`, MIT, ★63).
  Solo Ogmo falta de verdad (ver encargo #8).
- **Grafo de mazmorra con llaves** — parecía un hueco (el encargo lo pedía como tema de
  mazmorras) pero el mecanismo — grafo con aristas que exigen una habilidad/ítem, validado con
  BFS y detección de soft-locks — ya existe completo en `13·22` §3.1-3.2. Solo falta el ejemplo
  a escala más pequeña (una mazmorra, no un mundo), que es la misma técnica.
- **`room_instance_add` y generación por piezas con rooms** — parecía razonable esperar un
  patrón de generación procedural usando rooms nativas de GameMaker, pero `13·07` §7.1 explica
  con cita textual del manual por qué es una trampa (corrompe el asset permanentemente) y
  recomienda con razón datos JSON + `GMRoomLoader` en su lugar. No es un hueco: es una decisión
  técnica ya justificada.
- **Rendimiento de ruido (precalcular vs Draw)** — completamente cubierto con una tabla de
  costes medidos (`13·07` §2.9), incluida la trampa de reconstruir `RuidoPerlin` dentro de un
  bucle y la de `array_create` anidado compartiendo referencia.
- **Metaballs** — existen y están bien documentados (`13·08` §12), aunque con una técnica
  distinta a marching squares (recorte de alfa por sprite); no es un hueco de metaballs, es un
  hueco de la técnica alternativa de marching squares (ver encargo #2).
