# 45 · Géneros sin receta propia — sigilo, horror, táctica, granja y idle

> Cinco géneros que la auditoría de diseño de 2026-09-06 encontró sin cubrir, o cubiertos con
> una sola fila de tabla. Esto **no es** una receta completa por género — serían cinco
> documentos del tamaño de `04 · 09` cada uno—. Es lo que falta de verdad: la **convención**
> que el jugador trae puesta al sentarse a jugar, los **tres sistemas críticos** que definen el
> género, y a qué receta y a qué documento de `13` apoyarte para construirlos. Donde el material
> técnico ya existe en otro sitio, este documento **enlaza y no repite una línea**; el código que
> sí aparece aquí es el que no estaba escrito en ningún otro documento de la biblioteca.

---

## 1 · Qué cubre este documento, y qué no

| Género | Qué había antes | Qué falta y este documento cierra | Técnica que YA existe (se enlaza) |
|---|---|---|---|
| **Sigilo** | Una fila de tabla en `04 · 02 §1` | El diseño: estados de alerta, y el medidor de detección | `13 · 13 §2.4` (cono de visión), `04 · 31 §5 y §11` (línea de visión, oído, memoria) |
| **Horror** | 0 apariciones | Convención, escasez, el enemigo intocable, sonido como amenaza | `13 · 09` (sonido), `04 · 42` (audio reactivo), `04 · 23`/`04 · 31` (IA de persecución y percepción) |
| **Táctica por turnos** | Una fila de tabla en `04 · 04 §1` | Casi nada de código nuevo: `04 · 35` ya lo tiene todo | `04 · 35` completo (rejilla, línea de tiro, turnos, IA de posicionamiento) |
| **Granja / pesca / cozy** | Una fila de tabla en `04 · 09 §1` | Calendario y estaciones, cultivos por celda, relaciones con regalo diario | `04 · 24 §6` (ciclo día/noche), `04 · 09 §5.5` (el reloj), `04 · 10 §5.2` (afinidad) |
| **Idle / incremental** | Solo una serie de YouTube citada en `03` | Números grandes, y sobre todo el progreso offline | `13 · 13 §8.1` (curva exponencial), `13 · 01 §4.4` (coste geométrico), `13 · 16 §2.4-2.6` (prestigio) |

Si tu juego mezcla dos de estos géneros (un roguelike de sigilo, una granja con combate
táctico), lee las dos secciones: los sistemas de este documento están escritos para
combinarse sin pisarse — todos usan el mismo patrón de señales de
[04 · 16](./16%20-%20Señales%20y%20desacoplamiento.md).

---

## 2 · Sigilo

### 2.1 · La convención: qué espera el jugador

Un jugador de sigilo espera tres promesas, y romperlas se nota más que en casi ningún otro
género:

1. **El peligro es legible ANTES de ocurrir.** Si te descubren sin haber visto venir el motivo,
   el juego hizo trampa. El cono de visión, la línea de visión y el medidor de detección
   (§2.2-§2.4) existen para eso.
2. **Fallar tiene grados, no un interruptor.** *Mark of the Ninja* resume la idea con un diseño
   muy simple: los enemigos muestran un signo de interrogación cuando **sospechan** y una
   exclamación cuando te han **visto de verdad** — dos estados, no uno — y el juego además
   oculta al jugador cualquier enemigo que el propio personaje no podría ver, para que la
   información en pantalla sea siempre la que el personaje tendría[^1].
3. **Siempre hay una salida.** Romper la línea de visión y esconderte debe funcionar. Si un
   enemigo alertado te encuentra igual pase lo que pases, el sigilo deja de ser un sistema y pasa
   a ser una cinemática que finges controlar.

> **La «regla del segundo intento».** Ser detectado no debería significar recargar la partida
> automáticamente. O bien la alerta es **recuperable** (el enemigo te pierde si rompes línea de
> visión el tiempo suficiente, §2.4) y pasa a combate/persecución en vez de a un fin de partida
> — la vía que construye este documento —, o bien tu diseño exige un fallo duro (sigilo puro,
> re-empezar el nivel) y entonces el coste de ese segundo intento se paga en **diseño de nivel**,
> no en el sistema de detección: el último punto de control se coloca justo antes de la zona de
> riesgo (`13 · 02` — hoja de nivel y checkpoints), para que fallar cueste segundos, no minutos.

### 2.2 · Sistema crítico 1 — cono de visión y línea de visión (ya existe)

Esto **ya está resuelto** y no se repite:

