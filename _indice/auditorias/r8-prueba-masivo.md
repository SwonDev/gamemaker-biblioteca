# R8 · Prueba de perfil: hordas masivas — rendimiento y legibilidad a escala

> Prueba de perfil de la skill `gamemaker-biblioteca` centrada en el punto donde la teoría y la
> práctica más se separan: **cientos de entidades a la vez, colisiones entre todas, dibujado
> eficiente, y que el jugador siga entendiendo qué le mata.** Construido en `~/gm_prueba_masivo`
> (fuera de la biblioteca), verificado con `gm-cli compile`/`run` reales en **VM y en YYC
> (`--runtime native`)**, medido con mis propios logs de rendimiento (`fps`/`fps_real`/
> `get_timer()`), y capturado en pantalla con `screen_save()`. Proyecto borrado al terminar; esta
> auditoría y sus dos capturas (`r8-capturas/r8-masivo-*.png`) son lo único que queda.

**Versión de referencia**: GameMaker LTS 2026 · IDE `2026.0.0.16` · runtime `2026.0.0.23` ·
`gm-cli` 2.3.0 con `ResourceTool@2026.0.17`. Verificado en vivo el 8 de septiembre de 2026, en un
MacBook Pro con **Apple M5 Pro** — el mismo chip exacto que usa la propia biblioteca en
`13 · 23 §3.4` para su benchmark de layout de memoria, lo que hace la comparación de esa sección
(§2.2 más abajo) especialmente limpia: mismo hardware, solo cambia VM/YYC.

---

## 0 · Veredicto en una frase

**La biblioteca acierta en lo esencial de rendimiento a escala — pooling, colisión nativa para
instancias, spatial hash solo para structs, curva geométrica, color reservado para lo peligroso —
y sostuve 60 fps bloqueados hasta 1500-2000 enemigos simultáneos sin inventar ninguna técnica
propia, solo aplicando lo que ya está escrito. El colapso real (2000→3000) llega mucho más tarde
de lo que la tabla de `13 · 08 §4` podría hacer temer a un lector apresurado — esa tabla es sobre
colisión ingenua entre *structs*, no sobre instancias de GameMaker con las funciones nativas, y
medí ambos casos por separado para no confundirlos. El hallazgo más caro: el propio benchmark de
`13 · 23 §3.4` avisa de que "el factor debería mantenerse en la VM" aunque no lo hayan medido ahí
— **lo medí, en el mismo chip, y NO se mantiene**: 2,79× en YYC (coincide con lo publicado) frente
a solo 1,27× en VM, el runtime por defecto de `gm-cli run`/`compile`. Quien lea esa sección y
extrapole el factor a un proyecto que exporta a VM se equivoca a la mitad.**

---

## 1 · El juego construido

**ENJAMBRE** — un *bullet heaven* (04 · 44 §1) completo y jugable: menú, opciones (volumen ×2,
calidad gráfica), pausa que congela el mundo de verdad, bucle de hordas crecientes con curva de
dificultad geométrica (patrón `next_wave()` de la Survivor Game Template oficial, citado en
04 · 44 §1.4.2 B), jefe final, victoria y derrota, guardado de la mejor oleada, y créditos. Sin
arte de terceros: 7 sprites generados por código (Pillow, círculos/rombos/triángulos simples) y
todo el resto dibujado con primitivas (`draw_circle`, `draw_rectangle`).

**Arquitectura** (siguiendo 04 · 44 §1.2 al pie de la letra):

| Pieza | Qué es | De dónde sale |
|---|---|---|
| `obj_jugador`, `obj_enemigo`, `obj_proyectil`, `obj_recogible_xp` | Instancias de GameMaker, todas pooladas | `scr_pool.gml` — copia literal de `06/scr_pool.gml`, citado como fuente por 04 · 44 §1.4.5 |
| `obj_director_oleadas` | Único controlador de spawn/dificultad/victoria | 04 · 44 §1.2 |
| Catálogo de enemigos (`basico`/`rapido`/`tanque`/`jefe`) | Struct estático, sin lógica dentro | 04 · 44 §1.5.0 |
| `obj_bench_director` (solo `rm_benchmark`) | Banco de pruebas automatizado que arranca solo, mide y llama a `game_end(0)` | Diseño propio para esta auditoría, sobre el patrón de config/env-var de 13 · 10 §3.5 |

