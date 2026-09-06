# 21 · Balance por simulación: Monte Carlo, Machinations y estrategias dominantes

> Cómo comprobar una economía o un combate **antes** de gastar el primer playtest humano: la
> notación de Machinations para dibujar fuentes, sumideros, convertidores y puertas en un papel
> —o en una pizarra— antes de escribir una sola línea de GML, su traducción directa a los campos
> de un `balance.json`, y la simulación de miles de partidas en GML para leer una **distribución**
> en vez de un único número. Es la continuación de
> [13 · 01 §4.4-4.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#44--balance-por-fórmulas-con-números),
> que da las fórmulas de balance (TTK, curva de coste geométrica) pero no la manera de
> comprobarlas sin que las juegue una persona.
>
> **Lo que NO cubre este documento** (y dónde está, para no repetirlo): la **teoría** de la
> dominancia estratégica y la matriz de pagos de Schreiber —qué es una estrategia dominante y
> cómo eliminarla ajustando coste, no poder— es de
> [13 · 15 §8](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md#8--dominancia-estratégica-y-mecánicas-transitivasintransitivas);
> aquí se **automatiza** esa matriz por fuerza bruta en vez de rellenarla a mano. La
> **telemetría de dominancia sobre partidas reales** (`dominancia_iniciar`, `dominancia_registrar`,
> `dominancia_informe`) ya está escrita en
> [13 · 15 §11.2](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md#112--telemetría-de-dominancia-schreiber)
> y aquí se **reutiliza tal cual**, alimentada con partidas simuladas en vez de playtests. El
> **mini-framework de pruebas** (`scr_pruebas`, `probar()`, `afirmar_*`) es de
> [13 · 10 §3](./10%20-%20Testing%20y%20QA.md#3--un-mini-framework-de-pruebas-en-un-solo-script-de-gml)
> y aquí solo se le añade un tipo de prueba nuevo: la que corre diez mil veces antes de afirmar
> algo. El **sistema de combate de referencia** —hitboxes, tipos de daño, arquetipos, fases de
> jefe— es de [13 · 18](./18%20-%20Diseño%20de%20combate%20y%20de%20jefes.md) y de
> [04 · 30](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md),
> [04 · 32](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md)
> y [04 · 34](../04%20-%20Recetas%20por%20género/34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md);
> el combate de este documento es deliberadamente un juguete de ocho líneas, hecho para que el
> ejemplo compile solo y quepa en la página — no es una arquitectura de combate. Y la **progresión
> por builds** (árboles de habilidades, monedas múltiples) es de
> [13 · 16](./16%20-%20Progresión%20-%20árboles%20de%20habilidades%2C%20desbloqueos%20y%20meta-progresión.md),
> cuyo propio §1.6 dice textualmente que «simularlo en serio con percentiles y detección de
> dominancia es un documento propio que esta biblioteca todavía no tiene»: este es ese documento.

---

## 1 · Los principios

### 1.1 · Por qué la hoja de cálculo se queda corta

[13 · 01 §2.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#23--probarlo-sin-motor)
ya recomienda «simular 100 iteraciones de la economía en columnas» como la tercera prueba de un
bucle, antes de abrir el motor. Una hoja de cálculo hace muy bien una cosa: **una** cadena de
causa-efecto, con **una** tirada de dados por fila. Se le atraganta todo lo que un juego real
tiene y una hoja no modela sin esfuerzo heroico:

- **Ramas condicionales** («si el jugador tiene el amuleto, el veneno no aplica») — en una hoja
  son un bosque de `SI()` anidados que nadie vuelve a tocar sin romperlos.
- **Bucles con parada dinámica** («repite hasta que alguien muera») — una hoja necesita una
  columna por turno posible, con un límite fijado a mano.
- **Miles de repeticiones** — 30 filas de dados a mano se hacen en un rato; 10 000 no se hacen
  nunca, y son exactamente las que hacen falta para ver la cola de la distribución (§1.3).
- **Estado compartido entre varias reglas** (armadura que reduce daño, que a su vez depende de
  un objeto que depende de un evento aleatorio anterior) — en código son tres funciones que se
  llaman; en una hoja son referencias circulares que Excel se niega a calcular.

La hoja de cálculo sigue siendo la herramienta correcta para **datos** — 200 filas de objetos que
hay que comparar de un vistazo, como ya dice
[13 · 01 §4.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#45--de-la-hoja-de-cálculo-al-juego).
No es la herramienta correcta para **simular un sistema con reglas, ramas y azar**, que es
exactamente el trabajo para el que sirven Machinations (§2.1) y una simulación en GML (§3).

### 1.2 · Monte Carlo, en una frase

> Un método de Monte Carlo estima un valor que no se puede calcular en una fórmula cerrada
> **muestreando al azar, muchas veces, y promediando los resultados**.

La justificación formal es la **Ley de los grandes números**, citada así, textualmente, en la
documentación oficial de Machinations (verificada en vivo el 2026-09-06,
`machinations.io/docs/the-monte-carlo-simulations`):

> «The average of the results obtained from a large number of trials should be close to the
> expected value and will tend to become closer to the expected value as more trials are
> performed.»

El ejemplo que usa esa misma página es perfecto porque es minúsculo: la probabilidad teórica de
sacar un 7 al lanzar dos dados es 6/36 (16,67 %). Si lanzas los dados 36 veces de verdad, **no**
vas a sacar un 7 exactamente 6 veces — la varianza de una muestra pequeña es alta. Con 1 000
lanzadas, el histograma empieza a parecerse a la campana de Gauss teórica; con 36, todavía no.
Esa es la razón de fondo por la que «probé la build tres partidas y parece que gana siempre» no
es una conclusión: es una muestra de tamaño 3.

### 1.3 · La media miente: por qué se lee distribución, no un número

Un caso real, de un estudio de caso de Machinations sobre balance F2P
(«*Balancing F2P Economies: Simulating Player Personas and Progression Curves with Machinations*»,
`www-content.machinations.io`, verificado en vivo el 2026-09-06) lo deja muy claro. La simulación
comparaba el poder de combate de cuatro perfiles de jugador (F2P puro, híbrido, comprador
premium…) tras una sesión de dos horas, con 100 jugadores simulados por perfil:

> «While the average difference is significant —Hybrid players achieve a 61% higher average
> power than F2P (Grind Only) players— relying solely on the mean is misleading.»
>
> «The distribution analysis confirmed a healthy, skill-based meta: the top 2% of F2P players
> achieved power scores exceeding 4.0K, outperforming 19% of the 'Premium Buyers'.»

La media decía «los que pagan tienen un 61 % más de poder: pay-to-win». La distribución completa
decía algo mucho más útil para diseñar: **el 2 % mejor de los jugadores gratuitos supera al 19 %
peor de los que pagan** — el sistema recompensa la habilidad tanto como el gasto, que es
precisamente lo que un diseño F2P sano necesita demostrar. Ninguna de las dos frases sale de la
misma simulación por accidente: la segunda exige mirar percentiles, no el promedio.

La regla general, aplicada a balance de combate o de progresión:

| Si solo miras… | Te puede pasar desapercibido… |
|---|---|
| La **media** de victorias/derrotas | Una opción que gana el 95 % de las veces contra un rival y pierde el 95 % contra otro (media ≈ 50 %, "equilibrada" en el papel) |
| La **media** del tiempo de combate (TTK) | Una arma con TTK medio igual a otra, pero el doble de varianza: unas veces mata en 2 segundos, otras en 12 — se siente injusta aunque la media cuadre (§3.7) |
| Solo **una** corrida | Cualquier cosa: con una muestra de 1, la varianza de la muestra ES el resultado |

### 1.4 · Qué preguntas responde esto que una fórmula cerrada no responde

[13 · 01 §4.4](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#44--balance-por-fórmulas-con-números)
da el TTK exacto para un daño y una cadencia **fijos**. La simulación hace falta en cuanto entra
**cualquier** azar que interactúa con una condición de parada:

- **¿Con qué frecuencia gana cada build/arma/carta si las enfrento muchas veces?** — la pregunta
  de dominancia de [13 · 15 §8](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md#8--dominancia-estratégica-y-mecánicas-transitivasintransitivas),
  respondida sin escribir la matriz de pagos a mano.
- **¿Cuál es el peor caso razonable, no el peor caso absoluto?** — el percentil 99 de un combate
  («9 de cada 10 000 combates duran más de X segundos») es información accionable; el máximo
  absoluto de una sola corrida no lo es.
- **¿Esta build es dominante, o solo la usa todo el mundo porque parece buena en el papel?** —
  requiere separar **tasa de uso** de **tasa de victoria** (§3.6), y eso exige poder simular
  ambas por separado, no solo observar telemetría de gente que ya eligió sesgada.
- **¿Cuánta variación es «emocionante» y cuánta es «injusta»?** — el coeficiente de variación
  de miles de combates (§3.7), no la sensación de un playtester tras tres partidas.

---

## 2 · El método, paso a paso

### 2.1 · Diagramar antes de programar: la notación de Machinations

[13 · 01 §4.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#41--el-vocabulario-correcto)
ya usa el vocabulario del libro de Adams y Dormans —Pool, Fuente, Sumidero, Convertidor,
Intercambiador— y menciona que ese libro «originó la herramienta Machinations». Lo que ese
apartado no daba es la **notación visual** con la que se dibuja una economía antes de tocar el
teclado. Verificado en vivo el 2026-09-06 contra `machinations.io/docs` y la documentación
enlazada desde ahí, el vocabulario completo con su comportamiento exacto:

| Elemento (letra verificada) | Qué es | Comportamiento verificado |
|---|---|---|
| **Pool (P)** | Almacena un recurso | «store Resources and are the building blocks of Machinations» — tiene una cantidad inicial, una **Capacidad** límite opcional y una política de **Overflow** (bloquear o drenar el exceso) |
| **Source (S)** | Genera recursos de la nada, sin límite | «produce unlimited numbers of Resources» — no tiene conexión de entrada; el ritmo lo decide la fórmula de su conexión de salida, no la Source en sí |
| **Drain (D)** | Consume recursos permanentemente | «consume Resources from Pools and other Nodes» — lo que entra en un Drain **sale de la economía para siempre**; puede drenar de varias fuentes a la vez y a ritmos distintos |
| **Resource Connection (C)** | Transporta un recurso entre dos nodos | Lleva una **fórmula**: un número fijo, una tirada de dados (`D6`, `4D10`), un porcentaje de probabilidad, o `random(min,max)` / `randomInt(min,max)` |
| **State Connection** | No mueve recursos: lee o fuerza el **estado** de otro nodo | Línea discontinua; con fórmula `*` se llama **Trigger** — dispara la acción de otro nodo sin transferir nada |
| **Converter** | N entradas (**coste**) → exactamente 1 salida (**producción**) | «receive resources which are drained… and generate new resources» — si falta **cualquiera** de los requisitos, no produce nada (§3.4) |
| **Trader** | ⩾ 2 entradas y ⩾ 2 salidas, de **colores** (tipos) distintos | Cambia de manos recursos que ya existían, sin crear ni destruir — el **Intercambiador** de `13 · 01 §4.1`, con nombre distinto |
| **Gate (G)** | Reparte o dispara, **no almacena** | Dos modos: **deterministic** (reparte por las proporciones fijas de sus salidas) y **random** (cada salida es una probabilidad de que el recurso la tome) |
| **Register (R)** | Calcula un valor a partir de otros nodos | No es un Pool: no acumula recursos del juego, computa un número derivado (piensa en él como una fórmula visible en el diagrama, no como un dato del juego) |
| **End condition (E)** | Para la simulación cuando se cumple | Sólo acepta State Connections como entrada; con varias End conditions en un diagrama, **basta con que se cumpla una** para parar |
| **Trigger Mode** (de cualquier nodo anterior) | Cuándo se dispara | 4 modos verificados: **Passive** (solo responde a un trigger externo), **Interactive** (solo con clic del usuario), **Automatic** (se dispara todos los Steps), **Enabling** (una vez, al arrancar o al activarse) |

> ⚠️ La documentación en vivo de `machinations.io/docs/converters-traders` etiqueta **tanto**
> Converters como Traders con la letra `(V)` en el texto de sus respectivas fichas — una
> inconsistencia real, observada el 2026-09-06, no un error de transcripción de este documento.
> Por eso la tabla de arriba no les asigna una letra: se identifican por nombre y comportamiento,
> que sí están verificados sin ambigüedad.

**Cómo se dibuja, en ASCII, sin la herramienta.** No hace falta la cuenta de pago de Machinations
para razonar con su vocabulario: un rombo para una Gate, un círculo para un Pool y una flecha con
la fórmula encima bastan en una pizarra o en el propio GDD
([13 · 14](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md)).
Ejemplo real, el mismo combate que se simula en código en §3.3 —pistola contra el enemigo
«bruto» de `13 · 01 §9.3`— dibujado ANTES de escribir una línea:

```
  Jugador ataca                    Gate (G), random           Pool (P)
  Trigger: Automatic               10 % / 90 %                vida_bruto = 180
  (cada Step = una ronda)                                          │
        │                          ┌──► 10% ──► x2 daño ──┐        │
        └──15 de daño (C)──► ◇ ────┤                      ├──D────►○
                                    └──► 90% ──► x1 daño ──┘        │
                                                                     ▼
                                                    State Connection (┄┄►)
                                                                     │
                                                                     ▼
                                                    End condition (⚑): vida_bruto ≤ 0

  Bruto ataca de vuelta            Pool (P)
  Trigger: Automatic               vida_jugador = 100
        │                               │
        └──25 de daño (C)──────D───────►○───┄┄►  End condition (⚑): vida_jugador ≤ 0
```

> El diamante ◇ (Gate) y el triángulo del faucet de una Source están confirmados por capturas
> reales de la documentación (`activation-modes`, ejemplo *Stack Jump*: «The Source
> (triangle-shaped component) produces a Block every second» y «the Jump Gate ◇»). El resto de
> glifos ASCII de arriba (○ para Pool, el trazo `┄┄►` para State Connection, ⚑ para End
> condition) son una convención mnemotécnica propia para dibujar a mano, no un calco verificado
> del icono exacto que pinta el editor — lo que importa para diseñar es el comportamiento de la
> tabla, no el pixel del icono.

Este diagrama de ocho líneas ya deja ver, **antes de programar**, la pregunta que responde §3:
¿la Gate de crítico al 10 % hace ganar a este jugador con más frecuencia de la que debería, o el
Drain del bruto (25 de daño por ronda) le mata antes de que el sumidero de vida del bruto llegue
a cero? Esa pregunta, con dos flujos que compiten por «quién llega antes a cero», es exactamente
la que una fórmula cerrada de TTK no responde sola (§1.4) y una simulación sí (§3.3).

### 2.2 · De Machinations a `balance.json`

`13 · 01 §9.3` ya define `balance.json` con `jugador`, `armas`, `enemigos` y `economia`. La
notación de §2.1 se traduce a ese mismo archivo sin inventar una estructura paralela — cada
elemento de Machinations es, o bien un campo existente, o bien un campo nuevo con un propósito
concreto:

| Elemento de Machinations | Dónde vive en `balance.json` / en el juego |
|---|---|
| **Pool** | Un campo numérico que se lee y se escribe: `enemigos.bruto.vida`, `jugador.vida` |
| **Source** | No es un campo: es el propio bucle del juego generando el recurso cada Step (el `Step` de simulación de §3.3, o `scr_config §9.2` para constantes que no cambian) |
| **Drain** | La resta que quita el recurso para siempre: `vida -= calcular_dano(...)` |
| **Resource Connection**, fórmula fija | Un número en el JSON: `armas.pistola.dano` |
| **Resource Connection**, fórmula de dados/porcentaje | Una llamada a azar en el código que lee ese campo — nunca un número fijo en el JSON |
| **Gate random** | Un campo de probabilidad nuevo: `armas.pistola.prob_critico` (§2.1, §3.3) |
| **Gate deterministic** | Un array de pesos fijos, p. ej. `distribucion_loot: { comun: 70, raro: 25, legendario: 5 }` |
| **Converter** | Una sub-tabla nueva con `requisitos` y `produccion` — ver `crafteo` en §3.1 |
| **Trader** | Un precio o tasa de cambio: `tienda.precio_objeto`, exactamente el Intercambiador que `13 · 01 §4.1` ya nombra |
| **Register** | **No** es un campo del JSON: es una función pura de GML que calcula un derivado (`tiempo_para_matar()` de `13 · 01 §9.4` es literalmente un Register hecho función) |
| **End condition** | La condición de parada de un `while` en la simulación (§3.3) |
| **Trigger Automatic** | Cada iteración del bucle de simulación — no hace falta un campo, es la estructura del propio bucle |

La fila del **Converter** es la única pieza nueva de estructura. Extiende `balance.json` con una
sub-tabla `crafteo`, siguiendo el comportamiento verificado («N entradas se consumen, exactamente
1 salida se produce, y si falta cualquier requisito no produce nada»):

```json
{
  "version": "1.5.0",
  "jugador":  { "vida": 100, "velocidad": 3.2, "invencible_frames": 45 },
  "armas": {
    "pistola":  { "dano": 15, "cadencia": 12, "cargador": 8, "prob_critico": 0.10 },
    "escopeta": { "dano": 54, "cadencia": 45, "cargador": 4, "prob_critico": 0.10 }
  },
  "enemigos": {
    "baba":    { "vida": 30,  "dano": 8,  "velocidad": 0.8 },
    "arquero": { "vida": 45,  "dano": 12, "velocidad": 1.2 },
    "bruto":   { "vida": 180, "dano": 25, "velocidad": 0.6 }
  },
  "crafteo": {
    "pocion_curacion": {
      "requisitos": { "hierba": 2, "frasco_vacio": 1 },
      "produccion": { "pocion_curacion": 1 }
    }
  },
  "economia": { "coste_base": 25, "coste_razon": 1.18, "oro_por_baba": 4 }
}
```

`escopeta.dano` pasa de `9` (por perdigón) a `54` porque, para el experimento de §3.3, interesa
el daño **total** de una descarga (6 perdigones × 9); si tu proyecto necesita seguir modelando
perdigón a perdigón para otros cálculos, guarda ambos campos (`dano_por_perdigon` y
`perdigones`) y deriva `54` en una función, no dupliques la fuente de verdad. El resto del
archivo —`jugador`, `enemigos`, `economia`— es exactamente el de `13 · 01 §9.3`; el único campo
realmente nuevo es `prob_critico`, que es la Gate random de crítico del diagrama de §2.1, y la
sub-tabla `crafteo`, que es el Converter.

### 2.3 · Diseñar el experimento: qué varía, qué se mide, cuántas corridas

Antes de escribir el bucle de simulación, tres decisiones por escrito — la misma disciplina que
`13 · 01 §8.2` pide para una ficha de sistema:

1. **Qué varía entre corridas.** Si es solo el azar (dados, crítico), basta una función pura con
   una fuente de azar inyectada (§3.3). Si varía también la **decisión** del jugador (qué build
   elige), hace falta un modelo de esa decisión — ver la distinción entre tasa de uso y tasa de
   victoria en §3.6, que necesitan **diseños de experimento distintos**.
2. **Qué se mide.** Decide la métrica ANTES de correr nada: tiempo hasta la condición de fin
   (turnos, TTK), quién ganó, o un tercer valor derivado (oro acumulado, daño total). Cambiar la
   métrica después de ver un resultado que no gusta es la versión de balance de p-hacking.
3. **Cuántas corridas.** Machinations documenta, citando la Ley de los grandes números (§1.2),
   un mínimo de **30 corridas** para que la media se acerque al valor esperado. Treinta bastan
   para una media — **no** bastan para un percentil de cola. La cuenta es aritmética, no una
   fórmula estadística cerrada: para que el percentil 99 tenga siquiera 100 muestras en esa
   última centésima de la distribución hacen falta `100 ÷ 0,01 = 10 000` corridas; para el
   percentil 95, `100 ÷ 0,05 = 2 000` bastan. ⚠️ Es una heurística de oficio derivada por
   aritmética simple, no una cifra de una fuente primaria — pero es la razón concreta por la que
   este documento simula **10 000** combates y no 30: 30 corridas nunca te van a enseñar cómo de
   mal puede ir el 1 % de las peores partidas, y ese 1 % es justo el que un jugador de verdad sí
   va a vivir alguna vez.

### 2.4 · Leer resultados: percentiles, no medias

Con los datos de N corridas ya en un array, el orden de lectura que evita las trampas de §1.3:

1. **Ordena el array** (`array_sort`, §3.2) — todo lo demás depende de que esté ordenado.
2. **Lee la media Y el percentil 50 (mediana) juntos.** Si se separan mucho, la distribución
   está sesgada (unas pocas corridas muy largas o muy cortas están arrastrando la media) — eso
   ya es una señal, antes de mirar nada más.
3. **Lee p90 y p99**, no solo el máximo. El máximo de una muestra de 10 000 es ruido de una sola
   tirada rarísima; el p99 es «esto le va a pasar a 1 de cada 100 jugadores», que sí es
   accionable.
4. **Compara la tasa de uso con la tasa de victoria** (§3.6) antes de tocar ningún número: son
   dos preguntas distintas y una fórmula de balance nunca debería intentar resolver las dos
   fusionadas en una.
5. **Compara el coeficiente de variación** (§3.7) contra el resto de opciones del mismo nivel de
   coste, no en abstracto: lo que importa es si esta opción es mucho más o menos volátil que sus
   rivales directas, no un umbral universal.

---

## 3 · Cómo se traduce a GameMaker

Todo el código de esta sección se compiló y se ejecutó de verdad con `gm-cli` (versión `2.3.0`,
toolchain `GMS2@2026.0.0.23`) el 2026-09-06, en un proyecto de prueba fuera de esta biblioteca.
Las salidas que aparecen entre bloques de código son literales, no ilustrativas.

### 3.1 · `balance.json` en memoria: sólo se añade `prob_critico`

`balance_cargar()` de
[13 · 01 §9.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#93--datos-de-balance-en-included-files)
no cambia: sigue siendo la única función que lee `balance.json`. Lo único que aporta este
documento es leer el campo nuevo al construir la estructura que consume el experimento:

```gml
/// scr_experimento_datos — puente entre balance.json (13 · 01 §9.3) y el experimento de §3.5.
/// No repite balance_cargar(): asume que global.balance ya existe.
function experimento_armas_desde_balance()
{
    return {
        pistola:  global.balance.armas.pistola,
        escopeta: global.balance.armas.escopeta
    };
}
```

### 3.2 · `scr_estadisticas` — media, percentil, desviación e histograma

`mean()` y `median()` existen en el runtime, pero son **variádicas**
(`mean(val0, val1, …)`): sirven para tres o cuatro valores conocidos de antemano, no para un
array de 10 000 elementos que no se puede desplegar como lista de argumentos. GameMaker tampoco
trae una función de percentil (verificado con `buscar.py`: «percentile» NO existe en el runtime
2026.0.0.23). Las cuatro funciones de abajo son las que faltan, con el método del **rango más
cercano** (*nearest-rank*) para el percentil — el más simple de implementar y el habitual para
leer un umbral de cola en telemetría de videojuegos:

```gml
// ═══════════════════════════════════════════════════════════════════════
//  scr_estadisticas — lo que mean()/median() no cubren: arrays grandes
// ═══════════════════════════════════════════════════════════════════════

/// @description Media de un array de reales. Usa array_reduce, no mean(): mean() es
///              variádica y no acepta un array de miles de elementos como un solo argumento.
function stats_media(_valores)
{
    var _n = array_length(_valores);
    if (_n == 0) return 0;
    return array_reduce(_valores, function(_previo, _actual) { return _previo + _actual; }) / _n;
}

/// @description Desviación estándar poblacional. _media se pasa ya calculada para no
///              recorrer el array dos veces si ya la tenías.
function stats_desviacion(_valores, _media)
{
    var _n = array_length(_valores);
    if (_n == 0) return 0;
    var _suma_cuadrados = 0;
    for (var _i = 0; _i < _n; _i++)
    {
        _suma_cuadrados += sqr(_valores[_i] - _media);
    }
    return sqrt(_suma_cuadrados / _n);
}

/// @description Percentil por el método del rango más cercano (nearest-rank). El array
///              DEBE venir ya ordenado ascendente — llama a array_sort(_valores, true) antes.
/// @param {Array<Real>} _valores_ordenados
/// @param {Real}        _p   0..100
function stats_percentil(_valores_ordenados, _p)
{
    var _n = array_length(_valores_ordenados);
    if (_n == 0) return 0;
    var _indice = clamp(ceil(_p / 100 * _n) - 1, 0, _n - 1);
    return _valores_ordenados[_indice];
}

/// @description Histograma ASCII de N cubos, para pegar directamente en show_debug_message
///              o en el log de gm-cli run — la manera más barata de "ver" una distribución
///              sin exportar nada a una hoja de cálculo.
function stats_histograma_ascii(_valores_ordenados, _cubos = 10)
{
    var _n = array_length(_valores_ordenados);
    if (_n == 0) return "(sin datos)";

    var _min = _valores_ordenados[0];
    var _max = _valores_ordenados[_n - 1];
    var _ancho = max(_max - _min, 1);
    var _cuentas = array_create(_cubos, 0);

    for (var _i = 0; _i < _n; _i++)
    {
        var _c = floor((_valores_ordenados[_i] - _min) / _ancho * _cubos);
        _c = clamp(_c, 0, _cubos - 1);
        _cuentas[_c]++;
    }

    var _pico = 1;
    for (var _i = 0; _i < _cubos; _i++) { _pico = max(_pico, _cuentas[_i]); }

    var _texto = "";
    for (var _i = 0; _i < _cubos; _i++)
    {
        var _barras = round(_cuentas[_i] / _pico * 30);
        _texto += string_repeat("█", _barras) + $" ({_cuentas[_i]})\n";
    }
    return _texto;
}
```

Verificado con una prueba (mini-framework de
[13 · 10 §3.1](./10%20-%20Testing%20y%20QA.md#31-el-script-scr_pruebas)):

```gml
probar("stats_media y stats_percentil sobre un array conocido", function() {
    var _v = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    afirmar_igual(stats_media(_v), 5.5);
    afirmar_igual(stats_percentil(_v, 50), 5);
    afirmar_igual(stats_percentil(_v, 100), 10);
});
```

```
│    ok    stats_media y stats_percentil sobre un array conocido  (0.01 ms)
```

### 3.3 · El combate simulado, con azar inyectado y reproducible

El combate de la simulación amplía `calcular_dano()` de
[13 · 10 §3.2](./10%20-%20Testing%20y%20QA.md#32-una-tanda-de-pruebas-real) —se reutiliza tal
cual, sin cambiar una línea— a una partida completa, turno a turno, hasta que uno de los dos
llega a cero. Y, siguiendo la regla de
[13 · 10 §2.2](./10%20-%20Testing%20y%20QA.md#22-inyecta-lo-que-no-controlas-azar-reloj-y-entrada),
el azar **no** llama a `random()` directamente: usa la misma `AzarReproducible` (un congruencial
lineal de 32 bits) que ese apartado ya define, para que 10 000 combates sean **reproducibles**
con una semilla y comparables antes/después de tocar un número del balance.

```gml
// ═══════════════════════════════════════════════════════════════════════
//  scr_simulacion_combate — un combate completo, no un único cálculo de TTK
// ═══════════════════════════════════════════════════════════════════════

/// @desc Fuente de azar reproducible (13 · 10 §2.2, reutilizada tal cual).
function AzarReproducible(_semilla) constructor
{
    estado = _semilla;

    static siguiente = function()
    {
        estado = (estado * 1103515245 + 12345) % 2147483648;
        return estado / 2147483648;
    }

    static entero_hasta = function(_n)
    {
        return floor(siguiente() * (_n + 1));
    }
}

/// @description Daño final tras armadura y crítico (13 · 10 §3.2, reutilizada tal cual).
function calcular_dano(_base, _armadura, _critico)
{
    if (!is_numeric(_base) || _base < 0) { throw $"dano base invalido: {_base}"; }
    var _absorcion = clamp(_armadura, 0, 0.9);
    var _dano = _base - (_base * _absorcion);
    if (_critico) { _dano *= 2; }
    return floor(_dano);
}

/// @description Combate completo, turno a turno. El jugador ataca primero cada ronda;
///              si el enemigo no muere, responde. Se detiene cuando uno de los dos llega
///              a 0 de vida o al límite de turnos (una End condition, en vocabulario de §2.1).
/// @param {Struct} _arma      { dano, cadencia, prob_critico } — de balance.json (§3.1)
/// @param {Struct} _enemigo   { vida, dano } — de balance.json (13 · 01 §9.3)
/// @param {Struct} _azar      Instancia de AzarReproducible
/// @param {Real}   _armadura_jugador  0..0.9
/// @returns {Struct} { turnos, gano_jugador }
function simular_combate(_arma, _enemigo, _azar, _armadura_jugador = 0)
{
    var _vida_enemigo = _enemigo.vida;
    var _vida_jugador = 100;
    var _turno = 0;
    var _limite_turnos = 500;   // corta combates que no deberían durar tanto: fallo de balance

    while (_vida_enemigo > 0 && _vida_jugador > 0 && _turno < _limite_turnos)
    {
        _turno++;
        var _critico = (_azar.siguiente() < _arma.prob_critico);   // la Gate random de §2.1
        _vida_enemigo -= calcular_dano(_arma.dano, 0, _critico);
        if (_vida_enemigo <= 0) break;
        _vida_jugador -= calcular_dano(_enemigo.dano, _armadura_jugador, false);
    }

    return { turnos: _turno, gano_jugador: (_vida_enemigo <= 0) };
}
```

Verificado, incluida la reproducibilidad (misma semilla ⇒ mismo resultado, la propiedad que hace
falta para comparar «antes» y «después» de un cambio de balance):

```gml
probar("simular_combate termina y declara un ganador", function() {
    var _arma = { dano: 15, cadencia: 12, prob_critico: 0.1 };
    var _enemigo = { vida: 30, dano: 8 };
    var _resultado = simular_combate(_arma, _enemigo, new AzarReproducible(1));
    afirmar_cierto(_resultado.turnos > 0);
});

probar("la misma semilla produce el mismo resultado (13 · 10 §5.3)", function() {
    var _arma = { dano: 15, cadencia: 12, prob_critico: 0.5 };
    var _enemigo = { vida: 30, dano: 8 };
    var _a = simular_combate(_arma, _enemigo, new AzarReproducible(99));
    var _b = simular_combate(_arma, _enemigo, new AzarReproducible(99));
    afirmar_igual(_a.turnos, _b.turnos);
    afirmar_igual(_a.gano_jugador, _b.gano_jugador);
});
```

```
│    ok    simular_combate termina y declara un ganador  (0.01 ms)
│    ok    la misma semilla produce el mismo resultado (13 · 10 §5.3)  (0.01 ms)
```

> ⚠️ `random_set_seed()` también existe y fija la secuencia global del motor, pero
> [13 · 10 §2.2](./10%20-%20Testing%20y%20QA.md#22-inyecta-lo-que-no-controlas-azar-reloj-y-entrada)
> ya avisa de que **no aísla**: cualquier otra llamada a `random()` en el mismo frame —una
> partícula, un sonido con variación de tono— desplaza la secuencia y dos corridas con «la misma
> semilla» dejan de ser iguales. Para 10 000 combates que se van a comparar entre sí, una fuente
> de azar propia e inyectada es la única forma segura.

### 3.4 · El Converter, en GML

El comportamiento verificado en §2.1 —N requisitos que se consumen, exactamente 1 salida que se
produce, y si falta cualquier requisito no se produce nada— se traduce a una única función que
opera sobre cualquier receta de la sub-tabla `crafteo` de §2.2:

```gml
/// @description Ejecuta un Converter de Machinations: consume TODOS los requisitos y produce
///              la salida, o no hace nada si falta cualquiera de ellos (comportamiento
///              verificado contra machinations.io/docs/converters-traders).
/// @param {Struct} _receta      { requisitos: {...}, produccion: {...} } — de crafteo en balance.json
/// @param {Struct} _inventario  Se modifica in-place SOLO si la conversión se ejecuta.
/// @returns {Bool} true si se ejecutó, false si faltaban requisitos.
function convertidor_ejecutar(_receta, _inventario)
{
    var _requisitos = _receta.requisitos;
    var _claves = struct_get_names(_requisitos);

    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        var _necesario  = struct_get(_requisitos, _claves[_i]);
        var _disponible = variable_struct_exists(_inventario, _claves[_i]) ? _inventario[$ _claves[_i]] : 0;
        if (_disponible < _necesario) { return false; }    // falta uno solo: no produce nada
    }

    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        _inventario[$ _claves[_i]] -= struct_get(_requisitos, _claves[_i]);
    }

    var _productos = struct_get_names(_receta.produccion);
    for (var _i = 0; _i < array_length(_productos); _i++)
    {
        var _clave    = _productos[_i];
        var _cantidad = struct_get(_receta.produccion, _clave);
        _inventario[$ _clave] = (variable_struct_exists(_inventario, _clave) ? _inventario[$ _clave] : 0) + _cantidad;
    }

    return true;
}
```

```gml
probar("el convertidor no produce nada si falta un requisito", function() {
    var _receta = { requisitos: { hierba: 2, frasco_vacio: 1 }, produccion: { pocion_curacion: 1 } };
    var _inventario = { hierba: 1, frasco_vacio: 1 };
    afirmar_cierto(!convertidor_ejecutar(_receta, _inventario));
    afirmar_igual(_inventario.hierba, 1, "no debe consumir nada si falla");
});

probar("el convertidor consume los requisitos y produce la salida", function() {
    var _receta = { requisitos: { hierba: 2, frasco_vacio: 1 }, produccion: { pocion_curacion: 1 } };
    var _inventario = { hierba: 2, frasco_vacio: 1 };
    afirmar_cierto(convertidor_ejecutar(_receta, _inventario));
    afirmar_igual(_inventario.hierba, 0);
    afirmar_igual(_inventario.pocion_curacion, 1);
});
```

```
│    ok    el convertidor no produce nada si falta un requisito  (0.01 ms)
│    ok    el convertidor consume los requisitos y produce la salida  (0.01 ms)
```

### 3.5 · Envolver la simulación en una prueba real: el gate de CI

Esta es la pieza que cierra el círculo con `13 · 01 §2.3` y con `13 · 10`: en vez de imprimir
10 000 resultados y leerlos a ojo, la simulación se envuelve en un `probar()` normal, con una
`afirmar_*` al final. Si el balance se rompe, `gm-cli run` sale con
`###game_end###1` (`13 · 10 §3.4`) igual que si hubiera fallado una prueba unitaria cualquiera —
sin que nadie tenga que abrir el juego y jugarlo:

```gml
probar("ninguna arma debería ganar más del 90% de los combates contra el bruto", function() {
    var _armas = experimento_armas_desde_balance();   // pistola y escopeta de balance.json
    var _bruto = global.balance.enemigos.bruto;

    var _metricas = experimento_armas(_armas, _bruto, 10000);

    afirmar_cierto(_metricas.pistola.tasa_victoria  <= 0.90, "pistola domina o es dominada");
    afirmar_cierto(_metricas.escopeta.tasa_victoria <= 0.90, "escopeta domina o es dominada");
});
```

La función `experimento_armas()` que orquesta todo lo de §3.2-§3.3-§3.6 y devuelve las métricas
para poder afirmarlas:

```gml
/// @description Corre N combates por arma contra el mismo enemigo (comparación CONTROLADA:
///              el uso es igual para todas a propósito, porque aquí se mide VICTORIA, no
///              preferencia — la preferencia es un experimento distinto, ver §3.6).
/// @param {Real} _semilla  Misma semilla = mismos combates, siempre. Cámbiala para confirmar
///                         que el resultado no es un capricho de una tirada rara (§2.3).
/// @returns {Struct}  una entrada por arma: { media, p50, p90, p99, cv, tasa_victoria }
function experimento_armas(_armas, _enemigo, _n_por_arma, _semilla = 12345)
{
    var _nombres = struct_get_names(_armas);
    dominancia_iniciar(_nombres);   // 13 · 15 §11.2, reutilizada tal cual
    victoria_iniciar(_nombres);     // nueva, §3.6

    var _azar = new AzarReproducible(_semilla);
    var _metricas = {};

    for (var _i = 0; _i < array_length(_nombres); _i++)
    {
        var _nombre = _nombres[_i];
        var _arma   = struct_get(_armas, _nombre);
        var _turnos = array_create(_n_por_arma, 0);

        for (var _j = 0; _j < _n_por_arma; _j++)
        {
            var _resultado = simular_combate(_arma, _enemigo, _azar);
            _turnos[_j] = _resultado.turnos;
            victoria_registrar(_nombre, _resultado.gano_jugador);
            if (_resultado.gano_jugador) { dominancia_registrar(_nombre); }
        }

        array_sort(_turnos, true);
        var _media = stats_media(_turnos);
        var _desv  = stats_desviacion(_turnos, _media);
        var _cv    = (_media == 0) ? 0 : (_desv / _media);
        var _v     = struct_get(global.victoria, _nombre);

        struct_set(_metricas, _nombre, {
            media: _media,
            p50:   stats_percentil(_turnos, 50),
            p90:   stats_percentil(_turnos, 90),
            p99:   stats_percentil(_turnos, 99),
            cv:    _cv,
            tasa_victoria: (_v.partidas == 0) ? 0 : (_v.ganadas / _v.partidas)
        });

        show_debug_message($"--- {_nombre} ({_n_por_arma} combates) ---");
        show_debug_message($"  turnos: media {string_format(_media,1,2)} · p50 {stats_percentil(_turnos,50)}"
                          + $" · p90 {stats_percentil(_turnos,90)} · p99 {stats_percentil(_turnos,99)}");
        show_debug_message($"  coeficiente de variacion: {string_format(_cv,1,3)}");
    }

    victoria_informe();
    dominancia_informe(0.60);
    return _metricas;
}
```

**Salida real de `gm-cli run --target mac`** (2026-09-06, runtime `2026.0.0.23`, con la pistola
de 15 de daño/12 de cadencia y la escopeta de 54 de daño/45 de cadencia de §2.2 — DPS nominal
casi idéntico: 75 frente a 72 por segundo):

```
│  --- pistola (10000 combates) ---
│    turnos: media 4.00 · p50 4 · p90 4 · p99 4
│    coeficiente de variacion: 0.000
│  --- escopeta (10000 combates) ---
│    turnos: media 3.71 · p50 4 · p90 4 · p99 4
│    coeficiente de variacion: 0.128
│  [victoria] pistola: 0% (0/10000)
│  [victoria] escopeta: 100% (10000/10000)
│  [uso] pistola: 0%
│  [uso] escopeta: 100% <- posible dominante
│  [rendimiento] 2 x 10000 combates simulados en 76.1 ms
│    FALLO ninguna arma debería ganar más del 90% de los combates contra el bruto  (76.15 ms)
│            esperaba true, obtuve 0. escopeta domina o es dominada
│  7 pruebas | 15 aserciones | 1 fallidas | 76.7 ms
│  RESULTADO: FALLO
│  ###game_end###1
```

**Esto es exactamente el hallazgo que esta técnica existe para producir.** El DPS nominal (75
frente a 72 golpes por segundo) sugiere paridad — es lo que `13 · 01 §4.4` calcularía a mano. La
simulación demuestra una dominancia absoluta: la escopeta gana el 100 % de las veces, la pistola
el 0 %, **con dos semillas distintas** (verificado también con `_semilla = 777`, mismo
resultado). La causa no es un error del código, es una frontera de umbral: el jugador tiene sus
propios 100 PV corriendo en paralelo, y el bruto le devuelve 25 por ronda — exactamente 4 rondas
antes de morir. La escopeta mata al bruto (180 de vida) en 4 golpes (216 de daño acumulado);
la pistola necesita 12. Como el jugador ataca primero cada ronda (§3.3), la escopeta cruza el
umbral de 180 justo a tiempo, antes de que el bruto complete su cuarto golpe; la pistola nunca
llega. Ninguna cuenta de DPS por sí sola iba a revelar esto, porque el TTK de cada arma no
compite contra un número absoluto: compite contra el reloj de vida del jugador, y esa carrera
sólo se ve corriendo el combate de verdad. (La corrección —subir la cadencia de la pistola, bajar
la vida del bruto, o dar armadura al jugador— es una decisión de diseño; lo que aporta la
simulación es la certeza de que hace falta, antes de que la descubra un jugador humano.)

### 3.6 · Cazar dominancia: tasa de uso frente a tasa de victoria

`13 · 15 §11.2` ya mide **tasa de uso** a partir de telemetría real: cuenta qué elige la gente
que ya está jugando. Eso responde «¿qué usa la gente?», no «¿qué debería ganar si todo el mundo
lo usara por igual?» — son dos preguntas que se contestan con dos diseños de experimento
distintos, y confundirlas lleva a conclusiones opuestas:

| | Tasa de **uso** alta | Tasa de **uso** baja |
|---|---|---|
| Tasa de **victoria** alta | Dominancia real: sube el coste o baja el poder (`13 · 15 §8.3`) | Opción infravalorada: nadie la prueba aunque gane cuando se usa — problema de comunicación/UI, no de números |
| Tasa de **victoria** baja | El jugador *cree* que es la mejor opción y no lo es — revisa cómo se presenta, no el balance | Sin problema: coincide uso y rendimiento bajos |

Este documento reutiliza **sin cambiar una línea** las tres funciones de dominancia de
[13 · 15 §11.2](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md#112--telemetría-de-dominancia-schreiber)
(`dominancia_iniciar`, `dominancia_registrar`, `dominancia_informe`) — la única diferencia es que
en aquel documento las alimenta un jugador humano jugando de verdad, y aquí las alimenta
`experimento_armas()` de §3.5. Lo que sí es nuevo aquí es la **tasa de victoria**, que
`13 · 15` no mide porque no la necesita para telemetría real (ahí el uso ya viene sesgado por
gente de verdad eligiendo):

```gml
function victoria_iniciar(_opciones)
{
    global.victoria = {};
    for (var _i = 0; _i < array_length(_opciones); _i++)
    {
        struct_set(global.victoria, _opciones[_i], { partidas: 0, ganadas: 0 });
    }
}

function victoria_registrar(_opcion, _gano)
{
    if (!struct_exists(global.victoria, _opcion)) return;
    var _v = struct_get(global.victoria, _opcion);
    _v.partidas++;
    if (_gano) { _v.ganadas++; }
}

function victoria_informe()
{
    var _nombres = struct_get_names(global.victoria);
    for (var _i = 0; _i < array_length(_nombres); _i++)
    {
        var _v = struct_get(global.victoria, _nombres[_i]);
        var _tasa = (_v.partidas == 0) ? 0 : (_v.ganadas / _v.partidas);
        show_debug_message($"[victoria] {_nombres[_i]}: {string(round(_tasa * 100))}% ({_v.ganadas}/{_v.partidas})");
    }
}
```

En el experimento de §3.5, uso y victoria coinciden (50 % de uso forzado, 0/100 % de victoria)
porque el diseño del experimento fue **controlado a propósito**: la pregunta que respondía era
«¿cuál gana?», no «¿cuál se usa?». Para responder la segunda pregunta con una simulación (en vez
de esperar a la telemetría real de `13 · 15 §11.2`) hace falta modelar una **persona de
jugador** — una regla de elección, no una elección uniforme — y comparar su tasa de uso
resultante contra su tasa de victoria; eso es exactamente lo que hizo el estudio de caso F2P de
§1.3 con sus cuatro perfiles de jugador (grinder puro, híbrido, comprador…), y es la extensión
natural de este documento en cuanto el proyecto tenga más de dos opciones que comparar.

### 3.7 · Varianza excesiva: el coeficiente de variación

El **coeficiente de variación** (`CV = desviación estándar ÷ media`) normaliza la dispersión para
poder comparar opciones con medias distintas — una desviación de 2 turnos significa cosas muy
distintas si la media es 4 turnos o 40. Ya sale calculado en `experimento_armas()` de §3.5;
`0,000` para la pistola (siempre muere en exactamente 4 rondas, sin ninguna variación posible en
el resultado) y `0,128` para la escopeta (algunos combates terminan en 3 rondas en vez de 4,
cuando un crítico adelanta el golpe decisivo).

| CV | Lectura |
|---|---|
| ≈ 0 | El resultado es (casi) siempre el mismo — el azar no llega a alcanzar el umbral que decide la partida (§3.5) |
| 0,15 – 0,40 | Rango sano habitual: hay variación perceptible sin que el resultado se sienta arbitrario |
| > 0,40 | Volatilidad alta: revisa si es la variedad deliberada de un roguelike (Costikyan, `13 · 15 §7`) o una fuente de frustración |

> ⚠️ Estos rangos son una heurística de oficio para orientar la lectura, no un umbral medido en
> una fuente primaria: no hay un «0,40 correcto» universal — lo que hay es la comparación entre
> las opciones de tu propio juego al mismo nivel de coste, que es lo que de verdad importa
> (`13 · 15 §8.1`).

### 3.8 · Ejecutarlo: `gm-cli`, una config propia, y el coste real

Igual que `13 · 10 §3.5` aísla las pruebas unitarias con una config dedicada, una tanda de Monte
Carlo de 10 000+ combates no debería correr en la build que juega la gente. El mismo patrón,
reutilizado sin cambios:

```sh
gm-cli resourcetool eval "config create name=Simulacion parent=Default"
gm-cli run --config Simulacion
```

```gml
// ─── Create de obj_ejecutor_simulacion ───
if (os_get_config() != "Simulacion") { instance_destroy(); exit; }

pruebas_iniciar();
probar("ninguna arma debería ganar más del 90% de los combates contra el bruto", function() {
    // ... el cuerpo de §3.5 ...
});
pruebas_terminar();
```

**El coste medido de verdad**: 2 × 10 000 combates (20 000 partidas simuladas, cada una de 3-4
rondas) se ejecutaron en **76,1 ms** en este Mac — sin acercarse al presupuesto por frame de
[13 · 10 §6.3](./10%20-%20Testing%20y%20QA.md#63-el-presupuesto-por-frame). Para una simulación
mucho más grande (cientos de miles de combates, árboles de habilidades completos de
`13 · 16`), la recomendación sigue siendo correrla como paso de CI dedicado —igual que las
pruebas unitarias— y no dentro del bucle de juego real: 10 000 combates cuestan menos de un
fotograma, pero 10 millones ya no, y una simulación de balance no tiene por qué competir por el
presupuesto de la sala que está jugando alguien de verdad.

---

## 4 · Checklist

- [ ] La economía o el combate que vas a balancear está **dibujado** con el vocabulario de §2.1
      (Pool, Source, Drain, Converter, Trader, Gate) antes de escribir GML.
- [ ] Cada elemento del diagrama tiene su fila correspondiente en `balance.json` (§2.2) — sin
      inventar una estructura paralela a `13 · 01 §9.3`.
- [ ] El azar de la simulación entra por una fuente inyectada (`AzarReproducible`, §3.3), nunca
      por `random()`/`irandom()` directamente — de lo contrario, no hay forma de reproducir un
      resultado raro ni de comparar «antes» y «después» de un cambio.
- [ ] El número de corridas está decidido según qué percentil quieres leer (§2.3): 30 para una
      media, miles para una cola.
- [ ] Lees **media, p50, p90 y p99 juntos** — nunca solo la media (§1.3, §2.4).
- [ ] Mides **tasa de uso** y **tasa de victoria** por separado si vas a hablar de dominancia
      (§3.6) — nunca una sola tasa fusionada.
- [ ] La simulación está envuelta en un `probar()` con una `afirmar_*` que falla si algo se sale
      de rango (§3.5) — no es un `show_debug_message` que hay que leer a ojo cada vez.
- [ ] El coeficiente de variación se compara **entre opciones del mismo nivel de coste**, no
      contra un umbral universal (§3.7).
- [ ] La simulación corre en su propia config de `gm-cli` (§3.8), no compite por el presupuesto
      de fotograma del juego real.
- [ ] Si el resultado es sorprendente (100 %/0 %, como en §3.5), lo has vuelto a correr con **otra
      semilla** antes de creerte que es una estrategia dominante real y no una casualidad de una
      tirada.

---

## 5 · Errores clásicos y cómo evitarlos

- **Comparar DPS nominal y dar el balance por bueno.** El ejemplo de §3.5 es real: 75 frente a 72
  de DPS por segundo sugería paridad; la simulación reveló un 100 %/0 %. El DPS ignora que el
  jugador tiene su propio reloj de vida corriendo en paralelo — simula el combate completo, no
  solo el TTK de una fórmula.
- **Correr 30 corridas y creer que basta para una cola.** 30 corridas confirman una media
  (Ley de los grandes números, §1.2); para un percentil 99 fiable hacen falta miles (§2.3). Con
  30 corridas nunca vas a ver el 1 % de peores casos, que es justo el que un jugador de verdad va
  a vivir alguna vez.
- **Usar `random()`/`irandom()` directamente dentro de la simulación.** Funciona para una corrida
  suelta; en cuanto quieres comparar «antes» y «después» de tocar el balance, o depurar por qué
  la corrida número 4 317 dio un resultado raro, necesitas poder reproducirla exactamente — y
  `random_set_seed()` no aísla (§3.3). Inyecta una fuente propia desde el primer día.
- **Confundir Convertidor con Intercambiador** (ya lo avisa `13 · 01 §4.1`, y aquí se repite
  porque el error concreto es fácil de cometer al traducir Machinations): un Converter destruye
  una cosa y crea otra distinta (2 hierbas + 1 frasco → 1 poción); un Trader sólo cambia de manos
  algo que ya existía (oro por un objeto). Si tu «convertidor» en realidad sólo mueve un recurso
  de un sitio a otro sin transformarlo, es un Trader, y modelarlo como Converter añade o destruye
  recursos sin que lo hayas decidido.
- **Fusionar tasa de uso y tasa de victoria en una sola métrica.** Una opción usada al 90 % con
  50 % de victorias y una opción usada al 10 % con 95 % de victorias cuentan historias opuestas
  (§3.6) — un único número de «popularidad» las confunde a las dos.
- **Simular con un jugador «óptimo» y llamarlo dominancia.** Si el modelo de decisión siempre
  elige matemáticamente lo mejor, vas a medir la matriz de pagos teórica (`13 · 15 §8.1`), que es
  útil, pero no es lo mismo que lo que la gente de verdad va a hacer. Para tasa de **uso**
  realista hace falta un modelo de persona de jugador (§3.6), no un optimizador.
- **No fijar un límite de turnos/rondas en el bucle de simulación.** Un combate mal balanceado
  (ninguno de los dos baja de cierto umbral, por ejemplo con armadura al 90 % y daño insuficiente
  para superarla) puede no terminar nunca; `_limite_turnos` en `simular_combate()` (§3.3) es la
  misma End condition de seguridad que `13 · 01 §4.4` recomienda para un jefe con demasiadas
  fases.
- **Olvidar que `gm-cli run` no propaga el código de salida del juego** (`13 · 10 §3.4`): si
  automatizas esta simulación en CI, lee la línea `###game_end###` de la salida, no `$?` del
  proceso.

---

## Ver también

- [13 · 01 — Diseño de juego: core loop, mecánicas, balance y dificultad](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) —
  el vocabulario de economía (§4.1), las fórmulas de TTK y curva de coste (§4.4) y el pipeline
  hoja de cálculo → `balance.json` (§4.5, §9.3) que este documento simula en vez de calcular a mano.
- [13 · 10 — Testing y QA](./10%20-%20Testing%20y%20QA.md) — `scr_pruebas`, `probar()` y
  `afirmar_*` (§3.1), la fuente de azar inyectable `AzarReproducible` (§2.2) y el aviso sobre
  `gm-cli run` y el código de salida (§3.4), reutilizados sin cambios en §3.
- [13 · 15 — Teoría del diseño: el canon en una tarde](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md) —
  la matriz de pagos y la eliminación iterativa de Schreiber (§8), y `dominancia_iniciar/
  registrar/informe` (§11.2), reutilizadas tal cual y alimentadas aquí con partidas simuladas.
- [13 · 16 — Progresión: árboles de habilidades, desbloqueos y meta-progresión](./16%20-%20Progresión%20-%20árboles%20de%20habilidades%2C%20desbloqueos%20y%20meta-progresión.md) —
  qué hace que una combinación de nodos sea un «build» (§1.6) y el antipatrón de la ruta
  dominante que este documento da ahora el método de cazar por simulación en vez de a ojo.
- [13 · 18 — Diseño de combate y de jefes](./18%20-%20Diseño%20de%20combate%20y%20de%20jefes.md) —
  el DPS de diseño junto al TTK por fase (§2.8) y la plantilla de balance de jefe en JSON
  (§4.4): el sistema de combate de referencia, del que el de este documento es una versión de
  ocho líneas hecha solo para que el ejemplo compile.
- [04 · 32 — Sistema de daño y efectos de estado](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) —
  el motor de daño y armadura real, del que `calcular_dano()` de este documento es la versión
  mínima de `13 · 10 §3.2`.

---

## Fuentes

Todas consultadas el **2026-09-06**, con `curl -sL -A "Mozilla/5.0"` y con la herramienta de
lectura de páginas web (`WebFetch`); `WebSearch` no se usó, por indicación del encargo. El sitio
de Machinations sirve su documentación como una aplicación Nuxt con el contenido embebido en un
bloque `<script>`; el texto citado abajo se extrajo de ese bloque tras descartar el andamiaje de
la SPA, no de una interpretación del HTML renderizado — cada cita se verificó localizando el
párrafo exacto en el HTML descargado.

**Verificadas en vivo, contenido leído**

- Machinations — *Gates* — <https://machinations.io/docs/gates> (HTTP 200) · deterministic
  frente a random, los 4 modos de trigger, «Gates support Resource Connections, State
  Connections, or BOTH» (§2.1)
- Machinations — *Drains* — <https://machinations.io/docs/drains> (HTTP 200) · «consume
  Resources from Pools and other Nodes… permanently removed from your games' economy» (§2.1)
- Machinations — *Pools* — <https://machinations.io/docs/pools> (HTTP 200) · Overflow y
  Capacity, «A Pool cannot have negative values except when influenced by a State Connection»
  (§2.1)
- Machinations — *Sources* — <https://machinations.io/docs/sources> (HTTP 200) · «produce
  unlimited numbers of Resources… no input Resource Connections» (§2.1)
- Machinations — *Registers* — <https://machinations.io/docs/registers> (HTTP 200) · «alter the
  state of Nodes or influence the flow of Resources based on the computation of multiple
  inputs» (§2.1)
- Machinations — *Converters & Traders* — <https://machinations.io/docs/converters-traders>
  (HTTP 200) · «Converters… need at least one input and one output», «Traders need at least two
  input and two output Resource Connections… require that the two types of Resources… are
  differentiated through Filter (Colour Coding)» (§2.1); también la inconsistencia de la letra
  `(V)` compartida, citada tal cual con su aviso (§2.1)
- Machinations — *Resource Connections* — <https://machinations.io/docs/resource-connections>
  (HTTP 200) · tipos de fórmula Number/Chance, «the origin node will have an X percent chance to
  transfer one resource» (§2.1)
- Machinations — *Activation Modes* — <https://machinations.io/docs/activation-modes> (HTTP 200) ·
  los 4 Trigger Modes con su definición textual (Passive/Interactive/Automatic/Enabling) (§2.1)
- Machinations — *End Conditions* — <https://machinations.io/docs/end-conditions> (HTTP 200) ·
  «stops running immediately when any End Condition is fulfilled» (§2.1)
- Machinations — *The Monte Carlo Simulations* —
  <https://machinations.io/docs/the-monte-carlo-simulations> (HTTP 200) · la cita textual de la
  Ley de los grandes números y el ejemplo de los dos dados/probabilidad de 7 (§1.2)
- Machinations Academy — *Sources: generating resources* —
  <https://www-content.machinations.io/academy/project-loot-and-craft/sources-generating-resources/>
  (HTTP 200) · notación de dados (`D6`, `4D10`) y `random(min,max)`/`randomInt(min,max)` (§2.1)
- Machinations Academy — *Predictions: estimating KPIs* —
  <https://www-content.machinations.io/academy/project-loot-and-craft/predictions-estimating-kpis/>
  (HTTP 200) · «it is required that at least 30 predictions are run to get a more accurate
  value of the parameter», citando la Ley de los grandes números (§2.3)
- Machinations — estudio de caso *Balancing F2P Economies: Simulating Player Personas and
  Progression Curves with Machinations* —
  <https://www-content.machinations.io/articles/balancing-f2p-economies-simulating-player-personas-and-progression-curves-with-machinations/>
  (HTTP 200) · las dos citas textuales sobre media frente a distribución y el hallazgo del top
  2 % F2P frente al 19 % premium (§1.3)
- Machinations — *Balancing a Battle Pass* —
  <https://www-content.machinations.io/articles/simulating-for-game-balance/> (HTTP 200) ·
  ejemplo real de Random Sorting Gates con probabilidad, Predictions y *Play History* como
  bucle de iteración de balance
- Machinations — *Balancing difficulty and score* (caso *Stack Jump*) —
  <https://www-content.machinations.io/articles/balancing-difficulty-score/> (HTTP 200) · «The
  Source (triangle-shaped component)», la Gate de fallo/éxito al 5 %/95 %, y el uso de State
  Connections y End Condition en un juego real publicado (§2.1)

**No abiertas o fuera de alcance esta sesión — sin URL de cita, marcadas con ⚠️ en el texto**

- Ernest Adams y Joris Dormans, *Game Mechanics: Advanced Game Design* (2012) — el libro que
  originó Machinations ya está citado en
  [13 · 01 §4.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#41--el-vocabulario-correcto);
  no se reabrió esta sesión para evitar una cita duplicada de una fuente ya verificada por otro
  documento de esta biblioteca.
- Un umbral numérico único para «coeficiente de variación sano» (§3.7) y para «cuántas corridas
  hacen falta por percentil» (§2.3) más allá de la aritmética `100 ÷ (1 − p)` — no existe una
  fuente primaria abierta esta sesión que fije esos números; se presentan explícitamente como
  heurística de oficio.
- El icono exacto de cada nodo de Machinations tal y como lo pinta el editor (más allá de
  Source = triángulo y Gate = diamante, ambos confirmados por texto literal de la documentación)
  — los glifos ASCII del diagrama de §2.1 son una convención propia para dibujar a mano, no una
  captura verificada de la interfaz.
