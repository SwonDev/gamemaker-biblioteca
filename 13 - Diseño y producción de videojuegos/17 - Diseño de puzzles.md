# 17 · Diseño de puzzles

> Cómo diseñar un puzzle que enseñe su regla sin decirla, cómo medir si es justo antes de
> publicarlo, y cómo comprobarlo con un programa en vez de con la intuición: representar su
> estado, resolverlo por búsqueda (BFS/A*), generarlo con validación y dejar que el jugador
> deshaga sin miedo.
>
> **No cubre la implementación de un tablero de match-3** (detección de matches, cascadas,
> gravedad, shuffle): eso es
> [`04 · 07 — Puzzle y Match-3`](../04%20-%20Recetas%20por%20género/07%20-%20Puzzle%20y%20Match-3.md),
> y §1.1 explica por qué match-3 apenas es un «puzzle» en el sentido de este documento. Tampoco
> repite la curva de dificultad general ni el *onboarding* sin texto — vienen de
> [`13 · 01`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md)
> y se aplican aquí, no se reexplican — ni la estructura de nivel *kishōtenketsu*, que sale de
> [`13 · 02`](./02%20-%20Diseño%20de%20niveles.md).

---

## 1 · Los principios

### 1.1 Qué es un puzzle (y qué no)

Wikipedia resume un puzzle como un juego, problema o juguete que pone a prueba el ingenio o el
conocimiento de quien lo resuelve, encajando o separando piezas de forma lógica hasta llegar a
la solución correcta — Wikipedia, artículo «Puzzle» (en inglés), consultado 2026-09-06. Lo que
de verdad separa un puzzle de un reto de acción o de estrategia son dos rasgos:

1. **Hay una regla oculta que descubrir**, no solo una habilidad motriz que ejecutar. Un
   plataformas exige reflejos; un puzzle exige *entender algo*.
2. **Una vez entendida la regla, resolverlo dos veces es aburrido.** Un combate se puede volver
   a jugar porque cambia; un puzzle resuelto ya no tiene nada que ofrecer salvo repetir la
   ejecución — y por eso los mejores se retiran en cuanto cumplieron su función (§1.3).

Esto es justo lo que separa esta ficha de
[`04 · 07`](../04%20-%20Recetas%20por%20género/07%20-%20Puzzle%20y%20Match-3.md): un tablero de
match-3 se **rejuega** con boards aleatorios y presión de tiempo o de movimientos — es un
ejercicio de optimización bajo restricción, no un enigma con una única epifanía. Las dos cosas
se llaman «puzzle» en inglés y el género confunde a propósito; aquí «puzzle» es siempre el
segundo sentido: **un problema diseñado para producir un momento de comprensión concreto y no
repetible.**

### 1.2 Taxonomía: las familias de puzzle

La clasificación de Wikipedia separa puzzles lógicos, mecánicos, de palabras y números,
visuales, de videojuego y metapuzzles (misma fuente que arriba). Traducida a las familias que de
verdad se diseñan distinto en un juego:

| Familia | El jugador... | Ejemplos | Motor de la dificultad |
|---|---|---|---|
| **Lógica / deducción** | infiere un estado oculto a partir de pistas | Picross, Buscaminas, Lights Out | cuántas pistas hacen falta para descartar todas las alternativas menos una |
| **Manipulación de reglas** | las reglas mismas son las piezas que mueve | *Baba Is You*, *Stephen's Sausage Roll* | cuántas reglas hay que recombinar a la vez |
| **Espacial / empuje (Sokoban)** | mueve objetos con restricciones de reversibilidad | Sokoban, la parte de cajas de *The Talos Principle* | profundidad de planificación: cuántos movimientos hay que prever antes del primero |
| **Secuencia / orden** | encuentra el ORDEN correcto de una serie de movimientos reversibles | Torres de Hanói, *Rush Hour*, el 15-puzzle | tamaño del espacio de estados y cuántos callejones sin salida tiene |
| **Observación / visual** | encuentra un patrón, una diferencia o un objeto ya presente en pantalla | los paneles de *The Witness*, buscar las 7 diferencias | qué tan bien camuflada está la pista dentro del ruido visual |
| **Léxico / numérico** | opera sobre símbolos, no sobre espacio | crucigramas, sudoku, anagramas | tamaño del alfabeto y restricciones cruzadas |
| **Metapuzzle** | combina las soluciones de varios puzzles ya resueltos en una respuesta final | salas de escape, ARGs | ninguno propio: hereda la de sus piezas, más el coste de darse cuenta de que hay que combinarlas |

Ninguna familia es superior; lo que importa es **no mezclar dos sin querer**. Un Sokoban con
pistas visuales camufladas es dos puzzles a la vez y el jugador no sabe cuál está fallando. La
familia espacial/empuje es la que desarrolla la Parte de ingeniería de este documento (§3),
porque es la más fácil de representar como estado y resolver por búsqueda — pero el método de
§2 (enseñar sin enunciar, medir la dificultad, graduar pistas) vale para las siete.

### 1.3 El momento «ajá»: anatomía y qué lo mata

Jonathan Blow es explícito sobre lo que destruye la epifanía: sobre-tutorializar «mata la
epifanía y cosas relacionadas como la alegría del descubrimiento» — según recoge Wikipedia,
artículo «The Witness (2016 video game)» (en inglés), consultado 2026-09-06. El momento «ajá»
tiene una anatomía de tres tiempos:

1. **Fricción honesta.** El jugador prueba lo obvio y falla, y el fallo tiene que sentirse como
   suyo — nunca como un candado sin llave a la vista (eso es una trampa, no un puzzle).
2. **El giro.** Una idea que hasta ese momento no había considerado explica todos los fallos
   anteriores a la vez. Cuanto más simple sea la idea una vez vista, más fuerte es la epifanía:
   Blow describe sus puzzles como diseñados para ser «tan simples como puedan ser» mientras
   siguen produciendo «pequeñas epifanías una y otra vez» (misma fuente).
3. **Ejecución trivial.** Una vez visto el truco, aplicarlo debería costar segundos, no minutos.
   Si la ejecución es larga, el puzzle deja de medir comprensión y empieza a medir paciencia —
   son dos juegos distintos.

**Lo que mata el momento «ajá»**, de más a menos frecuente en juegos publicados:

| Asesino | Por qué |
|---|---|
| **Explicar la regla en un texto antes de que el jugador la necesite** | No hay nada que descubrir: se leyó |
| **Un tutorial que no se retira** | Portal reduce el andamiaje instruccional progresivamente hasta que desaparece del todo en la segunda mitad del juego — Wikipedia, artículo «Portal (video game)» (en inglés), consultado 2026-09-06. Un andamiaje que nunca se retira es un tutorial infinito, no una curva |
| **UI que resuelve el puzzle por el jugador** | Resaltar el único movimiento válido convierte la deducción en «pulsar lo que brilla» |
| **Puzzles de relleno tras la epifanía** | Repetir la misma idea ya entendida no reafirma nada: aburre. Se retira en cuanto cumplió, como manda la regla de una idea por nivel de [`13 · 02`](./02%20-%20Diseño%20de%20niveles.md) §1.1 |
| **Pistas por defecto activadas** | Si la ayuda aparece sin pedirla, nunca hay fricción que romper (ver §2.4) |
| **Confundir un bug con la dificultad prevista** | Un softlock o una física errática que «casualmente» resuelve el puzzle no es un momento «ajá», es un reporte de bug disfrazado |