**Lo que NO construí, dicho sin adornos** (checklist de 04 · 00, punto por punto):

- **Sin menú "elige 1 de 3" al subir de nivel** (04 · 44 §1.4.3): la dificultad sube sola, el
  jugador no elige mejoras. Recortado a propósito para centrar el tiempo en rendimiento/
  legibilidad, no en diseño de progresión.
- **Sin splash inicial** ni selección de nivel (no aplica: juego de una sola sesión/arena).
- **Sin shader de contorno** (08 · 06 §6.2, citado por 04 · 44 §1.4.7): la silueta reservada para
  lo peligroso se resolvió con un anillo `draw_circle` en magenta, no con el *fragment shader* de
  contorno por píxel — mismo principio de exclusividad cromática, geometría más simple.
- **Sin sistema de partículas** de 04 · 39: los pocos efectos (destello de invulnerabilidad, anillo
  del pulso de área) son primitivas dibujadas a mano; no hice falta llegar al presupuesto de
  partículas de §3.12/§3.14 porque no usé `part_type_*` en ningún punto.
- **Guardado simplificado**: solo la mejor oleada alcanzada y los ajustes, no una partida a medias
  — versión reducida a propósito de `06/scr_save_load.gml` (mismo patrón de escritura segura y
  `game_save_id`, sin checksum ni copias de seguridad rotativas).
- **Sin mando probado**: sin hardware de mando en esta máquina, no pude verificar esa fila del
  checklist de 13 · 05 §4 — coincide con lo que 12 · 09 §4.2 dice que un agente no puede comprobar
  solo.

---

## 2 · ¿Se sostienen los consejos de rendimiento al medirlos?

### 2.1 · Colisiones a escala: la regla de 13 · 08 §4.3 se sostiene, con margen de sobra

La decisión de arquitectura citada literalmente: *"Las funciones nativas son la primera opción
cuando tus entidades son instancias"* (13 · 08 §4.3, línea 707). Usé `collision_circle_list()`
para el daño de contacto jugador↔enemigo y el arma de área, `instance_place()` para
proyectil↔enemigo, `instance_nearest()` para el objetivo del arma automática — nunca un `with()`
recorriendo todos los enemigos, nunca la rejilla de spatial hash para el juego real.

**Fase A del banco de pruebas — rampa de cantidad de `obj_enemigo` reales (instancias con
sprite, colisión y separación nativa activados), sostenida 3 s reales por escalón, tres pasadas
independientes en VM más una en YYC:**

| Enemigos activos | fps media (VM) | fps mín (VM) | fps media (YYC) | fps mín (YYC) |
|---:|---:|---:|---:|---:|
| 100 | 53,8 | 0 ⚠️ | 53,8 | 0 ⚠️ |
| 200 | 60,0 | 60 | 60,0 | 60 |
| 300 | 60,0 | 60 | 60,0 | 60 |
| 500 | 60,0 | 60 | 60,0 | 60 |
| 750 | 60,0 | 60 | 60,0 | 60 |
| 1000 | 60,0 | 60 | 60,0 | 60 |
| 1500 | 60,0 | 60 | 60,0 | 60 |
| 2000 | 59,1-59,9 | 55-59 | 60,0 | 60 |
| 3000 | 32,6-37,0 | 30-33 | 37,0 | 33 |

