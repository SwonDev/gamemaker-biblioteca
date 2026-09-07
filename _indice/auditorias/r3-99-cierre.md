# Auditoría de cierre — tercera ronda (segunda pasada, 2026-09-07)

> Rol: auditor de cierre. No redacto, verifico con evidencia. Once encargos se dieron por
> cerrados en esta sesión (siete documentos nuevos, once ampliaciones grandes, dos herramientas).
> Este informe comprueba cada uno contra el disco, ejecuta las herramientas de verificación y lee
> el código real donde un documento nuevo reutiliza una estructura de otro — que es donde la
> ronda anterior encontró sus fallos más caros.

**Aviso de concurrencia.** Durante esta auditoría había al menos otro agente escribiendo en vivo
sobre `_indice/PENDIENTE-r3.md`, `_indice/validar-codigo-gml.py`, `_indice/validar-compilacion-docs.py`
y el espejo del manual (`09 - Manual oficial/`) — confirmado con `ps aux` (procesos
`validar-compilacion-docs.py` y un bucle sobre `verificar-espejo.py --resumen` corriendo a la vez
que esta sesión). Esas tres áreas se marcan **en curso**, no como defecto, tal y como pedía el
encargo. Todo lo demás en este informe es una fotografía verificada en el momento de escribirlo.

---

## 1 · Encargo → estado real