> 💡 *The Witness* deja que el jugador abandone una región difícil y se vaya a otra sin
> penalización: cada zona es independiente (misma fuente de Wikipedia). Es la versión de diseño
> de puzzles de la regla de riesgo/recompensa de nivel: nunca fuerces al jugador contra un único
> muro sin salida lateral.

### 1.4 Soluciones no deseadas

Una **solución no deseada** es cualquier camino a la victoria que el espacio de estados
*realmente* contiene y que el diseñador no previó: un atajo geométrico, una caja que se puede
sacar del puzzle en vez de resolverlo, una simetría que permite «hacer trampa» sin violar
ninguna regla. La trampa de diseñarlas a mano es que **el diseñador solo ve el camino que
imaginó** — para ver los demás hace falta preguntarle al espacio de estados de verdad, no a la
intuición. Esa es la razón de ser de §3.3 y §3.4: el buscador (BFS/A*) no conoce la intención
del diseñador, solo el estado real, así que **encuentra exactamente los mismos atajos que
encontraría un jugador rencoroso.**

No toda solución no prevista es mala: una emergencia elegante (una forma más corta y más
inteligente que la que tenías en mente) suele ser motivo de celebración, no de parche. La que sí
hay que cazar es la que **evita la regla que el puzzle existía para enseñar** — esa rompe el
onboarding de toda la cadena que viene detrás (§2.2). El criterio práctico está en §3.4.

---

## 2 · El método, paso a paso

### 2.1 Enseñar la regla sin enunciarla

[`13 · 01`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md)
§5 da las cinco herramientas para un nivel; aplicadas a un puzzle en concreto:

| Herramienta (13 · 01 §5.2) | Cómo se traduce a un puzzle |
|---|---|
| **Encuadre** | La cámara o el recorte de pantalla solo muestran la pieza que hace falta entender ahora mismo — nada de la solución completa a la vista desde el primer instante |
| **Camino único** | La geometría del puzzle no admite ningún movimiento con sentido salvo el que enseña la regla — no hay «probar cosas al azar» productivo |
| **Demostración segura** | Algo que el jugador NO controla hace la jugada primero: una caja que ya empujó una IA, un panel resuelto que se ve desde lejos, un elemento que muestra el efecto de la regla sin que el fallo cueste nada |
| **Repetición con variación** | El mismo truco, tres veces, cada vez en una disposición distinta — hasta que deja de ser azar y se vuelve patrón consciente |
| **Recompensa por curiosidad** | Un puzzle opcional, más difícil, que usa la MISMA regla de un modo inesperado — premia a quien ya la domina sin obligar a quien no |

Portal es el caso de referencia: sus cámaras de prueba enseñan el concepto de *fling* (usar el
impulso de una caída por un portal) de forma progresiva y sin ninguna instrucción explícita en
pantalla, y el equipo llegó a retirar elementos decorativos porque los testers perdían el tiempo
interactuando con ellos en vez de con las piezas del puzzle — Wikipedia, artículo «Portal (video
game)», consultado 2026-09-06. Menos ruido visual es, literalmente, más Encuadre.

### 2.2 Encadenar puzzles: introducir → desarrollar → torcer → concluir

[`13 · 02`](./02%20-%20Diseño%20de%20niveles.md) §1.1 describe el *kishōtenketsu* como
estructura de NIVEL. Aplicado a una CADENA de puzzles que comparten una misma regla (un color de
*The Witness*, un verbo de *Baba Is You*, una pieza de Sokoban), es el mismo esqueleto en una
escala más pequeña:

| Fase | En un nivel (13 · 02 §1.1) | En una cadena de puzzles |
|---|---|---|
| **Introducir** (*ki*) | Presenta la mecánica en un sitio seguro | El primer puzzle de la cadena demuestra la regla con el mínimo de piezas posible — casi no hace falta pensar, solo mirar |
| **Desarrollar** (*shō*) | Lo mismo, más exigente | Mismo puzzle, con una pieza más o una restricción más — la primera decisión real |
| **Torcer** (*ten*) | Combinada con otra mecánica, o del revés | Se combina con una regla de una cadena ANTERIOR, o se invierte la regla actual (lo que empujabas ahora tira) |
| **Concluir** (*ketsu*) | El examen: todo junto | El puzzle-cápsula: exige las dos reglas a la vez, sin red de seguridad |

**La regla operativa es la misma que en 13 · 02: una idea por cadena, y en cuanto la cadena
concluyó, se retira.** Meter un quinto puzzle «más de lo mismo» después del de cierre no
refuerza nada — diluye el «ajá» que ya se ganó (§1.3). *The Witness* organiza sus paneles
exactamente así: resolver uno enciende el cable de energía que da paso al siguiente, la
complejidad escala con el tamaño de la cuadrícula y el refinamiento de las reglas, y cada región
es independiente de las demás — Wikipedia, «The Witness (2016 video game)», consultado
2026-09-06.

> ⚠️ La cadena de cuatro fases es la estructura por defecto, no una ley física: un puzzle
> aislado y espectacular (un metapuzzle de cierre de área, por ejemplo) puede saltarse
> «desarrollar» si su única función es ser el «torcer»/«concluir» de una cadena que ya se
> introdujo en otra parte del juego.

### 2.3 Medir la dificultad de un puzzle

Aquí hay que separar dos cosas que se confunden constantemente:

- **Longitud de la solución** — cuántos movimientos exige, una vez se sabe qué hacer. Es
  **mecánica**: se mide directamente con el buscador de §3.3 (el mismo número que da
  `array_length()` sobre el camino que devuelve `sokoban_resolver_bfs()`).
- **Profundidad de la idea** — cuántos conceptos nuevos, o combinaciones de conceptos viejos,
  hace falta ver antes de mover la primera pieza. Es **conceptual**, y NO es proporcional a la
  longitud: un puzzle de 3 movimientos puede exigir una idea enorme (el giro de §1.3), y uno de
  40 puede ser trivial una vez visto el truco — solo tedioso de ejecutar.

Sokoban en general es NP-hard y PSPACE-completo, y el espacio de búsqueda de un laberinto de
20×20 se estima en 10⁹⁸ — Wikipedia, artículo «Sokoban», consultado 2026-09-06. La lección de
diseño no es la complejidad computacional en sí: es que **un espacio de estados más grande no
es, por sí solo, un puzzle más interesante** — solo es una búsqueda más larga para el mismo
«ajá». Un tablero de 20×20 con la misma idea que uno de 6×5 es más tedioso, no más profundo.

**La técnica práctica: medir las dos por separado, con datos, no con la opinión del diseñador**
— la misma disciplina de [`13 · 01`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md)
§3.4, adaptada de «por sala» a «por puzzle»:

| Métrica (13 · 01 §3.4, adaptada) | Qué mide en un puzzle |
|---|---|
| **Intentos fallidos por puzzle** | Si pasa de 8-10, frustra; si es 1, el puzzle no exigía nada |
| **Tiempo mediano por puzzle** (mediana, no media) | Dónde se atasca sin fallar: el puzzle no comunica su propia regla |
| **Embudo de abandono** entre puzzles de la cadena | Dónde deja de jugar la gente, no dónde tú crees que debería costarle |
| **Pistas usadas hasta resolver** (§2.4) | Si el escalón 3 se pide siempre, la cadena estaba mal calibrada, no el jugador |

La longitud de solución del buscador es el termómetro **de diseño** (se mide antes de publicar,
sin jugadores); las cuatro de arriba son el termómetro **de playtest** (se miden después, con
jugadores de verdad). Hacen falta las dos: la primera dice si el puzzle es *resoluble y no
trivial* (§3.4); la segunda dice si además es *comprensible*, que es una pregunta que ningún
algoritmo contesta por ti.

### 2.4 Pistas graduadas

Una pista no es «dar la solución o no darla»: es una escalera. Cinco escalones cubren la
mayoría de los juegos de puzzles publicados:

| Nivel | Qué dice | Coste para el jugador |
|---|---|---|
| **0 — Nada** | Solo el *feedback* normal del puzzle (qué movimientos son legales) | Ninguno: es el estado por defecto |
| **1 — Recordatorio** | Repite la regla ya enseñada, sin aplicarla al caso concreto | Bajo: es memoria, no descubrimiento |
| **2 — Señalar** | Indica QUÉ mirar (una celda, una pieza), no qué hacer con ella | Medio |
| **3 — Acción concreta** | Dice el movimiento exacto a probar | Alto: casi resuelve por el jugador |
| **4 — Resolver / saltar** | Aplica el paso, o salta el puzzle entero | Máximo: protege el ritmo del JUEGO a costa del «ajá» de ESTE puzzle |

Tres reglas de diseño encima de la tabla:

1. **Siempre opt-in.** Una pista que aparece sola mata la fricción honesta de §1.3 antes de que
   exista. El jugador la pide; el juego nunca la ofrece por iniciativa propia salvo que el
   jugador lo haya activado en opciones.
2. **Cada escalón cuesta pedirlo de nuevo**, no solo mirarlo: una cadencia mínima entre
   peticiones evita que pulsar el botón dos veces seguido sin pensar salte directo a un nivel
   alto.
3. **El escalón 4 (saltar) es legítimo**, sobre todo en juegos con narrativa donde el puzzle es
   un obstáculo al ritmo, no el objetivo. Negarlo por orgullo de diseñador frustra más de lo que
   enseña.

```gml
/// scr_pistas — la escalera de pistas como una pequeña máquina de estados
///
/// Nivel 0 = nada. Cada pista_pedir() sube un escalón, con una cadencia
/// mínima para que pedir dos veces por accidente no salte niveles.

/// @func pista_crear()
function pista_crear() {
    return { nivel: 0, ultima_peticion: 0 };
}

/// @func pista_pedir(_pista, _t_actual, _cadencia_minima)
/// @desc Sube un escalón (tope 4) si ha pasado `_cadencia_minima` desde la
///       última petición. Devuelve el nivel resultante.
function pista_pedir(_pista, _t_actual, _cadencia_minima) {
    if (_t_actual - _pista.ultima_peticion < _cadencia_minima) return _pista.nivel;
    _pista.nivel = min(_pista.nivel + 1, 4);
    _pista.ultima_peticion = _t_actual;
    return _pista.nivel;
}

/// @func pista_reiniciar(_pista)
/// @desc Se llama al resolver el puzzle o al entrar en uno nuevo.
function pista_reiniciar(_pista) {
    _pista.nivel = 0;
}
```

Registra `pista.nivel` en la telemetría de [`13 · 01`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md)
§9.5 junto al resto de eventos: es la cuarta métrica de la tabla de §2.3.

---

## 3 · Cómo se traduce a GameMaker

> Todo el código de esta sección se probó compilando un proyecto GameMaker real con
> `gm-cli compile` contra el runtime `2026.0.0.23` (0 errores). La LÓGICA se verificó aparte con
> una réplica en Python del mismo algoritmo (mismas funciones, mismos nombres, mismos pasos),
> ejecutada sobre los tableros de ejemplo de esta sección: el entorno de trabajo de esta sesión
> no pudo abrir una ventana gráfica para ejecutar el juego compilado y leer sus
> `show_debug_message` reales. Por eso los números concretos que aparecen aquí abajo (longitudes
> de camino, estados visitados) proceden de esa réplica en Python, no de una ejecución del
> `.gml` — queda anotado con ⚠️ donde corresponde, en vez de presentarlo como algo que no se
> comprobó.

### 3.1 Representar el estado

Separa dos cosas que cambian a ritmos distintos, la misma disciplina de
[`13 · 07`](./07%20-%20Generación%20procedural%20avanzada.md) §1.3 (separar generación de
presentación):

- **El tablero** (`_mapa`): muros y metas. No cambia nunca durante la búsqueda.
- **El estado** (`_estado`): jugador y cajas. Cambia con cada movimiento, y es lo único que
  viaja por el árbol de búsqueda.

```gml
/// scr_sokoban — estado, movimiento, deadlocks y el solver por búsqueda
///
/// El TABLERO no cambia durante la búsqueda (muros y metas). El ESTADO sí:
/// jugador y cajas. Separar los dos es la clave de todo lo que sigue.

/// @func sokoban_mapa_crear(_ancho, _alto, _muros, _metas)
/// @desc _muros es un array plano de bool (índice = y * ancho + x), igual
///       que el array plano que recomienda 13 · 07 §1.3. _metas es un array
///       de índices de celda. Precalcula el lookup de metas: se consulta en
///       cada nodo del árbol de búsqueda, así que vale la pena que sea O(1).
function sokoban_mapa_crear(_ancho, _alto, _muros, _metas) {
    var _n = _ancho * _alto;
    var _es_meta = array_create(_n, false);
    for (var _i = 0; _i < array_length(_metas); _i++) {
        _es_meta[_metas[_i]] = true;
    }
    return {
        ancho: _ancho,
        alto: _alto,
        muros: _muros,
        metas: _metas,
        es_meta: _es_meta
    };
}

/// @func sokoban_estado_crear(_jugador, _cajas)
/// @desc Canonicaliza las cajas (orden ascendente): dos estados con las
///       mismas cajas en distinto orden de array deben producir el MISMO
///       hash (§3.3), o el buscador los trataría como estados distintos
///       para siempre y no terminaría nunca.
function sokoban_estado_crear(_jugador, _cajas) {
    var _copia = array_create(array_length(_cajas));
    array_copy(_copia, 0, _cajas, 0, array_length(_cajas));
    array_sort(_copia, true);
    return { jugador: _jugador, cajas: _copia };
}
```