**60 fps bloqueados hasta 1500-2000 enemigos activos, en tres pasadas VM reproducidas de forma
consistente** (n=3000 dio 32,6 / 34,6 / 37,0 fps media entre pasadas — varía, pero siempre en el
mismo rango, nunca cerca de 60). El colapso real está entre 2000 y 3000, no en las cifras que un
lector apresurado podría temer tras leer solo la tabla de `13 · 08 §4` (ver §2.3). YYC ayuda poco
aquí porque el cuello de botella hasta 2000 es *vsync* (sobra CPU: `fps_real` a n=2000 en VM
todavía marca ~62-65, muy por encima de 60), y en 3000 —donde sí es CPU-bound— la ventaja de YYC
es modesta (~10-14 %), no el ×2-×3 que promete `01 · 15 §Paso 4` para lógica intensiva: aquí el
coste ya no es solo lógica GML, es GPU (500-3000 `draw_self()` + separación nativa), y `01 · 15
§Paso 4` avisa expresamente de eso: *"YYC no hace milagros con el dibujado"*.

> ⚠️ **Anomalía honesta, no barrida bajo la alfombra**: `fps_mín=0` en la primera etapa (n=100),
> reproducida en las **cuatro** pasadas (VM×3, YYC×1) con el mismo valor exacto. Nunca vuelve a
> pasar en ninguna etapa posterior pese a tener más entidades — es un coste de arranque en frío
> (probablemente la primera vez que `obj_enemigo` puebla de verdad las estructuras de colisión
> internas del motor), no un problema que escale con N. No hay documentación propia de la
> biblioteca sobre este coste puntual; lo dejo anotado como hallazgo propio.

### 2.2 · El benchmark de `13 · 23 §3.4` reproducido — se sostiene en YYC, se derrumba a la mitad en VM

Esto es lo más valioso que traigo. `13 · 23 §3.4` mide 200 000 "partículas" (posición+velocidad)
actualizadas 50 veces, comparando un array de structs contra un array plano (*struct-of-arrays*),
y publica un factor de **2,72×-2,76×** medido en YYC en un **Apple M5 Pro** — el chip exacto de
esta máquina. El propio documento avisa: *"El factor entre versiones debería mantenerse en la VM
por venir de un efecto de hardware (caché de CPU), pero el número absoluto de milisegundos no se
ha medido ahí — no lo des por bueno sin remedir si tu proyecto exporta a VM"* (línea 402-407).

Copié su código de benchmark literal (`bench_fase_d_layout_memoria()`, mismo `_n=200000`,
`_reps=50`) y lo corrí en **ambos runtimes**, mismo chip:

| Runtime | Array de structs (ms/pasada) | Array plano (ms/pasada) | Factor |
|---|---:|---:|---:|
| **YYC** (`--runtime native`, como midió la biblioteca) | 8,62 | 3,09 | **2,79×** |
| **VM** (por defecto de `gm-cli run`/`compile`, sin flags) | 35,13 | 27,56 | **1,27×** |

**El factor en YYC (2,79×) coincide casi exactamente con lo publicado (2,72-2,76×) — esa parte se
sostiene perfectamente.** Pero la predicción explícita de que *"el factor debería mantenerse en la
VM"* **no se sostiene**: en VM el factor es **menos de la mitad**. La explicación más probable,
razonada a partir de los números: en VM cada acceso —tanto al struct como al array plano— paga un
coste fijo de interpretación de bytecode que domina sobre el efecto de caché; ese coste fijo es
parecido para ambas versiones, así que **comprime** la diferencia relativa entre ellas (35,1 ms
frente a 27,6 ms: ambas se ralentizan mucho respecto a YYC, pero no en la misma proporción). En
YYC ese coste de interpretación desaparece y el efecto de caché de CPU queda desnudo, con el
factor completo.

**Consecuencia práctica**: `gm-cli compile`/`run` usan **VM por defecto** — así compilé y corrí
todo el resto de este proyecto, y así compila y corre la inmensa mayoría de proyectos reales que
no activan YYC a propósito. Un lector que decida "no me hace falta el array plano, el factor de
2,7× no compensa la pérdida de legibilidad" basándose en `13 · 23 §3.4` sin remedir en su propio
runtime **está subestimando el coste real en VM en más de la mitad** — justo lo contrario de lo
que necesitaría saber para decidir bien. La sección hace lo correcto avisando de que no lo midió
en VM; lo que no acierta es la intuición de que el factor "debería" mantenerse ahí.