| # | Encargo | Estado | Evidencia |
|---|---|---|---|
| 1 | `04/46` — Eje Z falso | ✅ Cerrado | 595 líneas, 9 secciones, 14 bloques `gml`. Enlazado en `04/_INDICE-RECETAS.md:80`. Compila (ver §4). |
| 2 | `04/47` — Beat 'em up y brawler | ✅ Cerrado | 854 líneas, 14 secciones, 30 bloques `gml`. Reutiliza `GestorFichas` de `04/33` correctamente (§3.1). Enlazado en el índice (línea 81). |
| 3 | `04/48` — Aventura gráfica | ✅ Cerrado | 1420 líneas, 35 bloques `gml`. Enlazado (línea 82). |
| 4 | `04/49` — Deportes y física de mesa | ✅ Cerrado | 1831 líneas, 63 bloques `gml`. Reutiliza `GestorFichas` (§A.5.4) y `Arrive`/`llegar_a()` de `04/23` (§A.5.2) con firmas correctas. Enlazado (línea 83). |
| 5 | `04/50` — Juego de lucha | ✅ Cerrado | 1526 líneas, 37 bloques `gml`. Reutiliza `RecursoCombate` de `04/36` (§3.6.4, §3.7) con firma correcta. Enlazado (línea 84). |
| 6 | `04/51` — Colonia y constructor de bases | ⚠️ Cerrado con defectos | 1795 líneas, 27 bloques `gml`. Reutiliza `Needs()`, el patrón BFS del *flood fill* y `WorldGrid`/`objWorldGrid` de `04/09`. **Dos bugs reales encontrados, ver §3.1 y §3.2.** Enlazado (línea 85). |
| 7 | `04/52` — Live-ops técnico | ✅ Cerrado | 497 líneas, 7 secciones, 14 bloques `gml`. Enlazado (línea 86) y enlazado *hacia* desde `13/20` (línea 332-337, distinción servicio-en-vivo-completo vs. pieza técnica). |
| 8 | `05/05` — Entregar el juego | ✅ Cerrado | 875 líneas, 12 secciones. Cubre los seis puntos exactos que pedía `r3-ENCARGOS-CONFLUENTES.md` §1: `steamcmd` (9 menciones), `notarytool`/`codesign`/`stapler` (8/8/3), `SmartScreen` (13), `butler` (4, enlaza a `07` sin repetir), App Bundle/Play (22), TestFlight (3). No existía índice propio en `05 -Referencia/`; está en `_indice/MAPA.json:700-701` y en `_indice/skills/.../indice-documentos.md:195`. **No está en el README raíz** — ver §3.3. |
| 9 | `07/23` — Arte generado por IA | ✅ Cerrado | 242 líneas, 9 secciones. Enlazado en `07/_INDICE-ECOSISTEMA.md:33`. |
| 10 | `13/25` — Legal de terceros | ✅ Cerrado | 283 líneas, 10 secciones, con casos verificados y fecha (Nintendo, Take-Two/OpenIV, Sega). Enlazado en `13/_INDICE-DISENO.md:42` y enlazado *desde* `13/26` y `13/11`. **No enlazado desde `13/20`**, el destino que pedía el encargo confluente — ver §3.4. |
| 11 | `13/26` — Comunidad propia | ✅ Cerrado | 591 líneas, 7 secciones, con casos verificados (No Man's Sky, Digital Homicide). Enlazado en el índice (línea 43). |
| 12 | `13/07` — ampliar procedural (marching squares, arena granular) | ✅ Cerrado | +1193/-líneas. `## 3 ter · Marching squares` (línea 958) con fuente citada (Jamie Wong, 2014) y remisión cruzada a `13/08` §12 (metaballs). Arena granular: buscar confirmado en el documento. |
| 13 | `13/22` — ampliar diseño de mundo (ciudades) | ✅ Cerrado | +249 líneas. `### 3.3 bis · Ciudades y redes de calles` (línea 564) con dos patrones (rejilla, orgánico) y fuente citada. |
| 14 | `01/12` — ampliar input | ✅ Cerrado | +305 líneas. |
| 15 | `13/05` — ampliar UI y UX | ✅ Cerrado | +218 líneas. Cierra dos huecos explícitos: mnemónicos en menús con pestañas y un campo de texto genérico que unifica `04/11` (altas de highscore) y `08/12` (`clipboard_get_text`) — con la advertencia explícita de «no repetir, reutilizar» (línea ~1030 y siguientes). |
| 16 | `13/01` — ampliar diseño de juego | ✅ Cerrado | +447 líneas. Corrige la cita rota a `01/15` sobre el *profiler* (línea 12-13, ver §5). |
| 17 | `04/45` — ampliar géneros sin receta (granja) | ✅ Cerrado | +254 líneas. `Animal()` compone `Needs()` de `04/09` correctamente, con nota explícita de por qué NO llama a `needs.update()` (degradación diaria, no por fotograma) — línea 635. |
| 18 | `04/09` — ampliar survival/crafting | ⚠️ Cerrado con defecto | +462 líneas. Corrige los dos defectos verificados de la ronda anterior (`celda_construible`/`punto_en_rango` inventadas, ausencia de rejilla de ocupación) sustituyéndolos por `WorldGrid`/`objWorldGrid` y `point_distance()` — **pero introduce un defecto nuevo, ver §3.1**. |
| 19 | `01/14` y `01/15` — persistencia y depuración | ✅ Cerrado | +141 y +449 líneas. `01/15` añade RenderDoc (21 menciones), Instruments (12) y Android Profiler (8) — exactamente lo que pedía `r3-ENCARGOS-CONFLUENTES.md` §2. |
| 20 | `06/scr_save_load.gml` | ✅ Cerrado | +259/-líneas. |
| 21 | `04/14` — ampliar multijugador | ✅ Cerrado | +72 líneas. |
| 22 | `04/21` y `07/18` — localización (RTL/CJK vía Scribble) | ✅ Cerrado | +181 y +96 líneas. Ambos mencionan RTL y CJK/chino/japonés/coreano varias veces. |
| 23 | `13/12` — ampliar narrativa | ✅ Cerrado | +225 líneas. |
| 24 | `08/22` — Spine | ✅ Cerrado | +99 líneas. Corrige el defecto verificado de la ronda anterior: el comentario de la línea 33 ahora dice explícitamente que `skeleton_animation_set()` no tiene parámetro de *track* (siempre usa el 0) y que el bucle es el segundo argumento — contradiciendo (correctamente) el «en bucle» erróneo de antes. Ver §5. |
| 25 | `13/10` — Testing y QA | ✅ Cerrado | +518 líneas. `replay_verificar()` (línea 2186) **ahora sí compara el hash** contra `_replay.hash` antes de re-simular — corrige el defecto grave nº 2 de la ronda anterior. Además añade la consola de comandos en *runtime* (§7.5, línea 1315) y *rate limiting* (§14.7). |
| 26 | `12/05` y `12/08` — herramientas | ✅ Cerrado | +112 y +117 líneas. `12/05` documenta LDtkParser con pasos verificados contra su propio README (fecha de verificación explícita: 07-09-2026) y una advertencia correcta de que la recarga en vivo no debe viajar a producción. |

**Resumen:** de los 26 ítems de la lista de encargo (11 documentos + 15 ampliaciones/herramientas
contadas por separado), **24 cerrados limpios y 2 cerrados con defectos nuevos** (`04/09` y
`04/51`, el mismo defecto propagándose entre ambos — ver abajo). Ninguno quedó a medias ni con
solo el título.

---

## 2 · Los cinco defectos verificados de la ronda anterior

Los cinco defectos que este mismo papel de auditor había encontrado y que `PENDIENTE-r3.md`
listaba como «verificados y NO corregidos todavía» **están corregidos, con evidencia leída
línea a línea**:

1. 🔴 Escritura en `working_directory` (15 ocurrencias, 10 recetas) — **corregido**. Grep dirigido
   a patrones de apertura en modo escritura (`file_text_open_write`, `file_bin_open` modo 1/2,
   `buffer_save`) combinados con `working_directory` en `04/`, `13/` y `01/`: **0 resultados**. Los
   10 documentos afectados ahora llevan el comentario `⚠️ game_save_id, NO working_directory` en
   el mismo lugar donde antes escribían mal (ejemplo: `04/03:1236`, `04/04:1448`, `04/06:316`,
   `04/07:1023`, `04/09:1558`, `04/10:1209`, `04/11:288`, `04/12:1013`, `04/15:1208`,
   `04/05:1071`).
2. 🔴 `replay_verificar()` en `13/10` nunca comparaba el hash — **corregido**, ver ítem 25 arriba.
3. 🟠 `08/22:33` contradecía la firma real de `skeleton_animation_set` — **corregido**, ver
   ítem 24 arriba.
4. 🟠 `04/09 §5.3` llamaba a `celda_construible()`/`punto_en_rango()` inventadas y no consultaba
   ocupación — **corregido**, con una nota explícita en el propio documento (línea 614-623)
   citando el informe que lo detectó. **Pero la corrección introduce un defecto nuevo — §3.1.**
5. 🟠 Citas cruzadas rotas (`13/01`→`01/15`, `01/01 §5` Workspaces, `04/28`↔`13/03` DPI) —
   **las tres corregidas**, ver §5.

---

## 3 · Defectos nuevos encontrados en esta pasada

### 3.1 🔴 `objWorldGrid` se usa pero nunca se instancia — `04/09` y `04/51`

`04/09 §5.3` (líneas 626, 641) y `04/51` (líneas 1109, 1168, más los usos de `.celdas`/`.ocupada`
del *flood fill* de soporte en §5.4-5.5) llaman a `objWorldGrid.ocupada(...)`,
`objWorldGrid.ocupar(...)` y `objWorldGrid.liberar(...)` como si `objWorldGrid` fuera un objeto
GameMaker existente cuyas variables son las del struct `WorldGrid()` (definido en `04/09` línea
688, `function WorldGrid() constructor`).

**El objeto `objWorldGrid` no aparece en ningún sitio del documento**:

- No está en la «Jerarquía de objetos» de `04/09 §2` (línea 43-60) — sí está `objChunkManager`,
  que además tiene su propio evento Create documentado (línea 808, `// objChunkManager — Create`).
- `WorldGrid` tampoco está en la tabla de Structs de esa misma sección (línea 66-70).
- No hay ningún `// objWorldGrid — Create` en el documento, ni un `new WorldGrid()` asignado a
  ninguna variable global o de instancia.
- `survival_save()`/`survival_load()` (`04/09 §6`, línea 1533 y siguientes) serializan
  `objChunkManager.chunks`, `objTimeOfDay` y `global.survival`, pero **nunca tocan
  `objWorldGrid`** — la grid de ocupación de construcciones ni se guarda ni se restaura.

Quien siga la receta al pie de la letra escribe `objWorldGrid.ocupada(_grid_x, _grid_y)` en el
Step de `objBuildManager` sin que `objWorldGrid` exista como asset ni como variable — error de
«unknown variable / unresolved object index» en tiempo de compilación o ejecución, exactamente
la clase de fallo que la propia corrección de este defecto (ítem 4 de la ronda anterior) dice
evitar. `04/51` hereda el mismo hueco porque reutiliza `objWorldGrid` tal cual, sin volver a
declararlo.

**Corrección mínima**: añadir `objWorldGrid` a la jerarquía de objetos de `04/09 §2`, un bloque
`// objWorldGrid — Create` con `grid = new WorldGrid();` (o, más simple, copiar las variables del
constructor directamente al Create del objeto) y una línea en `survival_save()`/`survival_load()`
que serialice/restaure `objWorldGrid.celdas`.

### 3.2 🔴 `"sueño"` en vez de `"sueno"` — `04/51:853`

```gml
{ tipo: NecesidadTipo.SUENO,   valor: variable_struct_get(base, "sueño"),  umbral: UMBRAL_SUENO_URGENTE  },
```

El campo real, definido en `Needs()` (`04/09` línea 246, `sueno = 100;`, sin eñe — coherente con
la convención `snake_case`/ASCII de la biblioteca), se llama **`sueno`**. La clave de cadena que
usa `04/51` para leerlo con `variable_struct_get()` lleva eñe: **`"sueño"`**. Como
`variable_struct_get()` busca por nombre literal, esta llamada **nunca encuentra el campo** y
devuelve `undefined`; la resta `_c.umbral - _c.valor` de la línea siguiente (línea 863) opera
sobre `undefined` y GameMaker Runtime 2026.0.0.23 lanza un error de tipo en tiempo de ejecución
— o, en el mejor de los casos, la urgencia de sueño de cada colono nunca se detecta.

Es exactamente el error de identificador con eñe que el encargo pedía cazar, solo que no está en
el *nombre* de la variable (que sigue las convenciones bien) sino en un **literal de cadena** que
la referencia por fuera — invisible para cualquier grep que busque identificadores GML con tilde,
visible solo comparando la llamada contra la firma real, que es justo lo que este informe hizo.

**Corrección**: `variable_struct_get(base, "sueno")` (sin eñe), en `04/51:853`. **Aplicada
directamente en esta auditoría** (una línea, trivial) — verificado que ya no queda ninguna `"sueño"`
con eñe en el documento.

### 3.3 🟡 `README.md` no refleja los documentos nuevos

El recuento de la tabla de carpetas en la raíz (`README.md`) no se actualizó tras esta ronda:

| Línea | Carpeta | Dice | Es en realidad |
|---|---|---|---|
| 131 | `04 - Recetas por género` | 46 | 53 (00-52) |
| 132 | `05 - Referencia` | 4 | 5 (01-05) |
| 140 | `13 - Diseño y producción de videojuegos` | 24 | 26 (01-26) |
| 143 | Total de documentos propios | 245 | (recalcular; el propio `actualizar.py` reporta **244** «documentos en español» tras esta sesión — la cifra del README ya no coincidía ni antes de esta ronda) |

Los índices internos de cada carpeta (`_INDICE-RECETAS.md`, `_INDICE-DISENO.md` — este último sí
dice «26 documentos» correctamente en su cabecera —, `_INDICE-ECOSISTEMA.md`) están al día; el
desfase está solo en la puerta de entrada del repositorio.

### 3.4 🟡 El encargo confluente de «marcas y fan games» no enlaza desde su destino declarado

`r3-ENCARGOS-CONFLUENTES.md §3` pedía el contenido con «Destino: `13 - …/20 - Modelo de negocio,
monetización y ética`». El contenido se escribió (`13/25`, bien) pero como **documento aparte**,
lo cual es razonable — y **`13/20` no fue actualizado para enlazar hacia `13/25`** (comprobado:
`grep -n "13.*25\|Legal de terceros\|fan game\|marca registrada\|parodia"` sobre `13/20` no
devuelve nada). `13/20` sí se tocó esta sesión, pero para un enlace distinto (live-ops, línea
332-337). El documento nuevo está bien conectado desde `13/26`, `13/11` y el índice de carpeta,
así que es descubrible — solo no desde el sitio exacto que pedía el encargo.

### 3.5 🟢 `04/35` — el tablero hexagonal quedó sin ampliar

`_indice/PENDIENTE-r3.md` (versión de antes de esta sesión) incluía «ampliar `04/35` con el
tablero hexagonal» en la cola de redacción de géneros. `git diff --stat` sobre
`04 - Recetas por género/35 - Combate por turnos y táctico en rejilla.md` muestra **2 líneas
cambiadas, 0 añadidas de sección** — no se tocó el contenido hexagonal. No estaba en la lista de
once encargos de esta sesión, así que no es un incumplimiento de lo encargado hoy, pero sigue
siendo trabajo pendiente real y debe seguir en la cola.

### 3.6 🟢 Falso positivo del corrector ortográfico (no es un defecto)

`actualizar.py` paso 4 marca `13/06:1202` por la palabra «codigo» sin tilde. Verificado: es el
flag literal `--codigo` de `_indice/buscar.py` (`if a == "--codigo":`, línea 318 de ese script) —
un identificador de CLI, no prosa. No se toca.

---

## 4 · Herramientas de verificación — salida real

```
$ python3 _indice/validar-codigo-gml.py
runtime: 3486 símbolos · propias definidas: 1879 · extensiones/librerías: 43349
102 funciones propias de ejemplo (informativo) · 0 posibles funciones del runtime INVENTADAS
Ningún nombre con prefijo del runtime sin resolver: el código no inventa funciones.

$ python3 _indice/verificar-enlaces.py
1831 rutas correctas · 0 rotas
```

**Identificadores GML con tilde/eñe**: heurística dirigida (identificador con tilde/eñe seguido de
`(` o `=`, dentro de bloques ` ```gml `) sobre los 11 documentos nuevos y los 18 archivos
ampliados — **0 resultados**. El único acento fuera de sitio de toda la ronda es el de §3.2, que
está en un literal de cadena, no en un identificador — por eso no lo caza esta heurística ni
`validar-codigo-gml.py` (que solo mira símbolos del runtime, no claves de struct).

**Guardado en `working_directory`**: 0 ocurrencias de escritura en los documentos de `04/`, `13/`
y `01/` — ver §2, ítem 1.

### `python3 _indice/actualizar.py` — salida completa, código de salida **1**

```
1. Enlaces internos
1831 rutas correctas · 0 rotas

2. Índices y MAPA.json
documentos en español : 244
manual (inglés)       : 3119
manual (español)      : 3142
archivos .gml          : 61824
símbolos explicados    : 2386  (cruce símbolo → documento)
símbolos de la API     : 3486  (de ellos 34 solo en fnames)
runtime leído          : 2026.0.0.23
MAPA.json sincronizado con el disco.

3. Coherencia de MAPA.json y del catálogo de código con el disco
256 entradas, todas existen en el disco.

4. Ortografía española
✗ 13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md
codigo

5. Cobertura de la API
3213 de 3213 símbolos vigentes son localizables (100 %).

6. Nombres de archivo
Todos los nombres de archivo están bien escritos.

7. Prueba de descubrimiento (¿un LLM encuentra lo que necesita?)
1 de 49 tareas sin resolver.
✗ Un árbol de habilidades con requisitos y respec
no apareció: «Progresión»

8. Cobertura por familias de símbolos (dónde falta doc didáctico)
Todas las familias grandes de símbolos tienen algún documento propio.

9. Código GML (¿inventa alguna función del runtime?)
102 funciones propias de ejemplo (informativo) · 0 posibles funciones del runtime INVENTADAS
Ningún nombre con prefijo del runtime sin resolver: el código no inventa funciones.

10. Compilación real del GML de los documentos (¿es sintaxis válida?)
3212 bloques se van a compilar; 289 se saltan:
✓ Los 3212 bloques compilables de los documentos compilan sin errores de sintaxis.
Tiempo total: 24.4s

11. Skill para agentes (gamemaker-biblioteca): índice generado y rutas citadas
references/indice-documentos.md regenerado: 256 documentos.
Todas las rutas que cita la skill existen.
✓ Claude Code: .../.claude/skills/gamemaker-biblioteca → esta carpeta
✓ Codex (pool): .../.codex/skills-pool/gamemaker-biblioteca → esta carpeta
✗ Codex (activa): falta /Users/adrianpereradelgado/.codex/skills/gamemaker-biblioteca

12. Espejo español del manual (¿va a la par del inglés?)
3119 páginas comparadas · 0 ausentes · 22 incompletas · 0 con literales traducidos

Queda trabajo:
 · 1 documentos con tildes ausentes   [FALSO POSITIVO — ver §3.6]
 · hay tareas de ejemplo que la biblioteca no resuelve   [preexistente, no de esta ronda]
 · el espejo español del manual tiene páginas ausentes, incompletas o con literales
   traducidos   [EN CURSO — ver aviso de concurrencia]
```

**Lectura del paso 10, el hallazgo más importante de esta pasada**: `validar-compilacion-docs.py`
**ya existe y funciona**, integrado como paso 10 de `actualizar.py`. Era el pendiente número 1 de
la ronda anterior («no llegó a crearse»). Compila de verdad, con `gm-cli`, los 3212 bloques
` ```gml ` de toda la documentación (los 11 documentos nuevos y las 18 ampliaciones incluidos) y
**los 3212 compilan sin error de sintaxis** en 24,4 s. Esto no estaba verificado la ronda pasada
más que a mano, archivo por archivo; ahora es un paso automático y repetible.

**Lectura del paso 12**: el espejo del manual pasó de «508 incompletas · 84 con literales
traducidos» (cifra de `PENDIENTE-r3.md` al empezar esta sesión) a **22 incompletas · 0 con
literales traducidos**. Es trabajo de otro agente en curso ahora mismo (confirmado por proceso
vivo), no de esta redacción — se anota como avance, no como encargo cerrado por esta ronda.

---

## 5 · Coherencia entre lo nuevo y lo viejo — reutilizaciones verificadas

Se leyó la firma real en el documento de origen y se comprobó la llamada en el documento que la
reutiliza, para **siete** casos (se pedían al menos cinco):

| # | Struct/función | Origen (firma real) | Reutilizado en | Resultado |
|---|---|---|---|---|
| 1 | `WorldGrid().ocupada(_x,_y)` / `.ocupar(_x,_y,_inst)` | `04/09:694-700` | `04/09 §5.3` (línea 626, 641) | ✅ Firma respetada, **pero `objWorldGrid` nunca se instancia** — §3.1 |
| 2 | `Needs()` — campos y métodos (`consumir`, `serialize`, `Needs.deserialize`) | `04/09:240-350` | `Animal()` en `04/45:635-701` | ✅ Correcto, con nota explícita de por qué NO se llama a `needs.update()` |
| 3 | `Inventory(_capacidad)` — `.has()`, `.remove()`, `.add()`, `.count()` | `04/04:505-590` | `Recipe.puede_craftear()`/`.craftear()` en `04/09:369-397` | ✅ Correcto |
| 4 | `GestorFichas(_objetivo,_cap_rejilla,_cap_ataque,_radio_aprox,_radio_ataque,_ranuras=8)` | `04/33:237-243` | `04/47:487` (`new GestorFichas(obj_jugador, 3, 2, …)`) y `04/49:569` (`new GestorFichas(global.balon, 5, 2, 90, 35)`) | ✅ Correcto en los dos sitios — orden y número de argumentos coinciden, y ambos usan la nota de `04/33` de que el objetivo solo necesita `x`/`y` |
| 5 | `RecursoCombate(_maximo,_regen_por_frame,_retardo_frames)` — campo `.actual` | `04/36:468` | `04/50:1111` (guardia) y `04/50:1202` (barra de súper) | ✅ Correcto en ambos usos |
| 6 | `Needs()` compuesto dentro de `NecesidadesColono()` (`base = new Needs()`) | `04/09` | `04/51:807-880` | ⚠️ Estructura correcta, pero **`variable_struct_get(base, "sueño")` con eñe no encuentra el campo real `sueno`** — §3.2 |
| 7 | Patrón BFS de 4-vecinos del *flood fill* (`dungeon_flood_fill`, `04/05:592`) | `04/05 §5.4` | `soporte_calcular()`/`habitaciones_detectar()` en `04/51 §5.4-5.5` (líneas 1129, 1230) | ✅ El patrón se adapta correctamente (expande sobre ocupado en vez de sobre suelo transitable) y usa `_grid.ocupada()`/`_grid.celdas` con los nombres reales del struct `WorldGrid` — **hereda el defecto de §3.1 porque depende del mismo `objWorldGrid` nunca instanciado** |
| 8 | `llegar_a(_tx,_ty,_vel,_radio_freno)` («Arrive») | `04/23:64` | `04/49:519` (`llegar_a(_obj.x, _obj.y, VELOCIDAD_MAX, RADIO_FRENADO)`) | ✅ Correcto |

De ocho reutilizaciones verificadas, **seis son correctas y dos arrastran el mismo defecto**
(`objWorldGrid`), más un noveno hallazgo aislado (`"sueño"`/`sueno"`) en una reutilización que por
lo demás está bien construida. No es una reutilización mal *diseñada* — el patrón de composición
(`base = new Needs()`, delegar en el struct de origen en vez de copiarlo) es exactamente lo
correcto, y así lo explica el propio documento antes del bloque de código (línea 793-795,
comparándolo con cómo `04/47 §4.3` extiende `04/30` sin tocarlo). El fallo es una errata de una
palabra dentro de, por lo demás, una integración bien razonada.

### Citas cruzadas verificadas (las cuatro de `r3-ENCARGOS-CONFLUENTES.md §4`)

| Cita rota | Estado |
|---|---|
| `13/01` → `01/15` sobre «el profiler» | ✅ Corregida: `13/01:12-13` ahora enlaza a `01/15` explícitamente |
| `01/01 §5` promete Workspaces y no los desarrolla | ✅ Corregida: `01/01:166-168`, sección «Los Workspaces» desarrollada |
| `08/22:33` contradice `skeleton_animation_set` | ✅ Corregida, ver §2 ítem 3 |
| `04/28` y `13/03` sin enlazar en DPI/*letterbox* | ✅ Corregida: enlace en ambos sentidos (`04/28:250,324` → `13/03`; `13/03:1031,1381` → `04/28`) |

---

## 6 · Trabajo en curso (no evaluado como defecto, por encargo explícito)

- **Espejo del manual (`09 - Manual oficial/`)**: proceso vivo confirmado
  (`verificar-espejo.py --resumen` en un bucle de estabilización). Avance real desde el inicio de
  esta sesión: 508→22 páginas incompletas, 84→0 con literales traducidos.
- **`_indice/validar-compilacion-docs.py`**: confirmado en ejecución por otro proceso
  (`ps aux`) durante parte de esta auditoría. Ya integrado en `actualizar.py` paso 10 y
  funcionando (ver §4) — el pendiente nº 1 de la ronda anterior está, de hecho, ya resuelto.
- **`reconstruir.sh`**: no existe con ese nombre exacto, pero `_indice/reconstruccion/descargar_manual.py`
  es nuevo y sin trackear (`git status`: `??`), consistente con trabajo del mismo bloque en marcha.
- **`_indice/PENDIENTE-r3.md`** cambió de contenido *mientras* se escribía este informe (otro
  agente lo está actualizando en vivo) — normal dado el aviso de concurrencia, no se ha usado como
  fuente de verdad para el estado, solo como punto de partida.

---

## 7 · Lo que queda — honesto y corto

1. **Arreglar `objWorldGrid`** en `04/09` (y por herencia en `04/51`): añadirlo a la jerarquía de
   objetos, darle un evento Create que instancie `WorldGrid()`, y serializarlo/restaurarlo en
   `survival_save()`/`survival_load()`. Es un defecto real de compilación/ejecución, no cosmético.
2. ~~Arreglar `"sueño"` → `"sueno"` en `04/51:853`~~ — **ya corregido** en esta misma auditoría.
3. **Actualizar los recuentos del `README.md` raíz** (líneas 131, 132, 140, 143) — 04: 46→53,
   05: 4→5, 13: 24→26, total: recalcular contra el 244 que reporta `actualizar.py`.
4. **Enlazar `13/25` desde `13/20`**, que era el destino que pedía el encargo confluente —
   una frase y un enlace, el documento ya existe y está bien escrito.
5. **`04/35` sigue sin el tablero hexagonal** — no era parte de los once encargos de hoy, pero
   sigue en la cola de la ronda anterior y no se debe olvidar.
6. **El espejo del manual** (22 páginas incompletas) y **`validar-compilacion-docs.py`/`reconstruir.sh`**
   — en curso por otro agente ahora mismo; no repetir el trabajo, solo esperar a que termine y
   volver a correr `actualizar.py` paso 12 para confirmar 0 incompletas.
7. El hueco de descubrimiento del paso 7 de `actualizar.py` («árbol de habilidades» no aparece
   buscando «Progresión») es preexistente a esta ronda — no se investigó a fondo por no ser parte
   del encargo, pero queda anotado para quien retome `probar-descubrimiento.py`.

**Nada de lo anterior es cosmético salvo los puntos 3 y 4.** El punto 2 ya se corrigió en esta
misma pasada. El punto 1 (`objWorldGrid`) sigue abierto — no es una línea, es una pieza que falta
(objeto + Create + guardado), y es el único bug real de compilación/ejecución que queda de toda
la ronda.
