# 22 · Diseño de mundo y exploración

> Cómo se **distribuyen las razones para explorar** por un mundo de juego, y cómo esa
> distribución se convierte en decisiones concretas de mapa, brújula y viaje rápido — no en un
> accidente que se descubre en el playtest. Cierra con el **grafo de bloqueos**: el artefacto de
> papel que un metroidvania necesita dibujar antes de abrir el Room Editor, y el código que lo
> valida por alcanzabilidad en vez de fiarlo al ojo.
>
> **Lo que NO cubre este documento** (y dónde está, para no repetirlo): la **estructura** de un
> mundo —lineal, hub, mundo abierto por zonas, metroidvania o procedural, con su coste y su
> receta— es de
> [13 · 02 §2.6](./02%20-%20Diseño%20de%20niveles.md#26-tipos-de-estructura); aquí se explica
> **cuándo** elegir cada una, no qué es cada una. La **legibilidad de una sala** —landmarks,
> *weenies*, líneas de guía, *gating* duro/blando/de conocimiento— es de
> [13 · 02 §1.3-§1.4](./02%20-%20Diseño%20de%20niveles.md#13-legibilidad-puntos-de-referencia-weenies-y-líneas-de-guía);
> aquí se extiende a la escala del **mundo**, no de la sala. La **implementación completa de un
> metroidvania** —transiciones entre rooms, `WorldState`, gates, minimapa por datos— es de
> [04 · 06](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md); aquí se diseña el grafo
> que esa implementación ejecuta, no se repite su código de transición. La **pantalla de mapa
> completo**, con desplazamiento, zoom y viaje rápido ya construidos, es de
> [13 · 05 §3.5 j](./05%20-%20UI%20y%20UX%20de%20juego.md#j-pantalla-de-mapa-completo-desplazamiento-y-zoom-salas-y-viaje-rápido);
> aquí sólo se añade **cuándo** permitirlo, no cómo se dibuja. El **sistema de cámara**
> —atractores, detractores, cinemáticas— es de
> [13 · 19](./19%20-%20Cámaras%20de%20juego%20-%20encuadre,%20seguimiento%20y%20control.md); aquí
> se usa, no se repite. El **grafo de gating de mecánicas sueltas**, como diagrama de papel, ya
> vive en
> [13 · 14 §2.20](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#220--el-catálogo-de-diagramas-de-diseño);
> aquí se aplica la misma idea a escala de **zonas de mundo** y se le añade la validación
> automática que aquel documento no da.

---

## 1 · Los principios

### 1.1 El bucle: curiosidad → observación → navegación → recompensa

Explorar no es caminar: es resolver, una y otra vez, el mismo bucle de cuatro fases. Es la
especialización a nivel de mundo del bucle de acción de
[13 · 01 §2.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#22--dibujarlo-antes-de-programar):
en vez de «acción → sistema → cambio», aquí la unidad es «pregunta → respuesta parcial → apuesta
→ pago».

| Fase | Qué pasa | La pregunta del jugador | Falla si… |
|---|---|---|---|
| **1. Curiosidad** | Percibe un misterio sin resolver: una silueta lejana, un color que no encaja, un sonido fuera de vista | «¿Qué es eso?» | No hay nada que perciba: el mundo no plantea preguntas (pasillo homogéneo, sin *landmarks*, 13 · 02 §1.3) |
| **2. Observación** | Reúne información a distancia sin comprometerse: mira el *landmark*, calcula si hay ruta, decide si vale el rodeo | «¿Cómo llego, y merece la pena?» | La única forma de saberlo es ir (coste de oportunidad ciego) — o el mapa/brújula ya lo responde por él (§1.3) |
| **3. Navegación** | Compromete tiempo y riesgo: camina, salta, esquiva, quizá retrocede sobre terreno conocido | «¿Voy bien?» | El camino no confirma progreso: sin nuevos *landmarks* a medio camino (13 · 02 §1.3) el jugador se rinde antes de llegar |
| **4. Recompensa** | Encuentra algo que justifica el viaje: material, narrativo, de competencia (una habilidad) o puramente estético (una vista) | «¿Mereció la pena, y qué veo ahora?» | La recompensa no **recontextualiza** nada (04 · 06 §1) — o no deja visible el siguiente gancho de curiosidad |

> 🔺 **El bucle tiene que reiniciarse solo.** La fase 4 no termina en «recompensa recogida»:
> termina en **una fase 1 nueva ya visible** desde el punto al que has llegado. Es la razón por la
> que las atalayas funcionan en tantos juegos de mundo abierto: no es el desbloqueo de mapa lo que
> engancha, es que desde arriba se ven dos o tres siluetas nuevas que antes no estaban ahí. Un
> mundo donde la recompensa es un callejón sin salida (recoges el objeto y das media vuelta, sin
> nada nuevo que mirar) rompe el bucle en su punto más caro: justo después de haber pagado el
> coste de navegación.

Esta es también la lente que le falta al canon de
[13 · 15 §4.2](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md#42--un-subconjunto-operativo-de-18-lentes)
para aplicarse a un mundo entero en vez de a un sistema aislado: la **Lente de la Curiosidad**
pregunta «¿qué preguntas se hace el jugador, y cuáles respondo yo y cuáles dejo abiertas?» — aquí
esa pregunta se contesta con un método de cuatro fases, no con una intuición.

Dos combinaciones rotas, aparte de las de la tabla, merecen nombre propio porque se repiten:

- **Recompensa ciega.** Un cofre en campo abierto sin ningún *landmark* ni señal previa no es
  «una sorpresa agradable»: salta las fases 1-3 y el jugador lo vive como suerte, no como mérito.
  Es indistinguible de un generador aleatorio de botín — no enseña a leer el mundo.
- **Navegación sin recompensa.** El peor pecado del diseño de mundo: un pasillo largo, con
  *landmarks* correctos y ritmo correcto (13 · 02 §1.2), que termina en nada. El jugador aprende a
  desconfiar de la fase 1 la próxima vez que vea un *landmark* — el coste no es local, contamina
  el resto del mundo.

### 1.2 Densidad de puntos de interés, y el coste de amontonarlos

Un **punto de interés** (POI) es cualquier cosa que paga la fase 4 del bucle: un cofre, un jefe
opcional, un mirador, un objeto de *lore*, un atajo que se desbloquea desde el otro lado. No lo
son los pasillos, las salas de combate obligatorias ni la decoración pura — eso es tejido
conectivo, y su ritmo ya está resuelto en 13 · 02 §1.2.

**La métrica correcta es POIs por minuto de recorrido, no POIs por metro cuadrado.** La
percepción de densidad la gobierna el tiempo que el jugador tarda en cruzar el espacio —frenado
por obstáculos, combates y *backtracking*—, no el área en píxeles. Dos zonas con la misma
superficie pero controles de movimiento distintos (una con doble salto, otra sin él) tienen
densidades percibidas distintas con el mismo número de POIs.

| Peso del POI | Qué es | Cuota orientativa (por zona de ~3-5 min de recorrido) |
|---|---|---|
| **Crítico** | Habilidad, llave, o zona que el juego exige para progresar | 1 (casi nunca más de uno por zona — es el `mundo_zonas_distancias` de §3.2 el que ya obliga a pasar por aquí) |
| **Opcional mayor** | Jefe opcional, mejora de estadística grande, atajo permanente | 1-2 |
| **Opcional menor** | *Lore*, cosmético, moneda, mejora pequeña | 2-4 |
| **Decorativo** | No interactivo: silueta, sonido ambiental, parte del *parallax* | Sin límite — es tejido conectivo, no cuenta como POI |

> ⚠️ La cuota de la tabla es un punto de partida razonable para un metroidvania de ritmo medio, no
> una medición: ajústala con el playtest cuantitativo de
> [13 · 01 §3.4](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#34-medir-la-dificultad-con-datos-no-con-opiniones)
> (mediana de tiempo real por zona, no la media) antes de tratarla como definitiva.

La distribución física de los POIs dentro de una zona —que no se amontonen ni dejen calvas— es un
problema ya resuelto: el muestreo de Poisson-disc de
[13 · 07 §4](./07%20-%20Generación%20procedural%20avanzada.md#4--poisson-disc-distribuir-cosas-sin-que-se-amontonen)
se reutiliza sin cambios en §3.3; aquí sólo se decide la **cuota** que ese algoritmo recorta.

### 1.3 El mapa y la brújula son una decisión de diseño, no un *widget*

El mapa y la brújula no son UI que se añade al final: son el mando que regula cuánto peso tiene la
**fase 2 (observación)** del bucle de §1.1. Cuanto más automatiza el mapa esa fase, menos falta
hace que el jugador mire el mundo — y es una decisión que hay que tomar como **pilar de diseño**
([13 · 14 §1.3](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#13--pilares-de-diseño-3-5-frases-que-resuelven-discusiones)),
no como ajuste de última hora en la pantalla de opciones.

| Punto del espectro | Qué hace | Ejemplo (analizado en Boss Keys, ver Fuentes) | Efecto sobre la fase 2 |
|---|---|---|---|
| **Sin mapa** | El jugador construye el mapa mental él mismo (Kevin Lynch, ya citado en 13 · 02 §1.3) | *Dark Souls* (mundo interconectado sin brújula ni mapa en pantalla) | Máximo: la observación es la única herramienta de navegación |
| **Mapa manual, sin iconos automáticos** | El mapa revela **forma** al visitar, pero el jugador coloca sus propios pines | *Hollow Knight* (mapa comprado por zona a un cartógrafo; el pin es una decisión del jugador) | Alto: sigue haciendo falta mirar el mundo para saber qué hay donde |
| **Mapa con iconos automáticos, brújula sólo en camino crítico** | Los POIs opcionales no aparecen hasta descubrirlos; el objetivo obligatorio sí se señala | Patrón recomendado por defecto (ver abajo) | Medio: preserva el descubrimiento opcional, protege al jugador perdido en lo obligatorio |
| **Brújula/marcador automático a todo** | Cada POI conocido tiene un icono y una flecha desde el minuto uno | La mayoría de mundo abierto de acción mainstream | Mínimo: la fase 2 desaparece, el mundo se convierte en una lista de tareas |

**El coste de llenar el mapa de iconos** no es estético, son tres costes concretos:

1. **Ahoga la señal en ruido.** Cuarenta iconos de cofre idénticos en la misma vista son el
   equivalente, a escala de mapa, de las «dos torres iguales» que 13 · 02 §1.3 señala como
   pérdida de legibilidad: si todo es un punto de referencia, nada lo es.
2. **Convierte motivación intrínseca en extrínseca.** Un mapa que ya dice dónde está todo
   convierte la exploración en una lista de tareas — exactamente el riesgo que
   [13 · 15 §5.1](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md#51--el-marco)
   describe para la **autonomía**: el jugador deja de decidir hacia dónde mirar porque el juego ya
   decidió por él. La sensación de «limpiar el mapa» sustituye a la de «descubrir».
3. **Entrena a ignorar el mundo.** Una vez el jugador aprende que el mapa es la fuente de verdad,
   deja de mirar los *landmarks* del entorno (§2.3) — y esa costumbre no se revierte a mitad de
   partida aunque el diseño mejore en la siguiente zona.

> 💡 **Recomendación por defecto para esta biblioteca:** revelar la **forma** del mapa al
> visitarlo físicamente (igual que hace `mapa_sala_marcar()` en
> [13 · 05 §3.5 j](./05%20-%20UI%20y%20UX%20de%20juego.md#j-pantalla-de-mapa-completo-desplazamiento-y-zoom-salas-y-viaje-rápido)
> con `SalaEstado.VISITADA`), permitir pines manuales del jugador, y reservar el marcador
> **automático** para el objetivo del camino crítico — nunca para un POI opcional. Es el punto
> medio que no mata la curiosidad y no castiga a quien se pierde en lo obligatorio.

### 1.4 Viaje rápido: cuándo, cuánto y qué destruye

El viaje rápido es una válvula sobre el coste de *backtracking* de un mundo grande, no un
añadido gratis. Dos preguntas de diseño, y ninguna se responde por defecto con «sí, siempre»:

**¿Cuándo se desbloquea?** Cuanto antes, más plano se siente el mundo — nunca hace falta aprender
su geografía real. Cuanto más tarde, más riesgo de que el *backtracking* sin él resulte tedioso
antes de que exista la válvula. La regla práctica: **el viaje rápido se desbloquea después de que
el jugador haya recorrido una zona entera a pie al menos una vez**, nunca antes de la primera
vuelta completa — así el mundo ya quedó «aprendido» cuando el atajo empieza a ahorrar el viaje.

**¿Cuánto cuesta?** Tres niveles, de menos a más fricción:

| Coste | Efecto | Cuándo |
|---|---|---|
| **Gratis e instantáneo** | Máxima comodidad; el mundo deja de sentirse grande en cuanto se desbloquea | Juegos donde la exploración ya terminó su función narrativa (fin de partida, *New Game+*, 04 · 06 §8 punto 8) |
| **Con fricción leve** (tiempo de carga, animación, sin poder usarse en combate) | Sigue ahorrando el tedio de repetir un tramo sin borrar del todo la sensación de distancia | Recomendado por defecto en un metroidvania o mundo abierto por zonas |
| **Con coste de recurso** (moneda, objeto consumible) | Mantiene el viaje rápido como decisión económica, no como reflejo — el coste de esa moneda es tema de [13 · 20](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md), no de este documento | *Survival* y gestión, donde el desplazamiento ya es parte de la economía (04 · 09) |

**Qué destruye, si se aplica sin criterio:**

- **La percepción de escala.** El comentario más repetido sobre mundos abiertos con viaje rápido
  temprano es que «el mundo se siente pequeño en cuanto lo desbloqueas» — porque deja de costar
  nada cruzarlo.
- **El contenido incidental.** Si el diseño esconde secretos **a lo largo** de una ruta (no en su
  destino), el viaje rápido compite directamente con ese contenido: nadie lo ve una segunda vez si
  puede saltárselo. No coloques contenido irrepetible en un tramo que el viaje rápido vaya a
  saltarse.
- **La tensión de recursos.** En un bucle con comida, combustible o tiempo limitado (04 · 09), el
  desplazamiento *es* la mecánica de riesgo. Un viaje rápido gratuito la anula por completo — de
  ahí que tantos juegos de supervivencia lo retrasen mucho o le pongan un coste real.

**Qué conectar, y qué no:** conecta nodos de tipo *hub* (el punto que todo el mundo visita a
menudo) o zonas terminales lejanas en pasos de grafo (§3.2 da la métrica exacta: la distancia BFS
que devuelve `mundo_zonas_distancias()`). **Nunca conectes dos puntos pensados para que el
jugador los recorra a pie** — un tramo narrativo de ida y vuelta pierde su función si se puede
saltar desde el primer día. Distinto de esto es el **atajo físico** (una puerta de un solo
sentido que el jugador abre desde el otro lado, 04 · 06 §8 punto 2): no es viaje rápido, es
geografía que se acorta una vez recorrida — y normalmente es preferible a un menú de
teletransporte porque no rompe nunca la continuidad espacial.

### 1.5 Hub, mundo abierto por zonas o metroidvania: el criterio

13 · 02 §2.6 ya da la tabla de forma/coste/receta de cada estructura. Lo que falta es el criterio
para **elegir** entre ellas, no repetir qué son:

| Pregunta | Hub | Mundo abierto por zonas | Metroidvania |
|---|---|---|---|
| **¿Cuánto entiende el jugador del mundo en la primera hora?** | Todo el «menú» de opciones, aunque no pueda entrar a todas | Una zona a la vez, en orden más o menos lineal | Nada — el mundo se revela progresivamente incluso en salas ya visitadas, según qué habilidad tengas |
| **¿Cuánto cuesta un *backtrack*?** | Barato: siempre se vuelve al centro | Caro salvo viaje rápido (§1.4) | El *backtrack* **es** el contenido: cada habilidad nueva recontextualiza terreno ya visto (04 · 06 §1) |
| **¿Qué tan reversible es un cambio de diseño tardío?** | Alta: una sala lateral es casi independiente, fácil de añadir o quitar en producción tardía ([13 · 11 §1.5](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#15-la-matriz-de-recorte)) | Media: mover una zona afecta a sus vecinas inmediatas | Baja: el grafo de bloqueos (§2.1) acopla todo — mover un ítem cambia el orden de entrega de las habilidades que dependen de él, y hay que re-validar (§2.5) |

La fila de reversibilidad es la que más se ignora y la más cara de ignorar: un metroidvania es la
estructura **menos amigable con recortes de alcance tardíos** de las tres, precisamente porque
el grafo de bloqueos es un sistema, no una colección de salas — recórtalo pensando en el grafo
completo (§2.1), no sala por sala.

### 1.6 Densidad de contenido frente a tamaño del mapa

La calidad percibida de un mundo correlaciona con la densidad de POIs en el **camino crítico y
sus alrededores inmediatos** (§1.2), no con el área total del mapa. Un mapa pequeño y denso se
lee como «lleno de secretos»; un mapa grande con el mismo número absoluto de POIs se lee como
«vacío», porque el tiempo de recorrido añadido diluye la densidad por minuto sin añadir nada que
mirar durante ese tiempo extra.

> 💡 **Regla de bolsillo para un equipo pequeño:** cada metro cuadrado nuevo de mundo tiene que
> pagar su alquiler en puntos de interés, o se recorta. Por defecto, diseña el mapa **más pequeño**
> que sostenga la cuota de POIs de §1.2 a la densidad objetivo; hazlo crecer sólo si también
> creces el número de POIs en la misma proporción — nunca al revés.

Esto convierte el tamaño del mapa en una línea más de la
[matriz de recorte](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#15-la-matriz-de-recorte)
de 13 · 11, sujeta a la misma disciplina de alcance que cualquier otra *feature*: si el
*vertical slice* ([13 · 11 §1.4](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#14-prototipo-mvp-y-vertical-slice-tres-cosas-distintas))
demuestra la densidad objetivo en una zona pequeña, extrapolar el mapa completo sin extrapolar
también el contenido es la forma más común de que un mundo grande se sienta vacío en el
lanzamiento.

---

## 2 · El método, paso a paso

### 2.1 El grafo de bloqueos: el artefacto que se dibuja antes de la primera sala

Un metroidvania (o cualquier mundo con *gating* por habilidad, 13 · 02 §1.4) se diseña primero
como un **grafo**, no como una colección de salas. Es la misma idea que
[13 · 14 §2.20](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#220--el-catálogo-de-diagramas-de-diseño)
ya presenta para mecánicas sueltas —un nodo por cosa, una flecha por «esto requiere aquello»—,
aplicada a la escala de **zonas de mundo** en vez de mecánicas, con dos añadidos que aquel
diagrama de papel no cubre: un modelo de datos concreto (§3.1) y la validación automática por
alcanzabilidad (§2.5 / §3.2) en vez de fiarlo al ojo.

**Nodos** = zonas o salas clave: no hace falta un nodo por cada pantalla, sólo por cada punto de
decisión (una bifurcación, una sala con un pickup, un gate). **Aristas** = conexiones físicas
entre zonas, con una etiqueta opcional: qué habilidad hace falta para cruzarla.

```
LEYENDA   ──▶ conexión libre     ══▶ requiere habilidad (etiquetada)

  [Hub] ──▶ [Bosque] ══(doble_salto)══▶ [Copas del bosque] ──▶ [Torre este] (habilidad: dash)
   │                        │
   │                        └──▶ [Cueva] ══(dash)══▶ [Lago] ──▶ [Hub] (atajo, 04 · 06 §8.2)
   └──▶ [Cripta] ══(llave_cripta)══▶ [Sala del jefe]
```

A diferencia del árbol de habilidades de
[13 · 16 §1.7](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#17-cuándo-no-hace-falta-un-grafo),
que es un **DAG** donde un ciclo siempre es un error, el grafo de mundo **debe** tener ciclos: un
mundo sin ningún camino de vuelta al *hub* que no sea repetir el camino de ida se siente lineal
disfrazado de abierto. Por eso §2.5/§3.2 sólo validan **alcanzabilidad y orfandad**, no ciclos —
al contrario que la validación de 13 · 16 §3.2, que sí busca ciclos porque en un árbol de
habilidades un ciclo es, por definición, un candado sin llave.

**Las dos preguntas que este artefacto tiene que responder antes de tocar el Room Editor:**

1. Con las habilidades entregadas **en el orden que el diseño pretende**, ¿es alcanzable la zona
   de cada habilidad usando sólo las habilidades anteriores? (Si el paso 4 exige la zona del paso
   6, hay un *soft-lock* — y es gratis encontrarlo aquí, carísimo encontrarlo en producción.)
2. Con **todas** las habilidades entregadas, ¿queda alguna zona inalcanzable? (Contenido muerto:
   una sala que nadie va a ver nunca, porque ninguna combinación de habilidades llega a ella.)

### 2.2 Presupuestar puntos de interés por zona

Con el grafo dibujado, cada nodo recibe una cuota de POIs (§1.2) calculada a partir de su
**profundidad estimada de recorrido**: cuántos pasos del grafo separan esa zona del *hub* o del
punto de entrada, multiplicado por el tiempo medio de cruce de una zona. Una zona a un salto del
*hub* necesita menos densidad que una zona a cinco saltos, porque el jugador ya invirtió más
tiempo en llegar y espera más a cambio (la misma lógica de riesgo/recompensa de
[13 · 02 §1.5](./02%20-%20Diseño%20de%20niveles.md#15-riesgo-recompensa-secretos-y-atajos),
aplicada a la escala de zona en vez de sala).

| Zona (ejemplo del grafo de §2.1) | Pasos desde el *hub* | POIs crítico | POIs opcional mayor | POIs opcional menor |
|---|---|---|---|---|
| Bosque | 1 | 1 (doble salto) | 0 | 2 |
| Copas del bosque | 2 | 0 | 1 (mirador, §2.3) | 3 |
| Cueva | 2 | 0 | 1 (atajo al lago) | 2 |
| Sala del jefe | 2 | 1 (jefe obligatorio) | 0 | 0 |

Esta tabla se rellena **antes** de modelar una sola sala, del mismo modo que la hoja de nivel de
[13 · 02 §4](./02%20-%20Diseño%20de%20niveles.md#4--la-hoja-de-nivel-la-plantilla-que-se-rellena-antes-de-construir)
se rellena antes de abrir el Room Editor.

### 2.3 Señalizar a distancia: *landmarks* de mundo y la cámara que enseña

13 · 02 §1.3 ya define *landmark*, *weenie* y líneas de guía a escala de **sala**. A escala de
**mundo** el mismo vocabulario se aplica con un presupuesto distinto: un *landmark* de mundo tiene
que ser visible desde **varias zonas de distancia**, no sólo desde la sala contigua — una torre,
una montaña partida, una columna de humo. Es la señal que precarga la fase 1 del bucle de §1.1
mucho antes de que la fase 3 (navegación) sea siquiera posible.

**La regla de 13 · 02 §1.4 — «la cerradura se enseña antes que la llave»— se traslada a escala de
mundo así:** muestra el *landmark* de una zona bloqueada desde una zona **ya accesible**, mucho
antes de que el jugador tenga la habilidad para llegar. Si la torre del ejemplo de §2.1 se ve
desde el Bosque nada más entrar, el jugador ya sabe que existe cuando por fin consigue el *dash*
que la abre — el reconocimiento («ahí es donde iba esto») sustituye a la sorpresa vacía.

**El papel de la cámara**, ya resuelto en
[13 · 19](./19%20-%20Cámaras%20de%20juego%20-%20encuadre,%20seguimiento%20y%20control.md), es lo
que convierte un *landmark* estático en una **enseñanza activa**:

- Un **atractor de cámara** con peso negativo (13 · 19 §3.6, *detractor*) puede ocultar
  deliberadamente un *landmark* hasta que el jugador se acerca físicamente — útil para secretos
  que no deben verse desde lejos.
- Un **plano de revelación** (13 · 19 §3.11, la cola de planos del director de cámara) es la
  herramienta correcta para el momento exacto en que un *landmark* se vuelve visible por primera
  vez: la cámara se aparta del jugador un segundo, encuadra la silueta, y vuelve. Es la fase 1 del
  bucle, dramatizada — el código concreto está en §3.5.

### 2.4 Diseñar el viaje rápido: qué conectar y qué no

Con el grafo y las distancias de §3.2 ya calculadas, elegir los nodos de viaje rápido es
mecánico: son candidatos los nodos con **grado alto** (muchas aristas — normalmente el *hub* y
las bifurcaciones grandes) y los nodos **lejanos** cuya distancia BFS al punto de entrada supera
un umbral fijado por el ritmo del juego (por ejemplo, más de 6 pasos). Los nodos que sólo existen
para conectar dos zonas por un pasillo con contenido incidental (§1.4) se excluyen explícitamente
de la lista, aunque el algoritmo de grado los proponga.

### 2.5 Validar el grafo antes de modelar nada

El paso final del método, antes de que nadie abra el Room Editor: escribir el orden de entrega de
habilidades previsto (`[{habilidad: "doble_salto", zona: "bosque"}, {habilidad: "dash",
zona: "cueva"}, ...]`) y comprobarlo contra el grafo con el mismo patrón de recorrido por anchura
que ya usa
[13 · 16 §3.2](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#32-validación-por-grafo-ciclos-kahnbfs-y-alcanzabilidad-bfs)
para el árbol de habilidades: una cola con índice de cabeza, un conjunto de visitados como
*struct*, sin `ds_queue`. La diferencia es qué abre una arista — allí, que **todos** los
prerrequisitos de un nodo estén cumplidos (o uno solo, en modo O); aquí, que el jugador **tenga**
la habilidad que etiqueta esa arista. El código completo está en §3.2.

Cualquier fallo aquí es un cambio de **grafo**, no de sala: es la razón de ser de este método.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 El grafo de bloqueos como datos

```gml
// ---------------------------------------------------------------------------
// scr_mundo_grafo
// Verificado: array_push, array_length, struct_get_names, variable_struct_exists NO EXISTE
//             error — SÍ EXISTE, verificado con buscar.py
// ---------------------------------------------------------------------------

/// @func mundo_grafo_nuevo()
/// @desc Un grafo de bloqueos: zonas (nodos) y conexiones (aristas), algunas con requisito
///       de habilidad. Se rellena a mano al dibujar el grafo de §2.1, o se carga de un JSON
///       exportado desde ahí — el formato es el mismo que usa `arbol_construir()` en
///       13 · 16 §3.1, con "zonas" en vez de "nodos" y aristas con "requiere" en vez de
///       prerrequisitos Y/O.
/// @returns {Struct}
function mundo_grafo_nuevo()
{
    return { zonas: {} };
}

/// @func mundo_zona_registrar(_grafo, _id, _x, _y)
/// @desc Una vez por zona del grafo de §2.1. _x/_y son coordenadas de MUNDO (para el minimapa
///       y la brújula de §3.4), no de la sala en sí.
function mundo_zona_registrar(_grafo, _id, _x, _y)
{
    _grafo.zonas[$ _id] = { x: _x, y: _y, adyacentes: [] };
}

/// @func mundo_conexion_crear(_grafo, _desde, _hacia, _requiere = "", _bidireccional = true)
/// @desc Una arista del grafo. _requiere es el nombre de la habilidad que la abre, o "" si es
///       libre. _bidireccional en false modela un atajo de un solo sentido (04 · 06 §8.2): la
///       puerta se abre desde el lado lejano, pero no hace falta la habilidad para VOLVER por
///       ahí una vez abierta — represéntalo como dos llamadas, la segunda sin _requiere.
function mundo_conexion_crear(_grafo, _desde, _hacia, _requiere = "", _bidireccional = true)
{
    array_push(_grafo.zonas[$ _desde].adyacentes, { destino: _hacia, requiere: _requiere });
    if (_bidireccional)
    {
        array_push(_grafo.zonas[$ _hacia].adyacentes, { destino: _desde, requiere: _requiere });
    }
}
```

```gml
// Uso: el grafo de §2.1, en código (normalmente se carga de JSON, no se escribe así a mano
// salvo para pruebas — 13 · 10 §3.1)
var _mundo = mundo_grafo_nuevo();
mundo_zona_registrar(_mundo, "hub", 0, 0);
mundo_zona_registrar(_mundo, "bosque", 200, 0);
mundo_zona_registrar(_mundo, "copas", 200, -150);
mundo_zona_registrar(_mundo, "cueva", 350, 50);
mundo_zona_registrar(_mundo, "lago", 550, 50);
mundo_zona_registrar(_mundo, "cripta", -200, 0);
mundo_zona_registrar(_mundo, "sala_jefe", -350, 0);

mundo_conexion_crear(_mundo, "hub", "bosque");
mundo_conexion_crear(_mundo, "bosque", "copas", "doble_salto");
mundo_conexion_crear(_mundo, "bosque", "cueva");
mundo_conexion_crear(_mundo, "cueva", "lago", "dash");
mundo_conexion_crear(_mundo, "lago", "hub", "", true);          // atajo, 04 · 06 §8.2
mundo_conexion_crear(_mundo, "hub", "cripta", "llave_cripta");
mundo_conexion_crear(_mundo, "cripta", "sala_jefe");
```

### 3.2 Validar alcanzabilidad y orden de entrega (BFS — el patrón de 13 · 16 §3.2)

```gml
// ---------------------------------------------------------------------------
// scr_mundo_validar
// Verificado: array_push, array_length, variable_struct_exists, struct_get_names
// ---------------------------------------------------------------------------

/// @func mundo_zonas_distancias(_grafo, _inicio, _habilidades)
/// @desc BFS desde _inicio, en pasos de zona. Una arista con "requiere" sólo se cruza si
///       _habilidades la contiene. MISMO PATRÓN que arbol_nodos_alcanzables() de 13 · 16
///       §3.2 —cola por índice de cabeza (no ds_queue), visitados como struct usado como
///       set— adaptado: allí una arista se abre por los PADRES de un nodo (modo Y/O de un
///       árbol); aquí se abre por una HABILIDAD sobre una arista de mundo.
/// @param {Struct} _grafo
/// @param {String} _inicio       Id de la zona de entrada.
/// @param {Struct} _habilidades  Set de habilidades ya entregadas (struct: variable_struct_exists).
/// @returns {Struct}  id de zona → distancia en pasos (Real). Una zona NO alcanzable no
///                     aparece: pregúntalo con variable_struct_exists(), no con un centinela.
function mundo_zonas_distancias(_grafo, _inicio, _habilidades)
{
    var _dist   = {};
    _dist[$ _inicio] = 0;

    var _cola   = [_inicio];
    var _cabeza = 0;

    while (_cabeza < array_length(_cola))
    {
        var _actual = _cola[_cabeza];
        _cabeza++;

        var _adyacentes = _grafo.zonas[$ _actual].adyacentes;
        for (var _i = 0; _i < array_length(_adyacentes); _i++)
        {
            var _arista = _adyacentes[_i];
            if (variable_struct_exists(_dist, _arista.destino)) continue;   // ya visitada

            var _cruzable = (_arista.requiere == "")
                          || variable_struct_exists(_habilidades, _arista.requiere);
            if (!_cruzable) continue;

            _dist[$ _arista.destino] = _dist[$ _actual] + 1;
            array_push(_cola, _arista.destino);
        }
    }
    return _dist;
}

/// @func mundo_grafo_validar_progresion(_grafo, _inicio, _orden_habilidades)
/// @desc LA prueba que importa antes de construir una sola sala (§2.5). _orden_habilidades es
///       el orden en el que el diseño PRETENDE entregar cada habilidad, con la zona donde
///       vive: [{ habilidad: "doble_salto", zona: "bosque" }, ...]. Comprueba que cada zona
///       sea alcanzable con SÓLO las habilidades entregadas hasta el paso anterior — si el
///       paso 4 exige la zona del paso 6, es un soft-lock y esta función lo dice antes de
///       perder una semana modelando salas.
/// @param {Struct} _grafo
/// @param {String} _inicio
/// @param {Array<Struct>} _orden_habilidades
/// @returns {Struct}  { valido: Bool, fallos: Array<String> }
function mundo_grafo_validar_progresion(_grafo, _inicio, _orden_habilidades)
{
    var _habilidades = {};
    var _fallos = [];

    for (var _i = 0; _i < array_length(_orden_habilidades); _i++)
    {
        var _paso = _orden_habilidades[_i];
        var _dist = mundo_zonas_distancias(_grafo, _inicio, _habilidades);

        if (!variable_struct_exists(_dist, _paso.zona))
        {
            array_push(_fallos, $"Paso {_i}: la zona '{_paso.zona}' (entrega '{_paso.habilidad}') "
                               + $"no es alcanzable con {struct_get_names(_habilidades)}");
        }

        _habilidades[$ _paso.habilidad] = true;   // se entrega DESPUÉS de comprobar que se llega
    }

    // Alcanzabilidad final: con TODAS las habilidades, ¿queda alguna zona huérfana? (§2.1,
    // pregunta 2 — a diferencia de 13 · 16 §3.2, aquí NO se busca ningún ciclo: el grafo de
    // mundo debe tenerlos, §2.1).
    var _todas = mundo_zonas_distancias(_grafo, _inicio, _habilidades);
    var _ids   = struct_get_names(_grafo.zonas);
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        if (!variable_struct_exists(_todas, _ids[_i]))
        {
            array_push(_fallos, $"Zona huérfana, inalcanzable con TODAS las habilidades: '{_ids[_i]}'");
        }
    }

    var _valido = (array_length(_fallos) == 0);
    if (!_valido)
    {
        show_debug_message($"mundo_grafo_validar_progresion: {array_length(_fallos)} fallo(s)");
    }
    return { valido: _valido, fallos: _fallos };
}
```

```gml
// Uso: sobre el grafo de §3.1
var _orden = [
    { habilidad: "doble_salto",  zona: "copas" },
    { habilidad: "dash",         zona: "lago"  },
    { habilidad: "llave_cripta", zona: "sala_jefe" },
];
var _resultado = mundo_grafo_validar_progresion(_mundo, "hub", _orden);
// _resultado.valido == true si "cripta" (que da acceso a "sala_jefe") es alcanzable con
// "" (ninguna habilidad, porque la arista hub→cripta exige "llave_cripta" y ese es
// precisamente el paso que se está comprobando) — en este grafo de ejemplo SÍ lo es,
// porque hub→cripta no depende de doble_salto ni de dash.
```

> 💡 **Envuélvelo como prueba automática.** El sitio natural para
> `mundo_grafo_validar_progresion()` es el mismo `scr_pruebas` de
> [13 · 10 §3.1](./10%20-%20Testing%20y%20QA.md#31-el-script-scr_pruebas) que 13 · 16 recomienda
> para `arbol_validar()`: una prueba que falla en rojo antes de un `gm-cli compile`, no un
> vistazo al diagrama de papel que se olvida de repetir tras el segundo cambio de diseño.

> ⚠️ **Este BFS no es el mismo que el de 13 · 07 §10.** `distancias_bfs()` en 13 · 07 recorre una
> **rejilla de celdas** generada proceduralmente (un nivel, no un mundo entero de zonas
> nombradas) y no conoce habilidades. `mundo_zonas_distancias()` recorre un **grafo de zonas con
> nombre**, con aristas que se abren o no según qué lleve el jugador encima. Comparten el patrón
> de recorrido (cola con índice de cabeza) pero resuelven preguntas distintas — no son
> intercambiables.

### 3.3 Distribuir puntos de interés por zona

```gml
// ---------------------------------------------------------------------------
// scr_mundo_poi
// Verificado: array_length, array_create
// Depende de muestreo_poisson() (13 · 07 §4) — NO se redefine aquí.
// ---------------------------------------------------------------------------

/// @func mundo_poi_distribuir(_zona_ancho, _zona_alto, _radio_min, _semilla, _cuota)
/// @desc Envuelve muestreo_poisson() (13 · 07 §4) y la recorta a la cuota que §2.2 asignó a
///       esta zona. Bridson no prioriza candidatos entre sí, así que recortar a los primeros
///       _cuota sigue siendo determinista (misma semilla, mismo resultado) sin repetir el
///       algoritmo.
/// @param {Real} _cuota  El total de POIs (crítico + opcional mayor + opcional menor) de §2.2.
/// @returns {Array<Struct>}  Array de { px, py }, tantos como quepan hasta _cuota.
function mundo_poi_distribuir(_zona_ancho, _zona_alto, _radio_min, _semilla, _cuota)
{
    var _candidatos = muestreo_poisson(_zona_ancho, _zona_alto, _radio_min, _semilla);
    if (array_length(_candidatos) <= _cuota) return _candidatos;

    var _recortado = array_create(_cuota);
    for (var _i = 0; _i < _cuota; _i++) _recortado[_i] = _candidatos[_i];
    return _recortado;
}
```

> 💡 **Híbrido: autor + algoritmo.** El truco que ya usa 13 · 07 §4 para densidades por bioma
> (generar de más y descartar con criterio) se extiende de forma natural aquí: coloca a mano los
> POIs **críticos** de §2.2 (son pocos y suelen tener una razón narrativa para su posición exacta)
> y usa `mundo_poi_distribuir()` sólo para rellenar los opcionales menores alrededor, filtrando
> con `point_distance()` cualquier candidato que caiga demasiado cerca de un POI crítico ya
> colocado a mano. Es la misma filosofía «híbrido, casi siempre» que
> [13 · 02 §2.6](./02%20-%20Diseño%20de%20niveles.md#26-tipos-de-estructura) recomienda para la
> estructura del mundo entero, aplicada aquí a su contenido.

### 3.4 La brújula: apuntar al punto de interés no descubierto más cercano

```gml
// ---------------------------------------------------------------------------
// scr_brujula
// Verificado: point_distance, point_direction, variable_struct_exists, array_length, infinity
// ---------------------------------------------------------------------------

/// @func brujula_direccion(_x, _y, _pois, _descubiertos)
/// @desc Dirección (grados) hacia el POI NO descubierto más cercano, o -1 si no queda
///       ninguno. _pois es un array de { id, x, y }; _descubiertos es un struct usado como
///       set (mismo patrón que _habilidades en §3.2). Sólo apunta al camino crítico si eso es
///       lo que §1.3 decidió automatizar — para POIs opcionales, no llames a esta función:
///       ahí manda el pin manual del jugador, no el código.
/// @returns {Real}  Grados (0 = derecha, sentido antihorario, como el resto de GML), o -1.
function brujula_direccion(_x, _y, _pois, _descubiertos)
{
    var _mejor_dist = infinity;
    var _mejor_dir  = -1;

    for (var _i = 0; _i < array_length(_pois); _i++)
    {
        var _poi = _pois[_i];
        if (variable_struct_exists(_descubiertos, _poi.id)) continue;

        var _dist = point_distance(_x, _y, _poi.x, _poi.y);
        if (_dist < _mejor_dist)
        {
            _mejor_dist = _dist;
            _mejor_dir  = point_direction(_x, _y, _poi.x, _poi.y);
        }
    }
    return _mejor_dir;
}
```

```gml
/// obj_hud — Draw GUI (fragmento)
// global.pois: array de { id, x, y } — normalmente sólo el/los objetivo(s) de camino crítico,
// por la recomendación de §1.3. global.pois_descubiertos: struct-set, igual que en §3.2/§3.5.
var _dir = brujula_direccion(obj_jugador.x, obj_jugador.y, global.pois, global.pois_descubiertos);
if (_dir >= 0)
{
    draw_sprite_ext(spr_aguja_brujula, 0, display_get_gui_width() * 0.5, 40, 1, 1,
                     _dir, c_white, 1);
}
```

### 3.5 La cámara que enseña: atractores, detractores y el plano de revelación

Ninguna función nueva aquí: se reutilizan tal cual `atractor_crear()` /
`camara_atraccion_evaluar()` (13 · 19 §3.6) y `cinematica_encolar()` / `cinematica_reproducir()`
(13 · 19 §3.11).

```gml
/// obj_mirador — Create (una instancia por landmark que se revela por primera vez, §2.3)
landmark_x  = 900;     // coordenadas de MUNDO del landmark que este mirador enseña
landmark_y  = -400;
visto       = false;
```

```gml
/// obj_mirador — Step
if (!visto && place_meeting(x, y, obj_jugador))
{
    visto = true;
    global.pois_descubiertos[$ "torre_este"] = true;   // §3.4: deja de atraer la brújula

    // Tres planos: acerca a la torre, mantenla en pantalla un momento con MENOS zoom (para que
    // se vea más mundo alrededor, no sólo la silueta), y vuelve al jugador. La cola y el
    // director de cámara son de 13 · 19 §3.11 — no se redefinen aquí.
    cinematica_encolar(x, y, 0.5, ease_out_quad, 1);
    cinematica_encolar(landmark_x, landmark_y, 1.6, ease_in_out_sine, 0.6);
    cinematica_encolar(obj_jugador.x, obj_jugador.y, 0.5, ease_in_out_sine, 1);
    cinematica_reproducir();
}
```

> 🔺 **Un plano de revelación es una cinemática, con las mismas reglas.** Tiene que ser saltable
> (04 · 00 §4, ya exigido en 13 · 19 §3.11) y no debe repetirse si el jugador vuelve a pasar por el
> mismo mirador — de ahí el `visto` que lo convierte en un disparador de una sola vez, el mismo
> patrón que los *triggers* de 13 · 02 §3.6.

Para ocultar en vez de revelar —un secreto que no debe verse hasta estar cerca—, el mismo sistema
sirve con un peso negativo (13 · 19 §3.6, *detractor*): un `atractor_crear(_x, _y, 40, 200, -0.4)`
colocado sobre el secreto empuja la cámara **lejos** de él mientras el jugador está fuera del
radio interior, sin necesitar ningún código nuevo.

### 3.6 Enganchar el viaje rápido a la pantalla de mapa

La pantalla de mapa completo —con desplazamiento, zoom, estados `OCULTA`/`VISITADA`/
`DESCUBIERTA` y la llamada a `ir_a_escena()`— ya está resuelta entera en
[13 · 05 §3.5 j](./05%20-%20UI%20y%20UX%20de%20juego.md#j-pantalla-de-mapa-completo-desplazamiento-y-zoom-salas-y-viaje-rápido)
y no se repite aquí. Lo único que falta es la decisión de **§1.4**: cuándo el viaje rápido está
permitido, que hoy esa función no comprueba.

```gml
/// @func viaje_rapido_permitido(_desde_sala, _en_combate)
/// @desc La pregunta de diseño de §1.4, en código: sin coste en moneda (eso es 13 · 20 si tu
///       diseño lo pide) y bloqueado en combate o dentro de una arena de jefe — un booleano
///       que ya tengas en tu máquina de estados de combate (13 · 18) resuelve _en_combate.
/// @param {String} _desde_sala   global.room_id actual (04 · 06 §2).
/// @param {Bool}   _en_combate
/// @returns {Bool}
function viaje_rapido_permitido(_desde_sala, _en_combate)
{
    if (_en_combate) return false;
    return !string_starts_with(_desde_sala, "arena_");
}
```

```gml
/// mapa_actualizar(_mapa) — 13 · 05 §3.5 j, con dos líneas añadidas (marcadas). El resto de la
/// función —zoom, desplazamiento, foco— es idéntico y no se repite.
if (_mapa.foco >= 0
&& (keyboard_check_pressed(vk_enter) || gamepad_button_check_pressed(0, gp_face1)))
{
    var _s = _mapa.salas[_mapa.foco];
    if (_s.estado == SalaEstado.DESCUBIERTA
    && viaje_rapido_permitido(global.room_id, obj_jugador.en_combate))                // ← añadido
    {
        ir_a_escena(_s.id_sala);
    }
    else if (_s.estado == SalaEstado.DESCUBIERTA)
    {
        aviso_lanzar("No puedes viajar rápido ahora mismo", "error");                 // ← añadido
    }
    else
    {
        audio_play_sound(snd_ui_error, 10, false);
        aviso_lanzar("Aún no has llegado ahí", "error");
    }
}
```

---

## 4 · Checklist

**Antes de abrir el Room Editor:**

- [ ] El grafo de bloqueos existe (papel o JSON), con una zona por nodo y una arista por conexión
- [ ] Cada arista con requisito de habilidad está etiquetada, y las que no lo llevan son libres a propósito
- [ ] `mundo_grafo_validar_progresion()` (§3.2) no devuelve fallos con el orden de entrega previsto
- [ ] Ninguna zona queda huérfana con todas las habilidades entregadas
- [ ] Cada zona tiene una cuota de POIs asignada (§2.2), no «lo que caiga bien al modelar»
- [ ] Se decidió, como pilar de diseño (13 · 14 §1.3), cuánto automatiza el mapa/brújula — no quedó pendiente para la fase de UI

**Antes de dar el mundo por terminado:**

- [ ] Todo *landmark* de mundo es único y visible desde al menos una zona antes de ser alcanzable
- [ ] El viaje rápido sólo conecta nodos *hub* o zonas lejanas ya recorridas por completo una vez
- [ ] Ningún tramo pensado para caminarse tiene un atajo de viaje rápido que lo salte antes de tiempo
- [ ] El mapa no revela iconos de POIs **opcionales** antes de descubrirlos a pie
- [ ] La densidad de POIs por minuto de recorrido es pareja entre zonas del mismo peso, o la diferencia es intencional
- [ ] Se ha jugado el mundo entero desde cero con el orden de habilidades previsto, sin atajos de desarrollador
- [ ] `gm-cli compile` sale limpio y el mundo se ha recorrido entero tras compilar

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| **Diseñar salas antes del grafo** | Un ítem queda detrás de una puerta que exige otro ítem que todavía no existía en el diseño | Grafo de bloqueos (§2.1) y validación (§2.5/§3.2) antes del Room Editor |
| **Tratar el grafo de mundo como un árbol de habilidades** | *Backtracking* siempre por el mismo pasillo; se siente lineal disfrazado de abierto | Un grafo de mundo SÍ necesita ciclos de vuelta al *hub* (§2.1) — no se valida como un DAG |
| **Un icono en el mapa por cada coleccionable** | El mapa se convierte en lista de tareas; el jugador deja de mirar el mundo | Revelar forma al visitar + pines manuales + marcador automático sólo en camino crítico (§1.3) |
| **Viaje rápido desde el minuto uno** | El mundo nunca se siente grande; nadie llega a aprender su geografía | Desbloquear tras la primera vuelta completa a una zona (§1.4) |
| **Viaje rápido a cualquier punto descubierto** | Rompe la tensión de recursos en *survival*; el *backtracking* deja de ser contenido | Conectar sólo nodos *hub*/lejanos (§2.4), nunca un tramo pensado para caminarse |
| **Dos *landmarks* iguales en la misma vista** | El jugador no distingue cuál es el de verdad, a escala de mundo (13 · 02 §1.3) | Un *landmark* único por zona visible; el resto es decoración |
| **Mapa grande con el mismo contenido que uno pequeño** | Se siente vacío aunque el recuento total de POIs sea «correcto» | Densidad por tiempo de recorrido (§1.2), no por área; recorta mapa antes que rellenarlo (§1.6, 13 · 11 §1.5) |
| **Validar el grafo mirándolo, no ejecutándolo** | Un *soft-lock* llega a producción y se descubre en la semana 20 de playtest | `mundo_grafo_validar_progresion()` (§3.2) como prueba automática (13 · 10 §3.1) |
| **Puerta de habilidad sin señal previa** | El jugador no recuerda que existía cuando por fin consigue la llave | Enseñar la cerradura antes que la llave (13 · 02 §1.4) a escala de mundo, con un *landmark* visible antes de ser alcanzable (§2.3) |

---

## Ver también

- [13 · 02 — Diseño de niveles](./02%20-%20Diseño%20de%20niveles.md) — legibilidad, *landmarks* y
  *gating* a escala de sala (§1.3-§1.4), tipos de estructura de mundo (§2.6) y la hoja de nivel
  (§4) de la que §2.2 toma el hábito de rellenar antes de construir.
- [13 · 05 — UI y UX de juego](./05%20-%20UI%20y%20UX%20de%20juego.md) §3.5 j — la pantalla de
  mapa completo (desplazamiento, zoom, estados de sala, viaje rápido) que §3.6 engancha sin
  reescribir.
- [13 · 07 — Generación procedural avanzada](./07%20-%20Generación%20procedural%20avanzada.md)
  §4 — el muestreo de Poisson-disc que §3.3 envuelve; §10 — el BFS de rejilla, distinto en
  propósito del BFS de grafo de zonas de §3.2.
- [13 · 10 — Testing y QA](./10%20-%20Testing%20y%20QA.md) §3.1 — `scr_pruebas`, el sitio natural
  para envolver `mundo_grafo_validar_progresion()` como prueba automática.
- [13 · 11 — Producción, alcance y lanzamiento](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md)
  §1.4-§1.5 — *vertical slice* y matriz de recorte: el tamaño del mundo como línea de alcance
  (§1.6).
- [13 · 14 — El documento de diseño](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md)
  §1.3 — pilares de diseño, donde se decide cuánto automatiza el mapa (§1.3); §2.20 — el grafo de
  gating de mecánicas sueltas del que §2.1 es la versión a escala de mundo.
- [13 · 15 — Teoría del diseño](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md)
  §4.2 — la Lente de la Curiosidad de Schell, que §1.1 convierte en un método de cuatro fases;
  §5.1 — autonomía, competencia y relación (SDT), la base del argumento contra el mapa lleno de
  iconos (§1.3).
- [13 · 16 — Progresión](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md)
  §3.2 — el patrón de BFS por *struct*-set que §3.2 de este documento reutiliza y adapta de
  árbol a grafo de zonas.
- [13 · 18 — Diseño de combate y de jefes](./18%20-%20Diseño%20de%20combate%20y%20de%20jefes.md) —
  la máquina de estados de combate de la que §3.6 toma el booleano `en_combate`.
- [13 · 19 — Cámaras de juego](./19%20-%20Cámaras%20de%20juego%20-%20encuadre,%20seguimiento%20y%20control.md)
  §3.6 — atractores y detractores; §3.11 — el director de cámara y sus cinemáticas saltables,
  ambos reutilizados sin cambios en §3.5.
- [04 · 00 — Anatomía de un juego completo](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md)
  §4 — por qué toda cinemática *scripted* debe ser saltable, exigido también al plano de
  revelación de §3.5.
- [04 · 06 — Metroidvania](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md) — la
  implementación completa que el grafo de §2.1 gobierna: transiciones entre rooms, `WorldState`,
  gates, minimapa por datos, y §8 (atajos, viaje rápido, New Game+) del que §1.4/§2.4 son la capa
  de diseño.
- [04 · 09 — Survival y crafting](../04%20-%20Recetas%20por%20género/09%20-%20Survival%20y%20crafting.md)
  — mundo abierto por zonas y el coste de recursos que el viaje rápido puede anular (§1.4).

---

## Fuentes

Consultadas el **6 de septiembre de 2026**.

- **Kevin Lynch, *The Image of the City*** (MIT Press, 1960) — caminos, puntos de referencia y
  nodos como vocabulario del mapa mental: ya citado y verificado en
  [13 · 02 §1.3](./02%20-%20Diseño%20de%20niveles.md#13-legibilidad-puntos-de-referencia-weenies-y-líneas-de-guía);
  se reutiliza aquí sin volver a abrir la fuente, aplicado a escala de mundo (§2.3).
- **Christopher W. Totten, *An Architectural Approach to Level Design*, 2.ª ed.**, CRC Press / A
  K Peters, 2019 (ISBN 978-0815361367) — *prospect and refuge* y comunicación visual a distancia:
  ya citado y verificado (con el aviso de HTTP 403 en la ficha del editor) en
  [13 · 02 Fuentes](./02%20-%20Diseño%20de%20niveles.md); se reutiliza sin volver a abrir la
  fuente.
- **Jesse Schell, *The Art of Game Design: A Book of Lenses*** — la Lente de la Curiosidad,
  citada de pasada en
  [13 · 15 §4.2](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md#42--un-subconjunto-operativo-de-18-lentes);
  §1.1 de este documento es su desarrollo en un método de cuatro fases aplicado a exploración de
  mundo.
- **Self-Determination Theory** — el marco de autonomía/competencia/relación de Deci y Ryan, ya
  verificado contra `selfdeterminationtheory.org` en
  [13 · 15 §5.1](./15%20-%20Teoría%20del%20diseño%20-%20el%20canon%20en%20una%20tarde.md#51--el-marco);
  se reutiliza aquí sin volver a abrir la fuente para el argumento de §1.3 sobre el mapa lleno de
  iconos.
- **Mark Brown (*Game Maker's Toolkit*), «Following the Little Dotted Line»** —
  <https://www.youtube.com/watch?v=FzOCkXsyIqo>. Verificado en vivo el título y la existencia del
  vídeo mediante una petición HTTP directa a la página de resultados de YouTube (no WebSearch,
  excluido de esta tarea). ⚠️ **Divulgación secundaria**, en la misma categoría que la cita de
  Mark Brown ya aceptada en
  [13 · 02 Fuentes](./02%20-%20Diseño%20de%20niveles.md): no se pudo extraer la transcripción
  completa en esta sesión (la herramienta de transcripción disponible no devolvió contenido
  utilizable), así que el argumento de §1.3 sobre el coste de los marcadores automáticos se
  apoya en el título confirmado y en el consenso de diseño ya bien documentado sobre el tema
  (Lynch, SDT), no en una cita textual del vídeo.
- **Mark Brown (*Boss Keys*), «The World Design of Hollow Knight»** —
  <https://www.youtube.com/watch?v=7ITtPPE-pXE>. Mismo método de verificación que el anterior:
  título y capítulos confirmados en vivo (uno de ellos, literalmente, «Dependency Chart» — el
  grafo de dependencias de habilidades y zonas que §2.1 formaliza), transcripción no disponible
  en esta sesión. ⚠️ Citado como referencia de que el análisis por grafo de dependencias de un
  metroidvania es una práctica de análisis de diseño ya establecida, no como fuente textual de
  ningún dato concreto de este documento.
- **Mark Brown (*Boss Keys*), «El Diseño del Mundo de Dark Souls»** —
  <https://www.youtube.com/watch?v=QhWdBhc3Wjc>. Mismo método y misma reserva que el anterior;
  citado en §1.3 como ejemplo verificado-por-título de un mundo interconectado sin mapa
  automático.
- **GameMaker LTS 2026, manual oficial** (espejo local en `09 - Manual oficial/`): páginas de
  `point_direction`, `point_distance`, `place_meeting`, `display_get_gui_width`,
  `string_starts_with`, `variable_struct_exists`, `struct_get_names`, `array_create` y
  `array_push` — todas verificadas contra el `GmlSpec.xml` del runtime **2026.0.0.23** con
  `python3 "_indice/buscar.py"` antes de usarse en el código de este documento.
- **Blog oficial, «Expanding Worlds: Building Games With Interconnected Levels»** (Gurpreet S.
  Matharoo, 12-08-2021) — ya citado y verificado en
  [13 · 02 Fuentes](./02%20-%20Diseño%20de%20niveles.md): <https://gamemaker.io/en/blog/multiple-levels-tutorial>;
  reutilizado como fuente de la arquitectura de rooms conectadas que 04 · 06 implementa y este
  documento diseña por adelantado.

**Verificación de la API.** Todos los símbolos del runtime usados en este documento —
`array_push`, `array_length`, `array_create`, `struct_get_names`, `variable_struct_exists`,
`point_distance`, `point_direction`, `place_meeting`, `display_get_gui_width`,
`string_starts_with`, `draw_sprite_ext`, `infinity`, `show_debug_message`, `keyboard_check_pressed`,
`vk_enter`, `gamepad_button_check_pressed`, `gp_face1`, `audio_play_sound`— se comprobaron uno a
uno con `python3 "_indice/buscar.py" <símbolo>` contra el runtime instalado antes de escribirse.
Ninguno está marcado como obsoleto. Las funciones que **no** son del runtime —
`mundo_grafo_nuevo`, `mundo_zona_registrar`, `mundo_conexion_crear`, `mundo_zonas_distancias`,
`mundo_grafo_validar_progresion`, `mundo_poi_distribuir`, `brujula_direccion`,
`viaje_rapido_permitido`— son código propio de este documento; ninguna usa un prefijo de familia
reservada del runtime (`mundo_*` y `brujula_*` no coinciden con ninguna familia nativa). Las
funciones `muestreo_poisson()` (13 · 07 §4), `atractor_crear()` / `camara_atraccion_evaluar()`
(13 · 19 §3.6), `cinematica_encolar()` / `cinematica_reproducir()` (13 · 19 §3.11),
`mapa_actualizar()` / `mapa_sala_marcar()` / `ir_a_escena()` / `aviso_lanzar()` (13 · 05 §3.5 j) y
`ease_out_quad` / `ease_in_out_sine` (`06/scr_math_util.gml`, dependencia ya documentada en
13 · 19) ya existen y están verificadas en sus documentos de origen: no se redefinen aquí, se dan
por dependencia y se llaman tal cual.