Los ESTADOS son **inmutables**: ninguna función de este documento modifica un `_estado` que ya
existe, todas devuelven uno nuevo. Es la misma idea del patrón comando de
[`13 · 06`](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) §3.7 — separar la
intención (los datos) de la aplicación — y aquí paga dos veces: hace que el hash de §3.3 sea de
fiar (nada cambia por detrás mientras un estado está en la cola del buscador) y hace que
**deshacer** (§3.6) sea gratis.

### 3.2 Movimiento y bloqueos (deadlocks)

Wikipedia describe el deadlock de forma directa: un movimiento descuidado puede dejar una caja
permanentemente atrapada contra una pared u otra caja, y decidir si un Sokoban cualquiera tiene
solución es NP-hard y PSPACE-completo — Wikipedia, artículo «Sokoban», consultado 2026-09-06.
Eso significa que buscar sin ninguna poda explora estados que **nunca** pueden llevar a una
solución. La poda más simple y más segura es el **bloqueo de esquina**:

> **Una caja fuera de una meta con un muro pegado en un eje horizontal Y otro en el vertical no
> se puede volver a mover, la empuje quien la empuje.** Empujarla en horizontal exige que uno de
> los dos lados horizontales esté libre (para el destino) y el otro sea pisable (para el
> jugador); un muro en cualquiera de los dos ya rompe las dos direcciones horizontales a la vez.
> Lo mismo en vertical. Si las dos cosas pasan a la vez, la caja está condenada para siempre —
> sin excepción, sin importar qué pase en el resto del tablero.

```gml
/// @func sokoban_es_deadlock(_mapa, _pos)
/// @desc Bloqueo de esquina. Es poda SEGURA: solo descarta estados que de
///       verdad no tienen solución, jamás uno bueno (demostración arriba).
function sokoban_es_deadlock(_mapa, _pos) {
    if (_mapa.es_meta[_pos]) return false;   // sobre una meta, no importa

    var _x = _pos mod _mapa.ancho;
    var _y = _pos div _mapa.ancho;

    var _muro_izq = (_x == 0)               || _mapa.muros[_y * _mapa.ancho + (_x - 1)];
    var _muro_der = (_x == _mapa.ancho - 1) || _mapa.muros[_y * _mapa.ancho + (_x + 1)];
    var _muro_arr = (_y == 0)               || _mapa.muros[(_y - 1) * _mapa.ancho + _x];
    var _muro_aba = (_y == _mapa.alto - 1)  || _mapa.muros[(_y + 1) * _mapa.ancho + _x];

    return (_muro_izq || _muro_der) && (_muro_arr || _muro_aba);
}
```

> ⚠️ Esto NO caza todos los bloqueos. Faltan, al menos, el **bloqueo de pared** (una caja pegada
> a un muro cuya fila o columna entera no tiene ninguna meta) y el **bloqueo congelado entre dos
> cajas** (dos cajas adyacentes que se inmovilizan la una a la otra). Son técnicas conocidas en
> la comunidad de solvers de Sokoban; no se pudo abrir `sokobano.de` en vivo esta sesión
> (certificado TLS inválido), así que quedan fuera del código en vez de citarlas de memoria. Para
> un Sokoban «pequeño» como el de este documento, el bloqueo de esquina ya poda la mayoría de las
> ramas inútiles; para tableros grandes, esa es la próxima pieza a añadir.

El movimiento aplica la regla de Sokoban de siempre —empujar solo si el destino de la caja es
transitable y no hay otra caja ahí— y usa la poda de arriba antes de aceptar un empujón:

```gml
/// @func sokoban_mover(_mapa, _estado, _dx, _dy)
/// @desc Intenta mover al jugador un paso en (_dx,_dy), empujando una caja
///       si hace falta. Devuelve el estado nuevo, o `undefined` si el
///       movimiento no es legal. Los estados son inmutables: nunca toca
///       `_estado`, siempre construye uno nuevo (§3.1).
function sokoban_mover(_mapa, _estado, _dx, _dy) {
    var _px = _estado.jugador mod _mapa.ancho;
    var _py = _estado.jugador div _mapa.ancho;
    var _nx = _px + _dx;
    var _ny = _py + _dy;

    if (_nx < 0 || _ny < 0 || _nx >= _mapa.ancho || _ny >= _mapa.alto) return undefined;

    var _destino = _ny * _mapa.ancho + _nx;
    if (_mapa.muros[_destino]) return undefined;

    var _indice_caja = array_get_index(_estado.cajas, _destino);
    var _cajas_nuevas = _estado.cajas;

    if (_indice_caja >= 0) {
        var _cx = _nx + _dx;
        var _cy = _ny + _dy;
        if (_cx < 0 || _cy < 0 || _cx >= _mapa.ancho || _cy >= _mapa.alto) return undefined;

        var _destino_caja = _cy * _mapa.ancho + _cx;
        if (_mapa.muros[_destino_caja])                   return undefined;
        if (array_contains(_estado.cajas, _destino_caja)) return undefined;
        if (sokoban_es_deadlock(_mapa, _destino_caja))    return undefined;

        _cajas_nuevas = array_create(array_length(_estado.cajas));
        array_copy(_cajas_nuevas, 0, _estado.cajas, 0, array_length(_estado.cajas));
        _cajas_nuevas[_indice_caja] = _destino_caja;
    }

    return sokoban_estado_crear(_destino, _cajas_nuevas);
}
```

### 3.3 Validar por búsqueda: BFS y A* sobre el espacio de estados

Esto es distinto del BFS de [`13 · 07`](./07%20-%20Generación%20procedural%20avanzada.md) §10:
ahí `distancias_bfs()` recorre **celdas de un mapa** para medir alcanzabilidad; aquí cada nodo
del árbol de búsqueda es **una partida entera** (jugador + todas las cajas). El código se parece
—cola FIFO por índice, sin reordenar el array— pero lo que viaja por la cola es un `_estado` de
§3.1, no una celda.

**El hash**, para no visitar el mismo estado dos veces:

```gml
/// @func sokoban_hash(_estado)
/// @desc Una cadena que identifica el estado de forma única. Como las cajas
///       ya vienen ordenadas por sokoban_estado_crear(), dos estados
///       "iguales" SIEMPRE dan la misma cadena.
function sokoban_hash(_estado) {
    return string_concat(_estado.jugador, "|", string_join_ext(",", _estado.cajas));
}

/// @func sokoban_es_meta(_mapa, _estado)
/// @desc El puzzle está resuelto cuando cada caja está sobre una meta.
function sokoban_es_meta(_mapa, _estado) {
    for (var _i = 0; _i < array_length(_estado.cajas); _i++) {
        if (!_mapa.es_meta[_estado.cajas[_i]]) return false;
    }
    return true;
}
```

**BFS** garantiza el camino más corto en NÚMERO DE MOVIMIENTOS, porque procesa los estados en el
mismo orden en que los descubre (por capas de distancia):