- El **cono de visión** con el ángulo real (producto escalar normalizado, sin arcocosenos) es
  `en_cono_vision()` en
  [13 · 13 §2.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md#24--cono-de-visión-con-el-ángulo-de-verdad).
  Responde «¿puede el enemigo mirar hacia ahí?».
- La **línea de visión** (¿hay una pared en medio?) es `hay_vision_libre()` en
  [04 · 31 §5](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md#5--un-enemigo-completo),
  sobre `collision_line`. Responde «¿de verdad llega a ver?». El cono decide **dónde puede**
  mirar; el rayo decide **qué llega a ver** — son preguntas distintas y hacen falta las dos.
- El **oído** (radio sin rayo, más barato y da mejor juego) y la **memoria** (última posición
  conocida, investigación tras perder de vista) están completos en
  [04 · 31 §11](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md#11--percepción-ver-oír-recordar-y-avisar),
  con el patrón de alerta de grupo por señales.

Lo que **falta** encima de esto es el diseño: qué significan esos datos para el jugador, y eso
son §2.3 y §2.4.

### 2.3 · Sistema crítico 2 — estados de alerta legibles

Cuatro estados, no dos ni veinte. Menos de cuatro no distingue «sospecha» de «combate»; más de
cuatro es ruido que el jugador no puede leer de un vistazo.

```gml
enum EstadoAlerta { DESPREVENIDO, SOSPECHA, ALERTA, COMBATE }
```

Esto se añade a la **misma pizarra** que ya usa `04 · 31` (`pizarra.alerta`, `pizarra.ultima_x`,
`pizarra.ultima_y`): no es un sistema paralelo, son dos campos más sobre la estructura que ya
existe.

```gml
/// obj_guardia · Create — dos campos nuevos sobre la pizarra de 04 · 31 §3
pizarra.estado_alerta = EstadoAlerta.DESPREVENIDO;
pizarra.deteccion     = 0;                  // 0..100 — el medidor de §2.4

#macro DETECCION_SUBIDA        55           // puntos/seg mientras el jugador está a la vista
#macro DETECCION_BAJADA        25           // puntos/seg al perderlo de vista
#macro DETECCION_UMBRAL_ALERTA 100
```

### 2.4 · Sistema crítico 3 — el medidor de detección, y cómo cambia de estado

*Splinter Cell* resuelve la legibilidad con un **medidor de luz** permanente en pantalla que
dice «cuán visible eres ahora mismo», útil incluso cuando el ojo no puede juzgarlo a simple
vista (gafas de visión nocturna, penumbra)[^2]. La misma idea, invertida, sirve para «cuánto te
está detectando el enemigo»: en vez de un interruptor «visto / no visto», un valor 0-100 que
sube mientras el cono te ve sin obstáculos y baja cuando te pierde. Es exactamente el patrón de
`ia_ve_al_jugador()` de `04 · 31 §5` (que ya cachea una comprobación por tick), con un
acumulador encima.

```gml
/// obj_guardia · Step — un tick de detección, aparte del árbol (que decide QUÉ hacer)
var _visto = ia_ve_al_jugador(pizarra);            // 04 · 31 §5, ya cacheado 1 vez por tick
var _dt    = delta_time / 1000000;

pizarra.deteccion += (_visto ? DETECCION_SUBIDA : -DETECCION_BAJADA) * _dt;
pizarra.deteccion  = clamp(pizarra.deteccion, 0, 100);

var _anterior = pizarra.estado_alerta;
if      (pizarra.deteccion >= DETECCION_UMBRAL_ALERTA) { pizarra.estado_alerta = EstadoAlerta.COMBATE; }
else if (pizarra.deteccion >= 60)                      { pizarra.estado_alerta = EstadoAlerta.ALERTA; }
else if (pizarra.deteccion >= 20)                      { pizarra.estado_alerta = EstadoAlerta.SOSPECHA; }
else                                                    { pizarra.estado_alerta = EstadoAlerta.DESPREVENIDO; }

if (pizarra.estado_alerta != _anterior) {
    senal_emitir("cambio_alerta", { guardia: id, de: _anterior, a: pizarra.estado_alerta });
}
```

> 💡 **La «regla del segundo intento» sale gratis de esta misma cuenta.** Como `deteccion` BAJA
> sola en cuanto rompes línea de visión, `COMBATE` no es un callejón sin salida: si el jugador
> se esconde el tiempo suficiente, el contador desciende solo de vuelta a `ALERTA` →
> `SOSPECHA` → `DESPREVENIDO`, sin ningún código adicional de «perdonar». Que `COMBATE` derive a
> combate real (`04 · 30`/`04 · 34`) o a un *game over* es una decisión de diseño, no de este
> sistema: el medidor solo mide, no castiga.

La representación en pantalla toma prestado el vocabulario visual de *Mark of the Ninja* (icono
sobre la cabeza) y de *Splinter Cell* (barra permanente):

```gml
/// obj_guardia · Draw — icono sobre la cabeza, un signo por estado (Mark of the Ninja)
var _iconos = ["", "?", "!", "!!"];
if (pizarra.estado_alerta != EstadoAlerta.DESPREVENIDO) {
    draw_text(x - 4, y - 40, _iconos[pizarra.estado_alerta]);
}
```

```gml
/// obj_jugador · Draw GUI — el medidor lee la detección MÁS ALTA entre todos los guardias
var _deteccion_maxima = 0;
with (obj_guardia) { _deteccion_maxima = max(_deteccion_maxima, pizarra.deteccion); }

if (_deteccion_maxima > 0) {
    draw_healthbar(20, 20, 140, 32, _deteccion_maxima, c_black, c_yellow, c_red, 0, true, true);
}
```

> 🔺 **No confundas el medidor con la barra de vida.** `draw_healthbar` es solo la función de
> dibujo (rango 0-100, dos colores); no representa vida aquí, representa cuánto te ven. Ponle un
> rótulo o un color inconfundible (amarillo→rojo, nunca verde→rojo como una barra de vida) para
> que el jugador no las confunda a simple vista.

### 2.5 · A qué apoyarte

- Cono, línea de visión, oído y memoria: **ya construidos**, enlazados arriba — no los
  reimplementes.
- Persecución y ataque cuando `estado_alerta` llega a `COMBATE`: la máquina de estados de
  [04 · 31 §5](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md#5--un-enemigo-completo)
  (huir/curarse/perseguir/atacar/patrullar) se reutiliza sin tocarla: `estado_alerta` decide qué
  rama del árbol tiene sentido, el árbol sigue decidiendo cómo ejecutarla.
- Combate cuerpo a cuerpo o a distancia si `COMBATE` deriva en pelea:
  [04 · 30](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md) y
  [04 · 34](./34%20-%20Combate%20a%20distancia%20-%20armas,%20munición%20y%20balística.md).
- Alerta de grupo por señales (un guardia grita, los demás se apuntan):
  [04 · 31 §11](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md#11--percepción-ver-oír-recordar-y-avisar)
  sobre [04 · 16](./16%20-%20Señales%20y%20desacoplamiento.md).

---

## 3 · Horror

### 3.1 · La convención

El terror en un juego no es «un monstruo feo»: es **vulnerabilidad estructural**. Tres reglas
que casi todo horror de éxito respeta:

1. **El jugador es más débil que la amenaza**, casi siempre sin capacidad de matarla —
   *Amnesia*, *Outlast*, *Alien: Isolation*— o con una capacidad tan cara que usarla da miedo
   por sí sola.
2. **Los recursos son escasos y su cantidad restante es incierta.** La ansiedad no viene de
   «tengo poco», viene de «no sé cuánto me queda».
3. **El peligro se telegrafía lo justo.** Sin aviso, el susto es injusto (rompe la promesa de
   legibilidad del §2.1); con demasiado aviso, deja de asustar. El sonido es la herramienta
   principal para ese telegrafiado — más barata y más ambigua que la imagen.

### 3.2 · Sistema crítico 1 — recursos escasos como economía del miedo

Esto es una aplicación del vocabulario de economía que ya tiene la biblioteca, no un sistema
nuevo: fuentes, sumideros, convertidores e intercambiadores están definidos en
[13 · 01 §4.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#41--el-vocabulario-correcto).
En horror, la decisión de diseño es **invertir la proporción** frente a un survival normal: en
`04 · 09` las necesidades (§4.4) tienen una fuente predecible (comer, beber) porque el objetivo
es *gestionar*, no asustar. En horror, la fuente (munición, vendas, pilas) debe ser **rara y
aleatoria** — un cofre que a veces da 2 balas y a veces 0 — para que el jugador nunca calcule
con certeza cuánto tiene garantizado. Es la misma tabla de `04 · 09 §4.4`, con una columna
más: la *varianza* del hallazgo, no solo su tasa media.

```gml
/// scr_horror_recursos — engancha sobre WeaponAmmoState de 04 · 34 §5.1, no lo reescribe.
/// Un arma poco fiable dispara la misma ansiedad que un recurso escaso: el jugador nunca sabe
/// con certeza si el disparo que necesita va a salir.
#macro PROBABILIDAD_ENCASQUILLE 0.06     // 1 de cada ~17 disparos, ajustable con 13 · 01 §9.4

/// @func arma_intentar_disparo(_ammo_state)
/// @desc Llama a esto ANTES de restar munición con WeaponAmmoState (04 · 34 §5.1).
/// @return {Bool} false = se encasquilla: gasta el turno, no la bala.
function arma_intentar_disparo(_ammo_state)
{
    if (random(1) < PROBABILIDAD_ENCASQUILLE) {
        audio_play_sound(snd_arma_encasquillada, 10, false);
        return false;
    }
    return true;
}
```

### 3.3 · Sistema crítico 2 — el enemigo que no se puede matar

Aquí hay una economía de trabajo que conviene aprovechar: **un monstruo de terror es, en la
arquitectura de esta biblioteca, un guardia de sigilo con otra piel.** Reutiliza el medidor de
detección de §2.4 tal cual — el jugador quiere que ese número se mantenga BAJO en vez de
gestionarlo, pero el sistema es idéntico — y la investigación por memoria de
`04 · 31 §11` para que el monstruo vaya a mirar donde te vio por última vez, en vez de
teletransportarse a tu posición actual.

Lo que sí cambia respecto a un guardia:

1. **Nunca es dañable.** No le des un componente de vida: la colisión con él dispara una
   secuencia de captura/muerte, nunca resta puntos de golpe. Es una decisión de diseño en el
   objeto, no un sistema nuevo — simplemente no conectes `dano_resolver()` de `04 · 32` a esta
   instancia.
2. **Investiga sin ruta fija.** *Alien: Isolation* lo describe así en sus propias notas de
   diseño: el sistema de comportamiento del Xenomorfo se va desbloqueando según interactúa con
   el jugador, «creando la ilusión de que el Alien aprende de cada encuentro y ajusta su
   estrategia de caza en consecuencia»[^3]. El diseñador Gary Napper explicó el motivo: «si el
   Alien fuera guionizado, verías el mismo comportamiento. Eso lo vuelve predecible, y mucho
   menos aterrador»[^3]. En GML, la parte que **sí puedes construir** es la rama de
   investigación sin ruta fija que ya escribió `04 · 31 §11` (persigue la última posición
   conocida con `mp_potential_step`, no un camino grabado): reutilízala como el comportamiento
   por defecto del monstruo, y añade variación con `wander` de
   [04 · 23 §3](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md#3--wander--deambular-con-naturalidad)
   mientras patrulla sin pista.
3. **Solo se evade, nunca se enfrenta.** El movimiento de huida del jugador (no del enemigo) usa
   `huir_de()` de
   [04 · 23 §1](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md#1--seek-y-flee--perseguir-y-huir),
   igual que la rama `ia_huir` de `04 · 31 §5` pero con los papeles invertidos.

### 3.4 · Sistema crítico 3 — el sonido como mecánica, y la tensión continua

El principio ya está escrito en
[13 · 09 §1.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#13-oír-siempre-lo-importante)
(«oír siempre lo importante») y su implementación cuantitativa en
[04 · 42 §3.4](./42%20-%20Audio%20reactivo%20al%20mundo%20-%20materiales,%20zonas%20y%20estados%20de%20mezcla.md#34-el-sistema-de-importancia-de-overwatch-puntuar-agrupar-en-cubos-y-resolver-por-frame)
(el sistema de importancia de *Overwatch*, que puntúa y no solo compara volúmenes). En horror,
el sonido no es ambientación: **es el sensor del jugador**, el equivalente al oído del guardia
de `04 · 31 §11` pero para el bando contrario — el crujido de un tablón dice «el monstruo está
cerca» antes de que la cámara lo enseñe.

Lo que falta encima de `04 · 26` (música adaptativa) es una variante: `04 · 26` cambia de capa
por **estados discretos** (`combate_empieza`/`combate_acaba`); el terror necesita una **tensión
continua**, que sube y baja como un dial, no como un interruptor:

```gml
/// obj_musica_horror · Step — variante continua del crossfade de 04 · 26.
/// En vez de un audio_sound_gain(destino, tiempo) puntual por evento, la ganancia SIGUE un
/// valor 0..1 cada frame: la proximidad del monstruo (o su `pizarra.deteccion` de §2.4/§3.3).
var _proximidad = clamp(1 - (point_distance(x, y, obj_monstruo.x, obj_monstruo.y) / 400), 0, 1);
audio_sound_gain(capas.tension, _proximidad, 200);   // 200 ms: sigue el valor sin saltos audibles
```

> 💡 **200 ms, no 0.** Un `audio_sound_gain` instantáneo cada frame suena a temblor eléctrico;
> 150-250 ms suaviza el seguimiento sin que se note el retardo, igual que recomienda `04 · 26`
> para las transiciones por estado.

### 3.5 · A qué apoyarte

- Escasez de recursos: vocabulario de
  [13 · 01 §4.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#41--el-vocabulario-correcto),
  necesidades de [04 · 09 §4.4](./09%20-%20Survival%20y%20crafting.md#44-necesidades).
- Munición y recarga: [04 · 34](./34%20-%20Combate%20a%20distancia%20-%20armas,%20munición%20y%20balística.md)
  — `arma_intentar_disparo()` de §3.2 se engancha antes de `WeaponAmmoState`, no lo sustituye.
- Persecución sin ruta fija y percepción: [04 · 31 §11](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md#11--percepción-ver-oír-recordar-y-avisar),
  esquiva/patrulla en [04 · 23](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md).
- Sonido posicional, oclusión y prioridad de voces: [13 · 09 §5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#5--sonido-posicional-en-2d).
- Curvas de dificultad/tensión (invertidas: aquí sube el miedo, no el poder del jugador):
  [13 · 01 §3.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#32--las-cuatro-formas-de-curva).
- Accesibilidad de fotosensibilidad (los sustos con flash tienen un límite): [04 · 27](./27%20-%20Accesibilidad.md).

---

## 4 · Táctica por turnos

### 4.1 · La convención

Un jugador de táctica por turnos espera un **contrato de confianza numérico**: cada decisión se
toma con información completa o con una probabilidad explícita, nunca a ciegas. *XCOM: Enemy
Unknown* hizo de esto casi todo su diseño de interfaz — «la interfaz informa al jugador de la
posibilidad de acertar un disparo y del daño que va a infligir»[^4] antes de que el jugador
confirme la acción — y la polémica que generó cuando los jugadores sospecharon que las
probabilidades mostradas no coincidían con las tiradas reales («los dados secretos de XCOM:
Enemy Within»[^4]) es la prueba de lo caro que sale romper esa promesa. La rejilla, la cobertura
y el orden de turnos son la gramática; el porcentaje de acierto es el contrato.

### 4.2 · Los tres sistemas críticos, y por qué ya están escritos

Este es el género con **menos código pendiente** de los cinco: `04 · 35` es un documento de
1 700 líneas construido exactamente para esto. No se repite nada; se listan los tres sistemas y
dónde viven:

| Sistema crítico | Dónde está, ya construido |
|---|---|
| **1 · Rejilla táctica**: coste de movimiento (no solo casillas), terreno y altura como multiplicadores | [04 · 35 §1.6-§1.7](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md#16-la-rejilla-táctica-coste-de-movimiento-no-casillas), rango de movimiento por Dijkstra en [§5.10](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md#510-rango-de-movimiento-dijkstra-por-presupuesto) |
| **2 · Línea de tiro y cobertura**: información perfecta antes de comprometerse | [04 · 35 §1.8](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md#18-línea-de-tiro-y-zona-de-amenaza), `linea_de_tiro()` en [§5.12](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md#512-línea-de-tiro-en-rejilla) |
| **3 · Orden de turnos e IA de posicionamiento** | Iniciativa y ATB en [§1.2 y §4.1-§4.2](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md#12-iniciativa-frente-a-atb-dos-relojes-distintos), IA por utilidad en [§5.14](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md#514-ia-de-posicionamiento-por-utilidad) |

### 4.3 · Lo único que falta: la probabilidad de acierto percibida

`04 · 35 §8` deja la precisión como el primer punto de «cómo escalarlo», apoyándose en las
distribuciones de
[13 · 13 §5.1-§5.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md#5--probabilidad-y-aleatoriedad)
— pero ninguno de los dos documentos da la tirada en sí. La lección de la polémica de XCOM no es
técnica, es de diseño: **si vas a mostrar un `73 %`, la tirada real debe sentirse coherente con
ese número a lo largo de una sesión**, aunque un `irandom` uniforme puntual pueda fallar dos
veces seguidas con un 90 %. La misma técnica que ya usa la biblioteca para el crítico —
`13 · 13 §5.7`, «crítico con piedad»— resuelve esto sin trucar el número mostrado:

```gml
/// scr_precision_tactica — variante de "piedad" (13 · 13 §5.7) aplicada al acierto, no al
/// crítico. NO cambia el % mostrado al jugador: reduce la varianza de rachas de fallo largas
/// sin tocar la media a largo plazo.
/// @func ataque_resolver_con_percepcion(_unidad, _probabilidad_pct)
/// @param {Struct} _unidad             La unidad que ataca (necesita el campo `fallos_seguidos`).
/// @param {Real}   _probabilidad_pct   El número que YA se le mostró al jugador, 0..100.
/// @return {Bool} true = acierta.
function ataque_resolver_con_percepcion(_unidad, _probabilidad_pct)
{
    // Cada fallo consecutivo añade un empujón hacia el acierto, con tope: igual que el crítico
    // con piedad, nunca garantiza el acierto, solo hace las rachas largas menos probables.
    var _bono    = min(_unidad.fallos_seguidos * 4, 20);
    var _tirada  = random(100);
    var _acierta = (_tirada < _probabilidad_pct + _bono);

    _unidad.fallos_seguidos = _acierta ? 0 : (_unidad.fallos_seguidos + 1);
    return _acierta;
}
```

> 🔺 **Esto es un ajuste de percepción, no una corrección de un sistema roto.** Si tu `73 %`
> mostrado ya es el `73 %` que tira `random()`, el sistema funciona correctamente — la piedad
> solo existe porque los humanos perciben mal las rachas de una distribución uniforme real. No
> lo apliques a IA competitiva ni a nada que se vaya a auditar por *replay*: ahí, el número
> mostrado debe ser exactamente la probabilidad real, sin ajuste.

### 4.4 · A qué apoyarte

Todo lo demás — el bucle central, el menú de batalla como pila de contextos, habilidades desde
JSON, el `BattleManager`, terreno y altura — está en
[04 · 35](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md). Si el juego
necesita enfriamientos reales entre combates o un árbol de progresión de habilidades, `04 · 35
§8` remite a [04 · 36](./36%20-%20Habilidades,%20enfriamientos%20y%20recursos%20de%20combate.md);
si necesita arquetipos de enemigo con ficha propia y un director de intensidad, remite a
[04 · 33](./33%20-%20Diseño%20de%20enemigos,%20encuentros%20y%20director%20de%20combate.md).

---

## 5 · Granja / pesca / cozy

### 5.1 · La convención

Un *cozy game* (*Stardew Valley* es la referencia canónica del subgénero) invierte
deliberadamente la tensión de un survival: **la ausencia de fracaso es la característica, no un
descuido.** ConcernedApe (Eric Barone) lo hizo explícito frente al modelo de *Harvest Moon* del
que partía: mantuvo el juego abierto «para que los jugadores no sintieran prisa por intentar
completarlo todo»[^5], diseñado «para fomentar un estilo de juego relajado, permitiendo a los
jugadores tomarse todo el tiempo que quisieran»[^5]. Tres consecuencias de diseño directas:

1. **El calendario presiona sin castigar.** Las estaciones avanzan pase lo que pase, pero
   perderse una cosecha cuesta ingresos, nunca la partida.
2. **Las relaciones son el sistema de progresión social**, en paralelo al económico: «interactuar
   con la gente del pueblo y darle regalos construye relaciones con el tiempo»[^5].
3. **El ritmo tranquilo es una decisión, no un límite técnico.** No compenses la falta de
   amenaza con más ruido de sistemas: un día tranquilo con pocas tareas bien pulidas es el
   objetivo, no un nivel a medio terminar.

### 5.2 · Sistema crítico 1 — calendario y estaciones, sobre el reloj que ya existe

El reloj día/noche **ya está resuelto** en
[04 · 09 §5.5](./09%20-%20Survival%20y%20crafting.md#55-ciclo-díanoche) (el valor
`objTimeOfDay.tiempo`, 0..1) y su rampa de color en
[04 · 24 §6](./24%20-%20Iluminación%202D.md#6--ciclo-díanoche-con-rampa-de-color). Lo que falta
es la capa de **calendario** encima: contar días y agrupar en estaciones, algo que un survival
de supervivencia pura no necesita pero un cozy sí, porque las estaciones son su sistema de
contenido (cultivos, festivales, ropa).

```gml
/// obj_calendario · Create — una capa de días/estaciones sobre el reloj de 04 · 09 §5.5.
/// NO sustituye a objTimeOfDay: lo observa.
dia_actual         = 1;
estacion_indice    = 0;                 // 0 primavera · 1 verano · 2 otoño · 3 invierno
dias_por_estacion  = 28;                // el mismo reparto que usa Stardew Valley
tiempo_anterior    = objTimeOfDay.tiempo;

global.nombres_estacion = ["Primavera", "Verano", "Otoño", "Invierno"];

/// obj_calendario · Step — se dispara UNA vez por vuelta completa del reloj, no cada frame
if (objTimeOfDay.tiempo < tiempo_anterior) {          // el reloj dio la vuelta: 0.98 → 0.01
    dia_actual += 1;
    if (dia_actual > dias_por_estacion) {
        dia_actual      = 1;
        estacion_indice = (estacion_indice + 1) mod 4;
        senal_emitir("cambio_estacion", { estacion: estacion_indice });
    }
    senal_emitir("nuevo_dia", { dia: dia_actual, estacion: estacion_indice });
}
tiempo_anterior = objTimeOfDay.tiempo;
```

> 💡 **`nuevo_dia` es el reloj de todo lo demás en este género.** Los cultivos de §5.3 y el
> límite de regalos de §5.4 se enganchan a esta única señal — reutiliza el patrón de
> [04 · 16](./16%20-%20Señales%20y%20desacoplamiento.md), no un `alarm` por sistema.

### 5.3 · Sistema crítico 2 — cultivos por celda, como datos

Un survival tiene nodos de recurso como **instancias** (`04 · 09 §5.2`); un cultivo de granja es
mejor como **dato por celda**, porque el huerto puede tener cientos de parcelas y cada una solo
necesita cuatro campos, no un objeto completo con su propio Step. Es el mismo criterio de «datos
frente a instancias» de `13 · 06`, aplicado aquí por primera vez a un tablero de cultivo.

```gml
/// scr_cultivos — el huerto como array plano, índice = fila * ancho + col (04 · 35 §5.9 usa el
/// mismo patrón para su rejilla táctica).

enum EstadoCultivo { VACIA, PLANTADA, CRECIENDO, MADURA, MARCHITA }

global.huerto_ancho = 12;
global.huerto_alto  = 8;
global.huerto       = array_create(global.huerto_ancho * global.huerto_alto);

// ⚠️ NO uses array_create(n, {...}) con un struct de relleno: todas las celdas compartirían
// la MISMA referencia. Cada celda necesita su propio struct, de ahí el bucle.
for (var _i = 0; _i < array_length(global.huerto); _i++) {
    global.huerto[_i] = { estado: EstadoCultivo.VACIA, tipo: -1, edad_dias: 0, regada: false };
}

#macro DIAS_VENTANA_COSECHA 3   // días que aguanta MADURA sin cosechar antes de marchitarse

global.tipos_semilla = [
    { id: "nabo",   nombre: "Nabo",   dias_por_etapa: 1, etapas: 4, valor_venta: 60 },
    { id: "patata", nombre: "Patata", dias_por_etapa: 2, etapas: 3, valor_venta: 80 },
];

/// @func huerto_indice(_col, _fila)
function huerto_indice(_col, _fila) { return _fila * global.huerto_ancho + _col; }

/// @func cultivo_plantar(_col, _fila, _tipo_semilla)
/// @return {Bool}
function cultivo_plantar(_col, _fila, _tipo_semilla)
{
    var _i = huerto_indice(_col, _fila);
    if (global.huerto[_i].estado != EstadoCultivo.VACIA) { return false; }
    global.huerto[_i] = { estado: EstadoCultivo.PLANTADA, tipo: _tipo_semilla, edad_dias: 0, regada: false };
    return true;
}

/// @func cultivo_regar(_col, _fila)
function cultivo_regar(_col, _fila) { global.huerto[huerto_indice(_col, _fila)].regada = true; }

/// @func cultivo_avanzar_dia(_i)
/// @desc Se llama UNA vez por celda, desde el oyente de "nuevo_dia" de abajo. Sin agua no hay
///       fallo brusco: la planta se marchita, no desaparece — el jugador puede arrancarla y
///       volver a intentarlo, coherente con la regla de «ausencia de fracaso duro» de §5.1.
///       Tampoco lo hay al madurar y no cosechar a tiempo: hay DIAS_VENTANA_COSECHA de margen
///       antes de que MADURA pase a MARCHITA (informe de auditoría r3-2026-09-06, tema 45: la
///       versión anterior de esta función se quedaba en MADURA para siempre, sin ventana ni
///       forma de perder la cosecha por descuido).
function cultivo_avanzar_dia(_i)
{
    var _c = global.huerto[_i];
    if (_c.estado == EstadoCultivo.VACIA || _c.estado == EstadoCultivo.MARCHITA) { return; }

    if (!_c.regada) { _c.estado = EstadoCultivo.MARCHITA; return; }

    _c.edad_dias += 1;
    _c.regada     = false;                      // hay que regar cada día, otra vez
    var _semilla       = global.tipos_semilla[_c.tipo];
    var _etapa_actual  = min(floor(_c.edad_dias / _semilla.dias_por_etapa), _semilla.etapas - 1);
    _c.estado = (_etapa_actual >= _semilla.etapas - 1) ? EstadoCultivo.MADURA : EstadoCultivo.CRECIENDO;

    if (_c.estado == EstadoCultivo.MADURA) {
        var _dias_maduro = _c.edad_dias - _semilla.dias_por_etapa * (_semilla.etapas - 1);
        if (_dias_maduro > DIAS_VENTANA_COSECHA) { _c.estado = EstadoCultivo.MARCHITA; }
    }
}

/// obj_calendario · Create — recorre TODO el huerto una vez por día, no una vez por frame
senal_escuchar("nuevo_dia", function(_d) {
    for (var _i = 0; _i < array_length(global.huerto); _i++) { cultivo_avanzar_dia(_i); }
});

/// @func cultivo_cosechar(_col, _fila)
/// @desc Cierra el bucle que cultivo_avanzar_dia() deja abierto (informe de auditoría
///       r3-2026-09-06, tema 45: «04 · 45 §5.3 solo llega a EstadoCultivo.MADURA», sin ninguna
///       función que retire la planta ni entregue nada). Entrega la cosecha al inventario del
///       jugador — reutiliza `Inventory.add()` de 04 · 04 §5.2 / 04 · 09 §4.2, que ya vive en
///       `global.inventory` en cualquier receta que haya cargado items.json — y deja la celda
///       vacía para volver a plantar.
/// @return {Bool} Si se cosechó algo.
function cultivo_cosechar(_col, _fila)
{
    var _i = huerto_indice(_col, _fila);
    var _c = global.huerto[_i];
    if (_c.estado != EstadoCultivo.MADURA) { return false; }

    var _semilla = global.tipos_semilla[_c.tipo];

    // ⚠️ Inventory.add() (04 · 04 §5.2) llama a item_get_def() y falla en silencio (con un
    // show_debug_message) si el id no está en items.json (04 · 04 §5.3): el `id` de cada
    // entrada de tipos_semilla DEBE tener su ficha ahí, con el mismo id, antes de cosechar nada.
    global.inventory.add(_semilla.id, 1);

    global.huerto[_i] = { estado: EstadoCultivo.VACIA, tipo: -1, edad_dias: 0, regada: false };
    return true;
}

/// @func cultivo_arrancar(_col, _fila)
/// @desc Limpia una celda MARCHITA (o cualquier otra) sin entregar nada, para volver a
///       plantar. Sin esto, una celda que se marchitó se queda ocupada para siempre.
function cultivo_arrancar(_col, _fila)
{
    global.huerto[huerto_indice(_col, _fila)] = { estado: EstadoCultivo.VACIA, tipo: -1, edad_dias: 0, regada: false };
}
```

### 5.4 · Sistema crítico 3 — relaciones con NPC: regalos y corazones

La afinidad **ya existe** como sistema de datos: `VNState.afinidad_get()` y
`afinidad_sumar()` en
[04 · 10 §5.2](./10%20-%20Visual%20Novel%20y%20narrativa.md#52-estado-de-la-historia). Lo que
un cozy añade encima es la convención que lo distingue de una visual novel: **un regalo al día
por personaje**, y los corazones como la unidad que el jugador realmente lee.

```gml
/// scr_relaciones_granja — envuelve VNState.afinidad_sumar (04 · 10 §5.2); no la reescribe.
global.regalos_hoy = {};                        // { ana: true } — se vacía cada nuevo día

senal_escuchar("nuevo_dia", function(_d) { global.regalos_hoy = {}; });

/// @func regalo_dar(_vn_state, _personaje, _item, _favoritos)
/// @desc Un solo regalo cuenta por día; el resto se pierde en un "gracias, pero ya tengo
///       suficiente por hoy" — la regla que evita comprar la relación de golpe en una tarde.
/// @param {Struct}        _vn_state   Instancia de VNState (04 · 10 §5.2).
/// @param {String}        _personaje
/// @param {String}        _item
/// @param {Array<String>} _favoritos  Ítems favoritos de ese personaje.
/// @return {Bool} Si el regalo contó.
function regalo_dar(_vn_state, _personaje, _item, _favoritos)
{
    if (variable_struct_exists(global.regalos_hoy, _personaje)) { return false; }
    global.regalos_hoy[$ _personaje] = true;

    var _es_favorito = array_contains(_favoritos, _item);
    _vn_state.afinidad_sumar(_personaje, _es_favorito ? 8 : 2);
    return true;
}

/// @func corazones_de(_vn_state, _personaje, _afinidad_por_corazon = 25)
/// @desc Traduce la afinidad numérica de 04 · 10 en "corazones" (0..10), la unidad que un
///       jugador de cozy espera ver, en vez de un número de afinidad en bruto.
function corazones_de(_vn_state, _personaje, _afinidad_por_corazon = 25)
{
    return min(10, floor(_vn_state.afinidad_get(_personaje) / _afinidad_por_corazon));
}
```

### 5.5 · A qué apoyarte

- Reloj y rampa de color día/noche: [04 · 09 §5.5](./09%20-%20Survival%20y%20crafting.md#55-ciclo-díanoche)
  y [04 · 24 §6](./24%20-%20Iluminación%202D.md#6--ciclo-díanoche-con-rampa-de-color).
- Recolección, inventario por pila y recetas de crafteo (la base de la economía de temporada):
  [04 · 09 §4.1-§4.3](./09%20-%20Survival%20y%20crafting.md#4-sistemas-clave).
- Diálogo, *barks* y el gestor de misiones para las líneas de los NPC:
  [13 · 12 §3.5 y §6.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md#65-un-gestor-de-misiones-mínimo-con-estado-fallada).
- Afinidad y guardado del estado de la historia: [04 · 10 §5.2](./10%20-%20Visual%20Novel%20y%20narrativa.md#52-estado-de-la-historia).
- Señales para desacoplar calendario, cultivos y relaciones entre sí: [04 · 16](./16%20-%20Señales%20y%20desacoplamiento.md).
- Ganado, el otro medio del bucle de granja que faltaba: §5.6, justo debajo.

### 5.6 · Ganado

El informe de auditoría de esta biblioteca (r3-2026-09-06, tema 46) lo marca como el hueco más
caro del género después de la cosecha: **cero resultados de animales de granja** en toda la
biblioteca. *Stardew Valley* reparte su economía casi a partes iguales entre cultivos y ganado
(huevos, leche, lana), así que un cozy sin animales solo tiene la mitad del bucle de §5.1.

**Qué reutiliza, y qué NO.** `Needs()` de
[04 · 09 §5.0](./09%20-%20Survival%20y%20crafting.md#50-necesidades) da el struct correcto —cinco
campos 0..100, `consumir()`, `serialize()`— pero está **calibrado por fotograma**:
`tasa_hambre = 0.030` vacía el 0..100 en unos 3 300 frames (~55 s a 60 fps), y
`daño_por_frame()` devuelve daño **por fotograma**, no por día. Llamar a
`needs.update()`/`needs.daño_por_frame()` una sola vez al día —la cadencia de este documento,
la señal `nuevo_dia` de §5.2— sería 1 200 veces más lento de lo que sus propios nombres
prometen: el mismo tipo de error de unidades que el informe de auditoría destapó en
`skeleton_animation_get_position()` (devuelve 0..1, no segundos) en otro documento de esta
biblioteca. Por eso `Animal()` reutiliza el **struct** de `Needs` —los campos, `consumir()`,
`serialize()`/`deserialize()`— pero escribe su **propia** degradación diaria en
`avanzar_dia()`, en vez de llamar a los métodos calibrados por frame.

```gml
/// scr_ganado — struct Animal(_tipo, _pos_x, _pos_y) sobre Needs() (04 · 09 §5.0, solo como
/// contenedor de datos — ver el aviso de arriba) y la señal "nuevo_dia" (§5.2).
/// Verificado: random(n), max, min, array_delete, array_push, ya en uso en esta biblioteca.
/// pos_x/pos_y en vez de x/y aunque esto sea un struct y no una instancia: la regla de
/// convenciones de esta biblioteca (05 · 04) evita x/y como variable propia sin excepción.

global.tipos_animal = [
    { id: "gallina", nombre: "Gallina", producto: "huevo", dias_produccion: 1, umbral_feliz: 60 },
    { id: "vaca",    nombre: "Vaca",    producto: "leche", dias_produccion: 2, umbral_feliz: 55 },
];

/// @func Animal(_tipo, _pos_x, _pos_y)
/// @param {Real} _tipo  Índice en global.tipos_animal.
function Animal(_tipo, _pos_x, _pos_y) constructor
{
    tipo   = _tipo;
    pos_x  = _pos_x;
    pos_y  = _pos_y;
    needs  = new Needs();      // reutiliza el struct de 04 · 09 §5.0 — NO se llama a needs.update()

    dias_desde_produccion = 0;
    dias_sin_comer        = 0;
    edad_dias             = 0;

    /// @desc Alimenta al animal HOY. Needs.consumir() (04 · 09 §5.0) es una suma con
    ///       clamp a 100: no depende de la cadencia de llamada, se reutiliza tal cual.
    alimentar = function()
    {
        needs.consumir({ hambre: 40 });
        dias_sin_comer = 0;
    };

    /// @desc Se llama UNA vez por día, desde el oyente de "nuevo_dia" — mismo patrón que
    ///       cultivo_avanzar_dia() de §5.3.
    /// @return {Struct|Undefined} { producto, cantidad } si produjo hoy; { producto: "murio" }
    ///         si murió de hambre; undefined si no pasó nada especial.
    avanzar_dia = function()
    {
        edad_dias += 1;

        // Degradación DIARIA propia — NO needs.update(), calibrado por frame (ver aviso arriba).
        needs.hambre = max(0, needs.hambre - 35);
        dias_sin_comer += 1;

        if (dias_sin_comer >= 4) { return { producto: "murio", cantidad: 0 }; }

        var _def   = global.tipos_animal[tipo];
        var _feliz = (needs.hambre >= _def.umbral_feliz);

        if (_feliz)
        {
            dias_desde_produccion += 1;
            if (dias_desde_produccion >= _def.dias_produccion)
            {
                dias_desde_produccion = 0;
                return { producto: _def.producto, cantidad: 1 };
            }
        }
        return undefined;
    };

    /// @desc Probabilidad de cría simple: solo si está bien alimentado, una tirada diaria baja.
    /// @return {Bool}
    intentar_reproducir = function(_prob_diaria = 0.05)
    {
        return (needs.hambre >= global.tipos_animal[tipo].umbral_feliz) && (random(1) < _prob_diaria);
    };

    serialize = function()
    {
        return {
            tipo: tipo, pos_x: pos_x, pos_y: pos_y, needs: needs.serialize(),
            dias_desde_produccion: dias_desde_produccion,
            dias_sin_comer: dias_sin_comer, edad_dias: edad_dias
        };
    };

    static deserialize = function(_d)
    {
        var _a = new Animal(_d.tipo, _d.pos_x, _d.pos_y);
        _a.needs                   = Needs.deserialize(_d.needs);
        _a.dias_desde_produccion   = _d.dias_desde_produccion;
        _a.dias_sin_comer          = _d.dias_sin_comer;
        _a.edad_dias               = _d.edad_dias;
        return _a;
    };
}

global.animales = [];   // array de Animal — el corral entero, como datos (mismo criterio que §5.3)

/// @func animal_registrar(_tipo, _pos_x, _pos_y)
function animal_registrar(_tipo, _pos_x, _pos_y)
{
    array_push(global.animales, new Animal(_tipo, _pos_x, _pos_y));
}

/// obj_calendario · Create — recorre TODO el corral una vez por día, junto al huerto de §5.3
senal_escuchar("nuevo_dia", function(_d) {
    for (var _i = array_length(global.animales) - 1; _i >= 0; _i--)
    {
        var _animal   = global.animales[_i];
        var _resultado = _animal.avanzar_dia();

        if (_resultado == undefined) { continue; }

        if (_resultado.producto == "murio")
        {
            // ⚠️ Sin fracaso duro (§5.1): perder un animal por descuido escuece, pero el
            // jugador sigue jugando. Notifícalo con una señal propia en vez de un array
            // aparte de "eventos del día": reutiliza el mismo bus de 04 · 16.
            senal_emitir("animal_murio", { tipo: _animal.tipo, pos_x: _animal.pos_x, pos_y: _animal.pos_y });
            array_delete(global.animales, _i, 1);
            continue;
        }

        // Producto al inventario del jugador — mismo Inventory.add() que cultivo_cosechar()
        // (§5.3) y con el mismo requisito: el id del producto debe existir en items.json
        // (04 · 04 §5.3).
        global.inventory.add(_resultado.producto, _resultado.cantidad);

        if (_animal.intentar_reproducir())
        {
            array_push(global.animales, new Animal(_animal.tipo, _animal.pos_x + 16, _animal.pos_y));
        }
    }
});
```

> 💡 **Dos motivos distintos para dos decisiones distintas.** El `for` recorre `global.animales`
> **hacia atrás** porque `array_delete()` desplaza los elementos posteriores un hueco hacia
> abajo: en un bucle hacia delante, borrar el índice `_i` hace que el elemento que antes estaba
> en `_i + 1` pase a `_i` y el `for` lo salte sin procesarlo. Que la cría nazca al final del array
> y **no** se procese el mismo día es un motivo aparte: `array_length(global.animales) - 1` se
> evalúa **una sola vez**, al entrar en el `for` (igual que en C), así que cualquier animal que
> `array_push()` añada más allá de esa longitud original queda fuera del rango del bucle en
> curso, sin importar si se recorriera hacia delante o hacia atrás.

---

## 6 · Idle / incremental / clicker

### 6.1 · La convención

Un idle se juega en dos modos que no se parecen: **activo** (el jugador hace clic, decide
compras) y **pasivo** (el juego produce solo, incluso con la ventana cerrada). Romper el segundo
modo — que el progreso se detenga al cerrar el juego — rompe el género entero, porque la promesa
implícita de un idle es «vuelve más tarde y habrá merecido la pena». El artículo de referencia
del género señala que *AdVenture Capitalist* fue pionero al implementar «un sistema de ganancias
offline que rastrea el progreso del jugador cuando el juego no está abierto»[^6] — hoy es una
expectativa mínima, no una característica diferencial.

### 6.2 · Sistema crítico 1 — la curva de coste exponencial (ya existe)

**No hay nada nuevo que escribir aquí.** La curva que define al género —cada mejora cuesta un
poco más que la anterior, en progresión geométrica— ya tiene función propia:
`progresion_exponencial(_nivel, _base, _razon)` en
[13 · 13 §8.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md#81--las-cinco-formas-y-qué-comunica-cada-una),
y el método para elegir la razón (el parámetro más peligroso de todos, según la propia tabla de
esa sección) en
[13 · 01 §4.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#44--balance-por-fórmulas-con-números)
(«curva de coste geométrica»). El uso en un idle es literal:

```gml
/// El coste de la mejora N+1, con razón 1,15 — el rango bajo que 13 · 13 §8.2 recomienda
/// para "la decisión de ¿ahorro o compro ya?", el pulso central de cualquier idle.
var _coste_siguiente = progresion_exponencial(edificios_comprados + 1, COSTE_BASE, 1.15);
```

### 6.3 · Sistema crítico 2 — números grandes, y su notación

`13 · 13 §11.4` ya explica el límite (los reales pierden precisión exacta por encima de `2^53`,
`int64` cubre hasta `9,2·10¹⁸`) y **nombra** la solución para lo que va más allá — «guardar
mantisa y exponente por separado y mostrar “1,4 aa”»[^7] — pero no la construye. Eso es lo que
falta:

```gml
/// scr_numeros_grandes — la representación que 13 · 13 §11.4 solo nombra; aquí se construye.

global.sufijos_grandes = ["", "K", "M", "B", "T"];    // hasta el billón corto (10^12)

/// @func numero_abreviado(_valor)
/// @desc 1500 → "1.5K" · 2340000 → "2.3M". Por encima de T sigue con pares de letras
///       (aa, ab, ac... az, ba...) — el mismo patrón que usan los idle comerciales para
///       cifras que ya no caben en un nombre corto.
/// @param {Real} _valor
/// @return {String}
function numero_abreviado(_valor)
{
    if (_valor < 1000) { return string(floor(_valor)); }

    var _exponente = floor(ln(_valor) / ln(1000));     // ¿cuántos grupos de 1000?
    var _mantisa   = _valor / power(1000, _exponente);
    var _sufijo;

    if (_exponente < array_length(global.sufijos_grandes)) {
        _sufijo = global.sufijos_grandes[_exponente];
    } else {
        var _n      = _exponente - array_length(global.sufijos_grandes);
        _sufijo = chr(97 + (_n div 26)) + chr(97 + (_n mod 26));   // aa, ab, ac...
    }

    return string_format(_mantisa, 1, 2) + _sufijo;
}
```

> ⚠️ **Esto es solo la representación en pantalla.** Si tu producción total supera `int64`
> (`9,2·10¹⁸`) de verdad — un idle maduro con horas de partida lo consigue —, la variable que
> acumulas también debe ser mantisa+exponente, no un `real` ni un `int64` que se desborda en
> silencio. `13 · 13 §11.4` explica el porqué; este documento no repite esa parte.

### 6.4 · Sistema crítico 3 — el progreso offline, y el prestigio

El guardado en sí **no cambia**: usa `guardar_partida()`/`cargar_partida()` de
[01 · 14 §9](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#9-sistema-de-guardado-completo-recomendado)
tal cual. Un idle solo añade **un campo** al struct de datos que ya construye esa función
(`guardado_en: date_current_datetime()`), y una función nueva que convierte «cuánto tiempo pasó»
en recursos — la pieza que
[08 · 18](../08%20-%20Referencia%20GML%20completa/18%20-%20Fecha%20y%20hora.md) no da: su receta
de «cuánto tiempo lleva el jugador sin entrar» **mide** el tiempo, no lo convierte en nada.

```gml
/// scr_progreso_offline — la conversión que falta encima de 01 · 14 §9 y 08 · 18.

/// @func progreso_offline_aplicar(_datos, _produccion_por_segundo, _tope_horas)
/// @desc Se llama justo después de cargar_partida() (01 · 14 §9), antes de aplicar el resto
///       de _datos. Usa date_second_span (08 · 18) para medir, y aquí se convierte en recursos.
/// @param {Struct} _datos                  Lo que devolvió cargar_partida().
/// @param {Real}   _produccion_por_segundo Suma de todas las fuentes activas (13 · 01 §4.1).
/// @param {Real}   _tope_horas             Máximo de horas que se pagan de una sentada.
/// @return {Struct} { ganado, segundos_cobrados, se_topo }
function progreso_offline_aplicar(_datos, _produccion_por_segundo, _tope_horas)
{
    if (!variable_struct_exists(_datos, "guardado_en")) {
        return { ganado: 0, segundos_cobrados: 0, se_topo: false };   // guardado sin el campo
    }

    var _ahora          = date_current_datetime();
    var _segundos_fuera = date_second_span(_datos.guardado_en, _ahora);
    var _tope_segundos  = _tope_horas * 3600;
    var _cobrados       = clamp(_segundos_fuera, 0, _tope_segundos);

    return {
        ganado            : _produccion_por_segundo * _cobrados,
        segundos_cobrados : _cobrados,
        se_topo           : (_segundos_fuera > _tope_segundos)
    };
}
```

```gml
/// obj_control · Create — al arrancar el juego
var _datos = cargar_partida();                                // 01 · 14 §9, sin tocar
if (!is_undefined(_datos))
{
    global.recursos = _datos.globales.recursos;

    var _r = progreso_offline_aplicar(_datos, PRODUCCION_POR_SEGUNDO, 8);   // tope: 8 horas
    global.recursos += _r.ganado;

    if (_r.segundos_cobrados > 60) {                            // no molestes por 40 s de alt-tab
        var _h = floor(_r.segundos_cobrados / 3600);
        var _m = floor((_r.segundos_cobrados mod 3600) / 60);
        global.mensaje_offline = $"Mientras estabas fuera ({_h}h {_m}m): +{numero_abreviado(_r.ganado)}"
                                + (_r.se_topo ? "\n(tope de producción alcanzado)" : "");
    }
}
```

> 🔺 **El tope offline (`_tope_horas`) no es un detalle técnico, es una decisión de diseño.**
> Sin tope, dejar el juego cerrado una semana es estrictamente mejor que jugar; con un tope
> generoso (8-24 h es habitual en el género) el progreso offline sigue premiando volver, sin
> volverse el único bucle que importa.

**Con rendimientos decrecientes en vez de tope duro** (informe de auditoría r3-2026-09-06, tema
98). `progreso_offline_aplicar()` de arriba paga en **lineal** hasta `_tope_horas` y **cero** a
partir de ahí: un jugador que vuelve a las 8h01m con `_tope_horas = 8` pierde justo el minuto 481,
mientras que uno que vuelve a las 7h59m no pierde nada — es un acantilado, no una curva. La
alternativa reutiliza `progresion_logaritmica(_nivel, _base)` de
[13 · 13 §8.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md#81--las-cinco-formas-y-qué-comunica-cada-una)
**tal cual, sin reescribir su fórmula** — solo se compone distinto: las horas fuera hacen de
`_nivel`, para que cada hora adicional siga sumando algo pero cada vez menos, sin ningún corte.

```gml
/// scr_progreso_offline (continuación) — variante SIN tope duro sobre progreso_offline_aplicar()
/// de arriba. No la sustituye: elige una de las dos según qué prefieras para tu juego.

/// @func progreso_offline_aplicar_decreciente(_datos, _produccion_por_segundo, _escala_horas)
/// @desc Las primeras horas pagan casi lo mismo que la versión lineal (para _horas_fuera
///       pequeño frente a _escala_horas, ln(1+x) ≈ x); pasada _escala_horas, cada hora extra
///       rinde cada vez menos, sin un tope que la corte de golpe.
/// @param {Struct} _datos                  Lo que devolvió cargar_partida() (01 · 14 §9).
/// @param {Real}   _produccion_por_segundo Suma de fuentes activas (13 · 01 §4.1).
/// @param {Real}   _escala_horas           Horas a las que la curva empieza a notarse (4-8 es habitual).
/// @return {Struct} { ganado, horas_fuera }
function progreso_offline_aplicar_decreciente(_datos, _produccion_por_segundo, _escala_horas)
{
    if (!variable_struct_exists(_datos, "guardado_en")) {
        return { ganado: 0, horas_fuera: 0 };
    }

    var _horas_fuera = date_second_span(_datos.guardado_en, date_current_datetime()) / 3600;

    // progresion_logaritmica(_nivel, _base) = _base * ln(_nivel + 1) — 13 · 13 §8.1, sin tocar
    // su cuerpo. Aquí _nivel = horas_fuera / _escala_horas y se reescala el resultado × _escala_horas
    // para volver a "horas equivalentes", en vez del "valor bruto del nivel 1" con el que se
    // pensó originalmente para curvas de XP.
    var _horas_efectivas = progresion_logaritmica(_horas_fuera / _escala_horas, 1) * _escala_horas;

    return {
        ganado      : _produccion_por_segundo * _horas_efectivas * 3600,
        horas_fuera : _horas_fuera
    };
}
```

> 💡 **Por qué no hace falta `clamp()`.** La curva no necesita tope porque ya se aplana sola: la
> derivada de `escala·ln(h/escala + 1)` respecto a `h` es `escala/(h + escala)`, que vale 1 en
> `h = 0` (paga igual que la lineal al principio) y tiende a 0 según `h` crece — cada hora extra
> vale menos que la anterior sin que ningún `if` tenga que decirlo.

El **prestigio** —reiniciar el progreso a cambio de una moneda permanente que acelera la
siguiente vuelta— es el mismo patrón de monedas múltiples que ya construyó
[13 · 16 §2.4-§2.6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#26-el-patrón-de-monedas-múltiples-partida-frente-a-meta)
para roguelites (`RunState.oro` que se pierde frente a `MetaProgress.oro_total` que persiste, y
`moneda_transferir_a_meta()` para el paso de una a otra). Un idle no necesita un sistema nuevo:
necesita llamar a esa misma función en el momento de prestigiar, con la producción acumulada de
la vuelta como `_campo_run` y la moneda de prestigio como `_campo_meta`.

### 6.5 · A qué apoyarte

- Curva de coste y balance por fórmulas: [13 · 13 §8](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md#8--curvas-de-crecimiento-para-diseño)
  y [13 · 01 §4.4-§4.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#44--balance-por-fórmulas-con-números).
- Enteros grandes e `int64`: [13 · 13 §11.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md#114--enteros-grandes-e-int64).
- Guardado versionado y patrón JSON: [01 · 14 §9](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#9-sistema-de-guardado-completo-recomendado);
  recetas de fecha y hora: [08 · 18](../08%20-%20Referencia%20GML%20completa/18%20-%20Fecha%20y%20hora.md).
- Prestigio y monedas múltiples: [13 · 16 §2.4-§2.6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#26-el-patrón-de-monedas-múltiples-partida-frente-a-meta).
- Panel de balance en caliente para ajustar `_razon` sin recompilar: [13 · 01 §9.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#94--balance-en-caliente-con-el-debug-overlay).

---

## 7 · Checklist transversal

- [ ] **Sigilo**: el jugador nunca es descubierto sin haber visto venir el motivo (cono +
      línea de visión + medidor visibles o inferibles).
- [ ] **Sigilo**: `COMBATE` (o el fallo duro equivalente) tiene una vía de recuperación
      razonable — decaimiento del medidor o un punto de control cercano, nunca las dos cosas
      ausentes a la vez.
- [ ] **Horror**: ningún recurso crítico tiene una fuente 100 % predecible; el jugador nunca
      sabe con certeza cuánto le queda garantizado.
- [ ] **Horror**: el enemigo principal no tiene componente de vida/daño conectado — la colisión
      dispara una secuencia, no una pelea.
- [ ] **Táctica**: todo ataque muestra su probabilidad ANTES de confirmarse, y esa cifra es
      honesta (o el ajuste de percepción de §4.3 está documentado como tal).
- [ ] **Granja**: perder una cosecha, un día o un regalo cuesta ingresos o tiempo, nunca la
      partida.
- [ ] **Granja**: los cultivos son datos por celda, no instancias — un huerto de 200 parcelas no
      debería generar 200 Steps.
- [ ] **Idle**: el juego calcula progreso offline al cargar, con un tope explícito.
- [ ] **Idle**: los números que superan la pantalla usan `numero_abreviado()` (o equivalente)
      antes de desbordar el HUD o perder precisión en silencio.

## 8 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| Un guardia que detecta al instante, sin cono ni medidor | Se usa `distance <= N` en vez de `en_cono_vision()` + `hay_vision_libre()` | Combina siempre ángulo (§2.2) y línea de visión; nunca solo distancia |
| El medidor de detección sube y baja a saltos | Se actualiza por evento en vez de por frame con `delta_time` | El acumulador de §2.4 es continuo; los saltos rompen la legibilidad que pide el género |
| Un monstruo de terror con barra de vida | Se reutiliza el esqueleto de un enemigo normal sin quitarle el daño | Nunca conectes `dano_resolver()` (`04 · 32`) a la instancia del monstruo intocable |
| Música de tensión que sube y baja de golpe | `audio_sound_gain` con tiempo 0 en vez de 150-250 ms | Sigue siempre la recomendación de suavizado de `04 · 26` y §3.4 |
| Mostrar un % de acierto que no coincide con la tirada real | Se aplica una piedad agresiva que cambia la media, no solo la varianza | El bono de §4.3 tiene tope (20 puntos); si necesitas más, sube el % mostrado, no el ajuste oculto |
| Cultivos como instancias con su propio Step | Copiar el patrón de nodo de recurso de `04 · 09 §5.2` sin adaptarlo | Un huerto grande son datos (§5.3); las instancias son para lo que el jugador toca directamente |
| `array_create(n, {...})` para inicializar una rejilla de structs | Parece más corto que un bucle | Todas las celdas comparten la MISMA referencia de struct; usa el bucle de §5.3 |
| Progreso offline sin tope | Se copia solo la fórmula de producción, sin el `clamp` | `progreso_offline_aplicar()` (§6.4) siempre acota a `_tope_horas` |
| Guardar la producción acumulada como `real` sin vigilar el límite | Los números crecen más rápido de lo previsto en playtesting | Vigila `int64` (`13 · 13 §11.4`) y planea la migración a mantisa+exponente con tiempo |

## Ver también

- [04 · 31 — IA de decisión](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md) — percepción, blackboard y el enemigo completo de los que parten §2 y §3.
- [04 · 35 — Combate por turnos y táctico en rejilla](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md) — el documento que cubre casi entero el §4.
- [04 · 09 — Survival y crafting](./09%20-%20Survival%20y%20crafting.md) — necesidades, chunking y el reloj día/noche del que parte §5.
- [04 · 24 — Iluminación 2D](./24%20-%20Iluminación%202D.md) — la rampa de color día/noche que consume el calendario de §5.2.
- [04 · 10 — Visual Novel y narrativa](./10%20-%20Visual%20Novel%20y%20narrativa.md) — `VNState` y afinidad, la base de las relaciones de §5.4.
- [04 · 16 — Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — el patrón de eventos que conecta calendario, cultivos, relaciones y alerta de grupo.
- [04 · 23 — IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) — seek/flee/wander que usan §3.3 y la persecución de §2.
- [04 · 26 — Música adaptativa por capas](./26%20-%20Música%20adaptativa%20por%20capas.md) — el crossfade del que §3.4 deriva la variante continua.
- [04 · 34 — Combate a distancia](./34%20-%20Combate%20a%20distancia%20-%20armas,%20munición%20y%20balística.md) — `WeaponAmmoState`, sobre el que se engancha el encasquille de §3.2.
- [04 · 42 — Audio reactivo al mundo](./42%20-%20Audio%20reactivo%20al%20mundo%20-%20materiales,%20zonas%20y%20estados%20de%20mezcla.md) — el sistema de importancia que sostiene el §3.4.
- [13 · 01 — Diseño de juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) — vocabulario de economía (§2.1, §3.2), curvas de dificultad (§3.1, §3.4) y coste geométrico (§4.2, §6.2).
- [13 · 09 — Diseño de sonido y mezcla](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) — la base del §3.4.
- [13 · 12 — Diseño narrativo y diálogos](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md) — *barks* y gestor de misiones que completan el §5.4.
- [13 · 13 — Matemáticas aplicadas al juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) — cono de visión (§2.2), probabilidad con piedad (§4.3) y curvas de crecimiento (§6.2-§6.3).
- [13 · 16 — Progresión](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md) — monedas múltiples y prestigio del §6.4.
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — el sistema de guardado sobre el que se apoya el §6.4.
- [08 · 18 — Fecha y hora](../08%20-%20Referencia%20GML%20completa/18%20-%20Fecha%20y%20hora.md) — `date_current_datetime`/`date_second_span`, la base del §6.4.

## Fuentes

**Manual oficial y runtime** — todos los símbolos de GML de este documento comprobados con
`python3 _indice/buscar.py` contra el runtime `2026.0.0.23` (espejo local en
`09 - Manual oficial/`): `clamp`, `lerp`, `merge_colour`, `draw_healthbar`, `date_current_datetime`,
`date_second_span`, `array_create`, `array_contains`, `array_get_index`, `chr`, `ln`, `power`,
`string_format`, `variable_struct_exists`, `random`, `point_distance`, `audio_sound_gain`,
`audio_play_sound`, `delta_time`. `senal_emitir`/`senal_escuchar` (`04 · 16`), `en_cono_vision`
(`13 · 13 §2.4`), `hay_vision_libre`/`ia_ve_al_jugador` (`04 · 31 §5`) y
`VNState.afinidad_get`/`afinidad_sumar` (`04 · 10 §5.2`) son funciones **propias de la
biblioteca**, no del runtime: se enlazan a su definición en vez de reescribirlas.

**Diseño, consultadas el 2026-09-06:**

[^1]: *Mark of the Ninja*, Wikipedia — «enemies which would be invisible to the character are
    also invisible to the player»; los ruidos como círculos que se expanden; los iconos de
    interrogación (sospecha) y exclamación (alerta) sobre la cabeza de los guardias —
    <https://en.wikipedia.org/wiki/Mark_of_the_Ninja>

[^2]: *Tom Clancy's Splinter Cell*, Wikipedia — «the game displays a "light meter" that reflects
    how visible the player character is to enemies», activo incluso con visión nocturna o
    térmica —
    <https://en.wikipedia.org/wiki/Tom_Clancy%27s_Splinter_Cell_(video_game)>

[^3]: *Alien: Isolation*, Wikipedia — el sistema de comportamiento del Xenomorfo se desbloquea
    según interactúa con el jugador, «creating the illusion that the Alien learns from each
    interaction and appropriately adjusts its hunting strategy»; cita del diseñador de
    *gameplay* Gary Napper: «if the Alien was scripted, you'd see the same behaviour. That makes
    the Alien become predictable, and a lot less scary» —
    <https://en.wikipedia.org/wiki/Alien:_Isolation>

[^4]: *XCOM: Enemy Unknown*, Wikipedia — «the game's user interface informs the player of the
    possibility of landing a successful shot and the amount of damage they will deal»; la propia
    página enlaza la controversia conocida como «the secret dice rolls of XCOM: Enemy Within.
    How Firaxis fudge the numbers» sobre la percepción de justicia de esas probabilidades —
    <https://en.wikipedia.org/wiki/XCOM:_Enemy_Unknown>

[^5]: *Stardew Valley*, Wikipedia — calendario de cuatro estaciones de 28 días con *bundles*;
    «interacting with townspeople and giving gifts builds relationships over time»; «Barone kept
    Stardew Valley open-ended so players would not feel rushed to try to complete everything»,
    diseñado «to encourage a relaxed playstyle, allowing players to take as much time as they
    wanted» —
    <https://en.wikipedia.org/wiki/Stardew_Valley>

[^6]: *Incremental game*, Wikipedia — *AdVenture Capitalist* como pionero de «un sistema de
    ganancias offline que rastrea el progreso del jugador cuando el juego no está abierto»;
    prestigio como reinicio a cambio de ventajas permanentes; números expresados en notación
    científica o con nombres abreviados a partir de cierta magnitud —
    <https://en.wikipedia.org/wiki/Incremental_game>

[^7]: `13 · 13 §11.4` de esta misma biblioteca, sobre `int64` y la representación mantisa +
    exponente para cifras que lo superan — no es una fuente externa, se cita para dejar claro
    qué parte de §6.3 es nueva y cuál solo implementa lo ya escrito allí.
