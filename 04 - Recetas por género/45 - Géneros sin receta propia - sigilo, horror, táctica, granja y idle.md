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

## 7 · Géneros que se resuelven combinando piezas ya escritas

> Diez géneros más que la auditoría `_indice/auditorias/r4-generos.md` (2026-09-07) encontró
> sin cubrir o cubiertos a medias. A diferencia de §2-§6, ninguno de estos necesita una receta
> completa propia: la mayoría son la combinación honesta de sistemas que esta biblioteca ya
> tiene escritos en otro sitio. Donde de verdad falta algo — gestión deportiva y tower offense
> — este documento lo construye con código real; donde el hueco es genuino pero no se cierra hoy
> (city builder a escala de ciudad, 4X completo) se dice sin rodeos, con el motivo y la
> auditoría que lo determinó.

### 7.1 · Walking simulator y terror en primera persona explícito

Se combinan aquí porque comparten la misma base técnica — cámara subjetiva, exploración sin
combate — y la diferencia entre ambos es de tono, no de sistema.

**Walking simulator.** Wikipedia lo define como «un juego de aventura que consiste
principalmente en movimiento e interacción con el entorno»[^8], y es explícito en lo que le
falta a propósito: «los *walking sims* generalmente no tienen mecánicas de combate ni
escenarios tradicionales de victoria o derrota»[^8]. Las piezas que ya existen cubren el género
entero: el bucle de curiosidad → observación → navegación → recompensa que estructura la
exploración está en
[13 · 22 §1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/22%20-%20Diseño%20de%20mundo%20y%20exploración.md#1--los-principios),
con el grafo de bloqueos de §2 si el paseo tiene progresión de zonas; la cámara en primera
persona con el ratón bloqueado — sensibilidad, `window_mouse_set_locked`, el patrón correcto
con `window_mouse_get_delta_x`/`_y` en vez de recentrar el cursor cada frame — está completa en
[04 · 29 §7](./29%20-%203D%20en%20GameMaker.md#primera-persona-con-el-ratón-bloqueado)
(«Primera persona con el ratón bloqueado»); la narrativa ambiental sin diálogo hablado —
objetos, descripciones, documentos encontrados — está en
[13 · 12 §3.1-§3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md#31-narrativa-ambiental-environmental-storytelling);
si el juego SÍ tiene diálogo hablado con NPC, la maquinaria completa (guion como datos, parser,
caja de texto) es [04 · 10](./10%20-%20Visual%20Novel%20y%20narrativa.md).

Lo que ningún documento anterior cubre, porque son reglas negativas — lo que el género
DELIBERADAMENTE no tiene: **sin HUD de combate** (ni barra de vida ni munición: si aparece un
HUD, que sea un objetivo o un diario, no un estado de batalla); **sin *fail state*** — no hay
forma de «perder» un walking simulator, así que ninguna mecánica de detección o daño de este
documento debería colarse sin que el diseño lo pida explícitamente; y **el ritmo lo marca la
interacción con objetos del mundo**, no un temporizador ni una oleada — el jugador decide cuándo
avanzar, la única presión legítima es la curiosidad.

**Terror en primera persona explícito** (*found footage*, cámara subjetiva, «no puedo correr
para siempre») es la combinación directa de esas tres piezas con el [§3](#3--horror) de este
propio documento (horror genérico: recursos escasos, enemigo intocable, sonido como amenaza). No
hace falta ni una línea de código nueva: la cámara de `04 · 29 §7` sustituye a cualquier cámara
de plataformas o *top-down* que los ejemplos de §3 dieran por hecha, y el resto — el medidor de
detección reutilizado como monstruo (§3.3), la munición poco fiable (§3.2), la tensión continua
(§3.4) — funciona sin cambios porque nunca dependió de una cámara concreta.

### 7.2 · Life sim (simulación de vida cotidiana, estilo *Sims*)

Un life sim no tiene un sistema propio que construir: es la superposición de tres que esta
biblioteca ya escribió por separado y nunca se habían nombrado juntos como género. **Necesidades**
— hambre, energía, higiene, diversión, con decaimiento y umbrales — es `Needs()` en
[04 · 09 §5.0](./09%20-%20Survival%20y%20crafting.md#50-necesidades), el mismo struct que §5.6
de este documento reutiliza para el ganado (con su propia degradación diaria en vez de los
métodos calibrados por fotograma, si la cadencia del juego es por franjas de actividad y no
tiempo real puro). **Relaciones** — afinidad con NPC, regalos, ramificación de diálogo — es
`VNState` en
[04 · 10 §5.2](./10%20-%20Visual%20Novel%20y%20narrativa.md#52-estado-de-la-historia), el mismo
sistema que §5.4 de este documento envuelve para los corazones de granja. **Rutinas** — qué hace
cada NPC a cada hora del día, y el despachador que decide su siguiente tarea — es
[04 · 51 §3](./51%20-%20Colonia%20y%20constructor%20de%20bases%20-%20trabajadores%20autónomos.md#3--rutinas-y-horarios-de-npc),
ya diseñado sobre el mismo reloj de `04 · 09 §5.5`.

Ningún life sim necesita un sistema nuevo por esto: necesita las tres piezas trabajando sobre el
MISMO reloj (`04 · 09 §5.5`) y el MISMO bus de señales
([04 · 16](./16%20-%20Señales%20y%20desacoplamiento.md)), exactamente como ya se conectan
calendario, cultivos y relaciones en §5 de este documento. La diferencia frente a una granja
*cozy* no es técnica, es de foco: la granja pone el cultivo en el centro y las relaciones
alrededor; un life sim invierte esa jerarquía y pone las necesidades y relaciones del personaje
jugable en el centro, con el trabajo o la economía como una rutina de horario más
(`04 · 51 §3.1`) en vez del sistema principal.

### 7.3 · City builder / tycoon a escala de ciudad

**Esto NO está cubierto**, y conviene decirlo con precisión para no confundirlo con lo que sí lo
está. [04 · 51](./51%20-%20Colonia%20y%20constructor%20de%20bases%20-%20trabajadores%20autónomos.md)
(colonia y constructor de bases) resuelve un género vecino pero distinto: colonos individuales
con nombre, necesidades y una IA de tareas (*RimWorld*, *Dwarf Fortress*) — cada habitante es una
instancia que el jugador puede seleccionar y seguir. Un *city builder* a escala de ciudad
(*SimCity*, *Cities: Skylines*) es otra cosa: miles de habitantes son estadística agregada, no
instancias, y el sistema que define el género — zonificación que hace crecer el mapa de forma
orgánica según la demanda, y simulación de tráfico sobre una red de calles — no tiene ni una
línea escrita en esta biblioteca (auditoría `r4-generos.md`, tema 18).

Lo que SÍ existe y ayuda de verdad, sin ser el sistema en sí: la generación de calles y manzanas
de
[13 · 22 §3.3 bis](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/22%20-%20Diseño%20de%20mundo%20y%20exploración.md#33-bis--ciudades-y-redes-de-calles)
es geometría de mundo (trazar una red de vías con reglas de manzana), no el sistema económico que
un *city builder* necesita para decidir DÓNDE crece la ciudad — pero es la base geométrica sobre
la que ese sistema se construiría. Las redes de energía y fluidos dirigidas sobre grafo de
[04 · 51 §6](./51%20-%20Colonia%20y%20constructor%20de%20bases%20-%20trabajadores%20autónomos.md#6--redes-de-energía-y-fluidos)
son el mismo patrón de datos que necesitaría una red de tráfico, solo que sin los nodos de
«vehículo» moviéndose por ella.

Si tu juego necesita esto de verdad, son dos sistemas nuevos y sustanciales — no una receta de
una tarde: zonificación con crecimiento por demanda, y simulación de tráfico aunque sea agregada,
sin vehículos individuales. Candidatos a documento propio si esta biblioteca los cierra en el
futuro, no algo que este documento resuelve hoy.

### 7.4 · Gestión deportiva / manager

**La convención.** Un jugador de manager deportivo (*Football Manager* es el ejemplo dominante
del género) no controla el partido: decide antes de que empiece — alineación, táctica, fichajes —
y lo ve resolverse. Wikipedia resume la distinción de género con precisión: los juegos de gestión
deportiva sitúan al jugador «en el papel de mánager o ejecutivo de un equipo en vez de controlar
directamente a los atletas durante los partidos», con una jugabilidad centrada en «planificación
estratégica, fichajes, gestión financiera, entrenamiento y desarrollo del equipo a largo plazo», y
el género se asocia con «sistemas estadísticos profundos y progresión a largo plazo, más que con
la acción momento a momento»[^9].

`04 · 49` cubre el género vecino — deportes **jugados** en tiempo real, con balón físico, pase e
IA por roles — y es explícito en que nunca resuelve un partido por simulación de eventos
discretos ni por un menú de alineación (auditoría `r4-generos.md`, tema 17, verificado leyendo su
índice de secciones completo). Esta sección cierra ese hueco concreto: un motor de partido que
resuelve por probabilidad, no por física, más la plantilla, las transferencias y el calendario de
liga que lo rodean.

**Por qué esto SÍ lleva código nuevo, a diferencia del resto de §7.** El resto de este documento
conecta piezas que ya existen; un manager deportivo necesita un motor de resolución que no se
parece a nada más de la biblioteca — ni al combate de `04 · 30`/`04 · 34` (daño instancia a
instancia), ni a la táctica de `04 · 35` (rejilla y turnos), ni a la economía de `13 · 01 §4.1`
(fuentes y sumideros sin narrativa de partido). Es su propio motor: posesión → ataque → tiro,
resuelto con probabilidades derivadas de comparar estadísticas de plantilla, más el avance del
minuto con una máquina de estados simple.

```gml
/// scr_manager_partido — el motor: plantilla, fuerza de equipo y probabilidad de gol.
/// Ningún símbolo de aquí sustituye nada de 04 · 30/04 · 34/04 · 35: es un motor nuevo,
/// pensado para resolverse sin física ni frame a frame.

enum EstadoPartidoSim { PRIMERA_PARTE, DESCANSO, SEGUNDA_PARTE, FINALIZADO }
enum ResultadoPosesion { SIN_LLEGADA, PARADA, GOL }

/// @func jugador_crear(_nombre, _posicion, _ataque, _defensa, _valor_mercado)
/// @param {String} _posicion  "GUARDAMETA" · "DEFENSA" · "CENTROCAMPISTA" · "DELANTERO"
function jugador_crear(_nombre, _posicion, _ataque, _defensa, _valor_mercado)
{
    return {
        nombre: _nombre, posicion: _posicion,
        ataque: _ataque, defensa: _defensa,          // 1..100
        valor_mercado: _valor_mercado
    };
}

/// @func equipo_crear(_nombre, _jugadores, _presupuesto)
function equipo_crear(_nombre, _jugadores, _presupuesto)
{
    return {
        nombre: _nombre, jugadores: _jugadores, presupuesto: _presupuesto,
        puntos: 0, ganados: 0, empatados: 0, perdidos: 0,
        goles_favor: 0, goles_contra: 0
    };
}

/// @func equipo_fuerza_ataque(_equipo)
/// @desc Media de ataque de los jugadores de campo (todos menos el guardameta).
function equipo_fuerza_ataque(_equipo)
{
    var _suma = 0, _n = 0;
    for (var _i = 0; _i < array_length(_equipo.jugadores); _i++)
    {
        var _j = _equipo.jugadores[_i];
        if (_j.posicion != "GUARDAMETA") { _suma += _j.ataque; _n += 1; }
    }
    return (_n > 0) ? (_suma / _n) : 50;
}

/// @func equipo_fuerza_defensa(_equipo)
/// @desc Media de defensa del bloque defensivo: defensas y guardameta, no delanteros.
function equipo_fuerza_defensa(_equipo)
{
    var _suma = 0, _n = 0;
    for (var _i = 0; _i < array_length(_equipo.jugadores); _i++)
    {
        var _j = _equipo.jugadores[_i];
        if (_j.posicion == "DEFENSA" || _j.posicion == "GUARDAMETA") { _suma += _j.defensa; _n += 1; }
    }
    return (_n > 0) ? (_suma / _n) : 50;
}

#macro PARTIDO_PROB_GOL_BASE   0.10   // conversión con fuerzas iguales, punto de partida a ajustar
#macro PARTIDO_PROB_GOL_MIN    0.02
#macro PARTIDO_PROB_GOL_MAX    0.45

/// @func partido_probabilidad_gol(_fuerza_ataque, _fuerza_defensa)
/// @desc Convierte la comparación ataque/defensa en una probabilidad de gol POR OCASIÓN ya
///       creada, 0..1. Lineal y acotada a propósito: nada de exponenciales que disparen la
///       probabilidad con diferencias de plantilla extremas.
function partido_probabilidad_gol(_fuerza_ataque, _fuerza_defensa)
{
    var _diferencia = _fuerza_ataque - _fuerza_defensa;              // -99..99
    var _prob = PARTIDO_PROB_GOL_BASE + (_diferencia / 100) * 0.35;
    return clamp(_prob, PARTIDO_PROB_GOL_MIN, PARTIDO_PROB_GOL_MAX);
}

/// @func partido_resolver_posesion(_atacante, _defensor)
/// @desc Un evento discreto en dos tiradas: primero si la posesión LLEGA a generar una
///       ocasión (favorece al equipo con más ataque frente a la defensa rival), y solo si
///       llega, si esa ocasión se convierte. Mismo patrón de "una tirada por evento" que
///       arma_intentar_disparo() (§3.2 de este documento): random() contra una probabilidad
///       calculada, nunca física ni posición real de balón.
function partido_resolver_posesion(_atacante, _defensor)
{
    var _fuerza_ataque  = equipo_fuerza_ataque(_atacante);
    var _fuerza_defensa = equipo_fuerza_defensa(_defensor);

    var _prob_llegada = clamp(0.35 + (_fuerza_ataque - _fuerza_defensa) / 200, 0.15, 0.65);
    if (random(1) >= _prob_llegada) { return ResultadoPosesion.SIN_LLEGADA; }

    var _prob_gol = partido_probabilidad_gol(_fuerza_ataque, _fuerza_defensa);
    return (random(1) < _prob_gol) ? ResultadoPosesion.GOL : ResultadoPosesion.PARADA;
}

/// @func partido_crear(_local, _visitante)
function partido_crear(_local, _visitante)
{
    return {
        local: _local, visitante: _visitante,
        goles_local: 0, goles_visitante: 0,
        minuto: 0, estado: EstadoPartidoSim.PRIMERA_PARTE,
        eventos: []                          // feed de texto para un marcador "en directo"
    };
}

#macro PARTIDO_PROB_POSESION_POR_MINUTO   0.5   // ~45 posesiones "que cuentan" en 90 minutos

/// @func partido_simular_minuto(_partido)
/// @desc Un minuto puede no tener nada que contar (posesión trivial en el centro del campo):
///       simular las 90 posesiones de un partido no aporta nada que el marcador no cuente ya.
///       La posesión se reparte por fuerza total: el equipo mejor valorado la tiene más a
///       menudo, no 50/50 fijo.
function partido_simular_minuto(_partido)
{
    if (random(1) >= PARTIDO_PROB_POSESION_POR_MINUTO) { return; }

    var _poder_local     = (equipo_fuerza_ataque(_partido.local)     + equipo_fuerza_defensa(_partido.local))     / 2;
    var _poder_visitante = (equipo_fuerza_ataque(_partido.visitante) + equipo_fuerza_defensa(_partido.visitante)) / 2;
    var _ataca_local = (random(_poder_local + _poder_visitante) < _poder_local);

    var _atacante = _ataca_local ? _partido.local     : _partido.visitante;
    var _defensor = _ataca_local ? _partido.visitante : _partido.local;

    var _resultado = partido_resolver_posesion(_atacante, _defensor);
    if (_resultado == ResultadoPosesion.GOL)
    {
        if (_ataca_local) { _partido.goles_local += 1; } else { _partido.goles_visitante += 1; }
        array_push(_partido.eventos, { minuto: _partido.minuto, texto: $"¡Gol de {_atacante.nombre}!" });
    }
    else if (_resultado == ResultadoPosesion.PARADA)
    {
        array_push(_partido.eventos, { minuto: _partido.minuto, texto: $"Ocasión de {_atacante.nombre}, parada del guardameta." });
    }
}

/// @func partido_avanzar_minuto(_partido)
/// @desc Se llama UNA vez por minuto simulado — desde un Step con temporizador si el
///       jugador está viendo el partido "en directo", o en bucle si pulsa "simular todo".
///       La máquina de estados que pide el encargo: dos tiempos de 45 minutos y un descanso.
function partido_avanzar_minuto(_partido)
{
    switch (_partido.estado)
    {
        case EstadoPartidoSim.PRIMERA_PARTE:
            _partido.minuto += 1;
            partido_simular_minuto(_partido);
            if (_partido.minuto >= 45) { _partido.estado = EstadoPartidoSim.DESCANSO; }
            break;

        case EstadoPartidoSim.DESCANSO:
            _partido.estado = EstadoPartidoSim.SEGUNDA_PARTE;
            break;

        case EstadoPartidoSim.SEGUNDA_PARTE:
            _partido.minuto += 1;
            partido_simular_minuto(_partido);
            if (_partido.minuto >= 90) { _partido.estado = EstadoPartidoSim.FINALIZADO; }
            break;

        case EstadoPartidoSim.FINALIZADO:
            break;                            // nada más: el llamador debe dejar de avanzar
    }
}

/// @func partido_simular_completo(_local, _visitante)
/// @desc Resuelve el partido entero de una vez, para las jornadas que el jugador NO ve en
///       directo — reutiliza la MISMA máquina de estados de partido_avanzar_minuto(), no una
///       lógica paralela.
function partido_simular_completo(_local, _visitante)
{
    var _partido = partido_crear(_local, _visitante);
    while (_partido.estado != EstadoPartidoSim.FINALIZADO) { partido_avanzar_minuto(_partido); }
    return _partido;
}
```

> ⚠️ **Estas constantes son un punto de partida, no una calibración real.** Con
> `PARTIDO_PROB_GOL_BASE = 0.10` y `PARTIDO_PROB_POSESION_POR_MINUTO = 0.5`, dos equipos iguales
> anotan de media 1-2 goles por partido combinados. No se ha verificado contra una fuente
> primaria cuántos goles produce de media un partido de fútbol real, así que aquí no se cita esa
> cifra: ajusta las constantes con el panel de balance en caliente de
> [13 · 01 §9.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#94--balance-en-caliente-con-el-debug-overlay)
> hasta que el resultado se sienta correcto en tu propio *playtesting*, sin dar por buena esta
> calibración de fábrica.

Plantilla, transferencias y calendario de liga completan el bucle: fichar gastando presupuesto,
y una tabla de posiciones que se recalcula cada jornada.

```gml
/// scr_manager_liga — resultado aplicado a la tabla, fichajes y calendario de vuelta única.

/// @func partido_aplicar_resultado(_partido)
/// @desc Traduce el marcador final en puntos de liga (3-1-0) y estadística de gol. Se llama
///       UNA vez, al terminar el partido (estado FINALIZADO), nunca durante la simulación.
function partido_aplicar_resultado(_partido)
{
    var _local = _partido.local, _visitante = _partido.visitante;

    _local.goles_favor      += _partido.goles_local;
    _local.goles_contra     += _partido.goles_visitante;
    _visitante.goles_favor  += _partido.goles_visitante;
    _visitante.goles_contra += _partido.goles_local;

    if (_partido.goles_local > _partido.goles_visitante)
    {
        _local.puntos += 3;     _local.ganados += 1;     _visitante.perdidos += 1;
    }
    else if (_partido.goles_local < _partido.goles_visitante)
    {
        _visitante.puntos += 3; _visitante.ganados += 1; _local.perdidos += 1;
    }
    else
    {
        _local.puntos += 1;     _visitante.puntos += 1;
        _local.empatados += 1;  _visitante.empatados += 1;
    }
}

/// @func mercado_fichar(_jugador, _origen, _destino)
/// @desc Mueve un jugador de un equipo a otro si el presupuesto del destino alcanza. No
///       reescribe jugador_crear() ni equipo_crear(): solo mueve el struct entre dos arrays
///       y ajusta el presupuesto de ambos lados.
/// @return {Bool}
function mercado_fichar(_jugador, _origen, _destino)
{
    if (_destino.presupuesto < _jugador.valor_mercado) { return false; }

    var _indice = array_get_index(_origen.jugadores, _jugador);
    if (_indice < 0) { return false; }                 // _jugador no está en el equipo _origen

    array_delete(_origen.jugadores, _indice, 1);
    array_push(_destino.jugadores, _jugador);

    _destino.presupuesto -= _jugador.valor_mercado;
    _origen.presupuesto  += _jugador.valor_mercado;
    return true;
}

/// @func liga_generar_calendario(_equipos)
/// @desc Calendario de una vuelta (todos contra todos una vez) por el método del círculo: un
///       equipo fijo, los demás rotan una posición cada jornada. Con número impar de equipos
///       se añade un hueco `undefined` que cada uno se salta una vez (jornada de descanso).
/// @param {Array<Struct>} _equipos
/// @return {Array} un array de jornadas; cada jornada es un array de { local, visitante }
function liga_generar_calendario(_equipos)
{
    var _lista = array_create(array_length(_equipos));
    array_copy(_lista, 0, _equipos, 0, array_length(_equipos));
    if (array_length(_lista) mod 2 != 0) { array_push(_lista, undefined); }

    var _n = array_length(_lista);
    var _jornadas = [];

    for (var _j = 0; _j < _n - 1; _j++)
    {
        var _partidos_jornada = [];
        for (var _i = 0; _i < _n / 2; _i++)
        {
            var _local     = _lista[_i];
            var _visitante = _lista[_n - 1 - _i];
            if (_local != undefined && _visitante != undefined)
            {
                array_push(_partidos_jornada, { local: _local, visitante: _visitante });
            }
        }
        array_push(_jornadas, _partidos_jornada);

        // Rotar: la posición 0 se queda fija, el último pasa a la 1 y el resto se desplaza.
        var _ultimo = _lista[_n - 1];
        for (var _k = _n - 1; _k > 1; _k--) { _lista[_k] = _lista[_k - 1]; }
        _lista[1] = _ultimo;
    }
    return _jornadas;
}

/// @func liga_tabla_posiciones(_equipos)
/// @desc Copia y ordena por puntos y, en empate, por diferencia de goles. array_sort()
///       modifica el array que recibe: se ordena una COPIA, nunca la lista original de
///       equipos — evita reordenar por sorpresa la fuente de verdad de la liga.
function liga_tabla_posiciones(_equipos)
{
    var _tabla = array_create(array_length(_equipos));
    array_copy(_tabla, 0, _equipos, 0, array_length(_equipos));

    array_sort(_tabla, function(_a, _b)
    {
        if (_a.puntos != _b.puntos) { return (_b.puntos - _a.puntos); }
        var _dg_a = _a.goles_favor - _a.goles_contra;
        var _dg_b = _b.goles_favor - _b.goles_contra;
        return (_dg_b - _dg_a);              // ambos restos son enteros: sin el aviso de coma
                                              // flotante que el manual hace sobre array_sort()
    });
    return _tabla;
}
```

**A qué apoyarte**

- Deportes jugados en tiempo real, si el juego combina ambos modos (partido jugable a veces,
  simulado otras): [04 · 49](./49%20-%20Deportes%20y%20física%20de%20mesa.md).
- Economía y ajuste fino: `13 · 01 §4.1` (vocabulario de fuentes y sumideros) y
  `13 · 01 §9.4` (panel de balance en caliente, reutilizable tal cual para las constantes de
  arriba).
- Guardado de plantilla, calendario y tabla:
  [01 · 14 §9](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#9-sistema-de-guardado-completo-recomendado),
  el mismo patrón JSON que usa el idle de §6.4 de este documento.

### 7.5 · 4X (explorar, expandir, explotar, exterminar)

Un 4X (*Civilization*, *Old World*) une dos motores que la biblioteca ya construyó completos, más
una pieza que falta. El RTS de
[04 · 13 §4-§5](./13%20-%20Estrategia%20y%20gestión.md#4-sistemas-clave) da selección, órdenes,
niebla de guerra y producción por cola — el «expandir/explotar» de la sigla, con el turno
cambiado por tiempo real si tu 4X es por turnos (la mayoría lo son: cambia el bucle de Step por
una fase de turno, sin tocar la selección ni las órdenes). La táctica por turnos de
[04 · 35](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md) completa da el
«exterminar» cuando dos ejércitos chocan en una casilla — rejilla, línea de tiro, cobertura,
iniciativa.

Lo que falta de verdad son dos sistemas de gestión de imperio que ningún RTS necesita: el árbol
tecnológico y la diplomacia. El árbol tecnológico NO es un sistema nuevo — es el mismo grafo de
nodos con prerrequisitos que
[13 · 16 §3.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#31-el-grafo-de-nodos-modelo-de-datos-en-json-y-carga-a-structs)
ya construyó para árboles de habilidades (modelo de datos en JSON, carga a *structs*), con la
validación de ciclos y alcanzabilidad de
[13 · 16 §3.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#32-validación-por-grafo-ciclos-kahnbfs-y-alcanzabilidad-bfs);
un árbol tecnológico de 4X es ese mismo grafo con «coste en turnos de investigación» en vez de
«coste en puntos de habilidad» como unidad de desbloqueo. La diplomacia (tratados, guerra y paz,
IA de facción con actitud hacia el jugador) no tiene ni una pieza reutilizable en esta
biblioteca — es el hueco real, y no se resuelve componiendo documentos existentes (auditoría
`r4-generos.md`, tema 15).

### 7.6 · Sandbox creativo

Un modo *sandbox*/creativo (Minecraft en modo creativo, el editor libre de muchos *builders*) no
tiene sistemas propios: es el MISMO inventario y crafteo de
[04 · 09 §4.1-§4.3](./09%20-%20Survival%20y%20crafting.md#4-sistemas-clave) y la MISMA colocación
en rejilla de
[04 · 51 §5.1](./51%20-%20Colonia%20y%20constructor%20de%20bases%20-%20trabajadores%20autónomos.md#51--plano-frente-a-construido-dos-capas-no-una),
con los sumideros de recursos desconectados — nunca se gasta lo que se coloca, nunca hay un
contador de cuánto queda. Es, literalmente, el «modo sin fallar» que §5.1 de este mismo documento
ya nombra para la granja, llevado un paso más allá: no solo sin fallo, sin coste. Lo único que un
*sandbox* añade encima de esos dos sistemas es una bandera de modo que la validación de coste ya
existente debe consultar antes de descontar materiales — no un sistema nuevo.

### 7.7 · Tower offense

Un *tower offense* invierte quién ataca y quién defiende frente a un tower defense: en vez de
torres estáticas defendiendo un camino contra enemigos que avanzan, son **unidades móviles las
que avanzan** hacia un objetivo defendido por posiciones estáticas. `04 · 08 §1` ya lo nombra en
su tabla de subgéneros («Torres móviles que avanzan», dificultad Media) sin desarrollarlo — esta
sección lo desarrolla reutilizando, sin tocar ni una línea, el mismo `TDGrid` y el mismo
*pathfinding* de
[04 · 08 §5.1](./08%20-%20Tower%20Defense.md#51-la-grid-lógica) (`mp_grid_create`,
`calcular_path()` sobre `mp_grid_path`). Lo único que cambia es qué objeto sigue el camino y qué
objeto dispara.

```gml
/// obj_atacante_movil · Create — la "torre" de 04 · 08 pasa a ser esto: una unidad que
/// avanza en vez de defender quieta. Usa la MISMA TDGrid de 04 · 08 §5.1: no se crea una
/// rejilla nueva, se recibe la del nivel al spawnear (mismo patrón que enemigo_set_path()
/// de 04 · 08 §5.5, con origen y destino invertidos).
/// @param {Struct} _grid     TDGrid (04 · 08 §5.1), ya existente en el nivel.
/// @param {Real}   _celda_x  Celda de origen (spawn del atacante).
/// @param {Real}   _celda_y
/// @param {Real}   _obj_x    Celda del objetivo defendido.
/// @param {Real}   _obj_y

grid           = _grid;
vida           = 40;
dano_impacto   = 10;                        // daño al objetivo defendido, al llegar
velocidad_base = 1.2;

var _ruta = grid.calcular_path(_celda_x, _celda_y, _obj_x, _obj_y);
if (_ruta == noone)
{
    instance_destroy();                     // sin camino al objetivo: no tiene sentido existir
    exit;
}
path_start(_ruta, velocidad_base, path_action_stop, false);
```

```gml
/// obj_atacante_movil · Step — llega al objetivo defendido, o muere en el camino
if (path_position >= 1)
{
    with (obj_objetivo_defendido) { vida -= other.dano_impacto; }
    if (path_exists(path_index)) { path_delete(path_index); }
    instance_destroy();
    exit;
}

if (vida <= 0)
{
    if (path_exists(path_index)) { path_delete(path_index); }
    instance_destroy();
}
```

El defensor estático es literalmente `objTowerBase` de
[04 · 08 §5.3](./08%20-%20Tower%20Defense.md#53-torre-targeting-y-disparo) sin cambiar ni una
línea de apuntado ni de disparo — el único cambio es a quién apunta `buscar_objetivo()`: el
`with (objEnemyBase)` de esa función pasa a ser `with (obj_atacante_movil)`, porque ahora es el
atacante quien se mueve por el camino y el defensor quien se queda quieto disparándole. El
objetivo defendido es la única pieza sin equivalente en un TD normal — ahí no hay «vidas del
jugador» que perder, hay una estructura con barra de vida propia:

```gml
/// obj_objetivo_defendido · Create
vida     = 500;
vida_max = 500;

/// obj_objetivo_defendido · Step
if (vida <= 0) { global.atacante_gana = true; }   // el objetivo cayó: gana quien atacaba
```

Las oleadas de atacantes reutilizan sin cambios
[04 · 08 §5.8](./08%20-%20Tower%20Defense.md#58-oleadas-desde-structs) (oleadas desde *structs*):
esa función solo le importa instanciar un objeto desde una definición, es indiferente a si el
objeto instanciado avanza o defiende.

### 7.8 · Escape room / sala de escape

Una sala de escape no tiene ni un sistema propio: es
[04 · 48](./48%20-%20Aventura%20gráfica%20y%20point%20and%20click.md) (aventura gráfica y *point
& click*) con el mapa recortado a una sola sala. Los sistemas que definen una sala de escape ya
están completos ahí — hotspots por objeto, máscara o polígono
([§3.1](./48%20-%20Aventura%20gráfica%20y%20point%20and%20click.md#31--hotspots-tres-formas-de-marcar-una-zona-interactiva)),
cursor contextual con prioridad (§3.2), inventario combinatorio para combinar objetos entre sí
([§3.7](./48%20-%20Aventura%20gráfica%20y%20point%20and%20click.md#37--inventario-combinatorio)),
y estado del mundo por banderas globales para que abrir el cajón dependa de haber usado la llave
en la cerradura antes (§3.8). Lo único que una sala de escape NO necesita de `04 · 48` es el
viaje entre escenas (§2, la transición entre habitaciones de una aventura completa): vive y muere
en una sola *room*, con el mismo sistema de banderas decidiendo qué hotspot se activa según lo
que ya se resolvió, no qué habitación se carga.

### 7.9 · Experiencias de menos de 5 minutos (*microgames* de *jam*/itch)

**La convención:** en un *microgame* el jugador decide en los primeros segundos si sigue
jugando.
[13 · 11 §1.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción,%20alcance%20y%20lanzamiento.md#14-prototipo-mvp-y-vertical-slice-tres-cosas-distintas)
ya fija el prototipo como «jugable en un minuto»; un *microgame* de *jam* ES ese prototipo,
pulido, sin las capas de progresión que un juego completo añadiría encima.
[04 · 11](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md) (arcade y juegos de un botón) es la
pieza técnica más cercana — control reducido a una entrada, dificultad progresiva, reinicio
instantáneo (§5.5) — pero pensada para un juego que se rejuega muchas veces seguidas, no para una
sesión que empieza y acaba una sola vez.

Lo que falta encima de esas dos piezas son dos reglas de ritmo que solo importan cuando la sesión
completa dura menos que la paciencia de quien juega una *jam*:

**1 · Sin menú, carga inmediata.** El juego no se abre con una pantalla de título esperando una
pulsación: empieza jugándose. Si hacen falta instrucciones, van ENCIMA de la acción, no antes —
la «regla de los 3 segundos»: el objetivo se lee sin pulsar nada, y se retira solo.

```gml
/// obj_control · Create — arranca el juego en marcha; no hay un room de menú que cargar antes
partida_tiempo    = 0;
mostrar_objetivo  = true;

/// obj_control · Step — el rótulo se retira solo, nunca por una pulsación de "empezar"
partida_tiempo += delta_time / 1000000;
if (partida_tiempo > 3) { mostrar_objetivo = false; }

/// obj_control · Draw GUI — el objetivo se lee mientras el juego YA está corriendo debajo
if (mostrar_objetivo)
{
    draw_set_alpha(clamp(1 - (partida_tiempo / 3), 0, 1));      // se desvanece, no corta de golpe
    draw_text(20, 20, "Objetivo: llega a la meta antes de que suba la marea");
    draw_set_alpha(1);
}
```

**2 · Reinicio instantáneo, sin pantalla de resultados de tres clics.**
[04 · 11 §5.5](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md#55-muerte-y-reinicio-instantáneo)
ya construyó la muerte y el reinicio instantáneo para arcade; un *microgame* usa el MISMO patrón
sin cambiar nada, con una diferencia de tono: no suele haber un *high score* que justifique una
pantalla aparte, así que el reinicio vuelve al juego directamente, no a un menú de resultados.

### 7.10 · Lo que queda fuera, y por qué

La auditoría `_indice/auditorias/r4-generos.md` (2026-09-07) cribó estos géneros contra las
etiquetas reales de itch.io y Steam y decidió que ninguno justifica receta propia hoy — por baja
demanda real en GameMaker, o porque exigen infraestructura de *live service* fuera del alcance de
un proyecto en solitario. El número entre paréntesis es el tema de esa auditoría, por si una
ronda futura quiere revisar el veredicto.

| Género | Por qué no |
|---|---|
| **Immersive sim** (sistemas emergentes, sin guion) | Alcance enorme —*Deus Ex*, *Prey*— y prácticamente inexistente en GameMaker; 0 resultados en la biblioteca antes de esta auditoría (tema 7) |
| **MOBA** (carriles, torres, *creeps*) | Exige infraestructura de *matchmaking* y balance competitivo de *live service* fuera del alcance realista de un proyecto en solitario (tema 10) |
| **Extraction shooter** (loteo, extracción, perder botín al morir) | Los cimientos de red ya existen (`04 · 14 §10`, tablas de *loot* de `04 · 05`), pero el género completo con red competitiva en tiempo real es más proyecto que receta (tema 8) |
| **Battle royale** (zona que se encoge, último en pie) | Mismos cimientos de red que el *extraction shooter*; la mecánica del círculo es sencilla (`lerp` sobre un radio), la infraestructura de decenas de jugadores simultáneos no lo es (tema 9) |
| **Hidden object games** (objetos ocultos) | Género casi extinto fuera de móvil casual; 0 resultados, sin demanda que lo justifique (tema 28) |
| **Juegos de palabras** (*Wordle*-style) | Las funciones de comparación de cadenas ya existen sueltas en `08` (referencia GML); falta ensamblarlas en una receta, pero la demanda es baja (tema 29) |
| **Juegos de dibujar** (*Gartic Phone*-style) | La captura de trazos con `surface`/`sprite_add` existe dispersa en otros documentos, nunca ensamblada para esto; baja demanda (tema 32) |
| **Mecanografía** (*typing games*) | Técnicamente cercano a las ventanas de acierto de `13 · 19` (rítmica) pero sin desarrollar; baja demanda (tema 33) |
| **Simuladores hardcore de vuelo/conducción** | GameMaker es mal ajuste para aerodinámica realista y sistemas de cabina complejos; `04 · 12` cubre el eje arcade, no el simulador duro (tema 21) |

Si tu proyecto necesita de verdad uno de estos, la columna «por qué no» es un punto de partida
honesto, no un veto: dice qué falta y por qué esta biblioteca no lo dio por prioritario hoy, no
que sea imposible construirlo.

---

## 8 · Checklist transversal

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
- [ ] **Manager deportivo**: la probabilidad de gol sale de comparar estadísticas de plantilla
      (`equipo_fuerza_ataque()`/`_defensa()`), nunca un marcador fijado a mano.
- [ ] **Tower offense**: el atacante móvil usa el MISMO `TDGrid`/pathfinding de `04 · 08 §5.1` —
      no se reimplementa un A* nuevo solo por invertir quién ataca y quién defiende.
- [ ] **Experiencias <5 min**: el objetivo se lee en los primeros segundos sin pulsar nada, y no
      hay pantalla de menú antes de que el juego empiece a correr.

## 9 · Errores clásicos y cómo evitarlos

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
| Simular un partido de manager con `random()` puro, sin comparar plantillas | Parece «aleatorio = justo» | El marcador debe correlacionar con la calidad del equipo: calcula `equipo_fuerza_ataque()`/`_defensa()` (§7.4) antes de tirar el dado |
| Reimplementar el pathfinding para un tower offense | Parece que «atacar» necesita una rejilla distinta de «defender» | Es la MISMA `TDGrid` de `04 · 08 §5.1` (§7.7): solo cambia qué objeto la usa y en qué dirección va el camino |
| Un *microgame* con pantalla de título y menú de opciones antes de jugar | Se copia la estructura de un juego completo por costumbre | La regla de los 3 segundos (§7.9): el juego empieza corriendo, el objetivo se lee encima, sin pulsar nada |

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
- [13 · 22 — Diseño de mundo y exploración](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/22%20-%20Diseño%20de%20mundo%20y%20exploración.md) — el bucle de exploración del §7.1, y la generación de calles del §7.3.
- [04 · 29 — 3D en GameMaker](./29%20-%203D%20en%20GameMaker.md) — la cámara en primera persona con el ratón bloqueado que usan el §7.1 y el terror en primera persona.
- [04 · 51 — Colonia y constructor de bases](./51%20-%20Colonia%20y%20constructor%20de%20bases%20-%20trabajadores%20autónomos.md) — rutinas y horarios (§7.2), redes de energía (§7.3) y colocación en rejilla (§7.6).
- [04 · 13 — Estrategia y gestión](./13%20-%20Estrategia%20y%20gestión.md) — el RTS completo que sostiene la mitad del §7.5.
- [04 · 08 — Tower Defense](./08%20-%20Tower%20Defense.md) — la `TDGrid` y el *pathfinding* que reutiliza sin cambios el §7.7.
- [04 · 48 — Aventura gráfica y point and click](./48%20-%20Aventura%20gráfica%20y%20point%20and%20click.md) — hotspots, cursor contextual e inventario combinatorio, la base del §7.8.
- [13 · 11 — Producción, alcance y lanzamiento](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción,%20alcance%20y%20lanzamiento.md) — la escala prototipo/MVP/vertical slice del §7.9.
- [04 · 11 — Arcade y juegos de un botón](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md) — el reinicio instantáneo que reutiliza sin cambios el §7.9.
- [04 · 49 — Deportes y física de mesa](./49%20-%20Deportes%20y%20física%20de%20mesa.md) — el deporte JUGADO en tiempo real, el género vecino del manager de §7.4.

## Fuentes

**Manual oficial y runtime** — todos los símbolos de GML de este documento comprobados con
`python3 _indice/buscar.py` contra el runtime `2026.0.0.23` (espejo local en
`09 - Manual oficial/`): `clamp`, `lerp`, `merge_colour`, `draw_healthbar`, `date_current_datetime`,
`date_second_span`, `array_create`, `array_contains`, `array_get_index`, `chr`, `ln`, `power`,
`string_format`, `variable_struct_exists`, `random`, `point_distance`, `audio_sound_gain`,
`audio_play_sound`, `delta_time`. Añadidos para el §7: `array_sort`, `array_copy`,
`array_length`, `array_push`, `array_delete`, `instance_destroy`, `path_start`, `path_position`,
`path_index`, `path_exists`, `path_delete`, `path_action_stop`, `draw_text`, `draw_set_alpha`.
`senal_emitir`/`senal_escuchar` (`04 · 16`), `en_cono_vision`
(`13 · 13 §2.4`), `hay_vision_libre`/`ia_ve_al_jugador` (`04 · 31 §5`),
`VNState.afinidad_get`/`afinidad_sumar` (`04 · 10 §5.2`) y `TDGrid.calcular_path`/`mp_grid_path`
(`04 · 08 §5.1`) son funciones **propias de la biblioteca**, no del runtime: se enlazan a su
definición en vez de reescribirlas.

**Diseño, consultadas el 2026-09-06 (§1-§6) y el 2026-09-07 (§7):**

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

[^8]: *Walking simulator*, Wikipedia, consultada el 2026-09-07 — «an adventure game that
    consists primarily of movement and environmental interaction»; «walking sims generally do
    not have combat mechanics or traditional win/lose scenarios» —
    <https://en.wikipedia.org/wiki/Walking_simulator>

[^9]: *Sports game*, Wikipedia, sección «Management», consultada el 2026-09-07 — los juegos de
    gestión deportiva sitúan al jugador «in the role of a team manager or executive rather than
    directly controlling athletes during matches», con jugabilidad centrada en «strategic
    planning, player transfers, financial management, training, and long-term team development»
    y asociada a «deep statistical systems and long-term progression rather than moment-to-moment
    action» —
    <https://en.wikipedia.org/wiki/Sports_game>