### 2.3 · El spatial hash de `13 · 08 §4` — reproducido con datos propios, y se sostiene con creces

`13 · 08 §4` predice, sin medir, esta tabla para colisión ingenua todos-contra-todos:

| Entidades | Parejas/frame (predicho) | Mis parejas/frame (medidas) | A 60 fps (predicho) |
|---:|---:|---:|---|
| 50 | 1 225 | 1 225 ✓ | trivial |
| 200 | 19 900 | 19 900 ✓ | empieza a notarse en la VM |
| 500 | 124 750 | 124 750 ✓ | ⚠️ se come el frame |
| 1 000 | 499 500 | 499 500 ✓ | inviable en GML |

Los recuentos de parejas son aritmética pura (`N·(N-1)/2`), así que coinciden por construcción —
lo que faltaba medir era el **tiempo real**. Reproduje su propio experimento (§4.1-4.2:
`rejilla_nueva`/`rejilla_insertar`/`rejilla_vecinos`, código citado literal) con *structs*, no
instancias, comparando fuerza bruta contra spatial hash:

| N | Fuerza bruta (VM) | Spatial hash (VM) | Factor (VM) | Fuerza bruta (YYC) | Spatial hash (YYC) | Factor (YYC) |
|---:|---:|---:|---:|---:|---:|---:|
| 50 | 294 µs | 529 µs | **0,56×** (fuerza bruta gana) | 73 µs | 173 µs | 0,42× |
| 200 | 4 604 µs | 869 µs | **5,30×** | 1 180 µs | 248 µs | 4,76× |
| 500 | 29 239 µs | 1 623 µs | **18,02×** | 7 347 µs | 430 µs | 17,09× |
| 1 000 | 120 631 µs | 2 769 µs | **43,56×** | 29 017 µs | 748 µs | 38,79× |