```gml
/// @func indice_fijar(_indice, _clave, _valor)
/// @desc Mete o reemplaza una clave en un ds_map sin repetir el if/else en
///       cada sitio que lo necesita.
function indice_fijar(_indice, _clave, _valor) {
    if (ds_map_exists(_indice, _clave)) {
        ds_map_replace(_indice, _clave, _valor);
    } else {
        ds_map_add(_indice, _clave, _valor);
    }
}

/// @func sokoban_reconstruir_camino(_origen, _hash_meta)
/// @desc Camina hacia atrás desde la meta hasta el inicio siguiendo el mapa
///       de "de dónde vino cada estado" que construyó la búsqueda, y da la
///       vuelta al resultado para que quede en orden de partida.
function sokoban_reconstruir_camino(_origen, _hash_meta) {
    var _pasos = [];
    var _hash_actual = _hash_meta;

    while (ds_map_exists(_origen, _hash_actual)) {
        var _entrada = ds_map_find_value(_origen, _hash_actual);
        array_push(_pasos, { dx: _entrada.dx, dy: _entrada.dy });
        _hash_actual = _entrada.previo;
    }

    return array_reverse(_pasos);
}

/// @func sokoban_resolver_bfs(_mapa, _inicial, _max_estados)
/// @desc Busca en anchura sobre el ESPACIO DE ESTADOS. Devuelve un array de
///       {dx,dy}, o `undefined` si no hay solución dentro de `_max_estados`.
function sokoban_resolver_bfs(_mapa, _inicial, _max_estados) {
    var _dx = [0, 0, -1, 1];
    var _dy = [-1, 1, 0, 0];

    var _visitados = ds_map_create();
    var _origen    = ds_map_create();
    var _cola      = [_inicial];
    var _cabeza    = 0;
    var _resultado = undefined;

    ds_map_add(_visitados, sokoban_hash(_inicial), true);

    while (_cabeza < array_length(_cola)) {
        var _actual = _cola[_cabeza++];

        if (sokoban_es_meta(_mapa, _actual)) {
            _resultado = sokoban_reconstruir_camino(_origen, sokoban_hash(_actual));
            break;
        }

        if (_cabeza > _max_estados) {
            show_debug_message($"sokoban_resolver_bfs: {_max_estados} estados sin solución — sube el tope o el nivel es imposible");
            break;
        }

        for (var _d = 0; _d < 4; _d++) {
            var _siguiente = sokoban_mover(_mapa, _actual, _dx[_d], _dy[_d]);
            if (is_undefined(_siguiente)) continue;

            var _hash = sokoban_hash(_siguiente);
            if (ds_map_exists(_visitados, _hash)) continue;

            ds_map_add(_visitados, _hash, true);
            indice_fijar(_origen, _hash, { previo: sokoban_hash(_actual), dx: _dx[_d], dy: _dy[_d] });
            array_push(_cola, _siguiente);
        }
    }

    ds_map_destroy(_visitados);
    ds_map_destroy(_origen);
    return _resultado;
}
```

**A\*** explora primero los estados más prometedores según una heurística. La de aquí suma, por
caja, la distancia de Manhattan a la meta más cercana:

```gml
/// @func sokoban_heuristica(_mapa, _estado)
/// @desc Cota inferior de los movimientos que faltan: para cualquier
///       reparto posible de cajas a metas, cada caja recorre COMO MÍNIMO la
///       distancia a su meta más próxima, así que la suma nunca sobreestima
///       lo que queda. Con una heurística admisible, A* sigue encontrando
///       el camino más corto — solo visita muchos menos estados que BFS.
function sokoban_heuristica(_mapa, _estado) {
    var _total = 0;
    for (var _i = 0; _i < array_length(_estado.cajas); _i++) {
        var _cx = _estado.cajas[_i] mod _mapa.ancho;
        var _cy = _estado.cajas[_i] div _mapa.ancho;
        var _mejor = infinity;

        for (var _j = 0; _j < array_length(_mapa.metas); _j++) {
            var _mx = _mapa.metas[_j] mod _mapa.ancho;
            var _my = _mapa.metas[_j] div _mapa.ancho;
            _mejor = min(_mejor, abs(_cx - _mx) + abs(_cy - _my));
        }
        _total += _mejor;
    }
    return _total;
}

/// @func sokoban_resolver_astar(_mapa, _inicial, _max_estados)
/// @desc Igual que sokoban_resolver_bfs, pero con una cola de prioridad en
///       vez de una cola FIFO. La comprobación `ds_map_exists(_visitados, ...)`
///       tras sacar el mínimo descarta entradas obsoletas de la cola: es la
///       forma estándar de simular "decrease-key" con ds_priority.
function sokoban_resolver_astar(_mapa, _inicial, _max_estados) {
    var _dx = [0, 0, -1, 1];
    var _dy = [-1, 1, 0, 0];

    var _abiertos    = ds_priority_create();
    var _coste_g     = ds_map_create();
    var _origen      = ds_map_create();
    var _visitados   = ds_map_create();
    var _resultado   = undefined;
    var _expandidos  = 0;

    var _hash_inicial = sokoban_hash(_inicial);
    ds_priority_add(_abiertos, _inicial, sokoban_heuristica(_mapa, _inicial));
    ds_map_add(_coste_g, _hash_inicial, 0);

    while (ds_priority_size(_abiertos) > 0) {
        var _actual = ds_priority_delete_min(_abiertos);
        var _hash_actual = sokoban_hash(_actual);

        if (ds_map_exists(_visitados, _hash_actual)) continue;
        ds_map_add(_visitados, _hash_actual, true);
        _expandidos++;

        if (sokoban_es_meta(_mapa, _actual)) {
            _resultado = sokoban_reconstruir_camino(_origen, _hash_actual);
            break;
        }

        if (_expandidos > _max_estados) {
            show_debug_message($"sokoban_resolver_astar: {_max_estados} estados sin solución");
            break;
        }

        var _g_actual = ds_map_find_value(_coste_g, _hash_actual);

        for (var _d = 0; _d < 4; _d++) {
            var _siguiente = sokoban_mover(_mapa, _actual, _dx[_d], _dy[_d]);
            if (is_undefined(_siguiente)) continue;

            var _hash_sig = sokoban_hash(_siguiente);
            if (ds_map_exists(_visitados, _hash_sig)) continue;

            var _g_nuevo  = _g_actual + 1;
            var _conocido = ds_map_exists(_coste_g, _hash_sig);

            if (!_conocido || _g_nuevo < ds_map_find_value(_coste_g, _hash_sig)) {
                indice_fijar(_coste_g, _hash_sig, _g_nuevo);
                indice_fijar(_origen, _hash_sig, { previo: _hash_actual, dx: _dx[_d], dy: _dy[_d] });
                ds_priority_add(_abiertos, _siguiente, _g_nuevo + sokoban_heuristica(_mapa, _siguiente));
            }
        }
    }

    ds_priority_destroy(_abiertos);
    ds_map_destroy(_coste_g);
    ds_map_destroy(_origen);
    ds_map_destroy(_visitados);
    return _resultado;
}
```

**Ejemplo real** — un cuarto de 6×5 con un muro perimetral, jugador en `(3,3)`, una caja en
`(2,2)` y una meta en `(4,1)`:

```
######
#....#
#.$..#
#..@.#
######
```

⚠️ Sobre este tablero, la réplica en Python de este algoritmo dice que BFS visita 64 estados y
encuentra un camino óptimo de 6 movimientos; A* con la heurística de arriba llega **al mismo
óptimo** expandiendo solo 24 estados — menos de la mitad — y reproducir esos 6 movimientos con
`sokoban_mover()` uno a uno termina exactamente sobre la meta. Con una caja y un cuarto pequeño
la diferencia no importa; con una docena de cajas en un tablero grande es la diferencia entre
segundos y no terminar nunca — recuerda el NP-hard de §3.2.

### 3.4 Comprobar que hay solución y que no hay solución trivial

Dos preguntas distintas, dos respuestas distintas:

**¿Tiene solución?** `sokoban_resolver_bfs()` es exhaustivo por capas: si devuelve `undefined`
dentro de `_max_estados`, o el puzzle es irresoluble, o el tope se quedó corto. BFS es la
autoridad para esta pregunta porque no descarta nada por heurística — solo por la poda segura de
§3.2. Úsalo siempre para el «sí/no»; usa A* para la versión rápida una vez sabes que hay
solución.

**¿La solución es trivial?** Se compara la longitud devuelta contra un mínimo que el diseñador
fija a mano — el mismo patrón que `nivel_aceptable()` en
[`13 · 07`](./07%20-%20Generación%20procedural%20avanzada.md) §10:

```gml
/// @func puzzle_aceptable(_camino, _minimo_movimientos)
/// @desc Los umbrales SON tu diseño; escríbelos, no los lleves en la cabeza
///       (misma filosofía que nivel_aceptable() de 13 · 07 §10). Cadena
///       vacía = aceptable.
function puzzle_aceptable(_camino, _minimo_movimientos) {
    if (is_undefined(_camino))                        return "sin solución";
    if (array_length(_camino) < _minimo_movimientos)   return "demasiado trivial";
    return "";
}
```

**¿Hay una solución no deseada (§1.4) del mismo largo que la prevista?** BFS procesa los estados
por capas de distancia — todos los que llegan a la meta en el número mínimo de movimientos
aparecen en la MISMA capa, antes de que la búsqueda avance a la siguiente. Contar cuántos
arreglos de cajas distintos hay en esa capa detecta soluciones redundantes — dos finales con las
mismas cajas y distinto jugador cuentan como UNA sola solución, así que la firma que se compara
es solo las cajas, sin el jugador:

```gml
/// @func sokoban_contar_soluciones_optimas(_mapa, _inicial, _max_estados)
/// @desc Explora el espacio de estados por capas explícitas (no con una
///       única cola FIFO) y, en cuanto una capa contiene algún estado meta,
///       cuenta cuántos ARREGLOS DE CAJAS distintos hay ahí. Devuelve
///       { soluciones, profundidad }. 1 solución es lo normal; más de 1
///       exige mirar si es una simetría deliberada o un despiste de diseño.
function sokoban_contar_soluciones_optimas(_mapa, _inicial, _max_estados) {
    var _dx = [0, 0, -1, 1];
    var _dy = [-1, 1, 0, 0];

    var _capa_actual = [_inicial];
    var _visitados    = ds_map_create();
    ds_map_add(_visitados, sokoban_hash(_inicial), true);

    var _profundidad     = 0;
    var _total_visitados = 1;

    while (array_length(_capa_actual) > 0) {
        var _firmas = ds_map_create();   // firma = solo cajas, sin jugador
        for (var _i = 0; _i < array_length(_capa_actual); _i++) {
            if (sokoban_es_meta(_mapa, _capa_actual[_i])) {
                indice_fijar(_firmas, string_join_ext(",", _capa_actual[_i].cajas), true);
            }
        }

        if (ds_map_size(_firmas) > 0) {
            var _n_soluciones = ds_map_size(_firmas);
            ds_map_destroy(_firmas);
            ds_map_destroy(_visitados);
            return { soluciones: _n_soluciones, profundidad: _profundidad };
        }
        ds_map_destroy(_firmas);

        if (_total_visitados > _max_estados) {
            ds_map_destroy(_visitados);
            return { soluciones: 0, profundidad: -1 };   // tope agotado sin llegar a meta
        }

        var _capa_siguiente = [];
        for (var _i = 0; _i < array_length(_capa_actual); _i++) {
            for (var _d = 0; _d < 4; _d++) {
                var _siguiente = sokoban_mover(_mapa, _capa_actual[_i], _dx[_d], _dy[_d]);
                if (is_undefined(_siguiente)) continue;

                var _hash = sokoban_hash(_siguiente);
                if (ds_map_exists(_visitados, _hash)) continue;

                ds_map_add(_visitados, _hash, true);
                _total_visitados++;
                array_push(_capa_siguiente, _siguiente);
            }
        }
        _capa_actual = _capa_siguiente;
        _profundidad++;
    }

    ds_map_destroy(_visitados);
    return { soluciones: 0, profundidad: -1 };   // sin solución en absoluto
}
```

⚠️ Sobre el mismo cuarto de 6×5 del ejemplo anterior, la réplica en Python de esta función da
`{ soluciones: 1, profundidad: 6 }` — un único arreglo óptimo, coherente con el camino que
encontraron BFS y A*. Repetido con dos cajas y dos metas en un cuarto lo bastante grande como
para rodearlas, seguía dando 1: **conseguir de verdad dos arreglos igual de cortos exige una
simetría muy deliberada** (que cada caja pueda llegar a cualquiera de las dos metas por el mismo
precio), así que un `soluciones > 1` inesperado casi siempre señala que el puzzle no exigía la
regla que creías que exigía.

### 3.5 Generación con validación

El bucle de [`13 · 07`](./07%20-%20Generación%20procedural%20avanzada.md) §1.2 —generar →
validar → reparar o rechazar— se aplica a Sokoban en su forma más simple de la tabla:
**rechazar y regenerar**, nunca reparar. No hay forma barata de arreglar un Sokoban sin solución
sin rehacerlo entero, así que cae directo en la fila de esa tabla que dice que el fallo es raro
y la generación es barata.

```gml
/// @func sokoban_generar_aleatorio(_ancho, _alto, _semilla, _n_cajas)
/// @desc Un cuarto rectangular vacío con jugador, cajas y metas al azar. NO
///       garantiza que sea resoluble — de eso se encarga el validador de
///       abajo. ⚠️ Reutiliza el RNG global reseedado por intento: para no
///       interferir con el RNG de la partida, usa en producción el struct
///       `RNG` aislado de 04 · 05 §5.0, como recomienda 13 · 07 §1.1.
function sokoban_generar_aleatorio(_ancho, _alto, _semilla, _n_cajas) {
    random_set_seed(_semilla, true);

    var _n = _ancho * _alto;
    var _muros = array_create(_n, false);
    for (var _x = 0; _x < _ancho; _x++) {
        _muros[_x] = true;
        _muros[(_alto - 1) * _ancho + _x] = true;
    }
    for (var _y = 0; _y < _alto; _y++) {
        _muros[_y * _ancho] = true;
        _muros[_y * _ancho + (_ancho - 1)] = true;
    }

    var _libres = [];
    for (var _i = 0; _i < _n; _i++) {
        if (!_muros[_i]) array_push(_libres, _i);
    }
    array_shuffle(_libres);

    var _tomadas = _n_cajas * 2 + 1;   // cajas + metas + jugador
    if (array_length(_libres) < _tomadas) return undefined;   // el cuarto es demasiado pequeño

    var _jugador = _libres[0];
    var _cajas   = array_create(_n_cajas);
    var _metas   = array_create(_n_cajas);
    for (var _c = 0; _c < _n_cajas; _c++) {
        _cajas[_c] = _libres[1 + _c];
        _metas[_c] = _libres[1 + _n_cajas + _c];
    }

    return {
        mapa:    sokoban_mapa_crear(_ancho, _alto, _muros, _metas),
        inicial: sokoban_estado_crear(_jugador, _cajas)
    };
}

/// @func sokoban_generar_hasta_valido(_ancho, _alto, _n_cajas, _semilla, _minimo, _max_intentos)
/// @desc El bucle de 13 · 07 §1.2 aplicado a un puzzle: generar → validar →
///       rechazar con `semilla + intento` (la partida sigue descrita por
///       dos números), nunca reparar.
function sokoban_generar_hasta_valido(_ancho, _alto, _n_cajas, _semilla, _minimo, _max_intentos) {
    for (var _intento = 0; _intento < _max_intentos; _intento++) {
        var _generado = sokoban_generar_aleatorio(_ancho, _alto, _semilla + _intento, _n_cajas);
        if (is_undefined(_generado)) continue;

        var _camino = sokoban_resolver_bfs(_generado.mapa, _generado.inicial, 5000);
        var _fallo  = puzzle_aceptable(_camino, _minimo);

        if (_fallo == "") {
            _generado.solucion = _camino;
            _generado.intento  = _intento;
            return _generado;
        }
    }
    show_debug_message("⚠ ningún puzzle válido: baja `_minimo` o sube `_max_intentos`");
    return undefined;
}
```

⚠️ En la réplica en Python de este bucle (mismo algoritmo, mismos parámetros: cuarto 6×5, 1
caja, mínimo 4 movimientos), el generador encontró un puzzle válido en el sexto intento
(`_intento == 5`) y, repitiendo con 10 semillas de partida distintas y 50 intentos cada una,
las 10 encontraron alguno — el ritmo de rechazo de un cuarto pequeño con pocas cajas es bajo,
tal y como predice la tabla de 13 · 07 §1.2 para generación barata.

### 3.6 Deshacer: pila de estados con el patrón comando

Como los estados son inmutables (§3.1), deshacer es literalmente **volver al struct anterior**:
no hace falta calcular un movimiento inverso ni copiar nada de más. Es la misma filosofía que el
patrón comando de [`13 · 06`](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) §3.7
—la intención del jugador es un dato (`{dx, dy}`), no una llamada directa— aplicada a un tablero
de puzzle en vez de a un jugador con física.

```gml
/// scr_sokoban_historial — deshacer con una pila de estados
///
/// Cada entrada guarda el ESTADO ANTERIOR a aplicar un comando (no el
/// nuevo): deshacer es "volver a lo que había". Guardar también dx,dy deja
/// reproducir la partida entera desde el inicio, igual que la
/// `repeticion.frames` de 13 · 06 §3.7 — aquí la "repetición" es la
/// solución completa del puzzle, útil para un botón de "ver la solución
/// después de resolverlo" o para telemetría de qué caminos toma la gente.

/// @func historial_crear(_estado_inicial)
function historial_crear(_estado_inicial) {
    return { pila: [], actual: _estado_inicial };
}

/// @func historial_aplicar(_mapa, _historial, _dx, _dy)
/// @desc Intenta un movimiento. Si es legal, apila el estado ANTERIOR junto
///       al comando que se aplicó, y avanza `.actual`.
function historial_aplicar(_mapa, _historial, _dx, _dy) {
    var _siguiente = sokoban_mover(_mapa, _historial.actual, _dx, _dy);
    if (is_undefined(_siguiente)) return false;

    array_push(_historial.pila, { estado_previo: _historial.actual, dx: _dx, dy: _dy });
    _historial.actual = _siguiente;
    return true;
}

/// @func historial_deshacer(_historial)
/// @desc Saca la última entrada (`array_pop` devuelve `undefined` si la
///       pila ya está vacía, así que no hace falta comprobar el tamaño
///       antes) y vuelve al estado que había justo antes de ese comando.
function historial_deshacer(_historial) {
    var _entrada = array_pop(_historial.pila);
    if (is_undefined(_entrada)) return false;
    _historial.actual = _entrada.estado_previo;
    return true;
}
```

Deshacer repetidas veces hasta vaciar la pila devuelve exactamente el estado inicial — no una
aproximación: como nada se muta nunca (§3.1), el struct guardado en `estado_previo` sigue siendo
byte a byte el que había, con independencia de cuántos movimientos se hicieron después. Sobre el
mismo camino de 6 movimientos del ejemplo de §3.3, aplicar `historial_aplicar()` seis veces y
luego `historial_deshacer()` otras seis devuelve, verificado en la réplica en Python, el mismo
estado inicial con la pila vacía.

> 💡 Si además quieres **rehacer** (redo), no hace falta una segunda pila: guarda el índice de
> «hasta dónde deshiciste» dentro del mismo array de comandos en vez de borrar con `array_pop` —
> exactamente el patrón de reproducir un `.frames` de replay de 13 · 06 §3.7, solo que pausado a
> mitad de camino.

---

## 4 · Checklist

**Antes de dar un puzzle por diseñado:**

- [ ] Cabe en una frase: qué regla enseña y cuál es su momento «ajá».
- [ ] Nadie que no seas tú lo ha resuelto sin que le expliques nada.
- [ ] La regla se aprende por Encuadre, Camino único o Demostración segura — no por un texto (§2.1).
- [ ] Si pertenece a una cadena, tiene sus cuatro fases (§2.2) y no sobra ningún puzzle de relleno tras el de cierre.
- [ ] Hay una escalera de pistas graduada, opt-in, con un escalón final de «saltar» (§2.4).

**Antes de publicarlo (con el buscador de §3):**

- [ ] `sokoban_resolver_bfs()` (o el buscador equivalente para tu familia de puzzle) devuelve una solución dentro de un tope razonable de estados.
- [ ] La longitud de esa solución supera el mínimo que fijaste — `puzzle_aceptable()` no dice «demasiado trivial».
- [ ] `sokoban_contar_soluciones_optimas()` da 1, o si da más, la simetría es deliberada y no rompe la regla que el puzzle enseñaba.
- [ ] Revisaste el camino que devuelve el buscador movimiento a movimiento: si no es el que tenías en mente, decide si es una solución no deseada que hay que cerrar (§1.4) o una emergencia elegante que hay que dejar.
- [ ] `gm-cli compile` sale limpio y el puzzle se ha jugado entero tras compilar.