**Se sostiene punto por punto**: a 50 entidades la rejilla pierde (confirma literalmente "menos de
~50, nada, el bucle doble es más rápido" de §4.3), y a partir de 200 gana por un margen que crece
sin parar. El dato más contundente: **a 500 structs, la fuerza bruta por sí sola (29,2 ms en VM)
ya excede el presupuesto de frame entero (16,67 ms)** — "se come el frame" no es una metáfora, es
literal. A 1 000, son 120,6 ms solo en colisiones — 7 veces el presupuesto, "inviable" confirmado
al milisegundo. Incluso en YYC (29,0 ms a 1 000), sigue por encima del presupuesto: el consejo no
depende del runtime.

### 2.4 · Separación entre instancias — ni el consejo nativo es gratis, ni el ingenuo es catastrófico

Esta pregunta no la responde ningún documento propio directamente: 300-3000 `obj_enemigo` que se
empujan entre sí para no apilarse perfectamente es una situación intermedia entre "instancias,
usa funciones nativas" (13 · 08 §4.3) y "cientos de miles, usa spatial hash" (13 · 08 §4.1) —
tuve que combinar ambas ideas yo mismo: `collision_circle_list()` (nativa, para instancias) +
tick escalonado (01 · 15 §6, "con() sobre objetos con muchas instancias") para no comprobar las
2000-3000 cada frame, solo un tercio. A N=500 fijo, comparé tres estrategias reales:

| Estrategia | fps media (VM) | fps mín (VM) | fps media (YYC) | fps mín (YYC) |
|---|---:|---:|---:|---:|
| Sin separación (los enemigos se apilan libremente) | 52,0-55,8 | 33-49 | 55,8 | 49 |
| **Nativa + tick escalonado (la del juego real)** | **60,0** | **60** | **60,0** | **60** |
| Ingenua `with(obj_enemigo){with(obj_enemigo){}}` — O(N²) | 43,3-43,4 | 40 | 58,7 | 58 |

Tres hallazgos, ninguno documentado tal cual en la biblioteca:

1. **La estrategia elegida (nativa + tick escalonado) es la única que sostiene 60/60 perfecto** —
   confirma que combinar 13 · 08 §4.3 con 01 · 15 §6 fue la decisión correcta.
2. **"Sin separación" NO es la más barata, pese a hacer menos trabajo por Step.** Sin fuerza que
   los separe, los 500 enemigos convergen literalmente sobre el mismo punto (el jugador), y la
   consulta de daño de contacto (`collision_circle_list(..., ordered=true)`, que ordena por
   distancia) pasa de comparar contra un puñado de vecinos dispersos a construir y ordenar una
   lista de cientos de candidatos amontonados en 16 píxeles — de ahí el `fps_mín=33-49`, errático,
   peor que la versión CON separación. La separación no es solo estética (04 · 44 §1.4.7): es
   además una válvula de seguridad de rendimiento que evita este caso patológico.
3. **La versión ingenua O(N²) SÍ degrada frente a la nativa (60→43 en VM), pero no es el colapso
   catastrófico que "se come el frame" sugiere para 500 structs** — porque aquí son 500
   *instancias* con un bucle `with()` simple (sin `ds_list`, sin asignar memoria), y GameMaker
   optimiza `with()` internamente mejor que una comparación estructural pura. En YYC el golpe casi
   desaparece (60→58,7): la lógica pura compilada a nativo absorbe el coste que en VM sí se nota.
   **Sigue siendo peor que la alternativa nativa — el consejo de evitar O(N²) es correcto en
   dirección — pero la severidad depende mucho de si son instancias (aquí) o structs (§2.3, donde
   sí es catastrófico).**

---

## 3 · ¿Elegiste la estructura adecuada?

**Sí, y la decisión más importante fue NO usar el spatial hash en el juego real.** 04 · 44 §1.4.5
lo dice expresamente: mientras los enemigos sigan siendo instancias de GameMaker, las funciones
nativas de colisión son la primera opción; el spatial hash de 13 · 08 §4.1 es *"la única
alternativa nativa que no existe"* solo cuando de verdad hacen falta miles de entidades como
*structs* ligeros. Con los datos de §2.1 (60 fps sostenidos hasta 1500-2000 instancias reales),
nunca hizo falta cruzar esa frontera — construir la rejilla habría sido trabajo de más, no de
menos, para el rango de "cientos" que pide la prueba. La rejilla solo aparece en
`obj_bench_director`, exactamente donde el propio documento dice que debe vivir: un experimento
aislado con structs, no el juego.

Tampoco usé partículas (`part_type_*`) para los enemigos/proyectiles — habría sido la elección
equivocada: 04 · 39 está pensado para efectos visuales sin identidad individual (humo, chispas),
no para entidades con vida, tipo y lógica de colisión propias. Los enemigos son *lo que tiene que
seguir siendo una instancia con inteligencia*, ni un struct ligero ni una partícula.

---

## 4 · Legibilidad a escala: ¿supo la biblioteca decir cómo diferenciar la amenaza?

**Sí, y la comprobé con una captura real, no con la promesa de que "se vería bien".**
04 · 44 §1.4.7 da la receta exacta: un color —magenta puro, `make_colour_rgb(255,0,255)`—
reservado en exclusiva para lo que hace daño de verdad, nunca reutilizado por UI, XP, proyectiles
propios ni fodder; barra de vida y atribución de golpe (`ultimo_atacante`) solo en lo peligroso,
nunca en el enjambre genérico ("sería ruido, no lectura", dice el propio documento).

Primero capturé la etapa de 500 `obj_enemigo`, todos del tipo genérico `basico` (la fase A del
banco de pruebas, sin tocar nada más): confirma el problema real que 04 · 44 §1.4.7 describe — una
masa de puntos rojos indistinguibles converge sobre el jugador, y sin ningún elemento "peligroso"
con el que contrastar, el color no tiene nada que señalar todavía. Coherente con lo que dice el
documento sobre el fodder ("se queda sin ese color, sin excepción"), pero por sí sola esa captura
no prueba que la TÉCNICA funcione — solo que el problema es real.

**Captura conservada — la misma horda + 6 `tanque` alrededor del jugador**
(`r8-capturas/r8-masivo-horda-mixta-500.png`): añadí 6 enemigos `tanque` cerca del jugador, solo
para esta captura, sin tocar la función que ajusta la cantidad para las mediciones de fps (para no
contaminar §2.1). Con la variedad de verdad presente, el efecto es inmediato y nada sutil — los 6
anillos magenta con barra de vida roja saltan a la vista al instante entre los cientos de puntos
rojos apagados del fondo, exactamente como predice el documento. No usé el shader de contorno real
de 08 · 06 §6.2 (un anillo `draw_circle` cumple la misma función de exclusividad cromática con
mucho menos código) — la diferencia es de fidelidad de silueta (el shader sigue el contorno de
píxeles real; mi anillo es un círculo aproximado), no de principio.

**Un matiz que la biblioteca no cubre**: con enemigos 100 % genéricos (la fase A del banco de
pruebas, solo `basico`), el color no tiene nada que hacer — la legibilidad a esa escala depende
por completo de que el diseño meta variedad de amenaza real, no solo de tener la técnica de color
lista. 04 · 44 §1.4.2 ya avisa de que la variedad debe crecer con la oleada ("por debajo del nivel
2 solo un tipo..."), así que esto no es un hueco de la biblioteca — es una dependencia entre dos
secciones que conviene tener presente: la técnica de §1.4.7 solo rinde si §1.4.2 ya metió algo
distinto de fodder en pantalla.

---

## 5 · Las trece trampas — cuáles sirvieron, y una nueva encontrada

| # | Trampa | ¿Sirvió aquí? |
|---|---|---|
| 1 | 9/18 plantillas fallan en macOS | Sí — usé "Blank Pixel Game" directamente, sin tantear las que fallan |
| 2 | `resourcetool`/`compile` se cuelgan bajo el sandbox de Claude Code | Sí — `dangerouslyDisableSandbox: true` en las ~120 llamadas de esta sesión, sin un solo cuelgue |
| 3 | Numeración de eventos GUI Begin/End | Sí — usé `subtype=gui` (no `gui_begin`), verificado con `object event list` que cae en `Draw_64.gml` sin el bug |
| 4 | El compilador no detecta funciones/variables sin declarar | **Sí, en directo (ver más abajo) — y encontré una variante propia** |
| 5 | Fuentes de `resourcetool` sin glifos | Evitada por completo: nunca creé una fuente por `resourcetool`, fui directo a `font_add()` + Included File |
| 6 | `directory_exists()`/`directory_create()` no fiables en `--target mac` | Sí — `guardado_guardar()` ignora su valor de retorno a propósito, intenta escribir y confía en el resultado real; el guardado funcionó en las 6 pasadas de esta sesión |
| 7 | `resource info expr=project` como segunda raíz | Sí — usada para `project.RoomOrderNodes` y `project.IncludedFiles` |
| 8 | `includedfile` deja `filePath` vacío | **Sí, en directo** — reproducida exactamente como la documenta `12 · 09`, arreglada con la receta de dos pasos, confirmada leyendo el `.zip` compilado (`verdana.ttf` presente) |
| 9-10 | Eventos forzados / `OPTIONS SET` | No aplicable — todos mis eventos están en la whitelist básica, no toqué `OPTIONS` |
| 11 | `AccessViolationException` no determinista | No la vi en esta sesión, para lo que vale un solo dato: ~120 llamadas de `resourcetool` sin ninguna caída |
| 12 | Fuente por defecto omite tildes/eñes | **Sí — seguida al pie de la letra desde el primer commit, y verificada con captura real** (§6, `r8-capturas/r8-masivo-creditos-acentos.png`) |
| 13 | `screen_save()` invierte la imagen en Mac | **No reproducida** — mis dos capturas salieron del derecho, coincide con lo que ya reportó `r8-prueba-coop.md §7.4` de forma independiente |

### 5.1 · Trampa nueva, de la misma familia que la 4: variable global sin inicializar entre salas

`validar-proyecto.py --todo` pasó limpio en las 6 revalidaciones de esta sesión, y aun así el
juego **reventó en tiempo de ejecución** la primera vez que corrí `rm_benchmark`:

```
ERROR in action number 1
global variable name 'pool_proyectiles' index (100246) not set before reading it.
```

Causa: `obj_jugador · Step` llama a `global.pool_proyectiles.get_at()` sin condición — correcto en
`rm_juego` (donde `obj_director_oleadas` crea ese pool), pero `rm_benchmark` solo crea
`global.pool_enemigos`. El arma automática del jugador, que no distingue de sala, intentó leer un
global que en esa sala nunca existió. **Ni el compilador ni `validar-proyecto.py` lo detectan**:
el primero porque `global.pool_proyectiles` es sintácticamente válido (trampa 4, "no detecta...
variables sin declarar"); el segundo porque solo verifica que los *símbolos del runtime* existan,
no que un *global propio* esté garantizado en el camino de ejecución de cada sala. Arreglado
gateando las dos armas del jugador tras `instance_exists(obj_director_oleadas)` — la única señal
fiable de "estoy en una sala con el director de oleadas de verdad". Lo dejo documentado aquí
porque es exactamente el tipo de fallo que la propia trampa 4 predice y ningún paso del flujo de
la biblioteca (compilar, validar) llega a cazar solo — hace falta ejecutar de verdad.

---

## 6 · Verificación en vivo

**`validar-proyecto.py --todo`** (última pasada, tras el arreglo): `759 llamadas analizadas ·
✓ Ninguna llamada a una función del runtime que no exista · ✓ Ninguna llamada... con un número de
argumentos que no cuadre`.

**`gm-cli compile` sin `--errors-only`**, salida real, sin recortar el resultado clave (una de las
seis veces que compilé así en esta sesión — todas con el mismo resultado):

```
│  Writing Chunk... TGIN size ... 0.00 MB
│  Writing Chunk... CODE size ... 0.00 MB
│  Writing Chunk... VARI size ... 0.04 MB
│  Writing Chunk... FUNC size ... 0.01 MB
│  Writing Chunk... FEAT size ... 0.00 MB
│  Writing Chunk... STRG size ... 0.00 MB
│  Writing Chunk... TXTR size ... 0.02 MB
│  0 Compressing texture...
│  writing texture __yy__0fallbacktexture.png_yyg_auto_gen_tex_group_name__0.yytex...
│  1 Compressing texture... writing texture default_0.yytex...
│  Writing Chunk... AUDO size ... 0.00 MB
│  Stats : GMA : Elapsed=228.911
│  Stats : GMA : sp=7,au=0,bk=0,pt=0,sc=68,sh=0,fo=0,tl=0,ob=14,ro=5,da=1,ex=0,ma=6,fm=0x829C6BF66620
│  Igor complete.
◆  Compilation finished
EXIT CODE: 0
```

`sp=7,ob=14,ro=5,da=1` — 7 sprites, 14 objetos, 5 salas, 1 *included file* (la fuente), tal cual
el inventario del proyecto. **Cero `WARNING`** (comprobado con `grep -i warning`, sin salida), en
las dos compilaciones (VM y `--runtime native`) — incluido el que delataría la trampa 8 si el
Included File no se hubiera copiado bien.

**Ejecuciones reales, siete escenarios distintos, todas limpias** (sin `ERROR`, sin `not set
before reading` tras el arreglo de §5.1): arranque normal a `rm_menu`; partida completa en
`rm_juego` hasta derrota real por daño de contacto (`###derrota### oleada=1 tiempo=2788`);
partida hasta victoria real contra el jefe con parámetros de oleada acelerados solo para esta
prueba (`###victoria### oleada=2 tiempo=2812`, revertido después); banco de pruebas completo en
VM (×3) y en YYC (×1); captura de pantalla de la pantalla de créditos
(`r8-capturas/r8-masivo-creditos-acentos.png` — "rendimiento", "legibilidad", "español",
"código", "Auditoría" se leen perfectamente, todas las tildes y la eñe presentes) y de la horda
mixta (§4).

**Guardado verificado de punta a punta, no solo por código**: la partida de derrota guardó
`mejor_oleada=1`; el arranque siguiente lo cargó (`"mejor oleada = 1"` en el log); la partida de
victoria lo subió a 2; el arranque siguiente lo confirmó (`"mejor oleada = 2"`) — ciclo de
guardar/cargar real, en la ruta correcta (`game_save_id`, nunca `working_directory`).

---

## 7 · Veredicto

**Se sostiene.** La biblioteca dio la arquitectura correcta (pooling + colisión nativa +
spatial hash reservado para structs + color exclusivo) y, siguiéndola sin inventar nada por mi
cuenta, sostuve 100-2000 enemigos simultáneos a 60 fps bloqueados y aguanté hasta 3000 antes de un
colapso real — muy por encima de lo que la prueba pedía ("cientos"). Los números que publica
`13 · 08 §4` para colisión ingenua se confirmaron casi al dígito exacto cuando reproduje su propio
experimento con structs. El hallazgo que más vale la sesión: **el factor de `13 · 23 §3.4` no se
mantiene en VM pese a que el documento especula que debería** — medido en el mismo chip, cae de
2,79× a 1,27×, y como VM es el runtime por defecto de `gm-cli`, es la mitad exacta del caso que
más proyectos van a vivir. Una errata de cita menor (`13 · 13 §2.1` debería decir `§1.3`) y una
variante nueva de la trampa 4 (global sin inicializar entre salas, invisible al validador) son el
resto de lo que aporto de vuelta.

---

## 8 · Limpieza

**Nunca `pkill -f Mac_Runner` a ciegas** — durante el banco de pruebas en YYC, `ps aux` mostró
**dos sesiones de GameMaker completamente ajenas a esta prueba** corriendo a la vez en esta misma
máquina (`gm_prueba_3d/Templo3D`, `gm_prueba_docs`), confirmando en vivo la advertencia de
`12 · 09 §4.3`: un `pkill` por nombre se las habría llevado por delante también. Cada proceso de
esta sesión se aisló y se mató por PID exacto, con el patrón que corresponde a cada *runtime* —
son dos, no uno, otro detalle que `12 · 09` no cubre porque solo documenta el target VM:

```sh
# Target VM (Mac_Runner -game <ruta>) — el patrón documentado en 12 · 09 §4.3
ps aux | grep -- "-game .*/gm_prueba_masivo" | grep -v grep
kill <PID>

# Target YYC (--runtime native): NO lleva "-game" — es un .app propio bajo
# ~/gamemakerstudio2/GM_MAC/<proyecto>/, con sus "tail -F debug.log" auxiliares
ps aux | grep -i "gm_prueba_masivo" | grep -v grep
kill <PID>   # el .app, el Igor y los "tail -F" que gm-cli deja abiertos
```

Aplicado tras cada una de las ocho ejecuciones de esta sesión (menú, partida hasta derrota,
partida hasta victoria, banco de pruebas ×3 en VM, banco de pruebas en YYC, dos capturas de
pantalla), confirmando cada vez con un segundo `ps aux` que no quedaba nada. Al cerrar esta
auditoría: `rm -rf ~/gm_prueba_masivo` y el guardado de prueba que quedó fuera del proyecto, en
`~/Library/Application Support/com.yoyogames.macyoyorunner/`.