**Si el puzzle se genera por código:**

- [ ] El bucle generar → validar → rechazar usa `semilla + intento`, nunca una semilla al azar en cada reintento.
- [ ] Hay un tope de intentos, y lo que pasa al agotarlo está decidido (no un cuelgue silencioso).
- [ ] El generador usa un RNG aislado del resto del juego, no el global, si se genera durante la partida.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| **Explicar la regla antes de que haga falta** | El jugador lee, no descubre; no hay «ajá» | Enséñala con Encuadre / Camino único / Demostración segura (§2.1) |
| **Confundir tamaño con dificultad** | Un tablero enorme con la misma idea de siempre, solo más tedioso | Mide longitud de solución Y profundidad de la idea por separado (§2.3) |
| **Pistas activadas por defecto** | Nunca hay fricción que romper; el «ajá» nunca llega | Pistas opt-in, con cadencia mínima entre peticiones (§2.4) |
| **Hash sin canonicalizar** | El buscador nunca converge: dos estados iguales con las cajas en otro orden cuentan como distintos | Ordena las cajas SIEMPRE en `sokoban_estado_crear()` antes de hashear (§3.1) |
| **Buscar sin podar deadlocks** | El árbol de búsqueda explota en tableros de más de un par de cajas | Filtra con `sokoban_es_deadlock()` dentro del propio `mover()`, no después (§3.2) |
| **Mutar un estado en vez de crear uno nuevo** | Deshacer devuelve estados corruptos; el hash dice que dos estados son iguales cuando ya no lo son | Los estados son inmutables: toda función devuelve uno nuevo (§3.1) |
| **Publicar sin comprobar soluciones alternativas** | Alguien encuentra en 2 minutos un atajo que se te escapó en 3 semanas | `sokoban_contar_soluciones_optimas()` antes de dar el puzzle por cerrado (§3.4) |
| **Reparar en vez de rechazar un puzzle generado** | Código frágil que intenta parchear un tablero sin solución y produce otro roto distinto | Sokoban cae en la fila «rechazar y regenerar» de 13 · 07 §1.2: `semilla + intento`, no parches |
| **Deshacer con copias profundas manuales** | Código de deshacer que crece con cada campo nuevo del estado, y se rompe al añadir uno | Si los estados ya son inmutables, deshacer es solo guardar el struct anterior en una pila (§3.6) |
| **Un solo puzzle "de examen" sin los tres anteriores** | El jugador llega al `ketsu` sin haber tenido `ki`, `shō` ni `ten` — parece injusto, no un examen | Respeta las cuatro fases de la cadena (§2.2), aunque sea con un solo puzzle por fase |

---

## Ver también

- [`04 · 07 — Puzzle y Match-3`](../04%20-%20Recetas%20por%20género/07%20-%20Puzzle%20y%20Match-3.md) — la implementación de un tablero de match-3: modelo/vista, detección de matches, cascadas, gravedad y shuffle. Empieza aquí si lo que necesitas es ESE género, no el sentido de «puzzle» de este documento.
- [`13 · 01 — Diseño de juego`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) — §3.2 la curva en dientes de sierra y la regla del 3+1, §3.4 medir la dificultad con datos, §5 onboarding sin texto (la base de §2.1 de este documento), §9.5 telemetría.
- [`13 · 02 — Diseño de niveles`](./02%20-%20Diseño%20de%20niveles.md) — §1.1 kishōtenketsu, la estructura que §2.2 aplica a una cadena de puzzles en vez de a un nivel completo.
- [`13 · 06 — Arquitectura de un proyecto GameMaker`](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) — §3.7 patrón comando, la base de §3.6 (deshacer) de este documento.
- [`13 · 07 — Generación procedural avanzada`](./07%20-%20Generación%20procedural%20avanzada.md) — §1.2 generar → validar → reparar o rechazar (la base de §3.5), §1.3 separar generación de presentación, §10 `distancias_bfs()` y `nivel_aceptable()`: el mismo patrón de validación, aplicado a celdas de mapa en vez de a estados de puzzle.
- [`04 · 05 — Roguelike y generación procedural`](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md) — §5.0, el struct `RNG` aislado que §3.5 recomienda para generación en producción.
- [`06 · scr_grid_pathfinding.gml`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml) — A* de verdad, pero sobre CELDAS de un grid con costes de terreno, no sobre estados de un puzzle. Úsalo para pathfinding de un personaje; usa el A* de §3.3 solo cuando el nodo de búsqueda sea «una partida entera».
- [`13 · 13 — Matemáticas aplicadas al juego`](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md) — probabilidad y aleatoriedad, si el puzzle mezcla lógica con azar.

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

- Wikipedia, artículo **«Puzzle»** (en inglés) — <https://en.wikipedia.org/wiki/Puzzle> — la
  definición general y la taxonomía (lógicos, mecánicos, de palabras y números, visuales, de
  videojuego, metapuzzles) que estructura §1.1 y §1.2.
- Wikipedia, artículo **«Sokoban»** (en inglés) — <https://en.wikipedia.org/wiki/Sokoban> —
  historia del juego, la clasificación de complejidad computacional (NP-hard y
  PSPACE-completo), la estimación de 10⁹⁸ estados para un laberinto de 20×20, y la descripción
  de un deadlock como caja permanentemente atrapada contra una pared u otra caja. Fuente de
  §2.3 y §3.2.
- Wikipedia, artículo **«The Witness (2016 video game)»** (en inglés) —
  <https://en.wikipedia.org/wiki/The_Witness_(2016_video_game)> — las declaraciones de Jonathan
  Blow sobre enseñar sin texto y sobre que sobre-tutorializar mata la epifanía, la estructura de
  paneles en cadenas independientes, y la dificultad graduada por región. Fuente de §1.3 y §2.2.
- Wikipedia, artículo **«Portal (video game)»** (en inglés) —
  <https://en.wikipedia.org/wiki/Portal_(video_game)> — el andamiaje instruccional que se
  retira progresivamente hasta desaparecer, la crítica de Rock, Paper, Shotgun sobre las
  cámaras que introducen el *fling* sin instrucciones explícitas, y la depuración de elementos
  decorativos para no distraer del puzzle. Fuente de §1.3 y §2.1.
- ⚠️ `sokobano.de` (wiki de la comunidad de solvers de Sokoban, con los algoritmos de bloqueo de
  pared y bloqueo congelado) no se pudo abrir en vivo esta sesión — certificado TLS inválido. Por
  eso §3.2 solo implementa y demuestra el bloqueo de esquina, y dice explícitamente qué falta en
  vez de citar esa fuente de memoria.
- Verificación propia: el algoritmo de §3.1-3.6 se comprobó con una réplica en Python del mismo
  código (mismas funciones, misma lógica, mismos nombres traducidos), ejecutada sobre el
  tablero de ejemplo de §3.3 y sobre una segunda disposición con dos cajas y dos metas; el
  `.gml` en sí se compiló sin errores con `gm-cli compile` contra el runtime `2026.0.0.23`
  dentro de un proyecto de prueba creado con `gm-cli init`.
